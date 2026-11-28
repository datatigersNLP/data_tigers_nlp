"""Réglage de la récupération v2 sur le jeu CDTN (#138), sans lire les questions ni les extraits du lot de test.

    python scripts/recuperation/reglage_cdtn.py preparer             # population, E5, BM25 V3 (caches)
    python scripts/recuperation/reglage_cdtn.py reclasser <clé>      # scores d'un reclasseur (cache)
    python scripts/recuperation/reglage_cdtn.py grille               # toutes les configurations

Population (étude 04, section 6) : requêtes jugées « oui » ou « partiel », sans les formulations écartées.
Population principale : les formulations en forme de question ; les titres en analyse secondaire ; en
sensibilité, les requêtes dont aucune fiche n'est parmi les 61 fiches du lot de test (seules les URL du lot
sont lues, comme dans scripts/adaptation_qwen/separation.py). Effectif utile : les requêtes.
Sorties dans data/evaluation/recuperation/, qui n'est pas versionné.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recuperation as rc  # noqa: E402

RACINE = rc.RACINE
sys.path.insert(0, str(RACINE / "scripts" / "adaptation_qwen"))
import rag  # noqa: E402
import separation  # noqa: E402

JEU_CDTN = RACINE / "data" / "evaluation" / "cdtn" / "jeu_cdtn.json"
IDENTIFIANTS = RACINE / "evaluation" / "cdtn" / "identifiants.csv"
JUGEMENTS = RACINE / "evaluation" / "cdtn" / "jugements.csv"
SHA256_JUGEMENTS = "0ddf16834b9ebdb2c9c71eeb78df2f2412130473dc9f3af892c7f757cc131968"  # étude 04, section 5
SORTIE = RACINE / "data" / "evaluation" / "recuperation"
PROFONDEUR = 100       # profondeur des classements de premier niveau
CANDIDATS_MAX = 50     # candidats reclassés au plus, par source
GRAINE = 20261109
TIRAGES = 2000
VALEURS_K = (5, 8, 10, 15)
VALEURS_CANDIDATS = (20, 50)
REFERENCE = rc.Configuration(k=5)   # la chaîne actuelle : E5 seul, 5 passages
COUT_RECLASSEUR = {None: 0, "mmarco-minilm": 1, "camembert-mmarco": 2, "bge-m3": 3}   # ordre de coût, pour départager


class ErreurReglage(ValueError):
    pass


def ecrire_json(chemin: Path, objet) -> str:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    texte = json.dumps(objet, ensure_ascii=False, indent=1, sort_keys=True)
    chemin.write_text(texte + "\n", encoding="utf-8")
    return hashlib.sha256((texte + "\n").encode("utf-8")).hexdigest()


def lire_json(chemin: Path):
    return json.loads(chemin.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------------------------------
# Population
# ---------------------------------------------------------------------------------------------------------------
def empreinte_jeu(requetes) -> str:
    # même définition que scripts/evaluation/cdtn_jeu.py (empreinte_jeu) : identifiants seulement
    lignes = [f"{fo['id']}\t{' '.join(r['passages_pertinents'])}" for r in requetes for fo in r["formulations"]]
    return hashlib.sha256("\n".join(lignes).encode("utf-8")).hexdigest()


def charger_population(index: rag.IndexCommun) -> dict:
    jeu = lire_json(JEU_CDTN)
    requetes = jeu["requetes"]
    if empreinte_jeu(requetes) != jeu["empreinte_identifiants"]:
        raise ErreurReglage("jeu_cdtn.json : empreinte des identifiants incohérente")
    with open(IDENTIFIANTS, encoding="utf-8", newline="") as f:
        versionnes = {r["id_formulation"]: (r["id_requete"], r["type"], r["passages_pertinents"].split())
                      for r in csv.DictReader(f)}
    locaux = {fo["id"]: (r["id"], fo["type"], r["passages_pertinents"]) for r in requetes for fo in r["formulations"]}
    if versionnes != locaux:
        raise ErreurReglage("jeu_cdtn.json diffère de evaluation/cdtn/identifiants.csv")
    if rc.sha256_fichier(JUGEMENTS) != SHA256_JUGEMENTS:
        raise ErreurReglage("jugements.csv : empreinte différente de celle de l'étude 04")
    verdicts, ecartees = {}, set()
    with open(JUGEMENTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["id_formulation"]:
                if r["verdict"] != "écartée":
                    raise ErreurReglage(f"Jugement de formulation inattendu : {r}")
                ecartees.add(r["id_formulation"])
            else:
                if r["id_requete"] in verdicts:
                    raise ErreurReglage(f"Deux verdicts pour {r['id_requete']}")
                verdicts[r["id_requete"]] = r["verdict"]
    position = {p["passage_id"]: i for i, p in enumerate(index.passages)}
    fiches_test = separation.fiches_exclues(separation.lire_jeu())
    retenues = []
    for r in requetes:
        if verdicts.get(r["id"]) not in ("oui", "partiel"):
            continue
        formulations = [fo for fo in r["formulations"] if fo["id"] not in ecartees]
        if not formulations:
            continue
        pertinents = [position[p] for p in r["passages_pertinents"]]
        retenues.append({"id": r["id"], "verdict": verdicts[r["id"]], "pertinents": pertinents,
                         "fiches": sorted({s["fiche"] for s in r["sections"]}),
                         "hors_fiches_test": not ({s["fiche"] for s in r["sections"]} & fiches_test),
                         "formulations": [{"id": fo["id"], "type": fo["type"], "texte": fo["texte"]}
                                          for fo in formulations]})
    n_req = len(retenues)
    n_form = sum(len(r["formulations"]) for r in retenues)
    n_titres = sum(fo["type"] == "titre" for r in retenues for fo in r["formulations"])
    if (n_req, n_form, n_titres) != (131, 494, 131):
        raise ErreurReglage(f"Population : {n_req} requêtes, {n_form} formulations, {n_titres} titres ; "
                            "l'étude 04 en publie 131, 494 et 131")
    return {"requetes": retenues, "fiches_test": separation.empreinte_fiches(fiches_test)}


# ---------------------------------------------------------------------------------------------------------------
# Étape 1 : préparation
# ---------------------------------------------------------------------------------------------------------------
def preparer() -> None:
    from lexical_baselines import BM25Retriever
    index = rag.charger_index()
    table = rc.charger_passages_m2(index)
    population = charger_population(index)
    formulations = [fo for r in population["requetes"] for fo in r["formulations"]]
    debut = time.perf_counter()
    modele = rag.charger_encodeur()
    vecteurs = np.stack([rag.encoder_question(modele, fo["texte"]) for fo in formulations])
    duree_e5 = time.perf_counter() - debut
    scores_e5 = vecteurs @ index.matrice.T
    listes_e5 = [rc.classement(s)[:PROFONDEUR].tolist() for s in scores_e5]
    bm25 = BM25Retriever(stopwords_variant="snowball_no_negation", stemming="french").fit(
        rc.textes_lexicaux(table), doc_ids=table.passage_id.tolist())
    scores_bm25 = bm25.score_matrix([fo["texte"] for fo in formulations])
    listes_bm25 = [rc.classement(s, positifs=True)[:PROFONDEUR].tolist() for s in scores_bm25]
    caches = {
        "formulations": [fo["id"] for fo in formulations],
        "e5": listes_e5, "bm25": listes_bm25,
        "cosinus_max_e5": [float(s.max()) for s in scores_e5],
        "duree_encodage_e5_s": round(duree_e5, 2),
    }
    sha = ecrire_json(SORTIE / "classements.json", caches)
    manifeste = {
        "ecrit_le": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "population": {"requetes": len(population["requetes"]), "formulations": len(formulations),
                       "empreinte_fiches_test": population["fiches_test"]},
        "entrees": {"jeu_cdtn": rc.sha256_fichier(JEU_CDTN), "identifiants": rc.sha256_fichier(IDENTIFIANTS),
                    "jugements": SHA256_JUGEMENTS, "index": index.entete["index"]["sha256"],
                    "passages": index.entete["metadonnees"]["sha256"]},
        "e5": {"modele": rag.MODELE_E5, "revision": rag.REVISION_E5},
        "bm25": "V3 : mots vides Snowball sans négations, racinisation, k1 = 1,2, b = 0,75, idf de Lucene",
        "classements_sha256": sha,
        "environnement": {"python": platform.python_version(), "plateforme": platform.platform()},
    }
    ecrire_json(SORTIE / "manifeste.json", manifeste)
    ecrire_json(SORTIE / "population.json", population)
    print(f"{len(population['requetes'])} requêtes, {len(formulations)} formulations ; E5 en {duree_e5:.1f} s")


def charger_caches():
    manifeste = lire_json(SORTIE / "manifeste.json")
    texte = (SORTIE / "classements.json").read_text(encoding="utf-8")
    if hashlib.sha256(texte.encode("utf-8")).hexdigest() != manifeste["classements_sha256"]:
        raise ErreurReglage("classements.json : empreinte différente du manifeste")
    return manifeste, json.loads(texte), lire_json(SORTIE / "population.json")


def candidats_a_reclasser(classements) -> list[list[int]]:
    """Union des 50 premiers candidats des deux sources (E5 et fusion RRF), dans l'ordre d'apparition."""
    sortie = []
    for e5, bm25 in zip(classements["e5"], classements["bm25"]):
        rrf = rc.fusion_rrf([e5, bm25])[:CANDIDATS_MAX]
        vus, liste = set(), []
        for i in list(e5[:CANDIDATS_MAX]) + list(rrf):
            if i not in vus:
                vus.add(i)
                liste.append(int(i))
        sortie.append(liste)
    return sortie


# ---------------------------------------------------------------------------------------------------------------
# Étape 2 : scores d'un reclasseur
# ---------------------------------------------------------------------------------------------------------------
def reclasser(cle: str) -> None:
    index = rag.charger_index()
    table = rc.charger_passages_m2(index)
    textes = rc.textes_lexicaux(table)
    manifeste, classements, population = charger_caches()
    textes_formulations = {fo["id"]: fo["texte"] for r in population["requetes"] for fo in r["formulations"]}
    candidats = candidats_a_reclasser(classements)
    modele = rc.Reclasseur(cle)
    debut = time.perf_counter()
    scores = {}
    for fid, liste in zip(classements["formulations"], candidats):
        s = modele.scores(textes_formulations[fid], [textes[i] for i in liste])
        scores[fid] = {str(i): float(v) for i, v in zip(liste, s)}
    duree = time.perf_counter() - debut
    paires = sum(len(v) for v in scores.values())
    sha = ecrire_json(SORTIE / f"reclasseur_{cle}.json",
                      {"cle": cle, "modele": modele.nom, "revision": modele.revision, "paires": paires,
                       "duree_s": round(duree, 1), "classements_sha256": manifeste["classements_sha256"],
                       "scores": scores})
    print(f"{cle} : {paires} paires en {duree:.0f} s ({paires / duree:.1f} paires/s) ; sha256 {sha[:16]}")


# ---------------------------------------------------------------------------------------------------------------
# Étape 3 : grille
# ---------------------------------------------------------------------------------------------------------------
def ndcg(classement, pertinents, n=10) -> float:
    rel = set(pertinents)
    dcg = sum(1 / math.log2(r + 1) for r, i in enumerate(classement[:n], 1) if i in rel)
    idcg = sum(1 / math.log2(r + 1) for r in range(1, min(n, len(rel)) + 1))
    return dcg / idcg


def rr(classement, pertinents, n=10) -> float:
    rel = set(pertinents)
    return next((1 / r for r, i in enumerate(classement[:n], 1) if i in rel), 0.0)


def configurations() -> list[rc.Configuration]:
    liste = []
    for source in ("e5", "rrf"):
        for reclasseur in (None, *rc.RECLASSEURS):
            for candidats in ((0,) if reclasseur is None else VALEURS_CANDIDATS):
                for k in VALEURS_K:
                    if reclasseur and candidats < k:
                        continue
                    for voisins in (False, True):
                        liste.append(rc.Configuration(k=k, source=source, reclasseur=reclasseur,
                                                      candidats=candidats, voisins=voisins))
    return liste


def agreger(valeurs_par_requete: dict, ids: list[str], rng) -> dict:
    """Moyenne sur les requêtes des moyennes par requête, et intervalle à 95 % par bootstrap sur les requêtes."""
    m = np.array([valeurs_par_requete[i] for i in ids], dtype=np.float64)
    tirages = rng.integers(0, len(m), size=(TIRAGES, len(m)))
    boot = m[tirages].mean(axis=1)
    return {"moyenne": float(m.mean()), "ic95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
            "requetes": len(m)}


def grille(sans_reclasseur: bool = False) -> None:
    index = rag.charger_index()
    table = rc.charger_passages_m2(index)
    cles = rc.sections(table)
    manifeste, classements, population = charger_caches()
    tok = rc.generation.charger_tokeniseur_qwen()
    formulations = {fo["id"]: (r["id"], fo) for r in population["requetes"] for fo in r["formulations"]}
    pertinents = {r["id"]: r["pertinents"] for r in population["requetes"]}
    reclasseurs = {}
    for cle in rc.RECLASSEURS:
        chemin = SORTIE / f"reclasseur_{cle}.json"
        if chemin.exists():
            d = lire_json(chemin)
            if d["classements_sha256"] != manifeste["classements_sha256"] or d["revision"] != rc.RECLASSEURS[cle][1]:
                raise ErreurReglage(f"Cache du reclasseur {cle} incohérent avec les classements")
            reclasseurs[cle] = {fid: {int(i): v for i, v in s.items()} for fid, s in d["scores"].items()}
        elif not sans_reclasseur:
            raise ErreurReglage(f"Scores du reclasseur {cle} absents : lancer « reclasser {cle} »")
    cache_tokens: dict = {}

    def mesurer(fid, indices):
        cle = (fid, tuple(indices))
        if cle not in cache_tokens:
            contexte = rc.construire_contexte_v2(formulations[fid][1]["texte"], indices, index.passages)
            cache_tokens[cle] = rc.compter_tokens(tok, contexte)
        return cache_tokens[cle]

    lignes, configs = [], [c for c in configurations() if c.reclasseur is None or c.reclasseur in reclasseurs]
    for c in configs:
        for n, fid in enumerate(classements["formulations"]):
            rid, fo = formulations[fid]
            ordre = rc.classement_final(c, classements["e5"][n], classements["bm25"][n],
                                        reclasseurs.get(c.reclasseur, {}).get(fid), profondeur=PROFONDEUR)
            groupes = rc.groupes_du_contexte(ordre[:c.k], cles, c.voisins)
            contexte, retires = rc.dans_le_budget(groupes, lambda ind: mesurer(fid, ind))
            rel = set(pertinents[rid])
            trouves = rel & set(contexte)
            lignes.append({"configuration": c.nom, "formulation": fid, "requete": rid, "type": fo["type"],
                           "rappel_contexte": int(bool(trouves)), "couverture": len(trouves) / len(rel),
                           "precision_contexte": len(trouves) / len(contexte), "ndcg10": ndcg(ordre, rel),
                           "rr10": rr(ordre, rel), "passages": len(contexte), "tokens": mesurer(fid, contexte),
                           "groupes_retires": retires})
    with open(SORTIE / "formulations_grille.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(lignes)
    resume = resumer(lignes, configs, population)
    ecrire_json(SORTIE / "resultats_grille.json", resume)
    afficher(resume)


def resumer(lignes, configs, population) -> dict:
    hors_test = {r["id"] for r in population["requetes"] if r["hors_fiches_test"]}
    metriques = ("rappel_contexte", "couverture", "precision_contexte", "ndcg10", "rr10", "passages", "tokens")
    par = {}
    for l in lignes:
        par.setdefault((l["configuration"], l["type"]), {}).setdefault(l["requete"], []).append(l)
    resultats = {}
    for c in configs:
        bloc = {"configuration": c.nom, "k": c.k, "source": c.source, "reclasseur": c.reclasseur,
                "candidats": c.candidats, "voisins": c.voisins}
        for population_nom, type_, filtre in (("questions", "question", None), ("titres", "titre", None),
                                             ("questions_hors_fiches_test", "question", hors_test)):
            groupes = par[(c.nom, type_)]
            ids = sorted(r for r in groupes if filtre is None or r in filtre)
            bloc[population_nom] = {}
            for m in metriques:
                moyennes = {r: float(np.mean([l[m] for l in groupes[r]])) for r in ids}
                bloc[population_nom][m] = agreger(moyennes, ids, np.random.default_rng(GRAINE))
            bloc[population_nom]["tokens_max"] = max(l["tokens"] for r in ids for l in groupes[r])
            bloc[population_nom]["formulations_tronquees"] = sum(l["groupes_retires"] > 0 for r in ids for l in groupes[r])
        resultats[c.nom] = bloc
    # écart apparié à la référence, par requête, sur la population principale
    ref = par[(REFERENCE.nom, "question")]
    for c in configs:
        groupes = par[(c.nom, "question")]
        ids = sorted(groupes)
        d = {r: float(np.mean([l["rappel_contexte"] for l in groupes[r]]) - np.mean([l["rappel_contexte"] for l in ref[r]]))
             for r in ids}
        resultats[c.nom]["questions"]["ecart_rappel_vs_reference"] = agreger(d, ids, np.random.default_rng(GRAINE))
    return {"reference": REFERENCE.nom, "graine": GRAINE, "tirages": TIRAGES, "configurations": resultats,
            "choix": choisir(resultats)}


K_AMENDEMENT_A1 = 10


def choisir(resultats: dict) -> dict:
    """Deux règles, toutes deux publiées sur le #138 avant la lecture des résultats des reclasseurs.

    Règle initiale : le meilleur rappel du contexte sur les questions ; à un point près, la configuration la moins
    coûteuse (tokens moyens, puis coût du reclasseur, puis candidats). Elle choisit toujours le plus grand k, car le
    rappel du contexte croît avec k : c'est son défaut, gardé ici pour la transparence.
    Amendement A1 (retenu) : k = 10 fixé d'avance, sans voisins ; la même règle choisit le classement.
    """
    def appliquer(candidates):
        meilleur = max(r["questions"]["rappel_contexte"]["moyenne"] for r in candidates)
        eligibles = [r for r in candidates if r["questions"]["rappel_contexte"]["moyenne"] >= meilleur - 0.01]
        eligibles.sort(key=lambda r: (r["questions"]["tokens"]["moyenne"], COUT_RECLASSEUR[r["reclasseur"]],
                                      r["candidats"], r["configuration"]))
        return {"meilleur_rappel": meilleur, "eligibles": [r["configuration"] for r in eligibles],
                "retenue": eligibles[0]["configuration"]}
    a1 = [r for r in resultats.values() if r["k"] == K_AMENDEMENT_A1 and not r["voisins"]]
    return {"regle_initiale": appliquer(list(resultats.values())), "amendement_a1": appliquer(a1),
            "retenue": appliquer(a1)["retenue"]}


def afficher(resume: dict) -> None:
    conf = resume["configurations"]
    print(f"{'configuration':42} {'rappel ctx':>18} {'écart réf.':>20} {'nDCG@10':>8} {'passages':>8} {'tokens':>7} {'max':>6}")
    for nom, r in sorted(conf.items(), key=lambda kv: -kv[1]["questions"]["rappel_contexte"]["moyenne"]):
        q = r["questions"]
        a, (b, h) = q["rappel_contexte"]["moyenne"], q["rappel_contexte"]["ic95"]
        e, (eb, eh) = q["ecart_rappel_vs_reference"]["moyenne"], q["ecart_rappel_vs_reference"]["ic95"]
        print(f"{nom:42} {100*a:5.1f} [{100*b:4.1f} ; {100*h:4.1f}] {100*e:+6.1f} [{100*eb:+5.1f} ; {100*eh:+5.1f}] "
              f"{q['ndcg10']['moyenne']:8.3f} {q['passages']['moyenne']:8.1f} {q['tokens']['moyenne']:7.0f} {q['tokens_max']:6d}")
    ch = resume["choix"]
    print("règle initiale :", ch["regle_initiale"]["retenue"], "; amendement A1 (retenu) :", ch["retenue"],
          "; éligibles A1 :", ", ".join(ch["amendement_a1"]["eligibles"]))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sous = parser.add_subparsers(dest="commande", required=True)
    sous.add_parser("preparer")
    r = sous.add_parser("reclasser")
    r.add_argument("cle", choices=sorted(rc.RECLASSEURS))
    g = sous.add_parser("grille")
    g.add_argument("--sans-reclasseur", action="store_true", help="n'évaluer que les configurations sans reclasseur")
    args = parser.parse_args(argv)
    if args.commande == "preparer":
        preparer()
    elif args.commande == "reclasser":
        reclasser(args.cle)
    else:
        grille(args.sans_reclasseur)
    return 0


if __name__ == "__main__":
    sys.exit(main())
