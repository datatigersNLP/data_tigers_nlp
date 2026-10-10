"""
Seuil d'abstention du notebook 03 tiré des requêtes du CDTN (protocole, section 8.2 ; décision 3 du Weekly 4).

Le seuil vaut le 5e centile des scores maximaux, c'est-à-dire du plus grand cosinus avec les passages M2 pour
l'encodeur servi (q8, dans le navigateur), des variantes du CDTN rédigées en question. Seules comptent les
variantes des requêtes dont au moins une référence vise une fiche de notre corpus, reconnue par son identifiant
exact : les autres requêtes renvoient à des sources absentes de notre corpus et feraient baisser le seuil.

Les données du CDTN n'ont pas de licence : elles ne sont jamais versionnées. Le script les lit dans `data/`,
au commit figé, après contrôle de leur empreinte ; seuls le code et des identifiants de variantes le sont.

Usage, depuis la racine du dépôt :
    python scripts/evaluation/cdtn_seuil.py preparer   # écrit data/evaluation/cdtn/questions_cdtn.json
    (page scripts/evaluation/encodage_navigateur.html?lot=cdtn, résultat dans data/evaluation/cdtn/vecteurs_cdtn.json)
    python scripts/evaluation/cdtn_seuil.py calculer   # écrit data/evaluation/notebook03/seuil_cdtn.json
"""

import hashlib
import json
import pathlib
import sys

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[2]
SOURCE = {
    "depot": "SocialGouv/datafiller-data",
    "commit": "6d16869c5241b8b7d571920462c034ee3976318e",
    "chemin": "data/requests.json",
    "sha256": "02ee32bfb6359bc5d061b769fd10e42a0b288d441381c725fddbd3a64d579a7c",
}
FICHIER_SOURCE = RACINE / "data/evaluation/cdtn/requests_6d16869.json"
QUESTIONS = RACINE / "data/evaluation/cdtn/questions_cdtn.json"
VECTEURS = RACINE / "data/evaluation/cdtn/vecteurs_cdtn.json"
SEUIL = RACINE / "data/evaluation/notebook03/seuil_cdtn.json"
PREFIXE_FICHE = "/fiche-ministere-travail/"
PREFIXE_REQUETE = "query: "
CENTILE = 5


def sha256_fichier(chemin):
    return hashlib.sha256(pathlib.Path(chemin).read_bytes()).hexdigest()


def identifiant_fiche(url_cdtn):
    """Identifiant d'une fiche du ministère dans une référence du CDTN, sans l'ancre de section ; None sinon."""
    if not url_cdtn.startswith(PREFIXE_FICHE):
        return None
    return url_cdtn[len(PREFIXE_FICHE):].split("#", 1)[0]


def est_question(variante):
    """Règle du 4 octobre (#56) : une variante est rédigée en question si elle contient un point d'interrogation."""
    return "?" in variante


def selectionner(requetes, identifiants_corpus):
    """Variantes retenues, avec leur identifiant stable « R<requête>-V<variante> » (positions dans la source)."""
    retenues = []
    for i, req in enumerate(requetes):
        fiches = {identifiant_fiche(r["url"]) for r in req["refs"]} - {None}
        if not fiches & identifiants_corpus:
            continue
        for j, v in enumerate(req["variants"]):
            if est_question(v):
                retenues.append({"id": f"R{i:03d}-V{j:02d}", "texte": v})
    return retenues


def empreinte_lot(questions):
    """Même calcul que le notebook 03 et la page du navigateur : SHA-256 du JSON compact des questions."""
    return hashlib.sha256(json.dumps(questions, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def charger_m2():
    """Vecteurs M2 du notebook 02, contrôlés comme dans le notebook 03 : empreinte, alignement, normes."""
    variantes = json.loads((RACINE / "data/indexation/variantes/variantes.json").read_text(encoding="utf-8"))
    v = variantes["m2"]
    chemin = RACINE / "data/indexation/variantes" / v["index"]
    if sha256_fichier(chemin) != v["sha256_index"]:
        raise ValueError("Empreinte de l'index M2 différente de variantes.json.")
    entete = json.loads((RACINE / "data/indexation/site/index_m2.json").read_text(encoding="utf-8"))
    if entete["index"]["sha256"] != v["sha256_index"]:
        raise ValueError("L'index M2 n'est pas celui du site.")
    E = np.fromfile(chemin, dtype="<f4").reshape(v["nb_vecteurs"], 384)
    if not np.allclose(np.linalg.norm(E, axis=1), 1.0, atol=1e-4):
        raise ValueError("Vecteurs M2 non normalisés.")
    return E, entete


def identifiants_corpus():
    manifeste = json.loads((RACINE / "data/decoupage/passages/manifeste.json").read_text(encoding="utf-8"))
    info = manifeste["methodes"]["m2"]
    chemin = RACINE / info["fichier"]
    if sha256_fichier(chemin) != info["sha256_fichier"]:
        raise ValueError("Empreinte des passages M2 différente du manifeste.")
    return {u.rstrip("/").rsplit("/", 1)[1] for u in pd.read_parquet(chemin)["url"]}


def preparer():
    if sha256_fichier(FICHIER_SOURCE) != SOURCE["sha256"]:
        raise ValueError("Empreinte de la source du CDTN différente de celle figée dans #56.")
    requetes = json.loads(FICHIER_SOURCE.read_text(encoding="utf-8"))
    retenues = selectionner(requetes, identifiants_corpus())
    n_req = len({q["id"].split("-")[0] for q in retenues})
    QUESTIONS.write_text(json.dumps({"prefixe": PREFIXE_REQUETE, "empreinte": empreinte_lot(retenues),
                                     "questions": retenues}, ensure_ascii=False), encoding="utf-8")
    print(f"{len(retenues)} variantes rédigées en question, issues de {n_req} requêtes, écrites dans "
          f"{QUESTIONS.relative_to(RACINE)} (empreinte {empreinte_lot(retenues)[:16]}...)")


def calculer():
    lot = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    r = json.loads(VECTEURS.read_text(encoding="utf-8"))
    E, entete = charger_m2()
    attendu = {"depot": entete["modele"]["depot"], "revision": entete["modele"]["revision"],
               "dtype": entete["modele"]["dtype"], "prefixe": PREFIXE_REQUETE,
               "empreinte_questions": empreinte_lot(lot["questions"]),
               "identifiants": [q["id"] for q in lot["questions"]]}
    ecarts = [k for k, v in attendu.items() if r.get(k) != v]
    if ecarts:
        raise ValueError(f"Vecteurs du navigateur incohérents avec le lot ou le site : {ecarts}")
    U = np.array(r["vecteurs"], dtype=np.float32)
    if U.shape != (len(lot["questions"]), 384) or not np.allclose(np.linalg.norm(U, axis=1), 1.0, atol=1e-3):
        raise ValueError("Vecteurs du navigateur de forme ou de norme inattendue.")
    scores = (U @ E.T).max(axis=1)
    seuil = float(np.percentile(scores, CENTILE))   # interpolation linéaire, méthode par défaut de NumPy
    resultat = {
        "seuil": seuil, "centile": CENTILE, "interpolation": "linéaire (numpy.percentile par défaut)",
        "variantes": len(scores), "requetes": len({q["id"].split("-")[0] for q in lot["questions"]}),
        "regle": "variantes contenant « ? », des requêtes dont une référence vise une fiche du corpus par "
                 "identifiant exact ; score = plus grand cosinus avec les passages M2, encodeur servi (q8)",
        "source": SOURCE, "empreinte_questions": attendu["empreinte_questions"],
        "modele": {k: attendu[k] for k in ("depot", "revision", "dtype")},
        "navigateur": r.get("navigateur"), "transformers_js": r.get("transformers_js"),
        "scores": {"min": float(scores.min()), "mediane": float(np.median(scores)), "max": float(scores.max())},
    }
    SEUIL.write_text(json.dumps(resultat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"seuil = {seuil:.4f} (5e centile de {len(scores)} scores maximaux) écrit dans {SEUIL.relative_to(RACINE)}")


def sanity_check():
    """Contrôles calculés à la main."""
    assert identifiant_fiche("/fiche-ministere-travail/la-demission#Faut-il") == "la-demission"
    assert identifiant_fiche("/fiche-service-public/la-demission") is None
    assert est_question("Puis-je démissionner ?") and not est_question("démission préavis")
    source = [
        {"title": "a", "variants": ["x ?", "y"], "refs": [{"url": "/fiche-ministere-travail/f1#s"}]},
        {"title": "b", "variants": ["z ?"], "refs": [{"url": "/fiche-service-public/f1"}]},
        {"title": "c", "variants": ["t", "u ?", "w ?"], "refs": [{"url": "/code-du-travail/l1"},
                                                                {"url": "/fiche-ministere-travail/f2"}]},
    ]
    assert selectionner(source, {"f1", "f2"}) == [{"id": "R000-V00", "texte": "x ?"},
                                                  {"id": "R002-V01", "texte": "u ?"},
                                                  {"id": "R002-V02", "texte": "w ?"}]
    assert selectionner(source, {"f2"}) == [{"id": "R002-V01", "texte": "u ?"}, {"id": "R002-V02", "texte": "w ?"}]
    # empreinte : identique au calcul du notebook 03 sur le même texte JSON compact
    assert empreinte_lot([{"id": "a", "texte": "é"}]) == hashlib.sha256('[{"id":"a","texte":"é"}]'.encode()).hexdigest()
    # 5e centile linéaire de 0, 1, ..., 20 : position 0,05 x 20 = 1, donc 1
    assert float(np.percentile(np.arange(21.0), CENTILE)) == 1.0
    return True


if __name__ == "__main__":
    assert sanity_check()
    {"preparer": preparer, "calculer": calculer}[sys.argv[1]]()
