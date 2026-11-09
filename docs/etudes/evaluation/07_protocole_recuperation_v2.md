# Protocole 07 : confirmation de la récupération v2 sur le lot de test

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Tickets** #138 (récupération v2), #139 (évaluation de la récupération)  
**Responsable** Mahé BEGNIS  
**Statut** brouillon du 9 novembre 2026, à figer par un commit avant toute lecture du lot de test par la récupération v2. Le protocole 06 et son verrou ne sont pas modifiés.

---

## 1. Objet

Vérifier une seule fois, sur le lot de test, que la configuration de récupération retenue sur le jeu CDTN (#138, amendement A1) met plus souvent un passage pertinent dans le contexte du modèle que la chaîne actuelle. Cette confirmation porte sur la récupération seule : aucune réponse n'est générée.

## 2. Systèmes comparés

* **Référence R0** : la chaîne de B1, soit E5 en fp32 sur l'index M2 et les 5 premiers passages (`rag.recuperer_passages`).
* **Récupération v2** : la configuration retenue par l'amendement A1, désignée par son nom et par l'empreinte SHA-256 de `data/evaluation/recuperation/resultats_grille.json`, inscrits ici au gel.
* **Ce qui ne change pas** : le même index, le même encodeur et la même abstention (seuil S sur le cosinus maximal d'E5).

## 3. Jeu et pertinence

* **Questions** : `jeu-questions-v1`, lot de test, les 73 questions du corpus. Les 24 questions hors corpus ne sont pas concernées, car l'abstention ne change pas.
* **Pertinence** : la règle D4 (`scripts/evaluation/pertinence.py`, inchangé), à partir de l'extrait annoté de chaque question.

## 4. Critère principal

* **Rappel du contexte** : la part des 73 questions dont le contexte final contient au moins un passage pertinent.
* **Comparaison appariée** de la v2 à R0 avec `paired_success_test` (`scripts/evaluation/metrics.py`), les questions étant groupées par fiche (61 fiches) : différence, intervalle à 95 % et test d'Obuchowski, bilatéral, au seuil de 5 %.
* **Conclusion** : l'amélioration n'est dite démontrée que si la borne basse de l'intervalle est positive.

## 5. Critères secondaires, descriptifs

* Recall@5 du classement v2, à budget égal de 5 passages, et MRR@10.
* Rappel au niveau de la fiche.
* Tokens de Qwen du prompt (moyenne et maximum), et nombre de questions dont le contexte est coupé par le budget de 7 616 tokens.
* Les p-valeurs secondaires sont corrigées par la méthode de Holm.

## 6. Analyse de sensibilité

Les passages des contextes de R0 et de la v2 qui ne sont pas pertinents selon D4 sont jugés à la main (#139) :
* ordre mélangé et système masqué ;
* deux juges sur un sous-ensemble, pour un kappa de Cohen.

Le critère principal est recalculé avec cette pertinence élargie. Si les deux conclusions diffèrent, les deux sont publiées, et D4 reste le critère principal.

## 7. Contrôle préalable

Avant de calculer la v2, le script reproduit le Recall@5 d'E5 en fp32 sur M2 publié par le notebook 03 (33 questions sur 73, soit 45,2 %). En cas d'écart, il s'arrête sans rien calculer d'autre.

## 8. Déclarations

* **Le lot de test n'est pas vierge pour la récupération.** Le notebook 03 y a publié le Recall@10 d'E5 (58,9 %) et les rangs d'E5 et de BM25 V3 jusqu'au 10e passage. Le 9 novembre, des comptes exploratoires ont été faits sur ces rangs (union d'E5 et de BM25, 6 à 10 passages). Ils n'ont servi à aucun choix : k = 10 est fixé par l'amendement A1, pour des raisons de budget et d'entraînement. Pour une configuration sans reclasseur, le résultat de cette confirmation est donc en partie déductible de chiffres déjà publiés ; seul un reclasseur y apporte une information nouvelle.
* **L'amendement A1** du 9 novembre a corrigé la règle de choix avant la lecture des résultats des reclasseurs (commentaire du #138).
* **L'adaptateur** a été entraîné sur des contextes de 5 passages d'E5. L'effet de la v2 sur les réponses ne sera mesuré qu'à titre exploratoire, après la mesure du protocole 06.

## 9. Exécution

`scripts/recuperation/confirmer_test.py` refuse de lire le lot de test :
* si ce fichier n'est pas committé à l'identique ;
* si l'empreinte des résultats de la grille diffère de celle inscrite à la section 2 ;
* si le contrôle de la section 7 échoue.

Les sorties vont dans `data/evaluation/recuperation/confirmation/`.

## 10. Historique

* **9 novembre 2026** : brouillon.
