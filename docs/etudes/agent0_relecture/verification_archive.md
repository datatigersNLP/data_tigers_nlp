# Vérification de l'archive Agent0 — 20 octobre 2026

**Les 93 fichiers attendus sont reçus et les contrôles de cohérence listés ci-dessous concordent.** Les 15 candidats sont encore `human: pending` ; aucune décision humaine n'est attribuée.
[Détails et empreintes](verification_archive.json) — [questions et sources](questions_et_sources.md) — [grille vierge](grille_relecture.json).

## Identification

- Archive : `agent0_relecture_20261020.zip` ; 202721 octets.
- SHA-256 : `e6cb410c6c8cbcdd9fb4f5392cab9fc41a32f74fe48dd3c49b0121326eb76f74`, identique à l'empreinte affichée sur le Legion.
- CRC ZIP, noms uniques et chemins relatifs vérifiés ; 18 dossiers de cinq fichiers et trois sélections.
- Les octets du ZIP et des originaux sont conservés. Seules des copies de travail ont été lues pour les contrôles ; les traces ne sont pas publiées dans Git.

## Contrôles exécutés

1. Lecture JSON sans clés dupliquées ni constantes hors JSON. Cohérence des manifestes, résumés, candidats, rejets et traces.
2. Comparaison des trois sélections avec leurs empreintes, le corpus M2 complet et la reproduction des tirages à graine 20261018. Groupes, ordre et valeurs des passages conformes.
3. Comparaison de 129 empreintes déclarées de scripts aux contenus Git de 13 commits, soit 21 blobs distincts. Les 129 concordances sont obtenues avec les fins de ligne CRLF de la copie Windows.
4. Reconstruction des 18 prompts à partir des fonctions de préparation versionnées et du schéma commun inchangé. Messages, schéma, version et empreinte du prompt conformes aux manifestes.
5. Vérification du texte raw system/user/assistant, de ses empreintes et de celle du gabarit ; modèle/digest/tokeniseur/révision, options et budget 8192/512/64 conformes. Les comptages rapportés HF/Ollama concordent, sans recomptage avec le vrai tokeniseur.
6. Comparaison des réponses brutes, métadonnées de fin et mesures aux résumés. Quinze candidats identiques aux enveloppes reproduites ; trois rejets reproduits avec les validateurs des commits déclarés.
7. Recoupement des 153 empreintes de fichiers antérieurs utilisées par la déduplication. Quatorze questions recopiées avant réception identiques aux originaux ; quinzième question récupérée dans `multi_passage_003`.
Les fonctions de préparation et validation ont été évaluées hors des imports opérationnels ; aucune API Ollama, génération ou tokenisation réelle n'a été appelée. Ce sont des contrôles sur les données reçues, pas une nouvelle campagne de tests unitaires.

## Versions déclarées et recoupées

| Run | Commit déclaré | Prompt | HF / Ollama → sortie |
|---|---|---|---|
| `simple_001` | [`823621b`](https://github.com/datatigersNLP/data_tigers_nlp/commit/823621b18535f245ad05bb99a762dbff39bc2ae0) | `agent0-simple-reformulation-v1` | 1259 / 1259 → 173 |
| `reformulation_001` | [`e6d6a64`](https://github.com/datatigersNLP/data_tigers_nlp/commit/e6d6a640769d394155940fdd13226199c5192001) | `agent0-simple-reformulation-v1` | 1284 / 1284 → 171 |
| `multi_passage_001` | [`53d4da2`](https://github.com/datatigersNLP/data_tigers_nlp/commit/53d4da2ec79588a1a241702088a98681233827d4) | `agent0-multi-passage-v1` | 1925 / 1925 → 438 |
| `multi_passage_002` | [`475aa90`](https://github.com/datatigersNLP/data_tigers_nlp/commit/475aa902fcfd70d980019433557959f3507c803b) | `agent0-multi-passage-v2` | 2023 / 2023 → 452 |
| `multi_passage_003` | [`824eaa1`](https://github.com/datatigersNLP/data_tigers_nlp/commit/824eaa12b9bbfca03e93aa7e3586615369139788) | `agent0-multi-passage-v3` | 2101 / 2101 → 429 |
| `multi_passage_004` | [`1f7eeca`](https://github.com/datatigersNLP/data_tigers_nlp/commit/1f7eeca8eea1014e959b7318079ae177d2980037) | `agent0-multi-passage-v3` | 1833 / 1833 → 404 |
| `multi_passage_005` | [`1f7eeca`](https://github.com/datatigersNLP/data_tigers_nlp/commit/1f7eeca8eea1014e959b7318079ae177d2980037) | `agent0-multi-passage-v3` | 2764 / 2764 → 373 |
| `multi_passage_006` | [`1f7eeca`](https://github.com/datatigersNLP/data_tigers_nlp/commit/1f7eeca8eea1014e959b7318079ae177d2980037) | `agent0-multi-passage-v3` | 2100 / 2100 → 385 |
| `adversarial_001` | [`0a22c0d`](https://github.com/datatigersNLP/data_tigers_nlp/commit/0a22c0d6229b699239cb77c03a299b1c754ef987) | `agent0-adversarial-v1` | 1450 / 1450 → 419 |
| `adversarial_002` | [`9f06371`](https://github.com/datatigersNLP/data_tigers_nlp/commit/9f063711a346643e895f0f8387dbffe648a79fb3) | `agent0-adversarial-v2` | 1509 / 1509 → 255 |
| `adversarial_003` | [`9133ffc`](https://github.com/datatigersNLP/data_tigers_nlp/commit/9133ffc6d26b6d3ae33bf8abd76ac776f9529641) | `agent0-adversarial-v3` | 2028 / 2028 → 372 |
| `adversarial_004` | [`9133ffc`](https://github.com/datatigersNLP/data_tigers_nlp/commit/9133ffc6d26b6d3ae33bf8abd76ac776f9529641) | `agent0-adversarial-v3` | 1866 / 1866 → 499 |
| `hors_corpus_001` | [`72ea697`](https://github.com/datatigersNLP/data_tigers_nlp/commit/72ea6979464be99554930f508b9ad4d90680bb30) | `agent0-hors-corpus-v1` | 1441 / 1441 → 156 |
| `hors_corpus_002` | [`c54561c`](https://github.com/datatigersNLP/data_tigers_nlp/commit/c54561c9b6832dfb30282229bfebdbfad13894e7) | `agent0-hors-corpus-v1` | 1883 / 1883 → 175 |
| `hors_corpus_003` | [`c54561c`](https://github.com/datatigersNLP/data_tigers_nlp/commit/c54561c9b6832dfb30282229bfebdbfad13894e7) | `agent0-hors-corpus-v1` | 1721 / 1721 → 167 |
| `hors_corpus_004` | [`670c43f`](https://github.com/datatigersNLP/data_tigers_nlp/commit/670c43fd1533358b39a9ea70a3a5a5e3a85e2739) | `agent0-hors-corpus-v2` | 1528 / 1528 → 184 |
| `hors_corpus_005` | [`670c43f`](https://github.com/datatigersNLP/data_tigers_nlp/commit/670c43fd1533358b39a9ea70a3a5a5e3a85e2739) | `agent0-hors-corpus-v2` | 1970 / 1970 → 222 |
| `hors_corpus_006` | [`670c43f`](https://github.com/datatigersNLP/data_tigers_nlp/commit/670c43fd1533358b39a9ea70a3a5a5e3a85e2739) | `agent0-hors-corpus-v2` | 1808 / 1808 → 185 |

Toutes les déclarations de code portent `git_dirty: false`, Python 3.12.15. Ollama 0.40.5 est déclaré jusqu'à `multi_passage_003`, puis 0.40.6 dans les runs suivants. Les versions détaillées figurent dans le JSON ; elles sont lues dans les traces reçues.

## Limites et relecture restante

- La concordance des empreintes et des traces établit une cohérence des données reçues avec les références versionnées, sans attestation indépendante de l'exécution sur la machine.
- Les appels du modèle et les comptages du vrai tokeniseur n'ont pas été rejoués ici ; aucune latence ou performance matérielle nouvelle n'est déduite.
- La nécessité/suffisance des sources, les prémisses, corrections et motifs d'absence restent à relire humainement. Aucun verdict, point attendu ou admission n'est créé.
- La grille conserve ses champs humains vierges, y compris le recoupement de provenance par le relecteur. Les informations techniques sont séparées.
- Ces essais ont servi à ajuster les prompts. Ils ne remplacent pas le pilote indépendant de #95 ou la vérification du corpus complet pour hors corpus.

