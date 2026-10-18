# Chaîne RAG du volet B — issue #51

Responsables : Jibril BENSALEM et Maïmouna SIGNATE. Soutien : Remy RAYANE et Mahé BEGNIS.

## État au 18 octobre 2026

Seule l'étape 1 est implémentée : le chargement contrôlé de l'index commun.
Le script ne charge aucun encodeur, ne récupère aucun top 5 et n'appelle pas Ollama.
La chaîne RAG complète reste à construire ; cette étape ne valide pas les critères de clôture de #51.

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

Résultat attendu, **pas encore constaté sur le Legion** : code de sortie 0 et résumé JSON avec :

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
La lecture et les normes de la **matrice réelle** n'ont donc pas été contrôlées ici. La commande `--check-index`
sur la copie Git complète de Jibril ou Maïmouna est le contrôle restant avant l'étape 2.

| Niveau | État |
|---|---|
| Tests Python sur exports artificiels | 15 réussis |
| Métadonnées réelles | Empreinte et schéma contrôlés |
| Matrice réelle, sur le Legion | À exécuter |
| Encodage E5 et récupération | Pas encore implémentés |
| Appel réel à Ollama | Aucun |
| RAG complet | Non validé |

## 4. Suite prévue, hors de cette première étape

1. Charger E5 Python fp32 et retourner cinq passages, sans génération.
2. Construire le contexte numéroté et conserver la correspondance `[P1]` → `passage_id` → source.
3. Finaliser le prompt et le budget de contexte, puis appeler le Qwen local validé dans #31.
4. Distinguer réponse citée, abstention du modèle, sortie invalide et erreur technique.
5. Documenter des sorties réellement obtenues, dont une abstention, sans modifier les questions.

Pour les premiers essais, les questions Q036 (`dans_corpus`) et Q003 (`hors_corpus`) du lot de **calibration** au tag
`jeu-questions-v1` ont été proposées avant exécution dans la conception. Leur texte restera inchangé.
Le lot de test, les métriques, la calibration et les décisions de #52 ne sont pas modifiés.

Une référence qui existe parmi les passages fournis est structurellement valide ; cela ne prouve pas que le passage
justifie la phrase. Cette distinction devra rester explicite dans les résultats.
