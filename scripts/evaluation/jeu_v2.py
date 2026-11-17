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


def feuilles_juge(nombre: int = 2) -> dict:
    """Feuilles de la consigne J : les questions qui passent les contrôles mécaniques, réparties en lots."""
    candidats = {c["passage_id"]: c for c in json.loads((TRAVAIL / "candidats.json").read_text(encoding="utf-8"))}
    items = [r for r in json.loads((TRAVAIL / "controles_mecaniques.json").read_text(encoding="utf-8"))
             if not r["motifs_mecaniques"]]
    entrees = [{"passage_id": r["passage_id"], "passage": candidats[r["passage_id"]]["entete"] + "\n"
                + candidats[r["passage_id"]]["texte"], "question": r["question"], "extrait": r["extrait"]} for r in items]
    (TRAVAIL / "juge").mkdir(exist_ok=True)
    taille = -(-len(entrees) // nombre)
    for k in range(nombre):
        ecrire(TRAVAIL / "juge" / f"feuille_j_{k + 1}.json", entrees[k * taille:(k + 1) * taille])
    return {"entrees": len(entrees), "feuilles": nombre}


def contexte_hors_corpus(fichier: Path) -> dict:
    """Consigne V : pour chaque question hors corpus candidate, les 10 premiers passages de la fusion RRF
    de l'E5 de base et de BM25 V3 (configuration de la #138, sans reclasseur)."""
    for sous in ("scripts/rag", "scripts/recuperation"):
        sys.path.insert(0, str(RACINE / sous))
    import rag
    import recuperation as rc
    from lexical_baselines import BM25Retriever
    questions = json.loads(fichier.read_text(encoding="utf-8"))
    index = rag.charger_index()
    table = rc.charger_passages_m2(index)
    textes = rc.textes_lexicaux(table)
    bm25 = BM25Retriever(stopwords_variant="snowball_no_negation", stemming="french").fit(
        textes, doc_ids=table.passage_id.tolist())
    e5 = rag.charger_encodeur()
    entrees = []
    for q in questions:
        dense = rc.classement(rag.encoder_question(e5, q) @ index.matrice.T)[:100].tolist()
        lexical = rc.classement(bm25.score_matrix([q])[0], positifs=True)[:100].tolist()
        tete = rc.fusion_rrf([dense, lexical])[:10]
        entrees.append({"question": q, "passages": [{"passage_id": table.passage_id.iloc[i], "texte": textes[i]}
                                                    for i in tete]})
    (TRAVAIL / "juge").mkdir(exist_ok=True)
    ecrire(TRAVAIL / "juge" / "feuille_v.json", entrees)
    return {"questions": len(entrees)}


ACCEPTE_REPOND = {"oui", "partiel"}
HORS_CORPUS_RETENUES = 40
HORS_CORPUS_MIN = 30
GENERATEUR = "Claude Opus 5.5 (sous-agent, contexte neuf)"
JUGE = "Claude Fable 5.2 (sous-agent, contexte neuf)"
COLONNES = ["id", "lot", "type", "theme", "question", "url", "extrait", "redacteur", "double_annotation", "remarque",
            "passage_id"]


def lire_json(chemin: Path):
    return json.loads(chemin.read_text(encoding="utf-8"))


def forme_valide(question: str) -> bool:
    q = question.strip()
    return LONGUEUR[0] <= len(q) <= LONGUEUR[1] and q.endswith("?") and q.count("?") == 1 and not META.search(q)


def assembler() -> dict:
    """Jeu final selon les sections 3 et 4 du protocole 10 ; refuse tout désalignement entre fichiers."""
    sorties = TRAVAIL / "sorties"
    candidats = lire_json(TRAVAIL / "candidats.json")
    controles = {r["passage_id"]: r for r in lire_json(TRAVAIL / "controles_mecaniques.json")}
    feuilles = [lire_json(TRAVAIL / "juge" / f"feuille_j_{k}.json") for k in (1, 2)]
    verdicts = [lire_json(sorties / f"verdicts_j_{k}.json") for k in (1, 2)]
    juge = {}
    for feuille, v in zip(feuilles, verdicts):
        if [e["passage_id"] for e in feuille] != [x["passage_id"] for x in v]:
            raise ErreurJeuV2("Verdicts du juge non alignés sur leur feuille")
        juge.update({x["passage_id"]: x for x in v})
    if len(controles) != len(candidats):
        raise ErreurJeuV2("Contrôles mécaniques incomplets")

    def accepte(c) -> tuple[bool, str]:
        r = controles[c["passage_id"]]
        if r["motifs_mecaniques"]:
            return False, "contrôle mécanique : " + ", ".join(r["motifs_mecaniques"])
        j = juge[c["passage_id"]]
        ok = (j["comprehensible_seule"] == "oui" and j["repond"] in ACCEPTE_REPOND and j["extrait_repond"] == "oui")
        return ok, f"juge : compréhensible {j['comprehensible_seule']}, répond {j['repond']}, extrait {j['extrait_repond']}"

    lignes, journal = [], []
    for url in sorted({c["url"] for c in candidats}):
        retenus = 0
        for c in sorted((c for c in candidats if c["url"] == url), key=lambda c: c["rang"]):
            ok, motif = accepte(c)
            garde = ok and retenus < RETENUS_PAR_FICHE
            journal.append({"passage_id": c["passage_id"], "rang": c["rang"], "accepte": ok, "retenu": garde, "motif": motif})
            if garde:
                retenus += 1
                r = controles[c["passage_id"]]
                lignes.append({"lot": "test", "type": "dans_corpus", "theme": c["titre_fiche"], "question": r["question"],
                               "url": url, "extrait": r["extrait"], "redacteur": GENERATEUR, "double_annotation": "non",
                               "remarque": f"rang {c['rang']} ; {motif} ({JUGE})", "passage_id": c["passage_id"]})
    generees = lire_json(sorties / "hors_corpus_generateur.json")
    verifs = lire_json(sorties / "verdicts_v_1.json") + lire_json(sorties / "verdicts_v_2.json")
    if [v["question"] for v in verifs] != generees:
        raise ErreurJeuV2("Verdicts hors corpus non alignés sur les questions générées")
    hors = [q for q, v in zip(generees, verifs) if v["un_passage_repond"] == "non" and forme_valide(q)]
    if len(hors) < HORS_CORPUS_MIN:
        raise ErreurJeuV2(f"{len(hors)} questions hors corpus retenues, moins de {HORS_CORPUS_MIN} : second lot requis")
    for q in hors[:HORS_CORPUS_RETENUES]:
        lignes.append({"lot": "test", "type": "hors_corpus", "theme": "", "question": q, "url": "", "extrait": "",
                       "redacteur": GENERATEUR, "double_annotation": "non",
                       "remarque": f"aucun des 10 premiers passages de la fusion ne répond ({JUGE})", "passage_id": ""})
    for k, l in enumerate(lignes, start=1):
        l["id"] = f"V{k:03d}"
    SORTIE.mkdir(parents=True, exist_ok=True)
    with (SORTIE / "questions_v2.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES)
        w.writeheader()
        w.writerows([{k: l[k] for k in COLONNES} for l in lignes])
    ecrire(TRAVAIL / "journal_selection.json", journal)
    entrees = sorted(p for p in TRAVAIL.rglob("*.json") if p.parent.name in ("lots", "sorties", "juge")) + \
        [TRAVAIL / "candidats.json", TRAVAIL / "controles_mecaniques.json", TRAVAIL / "journal_selection.json"]
    manifeste = {"protocole": "docs/etudes/evaluation/10_protocole_jeu_v2.md",
                 "sha256_protocole": sha256(RACINE / "docs/etudes/evaluation/10_protocole_jeu_v2.md"),
                 "questions_v2_csv": sha256(SORTIE / "questions_v2.csv"),
                 "fichiers_de_travail": {str(p.relative_to(TRAVAIL)): sha256(p) for p in entrees}}
    ecrire(SORTIE / "manifeste.json", manifeste)
    corpus = [l for l in lignes if l["type"] == "dans_corpus"]
    par_fiche = {}
    for l in corpus:
        par_fiche[l["url"]] = par_fiche.get(l["url"], 0) + 1
    return {"dans_corpus": len(corpus), "hors_corpus": len(lignes) - len(corpus), "fiches": len(par_fiche),
            "fiches_a_une_question": sum(v == 1 for v in par_fiche.values()),
            "candidats_acceptes": sum(j["accepte"] for j in journal), "hors_corpus_disponibles": len(hors)}


def recouvrement() -> dict:
    """Indice de Jaccard question-extrait, jeu v2 contre jeu v1 (questions du corpus), section 3 du protocole."""
    import statistics
    v1 = [r for r in lire_jeu_v1() if r["type"] == "dans_corpus" and r["extrait"].strip()]
    v2 = [r for r in csv.DictReader((SORTIE / "questions_v2.csv").open(encoding="utf-8")) if r["type"] == "dans_corpus"]
    j1 = [jaccard(r["question"], r["extrait"]) for r in v1]
    j2 = [jaccard(r["question"], r["extrait"]) for r in v2]
    res = {"v1": {"n": len(j1), "mediane": statistics.median(j1), "moyenne": statistics.fmean(j1)},
           "v2": {"n": len(j2), "mediane": statistics.median(j2), "moyenne": statistics.fmean(j2)}}
    ecrire(TRAVAIL / "recouvrement.json", res)
    return res


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sous = p.add_subparsers(dest="commande", required=True)
    sous.add_parser("tirer")
    c = sous.add_parser("controler")
    c.add_argument("fichiers", nargs="+", type=Path)
    sous.add_parser("feuilles_juge")
    h = sous.add_parser("contexte_hors_corpus")
    h.add_argument("fichier", type=Path)
    sous.add_parser("assembler")
    sous.add_parser("recouvrement")
    a = p.parse_args(argv)
    if a.commande in ("assembler", "recouvrement"):
        print(json.dumps(assembler() if a.commande == "assembler" else recouvrement(), ensure_ascii=False, indent=1))
        return 0
    if a.commande == "tirer":
        print(json.dumps(tirer(), ensure_ascii=False, indent=1))
    elif a.commande == "controler":
        print(json.dumps(controler(a.fichiers), ensure_ascii=False, indent=1))
    elif a.commande == "feuilles_juge":
        print(json.dumps(feuilles_juge(), ensure_ascii=False, indent=1))
    elif a.commande == "contexte_hors_corpus":
        print(json.dumps(contexte_hors_corpus(a.fichier), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
