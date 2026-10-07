# GitHub CLI (`gh`)

## Identification
- Version : 2.101.0
- Nature : application en ligne de commande
- Assignés : toute l'équipe (premier usage consigné au journal le 19/09) ; première version de la fiche rédigée par Vaneck
- Coordination : toute l'équipe
- Période d'utilisation : depuis le 19 septembre 2026
- Besoin du projet auquel il répond : manipuler tickets, pull requests, board et réglages du dépôt sans passer
  par l'interface web, et rendre ces opérations reproductibles dans des scripts.

## Mise en place
- Installation puis `gh auth login`.
- Prérequis découvert en chemin : la lecture du board (GitHub Projects) exige une portée supplémentaire,
  `read:project`, à ajouter au jeton avec `gh auth refresh -s read:project`. Sans elle, les commandes
  `gh project` échouent.

## Usage réel
- Création de la pull request #42, assignation, lecture des tickets et du board.
- Ticket #29 : activation de GitHub Pages en mode « GitHub Actions » par l'API
  (`gh api -X POST repos/<dépôt>/pages -f build_type=workflow`), vérification de l'état du site et des
  exécutions de l'action (`gh run list`).

## Qualités observées
- Toutes les opérations courantes tiennent en une commande, réutilisable et traçable.
- `gh api` donne accès à toute l'API REST, y compris aux réglages absents des sous-commandes.

## Défauts et limites observés
- `gh api` **bascule silencieusement de GET en POST dès qu'un champ `-f` est fourni** : une requête de lecture
  a tenté de créer un ticket, et n'a échoué (erreur 422) que faute de titre. Contournement : écrire les requêtes
  de lecture sans `-f` (journal d'usage de l'IA, 19/09).
- Les droits de l'API ne correspondent pas toujours à l'intuition : avec le rôle *maintain*, l'activation de
  Pages a réussi, mais l'ajout de la branche `dev` aux branches autorisées à publier a été refusé
  (« Must have admin rights to Repository », 403). Un administrateur a dû le faire dans l'interface (#29).

## Comparaison
- Méthode précédente : interface web de GitHub.
- L'interface reste préférable pour les réglages ponctuels réservés aux administrateurs, et pour relire une
  pull request ligne à ligne.

## Décision
Adopté.
- Motif : gain net pour les opérations répétées et scriptables ; les pièges observés sont connus et documentés.

## Preuves
- Journal d'usage de l'IA, entrée du 19/09 (bascule GET vers POST).
- Ticket #29 et pull request #42 (Pages, droits de l'environnement `github-pages`).
- Pull request #42 (création en ligne de commande).
