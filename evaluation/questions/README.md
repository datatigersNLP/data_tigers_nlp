# Jeu de questions annotées — issue #44

Ce dossier prépare le jeu de référence humain utilisé pour évaluer la recherche du volet A et le comportement du volet B. Les questions doivent être rédigées par les membres de l'équipe. Les questions générées par une IA, même simplement reformulées ou relues, ne doivent pas être utilisées dans le jeu de test (issue #44).

Le 3 octobre 2026, les formulations et extraits IA précédemment transférés ont été retirés du jeu principal. Le fichier de brouillons a été supprimé de la version courante, sans réécrire l'historique Git. Les rédacteurs déjà exposés aux brouillons le signalent dans `remarque` ; ils ne les consultent pas pendant la nouvelle rédaction.

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

- `questions_annotees.csv` : 105 lignes réservées, avec thème, URL indicative et métadonnées ; les colonnes `question` et `extrait` restent vides jusqu'à la rédaction et l'annotation humaines ;
- `annotations_secondaires.csv` : annotations indépendantes du sous-échantillon à double annoter.

Les fichiers sont en UTF-8, séparés par des virgules. Les champs contenant une virgule, un guillemet ou un saut de ligne doivent être entourés de guillemets doubles ; un guillemet contenu dans un champ est doublé.

## Rédaction indépendante, puis annotation

1. Prendre uniquement le thème de la ligne et imaginer une situation réaliste. Ne pas consulter les anciennes questions IA, les extraits, les passages découpés ni les résultats du moteur.
2. Écrire la question avec ses propres mots et enregistrer cette première formulation avant de consulter l'URL ou la fiche.
3. Ouvrir ensuite la fiche indicative pour rechercher une réponse. L'URL peut être remplacée par celle d'une autre fiche pertinente.
4. Copier mot pour mot un extrait qui répond réellement à la question, depuis la page du site. Ne pas retoucher la question pour la faire coller à cet extrait.
5. Si aucune fiche du corpus ne répond, classer la question comme candidate `hors_corpus`, vider URL/extrait et expliquer la vérification dans `remarque`. Le simple échec du moteur ne prouve pas l'absence de réponse.
6. Confirmer humainement le type et faire relire l'annotation.

Les 74 lignes `dans_corpus` et 31 lignes `hors_corpus` sont des objectifs de répartition, pas des annotations déjà établies. En cas de reclassement, conserver l'identifiant et le lot ; ajuster avec les responsables d'autres lignes ou en ajouter avant gel pour maintenir au moins 68 questions dans le corpus dans le test. Ne jamais attribuer artificiellement un type pour satisfaire un quota.

Les contrôles réussis sur les anciens brouillons ne valident pas le nouveau jeu humain : ils doivent être refaits sur les nouvelles questions et annotations. La génération de questions par IA reste réservée aux paires d'entraînement, hors de ce jeu.

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
- `type` : `dans_corpus` ou `hors_corpus` ; les valeurs initiales sont des cibles à confirmer après rédaction.
- `theme` : catégorie fonctionnelle courte, définie par l'équipe.
- `question` : formulation présentée au système.
- `url` : URL indicative avant rédaction, puis URL canonique de la fiche effectivement annotée ; vide pour une question hors corpus.
- `extrait` : extrait copié mot pour mot depuis la fiche et suffisant pour répondre.
- `redacteur` : nom ou identifiant GitHub de l'auteur de la question.
- `double_annotation` : `oui` si la question appartient au sous-échantillon de 20 %, sinon `non`.
- `remarque` : cas limite, justification hors corpus ou information utile.

Pour la seconde annotation, l'annotateur ne consulte pas l'annotation principale. Il renseigne séparément `annotations_secondaires.csv`.

Après leur réalisation indépendante, les 21 annotations secondaires de Jibril, Maïmouna et Vaneck ont été regroupées dans un classeur Excel commun, puis exportées vers `annotations_secondaires.csv`. Le classeur commun sert à la consolidation des résultats ; il ne remplace pas le principe d'indépendance de la seconde annotation.

Après gel des deux annotations, l'équipe compare l'URL puis l'extrait et renseigne les colonnes d'accord selon les règles retenues le 6 octobre 2026 :

- `accord_url = oui` si les deux annotations utilisent la même URL canonique ;
- `accord_url = non` si les URL sont différentes, ou si une annotation trouve une réponse dans le corpus et l'autre conclut hors corpus ;
- `accord_extrait = oui` si les extraits sont identiques, ou s'ils sont différents mais correspondent au même passage et répondent tous deux à la question.
- si les deux annotations concluent `hors_corpus`, `accord_url = oui` et `accord_extrait = n/a`, puisqu'aucun extrait n'est applicable.

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
- répartition raisonnable des thèmes, des URL et des styles de formulation ;
- origine humaine des questions et éventuelle exposition préalable aux brouillons documentées ;
- recouvrement lexical question/extrait examiné comme alerte de relecture, jamais comme rejet automatique : les termes juridiques communs ne suffisent pas à prouver un biais. Ne pas utiliser cette alerte pour optimiser les questions d'après les résultats du moteur.

Le jeu est figé par un tag avant la première mesure. Le lot de test ne doit ensuite plus être modifié à la lumière des résultats.
