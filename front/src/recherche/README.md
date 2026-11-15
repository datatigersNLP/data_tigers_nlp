# Moteur de recherche du site (#48)

`moteur.js` applique les règles de lecture de l'export du notebook 02 (`docs/etudes/indexation/02_indexation.md`, section 6). Il ne contient aucune interface : il charge et vérifie l'index, charge le modèle et classe les passages. L'interface est dans `front/src/composants/` : `Conversation.jsx`, qui présente les résultats par fiche (`Fiche.jsx`, `Passage.jsx`).

## Ce que fait le module

- `chargerIndex(base)` : lit l'en-tête `index_m2.json`, puis la matrice et les passages ; refuse l'index si le format, la taille ou une empreinte SHA-256 ne correspond pas.
- `chargerModele(pipeline, entete, { suivre, env, dossierModeles })` : charge le modèle de l'en-tête avec sa précision (q8). Si l'en-tête porte `"emplacement": "site"`, le modèle est lu dans `dossierModeles`, déclaré à Transformers.js comme hôte distant (`env.remoteHost`), sans jamais interroger le Hub ; sinon, il vient du Hub, à la révision de l'en-tête. `suivre` reçoit la progression du téléchargement.
- `classer(matrice, N, D, q, k)` : produit scalaire avec les 4 240 passages et les k meilleurs ; à score égal, l'ordre de l'index.
- `creerMoteur(pipeline, base)` : les trois ensemble ; `rechercher(question, k)` renvoie les k meilleurs passages avec leur rang, leur score, leur fiche, leur section et leur lien profond (`url_citation`) ; `seuilAbstention` et `borneZoneGrise` donnent le seuil et la borne applicables à l'en-tête, ou `null`.
- `referenceAbstention(entete)` : la référence de `ABSTENTIONS` qui vaut pour ce modèle, cette précision et cet index, ou `null`.
- `horsPerimetre(resultats, seuil)` : vrai si le meilleur passage reste strictement sous le seuil.
- `zoneGrise(resultats, seuil, borne)` : vrai si le meilleur passage est au-dessus du seuil, mais strictement sous la borne (A3, #164) ; toujours faux sans borne.
- `regrouperParFiche(resultats)` : les passages regroupés par fiche (A2, #164), dans l'ordre du meilleur passage de chaque fiche ; aucun passage n'est retiré ni réordonné entre fiches.
- Le hook `useMoteur` renvoie les deux drapeaux avec chaque recherche (`{ resultats, duree, horsPerimetre, zoneGrise }`).

## Abstention

Deux références, dans `ABSTENTIONS` : celle de l'encodeur de base (`ABSTENTION`), servi jusqu'au 15 novembre 2026, et celle de l'encodeur ajusté (`ABSTENTION_AJUSTE`), servi depuis (#164). Le moteur applique celle dont le modèle, la précision et l'index sont ceux de l'en-tête chargé.

### Encodeur de base

- **Le seuil.** `ABSTENTION.seuil` vaut 0,8559679388999939. Il a été fixé le 10 octobre 2026, avant la mesure, comme le 5e centile des scores maximaux de 479 variantes du CDTN rédigées en question (protocole du notebook 03, section 8.2).
- **Ce qu'il vaut.** Sur le lot de test, il garde 72 des 73 questions du corpus et rejette 9 des 24 questions hors corpus. Il signale donc surtout les saisies sans rapport avec le droit du travail, et non les questions juridiques absentes de nos fiches.
- **Pour quel modèle.** Il ne vaut que pour les vecteurs avec lesquels il a été calculé : le modèle est reconnu à l'empreinte de son fichier ONNX (le q8 de Xenova, `f80102d3…`, ou sa version élaguée sans perte, `4499d46b…`, qui donne les mêmes vecteurs), et l'index à la sienne (`2ec45586…`). Pour un modèle ou un index sans référence, `seuilAbstention` vaut `null` et aucune question n'est signalée : le seuil doit alors être recalculé par `scripts/evaluation/cdtn_seuil.py`.

### Encodeur ajusté (#164)

- **Le seuil.** `ABSTENTION_AJUSTE.seuil` vaut 0,7682965993881226 : même règle, recalculée avec les 479 variantes du CDTN encodées dans le navigateur par l'ajusté (`cdtn_seuil.py calculer_ajuste`) ; intervalle à 95 % de 0,7472 à 0,7827.
- **La zone grise.** `ABSTENTION_AJUSTE.zoneGrise` vaut 0,8140405416488647, le 25e centile de la même population (`cdtn_seuil.py zone_grise_ajuste`) : 96 des 479 variantes, toutes légitimes, y tombent. Entre le seuil et cette borne, le site affiche un avertissement et tous les passages.
- **Ce qu'ils valent.** Sur le lot de test, 70 des 73 questions du corpus sont conservées, dont 23 en zone grise ; 10 des 24 questions hors corpus sont rejetées et 13 autres reçoivent l'avertissement (`docs/etudes/evaluation/05_resultats_ajustement.md`).
- **Pour quel modèle.** Le q8 ajusté complet (`934a202b…`) ou sa version élaguée (`13ed78c9…`), avec l'index `front/public/index_ajuste/` (`dc8daa72…`). Un croisement, modèle ajusté avec l'index de base ou l'inverse, n'a pas de référence : aucun seuil.

### À l'affichage

Ne pas masquer les passages sans recours : un message signale la question, et le visiteur peut afficher quand même les passages les plus proches (#53). En zone grise, les passages restent affichés.

## Intégration dans le site

1. Ajouter Transformers.js à la version figée du site : `npm install @huggingface/transformers@4.3.0 --save-exact`, dans `front/`.
2. Les trois fichiers de l'index sont versionnés dans `front/public/index_ajuste/`, lu par le site depuis le 15 novembre 2026, et dans `front/public/index/`, celui de l'encodeur de base, que lit la chaîne du volet B (option A, validée le 11 octobre 2026). Ne pas les régénérer : voir le fichier `SOURCES.md` de chaque dossier.
3. Le modèle, élagué sans perte (65,7 Mio au lieu de 112,8 ; #50), est versionné dans `front/public/modele/`, dans un dossier nommé d'après son empreinte : voir `front/public/modele/SOURCES.md`.
4. Dans le composant :

```
import { pipeline, env } from "@huggingface/transformers";
import { creerMoteur } from "./recherche/moteur.js";

const moteur = await creerMoteur(pipeline, import.meta.env.BASE_URL + "index_ajuste/", {
  env, dossierModeles: import.meta.env.BASE_URL + "modele/",
  suivre: (p) => { /* afficher p.status et p.progress pendant le premier chargement */ },
});
const resultats = await moteur.rechercher(question, 10);
```

`import.meta.env.BASE_URL` vaut `/data_tigers_nlp/` une fois en ligne : sans lui, les fichiers seraient cherchés à la racine du domaine.

## Contrôles

- Tests sans dépendance : `node --test front/src/recherche/moteur.test.js`. Les tests sur les vrais fichiers lisent `data/indexation/` ; ils sont sautés si l'export est absent (variable facultative `RACINE_DONNEES` pour pointer vers un clone qui l'a).
- Abstention : le classement du site redonne le seuil et ses 24 rejets sur les 479 variantes du CDTN (test sauté sans `data/evaluation/cdtn/`). Le 13 octobre 2026, sur les 97 questions du lot de test, le moteur prend les mêmes décisions que le notebook 03, avec un écart de score d'au plus 6e-8 et aucune question à moins de 6,9e-4 du seuil.
- Modèle élagué : `scripts/allegement/verifier_elagage.py` (découpage et sorties, en Python) et `scripts/allegement/controle_navigateur.html` (822 vecteurs identiques bit à bit dans le navigateur, le 14 octobre 2026).
- Encodeur ajusté (#164) : le site construit, servi sur 127.0.0.1 et piloté dans Chrome 155, affiche pour les 97 questions du lot de test les mêmes 10 passages, scores, fiches et états que le calcul Python de `scripts/evaluation/mesures_site_164.py` (15 novembre 2026). Le test « abstention ajustée » de `moteur.test.js` redonne le seuil, la borne, 24 rejets et 96 questions en zone grise sur le CDTN (sauté sans `data/adaptation/navigateur/vecteurs/`).
- Parité complète dans le navigateur : `scripts/indexation/parite_moteur.html` ; avec `?site`, sur l'index et le modèle versionnés du site. Le 14 octobre 2026, dans les deux cas, mêmes 5 premiers passages et mêmes scores sur les 24 requêtes, sans aucune requête vers le Hub avec `?site`. Le 10 octobre 2026, les 24 requêtes du contrôle donnent les mêmes 5 premiers passages et les mêmes scores que la page de contrôle du notebook 02, à l'écart nul, en 19,7 ms par question en médiane, encodage compris.
