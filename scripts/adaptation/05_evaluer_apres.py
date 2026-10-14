"""
scripts/adaptation/05_evaluer_apres.py
Évaluation rigoureuse du modèle ajusté sur le jeu de test et test statistique apparié face à la baseline.
"""

import json
import os
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Standard d'import du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importer les métriques validées du projet
from scripts.evaluation.metrics import (
    evaluate_retrieval,
    rank_by_score,
    proportion_ci,
    compute_mcnemar_test,
)


def main():
    print("[1/6] Chargement des données du benchmark et des résultats baseline...")
    with open("data/adaptation/benchmark_test.json", "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    with open("data/adaptation/resultats_baseline.json", "r", encoding="utf-8") as f:
        res_baseline = json.load(f)

    with open("data/adaptation/preds_baseline.json", "r", encoding="utf-8") as f:
        baseline_preds_data = json.load(f)

    df_m2 = pd.read_parquet("data/decoupage/passages/passages_m2.parquet")
    passage_ids = df_m2["passage_id"].tolist()
    passages_text = df_m2["entree_encodeur"].tolist()

    queries = [f"query: {item['question']}" for item in benchmark]
    ground_truth = [item["ground_truth_passage_ids"] for item in benchmark]
    groups = [item["group"] for item in benchmark]

    print(f"       {len(queries)} requêtes de test")
    print(f"       {len(passages_text)} passages à encoder")

    print("[2/6] Chargement du modèle ajusté (models/multilingual-e5-small-finetuned)...")
    model_path = "models/multilingual-e5-small-finetuned"
    model = SentenceTransformer(model_path)

    print("[3/6] Encodage des passages avec le modèle ajusté...")
    t0 = time.time()
    passage_embeddings = model.encode(
        passages_text,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    t_passages = time.time() - t0
    print(f"       Encodage des passages terminé en {t_passages:.2f}s ({len(passages_text)/t_passages:.1f} pass/s)")

    print("[4/6] Encodage des requêtes de test...")
    t0 = time.time()
    query_embeddings = model.encode(
        queries,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    print(f"       Encodage des requêtes terminé en {time.time() - t0:.2f}s")

    print("[5/6] Calcul des prédictions et métriques après adaptation...")
    sims = np.dot(query_embeddings, passage_embeddings.T)
    preds_after = []
    for i in range(len(benchmark)):
        ranked_indices = rank_by_score(sims[i])
        ranked_ids = [passage_ids[idx] for idx in ranked_indices]
        preds_after.append(ranked_ids)

    k_vals = (1, 3, 5, 10)
    metrics_after = evaluate_retrieval(preds_after, ground_truth, k_values=k_vals)

    # Intervalles de confiance Wilson 95%
    ci_res_after = {}
    for k in k_vals:
        hits = [int(any(gt in p[:k] for gt in (g if isinstance(g, (set, list)) else [g]))) for p, g in zip(preds_after, ground_truth)]
        low, high = proportion_ci(hits, level=0.95)
        ci_res_after[f"ci_recall@{k}"] = (round(low, 4), round(high, 4))

    print("[6/6] Tests statistiques appariés (Avant vs Après)...")
    preds_before = [item["top10_preds"] for item in baseline_preds_data]

    # Test de McNemar (et Obuchowski groupé par fiche) pour chaque k
    tests_apparies = {}
    for k in [1, 3, 5, 10]:
        # Tester si Modèle Après (A) vs Modèle Avant (B) présente une différence significative
        mcn = compute_mcnemar_test(preds_after, preds_before, ground_truth, k=k, groups=groups)
        tests_apparies[f"recall@{k}"] = mcn

    # Affichage du tableau comparatif
    b_metrics = res_baseline["metrics"]
    print("\n" + "=" * 80)
    print(f"{'Métrique':<12} | {'Avant (Base)':<15} | {'Après (Ajusté)':<15} | {'Écart (pts)':<12} | {'p-value':<10} | {'Significatif (5%)'}")
    print("-" * 80)

    for k in [1, 3, 5, 10]:
        m_key = f"recall@{k}"
        v_avant = b_metrics[m_key] * 100
        v_apres = metrics_after[m_key] * 100
        diff = v_apres - v_avant
        t_info = tests_apparies[m_key]
        p_val = t_info.get("p_value_groups", t_info["p_value"])
        sig = "OUI" if t_info["significant_5pct"] else "NON"
        print(f"Recall@{k:<6} | {v_avant:6.2f}%         | {v_apres:6.2f}%         | {diff:+6.2f}%      | {p_val:.4f}     | {sig}")

    mrr_avant = b_metrics["mrr"]
    mrr_apres = metrics_after["mrr"]
    mrr_diff = mrr_apres - mrr_avant
    print(f"MRR@10       | {mrr_avant:6.4f}          | {mrr_apres:6.4f}          | {mrr_diff:+6.4f}       | {'-':<10} | {'-'}")
    print("=" * 80 + "\n")

    # Rapport complet
    rapport_comparatif = {
        "n_questions": len(benchmark),
        "n_passages": len(df_m2),
        "metrics_avant": b_metrics,
        "ci_avant": res_baseline["confiance_95"],
        "metrics_apres": metrics_after,
        "ci_apres": ci_res_after,
        "ecarts": {
            "recall@1": metrics_after["recall@1"] - b_metrics["recall@1"],
            "recall@3": metrics_after["recall@3"] - b_metrics["recall@3"],
            "recall@5": metrics_after["recall@5"] - b_metrics["recall@5"],
            "recall@10": metrics_after["recall@10"] - b_metrics["recall@10"],
            "mrr@10": metrics_after["mrr"] - b_metrics["mrr"],
        },
        "tests_statistiques_apparies": tests_apparies,
        "date_evaluation": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open("data/adaptation/resultats_comparaison.json", "w", encoding="utf-8") as f:
        json.dump(rapport_comparatif, f, ensure_ascii=False, indent=2)

    # Sauvegarder les embeddings après
    np.save("data/adaptation/passage_embeddings_apres.npy", passage_embeddings)
    print("Rapport comparatif sauvegardé dans data/adaptation/resultats_comparaison.json")


if __name__ == "__main__":
    main()
