# Audit statistique du notebook 03, avant la mesure

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** Issue #46 · Branche `feat/46-notebook-03`  
**Auteur** Mahé BEGNIS  
**Date** 10 octobre 2026, avant toute mesure sur le lot de test  

---

## 1. Objet

Le protocole du notebook 03 (`03_protocole.md`, figé le 10 octobre) tranche le critère du rapport J2 par un test de non-infériorité : l'encodeur servi n'est pas moins bon que BM25 de plus de 15 points de Recall@5, au risque unilatéral de 2,5 %. Cet audit vérifie, par simulation, que la règle de décision figée tient ce risque, avec la puissance annoncée, sur la structure réelle du lot de test.

* **Aucune donnée de mesure.** La simulation n'utilise que le nombre de questions du corpus par fiche annotée dans le lot de test. Aucun système n'est interrogé.
* **Reproductible.** `scripts/evaluation/audit_statistique.py`, graine 20261010, 10 000 tirages par scénario ; l'erreur de Monte-Carlo vaut au plus 0,5 point, et environ 0,2 point au voisinage de 2,5 %.

---

## 2. Ce qui est simulé

* **Structure.** 73 questions du corpus, réparties sur 61 fiches : 51 fiches à une question, 8 à deux, 2 à trois.
* **Tirage.** Chaque question tombe dans l'une des quatre cases de la table appariée : E5 seul réussit, BM25 seul réussit, les deux, aucun. Chaque système réussit environ 80 % des questions quand l'écart est nul, l'ordre de grandeur observé sur PIAF.
* **Désaccord.** La part des questions où un seul système réussit vaut 0,14 (celle de PIAF entre E5 et BM25 V3), 0,20 ou 0,25 ; 0,20 à 0,30 quand l'écart vaut -15 points, qui exige au moins 15 % de désaccord.
* **Dépendance.** Deux scénarios : questions indépendantes, puis questions d'une même fiche qui reprennent l'issue de la première question de la fiche avec la probabilité 0,5.
* **Règle figée.** Celle du notebook : intervalle d'Agresti et Min sous 10 paires discordantes, Wald robuste aux fiches sinon ; critère satisfait si la borne basse dépasse -15 points.

---

## 3. Résultats

Part des tirages où le critère est déclaré satisfait, et couverture de l'intervalle à 95 % de l'écart.

| Écart réel | Désaccord | Corrélation | Règle figée : critère | Règle figée : couverture | Tango corrigé : critère | Tango corrigé : couverture |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 0,14 | non | 92,0 % | 95,0 % | 86,5 % | 95,8 % |
| 0 | 0,20 | non | 81,6 % | 94,4 % | 76,5 % | 95,8 % |
| 0 | 0,25 | non | 73,1 % | 94,1 % | 68,8 % | 95,0 % |
| -15 points | 0,20 | non | 4,7 % | 93,6 % | 2,1 % | 95,1 % |
| -15 points | 0,25 | non | 3,3 % | 94,4 % | 1,9 % | 95,5 % |
| -15 points | 0,30 | non | 3,0 % | 94,2 % | 2,2 % | 95,3 % |
| 0 | 0,14 | oui | 87,8 % | 94,6 % | 81,2 % | 95,7 % |
| 0 | 0,20 | oui | 76,1 % | 94,5 % | 70,8 % | 95,3 % |
| 0 | 0,25 | oui | 66,7 % | 94,2 % | 62,7 % | 95,0 % |
| -15 points | 0,20 | oui | 5,2 % | 93,1 % | 2,5 % | 94,6 % |
| -15 points | 0,25 | oui | 3,6 % | 94,2 % | 2,3 % | 94,9 % |
| -15 points | 0,30 | oui | 3,3 % | 94,2 % | 2,5 % | 95,0 % |

Lecture : avec un écart réel nul, la colonne « critère » est la puissance ; avec un écart réel de -15 points, c'est le risque d'erreur, qui devrait valoir au plus 2,5 %.

* **Puissance conforme.** Avec un écart nul, la règle figée conclut dans 67 à 92 % des tirages, cohérent avec les 72 à 93 % annoncés au protocole pour 72 questions indépendantes.
* **Risque trop élevé.** À la marge, la règle figée conclut à tort dans 3,0 à 5,2 % des tirages, au lieu de 2,5 %. L'écart dépasse largement l'erreur de Monte-Carlo.
* **Intervalle d'une proportion bien calibré.** Le Wilson à effectif corrigé de l'effet de plan couvre la vraie valeur dans 94,0 à 94,9 % des tirages, pour des proportions de 0,6, 0,8 et 0,9, avec ou sans corrélation.

---

## 4. Pourquoi la règle figée se trompe trop souvent

Le Wald estime la variance de l'écart avec les proportions observées. Quand l'écart réel vaut -15 points avec 20 % de désaccord, E5 seul réussit 2,5 % des questions et BM25 seul 17,5 %. Sur 73 questions, cela fait en moyenne 2 et 13 questions : les tirages où l'écart observé est moins défavorable sont aussi ceux où la variance estimée est la plus faible. La borne basse remonte alors au-dessus de la marge plus souvent que prévu. L'intervalle d'Agresti et Min, qui ajoute une demi-observation à chaque case, ne suffit pas : simulé seul, il donne 3,2 à 5,3 %, comme un Wald avec quantile de Student à 60 degrés de liberté (2,9 à 4,2 %).

---

## 5. La correction proposée : le score de Tango corrigé de l'effet de plan

* **Principe.** Le test du score de Tango (Statistics in Medicine, 1998) calcule la variance de l'écart sous l'hypothèse testée, c'est-à-dire à la marge exacte, avec l'estimateur du maximum de vraisemblance des probabilités contraint par cette marge, et non à l'écart observé. C'est la méthode de référence pour la non-infériorité sur données appariées.
* **Regroupement.** Seul, il ignore que des questions d'une même fiche se ressemblent : son risque monte à 3,1 à 3,3 % dans le scénario corrélé. On divise donc la statistique par la racine de l'effet de plan, le rapport des variances de l'écart avec et sans regroupement par fiche, au moins égal à 1. C'est la correction que le protocole applique déjà à l'intervalle d'une proportion.
* **Résultat.** Risque de 1,9 à 2,5 % dans tous les scénarios, couverture de 94,6 à 95,8 %. La puissance baisse de 4 à 7 points (63 à 87 %) : c'est le prix d'un risque tenu, la règle figée n'étant plus puissante que parce qu'elle se trompe trop souvent.
* **Implémentation.** La fonction `noninferiority_tango` du module de métriques. L'estimateur contraint suit la formule fermée de Tango, recoupée par optimisation numérique à 4e-9 près. À marge nulle, la statistique se réduit à celle de McNemar, ce que vérifie un contrôle calculé à la main. L'intervalle est obtenu en inversant le score, et la décision équivaut à une borne basse supérieure à -15 points.

---

## 6. Décision à prendre avant la mesure

Le protocole est figé, et cet audit ne le modifie pas. Deux possibilités, à trancher avant la mesure :

* **Garder la règle figée**, en publiant avec le résultat son risque réel, de 3 à 5 % au lieu de 2,5 %.
* **Amender le protocole**, avec le score de Tango corrigé de l'effet de plan pour le verdict du critère du J2, l'intervalle de Wald ou d'Agresti et Min restant publié à titre descriptif. Cet amendement repose sur la seule simulation, sans aucune donnée de mesure ; il impose de figer à nouveau le protocole et d'inscrire sa nouvelle empreinte dans le notebook.

Recommandation : amender. Un critère annoncé « au risque de 2,5 % » doit tenir ce risque, et la correction est standard, simple et déjà testée.
