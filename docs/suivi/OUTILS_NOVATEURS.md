# Suivi des outils novateurs

Ticket #25. Le sujet accorde jusqu'à trois points bonus pour une analyse substantielle de **cinq outils
novateurs réellement employés** pendant le projet. Une liste ou une reprise de la documentation officielle n'a
aucune valeur : ce qui compte, ce sont les observations faites au moment de l'usage, difficultés et échecs
compris. Ce fichier sert à les consigner au fil du projet, avant la sélection des cinq outils du rapport final.

## Principes

1. **Suivre plus de cinq candidats au départ**, n'en retenir que cinq pour le rapport final.
2. **Un outil n'entre dans le tableau que s'il a été réellement utilisé** pour une tâche du projet. Un outil
   seulement évoqué ou installé n'est jamais présenté comme testé.
3. **Chaque observation renvoie à une preuve** : ticket, pull request, commit, commande, mesure ou capture.
4. **Les échecs et les abandons sont conservés**, jamais supprimés : ce sont souvent les retours les plus
   instructifs.
5. **Comparer à la méthode utilisée auparavant** lorsque c'est pertinent.
6. **Deux outils presque identiques ne font pas deux retours** si les observations sont les mêmes.

**Différence avec le journal d'usage de l'IA** (`docs/journal/JOURNAL_USAGE_IA.md`) : le journal consigne
chaque usage d'un assistant d'IA, session par session, pour la traçabilité exigée par le sujet. Ce fichier-ci
évalue un outil dans la durée : mise en place, qualités, défauts, décision. Un assistant d'IA peut figurer dans
les deux, avec des contenus différents.

## Comment contribuer

Chaque outil a un **référent** : la personne qui l'a le plus utilisé. Il remplit la fiche et la tient à jour ;
les autres utilisateurs y ajoutent leurs observations.

1. **Remplir la fiche dès le premier usage réel**, tant que les difficultés sont encore en mémoire : copier le
   modèle ci-dessous dans la partie « Fiches » et mettre à jour la ligne de l'outil dans le tableau.
2. **L'envoyer par une pull request vers `dev`**, depuis la branche du ticket où l'outil a servi ou depuis une
   branche dédiée (`docs/25-fiche-<outil>`). Un autre membre relit avant la fusion.
3. **La compléter au fil du projet** : nouvel échec, contournement, mesure, temps gagné ou perdu. Un outil
   abandonné n'est pas supprimé : sa décision passe à « abandonné », avec le motif.
4. **En dire une phrase au Weekly** : ce qui a changé pour l'outil depuis la dernière revue.
5. **Présélection, puis rapport final** : l'équipe retient les cinq retours les plus riches, rédigés dans le
   rapport ; les autres fiches restent dans le dépôt comme trace.

## Calendrier proposé (à valider en Weekly)

| Étape | Moment |
|---|---|
| Revue courte du tableau | à chaque Weekly, cinq minutes au plus |
| Présélection des cinq outils | Weekly 8 (4 novembre), avant le jalon J3 |
| Fiches des cinq outils finalisées | avant la rédaction du rapport final |

**Critères de sélection proposés** : un usage réel et répété, des preuves disponibles, au moins une difficulté
ou une limite observée, et un retour qui dit quelque chose que la documentation officielle ne dit pas.

## Tableau de suivi

Les référents sont proposés d'après les preuves existantes et restent à confirmer en Weekly. Pour un outil utilisé par toute l'équipe, chacun complète la fiche avec ses propres observations, signées de son nom.

| Outil | Version | Utilisateurs | Usage réel | Preuves | Intérêt du retour | Référent proposé | Décision |
|---|---|---|---|---|---|---|---|
| GitHub CLI (`gh`) | 2.101.0 | équipe | depuis le 19/09 | journal IA (19/09), PR #42, ticket #29 | élevé : pièges d'API et de droits observés | toute l'équipe | adopté |
| GitHub Actions et Pages | `actions/deploy-pages` v5 | Vaneck | depuis le 30/09 | ticket #29, PR #42, workflow `deploiement-volet-a.yml` | moyen : chemin de base et droits de l'environnement | Vaneck | adopté |
| Transformers.js | 4.3.0 | à compléter | depuis le 19/09 | rapport J2 (faisabilité), PR #40 (pages de contrôle) | élevé : écart entre navigateur et Python mesuré | à désigner | à compléter |
| ONNX Runtime (Python et Web) | 1.30.0 (Python) | Mahé, Rémy | PR #40, ticket #49 | PR #40, notebook 02, section 8 ; export et quantification de l'encodeur ajusté (`scripts/adaptation/06_exporter_onnx.py`, branche `feat/49-ajustement-encodeur`) | élevé : critère de parité échoué puis diagnostiqué | Mahé | à compléter |
| `uv` | à compléter | Mahé, Vaneck | PR #39, #40 | fichiers `requirements-lock.txt` multiplateformes, relecture de la PR #39 | moyen : reproductibilité entre Windows et macOS | Mahé | à compléter |
| Playwright | à compléter | à compléter | rapport J2 | rapport J2 (Chromium piloté pour la mesure de faisabilité) ; tests de l'interface du volet A prévus (#48, #53) | à évaluer | Vaneck | à compléter |
| Ollama | 0.34.4 | Jibril, Rémy | PR #41, ticket #49 | `docs/etudes/inference_locale_qwen.md`, `scripts/inference/test_qwen.ps1` ; génération de paires d'entraînement avec Qwen (`scripts/adaptation/03_generer_paires_locales.py`, branche `feat/49-ajustement-encodeur`) | élevé : échec d'import contourné | Jibril | à compléter |
| Assistants de développement IA | à compléter | équipe | depuis le début | journal d'usage de l'IA | à évaluer | toute l'équipe | à compléter |
| Sentence Transformers | 6.1.0 | Rémy | ticket #49 | ajustement contrastif de l'encodeur (`scripts/adaptation/04_ajuster_encodeur.py`), étude `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md`, branche `feat/49-ajustement-encodeur` | élevé : mesure avant et après ajustement | Rémy | à compléter |
| Vite (avec React et Tailwind CSS) | 8.3.0 | Vaneck, Maïmouna | tickets #7 et #29 | construction d'essai (#7), site du volet A en ligne (#29, PR #42), `front/` | moyen : chemin de base et page blanche, suite avec #48 et #53 | Vaneck ou Maïmouna, à confirmer | adopté |

## Modèle de fiche

Copier ce modèle pour chaque outil, sous un titre de niveau 3.

```markdown
### Nom de l'outil

**Identification**
- Version :
- Nature : application, bibliothèque, environnement, agent, assistant, service ou autre
- Utilisateurs :
- Période d'utilisation :
- Besoin du projet auquel il répond :

**Mise en place**
- Temps avant le premier résultat utile :
- Installation et configuration :
- Prérequis découverts en chemin :
- Difficultés non expliquées par la documentation :

**Usage réel**
- Tâche réalisée, ticket ou pull request :
- Commande, configuration ou scénario :
- Résultat obtenu :
- Temps gagné ou perdu, s'il peut être estimé :

**Qualités observées**
- 

**Défauts et limites observés**
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas :

**Comparaison**
- Méthode ou outil utilisé auparavant :
- Différences observées :
- Cas où l'ancienne méthode reste préférable :

**Décision** : adopté / conservé pour certains usages / abandonné / à réévaluer
- Motif :

**Preuves**
- Tickets, pull requests, captures, mesures :
```

## Fiches

### GitHub CLI (`gh`)

**Identification**
- Version : 2.101.0
- Nature : application en ligne de commande
- Utilisateurs : équipe (premier usage consigné au journal le 19/09) ; fiche commune à toute l'équipe, première version rédigée par Vaneck
- Période d'utilisation : depuis le 19 septembre 2026
- Besoin du projet auquel il répond : manipuler tickets, pull requests, board et réglages du dépôt sans passer
  par l'interface web, et rendre ces opérations reproductibles dans des scripts.

**Mise en place**
- Installation puis `gh auth login`.
- Prérequis découvert en chemin : la lecture du board (GitHub Projects) exige une portée supplémentaire,
  `read:project`, à ajouter au jeton avec `gh auth refresh -s read:project`. Sans elle, les commandes
  `gh project` échouent.

**Usage réel**
- Création de la pull request #42, assignation, lecture des tickets et du board.
- Ticket #29 : activation de GitHub Pages en mode « GitHub Actions » par l'API
  (`gh api -X POST repos/<dépôt>/pages -f build_type=workflow`), vérification de l'état du site et des
  exécutions de l'action (`gh run list`).

**Qualités observées**
- Toutes les opérations courantes tiennent en une commande, réutilisable et traçable.
- `gh api` donne accès à toute l'API REST, y compris aux réglages absents des sous-commandes.

**Défauts et limites observés**
- `gh api` **bascule silencieusement de GET en POST dès qu'un champ `-f` est fourni** : une requête de lecture
  a tenté de créer un ticket, et n'a échoué (erreur 422) que faute de titre. Contournement : écrire les requêtes
  de lecture sans `-f` (journal d'usage de l'IA, 19/09).
- Les droits de l'API ne correspondent pas toujours à l'intuition : avec le rôle *maintain*, l'activation de
  Pages a réussi, mais l'ajout de la branche `dev` aux branches autorisées à publier a été refusé
  (« Must have admin rights to Repository », 403). Un administrateur a dû le faire dans l'interface (#29).

**Comparaison**
- Méthode précédente : interface web de GitHub.
- L'interface reste préférable pour les réglages ponctuels réservés aux administrateurs, et pour relire une
  pull request ligne à ligne.

**Décision** : adopté.
- Motif : gain net pour les opérations répétées et scriptables ; les pièges observés sont connus et documentés.

**Preuves**
- Journal d'usage de l'IA, entrée du 19/09 (bascule GET vers POST).
- Ticket #29 et pull request #42 (Pages, droits de l'environnement `github-pages`).
- Pull request #42 (création en ligne de commande).
