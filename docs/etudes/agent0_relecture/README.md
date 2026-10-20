# Agent0 Light — support de préparation à la relecture (#95)

Préparé le 20 octobre 2026 depuis le commit `36bb4e05094dbc68d1975f1d8ea01eac50de166b` de #103, encore en brouillon. Préparation documentaire uniquement ; le pilote de 25 candidats n'est ni constitué ni figé.

## Parcours de lecture

1. Ouvrir [les questions et sources](questions_et_sources.md), puis vérifier les fichiers originaux.
2. Renseigner une première lecture dans [la grille distincte](grille_relecture.json) : personne, date, décision et justification. Toutes les décisions sont vierges.
3. Consulter ensuite [les observations assistées](observations_assistees.md), relever accords/désaccords et compléter les recherches nécessaires.
4. Vérifier la provenance et la cohérence du lot avant admission ; une relecture distincte du code reste nécessaire avant fusion.

## Inventaire rapporté

| Catégorie | Candidats | Rejets automatiques |
|---|---:|---:|
| `simple` | 1 | 0 |
| `reformulation` | 1 | 0 |
| `multi_passage` | 4 | 2 |
| `adversarial` | 3 | 1 |
| `hors_corpus` | 6 | 0 |
| Total | 15 | 3 |

Les 18 runs sont rapportés dans les retours utilisateur et l'étude. Les 15 candidats ont un statut humain `pending` rapporté ; aucun verdict ni point attendu n'est attribué ici. Aucun hors corpus n'est confirmé.
14 formulations sont disponibles ; celle de `multi_passage_003` manque. Les extraits proposés de `multi_passage_002` et `003` restent à recueillir. Les champs non affichés et les octets originaux ne sont pas reconstitués.
Des objets de candidats ont été copiés dans la conversation, mais les fichiers de run complets n'ont pas été reçus. Pour le cas simple, des blocs de provenance partiels sont documentés en étude §12 ; ils ne remplacent pas le manifeste et les traces complets.

| Run | Sortie rapportée | Source documentaire |
|---|---|---|
| `simple_001` | 1 candidat, aucun rejet | [Étude §12](../agent0_light.md) |
| `reformulation_001` | 1 candidat, aucun rejet | [Étude §12](../agent0_light.md) |
| `multi_passage_002` | 1 candidat, aucun rejet | [Étude §16](../agent0_light.md) |
| `multi_passage_003` | 1 candidat, aucun rejet | [Étude §17](../agent0_light.md) |
| `multi_passage_004` | 1 candidat, aucun rejet | [Étude §18](../agent0_light.md) |
| `multi_passage_006` | 1 candidat, aucun rejet | [Étude §18](../agent0_light.md) |
| `adversarial_001` | 1 candidat, aucun rejet | [Étude §21](../agent0_light.md) |
| `adversarial_002` | 1 candidat, aucun rejet | [Étude §22](../agent0_light.md) |
| `adversarial_003` | 1 candidat, aucun rejet | [Étude §23](../agent0_light.md) |
| `hors_corpus_001` | 1 candidat, aucun rejet | [Étude §26](../agent0_light.md) |
| `hors_corpus_002` | 1 candidat, aucun rejet | [Étude §27](../agent0_light.md) |
| `hors_corpus_003` | 1 candidat, aucun rejet | [Étude §27](../agent0_light.md) |
| `hors_corpus_004` | 1 candidat, aucun rejet | [Étude §28](../agent0_light.md) |
| `hors_corpus_005` | 1 candidat, aucun rejet | [Étude §28](../agent0_light.md) |
| `hors_corpus_006` | 1 candidat, aucun rejet | [Étude §28](../agent0_light.md) |
| `multi_passage_001` | aucun candidat, 1 rejet | [Étude §15](../agent0_light.md) |
| `multi_passage_005` | aucun candidat, 1 rejet | [Étude §18](../agent0_light.md) |
| `adversarial_004` | aucun candidat, 1 rejet | [Étude §23](../agent0_light.md) |

## Référence et portée

- Corpus M2 : 4240 passages, 261 fiches.
- SHA-256 entête : `586cf190293d206e4b9affd72cd37a23c367d34537b0c831305f66084084ee23`.
- SHA-256 passages : `aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d`.
- [sources_m2.json](sources_m2.json) contient huit passages complets vérifiés contre les blobs versionnés. Ce n'est pas le corpus complet.
- Les essais ont servi à la mise au point : ils ne sont pas un pilote indépendant ou un échantillon représentatif.
- Les questions sont des copies de formulations rapportées, pas des fichiers originaux authentifiés. Aucune empreinte d'un candidat ou run manquant n'est inventée.

## Comment décider

Relire la question originale, sa catégorie proposée et les passages complets. Vérifier suffisance, conditions, exceptions et doublons sémantiques ; la difficulté reste une cible.
Pour multi_passage, les sources doivent être toutes deux nécessaires et suffisantes. Pour adversarial, vérifier la prémisse dans la question et la correction. Pour hors_corpus, vérifier le corpus figé complet et tracer méthodes, termes/variantes, passages examinés et limites.
La grille de travail permet `accepted`, `rejected` ou `uncertain` après une relecture effective. `uncertain` est une notion de ce support, distincte du contrat : le candidat reste `pending`. Un cas mal classé doit être rejeté, sans changer sa question ou son type pour sauver le cas.
Avant toute transcription vers une copie revue, respecter `ValidationCas` : en attente, aucun verdict/relecteur/note/point attendu dans `validation`. Une décision humaine effective doit avoir un nom et une note ; une acceptation exige un verdict de répondabilité et des points attendus uniquement pour une réponse possible. Conserver la question, l'original et la trace de toute édition.
Les notes et recherches provisoires restent dans ce support distinct. Aucun outil d'application automatique n'est fourni. Un contrôle de schéma seul ne valide pas une décision.
Les objectifs de #95 ne sont pas des quotas d'acceptation. Les cas non confirmés restent à part et ne servent pas à calculer la qualité du lot. Aucun travail de relecture n'est attribué à Mahé ou Remy sans intervention réelle.

## Pièces à recueillir sur le Legion

Pour chacun des 18 runs : `manifest.json`, `summary.json`, `candidates.jsonl`, `rejected.jsonl`, `traces.jsonl`, y compris les fichiers vides. Ajouter les trois sélections ci-dessous.
Ces originaux permettront de comparer les questions/champs, empreintes, versions, paramètres et sources de génération. Un manifeste ne prouve pas une absence documentaire.
À la racine du dépôt Windows, ce bloc crée une archive à côté du dépôt. Il vérifie les fichiers demandés et refuse d'écraser une archive existante. Les runs sont seulement lus ; aucun modèle n'est appelé et les traces restent hors Git.

```powershell
$runsAgent0 = @(
    'simple_001',
    'reformulation_001',
    'multi_passage_002',
    'multi_passage_003',
    'multi_passage_004',
    'multi_passage_006',
    'adversarial_001',
    'adversarial_002',
    'adversarial_003',
    'hors_corpus_001',
    'hors_corpus_002',
    'hors_corpus_003',
    'hors_corpus_004',
    'hors_corpus_005',
    'hors_corpus_006',
    'multi_passage_001',
    'multi_passage_005',
    'adversarial_004'
)
$fichiersAgent0 = @('manifest.json', 'summary.json', 'candidates.jsonl', 'rejected.jsonl', 'traces.jsonl')
$itemsAgent0 = @()
foreach ($runAgent0 in $runsAgent0) {
    $dossierAgent0 = Join-Path '.\data\synthetic' $runAgent0
    foreach ($nomAgent0 in $fichiersAgent0) {
        $fichierAgent0 = Join-Path $dossierAgent0 $nomAgent0
        if (-not (Test-Path -LiteralPath $fichierAgent0 -PathType Leaf)) { throw "Fichier manquant : $fichierAgent0" }
    }
    $itemsAgent0 += $dossierAgent0
}
$sourcesAgent0 = @(
    '.\data\synthetic\sources\selection_001.json',
    '.\data\synthetic\sources\paires_001.json',
    '.\data\synthetic\sources\paires_002.json'
)
foreach ($sourceAgent0 in $sourcesAgent0) {
    if (-not (Test-Path -LiteralPath $sourceAgent0 -PathType Leaf)) { throw "Fichier manquant : $sourceAgent0" }
}
$itemsAgent0 += $sourcesAgent0
$archiveAgent0 = Join-Path (Split-Path -Parent (Get-Location).Path) 'agent0_relecture_20261020.zip'
if (Test-Path -LiteralPath $archiveAgent0) { throw "Archive existante : $archiveAgent0" }
Compress-Archive -LiteralPath $itemsAgent0 -DestinationPath $archiveAgent0 -ErrorAction Stop
Get-FileHash -LiteralPath $archiveAgent0 -Algorithm SHA256
```

Archive attendue : `C:\Users\jibri\Documents\GitHub\agent0_relecture_20261020.zip` si le dépôt est à l'emplacement des retours. Le bloc est une procédure PowerShell ; il n'a pas été exécuté sur le Legion ni dans PowerShell ici.
Transmettre l'archive hors Git pour compléter la provenance. Les empreintes de ses fichiers seront calculées depuis les octets reçus, sans reconstruction depuis les résumés.

## État de préparation

Le support permet une prélecture. La relecture finale et l'admission attendent les originaux, la lecture humaine et les recherches nécessaires. #94 et #95 restent partielles ; #103 reste en brouillon.
Aucun candidat, rejet ou verdict d'origine modifié, aucune génération, évaluation du RAG, fusion ou clôture. Le lot et son manifeste devront être figés avant les réponses du RAG.
Ce dossier de travail n'est pas placé dans `evaluation/synthetic/` et ne remplace pas le Gold Set humain. Estimation initiale #95 : 4 h prévisionnelles inchangées ; aucun temps réel déclaré.

