# Agent0 Light : génération synthétique locale (#91 à #93)

## 1. Périmètre et état

Responsable : Jibril BENSALEM. Relecteurs désignés : Mahé BEGNIS (`mahebegnis`) et Remy RAYANE (`Remynou`).
État au 18 octobre 2026 : contrat et préparateur de sources implémentés ; 44 tests, contrôle du corpus et première
sélection réussis sur le Windows de Jibril. L'aperçu de #93 a également passé les 58 tests et la préparation Windows.
Le contrôle du modèle/gabarit/budget a également réussi sur Windows : 75 tests, entrée HF de 1 259 tokens.
La génération simple/reformulée et ses contrôles sont implémentés : 93 tests réussis ici et sur Windows.
Deux candidats réels, simple et reformulation, ont passé les contrôles techniques ; leurs objets complets ont
été transmis et comparés à la source. La provenance du cas simple est confirmée. La relecture indépendante
de #93 et les verdicts humains sur les cas restent attendus. La PR RAG #85 est préservée.

Agent0 Light est un outil exploratoire pour proposer des exercices supplémentaires au RAG, puis étudier ses
faiblesses. Qwen n'est ni réentraîné ni utilisé comme juge unique. Le Gold Set de #44 reste la référence humaine ;
les questions générées, même relues, restent synthétiques. Le présent travail ne remplace ni le protocole officiel,
ni la mesure du volet B de #52, ni une adaptation du modèle au sens du sujet.

| Ensemble | Rôle | Emplacement |
|---|---|---|
| Gold Set humain | Évaluation de référence, règles existantes de #44 | `evaluation/questions/`, tag `jeu-questions-v1` |
| Candidats synthétiques | Propositions à contrôler et relire | Futur `data/synthetic/<run_id>/` |
| Challenge Set figé | Comparaisons exploratoires sur des cas synthétiques relus | Futur `evaluation/synthetic/`, petit lot et manifeste (#95) |
| Paires d'entraînement | Ajustement de l'encodeur, pipeline existant #49 | `data/adaptation/`, séparé du Challenge Set |

Cette séparation est l'extension demandée par Jibril le 18 octobre. Le README du jeu humain, les questions,
les annotations et le protocole officiel ne sont pas modifiés.

## 2. Principe : proposition et fiche de suivi

Comme une copie et sa fiche de correction, on distingue deux objets :

1. `Proposition` est ce que le futur Qwen pourra retourner : question, type, preuves et raisons proposées.
2. `CasSynthetique` ajoute les métadonnées du programme : identifiant `SYN_<run_id>_<numéro>`, lot, origine
   synthétique, sources réellement fournies à la génération et suivi des contrôles.

`schema_generation()` exporte le JSON Schema de `Proposition`. Il sera transmis à Ollama en #93 ; le programme
validera ensuite sa sortie. Les règles croisées écrites en Python ne figurent pas toutes dans ce JSON Schema :
recevoir un JSON conforme à sa structure ne dispense donc pas d'appeler `lire_proposition()`.

Le mode strict refuse par exemple la chaîne `"true"` à la place du booléen `true`. Les champs inconnus sont
interdits, y compris à l'intérieur d'une preuve. Une sortie Qwen contenant `id`, `run_id` ou `validation` est
refusée. Le parseur rejette aussi les clés JSON dupliquées, NaN/Infinity, le Markdown entourant le JSON et les
sorties incomplètes. Il ne répare ni ne reformule la réponse.

## 3. Champs et responsabilités

| Champ | Produit par | Sens |
|---|---|---|
| `question` | Qwen | Texte conservé tel que reçu, sans nettoyage silencieux |
| `type` | Qwen, selon la commande future | `simple`, `reformulation`, `multi_passage`, `adversarial` ou `hors_corpus` |
| `difficulty_target` | Qwen, selon la consigne future | `easy`, `medium` ou `hard` : difficulté visée, jamais mesurée |
| `answerable_proposed` | Qwen | Proposition de réponse possible ; aucune vérité terrain automatique |
| `evidence` | Qwen | Liste de couples `passage_id` / `excerpt` proposés comme preuves positives |
| `generation_reason` | Qwen | Objectif de génération |
| `adversarial_premise`, `correction_proposed` | Qwen | Prémisse à vérifier et correction proposée d'un piège |
| `out_of_corpus_reason` | Qwen | Motif proposé d'absence de réponse, à vérifier humainement |
| `id`, `run_id` | Programme | Identité stable du cas et lien vers le manifeste de l'exécution |
| `schema_version`, `set` | Programme | `synthetic-v1` et `synthetic_challenge`, pour identifier le contrat et l'origine |
| `generation_source_ids` | Programme | Passages fournis à Qwen, distincts des preuves positives de réponse |
| `validation.automatic` | Programme, après les contrôles futurs | `pending`, `passed` ou `failed` |
| `validation.human` | Relecture humaine | `pending`, `accepted` ou `rejected` |
| `validation.answerable_confirmed` | Relecture humaine | `null` avant confirmation ; booléen explicite pour un cas accepté |
| `reviewer`, `review_note`, `expected_points` dans `validation` | Relecture humaine | Auteur, justification et éléments attendus de réponse ; aucun jugement automatique |

Un cas hors corpus peut avoir des sources de génération, mais ses preuves positives restent vides. Il peut
aussi provenir d'une consigne hors domaine : les sources de génération sont alors vides et la consigne exacte
devra être conservée dans le manifeste/les traces de #93.

## 4. Règles de cohérence de cette première version

| Cas | Contrôle appliqué |
|---|---|
| Simple ou reformulation | Réponse possible proposée et preuves provenant d'un seul passage |
| Multi-passage | Réponse possible proposée et au moins deux identifiants de preuve distincts |
| Piège répondable | Prémisse, correction proposée et preuves requises |
| Piège non répondable | Prémisse et motif d'absence requis ; preuves et correction étayée absentes |
| Hors corpus | Réponse possible proposée à `false`, motif obligatoire et preuves vides |
| Tous les cas | Aucun doublon exact de preuve ; aucune preuve hors des sources de génération déclarées |

Ces règles expriment le contrat de la V1 ; elles ne démontrent ni la catégorie réelle ni la nécessité de combiner
deux passages. Le fait de savoir produire ces structures ne signifie pas que leurs prompts sont implémentés :
la génération simple/reformulation relève de #93, les trois autres catégories de #94.

## 5. Ce qui est vérifié maintenant, plus tard et humainement

`creer_candidat()` attribue l'identité d'une proposition déjà parsée. Il laisse les contrôles automatiques et la
relecture à `pending`, avec `answerable_confirmed: null`. Un schéma cohérent n'est pas un contrôle de corpus.

| Niveau | Contrôle | État |
|---|---|---|
| Contrat #91 | Champs, types et cohérence interne | Implémenté |
| Sources #92 | Empreinte M2, schéma des métadonnées et sélection d'identifiants existants | Implémenté, tests et sélection Windows réussis |
| Extraits #93 | Extraits de Qwen retrouvés mot pour mot dans les passages sélectionnés | À implémenter |
| Qualité #95 | Sens, suffisance, conditions, exceptions et absence de réponse dans le corpus complet | Relecture humaine à réaliser |
| Gel #95 | Lot, manifeste, empreintes et attentes figés avant mesure | À implémenter |

Un contrôle automatique réussi ne remplit jamais les champs humains. Le contrat exige pour une acceptation :
contrôles automatiques réussis, verdict explicite, nom et note de relecture, et des points attendus pour un cas
répondable. Pour un cas non répondable accepté, cette liste est vide : la justification se trouve dans la note de
relecture. Une proposition mal classée est rejetée ; une correction éventuelle doit être tracée séparément avant
un nouveau gel. Une relecture ne transforme jamais une question synthétique en question humaine du Gold Set.

Le schéma vérifie la cohérence des données déclarées, pas l'identité ou l'action réelle du relecteur. Ces modèles
ne sont pas un système d'authentification. Toute future écriture/lecture de fichier doit revalider l'objet complet :
modifier un objet Python en mémoire ne constitue pas une étape de validation.

Un cas incertain reste hors du lot mesuré. Pour un cas hors corpus, ni le refus de Qwen ni l'échec de récupération
ne prouvent l'absence d'une réponse. Pour un cas multi-passage, les sources doivent être nécessaires et suffisantes,
pas seulement distinctes. Les éventuelles sources alternatives valables devront aussi être considérées en #97.

## 6. Conventions des futures traces

#91 ne crée aucun lot ni aucun manifeste. Pour #93, chaque `run_id` désignera un dossier non écrasé contenant :

- `manifest.json` : commit du code, versions Python/Ollama, digest du modèle, empreinte du corpus, paramètres,
  graine, sélection et version/empreinte des prompts ;
- `traces.jsonl` : requêtes exactes, réponses brutes et erreurs techniques ;
- `candidates.jsonl` : cas ayant passé les contrôles automatiques, toujours à relire ;
- `rejected.jsonl` : rejets automatiques et motifs, sans réparation silencieuse.

L'unicité de `run_id` et de `id` à l'échelle des fichiers reste à contrôler lors du stockage (#93).
Les candidats non confirmés restent dans les traces, sans entrer dans le lot figé de #95. Chaque version figée du
Challenge Set conserve ses identifiants, ses sources et ses attentes avant d'observer les réponses du RAG. Un
nouveau lot ciblé constitue une nouvelle version ; ses pourcentages ne se comparent pas directement à ceux d'un
autre lot. Les modifications du système se comparent sur le même jeu figé.

## 7. Exécuter les tests sous Windows

Depuis la racine du dépôt, après récupération de la branche `feat/91-agent0-schema`, utiliser un environnement
séparé pour ne pas modifier le `.venv` du RAG :

Procédure exécutée par Jibril sous Windows, avec le Python du `.venv` existant :

```powershell
.\.venv\Scripts\python.exe -m venv .venv-agent0
.\.venv-agent0\Scripts\python.exe -m pip install -r .\scripts\synthetic\requirements-lock.txt
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
```

Exécuter les commandes l'une après l'autre et arrêter en cas d'erreur. Si `.venv-agent0` existe déjà et contient
un autre travail, vérifier cet environnement avant d'y installer les dépendances. Le Python du `.venv` sert à
créer un environnement indépendant ; ses paquets ne sont pas modifiés. Aucun poids de modèle n'est nécessaire.

L'autre procédure documentée initialement reste possible si `uv --version` réussit : `uv venv --python 3.12
.venv-agent0`, puis `uv pip sync --python .venv-agent0\Scripts\python.exe scripts/synthetic/requirements-lock.txt`.
`uv pip sync` remplace les paquets du seul environnement indiqué ; ne pas l'appliquer à un environnement partagé.
Chez Jibril, PowerShell ne trouvait pas `uv` le 18 octobre : la procédure `venv`/`pip` ci-dessus a fonctionné.

Pour afficher le schéma que recevra plus tard Ollama, sans appel de modèle :

```powershell
.\.venv-agent0\Scripts\python.exe -c "import json; from scripts.synthetic.schema import schema_generation; print(json.dumps(schema_generation(), ensure_ascii=False, indent=2))"
```

Vérification effectuée dans l'environnement de développement : **27 tests réussis**, Python 3.12.14 et Pydantic 2.14.0.
Compilation et export du schéma également contrôlés. Les dépendances
directes et transitives effectivement présentes sont listées dans `scripts/synthetic/requirements-lock.txt` ; ce
fichier a été relevé depuis les métadonnées de l'environnement, pas produit par un résolveur sur Windows.
Les tests utilisent uniquement des fixtures techniques, sans questions réglementaires ni données du Gold Set.
Aucun Qwen, E5, Ollama ou corpus réel n'est appelé.

### Retour Windows transmis par Jibril le 18 octobre

La création de `.venv-agent0` avec `venv` a réussi ; la commande de version affiche Python **3.12.15**. La sortie
`pip` confirme l'installation des cinq versions du verrou, dont Pydantic **2.14.0**. Jibril transmet ensuite les
27 noms de tests, tous `ok`, et le résumé `Ran 27 tests in 0.007s`, puis `OK`.

Cette trace confirme la réussite de la suite technique sur son Windows ; l'assistant n'a pas exécuté de commande
sur sa machine. Le résumé des tests ne contient pas de SHA Git : aucun commit exécuté n'est déduit du seul résumé.
La durée est celle des tests, sans rapport avec une latence de génération ou une mesure du RAG. La relecture de
Mahé et Remy reste à effectuer ; #91 n'est ni clôturée ni fusionnée sur la seule base de ces tests.

## 8. Références et suite

- [#91 : contrat](https://github.com/datatigersNLP/data_tigers_nlp/issues/91), puis [#92 : sources](https://github.com/datatigersNLP/data_tigers_nlp/issues/92).
- [Pydantic : mode strict](https://docs.pydantic.dev/latest/concepts/strict_mode/), [schéma JSON](https://docs.pydantic.dev/latest/concepts/json_schema/) et [validateurs](https://docs.pydantic.dev/latest/concepts/validators/), consultés le 18 octobre 2026.
- [Note d'assistance IA de cette étape](../journal/2026-10-18_agent0_light_91.md).

Le contrat #91 a passé les tests Windows ; la préparation des sources #92 est ajoutée ci-dessous sur une autre
branche. L'appel Qwen et les contrôles de sortie de #93, le benchmark #96/#97 et la boucle #98 restent à implémenter. Les charges réelles ne
sont pas déduites des durées de conversation ; elles seront déclarées par les contributeurs à la clôture.

## 9. Préparer les sources M2 (#92)

### Principe et branche

Un passage est un morceau de fiche. Pour éviter que les longues fiches dominent le tirage, le script choisit
uniformément des URL distinctes, puis un passage dans chacune. Le lot initial reste un échantillon exploratoire,
ni une sélection de passages pertinents pour une question, ni une garantie de couverture de tous les thèmes.

`scripts/synthetic/corpus.py` utilise seulement la bibliothèque standard. Il lit les deux JSON de
`front/public/index/`, jamais la matrice FP32, E5, Ollama, les questions humaines ou leurs annotations.
`test_corpus.py` est séparé des tests du contrat pour préserver leur relecture.

La branche `feat/92-agent0-sources` part du schéma testé (`521286d`, PR #99 encore ouverte au démarrage).
Elle ne modifie pas la branche #91 ni la PR RAG #85. Sa PR cible dev et dépend de #99 : intégrer #99 et remettre
la branche #92 à jour avant sa fusion, en préservant les éventuelles corrections de relecture.

### Les trois opérations

1. **Charger.** Contrôler le format du manifeste, le découpage M2, le nom du fichier, son SHA-256, le nombre
   d'objets, les neuf champs attendus, les identifiants uniques et les identifiants/URL/textes non vides.
2. **Sélectionner.** Trier les identifiants et les URL, puis utiliser un générateur aléatoire local à graine fixe.
   Le programme ne modifie ni l'ordre du corpus chargé ni les textes et ne dérègle pas le générateur aléatoire global.
3. **Tracer.** Conserver les groupes de passages avec leurs textes et métadonnées intacts, les deux empreintes
   JSON, le mode, la graine, la version de l'algorithme, Python, le commit Git, l'état modifié de la copie et
   l'empreinte du script dans un nouveau manifeste JSON UTF-8, sans écraser une sortie existante.

Les empreintes détectent une divergence par rapport au manifeste lu ; elles n'authentifient pas un manifeste
remplacé avec tous ses fichiers. Utiliser les exports versionnés, sans recalculer leurs empreintes pour contourner
un refus. Le bloc `modele` du manifeste décrit le modèle q8 du navigateur ; il ne choisit aucun générateur ici.

### Modes

| Mode | Unité sélectionnée | Particularité |
|---|---|---|
| Défaut, `--count N --seed S` | N fiches distinctes, un passage chacune | 5 fiches et graine 20261018 par défaut |
| `--pairs --count N --seed S` | N fiches distinctes ayant au moins deux passages | Deux identifiants distincts de la même fiche par groupe |
| `--ids ID1 ID2 ...` | Un groupe par identifiant, dans l'ordre donné | Pas de tirage ni de graine ; même fiche permise, doublons refusés |
| `--check-corpus` | Aucune sélection | Contrôle et résumé seulement ; aucun fichier écrit |

Une paire ne prouve pas que ses deux passages sont nécessaires à une réponse : ce contrôle relève de #94/#95.
Pour conserver le regroupement exact des paires, garder leur manifeste. `--ids` rejoue une liste ordonnée de
passages indépendants. Une demande impossible est refusée, sans répétition d'une fiche pour atteindre un quota.
La reproductibilité suppose les mêmes données, paramètres, code et environnement ; les identifiants enregistrés
permettent de retrouver la sélection même si une autre version de Python change le comportement du tirage.

### Commandes Windows, après récupération de la branche #92

Depuis la racine, avec l'environnement Agent0 déjà installé :

```powershell
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\corpus.py --check-corpus
```

Ces contrôles doivent précéder la sélection réelle. Pour préparer ensuite cinq sources :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\corpus.py --count 5 --seed 20261018 --output .\data\synthetic\sources\selection_001.json
```

Le résumé console contient les identifiants et les empreintes ; le fichier conserve aussi les textes complets.
Changer le nom de sortie pour une nouvelle exécution. Ce manifeste préparatoire ne contient aucune question.
`--index-dir` permet de désigner un autre dossier de fichiers pour les contrôles, notamment les exports techniques
des tests ; ce n'est pas une décision autorisant un autre corpus dans l'évaluation du projet.

Pour une sélection, une copie Git est requise afin d'enregistrer le commit du code. Si `git_dirty` vaut `true`,
le commit seul ne représente pas tous les changements locaux : conserver le diff avant une comparaison formelle.
`--check-corpus` reste utilisable sans Git. Le code retour est 0 en succès, 1 pour un refus opérationnel et 2 pour
une combinaison d'arguments invalide.

### Contrôles réalisés dans l'environnement de développement

- **44 tests réussis** : les 27 tests du schéma et 17 tests de chargement, diversité, répétition du tirage, paires,
  sélection explicite, provenance simulée et sauvegarde sans écrasement. Exports techniques artificiels, aucun modèle.
- **Contrôle réel des JSON versionnés** récupérés par le connecteur : 1 410 et 6 428 126 octets ; empreinte de l'en-tête
  `586cf190…`, empreinte des passages `aee5bbdb…`, 4 240 passages et 261 fiches ; commande `--check-corpus` réussie.
- Fonctions de sélection appelées sur ces métadonnées : cinq fiches distinctes, répétition identique et rejeu des
  identifiants identique. Deux paires de passages distincts d'une même fiche ont également été préparées.
- La matrice n'est pas présente dans cette copie locale de contrôle et n'a pas été lue. Le contexte matériel, le
  tokeniseur et le budget Qwen restent hors de cet incrément.

Ces contrôles ne prouvent ni pertinence juridique, ni suffisance d'une réponse. L'exécution Windows est désormais
réussie, selon les traces ci-dessous. Relecture de Mahé et Remy attendue avant fusion ; aucune charge réelle n'est
encore renseignée.

### Retour Windows transmis par Jibril le 18 octobre

Jibril transmet la suite complète : **44 tests `ok`**, résumé `Ran 44 tests in 0.346s`, puis `OK`.
`--check-corpus` retourne `corpus_verifie`, 4 240 passages, 261 fiches et les deux empreintes attendues.
La durée est celle des tests techniques, sans inférence ni mesure de performance du RAG.

La commande de sélection avec `--count 5 --seed 20261018` retourne ensuite `selection_preparee` et
`nombre_groupes: 5`. Sa trace indique la sauvegarde dans `data/synthetic/sources/selection_001.json` sur le PC
de Jibril. Le contenu complet de ce fichier n'a pas été transmis à l'assistant ; le résumé console est la preuve
analysée ici. Il contient les mêmes cinq identifiants que le tirage réalisé dans l'environnement de développement :

- `m2-article374529-0004` ;
- `m2-article377050-0003` ;
- `m2-article374500-0003` ;
- `m2-article377588-0003` ;
- `m2-article378349-0008`.

La provenance rapporte Python **3.12.15**, le commit `fea315586276f3484feec0b6b53bb1fd007f315a`,
`git_dirty: false`, et le SHA-256 du script
`3371face67648895dc966307b95cabd7f7c522062e88fea3c6fc83e61495edaf`. Cette empreinte correspond exactement
au script versionné avec des fins de ligne CRLF. La copie LF du même blob Git donne
`e8c25e53328d21e7412429bba4a1fec393b6268c693b26699a508bd2b4ebb25a` : la différence est expliquée par les
fins de ligne, sans changement du code. L'empreinte enregistrée décrit les octets effectivement exécutés sur ce PC.
Les JSON du corpus ont les mêmes octets sur les deux machines ; leur dossier est marqué `-text` dans `.gitattributes`.
Contrairement au résumé des tests seul, cette trace de sélection identifie explicitement le commit exécuté.
Le programme rapporte `ollama_appele: false` et `matrice_lue: false`. Aucun cas synthétique n'est encore généré.
Les commits documentaires suivants ne modifient pas les sources utilisées pour ce tirage ; son manifeste garde
correctement la provenance de son exécution initiale.

[Note d'assistance IA #92](../journal/2026-10-18_agent0_light_92.md).


## 10. Premier incrément de #93 : inspecter la consigne avant l'inférence

Jibril a vérifié son serveur local le 18 octobre : l'API annonce Ollama **0.40.5** et le catalogue renvoie
`qwen2.5-7b-instruct:q4_k_m-local`, digest
`6ec54444a8511aae6c2116b172eb3685d1416c523bfee0252ca33c7e55c481e4`.
Cela confirme le serveur et l'identité déclarée du modèle, pas encore le gabarit ni le budget de la future requête.

Cet incrément prépare la fiche d'exercice avant de la confier à Qwen. Il ne produit aucune question :

- `prompts.py` définit une consigne système commune et deux consignes distinctes, simple et reformulation.
  Version : `agent0-simple-reformulation-v1`. Le passage complet et le schéma de `Proposition` sont inclus.
- `generate.py --prepare-only` relit un manifeste #92, vérifie ses empreintes de corpus et chaque passage contre
  le corpus chargé. Il refuse un identifiant inconnu, une source modifiée ou dupliquée et un JSON ambigu.
- Le groupe demandé est numéroté à partir de 1 et doit contenir un seul passage. Une paire n'est pas traitée
  silencieusement comme un passage. Les autres catégories attendent #94.
- Le fichier `agent0-preparation-v1` conserve la source, les messages, le schéma de sortie, leur empreinte,
  la provenance de la sélection et celle du code actuel. L'empreinte de la sélection porte sur les octets de son
  fichier ; celle du prompt porte sur son objet JSON sérialisé en UTF-8 avec clés triées.
- Aucune dépendance supplémentaire : les fichiers de #91/#92 et leurs verrous restent inchangés.
  Ni Ollama, ni tokeniseur, ni matrice, ni Gold Set ne sont appelés ou lus par cette commande.

Les instructions demandent une proposition autonome en français, des extraits continus exacts et la conservation
des conditions utiles. La difficulté reste une cible imposée. Ces instructions ne prouvent pas leur respect par
le futur modèle ; les contrôles des sorties et la relecture humaine sont des étapes séparées.

### Essai Windows de l'aperçu

La branche `feat/93-agent0-generation` part de la tête `b8b6118` de #100. Sa PR cible `dev`, mais dépend
des PR #99 puis #100 : les intégrer avant elle, puis synchroniser en préservant les éventuelles corrections.
Le diff global inclut ces dépendances tant qu'elles ne sont pas fusionnées.

Depuis la racine du dépôt, vérifier d'abord que `git status --short --branch` ne montre pas de modifications
locales à préserver. Puis récupérer la branche et exécuter les tests avec l'environnement déjà installé :

```powershell
git fetch origin
git switch --track origin/feat/93-agent0-generation
git status --short --branch
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
```

Arrêter à la première erreur. Pour préparer le premier groupe du fichier déjà créé par Jibril :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --prepare-only --sources .\data\synthetic\sources\selection_001.json --group 1 --type simple --difficulty easy --output .\data\synthetic\preparations\simple_001.json
```

Le résumé doit annoncer `prompt_prepare`, `m2-article374529-0004`, `ollama_appele: false` et
`budget_tokens_verifie: false`. Ce dernier point est volontaire : l'aperçu ne permet pas de lancer une
inférence. Pour lire la consigne préparée dans le terminal :

```powershell
$apercuAgent0 = Get-Content -Raw -Encoding UTF8 .\data\synthetic\preparations\simple_001.json | ConvertFrom-Json
$apercuAgent0.prompt.messages | Format-List role, content
```

Pour l'autre consigne, remplacer `--type simple` par `--type reformulation` et choisir une nouvelle sortie,
par exemple `reformulation_001.json`. Sans `--output`, le programme affiche toute la préparation JSON.
Un fichier existant est refusé ; ne pas supprimer la première trace pour refaire un essai.

### Preuves et limites

**58 tests réussis ici**, Python 3.12.14 et Pydantic 2.14.0 : les 44 existants et 14 nouveaux tests.
La compilation et l'aide CLI sont contrôlées. Les tests utilisent des fixtures techniques ; la provenance Git
est simulée pour la commande car cette copie locale de contrôle n'est pas un checkout Git complet.

Les fonctions ont aussi été exécutées sur les vrais JSON M2 avec une sélection reconstruite à graine 20261018 :
le premier passage est bien `m2-article374529-0004`, de 318 caractères, conservés intégralement dans les deux
prompts. Ce contrôle n'est pas une lecture du fichier Windows de Jibril et ne revendique aucune provenance Git
réelle pour sa sélection reconstruite. L'essai Windows du premier aperçu a depuis réussi ; voir le retour ci-dessous.

La lecture des helpers publics de #85 confirme leur intérêt pour le contrôle du modèle, du gabarit et des
tokens. Ils ne sont pas présents sur cette branche, et l'aperçu n'importe pas le RAG. Le prochain incrément
ajoutera la fin de génération, les sorties brutes, les rejets et le stockage des candidats. Le client et le budget
sont désormais ajoutés par le deuxième incrément décrit en section 11. Aucun module de #85 n'est modifié. #93 reste ouverte et sa PR en brouillon ; l'estimation globale
de 6 h du ticket reste une prévision, sans temps réel inventé.

[Note d'assistance IA #93](../journal/2026-10-18_agent0_light_93.md).


### Retour Windows du premier aperçu, transmis le 18 octobre

La trace de Jibril montre le passage à `feat/93-agent0-generation`, un statut propre, puis les **58 tests**
réussis (`Ran 58 tests in 0.364s`, `OK`). La commande d'aperçu retourne `prompt_prepare`, catégorie
`simple`, cible `easy`, source `m2-article374529-0004`, version `agent0-simple-reformulation-v1`.
Elle rapporte Python 3.12.15, le commit `89202adefea0f33da154cb2e5dd7c8993cbc5c7d` et `git_dirty: false`.

L'empreinte du prompt
`161c5588984933f6bd73ad9155c651de52383a91559ee06e4557a2b965429a5e`
est identique à celle obtenue ici. Les empreintes de `generate.py`, `prompts.py` et `schema.py`
correspondent exactement à leurs octets CRLF, vérifiés contre les blobs LF exécutés ici.
La trace annonce la sauvegarde dans `data/synthetic/preparations/simple_001.json` ; son contenu complet n'a
pas été transmis. `ollama_appele`, `matrice_lue` et `budget_tokens_verifie` sont à `false`.
C'est la réussite de la préparation hors ligne, sans question générée ni validation sémantique.

## 11. Deuxième incrément de #93 : vérifier la place avant génération

Le contexte de Qwen ressemble à une valise : consigne, schéma, passage et réponse future doivent tenir ensemble.
`client_qwen.py` prépare la requête sans l'envoyer. Il reprend les garde-fous des helpers publics de #85
au commit `df91b85`, avec une adaptation explicite dans ce seul fichier : aucun import du RAG non fusionné,
aucune modification de #85. Après sa stabilisation, une éventuelle mutualisation pourra être discutée séparément.

### Contrôles et paramètres

- Appels locaux limités à `/api/version`, `/api/tags` et `/api/show` sur `127.0.0.1:11434`.
  Le client refuse d'appeler `/api/generate` à cet incrément.
- Modèle unique, digest de #31/#85, format GGUF, famille qwen2, quantification Q4_K_M, version et gabarit non vides.
  Les métadonnées retournées, y compris le gabarit et les paramètres déclarés par le modèle, sont conservées.
- Tokeniseur `Qwen/Qwen2.5-7B-Instruct`, révision `a09a35458c702b33eeacc393d103063234e8bc28`.
  Cache local par défaut, `trust_remote_code=False`. Une option explicite autorise son téléchargement si nécessaire.
- Gabarit Ollama rendu une fois et comparé au format Qwen system/user attendu, puis compté avec
  `add_special_tokens=False` et `truncation=False`.
- Contexte **8 192**, réponse réservée **512**, marge **64** : entrée au plus **7 616 tokens** selon le tokeniseur HF.
  Un dépassement est refusé ; le programme ne coupe pas un passage pour le faire tenir.
- La requête préparée utilise `raw: true`, `stream: false`, `format` avec le schéma JSON, température 0,
  graine 20261018 et maintien du modèle 30 minutes. Elle est enregistrée, jamais envoyée par ce mode.

`budget_tokens_verifie: true` signifie que le contrôle préliminaire HF a réussi.
`comptage_ollama_compare: false` rappelle qu'il faudra comparer ce compte à `prompt_eval_count` après
la première génération réelle. Aucun résultat de Qwen, fin de génération ou qualité de question n'est encore validé.
Le futur appel devra refaire ces contrôles, plutôt qu'envoyer aveuglément une ancienne requête sauvegardée.

### Dépendances

`requirements.txt` ajoute `transformers==5.17.0` et `jinja2==3.1.6`.
Le verrou complet a été résolu avec uv 0.12.23, Python cible 3.12 et contraintes du verrou existant du notebook 02,
en conservant les cinq versions de #91. Il inclut les marqueurs Windows/Linux et s'installe avec pip.
Les fichiers de contraintes du notebook 02 et du RAG ne changent pas.

Le verrou a été installé dans un environnement neuf ici : `pip check` réussit.
Transformers 5.17.0, Tokenizers 0.23.2 et Jinja2 3.1.6 sont importables sans torch.
Le message « PyTorch was not found » est attendu : seuls les outils de tokenisation sont utilisés côté Python ;
Qwen reste exécuté par Ollama. Aucun poids Qwen ni encodeur E5 n'est installé par ce verrou.

Commande de résolution utilisée ici, avec une copie locale du verrou d'indexation comme contrainte supplémentaire :

```bash
uv pip compile scripts/synthetic/requirements.txt --universal --python-version 3.12 --no-header --no-annotate -c /chemin/vers/la-copie-du-verrou-indexation.txt -o /chemin/vers/le-nouveau-verrou.txt
```

La résolution n'est pas à relancer pour l'essai Windows : installer le verrou versionné suffit.

### Commandes Windows, sur la branche #93

Vérifier l'état local avant la mise à jour ; exécuter une commande à la fois et arrêter en cas d'erreur.

```powershell
git status --short --branch
git pull --ff-only
.\.venv-agent0\Scripts\python.exe -m pip install -r .\scripts\synthetic\requirements-lock.txt
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
```

Avec Ollama démarré, préparer le budget de la même source, dans un nouveau fichier :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --prepare-qwen --sources .\data\synthetic\sources\selection_001.json --group 1 --type simple --difficulty easy --output .\data\synthetic\preparations\budget_simple_001.json
```

Résultat attendu : `requete_preparee`, `ollama_appele: true` (métadonnées seulement),
`budget_tokens_verifie: true`, `generation_appelee: false`, plus le nombre `nb_tokens_hf`.
Le mode `--prepare-only` reste utilisable hors ligne avec son comportement initial.

Si le tokeniseur figé manque dans le cache, la commande refuse et explique l'option
`--allow-tokenizer-download`. Rejouer alors la même commande avec cette option autorise uniquement
le téléchargement du tokeniseur depuis Hugging Face. L'aperçu `simple_001.json` reste conservé.
Ne pas changer le modèle, le digest ou les limites pour contourner une erreur.

### Vérifications du deuxième incrément et limites

**75 tests réussis ici**, dont 17 nouveaux tests du client et de son intégration à la CLI.
Serveur et tokeniseur Qwen simulés dans la suite, erreurs HTTP/délai/JSON, modèle absent ou ambigu,
mauvais digest/gabarit, limite exacte et dépassement d'un token, cache, sauvegarde et refus de génération.
Compilation et cohérence des dépendances vérifiées.

Un essai complémentaire utilise réellement les bibliothèques installées et le moteur Jinja avec un tokeniseur
WordLevel technique minimal : rendu et comptage réussis, 13 tokens sur cette fixture. Ce n'est ni le tokeniseur
Qwen réel ni une inférence ; ce chiffre n'est pas une mesure du prompt réglementaire.
Le cache/tokeniseur Qwen réel, le gabarit retourné par Ollama et le budget de Jibril restent à vérifier sur son PC.

La PR #101 reste en brouillon, le ticket #93 ouvert et la génération de candidats à implémenter après ce retour.
Les échecs de préparation sont affichés avec un code retour non nul ; les traces persistantes des appels et
échecs de génération seront ajoutées avec le stockage du prochain incrément. Aucune charge réelle n'est déduite.

Références techniques consultées le 18 octobre 2026 :
[Ollama, génération raw et schéma JSON](https://docs.ollama.com/api/generate),
[Hugging Face, gabarits de conversation](https://huggingface.co/docs/transformers/chat_templating),
[tokeniseurs et absence de troncature](https://huggingface.co/docs/transformers/main_classes/tokenizer).


### Retour Windows du budget, transmis le 18 octobre

L'installation pip du verrou enrichi réussit, y compris les dépendances Windows. Les **75 tests** sont `ok`,
résumé `Ran 75 tests in 0.527s`, puis `OK`. Le mode `--prepare-qwen` produit `requete_preparee`,
commit `1ab3530a3938044861e187f24aad42b108e71e46`, copie propre, Python 3.12.15.
Il rapporte Ollama 0.40.5, le digest Qwen attendu, Transformers 5.17.0, Tokenizers 0.23.2 et Jinja2 3.1.6.

L'entrée HF est de **1 259 tokens** : avec 512 de réponse et 64 de marge, le total prévu est **1 835 / 8 192**.
Le compte d'Ollama reste à comparer après une génération. Le gabarit rapporté a l'empreinte
`d5495a1e5db0611132a97e46a65dbb64a642a499421228b9c8b93229097fa9a4`.
L'empreinte de l'entrée raw
`87a09564d05c27576497f226e047f89553f35a59a95034ce0bf59240fdc844ed`
correspond exactement au texte reconstruit ici depuis les messages et le format Qwen contrôlé.
Le prompt garde l'empreinte précédente `161c5588…`.

La trace annonce la sauvegarde de `budget_simple_001.json` sur son PC ; le fichier complet n'a pas été transmis.
`ollama_appele: true` concerne les métadonnées, `generation_appelee: false` confirme le mode préparatoire.
Le message d'absence de PyTorch est attendu. Aucune génération n'est déduite de ce contrôle du budget.

## 12. Troisième incrément de #93 : un appel, un candidat ou un rejet

Le programme donne maintenant la fiche d'exercice à Qwen. Il conserve sa copie brute avant de la contrôler.
Un JSON conforme et un extrait retrouvé ne prouvent toujours pas que la question ou sa réponse sont correctes.

| Fichier | Responsabilité |
|---|---|
| `client_qwen.py` | Refaire les contrôles du modèle/budget, puis envoyer un seul appel local avec délai de 300 s |
| `validation.py` | Vérifier le contrat, la demande, les extraits exacts et les doublons |
| `run.py` | Réserver un dossier, tracer l'exécution et enregistrer candidat, rejet et résumé |
| `generate.py` | Exposer les trois modes et leurs arguments, sans appeler le RAG |

### Contrôles et fichiers produits

La fin doit être `done: true`, `done_reason: stop`. Le modèle retourné doit être celui demandé.
`prompt_eval_count` doit égaler le compte HF et `eval_count` être un entier positif au plus égal à 512.
Toute incohérence est une **erreur technique**, même si la réponse contient un JSON apparemment correct.

Après ces contrôles, le parseur strict de #91 refuse toute réparation implicite, métadonnée ajoutée par Qwen
ou JSON ambigu. Le type et la difficulté doivent correspondre à la commande. Chaque preuve doit utiliser
l'identifiant fourni et un extrait retrouvé mot pour mot dans le texte complet, sans normalisation de l'extrait.

La déduplication compare les questions après NFKC, passage en minuscules Unicode, remplacement de la ponctuation
par des espaces et réduction des espaces. Elle lit uniquement les `*/candidates.jsonl` du même dossier
`data/synthetic/`, sans Gold Set. Les chemins relatifs et empreintes de ces fichiers sont tracés.
Elle ne détecte pas tous les doublons de sens ; un fichier de candidats corrompu bloque le run avant le modèle.
Les runs de cette V1 s'exécutent l'un après l'autre ; aucun coordinateur de runs concurrents n'est ajouté.

Le dossier `data/synthetic/<run_id>/` doit être nouveau et contient :

| Fichier | Contenu |
|---|---|
| `manifest.json` | Configuration initiale, source et prompt complets, provenance, empreintes du code |
| `traces.jsonl` | État de déduplication, modèle/budget/requête, début d'appel, réponse brute ou erreur |
| `candidates.jsonl` | Un cas ayant passé les contrôles, ou fichier vide |
| `rejected.jsonl` | Un rejet automatique ou échec technique expliqué, ou fichier vide |
| `summary.json` | Statut final, compteurs, mesures techniques et identifiant éventuel |

Le manifeste et les trois fichiers JSONL sont créés avant l'appel. Les événements sont vidés vers le fichier
à chaque écriture. Une réponse reçue est tracée avant validation ; une erreur HTTP ou un corps invalide conserve
aussi les octets disponibles en base64 dans le diagnostic. Il n'y a ni relance automatique ni effacement d'un run.

Un dossier interrompu reste protégé et peut ne pas avoir de résumé final. Une panne d'écriture est signalée
comme erreur ; les fichiers déjà créés restent à inspecter. Utiliser un nouveau `run_id` pour un autre essai.

Un candidat a `validation.automatic: passed`, `human: pending`, `answerable_confirmed: null`
et aucun point de réponse confirmé. Son identifiant est `SYN_<run_id>_0001`.
Le texte de la question et ses extraits restent ceux reçus. Aucun candidat n'entre automatiquement dans le lot
figé de #95, et aucune règle d'entraînement ou d'évaluation officielle n'est modifiée.

### Premier essai Windows

Sur la branche #93, récupérer le code puis exécuter la suite. Les dépendances restent celles déjà installées.
Exécuter une commande à la fois et arrêter en cas d'erreur.

```powershell
git status --short --branch
git pull --ff-only
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
```

Avec Ollama démarré, générer **un seul candidat simple** :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --generate --run-id simple_001 --sources .\data\synthetic\sources\selection_001.json --group 1 --type simple --difficulty easy
```

Le résumé doit annoncer soit `candidat_prepare` avec une question à relire, soit `rejet_automatique` ou
`erreur_technique` avec un motif et les traces. Le code retour est 0 pour un candidat préparé, 1 pour un rejet
ou échec opérationnel, 2 pour des arguments incompatibles. Attendre le premier résultat avant l'essai reformulé.
Le délai de l'appel est au plus de 300 s côté client ; ce n'est pas une prévision de durée.

Après ce retour, l'autre catégorie s'utilise avec un nouveau `run_id`, par exemple `reformulation_001`,
et `--type reformulation`. `--output` reste réservé aux modes préparatoires ; les runs de génération
ont leur emplacement fixe dans `data/synthetic/`. Les anciens aperçus ne sont pas modifiés.

### Preuves et validation restante

**93 tests réussis ici**, Python 3.12.14 et Pydantic 2.14.0 : les 75 existants et 18 tests supplémentaires
de validation, client et stockage. Les deux catégories sont vérifiées avec des réponses techniques simulées.
Les tests couvrent un appel unique, erreurs HTTP/délai, réponse tronquée, comptes incohérents, JSON invalide,
source/extrait inventés, doublons, précédent fichier corrompu et refus de réutiliser un dossier.
Compilation, aide CLI et conservation des empreintes du prompt/raw Windows sont contrôlées.
Aucun appel réel à Qwen n'est prétendu ici.

Les premiers appels Windows simple et reformulation ont depuis réussi, avec une lecture assistée des deux
candidats ci-dessous. La relecture indépendante de Mahé/Remy et les verdicts humains restent attendus.
#93 et la PR #101 restent ouvertes ; aucune fusion ou charge réelle n'est déclarée.


### Premier candidat simple réel, retour Windows du 18 octobre

La session transmise par Jibril montre le fast-forward de `1ab3530` vers `823621b`, puis les **93 tests**
réussis : `Ran 93 tests in 0.447s`, `OK`. Le run `simple_001` retourne ensuite `candidat_prepare`,
un candidat et aucun rejet, identifiant `SYN_simple_001_0001`.

Question affichée : « Pendant le congé sans solde, le salaire du salarié est-il maintenu ? »

Le résumé annonce `done: true`, `done_reason: stop`, **1 259 tokens HF et 1 259 côté Ollama**,
**173 tokens générés**, comparaison effectuée et `relecture_humaine: pending`.
Il s'agit de la première génération synthétique réelle rapportée, distincte des réponses simulées des tests.
Aucune durée, mesure de mémoire ou d'utilisation GPU n'est fournie par ce résumé.

Jibril a ensuite transmis le candidat complet et les blocs `preparation.code` / `preparation.source` du manifeste.
La provenance confirme `823621b18535f245ad05bb99a762dbff39bc2ae0`, `git_dirty: false`, Python 3.12.15.
Les fichiers de traces complets n'ont pas été transmis.

Ce résultat confirme un premier passage de bout en bout, pas une mesure générale de qualité, une validation
humaine du cas ou son admission au lot figé. La lecture du cas et l'exécution reformulée ont ensuite été
réalisées ; leur comparaison est consignée ci-dessous. #93 reste ouverte.


### Comparaison des deux candidats et proposition à la relecture

Les deux objets JSON complets transmis par Jibril portent sur `m2-article374529-0004`, fiche
« Le congé sans solde », section « La rémunération est-elle maintenue pendant le congé ? ».
Ils citent exactement la même phrase du texte M2 :

> Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue.

| Cas | Question reçue | Entrée HF / Ollama | Tokens générés |
|---|---|---:|---:|
| `SYN_simple_001_0001` | Pendant le congé sans solde, le salaire du salarié est-il maintenu ? | 1 259 / 1 259 | 173 |
| `SYN_reformulation_001_0001` | Qu'arrive-t-il à la rémunération d'un employé pendant qu'il est en congé sans solde ? | 1 284 / 1 284 | 171 |

Le run reformulé rapporte `candidat_prepare`, un candidat, aucun rejet, `done: true`,
`done_reason: stop` et comparaison de tokens effectuée. Son résumé et son candidat complet sont fournis ;
son manifeste et ses traces complets ne le sont pas. Aucun SHA de code exécuté pour cette seconde inférence
n'est déduit du seul résumé. Le cas simple conserve la provenance explicitement lue ci-dessus.

La vérification locale de ces données reçues confirme l'extrait exact dans le corpus M2 versionné et deux
questions distinctes après normalisation. La reformulation reste légère : syntaxe ouverte et « employé »
pour « salarié », avec une bonne part du vocabulaire source conservée. Sa difficulté reste une cible `easy`,
sans difficulté mesurée ni performance de retrieval déduite.

Cette lecture assistée est favorable à la cohérence documentaire des exemples ; elle n'est pas la relecture
humaine indépendante de #95. Le passage complet conserve aussi l'information conditionnelle sur le CET.
Pour la variante plus ouverte, les relecteurs pourront préciser si cette nuance doit figurer dans les attentes
et si l'extrait court suffit. Aucun point attendu ni verdict humain n'est attribué ici.

Les deux objets gardent `automatic: passed`, `human: pending`, `answerable_confirmed: null`,
aucun nom/note de relecture et aucun point confirmé. Ils restent des candidats synthétiques, hors lot figé.

La V1 simple/reformulation est proposée à la relecture de la PR #101. Les **93 tests Windows** et les deux
appels réels constituent les preuves techniques disponibles ; ces deux exemples ne donnent aucun taux de
réussite général. Le code ne change pas après ces retours. #93 reste ouverte, avec son estimation initiale de
6 h ; aucun temps réel, fusion ou clôture n'est déclaré.

État GitHub vérifié le 18 octobre : Mahé a approuvé #99 sur `521286d` et #100 sur `b8b6118`.
Rémy reste demandé sur ces PR. Aucune review de #101 n'est encore déposée au moment du contrôle.
L'ordre d'intégration reste #99, #100, puis #101 ; préserver les éventuelles corrections avant chaque intégration.
Les remarques non bloquantes des reviews #99/#100 ne sont pas transformées en modifications du contrat dans cette mise à jour documentaire.


## 13. #94 — Première préparation multi-passage

Cet incrément initial prépare deux sources avant d'activer leur génération. Son état au commit `2cb10c1`
est décrit ci-dessous ; l'activation suivante et les retours Windows figurent en section 14. Les contrôles
de sortie multi-passage, les catégories adversarial/hors_corpus et leur exécution restent à réaliser.
Le schéma de #91 connaît déjà ces catégories ; aucune modification de ce contrat ni du sélecteur #92.

### Paire fournie et limite méthodologique

Le retour Windows de Jibril annonce une sélection `paires_001.json`, mode `paires`, graine `20261018`,
un groupe contenant, dans cet ordre, `m2-article374529-0002` et `m2-article374529-0000`.
Les empreintes M2 sont conformes ; la provenance annoncée est `e6d6a640769d394155940fdd13226199c5192001`,
copie propre, Python 3.12.15, sans appel Ollama ni lecture de matrice. Le fichier Windows complet n'a pas
été transmis ; ses octets et son empreinte ne sont pas prétendus lus ici.

La reconstruction locale du tirage retrouve ces mêmes identifiants. Les textes versionnés comportent
respectivement **1 184** et **575 caractères**, fiche « Le congé sans solde ».
Le premier détaille notamment l'exercice d'une autre activité, les clauses du contrat et la loyauté ;
le second présente l'accord avec l'employeur, la rémunération et les effets de l'absence.
Les passages se recouvrent aussi sur l'absence de réglementation. La paire est un point de départ potentiel,
pas une preuve qu'une véritable question de combinaison existe ou a été obtenue.

Le prompt demande une seule question cohérente, une information propre à chaque source, une preuve
exacte par passage et une justification de leur apport dans `generation_reason`. Cette justification reste
une proposition de Qwen. La relecture devra vérifier **nécessité et suffisance des deux sources** : citer
deux passages ou juxtaposer deux questions indépendantes ne suffit pas.

### Fichiers et formats

- `prompts.py` : nouveau prompt `agent0-multi-passage-v1`, sans exemple réglementaire ni réponse attendue.
- `generate.py` : groupe de deux passages pour `multi_passage`, un seul pour simple/reformulation.
- `test_multi_passage.py` : tests techniques de préparation, de sauvegarde et de blocage avant génération.
- `test_generate.py` : la vérification des deux anciens prompts continue de porter explicitement sur ces deux catégories.

Les anciens aperçus `agent0-preparation-v1` conservent leur objet `source` et leurs prompts inchangés.
L'aperçu multi-passage est explicitement `agent0-preparation-v2`, avec un tableau `sources` de deux objets
documentaires complets dans l'ordre du groupe. Il n'a pas de champ `source` singulier. Les règles de
provenance, empreintes, absence de troncature et refus d'écrasement restent communes.

`--prepare-only` fonctionne sans réseau. `--prepare-qwen` peut vérifier le budget avec le client existant,
sans génération et avec les mêmes réserves 8192/512/64 ; ce contrôle sur la paire réelle reste attendu.
`--generate --type multi_passage` est refusé avant lecture du corpus, API ou création de run, tant que
le validateur de sortie n'a pas été étendu. Aucun candidat multi-passage n'est déclaré par cet incrément.

### Essai Windows suivant

Exécuter une commande à la fois, et arrêter si elle échoue. Le statut Git doit être propre avant de changer
de branche ; conserver les éventuels changements locaux et les examiner avant de poursuivre.

```powershell
git status --short --branch
git fetch origin
git switch --track origin/feat/94-agent0-categories
git status --short --branch
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --prepare-only --sources .\data\synthetic\sources\paires_001.json --group 1 --type multi_passage --difficulty medium --output .\data\synthetic\preparations\multi_passage_001.json
```

Résultat attendu : `prompt_prepare`, deux `source_ids`, `version_prompt: agent0-multi-passage-v1`,
`ollama_appele: false`, `budget_tokens_verifie: false`. `medium` désigne une difficulté souhaitée,
pas une mesure. Empreinte du prompt reconstruit :
`f17fbef77a24d5b765ed4a8fd8f7a6ac3016ade28468b3c6f90410de97539c4e`.
Elle concerne le prompt avec cette paire et cette difficulté ; elle ne constitue pas l'empreinte du fichier Windows.
Attendre le retour de cet aperçu avant l'incrément de validation/génération.

### Vérifications et état

**101 tests réussis** sous Python 3.12.14 : les 93 précédents et 8 nouveaux, sur documents techniques
artificiels et client simulé. Couverture supplémentaire : deux sources exactes et ordonnées, paramètres
invalides, cardinalité, format versionné, reproductibilité, sauvegarde sans réseau, budget simulé sans génération,
génération bloquée avant ses effets et protection d'un fichier existant. Compilation et aide CLI contrôlées.
Reconstruction sur le corpus réel sans modèle ; empreinte du prompt simple toujours identique à celle du
premier aperçu Windows. Aucun appel réel au tokeniseur Qwen ou à Ollama n'est réalisé ici.

Travail isolé sur `feat/94-agent0-categories`, depuis #101 au commit `f725321` ; PR en brouillon vers `dev`,
dépendante de #99/#100/#101, avec Mahé et Remy demandés en relecture. Les branches RAG et #93 restent
inchangées. Pas de verdict humain, de gel du Challenge Set, de fusion ou de clôture. L'estimation #94 reste
7 h de travail actif prévisionnel pour l'ensemble des trois catégories ; aucune durée réelle n'est attribuée.


## 14. #94 — Contrôles de sortie et premier essai multi-passage

État de l'activation au commit `53d4da2` ; le résultat réel et l'ajustement suivant sont en section 15.

### Retours Windows de l'aperçu et du budget

Jibril transmet le checkout propre de `feat/94-agent0-categories`, les **101 tests réussis**
(`Ran 101 tests in 0.561s`, `OK`) et l'aperçu au commit
`2cb10c1f9589b70c2843ec4f366fc19d6af2f1f0`, copie propre, Python 3.12.15.
Les deux `source_ids` et l'empreinte du prompt correspondent à la reconstruction de la section 13.
Le fichier complet de préparation n'est pas transmis ; le résumé est la preuve disponible.

Le mode `--prepare-qwen` réussit au même commit, copie propre : Ollama 0.40.5, digest local conforme,
Transformers 5.17.0, Tokenizers 0.23.2 et Jinja2 3.1.6. Il annonce **1 925 tokens HF**, une réserve de
512 tokens de sortie et 64 de marge, soit **2 501 sur 8 192**. Aucune génération n'est appelée et le
comptage Ollama/GGUF n'est pas encore comparé. L'avertissement PyTorch absent est attendu : Python
utilise le tokeniseur, Ollama exécute le modèle.

Empreinte du texte raw rapportée :
`39885d2ecaa9fd6d036a6a0a313fe0e45591f23bdfd34beac2582338f8ebe61d`.
Elle est retrouvée ici par reconstruction du texte au format Qwen attendu, avec le même prompt.
Les empreintes CRLF de `prompts.py`, `schema.py` et `client_qwen.py` correspondent aussi au résumé.
Le tokeniseur Qwen réel n'est pas chargé ici et les 1 925 tokens ne sont pas présentés comme recomptés localement.

### Extension minimale

`validation.py` accepte désormais la préparation multi v2 avec deux sources distinctes et non vides.
Il vérifie la proposition JSON stricte, la catégorie/difficulté demandée, l'appartenance de chaque preuve
aux sources fournies et la présence de son extrait exact **dans son propre passage**. Les deux sources
doivent être couvertes ; un troisième identifiant, une preuve unique ou dupliquée ne suffisent pas.
Le contrôle commun des doublons normalisés reste actif entre les runs synthétiques, toutes catégories confondues.

Le candidat conserve les deux `generation_source_ids` dans l'ordre de sélection, même si les preuves sont
présentées dans l'autre ordre. Il garde `automatic: passed`, `human: pending`, `answerable_confirmed: null`
et aucun point attendu. Le JSON candidat reste `synthetic-v1`, qui prévoyait déjà plusieurs sources.
L'enveloppe de run reste `agent0-run-v1` et contient la préparation explicitement versionnée v2.
Les candidats et manifestes existants ne sont ni réécrits ni transformés.

Le blocage temporaire de `--generate --type multi_passage` est levé. L'orchestrateur, le client, le prompt,
le schéma et le corpus sont inchangés : un appel au plus, métadonnées et budget vérifiés à nouveau, sortie
brute conservée avant contrôle, puis candidat ou rejet. Le budget de sortie reste 512. Une fin `length`
reste une erreur technique tracée, même si le JSON reçu est valide ; aucune relance ou augmentation automatique.

Ces contrôles vérifient la structure et la fidélité des extraits, pas la pertinence de la question ni le besoin
réel de combiner les passages. La justification du générateur reste à relire. Aucun juge Qwen n'est ajouté.

### Premier appel réel à exécuter

Rester sur `feat/94-agent0-categories`. Exécuter une commande à la fois ; arrêter en cas d'échec ou de
modification locale inattendue, et examiner le statut avant de poursuivre.

```powershell
git status --short --branch
git pull --ff-only
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --generate --run-id multi_passage_001 --sources .\data\synthetic\sources\paires_001.json --group 1 --type multi_passage --difficulty medium
```

Le run est un nouveau dossier `data/synthetic/multi_passage_001/`, distinct des deux fichiers d'aperçu dans
`preparations/`. Attendre son résumé et le candidat complet avant d'aborder une autre catégorie :

```powershell
Get-Content -Raw -Encoding UTF8 .\data\synthetic\multi_passage_001\candidates.jsonl
```

Si le résumé annonce un rejet ou une erreur, transmettre son motif et conserver tous les fichiers du run.
Un dossier existant ne peut pas être réutilisé, même si l'appel a échoué. Aucun candidat réel multi-passage
n'est encore rapporté au moment de cet incrément.

### Vérification et état de review

**109 tests réussis** ici sous Python 3.12.14 et Pydantic 2.14.0. Huit tests ajoutés, et le test de blocage
temporaire remplacé par un test CLI de génération simulée : un appel, deux sources, manifeste et sortie brute
conservés, attente humaine. Les nouveaux tests couvrent aussi préparation ambiguë/incomplète/dupliquée,
preuves manquantes ou non fournies, extrait dans le mauvais passage, doublon, verdict injecté, rejets tracés
sans relance et sortie interrompue. Les parcours simple/reformulation restent testés. Compilation et aide CLI
contrôlées. Aucune nouvelle inférence réelle, modification de dépendance ou lecture du Gold Set ici.

PR #103 toujours en brouillon ; Mahé et Remy restent demandés. L'essai Windows de cette génération et
la relecture sémantique sont attendus. Les catégories adversarial/hors_corpus restent à réaliser dans #94.
Pas de fusion, clôture, admission au lot figé ou temps réel déclaré ; estimation globale de 7 h inchangée.


## 15. #94 — Premier rejet réel : liste aplatie et prompt v2

### Résultat reçu et diagnostic

Le terminal transmis par Jibril montre le fast-forward `2cb10c1..53d4da2`, puis **109 tests Windows
réussis** (`Ran 109 tests in 0.641s`, `OK`). Le run `multi_passage_001` reçoit une réponse Qwen complète :
`done: true`, `done_reason: stop`, **1925 tokens HF / 1925 Ollama**, **438 tokens générés**.
Le comptage est comparé ; la limite de sortie de 512 n'est pas atteinte.

Le résumé annonce `rejet_automatique`, **0 candidat, 1 rejet**, motif « Extrait non retrouvé mot pour mot
dans le passage fourni ». Le fichier des candidats affiché est vide, conformément à ce rejet.
Jibril transmet ensuite le JSON brut extrait des traces. Le manifeste complet et les autres traces du run
ne sont pas transmis ; aucun état Git d'exécution détaillé n'est attribué au seul résumé.

Question réellement proposée : « Quelles sont les conditions d'organisation d'un congé sans solde et
pourquoi est-il préférable d'envisager un autre type de congé selon le Code du travail ? »

La comparaison avec les textes M2 figés établit :

| Preuve | Contrôle sur le corpus |
|---|---|
| `m2-article374529-0000` | Extrait exact et continu. |
| `m2-article374529-0002` | Six sauts de ligne de la liste remplacés par six espaces ; aucun autre écart sur cet extrait. |

Le second extrait devient identique au segment source si ses `\n` sont remplacés par des espaces.
C'est une altération de mise en forme du texte cité, pas un mot inventé dans cet extrait. Le validateur
strict a correctement appliqué le contrat de copie exacte. La proposition rejetée reste dans les traces,
sans réparation silencieuse, réadmission ou verdict humain attribué.

La lecture sémantique assistée relève aussi une nuance : la source dit « il peut être plus intéressant »
et lie le choix au projet du salarié ; la question et sa justification disent « préférable ». Le risque est
d'en faire une recommandation générale. La formulation juxtapose également deux demandes reliées par « et » ;
la cohérence d'une véritable combinaison reste à examiner. Ces remarques sont des points de relecture,
distincts du motif de rejet automatique, et ne constituent pas une évaluation du RAG.

### Ajustement limité au prompt

`prompts.py` passe uniquement le prompt multi à **`agent0-multi-passage-v2`** :

- demander un segment court sur une seule ligne par source, sans liste ni assemblage ;
- interdire explicitement le remplacement d'un saut de ligne par un espace ;
- conserver les nuances de possibilité, d'obligation et de comparaison ;
- faire dépendre une même décision ou explication des deux informations.

Le validateur est inchangé : la consigne de génération privilégie les segments courts sur une ligne,
mais un extrait multiligne réellement exact reste recevable structurellement. La fidélité ne se confond
pas avec la longueur ou le nombre de lignes. Le schéma, le client, le budget, les sources et les prompts
simple/reformulation sont inchangés. Aucun exemple de question réglementaire ni point attendu n'est ajouté
aux consignes ou aux tests.

Un test de régression technique accepte une liste copiée exactement, puis rejette sa version aplatie.
**110 tests réussis ici**, Python 3.12.14 / Pydantic 2.14.0 ; compilation contrôlée.
Le prompt simple conserve son empreinte initiale ; reconstruction du prompt multi v2 `medium` sur la même paire :
`90a34805e7843a170dcbaaefd8767e211129dcd423eb8f4d86f619a0c4bef526`.
Aucune nouvelle génération réelle n'est exécutée ici. Cet ajustement sera évalué au prochain run ;
il ne garantit pas à lui seul une copie parfaite ni une meilleure question.

### Nouvel essai après mise à jour

Exécuter une commande à la fois sur `feat/94-agent0-categories`, avec un dépôt propre et arrêt en cas d'échec :

```powershell
git status --short --branch
git pull --ff-only
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --generate --run-id multi_passage_002 --sources .\data\synthetic\sources\paires_001.json --group 1 --type multi_passage --difficulty medium
```

Le nouveau run utilise un dossier distinct ; `multi_passage_001` et les aperçus v1 restent conservés.
La commande refait le contrôle modèle/tokeniseur/budget sur le nouveau prompt avant l'unique appel.
Le budget HF changera avec ces consignes ; les 1925 tokens appartiennent au prompt v1 du run rejeté.
La réserve de sortie reste 512 ; pas de relance automatique. Après un résumé `candidat_prepare` :

```powershell
Get-Content -Raw -Encoding UTF8 .\data\synthetic\multi_passage_002\candidates.jsonl
```

En cas de rejet, lire la réponse brute de ce nouveau run dans ses traces. Attendre ce retour avant une
nouvelle modification ou les catégories suivantes. #103 reste en brouillon, Mahé/Remy demandés ; #94 partielle.
Aucun candidat multi-passage admis, gel, fusion, clôture, entraînement ou temps réel déclaré.
L'estimation globale #94 reste 7 h actives prévisionnelles.


## 16. #94 — Deuxième essai : citations exactes, question à mieux cadrer

### Résultat transmis et lecture assistée

Jibril transmet **110 tests Windows réussis** (`Ran 110 tests in 0.588s`, `OK`), puis le résumé de
`multi_passage_002` et le candidat complet `SYN_multi_passage_002_0001`.
Le run annonce un candidat, aucun rejet, fin `stop`, **2023 tokens HF / Ollama**, **452 tokens générés**.
Avec 512 de sortie réservés et 64 de marge, le budget représente **2599/8192**. Ces valeurs concernent
le deuxième essai ; elles ne sont pas reportées sur le prochain prompt. Le manifeste complet n'est pas transmis.

Les deux extraits reçus sont retrouvés exactement dans leurs passages M2. Le candidat conserve, dans cet
ordre, `m2-article374529-0002` et `m2-article374529-0000`, `automatic: passed`, `human: pending`,
`answerable_confirmed: null`, sans relecteur, note ou point attendu. La cible de difficulté reste `medium`.

Question reçue : « Quelles sont les conditions et obligations du salarié lorsqu'il sollicite un congé sans
solde, et comment cela se compare-t-il avec les congés réglementés par le Code du travail ? »

La lecture assistée relève deux ambiguïtés, distinctes des contrôles automatiques réussis :

- **Comparaison non cadrée.** Les sources mentionnent des congés réglementés sans détailler leurs conditions.
  La question ne fixe aucun critère précis de comparaison et risque de demander une information absente.
- **Contexte déplacé.** La preuve sur les clauses du contrat et la loyauté concerne l'exercice d'une autre
  activité pendant le congé ; la question place les obligations au moment où le salarié le sollicite.

La justification du générateur ne résout pas ces ambiguïtés : c'est une proposition, pas une validation.
L'avis assisté est de ne pas intégrer ce cas sous cette forme dans le lot figé. **Aucun verdict humain n'est
attribué** : le JSON demeure en attente et n'est pas réécrit. Les deux sources doivent être nécessaires et
suffisantes pour une demande précisément cadrée avant admission au benchmark.

### Consignes v3 et vérifications

`agent0-multi-passage-v3` ajoute trois consignes générales : chaque élément demandé doit être documenté,
une comparaison exige des éléments décrits sur le même critère, et une règle doit garder sa situation et son
moment d'application. Aucun exemple réglementaire ni point attendu n'est injecté dans le prompt.
Schéma, sources, validateur, client, budget, formats et prompts simple/reformulation restent inchangés.

**110 tests réussis ici** sous Python 3.12.14 / Pydantic 2.14.0 et compilation contrôlée. La suite vérifie les
parcours et garde-fous existants, pas la qualité sémantique du nouveau prompt. Aucun test ne prétend mesurer
le sens d'une question par la présence d'un mot dans les consignes. Aucun nouvel appel réel au modèle ici.
Sources complètes et ordre conservés ; empreinte du prompt simple initiale retrouvée. Prompt multi v3
`medium` reconstruit sur la paire :
`7e96af896875af56ba0ad213dac99dbd646928d28df4c6f8b7cd1f5970a84d7a`.

### Essai suivant

Sur `feat/94-agent0-categories`, exécuter une commande à la fois, avec dépôt propre et arrêt en cas d'échec :

```powershell
git status --short --branch
git pull --ff-only
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --generate --run-id multi_passage_003 --sources .\data\synthetic\sources\paires_001.json --group 1 --type multi_passage --difficulty medium
```

Le contrôle du budget est refait avant l'appel. Les deux précédents runs restent conservés. Après
`candidat_prepare`, transmettre aussi le candidat complet :

```powershell
Get-Content -Raw -Encoding UTF8 .\data\synthetic\multi_passage_003\candidates.jsonl
```

Ces essais successifs sur une même paire servent à la mise au point des consignes ; ils ne mesurent pas la
performance de la catégorie multi-passage. Le pilote #95 devra inclure d'autres sources et une relecture
indépendante. Attendre ce retour avant la suite ; #103 reste en brouillon avec Mahé/Remy demandés,
#94 partielle, estimation globale de 7 h inchangée. Aucun verdict humain, gel, fusion, clôture ou temps réel déclaré.


## 17. #94 — Troisième essai et diversification des sources

Jibril transmet **110 tests Windows réussis** (`Ran 110 tests in 0.582s`, `OK`), le résumé de
`multi_passage_003` et le candidat complet `SYN_multi_passage_003_0001` : fin `stop`, **2101 tokens
HF / Ollama**, **429 tokens générés**, un candidat et aucun rejet. Budget réservé : **2677/8192**.
Le manifeste complet n'est pas transmis ; la version du code d'inférence n'est pas déduite du seul résumé.

Les deux extraits sont exacts et identiques à ceux du run `002`. La question reprend la même demande :
conditions/obligations pour bénéficier d'un congé sans solde et comparaison avec des congés réglementés.
Le cadrage de la comparaison et le contexte des obligations restent ambigus. L'ajout des trois consignes
n'a donc pas corrigé ce problème sur cet exemple. Aucun taux général d'efficacité n'en est déduit.
Avis assisté : ne pas intégrer ce cas dans le lot figé sous cette forme. Le candidat reste inchangé,
`automatic: passed`, `human: pending`, réponse non confirmée et aucun point attendu.

Les questions `002` et `003` diffèrent après la normalisation existante : elles ne constituent pas un
doublon lexical exact, tout en étant très proches par le sens. C'est une limite observée du filtre actuel,
pas une preuve de diversité du benchmark. La relecture #95 devra aussi examiner ces quasi-doublons ;
aucun juge LLM ni déduplication par embeddings n'est ajouté dans cet incrément.

### Choix suivant : conserver v3 et changer les passages

Le code, le prompt v3, les tests et le budget restent inchangés. Une nouvelle sélection de **trois paires**
est reconstruite avec `count=3`, `seed=20261018`, selon le sélecteur #92 existant. Elle sera conservée
dans son intégralité, sans choisir les sources en fonction d'une réponse Qwen favorable :

| Groupe | Fiche | Identifiants dans l'ordre |
|---|---|---|
| 1 | Le congé sans solde | `m2-article374529-0003`, `m2-article374529-0004` |
| 2 | Attributions SSCT du CSE | `m2-article377050-0017`, `m2-article377050-0003` |
| 3 | Médaille d'honneur du travail | `m2-article374500-0003`, `m2-article374500-0000` |

Le premier groupe associe procédure/accord écrit et rémunération/CET ; il appartient à la même fiche
que les essais précédents, avec une autre paire. Les autres groupes diversifient les fiches. Ce tirage
ne garantit pas la complémentarité ou la suffisance d'une paire. Le nombre de groupes influence le tirage :
une graine identique avec un autre `count` ne garantit pas le même premier groupe. Les identifiants et
le manifeste sauvegardé constituent la référence exacte.

Première commande Windows, sans modèle ni matrice, avec un nouveau nom de fichier :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\corpus.py --pairs --count 3 --seed 20261018 --output .\data\synthetic\sources\paires_002.json
```

Transmettre le résumé pour vérifier les groupes avant les nouveaux appels. Ensuite, tester les groupes
dans l'ordre et conserver chaque résultat, y compris les rejets ; ne pas présenter cette série de mise au point
comme un score de benchmark. Le pilote #95 et les attentes humaines restent distincts.

Cette mise à jour est documentaire. Les **110 tests** sont ceux du code inchangé exécuté précédemment
ici et du nouveau retour Windows ; aucune nouvelle exécution de tests ou inférence n'est revendiquée.
Le tirage est reconstruit ici sur le corpus contrôlé, sans création du fichier Windows ni provenance Git
d'exécution de ce futur fichier attribuée. PR #103 en brouillon, Mahé/Remy demandés, #94 partielle,
estimation globale 7 h inchangée ; aucun verdict humain, gel, fusion, clôture ou temps réel déclaré.


## 18. #94 — Retour des trois paires du 19 octobre 2026

### Sélection et résultats transmis

Sur le Legion de Jibril, la branche passe de `824eaa1` à `1f7eeca` par avance rapide ; seuls deux
documents changent. Le résumé de `paires_002.json` annonce le commit complet
`1f7eeca8eea1014e959b7318079ae177d2980037`, une copie propre et Python 3.12.15.
Il retrouve exactement les trois groupes annoncés en section 17, 4240 passages et 261 fiches,
sans appel Ollama ni lecture de matrice. Les empreintes annoncées sont :

- entête : `586cf190293d206e4b9affd72cd37a23c367d34537b0c831305f66084084ee23` ;
- passages : `aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d`.

Les trois groupes sont ensuite testés dans l'ordre, avec le prompt v3 conservé. Jibril transmet
les résumés des runs, les candidats complets de `004` et `006`, puis la sortie brute de `005`.
Les manifestes et traces complets des générations ne sont pas transmis ; l'état Git propre de
la sélection ne prouve pas à lui seul celui de chaque inférence. Aucun nouveau test unitaire
n'est annoncé dans ce retour, la mise à jour récupérée étant documentaire.

| Run | Groupe | Entrée HF / Ollama | Sortie | Fin | Résultat automatique |
|---|---|---:|---:|---|---|
| `multi_passage_004` | 1, congé sans solde | 1833 / 1833 | 404 tokens | stop | 1 candidat, 0 rejet |
| `multi_passage_005` | 2, CSE | 2764 / 2764 | 373 tokens | stop | 0 candidat, 1 rejet |
| `multi_passage_006` | 3, médaille du travail | 2100 / 2100 | 385 tokens | stop | 1 candidat, 0 rejet |

Avec les réserves inchangées de 512 tokens de sortie et 64 de marge, les budgets calculés à partir
des entrées transmises sont respectivement 2409, 3340 et 2676 sur 8192. Ce calcul n'est pas un
nouveau comptage avec le tokeniseur. Ces trois essais de mise au point ne mesurent pas un taux
de qualité général ni les performances du RAG.

### Lecture assistée, sans verdict humain

- **004.** Les deux extraits sont exacts dans `m2-article374529-0003` et `m2-article374529-0004`.
  La demande associe procédure et rémunération, sans la comparaison trop ouverte des essais précédents.
  Points à relire : accord grammatical dans « comment est-elle financée », portée générale de
  « conditions pour bénéficier », distinction entre procédure et conditions légales, caractère conditionnel
  du CET. Les deux passages servent l'ensemble de la demande, mais celle-ci juxtapose deux sous-demandes
  simples ; la difficulté `medium` n'est pas mesurée. Le candidat reste inchangé et humain en attente.
- **005.** La première preuve est exacte dans `m2-article377050-0003`. La seconde est attribuée à
  `m2-article377050-0017`, mais son contenu provient de `m2-article377050-0003`. Dans ce texte réel,
  deux caractères de contrôle `U+0001` et un espace supplémentaire sont omis par la sortie Qwen.
  Le contrôle local confirme l'égalité seulement après retrait des deux caractères et réduction du double
  espace ; aucune de ces transformations n'est appliquée au validateur ni au corpus. Une simple correction
  d'identifiant laisserait les deux preuves dans le même passage. La première citation expose l'objectif
  des enquêtes, pas les droits demandés ; la seconde décrit un droit d'alerte, sans étayer les obligations
  demandées en santé publique/environnement. Le rejet automatique est conservé, sans réparation ni relance.
- **006.** Les deux extraits sont exacts dans `m2-article374500-0003` et `m2-article374500-0000`.
  Le second recopie intégralement le passage et conserve sa liste multiligne : la consigne d'extrait court
  sur une ligne n'est pas suivie, mais une liste exacte est compatible avec le validateur strict existant.
  La question demande les « conditions » sans limiter son périmètre, alors que la première preuve
  ne cite que le cas des salariés travaillant en France. Les durées d'ancienneté ne sont pas détaillées
  dans cette paire ; la demande et le dépôt d'un dossier ne décrivent pas toute la procédure d'attribution.
  La justification du générateur surestime donc la suffisance des preuves. Le candidat reste inchangé
  et humain en attente ; ce cas n'est pas admis au lot figé par cette lecture assistée.

### Bilan et suite

Cette série produit deux candidats à relire et un rejet tracé. La fidélité et l'attribution des extraits
sont contrôlées ; la suffisance, la portée de la question et la nécessité réelle des deux passages
restent des responsabilités de relecture indépendante en #95. Aucun candidat de cette série n'a
reçu de verdict humain ; les questions, sources et runs restent intacts.

Conserver le prompt v3 et terminer cette série sans essai supplémentaire choisi selon le résultat.
Le prochain incrément technique de #94 concerne l'aperçu `adversarial`, puis ses contrôles de sortie :
prémisse potentiellement fausse, correction proposée et preuve exacte, toujours à relire. La relecture
des candidats reste nécessaire avant admission au Challenge Set ; elle ne bloque pas la préparation
technique des autres catégories. `hors_corpus` reste également à réaliser.

Cette mise à jour ne modifie que la documentation et le journal IA du 19 octobre. Pas de nouvelle
inférence ici, de changement de prompt, de budget, de modèle, de validateur ou de corpus, ni de tests
relancés. Les 110 tests restent ceux des exécutions précédemment documentées. #103 reste en brouillon,
Mahé/Remy demandés, #94 partielle ; aucun gel, fusion, clôture ou temps réel déclaré.


## 19. #94 — Aperçu des cas pièges, sans génération

### Périmètre de cet incrément

Le schéma `synthetic-v1` prévoit déjà les champs `adversarial_premise` et `correction_proposed`.
Le nouvel aperçu les réutilise, sans changer le schéma ni le validateur. Le prompt
`agent0-adversarial-v1` demande une question contenant une prémisse potentiellement fausse,
sa correction proposée et une preuve exacte provenant d'un seul passage fourni intégralement.
Il n'injecte aucun exemple de question réglementaire ou point attendu.

Ce premier incrément vise les pièges dont la correction est proposée comme sourçable :
`answerable_proposed: true`, avec `out_of_corpus_reason: null`. Ce choix concerne la consigne
de cet aperçu, pas une restriction du schéma général. Les pièges sans correction étayée et les
candidats hors corpus restent hors de cette étape. Une absence d'information ne prouve pas
qu'une prémisse est fausse ; la relecture doit vérifier la question, la prémisse, la correction,
les conditions et exceptions, ainsi que la suffisance des extraits.

La préparation utilise le format existant `agent0-preparation-v1`, avec une seule clé `source`.
Les modes `--prepare-only` et `--prepare-qwen` sont disponibles. La commande
`--generate --type adversarial` est explicitement bloquée avant la lecture du corpus,
la création d'un run ou un appel réseau : les contrôles de sortie propres aux pièges restent
à implémenter. Cette protection concerne la CLI ; aucun nouveau garde-fou n'est ajouté à
l'orchestrateur Python interne dans cet incrément.

### Contrôles exécutés ici

**118 tests réussis** sous Python 3.12.14 et Pydantic 2.14.0 : les 110 précédents et 8 nouveaux.
Les nouveaux tests couvrent le passage intégral sans réécriture, les sources/paramètres invalides,
la reproductibilité de la préparation, l'aperçu sans réseau ni modèle, le budget simulé sans
génération, le blocage précoce de `--generate`, la protection d'une sortie existante et le refus
d'une paire pour cette catégorie à source unique. Les fixtures sont techniques, sans question
juridique ni appel au vrai modèle. Un ancien test de catégorie indisponible cible désormais
`hors_corpus`, qui reste indisponible dans la CLI.

Compilation et aide CLI contrôlées. Les trois objets prompts existants, simple/reformulation/
multi-passage, sont comparés avant/après sur les mêmes fixtures et sont identiques. Schéma,
client Qwen, orchestrateur, validateur, budget, dépendances et corpus ne changent pas.

La première source de `selection_001.json` est reconstruite depuis M2 avec `count=5`,
`seed=20261018` : `m2-article374529-0004`, 318 caractères conservés intégralement.
L'empreinte des passages reste `aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d`.
Prompt adversarial `medium` reconstruit :
`1b25e5b176af89409244ed6f01fbae133fc920418de38930e70171b3ba573a27`.
Ce contrôle ne lit pas le manifeste Windows complet et ne lui attribue aucune nouvelle provenance.
Aucun appel Ollama ni comptage du vrai tokeniseur ici ; aucun budget réel ou candidat adversarial obtenu.

### Vérification progressive sur Windows

Sur `feat/94-agent0-categories`, vérifier d'abord que le dépôt est propre avant l'avance rapide,
puis lancer les tests :

```powershell
git status --short --branch
git pull --ff-only
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
```

Si les 118 tests passent, préparer l'aperçu avec le manifeste à source unique existant :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --prepare-only --sources .\data\synthetic\sources\selection_001.json --group 1 --type adversarial --difficulty medium --output .\data\synthetic\preparations\adversarial_001.json
```

Résultat attendu : `statut: prompt_prepare`, `passage_id: m2-article374529-0004`,
`version_prompt: agent0-adversarial-v1`, `ollama_appele: false`, `budget_tokens_verifie: false`.
La difficulté `medium` est demandée, non mesurée. Une sortie existante est refusée sans écrasement.
Transmettre le résultat des tests et le résumé de préparation avant le contrôle du budget réel.
Ne pas utiliser `paires_002.json` pour ce premier aperçu à source unique.

La suite sera le contrôle du budget Windows, puis les règles de validation de sortie et l'activation
explicite de la génération adversarial. La relecture indépendante de #95 reste requise avant admission
des cas au Challenge Set. #94 reste partielle et #103 en brouillon ; aucun candidat, verdict humain,
gel, fusion, clôture ou temps réel déclaré pour ce nouvel incrément.


## 20. #94 — Budget Windows et activation des cas pièges sourçables

### Retours vérifiés

Jibril transmet **118 tests Windows réussis** (`Ran 118 tests in 1.433s`, `OK`), puis l'aperçu
et le contrôle du budget adversarial au commit `f9ee12acce5815830ae87519e818a6b5019bb611`,
copie propre, Python 3.12.15. Source `m2-article374529-0004`, prompt `agent0-adversarial-v1`.
L'empreinte de prompt de la section 19 est retrouvée. Les empreintes CRLF des quatre scripts
generate/prompts/schema/client concordent également avec le retour Windows.

Le contrôle Qwen annonce **1450 tokens HF + 512 de sortie + 64 de marge = 2026/8192**,
`generation_appelee: false`, sans comparaison HF/Ollama encore possible. Le texte raw reconstruit
ici retrouve exactement `d9df91b5040c028d34a8d5e6add187d6baee69273d104ec052f4bad788dc97f5`.
Ce contrôle d'empreinte ne constitue pas un recomptage avec le vrai tokeniseur dans cet environnement.

Ollama est maintenant rapporté en **0.40.6**, contre 0.40.5 lors des retours précédents ; ne pas
attribuer ce changement à une action ou une date non déclarée. Le modèle, son digest de référence,
la révision du tokeniseur, le gabarit `d5495a1e...`, les dépendances et le budget restent identiques.
Cette version de serveur sera conservée dans les traces du prochain run. Aucun effet sur la qualité
ou les performances n'est déduit de ce seul changement de version.

### Contrôles et limites de la génération

La CLI autorise désormais `--generate --type adversarial` avec un nouveau `run_id`. Le validateur
exige une préparation v1 avec une seule source identifiée et non vide, sans tableau `sources` ambigu.
Pour cet incrément, `answerable_proposed` doit être vrai. Le schéma existant impose alors une prémisse
et une correction proposées non vides, des preuves et aucun motif hors corpus. Le schéma général
continue de représenter d'autres situations ; elles ne sont pas générables dans cette étape.

Les contrôles communs restent appliqués : JSON strict, catégorie/difficulté, preuve appartenant au
passage fourni, extrait exact dans ce passage et déduplication normalisée. Le programme ne confirme
pas que la prémisse figure sémantiquement dans la question, qu'elle est fausse, que la correction
la réfute, ni que la preuve suffit. Ces points restent à relire humainement. La correction n'a pas
à être un extrait littéral ; ce sont les citations `evidence` qui doivent être exactes.

La prémisse et la correction sont conservées telles que reçues dans le candidat exploratoire,
sans réécriture ni points attendus confirmés. `automatic: passed` laisse `human: pending`,
`answerable_confirmed: null`, sans relecteur ou note. Ces champs d'annotation ne devront pas être
transmis au RAG évalué lors du futur benchmark. Aucun branchement au benchmark n'est ajouté ici.

Un seul appel, budget recompté avant génération, sortie brute conservée avant contrôle, puis candidat
ou rejet tracé. Une réponse tronquée reste une erreur technique prioritaire ; pas de réparation ou
relance automatique. Prompt, schéma, client, orchestrateur, modèle, budget, corpus et RAG inchangés.

### Vérifications et premier essai Windows

**126 tests réussis ici** sous Python 3.12.14 / Pydantic 2.14.0. Le test de blocage temporaire devient
un succès CLI simulé ; 8 tests sont ajoutés : textes et attente humaine conservés, champs invalides et
proposition non sourçable refusés, préparation ambiguë/invalide, preuves invalides, verdict injecté ou
paramètres différents, doublon, rejet avec brut conservé et sortie tronquée traitée comme erreur technique.
Toutes les fixtures sont techniques, sans nouvelle question juridique ou appel au vrai modèle.
Compilation contrôlée ; prompt et texte raw comparés avant/après : identiques à la préparation budgétée.

Sur `feat/94-agent0-categories`, vérifier le dépôt propre avant l'avance rapide, puis les tests :

```powershell
git status --short --branch
git pull --ff-only
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
```

Si les 126 tests passent, avec Ollama démarré, lancer un seul essai :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --generate --run-id adversarial_001 --sources .\data\synthetic\sources\selection_001.json --group 1 --type adversarial --difficulty medium
```

Si le résumé annonce `candidat_prepare`, transmettre le candidat complet :

```powershell
Get-Content -Raw -Encoding UTF8 .\data\synthetic\adversarial_001\candidates.jsonl
```

En cas de rejet ou d'erreur, transmettre d'abord le résumé ; conserver les traces avant de décider
d'un nouvel essai. Aucune question adversarial réelle n'a encore été rapportée. #94 reste partielle,
hors_corpus et relecture indépendante encore à réaliser ; PR #103 en brouillon avec Mahé/Remy demandés.
Pas de verdict humain, gel, fusion, clôture ou temps réel déclaré ; estimation initiale de 7 h inchangée.


## 21. #94 — Premier candidat adversarial et forme de la question

Jibril transmet **126 tests Windows réussis** (`Ran 126 tests in 0.678s`, `OK`), puis le résumé
et le candidat complet de `adversarial_001` : **1450 HF / 1450 Ollama**, 419 tokens générés,
fin `stop`, un candidat et aucun rejet. La comparaison des comptes est réussie. Le manifeste
complet n'est pas transmis ; le SHA et l'état Git de cette inférence ne sont pas déduits du résumé.

Le champ `question` contient cette affirmation, conservée mot pour mot :
« Pendant le congé sans solde, le salaire du salarié est maintenu grâce à un compte épargne-temps (CET). »
Il est identique à `adversarial_premise` et ne formule pas de demande explicite. Le contrôle existant
accepte structurellement un texte non vide ; il ne vérifie pas la forme interrogative.

La preuve et la correction correspondent exactement au texte complet de `m2-article374529-0004`.
La correction conserve donc le non-maintien de la rémunération et la possibilité conditionnelle
d'utiliser les droits acquis sur un CET, si le dispositif existe et si son accord le prévoit.
La lecture assistée relève un mélange entre maintien du salaire et financement conditionnel ;
elle n'attribue pas de verdict définitif de fausseté à la prémisse. Le candidat demeure inchangé,
`human: pending`, sans relecteur, note ou point attendu confirmé. Aucune admission au lot figé.

### Ajustement limité du prompt

`agent0-adversarial-v2` précise trois consignes générales : phrase interrogative explicite terminée
par un point d'interrogation, prémisse intégrée dans cette demande plutôt qu'affirmation seule,
correction réservée à `correction_proposed` et non dévoilée dans la question. Aucun exemple
juridique n'est ajouté et le candidat initial n'est pas réécrit. Le validateur reste inchangé :
une ponctuation ne constitue pas une validation sémantique automatique.

**126 tests réussis ici** sous Python 3.12.14 / Pydantic 2.14.0, sans nouveau test ni appel réel.
Compilation contrôlée ; les prompts simple, reformulation et multi-passage sont identiques avant/après
sur les mêmes fixtures. La source de 318 caractères est conservée ; le prompt v2 `medium`
reconstruit a pour empreinte `ddecefb77e5573621c0bc072628829a358715bf552cfca02b18f4f7e48133728`.
Ces vérifications ne démontrent pas que Qwen suivra mieux la nouvelle consigne.

### Nouvel essai distinct

Sur la même branche, vérifier le dépôt propre avant récupération et relancer les 126 tests :

```powershell
git status --short --branch
git pull --ff-only
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
```

Puis, avec Ollama démarré, utiliser un nouveau run :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --generate --run-id adversarial_002 --sources .\data\synthetic\sources\selection_001.json --group 1 --type adversarial --difficulty medium
```

Le budget est recompté avant l'appel ; les 1450 tokens concernent v1, pas ce nouveau prompt.
Les limites 8192/512/64 sont conservées. Si le résultat annonce `candidat_prepare` :

```powershell
Get-Content -Raw -Encoding UTF8 .\data\synthetic\adversarial_002\candidates.jsonl
```

Transmettre le résumé et le candidat, ou d'abord le motif du rejet. Conserver `adversarial_001`
pour comparaison. Ces essais constituent une mise au point, pas un benchmark de qualité.
Hors_corpus et relecture indépendante restent à réaliser ; #94 partielle, #103 en brouillon,
Mahé/Remy demandés. Aucun verdict humain, gel, fusion, clôture ou temps réel déclaré.


## 22. #94 — Question neutre et piège à prémisse fausse

Jibril transmet **126 tests Windows réussis** (`Ran 126 tests in 0.887s`, `OK`) et le candidat
complet de `adversarial_002` : **1509 HF / 1509 Ollama**, 255 tokens générés, fin `stop`, un candidat
et aucun rejet. Budget réservé v2 : 2085/8192. Manifeste complet non transmis ; aucune provenance
Git détaillée de l'inférence n'est déduite du seul résumé.

La question reçue est : « Pendant le congé sans solde, la rémunération du salarié est-elle maintenue ? »
La preuve est une copie exacte de la première phrase de `m2-article374529-0004` ; la correction
est une reformulation cohérente avec celle-ci selon la lecture assistée. La forme interrogative est
obtenue, mais la question ne présente pas le maintien de la rémunération comme acquis : elle demande
si c'est le cas. L'affirmation du champ `adversarial_premise` n'est donc pas présupposée par la question.
La justification générée qui dit que la question « affirme » cette prémisse n'est pas une validation.

Avis assisté : ce cas ressemble à une question fermée simple ; son adéquation à un piège avec prémisse
fausse n'est pas établie. Le candidat et sa catégorie restent inchangés, `human: pending`, sans verdict
humain, requalification automatique ou admission au lot figé. Les contrôles de copie/structure ne
permettent pas de détecter ce défaut de catégorie.

### Consigne générale v3 et diversification annoncée

`agent0-adversarial-v3` ajoute trois consignes : la question présente la prémisse comme acquise pour
que répondre correctement impose de la contester ; une interrogation neutre ne suffit pas ; le champ
`adversarial_premise` ne remplace pas cette présupposition dans la question. Aucun exemple juridique,
question de remplacement ou point attendu n'est ajouté. Le validateur reste inchangé.

**126 tests réussis ici**, Python 3.12.14 / Pydantic 2.14.0, sans nouveau test ajouté ni appel modèle.
Compilation et comparaison des prompts simple/reformulation/multi avant/après contrôlées : identiques.
Ces vérifications ne mesurent pas la qualité des questions ni l'efficacité de la consigne v3.

Pour ne pas continuer à ajuster la consigne sur le congé sans solde, les deux prochains essais utiliseront
les groupes 2 puis 3 du manifeste existant `selection_001.json`. Ils proviennent du tirage initial à
cinq fiches, graine 20261018 ; aucun nouveau tirage selon une réponse favorable. Garder v3 et conserver
les deux résultats, y compris les rejets, avant tout autre ajustement des consignes.

| Ordre | Groupe | Run prévu | Passage attendu | Fiche |
|---|---:|---|---|---|
| 1 | 2 | `adversarial_003` | `m2-article377050-0003` | Attributions SSCT du CSE |
| 2 | 3 | `adversarial_004` | `m2-article374500-0003` | Médaille d'honneur du travail |

Les deux sources sont reconstruites et conservées intégralement, respectivement 1895 et 1383 caractères.
Cela ne lit pas le manifeste Windows complet et ne démontre pas la faisabilité de chaque piège.
Les caractères de contrôle déjà repérés dans le passage CSE restent inchangés ; le corpus figé et
le contrôle d'extrait exact ne sont pas assouplis. Empreintes des prompts v3 `medium` reconstruits :

- groupe 2 : `bd19aa3825433add5520d143697340c6bd233cdb20bf2117abcacd2aefd6337d` ;
- groupe 3 : `e20021c3abfeb04ba4c196333fb0bc6b87450efba2575e254ee67e02ebddcdb8`.

Après récupération sur la même branche et réussite des 126 tests Windows, premier essai avec Ollama démarré :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --generate --run-id adversarial_003 --sources .\data\synthetic\sources\selection_001.json --group 2 --type adversarial --difficulty medium
```

Si le résultat annonce `candidat_prepare` :

```powershell
Get-Content -Raw -Encoding UTF8 .\data\synthetic\adversarial_003\candidates.jsonl
```

Transmettre résumé/candidat ou le motif du rejet avant de lancer le groupe 3. Le script recompte
le budget avant chaque appel ; les 1509 tokens concernent l'ancien prompt et l'ancienne source.
Limites, modèle, schéma, client, orchestrateur, corpus et RAG inchangés. Il s'agit d'une mise au point,
pas d'un score de benchmark. #94 partielle, hors_corpus et relecture indépendante encore à réaliser ;
#103 en brouillon, Mahé/Remy demandés, aucun gel, fusion, clôture ou temps réel déclaré.


## 23. #94 — Bilan des deux autres sources adversarial v3

Les groupes 2 et 3 de la sélection initiale sont exécutés dans l'ordre annoncé, avec v3 conservé.
Jibril transmet **126 tests Windows réussis** avant le groupe 2 (`0.888s`, `OK`), puis son candidat
complet. Pour le groupe 3, il transmet le résumé de rejet et ensuite la proposition JSON brute.
Les manifestes et traces complets ne sont pas transmis ; aucun état Git détaillé des inférences
n'est déduit de ces résumés. Aucun nouveau test n'est annoncé entre les deux générations.

| Run | Groupe | HF / Ollama | Sortie | Fin | Résultat automatique |
|---|---:|---:|---:|---|---|
| `adversarial_003` | 2, CSE | 2028 / 2028 | 372 tokens | stop | 1 candidat, 0 rejet |
| `adversarial_004` | 3, médaille | 1866 / 1866 | 499 tokens | stop | 0 candidat, 1 rejet |

Budgets réservés calculés sur ces entrées : 2604 et 2442 sur 8192, avec 512 de sortie et 64 de marge.
Les 499 tokens du second run restent sous la limite ; aucune troncature n'est signalée.
Les deux comptes HF/Ollama concordent.

### CSE : copie exacte et catégorisation à relire

Le candidat mélange l'enquête mentionnée pour certaines alertes avec l'examen conjoint évoqué pour
la santé publique/l'environnement. Sa preuve est exacte dans `m2-article377050-0003`, mais commence
par « Dans ce cas » : le contexte précédent doit être lu pour établir à quelle situation elle se rapporte.
La correction proposée reprend cette distinction selon la lecture assistée ; la justification du modèle
va plus loin en affirmant une absence d'obligation d'enquête, là où le passage décrit la formulation
du Code dans ce cas. Ne pas transformer cette justification en règle générale.

La question reste formulée comme une demande de confirmation d'une obligation. Son adéquation à
une présupposition trompeuse, plutôt qu'à une question fermée, reste à examiner. Candidat inchangé,
`human: pending`, sans verdict, points attendus confirmés ou admission au lot figé.

### Médaille : rejet de copie et correction incohérente

La preuve est attribuée au bon passage `m2-article374500-0003`, mais **trois sauts de ligne de la
liste sont remplacés par des espaces**, sans autre différence dans ce segment. Le contrôle local
retrouve exactement la sortie après ce seul aplatissement ; le texte original n'est pas normalisé
dans le validateur ni réparé dans le run. Le fichier de candidats vide et le rejet sont conservés.

Indépendamment du rejet de copie, la correction parle d'un employeur étranger puis exige qu'il soit
français. Elle présente aussi les cas listés comme exclusifs avec « seulement si », en omettant le
paragraphe suivant qui prévoit une attribution exceptionnelle hors des établissements énumérés,
sous conditions d'ancienneté et de contribution au bon renom de la France. La question et le champ
prémisse restent des interrogations de confirmation, avec une portée « sans aucune exception » peu
claire. Ces observations sont une lecture assistée, pas un verdict humain supplémentaire.

### Conclusion de mise au point et suite

Cette série v3 produit un candidat à relire et un rejet tracé. Elle montre que la copie exacte et la
présence de champs ne garantissent pas une vraie prémisse fausse, une correction cohérente ou la
conservation des exceptions. Aucun taux général de qualité ou de difficulté n'en est déduit.

Conserver v3, les deux résultats et les runs précédents ; pas de nouvel ajustement de consigne
ou de relance dans ce bilan. La relecture indépendante de #95 reste nécessaire avant admission.
La suite technique prévue en #94 est l'aperçu `hors_corpus` : absence seulement proposée par le
générateur, preuves positives vides, verdict non confirmé et vérification sur le corpus figé complet.
Ni la seule source fournie ni un échec de récupération ne devront confirmer cette absence.

Mise à jour documentaire uniquement : étude et journal IA. Pas de code, prompt, source, budget,
modèle, validateur ou RAG modifié ; aucun test unitaire ou appel réel relancé ici. Les 126 tests
restent ceux précédemment exécutés et ceux rapportés sur Windows. #103 reste en brouillon,
Mahé/Remy demandés, #94 partielle ; aucun verdict humain, gel, fusion, clôture ou temps réel déclaré.


## 24. #94 — Aperçu hors corpus, sans absence confirmée

### Contrat et portée

Le nouveau prompt `agent0-hors-corpus-v1` utilise un passage complet comme point de départ pour
proposer une question voisine insuffisamment traitée dans ce passage. Le modèle ne reçoit pas
le corpus entier : une réponse peut se trouver dans une autre fiche. Il doit proposer un motif
provisoire dans `out_of_corpus_reason`, sans prétendre avoir déjà recherché dans les autres textes.
Une réponse conditionnelle suffisamment sourcée ne constitue pas un cas hors corpus.

Le contrat existant est réutilisé : `answerable_proposed: false`, `evidence: []`, motif non vide,
`adversarial_premise: null` et `correction_proposed: null`. La source de départ demeure dans la
provenance ; elle n'est ni une preuve positive de réponse ni une preuve d'absence. Le classement
reste une proposition, sans `answerable_confirmed` ou verdict humain attribué par le générateur.

L'aperçu garde `agent0-preparation-v1` et une seule clé `source`. La CLI charge les métadonnées du
corpus pour contrôler l'intégrité de la sélection ; cela n'est pas une vérification sémantique de
l'absence dans tous les passages. Les cinq catégories sont désormais proposées par la CLI dans
les modes `--prepare-only` et `--prepare-qwen`. **La génération hors_corpus reste bloquée** avant
lecture du corpus, création de run ou appel réseau ; ses contrôles de sortie attendent l'étape suivante.
Cette protection concerne la CLI, pas un nouveau verrou de l'orchestrateur interne.

### Relecture prévue, alignée avec #94 et #95

Avant d'admettre un futur candidat hors corpus au lot figé, la relecture humaine devra :

1. Identifier le corpus complet utilisé, son empreinte et son périmètre ; conserver la question générée
   et sa provenance. Le passage de départ ne limite pas la vérification aux seules sources de génération.
2. Chercher dans l'ensemble des textes figés avec les termes utiles et leurs variantes, puis lire les
   fiches et passages pertinents pour le besoin précis, les conditions et les exceptions. Une recherche
   ou une récupération sert d'aide ; l'absence de résultat ne constitue pas un verdict d'absence.
3. Si une réponse suffisante, même conditionnelle, est trouvée, ne pas confirmer le type hors corpus.
   Conserver les références qui contredisent le classement proposé ; ne pas réécrire la question pour
   la faire sortir du corpus ou satisfaire un quota de catégorie.
4. Tracer qui a relu, quand, sur quelle empreinte, les termes/méthodes utilisés, les passages examinés,
   le motif de décision et les limites. Tant que le verdict est en attente, garder ces notes dans le
   support de relecture distinct : le contrat interdit une `review_note` dans un candidat `human: pending`.
   Les champs de verdict existants ne seront remplis qu'après une décision humaine effective.

Si la vérification reste incertaine ou dépasse l'enveloppe du pilote, conserver le cas non confirmé
et documenter cette limite, comme prévu en #95. Aucun juge Qwen, contrôle lexical seul ou consultation
du Web ne remplace la vérification de notre corpus figé. Cette procédure reste à relire avec le pilote ;
elle ne modifie pas le Gold Set, ses quotas ou le protocole officiel d'évaluation.

### Vérifications exécutées ici

**134 tests réussis**, Python 3.12.14 / Pydantic 2.14.0 : les 126 précédents et 8 nouveaux tests
de l'aperçu hors corpus, sur fixtures techniques. Passage complet, entrées invalides, reproductibilité
sans verdict, aperçu sans réseau, budget simulé sans génération, blocage CLI précoce, protection d'une
sortie existante et refus d'une paire sont contrôlés. Le test d'ancienne catégorie indisponible utilise
désormais une catégorie inconnue. Compilation et aide CLI vérifiées.

Les quatre prompts existants, simple/reformulation/multi/adversarial, sont identiques avant/après sur
les mêmes fixtures. Schéma, client, orchestrateur, validateur, corpus, budget, dépendances et RAG inchangés.
Ces tests ne démontrent aucune absence de réponse ni l'efficacité du prompt.

La source initiale est reconstruite avec le tirage déjà utilisé, `count=5`, graine `20261018` :
`m2-article374529-0004`, 318 caractères conservés intégralement. Corpus M2 inchangé, empreinte
`aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d`.
Prompt hors_corpus `medium` : `c7188861ca3a65932b61a712592a814fa89163b43d669a64e86873e8b54177e6`.
Ce contrôle ne lit pas le manifeste Windows complet et ne lui attribue pas de nouvelle provenance.
Aucun Ollama, vrai tokeniseur, budget réel ou question hors corpus obtenu ici.

### Première vérification Windows

Sur `feat/94-agent0-categories`, vérifier le dépôt propre avant l'avance rapide, puis les tests :

```powershell
git status --short --branch
git pull --ff-only
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
```

Si les 134 tests passent, préparer l'aperçu avec le manifeste à source unique existant :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --prepare-only --sources .\data\synthetic\sources\selection_001.json --group 1 --type hors_corpus --difficulty medium --output .\data\synthetic\preparations\hors_corpus_001.json
```

Attendu : `prompt_prepare`, source `m2-article374529-0004`, version `agent0-hors-corpus-v1`,
`ollama_appele: false`, `budget_tokens_verifie: false`. Une sortie existante est refusée sans écrasement.
Transmettre les tests et le résumé avant le budget réel. La génération et ses contrôles seront un
incrément ultérieur ; l'admission exige ensuite la relecture du corpus complet. #94 reste partielle,
#103 en brouillon, Mahé/Remy demandés ; aucun candidat hors corpus, verdict humain, gel, fusion,
clôture ou temps réel déclaré. Estimation initiale de 7 h inchangée.


## 25. #94 — Budget Windows vérifié et génération hors corpus activée

### Preuves transmises et contrôle du budget

Jibril transmet **134 tests Windows réussis** (`1.105s`, `OK`), puis l'aperçu et la préparation
Qwen au commit `65774deb68df98c50e7652ce24f5c803713ca6cc`, copie propre, Python 3.12.15.
Source `m2-article374529-0004`, prompt `agent0-hors-corpus-v1`, difficulté `medium`.

Le contrôle rapporte **1441 HF + 512 sortie + 64 marge = 2017/8192**, sans génération :
`generation_appelee: false`, `comptage_ollama_compare: false`. L'égalité HF/Ollama reste à
vérifier sur le premier run. Ollama 0.40.6, digest Qwen, gabarit, révision du tokeniseur et versions
des dépendances identiques aux références transmises précédemment.

Empreintes retrouvées ici sur la source M2 intégrale de 318 caractères, sans utiliser le vrai
tokeniseur ni appeler Ollama :

- prompt : `c7188861ca3a65932b61a712592a814fa89163b43d669a64e86873e8b54177e6` ;
- texte raw : `542f8728dab2b409ecd4290efbc5d311ac2ecec00457f02b6efddacf942f75f3`.

Les empreintes Windows des quatre scripts déclarés sont retrouvées avec leurs fins de ligne CRLF.
Cette reconstruction ne remplace pas la lecture du manifeste Windows complet et ne refait pas le
comptage de 1441 tokens. Le message PyTorch est cohérent avec l'usage du seul tokeniseur dans Python ;
l'inférence locale reste exécutée par Ollama.

### Contrôles et activation

Le validateur exige désormais aussi pour `hors_corpus` une préparation v1, une seule clé `source`,
un identifiant et un texte non vides ; une préparation ambiguë avec `sources` est refusée.
Ce contrôle partage la règle déjà appliquée à adversarial, dont le comportement est conservé.

Les règles croisées du schéma existant sont réutilisées : `answerable_proposed: false`,
`evidence: []`, motif non vide et champs adversarial nuls. Le motif, la question et la justification
reçus restent intacts. Le programme ne vérifie pas que le motif est juste ni qu'une réponse est absente
du passage de départ ou du corpus entier. La source reste dans `generation_source_ids` comme
provenance, sans devenir une preuve positive ou une preuve d'absence.

Le blocage temporaire de `--generate --type hors_corpus` est levé. Les contrôles communs demeurent :
JSON strict, catégorie/difficulté demandées, déduplication normalisée et un seul appel maximum.
Une sortie valide structurellement crée un candidat `automatic: passed`, `human: pending`,
`answerable_confirmed: null`, sans relecteur, note humaine ou points attendus.
La relecture complète décrite en section 24 reste nécessaire avant toute admission.

Brut, manifeste, candidat ou rejet et erreurs techniques sont tracés par l'orchestrateur existant.
Aucune réparation ou relance automatique. Les cinq catégories ont maintenant leurs trois modes CLI ;
cela ne constitue pas une validation sémantique ou l'achèvement du pilote.

### Vérifications exécutées ici et premier essai Windows

**142 tests réussis ici**, Python 3.12.14 / Pydantic 2.14.0 : 8 nouveaux tests de validation/traces ;
l'ancien test de blocage est remplacé par un succès CLI simulé avec un seul appel.
Textes/provenance et attente humaine, proposition répondable ou preuves positives interdites,
motif/champs adversarial incohérents, préparation ambiguë, verdict injecté, catégorie/difficulté,
doublon, rejet brut et sortie tronquée couverts sur des fixtures techniques.
Compilation et aide CLI contrôlées. Prompt, schéma, client, orchestrateur, corpus, budget, modèle,
dépendances et RAG inchangés ; aucun vrai tokeniseur, appel réel ou candidat hors corpus obtenu ici.

Sur le Legion, vérifier le dépôt propre puis récupérer et tester :

```powershell
git status --short --branch
git pull --ff-only
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
```

Si les 142 tests passent, un seul premier run :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --generate --run-id hors_corpus_001 --sources .\data\synthetic\sources\selection_001.json --group 1 --type hors_corpus --difficulty medium
Get-Content -Raw -Encoding UTF8 .\data\synthetic\hors_corpus_001\candidates.jsonl
```

Le budget est recompté avant l'appel ; un candidat ou un rejet sera conservé. Transmettre le résumé
et le candidat complet, ou la réponse brute en cas de rejet, avant une nouvelle génération.
Les préparations existantes ne sont pas écrasées et les autres runs restent conservés.

#94 reste partielle en attente des essais et relectures ; #103 en brouillon avec Mahé/Remy demandés.
Aucun verdict humain, admission au lot figé, gel, fusion, clôture ou temps réel déclaré ;
estimation initiale de 7 h inchangée.


## 26. #94 — Premier essai hors corpus : question couverte par sa source

### Résultat transmis

Jibril transmet **142 tests Windows réussis** (`0.985s`, `OK`), puis le résumé et le candidat
complet de `hors_corpus_001` : **1441 HF / 1441 Ollama**, 156 tokens générés, fin `stop`,
un candidat et aucun rejet automatique. Identifiant `SYN_hors_corpus_001_0001`,
source `m2-article374529-0004`, validation automatique passée et humaine `pending`.
Manifeste et traces complets non transmis : ne pas déduire le SHA/état Git, la version exacte du
prompt ou les autres détails de cette inférence du seul résumé et du budget précédent.

Question conservée : « Quelles conditions doivent être remplies pour que le salarié puisse utiliser
son compte épargne-temps (CET) pendant son congé sans solde ? »
Motif proposé : « L'information sur les conditions spécifiques n'est pas fournie dans ce passage. »

### Lecture assistée contre la source figée

Le passage M2 intégral donne déjà les conditions pertinentes : CET mis en place dans l'entreprise,
utilisation des droits acquis et possibilité de financement prévue par l'accord ayant instauré le CET.
La question ne précise pas d'autre information manquante. Le motif d'absence est ainsi contredit
par le passage de départ lui-même : `evidence: []` signifie seulement qu'aucune preuve positive
n'a été proposée dans ce candidat, pas que le corpus n'en contient pas.

Avis assisté : **ne pas admettre ce candidat en l'état au lot figé comme hors corpus**.
Le candidat reste intact et humain en attente ; aucune décision humaine, réécriture, réparation,
requalification ou admission automatique. Cette contre-preuve locale suffit à contester le classement
proposé ; elle n'est pas une vérification exhaustive d'absence dans le corpus complet.
Les futurs cas non contredits ainsi exigeront toujours la procédure de relecture de la section 24.

### Suite annoncée avant de nouveaux résultats

Conserver `agent0-hors-corpus-v1` : il demandait déjà d'éviter une question traitable par le passage,
même conditionnellement. Ce premier essai montre que la consigne n'a pas suffi sur cette source ;
il ne justifie ni un taux général de qualité ni un filtre lexical présenté comme vérification sémantique.
Aucun ajout d'exemple juridique ou juge LLM.

Pour compléter la mise au point avec des thèmes distincts, les deux groupes suivants du tirage initial
sont préannoncés, sans modifier le prompt :

| Ordre | Groupe | Source attendue | Run prévu |
|---|---:|---|---|
| 1 | 2 | `m2-article377050-0003` — CSE | `hors_corpus_002` |
| 2 | 3 | `m2-article374500-0003` — médaille du travail | `hors_corpus_003` |

Identifiants retrouvés par reconstruction du tirage `count=5`, graine `20261018`, sur le corpus
figé inchangé ; cela ne constitue pas une lecture du manifeste Windows complet.
Conserver tous les résultats, candidats et rejets, et lire chaque sortie avant la suivante.
Ces sources déjà utilisées pendant la mise au point ne constituent pas un pilote indépendant #95.

Prochain essai, groupe 2 :

```powershell
.\.venv-agent0\Scripts\python.exe .\scripts\synthetic\generate.py --generate --run-id hors_corpus_002 --sources .\data\synthetic\sources\selection_001.json --group 2 --type hors_corpus --difficulty medium
Get-Content -Raw -Encoding UTF8 .\data\synthetic\hors_corpus_002\candidates.jsonl
```

Budget recompté avant chaque appel, sans troncature ; les 1441 tokens concernent le premier passage.
Documentation et journal seulement : aucun code, prompt, validateur, corpus, modèle ou budget modifié,
aucun test unitaire ou appel réel relancé ici. #94 partielle, #103 en brouillon avec Mahé/Remy demandés ;
aucun verdict humain, admission, gel, fusion, clôture ou temps réel déclaré. Estimation 7 h inchangée.
