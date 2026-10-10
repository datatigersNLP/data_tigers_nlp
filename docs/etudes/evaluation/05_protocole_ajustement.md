# Protocole de la mesure de l'encodeur ajusté

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** Issue #49, mesure unique avant et après l'ajustement fin  
**Responsables** Remy RAYANE (ajustement), Mahé BEGNIS (mesure)  
**Statut** proposé le 10 octobre 2026, à finaliser et figer au Weekly 5 du 14 octobre, avant toute mesure de l'encodeur ajusté  

---

## 1. Objet

Décider, par une mesure unique écrite d'avance, si le site sert l'encodeur ajusté sur notre corpus ou l'encodeur de base, pour la finalisation du volet A le 18 octobre. Le notebook 03 fournit la mesure « avant » ; ce protocole ne la refait pas.

* **Déclaration.** La PR #63, fermée sans fusion le 7 octobre, a déjà évalué l'encodeur de base et un encodeur ajusté sur le lot de test. Ces chiffres sont exploratoires (Weekly 4, décision 2). Les choix d'entraînement faits après les avoir vus doivent être déclarés ici avant la mesure.

---

## 2. Conditions préalables

* **Recette figée.** Données, paires, hyperparamètres et nombre d'époques sont figés et versionnés avant la mesure ; aucun réglage n'utilise le lot de test ni le CDTN. Les réglages se font sur le lot de calibration, sur PIAF ou sur une part réservée des paires générées.
* **Étanchéité.** Les fiches du jeu de l'équipe sont exclues de l'entraînement, comme dans la PR #63 ; le filtre de Jaccard contre les questions de test est conservé et documenté comme un écart assumé au critère de #49.
* **Modèle servi.** L'encodeur ajusté est exporté en ONNX et quantifié en q8 comme le modèle actuel, puis passe les contrôles de parité et de fidélité du notebook 02. Les 4 240 passages M2 sont réencodés avec lui, ce qui produit un nouvel index et un nouvel en-tête.

---

## 3. Mesure

* **Systèmes.** E5 de base servi et E5 ajusté servi, tous deux encodés dans le navigateur en q8, chacun avec son index M2.
* **Jeux.** Le lot de test figé (`jeu-questions-v1`, 73 questions du corpus, 24 hors corpus), avec la règle de pertinence D4 du protocole du notebook 03 ; le jeu du CDTN (`04_cdtn.md`), requêtes jugées pertinentes à la relecture.
* **Métrique principale.** Recall@5 au niveau du passage, comparée par paires.
* **Écart.** Recall@5 de l'ajusté moins celui de la base, avec l'intervalle du score de Tango corrigé de l'effet de plan (`noninferiority_tango`, `03_audit_statistique.md`) : questions groupées par fiche pour le jeu de l'équipe, formulations groupées par requête pour le CDTN.
* **Également rapportés.** Recall@1 et @10, MRR@10, niveau de la fiche, AUC de l'abstention sur le lot de test.

---

## 4. Règle de déploiement, écrite d'avance

* **Servir l'encodeur ajusté** si ses contrôles de parité passent, et si son écart observé de Recall@5 avec la base est positif ou nul à la fois sur le jeu de l'équipe et sur le CDTN.
* **Garder l'encodeur de base** dans tous les autres cas.
* **Pourquoi deux jeux.** Sur 73 questions, aucun test ne détecte un gain de quelques points. Exiger le même sens sur deux jeux indépendants protège d'un hasard favorable sur l'un d'eux. Par simulation, sur la structure des deux jeux et avec 20 % de désaccord entre modèles, la règle sert l'ajusté dans 0,0 % des cas s'il est réellement moins bon de 10 points, 1,2 % s'il l'est de 5 points, 28 % à égalité, 80 % s'il est meilleur de 5 points et 97,6 % s'il l'est de 10 points.
* **Conclusion statistique.** L'ajusté n'est déclaré meilleur que si la borne basse de l'intervalle de l'écart sur le jeu de l'équipe dépasse 0 ; sinon, le rapport dit seulement que l'écart n'est pas démontré.

---

## 5. Calendrier proposé

| Date | Étape | Qui |
|---|---|---|
| 13 octobre | Recette figée et déclaration des choix faits après la PR #63 | Remy |
| 14 octobre | Protocole finalisé et figé au Weekly 5 | Remy, Mahé |
| 15 octobre | Export ONNX q8, contrôles de parité, réencodage des passages ; mesure unique | Remy, Mahé |
| 16 octobre | Décision selon la section 4 ; rapport | Mahé |
| 17 octobre | Index et en-tête du modèle retenu dans le site | Maïmouna, Vaneck |
