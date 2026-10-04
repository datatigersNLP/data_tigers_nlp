"""
Validation de la chaîne de mesure de recherche d'information sur le jeu PIAF (Issue #45).

Ce script :
1. Télécharge et fige le jeu public français PIAF (AgentPublic/piaf).
2. Extrait les 761 contextes uniques et les 3 835 questions associées.
3. Évalue 3 approches de récupération :
   - Aléatoire (baseline probabiliste)
   - BM25 (référence lexicale via rank_bm25)
   - Dense E5 (intfloat/multilingual-e5-small avec préfixes 'passage: ' et 'query: ')
4. Calcule Recall@1, Recall@3, Recall@5, Recall@10 et MRR.
5. Effectue le test statistique apparié de McNemar entre E5 et BM25 sur le Recall@5.
6. Sauvegarde les résultats bruts et le résumé pour le rapport.
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from typing import List, Dict, Tuple, Any

import numpy as np
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# Import local du module de métriques validé
sys.path.insert(0, str(Path(__file__).resolve().parent))
from metrics import evaluate_retrieval, compute_mcnemar_test, sanity_check_manual_examples

# --- Constantes et reproductibilité ---
DATASET_ID = "AgentPublic/piaf"
DATASET_REVISION = "bda8c063bc7297180796cd835d1974c0bc71c521"
MODEL_ID = "intfloat/multilingual-e5-small"
PREFIXE_PASSAGE = "passage: "
PREFIXE_REQUETE = "query: "
BATCH_SIZE = 32
RANDOM_SEED = 42

OUTPUT_DIR = Path("data/evaluation/piaf")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def simple_tokenize(text: str) -> List[str]:
    """Tokenisation lexicale robuste en minuscules pour BM25."""
    return re.findall(r"\w+", text.lower(), re.UNICODE)


def run_benchmark():
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

    # Extraction des contextes uniques
    # On garantit un ordre déterministe
    context_to_id: Dict[str, int] = {}
    id_to_context: Dict[int, str] = {}
    doc_titles: Dict[int, str] = {}

    queries: List[str] = []
    ground_truth_doc_ids: List[int] = []
    sample_info: List[Dict[str, Any]] = []

    for item in dataset:
        ctx = item["context"].strip()
        if ctx not in context_to_id:
            new_id = len(context_to_id)
            context_to_id[ctx] = new_id
            id_to_context[new_id] = ctx
            doc_titles[new_id] = item.get("title", "")

        doc_id = context_to_id[ctx]
        q_text = item["question"].strip()
        queries.append(q_text)
        ground_truth_doc_ids.append(doc_id)
        sample_info.append({
            "question_id": item["id"],
            "question": q_text,
            "target_doc_id": doc_id,
            "target_title": item.get("title", ""),
        })

    n_passages = len(context_to_id)
    n_queries = len(queries)
    print(f"Nombre de contextes uniques (passages) : {n_passages}")
    print(f"Nombre de requêtes d'évaluation : {n_queries}")
    assert n_passages == 761, f"Attendu 761 contextes, obtenu {n_passages}"
    assert n_queries == 3835, f"Attendu 3835 requêtes, obtenu {n_queries}"

    # Sauvegarde des métadonnées du corpus PIAF pour traçabilité
    with open(OUTPUT_DIR / "piaf_corpus_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "n_passages": n_passages,
            "n_queries": n_queries,
            "dataset_id": DATASET_ID,
            "revision": DATASET_REVISION
        }, f, indent=2)

    passages_list = [id_to_context[i] for i in range(n_passages)]

    # --- 1. Baseline Aléatoire ---
    print("\n" + "=" * 70)
    print("Étape 3 : Baseline 1 — Tirage Aléatoire (Random)")
    print("=" * 70)
    rng = np.random.default_rng(RANDOM_SEED)
    random_preds: List[List[int]] = [
        rng.permutation(n_passages)[:10].tolist()
        for _ in range(n_queries)
    ]
    random_results = evaluate_retrieval(random_preds, ground_truth_doc_ids)
    print(f"Random - Recall@1: {random_results['recall@1']:.4f} | Recall@5: {random_results['recall@5']:.4f} | MRR: {random_results['mrr']:.4f}")

    # --- 2. Baseline Lexicale BM25 ---
    print("\n" + "=" * 70)
    print("Étape 4 : Baseline 2 — BM25 (rank_bm25)")
    print("=" * 70)
    t0_bm25_index = time.time()
    tokenized_corpus = [simple_tokenize(p) for p in passages_list]
    bm25 = BM25Okapi(tokenized_corpus)
    bm25_index_time = time.time() - t0_bm25_index
    print(f"Index BM25 construit en {bm25_index_time:.2f}s")

    t0_bm25_query = time.time()
    bm25_preds: List[List[int]] = []
    for q in queries:
        tok_q = simple_tokenize(q)
        scores = bm25.get_scores(tok_q)
        top10_idx = np.argsort(scores)[::-1][:10].tolist()
        bm25_preds.append(top10_idx)
    bm25_query_time = time.time() - t0_bm25_query
    avg_bm25_ms = (bm25_query_time / n_queries) * 1000
    bm25_results = evaluate_retrieval(bm25_preds, ground_truth_doc_ids)
    print(f"BM25 - Recall@1: {bm25_results['recall@1']:.4f} | Recall@5: {bm25_results['recall@5']:.4f} | MRR: {bm25_results['mrr']:.4f}")
    print(f"Temps moyen BM25 : {avg_bm25_ms:.2f} ms/requête")

    # --- 3. Dense E5 (multilingual-e5-small) ---
    print("\n" + "=" * 70)
    print(f"Étape 5 : Méthode Dense — {MODEL_ID}")
    print("=" * 70)
    t0_model = time.time()
    model = SentenceTransformer(MODEL_ID, device="cpu")
    print(f"Modèle chargé en {time.time() - t0_model:.2f}s")

    # Encodage des passages avec préfixe 'passage: '
    print(f"Encodage de {n_passages} passages (préfixe '{PREFIXE_PASSAGE}')...")
    passages_with_prefix = [PREFIXE_PASSAGE + p for p in passages_list]
    t0_enc_passages = time.time()
    passage_embeddings = model.encode(
        passages_with_prefix,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=True,
        convert_to_numpy=True
    ).astype(np.float32)
    enc_passages_time = time.time() - t0_enc_passages
    print(f"Passages encodés en {enc_passages_time:.2f}s. Matrice shape: {passage_embeddings.shape}")
    
    # Vérification des normes
    norms = np.linalg.norm(passage_embeddings, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-4), "Erreur : les embeddings de passages ne sont pas normalisés L2."

    # Encodage des requêtes avec préfixe 'query: '
    print(f"Encodage de {n_queries} requêtes (préfixe '{PREFIXE_REQUETE}')...")
    queries_with_prefix = [PREFIXE_REQUETE + q for q in queries]
    t0_enc_queries = time.time()
    query_embeddings = model.encode(
        queries_with_prefix,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=True,
        convert_to_numpy=True
    ).astype(np.float32)
    enc_queries_time = time.time() - t0_enc_queries
    avg_e5_ms = (enc_queries_time / n_queries) * 1000
    print(f"Requêtes encodées en {enc_queries_time:.2f}s ({avg_e5_ms:.2f} ms/requête)")

    # Calcul de similarité cosinus (produit scalaire direct car normalisés)
    print("Calcul des similarités vectorielles (produit matriciel)...")
    # S = Q (3835, 384) x P^T (384, 761) -> (3835, 761)
    similarity_matrix = np.matmul(query_embeddings, passage_embeddings.T)
    
    dense_preds: List[List[int]] = []
    for i in range(n_queries):
        row_scores = similarity_matrix[i]
        top10_idx = np.argsort(row_scores)[::-1][:10].tolist()
        dense_preds.append(top10_idx)

    dense_results = evaluate_retrieval(dense_preds, ground_truth_doc_ids)
    print(f"Dense E5 - Recall@1: {dense_results['recall@1']:.4f} | Recall@5: {dense_results['recall@5']:.4f} | MRR: {dense_results['mrr']:.4f}")

    # --- 4. Test statistique de McNemar (E5 vs BM25 sur Recall@5) ---
    print("\n" + "=" * 70)
    print("Étape 6 : Test de significativité apparié (McNemar sur Recall@5)")
    print("=" * 70)
    mcnemar_r5 = compute_mcnemar_test(dense_preds, bm25_preds, ground_truth_doc_ids, k=5)
    print(f"Table de contingence : {mcnemar_r5['contingency_table']}")
    print(f"E5 seul réussit : {mcnemar_r5['contingency_table']['n_10_A_only']}")
    print(f"BM25 seul réussit : {mcnemar_r5['contingency_table']['n_01_B_only']}")
    print(f"Statistique Chi2 : {mcnemar_r5['chi2_statistic']:.2f}")
    print(f"p-valeur (test binomial exact) : {mcnemar_r5['p_value']:.4e}")
    print(f"Différence statistiquement significative (p < 0.05) : {mcnemar_r5['significant_5pct']}")

    # --- 5. Exemples qualitatifs pour le rapport ---
    print("\n" + "=" * 70)
    print("Étape 7 : Analyse qualitative d'échantillons")
    print("=" * 70)
    qualitative_samples = []
    # Sélectionnons 3 requêtes variées :
    sample_indices = [0, 42, 128]
    for idx in sample_indices:
        q_text = queries[idx]
        target_id = ground_truth_doc_ids[idx]
        target_title = doc_titles[target_id]
        
        dense_rank = dense_preds[idx].index(target_id) + 1 if target_id in dense_preds[idx] else ">10"
        bm25_rank = bm25_preds[idx].index(target_id) + 1 if target_id in bm25_preds[idx] else ">10"
        
        info = {
            "query": q_text,
            "target_title": target_title,
            "dense_rank": dense_rank,
            "bm25_rank": bm25_rank,
            "dense_score": float(similarity_matrix[idx, target_id]),
        }
        qualitative_samples.append(info)
        print(f"Q: '{q_text}' (Doc: {target_title}) -> Rang E5: {dense_rank} | Rang BM25: {bm25_rank}")

    # --- Synthèse et sauvegarde ---
    summary = {
        "dataset": {
            "name": DATASET_ID,
            "revision": DATASET_REVISION,
            "n_passages": n_passages,
            "n_queries": n_queries,
        },
        "metrics": {
            "random": random_results,
            "bm25": bm25_results,
            "dense_e5": dense_results,
        },
        "mcnemar_recall5": mcnemar_r5,
        "timing": {
            "bm25_ms_per_query": avg_bm25_ms,
            "dense_e5_ms_per_query": avg_e5_ms,
        },
        "qualitative_samples": qualitative_samples
    }

    results_file = OUTPUT_DIR / "resultats_benchmark.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nRésultats complets sauvegardés dans : {results_file}")

    # Affichage du tableau récapitulatif final
    print("\n" + "=" * 70)
    print("TABLEAU RÉCAPITULATIF DES RÉSULTATS (PIAF)")
    print("=" * 70)
    print(f"{'Méthode':<20} | {'Recall@1':<10} | {'Recall@3':<10} | {'Recall@5':<10} | {'Recall@10':<10} | {'MRR':<10}")
    print("-" * 78)
    for name, r in [("Aléatoire", random_results), ("BM25 (lexical)", bm25_results), ("Dense E5 (small)", dense_results)]:
        print(f"{name:<20} | {r['recall@1']:<10.4f} | {r['recall@3']:<10.4f} | {r['recall@5']:<10.4f} | {r['recall@10']:<10.4f} | {r['mrr']:<10.4f}")
    print("=" * 78)


if __name__ == "__main__":
    run_benchmark()
