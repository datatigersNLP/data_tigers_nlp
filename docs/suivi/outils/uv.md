# uv

## Identification
- Version : variable selon les membres, voir « Versions utilisées »
- Nature : gestionnaire d'environnements et de dépendances Python
- Assignés : Mahé (#35, #30, #45 à #47), Vaneck (relecture de la PR #39) ; prévus : Rémy (#46, #47)
- Coordination : Mahé
- Période d'utilisation : à compléter
- Besoin du projet auquel il répond : créer des environnements Python reproductibles, avec des dépendances figées pour toutes les plateformes.

## Versions utilisées
Chaque membre tient sa propre ligne à jour.

| Membre | Version | Système | Remarque |
|---|---|---|---|
| Mahé | à compléter | macOS | |
| Vaneck | à compléter | Windows | relance du notebook 01 (relecture de la PR #39), Python 3.12.14 |
| Rémy | à compléter | à compléter | |

## Mise en place
- Temps avant le premier résultat utile :
- Installation et configuration :
- Prérequis découverts en chemin :
- Difficultés non expliquées par la documentation :
  - (Vaneck) Sous Windows, l'interpréteur de l'environnement est `.venv\Scripts\python.exe` : la commande de
    reproduction du notebook 01, écrite avec `.venv/bin/python` (chemin macOS et Linux), échoue telle quelle
    (relecture de la PR #39).

## Usage réel
- Tâche réalisée, ticket ou pull request :
  - (Vaneck) Relecture de la PR #39 : notebook 01 relancé intégralement sous Windows pour vérifier sa
    reproductibilité.
- Commande, configuration ou scénario :
  - (Vaneck) Environnement créé avec uv (Python 3.12.14), dépendances installées depuis le fichier
    `requirements-lock.txt`, notebook exécuté de bout en bout par `nbclient`.
- Résultat obtenu :
  - (Vaneck) Exécution complète en 2 212 s (environ 37 min). Mêmes effectifs que sur macOS pour toutes les
    méthodes (M0 5 284, M1 5 317, M2 4 240, M3 4 229 passages) et empreinte de M0 identique ; empreintes de
    M1, M2 et M3 différentes, l'extraction du texte conservant 3 964 979 caractères contre 3 965 010.
- Temps gagné ou perdu, s'il peut être estimé :

## Qualités observées
- (Vaneck) Le fichier figé toutes plateformes s'installe tel quel sous Windows : aucune dépendance à résoudre
  à la main.

## Défauts et limites observés
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas :
  - (Vaneck) Figer les dépendances ne suffit pas à rendre un résultat identique au caractère près entre
    systèmes : avec les mêmes bibliothèques, l'écart observé coïncide avec une version de Python différente
    (3.12.14 sous Windows, 3.12.11 sous macOS), cause probable mais non confirmée. Le déterminisme se vérifie
    sur une même machine, pas d'une plateforme à l'autre.

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
- Fichiers `requirements-lock.txt` multiplateformes (`uv pip compile --universal`) des notebooks 01 à 03.
- Relecture de la PR #39 : notebook 01 relancé sous Windows, mêmes effectifs mais empreintes différentes de celles de macOS ; chemin `.venv/bin/python` à remplacer par `.venv\Scripts\python.exe` sous Windows.
