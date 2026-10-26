"""
Seuil S de l'état B2 du protocole de mesure du volet B (`docs/etudes/evaluation/06_protocole_volet_b.md`, section 7).

La population est celle du seuil du site (`cdtn_seuil.py`, protocole du notebook 03, section 8.2) : les variantes du
CDTN rédigées en question, issues des requêtes dont au moins une référence vise une fiche de notre corpus. Seul
l'encodage change. Les variantes sont encodées par E5 en fp32 sur processeur, exactement comme la question dans la
chaîne RAG de la PR #85 : même modèle et même révision, préfixe `query: `, normalisation L2, une question par appel
et aucune troncature. Le score d'une variante est le plus grand produit scalaire avec les vecteurs fp32 de l'index
du site (`front/public/index/`), celui que lit la #85. Le seuil vaut le 5e centile de ces scores, par interpolation
linéaire. En B2, le système s'abstient si le score de la question est strictement inférieur au seuil.

Les données du CDTN n'ont pas de licence : elles restent dans `data/` et ne sont jamais versionnées. Seuls le code et
des agrégats le sont.

Usage, depuis la racine du dépôt, avec l'environnement de `scripts/rag/requirements.txt` :
    HF_HUB_OFFLINE=1 python scripts/evaluation/seuil_b2.py calculer      # écrit data/evaluation/volet_b/seuil_b2.json
    python scripts/evaluation/seuil_b2.py incertitude                    # intervalle du seuil, par requête
"""

import hashlib
import json
import pathlib
import platform
import sys
from importlib.metadata import version

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cdtn_seuil import CENTILE, GRAINE, QUESTIONS, SOURCE, TIRAGES, empreinte_lot, sha256_fichier  # noqa: E402

RACINE = pathlib.Path(__file__).resolve().parents[2]
DOSSIER_INDEX = RACINE / "front" / "public" / "index"
SEUIL_SITE = RACINE / "data/evaluation/notebook03/seuil_cdtn.json"
RESULTAT = RACINE / "data/evaluation/volet_b/seuil_b2.json"
INCERTITUDE = RACINE / "data/evaluation/volet_b/incertitude_seuil_b2.json"

# Configuration de la chaîne RAG de la PR #85 (scripts/rag/rag.py, commit df91b85)
MODELE_E5 = "intfloat/multilingual-e5-small"
REVISION_E5 = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
BUDGET_E5 = 512
PREFIXE = "query: "
TOLERANCE_NORME = 1e-5
VARIANTES_ATTENDUES = 479   # population du seuil du site, figée le 10 octobre 2026


def charger_index():
    """Matrice fp32 de l'index du site, contrôlée comme dans la #85 : format, empreinte, forme, normes."""
    entete = json.loads((DOSSIER_INDEX / "index_m2.json").read_text(encoding="utf-8"))
    index, requete = entete["index"], entete["requete"]
    if entete.get("format") != "index-e5-v1" or index.get("moteur") != "PyTorch fp32 (intfloat/multilingual-e5-small)":
        raise ValueError("Index attendu : index-e5-v1, PyTorch fp32")
    if index.get("type") != "float32" or index.get("ordre_octets") != "little-endian":
        raise ValueError("Matrice attendue : float32 petit-boutiste")
    if requete.get("prefixe") != PREFIXE or requete.get("pooling") != "mean" or requete.get("normalize") is not True:
        raise ValueError("Configuration E5 attendue : query: , mean, normalisation L2")
    chemin = DOSSIER_INDEX / index["fichier"]
    if sha256_fichier(chemin) != index["sha256"]:
        raise ValueError("Empreinte de la matrice différente de l'en-tête")
    matrice = np.fromfile(chemin, dtype="<f4").reshape(index["nb_vecteurs"], index["dimension"])
    if not np.isfinite(matrice).all() or np.any(np.abs(np.linalg.norm(matrice, axis=1) - 1) >= TOLERANCE_NORME):
        raise ValueError("Vecteurs de l'index non finis ou non normalisés à 1 ± 1e-5")
    return matrice, index


def charger_questions():
    lot = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    questions = lot["questions"]
    if lot.get("prefixe") != PREFIXE or empreinte_lot(questions) != lot.get("empreinte"):
        raise ValueError("Lot du CDTN incohérent avec son empreinte ou son préfixe")
    site = json.loads(SEUIL_SITE.read_text(encoding="utf-8"))
    if site["empreinte_questions"] != lot["empreinte"] or len(questions) != VARIANTES_ATTENDUES:
        raise ValueError("Population différente de celle du seuil du site")
    return questions, lot["empreinte"], site["seuil"]


def charger_encodeur():
    """Même chargement que la #85 : Sentence Transformers, révision figée, processeur, fp32."""
    from sentence_transformers import SentenceTransformer
    modele = SentenceTransformer(MODELE_E5, revision=REVISION_E5, device="cpu")
    modele.float()
    modele.eval()
    modele.max_seq_length = BUDGET_E5
    return modele


def encoder(modele, texte):
    """Même calcul que `encoder_question` de la #85 : une question par appel, sans troncature."""
    entree = PREFIXE + texte
    if len(modele.tokenizer(entree, truncation=False)["input_ids"]) > BUDGET_E5:
        raise ValueError(f"Variante de plus de {BUDGET_E5} tokens E5")
    sortie = np.asarray(modele.encode([entree], batch_size=32, normalize_embeddings=True,
                                      convert_to_numpy=True, show_progress_bar=False), dtype=np.float32)
    if sortie.shape != (1, 384) or abs(float(np.linalg.norm(sortie[0])) - 1) >= TOLERANCE_NORME:
        raise ValueError("Vecteur de forme ou de norme inattendue")
    return sortie[0]


def calculer():
    matrice, index = charger_index()
    questions, empreinte, seuil_site = charger_questions()
    modele = charger_encodeur()
    scores = np.array([float((matrice @ encoder(modele, q["texte"])).max()) for q in questions])
    seuil = float(np.percentile(scores, CENTILE))   # interpolation linéaire, méthode par défaut de NumPy
    resultat = {
        "seuil": seuil, "centile": CENTILE, "interpolation": "linéaire (numpy.percentile par défaut)",
        "regle_b2": "abstention si le score de la question est strictement inférieur au seuil",
        "variantes": len(scores), "requetes": len({q["id"].split("-")[0] for q in questions}),
        "sous_le_seuil": int((scores < seuil).sum()),
        "population": "celle de cdtn_seuil.py : variantes contenant « ? », des requêtes dont une référence vise "
                      "une fiche du corpus par identifiant exact",
        "source": SOURCE, "empreinte_questions": empreinte,
        "encodage": {"modele": MODELE_E5, "revision": REVISION_E5, "appareil": "cpu", "dtype": "float32",
                     "prefixe": PREFIXE, "normalisation": "L2", "par_appel": 1, "troncature": "aucune",
                     "budget_tokens": BUDGET_E5,
                     "versions": {p: version(p) for p in ("sentence-transformers", "transformers", "torch", "numpy")},
                     "python": platform.python_version(), "machine": platform.machine()},
        "index": {"fichier": f"front/public/index/{index['fichier']}", "sha256": index["sha256"],
                  "vecteurs": index["nb_vecteurs"]},
        "scores": {"min": float(scores.min()), "mediane": float(np.median(scores)), "max": float(scores.max())},
        "seuil_site_q8": seuil_site,
        "scores_par_variante": [{"id": q["id"], "score": s} for q, s in zip(questions, scores.tolist())],
    }
    RESULTAT.parent.mkdir(parents=True, exist_ok=True)
    RESULTAT.write_text(json.dumps(resultat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"seuil S = {seuil:.4f} (5e centile de {len(scores)} scores maximaux, {resultat['sous_le_seuil']} "
          f"sous le seuil) ; seuil du site en q8 : {seuil_site:.4f}")
    print(f"écrit dans {RESULTAT.relative_to(RACINE)}, SHA-256 {sha256_fichier(RESULTAT)}")


def incertitude():
    """Intervalle à 95 % du seuil, par rééchantillonnage des requêtes, comme `cdtn_seuil.py`. N'écrit jamais dans
    le fichier du seuil."""
    r = json.loads(RESULTAT.read_text(encoding="utf-8"))
    scores = np.array([x["score"] for x in r["scores_par_variante"]])
    requetes = np.array([x["id"].split("-")[0] for x in r["scores_par_variante"]])
    noms = np.unique(requetes)
    par_requete = [scores[requetes == x] for x in noms]
    rng = np.random.default_rng(GRAINE)
    tirages = np.array([np.percentile(np.concatenate([par_requete[i] for i in rng.integers(0, len(noms), len(noms))]),
                                      CENTILE) for _ in range(TIRAGES)])
    res = {"seuil": r["seuil"], "ic95_requetes": [float(np.percentile(tirages, 2.5)), float(np.percentile(tirages, 97.5))],
           "requetes": len(noms), "variantes": len(scores), "tirages": TIRAGES, "graine": GRAINE,
           "sha256_resultat": sha256_fichier(RESULTAT)}
    INCERTITUDE.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False))


def sanity_check():
    """Contrôles calculés à la main."""
    # 5e centile linéaire de 0, 1, ..., 20 : position 0,05 x 20 = 1, donc 1
    assert float(np.percentile(np.arange(21.0), CENTILE)) == 1.0
    # 5e centile linéaire de 0, 10, 20, 30 : position 0,05 x 3 = 0,15, donc 1,5
    assert abs(float(np.percentile(np.array([0.0, 10.0, 20.0, 30.0]), CENTILE)) - 1.5) < 1e-12
    # strictement inférieur : un score égal au seuil n'est pas rejeté
    assert not (np.float32(0.85) < float(np.float32(0.85)))
    return True


if __name__ == "__main__":
    assert sanity_check()
    {"calculer": calculer, "incertitude": incertitude}[sys.argv[1]]()
