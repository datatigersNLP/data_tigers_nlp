# Sentence Transformers

## Identification
- Version : 6.1.0 (figée dans les fichiers `requirements-lock.txt` : identique pour tous)
- Nature : bibliothèque d'entraînement et d'usage d'encodeurs
- Assignés : Rémy (#49) ; prévus : Mahé, Jibril (#49) ; Mahé, Rémy (#46)
- Coordination : Rémy
- Période d'utilisation : (Remy) du 1er au 14 octobre 2026 pour l'étude #49 (PR #63) ; utilisé ensuite par Mahé le 9 novembre pour le reclassement `CrossEncoder` du volet B (#138, PR #141)
- Besoin du projet auquel il répond : ajuster l'encodeur sur le corpus par apprentissage contrastif, et l'évaluer avant et après.

## Mise en place
- Temps avant le premier résultat utile : (Remy) moins d'une demi-journée sous Windows 11 pour aligner l'environnement et exécuter un premier ajustement contrastif avec `MultipleNegativesRankingLoss` (#49, PR #63).
- Installation et configuration : (Remy) version `sentence-transformers==6.1.0` déclarée dans `scripts/adaptation/requirements.txt` (exécutée sur Python 3.12.10 avec `torch 2.14.0` et `transformers 5.18.0`, Windows 11).
- Prérequis découverts en chemin : (Remy) nécessité de conserver strictement les préfixes asymétriques E5 (`query: ` et `passage: `) lors de la construction des paires d'entraînement pour respecter la géométrie latente du modèle pré-entraîné (#49).
- Difficultés non expliquées par la documentation :
  - (Remy) La sauvegarde native de Sentence Transformers ne produit pas un modèle `q8` consommable directement par Transformers.js dans le navigateur : une chaîne dédiée d'export ONNX (`scripts/adaptation/06_exporter_onnx.py`, PR #63) avec quantification symétrique s'est avérée indispensable.
  - (Remy) Lors de la sauvegarde sous `transformers 5.18`, `tokenizer.json` est resérialisé avec une règle de prétraitement légèrement différente de celle d'origine (écart sur 6 formulations du CDTN avec espace final), amenant à proposer la conservation du tokeniseur de base (`01_ajustement_encodeur_contrastif.md`, section 5.2).

## Usage réel
- Tâche réalisée, ticket ou pull request : (Remy) Ticket #49 et PR #63 : entraînement contrastif (`scripts/adaptation/04_ajuster_encodeur.py`) et étude `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md`.
- Commande, configuration ou scénario : (Remy) fine-tuning de `intfloat/multilingual-e5-small` sur 109 paires issues de 110 fiches hors test, avec `MultipleNegativesRankingLoss` (`batch_size=16`, 2 époques, `lr=2e-5`, 185,5 s sur CPU 16 cœurs).
- Résultat obtenu : (Remy) perte d'entraînement décroissante de `1,5610` à `0,4717` (`model.safetensors`, SHA-256 `5b8db94a...`) et tendance exploratoire favorable hors protocole (`+19,44` pts sur Recall@5 avant gel du notebook 03). Cependant, la mesure officielle prévue au protocole 05 n'ayant pas été effectuée avant l'échéance du 16 octobre, la règle de repli écrite d'avance a maintenu l'encodeur de base élagué en production ; le 30 octobre, la poursuite de la mesure officielle n'a pas été retenue dans le calendrier resserré, tout en laissant **le ticket #49 ouvert** (`docs/suivi/SUIVI.md`).
- Temps gagné ou perdu, s'il peut être estimé : (Remy) mise en place rapide de la boucle contrastive comparée à une implémentation PyTorch manuelle (PR #63).

## Qualités observées
- (Remy) Interface standardisée claire pour les bi-encodeurs et prise en charge directe des négatifs implicites du lot via `MultipleNegativesRankingLoss` (`04_ajuster_encodeur.py`).
- (Remy) Prise en charge directe de l'asymétrie et de l'encodage en Python en un jeu minimal de paramètres.

## Défauts et limites observés
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas :
  - (Remy) Sensibilité aux faux négatifs dans les mini-lots : avec `MultipleNegativesRankingLoss`, deux passages juridiquement voisins placés dans un même lot de taille 16 sont pénalisés comme négatifs, imposant de limiter les tirages à au plus un passage par fiche (`01_ajustement_encodeur_contrastif.md`).
  - (Remy) Dépendance lourde à PyTorch / `transformers`, inutilisable en l'état dans un client web statique sans export ONNX et vérification in-browser (PR #63).

## Comparaison
- Méthode ou outil utilisé auparavant : (Remy) encodeur pré-entraîné brut `multilingual-e5-small` sans réajustement des poids.
- Différences observées : (Remy) permet une spécialisation rapide de l'espace latent sur le domaine, mais exige un cloisonnement strict des fiches d'évaluation, un filtrage des paires et une double validation sur jeu externe.
- Cas où l'ancienne méthode reste préférable : (Remy) l'encodeur de base reste préférable tant qu'il satisfait les critères de non-infériorité sans coût de revalidation ni risque de dérive de tokenisation (#49, règle de repli du protocole 05 appliquée le 16 octobre).

## Décision
À compléter : adopté / conservé pour certains usages / abandonné / à réévaluer.
- Motif :

## À retenir pour le rapport
- Apport : (Remy) prototypage rapide de l'apprentissage contrastif (`MultipleNegativesRankingLoss`) sur corpus juridique francophone (#49, PR #63).
- Principale limite : (Remy) sensibilité aux faux négatifs en lot et dépendance à une chaîne complète d'export ONNX et de contrôle de fidélité pour le web.
- Ce que la documentation ne dit pas : (Remy) la resérialisation implicite de `tokenizer.json` sous `transformers 5.18` modifie marginalement le découpage de chaînes comportant un espace final (`01_ajustement_encodeur_contrastif.md`, section 5.2).

## Preuves
- Ticket #49 et PR #63 : `scripts/adaptation/03_generer_paires_locales.py`, `04_ajuster_encodeur.py`, `06_exporter_onnx.py`, étude `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md` et protocole `docs/etudes/evaluation/05_protocole_ajustement.md`.
- `docs/suivi/SUIVI.md` : application de la règle de repli le 16/10, non-maintien de la mesure officielle le 30/10 et maintien du ticket #49 ouvert.
