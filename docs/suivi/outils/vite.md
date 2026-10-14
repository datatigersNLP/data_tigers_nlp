# Vite (avec React et Tailwind CSS)

## Identification
- Version : Vite 8.3.0, React 19.3.0, Tailwind CSS 4.3.3 (figées dans `front/package.json` et
  `front/package-lock.json` : identiques pour tous)
- Nature : outil de construction du site et serveur de développement
- Assignés : Vaneck, Maïmouna (#7, #29) ; prévus : Mahé, Rémy (#48) ; Jibril (#53)
- Coordination : Vaneck, Jibril
- Période d'utilisation : depuis le 30 septembre 2026 (création du site du volet A, #29)
- Besoin du projet auquel il répond : construire le site statique du volet A.

## Mise en place
- Temps avant le premier résultat utile : (Vaneck) quelques minutes : installation des dépendances en 14 s
  (36 paquets), première construction en environ 0,5 s.
- Installation et configuration : (Vaneck) projet créé dans `front/` avec des versions exactes (sans `^`) ;
  Tailwind 4 branché par le greffon `@tailwindcss/vite`, sans fichier de configuration, les couleurs de la
  charte déclarées dans `@theme` ; installation reproductible avec `npm ci`.
- Prérequis découverts en chemin :
  - (Vaneck) Node.js 20.19 ou plus récent, ou 22.12 et plus (champ `engines` de Vite 8).
  - (Vaneck) `@vitejs/plugin-react` 6.1.1 exige Vite 8 ou plus.
- Difficultés non expliquées par la documentation :
  - (Vaneck) Le chemin de base (`base`) doit valoir `/data_tigers_nlp/` pour GitHub Pages : sans lui, la
    construction réussit et le site se déploie, mais la page reste blanche, car les fichiers JS et CSS sont
    cherchés à la racine du domaine. La défaillance est silencieuse (risque déjà relevé au ticket #7).

## Usage réel
- Tâche réalisée, ticket ou pull request : (Vaneck) page de préfiguration du volet A, ticket #29, pull request
  #42.
- Commande, configuration ou scénario : (Vaneck) `npm run build`, puis `npm run preview` pour servir le site
  comme en production sous `/data_tigers_nlp/` ; vérification que la page, le JS, le CSS et l'icône répondent
  en HTTP 200 ; captures en largeur ordinateur et téléphone (375 px).
- Résultat obtenu : (Vaneck) JS de 227 Kio (71 Kio compressé), CSS de 16 Kio (4 Kio compressé) ; version et
  date de construction injectées dans la page par l'option `define`.
- Temps gagné ou perdu, s'il peut être estimé : (Vaneck) constructions quasi instantanées, aucun temps perdu
  à attendre.

## Qualités observées
- (Vaneck) Construction très rapide, moins d'une seconde pour le site actuel.
- (Vaneck) `vite preview` reproduit le chemin de base de GitHub Pages en local : on vérifie l'absence de page
  blanche avant de déployer.
- (Vaneck) Tailwind 4 s'intègre sans fichier de configuration ; le CSS livré ne contient que les classes
  utilisées.

## Défauts et limites observés
- (Vaneck) Erreur de chemin de base silencieuse : rien ne la signale à la construction (voir « Mise en place »).
- (Vaneck) Avec un chemin de base, le serveur de développement sert aussi le site sous `/data_tigers_nlp/` :
  l'adresse `http://localhost:5173/` seule ne montre rien.

## Comparaison
- Méthode ou outil utilisé auparavant : (Vaneck) alternatives écartées au ticket #7 : Preact avec htm, et
  JavaScript natif chargé depuis un CDN.
- Différences observées : (Vaneck) React et Tailwind coûtent peu dans le site livré (environ 70 Kio compressés
  mesurés au #7) et apportent un modèle à composants pour gérer les états de l'interface.
- Cas où l'ancienne méthode reste préférable : (Vaneck) une page sans état, sans interaction, pourrait se passer
  d'une chaîne de construction.

## Décision
Adopté.
- Motif : (Vaneck) chaîne rapide, reproductible, compatible avec GitHub Pages une fois le chemin de base réglé.

## À retenir pour le rapport
- Apport : un site statique construit en moins d'une seconde, vérifiable en local exactement comme en ligne.
- Principale limite : une erreur de chemin de base produit une page blanche sans aucun message d'erreur.
- Ce que la documentation ne dit pas clairement : qu'il faut tester avec `vite preview` sous le bon chemin avant
  chaque déploiement.

## Preuves
- Ticket #7 : construction d'essai et choix de la chaîne front-end.
- Ticket #29 et pull request #42 : site du volet A dans `front/`, chemin de base `/data_tigers_nlp/` pour éviter la page blanche.
- `front/vite.config.js`, `front/package.json`, `front/README.md`.
