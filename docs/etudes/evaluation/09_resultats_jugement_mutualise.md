# Résultats du jugement mutualisé et des métriques à plusieurs passages

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** Issue #139  
**Protocole** `09_protocole_jugement_mutualise.md`, figé le 16 novembre 2026 avant tout jugement (commit `4473a43`, SHA-256 `95a825e8…`)  
**Statut** mesure du 16 novembre 2026, **provisoire** : les juges sont deux modèles d'IA, et l'étalonnage humain prévu par la section 5 du protocole n'est pas encore revenu. Toutes les mesures sont descriptives : aucune décision passée ne change  

---

## 1. En bref

* **La règle D4 sous-estime nettement tous les systèmes.** Avec la règle principale (les deux juges jugent que le passage répond), l'encodeur ajusté servi trouve un passage pertinent dans les 5 premiers pour 74,0 % des questions, contre 63,0 % selon D4 ; dans les 10 passages affichés par le site, pour 84,9 %, contre 74,0 %.
* **Le gain de l'ajustement résiste à la correction, mais rétrécit.** L'écart de l'ajusté à la base passe de +19,2 points selon D4 à +13,7 points [+3,2 ; +25,0] avec la règle principale. Avec la règle large (un passage qui répond en partie compte), il tombe à +1,4 point [-8,4 ; +11,4] : les deux encodeurs montrent presque toujours un élément de réponse, et l'ajusté se distingue surtout en trouvant le passage qui répond entièrement.
* **Dans le volet B, la récupération plafonne moins qu'on le croyait, et la génération pèse davantage.** Avec la règle principale, le contexte de B2 contient un passage pertinent pour 62,5 % des questions, et celui de la récupération v2 pour 89,0 %. Le modèle adapté n'en cite un que dans un cas sur deux environ : en V2, sur 35 échecs, 21 viennent du modèle (11 abstentions et 10 citations d'un autre passage alors qu'un passage pertinent est fourni), 6 du seuil d'abstention et 8 seulement de la récupération.
* **M4 corrigé** : 30,6 % pour B2 (25,0 % selon D4) et 52,1 % pour V2 (37,0 %). L'écart de V2 à B2 passe de +11,1 points (p = 0,077) à +20,8 points [+9,2 ; +32,9] (p = 0,0015). Cela ne change pas la décision du protocole 08, qui portait aussi sur M1 (18 sur 24 en V2 contre 20 sur 24 en B2).
* **Sur le CDTN**, le succès à 5 de l'ajusté (72,3 %) cache un rappel bien plus faible : seulement 32,7 % des passages pertinents d'une requête sont dans les 5 premiers, 46,8 % dans les 10 premiers, pour une médiane de 5 passages pertinents par requête. Le nDCG@10 vaut 41,5 % pour l'ajusté, 35,9 % pour la base et 35,0 % pour BM25.

---

## 2. Juges et fiabilité

| | J1 (Claude Opus 5.5) | J2 (Claude Sonnet 5.5) | Seuil du protocole |
|---|---:|---:|---|
| Contrôles positifs reconnus (répond ou en partie) | 40 sur 40 | 40 sur 40 | au moins 32 |
| dont jugés « répond » | 26 | 25 | |
| Contrôles négatifs acceptés | 0 sur 40 | 0 sur 40 | au plus 2 |
| Vivier : répond, en partie, ne répond pas | 40, 202, 375 | 50, 172, 395 | |

* **Les deux juges sont fiables** au sens du protocole, et tous deux sont retenus.
* **Accord sur les 617 paires du vivier** : 92,9 % d'accord brut, kappa de Cohen 0,861 [0,822 ; 0,898], 0,882 [0,848 ; 0,914] avec une pondération linéaire. C'est un accord élevé, mais entre deux modèles de la même famille, dont les erreurs peuvent être corrélées : seul l'étalonnage humain dira si cet accord vaut justesse.
* **D4 accepte déjà des passages partiels** : 14 à 15 des 40 contrôles positifs, tous pertinents selon D4, sont jugés « en partie » et non « répond ». D4 est un minorant par construction des majorants, qui la contiennent ; ce n'est pas une mesure de réponse complète.
* **Paires du vivier jugées pertinentes** : 37 par la règle principale, 246 par la règle large. L'écart vient du verdict « en partie », très fréquent : la règle large est généreuse, et la règle principale est le majorant à retenir.

---

## 3. Volet A, lot de test (73 questions du corpus)

Succès à k : part des questions dont au moins un passage pertinent figure dans les k premiers. Intervalles de Wilson à 95 %, corrigés de l'effet de plan par fiche annotée.

| | Base, minorant D4 | Base, majorant principal | Ajusté, minorant D4 | Ajusté, majorant principal | Ajusté, majorant large |
|---|---|---|---|---|---|
| Succès à 5 | 43,8 % [32,9 ; 55,4] | 60,3 % [49,0 ; 70,5] | 63,0 % [50,9 ; 73,6] | 74,0 % [62,4 ; 83,0] | 90,4 % [79,1 ; 95,9] |
| Succès à 10 | 57,5 % [45,8 ; 68,5] | 75,3 % [63,6 ; 84,2] | 74,0 % [62,2 ; 83,1] | 84,9 % [76,1 ; 90,9] | 97,3 % [90,9 ; 99,2] |
| Fiche à 5 | 83,6 % [73,0 ; 90,5] | 84,9 % [75,2 ; 91,3] | 86,3 % [76,5 ; 92,4] | 87,7 % [77,7 ; 93,6] | 95,9 % [85,7 ; 98,9] |

Avec la règle large, la base atteint 89,0 % de succès à 5 et 95,9 % à 10.

**Écart de l'ajusté à la base** (intervalle du score de Tango corrigé de l'effet de plan ; questions gagnées par l'ajusté seul et par la base seule ; McNemar exact) :

| Succès à 5 | Écart | IC 95 % | Gagnées / perdues | p |
|---|---:|---|---:|---:|
| Minorant D4 | +19,2 | [+9,7 ; +30,4] | 15 / 1 | 0,0005 |
| Majorant principal | +13,7 | [+3,2 ; +25,0] | 13 / 3 | 0,021 |
| Majorant large | +1,4 | [-8,4 ; +11,4] | 4 / 3 | 1 |

**Analyse des échecs à 5 passages** (échecs selon D4, règle principale) :

| | Base (41 échecs) | Ajusté (27 échecs) |
|---|---:|---:|
| Autre passage valable (un passage montré répond) | 12 | 8 |
| Bonne fiche, passage insuffisant | 18 | 10 |
| Mauvaise fiche | 11 | 9 |

**Lecture.** Sur les 27 questions que l'ajusté manque selon D4, 8 ont en fait un passage qui répond, 10 sont sur la bonne fiche sans passage suffisant, et 9 seulement sont de vrais échecs de recherche. Le site, qui affiche 10 passages regroupés par fiche, montre un passage qui répond pour 84,9 % des questions.

---

## 4. Volet B, lot de test (modèle adapté)

Questions du corpus sans erreur technique (72 en B2, 73 en V1 et V2). Plafond : part des questions dont le contexte contient un passage pertinent. M4 : réponse citée dont une citation renvoie à un passage pertinent ; c'est une mesure de **traçabilité**, pas d'exactitude.

| | B2 | V1 | V2 |
|---|---|---|---|
| Plafond, minorant D4 | 45,8 % | 72,6 % | 72,6 % |
| Plafond, majorant principal | 62,5 % | 89,0 % | 89,0 % |
| Plafond, majorant large | 90,3 % | 98,6 % | 98,6 % |
| M4, minorant D4 | 25,0 % [16,0 ; 36,9] | 32,9 % [23,1 ; 44,4] | 37,0 % [26,4 ; 48,9] |
| M4, majorant principal | 30,6 % [20,9 ; 42,3] | 43,8 % [34,0 ; 54,2] | 52,1 % [41,0 ; 62,9] |
| M4, majorant large | 44,4 % [33,3 ; 56,2] | 58,9 % [47,3 ; 69,6] | 68,5 % [56,9 ; 78,1] |
| M4 quand un passage pertinent est fourni (principal) | 48,9 % | 49,2 % | 58,5 % |

**Écarts appariés de M4** (Tango corrigé de l'effet de plan, McNemar exact) :

| | Minorant D4 | Majorant principal | Majorant large |
|---|---|---|---|
| V2 moins B2 | +11,1 [+0,2 ; +22,6], p = 0,077 | +20,8 [+9,2 ; +32,9], p = 0,0015 | +23,6 [+12,3 ; +35,7], p = 0,0002 |
| V1 moins B2 | +6,9 [-3,9 ; +18,2], p = 0,30 | +12,5 [+1,4 ; +24,1], p = 0,049 | +13,9 [+3,9 ; +25,2], p = 0,013 |
| V2 moins V1 | +4,1 [-5,5 ; +14,2], p = 0,55 | +8,2 [-3,0 ; +19,8], p = 0,21 | +9,6 [-0,2 ; +20,3], p = 0,092 |

**Analyse des échecs** (questions sans M4, règle principale) :

| | B2 (50) | V1 (41) | V2 (35) |
|---|---:|---:|---:|
| Récupération (aucun passage pertinent fourni) | 27 | 8 | 8 |
| Abstention du modèle, passage pertinent fourni | 16 | 23 | 11 |
| Abstention sous le seuil | 2 | 2 | 6 |
| Citation non pertinente, passage pertinent fourni | 5 | 8 | 10 |

**Lecture.** En B2, plus de la moitié des échecs (27 sur 50) viennent encore de la récupération. Avec la récupération v2, ils ne sont plus que 8 : les échecs restants tiennent surtout au modèle, d'abord à ses abstentions alors que le passage est fourni (23 en V1, 11 en V2), puis aux réponses qui citent un autre passage (8 et 10) ; le seuil d'abstention en ajoute 2 en V1 et 6 en V2. Ces chiffres sont descriptifs : le lot de test a déjà servi à la décision du protocole 08, qui garde B2 comme référence parce que V2 perd deux abstentions correctes hors corpus.

---

## 5. CDTN, métriques à plusieurs passages

494 formulations de 131 requêtes réelles, 5 passages pertinents par requête en médiane (de 1 à 22). Intervalles à 95 % par rééchantillonnage des requêtes.

| | Base | Ajusté | BM25 V3 | Ajusté moins base |
|---|---|---|---|---|
| Succès à 5 | 67,4 % [59,6 ; 74,5] | 72,3 % [64,6 ; 79,2] | 66,4 % [58,7 ; 73,6] | +4,9 [+0,8 ; +9,1] |
| Succès à 10 | 80,8 % [74,8 ; 86,1] | 82,8 % [77,1 ; 87,8] | 76,9 % [69,9 ; 83,2] | +2,0 [-0,6 ; +4,7] |
| Rappel à 5 | 28,2 % [22,8 ; 34,4] | 32,7 % [26,4 ; 39,5] | 27,6 % [22,2 ; 33,9] | +4,4 [+1,9 ; +7,5] |
| Rappel à 10 | 42,3 % [35,7 ; 49,3] | 46,8 % [39,8 ; 54,0] | 40,7 % [34,2 ; 47,5] | +4,5 [+2,3 ; +7,2] |
| nDCG@10 | 35,9 % [30,7 ; 41,3] | 41,5 % [35,8 ; 47,5] | 35,0 % [30,1 ; 40,1] | +5,6 [+3,5 ; +8,0] |
| Précision à 5 | 25,3 % [20,9 ; 30,5] | 28,4 % [23,8 ; 33,6] | 24,3 % [19,9 ; 29,1] | +3,0 [+1,5 ; +4,6] |

**Lecture.** Le succès à 5 dit si au moins un passage pertinent est trouvé ; le rappel dit quelle part des passages pertinents l'est. L'ajusté améliore toutes les métriques, et l'écart est net sur celles qui comptent tous les passages pertinents (nDCG@10 +5,6 points [+3,5 ; +8,0]). La précision est sous-estimée, car les jugements du CDTN de 2021 ne sont pas exhaustifs.

---

## 6. Contrôles

* **Gel** : le protocole a été figé et poussé avant le tirage du vivier ; le script refuse de tirer ou de mesurer si l'empreinte du protocole diffère.
* **Reproduction sous D4** : le calcul redonne exactement les chiffres publiés (A1, protocole 08, succès à 5 du CDTN à 10⁻¹² près) ; sinon, il n'écrit rien.
* **Deux exécutions** au contenu identique (SHA-256 `5df807de…`).
* **Recalcul indépendant**, hors du dépôt et sans importer le script de mesure : aucun écart sur les effectifs, les intervalles, l'accord, les analyses d'échecs et le CDTN. Sa sensibilité a été vérifiée : quatre erreurs injectées dans une copie de la mesure (un effectif, une borne d'intervalle, une valeur du CDTN, une case des échecs) sont toutes détectées.
* **Tests** : `test_jugement_139.py`, 17 tests, dont des tests sur données réelles qui contrôlent que les feuilles ne révèlent ni le système, ni le rang, ni l'adresse, ni la nature des paires ; 12 erreurs volontaires injectées, toutes détectées.

---

## 7. Limites

* **Juges d'IA, étalonnage en attente** : 100 paires (80 du vivier, 20 contrôles) sont à juger par deux membres de l'équipe. Si le kappa entre le consensus humain et la règle principale est inférieur à 0,6, les majorants seront déclarés non étayés.
* **Lot de test** : sixième exploitation ; tout est descriptif.
* **Traçabilité, pas exactitude** : un passage pertinent cité ne garantit pas une réponse juste. L'exactitude reste jugée par le #52, sur 20 réponses.
* **Non couverts** : le témoin T, les questions hors corpus, et le contrôle de l'ancrage des citations affirmation par affirmation.

---

## 8. Fichiers

Dans `data/evaluation/jugement_139/`, non versionné.

| Fichier | SHA-256 |
|---|---|
| `vivier.json` (clé, hors des feuilles) | `403e4245c92c66f26620086e8c77fa9f014863cd147dbbfd72d15e5a39a452ba` |
| `feuilles/lot_01.json` à `lot_07.json` | `25c9ba93…`, `56017c3d…`, `585785f6…`, `da40ba2d…`, `c579e8b9…`, `4b5d7dda…`, `a6d5adf9…` |
| `etalonnage/feuille_etalonnage.csv` | `602b1f76dc11d8c35b71e6ac2c108fa1d5c88488a0ce9ef60263cf863f5497f8` |
| `mesure_20261116T101733Z.json` et `mesure_20261116T101736Z.json` | `5df807de0a8c3e9cea65b621811e766fa02f1456300d06d70afa13e6d8ccb059` |

Les empreintes des 14 fichiers de verdicts sont inscrites dans la mesure.
