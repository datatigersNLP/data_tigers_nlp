"""Jeu de questions v2, synthétique (#171, protocole 10).

    python scripts/evaluation/jeu_v2.py tirer        # candidats et lots pour les générateurs
    python scripts/evaluation/jeu_v2.py controler <sorties.json> [...]   # contrôles mécaniques des questions générées
    python scripts/evaluation/jeu_v2.py assembler    # jeu final, une fois les verdicts des juges enregistrés

Les règles sont celles du protocole 10 (`docs/etudes/evaluation/10_protocole_jeu_v2.md`), figé avant toute génération.
Les fichiers de travail vont dans `data/evaluation/jeu_v2/` (non versionné) ; le jeu final dans `evaluation/questions_v2/`.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "scripts" / "evaluation"))

import pertinence  # noqa: E402  (règle D4, inchangée)

MANIFESTE_M2 = RACINE / "data" / "decoupage" / "passages" / "manifeste.json"
JEU_V1 = RACINE / "evaluation" / "questions" / "questions_annotees.csv"
SHA256_JEU_V1 = "807498144fec46722ffab045a87c191b6282a86300799976869d4d6c1755fb35"
TRAVAIL = RACINE / "data" / "evaluation" / "jeu_v2"
SORTIE = RACINE / "evaluation" / "questions_v2"

GRAINE = (20261117, 171)       # flux distinct de celui du protocole 09 (default_rng(20261117))
CANDIDATS_PAR_FICHE = 3
RETENUS_PAR_FICHE = 2
TOKENS_MIN = 40
LONGUEUR = (25, 220)
JACCARD_MAX = 0.40
META = re.compile(r"\b(selon|d['’]après|dans)\s+(ce|cet|cette|le|la|les)\s+(texte|extrait|passage|fiche|document|article)s?\b"
                  r"(?!\s+(de|du|des)\b)", re.I)


class ErreurJeuV2(RuntimeError):
    pass


def sha256(chemin: Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def mots(texte: str) -> set[str]:
    texte = unicodedata.normalize("NFC", texte.lower())
    return set(re.findall(r"[0-9a-zà-ÿœæ]+", texte))


def jaccard(a: str, b: str) -> float:
    x, y = mots(a), mots(b)
    return len(x & y) / len(x | y) if x | y else 0.0


def lire_jeu_v1() -> list[dict]:
    if sha256(JEU_V1) != SHA256_JEU_V1:
        raise ErreurJeuV2("Empreinte du jeu v1 différente de celle du verrou")
    return list(csv.DictReader(JEU_V1.open(encoding="utf-8")))


def table_m2():
    import pandas as pd
    description = json.loads(MANIFESTE_M2.read_text(encoding="utf-8"))["methodes"]["m2"]
    chemin = RACINE / description["fichier"]
    if sha256(chemin) != description["sha256_fichier"]:
        raise ErreurJeuV2("passages_m2.parquet : empreinte différente du manifeste")
    return pd.read_parquet(chemin)


def fiches_de_test(jeu_v1: list[dict]) -> list[str]:
    fiches = sorted({r["url"] for r in jeu_v1 if r["lot"] == "test" and r["type"] == "dans_corpus"})
    if len(fiches) != 61:
        raise ErreurJeuV2(f"{len(fiches)} fiches de test au lieu de 61")
    return fiches


def tirer() -> dict:
    import numpy as np
    jeu_v1, table = lire_jeu_v1(), table_m2()
    rng = np.random.default_rng(list(GRAINE))
    candidats = []
    for url in fiches_de_test(jeu_v1):
        eligibles = table[(table.url == url) & (table.n_tokens >= TOKENS_MIN)]
        ordre = rng.permutation(len(eligibles))[:CANDIDATS_PAR_FICHE]
        if len(ordre) < CANDIDATS_PAR_FICHE:
            raise ErreurJeuV2(f"Moins de {CANDIDATS_PAR_FICHE} passages éligibles : {url}")
        for rang, i in enumerate(ordre, start=1):
            p = eligibles.iloc[int(i)]
            candidats.append({"rang": rang, "passage_id": p.passage_id, "url": url, "titre_fiche": p.titre_fiche,
                              "entete": p.entete, "texte": p.texte, "n_tokens": int(p.n_tokens)})
    TRAVAIL.mkdir(parents=True, exist_ok=True)
    (TRAVAIL / "lots").mkdir(exist_ok=True)
    ecrire(TRAVAIL / "candidats.json", candidats)
    for rang in range(1, CANDIDATS_PAR_FICHE + 1):
        lot = [{k: c[k] for k in ("passage_id", "titre_fiche", "entete", "texte")} for c in candidats if c["rang"] == rang]
        ecrire(TRAVAIL / "lots" / f"rang_{rang}.json", lot)
    titres = sorted(set(table.titre_fiche))
    ecrire(TRAVAIL / "lots" / "titres_fiches.json", titres)
    return {"candidats": len(candidats), "fiches": len({c["url"] for c in candidats}), "titres": len(titres),
            "empreintes": {p.name: sha256(p) for p in sorted((TRAVAIL / "lots").glob("*.json"))}}


def ecrire(chemin: Path, contenu) -> None:
    chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def normaliser_espaces(texte: str) -> str:
    return re.sub(r"\s+", " ", texte).strip()


def controle_mecanique(question: str, extrait: str, texte_passage: str, questions_v1: list[str]) -> list[str]:
    """Motifs de rejet mécaniques (protocole 10, section 3) ; liste vide si la question passe."""
    motifs = []
    q = question.strip()
    if not LONGUEUR[0] <= len(q) <= LONGUEUR[1]:
        motifs.append("longueur")
    if not q.endswith("?") or q.count("?") != 1:
        motifs.append("point_interrogation")
    if META.search(q):
        motifs.append("renvoi_au_texte")
    if normaliser_espaces(extrait) not in normaliser_espaces(texte_passage):
        motifs.append("extrait_non_verbatim")
    elif not pertinence.est_pertinent(extrait, texte_passage):
        motifs.append("extrait_non_reconnu_par_D4")
    if max((jaccard(q, v) for v in questions_v1), default=0.0) > JACCARD_MAX:
        motifs.append("proche_jeu_v1")
    return motifs


def controler(fichiers: list[Path]) -> dict:
    candidats = {c["passage_id"]: c for c in json.loads((TRAVAIL / "candidats.json").read_text(encoding="utf-8"))}
    questions_v1 = [r["question"] for r in lire_jeu_v1()]
    resultats = []
    for f in fichiers:
        for item in json.loads(f.read_text(encoding="utf-8")):
            c = candidats.get(item.get("passage_id"))
            if c is None:
                raise ErreurJeuV2(f"Passage inconnu dans {f.name} : {item.get('passage_id')}")
            motifs = controle_mecanique(item["question"], item["extrait"], c["texte"], questions_v1)
            resultats.append({**item, "rang": c["rang"], "url": c["url"], "motifs_mecaniques": motifs})
    ecrire(TRAVAIL / "controles_mecaniques.json", resultats)
    return {"questions": len(resultats), "rejetees": sum(bool(r["motifs_mecaniques"]) for r in resultats)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sous = p.add_subparsers(dest="commande", required=True)
    sous.add_parser("tirer")
    c = sous.add_parser("controler")
    c.add_argument("fichiers", nargs="+", type=Path)
    a = p.parse_args(argv)
    if a.commande == "tirer":
        print(json.dumps(tirer(), ensure_ascii=False, indent=1))
    elif a.commande == "controler":
        print(json.dumps(controler(a.fichiers), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
