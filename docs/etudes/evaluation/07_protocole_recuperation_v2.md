# Protocole 07 : confirmation de la récupération v2 sur le lot de test

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Tickets** #138 (récupération v2), #139 (évaluation de la récupération)  
**Responsable** Mahé BEGNIS  
**Statut** figé le 9 novembre 2026, avec l'accord de Mahé, avant toute lecture du lot de test par la récupération v2. Le protocole 06 et son verrou ne sont pas modifiés.

---

## 1. Objet

Vérifier une seule fois, sur le lot de test, que la configuration de récupération retenue sur le jeu CDTN (#138, amendement A1) met plus souvent un passage pertinent dans le contexte du modèle que la chaîne actuelle. Cette confirmation porte sur la récupération seule : aucune réponse n'est générée.

## 2. Systèmes comparés

* **Référence R0** : la chaîne de B1, soit E5 en fp32 sur l'index M2 et les 5 premiers passages (`rag.recuperer_passages`).
* **Récupération v2** : la configuration retenue par l'amendement A1, `rrf+k10+bge-m3@20`. Elle fusionne les 100 premiers passages d'E5 et de BM25 V3 (RRF, k = 60), fait reclasser les 20 premiers par `BAAI/bge-reranker-v2-m3` (révision `953dc6f6`), et donne les 10 premiers au modèle, sans voisins, sous le budget de 7 616 tokens.
* **Ce qui ne change pas** : le même index, le même encodeur et la même abstention (seuil S sur le cosinus maximal d'E5).

Empreinte SHA-256 des résultats de la grille (`data/evaluation/recuperation/resultats_grille.json`) :

```
2c8619caf32d043cdc7f497ff1ffdf5a52b407190293d23f5f2a625cc020bf4a
```

## 3. Jeu et pertinence

* **Questions** : `jeu-questions-v1`, lot de test, les 73 questions du corpus. Les 24 questions hors corpus ne sont pas concernées, car l'abstention ne change pas.
* **Pertinence** : la règle D4 (`scripts/evaluation/pertinence.py`, inchangé), à partir de l'extrait annoté de chaque question.

## 4. Critère principal

* **Rappel du contexte** : la part des 73 questions dont le contexte final contient au moins un passage pertinent.
* **Comparaison appariée** de la v2 à R0 avec `paired_success_test` (`scripts/evaluation/metrics.py`), les questions étant groupées par fiche (61 fiches) : différence, intervalle de Wald à 95 % à erreur type robuste aux fiches (`ci_difference`), et test d'Obuchowski, bilatéral, au seuil de 5 % (`p_value_groups`).
* **Conclusion** : l'amélioration n'est dite démontrée que si la borne basse de cet intervalle est positive. La p-valeur d'Obuchowski et l'intervalle d'Agresti-Min sont rapportés à côté.

## 5. Critères secondaires, descriptifs

* **Deux tests secondaires**, appariés et groupés par fiche comme le critère principal, avec leurs p-valeurs corrigées par la méthode de Holm :
* Recall@5 du classement v2, à budget égal de 5 passages, contre R0 ;
* rappel au niveau de la fiche, c'est-à-dire un passage de la fiche annotée dans le contexte, pour la v2 contre R0.
* **Descriptifs** : MRR@10 des deux classements, tokens de Qwen du prompt (moyenne et maximum), et nombre de questions dont le contexte est coupé par le budget.

## 6. Analyse de sensibilité

Les passages des contextes de R0 et de la v2 qui ne sont pas pertinents selon D4 sont jugés à la main (#139) :
* ordre mélangé et système masqué ;
* deux juges sur un sous-ensemble, pour un kappa de Cohen.

Le critère principal est recalculé avec cette pertinence élargie. Si les deux conclusions diffèrent, les deux sont publiées, et D4 reste le critère principal.

## 7. Contrôle préalable

Avant de calculer la v2, le script reproduit, pour les 73 questions, le rang du premier passage pertinent (jusqu'au 10e) d'E5 en fp32 et de BM25 V3, publiés par le notebook 03 (`rangs_mesure.csv`), ainsi que son Recall@5 d'E5 (33 questions sur 73, soit 45,2 %). Au moindre écart, il s'arrête sans rien calculer d'autre.

## 8. Déclarations

* **Le lot de test n'est pas vierge pour la récupération.** Le notebook 03 y a publié le Recall@10 d'E5 (58,9 %) et les rangs d'E5 et de BM25 V3 jusqu'au 10e passage. Le 9 novembre, des comptes exploratoires ont été faits sur ces rangs (union d'E5 et de BM25, 6 à 10 passages). Ils n'ont servi à aucun choix : k = 10 est fixé par l'amendement A1, pour des raisons de budget et d'entraînement. Pour une configuration sans reclasseur, le résultat de cette confirmation est donc en partie déductible de chiffres déjà publiés ; seul un reclasseur y apporte une information nouvelle.
* **L'amendement A1** du 9 novembre a corrigé la règle de choix avant la lecture des résultats des reclasseurs (commentaire du #138).
* **L'adaptateur** a été entraîné sur des contextes de 5 passages d'E5. L'effet de la v2 sur les réponses ne sera mesuré qu'à titre exploratoire, après la mesure du protocole 06.

## 9. Exécution

`scripts/recuperation/confirmer_test.py` refuse de lire le lot de test :
* si ce protocole, ce script ou `scripts/recuperation/recuperation.py` ne sont pas committés à l'identique ;
* si l'empreinte des résultats de la grille diffère de celle inscrite à la section 2, ou si la configuration qu'ils retiennent n'est pas `rrf+k10+bge-m3@20` ;
* si les dix empreintes de la chaîne verrouillée de la mesure diffèrent de celles de la PR #131.

Il ne calcule pas la v2 si le contrôle de la section 7 échoue. La confirmation n'est lancée qu'une fois ce protocole, le script et le module poussés sur GitHub.

Les sorties vont dans `data/evaluation/recuperation/confirmation/`.

## 10. Historique

* **9 novembre 2026** : brouillon, puis gel avec l'accord de Mahé, après la publication des résultats de la grille sur le #138 et avant toute lecture du lot de test par la récupération v2.
