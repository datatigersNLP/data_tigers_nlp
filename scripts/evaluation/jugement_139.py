"""Jugement mutualisé du lot de test et métriques à plusieurs passages (#139, protocole 09).

Le protocole `docs/etudes/evaluation/09_protocole_jugement_mutualise.md`, figé avant tout jugement, fixe le vivier, les
contrôles, la consigne, les juges, les règles d'agrégation et de fiabilité, et les mesures. Ce script les applique.

Commandes, depuis la racine du dépôt, environnement de `scripts/evaluation/requirements-lock.txt`, HF_HUB_OFFLINE=1 :
    python scripts/evaluation/jugement_139.py vivier                  # vivier, contrôles, feuilles et étalonnage (une fois)
    python scripts/evaluation/jugement_139.py importer J1 01 <fichier>  # verdicts d'un juge pour un lot (une fois)
    python scripts/evaluation/jugement_139.py etat                    # lots jugés et lots manquants
    python scripts/evaluation/jugement_139.py mesurer                 # deux exécutions identiques exigées
    python scripts/evaluation/jugement_139.py etalonnage <h1.csv> <h2.csv>   # accord avec les jugements humains
Les sorties vont dans data/evaluation/jugement_139/, qui n'est pas versionné ; leurs empreintes sont publiées sur le #139.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import math
import sys
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
if str(ICI) not in sys.path:
    sys.path.insert(0, str(ICI))
import ajustement_05 as a05  # noqa: E402
from metrics import noninferiority_tango, paired_success_test, proportion_ci  # noqa: E402

RACINE = a05.RACINE
D = a05.D
PROTOCOLE_09 = RACINE / "docs/etudes/evaluation/09_protocole_jugement_mutualise.md"
SHA256_PROTOCOLE_09: str | None = "95a825e8bac7f59a8219a0990ce884694e9c52b95c7725ea1b979ac730a32f14"   # gel du 16 novembre 2026, avant le tirage du vivier
SORTIES = D / "evaluation/jugement_139"
CLE = SORTIES / "vivier.json"
FEUILLES = SORTIES / "feuilles"
VERDICTS = SORTIES / "verdicts"
ETALONNAGE = SORTIES / "etalonnage"
MESURE_A1 = D / "evaluation/ajustement_05/mesure_20261115T142540Z.json"
ETATS_B = {"B2": D / "evaluation/volet_b/mesure/apres/B2.jsonl",
           "V1": D / "evaluation/volet_b/chaine_v2/test/apres/V1.jsonl",
           "V2": D / "evaluation/volet_b/chaine_v2/test/apres/V2.jsonl"}
CLASSEMENTS_CDTN = D / "evaluation/recuperation/classements.json"
ENTREES = {
    "mesure_a1": (MESURE_A1, "d35b49365f0c36eea556b3ad847d3cc98975b30f759f1e9f7d122cfe1a992d90"),
    "B2": (ETATS_B["B2"], "dae33de7c521950179724934a8e264e270cff4cdd93f39b8379e0715055e33a1"),
    "V1": (ETATS_B["V1"], "72868e82ab1c20aa4939ae557287ac8eea3db724adad07b0fe70b25fc03580cc"),
    "V2": (ETATS_B["V2"], "78f51dc2c4da34395c6ab82b71eb5f66d6079fd2102e0366e60722ffe37dcd39"),
    "classements_cdtn": (CLASSEMENTS_CDTN, "c183aa20e787146a68bb0864d648c390d9a15cbdd3d21a84e3027c0927b2e3c1"),
    "vecteurs_test_ajuste": (a05.VECTEURS / "vecteurs_navigateur_ajuste.json",
                             "7bbecb8390d0b2f685146ccdb2b40df420c5652f5a92951247e9cfd0fd0a61a8"),
    "vecteurs_cdtn_base": (a05.VECTEURS / "vecteurs_cdtn_mesure_base.json",
                           "4f220399e8cba9677c895babc3d0a4f704eccd1e4aa1857b4cd5315a67bb98b7"),
    "vecteurs_cdtn_ajuste": (a05.VECTEURS / "vecteurs_cdtn_mesure_ajuste.json",
                             "678aae7ff7f8f0c3205288ea026d96db6fa1f9d552c96095bb2dd0b2dd93f1da"),
}
GRAINE = 20261116
GRAINE_ETALONNAGE = 20261117
N_CONTROLES = 40
TAILLE_LOT = 100
N_ETALONNAGE = {"vivier": 80, "positif": 10, "negatif": 10}
TIRAGES = 10_000
JUGES = ("J1", "J2")
VERDICTS_POSSIBLES = ("repond", "en_partie", "ne_repond_pas")
ORDRE = {"ne_repond_pas": 0, "en_partie": 1, "repond": 2}
SENSIBILITE_MIN = 32                 # contrôles positifs jugés repond ou en_partie, sur 40 (80 %)
FAUX_POSITIFS_MAX = 2                # contrôles négatifs jugés repond ou en_partie, sur 40 (5 %)
KAPPA_ETALONNAGE_MIN = 0.6
SYSTEMES_A = ("base", "ajuste")
PROFONDEURS_A = (5, 10)
CONSIGNE = (
    "Chaque paire associe une question de droit du travail, posée comme le ferait un salarié ou un employeur, et un "
    "passage d'une fiche du ministère du Travail (titre de la fiche, chemin de la section, puis texte). Jugez seulement si "
    "ce passage, lu seul, permet de répondre à la question. « répond » : le passage contient l'information qui répond à "
    "la question posée ; une réponse qu'il faut nuancer par des conditions ou des exceptions présentes dans le passage "
    "compte comme une réponse. « en partie » : le passage donne un élément utile de la réponse (une condition, un cas, une "
    "partie d'une liste), mais pas l'essentiel, ou il répond à une question voisine, plus générale ou plus restreinte. "
    "« ne répond pas » : le passage traite d'un autre sujet, ou du même sujet sans donner d'élément de réponse. Ne jugez "
    "ni l'exactitude juridique ni la date du passage, et n'utilisez aucune connaissance extérieure pour compléter un "
    "passage incomplet.")
# Chiffres publiés que le calcul doit redonner sous D4 (protocole 09, section 7)
REPRODUCTION_A = {("base", "succes@5"): 32, ("ajuste", "succes@5"): 46, ("base", "succes@10"): 42,
                  ("ajuste", "succes@10"): 54, ("base", "fiche@5"): 61, ("ajuste", "fiche@5"): 63}
REPRODUCTION_B = {"B2": {"questions": 72, "plafond": 33, "m4": 18}, "V1": {"questions": 73, "plafond": 53, "m4": 24},
                  "V2": {"questions": 73, "plafond": 53, "m4": 27}}


class ErreurJugement(RuntimeError):
    """Précondition ou contrôle non rempli : rien n'est écrit."""


# Outils

def sha256_fichier(chemin: Path) -> str:
    return a05.sha256_fichier(chemin)


def ecrire_une_fois(chemin: Path, contenu) -> str:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    texte = contenu if isinstance(contenu, str) else json.dumps(contenu, ensure_ascii=False, indent=1)
    with open(chemin, "x", encoding="utf-8") as f:
        f.write(texte)
    return sha256_fichier(chemin)


def verifier_gel() -> None:
    if SHA256_PROTOCOLE_09 is None:
        raise ErreurJugement("Protocole 09 non figé : son empreinte n'est pas inscrite")
    if not PROTOCOLE_09.is_file() or sha256_fichier(PROTOCOLE_09) != SHA256_PROTOCOLE_09:
        raise ErreurJugement("Protocole 09 absent ou modifié depuis son gel")


def verifier_entrees() -> dict:
    sortie = {}
    for cle, (chemin, attendue) in ENTREES.items():
        if not chemin.is_file() or sha256_fichier(chemin) != attendue:
            raise ErreurJugement(f"{cle} : fichier absent ou d'empreinte différente ({chemin})")
        sortie[cle] = attendue
    sortie.update(a05.verifier_empreintes({"q8_ajuste", "q8_base", "population_cdtn", "vecteurs_notebook03",
                                           "jugements_cdtn"}))
    return sortie


def kappa(a: list[int], b: list[int], k: int = 3, ponderation: str | None = None) -> float:
    """Kappa de Cohen entre deux listes de classes 0 à k - 1 ; ponderation=None ou "lineaire"."""
    n = len(a)
    if n == 0 or n != len(b):
        raise ValueError("listes vides ou de longueurs différentes")
    o = np.zeros((k, k))
    for x, y in zip(a, b):
        o[x, y] += 1
    return _kappa_table(o, ponderation)


def _kappa_table(o: np.ndarray, ponderation: str | None) -> float:
    k, n = o.shape[0], o.sum()
    i, j = np.indices((k, k))
    w = (i == j).astype(float) if ponderation is None else 1 - np.abs(i - j) / (k - 1)
    e = np.outer(o.sum(1), o.sum(0)) / n
    po, pe = (w * o).sum() / n, (w * e).sum() / n
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def kappa_ic(a: list[int], b: list[int], k: int = 3, ponderation: str | None = None,
             tirages: int = TIRAGES, graine: int = GRAINE) -> list[float]:
    """Intervalle à 95 % par rééchantillonnage des paires (percentiles)."""
    codes = np.asarray(a) * k + np.asarray(b)
    rng = np.random.default_rng(graine)
    valeurs = []
    for _ in range(tirages):
        t = np.bincount(codes[rng.integers(0, len(codes), len(codes))], minlength=k * k).reshape(k, k).astype(float)
        valeurs.append(_kappa_table(t, ponderation))
    v = np.asarray(valeurs)
    v = v[np.isfinite(v)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def ndcg10(classement: list[int], pertinents: set) -> float:
    dcg = sum(1 / math.log2(r + 1) for r, i in enumerate(classement[:10], 1) if i in pertinents)
    idcg = sum(1 / math.log2(r + 1) for r in range(1, min(len(pertinents), 10) + 1))
    return dcg / idcg if idcg else 0.0


def proportion(succes: list[bool], groupes: list) -> dict:
    n, s = len(succes), int(sum(succes))
    bas, haut = proportion_ci(succes, groups=groupes, method="wilson")
    return {"succes": s, "questions": n, "part": s / n, "ic95": [bas, haut]}


def ecart_apparie(sa: list[bool], sb: list[bool], groupes: list) -> dict:
    t = noninferiority_tango(sa, sb, margin=0.0, groups=groupes, level=0.95)
    m = paired_success_test(sa, sb, groups=groupes)
    return {"ecart": t["difference"], "ic95_tango": list(t["ci_score"]), "effet_de_plan": t["design_effect"],
            "a_seul": t["n_10_A_only"], "b_seul": t["n_01_B_only"], "p_mcnemar": m["p_value"]}


# Données du lot de test

def donnees_test() -> dict:
    """Table du site, questions du corpus du lot de test, pertinence D4, classements des deux systèmes, sorties de B."""
    import mesure
    from pertinence import IndexPertinence
    table, index = a05.table_et_index_site()
    if not table.entree_encodeur.str.startswith("passage: ").all():
        raise ErreurJugement("Entrée d'encodeur sans préfixe")
    slug = [mesure.fiche(u) for u in table.url]
    questions = [q for q in mesure.lire_jeu("test") if q["type"] == "dans_corpus"]
    ip = IndexPertinence(table.texte.tolist())
    d4 = {q["id"]: set(ip.pertinents(q["extrait"])) for q in questions}
    matrices = {"base": index.matrice, "ajuste": a05.charger_index_ajuste()}
    vecteurs = {"base": a05.charger_vecteurs(a05.VECTEURS_NB03, None),
                "ajuste": a05.charger_vecteurs(a05.VECTEURS / "vecteurs_navigateur_ajuste.json", "ajuste")}
    classements = {s: {q["id"]: np.argsort(-(matrices[s] @ vecteurs[s][q["id"]]), kind="stable")[:10].tolist()
                       for q in questions} for s in SYSTEMES_A}
    position = {p: i for i, p in enumerate(table.passage_id)}
    etats = {}
    for etat, chemin in ETATS_B.items():
        lignes = {r["id"]: r for r in map(json.loads, chemin.read_text(encoding="utf-8").splitlines())}
        etats[etat] = {q["id"]: {"classe": lignes[q["id"]]["classe"], "appel_modele": lignes[q["id"]]["appel_modele"],
                                 "contexte": [position[p] for p in lignes[q["id"]]["passages"]],
                                 "cites": [position[p] for p in lignes[q["id"]]["passages_cites"]]}
                       for q in questions}
    return {"table": table, "slug": slug, "questions": questions, "d4": d4, "classements": classements, "etats": etats}


def construire_vivier(d: dict) -> dict:
    """(question, passage) -> sources, selon la section 3 du protocole."""
    vivier: dict[tuple[str, int], set] = {}
    for s in SYSTEMES_A:
        for k in PROFONDEURS_A:
            for q in d["questions"]:
                top = d["classements"][s][q["id"]][:k]
                if not set(top) & d["d4"][q["id"]]:
                    for i in top:
                        vivier.setdefault((q["id"], i), set()).add(f"A_{s}@{k}")
    for etat, sorties in d["etats"].items():
        for q in d["questions"]:
            o = sorties[q["id"]]
            if o["classe"] == "erreur_technique":
                continue
            if o["contexte"] and not set(o["contexte"]) & d["d4"][q["id"]]:
                for i in o["contexte"]:
                    vivier.setdefault((q["id"], i), set()).add(f"B_{etat}_contexte")
            if o["classe"] == "reponse_citee" and not set(o["cites"]) & d["d4"][q["id"]]:
                for i in o["cites"]:
                    vivier.setdefault((q["id"], i), set()).add(f"B_{etat}_cite")
    return vivier


def tirer_controles(d: dict, vivier: dict, rng: np.random.Generator) -> tuple[list, list]:
    qs = d["questions"]
    positifs = []
    for k in rng.choice(len(qs), N_CONTROLES, replace=False).tolist():
        p = sorted(d["d4"][qs[k]["id"]])
        positifs.append((qs[k]["id"], p[int(rng.integers(len(p)))]))
    negatifs = []
    for k in rng.choice(len(qs), N_CONTROLES, replace=False).tolist():
        q = qs[k]
        exclues = {q["fiche"]} | {d["slug"][i] for i in d["d4"][q["id"]]}
        candidats = [i for i in range(len(d["slug"])) if d["slug"][i] not in exclues and (q["id"], i) not in vivier]
        negatifs.append((q["id"], candidats[int(rng.integers(len(candidats)))]))
    return positifs, negatifs


def affichage(d: dict, i: int) -> str:
    return d["table"].entree_encodeur.iloc[i][len("passage: "):]


def vivier_et_feuilles() -> dict:
    verifier_gel()
    entrees = verifier_entrees()
    if CLE.exists():
        raise ErreurJugement("Vivier déjà tiré : rien n'est écrasé")
    d = donnees_test()
    vivier = construire_vivier(d)
    rng = np.random.default_rng(GRAINE)
    positifs, negatifs = tirer_controles(d, vivier, rng)
    paires = ([{"question": q, "passage": i, "nature": "vivier", "sources": sorted(vivier[(q, i)])}
               for q, i in sorted(vivier)]
              + [{"question": q, "passage": i, "nature": "controle_positif", "sources": []} for q, i in positifs]
              + [{"question": q, "passage": i, "nature": "controle_negatif", "sources": []} for q, i in negatifs])
    ordre = rng.permutation(len(paires)).tolist()
    texte_q = {q["id"]: q["question"] for q in d["questions"]}
    cle = []
    for n, k in enumerate(ordre, 1):
        p = paires[k]
        cle.append({"id": f"J{n:04d}", "lot": f"{(n - 1) // TAILLE_LOT + 1:02d}", "question": p["question"],
                    "passage": p["passage"], "passage_id": d["table"].passage_id.iloc[p["passage"]],
                    "nature": p["nature"], "sources": p["sources"]})
    empreintes = {}
    for lot in sorted({c["lot"] for c in cle}):
        feuille = {"lot": lot, "consigne": CONSIGNE, "verdicts_possibles": list(VERDICTS_POSSIBLES),
                   "paires": [{"id": c["id"], "question": texte_q[c["question"]], "passage": affichage(d, c["passage"])}
                              for c in cle if c["lot"] == lot]}
        empreintes[lot] = ecrire_une_fois(FEUILLES / f"lot_{lot}.json", feuille)
    # Étalonnage humain (section 5) : 80 paires du vivier, 10 contrôles de chaque sorte, nouveaux identifiants
    rng_h = np.random.default_rng(GRAINE_ETALONNAGE)
    choisies = []
    for nature, nombre in (("vivier", 80), ("controle_positif", 10), ("controle_negatif", 10)):
        candidats = [c["id"] for c in cle if c["nature"] == nature]
        choisies += sorted(rng_h.choice(candidats, nombre, replace=False).tolist())
    choisies = [choisies[k] for k in rng_h.permutation(len(choisies)).tolist()]
    par_id = {c["id"]: c for c in cle}
    cle_h = [{"id": f"H{n:03d}", "paire": j} for n, j in enumerate(choisies, 1)]
    flux = io.StringIO()
    w = csv.writer(flux, lineterminator="\n")
    w.writerow(["id", "question", "passage", "verdict", "motif"])
    for h in cle_h:
        c = par_id[h["paire"]]
        w.writerow([h["id"], texte_q[c["question"]], affichage(d, c["passage"]), "", ""])
    contenu = {"protocole_09": SHA256_PROTOCOLE_09, "entrees": entrees, "graines": [GRAINE, GRAINE_ETALONNAGE],
               "effectifs": {"vivier": len(vivier), "controles_positifs": len(positifs),
                             "controles_negatifs": len(negatifs), "paires": len(cle), "questions_du_vivier":
                             len({q for q, _ in vivier})},
               "feuilles": empreintes, "paires": cle, "etalonnage": cle_h}
    contenu["etalonnage_feuille"] = ecrire_une_fois(ETALONNAGE / "feuille_etalonnage.csv", flux.getvalue())
    ecrire_une_fois(CLE, contenu)
    print(json.dumps({k: contenu[k] for k in ("effectifs", "feuilles", "etalonnage_feuille")}, ensure_ascii=False,
                     indent=1))
    return contenu


# Verdicts

def lire_cle() -> dict:
    verifier_gel()
    return json.loads(CLE.read_text(encoding="utf-8"))


def importer(juge: str, lot: str, fichier: Path) -> str:
    """Contrôle un fichier de verdicts et le recopie, une seule fois, dans data/evaluation/jugement_139/verdicts/."""
    if juge not in JUGES:
        raise ErreurJugement(f"Juge inconnu : {juge}")
    cle = lire_cle()
    attendus = [c["id"] for c in cle["paires"] if c["lot"] == lot]
    if not attendus:
        raise ErreurJugement(f"Lot inconnu : {lot}")
    v = json.loads(Path(fichier).read_text(encoding="utf-8"))
    ids = [x["id"] for x in v.get("verdicts", [])]
    if sorted(ids) != attendus or len(ids) != len(set(ids)):
        raise ErreurJugement(f"Les verdicts ne portent pas exactement sur les {len(attendus)} paires du lot {lot}")
    if any(x.get("verdict") not in VERDICTS_POSSIBLES or not str(x.get("motif", "")).strip() for x in v["verdicts"]):
        raise ErreurJugement("Verdict inconnu ou motif vide")
    propre = {"juge": juge, "lot": lot, "source_sha256": sha256_fichier(Path(fichier)),
              "verdicts": sorted(({"id": x["id"], "verdict": x["verdict"], "motif": x["motif"]} for x in v["verdicts"]),
                                 key=lambda x: x["id"])}
    return ecrire_une_fois(VERDICTS / juge / f"lot_{lot}.json", propre)


def lire_verdicts(cle: dict) -> dict:
    lots = sorted({c["lot"] for c in cle["paires"]})
    sortie = {}
    for juge in JUGES:
        manquants = [lot for lot in lots if not (VERDICTS / juge / f"lot_{lot}.json").is_file()]
        if manquants:
            raise ErreurJugement(f"{juge} : lots non jugés {manquants}")
        sortie[juge] = {x["id"]: x["verdict"] for lot in lots
                        for x in json.loads((VERDICTS / juge / f"lot_{lot}.json").read_text(encoding="utf-8"))["verdicts"]}
    return sortie


def fiabilite(cle: dict, verdicts: dict) -> dict:
    sortie = {}
    for juge, v in verdicts.items():
        pos = sum(v[c["id"]] in ("repond", "en_partie") for c in cle["paires"] if c["nature"] == "controle_positif")
        neg = sum(v[c["id"]] in ("repond", "en_partie") for c in cle["paires"] if c["nature"] == "controle_negatif")
        pos_r = sum(v[c["id"]] == "repond" for c in cle["paires"] if c["nature"] == "controle_positif")
        sortie[juge] = {"positifs_reconnus": pos, "positifs_repond": pos_r, "negatifs_acceptes": neg,
                        "fiable": pos >= SENSIBILITE_MIN and neg <= FAUX_POSITIFS_MAX}
    return sortie


def pertinence_jugee(cle: dict, verdicts: dict, fiab: dict) -> dict:
    """Paires du vivier jugées pertinentes, règle principale et règle large (section 6)."""
    fiables = [j for j in JUGES if fiab[j]["fiable"]]
    if not fiables:
        return {"juges_retenus": [], "principale": set(), "large": set()}
    principale, large = set(), set()
    for c in cle["paires"]:
        if c["nature"] != "vivier":
            continue
        v = [verdicts[j][c["id"]] for j in fiables]
        if all(x == "repond" for x in v):
            principale.add((c["question"], c["passage"]))
        if any(x in ("repond", "en_partie") for x in v):
            large.add((c["question"], c["passage"]))
    return {"juges_retenus": fiables, "principale": principale, "large": large}


# Mesures

def pertinents_par_definition(d: dict, juges: dict) -> dict:
    defs = {"minorant_d4": {q["id"]: set(d["d4"][q["id"]]) for q in d["questions"]}}
    for nom, cles in (("majorant_principal", juges["principale"]), ("majorant_large", juges["large"])):
        defs[nom] = {q["id"]: set(d["d4"][q["id"]]) | {i for (qq, i) in cles if qq == q["id"]} for q in d["questions"]}
    return defs


def mesures_a(d: dict, defs: dict) -> dict:
    groupes = [q["fiche"] for q in d["questions"]]
    res = {}
    succes = {}
    for nom, pert in defs.items():
        res[nom] = {}
        for s in SYSTEMES_A:
            cl = d["classements"][s]
            fiches_p = {q["id"]: {d["slug"][i] for i in pert[q["id"]]} for q in d["questions"]}
            m = {f"succes@{k}": [bool(set(cl[q["id"]][:k]) & pert[q["id"]]) for q in d["questions"]] for k in (5, 10)}
            m["fiche@5"] = [any(d["slug"][i] in fiches_p[q["id"]] for i in cl[q["id"]][:5]) for q in d["questions"]]
            succes[(nom, s)] = m
            res[nom][s] = {k: proportion(v, groupes) for k, v in m.items()}
        res[nom]["ajuste moins base"] = {k: ecart_apparie(succes[(nom, "ajuste")][k], succes[(nom, "base")][k], groupes)
                                         for k in ("succes@5", "succes@10", "fiche@5")}
    return res, succes


def taxonomie_a(d: dict, defs: dict) -> dict:
    sortie = {}
    for s in SYSTEMES_A:
        compte = {"autre passage valable": 0, "bonne fiche, passage insuffisant": 0, "mauvaise fiche": 0}
        detail = {}
        for q in d["questions"]:
            top = d["classements"][s][q["id"]][:5]
            if set(top) & d["d4"][q["id"]]:
                continue
            fiches_d4 = {d["slug"][i] for i in d["d4"][q["id"]]}
            if set(top) & defs["majorant_principal"][q["id"]]:
                c = "autre passage valable"
            elif any(d["slug"][i] in fiches_d4 for i in top):
                c = "bonne fiche, passage insuffisant"
            else:
                c = "mauvaise fiche"
            compte[c] += 1
            detail[q["id"]] = c
        sortie[s] = {"echecs_d4": sum(compte.values()), "categories": compte, "par_question": detail}
    return sortie


def mesures_b(d: dict, defs: dict) -> dict:
    res = {}
    succes = {}
    for etat, sorties in d["etats"].items():
        qs = [q for q in d["questions"] if sorties[q["id"]]["classe"] != "erreur_technique"]
        groupes = [q["fiche"] for q in qs]
        res[etat] = {"questions": len(qs), "exclues": sorted(q["id"] for q in d["questions"] if q not in qs)}
        for nom, pert in defs.items():
            plafond = [bool(set(sorties[q["id"]]["contexte"]) & pert[q["id"]]) for q in qs]
            m4 = [sorties[q["id"]]["classe"] == "reponse_citee" and bool(set(sorties[q["id"]]["cites"]) & pert[q["id"]])
                  for q in qs]
            succes[(etat, nom)] = dict(zip([q["id"] for q in qs], m4))
            res[etat][nom] = {"plafond": proportion(plafond, groupes), "m4": proportion(m4, groupes),
                              "m4_si_passage_fourni": (sum(m4) / sum(plafond)) if sum(plafond) else None}
    for a, b in (("V2", "B2"), ("V1", "B2"), ("V2", "V1")):
        communes = [q for q in d["questions"] if q["id"] in succes[(a, "minorant_d4")] and q["id"] in succes[(b, "minorant_d4")]]
        groupes = [q["fiche"] for q in communes]
        res[f"{a} moins {b}"] = {nom: ecart_apparie([succes[(a, nom)][q["id"]] for q in communes],
                                                    [succes[(b, nom)][q["id"]] for q in communes], groupes)
                                 for nom in defs}
    return res


def taxonomie_b(d: dict, defs: dict) -> dict:
    sortie = {}
    pert = defs["majorant_principal"]
    for etat, sorties in d["etats"].items():
        compte = {"récupération": 0, "abstention du modèle": 0, "abstention sous le seuil": 0,
                  "citation non pertinente": 0, "sortie invalide": 0}
        for q in d["questions"]:
            o = sorties[q["id"]]
            if o["classe"] == "erreur_technique":
                continue
            if o["classe"] == "reponse_citee" and set(o["cites"]) & pert[q["id"]]:
                continue
            if not set(o["contexte"]) & pert[q["id"]]:
                c = "récupération"
            elif o["classe"] == "abstention":
                c = "abstention du modèle" if o["appel_modele"] else "abstention sous le seuil"
            elif o["classe"] == "reponse_citee":
                c = "citation non pertinente"
            else:
                c = "sortie invalide"
            compte[c] += 1
        sortie[etat] = {"echecs": sum(compte.values()), "categories": compte}
    return sortie


def controle_reproduction(d: dict, res_a: dict, res_b: dict) -> dict:
    ecarts = []
    for (s, m), attendu in REPRODUCTION_A.items():
        if res_a["minorant_d4"][s][m]["succes"] != attendu:
            ecarts.append(f"A {s} {m} : {res_a['minorant_d4'][s][m]['succes']} au lieu de {attendu}")
    a1 = json.loads(MESURE_A1.read_text(encoding="utf-8"))["jeu_equipe"]["systemes"]
    for s in SYSTEMES_A:
        for m, cle in (("succes@5", "recall@5"), ("succes@10", "recall@10"), ("fiche@5", "recall@5_fiche")):
            if abs(res_a["minorant_d4"][s][m]["part"] - a1[s][cle]) > 1e-12:
                ecarts.append(f"A {s} {m} différent de la mesure de A1")
    for etat, attendu in REPRODUCTION_B.items():
        r = res_b[etat]
        obtenu = {"questions": r["questions"], "plafond": r["minorant_d4"]["plafond"]["succes"],
                  "m4": r["minorant_d4"]["m4"]["succes"]}
        if obtenu != attendu:
            ecarts.append(f"B {etat} : {obtenu} au lieu de {attendu}")
    return {"conforme": not ecarts, "ecarts": ecarts}


def mesures_cdtn() -> dict:
    """Métriques à plusieurs passages sur le CDTN (section 7), avec reproduction du succès à 5 de la mesure de A1."""
    pop = json.loads(a05.POPULATION_CDTN.read_text(encoding="utf-8"))
    formulations, pertinents, requetes = [], [], []
    for r in pop["requetes"]:
        for f in r["formulations"]:
            formulations.append(f["id"])
            pertinents.append(set(r["pertinents"]))
            requetes.append(r["id"])
    table, index = a05.table_et_index_site()
    matrices = {"base": index.matrice, "ajuste": a05.charger_index_ajuste()}
    vecteurs = {"base": a05.charger_vecteurs(a05.VECTEURS / "vecteurs_cdtn_mesure_base.json", "base"),
                "ajuste": a05.charger_vecteurs(a05.VECTEURS / "vecteurs_cdtn_mesure_ajuste.json", "ajuste")}
    classements = {s: [np.argsort(-(matrices[s] @ vecteurs[s][f]), kind="stable")[:10].tolist() for f in formulations]
                   for s in SYSTEMES_A}
    c = json.loads(CLASSEMENTS_CDTN.read_text(encoding="utf-8"))
    ids_c = [x if isinstance(x, str) else x["id"] for x in c["formulations"]]
    if ids_c != formulations:
        raise ErreurJugement("Classements BM25 dans un autre ordre que la population")
    classements["bm25"] = [x[:10] for x in c["bm25"]]
    uniques = sorted(set(requetes))
    rang_requete = np.array([uniques.index(r) for r in requetes])
    rng = np.random.default_rng(GRAINE)
    tirages = rng.integers(0, len(uniques), size=(TIRAGES, len(uniques)))
    nb = np.bincount(rang_requete, minlength=len(uniques)).astype(float)

    def intervalle(valeurs: np.ndarray) -> list[float]:
        somme = np.bincount(rang_requete, weights=valeurs, minlength=len(uniques))
        moyennes = somme[tirages].sum(1) / nb[tirages].sum(1)
        return [float(np.percentile(moyennes, 2.5)), float(np.percentile(moyennes, 97.5))]

    res, brut = {"formulations": len(formulations), "requetes": len(uniques), "systemes": {}}, {}
    for s, cl in classements.items():
        m = {"succes@5": [float(bool(set(x[:5]) & p)) for x, p in zip(cl, pertinents)],
             "succes@10": [float(bool(set(x[:10]) & p)) for x, p in zip(cl, pertinents)],
             "rappel@5": [len(set(x[:5]) & p) / len(p) for x, p in zip(cl, pertinents)],
             "rappel@10": [len(set(x[:10]) & p) / len(p) for x, p in zip(cl, pertinents)],
             "ndcg@10": [ndcg10(x, p) for x, p in zip(cl, pertinents)],
             "precision@5": [len(set(x[:5]) & p) / 5 for x, p in zip(cl, pertinents)]}
        brut[s] = {k: np.asarray(v) for k, v in m.items()}
        res["systemes"][s] = {k: {"valeur": float(np.mean(v)), "ic95": intervalle(np.asarray(v))} for k, v in m.items()}
    res["ajuste moins base"] = {k: {"ecart": float(np.mean(brut["ajuste"][k] - brut["base"][k])),
                                    "ic95": intervalle(brut["ajuste"][k] - brut["base"][k])} for k in brut["base"]}
    a1 = json.loads(MESURE_A1.read_text(encoding="utf-8"))["cdtn"]["systemes"]
    ecarts = [s for s in SYSTEMES_A if abs(res["systemes"][s]["succes@5"]["valeur"] - a1[s]["recall@5"]) > 1e-12]
    res["reproduction_succes@5_a1"] = {"conforme": not ecarts, "ecarts": ecarts}
    res["pertinents_par_requete"] = {"mediane": float(np.median([len(r["pertinents"]) for r in pop["requetes"]])),
                                     "min": min(len(r["pertinents"]) for r in pop["requetes"]),
                                     "max": max(len(r["pertinents"]) for r in pop["requetes"])}
    return res


def accord(cle: dict, verdicts: dict) -> dict:
    ids = [c["id"] for c in cle["paires"] if c["nature"] == "vivier"]
    a = [ORDRE[verdicts["J1"][i]] for i in ids]
    b = [ORDRE[verdicts["J2"][i]] for i in ids]
    repartition = {j: {v: sum(verdicts[j][i] == v for i in ids) for v in VERDICTS_POSSIBLES} for j in JUGES}
    return {"paires": len(ids), "accord_brut": float(np.mean(np.asarray(a) == np.asarray(b))),
            "kappa": kappa(a, b), "kappa_ic95": kappa_ic(a, b),
            "kappa_lineaire": kappa(a, b, ponderation="lineaire"),
            "kappa_lineaire_ic95": kappa_ic(a, b, ponderation="lineaire"), "repartition": repartition}


def mesurer() -> dict:
    verifier_gel()
    entrees = verifier_entrees()
    cle = lire_cle()
    verdicts = lire_verdicts(cle)
    d = donnees_test()
    if len(construire_vivier(d)) != cle["effectifs"]["vivier"]:
        raise ErreurJugement("Vivier recalculé différent de celui tiré")
    fiab = fiabilite(cle, verdicts)
    juges = pertinence_jugee(cle, verdicts, fiab)
    if not juges["juges_retenus"]:
        raise ErreurJugement("Aucun juge fiable : aucun majorant n'est publié (section 6)")
    defs = pertinents_par_definition(d, juges)
    res_a, _ = mesures_a(d, defs)
    res_b = mesures_b(d, defs)
    repro = controle_reproduction(d, res_a, res_b)
    if not repro["conforme"]:
        raise ErreurJugement(f"Reproduction sous D4 non conforme : {repro['ecarts']}")
    cdtn = mesures_cdtn()
    if not cdtn["reproduction_succes@5_a1"]["conforme"]:
        raise ErreurJugement("Succès à 5 du CDTN différent de la mesure de A1")
    contenu = {"protocole_09": SHA256_PROTOCOLE_09, "entrees": entrees, "cle_sha256": sha256_fichier(CLE),
               "verdicts_sha256": {j: {p.name: sha256_fichier(p) for p in sorted((VERDICTS / j).glob("lot_*.json"))}
                                   for j in JUGES},
               "reproduction_d4": repro, "fiabilite": fiab, "accord_entre_juges": accord(cle, verdicts),
               "juges_retenus": juges["juges_retenus"],
               "paires_jugees_pertinentes": {"principale": len(juges["principale"]), "large": len(juges["large"])},
               "volet_a": res_a, "echecs_volet_a": taxonomie_a(d, defs), "volet_b": res_b,
               "echecs_volet_b": taxonomie_b(d, defs), "cdtn": cdtn,
               "statut": "provisoire : étalonnage humain non intégré (protocole 09, section 6)"}
    contenu = json.loads(json.dumps(contenu, ensure_ascii=False, default=float))
    precedent = sorted(SORTIES.glob("mesure_*.json"))
    chemin = SORTIES / f"mesure_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    empreinte = ecrire_une_fois(chemin, contenu)
    if precedent:
        identique = json.loads(precedent[-1].read_text(encoding="utf-8")) == contenu
        print(f"seconde exécution : contenu {'identique' if identique else 'DIFFÉRENT'} de {precedent[-1].name}")
        if not identique:
            raise ErreurJugement("Deux exécutions différentes : résultat non retenu")
    print(f"{chemin.relative_to(RACINE)} SHA-256 {empreinte}")
    return contenu


def etalonnage(fichiers: list[Path]) -> dict:
    """Accord des jugements humains entre eux et avec la règle principale des juges d'IA (section 6)."""
    cle = lire_cle()
    verdicts = lire_verdicts(cle)
    par_h = {h["id"]: h["paire"] for h in cle["etalonnage"]}
    nature = {c["id"]: c["nature"] for c in cle["paires"]}
    humains = []
    for f in fichiers:
        with open(f, encoding="utf-8-sig", newline="") as flux:
            lignes = list(csv.DictReader(flux))
        if sorted(x["id"] for x in lignes) != sorted(par_h) or any(x["verdict"] not in VERDICTS_POSSIBLES for x in lignes):
            raise ErreurJugement(f"{Path(f).name} : identifiants ou verdicts non conformes")
        humains.append({x["id"]: x["verdict"] for x in lignes})
    ids = sorted(par_h)
    h1, h2 = ([ORDRE[h[i]] for i in ids] for h in humains)
    vivier = [i for i in ids if nature[par_h[i]] == "vivier"]
    consensus = [int(humains[0][i] == "repond" and humains[1][i] == "repond") for i in vivier]
    ia = [int(all(verdicts[j][par_h[i]] == "repond" for j in JUGES)) for i in vivier]
    k_ia = kappa(consensus, ia, k=2)
    res = {"humains": [str(Path(f).name) for f in fichiers], "fichiers_sha256": [sha256_fichier(Path(f)) for f in fichiers],
           "kappa_humains": kappa(h1, h2), "kappa_humains_ic95": kappa_ic(h1, h2),
           "kappa_consensus_humain_ia": k_ia, "kappa_consensus_humain_ia_ic95": kappa_ic(consensus, ia, k=2),
           "paires_du_vivier": len(vivier),
           "controles_positifs_reconnus_par_les_humains": [sum(h[i] in ("repond", "en_partie") for i in ids
                                                               if nature[par_h[i]] == "controle_positif") for h in humains],
           "controles_negatifs_acceptes_par_les_humains": [sum(h[i] in ("repond", "en_partie") for i in ids
                                                               if nature[par_h[i]] == "controle_negatif") for h in humains],
           "majorants": "étayés" if k_ia >= KAPPA_ETALONNAGE_MIN else "non étayés (kappa inférieur à 0,6)"}
    ecrire_une_fois(ETALONNAGE / f"etalonnage_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json", res)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return res


def etat() -> dict:
    cle = lire_cle()
    lots = sorted({c["lot"] for c in cle["paires"]})
    r = {j: {"jugés": [l for l in lots if (VERDICTS / j / f"lot_{l}.json").is_file()]} for j in JUGES}
    print(json.dumps(r, ensure_ascii=False))
    return r


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = p.add_subparsers(dest="commande", required=True)
    sp.add_parser("vivier")
    pi = sp.add_parser("importer")
    pi.add_argument("juge")
    pi.add_argument("lot")
    pi.add_argument("fichier", type=Path)
    sp.add_parser("etat")
    sp.add_parser("mesurer")
    pe = sp.add_parser("etalonnage")
    pe.add_argument("fichiers", type=Path, nargs=2)
    a = p.parse_args(argv)
    if a.commande == "vivier":
        vivier_et_feuilles()
    elif a.commande == "importer":
        print(importer(a.juge, a.lot, a.fichier))
    elif a.commande == "etat":
        etat()
    elif a.commande == "mesurer":
        mesurer()
    else:
        etalonnage(a.fichiers)
    return 0


if __name__ == "__main__":
    sys.exit(main())
