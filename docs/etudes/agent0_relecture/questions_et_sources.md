# Questions et sources — originaux reçus le 20 octobre 2026

Les 15 formulations et champs proposés ci-dessous sont copiés depuis les `candidates.jsonl` de l'archive reçue. Leur concordance avec les sorties brutes a été contrôlée ; les questions ne sont pas corrigées.
Les 15 candidats conservent leur statut original `human: pending`. Les décisions de [la grille](grille_relecture.json) restent vierges.
Lire les questions et sources avant les [observations assistées](observations_assistees.md). Les justifications affichées sont celles du générateur, pas des verdicts.
[Vérification des originaux](verification_archive.md) — [empreintes et détails techniques](verification_archive.json). Les traces intégrales restent hors Git.
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

Identifiant : `SYN_simple_001_0001`. Catégorie proposée : `simple` ; difficulté cible : `easy`.
`answerable_proposed: true` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Pendant le congé sans solde, le salaire du salarié est-il maintenu ?

### Sources de génération

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés par le générateur

Preuve proposée dans `m2-article374529-0004` :

```text
Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue.
```

Justification proposée (`generation_reason`) :

La question est directement repérable dans le passage et ne nécessite aucune supposition ou interprétation.

### Provenance contrôlée

Original reçu : `simple_001/candidates.jsonl` ; SHA-256 : `c3d07fb70b38dd69b15b863e9a7d5a6b6444847f3809296ae80ab60b3648690e`.
Commit déclaré : [`823621b`](https://github.com/datatigersNLP/data_tigers_nlp/commit/823621b18535f245ad05bb99a762dbff39bc2ae0). Prompt reconstruit : `agent0-simple-reformulation-v1`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## reformulation_001

Identifiant : `SYN_reformulation_001_0001`. Catégorie proposée : `reformulation` ; difficulté cible : `easy`.
`answerable_proposed: true` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Qu'arrive-t-il à la rémunération d'un employé pendant qu'il est en congé sans solde ?

### Sources de génération

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés par le générateur

Preuve proposée dans `m2-article374529-0004` :

```text
Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue.
```

Justification proposée (`generation_reason`) :

Reformuler la demande en conservant le sens original du passage.

### Provenance contrôlée

Original reçu : `reformulation_001/candidates.jsonl` ; SHA-256 : `978127a1fa4a0d1af0c277cf5e9bfe0cd6c9d4b2da23fa1c4462513719bc407f`.
Commit déclaré : [`e6d6a64`](https://github.com/datatigersNLP/data_tigers_nlp/commit/e6d6a640769d394155940fdd13226199c5192001). Prompt reconstruit : `agent0-simple-reformulation-v1`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## multi_passage_002

Identifiant : `SYN_multi_passage_002_0001`. Catégorie proposée : `multi_passage` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Quelles sont les conditions et obligations du salarié lorsqu'il sollicite un congé sans solde, et comment cela se compare-t-il avec les congés réglementés par le Code du travail ?

### Sources de génération

[`m2-article374529-0002`](#m2-article374529-0002), [`m2-article374529-0000`](#m2-article374529-0000)

### Éléments proposés par le générateur

Preuve proposée dans `m2-article374529-0002` :

```text
Si le congé sans solde permet, en principe, au salarié de travailler pour un autre employeur, celui-ci doit préalablement vérifier son contrat de travail. Si une clause de non-concurrence ou d'exclusivité y figure, il risque une sanction voire un licenciement en ne s'y conformant pas. Même en l'absence de clause, le salarié reste tenu par une obligation de loyauté envers son employeur.
```

Preuve proposée dans `m2-article374529-0000` :

```text
Le congé sans solde n'est pas réglementé par le Code du travail : aucune condition ni procédure ne sont imposées pour en bénéficier. Son organisation et sa durée sont définies de gré à gré entre le salarié et l'employeur. Celui-ci est libre de l'accepter ou de le refuser.
```

Justification proposée (`generation_reason`) :

La question nécessite de combiner les informations sur les conditions et obligations du salarié lorsqu'il sollicite un congé sans solde (dans le premier passage) avec la nature non-réglementée de ce congé (dans le second passage). Cela permet de comparer le congé sans solde avec les congés réglementés par le Code du travail, en mettant en évidence les différences et les obligations spécifiques.

### Provenance contrôlée

Original reçu : `multi_passage_002/candidates.jsonl` ; SHA-256 : `2dbe1ba7a04168a08c13aa1594a9844fa817c0e03296028e2d05d8cbaa7a44de`.
Commit déclaré : [`475aa90`](https://github.com/datatigersNLP/data_tigers_nlp/commit/475aa902fcfd70d980019433557959f3507c803b). Prompt reconstruit : `agent0-multi-passage-v2`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## multi_passage_003

Identifiant : `SYN_multi_passage_003_0001`. Catégorie proposée : `multi_passage` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Quelles sont les conditions et obligations du salarié lorsqu'il souhaite bénéficier d'un congé sans solde, et comment cela se compare à d'autres types de congés réglementés ?

### Sources de génération

[`m2-article374529-0002`](#m2-article374529-0002), [`m2-article374529-0000`](#m2-article374529-0000)

### Éléments proposés par le générateur

Preuve proposée dans `m2-article374529-0002` :

```text
Si le congé sans solde permet, en principe, au salarié de travailler pour un autre employeur, celui-ci doit préalablement vérifier son contrat de travail. Si une clause de non-concurrence ou d'exclusivité y figure, il risque une sanction voire un licenciement en ne s'y conformant pas. Même en l'absence de clause, le salarié reste tenu par une obligation de loyauté envers son employeur.
```

Preuve proposée dans `m2-article374529-0000` :

```text
Le congé sans solde n'est pas réglementé par le Code du travail : aucune condition ni procédure ne sont imposées pour en bénéficier. Son organisation et sa durée sont définies de gré à gré entre le salarié et l'employeur. Celui-ci est libre de l'accepter ou de le refuser.
```

Justification proposée (`generation_reason`) :

La question nécessite d'analyser les conditions et obligations du salarié lorsqu'il souhaite bénéficier d'un congé sans solde, en se basant sur les informations fournies dans les deux passages. Elle demande également de comparer ces conditions à d'autres types de congés réglementés, ce qui nécessite de combiner les informations des deux sources.

### Provenance contrôlée

Original reçu : `multi_passage_003/candidates.jsonl` ; SHA-256 : `b9b3325f5ccb83241812ea64c7b288b744f321d68ac079edc129f66db4e28ae0`.
Commit déclaré : [`824eaa1`](https://github.com/datatigersNLP/data_tigers_nlp/commit/824eaa12b9bbfca03e93aa7e3586615369139788). Prompt reconstruit : `agent0-multi-passage-v3`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## multi_passage_004

Identifiant : `SYN_multi_passage_004_0001`. Catégorie proposée : `multi_passage` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Quelles conditions doivent être respectées pour bénéficier d'un congé sans solde et comment est-elle financée ?

### Sources de génération

[`m2-article374529-0003`](#m2-article374529-0003), [`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés par le générateur

Preuve proposée dans `m2-article374529-0003` :

```text
Afin de prévenir tout litige, le principe du congé, sa durée, les conditions de retour dans l'entreprise... doivent faire l'objet d'un accord écrit entre l'employeur et le salarié. Il convient également de se reporter à la convention collective applicable à l'entreprise qui peut prévoir des dispositions à ce sujet.
```

Preuve proposée dans `m2-article374529-0004` :

```text
Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue. Si un compte épargne-temps (CET) a été mis en place dans l’entreprise, le salarié peut toutefois utiliser les droits acquis sur son CET pour « financer » ce congé, dès lors que cette possibilité est prévue par l’accord ayant instauré le CET.
```

Justification proposée (`generation_reason`) :

La question nécessite d'associer les informations sur la procédure du congé sans solde (dans le premier passage) et la rémunération pendant ce congé (dans le second passage). Ces deux passages fournissent des informations complémentaires pour répondre à la question, en combinant les conditions d'accord écrit et la possibilité de financement via un CET.

### Provenance contrôlée

Original reçu : `multi_passage_004/candidates.jsonl` ; SHA-256 : `0a0283607e68ba6eb15e8e0d464a16e2ce9b623b01f692382f35c8bf3da3410a`.
Commit déclaré : [`1f7eeca`](https://github.com/datatigersNLP/data_tigers_nlp/commit/1f7eeca8eea1014e959b7318079ae177d2980037). Prompt reconstruit : `agent0-multi-passage-v3`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## multi_passage_006

Identifiant : `SYN_multi_passage_006_0001`. Catégorie proposée : `multi_passage` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Quelles conditions doivent remplir les salariés pour obtenir la médaille d'honneur du travail, et comment est-elle attribuée ?

### Sources de génération

[`m2-article374500-0003`](#m2-article374500-0003), [`m2-article374500-0000`](#m2-article374500-0000)

### Éléments proposés par le générateur

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

Justification proposée (`generation_reason`) :

La question nécessite d'analyser les conditions d'obtention de la médaille d'honneur du travail, qui sont détaillées dans le premier passage, et de comprendre le processus d'attribution, qui est expliqué dans le second passage. Ces deux informations sont complémentaires et ne peuvent être traitées indépendamment pour répondre à la question.

### Provenance contrôlée

Original reçu : `multi_passage_006/candidates.jsonl` ; SHA-256 : `bc376df6ff0affb424c50321cc0c914937e9fe2476e6ad834ec2f966535200ab`.
Commit déclaré : [`1f7eeca`](https://github.com/datatigersNLP/data_tigers_nlp/commit/1f7eeca8eea1014e959b7318079ae177d2980037). Prompt reconstruit : `agent0-multi-passage-v3`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## adversarial_001

Identifiant : `SYN_adversarial_001_0001`. Catégorie proposée : `adversarial` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Pendant le congé sans solde, le salaire du salarié est maintenu grâce à un compte épargne-temps (CET).

### Sources de génération

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés par le générateur

Preuve proposée dans `m2-article374529-0004` :

```text
Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue. Si un compte épargne-temps (CET) a été mis en place dans l’entreprise, le salarié peut toutefois utiliser les droits acquis sur son CET pour « financer » ce congé, dès lors que cette possibilité est prévue par l’accord ayant instauré le CET.
```

Justification proposée (`generation_reason`) :

La prémisse est fausse car elle suggère que le salaire est maintenu pendant le congé sans solde, ce qui est contraire aux informations fournies dans le passage. Le passage indique clairement que la rémunération n'est pas maintenue, mais que le CET peut être utilisé pour financer le congé, sous certaines conditions.

Prémisse proposée :

Pendant le congé sans solde, le salaire du salarié est maintenu grâce à un compte épargne-temps (CET).

Correction proposée :

Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue. Si un compte épargne-temps (CET) a été mis en place dans l’entreprise, le salarié peut toutefois utiliser les droits acquis sur son CET pour « financer » ce congé, dès lors que cette possibilité est prévue par l’accord ayant instauré le CET.

### Provenance contrôlée

Original reçu : `adversarial_001/candidates.jsonl` ; SHA-256 : `0fd31993a2289ee3cb250bff9838d774896708893f68150f4c09f74eb331181d`.
Commit déclaré : [`0a22c0d`](https://github.com/datatigersNLP/data_tigers_nlp/commit/0a22c0d6229b699239cb77c03a299b1c754ef987). Prompt reconstruit : `agent0-adversarial-v1`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## adversarial_002

Identifiant : `SYN_adversarial_002_0001`. Catégorie proposée : `adversarial` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Pendant le congé sans solde, la rémunération du salarié est-elle maintenue ?

### Sources de génération

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés par le générateur

Preuve proposée dans `m2-article374529-0004` :

```text
Pendant le congé sans solde, la rémunération du salarié n’est pas maintenue.
```

Justification proposée (`generation_reason`) :

La question contient une prémisse fausse en affirmant que la rémunération est maintenue pendant le congé sans solde, alors que le passage indique clairement qu'elle n'est pas maintenue. Cette prémisse peut être corrigée en citant le texte directement.

Prémisse proposée :

La rémunération du salarié est maintenue pendant le congé sans solde.

Correction proposée :

La rémunération du salarié n’est pas maintenue pendant le congé sans solde.

### Provenance contrôlée

Original reçu : `adversarial_002/candidates.jsonl` ; SHA-256 : `7ab454b917b0a52f08b039ea2d2a29d4912f7c9dd4ed86a08320eac35f17c19e`.
Commit déclaré : [`9f06371`](https://github.com/datatigersNLP/data_tigers_nlp/commit/9f063711a346643e895f0f8387dbffe648a79fb3). Prompt reconstruit : `agent0-adversarial-v2`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## adversarial_003

Identifiant : `SYN_adversarial_003_0001`. Catégorie proposée : `adversarial` ; difficulté cible : `medium`.
`answerable_proposed: true` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Lorsqu'un représentant du CSE constate que les produits ou procédés de fabrication utilisés par l'établissement font peser un risque grave pour la santé publique ou l'environnement, l'employeur est obligé de réaliser une enquête avec le membre de la délégation du personnel qui a effectué le signalement ?

### Sources de génération

[`m2-article377050-0003`](#m2-article377050-0003)

### Éléments proposés par le générateur

Preuve proposée dans `m2-article377050-0003` :

```text
Dans ce cas, le Code du travail ne fait pas référence à une enquête, mais un examen conjoint de la situation.
```

Justification proposée (`generation_reason`) :

La prémisse est fausse car le passage indique que le Code du travail ne fait pas référence à une enquête, mais à un examen conjoint de la situation. Cette prémisse permet de corriger la question en soulignant que l'employeur n'est pas obligé de réaliser une enquête, mais un examen conjoint.

Prémisse proposée :

Lorsqu'un représentant du CSE constate un risque grave pour la santé publique ou l'environnement, l'employeur est obligé de réaliser une enquête avec le membre de la délégation du personnel qui a effectué le signalement.

Correction proposée :

Dans ce cas, le Code du travail ne fait pas référence à une enquête, mais à un examen conjoint de la situation.

### Provenance contrôlée

Original reçu : `adversarial_003/candidates.jsonl` ; SHA-256 : `dd6c27b6470b9a096880da26ee8039c5118731943e2ba052211fc60bb4d9f119`.
Commit déclaré : [`9133ffc`](https://github.com/datatigersNLP/data_tigers_nlp/commit/9133ffc6d26b6d3ae33bf8abd76ac776f9529641). Prompt reconstruit : `agent0-adversarial-v3`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## hors_corpus_001

Identifiant : `SYN_hors_corpus_001_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Quelles conditions doivent être remplies pour que le salarié puisse utiliser son compte épargne-temps (CET) pendant son congé sans solde ?

### Sources de génération

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés par le générateur

`evidence: []`. Cela ne constitue pas une preuve d'absence documentaire.

Justification proposée (`generation_reason`) :

Vérifier les conditions spécifiques pour l'utilisation du compte épargne-temps (CET) pendant un congé sans solde.

Motif d'absence proposé :

L'information sur les conditions spécifiques n'est pas fournie dans ce passage.

### Provenance contrôlée

Original reçu : `hors_corpus_001/candidates.jsonl` ; SHA-256 : `146d8864638afe9df513afbc78e46d35d886f6de43c348e08d875ee350f66be8`.
Commit déclaré : [`72ea697`](https://github.com/datatigersNLP/data_tigers_nlp/commit/72ea6979464be99554930f508b9ad4d90680bb30). Prompt reconstruit : `agent0-hors-corpus-v1`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## hors_corpus_002

Identifiant : `SYN_hors_corpus_002_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Quelles sont les conditions pour déclencher une alerte par un représentant du CSE en matière de santé et de sécurité ?

### Sources de génération

[`m2-article377050-0003`](#m2-article377050-0003)

### Éléments proposés par le générateur

`evidence: []`. Cela ne constitue pas une preuve d'absence documentaire.

Justification proposée (`generation_reason`) :

Vérifier les conditions de déclenchement d'une alerte par un représentant du CSE en matière de santé et de sécurité dans le Code du travail.

Motif d'absence proposé :

L'information sur les conditions de déclenchement d'une alerte par un représentant du CSE en matière de santé et de sécurité n'est pas fournie dans ce passage.

### Provenance contrôlée

Original reçu : `hors_corpus_002/candidates.jsonl` ; SHA-256 : `b11019d66d3b295cbcc055a6dfa9f4aa1ccfd589aa98b25f894ec2282d5740dd`.
Commit déclaré : [`c54561c`](https://github.com/datatigersNLP/data_tigers_nlp/commit/c54561c9b6832dfb30282229bfebdbfad13894e7). Prompt reconstruit : `agent0-hors-corpus-v1`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## hors_corpus_003

Identifiant : `SYN_hors_corpus_003_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Quelles conditions doivent remplir les salariés résidant à l'étranger pour obtenir la médaille d'honneur du travail ?

### Sources de génération

[`m2-article374500-0003`](#m2-article374500-0003)

### Éléments proposés par le générateur

`evidence: []`. Cela ne constitue pas une preuve d'absence documentaire.

Justification proposée (`generation_reason`) :

Vérifier les conditions spécifiques pour les salariés résidant à l'étranger obtenir la médaille d'honneur du travail.

Motif d'absence proposé :

L'information sur les conditions spécifiques pour les salariés résidant à l'étranger n'est pas fournie dans ce passage.

### Provenance contrôlée

Original reçu : `hors_corpus_003/candidates.jsonl` ; SHA-256 : `8d3c44cda58199e61d5bc03c6dfe26ac182752bc111a45b147bad85d38a01dd8`.
Commit déclaré : [`c54561c`](https://github.com/datatigersNLP/data_tigers_nlp/commit/c54561c9b6832dfb30282229bfebdbfad13894e7). Prompt reconstruit : `agent0-hors-corpus-v1`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## hors_corpus_004

Identifiant : `SYN_hors_corpus_004_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Quelles sont les conditions pour que le salarié puisse utiliser son compte épargne-temps (CET) pendant un congé sans solde ?

### Sources de génération

[`m2-article374529-0004`](#m2-article374529-0004)

### Éléments proposés par le générateur

`evidence: []`. Cela ne constitue pas une preuve d'absence documentaire.

Justification proposée (`generation_reason`) :

Le passage documente que le salarié peut utiliser son CET pour financer le congé sans solde si cette possibilité est prévue par l'accord. Cependant, il ne précise pas les conditions exactes pour que cette utilisation soit possible.

Motif d'absence proposé :

Les conditions spécifiques pour l'utilisation du CET pendant un congé sans solde sont absentes dans le passage documenté.

### Provenance contrôlée

Original reçu : `hors_corpus_004/candidates.jsonl` ; SHA-256 : `2da1e6138b828c34f4ce650378856aa344a01efe0f0aff215665e2497cfb357a`.
Commit déclaré : [`670c43f`](https://github.com/datatigersNLP/data_tigers_nlp/commit/670c43fd1533358b39a9ea70a3a5a5e3a85e2739). Prompt reconstruit : `agent0-hors-corpus-v2`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## hors_corpus_005

Identifiant : `SYN_hors_corpus_005_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Quelles sont les conséquences légales pour l'employeur si une alerte est déclenchée en raison d'un risque grave pour la santé publique ou l'environnement ?

### Sources de génération

[`m2-article377050-0003`](#m2-article377050-0003)

### Éléments proposés par le générateur

`evidence: []`. Cela ne constitue pas une preuve d'absence documentaire.

Justification proposée (`generation_reason`) :

Le passage documente les conditions sous lesquelles une alerte peut être déclenchée par un représentant du CSE, mais ne fournit aucune information sur les conséquences légales pour l'employeur en cas de déclenchement d'une telle alerte.

Motif d'absence proposé :

L'information sur les conséquences légales pour l'employeur en cas de déclenchement d'une alerte n'est pas présente dans le passage fourni et doit être recherchée dans le corpus complet.

### Provenance contrôlée

Original reçu : `hors_corpus_005/candidates.jsonl` ; SHA-256 : `d313a0988c19ada222c842e168e856ee9cbf4466c2c288ec5b5a3cad8a263d44`.
Commit déclaré : [`670c43f`](https://github.com/datatigersNLP/data_tigers_nlp/commit/670c43fd1533358b39a9ea70a3a5a5e3a85e2739). Prompt reconstruit : `agent0-hors-corpus-v2`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## hors_corpus_006

Identifiant : `SYN_hors_corpus_006_0001`. Catégorie proposée : `hors_corpus` ; difficulté cible : `medium`.
`answerable_proposed: false` ; `automatic: passed` ; `human: pending` dans l'original.

### Question originale

Quelles conditions doivent remplir les salariés résidant à l'étranger pour obtenir la médaille d'honneur du travail de manière exceptionnelle ?

### Sources de génération

[`m2-article374500-0003`](#m2-article374500-0003)

### Éléments proposés par le générateur

`evidence: []`. Cela ne constitue pas une preuve d'absence documentaire.

Justification proposée (`generation_reason`) :

Le passage documente les conditions générales pour obtenir la médaille d'honneur du travail, mais ne précise pas les conditions exceptionnelles pour les salariés résidant à l'étranger.

Motif d'absence proposé :

L'information sur les conditions exceptionnelles pour les salariés résidant à l'étranger n'est pas présente dans le passage documenté.

### Provenance contrôlée

Original reçu : `hors_corpus_006/candidates.jsonl` ; SHA-256 : `6b31db8fba5e70cebd847674e77c86fa51292232e87feb120511b665ecdeab51`.
Commit déclaré : [`670c43f`](https://github.com/datatigersNLP/data_tigers_nlp/commit/670c43fd1533358b39a9ea70a3a5a5e3a85e2739). Prompt reconstruit : `agent0-hors-corpus-v2`. Sources et sélection conformes au corpus figé.
Les autres empreintes et les limites du contrôle figurent dans [le rapport](verification_archive.md). Aucun verdict humain n'est attribué.


## Sources complètes de référence

Les huit passages de référence proviennent des fichiers M2 au commit `36bb4e05094dbc68d1975f1d8ea01eac50de166b`. Les sources des 18 préparations reçues leur correspondent exactement. Cela ne limite pas à ces huit textes la vérification d'un cas hors corpus.
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

