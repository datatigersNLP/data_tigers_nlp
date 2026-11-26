# Protocole 10 : résultats des familles A, B et E

**Date** : 17 novembre 2026 ; complété le 21 novembre (sections 6 et 7 bis) et le 22 novembre (section 4, renoncement au #173). **Tickets** : #167, #171, #172, #173. **Règles** : protocole 10 (`10_protocole_jeu_v2.md`, figé avant toute génération, commit `ffa0486`, SHA-256 `8d123613…`). **Jeu** : `evaluation/questions_v2/questions_v2.csv`, étiquette `jeu-questions-v2` (`8bfd9fb`). **Auteur** : Mahé BEGNIS.

---

## 1. Objet et état

Cette page publie les familles de mesures du protocole 10, section 7, au fur et à mesure, et l'effet du nombre de passages demandé par l'enseignant :

* **Famille A** : la fusion de la recherche dense du site avec BM25 V3, candidate pour le volet A (#173).
* **Famille B, récupération** : la récupération du volet B, R0, R1 et R2, et la règle qui décide de la chaîne de démonstration (#172).
* **Famille E** : les encodeurs candidats pour le volet A (#167), la v2-T (section 7) et la v3-C (section 7 bis). Aucun n'est servi ; la v1 reste l'encodeur du site.

Les mesures sont faites par `scripts/evaluation/mesures_10.py` (commandes `famille_a`, `famille_b`, `effet_k`, `famille_e` et `famille_e_a3`). Chaque fichier de résultats est écrit une seule fois dans `data/evaluation/protocole_10/`, non versionné ; ses empreintes sont en section 10.

---

## 2. Écarts déclarés avant les résultats

* **Extraits courts du jeu v2** : la règle D4 exige un extrait d'au moins 80 caractères normalisés. 14 extraits du jeu v2 sur 121 sont plus courts. Pour eux, un passage est pertinent s'il contient l'extrait entier, normalisé avec ou sans les marques de liste : c'est plus strict que D4. Décidé avant tout résultat, codé dans `PertinenceV2`. Une analyse de sensibilité garde le seul passage source comme passage pertinent.
* **Requête de R2** : le protocole définit R2 comme la récupération v2 avec l'encodeur ajusté v1. La question est encodée ici par le q8 élagué que sert le site, avec onnxruntime en Python : c'est le choix de production du 17 novembre, pris avant la mesure, parce que les poids fp32 de l'ajusté (470 Mo) ne sont pas versionnés. La requête fp32 de la démonstration du 16 novembre est mesurée en sensibilité.
* **R0 avec le seuil S** : B2 s'abstient quand le cosinus maximal d'E5 est sous S = 0,8565. R0 est mesuré sans ce seuil, comme au protocole 07 ; la variante avec seuil, où une question refusée a un contexte vide, est descriptive.

---

## 3. Contrôles

* **Famille A, reproduction du protocole 05** : D, recalculé sur le CDTN (131 requêtes, 494 formulations), redonne question par question le Recall@5 publié de l'ajusté, 72,27 %.
* **Famille B, reproduction du protocole 07** : R0 et R1, recalculés sur la population « questions » du CDTN, redonnent formulation par formulation le rappel du contexte de la grille du 9 novembre : 70,89 % (`e5+k5`) et 85,05 % (`rrf+k10+bge-m3@20`). Les listes BM25 V3 recalculées sont identiques à celles du cache.
* **Famille B, reproduction de la confirmation du 9 novembre** : sur le lot de test du jeu v1, R0 et R1 redonnent exactement 45,2 % et 72,6 %.
* **Reclasseur** : les scores de 100 paires renotées d'un seul appel diffèrent du cache du protocole 07 de 0,00000051 au plus ; les écarts de lot n'ont pas d'effet sur l'ordre.
* **Requête q8 en Python** : sur les 161 questions du jeu v2, cosinus avec les vecteurs du navigateur de 0,98957 au minimum (médiane 0,99447). Le Recall@5 dense est le même avec les deux, 57,0 %.
* **Budget** : aucun contexte n'est tronqué ; le plus long compte 5 658 tokens, pour un plafond de 7 616.

---

## 4. Famille A : fusion du volet A

D est la recherche dense servie par le site (encodeur ajusté v1, requête q8 encodée dans le navigateur, index fp32). F est la fusion RRF de D et de BM25 V3. Critère principal : Recall@5 au passage. Secondaire : une fiche pertinente parmi les fiches des 10 passages affichés.

| Jeu | Questions (groupes) | Recall@5 D | Recall@5 F | Écart F moins D [IC 95 %] | F seul, D seul | McNemar exact |
|---|---:|---:|---:|---:|---:|---:|
| Jeu v2 | 121 (61 fiches) | 57,0 % | 62,0 % | +5,0 [−3,2 ; +13,4] | 14, 8 | p = 0,286 |
| Jeu v2, source seule | 121 (61 fiches) | 54,5 % | 59,5 % | +5,0 [−2,5 ; +12,7] | 13, 7 | p = 0,263 |
| CDTN | 494 (131 requêtes) | 72,3 % | 74,9 % | +2,6 [−1,4 ; +6,7] | 39, 26 | p = 0,136 |
| Jeu v1, lot de test (descriptif) | 73 (61 fiches) | 63,0 % | 56,2 % | −6,8 [−18,2 ; +4,1] | 5, 10 | p = 0,302 |

Fiche pertinente parmi les 10 passages affichés : 89,3 % contre 95,0 % sur le jeu v2 (+5,8 [+0,5 ; +12,2], 9 contre 2, McNemar exact p = 0,065) ; 93,1 % contre 94,1 % sur le CDTN (+1,0 [−0,9 ; +3,0]) ; 93,2 % contre 90,4 % sur le jeu v1.

* **Décision, par la règle de la section 7** : F est adoptée, car ses écarts sont positifs sur le jeu v2 et sur le CDTN.
* **F n'est pas dite meilleure** : les deux intervalles de Tango contiennent 0.
* **Le jeu humain va en sens inverse** : sur le lot de test du jeu v1, écrit par l'équipe sans IA, F perd 6,8 points (5 contre 10 questions). Ce lot a déjà été lu par plusieurs mesures, ce résultat est donc descriptif ; il pèse néanmoins contre une conclusion favorable à F.
* **Lecture** : les questions du jeu v2 sont générées à partir d'un passage et en reprennent un peu plus les mots (indice de Jaccard médian 0,111, contre 0,095 au jeu v1), ce qui avantage BM25. Le gain de F sur le jeu v2 est donc à lire comme un majorant.
* **Conséquence pour le #173** : la fusion dans le navigateur est permise par la règle mais pas démontrée utile. Elle ne devait être implémentée que si le temps le permettait avant le gel du 20 novembre, avec un test de parité entre Python et JavaScript.
* **Renoncement, le 21 novembre** (décision de Mahé) : la fusion n'est pas portée sur le site. Aucun gain n'est démontré, et le jeu humain va en sens inverse. Le site garde la recherche dense de l'encodeur ajusté v1.

---

## 5. Famille B : récupération du volet B

* **R0** : l'E5 de base, 5 passages (chaîne B2).
* **R1** : la fusion RRF de l'E5 de base et de BM25 V3, les 20 premiers candidats reclassés par bge-reranker-v2-m3, 10 passages dans le budget (V1, configuration retenue par le protocole 07).
* **R2** : la même, avec l'encodeur ajusté v1 pour la partie dense (démonstration depuis le 16 novembre).

Critère : la part des questions dont le contexte contient un passage pertinent. Sur le jeu v2, la pertinence suit D4 et la section 2 ; sur le CDTN, ce sont les passages pertinents du jeu CDTN, moyenne par requête puis sur les requêtes, comme au protocole 07.

| Rappel du contexte | Jeu v2 (121 questions) | CDTN (82 requêtes, 363 formulations) | Jeu v1, lot de test (73, descriptif) |
|---|---:|---:|---:|
| R0, E5 de base, 5 passages | 57,0 % | 70,9 % [62,9 ; 79,2] | 45,2 % |
| R0 avec le seuil S (descriptif) | 55,4 % (5 refus) | non mesuré | 43,8 % (2 refus) |
| R1, fusion et reclasseur, E5 de base | 86,0 % | 85,1 % [78,5 ; 91,2] | 72,6 % |
| R2, fusion et reclasseur, E5 ajusté | 84,3 % | 84,6 % [77,6 ; 91,0] | 75,3 % |
| R2, requête fp32 (sensibilité) | 83,5 % | non mesuré | non mesuré |
| Tokens du prompt, moyenne R0, R1, R2 | 1 714, 4 053, 4 128 | 1 657, 3 889, 3 947 | 1 672, 4 004, 4 043 |

| Écart | Jeu v2 [IC 95 % de Tango] | Discordants | McNemar exact, Holm | CDTN [IC 95 % bootstrap] |
|---|---:|---:|---:|---:|
| R2 moins R1 | −1,7 [−6,3 ; +2,3] | 1, 3 | p = 0,625 | −0,5 [−2,0 ; +0,6] |
| R1 moins R0 | +28,9 [+20,5 ; +38,0] | 37, 2 | p < 0,001 | +14,2 [+8,9 ; +19,9] |
| R2 moins R0 | +27,3 [+19,0 ; +36,2] | 35, 2 | p < 0,001 | +13,7 [+7,9 ; +19,8] |

Sur le jeu v1 (descriptif) : R2 moins R1, +2,7 [−2,5 ; +9,5] (2 contre 0) ; R1 moins R0, +27,4 [+15,9 ; +39,4] (22 contre 2).

* **Décision, par la règle de maintien de la section 7** : R2 n'est pas maintenue, car son rappel du contexte est inférieur à celui de R1 sur le jeu v2 (84,3 % contre 86,0 %) et sur le CDTN (84,6 % contre 85,1 %). La démonstration revient à R1.
* **Les écarts entre R1 et R2 sont faibles et non significatifs** : 1 question contre 3 sur le jeu v2. La règle tranche sur les estimations ponctuelles, comme elle l'annonçait ; elle ne dit pas que l'encodeur ajusté dégrade la récupération.
* **Le gain de la récupération v2 sur B2 est large et démontré** sur les trois jeux : +28,9 points sur le jeu v2, +14,2 sur le CDTN, +27,4 sur le jeu v1, tous significatifs après correction de Holm.
* **Lecture** : l'avantage de l'encodeur ajusté en recherche dense seule (protocole 05) ne survit pas à la fusion avec BM25 et au reclasseur, qui rattrapent les passages que l'E5 de base classe mal. Sur le jeu v2, l'ajusté et la base ont d'ailleurs le même Recall@5 dense (69 questions sur 121 chacun, 9 succès propres à chacun).
* **Conséquence pour le #172** : la chaîne de production sert R1 par défaut ; R2 reste disponible en option.

---

## 6. Famille B de bout en bout

R2 n'étant pas maintenue, la chaîne de démonstration est R1 : la mesure de bout en bout compare, sur les 161 questions du jeu v2, le modèle adapté en B2 (R0, 5 passages, consigne v1, seuil S) au modèle adapté dans R1 (10 passages, consigne v1, sans seuil), puis le témoin T dans R1. Conditions du protocole : Mac de Mahé, Ollama 0.40.13, modèles et digests du #52, température nulle, une exécution par état ; métriques M1 à M5 et règles de `scripts/rag/mesure.py`, pertinence de la section 2.

* **Écart déclaré, dates** : B2 a été exécuté le 17 novembre ; R1 avec le modèle adapté, interrompu le même jour par la fin de la session sans qu'aucun fichier soit écrit, a été repris le 21 novembre, suivi du témoin T. Même Mac, même version d'Ollama, mêmes digests ; les contextes de R1 sont contrôlés contre ceux de la section 5 avant toute génération.
* **Écart déclaré, durées** : pendant les exécutions du 21 novembre, la machine construisait aussi les diapositives ; les durées sont descriptives et peuvent en être un peu allongées.
* **Erreurs techniques** : 1 sur 161 en B2 (V036) ; 3 sur 161 dans chaque état de R1 (V022, V114, V122). Ce sont toutes des écarts entre le nombre de tokens compté par Ollama et par le tokeniseur de référence, sous le plafond de 5 %. Ces questions sont retirées des comparaisons qui les concernent.

| Sur les questions sans erreur | B2, modèle adapté | R1, modèle adapté | R1, témoin T |
|---|---:|---:|---:|
| M1, abstention correcte hors corpus | 39 sur 40 (97,5 %) | 39 sur 39 (100 %) | 38 sur 39 (97,4 %) |
| M2, abstention à tort sur le corpus | 57 sur 120 (47,5 %) | 33 sur 119 (27,7 %) | 91 sur 119 (76,5 %) |
| M3, réponse citée valide | 63 sur 120 (52,5 %) | 86 sur 119 (72,3 %) | 19 sur 119 (16,0 %) |
| M4, réponse citant un passage pertinent | 43 sur 120 (35,8 %) | 63 sur 119 (52,9 %) | 12 sur 119 (10,1 %) |
| M5, réponse hors corpus | 1 sur 40 | 0 sur 39 | 1 sur 39 |
| Durée par question, médiane | 4,9 s | 11,8 s | 11,9 s |
| Tokens du prompt, médiane | 1 722,5 | 4 121 | 4 121 |

| Comparaison appariée, sur la population commune | Écart de M4 [IC 95 %] | Discordants | McNemar exact, Holm | M1 |
|---|---:|---:|---:|---:|
| R1 adapté moins B2 adapté (118 questions, 39 hors corpus) | +16,9 [+6,4 ; +27,3] | 31, 11 | p = 0,003 | 39 contre 38 |
| R1 témoin moins R1 adapté (119 questions, 39 hors corpus) | −42,9 [−52,8 ; −32,5] | 3, 54 | p < 0,001 | 38 contre 39 |

* **Décision, par le critère de la section 7** : avec le modèle adapté, la chaîne de démonstration améliore M4 de 16,9 points sur B2, et la borne basse de l'intervalle dépasse 0 : l'amélioration est démontrée. M1 ne baisse pas : 39 abstentions correctes sur 39, contre 38, sur des questions hors corpus au sens du protocole (section 9). La chaîne R1 est confirmée pour la démonstration.
* **L'adaptation est décisive dans cette chaîne** : le témoin T, dans les mêmes conditions, s'abstient à tort sur 76,5 % des questions du corpus et ne cite un passage pertinent que pour 10,1 % d'entre elles.
* **Le coût est la durée** : 10 passages et un reclasseur font passer la durée médiane de 4,9 à 11,8 secondes par question.
* **Limites** : le jeu v2 est synthétique ; M4 mesure la traçabilité d'une réponse, pas son exactitude ; un seul passage est annoté par question ; M1 porte sur des questions hors corpus au sens du protocole, sans preuve qu'aucun passage du corpus n'y réponde (section 9).

---

## 7. Famille E : encodeur v2-T

La v2-T reprend la recette de l'encodeur ajusté v1 avec 2 289 paires d'entraînement au lieu de 109, dont les questions sont générées par le témoin T (amendement A2 du protocole 05, #167). L'amendement a été figé le 17 novembre (commit `2008338`, SHA-256 `e522a434…`), avant toute mesure de la v2 ; à ce gel, ses jeux de décision ont été alignés sur ce protocole. Recherche dense seule, aux conditions du site : vecteurs des questions calculés dans Chrome 155 par le q8 complet, index fp32 de chaque encodeur.

| Recall@5 | Questions (groupes) | v1, servie | v2-T | Écart [IC 95 %] | v2-T seule, v1 seule | McNemar exact |
|---|---:|---:|---:|---:|---:|---:|
| Jeu v2 | 121 (61 fiches) | 57,0 % | 62,8 % | +5,8 [−2,1 ; +14,0] | 15, 8 | p = 0,210 |
| CDTN | 494 (131 requêtes) | 72,3 % | 72,3 % | 0,0 [−4,3 ; +4,3] | 32, 32 | p = 1,000 |
| Lot de test du jeu v1 (descriptif) | 73 (61 fiches) | 63,0 % | 57,5 % | −5,5 [−15,9 ; +4,4] | 4, 8 | p = 0,388 |

* **Contrôles** : la v1 redonne le Recall@5 du protocole 05 sur le CDTN ; `ajustement_v2.py mesurer`, exécuté deux fois avec un contenu identique, redonne les mesures du 15 novembre de la base et de la v1 (contrôle A1 conforme) ; empreintes du q8, de l'index et du garde-fou contrôlées.
* **Règle de l'amendement A2 sur le jeu v2 et le CDTN** : les deux écarts sont positifs ou nuls et l'un est strictement positif ; la règle retient la v2-T. Elle n'est pas dite meilleure : l'intervalle sur le jeu v2 contient 0, et le CDTN donne une égalité exacte.
* **Le jeu humain va en sens inverse** : −5,5 points sur le lot de test (4 questions contre 8). Ce lot a été lu plusieurs fois, ce résultat est descriptif ; il pèse néanmoins contre un gain réel.
* **Lecture** : le seul écart positif vient du jeu v2, dont les questions sont générées à partir d'un passage, comme les paires d'entraînement de la v2-T. Plus de questions synthétiques de T n'ont pas amélioré la v1 sur les questions écrites par des humains.
* **Mise en service** : la v2-T n'est pas servie. Le 21 novembre, Mahé a décidé de mesurer plutôt la v3-C (amendement A3, section 7 ; section 7 bis de cette page).

---

## 7 bis. Famille E : encodeur v3-C (amendement A3)

La v3-C reprend la recette et les 2 720 passages de la v2-T ; seules les questions changent. Elles sont écrites par des sous-agents Claude Sonnet (`claude-sonnet-5-5`), un par lot de 42 ou 43 passages, et relues par deux juges Claude Opus (amendement A3 du protocole 05, #167). L'amendement, audité trois fois par un sous-agent Claude Opus indépendant, a été figé le 21 novembre avant toute génération (commit `3d52395`, SHA-256 `432fa7c7…`), avec le code de cette mesure (`famille_e_a3`, commit `b033277`) et une règle de mise en service plus stricte que celle de l'amendement A2.

* **Génération et relecture** : 64 lots, 66 appels contrôlés dans leurs journaux ; 2 lots relancés une fois pour un identifiant de passage mal recopié. Après filtres, 2 420 paires d'entraînement et 275 de validation. Les deux juges trouvent les mêmes 3 paires fausses sur 30 (kappa 1,0), à la limite de la règle.
* **Entraînement et garde-fou** : 304 pas en 946 secondes (4 fils de calcul), poids `921e8520…`. Garde-fou passé : Recall@5 de 96,7 % contre 93,1 % pour la v1 sur les questions de validation, écrites par le même générateur que l'entraînement.
* **Hébergement** : l'export rejoué sur la v1 redonne bit à bit les fichiers livrés ; q8 `3d5a24e6…` (cosinus minimal 0,9946 avec le fp32) ; élagage sans perte (935 sorties identiques bit à bit) ; index `ef475c9c…`, dont le code redonne bit à bit l'index de la v2-T.

| Recall@5 | Questions (groupes) | v1, servie | v3-C | Écart [IC 95 %] | v3-C seule, v1 seule | p de décision ; p de Holm |
|---|---:|---:|---:|---:|---:|---:|
| Jeu v2 | 121 (61 fiches) | 57,0 % | 69,4 % | +12,4 [+5,5 ; +20,3] | 18, 3 | 0,0015 ; 0,006 |
| CDTN | 494 (131 requêtes) | 72,3 % | 70,0 % | −2,2 [−6,6 ; +2,0] | 25, 36 | 0,289 ; 0,630 |
| Lot de test du jeu v1 | 73 (61 fiches) | 63,0 % | 57,5 % | −5,5 [−14,7 ; +2,7] | 2, 6 | |

La valeur p de décision est la plus grande de celle du test exact de McNemar et de celle du test groupé d'Obuchowski ; la correction de Holm porte sur quatre hypothèses, la v2-T et la v3-C, chacune sur le jeu v2 et le CDTN.

| Hors corpus, sous la borne de la zone grise (dont refusées) | Questions | v1, seuils servis | v3-C, seuils recalculés |
|---|---:|---:|---:|
| Jeu v2 | 40 | 39 (33) | 39 (28) |
| Lot de test du jeu v1 | 24 | 23 (10) | 18 (6) |

* **Contrôles**, tous conformes : la v1 redonne le Recall@5 du protocole 05 sur le CDTN ; la v2-T redonne exactement la mesure du 17 novembre ; la fonction des seuils redonne exactement les seuils servis de la v1 ; le code de mesure est celui du gel, la seule modification admise (la ligne `ajuste_v3` de la page d'encodage) étant contrôlée ; deux exécutions donnent des résultats identiques, et la décision est prise à la seconde.
* **Règle de l'amendement A3** : condition a (garde-fou) satisfaite ; b non, l'écart sur le CDTN est négatif ; c non, le gain n'est démontré que sur le jeu v2, avec un écart négatif sur le CDTN ; d non, recul sur le lot de test ; f non, 5 questions hors corpus de plus au-dessus de la borne sur le lot de test. **La v3-C n'est pas servie ; la v1 reste l'encodeur du site.**
* **Lecture** : la v3-C gagne nettement sur le jeu v2, le seul jeu écrit par Claude, comme ses paires d'entraînement ; elle ne gagne ni sur le CDTN ni sur les questions humaines, où elle recule à titre descriptif. Le gain observé tient au style des questions générées, pas à une meilleure recherche pour de vrais utilisateurs : c'est la circularité que la condition c devait écarter. Avec la v2-T, deux encodeurs entraînés sur plus de 2 000 questions synthétiques ne font pas mieux que la v1, entraînée sur 109 questions.
* **Seuils** : comme la v2-T, la v3-C répartit ses scores bien plus bas que la v1 (5e centile du CDTN 0,354 contre 0,768 ; 25e centile 0,464 contre 0,814). Ses seuils auraient dû être recalculés avant tout service.

---

## 8. Pourquoi 10 passages au lieu de 5

Le volet B donnait 5 passages au modèle (B2) ; la récupération v2 lui en donne 10, et le site du volet A en affiche 10 depuis le 15 novembre (#164). Le choix a été fait par l'amendement A1 du protocole 07, le 9 novembre, avant la lecture des résultats des reclasseurs (commentaire du #138). La grille sans reclasseur venait de montrer que le nombre de passages était le levier le plus fort : sur le CDTN, l'E5 de base passait de 70,9 % à 77,6 % de 5 à 10 passages. La règle initiale, qui maximisait le rappel, aurait toujours choisi le plus grand k de la grille, 15. k = 10 a donc été fixé d'avance, pour deux raisons qui ne tiennent pas aux résultats : le budget du prompt (5 101 tokens au plus sur le CDTN, pour un plafond de 7 616) et un écart limité aux contextes de 5 passages sur lesquels l'adaptateur du volet B a été entraîné. Les mesures confirment le constat : plus de passages pertinents entrent dans le contexte avec 10 passages qu'avec 5.

Effet de k seul, à récupération égale (descriptif ; `mesures_10.py effet_k`, et grille du protocole 07 pour le CDTN). Passer de 5 à 10 passages ne peut pas retirer un passage pertinent : aucune question n'est perdue, et l'écart compte les questions gagnées.

| Rappel du contexte, 5 puis 10 passages | Jeu v2 (121) | Jeu v1, lot de test (73) | CDTN, questions (82 requêtes) |
|---|---:|---:|---:|
| E5 de base | 57,0 % puis 66,1 % (11 gagnées) | 45,2 % puis 58,9 % (10 gagnées) | 70,9 % puis 77,6 % |
| Fusion RRF sans reclasseur | 66,9 % puis 76,9 % (12 gagnées) | 57,5 % puis 68,5 % (8 gagnées) | 70,7 % puis 83,5 % |
| R1, fusion et bge-m3 | 81,0 % puis 86,0 % (6 gagnées) | 68,5 % puis 72,6 % (3 gagnées) | 78,5 % puis 85,1 % |

* **Le gain de k est réel pour chaque récupération** : de 4 à 14 points selon le jeu et la méthode. Il est plus faible après le reclasseur, qui remonte déjà les bons passages dans les 5 premiers.
* **Ce qu'il coûte** : sur le CDTN, pour la chaîne retenue, 3 953 tokens de prompt en moyenne contre 2 179 à 5 passages, et une précision du contexte qui passe de 31,4 % à 23,4 % (part des passages donnés au modèle qui sont pertinents). Le modèle doit donc écarter plus de passages hors sujet ; c'est ce que mesure la famille B de bout en bout.
* **Pourquoi pas 15** : avec l'E5 de base, 15 passages donnent 85,9 % sur le CDTN, mais 4 805 tokens en moyenne et 6 889 au plus, près du plafond de 7 616 ; la fusion et le reclasseur atteignent un rappel voisin, 85,1 %, avec 10 passages et 3 953 tokens.
* **Volet A** : afficher 10 passages au lieu de 5, regroupés par fiche, fait gagner 6,8 points au rappel à la fiche sur le lot de test (5 questions gagnées, `05_resultats_ajustement.md`, section 4), au prix de 4,0 fiches à lire en moyenne au lieu de 2,4.

---

## 9. Limites

* **Le CDTN n'est pas neutre entre R1 et R2** : la configuration de R1 a été choisie sur ce jeu par le protocole 07. Seul le jeu v2 est indépendant pour cette comparaison ; il donne le même sens.
* **Questions générées par Claude** : proches du style d'un générateur, et un peu plus proches des mots du passage que les questions humaines. Le jeu v1 et le CDTN, écrits sans IA, servent de contrôle ; sur la famille A, le jeu v1 ne confirme pas le jeu v2, et sur la famille E, la v3-C, entraînée sur des questions de Claude, n'est démontrée meilleure que sur le jeu v2.
* **Un seul passage annoté par question au jeu v2** : les critères sont des minorants.
* **Questions hors corpus au sens du protocole, pas prouvées hors corpus** : une question est retenue si un juge d'IA ne trouve de réponse, même partielle, dans aucun des 10 premiers passages de la fusion E5 + BM25, sans reclasseur (protocole 10, section 4). Ce contrôle ne porte que sur ces 10 passages : il ne prouve pas qu'aucun des 4 240 passages ne réponde. M1 (« 39 abstentions correctes sur 39 ») mesure donc l'abstention sur des questions très probablement hors corpus ; une abstention sur une question qu'un passage non examiné couvrirait serait comptée correcte à tort. Remarque de Jibril sur la PR #174 (23/11) ; le jeu, gelé, n'est pas modifié.
* **Puissance** : 121 questions et 61 fiches ne permettent de détecter que des écarts de plusieurs points ; une égalité à deux points près n'est pas exclue entre R1 et R2.

---

## 10. Fichiers et empreintes

* `data/evaluation/protocole_10/famille_a_20261117T125533Z.json` : SHA-256 `4c7d40c72d0a394c5a0fd162f6dc154886495ff74fa5bc568c27f17cc423918d`.
* `data/evaluation/protocole_10/famille_b_20261117T131518Z.json` : SHA-256 `67c1b3ac2e7ead1b9c278e75e3646d314a43a37e0e05730f387626d13bccfba2`. Il contient, pour chaque question du jeu v2, les passages du contexte de chaque état.
* `data/evaluation/protocole_10/reclasseur_bge-m3_famille_b.json` : cache des scores du reclasseur, qui grandit à chaque mesure ; ce n'est pas un résultat. La famille B y a calculé 5 080 paires, dont 219 pour compléter les candidats de R2 sur le CDTN ; un score n'y est jamais recalculé.
* `data/evaluation/protocole_10/effet_k_20261117T131939Z.json` : SHA-256 `9cb00fe577f5a19bffba1b78324f1ecfb22a8a8578100b5a712a561bc2a7b517`.
* `data/evaluation/protocole_10/famille_e_20261117T134023Z.json` : SHA-256 `13c474b82fc6d41eb200619b899cad822991106bfe78faaa824417d72a93f231`. Mesure descriptive de l'amendement A2 : `data/evaluation/ajustement_v2/mesure_20261117T134055Z.json`, SHA-256 `7d0065b711848d637ba4dc18e3d9a917729a616d18b9bad704940027cf3706fd` (seconde exécution identique).
* `data/evaluation/protocole_10/famille_e_a3_20261121T162950Z.json` (première exécution) : SHA-256 `22376e298437624126cafbc6be61ae3aa7e595000074e8b710eeaf7834f9acee` ; `famille_e_a3_20261121T162956Z.json` (seconde, identique, décision valide) : SHA-256 `a27a45e493590e0ec8ef0addd5040b43fb791e92223c3a134fe63cc31fe35a50`. Registre de la v3 au moment de la mesure : `data/adaptation/v3/registre.jsonl`, chaîné, 144 événements, SHA-256 `a732dbebf6d629a6e2848282dce7e0d3708a5399c0951234fddc3438f7d32a4b`.
* Bout en bout : `bout_en_bout_B2_adapte_20261117T132817Z.json` (`0848326f…`), `bout_en_bout_R1_adapte_20261121T123542Z.json` (`6f4b866a…`), `bout_en_bout_R1_temoin_20261121T130808Z.json` (`b9ac9420…`), analyse `bout_en_bout_analyse_20261121T134041Z.json` (`c4571cb6…`).
* Environnement : `scripts/evaluation/requirements-lock.txt`, plus onnxruntime 1.30.0, version déjà figée par `scripts/indexation/requirements-lock.txt`.
