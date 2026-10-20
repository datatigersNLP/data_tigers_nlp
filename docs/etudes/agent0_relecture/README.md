# Agent0 Light — support de relecture des essais (#95)

Complété le 20 octobre 2026 à partir des originaux reçus. **18 runs, 15 candidats en attente et 3 rejets automatiques. Les 15 questions sont maintenant disponibles.**
L'archive correspond à l'empreinte affichée sur le Legion. Les contrôles de cohérence sont détaillés dans [le rapport](verification_archive.md).

## Parcours de relecture

1. Lire [les questions et sources](questions_et_sources.md), avec les formulations originales et les éléments proposés par le générateur.
2. Renseigner sa propre lecture dans [la grille distincte](grille_relecture.json) : personne, date, décision, preuves et justification. Toutes les décisions humaines sont vierges.
3. Consulter ensuite [les observations assistées](observations_assistees.md), relever accords/désaccords et compléter les recherches nécessaires.
4. Vérifier les doublons et la cohérence du lot avant toute admission. Une relecture distincte du code reste nécessaire avant fusion.

## Inventaire reçu et vérifié

| Catégorie | Candidats | Rejets automatiques |
|---|---:|---:|
| `simple` | 1 | 0 |
| `reformulation` | 1 | 0 |
| `multi_passage` | 4 | 2 |
| `adversarial` | 3 | 1 |
| `hors_corpus` | 6 | 0 |
| Total | 15 | 3 |

Les 15 candidats ont `human: pending` dans les fichiers reçus. Aucun nom de relecteur, note humaine ou point attendu n'y est attribué. Aucun hors corpus n'est confirmé.
La question de `multi_passage_003` et les extraits de `multi_passage_002`/`003` sont désormais complétés depuis les fichiers. Les 14 formulations déjà recopiées sont identiques aux originaux.
Les essais ont servi à mettre au point les prompts. Ils ne deviennent pas un pilote indépendant ou un échantillon représentatif après relecture.

## Archive et contrôle technique

- Fichier reçu : `agent0_relecture_20261020.zip`, 202721 octets.
- SHA-256 : `e6cb410c6c8cbcdd9fb4f5392cab9fc41a32f74fe48dd3c49b0121326eb76f74` ; identique à l'empreinte communiquée par Jibril.
- 93 fichiers attendus et reçus : cinq par run et trois sélections. CRC du ZIP vérifié.
- Sources et trois tirages conformes au corpus M2 figé ; 18 prompts reconstruits, 18 validations historiques reproduites.
- 129 déclarations d'empreintes de code retrouvées dans 13 commits et 21 blobs Git, avec fins de ligne CRLF ; 153 empreintes d'antécédents de déduplication concordantes.
- Comptages HF/Ollama rapportés concordants pour les 18 réponses. Aucun recomptage avec le vrai tokeniseur ni appel Ollama ici.
- [Rapport lisible](verification_archive.md) et [détails/empreintes des 93 fichiers](verification_archive.json). Les traces intégrales restent hors Git.
La collecte initiale reste tracée dans [la version précédente du README](https://github.com/datatigersNLP/data_tigers_nlp/blob/94b9ae0e4776686daedf4ee900feb03b852dbeeb/docs/etudes/agent0_relecture/README.md). L'archive déjà reçue n'a pas été modifiée.
Ce contrôle établit la cohérence des originaux et des déclarations reçues avec les références versionnées. Il ne constitue pas une attestation indépendante de l'exécution sur le Legion ni une validation du sens des questions.

## Référence documentaire

- Corpus M2 : 4240 passages, 261 fiches.
- SHA-256 entête : `586cf190293d206e4b9affd72cd37a23c367d34537b0c831305f66084084ee23`.
- SHA-256 passages : `aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d`.
- [sources_m2.json](sources_m2.json) conserve huit passages complets, identiques aux fichiers versionnés et aux sources reçues. Ce n'est pas le corpus complet.
- Les questions et champs proposés sont copiés depuis les `candidates.jsonl` reçus ; leur concordance avec les propositions brutes a été contrôlée. Aucune question n'est réécrite.

## Comment décider

Relire la question originale, sa catégorie proposée et les passages complets. Vérifier suffisance, conditions, exceptions et doublons sémantiques ; la difficulté reste une cible.
Pour multi_passage, les sources doivent être toutes deux nécessaires et suffisantes. Pour adversarial, vérifier la prémisse dans la question et la correction. Pour hors_corpus, vérifier le corpus figé complet et tracer méthodes, termes/variantes, passages examinés et limites.
La grille de travail permet `accepted`, `rejected` ou `uncertain` après une relecture effective. `uncertain` est propre à ce support : le candidat reste `pending`. Un cas mal classé doit être rejeté, sans changer la question ou son type pour sauver le cas.
Les résultats techniques sont renseignés séparément dans la grille. Les champs `originaux_et_provenance_verifies`, relecteur, date et décision restent à remplir par le relecteur humain. Ils ne sont pas cochés automatiquement à partir du rapport.
Avant toute transcription vers une copie revue, respecter `ValidationCas` : en attente, aucun verdict/relecteur/note/point attendu dans `validation`. Une décision humaine effective doit avoir un nom et une note ; une acceptation exige un verdict de répondabilité et des points attendus uniquement pour une réponse possible.
Conserver la question, l'original et la trace de toute édition. Les notes provisoires restent dans le support distinct ; aucun outil d'application automatique n'est fourni.
Les objectifs de #95 ne sont pas des quotas d'acceptation. Les cas non confirmés restent à part et ne servent pas à calculer la qualité du lot. Aucun travail de relecture n'est attribué à Mahé ou Remy sans intervention réelle.

## État et suite

Le dossier est complet pour commencer la relecture humaine de ces essais. Les décisions restent à prendre ; aucun lot de 25 nouveaux candidats ou manifeste d'évaluation n'est figé.
Les relecteurs peuvent recouper les fichiers d'origine dans l'archive transmise hors Git. Les questions de ce support restent distinctes du futur pilote indépendant.
#94 et #95 restent partielles ; #103 et #106 restent en brouillon. Aucun candidat, rejet ou verdict d'origine modifié, aucune génération ou évaluation du RAG, fusion ou clôture.
Ce dossier reste dans `docs/`, sans modification du Gold Set humain ou de `evaluation/synthetic/`. Estimation initiale #95 : 4 h prévisionnelles inchangée ; aucun temps réel déclaré.

