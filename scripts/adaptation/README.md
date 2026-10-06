# Pipeline d'adaptation de l'encodeur (Issue #49)

Ce dossier contient l'ensemble de la chaîne de traitement permettant d'ajuster finement l'encodeur sémantique `multilingual-e5-small` sur le corpus SocialGouv, de mesurer l'impact par un banc d'évaluation apparié, et d'exporter le modèle en format ONNX quantifié pour le navigateur.

---

## Vue d'ensemble des scripts

| Script | Rôle | Entrées | Sorties |
|---|---|---|---|
| [`01_preparer_benchmark.py`](01_preparer_benchmark.py) | Constitution du benchmark de test et cartographie d'exclusion | `questions_annotees.csv` (#44), `passages_m2.parquet` | `benchmark_test.json`, `exclusions_train.json` |
| [`02_mesurer_baseline.py`](02_mesurer_baseline.py) | Mesure de référence avant adaptation avec `multilingual-e5-small` pré-entraîné | `benchmark_test.json`, `passages_m2.parquet` | `resultats_baseline.json`, `preds_baseline.json` |
| [`03_generer_paires_locales.py`](03_generer_paires_locales.py) | Génération synthétique de paires avec Qwen2.5-7B local et filtres anti-fuite | `passages_m2.parquet`, `exclusions_train.json` | `train_paires.jsonl`, `echantillon_controle_train.json` |
| [`04_ajuster_encodeur.py`](04_ajuster_encodeur.py) | Fine-tuning contrastif (MultipleNegativesRankingLoss) | `train_paires.jsonl` | `models/multilingual-e5-small-finetuned/` |
| [`05_evaluer_apres.py`](05_evaluer_apres.py) | Évaluation après fine-tuning et tests statistiques appariés | `benchmark_test.json`, modèle ajusté | `resultats_comparaison.json` |
| [`06_exporter_onnx.py`](06_exporter_onnx.py) | Export ONNX FP32, quantification q8 et contrôles de parité/fidélité | Modèle ajusté PyTorch | `model.onnx`, `model_quantized.onnx`, `rapport_onnx_parite.json` |

---

## Garantie scientifique d'étanchéité (Zéro Data Leakage)

1. **Exclusion stricte au niveau de la fiche :** Les 67 fiches (URLs et pubIds) associées aux questions du jeu de test et du lot de calibration sont totalement exclues du vivier de passages d'entraînement (1 463 passages exclus sur 4 240, soit 34,5%).
2. **Filtrage lexical Jaccard :** Chaque question générée par Qwen2.5-7B est comparée à l'ensemble des questions du test set ; toute question présentant un score de Jaccard > 0,40 est immédiatement rejetée.
3. **Tests statistiques appariés :** L'évaluation calcule la valeur *p* exacte par test binomial de McNemar et par la statistique d'Obuchowski (McNemar pour données groupées par fiche) avec le module validé [`metrics.py`](../evaluation/metrics.py).
