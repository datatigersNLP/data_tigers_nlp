# Ollama

## Identification
- Version : variable selon les membres, voir « Versions utilisées »
- Nature : application d'exécution locale de modèles de langage
- Assignés : Jibril (#31, PR #41), Rémy (#49) ; prévus : Maïmouna (#51) ; Mahé (#52)
- Coordination : Jibril
- Période d'utilisation : à compléter
- Besoin du projet auquel il répond : faire tourner le modèle de langage du volet B en local, sans service externe.

## Versions utilisées
Chaque membre tient sa propre ligne à jour.

| Membre | Version | Système | Remarque |
|---|---|---|---|
| Jibril | 0.34.4 | Windows | GPU NVIDIA, Qwen2.5-7B Q4_K_M (PR #41) |
| Rémy | à compléter | à compléter | |
| Maïmouna | à compléter | à compléter | |
| Mahé | à compléter | à compléter | |

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

## Preuves
- Pull request #41 : première inférence locale de Qwen2.5-7B (`docs/etudes/inference_locale_qwen.md`, `scripts/inference/test_qwen.ps1`) ; échec du téléchargement direct (HTTP 400) contourné par `ollama create`.
- Ticket #49 : génération de paires d'entraînement avec Qwen (`scripts/adaptation/03_generer_paires_locales.py`).
