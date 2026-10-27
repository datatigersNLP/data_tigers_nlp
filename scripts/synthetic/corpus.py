"""Préparer des sources M2 traçables pour Agent0 Light (#92), sans modèle."""

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import platform
import random
import re
import subprocess
import sys


RACINE = Path(__file__).resolve().parents[2]
DOSSIER_INDEX = RACINE / "front" / "public" / "index"
GRAINE = 20261018
ALGORITHME = "m2-fiches-triees-v1"


class ErreurCorpus(ValueError):
    """Sources absentes, incohérentes ou sélection impossible."""


@dataclass(frozen=True)
class CorpusM2:
    passages: list[dict]
    sha256_entete: str
    sha256_passages: str


def _sha256(octets: bytes) -> str:
    return hashlib.sha256(octets).hexdigest()


def _valider_passages(passages, nombre: int) -> None:
    if not isinstance(passages, list) or len(passages) != nombre:
        raise ErreurCorpus("Nombre réel de passages différent du manifeste")
    identifiants = set()
    champs = ("passage_id", "titre_fiche", "section_titre", "url", "url_citation", "date_maj", "texte")
    for p in passages:
        if not isinstance(p, dict) or any(not isinstance(p.get(c), str) for c in champs):
            raise ErreurCorpus("Passage invalide : sept champs textuels requis")
        if any(not p[c].strip() for c in ("passage_id", "url", "texte")):
            raise ErreurCorpus("Identifiant, URL et texte doivent être non vides")
        if p["passage_id"] in identifiants:
            raise ErreurCorpus("Identifiant de passage dupliqué")
        identifiants.add(p["passage_id"])
        for c in ("chemin", "articles"):
            if not isinstance(p.get(c), list) or any(not isinstance(v, str) for v in p[c]):
                raise ErreurCorpus(f"{c} doit être une liste de textes")


def charger_corpus(dossier: Path | str = DOSSIER_INDEX) -> CorpusM2:
    """Vérifie les deux fichiers JSON ; la matrice et les textes restent inchangés."""
    dossier = Path(dossier)
    try:
        octets_entete = (dossier / "index_m2.json").read_bytes()
        entete = json.loads(octets_entete.decode("utf-8"))
        if not isinstance(entete, dict) or entete.get("format") != "index-e5-v1":
            raise ErreurCorpus("Format de manifeste attendu : index-e5-v1")
        source, meta = entete.get("source"), entete.get("metadonnees")
        if not isinstance(source, dict) or source.get("decoupage") != "m2":
            raise ErreurCorpus("Le découpage source doit être M2")
        if not isinstance(meta, dict) or meta.get("fichier") != "passages_m2.json":
            raise ErreurCorpus("Le manifeste doit désigner passages_m2.json dans ce dossier")
        nombre, empreinte = meta.get("nb_passages"), meta.get("sha256")
        if type(nombre) is not int or nombre < 1:
            raise ErreurCorpus("Nombre de passages strictement positif requis")
        if not isinstance(empreinte, str) or re.fullmatch(r"[0-9a-f]{64}", empreinte) is None:
            raise ErreurCorpus("Empreinte SHA-256 des passages invalide")
        octets_passages = (dossier / "passages_m2.json").read_bytes()
        if _sha256(octets_passages) != empreinte:
            raise ErreurCorpus("Empreinte des passages différente du manifeste ; récupérer les fichiers versionnés")
        passages = json.loads(octets_passages.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ErreurCorpus(f"Lecture des sources impossible : {exc}") from exc
    _valider_passages(passages, nombre)
    return CorpusM2(passages, _sha256(octets_entete), empreinte)


def _par_fiche(corpus: CorpusM2) -> dict[str, list[dict]]:
    groupes = {}
    for passage in sorted(corpus.passages, key=lambda p: p["passage_id"]):
        groupes.setdefault(passage["url"], []).append(passage)
    return groupes


def selectionner(corpus: CorpusM2, nombre: int = 5, graine: int = GRAINE,
                 paires: bool = False) -> list[list[dict]]:
    """Tire des fiches distinctes, puis un passage ou une paire par fiche."""
    if type(nombre) is not int or nombre < 1 or type(graine) is not int or type(paires) is not bool:
        raise ErreurCorpus("Nombre positif, graine entière et option paires booléenne requis")
    groupes = _par_fiche(corpus)
    taille = 2 if paires else 1
    fiches = sorted(url for url, passages in groupes.items() if len(passages) >= taille)
    if nombre > len(fiches):
        raise ErreurCorpus(f"Sélection impossible : {nombre} fiches demandées, {len(fiches)} éligibles")
    tirage = random.Random(graine)
    choisies = tirage.sample(fiches, nombre)
    return [tirage.sample(groupes[url], taille) for url in choisies]


def selectionner_ids(corpus: CorpusM2, identifiants: list[str]) -> list[list[dict]]:
    """Sélection explicite dans l'ordre demandé ; une même fiche est permise."""
    if (not isinstance(identifiants, list) or not identifiants
            or any(not isinstance(i, str) or not i.strip() for i in identifiants)):
        raise ErreurCorpus("Liste non vide d'identifiants requise")
    if len(identifiants) != len(set(identifiants)):
        raise ErreurCorpus("Identifiant demandé plusieurs fois")
    par_id = {p["passage_id"]: p for p in corpus.passages}
    inconnus = [i for i in identifiants if i not in par_id]
    if inconnus:
        raise ErreurCorpus(f"Identifiants inconnus : {', '.join(inconnus)}")
    return [[par_id[i]] for i in identifiants]


def provenance_code() -> dict:
    """Sans copie Git identifiable, refuser de produire un manifeste de sélection."""
    try:
        commit = subprocess.run(["git", "-C", str(RACINE), "rev-parse", "HEAD"],
                                check=True, capture_output=True, text=True).stdout.strip()
        etat = subprocess.run(["git", "-C", str(RACINE), "status", "--porcelain"],
                              check=True, capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ErreurCorpus("Copie Git nécessaire pour tracer le commit du code") from exc
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ErreurCorpus("Commit Git invalide")
    return {"git_commit": commit, "git_dirty": bool(etat.strip()),
            "sha256_corpus_py": _sha256(Path(__file__).read_bytes()),
            "python": platform.python_version()}


def creer_manifeste(corpus: CorpusM2, groupes: list[list[dict]], mode: str,
                    graine: int | None, code: dict) -> dict:
    """Conserve les textes sélectionnés et leurs métadonnées sans les réécrire."""
    return {"format": "agent0-sources-v1", "algorithme": ALGORITHME,
            "mode": mode, "graine": graine, "code": code,
            "corpus": {"sha256_entete": corpus.sha256_entete,
                       "sha256_passages": corpus.sha256_passages,
                       "nb_passages": len(corpus.passages), "nb_fiches": len(_par_fiche(corpus))},
            "groupes": groupes, "ollama_appele": False, "matrice_lue": False}


def enregistrer_manifeste(manifeste: dict, chemin: Path) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("x", encoding="utf-8", newline="\n") as fichier:
        fichier.write(json.dumps(manifeste, ensure_ascii=False, indent=2) + "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check-corpus", action="store_true", help="contrôler les sources sans sélection")
    modes.add_argument("--ids", nargs="+", help="rejouer des identifiants explicites, sans tirage")
    modes.add_argument("--pairs", action="store_true", help="tirer deux passages par fiche")
    parser.add_argument("--count", type=int, help="nombre de fiches à tirer, 5 par défaut")
    parser.add_argument("--seed", type=int, help=f"graine de tirage, {GRAINE} par défaut")
    parser.add_argument("--index-dir", type=Path, default=DOSSIER_INDEX)
    parser.add_argument("--output", type=Path, help="nouveau fichier de manifeste, sans écrasement")
    args = parser.parse_args(argv)
    if (args.check_corpus or args.ids) and (args.count is not None or args.seed is not None):
        parser.error("--count et --seed s'utilisent seulement avec un tirage")
    if args.check_corpus and args.output:
        parser.error("--check-corpus n'écrit pas de sélection")
    try:
        if args.output and args.output.exists():
            raise ErreurCorpus("Le fichier de sortie existe déjà ; choisir un autre nom")
        corpus = charger_corpus(args.index_dir)
        resume = {"statut": "corpus_verifie", "nb_passages": len(corpus.passages),
                  "nb_fiches": len(_par_fiche(corpus)), "sha256_entete": corpus.sha256_entete,
                  "sha256_passages": corpus.sha256_passages, "ollama_appele": False, "matrice_lue": False}
        if not args.check_corpus:
            graine = None if args.ids else (GRAINE if args.seed is None else args.seed)
            mode = "ids" if args.ids else ("paires" if args.pairs else "fiches")
            groupes = (selectionner_ids(corpus, args.ids) if args.ids else selectionner(
                corpus, 5 if args.count is None else args.count, graine, args.pairs))
            manifeste = creer_manifeste(corpus, groupes, mode, graine, provenance_code())
            if args.output:
                enregistrer_manifeste(manifeste, args.output)
            resume.update({"statut": "selection_preparee", "mode": mode, "graine": graine,
                           "code": manifeste["code"], "nombre_groupes": len(groupes),
                           "identifiants": [[p["passage_id"] for p in g] for g in groupes],
                           "output": str(args.output.resolve()) if args.output else None})
    except (ErreurCorpus, OSError) as exc:
        print(f"Préparation refusée : {exc}", file=sys.stderr)
        return 1
    print(json.dumps(resume, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
