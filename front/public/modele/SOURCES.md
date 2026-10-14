# Modèle servi par le site : sources, licence et élagage

## Contenu

Dossier `multilingual-e5-small-q8-elague-4499d46b/`, dont le nom porte les 8 premiers caractères de l'empreinte du fichier ONNX : chaque version a son propre chemin, et aucun navigateur ne peut servir une ancienne version depuis son cache.

| Fichier | Rôle | Taille | SHA-256 |
|---|---|---:|---|
| `LICENSE` | licence MIT de multilingual-e5-small | 1 083 octets | `b5cb7ff7859e7d282d98fc43ab081b0dda5dc659dc3385cf65740c759a7e6a6c` |
| `config.json` | configuration (taille du vocabulaire mise à jour) | 658 octets | `0cb92497dc627619529923b5ee0e6a845fded65d80cf62df3231e349c504625d` |
| `onnx/model_quantized.onnx` | modèle q8, table des mots élaguée | 68 862 041 octets | `4499d46b6ffc94746da7e91782977ec49699a035ffd4fba5d33393f86e4480d9` |
| `special_tokens_map.json` | jetons spéciaux, inchangés | 167 octets | `d05497f1da52c5e09554c0cd874037a083e1dc1b9cfd48034d1c717f1afc07a7` |
| `tokenizer.json` | tokeniseur élagué et renuméroté | 4 335 981 octets | `b4f51d4228181f14ef705d2afec4d2fda41096e67ba0df359cb83ee20ebdc2c6` |
| `tokenizer_config.json` | configuration du tokeniseur, inchangée | 443 octets | `a1d6bc8734a6f635dc158508bef000f8e2e5a759c7d92f984b2c86e5ff53425b` |

`manifeste.json` décrit la source, la règle et chaque fichier.

## Source

- **Modèle** : `intfloat/multilingual-e5-small`, licence MIT (Microsoft), dans sa conversion ONNX q8 `Xenova/multilingual-e5-small`, révision `761b726d`, fichier `onnx/model_quantized.onnx` d'empreinte `f80102d3…`. C'est le modèle que mesure le notebook 03 sous le nom « E5 servi ».
- **Licence** : MIT ; son texte est joint dans `LICENSE`, comme elle l'exige.

## Transformation : élagage sans perte du vocabulaire (#50)

- **Règle** : une pièce est gardée si chacune de ses lettres appartient à l'alphabet latin ou grec ; chiffres, ponctuation, symboles, espaces et diacritiques combinants sont toujours gardés, comme les jetons spéciaux.
- **Effet** : 121 271 pièces gardées sur 250 002 ; le q8 passe de 118 308 185 à 68 862 041 octets, sous la limite de 100 Mio par fichier de GitHub, et le tokeniseur de 17 082 730 à 4 335 981 octets.
- **Pourquoi c'est sans perte** : une pièce retirée contient une lettre absente de tout texte écrit avec les caractères gardés, et ne peut donc jamais en recouvrir un morceau. Le découpage en jetons, et donc les vecteurs, sont inchangés pour ces textes. Un texte en cyrillique, en chinois ou en arabe reçoit un jeton inconnu à la place des lettres retirées.
- **Script** : `scripts/allegement/elaguer_vocabulaire.py`, déterministe : deux exécutions donnent des fichiers identiques octet par octet.

## Vérifications, le 14 octobre 2026

- **Découpage** (`scripts/allegement/verifier_elagage.py`) : identique pour les 822 requêtes de contrôle du notebook 02, les 113 textes de la mesure du notebook 03, les 5 433 titres et variantes du CDTN et les 4 240 passages M2.
- **Sorties du q8 en Python** : identiques bit à bit sur 935 requêtes.
- **Navigateur** (`scripts/allegement/controle_navigateur.html`, Chromium, Transformers.js 4.3.0) : les 822 vecteurs de contrôle sont identiques bit à bit à ceux du q8 de Xenova mesurés au notebook 02, en 18,3 ms par requête.
- **Moteur du site** (`scripts/indexation/parite_moteur.html?site`) : mêmes 5 premiers passages et mêmes scores sur les 24 requêtes du contrôle, sans aucune requête vers le Hub.

## Règles

- **Ne pas modifier ces fichiers à la main.** Pour un autre modèle, l'encodeur ajusté (#49) par exemple : l'élaguer par le script, vérifier son identité avec sa version complète dans le navigateur, puis changer l'en-tête de l'index.
- **Le seuil d'abstention** du moteur (`front/src/recherche/moteur.js`, `ABSTENTION`) reconnaît ce modèle à l'empreinte de son fichier ONNX ; pour un autre modèle, il doit être recalculé.
