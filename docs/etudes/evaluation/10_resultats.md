# Protocole 10 : résultats des familles A et B (récupération)

**Date** : 17 novembre 2026. **Tickets** : #171, #172, #173. **Règles** : protocole 10 (`10_protocole_jeu_v2.md`, figé avant toute génération, commit `ffa0486`, SHA-256 `8d123613…`). **Jeu** : `evaluation/questions_v2/questions_v2.csv`, étiquette `jeu-questions-v2` (`8bfd9fb`). **Auteur** : Mahé BEGNIS.

---

## 1. Objet et état

Cette page publie deux des trois familles de mesures du protocole 10, section 7, et l'effet du nombre de passages demandé par l'enseignant :

* **Famille A** : la fusion de la recherche dense du site avec BM25 V3, candidate pour le volet A (#173).
* **Famille B, récupération** : la récupération du volet B, R0, R1 et R2, et la règle qui décide de la chaîne de démonstration (#172).

Restent à mesurer : la famille B de bout en bout, avec Ollama, et la famille E (encodeurs v2-T et v3-C, #167). Elles seront ajoutées ici.

Les mesures sont faites par `scripts/evaluation/mesures_10.py` (commandes `famille_a` et `famille_b`). Chaque fichier de résultats est écrit une seule fois dans `data/evaluation/protocole_10/`, non versionné ; ses empreintes sont en section 8.

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
* **Conséquence pour le #173** : la fusion dans le navigateur est permise par la règle mais pas démontrée utile. Elle n'est implémentée que si le temps le permet avant le gel du 20 novembre, avec un test de parité entre Python et JavaScript.

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

## 6. Bout en bout de la famille B : ce qui change

Le protocole compare, sur le jeu v2, le modèle adapté en B2 au modèle adapté « dans la chaîne de démonstration (R2) », puis le témoin T dans cette chaîne. R2 n'étant pas maintenue, la chaîne de démonstration est R1 : la mesure de bout en bout se fait avec R1, consigne v1, sans seuil. Les autres conditions sont celles du protocole.

---

## 7. Pourquoi 10 passages au lieu de 5

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

## 8. Limites

* **Le CDTN n'est pas neutre entre R1 et R2** : la configuration de R1 a été choisie sur ce jeu par le protocole 07. Seul le jeu v2 est indépendant pour cette comparaison ; il donne le même sens.
* **Questions générées par Claude** : proches du style d'un générateur, et un peu plus proches des mots du passage que les questions humaines. Le jeu v1 et le CDTN, écrits sans IA, servent de contrôle ; sur la famille A, le jeu v1 ne confirme pas le jeu v2.
* **Un seul passage annoté par question au jeu v2** : les critères sont des minorants.
* **Puissance** : 121 questions et 61 fiches ne permettent de détecter que des écarts de plusieurs points ; une égalité à deux points près n'est pas exclue entre R1 et R2.

---

## 9. Fichiers et empreintes

* `data/evaluation/protocole_10/famille_a_20261117T125533Z.json` : SHA-256 `4c7d40c72d0a394c5a0fd162f6dc154886495ff74fa5bc568c27f17cc423918d`.
* `data/evaluation/protocole_10/famille_b_20261117T131518Z.json` : SHA-256 `67c1b3ac2e7ead1b9c278e75e3646d314a43a37e0e05730f387626d13bccfba2`. Il contient, pour chaque question du jeu v2, les passages du contexte de chaque état.
* `data/evaluation/protocole_10/reclasseur_bge-m3_famille_b.json` : cache des scores du reclasseur (5 080 paires calculées pour la famille B, dont 219 pour compléter les candidats de R2 sur le CDTN), SHA-256 `08572df0b1268385403409032d0524b37e52d5286326b5c42406c77ac9b2dcc4`.
* `data/evaluation/protocole_10/effet_k_20261117T131939Z.json` : SHA-256 `9cb00fe577f5a19bffba1b78324f1ecfb22a8a8578100b5a712a561bc2a7b517`.
* Environnement : `scripts/evaluation/requirements-lock.txt`, plus onnxruntime 1.30.0, version déjà figée par `scripts/indexation/requirements-lock.txt`.
