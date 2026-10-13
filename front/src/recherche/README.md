# Moteur de recherche du site (#48)

`moteur.js` applique les règles de lecture de l'export du notebook 02 (`docs/etudes/indexation/02_indexation.md`, section 6). Il ne contient aucune interface : il charge et vérifie l'index, charge le modèle et classe les passages. L'interface reste à écrire dans `App.jsx` (#48, #53).

## Ce que fait le module

- `chargerIndex(base)` : lit l'en-tête `index_m2.json`, puis la matrice et les passages ; refuse l'index si le format, la taille ou une empreinte SHA-256 ne correspond pas.
- `chargerModele(pipeline, entete, { suivre })` : charge le modèle à la révision et avec la précision de l'en-tête (q8) ; `suivre` reçoit la progression du téléchargement.
- `classer(matrice, N, D, q, k)` : produit scalaire avec les 4 240 passages et les k meilleurs ; à score égal, l'ordre de l'index.
- `creerMoteur(pipeline, base)` : les trois ensemble ; `rechercher(question, 5)` renvoie les passages avec leur rang, leur score, leur fiche, leur section et leur lien profond (`url_citation`) ; `seuilAbstention` donne le seuil applicable à l'en-tête, ou `null`.
- `horsPerimetre(resultats, seuil)` : vrai si le meilleur passage reste strictement sous le seuil. Le hook `useMoteur` renvoie ce drapeau avec chaque recherche (`{ resultats, duree, horsPerimetre }`).

## Abstention

- **Le seuil.** `ABSTENTION.seuil` vaut 0,8559679388999939. Il a été fixé le 10 octobre 2026, avant la mesure, comme le 5e centile des scores maximaux de 479 variantes du CDTN rédigées en question (protocole du notebook 03, section 8.2).
- **Ce qu'il vaut.** Sur le lot de test, il garde 72 des 73 questions du corpus et rejette 9 des 24 questions hors corpus. Il signale donc surtout les saisies sans rapport avec le droit du travail, et non les questions juridiques absentes de nos fiches.
- **Pour quel modèle.** Il ne vaut que pour le modèle (`Xenova/multilingual-e5-small`, révision `761b726d`, q8) et l'index (`2ec45586…`) avec lesquels il a été calculé. Pour un autre en-tête, l'encodeur ajusté par exemple, `seuilAbstention` vaut `null` et aucune question n'est signalée : le seuil doit alors être recalculé par `scripts/evaluation/cdtn_seuil.py`.
- **À l'affichage.** Ne pas masquer les passages sans recours : un message signale la question, et le visiteur peut afficher quand même les passages les plus proches (#53).

## Intégration dans le site

1. Ajouter Transformers.js à la version figée du site : `npm install @huggingface/transformers@4.3.0 --save-exact`, dans `front/`.
2. Les trois fichiers de l'index sont versionnés dans `front/public/index/` (12,3 Mio ; option A, validée le 11 octobre 2026). Ne pas les régénérer : voir `front/public/index/SOURCES.md`.
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
- Abstention : le classement du site redonne le seuil et ses 24 rejets sur les 479 variantes du CDTN (test sauté sans `data/evaluation/cdtn/`). Le 13 octobre 2026, sur les 97 questions du lot de test, le moteur prend les mêmes décisions que le notebook 03, avec un écart de score d'au plus 6e-8 et aucune question à moins de 6,9e-4 du seuil.
- Parité complète dans le navigateur : `scripts/indexation/parite_moteur.html`. Le 10 octobre 2026, les 24 requêtes du contrôle donnent les mêmes 5 premiers passages et les mêmes scores que la page de contrôle du notebook 02, à l'écart nul, en 19,7 ms par question en médiane, encodage compris.
