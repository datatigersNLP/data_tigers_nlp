# Récupération v2 (#138) et chaîne v2 (#163) du volet B

Quatre leviers, réglés sur le jeu CDTN et jamais sur le lot de test : le nombre de passages, un reclasseur (cross-encoder), l'ajout des passages voisins de la même section, et la fusion des rangs d'E5 et de BM25 V3 (RRF).

La chaîne v2 (#163) branche cette récupération sur la génération du protocole 06, avec une consigne v2 et une abstention décidée par le reclasseur. Mesurée une fois sur le lot de test le 15 novembre 2026 (protocole 08), elle n'est pas adoptée : B2 reste la chaîne de référence (`docs/etudes/evaluation/08_resultats_chaine_v2.md`).

## Ce que ce dossier ne touche pas

* **Aucun des dix fichiers du verrou** de la mesure (`scripts/rag/verrou_mesure.json`, PR #131) : protocole 06, `mesure.py`, `rag.py`, `generation.py`, `metrics.py`, `pertinence.py`, jeu, seuil, index et passages. Le test `VerrouTests` recalcule leurs empreintes avec `mesure.empreintes_actuelles` et les compare au verrou.
* **L'abstention** : le seuil S reste appliqué au cosinus maximal d'E5, avant toute autre étape. Seul l'état V2 de la chaîne v2 s'abstient autrement, sur le score maximal de bge-m3 avec le seuil τ (protocole 08, section 4).
* **Le lot de test** : `reglage_cdtn.py` n'en lit que les URL, pour reconnaître les 61 fiches du lot, comme `scripts/adaptation_qwen/separation.py`.

## Fichiers

* `recuperation.py` : classement stable, fusion RRF en fractions exactes (k = 60), reclassement, voisins, contexte et budget.
  * Le contexte a le même format que `rag.construire_contexte`, pour un nombre quelconque de passages ; un test vérifie l'égalité exacte pour cinq passages.
  * Budget : la règle de `generation.preparer_entree`, soit 8 192 − 512 − 64 = 7 616 tokens de prompt au plus. Au-delà, les derniers groupes (une ancre et ses voisins) sont retirés ; aucun passage n'est tronqué.
* `reglage_cdtn.py` : préparation (population, E5, BM25 V3), scores des reclasseurs, grille des configurations.
* `confirmer_test.py` : la confirmation unique sur le lot de test, selon le protocole 07 (`docs/etudes/evaluation/07_protocole_recuperation_v2.md`). Il refuse de tourner si le protocole, le script ou le module ne sont pas committés à l'identique, et ne calcule la v2 qu'après avoir reproduit les rangs publiés par le notebook 03.
* `test_recuperation.py` : 19 tests sans modèle ni question d'évaluation.
* `chaine_v2.py` : la chaîne v2 et sa mesure selon le protocole 08 (`docs/etudes/evaluation/08_protocole_chaine_v2.md`) ; commandes `seuil` (calcul de τ sur le CDTN), `preparer` (contextes, une fois par lot), `executer` (un état, un modèle) et `analyser`. Il refuse de lire le lot de test si les empreintes du protocole 08 et de τ diffèrent de celles du gel, et contrôle le verrou de la #131 avant le calcul de τ, la préparation des contextes et chaque état.
* `test_chaine_v2.py` : 14 tests sans modèle ni question d'évaluation.

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
python scripts/recuperation/confirmer_test.py          # une seule fois, après le gel du protocole 07
python scripts/recuperation/test_chaine_v2.py
python scripts/recuperation/chaine_v2.py seuil
python scripts/recuperation/chaine_v2.py preparer --lot test
python scripts/recuperation/chaine_v2.py executer --lot test --phase temoin --etat V1 --modele MODELE --digest DIGEST
python scripts/recuperation/chaine_v2.py analyser --lot test
```

`executer` est lancé une fois par état et par modèle, dans l'ordre du protocole 08 (section 5), avec les modèles et digests publiés sur le #52. Les sorties vont dans `data/evaluation/recuperation/` et `data/evaluation/volet_b/chaine_v2/`, qui ne sont pas versionnés ; chaque cache est lié aux classements par son empreinte.
