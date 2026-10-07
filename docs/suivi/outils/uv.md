# uv

## Identification
- Version : à compléter
- Nature : gestionnaire d'environnements et de dépendances Python
- Assignés : Mahé (#35, #30, #45 à #47), Vaneck (relecture de la PR #39) ; prévus : Rémy (#46, #47)
- Coordination : Mahé
- Période d'utilisation : à compléter
- Besoin du projet auquel il répond : créer des environnements Python reproductibles, avec des dépendances figées pour toutes les plateformes.

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
- Fichiers `requirements-lock.txt` multiplateformes (`uv pip compile --universal`) des notebooks 01 à 03.
- Relecture de la PR #39 : notebook 01 relancé sous Windows, mêmes effectifs mais empreintes différentes de celles de macOS ; chemin `.venv/bin/python` à remplacer par `.venv\Scripts\python.exe` sous Windows.
