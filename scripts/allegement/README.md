# Allègement du modèle servi (#50)

Le q8 de `multilingual-e5-small` pèse 112,8 Mio, au-delà de la limite de 100 Mio par fichier de GitHub : il ne pouvait être servi que depuis le Hub de Hugging Face. 81 % de son poids est la table des mots, qui couvre une centaine de langues. Ce dossier en retire, sans perte pour le français, les pièces des autres alphabets, pour que le site serve lui-même un modèle de 65,7 Mio.

## Fichiers

| Fichier | Rôle |
|---|---|
| `elaguer_vocabulaire.py` | élague le tokeniseur et la table des mots, et écrit le modèle dans `front/public/modele/<nom>-<empreinte>/` avec son manifeste et sa licence |
| `verifier_elagage.py` | vérifie en Python que le découpage de nos textes et les sorties du modèle sont inchangés |
| `controle_navigateur.html` | vérifie dans le navigateur, comme sur le site, que les 822 vecteurs de contrôle du notebook 02 sont identiques bit à bit |
| `requirements.txt`, `requirements-lock.txt` | environnement figé, aligné sur celui de l'indexation |

## Le principe

- **Ce qui est retiré.** Les pièces du tokeniseur qui contiennent une lettre d'un autre alphabet que le latin ou le grec : cyrillique, chinois, arabe, etc. Les chiffres, la ponctuation, les symboles, les diacritiques combinants et les jetons spéciaux sont toujours gardés.
- **Ce qui est recopié.** Les lignes gardées de la table des mots, telles quelles, sans requantification : même échelle, même zéro.
- **Pourquoi c'est sans perte.** Le tokeniseur Unigram découpe un texte en choisissant, parmi les pièces qui en recouvrent des morceaux, le découpage le plus probable. Une pièce retirée contient une lettre absente de tout texte écrit avec les caractères gardés : elle ne peut jamais en recouvrir un morceau. Le découpage est donc le même, les jetons désignent les mêmes lignes, et les vecteurs sont identiques bit à bit.
- **La seule perte.** Un texte en cyrillique, en chinois ou en arabe reçoit un jeton inconnu à la place des lettres retirées.

## Procédure

Depuis la racine du dépôt :

```
uv venv --seed --python 3.12 .venv-allegement
uv pip sync --python .venv-allegement/bin/python scripts/allegement/requirements-lock.txt
.venv-allegement/bin/python scripts/allegement/elaguer_vocabulaire.py
.venv-allegement/bin/python scripts/allegement/verifier_elagage.py front/public/modele/<dossier écrit>
```

Puis servir le dépôt avec `python3 -m http.server 8765 --bind 127.0.0.1` et ouvrir `http://127.0.0.1:8765/scripts/allegement/controle_navigateur.html`, qui doit afficher « ÉLAGAGE SANS PERTE DANS LE NAVIGATEUR ». Les vérifications lisent les textes de `data/`, qui n'est pas versionné.

## Résultats sur le modèle servi, le 14 octobre 2026

| Contrôle | Résultat |
|---|---|
| Pièces gardées | 121 271 sur 250 002 |
| Modèle q8 | 118 308 185 octets, ramenés à 68 862 041 (65,7 Mio, -42 %) |
| Tokeniseur | 17 082 730 octets, ramenés à 4 335 981 (-75 %) |
| Deux exécutions du script | fichiers identiques octet par octet |
| Découpage | identique pour 822 requêtes de contrôle, 113 textes de la mesure, 5 433 textes du CDTN et 4 240 passages |
| Sorties du q8, en Python | 935 sur 935 identiques bit à bit |
| Vecteurs dans le navigateur | 822 sur 822 identiques bit à bit au q8 de Xenova, 18,3 ms par requête |
| Contrôle négatif | une seule ligne altérée de la table fait échouer les 935 sorties |

## Pour l'encodeur ajusté (#49)

Retenu par la mesure du protocole 05 et servi depuis le 15 novembre 2026 (#164) :

| Étape | Commande | Résultat |
|---|---|---|
| Élagage | `elaguer_vocabulaire.py --dossier data/adaptation/navigateur/ajuste --nom multilingual-e5-small-ajuste-q8-elague` | 118 371 400 octets ramenés à 68 925 256 ; deux exécutions identiques octet par octet |
| Contrôle en Python | `verifier_elagage.py <dossier élagué> --source data/adaptation/navigateur/ajuste` | découpage identique pour 822, 113, 5 433 et 4 240 textes ; 935 sorties sur 935 identiques bit à bit |
| Référence du navigateur | `scripts/evaluation/encoder_navigateur.py --modele ajuste --lot controle` | 822 vecteurs du q8 ajusté complet, dans `data/adaptation/navigateur/vecteurs/vecteurs_controle_ajuste.json` |
| Contrôle dans le navigateur | `scripts/evaluation/encoder_navigateur.py --page controle --index index_ajuste --reference ajuste` | 822 vecteurs sur 822 identiques bit à bit, 19,7 ms par requête |

Avec `?index=index_ajuste&reference=ajuste`, `controle_navigateur.html` lit le modèle désigné par l'en-tête de `front/public/index_ajuste/` et compare ses vecteurs à cette référence, après avoir vérifié que la référence vient du q8 d'origine de l'en-tête et porte sur les mêmes requêtes ; sans paramètre, la page compare toujours le modèle de base au q8 de Xenova. Le seuil d'abstention a été recalculé par `scripts/evaluation/cdtn_seuil.py calculer_ajuste`. Détail : `docs/etudes/evaluation/05_resultats_ajustement.md`.
