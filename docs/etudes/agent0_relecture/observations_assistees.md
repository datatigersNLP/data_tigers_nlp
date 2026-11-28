# Observations assistées — ne valent pas décisions humaines

Lire d'abord [les questions et sources](questions_et_sources.md), puis comparer sa propre lecture à ces remarques. Elles reprennent le travail assisté de mise au point et peuvent être contestées.
Les recommandations antérieures de non-admission ne remplissent aucun verdict de la grille. Aucun point attendu n'est prérempli.

## simple_001

Vérifier la suffisance de l'extrait et la portée de la question. La lecture assistée antérieure était favorable, sans verdict humain.

[Fiche neutre](questions_et_sources.md#simple_001) — [Étude, section 12](../agent0_light.md).

## reformulation_001

Vérifier la proximité avec simple_001, la nuance CET et si la reformulation apporte une variation utile. Ne pas compter cette paire comme deux observations indépendantes d'un thème.

[Fiche neutre](questions_et_sources.md#reformulation_001) — [Étude, section 12](../agent0_light.md).

## multi_passage_002

Comparaison trop générale avec des congés seulement mentionnés ; obligations liées à l'exercice d'une autre activité déplacées vers la demande. Extraits originaux désormais reçus et affichés dans la fiche ; nécessité et suffisance à examiner humainement.

[Fiche neutre](questions_et_sources.md#multi_passage_002) — [Étude, section 16](../agent0_light.md).

## multi_passage_003

Formulation exacte retrouvée dans l'archive et affichée dans la fiche : même comparaison générale et ambiguïté de contexte. Contrôler le quasi-doublon sémantique avec 002 à partir des deux originaux.

[Fiche neutre](questions_et_sources.md#multi_passage_003) — [Étude, section 17](../agent0_light.md).

## multi_passage_004

Portée des conditions, formulation « est-elle », financement CET conditionnel et nécessité réelle de combiner deux sources à examiner ; distinguer combinaison nécessaire et juxtaposition.

[Fiche neutre](questions_et_sources.md#multi_passage_004) — [Étude, section 18](../agent0_light.md).

## multi_passage_006

Question générale sur les conditions alors que le premier extrait n'en couvre qu'un cas ; ancienneté et procédure peu détaillées. Examiner les sources complètes et la suffisance de la paire.

[Fiche neutre](questions_et_sources.md#multi_passage_006) — [Étude, section 18](../agent0_light.md).

## adversarial_001

Le champ question est une affirmation. Examiner maintien du salaire / financement conditionnel du CET, existence d'une demande et pertinence du type adversarial.

[Fiche neutre](questions_et_sources.md#adversarial_001) — [Étude, section 21](../agent0_light.md).

## adversarial_002

Interrogation neutre plutôt qu'une fausse prémisse présentée comme acquise ; le champ premise seul ne suffit pas. Ressemblance avec le cas simple à examiner.

[Fiche neutre](questions_et_sources.md#adversarial_002) — [Étude, section 22](../agent0_light.md).

## adversarial_003

Distinguer enquête et examen conjoint en lisant le contexte de « Dans ce cas ». Examiner la présupposition dans la question ; ne pas généraliser l'absence de référence à une enquête en absence de toute obligation.

[Fiche neutre](questions_et_sources.md#adversarial_003) — [Étude, section 23](../agent0_light.md).

## hors_corpus_001

Les conditions CET sont déjà dans la source. Une absence de preuve positive proposée n'est pas une absence documentaire.

[Fiche neutre](questions_et_sources.md#hors_corpus_001) — [Étude, section 26](../agent0_light.md).

## hors_corpus_002

Motifs d'alerte déjà énumérés dans la source ; la formulation ne délimite pas d'autre information manquante.

[Fiche neutre](questions_et_sources.md#hors_corpus_002) — [Étude, section 27](../agent0_light.md).

## hors_corpus_003

Le passage décrit les situations à l'étranger et l'attribution exceptionnelle. Distinguer travail et résidence ; ne pas déduire l'absence de toutes les conditions de l'absence de seuils détaillés.

[Fiche neutre](questions_et_sources.md#hors_corpus_003) — [Étude, section 27](../agent0_light.md).

## hors_corpus_004

Motif contredit par les conditions présentes ; question proche de 001. La justification originale reconnaît l'accord puis prétend manquer de conditions exactes.

[Fiche neutre](questions_et_sources.md#hors_corpus_004) — [Étude, section 28](../agent0_light.md).

## hors_corpus_005

« Conséquences légales » ambigu : examen conjoint déjà évoqué. Ne pas réécrire la question pour y faire demander des sanctions ; absence dans le corpus complet non vérifiée.

[Fiche neutre](questions_et_sources.md#hors_corpus_005) — [Étude, section 28](../agent0_light.md).

## hors_corpus_006

Le paragraphe « À titre exceptionnel » décrit précisément le cas demandé ; motif contredit par la source.

[Fiche neutre](questions_et_sources.md#hors_corpus_006) — [Étude, section 28](../agent0_light.md).

## Rejets automatiques à conserver séparément

Ces trois runs ne fournissent aucun candidat à accepter dans la grille. Les fichiers d'origine sont reçus et les trois motifs de rejet ont été reproduits avec les validateurs versionnés. Les remarques de sens restent assistées ; aucune réparation ou réadmission n'est réalisée.

### multi_passage_001

Extrait non exact : six sauts de ligne remplacés par des espaces dans une liste. Rejet automatique conservé.

Sources rapportées : `m2-article374529-0002`, `m2-article374529-0000`.

### multi_passage_005

Preuve attribuée à un autre passage, avec deux caractères U+0001 et un espace omis. Réattribuer ne rétablirait pas une preuve de chaque source. Rejet automatique conservé.

Sources rapportées : `m2-article377050-0017`, `m2-article377050-0003`.

### adversarial_004

Extrait non exact : trois sauts de ligne remplacés par des espaces. Correction proposée aussi contradictoire sur l'employeur et omettant l'exception. Rejet automatique conservé.

Sources rapportées : `m2-article374500-0003`.

## Vigilances communes

- `automatic: passed` ne confirme pas la catégorie ou la suffisance documentaire.
- Examiner les ressemblances sémantiques entre catégories, notamment simple/adversarial neutre/hors corpus sur la rémunération.
- Pour hors corpus, une contre-preuve peut invalider le motif proposé ; l'absence de résultat de recherche ne prouve pas une absence de réponse.
- La relecture par une autre personne ne transforme pas les cas de mise au point en test indépendant.
- Les nombres visés en #95 sont des objectifs de génération, pas des quotas d'acceptation. Aucun hors corpus n'est confirmé dans les retours disponibles.

