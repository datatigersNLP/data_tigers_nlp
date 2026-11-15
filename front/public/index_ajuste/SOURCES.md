# Index de recherche de l'encodeur ajusté : sources et licence

Index lu par le site depuis le 15 novembre 2026 (#164). Celui de l'encodeur de base, `front/public/index/`, reste inchangé : la chaîne du volet B le lit.

## Contenu

| Fichier | Rôle | Taille | SHA-256 |
|---|---|---:|---|
| `index_m2.json` | en-tête : modèle ajusté servi par le site, précision, options de la requête, empreintes des deux autres fichiers | 1 514 octets | `d438f0254cdec9664136bf84a8109acf9bd34fdca772e891b147c8c19f939a8f` |
| `index_m2.f32` | 4 240 vecteurs de 384 dimensions, en float32 petit-boutiste | 6 512 640 octets | `dc8daa7243bec30c28ea4830daeb10970bcd3de8d819f71a602b5d0b306ea8f1` |
| `passages_m2.json` | les 4 240 passages, dans l'ordre des lignes de la matrice ; copie octet pour octet de `front/public/index/passages_m2.json` | 6 428 126 octets | `aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d` |

## Sources

- **Passages** : les mêmes que ceux de l'index de base ; producteur, extractions, instantané du 11 septembre 2026 et Licence Ouverte Etalab 2.0 : voir `front/public/index/SOURCES.md`.
- **Modèle** : l'encodeur `multilingual-e5-small` ajusté sur nos passages (#49, PR #63), licence MIT ; le site encode les questions avec sa version q8 élaguée sans perte, servie par le site lui-même : voir `front/public/modele/SOURCES.md`.

## Transformations

- **Vecteurs des passages** : réencodés en fp32 par l'encodeur ajusté, avec le tokeniseur de l'encodeur de base, comme l'index du site (configuration A du notebook 02 : index en fp32, requête en q8), par `scripts/evaluation/ajustement_05.py index`. Cosinus minimal de 0,99999982 avec l'index livré par Remy (`passage_embeddings_apres.npy`).
- **Dossier du site** : écrit par `scripts/evaluation/ajustement_05.py site`, qui copie la matrice et les passages, puis écrit l'en-tête avec leurs empreintes.

## Règles

- **Ne pas régénérer ces fichiers à la main** : c'est cet index que décrivent la mesure du protocole 05 et les contrôles du 15 novembre 2026 (`docs/etudes/evaluation/05_resultats_ajustement.md`).
- **Seuil d'abstention** : celui du moteur (`front/src/recherche/moteur.js`, `ABSTENTION_AJUSTE`) reconnaît cet index à l'empreinte de sa matrice ; un autre index n'aurait aucun seuil tant qu'il n'a pas été recalculé.
