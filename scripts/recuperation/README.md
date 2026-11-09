# Récupération v2 du volet B (#138)

Quatre leviers, réglés sur le jeu CDTN et jamais sur le lot de test : le nombre de passages, un reclasseur (cross-encoder), l'ajout des passages voisins de la même section, et la fusion des rangs d'E5 et de BM25 V3 (RRF).

## Ce que ce dossier ne touche pas

* **Aucun des dix fichiers du verrou** de la mesure (`scripts/rag/verrou_mesure.json`, PR #131) : protocole 06, `mesure.py`, `rag.py`, `generation.py`, `metrics.py`, `pertinence.py`, jeu, seuil, index et passages. Le test `VerrouTests` recalcule leurs empreintes avec `mesure.empreintes_actuelles` et les compare au verrou.
* **L'abstention** : le seuil S reste appliqué au cosinus maximal d'E5, avant toute autre étape.
* **Le lot de test** : `reglage_cdtn.py` n'en lit que les URL, pour reconnaître les 61 fiches du lot, comme `scripts/adaptation_qwen/separation.py`.

## Fichiers

* `recuperation.py` : classement stable, fusion RRF en fractions exactes (k = 60), reclassement, voisins, contexte et budget.
  * Le contexte a le même format que `rag.construire_contexte`, pour un nombre quelconque de passages ; un test vérifie l'égalité exacte pour cinq passages.
  * Budget : la règle de `generation.preparer_entree`, soit 8 192 − 512 − 64 = 7 616 tokens de prompt au plus. Au-delà, les derniers groupes (une ancre et ses voisins) sont retirés ; aucun passage n'est tronqué.
* `reglage_cdtn.py` : préparation (population, E5, BM25 V3), scores des reclasseurs, grille des configurations.
* `test_recuperation.py` : 16 tests sans modèle ni question d'évaluation.

## Reclasseurs

* `BAAI/bge-reranker-v2-m3`, révision `953dc6f6`, Apache-2.0.
* `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`, révision `1427fd65`, Apache-2.0.
* `antoinelouis/crossencoder-camembert-base-mmarcoFR`, révision `f009b88d`, MIT.

Tous en safetensors, chargés sans code distant (`trust_remote_code=False`) et sur CPU. Écartés : `Alibaba-NLP/gte-multilingual-reranker-base` et `jinaai/jina-reranker-v2-base-multilingual`, qui exigent du code distant ; le second a aussi une licence non commerciale.

## Exécution

Environnement : le fichier figé de l'évaluation, `scripts/evaluation/requirements-lock.txt` (Python 3.12).

```
python scripts/recuperation/test_recuperation.py
python scripts/recuperation/reglage_cdtn.py preparer
python scripts/recuperation/reglage_cdtn.py reclasser mmarco-minilm
python scripts/recuperation/reglage_cdtn.py reclasser camembert-mmarco
python scripts/recuperation/reglage_cdtn.py reclasser bge-m3
python scripts/recuperation/reglage_cdtn.py grille
```

Les sorties vont dans `data/evaluation/recuperation/`, qui n'est pas versionné ; chaque cache est lié aux classements par son empreinte.
