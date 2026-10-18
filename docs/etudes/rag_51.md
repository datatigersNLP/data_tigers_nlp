# Chaîne RAG du volet B — issue #51

Responsables : Jibril BENSALEM et Maïmouna SIGNATE. Soutien : Remy RAYANE et Mahé BEGNIS.

## État au 18 octobre 2026

Les étapes 1 (chargement de l'index), 2 (récupération Python fp32) et 3 (contexte numéroté) sont implémentées.
Le contrôle de l'index réel a réussi sur le Legion, d'après la sortie transmise par Jibril le 18 octobre.
L'étape 2 a également réussi sur Q036, selon la trace transmise par Jibril. Le contexte a été construit ici depuis
ses cinq résultats réels, sans réexécuter E5. Le client Ollama et le contrôle structurel des citations sont implémentés
dans `scripts/rag/generation.py`. Jibril a ensuite transmis une première exécution complète sur Q036 : réponse citée,
références existantes et comptes de tokens concordants. La lecture des passages révèle toutefois des conditions
d'application omises et des citations regroupées en introduction. Une seconde trace sur Q003 confirme une
abstention réelle avec la même configuration. La relecture du binôme, les tests Windows et la présentation à
l'équipe restent à confirmer ; la validation globale de #51 reste ouverte.

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
| Encodage E5 et récupération | Réussis pour Q036, trace transmise par Jibril |
| Appel réel à Ollama | Réussi pour Q036 et Q003 sur le Legion, traces transmises par Jibril |
| RAG complet | Q036 : réponse citée avec limites relevées ; Q003 : abstention ; validation globale en attente |

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
le texte suffit pour répondre.

### Résultat réel de Q036 transmis le 18 octobre

Source : fichier « Texte collé.txt » transmis par Jibril, SHA-256
`4694b24bb9deea5ab6c9f10920e21059c6e57ce2f9aa61522564dc8dbb808114`.
Ce résultat provient de son Legion ; l'assistant n'a pas exécuté E5 à distance.
Code exécuté : `a5d264a`. Versions rapportées : Python 3.12.15, NumPy 2.5.3,
Sentence Transformers 6.1.0, PyTorch 2.14.0, Transformers 5.17.0.
Le résumé confirme la révision E5 prévue, fp32 sur CPU, les empreintes de l'index et des passages,
`e5_charge: true` et `ollama_appele: false`.

| Rang | Passage | Indice | Score | Lecture qualitative des sources |
|---|---|---:|---:|---|
| 1 | `m2-article115181-0002` | 1085 | 0.8619567155838013 | Mesures de prévention et conditions d'application, fiche « Chaleur et canicule au travail » |
| 2 | `m2-article115181-0003` | 1086 | 0.8556755781173706 | Recommandations aux travailleurs ; ne pas les transformer en obligations de l'employeur |
| 3 | `m2-article374930-0019` | 2857 | 0.8504210114479065 | Obligations lors de l'embauche, moins directement liées à la question |
| 4 | `m2-article112732-0007` | 748 | 0.8481160998344421 | Suivi de santé du secteur du particulier employeur, moins directement lié à la question |
| 5 | `m2-article115181-0001` | 1084 | 0.8480237126350403 | Cadre de prévention du risque chaleur, même fiche que le premier passage |

Contrôle effectué ici sur la trace : chaque objet `passage` est identique à celui des métadonnées versionnées
à l'indice indiqué. Les passages 1 et 5 contiennent des éléments utiles pour une réponse conditionnelle.
Cette lecture qualitative de calibration n'est ni une mesure officielle D4 ni une validation juridique exhaustive.
Les scores proches de passages moins pertinents illustrent pourquoi ils ne doivent pas être lus comme des probabilités.
Les avertissements du Hub (accès sans jeton et cache Windows sans liens symboliques) n'ont pas empêché cette exécution.
La trace ne fournit pas de durée isolée d'encodage ou de recherche : aucun temps correspondant n'est inventé.

Contrôles exécutés ici après cette extension : **27 tests réussis** avec Python 3.12.14 et NumPy 2.3.5.
Ils couvrent notamment le préfixe et la conservation de la question humaine, la limite sans troncature, les
dimensions et normes, les égalités de score, la correspondance des passages, le refus du lot de test et le parcours
de la commande. Le chargement E5 et sa sortie sont simulés dans ces tests : ils ne prouvent ni la disponibilité
des poids, ni le vrai encodage, ni la qualité de récupération. L'exécution locale ci-dessus reste nécessaire.

## 5. Étape 3 : préparer la consigne et le contexte

`construire_contexte()` produit deux textes séparés : `system` (règles du RAG) et `prompt` (question inchangée,
puis cinq documents numérotés). Chaque document porte `[P1]` à `[P5]`, le titre de fiche, la section, les intertitres,
la date de mise à jour et le texte original intégral. Les textes ne sont ni résumés ni tronqués.
La table `sources`, séparée du prompt, associe chaque référence à son identifiant permanent et à ses URL.
Les vecteurs, scores et annotations attendues ne sont pas envoyés au générateur.

La consigne `rag-b1-v1`, dans `CONSIGNE_RAG`, reprend la proposition discutée : seules les sources fournies,
citations contrôlées, conditions et exceptions conservées, abstention explicite. Une précision sur la distinction entre
obligations et recommandations est motivée par le seul exemple de calibration Q036. Aucun réglage ne vient du lot de test.
La phrase d'abstention est : « Je ne peux pas répondre à cette question à partir des passages fournis. »
Les empreintes du système et du prompt sont consignées pour identifier exactement les textes utilisés ensuite.

```powershell
.\.venv\Scripts\python.exe .\scripts\rag\rag.py --prepare-context --question-id Q036
```

Ce mode refait la récupération puis affiche `contexte_prepare`, le contexte et sa table des sources.
Il ne contacte pas Ollama. La construction du contexte a été exécutée ici sur les cinq résultats réels transmis
par Jibril : 815 caractères pour le système, 7 769 pour le prompt ; les cinq textes y sont conservés intégralement.
Empreinte du système : `550e2a7bd98bee9d1ce681be3f32089077c6e9ed669573175525366d5d41b8fa`.
Empreinte du prompt de cet exemple : `99c15c28e74bee42811a2a790d64f67c97cd3f68207e7efd2522e06b42f7b3fa`.
Les nombres de caractères ne sont **pas** des nombres de tokens Qwen et ne valident pas le budget de contexte.

Après cette extension : **30 tests réussis** dans l'environnement de l'assistant, ainsi que le contrôle distinct
sur la trace réelle de récupération. Le vrai générateur n'a pas été appelé ; la vérification du gabarit Ollama et du
budget de tokens reste nécessaire avant le premier appel de génération.

## 6. Étapes 4 et 5 : Qwen local et contrôle des sorties

### Configuration locale observée

Jibril a interrogé `/api/show` et `/api/version` le 18 octobre et communiqué : Ollama **0.40.5**, modèle GGUF
de famille `qwen2`, 7.6B, quantification `Q4_K_M`, parent `qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf`.
Le gabarit est le Jinja Qwen avec rôles system/user/assistant et marqueurs `<|im_start|>` / `<|im_end|>`.
`parameters: null` ne signifie pas l'absence de réglages d'exécution : le script les fournit explicitement.
Cette version d'Ollama diffère de 0.34.4 dans #31 ; aucune performance de #31 n'est transposée au RAG.

Avant chaque génération, le client lit la version, le catalogue et les détails du modèle. Le nom local et le digest
de #31 (`6ec54444a8511aae6c2116b172eb3685d1416c523bfee0252ca33c7e55c481e4`) doivent correspondre, ainsi que la famille,
le format et la quantification. Un digest différent est signalé pour vérification, jamais remplacé automatiquement.

### Budget et appel

Le **tokeniseur seul** de `Qwen/Qwen2.5-7B-Instruct`, révision officielle figée
`a09a35458c702b33eeacc393d103063234e8bc28`, est chargé avec Transformers. Aucun second exemplaire des poids
génératifs n'est téléchargé. La révision a été relevée dans [l'API officielle du modèle](https://huggingface.co/api/models/Qwen/Qwen2.5-7B-Instruct).

Le gabarit retourné par Ollama est rendu par `apply_chat_template()` sur deux messages, system et user, avec
le début de réponse assistant. Pour cette baseline, le résultat doit être le format Qwen system/user attendu.
Ce texte est tokenisé avec `add_special_tokens=False` (les marqueurs sont déjà présents) et `truncation=False`.
Le comptage porte sur les tokens Qwen, et non ceux d'E5 ni les caractères.

| Paramètre de départ | Valeur |
|---|---|
| Passages | 5, textes intégraux |
| Température | 0.0 |
| Graine de génération | 20261018 |
| `num_ctx` | 8192 |
| `num_predict` | 512 |
| Marge de budget | 64 tokens |
| `stream` | false |
| `keep_alive` | 30m |
| Délai de génération | 300 s |
| Arrêts explicites | `<|im_end|>`, `<|endoftext|>`, `<|im_start|>` |

Ces valeurs sont une baseline documentée, pas un optimum démontré. La graine ne garantit pas une identité
des sorties entre versions ou matériels. Le contexte de 8192 donne de la place aux cinq passages ; son
exécution a réussi pour Q036 sur le Legion. La trace ne mesure pas l'utilisation du CPU, du GPU ou de la mémoire.

Si `tokens_entrée + 512 + 64 > 8192`, la génération est refusée sans supprimer de passage ni tronquer la question.
Le texte formaté est envoyé à `POST http://127.0.0.1:11434/api/generate` avec **`raw: true`** : Ollama n'ajoute pas
un second gabarit. C'est une différence explicite avec l'appel court de #31, nécessaire pour compter le texte exact
préparé. Voir [l'API officielle](https://github.com/ollama/ollama/blob/main/docs/api.md) et
[les gabarits Transformers](https://huggingface.co/docs/transformers/chat_templating).

Le compte HF n'est pas supposé équivalent au compte GGUF sans contrôle : après l'appel, `prompt_eval_count`
d'Ollama doit être égal au compte préparé. Un écart est une erreur technique, avec réponse brute conservée pour
diagnostic. Une interruption (`done_reason` autre que `stop`) ou un nombre de tokens de sortie incohérent est
également signalé. Aucune de ces situations n'est comptée comme une abstention du modèle.

### Contrôle structurel des citations

La réponse brute est conservée. Tout groupe entre crochets doit être une référence exacte parmi `[P1]` à `[P5]` ;
`[P1][P2]` est accepté, `[P8]`, `[P01]`, `[p1]`, `[P1, P2]` ou une référence non fermée sont refusés.
Le parseur est volontairement strict : les crochets ne sont pas réservés à d'autres usages dans ce format de sortie.

| Statut | Sens |
|---|---|
| `reponse_citee` | Au moins une citation existante et aucune référence mal formée détectée |
| `abstention_modele` | Phrase d'abstention exacte, à des espaces extérieurs près |
| `sortie_invalide` | Réponse vide, sans citation, avec référence invalide ou abstention mélangée à une autre sortie |
| `erreur_technique` | Génération interrompue, comptage incohérent ou métadonnées de sortie invalides |

Une autre formulation de refus est à examiner manuellement : elle n'est pas automatiquement assimilée à la phrase
contrôlée. `reponse_citee` ne prouve **ni la justification sémantique ni la couverture de chaque affirmation**.
Les deux indicateurs restent explicitement à false dans le rapport ; leur mesure relève de #52.

### Première exécution complète sur le Legion

Depuis la branche #51, Ollama lancé, récupérer le code puis les dépendances :

```powershell
git pull --ff-only
uv pip install --python .venv\Scripts\python.exe -r scripts/rag/requirements.txt
.\.venv\Scripts\python.exe .\scripts\rag\rag.py --generate --question-id Q036 --output .\data\rag\Q036_rag.json
```

Le JSON est écrit en UTF-8 dans `data/`, ignoré par Git, et affiché dans la console. Il conserve question et provenance,
passages, contexte, gabarit formaté envoyé, empreintes, budget, paramètres, identité du modèle, réponse brute,
mesures renvoyées par Ollama et contrôle des citations. Un fichier existant n'est jamais écrasé : choisir un autre nom.
Code de sortie 0 : réponse citée ou abstention contrôlée ; 1 : échec technique de préparation/appel/enregistrement ;
2 : sortie du modèle invalide ou génération reçue mais techniquement incohérente (trace conservée).
Une erreur d'arguments peut aussi donner le code 2, sans appel au modèle.

Après lecture de Q036, exécuter l'autre exemple prévu, sans reformuler la question humaine :

```powershell
.\.venv\Scripts\python.exe .\scripts\rag\rag.py --generate --question-id Q003 --output .\data\rag\Q003_rag.json
```

Q003 est annotée `hors_corpus` dans le lot de calibration. Le programme n'utilise pas ce type annoté pour forcer
la réponse. L'abstention réelle obtenue avec cette commande est documentée ci-dessous.

### Validation avant le premier appel réel

**45 tests réussis** ici sous Python 3.12.14 et NumPy 2.3.5, avec E5, tokeniseur Qwen et serveur Ollama simulés.
Ils vérifient notamment budget limite/dépassé, absence d'appel quand le budget est dépassé, référence du modèle,
quantification, requête UTF-8 locale et raw, citations inconnues/mal formées, conservation de la réponse interrompue,
distinction abstention/erreur et sauvegarde sans écrasement. Compilation Python et contrôle du diff exécutés.
Ces tests ne valident pas le vrai tokeniseur Qwen, le compte GGUF, la génération ni les ressources du Legion.
Les traces réelles de Q036 et Q003, analysées ci-dessous, complètent ces tests. Les tests dans l'environnement Windows,
la relecture du binôme et la présentation à l'équipe restent à confirmer avant de valider #51.

Pour les premiers essais, les questions Q036 (`dans_corpus`) et Q003 (`hors_corpus`) du lot de **calibration** au tag
`jeu-questions-v1` ont été proposées avant exécution dans la conception. Leur texte restera inchangé.
Le lot de test, les métriques, la calibration et les décisions de #52 ne sont pas modifiés.

Une référence qui existe parmi les passages fournis est structurellement valide ; cela ne prouve pas que le passage
justifie la phrase. Cette distinction devra rester explicite dans les résultats.

### Premier résultat RAG réel : Q036, 18 octobre 2026

Source : trace terminal « Texte collé(1).txt » transmise par Jibril, SHA-256
`1cc87a6c42eb998534cc1ba648e8a52a50e994ab485f62ed3a94d103757b322a`.
Elle rapporte l'exécution locale de la commande Q036 ci-dessus et l'enregistrement dans `data/rag/Q036_rag.json`.
L'assistant analyse cette trace ; il n'a pas lancé Qwen sur la machine de Jibril.
La question humaine, y compris « empoyeur », et le commit du jeu sont inchangés. Les cinq passages et leurs scores
correspondent à la récupération documentée en section 4. Le modèle et son digest correspondent à la référence #31.
Les versions Python et des dépendances correspondent à celles de la récupération réelle déjà rapportée.
La consigne reste `rag-b1-v1` et les paramètres restent ceux fixés avant cet essai.

| Contrôle ou mesure de cette exécution | Résultat |
|---|---|
| Statut | `reponse_citee`, `e5_charge: true`, `ollama_appele: true` |
| Entrée, tokeniseur HF / `prompt_eval_count` Ollama | 2 317 / 2 317 tokens, concordants |
| Budget contrôlé | 2 317 + 512 + 64 = 2 893 ≤ 8 192 |
| Sortie | 381 tokens, `done: true`, `done_reason: stop` |
| Références détectées | `[P1]`, `[P5]` ; aucune citation invalide détectée |
| Erreurs techniques rapportées | Aucune |
| `total_duration` Ollama | 46,2005116 s |
| `load_duration` Ollama | 21,9012127 s |
| `prompt_eval_duration` Ollama | 18,503807 s |
| `eval_duration` Ollama | 5,774473 s |

Les durées sont celles renvoyées par Ollama, converties de nanosecondes en secondes. `total_duration` n'est pas
une durée de la chaîne Python entière : elle ne mesure pas l'encodage E5, la récupération ou les téléchargements.
Ce résultat unique ne constitue pas une mesure systématique de performance, ni une observation des ressources.
Empreinte de l'entrée formatée : `ae84983d856c21745f83d5dcd05af26289c770815fe58bbc0f185190b44a77e5` ;
empreinte du gabarit : `d5495a1e5db0611132a97e46a65dbb64a642a499421228b9c8b93229097fa9a4`.

**Lecture qualitative de la réponse, par comparaison aux passages fournis :**

- Qwen reprend les huit mesures de prévention énumérées dans P1, sans transformer les conseils aux travailleurs
  de P2 en obligations de l'employeur ; les passages moins directement pertinents P3 et P4 ne sont pas cités.
- L'introduction présente ces mesures de manière générale. Elle ne reprend pas la condition de P5 concernant
  l'identification du risque par l'évaluation des risques, ni celle de P1 sur l'application en cas d'épisode de chaleur
  intense et l'adaptation en cas d'intensification. La portée de la réponse est donc trop générale par rapport aux sources.
- `[P1][P5]` figure dans l'introduction ; les huit puces ne portent pas chacune leur référence. La consigne demandant
  une citation accompagnant chaque affirmation n'est donc pas suivie dans sa forme prévue. Le contrôle structurel
  accepte néanmoins ces références existantes : il ne mesure pas la couverture des affirmations.
- La réponse reprend une longue liste plutôt qu'une synthèse brève. Le statut `reponse_citee` constate le respect
  du format des références ; il ne vaut pas validation sémantique ou juridique de la réponse.

Les indicateurs `justification_semantique_verifiee` et `couverture_des_affirmations_verifiee` restent à `false`.
La réponse brute n'est pas corrigée. Cette baseline a été conservée pour exécuter ensuite Q003 avec la même
consigne et les mêmes paramètres, comme prévu avant les essais. Aucune question ni aucun protocole d'évaluation
n'est modifié.

### Second résultat RAG réel : Q003, abstention, 18 octobre 2026

Source : trace terminal « Texte collé(2).txt » transmise par Jibril, SHA-256
`58a6acffbf0397ae61a7982e407700214c411cf03a00173d432fc22848f43f19`.
Le terminal confirme l'enregistrement de `data/rag/Q003_rag.json` sur son Legion. L'assistant analyse cette trace
sans exécuter Qwen à distance. Question humaine du lot de calibration, conservée mot pour mot :

> Un fonctionnaire peut-il avoir une autre activité à coté de son travail ?

Réponse brute intégrale :

> Je ne peux pas répondre à cette question à partir des passages fournis.

| Contrôle ou mesure de cette exécution | Résultat |
|---|---|
| Statut | `abstention_modele`, `e5_charge: true`, `ollama_appele: true` |
| Entrée, tokeniseur HF / `prompt_eval_count` Ollama | 1 822 / 1 822 tokens, concordants |
| Budget contrôlé | 1 822 + 512 + 64 = 2 398 ≤ 8 192 |
| Sortie | 17 tokens, `done: true`, `done_reason: stop` |
| Citations / erreurs techniques | Aucune citation, aucune erreur technique rapportée |
| `total_duration` Ollama | 1,1602394 s |
| `load_duration` Ollama | 0,0041829 s |
| `prompt_eval_duration` Ollama | 0,724377 s |
| `eval_duration` Ollama | 0,28686 s |

| Référence | Passage | Indice | Score | Sujet |
|---|---|---:|---:|---|
| P1 | `m2-article101113-0001` | 367 | 0.8584688901901245 | Incompatibilité entre conseiller prud'homal en activité et conseiller du salarié |
| P2 | `m2-article115944-0006` | 1098 | 0.8544212579727173 | Déclaration des activités de services à la personne |
| P3 | `m2-article376807-0030` | 3712 | 0.8535135984420776 | Commissions supplémentaires du CSE |
| P4 | `m2-article376115-0001` | 3443 | 0.8534690141677856 | Fonctions du collaborateur médecin du travail |
| P5 | `m2-article115944-0003` | 1095 | 0.8525987863540649 | Champ des activités de services à la personne |

Lecture qualitative limitée aux cinq passages : ils ne fournissent pas les règles de cumul d'activités d'un
fonctionnaire. L'abstention est donc cohérente avec le contexte reçu. La récupération renvoie toujours cinq voisins,
même lorsque leurs textes ne suffisent pas. Le score maximal de 0,8585 environ n'est ni une probabilité de réponse
correcte ni un seuil à adopter. Aucun seuil n'a été ajouté et aucune annotation n'a été envoyée au générateur.

Contrôles effectués ici sur la trace : les cinq textes et métadonnées correspondent exactement aux objets de
`passages_m2.json` aux indices rapportés ; le validateur reproduit `abstention_modele` sur la réponse brute ;
l'empreinte de l'entrée formatée est cohérente. Les consignes, options de génération, modèles, versions Python
et dépendances, ainsi que les empreintes de l'index et des passages, sont identiques à Q036.
Empreinte de l'entrée formatée : `df707a86d15c876a335e921c2f16fe25ffd320afb31a7e9b8b6f5c6b9e229cd0`.
Les durées viennent d'Ollama ; elles ne mesurent pas la chaîne Python entière. La durée très faible de chargement
est compatible avec un modèle déjà chargé, mais ne prouve pas son placement CPU/GPU. Les deux exemples ont des
entrées et longueurs de sortie différentes : leur durée ne mesure pas à elle seule un gain de performance.

Nous disposons désormais d'un exemple réel avec références existantes et d'un exemple réel d'abstention.
Ces deux cas de calibration ne donnent aucun taux de réussite, aucune qualité générale des citations et aucune
garantie d'abstention sur d'autres questions. Les limites de Q036 restent ouvertes. Aucun réglage n'est modifié
sur la base de ces résultats et aucune mesure systématique de #52 n'est lancée.
