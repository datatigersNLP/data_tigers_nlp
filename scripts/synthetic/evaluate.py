"""Lanceur exploratoire Agent0 (#96), distinct de la mesure officielle.

    python -m scripts.synthetic.evaluate --lot <dossier> --check-lot
    python -m scripts.synthetic.evaluate --lot <dossier> --run-id <nouveau_nom>

Le format du lot est décrit dans README_evaluation.md. Aucun gel ni verdict
humain n'est créé ici. L'adaptateur RAG reçoit seulement le texte des questions.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
import platform
import sys
import time
from typing import Annotated, Literal

from pydantic import Field, TypeAdapter, field_validator

if __package__:
    from .corpus import provenance_code
    from .schema import (CasSynthetique, IdentifiantLot, ModeleStrict, Texte,
                         _constante_interdite, _objet_sans_doublon)
    from .validation import (extrait_valide, normaliser_question,
                             verifier_contraintes_generation)
else:
    from corpus import provenance_code
    from schema import (CasSynthetique, IdentifiantLot, ModeleStrict, Texte,
                        _constante_interdite, _objet_sans_doublon)
    from validation import (extrait_valide, normaliser_question,
                            verifier_contraintes_generation)


RACINE = Path(__file__).resolve().parents[2]
SORTIES = RACINE / "data" / "synthetic" / "results"
SHA256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class ErreurEvaluation(ValueError):
    """Lot ou configuration incompatible : ne pas lancer la génération."""


class ManifesteLot(ModeleStrict):
    """Déclarations de gel et de séparation, à contrôler en revue humaine.

    Une valeur JSON ne prouve ni l'identité du relecteur ni l'indépendance.
    Le lanceur contrôle sa présence et sa cohérence, sans certifier le sens.
    """

    format: Literal["agent0-challenge-v1"]
    set: Literal["synthetic_challenge"]
    fige_le: Texte
    pilote_independant: Literal[True]
    note_separation: Texte
    nb_questions: Annotated[int, Field(ge=1, le=25)]
    sha256_questions: SHA256
    sha256_index: SHA256
    sha256_passages: SHA256

    @field_validator("pilote_independant", mode="before")
    @classmethod
    def verifier_declaration(cls, valeur):
        if type(valeur) is not bool or valeur is not True:
            raise ValueError("Déclaration booléenne explicite d'un pilote indépendant requise")
        return valeur

    @field_validator("fige_le")
    @classmethod
    def verifier_date(cls, valeur):
        date = datetime.fromisoformat(valeur)
        if date.utcoffset() is None or date > datetime.now(timezone.utc):
            raise ValueError("Date de gel passée avec fuseau explicite requise")
        return valeur


@dataclass(frozen=True)
class LotFige:
    manifeste: ManifesteLot
    cas: tuple[CasSynthetique, ...]
    manifeste_brut: bytes
    questions_brutes: bytes
    sha256_exclusions: str


def _sha(octets: bytes) -> str:
    return hashlib.sha256(octets).hexdigest()


def _json(octets: bytes):
    return json.loads(octets.decode("utf-8"), object_pairs_hook=_objet_sans_doublon,
                      parse_constant=_constante_interdite)


def _exclusions_historiques() -> tuple[set[str], str]:
    """Les candidats de mise au point identifiés ne deviennent pas un pilote."""
    brut = (RACINE / "docs/etudes/agent0_relecture/grille_relecture.json").read_bytes()
    reference = _json(brut)
    ids = [c["candidate_id_rapporte"] for c in reference["relectures"]]
    if not ids or any(not isinstance(i, str) or not i.strip() for i in ids):
        raise ValueError("Inventaire des candidats de mise au point invalide")
    return set(ids), _sha(brut)


def charger_lot(dossier: Path) -> LotFige:
    """Lit un snapshot sans modèle, sans produire de validation ni de sortie."""
    try:
        manifeste_brut = (Path(dossier) / "manifest.json").read_bytes()
        questions_brutes = (Path(dossier) / "questions.jsonl").read_bytes()
        manifeste = ManifesteLot.model_validate(_json(manifeste_brut))
        if _sha(questions_brutes) != manifeste.sha256_questions:
            raise ErreurEvaluation("Empreinte de questions.jsonl différente du gel")
        cas = tuple(CasSynthetique.model_validate(_json(l))
                    for l in questions_brutes.split(b"\n") if l.strip())
        exclus, sha_exclusions = _exclusions_historiques()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise ErreurEvaluation(f"Lot refusé : {exc}") from exc
    if len(cas) != manifeste.nb_questions:
        raise ErreurEvaluation("Effectif différent du manifeste")
    ids, questions = set(), set()
    for c in cas:
        if c.id in exclus:
            raise ErreurEvaluation(f"{c.id} : candidat de mise au point exclu du pilote indépendant")
        if c.validation.human != "accepted" or c.validation.automatic != "passed":
            raise ErreurEvaluation(f"{c.id} : acceptation humaine et contrôles requis")
        try:
            verifier_contraintes_generation(c, c.generation_source_ids)
        except ValueError as exc:
            raise ErreurEvaluation(f"{c.id} : {exc}") from exc
        cle = normaliser_question(c.question)
        if c.id in ids or not cle or cle in questions:
            raise ErreurEvaluation("Identifiant ou question normalisée vide/dupliqué")
        ids.add(c.id)
        questions.add(cle)
    return LotFige(manifeste, cas, manifeste_brut, questions_brutes, sha_exclusions)


def verifier_sources(lot: LotFige, index) -> None:
    """Contrôle le corpus et l'ancrage exact ; aucun jugement sémantique."""
    if (index.entete["index"]["sha256"] != lot.manifeste.sha256_index
            or index.entete["metadonnees"]["sha256"] != lot.manifeste.sha256_passages):
        raise ErreurEvaluation("Index ou passages différents du lot figé")
    passages = {p["passage_id"]: p for p in index.passages}
    for cas in lot.cas:
        if not set(cas.generation_source_ids).issubset(passages):
            raise ErreurEvaluation(f"{cas.id} : source de génération absente du corpus")
        for preuve in cas.evidence:
            if not extrait_valide(preuve.excerpt, passages[preuve.passage_id]["texte"]):
                raise ErreurEvaluation(f"{cas.id} : extrait différent du corpus figé")


class ChaineRag:
    """Adaptateur mince vers la baseline #85, sans import du CLI humain."""

    def __init__(self, index_dir: Path | None = None, modele=None, digest=None):
        if bool(modele) != bool(digest):
            raise ErreurEvaluation("Modèle et digest doivent être donnés ensemble")
        # Import différé : --check-lot ne nécessite pas NumPy ni de modèle.
        from scripts.rag import generation, rag

        self.rag, self.generation = rag, generation
        self.index = rag.charger_index(index_dir or rag.DOSSIER_INDEX)
        self.modele = modele or generation.MODELE_QWEN
        self.digest = digest or generation.DIGEST_QWEN_31
        self.encodeur = None

    def preparer(self):
        # Appelé après la vérification du lot et du corpus, une fois par run.
        self.encodeur = self.rag.charger_encodeur()
        infos = self.generation.verifier_ollama(self.modele, self.digest)
        versions = {}
        for nom in ("numpy", "sentence-transformers", "transformers", "pydantic"):
            try:
                versions[nom] = version(nom)
            except PackageNotFoundError:
                versions[nom] = None
        return {"encodeur": self.rag.MODELE_E5, "revision_e5": self.rag.REVISION_E5,
                "precision_e5": "fp32", "device_e5": "cpu", "top_k": 5,
                "version_prompt": self.rag.VERSION_PROMPT,
                "sha256_system": _sha(self.rag.CONSIGNE_RAG.encode("utf-8")),
                "index": self.index.entete, "ollama": infos,
                "parametres": self.generation.OPTIONS, "versions": versions,
                "seuil": None, "nature": "baseline #85, hors protocole 06"}

    def repondre(self, question: str) -> dict:
        debut = time.monotonic()
        resultats, contexte, generation = [], None, None
        phase = "recuperation"
        try:
            vecteur = self.rag.encoder_question(self.encodeur, question)
            resultats = self.rag.recuperer_passages(self.index, vecteur, top_k=5)
            phase = "contexte"
            contexte = self.rag.construire_contexte(question, resultats)
            phase = "generation"
            generation = self.generation.generer_reponse(
                contexte, self.rag.ABSTENTION, self.modele, self.digest)
            statut = generation["statut"]
            erreur = None
        except Exception as exc:
            statut = "erreur_technique"
            erreur = {"phase": phase, "type": type(exc).__name__, "message": str(exc)}
        return {"statut": statut, "resultats": resultats, "contexte": contexte,
                "generation": generation, "erreur": erreur,
                "duree_totale_s": time.monotonic() - debut}


def _ecrire(chemin: Path, objet: dict) -> None:
    with chemin.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(objet, f, ensure_ascii=False, allow_nan=False, indent=2)
        f.write("\n")


def _ligne(f, objet: dict) -> None:
    f.write(json.dumps(objet, ensure_ascii=False, allow_nan=False) + "\n")
    f.flush()


def empreintes_code() -> dict:
    chemins = [Path(__file__), Path(__file__).with_name("schema.py"),
               Path(__file__).with_name("validation.py"),
               RACINE / "scripts/rag/rag.py", RACINE / "scripts/rag/generation.py"]
    return {p.relative_to(RACINE).as_posix(): _sha(p.read_bytes().replace(b"\r\n", b"\n"))
            for p in chemins}


def executer(dossier_lot: Path, run_id: str, racine: Path = SORTIES,
             creer_chaine=None) -> dict:
    """Aucun nouvel essai automatique ; garde les runs partiels et erreurs."""
    TypeAdapter(IdentifiantLot).validate_python(run_id, strict=True)
    lot = charger_lot(dossier_lot)
    code = provenance_code()
    racine = Path(racine)
    racine.mkdir(parents=True, exist_ok=True)
    dossier = racine / run_id
    dossier.mkdir()  # Réservation atomique avant tout chargement/API.
    debut = time.monotonic()
    resume = {"format": "agent0-evaluation-summary-v1", "run_id": run_id,
              "statut": "interrompu", "nb_questions": len(lot.cas), "nb_resultats": 0,
              "erreurs_techniques": 0}
    phase = "preparation"
    try:
        (dossier / "jeu_manifest.json").write_bytes(lot.manifeste_brut)
        (dossier / "questions.jsonl").write_bytes(lot.questions_brutes)
        _ecrire(dossier / "manifest.json", {
            "format": "agent0-evaluation-v1", "run_id": run_id,
            "ecrit_le": datetime.now(timezone.utc).isoformat(),
            "nature": "evaluation_synthetique_exploratoire", "mesure_officielle": False,
            "lot": lot.manifeste.model_dump(), "sha256_manifeste_lot": _sha(lot.manifeste_brut),
            "sha256_inventaire_exclusions": lot.sha256_exclusions,
            "code": code, "sha256_code_lf": empreintes_code(),
            "python": platform.python_version()})
        with (dossier / "events.jsonl").open("x", encoding="utf-8", newline="\n") as events, \
                (dossier / "results.jsonl").open("x", encoding="utf-8", newline="\n") as resultats:
            chaine = (creer_chaine or ChaineRag)()
            verifier_sources(lot, chaine.index)
            _ecrire(dossier / "chaine.json", chaine.preparer())
            phase = "evaluation"
            for cas in lot.cas:
                _ligne(events, {"id": cas.id, "evenement": "debut_question",
                                "date": datetime.now(timezone.utc).isoformat()})
                debut_question = time.monotonic()
                try:
                    # Seule donnée du cas accessible au RAG. Les annotations restent ici.
                    retour = chaine.repondre(cas.question)
                except Exception as exc:
                    retour = {"statut": "erreur_technique", "erreur": {
                        "phase": "adaptateur", "type": type(exc).__name__, "message": str(exc)}}
                _ligne(resultats, {"id": cas.id, "question": cas.question, **retour,
                                    "duree_lanceur_s": time.monotonic() - debut_question})
                resume["nb_resultats"] += 1
                resume["erreurs_techniques"] += retour["statut"] == "erreur_technique"
                _ligne(events, {"id": cas.id, "evenement": "fin_question", "statut": retour["statut"]})
            resume["statut"] = "termine"
    except Exception as exc:
        resume.update(statut="erreur_" + phase,
                      erreur={"type": type(exc).__name__, "message": str(exc)})
    finally:
        resume["duree_totale_s"] = time.monotonic() - debut
        resume["sha256_fichiers"] = {p.name: _sha(p.read_bytes()) for p in sorted(dossier.iterdir())
                                    if p.is_file()}
        _ecrire(dossier / "summary.json", resume)
    return resume


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lot", type=Path, required=True)
    parser.add_argument("--check-lot", action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--output-root", type=Path, default=SORTIES)
    parser.add_argument("--modele")
    parser.add_argument("--digest")
    args = parser.parse_args(argv)
    if bool(args.modele) != bool(args.digest):
        parser.error("--modele et --digest doivent être donnés ensemble")
    if args.digest:
        try:
            TypeAdapter(SHA256).validate_python(args.digest, strict=True)
        except ValueError:
            parser.error("--digest doit être un SHA-256 de 64 caractères hexadécimaux minuscules")
    if args.check_lot and (args.run_id or args.modele):
        parser.error("--check-lot se donne seul avec --lot")
    if not args.check_lot and not args.run_id:
        parser.error("--run-id est requis pour exécuter")
    try:
        if args.check_lot:
            lot = charger_lot(args.lot)
            print(json.dumps({"statut": "declarations_et_empreinte_conformes",
                              "nb_questions": len(lot.cas), "ollama_appele": False,
                              "validation_semantique_attestee": False}, ensure_ascii=False))
            return 0
        # Le CLI humain rag.py et mesure.py ne sont jamais appelés.
        resultat = executer(args.lot, args.run_id, args.output_root,
                             lambda: ChaineRag(modele=args.modele, digest=args.digest))
        print(json.dumps(resultat, ensure_ascii=False, indent=2))
        return 0 if resultat["statut"] == "termine" else 1
    except (ValueError, OSError) as exc:
        print(f"Evaluation refusée : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # Rend aussi possible python scripts/synthetic/evaluate.py depuis un autre cwd.
    if not __package__:
        sys.path.insert(0, str(RACINE))
    raise SystemExit(main())
