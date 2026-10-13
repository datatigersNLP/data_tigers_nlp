# Protocole de la mesure de l'encodeur ajusté

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** Issue #49, mesure unique avant et après l'ajustement fin  
**Responsables** Remy RAYANE (ajustement), Mahé BEGNIS (mesure)  
**Statut** proposé le 10 octobre 2026, complété le 13 octobre (recette d'export, témoin, hébergement), à figer au Weekly 5 du 14 octobre, avant toute mesure de l'encodeur ajusté  

---

## 1. Objet

Décider, par une mesure unique écrite d'avance, si le site sert l'encodeur ajusté sur notre corpus ou l'encodeur de base, pour la finalisation du volet A le 18 octobre. Sur le jeu de l'équipe, le notebook 03 fournit la mesure « avant » (mesure unique du 13 octobre, PR #73) ; ce protocole ne la refait pas.

* **Déclaration.** La PR #63, fermée sans fusion le 7 octobre puis rouverte le 13 octobre, a déjà évalué l'encodeur de base et un encodeur ajusté sur le lot de test. Ces chiffres sont exploratoires (Weekly 4, décision 2) et ne servent pas à cette mesure. Le 13 octobre, sur #49, Remy a déclaré qu'aucun hyperparamètre n'avait été modifié après les avoir vus ; la recette est figée à cette date.

---

## 2. Conditions préalables

* **Recette d'entraînement figée.** 109 paires question-passage générées en local par Qwen2.5-7B, sans graine : le fichier `data/adaptation/train_paires.jsonl` n'est pas versionné, mais il est identifié par son empreinte et conservé par Remy. Ajustement par `MultipleNegativesRankingLoss`, lots de 16, taux d'apprentissage de 2e-5, 2 époques, graine d'entraînement 42, détaillés dans `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md`. Aucun réglage n'utilise le lot de test ni le CDTN.
* **Étanchéité.** Les fiches du jeu de l'équipe sont exclues de l'entraînement, comme dans la PR #63 ; le filtre de Jaccard contre les questions de test est conservé et documenté comme un écart assumé au critère de #49.
* **Recette d'export figée.** `scripts/adaptation/06_exporter_onnx.py`, au commit `7001645` : export ONNX en opset 14, puis quantification dynamique `QInt8`, par canal, avec `reduce_range` et `ActivationSymmetric`, sous onnx 1.23.2 et onnxruntime 1.30.0. Appliquée au modèle de base, elle redonne bit à bit 74 des 75 tenseurs quantifiés du q8 servi, le dernier à une valeur près sur 96 millions, mais pas son graphe : dans le navigateur, les deux modèles donnent un premier résultat différent pour 52 des 822 requêtes de contrôle du notebook 02, pour une fidélité globale égale (761 et 755 sur 822, McNemar p = 0,46).
* **Parité, condition du déploiement.** L'encodeur ajusté exporté en fp32 redonne les vecteurs de PyTorch : cosinus minimal d'au moins 0,99999 sur les 822 requêtes de contrôle du notebook 02, le seuil de son contrôle 1.
* **Fidélité, constatée avant le gel.** Dans le navigateur, sur les 822 requêtes, le premier résultat est celui du fp32 pour 753 requêtes avec l'ajusté, 761 avec le témoin et 755 avec le q8 servi ; l'écart entre l'ajusté et le témoin n'est pas significatif (McNemar exact, p = 0,50), mais les vecteurs de l'ajusté s'écartent davantage de son fp32 (cosinus médian de 0,9939, contre 0,9965 pour le témoin). Ces chiffres étaient connus avant le gel : ils sont rapportés et ne servent pas de critère.
* **Index.** Les 4 240 passages M2 (colonne `entree_encodeur`) sont réencodés en fp32 par l'encodeur ajusté, comme l'index du site (configuration A du notebook 02 : index en fp32, requête en q8), puis exportés au format du site avec leur en-tête. Le notebook de mesure les réencode lui-même et compare le résultat au fichier `passage_embeddings_apres.npy` de Remy.

Empreintes SHA-256, à contrôler à la réception des fichiers :

```
data/adaptation/train_paires.jsonl (109 paires, 174 552 octets)
2d377eb66e7f4ca0e8e4cf34b089e5da7c46e47ddceab9f964764df468c21698
models/multilingual-e5-small-finetuned/onnx/model_quantized.onnx (ajusté)
934a202bee5599fc45c0cb753414a7b2b490605bed84e72f471072e6ee53d047
models/multilingual-e5-small-base/onnx/model_quantized.onnx (témoin)
30ae0f2153f7e14ce5afe082c68ee251d0cce6c26e8caa71307fbd8ebf4bcb90
```

L'empreinte du témoin a été reproduite indépendamment, à partir du script ; celles de l'ajusté et des paires sont déclarées par Remy.

---

## 3. Mesure

* **E5 de base servi.** Le q8 de Xenova (révision `761b726d`) et l'index du site. Sur le jeu de l'équipe, ses résultats sont ceux du notebook 03.
* **E5 ajusté servi.** Le q8 ajusté et son index.
* **Témoin, à titre descriptif.** Le modèle de base passé par la même recette d'export, avec l'index du site. Il sépare l'effet de l'export (témoin moins base servie) de celui de l'ajustement (ajusté moins témoin).
* **Encodage.** Les questions et les formulations du CDTN sont encodées dans le navigateur en q8, par la page d'encodage du notebook 03 étendue aux modèles locaux, son comportement par défaut restant inchangé, sur la machine et le navigateur de la mesure du notebook 03. Seuls les vecteurs du navigateur sont utilisés : le contrôle du témoin a donné les mêmes chiffres sur deux machines (Windows x86 et Mac ARM), alors que le même calcul en Python sur processeur a donné 762 et 791 sur 822.
* **Jeux.** Le lot de test figé (`jeu-questions-v1`, 73 questions du corpus, 24 hors corpus), avec la règle de pertinence D4 du protocole du notebook 03 ; le jeu du CDTN (`04_cdtn.md`), réduit aux requêtes jugées `oui` ou `partiel` à la relecture, sans les formulations écartées, après l'import des trois relectures.
* **Métrique principale.** Recall@5 au niveau du passage, comparée par paires.
* **Écart.** Recall@5 de l'ajusté moins celui de la base servie, avec l'intervalle du score de Tango corrigé de l'effet de plan (`noninferiority_tango`, `03_audit_statistique.md`) : questions groupées par fiche pour le jeu de l'équipe, formulations groupées par requête pour le CDTN. Le même calcul compare, à titre descriptif, le témoin à la base servie et l'ajusté au témoin.
* **Également rapportés.** Recall@1 et @10, MRR@10, niveau de la fiche, AUC de l'abstention sur le lot de test.
* **Notebook.** `scripts/evaluation/05_ajustement.ipynb` réutilise la règle de pertinence D4, le module de métriques et, pour la base servie, les vecteurs de la mesure du notebook 03. Il ne lit le lot de test qu'en mode mesure, et seulement si les empreintes de ce protocole, du jeu, des deux modèles, de l'index ajusté et des jugements du CDTN sont celles inscrites. Comme le notebook 03, il est exécuté une fois par nbclient, puis une seconde fois pour contrôle.

---

## 4. Règle de déploiement, écrite d'avance

* **Servir l'encodeur ajusté** si sa parité passe (section 2), si son écart observé de Recall@5 avec la base servie est positif ou nul à la fois sur le jeu de l'équipe et sur le CDTN, et s'il peut être hébergé comme le prévoit la section 5 avant le 17 octobre.
* **Garder l'encodeur de base** dans tous les autres cas.
* **Pourquoi deux jeux.** Sur 73 questions, aucun test ne détecte un gain de quelques points. Exiger le même sens sur deux jeux indépendants protège d'un hasard favorable sur l'un d'eux. Par simulation, sur la structure des deux jeux et avec 20 % de désaccord entre modèles, la règle sert l'ajusté dans 0,0 % des cas s'il est réellement moins bon de 10 points, 1,2 % s'il l'est de 5 points, 28 % à égalité, 80 % s'il est meilleur de 5 points et 97,6 % s'il l'est de 10 points.
* **Conclusion statistique.** L'ajusté n'est déclaré meilleur que si la borne basse de l'intervalle de l'écart sur le jeu de l'équipe dépasse 0 ; sinon, le rapport dit seulement que l'écart n'est pas démontré.
* **Le témoin ne décide de rien.** Il sert à interpréter l'écart, pas à choisir le modèle servi.

---

## 5. Hébergement de l'encodeur ajusté

* **Contrainte.** Le q8 ajusté pèse 118 371 400 octets, soit 112,9 Mio. GitHub bloque tout fichier de plus de 100 Mio : il ne peut être ni versionné, ni servi par GitHub Pages depuis le dépôt.
* **Solution.** Le site charge déjà son modèle depuis le Hub de Hugging Face, au dépôt et à la révision inscrits dans l'en-tête de l'index (`front/src/recherche/moteur.js`). Si l'ajusté est retenu, il est publié dans un dépôt public de modèle sur le Hub, avec ses fichiers de configuration et de tokeniseur ; l'en-tête désigne ce dépôt à une révision figée, et le fichier ONNX publié doit avoir l'empreinte de la section 2.
* **Fiche du modèle.** Licence MIT de l'encodeur d'origine, provenance des passages (fiches du ministère, Etalab 2.0) et des questions générées (Qwen2.5-7B-Instruct, Apache 2.0), renvoi vers ce protocole.
* **Identifiants.** Le membre qui publie utilise son propre compte ; aucun jeton n'est partagé ni versionné.
* **Contrôle.** Après la publication, le contrôle 4 du notebook 02 (intégrité de l'export, vérifiée dans le navigateur) est rejoué sur le site avec le nouvel en-tête.

---

## 6. Calendrier

| Date | Étape | Qui |
|---|---|---|
| 13 octobre | Recette figée et déclaration ; recette d'export, témoin et contrôles de fidélité dans le navigateur | Remy, vérifié par Mahé |
| 14 octobre | Protocole figé au Weekly 5 ; notebook 05 en mode développement ; transmission privée de l'ajusté, en PyTorch et en ONNX | Remy, Mahé |
| 15 octobre | Import des trois relectures du CDTN ; parité de l'ajusté ; mesure unique et exécution de contrôle | Mahé, Remy |
| 16 octobre | Décision selon la section 4 ; rapport ; si l'ajusté est retenu, publication sur le Hub | Mahé, Remy |
| 17 octobre | Index et en-tête du modèle retenu dans le site ; contrôle 4 du notebook 02 | Maïmouna, Vaneck |

---

## 7. Historique

* **10 octobre 2026.** Protocole proposé.
* **13 octobre 2026.** Complété avant toute mesure de l'encodeur ajusté : recette d'export et empreintes, fidélité constatée, témoin descriptif, encodage dans le navigateur seulement, notebook de mesure, hébergement sur le Hub, calendrier.
