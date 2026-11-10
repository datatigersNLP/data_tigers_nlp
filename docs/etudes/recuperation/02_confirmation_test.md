# Récupération v2 : confirmation sur le lot de test

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** #138 (récupération v2 du volet B)  
**Responsable** Mahé BEGNIS  
**Statut** confirmation unique faite le 9 novembre 2026 à 11:02 UTC, selon le protocole 07 figé au commit `b1a36b1` et publié dans la PR #141 avant l'exécution.

---

## 1. Ce qui a été comparé

* **Référence R0** : la chaîne B1, soit E5 en fp32 et les 5 premiers passages.
* **Récupération v2** : `rrf+k10+bge-m3@20`, retenue sur le jeu CDTN (étude 01). Elle fusionne E5 et BM25 V3, fait reclasser les 20 premiers candidats par bge-m3, et donne 10 passages au modèle.
* **Questions** : les 73 questions du corpus du lot de test de `jeu-questions-v1`, issues de 61 fiches.
* **Pertinence** : la règle D4, à partir de l'extrait annoté de chaque question. Chacune des 73 questions a au moins un passage pertinent.
* **Portée** : la récupération seule. Aucune réponse n'a été générée.

## 2. Contrôles préalables

* **Fichiers figés** : le protocole, le script et le module étaient committés à l'identique ; les résultats de la grille avaient l'empreinte inscrite au protocole (`2c8619ca…`).
* **Chaîne verrouillée** : ses dix empreintes étaient celles de la PR #131.
* **Reproduction du notebook 03** : pour les 73 questions, les rangs du premier passage pertinent d'E5 et de BM25 V3, jusqu'au 10e, sont identiques à ceux publiés. Le Recall@5 d'E5 est retrouvé (33 sur 73), et le MRR@10 aussi (0,326), sans avoir été visé.

## 3. Critère principal : rappel du contexte

| | R0 | Récupération v2 |
|---|---|---|
| Questions dont le contexte contient un passage pertinent | 33 sur 73 (45,2 %) | 53 sur 73 (72,6 %) |

| Les deux réussissent | v2 seule | R0 seule | Aucune |
|---|---|---|---|
| 31 | 22 | 2 | 18 |

* **Écart apparié** : +27,4 points, intervalle de Wald à 95 % robuste aux fiches [+16,3 ; +38,5]. L'intervalle d'Agresti-Min, qui ne tient pas compte des fiches, donne [+15,1 ; +38,3].
* **Test d'Obuchowski** (61 fiches) : χ² = 16,39, p = 5,1 × 10⁻⁵. Le test binomial exact sur les 24 paires discordantes donne p = 3,6 × 10⁻⁵.
* **Conclusion selon le protocole 07** : la borne basse de l'intervalle est positive. **L'amélioration est démontrée.**

## 4. Critères secondaires

| Critère | R0 | v2 | Écart [IC 95 %] | p d'Obuchowski | p corrigé (Holm) |
|---|---|---|---|---|---|
| Recall@5 du classement v2, à budget égal de 5 passages | 45,2 % | 68,5 % | +23,3 [+12,7 ; +33,9] | 2,3 × 10⁻⁴ | 4,7 × 10⁻⁴ |
| Rappel au niveau de la fiche | 80,8 % | 94,5 % | +13,7 [+5,1 ; +22,3] | 8,0 × 10⁻³ | 8,0 × 10⁻³ |

Descriptifs :
* **MRR@10** : 0,326 pour R0, 0,528 pour la v2.
* **Tokens du prompt** : 1 672 en moyenne pour R0 ; 4 004 en moyenne et 5 517 au plus pour la v2, sous le plafond de 7 616. Aucune question n'est coupée par le budget.

## 5. Lecture

* **Le gain ne vient pas seulement du nombre de passages.** À 5 passages, la v2 atteint déjà 68,5 %, plus que les 10 premiers passages d'E5 seul (58,9 %, notebook 03). Le classement lui-même est meilleur, grâce à la fusion avec BM25 et au reclasseur. Ce dernier est la partie de la v2 sur laquelle le lot de test n'avait encore rien révélé.
* **Le gain est plus grand que sur le CDTN** : +27,4 points ici, contre +14,2. Les deux jeux ne mesurent pas la même chose. Le CDTN juge par section, avec plusieurs passages pertinents et une référence plus haute (70,9 %) ; le lot de test juge sur un seul extrait. Le chiffre du CDTN reste le plus prudent.
* **Deux questions seulement sont perdues** par la v2 par rapport à R0, contre 22 gagnées.

## 6. Limites

* **Récupération seule** : l'effet sur les réponses du modèle n'est pas mesuré. Un contexte deux fois plus long, moins précis et classé autrement peut aider ou gêner le générateur. L'adaptateur a en outre été entraîné sur des contextes de 5 passages d'E5.
* **Lot de test déjà exploité pour E5 et BM25** (protocole 07, section 8). Les choix de la v2 ont été faits sur le CDTN, et k = 10 a été fixé d'avance ; la composante sans précédent sur ce lot est le reclasseur.
* **Extrait unique** : la règle D4 ne connaît qu'un extrait par question, ce qui sous-estime les deux systèmes. Le jugement manuel des passages (#139) sert d'analyse de sensibilité.
* **Effectif** : 73 questions et 61 fiches. Les intervalles sont larges, mais leur borne basse reste nettement positive.

## 7. Reproduction

* **Commande** : `python scripts/recuperation/confirmer_test.py`. Elle s'arrête si le protocole, le script ou le module diffèrent du commit `b1a36b1`.
* **Empreintes SHA-256 des sorties** (`data/evaluation/recuperation/confirmation/`, non versionné) : `resultats.json` `3679f6fbed8a36ba…`, `questions.csv` `5a829be7d4fa2b25…`. Protocole 07 : `0d460075167a80ad…`.
* **Durée** : 3 min 29 s sur le Mac, dont le reclassement de 1 460 couples par bge-m3 sur CPU.

## 8. Suite

* **Chaîne complète, à titre exploratoire** après la mesure du protocole 06 : B2 avec la récupération v2, modèle de base et modèle adapté, sur la même machine.
* **#139** : jugement manuel des passages, pour la sensibilité et pour évaluer les voisins.
* **Démonstration** : bge-m3 demande de l'ordre de 2 s par question sur CPU ; à mesurer sur le Legion avant de l'intégrer à la #128.
