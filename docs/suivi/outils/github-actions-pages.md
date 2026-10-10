# GitHub Actions et GitHub Pages

## Identification
- Version : `actions/deploy-pages` v5, `actions/upload-pages-artifact` v5 (figées dans
  `.github/workflows/deploiement-volet-a.yml` : identiques pour tous)
- Nature : service d'intégration et de publication
- Assignés : Vaneck (#29) ; prévus : Maïmouna, Mahé, Rémy (#48) ; Jibril (#53)
- Coordination : Vaneck
- Période d'utilisation : depuis le 30 septembre 2026
- Besoin du projet auquel il répond : construire le site du volet A et le publier automatiquement à l'URL définitive à chaque fusion dans `dev`.

## Mise en place
- Temps avant le premier résultat utile : (Vaneck) site en ligne le jour même de la fusion de la PR #42
  (30/09), première exécution de l'action réussie.
- Installation et configuration : (Vaneck) aucune installation ; un fichier de workflow à deux étapes,
  construction (`npm ci` puis `npm run build` dans `front/`, Node 22) et publication (`upload-pages-artifact`
  puis `deploy-pages`), déclenché par un envoi sur `dev` touchant `front/` ou à la demande
  (`workflow_dispatch`). Source de Pages réglée sur « GitHub Actions », par l'API (`gh api -X POST
  repos/<dépôt>/pages -f build_type=workflow`).
- Prérequis découverts en chemin :
  - (Vaneck) GitHub Pages est indisponible sur un dépôt privé en plan gratuit : le dépôt a dû passer en public
    (contrainte relevée au rapport J2, décision d'équipe du 30/09).
  - (Vaneck) Le workflow doit déclarer les permissions `pages: write` et `id-token: write`.
- Difficultés non expliquées par la documentation :
  - (Vaneck) L'environnement `github-pages`, créé automatiquement à l'activation, **n'autorise que la branche par
    défaut (`main`) à publier**. Publier depuis `dev` exige de l'ajouter aux branches autorisées, réglage
    réservé à un administrateur : avec le rôle *maintain*, l'API répond « Must have admin rights to
    Repository » (403). Sans ce réglage, la construction réussit et seule la publication échoue.

## Usage réel
- Tâche réalisée, ticket ou pull request : (Vaneck) ticket #29, pull request #42, déploiement du site du volet A
  à https://datatigersnlp.github.io/data_tigers_nlp/.
- Commande, configuration ou scénario : (Vaneck) fusion de la PR dans `dev`, exécution automatique de l'action,
  contrôle avec `gh run list` et une requête HTTP sur l'URL ; le pied de page affiche le commit déployé
  (`GITHUB_SHA`, sept caractères) pour vérifier que la version en ligne est la dernière.
- Résultat obtenu : (Vaneck) exécution réussie, URL répondant en HTTP 200, page et ressources chargées sous
  `/data_tigers_nlp/`.
- Temps gagné ou perdu, s'il peut être estimé : (Vaneck) chaque redéploiement est automatique ; aucune
  manipulation manuelle de fichiers construits.

## Qualités observées
- (Vaneck) Publication sans serveur ni compte externe, gratuite et sans limite de minutes sur un dépôt public.
- (Vaneck) Le site suit `dev` sans intervention : fusionner une PR suffit pour le mettre à jour.
- (Vaneck) Redéploiement possible sans nouveau commit, par le bouton « Run workflow ».

## Défauts et limites observés
- (Vaneck) Restriction de branche de l'environnement `github-pages` non signalée à l'activation, et
  modifiable seulement par un administrateur (voir « Mise en place »).
- (Vaneck) Les exemples de configuration rencontrés citent souvent des versions majeures antérieures des actions
  officielles : vérifier la dernière version publiée avant de les copier (v7 pour `checkout` et `setup-node`,
  v5 pour les actions Pages au 30/09).
- (Vaneck) Sur un dépôt privé en plan gratuit, Pages n'est pas disponible.

## Comparaison
- Méthode ou outil utilisé auparavant : aucun déploiement avant #29 ; l'alternative courante est de pousser à la
  main le dossier construit sur une branche `gh-pages`.
- Différences observées : (Vaneck) avec l'action, la construction est refaite à partir des sources à chaque
  fois, et aucun fichier construit n'est versionné.
- Cas où l'ancienne méthode reste préférable : (Vaneck) aucun observé à ce stade.

## Décision
Adopté.
- Motif : (Vaneck) déploiement fiable et automatique depuis `dev`, une fois le réglage de l'environnement fait.

## À retenir pour le rapport
- Apport : publication automatique du volet A à chaque fusion, sans serveur.
- Principale limite : l'environnement `github-pages` n'autorise par défaut que `main`, et seul un administrateur
  peut changer ce réglage ; l'échec n'apparaît qu'au moment de publier.
- Ce que la documentation ne dit pas clairement : ce verrou de branche et les droits qu'il exige.

## Preuves
- Ticket #29 et pull request #42 : workflow `.github/workflows/deploiement-volet-a.yml`, premier déploiement réussi le 30/09.
- Réglage de l'environnement `github-pages` : la branche `dev` a dû être autorisée par un administrateur (#29).
- `front/README.md` : procédure de déploiement et de redéploiement.
