# Jeu de questions annotées — issue #44

Ce dossier prépare le jeu de référence humain utilisé pour évaluer la recherche du volet A et le comportement du volet B. Le fichier officiel `questions_annotees.csv` ne doit contenir aucune question générée automatiquement ni aucune formulation conservée telle quelle depuis un brouillon IA.

## État initial vérifié le 3 octobre 2026

Aucun jeu spécialisé travail-emploi n'était présent dans `dev`, dans les autres branches du dépôt, dans les pull requests ni dans les commentaires de l'issue #44. Les questions déjà disponibles évoquées par Mahé appartiennent au jeu généraliste PIAF : elles servent à valider la chaîne de mesure dans l'issue #45, mais ne remplacent pas le présent jeu.

## Dimensionnement retenu

Répartition retenue avant la rédaction :

- 105 questions au total ;
- 74 questions dans le corpus et 31 hors corpus (29,5 %) ;
- 8 questions de calibration : 6 dans le corpus et 2 hors corpus ;
- 97 questions de test : 68 dans le corpus et 29 hors corpus ;
- 21 questions tirées au sort pour une seconde annotation indépendante (20 %).

Ce découpage conserve 68 questions dans le corpus dans le lot de test, seuil retenu dans le rapport J2 pour détecter un écart apparié de 15 points, tout en réservant un petit lot de calibration.

## Répartition des rédacteurs

| Rédacteur | Identifiant GitHub | Identifiants | Total | Dans le corpus | Hors corpus |
|---|---|---|---:|---:|---:|
| Jibril Bensalem | `JIBZZOU` | Q001 à Q035 | 35 | 25 | 10 |
| Maïmouna Signate | `msignate` | Q036 à Q070 | 35 | 25 | 10 |
| Vaneck Dagar | `vanecktiyo` | Q071 à Q105 | 35 | 24 | 11 |

Chacun réalise aussi 7 annotations secondaires sur les questions d'un autre rédacteur. Les 21 lignes concernées et leurs annotateurs sont préremplis dans `annotations_secondaires.csv`.

## Fichiers

- `questions_candidates_ia.csv` : 105 brouillons de travail répartis entre les trois rédacteurs ; ce fichier n'est pas le jeu de test et ne doit jamais être utilisé pour mesurer les systèmes ;
- `questions_annotees.csv` : jeu principal officiel, une ligne par question validée et reformulée par une personne ;
- `annotations_secondaires.csv` : annotations indépendantes du sous-échantillon à double annoter.

Les fichiers sont en UTF-8, séparés par des virgules. Les champs contenant une virgule, un guillemet ou un saut de ligne doivent être entourés de guillemets doubles ; un guillemet contenu dans un champ est doublé.

## Traitement obligatoire des brouillons IA

Chaque rédacteur traite uniquement les lignes qui lui sont attribuées dans `questions_candidates_ia.csv`.

1. Ouvrir la source indiquée et vérifier que l'extrait permet réellement de répondre.
2. Reformuler substantiellement la question avec ses propres mots, sans consulter les résultats du moteur ni une réponse produite par un modèle.
3. Confirmer le type `dans_corpus` ou `hors_corpus`. Pour un cas hors corpus, vérifier l'absence dans l'ensemble du corpus figé et préciser la justification.
4. Copier seulement la version humaine validée dans la ligne correspondante de `questions_annotees.csv`.
5. Ne jamais copier directement un brouillon IA dans le fichier officiel.

Les 74 brouillons dans le corpus ont fait l'objet d'un contrôle automatique contre l'instantané figé : document, URL et présence littérale de l'extrait ont été vérifiés sans erreur. Ce contrôle technique ne remplace ni la vérification du sens ni la reformulation humaine. Les 31 propositions hors corpus restent à confirmer manuellement.

## Règles de rédaction

1. La question est rédigée par une personne qui n'a pas construit l'index.
2. Pour une question `dans_corpus`, partir d'une page du périmètre travail-emploi.gouv.fr, sans consulter les passages découpés ni les résultats du moteur.
3. Employer des formulations variées : langage courant, formulation précise, reformulation sans reprendre les mots du texte et sigles usuels (CDI, CDD, RTT, CSE).
4. Ne pas concentrer le jeu sur les fiches les plus connues : répartir les questions entre thèmes et URL.
5. Une question doit appeler une réponse vérifiable dans un extrait raisonnablement court ; éviter les questions d'opinion et les questions ambiguës.
6. Pour une question `hors_corpus`, laisser `url` et `extrait` vides et expliquer brièvement dans `remarque` pourquoi la question est plausible mais absente du périmètre.
7. Ne jamais modifier une question à partir des résultats de recherche ou des réponses du modèle.

## Règles d'annotation

- `id` : identifiant stable de la forme `Q001`.
- `lot` : `calibration` ou `test`.
- `type` : `dans_corpus` ou `hors_corpus`.
- `theme` : catégorie fonctionnelle courte, définie par l'équipe.
- `question` : formulation présentée au système.
- `url` : URL canonique de la fiche pour une question dans le corpus.
- `extrait` : extrait copié mot pour mot depuis la fiche et suffisant pour répondre.
- `redacteur` : nom ou identifiant GitHub de l'auteur de la question.
- `double_annotation` : `oui` si la question appartient au sous-échantillon de 20 %, sinon `non`.
- `remarque` : cas limite, justification hors corpus ou information utile.

Pour la seconde annotation, l'annotateur ne consulte pas l'annotation principale. Il renseigne séparément `annotations_secondaires.csv`. Après gel des deux annotations, l'équipe compare l'URL puis l'extrait et renseigne les colonnes d'accord.

## Contrôles avant gel

- identifiants uniques et champs obligatoires présents ;
- exactement un lot et un type autorisés par ligne ;
- URL appartenant au périmètre pour chaque question dans le corpus ;
- extrait retrouvé mot pour mot dans la fiche ;
- URL et extrait vides pour les questions hors corpus ;
- environ 30 % de questions hors corpus ;
- au moins 68 questions dans le corpus dans le lot de test ;
- 20 % du jeu en double annotation ;
- absence de doublons ou de reformulations quasi identiques ;
- répartition raisonnable des thèmes, des URL et des styles de formulation.

Le jeu est figé par un tag avant la première mesure. Le lot de test ne doit ensuite plus être modifié à la lumière des résultats.
