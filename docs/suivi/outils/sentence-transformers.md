# Sentence Transformers

## Identification
- Version : 6.1.0 (figée dans les fichiers `requirements-lock.txt` : identique pour tous)
- Nature : bibliothèque d'entraînement et d'usage d'encodeurs
- Assignés : Rémy (#49) ; prévus : Mahé, Jibril (#49) ; Mahé, Rémy (#46)
- Coordination : Rémy
- Période d'utilisation : du 1er au 14 octobre 2026 (étude de faisabilité d'apprentissage contrastif, ticket #49, PR #63)
- Besoin du projet auquel il répond : ajuster l'encodeur sur le corpus par apprentissage contrastif, et l'évaluer avant et après.

## Mise en place
- Temps avant le premier résultat utile : Moins d'une demi-journée pour installer l'environnement et valider un premier script d'entraînement contrastif avec `MultipleNegativesRankingLoss`.
- Installation et configuration : Installation via `uv pip install sentence-transformers==6.1.0` sous environnement isolé Python 3.12.
- Prérequis découverts en chemin : Nécessité de conserver rigoureusement les préfixes asymétriques E5 (`query: ` et `passage: `) dans le formatage des exemples pour préserver la structure de l'espace latent du modèle pré-entraîné.
- Difficultés non expliquées par la documentation : La conversion vers ONNX et la quantification 8 bits (q8) pour Transformers.js nécessitent une réexportation explicite (`exporter_onnx.py`), le format sauvegardé par défaut par Sentence Transformers n'étant pas directement consommable par le navigateur.

## Usage réel
- Tâche réalisée, ticket ou pull request : Ticket #49 et PR #63 : script d'entraînement `scripts/adaptation/04_ajuster_encodeur.py` et étude technique `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md`.
- Commande, configuration ou scénario : Entraînement contrastif de `multilingual-e5-small` avec fonction de perte `MultipleNegativesRankingLoss` (négatifs internes au lot).
- Résultat obtenu : Poids de l'ajusté générés (`5b8db94a...`) et quantifiés (`934a202b...`). Les résultats préliminaires ont montré la faisabilité de l'approche, mais la mesure définitive a été écartée pour respecter le chemin critique du volet B.
- Temps gagné ou perdu, s'il peut être estimé : Gain de temps significatif sur l'implémentation de la fonction de perte contrastive par rapport à une boucle d'entraînement PyTorch manuelle.

## Qualités observées
- API de haut niveau claire et standardisée pour le fine-tuning d'embeddings bi-encodeurs.
- Prise en charge native de l'apprentissage contrastif avec négatifs implicites du lot (`MultipleNegativesRankingLoss`).

## Défauts et limites observés
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas : Sensibilité aux faux négatifs dans le lot : si deux passages traitant d'une thématique similaire se retrouvent dans le même lot d'entraînement, le modèle les pénalise artificiellement comme négatifs.
- Dépendance lourde à PyTorch et `transformers`, non adaptée au service client direct dans le navigateur (nécessite ONNX Runtime).

## Comparaison
- Méthode ou outil utilisé auparavant : Encodeur dense pré-entraîné brut sans réapprentissage.
- Différences observées : Sentence Transformers simplifie le réglage fin des poids sémantiques, mais introduit un risque de surapprentissage si le corpus d'entraînement est restreint.
- Cas où l'ancienne méthode reste préférable : L'encodeur de base pré-entraîné reste préférable lorsqu'il satisfait déjà les critères de non-infériorité sans coût d'entraînement ni risque de régression sur le vocabulaire général.

## Décision
Conservé pour l'étude méthodologique ; abandonné pour le déploiement opérationnel.
- Motif : (Remy) Le volet A a été validé et clos avec l'encodeur de base élagué (règle de repli du protocole 05). La clôture de #49 au Weekly 8 permet de concentrer la bande passante sur le chemin critique du volet B.

## À retenir pour le rapport
- Apport : Prototypage rapide de l'apprentissage contrastif sur corpus francophone spécialisé.
- Principale limite : Nécessite une chaîne d'export et de validation de parité ONNX en aval pour le web.
- Ce que la documentation ne dit pas : L'impact des faux négatifs dans le lot et la nécessité de filtrer rigoureusement les paires pour éviter toute contamination du jeu d'évaluation.

## Preuves
- Ticket #49 : `scripts/adaptation/04_ajuster_encodeur.py`, étude `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md`.
- PR #63 : scripts d'export et d'évaluation préliminaire.
