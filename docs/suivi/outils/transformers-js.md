# Transformers.js

## Identification
- Version : 4.3.0 (figée dans les pages de contrôle de la PR #40, à figer dans `front/package.json` avec #48 :
  identique pour tous)
- Nature : bibliothèque d'inférence dans le navigateur
- Assignés : Mahé (J2, PR #40) ; prévus : Vaneck, Maïmouna, Rémy (#48), Rémy (#49), Mahé (#50)
- Coordination : Mahé
- Période d'utilisation : (Mahé) depuis le 27 septembre 2026 (notebook 02), puis le 10 octobre (notebook 03, #48)
- Besoin du projet auquel il répond : encoder la question du visiteur dans son navigateur, sans serveur, pour la recherche sémantique du volet A.

## Mise en place
- Temps avant le premier résultat utile : (Mahé) non relevé sur le moment.
- Installation et configuration :
  - (Mahé) Aucune installation pour les pages de contrôle : module ES importé depuis le CDN jsdelivr, version épinglée 4.3.0, et `env.allowLocalModels = false` pour ne chercher le modèle que sur le Hub (`scripts/indexation/controle_navigateur.html`, PR #40).
- Prérequis découverts en chemin :
  - (Mahé) Pages servies en HTTP sur la seule interface locale (`python -m http.server 8765 --bind 127.0.0.1`), pilotées par Playwright pour les mesures (PR #40, #62, #67).
- Difficultés non expliquées par la documentation :
  - (Mahé) Le `dtype` par défaut dépend du matériel : q8 en WASM, fp32 partout ailleurs, WebGPU compris, d'après `src/utils/dtypes.js` de la 4.3.0. Il faut donc toujours le passer explicitement (PR #40).
  - (Mahé) Sans `{ pooling: "mean", normalize: true }`, l'extracteur renvoie un vecteur par token ; l'exemple de la carte du modèle Xenova omet ces deux options (PR #40, `docs/etudes/indexation/02_indexation.md`, section 6).

## Usage réel
- Tâche réalisée, ticket ou pull request :
  - (Mahé) Contrôles du notebook 02 (#30, PR #40), encodage des questions du notebook 03 et des variantes du CDTN (#46, PR #62), moteur du site (#48, PR #67).
- Commande, configuration ou scénario :
  - (Mahé) `pipeline("feature-extraction", "Xenova/multilingual-e5-small", { revision, dtype: "q8", device: "wasm" })`, préfixe `query: `, options lues dans l'en-tête de l'index.
- Résultat obtenu :
  - (Mahé) En q8, le premier résultat est celui du calcul exact pour 91,8 % des requêtes, et il reste dans le top 5 pour 99,9 % (notebook 02, section 8).
  - (Mahé) Fidélité au fp32 de Python : cosinus d'au moins 0,9928 sur les 8 questions de calibration et 0,9926 sur 479 variantes du CDTN (PR #62).
  - (Mahé) 24 requêtes de contrôle sur 24 identiques à la page de contrôle, écart de score nul, 19,7 ms par question en médiane, encodage compris (PR #67).
- Temps gagné ou perdu, s'il peut être estimé :

## Qualités observées
- (Mahé) Déterministe : vecteurs identiques bit à bit entre deux sessions (notebook 02), et mêmes scores le 27 septembre et le 10 octobre sur les 24 requêtes du contrôle (PR #67).
- (Mahé) Rapide sur un poste ordinaire : environ 18 ms d'encodage par question en WASM, 1,7 ms pour la recherche exhaustive sur 4 240 passages (notebook 02).

## Défauts et limites observés
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas :
  - (Mahé) Le q8 du navigateur ne calcule pas comme le q8 de Python : la simulation en Python sous-estimait l'erreur réelle du site (96,5 % de premier résultat identique en Python, 91,8 % dans le navigateur). Une mesure de qualité doit se faire dans un vrai navigateur (notebook 02, section 8).
  - (Mahé) Premier chargement lourd : 112,8 Mio de modèle q8, au-delà de la cible de 50 Mio du rapport J2 (risque R2, #50).

## Comparaison
- Méthode ou outil utilisé auparavant : (Mahé) `sentence-transformers` en Python, en fp32, pour l'index.
- Différences observées : (Mahé) en fp32, le navigateur reproduit Python exactement (cosinus 1) ; en q8, presque.
- Cas où l'ancienne méthode reste préférable : (Mahé) l'encodage des 4 240 passages de l'index, fait une fois hors ligne.

## Décision
(Mahé) Adopté.
- Motif : (Mahé) seule façon de tenir l'exigence du sujet, une inférence entièrement dans le navigateur, sans serveur ; l'écart du q8 est mesuré, et le notebook 03 le teste (famille F3).

## À retenir pour le rapport
- Apport : (Mahé) une recherche sémantique sans serveur, en une vingtaine de millisecondes par question.
- Principale limite : (Mahé) le poids du modèle au premier chargement.
- Ce que la documentation ne dit pas : (Mahé) la précision par défaut change selon le matériel, et l'extracteur ne fait ni moyenne ni normalisation par défaut.

## Preuves
- Rapport J2 : faisabilité mesurée dans le navigateur (19,8 ms par requête).
- Pull request #40 : pages de contrôle exécutées dans un vrai navigateur, écart observé entre le q8 du navigateur et celui de Python.
- Pull request #62 : `scripts/evaluation/encodage_navigateur.html`, fidélité au fp32 sur la calibration et sur le CDTN.
- Pull request #67 : `front/src/recherche/moteur.js` et `scripts/indexation/parite_moteur.html`, parité sur les 24 requêtes du contrôle.
