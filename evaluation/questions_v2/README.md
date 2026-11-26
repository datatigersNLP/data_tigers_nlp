# Jeu de questions v2, synthétique (issue #171)

**Statut** : figé le 17 novembre 2026 et étiqueté `jeu-questions-v2`, avant qu'aucun système ne soit exécuté sur ses questions. Les règles sont celles du protocole 10 (`docs/etudes/evaluation/10_protocole_jeu_v2.md`), figé avant toute génération (commit `ffa0486`, SHA-256 `8d123613…`).

## Ce que ce jeu est, et ce qu'il n'est pas

- **Un jeu synthétique** : les questions ont été écrites par des sous-agents Claude Opus 5.5 et contrôlées par un juge Claude Fable 5.2, chacun dans un contexte neuf, sans accès au dépôt.
- **Une décision déclarée** : le README de `evaluation/questions/` réservait la génération par IA aux paires d'entraînement. Mahé a décidé le 17 novembre de s'en écarter, avec l'autorisation écrite de l'enseignant d'utiliser Claude pour générer des questions et évaluer (courriel conservé par Mahé, hors du dépôt).
- **Il ne remplace pas le jeu humain v1** (`evaluation/questions/`), qui reste la référence humaine et est mesuré à titre secondaire.
- **Pourquoi un jeu neuf** : le lot de test v1 a été lu par plus de six mesures ; toute comparaison nouvelle y est descriptive.

## Composition

- **161 questions** : 121 du corpus et 40 hors corpus, toutes au lot `test`.
- **Questions du corpus** : sur les 61 fiches du lot de test v1, exclues de tous les entraînements du projet (encodeurs ajustés et adaptation LoRA). Deux questions par fiche, sauf une fiche qui n'en a qu'une (`les-missions-et-les-prerogatives-de-linspection-du-travail`). Rangs retenus : 51 de rang 1, 49 de rang 2, 21 de rang 3.
- **Passage pertinent annoté** : le passage source (`passage_id`) ; l'extrait (`extrait`), recopié mot pour mot, permet d'appliquer la règle D4 comme au jeu v1.
- **Questions hors corpus** : 40, choisies dans l'ordre du générateur parmi les 59 qu'aucun des 10 premiers passages de la fusion E5 + BM25 ne couvrait, même en partie. Une candidate a été écartée parce qu'un passage sur le compte personnel de formation mentionnait l'âge de départ à la retraite. La règle « les 40 premières » donne surtout la fonction publique, la retraite, la fiscalité, la protection sociale, la famille et le logement ; la consommation et la micro-entreprise ne sont pas représentées. Ce contrôle ne porte que sur les 10 premiers passages : il ne prouve pas qu'aucun passage du corpus ne réponde (voir `docs/etudes/evaluation/10_resultats.md`, section 9).

## Contrôles

- **Contrôles mécaniques** (183 candidates) : une seule rejetée, pour proximité avec une question du jeu v1 (Jaccard au-dessus de 0,40). Tous les extraits sont présents mot pour mot dans leur passage et reconnus par la règle D4.
- **Juge de contrôle** (182 candidates) : toutes compréhensibles seules ; le passage répond pour 176 et en partie pour 6 ; l'extrait suffit pour 156. Les 26 refus portent surtout sur des extraits réduits à un élément de liste, sans la phrase qui le rend lisible.
- **Recouvrement lexical** entre la question et son extrait (indice de Jaccard sur les mots) : médiane 0,111 pour le jeu v2 (121 questions), contre 0,095 pour le jeu v1 (78 questions du corpus). Les questions générées reprennent un peu plus les mots de la réponse, ce qui peut avantager légèrement BM25.
- **Questions sur des références** : 5 questions du corpus portent sur des listes de textes ou de ressources (V016, V044, V082, V087, V095), parce que le tirage est tombé sur des passages de ce type.

## Limites

- **Circularité possible** : Claude a écrit ces questions, et une variante de l'encodeur (v3) est entraînée sur des questions de Claude. Les fiches sont disjointes et les modèles diffèrent, mais une proximité de style peut favoriser la v3. Le jeu v1 et le CDTN, écrits sans IA, servent de contrôle.
- **Un seul passage annoté par question** : le critère est un minorant, comme au jeu v1.
- **Style** : des questions concrètes et bien formées, plus régulières que de vraies questions d'utilisateurs.

## Fichiers

- `questions_v2.csv` : les colonnes du jeu v1, plus `passage_id`.
- `manifeste.json` : empreintes du protocole, du jeu et de tous les fichiers de travail (lots, sorties des générateurs, verdicts des juges, contrôles, journal de sélection), conservés dans `data/evaluation/jeu_v2/`, non versionné.
- Production : `scripts/evaluation/jeu_v2.py` (`tirer`, `controler`, `feuilles_juge`, `contexte_hors_corpus`, `assembler`, `recouvrement`) et ses tests, `test_jeu_v2.py`.
