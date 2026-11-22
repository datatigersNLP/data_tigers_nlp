"""Mesures descriptives du site après #164 (A2, résultats par fiche ; A3, zone grise), sur le lot de test.

Aucune décision n'en dépend : A1 (encodeur ajusté) a été décidé selon le protocole 05 et son amendement A1 ; le seuil
et la borne de la zone grise viennent du CDTN, fixés avant toute lecture du test (cdtn_seuil.py). Ce script ne fait
que décrire ce que voit un visiteur, avec les mêmes questions, les mêmes vecteurs du navigateur et la même règle de
pertinence (D4) que la mesure de A1.

Configurations comparées :
- site_avant : encodeur de base servi jusqu'au 15/11/2026, 5 passages, seuil de base ;
- ajuste_5 : encodeur ajusté, 5 passages (effet de A1 seul) ;
- ajuste_10 : encodeur ajusté, 10 passages regroupés par fiche (A1 et A2), seuil et zone grise de l'ajusté.

Contrôles préalables : les métriques de site_avant redonnent celles du notebook 03 (43,8 % au passage, 83,6 % à la
fiche, 72 questions sur 73 conservées, 9 sur 24 rejetées) ; celles de ajuste_5 et l'AUC redonnent la mesure de A1.

    HF_HUB_OFFLINE=1 python scripts/evaluation/mesures_site_164.py     # deux exécutions identiques exigées
Sortie écrite une seule fois dans data/evaluation/ajustement_05/site_164_<horodatage>.json (non versionné).
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
if str(RACINE / "scripts/evaluation") not in sys.path:
    sys.path.insert(0, str(RACINE / "scripts/evaluation"))

import ajustement_05 as a5  # noqa: E402
from metrics import noninferiority_tango, paired_success_test, proportion_ci  # noqa: E402
from pertinence import IndexPertinence  # noqa: E402

NB03 = RACINE / "data/evaluation/notebook03"
SEUIL_BASE = NB03 / "seuil_cdtn.json"
SEUIL_AJUSTE = NB03 / "seuil_cdtn_ajuste.json"
ZONE_GRISE = NB03 / "zone_grise_ajuste.json"
INDEX_SITE_AJUSTE = RACINE / "front/public/index_ajuste/index_m2.f32"
# valeurs servies par le site (front/src/recherche/moteur.js, ABSTENTION et ABSTENTION_AJUSTE)
SEUIL_BASE_SITE = 0.8559679388999939
SEUIL_AJUSTE_SITE = 0.7682965993881226
BORNE_SITE = 0.8140405416488647
INDEX_AJUSTE_SHA256 = "dc8daa7243bec30c28ea4830daeb10970bcd3de8d819f71a602b5d0b306ea8f1"
# résultats publiés à reproduire : notebook 03 (13/10/2026) et mesure de A1 (15/11/2026, #164)
ATTENDU = {"site_avant": {"passage": 32, "fiche": 61}, "ajuste_5": {"passage": 46},
           "abstention_base": {"conservees": 72, "rejetees": 9}, "auc_ajuste": 0.865}


class ErreurSite164(RuntimeError):
    """Précondition non remplie : rien n'est écrit."""


def classements(vecteurs: np.ndarray, matrice: np.ndarray, k: int) -> list[list[int]]:
    """k premiers passages par produit scalaire, à score égal dans l'ordre de l'index (tri stable, comme le site)."""
    return [np.argsort(-(matrice @ v), kind="stable")[:k].tolist() for v in vecteurs]


def fiches_affichees(top: list[int], url_passage: list[str]) -> list[str]:
    """Fiches distinctes, dans l'ordre de leur meilleur passage (regrouperParFiche du site)."""
    vues = []
    for i in top:
        if url_passage[i] not in vues:
            vues.append(url_passage[i])
    return vues


def proportion(succes: list[bool], groupes: list | None) -> dict:
    """Proportion et intervalle de Wilson à 95 %, corrigé de l'effet de plan si des groupes sont donnés."""
    n, k = len(succes), int(sum(succes))
    bas, haut = proportion_ci(succes, groups=groupes, method="wilson") if groupes else proportion_ci(succes)
    return {"succes": k, "n": n, "proportion": k / n, "ic95": [bas, haut]}


def configuration(vecteurs, matrice, k, pertinents, fiches_pertinentes, url_passage, groupes) -> dict:
    tops = classements(vecteurs, matrice, k)
    passage = [bool(set(t) & p) for t, p in zip(tops, pertinents)]
    affichees = [fiches_affichees(t, url_passage) for t in tops]
    fiche = [bool(set(a) & f) for a, f in zip(affichees, fiches_pertinentes)]
    nb = np.array([len(a) for a in affichees])
    return {"k": k, "rappel_passage": proportion(passage, groupes), "rappel_fiche": proportion(fiche, groupes),
            "fiches_affichees": {"moyenne": float(nb.mean()), "mediane": float(np.median(nb)), "min": int(nb.min()),
                                 "max": int(nb.max())},
            "_passage": passage, "_fiche": fiche}


def ecart(sa: list[bool], sb: list[bool], groupes: list) -> dict:
    t = noninferiority_tango(sa, sb, margin=0.0, groups=groupes, level=0.95)
    m = paired_success_test(sa, sb, groups=groupes)
    return {"ecart": t["difference"], "ic95_tango": list(t["ci_score"]), "effet_de_plan": t["design_effect"],
            "gagnees": t["n_10_A_only"], "perdues": t["n_01_B_only"], "p_mcnemar": m["p_value"]}


def lire_seuils() -> dict:
    sb = json.loads(SEUIL_BASE.read_text(encoding="utf-8"))["seuil"]
    sa = json.loads(SEUIL_AJUSTE.read_text(encoding="utf-8"))["seuil"]
    z = json.loads(ZONE_GRISE.read_text(encoding="utf-8"))
    if (sb, sa, z["borne_haute"], z["seuil"]) != (SEUIL_BASE_SITE, SEUIL_AJUSTE_SITE, BORNE_SITE, SEUIL_AJUSTE_SITE):
        raise ErreurSite164("Seuils des fichiers différents de ceux servis par le site")
    return {"base": sb, "ajuste": sa, "borne": z["borne_haute"],
            "empreintes": {p.name: a5.sha256_fichier(p) for p in (SEUIL_BASE, SEUIL_AJUSTE, ZONE_GRISE)}}


def mesurer() -> dict:
    import mesure
    empreintes = a5.verifier_empreintes({"vecteurs_notebook03", "q8_ajuste", "q8_base"})
    if a5.sha256_fichier(INDEX_SITE_AJUSTE) != INDEX_AJUSTE_SHA256 or \
            INDEX_SITE_AJUSTE.read_bytes() != a5.INDEX_AJUSTE.read_bytes():
        raise ErreurSite164("Index ajusté du site différent de celui de la mesure de A1")
    seuils = lire_seuils()
    table, index = a5.table_et_index_site()
    matrices = {"base": index.matrice, "ajuste": a5.charger_index_ajuste()}
    vecteurs = {"base": a5.charger_vecteurs(a5.VECTEURS_NB03, None),
                "ajuste": a5.charger_vecteurs(a5.VECTEURS / "vecteurs_navigateur_ajuste.json", "ajuste")}

    questions = mesure.lire_jeu("test")
    corpus = [q for q in questions if q["type"] == "dans_corpus"]
    hors = [q for q in questions if q["type"] == "hors_corpus"]
    index_p = IndexPertinence(table.texte.tolist())
    url_passage = [u.rstrip("/") for u in table.url]
    pertinents = [set(index_p.pertinents(q["extrait"])) for q in corpus]
    fiches_pertinentes = [{url_passage[i] for i in p} for p in pertinents]
    groupes = [q["fiche"] for q in corpus]

    v = {nom: np.stack([vecteurs[nom][q["id"]] for q in corpus]) for nom in ("base", "ajuste")}
    conf = {"site_avant": configuration(v["base"], matrices["base"], 5, pertinents, fiches_pertinentes, url_passage, groupes),
            "ajuste_5": configuration(v["ajuste"], matrices["ajuste"], 5, pertinents, fiches_pertinentes, url_passage, groupes),
            "ajuste_10": configuration(v["ajuste"], matrices["ajuste"], 10, pertinents, fiches_pertinentes, url_passage,
                                       groupes)}

    # meilleurs scores : questions du corpus et hors corpus, pour chaque encodeur
    meilleur = {nom: {"corpus": [float((matrices[nom] @ vecteurs[nom][q["id"]]).max()) for q in corpus],
                      "hors": [float((matrices[nom] @ vecteurs[nom][q["id"]]).max()) for q in hors]}
                for nom in ("base", "ajuste")}
    s_b, s_a, borne = seuils["base"], seuils["ajuste"], seuils["borne"]
    abstention = {
        "base": {"conservees": proportion([x >= s_b for x in meilleur["base"]["corpus"]], groupes),
                 "rejetees": proportion([x < s_b for x in meilleur["base"]["hors"]], None)},
        "ajuste": {"conservees": proportion([x >= s_a for x in meilleur["ajuste"]["corpus"]], groupes),
                   "rejetees": proportion([x < s_a for x in meilleur["ajuste"]["hors"]], None),
                   "auc": a5.auc(meilleur["ajuste"]["corpus"], meilleur["ajuste"]["hors"])},
    }
    zone_corpus = [s_a <= x < borne for x in meilleur["ajuste"]["corpus"]]
    zone_hors = [s_a <= x < borne for x in meilleur["ajuste"]["hors"]]
    fiche10 = conf["ajuste_10"]["_fiche"]
    au_dessus = [x >= borne for x in meilleur["ajuste"]["corpus"]]
    zone = {"corpus": proportion(zone_corpus, groupes), "hors_corpus": proportion(zone_hors, None),
            # parmi les questions du corpus : la zone grise signale-t-elle des résultats moins bons ?
            "rappel_fiche_10_en_zone_grise": {"succes": sum(f for f, z in zip(fiche10, zone_corpus) if z),
                                              "n": sum(zone_corpus)},
            "rappel_fiche_10_au_dessus_de_la_borne": {"succes": sum(f for f, a in zip(fiche10, au_dessus) if a),
                                                      "n": sum(au_dessus)},
            # parmi les questions affichées sans avertissement ni refus, combien sont hors corpus
            "hors_corpus_au_dessus_de_la_borne": sum(x >= borne for x in meilleur["ajuste"]["hors"])}

    controles = {
        "site_avant_passage": conf["site_avant"]["rappel_passage"]["succes"] == ATTENDU["site_avant"]["passage"],
        "site_avant_fiche": conf["site_avant"]["rappel_fiche"]["succes"] == ATTENDU["site_avant"]["fiche"],
        "ajuste_5_passage": conf["ajuste_5"]["rappel_passage"]["succes"] == ATTENDU["ajuste_5"]["passage"],
        "abstention_base": (abstention["base"]["conservees"]["succes"], abstention["base"]["rejetees"]["succes"])
                           == (ATTENDU["abstention_base"]["conservees"], ATTENDU["abstention_base"]["rejetees"]),
        "auc_ajuste": round(abstention["ajuste"]["auc"], 3) == ATTENDU["auc_ajuste"],
        "effectifs": (len(corpus), len(hors)) == (73, 24),
    }
    if not all(controles.values()):
        raise ErreurSite164(f"Contrôles de reproduction non conformes : {controles}")

    ecarts = {"fiche_ajuste_10_contre_site_avant": ecart(conf["ajuste_10"]["_fiche"], conf["site_avant"]["_fiche"], groupes),
              "fiche_ajuste_10_contre_ajuste_5": ecart(conf["ajuste_10"]["_fiche"], conf["ajuste_5"]["_fiche"], groupes),
              "passage_ajuste_10_contre_site_avant": ecart(conf["ajuste_10"]["_passage"], conf["site_avant"]["_passage"],
                                                           groupes)}
    for c in conf.values():
        c.pop("_passage"), c.pop("_fiche")
    return {"lot": "test", "questions_corpus": len(corpus), "questions_hors_corpus": len(hors),
            "fiches_du_lot": len(set(groupes)), "empreintes": {**empreintes, **seuils.pop("empreintes"),
                                                               "index_ajuste_site": INDEX_AJUSTE_SHA256},
            "seuils": seuils, "controles": controles, "configurations": conf, "ecarts": ecarts,
            "abstention": abstention, "zone_grise": zone}


def main() -> int:
    contenu = mesurer()
    precedent = sorted(a5.SORTIES.glob("site_164_*.json"))
    horodatage = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    chemin = a5.SORTIES / f"site_164_{horodatage}.json"
    empreinte = a5.ecrire_une_fois(chemin, contenu)
    if precedent:
        identique = json.loads(precedent[-1].read_text(encoding="utf-8")) == json.loads(chemin.read_text(encoding="utf-8"))
        print(f"seconde exécution : contenu {'identique' if identique else 'DIFFÉRENT'} de {precedent[-1].name}")
        if not identique:
            raise ErreurSite164("Deux exécutions différentes : résultat non retenu")
    print(f"{chemin.relative_to(RACINE)} SHA-256 {empreinte}")
    print(json.dumps({k: v for k, v in contenu.items() if k != "empreintes"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
