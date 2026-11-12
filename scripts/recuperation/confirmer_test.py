"""Confirmation unique de la récupération v2 sur le lot de test (protocole 07, #138).

    python scripts/recuperation/confirmer_test.py

Refuse de lire le lot de test si le protocole 07, ce script et le module de récupération ne sont pas committés à
l'identique, si les résultats de la grille diffèrent de ceux inscrits au protocole, ou si la chaîne verrouillée de
la mesure a changé. Avant de calculer la v2, reproduit les rangs publiés par le notebook 03 (E5 fp32 et BM25 V3,
73 questions) et son Recall@5 (33 sur 73) ; s'arrête au moindre écart.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recuperation as rc  # noqa: E402

RACINE = rc.RACINE
sys.path.insert(0, str(RACINE / "scripts" / "adaptation_qwen"))
import rag  # noqa: E402
import separation  # noqa: E402

PROTOCOLE = RACINE / "docs" / "etudes" / "evaluation" / "07_protocole_recuperation_v2.md"
FICHIERS_GELES = (PROTOCOLE, Path(__file__).resolve(), Path(rc.__file__).resolve())
CONFIGURATION = rc.Configuration(k=10, source="rrf", reclasseur="bge-m3", candidats=20)
GRILLE = RACINE / "data" / "evaluation" / "recuperation" / "resultats_grille.json"
SHA256_GRILLE = "2c8619caf32d043cdc7f497ff1ffdf5a52b407190293d23f5f2a625cc020bf4a"
RANGS_NB03 = RACINE / "data" / "evaluation" / "notebook03" / "rangs_mesure.csv"
COLONNES_NB03 = {"e5": "E5 fp32, m2", "bm25": "BM25 de référence (V3)"}
RAPPEL5_NB03 = (33, 73)
PROFONDEUR_NB03 = 10
SORTIE = RACINE / "data" / "evaluation" / "recuperation" / "confirmation"
VERROU_131 = {
    "protocole": "f41366f35c9057c6734489cbfe93fe3d98f17aa9d5eb3d8b507282f7db1b2301",
    "mesure": "d6a4df6a7c1d812abed4f677ca081f4bf40f7c6a10377352e08d127c96215e38",
    "rag": "302dce21a9ce81a67f804016078e7fc2ed2868aaf920693c1b74e19719c7ca9e",
    "generation": "37614842bc9ebbfd3b5f15c6f2d40e4027a11ae9e8b856bbea016db51718b9c7",
    "metrics": "1c9c28f2e0933016b32c1293c50ea1eb2d521bc91f05e69c2a2d4b26cb4f2de4",
    "pertinence": "5acd3aa98b6f035bfddfc724ed187c7dad4842950423a044d5ce2451669151fb",
    "jeu": "807498144fec46722ffab045a87c191b6282a86300799976869d4d6c1755fb35",
    "seuil": "7ba7230e5e8cda87fa1eb8dda2adc01d73c6702d542c27a4e3dc620464939936",
    "index": "2ec45586ab9aaa578f11e271d0ff077c87c105c5de50dcd839e5e9258475b886",
    "passages": "aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d",
}


class ErreurConfirmation(RuntimeError):
    pass


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(RACINE), *args], capture_output=True, text=True)


def verifier_preconditions() -> dict:
    for chemin in FICHIERS_GELES:
        rel = str(chemin.relative_to(RACINE))
        if git("ls-files", "--error-unmatch", rel).returncode != 0:
            raise ErreurConfirmation(f"{rel} n'est pas suivi par git")
        if git("diff", "--quiet", "HEAD", "--", rel).returncode != 0:
            raise ErreurConfirmation(f"{rel} diffère du dernier commit")
    texte = PROTOCOLE.read_text(encoding="utf-8")
    if SHA256_GRILLE not in texte or CONFIGURATION.nom not in texte:
        raise ErreurConfirmation("Le protocole 07 n'inscrit pas la configuration et l'empreinte de la grille")
    if rc.sha256_fichier(GRILLE) != SHA256_GRILLE:
        raise ErreurConfirmation("resultats_grille.json diffère de l'empreinte inscrite au protocole 07")
    if json.loads(GRILLE.read_text(encoding="utf-8"))["choix"]["retenue"] != CONFIGURATION.nom:
        raise ErreurConfirmation("La configuration retenue par la grille n'est pas celle du protocole 07")
    import mesure
    if mesure.empreintes_actuelles(rag.charger_index().entete) != VERROU_131:
        raise ErreurConfirmation("La chaîne verrouillée de la mesure a changé")
    commit = git("rev-parse", "HEAD").stdout.strip()
    return {"commit": commit, "protocole_sha256": rc.sha256_fichier(PROTOCOLE)}


def fiche_url(url: str) -> str:
    return url.split("#", 1)[0].rstrip("/")


def rang_premier(liste, pertinents, profondeur=None) -> float:
    liste = list(liste)[:profondeur] if profondeur else list(liste)
    return next((r for r, i in enumerate(liste, 1) if i in pertinents), math.inf)


def controle_notebook03(questions, rangs_e5, rangs_bm25) -> dict:
    """Compare les rangs recalculés (limités au 10e) à ceux publiés par le notebook 03."""
    with open(RANGS_NB03, encoding="utf-8", newline="") as f:
        publies = {r["question"]: r for r in csv.DictReader(f)}
    ecarts = []
    for q, re5, rbm in zip(questions, rangs_e5, rangs_bm25):
        for cle, rang in (("e5", re5), ("bm25", rbm)):
            attendu = float(publies[q["id"]][COLONNES_NB03[cle]])
            if attendu != rang:
                ecarts.append((q["id"], cle, attendu, rang))
    rappel5 = sum(r <= 5 for r in rangs_e5)
    return {"questions": len(questions), "ecarts": ecarts, "rappel5_e5": [rappel5, len(questions)],
            "conforme": not ecarts and len(publies) == len(questions) and (rappel5, len(questions)) == RAPPEL5_NB03}


def main() -> int:
    from lexical_baselines import BM25Retriever
    from metrics import holm, paired_success_test
    from pertinence import IndexPertinence

    preconditions = verifier_preconditions()
    index = rag.charger_index()
    table = rc.charger_passages_m2(index)
    cles = rc.sections(table)
    questions = [x for x in separation.lire_jeu() if x["lot"] == "test" and x["type"] == "dans_corpus"]
    if len(questions) != 73:
        raise ErreurConfirmation(f"{len(questions)} questions du corpus au lieu de 73")
    groupes = [fiche_url(q["url"]) for q in questions]
    index_p = IndexPertinence(table.texte.tolist())
    pertinents = [set(index_p.pertinents(q["extrait"])) for q in questions]
    url_passage = [u.rstrip("/") for u in table.url]
    fiches_pertinentes = [{url_passage[i] for i in r} for r in pertinents]

    modele = rag.charger_encodeur()
    vecteurs = np.stack([rag.encoder_question(modele, q["question"]) for q in questions])
    listes_e5 = [rc.classement(s)[:100].tolist() for s in vecteurs @ index.matrice.T]
    bm25 = BM25Retriever(stopwords_variant="snowball_no_negation", stemming="french").fit(
        rc.textes_lexicaux(table), doc_ids=table.passage_id.tolist())
    listes_bm25 = [rc.classement(s, positifs=True)[:100].tolist() for s in bm25.score_matrix([q["question"] for q in questions])]

    controle = controle_notebook03(questions,
                                   [rang_premier(l, p, PROFONDEUR_NB03) for l, p in zip(listes_e5, pertinents)],
                                   [rang_premier(l, p, PROFONDEUR_NB03) for l, p in zip(listes_bm25, pertinents)])
    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / "controle_notebook03.json").write_text(json.dumps(controle, ensure_ascii=False, indent=1, default=str) + "\n")
    if not controle["conforme"]:
        print(json.dumps(controle, ensure_ascii=False, indent=1, default=str))
        raise ErreurConfirmation("Le contrôle de la section 7 échoue : aucun calcul de la v2")
    print(f"Contrôle conforme : rangs E5 et BM25 V3 identiques au notebook 03, Recall@5 {controle['rappel5_e5']}")

    reclasseur = rc.Reclasseur(CONFIGURATION.reclasseur)
    textes = rc.textes_lexicaux(table)
    tok = rc.generation.charger_tokeniseur_qwen()
    lignes = []
    for n, q in enumerate(questions):
        candidats = rc.fusion_rrf([listes_e5[n], listes_bm25[n]])[:CONFIGURATION.candidats]
        scores = dict(zip(candidats, reclasseur.scores(q["question"], [textes[i] for i in candidats])))
        ordre_v2 = rc.classement_final(CONFIGURATION, listes_e5[n], listes_bm25[n], scores)
        mesurer = lambda ind: rc.compter_tokens(tok, rc.construire_contexte_v2(q["question"], ind, index.passages))
        contexte_v2, retires = rc.dans_le_budget(rc.groupes_du_contexte(ordre_v2[:CONFIGURATION.k], cles, False), mesurer)
        contexte_r0 = listes_e5[n][:5]
        rel, fiches = pertinents[n], fiches_pertinentes[n]
        lignes.append({
            "question": q["id"], "fiche": groupes[n], "pertinents": len(rel),
            "succes_r0": int(bool(rel & set(contexte_r0))), "succes_v2": int(bool(rel & set(contexte_v2))),
            "succes_fiche_r0": int(any(url_passage[i] in fiches for i in contexte_r0)),
            "succes_fiche_v2": int(any(url_passage[i] in fiches for i in contexte_v2)),
            "r5_v2": int(bool(rel & set(ordre_v2[:5]))),
            "rr10_r0": 1 / r if (r := rang_premier(listes_e5[n], rel, 10)) != math.inf else 0.0,
            "rr10_v2": 1 / r if (r := rang_premier(ordre_v2, rel, 10)) != math.inf else 0.0,
            "tokens_r0": mesurer(contexte_r0), "tokens_v2": mesurer(contexte_v2), "groupes_retires": retires,
        })
    col = lambda c: np.array([l[c] for l in lignes])
    principal = paired_success_test(col("succes_v2").astype(bool), col("succes_r0").astype(bool), groups=groupes)
    sec_r5 = paired_success_test(col("r5_v2").astype(bool), col("succes_r0").astype(bool), groups=groupes)
    sec_fiche = paired_success_test(col("succes_fiche_v2").astype(bool), col("succes_fiche_r0").astype(bool), groups=groupes)
    p_holm = holm([sec_r5["p_value_groups"], sec_fiche["p_value_groups"]])
    resultats = {
        "execute_le": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), **preconditions,
        "configuration": CONFIGURATION.nom, "questions": len(lignes), "fiches": len(set(groupes)),
        "principal": {"rappel_contexte_r0": float(col("succes_r0").mean()), "rappel_contexte_v2": float(col("succes_v2").mean()),
                      **principal, "amelioration_demontree": bool(principal["ci_difference"][0] > 0)},
        "secondaires": {
            "r5_v2_contre_r0": {**sec_r5, "p_holm": p_holm[0]},
            "fiche_contexte": {"r0": float(col("succes_fiche_r0").mean()), "v2": float(col("succes_fiche_v2").mean()),
                               **sec_fiche, "p_holm": p_holm[1]},
            "mrr10": {"r0": float(col("rr10_r0").mean()), "v2": float(col("rr10_v2").mean())},
            "tokens": {"r0_moyenne": float(col("tokens_r0").mean()), "v2_moyenne": float(col("tokens_v2").mean()),
                       "v2_max": int(col("tokens_v2").max()), "questions_coupees": int((col("groupes_retires") > 0).sum())},
        },
        "controle_notebook03": controle,
    }
    with open(SORTIE / "questions.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(lignes)
    (SORTIE / "resultats.json").write_text(json.dumps(resultats, ensure_ascii=False, indent=1, default=float) + "\n")
    print(json.dumps({"principal": resultats["principal"], "secondaires": resultats["secondaires"]},
                     ensure_ascii=False, indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
