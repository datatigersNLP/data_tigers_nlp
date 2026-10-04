"""
Validation de la chaîne de mesure de recherche d'information sur le jeu PIAF (Issue #45).

Ce script :
1. Télécharge et fige le jeu public français PIAF (AgentPublic/piaf) et le modèle, chacun sur une révision.
2. Extrait les 761 contextes uniques et les 3 835 questions associées.
3. Évalue les approches de récupération :
   - Aléatoire (baseline probabiliste), avec son espérance exacte
   - BM25, en quatre variantes : rank_bm25 par défaut, formule de Lucene, mots vides Snowball, racinisation
   - Dense E5 (intfloat/multilingual-e5-small avec préfixes 'passage: ' et 'query: ')
4. Recalcule chaque rang indépendamment, depuis la matrice de scores complète, et le confronte au module.
5. Calcule Recall@1, Recall@3, Recall@5, Recall@10 et MRR@10.
6. Compare E5 à chaque variante de BM25 : test exact de McNemar, puis différence, intervalle et test qui tiennent
   compte des questions groupées par contexte et par article.
7. Décrit les cas discordants par leur recouvrement lexical, et en tire des exemples au hasard.
8. Sauvegarde les résultats bruts et le résumé pour le rapport.

Dépendances : scripts/evaluation/requirements.txt. Depuis la racine du dépôt :
    python scripts/evaluation/01_valider_sur_piaf.py
"""

import csv
import hashlib
import json
import re
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from scipy import sparse
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import snowballstemmer

# Import local du module de métriques validé
sys.path.insert(0, str(Path(__file__).resolve().parent))
from metrics import (evaluate_retrieval, compute_mcnemar_test, sanity_check_manual_examples, rank_by_score,
                     proportion_ci)

# --- Constantes et reproductibilité ---
DATASET_ID = "AgentPublic/piaf"
DATASET_REVISION = "bda8c063bc7297180796cd835d1974c0bc71c521"
MODEL_ID = "intfloat/multilingual-e5-small"
MODEL_REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"  # celle du notebook 02
PREFIXE_PASSAGE = "passage: "
PREFIXE_REQUETE = "query: "
BATCH_SIZE = 32
RANDOM_SEED = 42
K_VALUES = (1, 3, 5, 10)
DEPTH = 10  # longueur des listes évaluées : le MRR calculé est le MRR@10

# liste française du projet Snowball, figée sur le même commit que le notebook 01
MOTS_VIDES_URL = ("https://raw.githubusercontent.com/snowballstem/snowball-website/"
                  "5a8cf2451d108217585d8e32d744f8b8fd20c711/algorithms/french/stop.txt")
MOTS_VIDES_SHA256 = "e235f5e633bf831c601ce6f1dc87d8608c038209a7aab64e69a9e70f52f83d4c"

# chemins ancrés à la racine du dépôt, quel que soit le dossier de lancement
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data" / "evaluation" / "piaf"


def simple_tokenize(text: str) -> List[str]:
    """Tokenisation lexicale robuste en minuscules pour BM25."""
    return re.findall(r"\w+", text.lower(), re.UNICODE)


def load_stopwords() -> set:
    """Liste Snowball, téléchargée une fois, refusée si son empreinte diffère de celle du notebook 01."""
    fichier = OUTPUT_DIR / "mots_vides_snowball.txt"
    if not fichier.exists():
        urllib.request.urlretrieve(MOTS_VIDES_URL, fichier)
    if hashlib.sha256(fichier.read_bytes()).hexdigest() != MOTS_VIDES_SHA256:
        raise RuntimeError(f"Empreinte inattendue pour {fichier}")
    # un mot en début de ligne, commentaire après une barre verticale
    return {ligne.split("|")[0].strip() for ligne in fichier.read_text(encoding="utf-8").splitlines()} - {""}


def bm25_scores(docs: List[List[str]], queries: List[List[str]], k1: float, b: float,
                idf: str = "lucene", epsilon: float = 0.25) -> np.ndarray:
    """
    Matrice des scores BM25 (questions x passages), calculée en une multiplication de matrices creuses.

    idf="lucene" : log(1 + (N - n_t + 0,5) / (n_t + 0,5)), toujours positif (formule de Lucene).
    idf="atire" : log((N - n_t + 0,5) / (n_t + 0,5)), dont les valeurs négatives (termes présents dans plus de la
    moitié des passages) sont remplacées par epsilon fois l'idf moyen : c'est la formule de BM25Okapi (rank_bm25).
    Un terme répété dans la question compte autant de fois, comme dans rank_bm25.
    """
    vocab: Dict[str, int] = {}
    rows, cols, vals = [], [], []
    for j, doc in enumerate(docs):
        for terme, tf in Counter(doc).items():
            rows.append(vocab.setdefault(terme, len(vocab)))
            cols.append(j)
            vals.append(tf)
    n_docs = len(docs)
    tf = sparse.csr_matrix((np.array(vals, dtype=np.float64), (rows, cols)), shape=(len(vocab), n_docs))
    n_t = np.diff(tf.indptr)  # nombre de passages qui contiennent chaque terme
    if idf == "lucene":
        idf_t = np.log(1 + (n_docs - n_t + 0.5) / (n_t + 0.5))
    else:
        brut = np.log(n_docs - n_t + 0.5) - np.log(n_t + 0.5)
        idf_t = np.where(brut < 0, epsilon * brut.mean(), brut)
    dl = np.array([len(doc) for doc in docs], dtype=np.float64)
    norm = k1 * (1 - b + b * dl / dl.mean())
    poids = tf.tocoo()
    poids = sparse.csr_matrix((idf_t[poids.row] * poids.data * (k1 + 1) / (poids.data + norm[poids.col]),
                               (poids.row, poids.col)), shape=tf.shape)
    q_rows, q_cols, q_vals = [], [], []
    for i, q in enumerate(queries):
        for terme, f in Counter(t for t in q if t in vocab).items():
            q_rows.append(i)
            q_cols.append(vocab[terme])
            q_vals.append(f)
    requetes = sparse.csr_matrix((q_vals, (q_rows, q_cols)), shape=(len(queries), len(vocab)))
    return (requetes @ poids).toarray()


def rank_bounds(scores: np.ndarray, targets: np.ndarray):
    """Rang de la cible, sans passer par aucun tri : ex aequo comptés pour elle (bas), puis contre elle (haut)."""
    cible = scores[np.arange(len(targets)), targets][:, None]
    return 1 + (scores > cible).sum(axis=1), (scores >= cible).sum(axis=1)


def run_benchmark():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 70)
    print("Étape 1 : Contrôle préliminaire des métriques unitaires")
    print("=" * 70)
    sanity_check_manual_examples()
    print("-> Tests unitaires des formules mathématiques : VALIDÉS.\n")

    print("=" * 70)
    print(f"Étape 2 : Chargement du dataset {DATASET_ID} (révision {DATASET_REVISION[:8]})")
    print("=" * 70)
    dataset = load_dataset(DATASET_ID, split="train", revision=DATASET_REVISION)
    print(f"Total entrées brutes : {len(dataset)}")

    # Extraction des contextes uniques, dans l'ordre de première apparition (ordre déterministe)
    context_to_id: Dict[str, int] = {}
    doc_titles: Dict[int, str] = {}
    queries: List[str] = []
    ground_truth_doc_ids: List[int] = []
    question_ids: List[str] = []
    articles: List[str] = []

    for item in dataset:
        ctx = item["context"].strip()
        if ctx not in context_to_id:
            context_to_id[ctx] = len(context_to_id)
            doc_titles[context_to_id[ctx]] = item["title"]
        queries.append(item["question"].strip())
        ground_truth_doc_ids.append(context_to_id[ctx])
        question_ids.append(item["id"])
        articles.append(item["title"])

    passages_list = list(context_to_id)
    n_passages = len(passages_list)
    n_queries = len(queries)
    targets = np.array(ground_truth_doc_ids)
    print(f"Nombre de contextes uniques (passages) : {n_passages}")
    print(f"Nombre de requêtes d'évaluation : {n_queries}")
    print(f"Nombre d'articles Wikipédia : {len(set(articles))}")
    assert n_passages == 761, f"Attendu 761 contextes, obtenu {n_passages}"
    assert n_queries == 3835, f"Attendu 3835 requêtes, obtenu {n_queries}"
    assert len(set(question_ids)) == n_queries, "Identifiants de questions en double"
    # les questions ne sont pas indépendantes : plusieurs par contexte, et plusieurs contextes par article
    par_contexte = Counter(ground_truth_doc_ids)
    print(f"Questions par contexte : {min(par_contexte.values())} à {max(par_contexte.values())}, "
          f"{n_queries / n_passages:.2f} en moyenne ; par article : {n_queries / len(set(articles)):.1f} en moyenne")

    # --- 1. Baseline Aléatoire ---
    print("\n" + "=" * 70)
    print("Étape 3 : Baseline 1 : Tirage Aléatoire (Random)")
    print("=" * 70)
    rng = np.random.default_rng(RANDOM_SEED)
    random_preds: List[List[int]] = [
        rng.permutation(n_passages)[:DEPTH].tolist()
        for _ in range(n_queries)
    ]
    random_results = evaluate_retrieval(random_preds, ground_truth_doc_ids, K_VALUES)
    # espérance exacte : la cible est à chaque rang avec la probabilité 1 / N
    random_expected = {f"recall@{k}": k / n_passages for k in K_VALUES}
    random_expected["mrr"] = sum(1 / r for r in range(1, DEPTH + 1)) / n_passages
    print(f"Random (tirage)   - Recall@1: {random_results['recall@1']:.4f} | Recall@5: {random_results['recall@5']:.4f}"
          f" | MRR@10: {random_results['mrr']:.4f}")
    print(f"Random (espérance) - Recall@1: {random_expected['recall@1']:.4f} | Recall@5: {random_expected['recall@5']:.4f}"
          f" | MRR@10: {random_expected['mrr']:.4f}")

    # --- 2. Baselines lexicales BM25 ---
    print("\n" + "=" * 70)
    print("Étape 4 : Baseline 2 : BM25, quatre variantes")
    print("=" * 70)
    tokenized_corpus = [simple_tokenize(p) for p in passages_list]
    tokenized_queries = [simple_tokenize(q) for q in queries]

    # V0, la référence d'origine : rank_bm25 avec ses réglages par défaut (k1 = 1,5 ; b = 0,75 ; epsilon = 0,25)
    bm25 = BM25Okapi(tokenized_corpus)
    t0_bm25_query = time.time()
    scores_v0 = np.vstack([bm25.get_scores(q) for q in tokenized_queries])
    avg_bm25_ms = (time.time() - t0_bm25_query) / n_queries * 1000
    # la réimplantation reproduit rank_bm25 avant de servir aux autres variantes
    ecart = np.abs(bm25_scores(tokenized_corpus, tokenized_queries, 1.5, 0.75, idf="atire") - scores_v0).max()
    assert ecart < 1e-9, f"La réimplantation de BM25 s'écarte de rank_bm25 : {ecart}"
    print(f"Réimplantation de BM25 conforme à rank_bm25 (écart maximal {ecart:.1e})")

    stopwords = load_stopwords()
    stemmer = snowballstemmer.stemmer("french")

    def sans_mots_vides(tokens):
        return [t for t in tokens if t not in stopwords]

    def racinise(tokens):
        return stemmer.stemWords(sans_mots_vides(tokens))

    systems: Dict[str, np.ndarray] = {"BM25 V0 (rank_bm25)": scores_v0}
    systems["BM25 V1 (Lucene)"] = bm25_scores(tokenized_corpus, tokenized_queries, 1.2, 0.75)
    systems["BM25 V2 (+ mots vides)"] = bm25_scores([sans_mots_vides(t) for t in tokenized_corpus],
                                                    [sans_mots_vides(t) for t in tokenized_queries], 1.2, 0.75)
    systems["BM25 V3 (+ racinisation)"] = bm25_scores([racinise(t) for t in tokenized_corpus],
                                                      [racinise(t) for t in tokenized_queries], 1.2, 0.75)
    print(f"Mots vides Snowball : {len(stopwords)} ; temps moyen BM25 V0 : {avg_bm25_ms:.2f} ms/requête (séquentiel)")

    # --- 3. Dense E5 (multilingual-e5-small) ---
    print("\n" + "=" * 70)
    print(f"Étape 5 : Méthode Dense, {MODEL_ID} (révision {MODEL_REVISION[:8]})")
    print("=" * 70)
    model = SentenceTransformer(MODEL_ID, revision=MODEL_REVISION, device="cpu")
    longest = max(len(model.tokenizer(PREFIXE_PASSAGE + p)["input_ids"]) for p in passages_list)
    assert longest <= model.max_seq_length, "Un passage serait tronqué par l'encodeur"
    print(f"Passage le plus long : {longest} tokens, budget {model.max_seq_length} : aucune troncature")

    passage_embeddings = model.encode(
        [PREFIXE_PASSAGE + p for p in passages_list],
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True
    ).astype(np.float32)
    t0_enc_queries = time.time()
    query_embeddings = model.encode(
        [PREFIXE_REQUETE + q for q in queries],
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True
    ).astype(np.float32)
    avg_e5_ms = (time.time() - t0_enc_queries) / n_queries * 1000
    assert np.allclose(np.linalg.norm(passage_embeddings, axis=1), 1.0, atol=1e-4)
    assert np.allclose(np.linalg.norm(query_embeddings, axis=1), 1.0, atol=1e-4)
    print(f"Encodage des requêtes : {avg_e5_ms:.2f} ms/requête (par lots de {BATCH_SIZE}, sans la recherche)")
    # S = Q (3835, 384) x P^T (384, 761) : produit scalaire, égal au cosinus pour des vecteurs normalisés
    systems["Dense E5"] = query_embeddings @ passage_embeddings.T

    # --- 4. Classements, métriques et recalcul indépendant des rangs ---
    print("\n" + "=" * 70)
    print("Étape 6 : Métriques et recalcul indépendant des rangs")
    print("=" * 70)
    preds: Dict[str, List[List[int]]] = {"Aléatoire": random_preds}
    results: Dict[str, Dict[str, float]] = {"Aléatoire": random_results}
    ranks: Dict[str, np.ndarray] = {}
    ties: Dict[str, int] = {}
    for name, scores in systems.items():
        preds[name] = [rank_by_score(row, DEPTH).tolist() for row in scores]
        results[name] = evaluate_retrieval(preds[name], ground_truth_doc_ids, K_VALUES)
        low, high = rank_bounds(scores, targets)
        rank = np.array([p.index(t) + 1 if t in p else np.inf for p, t in zip(preds[name], ground_truth_doc_ids)])
        # le rang lu dans la liste doit tomber dans l'intervalle des ex aequo, sinon le tri est faux
        assert np.all(((rank >= low) & (rank <= high)) | (np.isinf(rank) & (high > DEPTH))), name
        for k in K_VALUES:
            assert results[name][f"recall@{k}"] == np.mean(rank <= k), (name, k)
        ranks[name] = rank
        ties[name] = int(np.sum(high > low))
        print(f"{name:<26} cible à égalité de score avec un autre passage : {ties[name]} questions")
    print("-> Les métriques du module coïncident avec les rangs recalculés sans tri.")

    # --- 5. Tests appariés (E5 contre chaque variante de BM25) ---
    print("\n" + "=" * 70)
    print("Étape 7 : Comparaisons appariées E5 contre BM25")
    print("=" * 70)
    comparisons: Dict[str, Any] = {}
    for name in [s for s in systems if s.startswith("BM25")]:
        for k in (1, 5, 10):
            key = f"E5 vs {name[:7]} R@{k}"
            comparisons[key] = {
                "independantes": compute_mcnemar_test(preds["Dense E5"], preds[name], ground_truth_doc_ids, k=k),
                "par_contexte": compute_mcnemar_test(preds["Dense E5"], preds[name], ground_truth_doc_ids, k=k,
                                                     groups=ground_truth_doc_ids),
                "par_article": compute_mcnemar_test(preds["Dense E5"], preds[name], ground_truth_doc_ids, k=k,
                                                    groups=articles),
            }
            c = comparisons[key]
            lo, hi = c["par_article"]["ci_difference"]
            print(f"{key:<22} écart {100 * c['independantes']['difference']:+5.2f} pts, "
                  f"IC 95 % par article [{100 * lo:+.2f} ; {100 * hi:+.2f}], "
                  f"p exact {c['independantes']['p_value']:.1e}, p par contexte {c['par_contexte']['p_value_groups']:.1e}, "
                  f"p par article {c['par_article']['p_value_groups']:.1e}")
    mcnemar_r5 = comparisons["E5 vs BM25 V0 R@5"]["independantes"]
    print(f"Table de contingence (E5 vs BM25 V0, Recall@5) : {mcnemar_r5['contingency_table']}")
    print(f"Statistique Chi2 (Edwards) : {mcnemar_r5['chi2_statistic']:.2f}")

    # intervalles de Recall@5 par système, questions groupées par article
    ci_r5 = {name: proportion_ci(ranks[name] <= 5, groups=articles) for name in systems}

    # --- 6. Cas discordants : recouvrement lexical et exemples tirés au hasard ---
    print("\n" + "=" * 70)
    print("Étape 8 : Analyse des cas discordants (Recall@5, E5 contre BM25 V0)")
    print("=" * 70)

    def recouvrement(i: int) -> float:
        """Part des mots de la question, hors mots vides, présents dans le contexte cible."""
        mots = set(sans_mots_vides(tokenized_queries[i]))
        return len(mots & set(tokenized_corpus[targets[i]])) / max(1, len(mots))

    overlap = np.array([recouvrement(i) for i in range(n_queries)])
    e5_ok, bm_ok = ranks["Dense E5"] <= 5, ranks["BM25 V0 (rank_bm25)"] <= 5
    categories = {"deux succès": e5_ok & bm_ok, "E5 seul": e5_ok & ~bm_ok,
                  "BM25 seul": ~e5_ok & bm_ok, "deux échecs": ~e5_ok & ~bm_ok}
    overlap_summary = {name: {"n": int(m.sum()), "mediane": float(np.median(overlap[m])),
                              "moyenne": float(overlap[m].mean())} for name, m in categories.items()}
    for name, o in overlap_summary.items():
        print(f"{name:<12} {o['n']:>5} questions, recouvrement médian {o['mediane']:.2f}, moyen {o['moyenne']:.2f}")

    def show_rank(r: float):
        return int(r) if np.isfinite(r) else f">{DEPTH}"

    pick = np.random.default_rng(RANDOM_SEED)
    qualitative_samples = []
    for name in ("E5 seul", "BM25 seul"):
        for idx in pick.choice(np.flatnonzero(categories[name]), size=3, replace=False):
            info = {
                "categorie": name,
                "query": queries[idx],
                "target_title": doc_titles[targets[idx]],
                "dense_rank": show_rank(ranks["Dense E5"][idx]),
                "bm25_rank": show_rank(ranks["BM25 V0 (rank_bm25)"][idx]),
                "recouvrement": round(float(overlap[idx]), 2),
            }
            qualitative_samples.append(info)
            print(f"[{name}] Q: '{info['query']}' (Doc: {info['target_title']}) -> Rang E5: {info['dense_rank']} | "
                  f"Rang BM25: {info['bm25_rank']} | recouvrement {info['recouvrement']}")

    # --- Synthèse et sauvegarde ---
    summary = {
        "dataset": {
            "name": DATASET_ID,
            "revision": DATASET_REVISION,
            "n_passages": n_passages,
            "n_queries": n_queries,
            "n_articles": len(set(articles)),
        },
        "model": {"name": MODEL_ID, "revision": MODEL_REVISION, "passage_le_plus_long_tokens": longest},
        "metrics": results,
        "random_expected": random_expected,
        "ties": ties,
        "recall5_ci95_par_article": ci_r5,
        "comparisons": comparisons,
        "timing": {
            "bm25_v0_ms_par_requete_sequentiel": avg_bm25_ms,
            "dense_e5_ms_par_requete_par_lots": avg_e5_ms,
        },
        "overlap": overlap_summary,
        "qualitative_samples": qualitative_samples,
    }

    results_file = OUTPUT_DIR / "resultats_benchmark.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=float)
    # rangs par question, pour tout recalcul ou toute analyse ultérieure
    with open(OUTPUT_DIR / "rangs_par_question.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["question_id", "article", "contexte"] + list(systems))
        for i in range(n_queries):
            w.writerow([question_ids[i], articles[i], ground_truth_doc_ids[i]]
                       + [show_rank(ranks[s][i]) for s in systems])
    print(f"\nRésultats complets sauvegardés dans : {results_file}")

    # Affichage du tableau récapitulatif final
    print("\n" + "=" * 86)
    print("TABLEAU RÉCAPITULATIF DES RÉSULTATS (PIAF)")
    print("=" * 86)
    print(f"{'Méthode':<28} | {'Recall@1':<9} | {'Recall@3':<9} | {'Recall@5':<9} | {'Recall@10':<9} | {'MRR@10':<9}")
    print("-" * 86)
    rows = [("Aléatoire (espérance)", random_expected)] + list(results.items())
    for name, r in rows:
        print(f"{name:<28} | {r['recall@1']:<9.4f} | {r['recall@3']:<9.4f} | {r['recall@5']:<9.4f} | "
              f"{r['recall@10']:<9.4f} | {r['mrr']:<9.4f}")
    print("=" * 86)


if __name__ == "__main__":
    run_benchmark()
