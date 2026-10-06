# Validation de la chaîne de mesure de la recherche sur le jeu PIAF

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** Issue #45 · Branche `feat/45-metriques-piaf`  
**Responsable principal** Remy RAYANE  
**Soutien et relecture** Mahé BEGNIS  
**Exécution** 3 octobre 2026 (première version) ; 4 octobre 2026 (version relue, dont les résultats suivent)  

---

## 1. Contexte et objectif

Le sujet impose d'évaluer rigoureusement le système de recherche d'information (IR) sur le corpus du droit du travail au jalon J3 (notebook 03, issue #46).

Avant d'appliquer ces mesures à notre corpus et à notre propre jeu de questions, l'issue #45 a pour but de **valider la chaîne mathématique et logicielle de mesure sur un jeu public français déjà annoté** : **PIAF** (`AgentPublic/piaf`).

PIAF ne sert qu'à cette validation : il ne fait pas partie du jeu d'évaluation du projet. Ce jeu est celui que l'équipe rédige à la main (issue #44), complété, sur proposition de ses rédacteurs, par les requêtes annotées du CDTN (`SocialGouv/datafiller-data`). Aucun chiffre de ce rapport ne mesure donc notre système : ce qui se transpose, ce sont le code et des leçons de méthode (section 8).

Cette validation préalable poursuit trois objectifs :

1. **Garantir l'exactitude des métriques** (Recall@k et MRR) par des tests unitaires confrontés à des calculs manuels, puis par un recalcul indépendant sur tout le jeu.
2. **Fournir un module de calcul propre et réutilisable** (`scripts/evaluation/metrics.py`) pour le notebook 03.
3. **Établir une première comparaison appariée** entre l'approche lexicale classique (**BM25**) et l'approche dense par plongements (**`multilingual-e5-small`**).

La relecture du 4 octobre a reproduit à l'identique tous les chiffres de la première version. Elle a corrigé le code sur des cas absents de PIAF mais présents dans notre futur jeu de questions (section 3.4), et elle nuance deux conclusions : la significativité, une fois les questions groupées prises en compte (section 5.2), et l'avantage de E5, qui dépend du réglage de BM25 (section 5.3).

---

## 2. Données et protocole expérimental

### 2.1 Jeu de données PIAF

* **Dépôt Hugging Face :** `AgentPublic/piaf`
* **Révision figée (reproductibilité) :** `bda8c063bc7297180796cd835d1974c0bc71c521`
* **Licence :** MIT selon la fiche Hugging Face ; l'article PIAF (Keraron et al., LREC 2020) annonce CC BY-SA. Sans conséquence ici : le jeu est téléchargé, jamais versionné ni redistribué.
* **Passages uniques (paragraphes Wikipédia) :** N = 761
* **Questions annotées :** 3 835, chacune rattachée à son paragraphe d'origine, seul passage pertinent
* **Articles :** 191
* **Protocole d'annotation :** celui de SQuAD. Un annotateur lit un paragraphe et écrit plusieurs questions dont la réponse s'y trouve (article PIAF, sections 3 et 4). On compte au moins 5 questions par paragraphe (5,04 en moyenne, 13 au plus), et 20,1 par article en moyenne (150 au plus).

Ce protocole a deux conséquences, mesurées plus loin : les questions d'un même paragraphe ou d'un même article ne sont pas indépendantes (section 5.2), et une question écrite sous les yeux du paragraphe en reprend volontiers les mots (section 6).

### 2.2 Systèmes comparés

**Aléatoire.** L'espérance exacte, k / N pour Recall@k et (1 + 1/2 + ... + 1/10) / N pour le MRR@10, plus un tirage uniforme sans remise de 10 passages par question (graine 42), qui n'en est qu'une réalisation.

**BM25, quatre variantes.** Les mots sont mis en minuscules et découpés sur tout ce qui n'est ni lettre ni chiffre.

| Variante | Formule de l'idf | k1 | b | Traitement des mots |
|---|---|---:|---:|---|
| V0 (première version) | rank_bm25 (`BM25Okapi`) : idf négatifs remplacés par 0,25 fois l'idf moyen | 1,5 | 0,75 | aucun |
| V1 | Lucene : ln(1 + (N - n + 0,5) / (n + 0,5)), toujours positif | 1,2 | 0,75 | aucun |
| V2 | Lucene | 1,2 | 0,75 | mots vides Snowball retirés |
| V3 | Lucene | 1,2 | 0,75 | mots vides Snowball retirés, puis racinisation Snowball |

La liste de mots vides est celle du notebook 01 (projet Snowball, 154 mots, même commit et même empreinte). Les réglages sont les valeurs par défaut usuelles : aucun n'a été ajusté sur PIAF. Les variantes V1 à V3 sont calculées par une réimplantation en matrices creuses, qui reproduit les scores de rank_bm25 à 9e-12 près quand on lui donne la formule de V0.

**Recherche dense E5.** Modèle `intfloat/multilingual-e5-small` (384 dimensions) :

* révision du notebook 02 : `614241f622f53c4eeff9890bdc4f31cfecc418b3` ;
* préfixe `passage: ` pour les 761 paragraphes, préfixe `query: ` pour les 3 835 questions ;
* moyenne des tokens avec masque d'attention, puis normalisation L2 ;
* score : produit scalaire, égal au cosinus pour des vecteurs normalisés ;
* aucune troncature : le paragraphe le plus long compte 304 tokens, pour un budget de 512.

**Ex aequo.** À score égal, les passages sont rangés dans l'ordre de l'index (tri stable), pour tous les systèmes.

### 2.3 Formules des métriques

* **Recall@k**, convention de l'équipe (support sur l'encodeur, section des métriques) : pour chaque question, 1 si au moins un passage pertinent figure parmi les k premiers résultats, 0 sinon ; Recall@k est la moyenne sur les questions. C'est la « top-k accuracy » de DPR. BEIR appelle Recall@k la part des passages pertinents retrouvés : les deux coïncident ici, puisque chaque question n'a qu'un passage pertinent.
* **MRR@10** : moyenne, sur les questions, de 1 / rang du premier passage pertinent, comptée 0 quand il n'est pas dans les 10 premiers. La première version l'appelait MRR ; le MRR sans troncature est plus élevé de 0,0034 pour E5 et de 0,0036 pour BM25 V0.

### 2.4 Comparaison appariée

Les deux systèmes répondent aux mêmes questions. Pour un k donné, on note b le nombre de questions réussies par E5 seul, c celles réussies par BM25 seul, et n = 3 835.

* **Test exact de McNemar** : sous l'hypothèse d'égalité, b suit une loi binomiale de paramètres b + c et 1/2. La valeur p bilatérale vaut 2 fois P(X ≤ min(b, c)), plafonnée à 1. La statistique du chi2 avec la correction de continuité d'Edwards (1948) vaut (|b - c| - 1)² / (b + c).
* **Limite de ce test** : il suppose les questions indépendantes. Or les 5 questions d'un paragraphe partagent le même passage cible, et les paragraphes d'un article partagent leur sujet et leur vocabulaire.
* **Différence et intervalle robustes aux groupes** : la différence vaut d = (b - c) / n. Dans chaque groupe g (paragraphe ou article), D_g = (questions réussies par E5 seul) - (questions réussies par BM25 seul), et n_g est le nombre de questions. L'erreur type robuste vaut la racine de G / (G - 1) fois la somme des (D_g - n_g × d)², divisée par n, où G est le nombre de groupes. L'intervalle à 95 % vaut d plus ou moins 1,96 erreur type.
* **Test d'Obuchowski (Statistics in Medicine, 1998)**, McNemar pour données groupées : (G - 1) / G fois le carré de la somme des D_g, divisé par la somme des carrés des D_g, comparé à un chi2 à 1 degré de liberté. Avec un groupe par question, il se réduit au McNemar sans correction. Il pondère les questions également, comme Recall@k.
* **Effet de plan** : rapport des variances de d, groupée sur indépendante. Le nombre de questions divisé par l'effet de plan donne le nombre de questions « effectives ».

Le regroupement par article est le plus prudent : c'est lui qui fonde les conclusions.

---

## 3. Validation du code

### 3.1 Calculs à la main

`python scripts/evaluation/metrics.py` exécute onze contrôles dont le résultat a été calculé à la main : cible aux rangs 1, 3 et absente ; moyennes 1/3, 2/3 et 4/9 ; question à deux passages pertinents ; ensembles de types variés ; entrées invalides ; ex aequo ; intervalle de Wilson de 81 succès sur 263, publié par Newcombe (1998) : 0,2553 à 0,3662 ; McNemar, différence et intervalle sur trois questions ; test d'Obuchowski et intervalle groupé sur six questions en trois groupes (statistique 4/9, erreur type racine de 7 divisée par 6).

### 3.2 Recalcul indépendant sur tout le jeu

Pour chacune des 3 835 questions et chacun des cinq systèmes, le script recalcule le rang de la cible sans aucun tri : 1 plus le nombre de passages de score strictement supérieur, et, en comptant les ex aequo contre la cible, le nombre de passages de score supérieur ou égal. Le rang lu dans la liste classée tombe toujours dans cet intervalle, et chaque Recall@k du module coïncide exactement avec la part des questions de rang au plus k.

### 3.3 Reproduction

* Les chiffres de la première version se reproduisent à l'identique sur une autre machine : toutes les métriques à 4 décimales, la table de contingence, le chi2 et la valeur p.
* Le script corrigé tourne en une commande, en une minute environ sur CPU (Apple M4 Pro, jeu et modèle déjà en cache), depuis n'importe quel dossier. Deux exécutions donnent le même fichier de résultats, temps exceptés, et les mêmes rangs par question.
* Les dépendances sont figées dans `scripts/evaluation/requirements.txt` et `requirements-lock.txt`. La première version utilisait `datasets` et `rank_bm25` sans les déclarer, et ne figeait pas la révision du modèle.

### 3.4 Défauts corrigés dans le code

Aucun de ces défauts ne change les chiffres de PIAF, où chaque question a un seul passage pertinent. Tous auraient faussé le notebook 03 sans erreur visible.

| Défaut de la première version | Cas concret | Effet |
|---|---|---|
| Recall@k calculé comme la part des passages pertinents retrouvés, contraire à la convention de l'équipe | question à deux passages pertinents de même texte (le découpage M2 en compte 57), l'un au rang 2, l'autre au rang 7 | Recall@5 vaut 0,5 au lieu de 1, et McNemar compte un échec |
| Question sans passage pertinent acceptée | question hors corpus du jeu de questions | comptée 0, ce qui fait baisser Recall@k et MRR |
| `frozenset` lu comme un identifiant, tableau numpy refusé | ensemble pertinent construit par une autre étape | 0 sans erreur ; erreur de type |
| Liste plus courte que k acceptée | système qui renvoie 5 résultats, mesuré à k = 10 | Recall@10 égal à Recall@5 sans avertissement |
| Ex aequo rangés par ordre décroissant d'indice (`argsort` inversé) | BM25, où la cible est à égalité avec un autre passage pour 60 à 306 questions selon la variante | règle propre à chaque code, résultats non comparables |
| MRR tronqué à 10 mais nommé MRR | toute comparaison avec un MRR complet | écart de 0,003 à 0,004 sur PIAF |

---

## 4. Résultats

Mesures sur les 3 835 questions. L'intervalle de Recall@5 tient compte du regroupement des questions par article.

| Méthode | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@10 | Recall@5, IC 95 % |
|---|---:|---:|---:|---:|---:|---:|
| Aléatoire, espérance | 0,13 % | 0,39 % | 0,66 % | 1,31 % | 0,0038 | |
| Aléatoire, tirage (graine 42) | 0,08 % | 0,37 % | 0,76 % | 1,30 % | 0,0036 | |
| BM25 V0 (première version) | 64,25 % | 77,00 % | 81,07 % | 85,66 % | 0,7147 | 78,5 à 83,6 % |
| BM25 V1 (Lucene) | 66,18 % | 77,65 % | 82,43 % | 86,34 % | 0,7295 | 80,0 à 84,8 % |
| BM25 V2 (+ mots vides) | 66,60 % | 78,93 % | 83,42 % | 87,25 % | 0,7360 | 81,0 à 85,8 % |
| BM25 V3 (+ racinisation) | **68,24 %** | 80,63 % | 84,90 % | 88,81 % | 0,7532 | 82,7 à 87,1 % |
| Dense E5 (`multilingual-e5-small`) | 66,78 % | **83,21 %** | **87,20 %** | **90,90 %** | **0,7567** | 85,2 à 89,2 % |

* **Le tirage aléatoire** s'écarte de son espérance comme attendu : 3 succès à Recall@1 pour 5,04 attendus, soit 0,9 écart type. L'espérance, exacte, est la valeur de référence.
* **Les ex aequo** pèsent peu : en les comptant tous pour la cible, puis tous contre elle, le Recall@5 de V3 varie de 84,90 à 85,11 % et celui de V2 de 83,39 à 83,94 %. Aucune conclusion ne change.
* **Les temps** ne sont pas comparables entre méthodes, et ne sont pas des latences : environ 0,8 ms par question pour E5, encodage seul par lots de 32, et 0,5 ms pour BM25 V0, question par question, sur Apple M4 Pro. La première version mesurait 6,08 et 0,37 ms sur une autre machine.

---

## 5. Comparaisons appariées

### 5.1 La comparaison de la première version, confirmée

Recall@5, E5 contre BM25 V0 :

| | BM25 échec | BM25 succès (top 5) | Total |
|---|---:|---:|---:|
| **E5 échec** | 288 | 203 (c) | 491 |
| **E5 succès (top 5)** | 438 (b) | 2 906 | 3 344 |
| **Total** | 726 | 3 109 | 3 835 |

Les calculs de la première version sont exacts : écart de 6,13 points, chi2 d'Edwards de 85,42, valeur p exacte de 8,8e-21. Mais ils supposent 3 835 questions indépendantes.

### 5.2 Les questions groupées

Sur Recall@5, l'effet de plan vaut 1,6 avec un regroupement par paragraphe et 2,4 par article. Les 3 835 questions pèsent donc comme 2 400 questions indépendantes dans le premier cas, et 1 600 dans le second.

| Recall@5, E5 contre BM25 V0 | Écart | IC 95 % | Valeur p |
|---|---:|---:|---:|
| questions supposées indépendantes (McNemar exact) | +6,13 pts | +4,85 à +7,41 | 8,8e-21 |
| regroupement par paragraphe (Obuchowski) | +6,13 pts | +4,52 à +7,74 | 5,9e-13 |
| regroupement par article (Obuchowski) | +6,13 pts | +4,13 à +8,12 | 3,6e-08 |

L'écart reste très significatif, mais la valeur p de la première version surestime la preuve d'environ 13 ordres de grandeur. L'intervalle de l'écart est l'information utile : E5 gagne de 4 à 8 points de Recall@5 sur BM25 V0.

### 5.3 Sensibilité à la référence BM25

Écart E5 moins BM25, en points, avec l'intervalle à 95 % et la valeur p du test d'Obuchowski, questions groupées par article :

| Référence | Recall@1 | Recall@5 | Recall@10 |
|---|---|---|---|
| V0 (première version) | +2,53 [+0,37 ; +4,69], p = 0,027 | +6,13 [+4,13 ; +8,12], p = 4e-08 | +5,24 [+3,56 ; +6,92], p = 6e-08 |
| V1 (Lucene) | +0,60 [-1,58 ; +2,78], p = 0,59 | +4,77 [+2,89 ; +6,65], p = 3e-06 | +4,56 [+2,89 ; +6,23], p = 8e-07 |
| V2 (+ mots vides) | +0,18 [-2,05 ; +2,42], p = 0,87 | +3,78 [+1,93 ; +5,63], p = 1e-04 | +3,65 [+2,02 ; +5,28], p = 4e-05 |
| V3 (+ racinisation) | -1,46 [-3,48 ; +0,56], p = 0,16 | +2,29 [+0,55 ; +4,03], p = 0,009 | +2,09 [+0,59 ; +3,58], p = 0,006 |

* **À Recall@5 et Recall@10,** E5 fait significativement mieux que chacune des quatre variantes, mais l'écart passe de 6,1 à 2,3 points quand BM25 passe des réglages par défaut de rank_bm25 à la formule de Lucene, avec mots vides retirés et racinisation.
* **À Recall@1,** E5 ne fait pas mieux que BM25 dès que BM25 est réglé de façon usuelle : V3 est même devant de 1,5 point, sans que l'écart soit significatif.
* **Le réglage de la référence pèse donc autant que l'écart mesuré.** C'est le risque que nomme l'issue #47 : une référence mal réglée flatte l'encodeur.
* **Ce que ces chiffres ne tranchent pas.** Le critère du rapport J2 (l'encodeur ne fait pas moins bien que BM25) se mesurera sur notre jeu, pas sur PIAF. PIAF montre seulement que la conclusion peut dépendre de la métrique : ici, E5 passerait le critère à Recall@5 contre toutes les variantes, mais à Recall@1 seulement avec une marge de non-infériorité d'au moins 3,5 points, la borne basse de l'intervalle face à V3. La métrique et la marge doivent donc être fixées avant la mesure du notebook 03.

---

## 6. Analyse des cas discordants

Part des mots de la question, hors mots vides, présents dans le paragraphe cible (Recall@5, E5 contre BM25 V0) :

| Catégorie | Questions | Recouvrement médian | Recouvrement moyen |
|---|---:|---:|---:|
| deux succès | 2 906 | 0,60 | 0,59 |
| E5 seul | 438 | 0,20 | 0,22 |
| BM25 seul | 203 | 0,50 | 0,54 |
| deux échecs | 288 | 0,20 | 0,19 |

E5 gagne surtout quand la question reprend peu de mots du paragraphe ; BM25 gagne sur des questions à fort recouvrement, presque autant que celles que les deux réussissent. Exemples tirés au hasard parmi les cas discordants (graine 42) :

| Question | Article | Rang E5 | Rang BM25 V0 | Recouvrement |
|---|---|:---:|:---:|:---:|
| A quel poste joue Brodeur ? | Martin Brodeur | 2 | au-delà de 10 | 0,25 |
| Quelles sont les deux qualités du père du fils prodigue ? | Fils prodigue | 3 | au-delà de 10 | 0,40 |
| Vers quelle période la Chelidonium majus commence-t-elle à pousser? | Chelidonium majus | 1 | au-delà de 10 | 0,00 |
| Secteur de prospérité recente | Lyon | au-delà de 10 | 2 | 0,33 |
| comment était appelé le garçon? | Mariage homosexuel | au-delà de 10 | 1 | 0,33 |
| Dans quelle période le programme arrête-t-il ? | Marlyse de La Grange | 6 | 1 | 0,33 |

Plusieurs questions n'ont de sens qu'avec le paragraphe sous les yeux (« comment était appelé le garçon? »). Ce sont des questions de compréhension de lecture, pas des requêtes de recherche : elles pèsent sur les deux systèmes.

Les trois exemples de la première version (questions 0, 42 et 128) ne montraient pas de différence entre les systèmes : deux placent la cible au rang 1 pour les deux, et le troisième (« qui est le pere de John? », rangs 1 et 3) est réussi par les deux à Recall@5. L'explication proposée pour ce dernier ne s'appuyait sur aucune mesure.

---

## 7. Ce que cette étude établit, et ce qu'elle n'établit pas

### Ce qui est établi

1. **La justesse du code :** onze contrôles calculés à la main, et le recalcul sans tri des 3 835 rangs de chacun des cinq systèmes.
2. **La reproductibilité :** une commande, environ une minute sur CPU, résultats identiques d'une exécution à l'autre, versions et révisions figées.
3. **Sur PIAF, E5 fait mieux que BM25 à Recall@5 et Recall@10,** de 2,1 à 6,1 points selon la variante, écart significatif même en groupant les questions par article. **À Recall@1, il ne fait pas mieux qu'un BM25 réglé.**
4. **Le réglage de BM25 compte :** la formule de Lucene, le retrait des mots vides et la racinisation lui font gagner 3,8 points de Recall@5 sur PIAF (de 81,07 à 84,90 %).

### Ce qui n'est pas établi

* **La transposition au droit du travail.** PIAF est fait de paragraphes Wikipédia ; notre corpus est réglementaire, avec ses références d'articles et ses sigles.
* **Le sens de l'écart sur notre corpus, car PIAF biaise la mesure dans les deux sens.** En faveur de E5 : le modèle a été pré-entraîné notamment sur 150 millions de paires tirées de Wikipédia, puis ajusté, entre autres, sur des questions portant sur Wikipédia (SQuAD, MIRACL) (Wang et al., rapport technique Multilingual E5, 2024, tableaux 1 et 2). En faveur de BM25 : les questions ont été écrites devant le paragraphe et en reprennent les mots (recouvrement médian de 0,60 sur les questions réussies par les deux), ce que ne fera pas un utilisateur.
* **L'exhaustivité des passages pertinents.** Chaque question n'a qu'un paragraphe pertinent. Pour 76 questions (2,0 %), la réponse, d'au moins 15 caractères, figure mot pour mot dans un autre paragraphe du même article, et 3 textes de question identiques renvoient à des paragraphes différents. Les Recall@k mesurés sont donc légèrement sous-estimés, pour les deux systèmes.
* **Le comportement sur les sigles.** La première version écrivait que le notebook 02 avait montré un échec de l'encodeur sur les sigles « là où BM25 excelle ». Le notebook 02 n'a pas mesuré BM25. Il a observé, sur une seule question, que le passage attendu (article L. 1221-19) passe du rang 2 au rang 5 quand « contrat à durée indéterminée » devient « CDI », et la fiche du rang 1 au rang 4. Rien n'indique que BM25 ferait mieux sur ce passage : il ne rapproche que des mots identiques, et le passage écrit « contrat de travail à durée indéterminée », jamais « CDI ». Le sous-ensemble des questions à sigles est mesuré au notebook 03 (issue #46), et l'extension des sigles y est prévue.

---

## 8. Guide de réutilisation pour le notebook 03

Le module `scripts/evaluation/metrics.py` est autonome ; depuis un notebook du même dossier :

```python
from metrics import rank_by_score, evaluate_retrieval, compute_mcnemar_test, proportion_ci

# classements par score décroissant, ex aequo dans l'ordre de l'index
preds_e5 = [rank_by_score(ligne, depth=10).tolist() for ligne in scores_e5]

# ground_truth : pour chaque question, ses passages pertinents (au moins un)
resultats = evaluate_retrieval(preds_e5, ground_truth, k_values=(1, 3, 5, 10))
print(resultats["recall@5"], resultats["mrr"], resultats["profondeur"])

# comparaison appariée, questions groupées par fiche (une étiquette par question)
test = compute_mcnemar_test(preds_e5, preds_bm25, ground_truth, k=5,
                            groups=fiche_par_question)
print(test["difference"], test["ci_difference"], test["p_value_groups"])
```

Règles d'usage :

* **Passages pertinents :** un ensemble par question, jamais vide. Les questions hors corpus s'évaluent à part, avec l'abstention.
* **Classements :** toujours par `rank_by_score`, pour la même règle d'ex aequo entre systèmes, et sur au moins 10 passages.
* **Groupes :** les questions d'une même fiche se ressemblent, et les variantes d'une même requête du CDTN partagent leur jugement ; passer la fiche ou la requête en `groups`, et lire `p_value_groups` et `ci_difference`.
* **Non-infériorité :** l'encodeur n'est pas inférieur à BM25 avec la marge m si la borne basse de `ci_difference` dépasse -m. La métrique et la marge se fixent avant la première mesure.
* **Petits effectifs :** avec quelques dizaines de paires discordantes, l'intervalle de Wald de la différence devient approximatif ; la valeur p exacte de McNemar reste valable si les questions sont indépendantes.
* **Nommage :** le MRR calculé sur des listes de 10 résultats est le MRR@10.

Deux sources, donc deux analyses distinctes :

* **Jeu de l'équipe (issue #44), analyse principale.** Les passages pertinents sont ceux qui contiennent l'extrait annoté, selon une règle écrite avant la mesure (issue #46) ; les questions sont groupées par fiche ; les questions hors corpus s'évaluent à part, avec l'abstention.
* **Requêtes du CDTN, analyse secondaire.** Elle est rapportée à part, jamais fusionnée avec la principale : la pertinence y est jugée à la section, ce qui donne 4 passages pertinents par requête en médiane (appariement préliminaire du 4 octobre), et les requêtes sont surtout des mots-clés (20 sur 175 sont rédigées en question, variantes non comptées). C'est là que la convention de Recall@k compte le plus : avec l'ancienne définition, une requête dont un seul des 4 passages pertinents est retrouvé aurait compté 0,25.
* **Variantes du CDTN.** Chaque requête vient avec des variantes (14 en médiane), qui héritent toutes du même jugement : ce sont des reformulations d'une même requête, pas des questions indépendantes. Elles se passent avec la requête en `groups`, et l'effectif utile est le nombre de requêtes, pas le nombre de variantes.
* **Leçon de PIAF transposée.** Des questions écrites en lisant le texte en reprennent les mots et favorisent BM25 (section 6) ; le protocole de l'issue #44, qui fait écrire la question avant d'ouvrir la fiche, répond à ce biais. Les requêtes du CDTN, à base de mots-clés, peuvent elles aussi favoriser BM25 : raison de plus pour les analyser à part.

---

## 9. Historique

* **3 octobre 2026, première version (Remy RAYANE) :** module de métriques, script de validation sur PIAF, BM25 V0 contre E5, McNemar sur Recall@5.
* **4 octobre 2026, relecture (Mahé BEGNIS) :** chiffres reproduits à l'identique ; convention de Recall@k alignée sur celle de l'équipe ; entrées invalides refusées ; règle d'ex aequo commune ; intervalle de confiance, test d'Obuchowski et intervalle groupé ajoutés au module ; recalcul indépendant des rangs, variantes BM25 V1 à V3, espérance de l'aléatoire, révision du modèle et dépendances figées dans le script ; rapport révisé ; rôle de PIAF et analyse séparée des deux sources précisés.
