# Questions et sources — préparation de relecture du 20 octobre 2026

Ce support reproduit les questions rapportées et les champs proposés disponibles. Ce ne sont pas les fichiers JSONL originaux.
Les 15 entrées sont des candidats de mise au point. Les décisions restent vierges dans [la grille](grille_relecture.json).
Lire les questions et sources avant les [observations assistées](observations_assistees.md). Consulter les fichiers originaux et leurs justifications complètes avant de décider.
Une formulation exacte manque pour `multi_passage_003` ; ne pas la reconstruire depuis le résumé.
Le JSON [sources_m2.json](sources_m2.json) conserve les valeurs des huit passages, dont les sauts de ligne et les caractères U+0001.

## Index des candidats

| Run | Catégorie proposée | Fiche |
|---|---|---|
| `simple_001` | `simple` | [Lire](#simple_001) |
| `reformulation_001` | `reformulation` | [Lire](#reformulation_001) |
| `multi_passage_002` | `multi_passage` | [Lire](#multi_passage_002) |
| `multi_passage_003` | `multi_passage` | [Lire](#multi_passage_003) |
| `multi_passage_004` | `multi_passage` | [Lire](#multi_passage_004) |
| `multi_passage_006` | `multi_passage` | [Lire](#multi_passage_006) |
| `adversarial_001` | `adversarial` | [Lire](#adversarial_001) |
| `adversarial_002` | `adversarial` | [Lire](#adversarial_002) |
| `adversarial_003` | `adversarial` | [Lire](#adversarial_003) |
| `hors_corpus_001` | `hors_corpus` | [Lire](#hors_corpus_001) |
| `hors_corpus_002` | `hors_corpus` | [Lire](#hors_corpus_002) |
| `hors_corpus_003` | `hors_corpus` | [Lire](#hors_corpus_003) |
| `hors_corpus_004` | `hors_corpus` | [Lire](#hors_corpus_004) |
| `hors_corpus_005` | `hors_corpus` | [Lire](#hors_corpus_005) |
| `hors_corpus_006` | `hors_corpus` | [Lire](#hors_corpus_006) |

## simple_001

Identifiant rapporté : `SYN_simple_001_0001`. Catégorie proposée : `simple` ; difficulté cible : `easy`.
`answerable_proposed: true` ; `human: pending` rapporté.

### Question rapportée

Pendant le congé sans solde, le salaire du salarié est-il maintenu ?

### Sources de génération rapportées

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés disponibles

Preuve proposée dans `m2-article374529-0004` :

```text
Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue.
```

### Provenance de cette copie

Étude §12, question et extrait rapportés ; blocs de provenance partiels documentés.
[Contexte documentaire, section 12](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## reformulation_001

Identifiant rapporté : `SYN_reformulation_001_0001`. Catégorie proposée : `reformulation` ; difficulté cible : `easy`.
`answerable_proposed: true` ; `human: pending` rapporté.

### Question rapportée

Qu'arrive-t-il à la rémunération d'un employé pendant qu'il est en congé sans solde ?

### Sources de génération rapportées

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés disponibles

Preuve proposée dans `m2-article374529-0004` :

```text
Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue.
```

### Provenance de cette copie

Étude §12, question et extrait rapportés.
[Contexte documentaire, section 12](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## multi_passage_002

Identifiant rapporté : `SYN_multi_passage_002_0001`. Catégorie proposée : `multi_passage` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `human: pending` rapporté.

### Question rapportée

Quelles sont les conditions et obligations du salarié lorsqu'il sollicite un congé sans solde, et comment cela se compare-t-il avec les congés réglementés par le Code du travail ?

### Sources de génération rapportées

[`m2-article374529-0002`](#m2-article374529-0002), [`m2-article374529-0000`](#m2-article374529-0000)

### Éléments proposés disponibles

Extraits proposés non recopiés dans ce support : consulter `candidates.jsonl` original.
### Provenance de cette copie

Étude §16, question rapportée ; extraits exacts non recopiés dans ce dossier.
[Contexte documentaire, section 16](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## multi_passage_003

Identifiant rapporté : `SYN_multi_passage_003_0001`. Catégorie proposée : `multi_passage` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `human: pending` rapporté.

### Question rapportée

**Formulation exacte à recueillir dans le fichier original.**

### Sources de génération rapportées

[`m2-article374529-0002`](#m2-article374529-0002), [`m2-article374529-0000`](#m2-article374529-0000)

### Éléments proposés disponibles

Extraits proposés non recopiés dans ce support : consulter `candidates.jsonl` original.
### Provenance de cette copie

Étude §17 : résumé seulement ; formulation exacte indisponible dans les éléments utilisés ici.
[Contexte documentaire, section 17](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## multi_passage_004

Identifiant rapporté : `SYN_multi_passage_004_0001`. Catégorie proposée : `multi_passage` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `human: pending` rapporté.

### Question rapportée

Quelles conditions doivent être respectées pour bénéficier d'un congé sans solde et comment est-elle financée ?

### Sources de génération rapportées

[`m2-article374529-0003`](#m2-article374529-0003), [`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés disponibles

Preuve proposée dans `m2-article374529-0003` :

```text
Afin de prévenir tout litige, le principe du congé, sa durée, les conditions de retour dans l'entreprise... doivent faire l'objet d'un accord écrit entre l'employeur et le salarié. Il convient également de se reporter à la convention collective applicable à l'entreprise qui peut prévoir des dispositions à ce sujet.
```

Preuve proposée dans `m2-article374529-0004` :

```text
Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue. Si un compte épargne-temps (CET) a été mis en place dans l’entreprise, le salarié peut toutefois utiliser les droits acquis sur son CET pour « financer » ce congé, dès lors que cette possibilité est prévue par l’accord ayant instauré le CET.
```

### Provenance de cette copie

Candidat complet copié par Jibril dans la conversation ; fichier original non reçu.
[Contexte documentaire, section 18](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## multi_passage_006

Identifiant rapporté : `SYN_multi_passage_006_0001`. Catégorie proposée : `multi_passage` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `human: pending` rapporté.

### Question rapportée

Quelles conditions doivent remplir les salariés pour obtenir la médaille d'honneur du travail, et comment est-elle attribuée ?

### Sources de génération rapportées

[`m2-article374500-0003`](#m2-article374500-0003), [`m2-article374500-0000`](#m2-article374500-0000)

### Éléments proposés disponibles

Preuve proposée dans `m2-article374500-0003` :

```text
Peuvent obtenir la médaille d'honneur du travail les salariés, qu'ils soient ou non de nationalité française, travaillant sur le territoire de la République pour des employeurs français ou étrangers.
```

Preuve proposée dans `m2-article374500-0000` :

```text
- La médaille d'honneur du travail récompense l'ancienneté de services des salariés.
- Elle est :
  - attribuée à la demande du salarié qui doit déposer un dossier ;
  - assortie d'un diplôme et, dans certains cas, d'une gratification (convention collective ou usage de l'entreprise).
```

### Provenance de cette copie

Candidat complet copié par Jibril dans la conversation ; fichier original non reçu.
[Contexte documentaire, section 18](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## adversarial_001

Identifiant rapporté : `SYN_adversarial_001_0001`. Catégorie proposée : `adversarial` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `human: pending` rapporté.

### Question rapportée

Pendant le congé sans solde, le salaire du salarié est maintenu grâce à un compte épargne-temps (CET).

### Sources de génération rapportées

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés disponibles

Preuve proposée dans `m2-article374529-0004` :

```text
Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue. Si un compte épargne-temps (CET) a été mis en place dans l’entreprise, le salarié peut toutefois utiliser les droits acquis sur son CET pour « financer » ce congé, dès lors que cette possibilité est prévue par l’accord ayant instauré le CET.
```

Prémisse proposée :

Pendant le congé sans solde, le salaire du salarié est maintenu grâce à un compte épargne-temps (CET).

Correction proposée :

Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue. Si un compte épargne-temps (CET) a été mis en place dans l’entreprise, le salarié peut toutefois utiliser les droits acquis sur son CET pour « financer » ce congé, dès lors que cette possibilité est prévue par l’accord ayant instauré le CET.

### Provenance de cette copie

Candidat complet copié par Jibril dans la conversation ; fichier original non reçu.
[Contexte documentaire, section 21](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## adversarial_002

Identifiant rapporté : `SYN_adversarial_002_0001`. Catégorie proposée : `adversarial` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `human: pending` rapporté.

### Question rapportée

Pendant le congé sans solde, la rémunération du salarié est-elle maintenue ?

### Sources de génération rapportées

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés disponibles

Preuve proposée dans `m2-article374529-0004` :

```text
Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue.
```

Prémisse proposée :

La rémunération du salarié est maintenue pendant le congé sans solde.

Correction proposée :

La rémunération du salarié n’est pas maintenue pendant le congé sans solde.

### Provenance de cette copie

Candidat complet copié par Jibril dans la conversation ; fichier original non reçu.
[Contexte documentaire, section 22](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## adversarial_003

Identifiant rapporté : `SYN_adversarial_003_0001`. Catégorie proposée : `adversarial` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `human: pending` rapporté.

### Question rapportée

Lorsqu'un représentant du CSE constate que les produits ou procédés de fabrication utilisés par l'établissement font peser un risque grave pour la santé publique ou l'environnement, l'employeur est obligé de réaliser une enquête avec le membre de la délégation du personnel qui a effectué le signalement ?

### Sources de génération rapportées

[`m2-article377050-0003`](#m2-article377050-0003)

### Éléments proposés disponibles

Preuve proposée dans `m2-article377050-0003` :

```text
Dans ce cas, le Code du travail ne fait pas référence à une enquête, mais un examen conjoint de la situation.
```

Prémisse proposée :

Lorsqu'un représentant du CSE constate un risque grave pour la santé publique ou l'environnement, l'employeur est obligé de réaliser une enquête avec le membre de la délégation du personnel qui a effectué le signalement.

Correction proposée :

Dans ce cas, le Code du travail ne fait pas référence à une enquête, mais à un examen conjoint de la situation.

### Provenance de cette copie

Candidat complet copié par Jibril dans la conversation ; fichier original non reçu.
[Contexte documentaire, section 23](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## hors_corpus_001

Identifiant rapporté : `SYN_hors_corpus_001_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `human: pending` rapporté.

### Question rapportée

Quelles conditions doivent être remplies pour que le salarié puisse utiliser son compte épargne-temps (CET) pendant son congé sans solde ?

### Sources de génération rapportées

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés disponibles

`evidence: []` proposé. Cela ne constitue pas une preuve d'absence dans le corpus.
Motif d'absence proposé :

L'information sur les conditions spécifiques n'est pas fournie dans ce passage.

### Provenance de cette copie

Candidat complet copié par Jibril dans la conversation ; fichier original non reçu.
[Contexte documentaire, section 26](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## hors_corpus_002

Identifiant rapporté : `SYN_hors_corpus_002_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `human: pending` rapporté.

### Question rapportée

Quelles sont les conditions pour déclencher une alerte par un représentant du CSE en matière de santé et de sécurité ?

### Sources de génération rapportées

[`m2-article377050-0003`](#m2-article377050-0003)

### Éléments proposés disponibles

`evidence: []` proposé. Cela ne constitue pas une preuve d'absence dans le corpus.
Motif d'absence proposé :

L'information sur les conditions de déclenchement d'une alerte par un représentant du CSE en matière de santé et de sécurité n'est pas fournie dans ce passage.

### Provenance de cette copie

Candidat complet copié par Jibril dans la conversation ; fichier original non reçu.
[Contexte documentaire, section 27](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## hors_corpus_003

Identifiant rapporté : `SYN_hors_corpus_003_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `human: pending` rapporté.

### Question rapportée

Quelles conditions doivent remplir les salariés résidant à l'étranger pour obtenir la médaille d'honneur du travail ?

### Sources de génération rapportées

[`m2-article374500-0003`](#m2-article374500-0003)

### Éléments proposés disponibles

`evidence: []` proposé. Cela ne constitue pas une preuve d'absence dans le corpus.
Motif d'absence proposé :

L'information sur les conditions spécifiques pour les salariés résidant à l'étranger n'est pas fournie dans ce passage.

### Provenance de cette copie

Candidat complet copié par Jibril dans la conversation ; fichier original non reçu.
[Contexte documentaire, section 27](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## hors_corpus_004

Identifiant rapporté : `SYN_hors_corpus_004_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `human: pending` rapporté.

### Question rapportée

Quelles sont les conditions pour que le salarié puisse utiliser son compte épargne-temps (CET) pendant un congé sans solde ?

### Sources de génération rapportées

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés disponibles

`evidence: []` proposé. Cela ne constitue pas une preuve d'absence dans le corpus.
Motif d'absence proposé :

Les conditions spécifiques pour l'utilisation du CET pendant un congé sans solde sont absentes dans le passage documenté.

### Provenance de cette copie

Candidat complet copié par Jibril dans la conversation ; fichier original non reçu.
[Contexte documentaire, section 28](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## hors_corpus_005

Identifiant rapporté : `SYN_hors_corpus_005_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `human: pending` rapporté.

### Question rapportée

Quelles sont les conséquences légales pour l'employeur si une alerte est déclenchée en raison d'un risque grave pour la santé publique ou l'environnement ?

### Sources de génération rapportées

[`m2-article377050-0003`](#m2-article377050-0003)

### Éléments proposés disponibles

`evidence: []` proposé. Cela ne constitue pas une preuve d'absence dans le corpus.
Motif d'absence proposé :

L'information sur les conséquences légales pour l'employeur en cas de déclenchement d'une alerte n'est pas présente dans le passage fourni et doit être recherchée dans le corpus complet.

### Provenance de cette copie

Candidat complet copié par Jibril dans la conversation ; fichier original non reçu.
[Contexte documentaire, section 28](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## hors_corpus_006

Identifiant rapporté : `SYN_hors_corpus_006_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `human: pending` rapporté.

### Question rapportée

Quelles conditions doivent remplir les salariés résidant à l'étranger pour obtenir la médaille d'honneur du travail de manière exceptionnelle ?

### Sources de génération rapportées

[`m2-article374500-0003`](#m2-article374500-0003)

### Éléments proposés disponibles

`evidence: []` proposé. Cela ne constitue pas une preuve d'absence dans le corpus.
Motif d'absence proposé :

L'information sur les conditions exceptionnelles pour les salariés résidant à l'étranger n'est pas présente dans le passage documenté.

### Provenance de cette copie

Candidat complet copié par Jibril dans la conversation ; fichier original non reçu.
[Contexte documentaire, section 28](../agent0_light.md). Les fichiers et empreintes des originaux restent à recueillir.


## Sources complètes de référence

Ces huit passages sont extraits des fichiers M2 versionnés au commit `36bb4e05094dbc68d1975f1d8ea01eac50de166b`. Ils servent à lire les essais sans limiter à eux la vérification d'un cas hors corpus.
Empreinte complète des passages : `aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d`.
L'affichage remplace uniquement les caractères U+0001 par la notation `\u0001` ; le JSON associé conserve les valeurs sans cette convention d'affichage.

## m2-article374500-0000

**La médaille d'honneur du travail** — Chapô

[URL de provenance](https://travail-emploi.gouv.fr/la-medaille-dhonneur-du-travail) ; date de mise à jour déclarée : `2026-04-20`. Relire le corpus figé, pas une version Web modifiée depuis.

```text
- La médaille d'honneur du travail récompense l'ancienneté de services des salariés.
- Elle est :
  - attribuée à la demande du salarié qui doit déposer un dossier ;
  - assortie d'un diplôme et, dans certains cas, d'une gratification (convention collective ou usage de l'entreprise).
```

SHA-256 du texte UTF-8 : `9914be597dddf7ba50698d8f68554ab7f53821c35dfe40b74c9142088f8c4133`.

## m2-article374500-0003

**La médaille d'honneur du travail** — Quels salariés ?

[URL de provenance](https://travail-emploi.gouv.fr/la-medaille-dhonneur-du-travail) ; date de mise à jour déclarée : `2026-04-20`. Relire le corpus figé, pas une version Web modifiée depuis.

```text
Peuvent obtenir la médaille d'honneur du travail les salariés, qu'ils soient ou non de nationalité française, travaillant sur le territoire de la République pour des employeurs français ou étrangers.
La médaille d'honneur du travail peut également être décernée aux salariés, qu'ils soient ou non de nationalité française travaillant à l'étranger :
- Chez un employeur français ;
- Dans une succursale ou agence d'une entreprise ou d'un établissement dont le siège social est sur le territoire de la République ;
- Dans les filiales des sociétés françaises, même si ces filiales ne sont pas constituées selon le droit français.
À titre exceptionnel, et sous réserve qu'ils remplissent également les conditions d'ancienneté de services prévues par la réglementation, les salariés, qu'ils soient ou non de nationalité française, résidant à l'étranger et travaillant dans d'autres établissements que ceux visés ci-dessus, peuvent obtenir la médaille d'honneur du travail si leurs activités professionnelles ont particulièrement contribué au bon renom de la France.
Sont, en principe, exclus :
- Les fonctionnaires soumis au statut de la fonction publique ;
- Les magistrats de l'ordre judiciaire ;
- Les salariés qui par leur profession peuvent prétendre à d'autres récompenses (médaille d'honneur agricole, médaille d'honneur des chemins de fer... ) ;
- Les parlementaires en exercice.
```

SHA-256 du texte UTF-8 : `6fcb3867f38b7275b8419669a0cbe534f2807d4c2c11df3b6a65f03f6d300c06`.

## m2-article374529-0000

**Le congé sans solde** — Chapô

[URL de provenance](https://travail-emploi.gouv.fr/le-conge-sans-solde) ; date de mise à jour déclarée : `2021-12-21`. Relire le corpus figé, pas une version Web modifiée depuis.

```text
Le congé sans solde n'est pas réglementé par le Code du travail : aucune condition ni procédure ne sont imposées pour en bénéficier. Son organisation et sa durée sont définies de gré à gré entre le salarié et l'employeur. Celui-ci est libre de l'accepter ou de le refuser. Un salarié peut demander un congé sans solde pour divers motifs. Si sa demande est acceptée, il ne sera pas rémunéré, sauf à utiliser son compte épargne-temps. De même, la durée de son absence ne sera pas prise en compte pour le calcul des droits qu'il tient de son ancienneté, pour les congés payés...
```

SHA-256 du texte UTF-8 : `a4d87df47bbbccb48a8be65aa9a9462fabbeda0b7e2961d676d9ef3ba3471594`.

## m2-article374529-0002

**Le congé sans solde** — Quelles sont les caractéristiques ?

[URL de provenance](https://travail-emploi.gouv.fr/le-conge-sans-solde) ; date de mise à jour déclarée : `2021-12-21`. Relire le corpus figé, pas une version Web modifiée depuis.

```text
Par définition, le congé sans solde est un congé pour convenance personnelle : le salarié est totalement libre de l'utiliser à des fins personnelles (faire du sport, un voyage, s'occuper de ses enfants, ... ) ou professionnelles (créer une entreprise, exercer une autre activité professionnelle,... ).
Si le congé sans solde permet, en principe, au salarié de travailler pour un autre employeur, celui-ci doit préalablement vérifier son contrat de travail. Si une clause de non-concurrence ou d'exclusivité y figure, il risque une sanction voire un licenciement en ne s'y conformant pas. Même en l'absence de clause, le salarié reste tenu par une obligation de loyauté envers son employeur.
Toutefois, compte tenu de l'absence de réglementation concernant ce congé (et donc de garanties tant pour l'employeur que pour le salarié), il peut être plus intéressant d'opter pour un congé organisé par le Code du travail et dont l'objectif correspond au projet du salarié, tel :
- le congé sabbatique ;
- le congé ou temps partiel pour création d'entreprise ;
- les congés de formation ;
- le congé parental d'éducation ;
- le congé de solidarité familiale ;
- le congé de proche aidant,...
```

SHA-256 du texte UTF-8 : `807b65e0a4a52ef97a3043230e33700d3d45f7e461b5adc6d5a70bc3553ba20a`.

## m2-article374529-0003

**Le congé sans solde** — Quelle est la procédure ?

[URL de provenance](https://travail-emploi.gouv.fr/le-conge-sans-solde) ; date de mise à jour déclarée : `2021-12-21`. Relire le corpus figé, pas une version Web modifiée depuis.

```text
Le congé sans solde n'étant pas prévu par le Code du travail, aucune précision particulière concernant la procédure n'est donnée. Afin de prévenir tout litige, le principe du congé, sa durée, les conditions de retour dans l'entreprise... doivent faire l'objet d'un accord écrit entre l'employeur et le salarié. Il convient également de se reporter à la convention collective applicable à l'entreprise qui peut prévoir des dispositions à ce sujet.
```

SHA-256 du texte UTF-8 : `2a23877d1e98e215181438a3cdbbab6c6d141be6f41f3ad156eb211cc58d23c5`.

## m2-article374529-0004

**Le congé sans solde** — La rémunération est-elle maintenue pendant le congé ?

[URL de provenance](https://travail-emploi.gouv.fr/le-conge-sans-solde) ; date de mise à jour déclarée : `2021-12-21`. Relire le corpus figé, pas une version Web modifiée depuis.

```text
Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue. Si un compte épargne-temps (CET) a été mis en place dans l’entreprise, le salarié peut toutefois utiliser les droits acquis sur son CET pour « financer » ce congé, dès lors que cette possibilité est prévue par l’accord ayant instauré le CET.
```

SHA-256 du texte UTF-8 : `86f438f6f085b9d18ce7e56aa3a0433aa28271555682b4750d0b17d720f470b6`.

## m2-article377050-0003

**Les attributions du CSE en matière de santé, de sécurité et de conditions de travail** — Le CSE et la santé sécurité au travail (Web série droit du travail)

[URL de provenance](https://travail-emploi.gouv.fr/les-attributions-du-cse-en-matiere-de-sante-de-securite-et-de-conditions-de-travail) ; date de mise à jour déclarée : `2025-10-15`. Relire le corpus figé, pas une version Web modifiée depuis.

```text
Y participent au moins l'employeur ou un représentant désigné par lui et un représentant du personnel siégeant au CSE.
Lors de ces enquêtes, l'objectif est d'identifier les causes des accidents et de faire des préconisations en vue de prévenir la survenue de nouveaux incidents.
Ils ont ensuite un droit d'information et de consultation des documents.
Par exemple, lorsque l'employeur réceptionne des documents relatifs aux vérifications et contrôles mis à charge au titre de la santé et de la sécurité, il en informe les membres du CSE.
Il peut s'agir d'attestations, de consignes, de résultats ou de rapports.
L'employeur leur présente également la liste des actions de prévention et de protection prévues des risques professionnels.
Les membres de la délégation du personnel disposent ensuite d'un droit d'alerte. \u0001 En matière de santé et de sécurité, cette alerte peut être déclenchée\u0001 à plusieurs titres.
Premièrement, l'origine de l'alerte peut être le constat d'une atteinte aux droits des personnes, notamment à leur santé physique et mentale : par exemple, la découverte de faits de harcèlement moral ou sexuel.
Deuxièmement, l'origine de l'alerte peut être un danger grave et imminent : à titre d'exemple, une défaillance dans un système de protection qui menacerait immédiatement la vie d'un ou plusieurs travailleurs.
Dans les deux cas, le déclenchement de ces alertes oblige l'employeur à réaliser une enquête avec le membre de la délégation du personnel qui a effectué le signalement.
Enfin, une alerte peut être déclenchée par un représentant du CSE qui constate, notamment par l'intermédiaire d'un travailleur, que les produits ou procédés de fabrication utilisés ou mis en œuvre par l'établissement font peser un risque grave pour la santé publique ou l'environnement.
Dans ce cas, le Code du travail ne fait pas référence à une enquête, mais un examen conjoint de la situation.
```

SHA-256 du texte UTF-8 : `fd42ee64e0872061f4227f461de7341decab00ee63ddbfad48869faf165defc5`.

## m2-article377050-0017

**Les attributions du CSE en matière de santé, de sécurité et de conditions de travail** — De quels moyens dispose le CSE dans le cadre de ses attributions dans les domaines de la santé, de la sécurité et des conditions de travail ?

[URL de provenance](https://travail-emploi.gouv.fr/les-attributions-du-cse-en-matiere-de-sante-de-securite-et-de-conditions-de-travail) ; date de mise à jour déclarée : `2025-10-15`. Relire le corpus figé, pas une version Web modifiée depuis.

```text
Le médecin du travail et le responsable du service de sécurité et des conditions de travail assistent à ces réunions, avec voix consultative. L'agent de contrôle de l'inspection du travail ainsi que les agents des services de prévention des organismes de sécurité sociale sont invités à certaines de ces réunions SSCT ainsi qu’à l’ensemble des réunions de la CSSCT. Ils sont conviés à toutes les réunions portant sur la SSCT sur initiative de l’employeur ou à la demande de la majorité de la délégation du personnel du CSE.
Lorsque l'employeur est défaillant, et à la demande d'au moins la moitié des membres du CSE, celui-ci peut être convoqué par l'agent de contrôle de l'inspection du travail et siéger sous sa présidence.
L'employeur informe annuellement l'agent de contrôle de l'inspection du travail, le médecin du travail et l'agent des services de prévention des organismes de sécurité sociale du calendrier retenu pour les réunions consacrées aux sujets relevant de la santé, de la sécurité ou des conditions de travail, et leur confirme par écrit au moins 15 jours à l'avance la tenue de ces réunions.
Au même titre que les réunions du CSE, est également rémunéré comme temps de travail effectif et n'est pas déduit des heures de délégation le temps passé par les membres de la délégation du personnel du CSE :
- À la recherche de mesures préventives dans toute situation d'urgence et de gravité, notamment lors de la mise en œuvre de la procédure de danger grave et imminent mentionnée ci-dessus ;
- Aux enquêtes menées après un accident du travail grave ou des incidents répétés ayant révélé un risque grave ou une maladie professionnelle ou à caractère professionnel grave ;
- Aux réunions de la CSSCT (article R. 2315-7 du Code du travail) ;
- Aux formations en santé, sécurité et conditions de travail (article L. 2315-18 du Code du travail).
```

SHA-256 du texte UTF-8 : `4f2a83170b54f288d18a83438d7994d2625fbde36e9d04a61b0c15a7f0347eff`.

