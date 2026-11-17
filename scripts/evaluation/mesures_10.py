"""Mesures du protocole 10 (#171, section 7).

    python scripts/evaluation/mesures_10.py famille_a      # volet A : recherche dense servie contre fusion avec BM25 V3

Famille A : D, la recherche dense du site (encodeur ajusté v1, requête q8 encodée dans le navigateur, index fp32) ;
F, la fusion RRF (k = 60, profondeur 100) de D et de BM25 V3. Critère principal : Recall@5 au passage selon D4.
Secondaire : une fiche pertinente parmi les fiches des 10 passages affichés. Règle (section 7) : F est adoptée si son
écart de Recall@5 avec D est positif ou nul sur le jeu v2 et sur le CDTN, et strictement positif sur l'un des deux.

Contrôle de reproduction préalable : D, recalculé ici sur le CDTN, doit redonner question par question le Recall@5
de l'ajusté publié par le protocole 05 (`mesure_20261115T142537Z.json`) ; sinon rien n'est conclu.
Sorties écrites une seule fois dans `data/evaluation/protocole_10/`.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _sous in ("scripts/evaluation", "scripts/rag", "scripts/recuperation"):
    if str(RACINE / _sous) not in sys.path:
        sys.path.insert(0, str(RACINE / _sous))

import ajustement_05 as a5  # noqa: E402  (fonctions du protocole 05, inchangées)
import recuperation as rc  # noqa: E402
from pertinence import IndexPertinence  # noqa: E402

D = RACINE / "data"
JEU_V2 = RACINE / "evaluation" / "questions_v2" / "questions_v2.csv"
SHA256_JEU_V2 = "316d82816e924a8a474653240ce2372e0ec2a85e16870dfd6354f24db521f17f"   # étiquette jeu-questions-v2
VECTEURS = {"jeu_v2": a5.VECTEURS / "vecteurs_jeu_v2_ajuste.json", "cdtn": a5.VECTEURS / "vecteurs_cdtn_mesure_ajuste.json",
            "jeu_v1": a5.VECTEURS / "vecteurs_navigateur_ajuste.json"}
FORMULATIONS_CDTN = D / "evaluation" / "cdtn" / "formulations_mesure.json"
RESULTATS_05 = D / "evaluation" / "ajustement_05" / "mesure_20261115T142537Z.json"
INDEX_SERVI = RACINE / "front" / "public" / "index_ajuste" / "index_m2.f32"
SHA256_INDEX_SERVI = "dc8daa7243bec30c28ea4830daeb10970bcd3de8d819f71a602b5d0b306ea8f1"
PROFONDEUR = 100
AFFICHES = 10
SORTIES = D / "evaluation" / "protocole_10"


class ErreurMesure10(RuntimeError):
    pass


def sha256(chemin: Path) -> str:
    return hashlib.sha256(Path(chemin).read_bytes()).hexdigest()


def lire_jeu_v2() -> list[dict]:
    if sha256(JEU_V2) != SHA256_JEU_V2:
        raise ErreurMesure10("Jeu v2 différent de celui étiqueté jeu-questions-v2")
    return list(csv.DictReader(JEU_V2.open(encoding="utf-8")))


def matrice_ajuste() -> np.ndarray:
    if sha256(INDEX_SERVI) != SHA256_INDEX_SERVI:
        raise ErreurMesure10("Index servi par le site différent de celui du 15 novembre")
    m = a5.charger_index_ajuste()
    if not np.array_equal(m, np.fromfile(INDEX_SERVI, dtype="<f4").reshape(4240, 384)):
        raise ErreurMesure10("Index de mesure du protocole 05 différent de l'index servi")
    return m


def bm25(table):
    from lexical_baselines import BM25Retriever
    return BM25Retriever(stopwords_variant="snowball_no_negation", stemming="french").fit(
        rc.textes_lexicaux(table), doc_ids=table.passage_id.tolist())


def listes_d_et_f(vecteurs: np.ndarray, matrice: np.ndarray, lexical, textes: list[str]) -> tuple[list, list]:
    dense, fusion = [], []
    for v, q in zip(vecteurs, textes):
        d = rc.classement(matrice @ v)[:PROFONDEUR].tolist()
        l = rc.classement(lexical.score_matrix([q])[0], positifs=True)[:PROFONDEUR].tolist()
        dense.append(d)
        fusion.append(rc.fusion_rrf([d, l])[:PROFONDEUR])
    return dense, fusion


def evaluer(listes: list[list[int]], pertinents: list[set], fiches: list[set], url_passage: list[str]) -> dict:
    rangs = [[r for r, i in enumerate(l[:AFFICHES], 1) if i in p] for l, p in zip(listes, pertinents)]
    return {"r1": a5.succes_a(rangs, 1), "r5": a5.succes_a(rangs, 5), "r10": a5.succes_a(rangs, 10),
            "fiche10": [any(url_passage[i] in f for i in l[:AFFICHES]) for l, f in zip(listes, fiches)],
            "mrr10": a5.mrr10(rangs)}


def resume(s: dict) -> dict:
    n = len(s["r5"])
    return {"questions": n, "recall@1": sum(s["r1"]) / n, "recall@5": sum(s["r5"]) / n, "recall@10": sum(s["r10"]) / n,
            "mrr@10": s["mrr10"], "fiche_parmi_les_10_affiches": sum(s["fiche10"]) / n}


def comparer(nom: str, ids: list, vecteurs: np.ndarray, textes: list[str], pertinents: list[set], groupes: list,
             matrice, lexical, url_passage) -> dict:
    fiches = [{url_passage[i] for i in p} for p in pertinents]
    dense, fusion = listes_d_et_f(vecteurs, matrice, lexical, textes)
    sd, sf = evaluer(dense, pertinents, fiches, url_passage), evaluer(fusion, pertinents, fiches, url_passage)
    return {"jeu": nom, "questions": len(ids), "groupes": len(set(groupes)),
            "D": resume(sd), "F": resume(sf),
            "ecart_recall5_F_moins_D": a5.ecart(sf["r5"], sd["r5"], groupes),
            "ecart_fiche10_F_moins_D": a5.ecart(sf["fiche10"], sd["fiche10"], groupes),
            "_r5_D": sd["r5"]}


class PertinenceV2:
    """Écart déclaré au protocole 10, décidé le 17/11 avant tout résultat : D4 (IndexPertinence) exige un extrait d'au
    moins 80 caractères normalisés, que les extraits du jeu v1 respectaient tous. Pour les extraits plus courts du jeu
    v2 (14 sur 121), un passage est pertinent s'il contient l'extrait entier, normalisé avec ou sans les marques de
    liste : plus strict que D4, ce qui évite qu'un fragment commun de quelques mots suffise. Le passage source est
    toujours pertinent, puisque l'extrait y figure mot pour mot."""

    def __init__(self, textes: list[str]):
        from pertinence import LONGUEUR_MINIMALE, normaliser
        self.min, self.normaliser = LONGUEUR_MINIMALE, normaliser
        self.index = IndexPertinence(textes)
        self.textes = {r: [normaliser(t, r) for t in textes] for r in (False, True)}

    def court(self, extrait: str) -> bool:
        return len(self.normaliser(extrait, False)) < self.min

    def pertinents(self, extrait: str) -> set[int]:
        if not self.court(extrait):
            return set(self.index.pertinents(extrait))
        return {i for r in (False, True) for i, t in enumerate(self.textes[r]) if self.normaliser(extrait, r) in t}


def famille_a() -> dict:
    table, _ = a5.table_et_index_site()
    matrice = matrice_ajuste()
    lexical = bm25(table)
    url_passage = [u.rstrip("/") for u in table.url]
    index_p = IndexPertinence(table.texte.tolist())
    res = {"protocole": "10, section 7, famille A", "sha256_protocole": sha256(RACINE / "docs/etudes/evaluation/10_protocole_jeu_v2.md"),
           "jeux": {}}

    # jeu v2, questions du corpus
    corpus = [q for q in lire_jeu_v2() if q["type"] == "dans_corpus"]
    v = a5.charger_vecteurs(VECTEURS["jeu_v2"], "ajuste")
    pv2 = PertinenceV2(table.texte.tolist())
    pertinents = [pv2.pertinents(q["extrait"]) for q in corpus]
    pid = {p: i for i, p in enumerate(table.passage_id)}
    absents = [q["id"] for q, p in zip(corpus, pertinents) if pid[q["passage_id"]] not in p]
    if absents:
        raise ErreurMesure10(f"Passage source non reconnu : {absents}")
    res["pertinence_jeu_v2"] = {"extraits_courts": [q["id"] for q in corpus if pv2.court(q["extrait"])],
                                "passages_pertinents_par_question": {"min": min(map(len, pertinents)),
                                                                     "max": max(map(len, pertinents)),
                                                                     "moyenne": float(np.mean([len(p) for p in pertinents]))}}
    vecteurs_v2 = np.stack([v[q["id"]] for q in corpus])
    res["jeux"]["jeu_v2"] = comparer("jeu_v2", [q["id"] for q in corpus], vecteurs_v2, [q["question"] for q in corpus],
                                     pertinents, [q["url"] for q in corpus], matrice, lexical, url_passage)
    # sensibilité : le seul passage source comme passage pertinent (minorant pur)
    res["jeux"]["jeu_v2_source_seule"] = comparer("jeu_v2_source_seule", [q["id"] for q in corpus], vecteurs_v2,
                                                  [q["question"] for q in corpus], [{pid[q["passage_id"]]} for q in corpus],
                                                  [q["url"] for q in corpus], matrice, lexical, url_passage)

    # CDTN, population du protocole 05 (131 requêtes, 494 formulations)
    pop = json.loads(a5.POPULATION_CDTN.read_text(encoding="utf-8"))
    if sha256(a5.POPULATION_CDTN) != a5.EMPREINTES["population_cdtn"][1]:
        raise ErreurMesure10("Population du CDTN différente de celle du protocole 05")
    textes_cdtn = {q["id"]: q["texte"] for q in json.loads(FORMULATIONS_CDTN.read_text(encoding="utf-8"))["questions"]}
    ids, pert, grp = [], [], []
    for r in pop["requetes"]:
        for f in r["formulations"]:
            ids.append(f["id"]); pert.append(set(r["pertinents"])); grp.append(r["id"])
    vc = a5.charger_vecteurs(VECTEURS["cdtn"], "ajuste")
    cdtn = comparer("cdtn", ids, np.stack([vc[i] for i in ids]), [textes_cdtn[i] for i in ids], pert, grp,
                    matrice, lexical, url_passage)

    # contrôle de reproduction : D sur le CDTN doit redonner le protocole 05, question par question
    publie = json.loads(RESULTATS_05.read_text(encoding="utf-8"))
    r5_publie = publie["cdtn"]["systemes"]["ajuste"]["recall@5"]
    ref = a5.systeme(np.stack([vc[i] for i in ids]), matrice, pert, [{url_passage[i] for i in p} for p in pert], url_passage)
    if cdtn["_r5_D"] != ref["r5"] or abs(cdtn["D"]["recall@5"] - r5_publie) > 1e-12:
        raise ErreurMesure10(f"D ne reproduit pas le protocole 05 sur le CDTN : {cdtn['D']['recall@5']} contre {r5_publie}")
    res["controle_reproduction_05"] = {"cdtn_recall5_ajuste_publie": r5_publie, "recalcule": cdtn["D"]["recall@5"],
                                       "identique_question_par_question": True}
    res["jeux"]["cdtn"] = cdtn

    # jeu v1 (lot de test humain), à titre secondaire et descriptif
    import mesure
    v1 = [q for q in mesure.lire_jeu("test") if q["type"] == "dans_corpus"]
    vv1 = a5.charger_vecteurs(VECTEURS["jeu_v1"], "ajuste")
    res["jeux"]["jeu_v1_test"] = comparer("jeu_v1_test", [q["id"] for q in v1], np.stack([vv1[q["id"]] for q in v1]),
                                          [q["question"] for q in v1], [set(index_p.pertinents(q["extrait"])) for q in v1],
                                          [q["fiche"] for q in v1], matrice, lexical, url_passage)
    for j in res["jeux"].values():
        j.pop("_r5_D", None)

    e2, ec = (res["jeux"][k]["ecart_recall5_F_moins_D"]["ecart"] for k in ("jeu_v2", "cdtn"))
    adoptee = e2 >= 0 and ec >= 0 and (e2 > 0 or ec > 0)
    res["decision"] = {"regle": "F adoptée si l'écart de Recall@5 est positif ou nul sur le jeu v2 et le CDTN, et strictement positif sur l'un",
                       "ecart_jeu_v2": e2, "ecart_cdtn": ec, "F_adoptee": adoptee,
                       "F_dite_meilleure_jeu_v2": res["jeux"]["jeu_v2"]["ecart_recall5_F_moins_D"]["ic95_tango"][0] > 0,
                       "F_dite_meilleure_cdtn": res["jeux"]["cdtn"]["ecart_recall5_F_moins_D"]["ic95_tango"][0] > 0}
    SORTIES.mkdir(parents=True, exist_ok=True)
    chemin = SORTIES / f"famille_a_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    print(f"écrit {chemin.name}, SHA-256 {a5.ecrire_une_fois(chemin, res)}")
    return res


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("commande", choices=("famille_a",))
    a = p.parse_args(argv)
    res = famille_a()
    print(json.dumps({k: res[k] for k in ("controle_reproduction_05", "decision")}, ensure_ascii=False, indent=1))
    for nom, j in res["jeux"].items():
        e = j["ecart_recall5_F_moins_D"]
        print(f"{nom:12s} n={j['questions']:4d} | R@5 D {j['D']['recall@5']:.3f} F {j['F']['recall@5']:.3f} | écart {e['ecart']:+.3f} "
              f"[{e['ic95_tango'][0]:+.3f} ; {e['ic95_tango'][1]:+.3f}] F seul {e['ajuste_seul']} D seul {e['base_seule']} p={e['p_mcnemar']:.3f} | "
              f"fiche/10 D {j['D']['fiche_parmi_les_10_affiches']:.3f} F {j['F']['fiche_parmi_les_10_affiches']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
