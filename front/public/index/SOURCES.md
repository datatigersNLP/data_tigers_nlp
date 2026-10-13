# Index de recherche du volet A : sources et licence

## Contenu

| Fichier | Rôle | Taille | SHA-256 |
|---|---|---:|---|
| `index_m2.json` | en-tête : modèle, révision, précision, options de la requête, empreintes des deux autres fichiers | 1 082 octets | `4a0d1462b8cb525a29f7941545bef0d9718bd51a866f0584b78b82fb3b3fe0a9` |
| `index_m2.f32` | 4 240 vecteurs de 384 dimensions, en float32 petit-boutiste | 6 512 640 octets | `2ec45586ab9aaa578f11e271d0ff077c87c105c5de50dcd839e5e9258475b886` |
| `passages_m2.json` | les 4 240 passages, dans l'ordre des lignes de la matrice | 6 428 126 octets | `aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d` |

## Sources

- **Producteur** : ministère chargé du Travail, fiches pratiques du site travail-emploi.gouv.fr. La date de mise à jour de chaque fiche figure dans le champ `date_maj` de ses passages.
- **Extractions utilisées** : `SocialGouv/fiches-travail-data`, commit `fbf639f` (11 septembre 2026), et `AgentPublic/travail-emploi` sur Hugging Face, commit `98744a6`, instantané du 11 septembre 2026.
- **Licence** : Licence Ouverte Etalab 2.0, celle du jeu `AgentPublic/travail-emploi`. Elle autorise la réutilisation et la rediffusion, en citant la source et la date de mise à jour.
- **Modèle** : `intfloat/multilingual-e5-small`, licence MIT, révision `614241f6` pour les passages ; le site encode les questions avec sa conversion `Xenova/multilingual-e5-small`, révision `761b726d`, en q8.

## Transformations

- Découpage structurel M2 : un passage ne mélange jamais deux sections, et les blocs d'une section sont regroupés dans la limite de 512 tokens, en-tête « fiche > section > intertitres » compris (notebook 01, `scripts/decoupage/01_corpus_decoupage.ipynb`).
- Vectorisation des passages, avec l'en-tête de la fiche (notebook 02, `scripts/indexation/02_indexation.ipynb`), produite le 30 septembre 2026.

## Règles

- **Ne pas régénérer ces fichiers à la main.** C'est cet index, d'empreinte `2ec45586`, que mesure le notebook 03 sous le nom « E5 servi » : un index reconstruit sur une autre machine peut différer (relecture de la PR #39), et le site ne servirait plus le système mesuré.
- **Remplacer seulement par une version validée**, par exemple celle de l'encodeur ajusté (#49) ou du modèle allégé (#50), avec un nouvel en-tête et ses empreintes.
