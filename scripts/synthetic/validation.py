"""Contrôles automatiques des candidats #93/#94 ; aucune validation sémantique."""

import hashlib
from pathlib import Path
import re
import unicodedata

if __package__:
    from .schema import CasSynthetique, creer_candidat, lire_proposition
else:
    from schema import CasSynthetique, creer_candidat, lire_proposition


LONGUEUR_MIN_EXTRAIT = 20


def extrait_valide(extrait: str, texte: str) -> bool:
    """Vérifie la forme et l'ancrage exact, sans juger la suffisance de la preuve."""
    if len(extrait.strip()) < LONGUEUR_MIN_EXTRAIT or extrait != extrait.strip():
        return False
    return re.search(r"(?<!\w)" + re.escape(extrait) + r"(?!\w)", texte) is not None


def normaliser_question(question: str) -> str:
    texte = unicodedata.normalize("NFKC", question).casefold()
    texte = "".join(" " if unicodedata.category(c).startswith("P") else c for c in texte)
    return " ".join(texte.split())


def charger_questions_vues(dossier: Path, exclure: Path | None = None) -> tuple[set[str], list[dict]]:
    """Déduplique dans ce dossier de runs, sans lire les questions humaines."""
    questions, fichiers = set(), []
    for chemin in sorted(dossier.glob("*/candidates.jsonl")):
        if chemin.parent == exclure:
            continue
        octets = chemin.read_bytes()
        for ligne in octets.decode("utf-8").splitlines():
            if ligne.strip():
                candidat = CasSynthetique.model_validate_json(ligne)
                questions.add(normaliser_question(candidat.question))
        fichiers.append({"fichier": chemin.relative_to(dossier).as_posix(),
                         "sha256": hashlib.sha256(octets).hexdigest()})
    return questions, fichiers


def _sources_preparation(preparation: dict) -> list[dict]:
    if preparation["type"] in {"adversarial", "hors_corpus"}:
        source = preparation.get("source")
        if (preparation.get("format") != "agent0-preparation-v1" or "sources" in preparation
                or not isinstance(source, dict)
                or any(not isinstance(source.get(c), str) or not source[c].strip()
                       for c in ("passage_id", "texte"))):
            raise ValueError(f"Une préparation {preparation['type']} v1 "
                             "avec une source unique non vide est requise")
        return [source]
    if preparation["type"] != "multi_passage":
        return [preparation["source"]]
    sources = preparation.get("sources")
    if (preparation.get("format") != "agent0-preparation-v2" or "source" in preparation
            or not isinstance(sources, list) or len(sources) != 2):
        raise ValueError("Une préparation multi-passage v2 avec deux sources est requise")
    for source in sources:
        if (not isinstance(source, dict)
                or any(not isinstance(source.get(c), str) or not source[c].strip()
                       for c in ("passage_id", "texte"))):
            raise ValueError("Une source multi-passage identifiée et non vide est requise")
    if sources[0]["passage_id"] == sources[1]["passage_id"]:
        raise ValueError("Les deux sources multi-passage doivent être distinctes")
    return sources


def valider_proposition(texte: str, preparation: dict, run_id: str,
                       questions_vues: set[str]) -> CasSynthetique:
    proposition = lire_proposition(texte)
    if (proposition.type != preparation["type"]
            or proposition.difficulty_target != preparation["difficulty_target"]):
        raise ValueError("Catégorie ou difficulté différente de la demande")
    if proposition.type == "adversarial" and not proposition.answerable_proposed:
        raise ValueError("Cet incrément adversarial exige une correction proposée comme sourçable")
    sources = _sources_preparation(preparation)
    par_id = {source["passage_id"]: source for source in sources}
    for preuve in proposition.evidence:
        if preuve.passage_id not in par_id:
            raise ValueError("Preuve provenant d'une source non fournie")
        if not extrait_valide(preuve.excerpt, par_id[preuve.passage_id]["texte"]):
            raise ValueError(f"Extrait invalide : au moins {LONGUEUR_MIN_EXTRAIT} caractères, "
                             "sans espaces de bord, retrouvé mot pour mot sur des limites "
                             "de mots dans le passage fourni")
    if (proposition.type == "multi_passage"
            and {p.passage_id for p in proposition.evidence} != set(par_id)):
        raise ValueError("Chaque source multi-passage doit être couverte par une preuve")
    normalisee = normaliser_question(proposition.question)
    if not normalisee or normalisee in questions_vues:
        raise ValueError("Question vide après normalisation ou doublon normalisé")
    candidat = creer_candidat(proposition, run_id, 1, list(par_id))
    contenu = candidat.model_dump()
    contenu["validation"]["automatic"] = "passed"
    return CasSynthetique.model_validate(contenu)
