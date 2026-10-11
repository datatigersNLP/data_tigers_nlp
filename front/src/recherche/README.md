# Moteur de recherche du site (#48)

`moteur.js` applique les règles de lecture de l'export du notebook 02 (`docs/etudes/indexation/02_indexation.md`, section 6). Il ne contient aucune interface : il charge et vérifie l'index, charge le modèle et classe les passages. L'interface reste à écrire dans `App.jsx` (#48, #53).

## Ce que fait le module

- `chargerIndex(base)` : lit l'en-tête `index_m2.json`, puis la matrice et les passages ; refuse l'index si le format, la taille ou une empreinte SHA-256 ne correspond pas.
- `chargerModele(pipeline, entete, { suivre })` : charge le modèle à la révision et avec la précision de l'en-tête (q8) ; `suivre` reçoit la progression du téléchargement.
- `classer(matrice, N, D, q, k)` : produit scalaire avec les 4 240 passages et les k meilleurs ; à score égal, l'ordre de l'index.
- `creerMoteur(pipeline, base)` : les trois ensemble ; `rechercher(question, 5)` renvoie les passages avec leur rang, leur score, leur fiche, leur section et leur lien profond (`url_citation`).

## Intégration dans le site

1. Ajouter Transformers.js à la version figée du site : `npm install @huggingface/transformers@4.3.0 --save-exact`, dans `front/`.
2. Copier les trois fichiers de `data/indexation/site/` dans `front/public/index/` (12,3 Mio au total ; décision de versionnement à prendre, voir la PR).
3. Dans le composant :

```
import { pipeline } from "@huggingface/transformers";
import { creerMoteur } from "./recherche/moteur.js";

const moteur = await creerMoteur(pipeline, import.meta.env.BASE_URL + "index/", {
  suivre: (p) => { /* afficher p.status et p.progress pendant le premier chargement */ },
});
const resultats = await moteur.rechercher(question, 5);
```

`import.meta.env.BASE_URL` vaut `/data_tigers_nlp/` une fois en ligne : sans lui, les fichiers seraient cherchés à la racine du domaine.

## Contrôles

- Tests sans dépendance : `node --test front/src/recherche/moteur.test.js`. Les tests sur les vrais fichiers lisent `data/indexation/` ; ils sont sautés si l'export est absent (variable facultative `RACINE_DONNEES` pour pointer vers un clone qui l'a).
- Parité complète dans le navigateur : `scripts/indexation/parite_moteur.html`. Le 10 octobre 2026, les 24 requêtes du contrôle donnent les mêmes 5 premiers passages et les mêmes scores que la page de contrôle du notebook 02, à l'écart nul, en 19,7 ms par question en médiane, encodage compris.
