# ONNX Runtime (Python et Web)

## Identification
- Version : 1.30.0 en Python (figée dans les fichiers `requirements-lock.txt` : identique pour tous) ; ONNX
  Runtime Web suit la version embarquée par Transformers.js
- Nature : moteur d'exécution de modèles
- Assignés : Mahé (#30, PR #40), Rémy (#49) ; prévus : Jibril (#49) ; Mahé, Rémy (#50)
- Coordination : Mahé
- Période d'utilisation : à compléter
- Besoin du projet auquel il répond : exécuter l'encodeur au format ONNX, en Python pour l'index et dans le navigateur via Transformers.js.

## Mise en place
- Temps avant le premier résultat utile :
- Installation et configuration :
- Prérequis découverts en chemin :
- Difficultés non expliquées par la documentation :

## Usage réel
- Tâche réalisée, ticket ou pull request :
- Commande, configuration ou scénario :
- Résultat obtenu :
- Temps gagné ou perdu, s'il peut être estimé :

## Qualités observées
-

## Défauts et limites observés
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas :

## Comparaison
- Méthode ou outil utilisé auparavant :
- Différences observées :
- Cas où l'ancienne méthode reste préférable :

## Décision
À compléter : adopté / conservé pour certains usages / abandonné / à réévaluer.
- Motif :

## À retenir pour le rapport
- Apport :
- Principale limite :
- Ce que la documentation ne dit pas :

## Preuves
- Pull request #40 : parité ONNX fp32 et PyTorch, critère de parité q8 échoué puis diagnostiqué (notebook 02, section 8).
- Ticket #49 : export et quantification de l'encodeur ajusté (`scripts/adaptation/06_exporter_onnx.py`).
