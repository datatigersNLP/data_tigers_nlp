# Protocole de la mesure de l'encodeur ajusté

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** Issue #49, mesure unique avant et après l'ajustement fin  
**Responsables** Remy RAYANE (ajustement), Mahé BEGNIS (mesure)  
**Statut** proposé le 10 octobre 2026, complété le 13 octobre (recette d'export, témoin, hébergement), puis le 14 octobre (hébergement par élagage, seuil d'abstention), à figer au Weekly 5 du 14 octobre, avant toute mesure de l'encodeur ajusté  

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
* **Fidélité, constatée avant le gel.** Dans le navigateur, sur les 822 requêtes, le premier résultat est celui du fp32 pour 769 requêtes avec l'ajusté livré (q8 `934a202b…`), 761 avec le témoin et 755 avec le q8 servi ; l'écart entre l'ajusté et le témoin n'est pas significatif (McNemar exact, 53 contre 45, p = 0,48), mais les vecteurs de l'ajusté s'écartent davantage de son fp32 (cosinus médian de 0,9938, contre 0,9965 pour le témoin). Les chiffres publiés le 13 octobre (753 sur 822, p = 0,50) portaient sur un q8 antérieur, quantifié sans `ActivationSymmetric` : ils sont reproduits exactement avec cette ancienne recette, et remplacés ici par ceux du q8 livré, mesurés le 14 octobre. Ces chiffres étaient connus avant le gel : ils sont rapportés et ne servent pas de critère.
* **Reproductibilité, vérifiée le 14 octobre.** À partir des poids livrés (`model.safetensors`), le script 06 redonne bit à bit les deux fichiers ONNX livrés, fp32 et q8. La parité fp32 est atteinte sur les 822 requêtes de contrôle (cosinus minimal de 1,00000000). Les 199 tenseurs ont la forme de ceux du modèle de base ; l'ajustement les a modifiés de 1,1e-3 en médiane, en valeur relative.
* **Tokeniseur, proposition soumise au gel.** Celui du modèle livré a été réécrit par transformers 5.18 : même vocabulaire et mêmes scores, mais prétraitement écrit autrement. Le découpage est identique pour les 822 requêtes de contrôle, les 113 textes de la mesure du notebook 03 et les 4 240 passages, mais différent pour 6 des 607 formulations du CDTN (un espace final). Pour que l'ajusté ne diffère de l'encodeur de base que par ses poids, il est mesuré et servi avec le tokeniseur de l'encodeur de base.
* **Index.** Les 4 240 passages M2 (colonne `entree_encodeur`) sont réencodés en fp32 par l'encodeur ajusté, comme l'index du site (configuration A du notebook 02 : index en fp32, requête en q8), puis exportés au format du site avec leur en-tête. Le notebook de mesure les réencode lui-même et compare le résultat au fichier `passage_embeddings_apres.npy` de Remy. Contrôle préalable du 14 octobre : cosinus minimal de 0,99999984 entre les deux, et chaque passage retrouve sa ligne, à trois passages en double près.

Empreintes SHA-256, à contrôler à la réception des fichiers :

```
data/adaptation/train_paires.jsonl (109 paires, 174 552 octets)
2d377eb66e7f4ca0e8e4cf34b089e5da7c46e47ddceab9f964764df468c21698
models/multilingual-e5-small-finetuned/model.safetensors (ajusté, poids)
5b8db94ade7f3a05678a6cb36e4e49aa7d24f71aaaedfc5fcef43d811d2dee06
models/multilingual-e5-small-finetuned/onnx/model_quantized.onnx (ajusté)
934a202bee5599fc45c0cb753414a7b2b490605bed84e72f471072e6ee53d047
data/adaptation/passage_embeddings_apres.npy (index de Remy)
94e9f52a67b8e259bf04d341338e2e51f558661fbefb1502f6b0049fe218b3ed
models/multilingual-e5-small-base/onnx/model_quantized.onnx (témoin)
30ae0f2153f7e14ce5afe082c68ee251d0cce6c26e8caa71307fbd8ebf4bcb90
```

Les fichiers de l'ajusté ont été reçus le 14 octobre, conformes au manifeste de Remy. L'empreinte du témoin et celles des deux ONNX de l'ajusté ont été reproduites indépendamment, à partir du script ; celle des paires est déclarée par Remy.

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

* **Contrainte.** Le q8 ajusté pèse 118 371 400 octets, soit 112,9 Mio. GitHub bloque tout fichier de plus de 100 Mio : en l'état, il ne peut être ni versionné, ni servi par GitHub Pages.
* **Solution : l'élagage sans perte du vocabulaire (#50).** On retire du tokeniseur et de la table des mots les pièces qui contiennent une lettre d'un autre alphabet que le latin ou le grec, sans requantifier les lignes gardées. Pour tout texte écrit avec les caractères gardés, le découpage en jetons est inchangé, donc les vecteurs aussi. C'est ainsi que le site sert l'encodeur de base, depuis le dépôt (`front/public/modele/`), dans un dossier nommé d'après l'empreinte du fichier pour qu'aucun cache ne serve une ancienne version.
* **Ce qu'il donne sur l'encodeur de base.** Le fichier passe de 112,9 à 65,7 Mio. Le découpage est identique pour tous nos textes français (requêtes de contrôle, questions de la mesure, CDTN, passages), et les 822 vecteurs de contrôle sont identiques bit à bit dans le navigateur.
* **Condition pour l'ajusté.** La mesure de la section 3 porte sur le q8 ajusté complet. S'il est retenu, il est élagué par le même script, et sa version élaguée doit redonner bit à bit, dans le navigateur, les vecteurs de la version complète sur les 822 requêtes de contrôle ; sinon, il n'est pas servi.
* **Seuil d'abstention.** L'ajustement change la distribution des scores : le seuil est recalculé par `scripts/evaluation/cdtn_seuil.py`, selon la règle de la section 8.2 du protocole du notebook 03, avec les variantes du CDTN encodées dans le navigateur par l'encodeur retenu. Tant qu'il ne l'est pas, le moteur du site n'applique aucun seuil.
* **Licence.** Licence MIT de l'encodeur d'origine, jointe au modèle ; provenance des passages (fiches du ministère, Etalab 2.0) et des questions générées (Qwen2.5-7B-Instruct, Apache 2.0).
* **Contrôle.** Avant la fusion, le contrôle 4 du notebook 02 (intégrité de l'export, vérifiée dans le navigateur) est rejoué avec le nouvel en-tête.

---

## 6. Calendrier

| Date | Étape | Qui |
|---|---|---|
| 13 octobre | Recette figée et déclaration ; recette d'export, témoin et contrôles de fidélité dans le navigateur | Remy, vérifié par Mahé |
| 14 octobre | Protocole figé au Weekly 5 ; notebook 05 en mode développement ; transmission privée de l'ajusté, en PyTorch et en ONNX | Remy, Mahé |
| 15 octobre | Import des trois relectures du CDTN ; parité de l'ajusté ; mesure unique et exécution de contrôle | Mahé, Remy |
| 16 octobre | Décision selon la section 4 ; rapport ; si l'ajusté est retenu, élagage, contrôle d'identité dans le navigateur et nouveau seuil d'abstention | Mahé, Remy |
| 17 octobre | Index et en-tête du modèle retenu dans le site ; contrôle 4 du notebook 02 | Maïmouna, Vaneck |

---

## 7. Historique

* **10 octobre 2026.** Protocole proposé.
* **13 octobre 2026.** Complété avant toute mesure de l'encodeur ajusté : recette d'export et empreintes, fidélité constatée, témoin descriptif, encodage dans le navigateur seulement, notebook de mesure, hébergement sur le Hub, calendrier.
* **14 octobre 2026.** Hébergement par élagage sans perte du vocabulaire, depuis le dépôt, à la place du Hub ; contrôle d'identité de l'ajusté élagué ; seuil d'abstention recalculé pour l'encodeur retenu. Puis, à la réception des fichiers : fidélité corrigée (769 sur 822, sur le q8 livré), reproductibilité vérifiée, empreintes des poids et de l'index, proposition sur le tokeniseur. Toujours avant toute mesure de l'encodeur ajusté ; la règle de décision ne change pas.
