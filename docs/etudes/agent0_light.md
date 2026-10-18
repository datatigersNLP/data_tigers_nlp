# Agent0 Light : contrat des cas synthétiques (#91)

## 1. Périmètre et état

Responsable : Jibril BENSALEM. Relecteurs désignés : Mahé BEGNIS (`mahebegnis`) et Remy RAYANE (`Remynou`).
État au 18 octobre 2026 : schéma, contrôles de cohérence et tests préparés ; relecture des deux membres et
exécution Windows encore attendues. La PR RAG #85 n'est pas modifiée.

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
| Sources #92/#93 | Empreinte M2, identifiants réellement existants, extraits exacts | À implémenter |
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

```powershell
uv venv --python 3.12 .venv-agent0
uv pip sync --python .venv-agent0\Scripts\python.exe scripts/synthetic/requirements-lock.txt
.\.venv-agent0\Scripts\python.exe -m unittest discover -s scripts/synthetic -p "test_*.py" -v
```

Si cet environnement dédié existe déjà et contient un autre travail, vérifier ses paquets avant de le synchroniser.
`uv pip sync` remplace les paquets de l'environnement indiqué. Aucun poids de modèle n'est nécessaire ; seuls
Pydantic et ses dépendances seront installés. Les verrous et l'environnement des autres étapes ne sont pas changés.

Pour afficher le schéma que recevra plus tard Ollama, sans appel de modèle :

```powershell
.\.venv-agent0\Scripts\python.exe -c "import json; from scripts.synthetic.schema import schema_generation; print(json.dumps(schema_generation(), ensure_ascii=False, indent=2))"
```

Vérification effectuée dans l'environnement de développement : **27 tests réussis**, Python 3.12.14 et Pydantic 2.14.0.
Compilation et export du schéma également contrôlés. Les dépendances
directes et transitives effectivement présentes sont listées dans `scripts/synthetic/requirements-lock.txt` ; ce
fichier a été relevé depuis les métadonnées de l'environnement, pas produit par un résolveur sur Windows.
Les tests utilisent uniquement des fixtures techniques, sans questions réglementaires ni données du Gold Set.
Aucun Qwen, E5, Ollama ou corpus réel n'est appelé. La sortie Windows reste à transmettre avant l'étape suivante.

## 8. Références et suite

- [#91 : contrat](https://github.com/datatigersNLP/data_tigers_nlp/issues/91), puis [#92 : sources](https://github.com/datatigersNLP/data_tigers_nlp/issues/92).
- [Pydantic : mode strict](https://docs.pydantic.dev/latest/concepts/strict_mode/), [schéma JSON](https://docs.pydantic.dev/latest/concepts/json_schema/) et [validateurs](https://docs.pydantic.dev/latest/concepts/validators/), consultés le 18 octobre 2026.
- [Note d'assistance IA de cette étape](../journal/2026-10-18_agent0_light_91.md).

La prochaine modification se limitera à #92, après le retour des tests Windows. Ni le générateur #93, ni le
benchmark #96/#97, ni la boucle #98 ne sont implémentés ici. La charge réelle de #91 n'est pas déduite de la
durée de cette conversation ; elle sera déclarée par les contributeurs à la clôture.
