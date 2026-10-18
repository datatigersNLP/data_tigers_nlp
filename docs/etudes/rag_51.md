# Chaîne RAG du volet B — issue #51

Responsables : Jibril BENSALEM et Maïmouna SIGNATE. Soutien : Remy RAYANE et Mahé BEGNIS.

## État au 18 octobre 2026

Les étapes 1 (chargement de l'index) et 2 (récupération Python fp32) sont implémentées.
Le contrôle de l'index réel a réussi sur le Legion, d'après la sortie transmise par Jibril le 18 octobre.
L'étape 2 reste à exécuter avec le vrai encodeur E5 sur cette machine. Aucun appel à Ollama n'est implémenté.
La chaîne RAG complète reste à construire ; ces étapes ne valident pas les critères de clôture de #51.

L'estimation de 16 h cumulées est inscrite dans le ticket et le classeur avant le développement.
La charge réelle n'est pas renseignée avant la clôture.

## 1. Ce que fait le chargeur

`scripts/rag/rag.py` lit directement `front/public/index/` : aucune copie d'index n'est ajoutée au dépôt.

| Entrée | Contrôle |
|---|---|
| `index_m2.json` | Format `index-e5-v1`, M2, matrice PyTorch fp32 de référence, 384 dimensions, paramètres E5 attendus |
| `index_m2.f32` | Empreinte du manifeste, taille N × 384 × 4, float32 petit-boutiste, valeurs finies, normes à moins de 1e-5 de 1 |
| `passages_m2.json` | Empreinte du manifeste, N objets, identifiants uniques et non vides, textes non vides, types des neuf champs attendus |

La sortie Python est un `IndexCommun` : manifeste, matrice NumPy en lecture seule et liste des passages.
La ligne i de la matrice est associée à l'objet i de la liste, sans tri, réécriture ou normalisation des textes.
Comme des pages numérotées et leur catalogue, les deux fichiers doivent venir du même export.
Les empreintes empêchent de mélanger des fichiers différents de ceux décrits par le manifeste ; elles ne prouvent
ni une pertinence sémantique ni l'authenticité d'un manifeste remplacé avec tous ses fichiers. Le manifeste de référence
est celui versionné dans le dépôt.

Le bloc `modele` du manifeste décrit le q8 élagué servi par le navigateur. Il n'est pas utilisé pour charger un
modèle Python. La référence prévue pour l'étape 2 reste `intfloat/multilingual-e5-small`, fp32, révision
`614241f622f53c4eeff9890bdc4f31cfecc418b3`, avec `query: `, moyenne des tokens et normalisation L2.
Le seuil d'abstention q8 du site n'est pas transféré à cette configuration fp32.

## 2. Exécuter cette étape sous Windows

Depuis la racine du dépôt, après avoir récupéré la branche `feat/51-rag-index-commun`, avec l'environnement
Python 3.12 du notebook 02 déjà installé :

```powershell
.\.venv\Scripts\python.exe .\scripts\rag\rag.py --check-index
```

Le dossier est résolu depuis le fichier du script, indépendamment du dossier courant. Un autre dossier d'export
peut être fourni avec `--index-dir CHEMIN`.

Si l'environnement n'existe pas, les dépendances sont déjà figées par l'indexation (NumPy suffit pour cette étape) :

```powershell
uv venv --seed --python 3.12 .venv
uv pip sync --python .venv\Scripts\python.exe scripts/indexation/requirements-lock.txt
```

Synchroniser uniquement l'environnement dédié au projet : `uv pip sync` remplace ses paquets selon ce fichier.
Ne pas réinstaller un environnement déjà utilisé par un autre travail sans vérifier ses dépendances.

Résultat constaté dans la sortie transmise par Jibril le 18 octobre : résumé JSON avec :

- `statut` : `index_verifie` ;
- `nb_passages` : 4240 ; `dimension` : 384 ;
- `sha256_index` : `2ec45586ab9aaa578f11e271d0ff077c87c105c5de50dcd839e5e9258475b886` ;
- `sha256_passages` : `aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d` ;
- `e5_charge` et `ollama_appele` : `false`.

Un fichier absent ou incohérent produit « Index refusé », un détail et un code de sortie 1. Ne pas contourner
l'erreur en recalculant les empreintes du manifeste : récupérer les fichiers versionnés de la même révision.

## 3. Contrôles exécutés dans l'environnement de développement

Commande des tests sans modèle :

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s scripts/rag -p "test_*.py" -v
```

Exécutée ici le 18 octobre 2026 avec Python 3.12.14 et NumPy 2.3.5 : **15 tests réussis**, sous-cas inclus.
Le fichier figé du notebook utilise NumPy 2.5.3 : ces tests ne prouvent pas encore l'exécution dans cet environnement
exact ni sur Windows. Aucune dépendance existante n'a été modifiée.

Les tests utilisent des exports artificiels de deux vecteurs de 384 dimensions et deux documents techniques.
Ils couvrent le parcours valide, la conservation de l'ordre et du texte, la lecture seule, les fichiers manquants,
la corruption d'un octet, le réordonnancement des métadonnées, une taille binaire incohérente même après changement
de son empreinte, NaN/Inf, normes invalides, identifiants dupliqués, textes vides, schéma et manifeste incompatibles,
JSON/UTF-8 invalide, chemins hors du dossier et codes de sortie de la commande depuis un autre dossier.
Ils ne créent aucune question d'évaluation.

Contrôle distinct sur les **métadonnées réelles** du commit de départ `2d2658b` : fichier de 6 428 126 octets,
SHA-256 conforme au manifeste, 4 240 identifiants uniques, aucun texte vide et types des neuf champs conformes.

Limite d'accès : le connecteur GitHub ne restitue pas correctement le fichier binaire `.f32` dans cet environnement.
La lecture et les normes de la **matrice réelle** n'ont donc pas été contrôlées ici par l'assistant. Jibril a exécuté
`--check-index` sur sa copie complète et transmis la sortie réussie le 18 octobre : Python 3.12.15, NumPy 2.5.3,
uv 0.13.1, Windows/Legion. Le résumé affiche `index_verifie`, 4 240 passages, dimension 384 et les deux empreintes
attendues. Aucune sortie des tests unitaires Windows n'a été transmise ; on ne les déclare pas exécutés là-bas.

| Niveau | État |
|---|---|
| Tests Python sur exports artificiels | 15 réussis |
| Métadonnées réelles | Empreinte et schéma contrôlés |
| Matrice réelle, sur le Legion | Contrôle réussi, sortie transmise par Jibril |
| Encodage E5 et récupération | Implémentés, exécution réelle à faire |
| Appel réel à Ollama | Aucun |
| RAG complet | Non validé |

## 4. Étape 2 : récupérer cinq passages avec E5

Le mode `--retrieve-only` commence par lire une question humaine du lot de calibration au commit
`cdb48c97064de625df61703a9a41e106160e0f50` (tag `jeu-questions-v1`), avec `git show`.
Il ne lit pas une version de travail du CSV ; il n'utilise pas l'URL ni l'extrait annotés pour rechercher.
Le lot de test est refusé avant tout téléchargement du modèle. Le type annoté est conservé comme information
de provenance uniquement ; il ne modifie pas la récupération.

L'encodeur est chargé sur CPU, à la révision du notebook 02, puis explicitement converti en fp32 et placé en
mode évaluation. Sa révision fournit le pooling moyen de Sentence Transformers. L'entrée est le texte exact
précédé de `query: ` ; au-delà de 512 tokens E5, l'exécution est refusée au lieu de tronquer silencieusement.
`encode()` reprend les options du notebook : taille de lot 32 (une seule question ici), normalisation L2,
sortie NumPy fp32. Le produit scalaire avec la matrice existante et un tri stable donnent les cinq premiers passages.
À égalité, l'ordre des lignes de l'index est conservé. Aucun seuil d'abstention n'est appliqué à cette étape.

Depuis la racine, après `git pull --ff-only` sur la branche #51 :

```powershell
uv pip install --python .venv\Scripts\python.exe -r scripts/rag/requirements.txt
.\.venv\Scripts\python.exe .\scripts\rag\rag.py --retrieve-only --question-id Q036
```

Le fichier `requirements.txt` de #51 ne demande directement que NumPy et Sentence Transformers ; les dépendances
indirectes restent contraintes par le fichier figé du notebook 02. Il ne change aucun verrou existant.
Le premier chargement peut télécharger environ 470 Mio de poids E5 dans le cache Hugging Face, hors du dépôt.
Les paquets PyTorch et associés peuvent aussi être volumineux. Une connexion est nécessaire si le modèle n'est pas
déjà en cache. Le GPU est laissé disponible pour Qwen lors d'une étape ultérieure.

Q036 est utilisée mot pour mot : « Quelles sont les obligations légales de l'empoyeur en période de forte chaleur ? ».
Le JSON doit afficher `recuperation_effectuee`, `top_k: 5`, `e5_charge: true`, `ollama_appele: false`, la question et
son commit source, les versions et les cinq résultats. Chaque résultat contient rang, indice, score et toutes les
métadonnées du passage, dont son texte original. Le score de similarité n'est ni une probabilité ni une preuve que
le texte suffit pour répondre. Aucun résultat, classement ou temps réel pour Q036 n'est encore rapporté.

Contrôles exécutés ici après cette extension : **27 tests réussis** avec Python 3.12.14 et NumPy 2.3.5.
Ils couvrent notamment le préfixe et la conservation de la question humaine, la limite sans troncature, les
dimensions et normes, les égalités de score, la correspondance des passages, le refus du lot de test et le parcours
de la commande. Le chargement E5 et sa sortie sont simulés dans ces tests : ils ne prouvent ni la disponibilité
des poids, ni le vrai encodage, ni la qualité de récupération. L'exécution locale ci-dessus reste nécessaire.

## 5. Suite prévue après la récupération

1. Contrôler la récupération réelle sur le Legion.
2. Construire le contexte numéroté et conserver la correspondance `[P1]` → `passage_id` → source.
3. Finaliser le prompt et le budget de contexte, puis appeler le Qwen local validé dans #31.
4. Distinguer réponse citée, abstention du modèle, sortie invalide et erreur technique.
5. Documenter des sorties réellement obtenues, dont une abstention, sans modifier les questions.

Pour les premiers essais, les questions Q036 (`dans_corpus`) et Q003 (`hors_corpus`) du lot de **calibration** au tag
`jeu-questions-v1` ont été proposées avant exécution dans la conception. Leur texte restera inchangé.
Le lot de test, les métriques, la calibration et les décisions de #52 ne sont pas modifiés.

Une référence qui existe parmi les passages fournis est structurellement valide ; cela ne prouve pas que le passage
justifie la phrase. Cette distinction devra rester explicite dans les résultats.
