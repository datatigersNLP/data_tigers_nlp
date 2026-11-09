# Évaluer un lot synthétique avec la baseline RAG

Ticket #96. Préparation anticipée demandée par Jibril le 9 novembre 2026, pendant l'attente des relectures du lot d'adaptation. Cette contribution prépare le code et ses tests. Aucun nouveau pilote, verdict humain ou résultat réel du RAG n'est livré avec elle. Le ticket #96 reste ouvert jusqu'au lot indépendant relu et figé, à l'essai réel borné et à la relecture du code.

## Périmètre

Le lanceur réutilise les fonctions de `scripts/rag/rag.py` et `generation.py`, intégrées par #85 : E5 Python fp32 sur CPU, index M2 vérifié, cinq passages, construction du contexte `rag-b1-v1`, Qwen local et contrôle structurel des citations. Chaque appel reçoit le texte exact d'une question. La catégorie, les preuves attendues, les points attendus et les verdicts restent hors du retrieval et du prompt.

Cette baseline comprend la consigne d'abstention de #85 et n'ajoute aucun seuil de score. Le lanceur ne reproduit pas les états B0/B1/B2 de la mesure officielle et ne transpose pas le seuil q8 du site. Les seuils, questions humaines et fichiers de mesure de #52/#107 restent inchangés. Toute future variante du benchmark synthétique demandera une méthode distincte, écrite avant son exécution.

Le code ne génère pas de questions, n'entraîne pas de modèle, ne calcule pas les métriques de #97 et ne lance pas la boucle de #98. Les contrôles techniques ne certifient pas l'exactitude des réponses ni la suffisance des preuves.

## Préparer le lot, après relecture humaine

Un dossier hors Git contient deux fichiers :

- `questions.jsonl` : un `CasSynthetique` du contrat `synthetic-v1` par ligne, avec sa formulation intacte, ses sources et sa validation humaine déclarée.
- `manifest.json` : empreinte exacte du JSONL, empreintes de la matrice et des passages M2, effectif et déclarations de gel et de séparation.

Le pilote vise au plus 25 candidats. Il peut retenir moins de cas après relecture, sans forcer une catégorie ou un quota d'acceptation. Pour chaque cas évalué, `validation.automatic` doit valoir `passed` et `validation.human` doit valoir `accepted`. Le contrat exige alors un relecteur, une note, un verdict explicite de répondabilité et les points attendus pour les cas répondables. Les cas rejetés ou incertains sont conservés à part et n'entrent pas dans le lot évalué.

Gabarit documentaire incomplet, **volontairement refusé** par le lanceur :

```json
{
  "format": "agent0-challenge-v1",
  "set": "synthetic_challenge",
  "fige_le": "à renseigner après la relecture, date ISO avec fuseau",
  "pilote_independant": false,
  "note_separation": "à documenter avec les sources, générations et exclusions vérifiées",
  "nb_questions": 0,
  "sha256_questions": "à calculer sur les octets finaux de questions.jsonl",
  "sha256_index": "empreinte de index_m2.f32",
  "sha256_passages": "empreinte de passages_m2.json"
}
```

Le format d'entrée est proposé à la revue de #96. Le lanceur ne fournit aucune commande pour attribuer un verdict humain ou fabriquer un gel. La date de gel doit être passée avec fuseau explicite, l'effectif compris entre 1 et 25, les champs stricts et les empreintes cohérentes. Les doublons d'identifiant ou de question normalisée, les clés JSON dupliquées et les nombres non finis sont refusés. Les espaces et caractères des questions restent inchangés dans les appels.

Les identifiants des 15 candidats historiques de mise au point, inventoriés dans `docs/etudes/agent0_relecture/grille_relecture.json`, sont refusés même si une copie les marque acceptés. La grille historique vierge n'est pas un lot d'évaluation. Renommer des candidats ou mettre `pilote_independant` à `true` ne prouve pas l'indépendance : la revue humaine doit vérifier la séparation des fiches et la provenance des générations, puis figer le lot avant toute réponse du RAG. Les champs de validation restent des déclarations, sans authentification de l'identité humaine par le programme.

## Vérifier sans modèle

Depuis la racine du dépôt, avec Python 3.12 et les dépendances synthétiques disponibles :

```powershell
python -m scripts.synthetic.evaluate --lot C:\chemin\lot_independant --check-lot
```

Ce mode contrôle les déclarations, l'effectif, les candidats et l'empreinte du JSONL. Il ne charge ni E5 ni Qwen, n'appelle pas Ollama et ne crée aucun dossier de résultats. Sa sortie n'est pas une validation sémantique. La concordance du corpus et l'ancrage des extraits sont contrôlés au début de l'exécution, avant tout chargement de modèle ou appel Ollama.

## Exécuter après validation du lot

Préparer un environnement dédié avec les dépendances de `scripts/synthetic/requirements.txt` et de `scripts/rag/requirements.txt`, ainsi que les caches E5/tokeniseur et Ollama. Conserver l'environnement des mesures officielles avant/après. Le modèle Qwen doit déjà être importé dans Ollama.

```powershell
python -m scripts.synthetic.evaluate --lot C:\chemin\lot_independant --run-id pilote_001
```

Par défaut, le modèle et son digest sont ceux de #31. Pour servir un autre modèle Qwen compatible avec les helpers de #85, donner les deux paramètres ensemble :

```powershell
python -m scripts.synthetic.evaluate --lot C:\chemin\lot_independant --run-id pilote_autre_modele --modele NOM_OLLAMA --digest SHA256_COMPLET
```

Le serveur, le digest, les métadonnées GGUF et le gabarit sont vérifiés par les helpers de génération existants. La version réellement retournée par Ollama est enregistrée, sans attribuer à cette évaluation exploratoire la conformité au protocole officiel. Le CLI humain de calibration et `mesure.py` ne sont jamais invoqués.

Le dossier `data/synthetic/results/<run_id>/` est réservé avant tout modèle ou API. Un identifiant existant est refusé, y compris pour un run partiel. Il n'y a ni écrasement ni nouvel essai automatique d'une question. Le chargement du lot précède toute réservation et tout modèle. L'index est contrôlé avant E5 et Ollama. L'index et E5 sont chargés une fois pour le run, tandis que le Top 5 est calculé pour chaque question et les contrôles de génération restent ceux des helpers de #85.

Les fichiers conservés sont :

| Fichier | Contenu |
|---|---|
| `jeu_manifest.json` | Copie des octets du manifeste d'entrée |
| `questions.jsonl` | Copie exacte du JSONL accepté, conservée pour l'analyse séparée |
| `manifest.json` | Identité exploratoire du run, commit/état Git, empreintes du code LF et des entrées, version Python |
| `chaine.json` | Index, E5/révision, options de génération, modèle/digest/version/gabarit Ollama, versions installées |
| `results.jsonl` | Identifiant et texte de question, cinq passages récupérés avec rangs/scores/textes, contexte et table `[Pk]`, réponse brute, citations, diagnostics et mesures retournés par le helper |
| `events.jsonl` | Début et fin de chaque question, utile en cas d'interruption |
| `summary.json` | État final ou partiel, nombre de résultats, erreurs techniques, durée et empreintes des fichiers présents |

Les erreurs de préparation restent dans le résumé avec les snapshots disponibles. Une erreur de récupération, de budget ou d'API est technique, jamais une abstention ni un verdict juridique. Une génération incomplète conserve son statut technique, sa réponse brute et ses diagnostics. Une interruption laisse un résumé `interrompu` et les traces déjà écrites. `statut: termine` signifie que le traitement du lot s'est achevé, même si certaines questions ont des erreurs techniques ; leur nombre est explicite. Un fichier empêché par une erreur d'entrée/sortie ne peut pas être garanti.

## Tests et suite

```powershell
python -m unittest discover -s scripts/synthetic -p "test_*.py" -v
```

Les tests du lanceur utilisent des fixtures techniques et des ressources simulées. Les mentions d'acceptation et de relecteurs dans ces fixtures ne correspondent à aucune décision humaine réelle. Les vrais helpers de préparation du contexte sont exercés, mais aucun modèle ne tourne et aucune question juridique n'est créée.

La préparation anticipée n'atteste pas une reprise complète du périmètre reporté au 30 octobre. Le point suivant reste la constitution indépendante du pilote et sa relecture effective. L'essai réel borné de #96, sa revue indépendante puis l'analyse de #97 restent à réaliser. Les exécutions officielles et l'adaptation conservent la priorité.
