"""
scripts/adaptation/02_mesurer_baseline.py
Mesure rigoureuse de la baseline avant adaptation avec multilingual-e5-small pré-entraîné.
"""

import json
import os
import sys
import time
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from pathlib import Path

# Ajouter la racine du projet dans sys.path pour les imports inter-scripts
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importer les métriques validées du projet
from scripts.evaluation.metrics import evaluate_retrieval, rank_by_score, proportion_ci


def main():
    print("[1/5] Chargement des données...")
    with open("data/adaptation/benchmark_test.json", "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    df_m2 = pd.read_parquet("data/decoupage/passages/passages_m2.parquet")
    passage_ids = df_m2["passage_id"].tolist()
    passages_text = df_m2["entree_encodeur"].tolist()  # Déjà préfixé "passage: "

    queries = [f"query: {item['question']}" for item in benchmark]
    ground_truth = [item["ground_truth_passage_ids"] for item in benchmark]

    print(f"       {len(queries)} requêtes de test")
    print(f"       {len(passages_text)} passages à indexer")

    print("[2/5] Chargement du modèle intfloat/multilingual-e5-small pré-entraîné...")
    model = SentenceTransformer("intfloat/multilingual-e5-small")

    print("[3/5] Encodage des passages du corpus M2 (FP32)...")
    t0 = time.time()
    passage_embeddings = model.encode(
        passages_text,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    t_passages = time.time() - t0
    print(f"       Encodage des passages terminé en {t_passages:.2f}s ({len(passages_text)/t_passages:.1f} passages/s)")

    print("[4/5] Encodage des requêtes de test...")
    t0 = time.time()
    query_embeddings = model.encode(
        queries,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    print(f"       Encodage des requêtes terminé en {time.time() - t0:.2f}s")

    print("[5/5] Évaluation du classement par similarité cosinus...")
    preds = []
    # Calcul du produit scalaire (équivalent cosinus puisque normalisé)
    sims = np.dot(query_embeddings, passage_embeddings.T)

    for i in range(len(benchmark)):
        ranked_indices = rank_by_score(sims[i])
        ranked_ids = [passage_ids[idx] for idx in ranked_indices]
        preds.append(ranked_ids)

    # Calcul des métriques avec le module metrics.py
    k_vals = (1, 3, 5, 10)
    metrics_res = evaluate_retrieval(preds, ground_truth, k_values=k_vals)

    # Calcul des intervalles de confiance à 95% pour chaque Recall
    ci_res = {}
    for k in k_vals:
        hits = [int(any(gt in p[:k] for gt in (g if isinstance(g, (set, list)) else [g]))) for p, g in zip(preds, ground_truth)]
        low, high = proportion_ci(hits, level=0.95)
        ci_res[f"ci_recall@{k}"] = (round(low, 4), round(high, 4))

    result = {
        "modele": "intfloat/multilingual-e5-small (baseline pré-entraîné)",
        "date_evaluation": time.strftime("%Y-%m-%d %H:%M:%S"),
        "n_questions": len(benchmark),
        "n_passages": len(df_m2),
        "metrics": metrics_res,
        "confiance_95": ci_res,
        "temps_encodage_passages_sec": t_passages,
    }

    print("\n" + "=" * 55)
    print("RÉSULTATS BASELINE (AVANT ADAPTATION) :")
    print(f"  Recall@1  : {metrics_res['recall@1']*100:.2f}% (IC 95%: [{ci_res['ci_recall@1'][0]*100:.1f}%, {ci_res['ci_recall@1'][1]*100:.1f}%])")
    print(f"  Recall@3  : {metrics_res['recall@3']*100:.2f}% (IC 95%: [{ci_res['ci_recall@3'][0]*100:.1f}%, {ci_res['ci_recall@3'][1]*100:.1f}%])")
    print(f"  Recall@5  : {metrics_res['recall@5']*100:.2f}% (IC 95%: [{ci_res['ci_recall@5'][0]*100:.1f}%, {ci_res['ci_recall@5'][1]*100:.1f}%])")
    print(f"  Recall@10 : {metrics_res['recall@10']*100:.2f}% (IC 95%: [{ci_res['ci_recall@10'][0]*100:.1f}%, {ci_res['ci_recall@10'][1]*100:.1f}%])")
    print(f"  MRR@10    : {metrics_res['mrr']:.4f}")
    print("=" * 55 + "\n")

    # Sauvegarde des résultats et des prédictions détaillées
    with open("data/adaptation/resultats_baseline.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Sauvegarder les rangs top-10 pour chaque question pour le test apparié
    detailed_preds = []
    for i, item in enumerate(benchmark):
        detailed_preds.append({
            "id": item["id"],
            "question": item["question"],
            "ground_truth": item["ground_truth_passage_ids"],
            "top10_preds": preds[i][:10],
            "group": item["group"]
        })
    with open("data/adaptation/preds_baseline.json", "w", encoding="utf-8") as f:
        json.dump(detailed_preds, f, ensure_ascii=False, indent=2)

    # Sauvegarder les embeddings des passages
    np.save("data/adaptation/passage_embeddings_baseline.npy", passage_embeddings)
    print("Résultats et prédictions enregistrés dans data/adaptation/")


if __name__ == "__main__":
    main()
