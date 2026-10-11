# Playwright

## Identification
- Version : variable selon les membres, voir « Versions utilisées »
- Nature : bibliothèque d'automatisation de navigateur
- Assignés : Mahé (mesure de faisabilité du J2), Vaneck (#48) ; prévus : Vaneck, Jibril (#53)
- Coordination : Vaneck, Jibril
- Période d'utilisation : (Vaneck) depuis le 11 octobre 2026 (#48)
- Besoin du projet auquel il répond : piloter un vrai navigateur pour mesurer la recherche et tester l'interface du volet A.

## Versions utilisées
Chaque membre tient sa propre ligne à jour.

| Membre | Version | Système | Remarque |
|---|---|---|---|
| Mahé | à compléter | à compléter | mesure de faisabilité du J2 |
| Vaneck | `playwright-core` 1.64.0 | Windows | pilote Microsoft Edge déjà installé (`channel: "msedge"`), sans navigateur téléchargé |
| Jibril | à compléter | à compléter | |

## Mise en place
- Temps avant le premier résultat utile :
  - (Vaneck) Quelques minutes : outil déjà utilisé dans un projet précédent, paquet installé en 4 s, premier script
    fonctionnel dans la même session.
- Installation et configuration :
  - (Vaneck) `npm install playwright-core` dans un dossier de travail hors du dépôt : la variante `core` ne télécharge
    aucun navigateur. Le script lance Edge, déjà présent sur Windows, par `chromium.launch({ channel: "msedge" })`, en
    mode sans interface.
- Prérequis découverts en chemin :
  - (Vaneck) Les pages à tester doivent être servies par HTTP (`vite preview` pour le site,
    `python -m http.server 8765 --bind 127.0.0.1` pour les pages de contrôle du notebook 02) : le site vérifie
    l'empreinte de l'index avec `crypto.subtle`, disponible seulement en HTTPS ou sur localhost.
- Difficultés non expliquées par la documentation :
  - (Vaneck) Chaque contexte de navigateur part d'un cache vide : le modèle de 113 Mo est retéléchargé à chaque
    exécution, ce qui ajoute environ 50 s par parcours.

## Usage réel
- Tâche réalisée, ticket ou pull request :
  - (Vaneck) Relecture de la PR #67 et reproduction du notebook 02 : page `controle_navigateur.html` exécutée dans Edge
    sur mon propre export.
  - (Vaneck) Ticket #48, PR #71 : test de bout en bout de l'interface de chat avant ouverture de la PR.
- Commande, configuration ou scénario :
  - (Vaneck) Pages de contrôle : attente du lien de téléchargement (`#telechargement a`), puis lecture directe de
    `window.RESULTATS` par `page.evaluate`, sans cliquer sur le lien ni gérer de téléchargement de fichier.
  - (Vaneck) Chat : attente que la recherche soit prête, clic sur un exemple, question tapée au clavier
    (`page.fill`, `Enter`), comptage des passages, relevé des liens, captures pleine page en largeur ordinateur et
    téléphone (`isMobile`, 375 px).
  - (Vaneck) État d'erreur : `page.route()` bloque Hugging Face pour simuler une coupure réseau, puis le débloque avant
    un clic sur « Réessayer ».
- Résultat obtenu :
  - (Vaneck) Page de contrôle : 24 requêtes traitées en 60 s, empreintes conformes ; tests du moteur ensuite à 6 sur 6.
  - (Vaneck) Chat : recherche prête en 52 à 56 s, 5 passages par question, message d'erreur et nouvel essai
    fonctionnels, aucune erreur JavaScript relevée (`pageerror`, `console`).
- Temps gagné ou perdu, s'il peut être estimé :
  - (Vaneck) Un parcours complet rejoué en environ 2 min à chaque modification, au lieu de cliquer à la main ; c'est
    une capture de ce parcours qui a révélé une barre de progression fausse (« 1 Mo sur 16 Mo »).

## Qualités observées
- (Vaneck) Utilise un navigateur déjà installé : rien de lourd à télécharger.
- (Vaneck) Les attentes sur un élément (`waitForSelector`) suivent naturellement un chargement long, sans pause fixe.
- (Vaneck) `page.route()` permet de tester les cas d'erreur réseau, difficiles à provoquer à la main.
- (Vaneck) Captures pleine page et émulation d'un téléphone dans le même script.

## Défauts et limites observés
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas :
  - (Vaneck) Une expression régulière écrite dans un sélecteur de texte, à l'intérieur d'une chaîne JavaScript, a perdu
    son antislash : le test a échoué alors que le site fonctionnait. Les localisateurs filtrés
    (`locator("p", { hasText: … })`) évitent ce piège.
  - (Vaneck) Cache vide à chaque contexte : voir « Mise en place ».

## Comparaison
- Méthode ou outil utilisé auparavant :
  - (Vaneck) Captures d'Edge en ligne de commande (`msedge --headless --screenshot`) pour le ticket #29.
- Différences observées :
  - (Vaneck) La ligne de commande ne fait qu'une image de la page au repos : ni clic, ni saisie, ni attente d'un état.
    Elle imposait aussi une largeur minimale de fenêtre qui tronquait les captures en 390 px ; il avait fallu passer
    par un cadre de 375 px.
- Cas où l'ancienne méthode reste préférable :
  - (Vaneck) Une simple capture d'une page statique, sans aucune installation.

## Décision
(Vaneck) Adopté pour tester le parcours du site (#48, #53). À confirmer avec Jibril.
- Motif : (Vaneck) seul moyen essayé qui rejoue un vrai parcours, y compris le premier chargement et les erreurs.

## À retenir pour le rapport
- Apport : rejouer en deux minutes le parcours complet du site, erreurs réseau comprises, dans le navigateur déjà
  installé.
- Principale limite : chaque exécution repart d'un cache vide et retélécharge le modèle de 113 Mo.
- Ce que la documentation ne dit pas : qu'on peut éviter le téléchargement des navigateurs avec `playwright-core` et
  `channel: "msedge"`, et lire directement les résultats d'une page (`window.RESULTATS`) au lieu de gérer ses
  téléchargements.

## Preuves
- Rapport J2 et document de décisions du J2 : Chromium piloté par Playwright pour la mesure de faisabilité (19,8 ms par requête).
- PR #71 : tableau des vérifications du parcours de chat, faites avec Playwright.
- Journal d'usage de l'IA, sessions 23 et 24 de Vaneck : reproduction du notebook 02 et parcours du chat.
