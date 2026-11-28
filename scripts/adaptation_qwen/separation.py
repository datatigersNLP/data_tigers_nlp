"""Séparation stricte des données d'adaptation du volet B et du lot de test humain (#107, étape 4).

Règle de #107 : aucune donnée d'entraînement ne provient des fiches du lot de test humain (`jeu-questions-v1`), et
aucune question humaine ne sert à l'entraînement. Le contrôle est fait par script, pas par déclaration :
- une fiche est exclue dès qu'une question du corpus du lot de test y renvoie (61 fiches) ;
- un exemple est rejeté si l'un de ses passages, cible ou contexte, vient d'une fiche exclue ;
- un exemple est rejeté si sa question reprend mot pour mot une question du jeu humain, calibration comprise.

Le jeu humain est lu au commit du tag, après contrôle de son empreinte, comme dans la PR #85. Les passages sont ceux de
l'index du site (`front/public/index/passages_m2.json`).

Format d'un exemple, une ligne JSON par exemple : {"id": str, "question": str, "passages": [passage_id, ...]}.
Les autres champs sont ignorés par ce contrôle.

Usage, depuis la racine du dépôt :
    python scripts/adaptation_qwen/separation.py lister               # fiches exclues : nombre et empreinte
    python scripts/adaptation_qwen/separation.py verifier <exemples.jsonl>
"""

import csv
import hashlib
import io
import json
import sys
import unicodedata
from pathlib import Path
from subprocess import run

RACINE = Path(__file__).resolve().parents[2]
JEU_COMMIT = "cdb48c97064de625df61703a9a41e106160e0f50"   # tag jeu-questions-v1
FICHIER_QUESTIONS = "evaluation/questions/questions_annotees.csv"
SHA256_QUESTIONS = "807498144fec46722ffab045a87c191b6282a86300799976869d4d6c1755fb35"
PASSAGES = RACINE / "front" / "public" / "index" / "passages_m2.json"
FICHES_TEST_ATTENDUES = 61


class ErreurSeparation(ValueError):
    pass


def fiche(url):
    """Identifiant d'une fiche : dernier segment de son URL, sans barre finale ni ancre."""
    if not isinstance(url, str) or not url.startswith("https://travail-emploi.gouv.fr/"):
        raise ErreurSeparation(f"URL de fiche inattendue : {url!r}")
    return url.split("#", 1)[0].rstrip("/").rsplit("/", 1)[1]


def normaliser(texte):
    """Comparaison mot pour mot, aux espaces, à la casse et aux formes Unicode près."""
    return " ".join(unicodedata.normalize("NFC", texte).casefold().split())


def lire_jeu(racine=RACINE):
    octets = run(["git", "-C", str(racine), "show", f"{JEU_COMMIT}:{FICHIER_QUESTIONS}"],
                 check=True, capture_output=True).stdout
    if hashlib.sha256(octets).hexdigest() != SHA256_QUESTIONS:
        raise ErreurSeparation("Empreinte du jeu de questions différente de celle du tag jeu-questions-v1")
    return list(csv.DictReader(io.StringIO(octets.decode("utf-8"))))


def fiches_exclues(lignes):
    exclues = {fiche(x["url"]) for x in lignes if x["lot"] == "test" and x["type"] == "dans_corpus"}
    if len(exclues) != FICHES_TEST_ATTENDUES:
        raise ErreurSeparation(f"{len(exclues)} fiches de test au lieu de {FICHES_TEST_ATTENDUES}")
    return exclues


def empreinte_fiches(fiches):
    return hashlib.sha256("\n".join(sorted(fiches)).encode("utf-8")).hexdigest()


def fiche_par_passage(chemin=PASSAGES):
    passages = json.loads(Path(chemin).read_text(encoding="utf-8"))
    return {p["passage_id"]: fiche(p["url"]) for p in passages}


def verifier(exemples, exclues, questions_humaines, fiches):
    """Renvoie la liste des violations ; vide si les exemples respectent la séparation."""
    humaines = {normaliser(q) for q in questions_humaines}
    violations = []
    for n, ex in enumerate(exemples, 1):
        ident = ex.get("id", f"ligne {n}")
        ids = ex.get("passages")
        if not isinstance(ex.get("question"), str) or not isinstance(ids, list) or not ids:
            violations.append((ident, "exemple sans question ou sans passages"))
            continue
        inconnus = [p for p in ids if p not in fiches]
        if inconnus:
            violations.append((ident, f"passages absents de l'index : {inconnus}"))
        touchees = sorted({fiches[p] for p in ids if p in fiches} & exclues)
        if touchees:
            violations.append((ident, f"passages de fiches du lot de test : {touchees}"))
        if normaliser(ex["question"]) in humaines:
            violations.append((ident, "question identique à une question du jeu humain"))
    return violations


def lire_exemples(chemin):
    with open(chemin, encoding="utf-8") as f:
        return [json.loads(ligne) for ligne in f if ligne.strip()]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    lignes = lire_jeu()
    exclues = fiches_exclues(lignes)
    if argv[:1] == ["lister"]:
        print(f"{len(exclues)} fiches exclues, empreinte {empreinte_fiches(exclues)}")
        return 0
    if argv[:1] == ["verifier"] and len(argv) == 2:
        exemples = lire_exemples(argv[1])
        violations = verifier(exemples, exclues, [x["question"] for x in lignes], fiche_par_passage())
        for ident, motif in violations:
            print(f"{ident} : {motif}")
        print(f"{len(exemples)} exemples, {len(violations)} violation(s) ; fiches exclues {empreinte_fiches(exclues)[:16]}")
        return 1 if violations else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
