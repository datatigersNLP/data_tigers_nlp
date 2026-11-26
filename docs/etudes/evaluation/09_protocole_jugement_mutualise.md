# Protocole du jugement mutualisé et des métriques à plusieurs passages

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** Issue #139, évaluation de la récupération : métriques multi-passages et jugement mutualisé du lot de test  
**Responsable** Mahé BEGNIS (mesure)  
**Statut** rédigé et figé le 16 novembre 2026, avant tout jugement. Avant le gel, seule la taille du vivier a été calculée (section 3) ; aucun passage n'a été jugé et aucune métrique corrigée n'a été calculée  

---

## 1. Objet

Nos mesures de recherche reposent sur la règle D4 (`03_protocole.md`, section 3) : chaque question du jeu `jeu-questions-v1` a un seul extrait de référence, et un passage n'est pertinent que s'il en reprend un fragment suffisant. Deux faits montrent que cette règle sous-estime tous les systèmes.

* **Accord entre annotateurs.** Sur les 15 questions du corpus annotées deux fois, les deux annotateurs désignent la même fiche 14 fois, mais les mêmes passages pertinents 7 fois seulement (`03_protocole.md`, section 2).
* **Échecs sur la bonne fiche.** Avec l'encodeur ajusté servi, 17 des 27 questions sans passage pertinent dans les 5 premiers en ont un de la bonne fiche (`05_resultats_ajustement.md`).

Ce protocole mesure l'ampleur de cette sous-estimation, sans changer aucune décision passée.

* **Jugement mutualisé du lot de test.** Les passages montrés par les systèmes et non pertinents selon D4 sont jugés à l'aveugle, ce qui donne, à côté du minorant D4, un majorant de chaque métrique.
* **Métriques à plusieurs passages sur le CDTN**, qui a plusieurs passages pertinents par requête.
* **Analyse des échecs**, du volet A et du volet B.
* **M4 recalculé et requalifié.** M4 dit si une réponse cite un passage pertinent : c'est une mesure de traçabilité, pas d'exactitude. L'exactitude reste jugée à part (#52).

Toutes les mesures de ce protocole sont **descriptives**. Le lot de test a déjà été exploité cinq fois (notebook 03, protocoles 05, 06, 07 et 08) ; il n'est ici ni rejoué par un nouveau système ni utilisé pour régler quoi que ce soit, mais complété par de nouveaux jugements. L'encodeur ajusté reste servi (protocole 05), et B2 reste la chaîne de référence du volet B (protocole 08).

---

## 2. Systèmes et sorties jugés

Uniquement des sorties déjà produites et publiées, relues sans rien recalculer d'autre que leur classement.

* **Volet A, base servie et ajusté** : les 10 premiers passages de chaque question du corpus du lot de test, classés par produit scalaire entre le vecteur de la question calculé dans le navigateur (fichiers de la mesure de A1) et l'index du site (base) ou l'index fp32 de l'ajusté, comme `ajustement_05.py`.
* **Volet B, modèle adapté** : les contextes et les passages cités des états B2 (protocole 06, 5 passages) et V1, V2 (protocole 08, 10 passages). Le témoin T n'est pas couvert.
* **Questions** : les 73 questions du corpus du lot de test. Les questions hors corpus ne sont pas jugées.

---

## 3. Vivier, contrôles et feuilles

* **Vivier** : toutes les paires (question, passage) telles que le passage figure dans les 5 ou les 10 premiers d'un système du volet A pour une question où ce système n'a aucun passage pertinent selon D4 à cette profondeur, ou dans le contexte d'un état du volet B qui n'en contient aucun, ou parmi les passages cités d'une réponse dont aucune citation n'est pertinente selon D4. Les sorties en erreur technique, exclues des mesures du volet B, n'y entrent pas (Q088 en B2). Calculé le 16 novembre avant le gel : **617 paires** sur 53 questions. Un premier comptage, qui gardait le contexte de Q088 en B2, en donnait 618 ; la seule paire en plus était inutile à toute mesure.
* **Pourquoi c'est suffisant.** Une métrique de succès à la profondeur k ne dépend que des k passages montrés par le système : le vivier couvre donc entièrement chaque système et chaque profondeur mesurés. Un passage qu'aucun système ne montre n'est pas jugé ; il ne change aucune métrique.
* **Contrôles positifs** : 40 questions du corpus tirées au hasard, avec pour chacune un passage pertinent selon D4 tiré au hasard. Ils mesurent la sensibilité des juges.
* **Contrôles négatifs** : 40 questions tirées au hasard, avec pour chacune un passage tiré au hasard hors de la fiche annotée, hors des fiches de ses passages pertinents et hors du vivier de la question. Ils mesurent les faux positifs.
* **Tirages** : `numpy.random.default_rng(20261116)`, dans l'ordre suivant : contrôles positifs, contrôles négatifs, puis mélange des 697 paires.
* **Feuilles** : les 697 paires mélangées, réparties en 7 lots de 100 paires au plus, chacune sous un identifiant neutre (J0001 à J0697). Une paire montre la question, le titre de la fiche, le chemin de la section et le texte du passage, tels que le site les affiche. Elle ne montre ni l'adresse, ni l'identifiant du passage, ni le système, ni le rang, ni l'extrait annoté, ni la nature de la paire (vivier ou contrôle). La clé qui relie les identifiants aux paires reste hors des feuilles.
* **Données** : les questions ont été rédigées par l'équipe et les passages viennent de fiches publiques du ministère du Travail ; les feuilles ne contiennent aucune donnée personnelle.

---

## 4. Consigne et échelle

La consigne est la même pour tous les juges, mot pour mot :

> Chaque paire associe une question de droit du travail, posée comme le ferait un salarié ou un employeur, et un passage d'une fiche du ministère du Travail (titre de la fiche, chemin de la section, puis texte). Jugez seulement si ce passage, lu seul, permet de répondre à la question. « répond » : le passage contient l'information qui répond à la question posée ; une réponse qu'il faut nuancer par des conditions ou des exceptions présentes dans le passage compte comme une réponse. « en partie » : le passage donne un élément utile de la réponse (une condition, un cas, une partie d'une liste), mais pas l'essentiel, ou il répond à une question voisine, plus générale ou plus restreinte. « ne répond pas » : le passage traite d'un autre sujet, ou du même sujet sans donner d'élément de réponse. Ne jugez ni l'exactitude juridique ni la date du passage, et n'utilisez aucune connaissance extérieure pour compléter un passage incomplet.

* **Verdict** : une seule valeur par paire, `repond`, `en_partie` ou `ne_repond_pas`, et un motif d'une phrase.

---

## 5. Juges

* **Deux juges d'IA, déclarés non humains**, qui jugent tout le vivier et tous les contrôles : J1, Claude Opus 5.5, et J2, Claude Sonnet 5.5, deux modèles d'Anthropic d'une autre famille que le générateur du volet B (Qwen). Chaque lot est jugé dans un contexte neuf, qui ne contient que la consigne, la feuille du lot et le format de réponse : aucun juge ne voit les verdicts de l'autre, la clé, les résultats ou ce protocole.
* **Écart déclaré au #139**, qui prévoyait un jugement à la main : le vivier de 617 paires ne peut pas être jugé deux fois à la main avant la V1 du rapport (19 novembre). Le jugement humain sert donc d'étalonnage.
* **Étalonnage humain** : 100 paires tirées parmi les 697 (`default_rng(20261117)`) : 80 du vivier, 10 contrôles positifs et 10 négatifs, mélangées sous de nouveaux identifiants. Elles sont jugées avec la même consigne par deux membres de l'équipe désignés par Mahé, qui ne sont pas juges du #52, sans voir les verdicts des juges d'IA. La feuille ne contient aucune réponse du volet B.

---

## 6. Règles d'agrégation et de fiabilité, écrites d'avance

* **Fiabilité d'un juge** : il juge `repond` ou `en_partie` au moins 32 des 40 contrôles positifs (80 %), et au plus 2 des 40 contrôles négatifs (5 %). Un juge qui échoue est écarté ; si les deux échouent, aucun majorant n'est publié.
* **Pertinence jugée, règle principale (prudente)** : les deux juges fiables jugent `repond`. Si un seul juge est fiable, son verdict `repond` suffit, et c'est déclaré.
* **Pertinence jugée, règle large (sensibilité)** : au moins un juge fiable juge `repond` ou `en_partie`.
* **Minorant** : la pertinence selon D4, inchangée. **Majorant principal** : D4, ou pertinence jugée par la règle principale. **Majorant large** : D4, ou pertinence jugée par la règle large.
* **Pertinence d'une fiche** : elle contient un passage pertinent selon la définition retenue.
* **Accord entre juges** : kappa de Cohen à trois classes, sans pondération et avec une pondération linéaire, sur les 617 paires du vivier, avec un intervalle à 95 % par rééchantillonnage des paires (10 000 tirages, graine 20261116).
* **Étalonnage humain, quand il est disponible** : kappa entre les deux humains, puis entre le consensus humain (les deux humains jugent `repond`) et la règle principale des juges d'IA, sur les paires du vivier de l'échantillon. **Si ce second kappa est inférieur à 0,6, les majorants sont déclarés non étayés.** Tant que l'étalonnage n'est pas revenu, les majorants sont publiés comme provisoires.

---

## 7. Mesures

* **Contrôles de reproduction, préalables** : sous D4, le calcul doit redonner exactement les chiffres publiés.
* **Volet A, reproduction** : Recall@5 de 32 et 46 questions sur 73, Recall@10 de 42 et 54, Recall@5 à la fiche de 61 et 63, pour la base et l'ajusté (mesure de A1).
* **Volet B, reproduction** : passage pertinent dans le contexte pour 33 questions sur 72 (B2), 53 sur 73 (V1, V2) ; M4 de 18 sur 72, 24 sur 73 et 27 sur 73.
* **CDTN, reproduction** : succès à 5 de la base et de l'ajusté égal à celui de la mesure de A1 (67,4 % et 72,3 %), à 10⁻¹² près.
* **Volet A** : pour la base et l'ajusté, succès à 5 et à 10 au niveau du passage, succès à 5 au niveau de la fiche, sous le minorant, le majorant principal et le majorant large ; intervalle de Wilson corrigé de l'effet de plan par fiche annotée. Écart de l'ajusté à la base sous chaque définition : intervalle du score de Tango corrigé de l'effet de plan et valeur p exacte de McNemar.
* **Volet B** : pour B2, V1 et V2, part des questions dont le contexte contient un passage pertinent (plafond) et M4, sous les trois définitions, sur les questions sans erreur technique, avec les mêmes intervalles que le protocole 08 ; écarts appariés de M4, V2 moins B2, V1 moins B2 et V2 moins V1, sur les questions sans erreur technique dans les deux états, avec l'intervalle du score de Tango corrigé de l'effet de plan et la valeur p exacte de McNemar.
* **Analyse des échecs du volet A** (ajusté et base, à 5 passages, règle principale) : chaque échec D4 est classé « autre passage valable » (un passage montré est jugé pertinent), « bonne fiche, passage insuffisant » (sinon, un passage montré vient d'une fiche pertinente selon D4), ou « mauvaise fiche ».
* **Analyse des échecs du volet B** (B2, V1 et V2, règle principale) : chaque question du corpus sans M4 est classée « récupération » (aucun passage pertinent dans le contexte), « abstention du modèle », « abstention sous le seuil », « citation non pertinente » (réponse citée, passage pertinent fourni mais non cité) ou « sortie invalide ».
* **CDTN** (494 formulations, 131 requêtes, passages pertinents de la population du protocole 07) : pour la base et l'ajusté (vecteurs du navigateur de la mesure de A1) et pour BM25 V3 (`data/evaluation/recuperation/classements.json`) : succès à 5 et à 10, rappel à 5 et à 10 sur l'ensemble des passages pertinents (part des passages pertinents retrouvés, moyennée par formulation), nDCG@10 à gains binaires, précision à 5. Écart de l'ajusté à la base pour chaque métrique. Intervalles à 95 % par rééchantillonnage des requêtes (10 000 tirages, graine 20261116), apparié pour les écarts. Les jugements du CDTN de 2021 ne sont pas exhaustifs : la précision est sous-estimée, et elle est rapportée comme telle.
* **Deux exécutions** du calcul, au contenu identique, puis un recalcul indépendant hors du dépôt.

---

## 8. Limites déclarées

* **Juges d'IA** : leurs verdicts ne remplacent pas un jugement humain ; ils sont étalonnés par 100 paires jugées par deux membres de l'équipe (section 5).
* **Lot de test usé** : sixième exploitation, descriptive, sans nouveau système.
* **Exactitude non mesurée** : un passage pertinent cité ne garantit pas une réponse juste. L'exactitude des réponses du volet B reste jugée par le #52, sur 20 réponses, à titre descriptif.
* **Témoin T et questions hors corpus** : non couverts.
* **Contrôle de l'ancrage des citations**, affirmation par affirmation : reste à la feuille de route du #139.

---

## 9. Valeurs inscrites au gel

* **Jeu** : `jeu-questions-v1`, commit `cdb48c9`, empreinte contrôlée par `scripts/rag/mesure.py`.
* **Mesure de A1** : `data/evaluation/ajustement_05/mesure_20261115T142540Z.json`, SHA-256 `d35b4936…`.
* **Sorties du volet B** : `B2.jsonl` (protocole 06), `V1.jsonl` et `V2.jsonl` (protocole 08) ; leurs empreintes sont contrôlées par `scripts/evaluation/jugement_139.py`.
* **Graines** : 20261116 (contrôles, mélange, rééchantillonnages), 20261117 (étalonnage humain).

---

## 10. Historique

* **16 novembre 2026** : protocole rédigé et figé avant tout jugement ; taille du vivier calculée avant le gel.
