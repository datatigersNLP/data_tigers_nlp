# Site du volet A

Recherche sémantique dans les fiches travail-emploi, exécutée dans le navigateur (cas A3).

**URL définitive : https://datatigersnlp.github.io/data_tigers_nlp/**

Chaîne retenue au rapport J2 : Vite 8.3.0, React 19.3.0, Tailwind CSS 4.3.3. Versions figées dans
`package.json` et `package-lock.json`.

## Travailler en local

Prérequis : Node.js 20.19 ou plus récent (22 recommandé).

```bash
cd front
npm ci            # installe les versions exactes du package-lock.json
npm run dev       # serveur de développement, rechargement automatique
npm run build     # construit le site dans front/dist/
npm run preview   # sert front/dist/ comme en production
```

Le site est servi sous `/data_tigers_nlp/`, en local comme en ligne :
http://localhost:5173/data_tigers_nlp/ avec `npm run dev`, http://localhost:4173/data_tigers_nlp/ avec
`npm run preview`.

## Chemin de base

GitHub Pages sert le site dans un sous-dossier portant le nom du dépôt. La clé `base` de
`vite.config.js` vaut donc `/data_tigers_nlp/`. Sans elle, la construction réussit et le site se déploie,
mais la page reste blanche : les fichiers JavaScript et CSS sont cherchés à la racine du domaine. Si le dépôt
est renommé, cette valeur doit changer avec lui.

## Déploiement

Le déploiement est automatique : la GitHub Action `.github/workflows/deploiement-volet-a.yml` construit le
site et le publie à chaque envoi sur `dev` qui modifie `front/` ou l'action elle-même. Pour déployer, il
suffit donc de fusionner une pull request dans `dev`.

Pour redéployer sans nouveau commit : onglet **Actions**, action « Déploiement du volet A », bouton
**Run workflow**, branche `dev`.

Le pied de page affiche la version déployée (les 7 premiers caractères du commit) et la date de
construction. Pour vérifier qu'un déploiement a abouti, on compare cette version au dernier commit de `dev`.

### Réglages du dépôt, faits une seule fois

1. **Settings > Pages > Build and deployment > Source** : « GitHub Actions ».
2. **Settings > Environments > github-pages > Deployment branches and tags** : ajouter `dev`. Par défaut,
   GitHub n'autorise que la branche principale à publier. Ce réglage demande le rôle admin du dépôt.

## Vérifications après déploiement

- La page s'ouvre sans être connecté à GitHub, dans une fenêtre de navigation privée.
- Elle s'affiche encore après une actualisation (F5).
- Dans les outils de développement (F12), onglet Réseau : aucun fichier en erreur 404.
- La version du pied de page correspond au dernier commit de `dev`.
