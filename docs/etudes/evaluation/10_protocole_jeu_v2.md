# Protocole 10 : jeu de questions v2, étalonnage par juges d'IA et mesures du 17 novembre

**Ticket** #171, avec #172 (volet B), #173 (volet A) et #167 (encodeur v2). **Rédigé le** 17 novembre 2026, **figé avant toute génération** : son empreinte est publiée sur le #171 avant le premier appel à un générateur.

---

## 1. Objet et décisions

* **Décision de Mahé du 17 novembre** : construire un jeu de test neuf par des sous-agents Claude indépendants, et étalonner le jugement mutualisé du #139 par des juges d'IA, faute de temps pour un jugement humain avant la V1 du rapport.
* **Autorisation** : l'enseignant a autorisé par écrit l'usage de Claude pour générer des questions synthétiques et pour évaluer. Le courriel est conservé par Mahé, hors du dépôt.
* **Écart déclaré à la règle de l'équipe** : le README de `evaluation/questions/` réservait la génération par IA aux paires d'entraînement. Le jeu v2 s'en écarte, sur décision de Mahé. Il ne remplace pas le jeu humain v1, qui reste la référence humaine et est mesuré à titre secondaire.
* **Pourquoi un jeu neuf** : le lot de test v1 (73 questions du corpus, 24 hors corpus) a été lu par plus de six mesures ; toute comparaison nouvelle y est descriptive. Le jeu v2 n'a été lu par aucun système au moment du gel.

---

## 2. Questions du corpus

* **Fiches** : les 61 fiches des questions du corpus du lot de test v1. Elles sont exclues de tous les entraînements du projet : encodeurs ajustés v1 et v2 (67 fiches exclues, qui les contiennent) et adaptation LoRA du volet B (61 fiches, `scripts/adaptation_qwen/separation.py`).
* **Passages éligibles** : ceux du découpage M2 qui comptent au moins 40 tokens, soit 1 339 passages, de 5 à 63 par fiche.
* **Tirage** (`scripts/evaluation/jeu_v2.py tirer`) : pour chaque fiche, dans l'ordre alphabétique des adresses, une permutation des passages éligibles par `numpy.random.default_rng([20261117, 171])` ; les trois premiers sont les candidats de rang 1, 2 et 3. Soit 183 candidats.
* **Lots** : le lot de rang k contient le candidat de rang k de chaque fiche (61 passages). Un générateur ne voit donc jamais deux passages d'une même fiche.
* **Générateur** : un sous-agent Claude Opus 5.5 par lot, dans un contexte neuf, avec la seule consigne G de l'annexe et le fichier de son lot. Il ne voit ni le dépôt, ni le jeu v1, ni ce protocole.
* **Contenu d'une question** : la question, et l'extrait du passage qui y répond, recopié mot pour mot. Le passage source est le passage pertinent annoté ; l'extrait permet d'appliquer la règle D4 exactement comme au jeu v1.

---

## 3. Contrôles et sélection

* **Contrôle mécanique de forme** (`jeu_v2.py controler`, éliminatoire) : question de 25 à 220 caractères, terminée par un unique point d'interrogation, sans renvoi au texte (« selon le texte », « dans cette fiche », etc., sauf « la fiche de paie » et formes voisines).
* **Contrôle mécanique de l'extrait** (éliminatoire) : présent mot pour mot dans le texte du passage, aux espaces près, et reconnu pertinent par la règle D4.
* **Contrôle mécanique de nouveauté** (éliminatoire) : indice de Jaccard avec chacune des 105 questions du jeu v1 au plus 0,40, comme pour la v2 de l'encodeur.
* **Juge de contrôle** : un sous-agent Claude Fable 5.2, contexte neuf, consigne J de l'annexe. Une question est acceptée s'il la juge compréhensible seule, si le passage y répond en tout ou en partie, et si l'extrait suffit à répondre.
* **Sélection** : pour chaque fiche, les deux premiers candidats acceptés, dans l'ordre des rangs. Une fiche qui n'en a qu'un garde celui-là ; aucune régénération. Cible : 122 questions.
* **Mesure du recouvrement lexical** : indice de Jaccard entre chaque question et son passage, comparé à celui des questions du jeu v1 et de leur passage pertinent. L'écart est publié ; une question générée à partir d'un passage risque d'en reprendre les mots, ce qui avantagerait BM25.

---

## 4. Questions hors corpus

* **Générateur** : un autre sous-agent Claude Opus 5.5, contexte neuf, consigne H de l'annexe, qui ne reçoit que les titres des 261 fiches. 60 candidates.
* **Vérification** : pour chaque candidate, les 10 passages classés en tête par la fusion RRF de l'E5 de base et de BM25 V3 (configuration de la #138, sans reclasseur) sont soumis à un juge Claude Fable 5.2, consigne V de l'annexe. La candidate est retenue si aucun passage n'y répond, même en partie, et si les contrôles mécaniques de forme passent.
* **Sélection** : les 40 premières retenues, dans l'ordre du générateur. S'il en reste moins de 30, un second lot de 30 est demandé avec la même consigne, et c'est déclaré.

---

## 5. Gel du jeu

* **Fichiers versionnés** dans `evaluation/questions_v2/` : `questions_v2.csv` (colonnes du jeu v1, plus `passage_id`), un README et un manifeste des empreintes des lots, des sorties des générateurs et des verdicts des juges.
* **Ordre** : le jeu est commité et étiqueté `jeu-questions-v2` avant qu'un système ne soit exécuté sur ses questions. Les sorties brutes des sous-agents restent dans `data/evaluation/jeu_v2/`, non versionné, avec leurs empreintes au manifeste.

---

## 6. Étalonnage du jugement mutualisé (amendement au protocole 09)

* **Écart** : le protocole 09 prévoyait deux membres de l'équipe. Sur décision de Mahé, les 100 paires de `feuille_etalonnage.csv` sont jugées par deux juges d'IA d'autres modèles que J1 (Opus 5.5) et J2 (Sonnet 5.5) : C1, Claude Fable 5.2, et C2, Claude Haiku 5.5.
* **Conditions** : consigne du protocole 09, section 4, mot pour mot ; contexte neuf ; aucun accès aux verdicts de J1 et J2, à la clé ou aux résultats.
* **Règle inchangée** : kappa entre C1 et C2, puis entre leur consensus (les deux jugent `repond`) et la règle principale de J1 et J2. Si ce second kappa est inférieur à 0,6, les majorants sont déclarés non étayés.
* **Libellé** : en cas de succès, les majorants sont « confirmés par deux juges d'IA indépendants », jamais « étalonnés par des humains ». L'accord entre modèles d'un même éditeur ne remplace pas un jugement humain.

---

## 7. Mesures et règles de décision

Toutes les mesures du corpus portent sur les questions du corpus du jeu v2 ; celles du jeu v1 et du CDTN sont faites aux mêmes conditions et publiées.

### Famille A, volet A : fusion dans le navigateur (#173)

* **Systèmes** : D, la recherche dense servie (encodeur ajusté v1, requête q8 encodée dans le navigateur, index fp32) ; F, la fusion RRF (k = 60, profondeur 100) de D et de BM25 V3 (mots vides Snowball sans les négations, racinisation française, entrée en-tête et texte).
* **Critère** : Recall@5 au passage, selon D4. Secondaire : présence d'une fiche pertinente parmi les fiches des 10 passages affichés.
* **Règle** : F est adoptée si son écart de Recall@5 avec D est positif ou nul sur le jeu v2 et sur le CDTN (population du protocole 05), et strictement positif sur au moins l'un des deux. F n'est dite meilleure que si la borne basse de l'intervalle de Tango dépasse 0.
* **Ce qui ne change pas** : le refus et la zone grise restent calculés sur le score dense ; le comportement hors corpus est donc inchangé par construction.

### Famille E, encodeurs (#167)

* **Candidats** : v2-T (questions de T, amendement A2) et v3-C (questions de Claude, amendement A3, figé avant sa génération), contre v1, servi. Recherche dense seule, aux conditions du site.
* **Règle** : celle de l'amendement A2, section 7, appliquée à chaque candidat sur le jeu v2 et le CDTN. Correction de Holm sur les deux candidats pour la conclusion statistique.
* **Calendrier** : un candidat retenu n'est servi avant J4 que si le recalcul des seuils, le redéploiement et la vérification du site sont faits avant le gel du 20 novembre ; sinon après J4.

### Famille B, volet B (#172)

* **Récupération** : R0, l'E5 de base, 5 passages (chaîne B2) ; R1, la fusion de l'E5 de base et de BM25 avec le reclasseur bge-reranker-v2-m3 sur 20 candidats, 10 passages (V1) ; R2, la même avec l'encodeur ajusté v1 (démonstration depuis le 16 novembre). Critère : part des questions dont le contexte contient un passage pertinent selon D4, sur le jeu v2, et rappel du contexte sur le CDTN, comme au protocole 07.
* **Règle de maintien** : R2 reste en production si son critère est au moins celui de R1 sur le jeu v2 et sur le CDTN ; sinon la démonstration revient à R1.
* **Bout en bout, sur le jeu v2** : le modèle adapté en B2 (R0, consigne v1, seuil S) contre le modèle adapté dans la chaîne de démonstration (R2, consigne v1, sans seuil), puis le témoin T dans la chaîne de démonstration. Critère principal : M4. M1 ne doit pas baisser de plus d'une question, comme au protocole 08. M2, M3 et M5 sont descriptifs.
* **Conditions** : Mac de Mahé, Ollama 0.40.13, modèles et digests du #52, température nulle, graine de `generation.py`, une exécution par état.

---

## 8. Statistiques

* **Questions du corpus** : intervalle du score de Tango à 95 % corrigé de l'effet de plan (regroupement par fiche, deux questions par fiche), McNemar exact. **Hors corpus** : sans regroupement.
* **Comparaisons multiples** : correction de Holm au sein de chaque famille.

---

## 9. Limites déclarées d'avance

* **Circularité** : Claude génère des questions de test et, pour la v3-C, des questions d'entraînement. Les fiches sont disjointes, les modèles et les consignes diffèrent, mais une proximité de style entre questions générées peut favoriser la v3-C. Le jeu humain v1 et le CDTN, écrits sans IA, servent de contrôle.
* **Un seul passage annoté par question** : le critère est un minorant, comme au jeu v1.
* **Questions générées depuis un passage** : elles peuvent en reprendre les mots ; l'écart de recouvrement lexical avec le jeu v1 est publié.
* **Juges d'IA** : leurs verdicts ne remplacent pas un jugement humain.

---

## 10. Exécution, sécurité et données personnelles

* Les sous-agents ne reçoivent que des passages de fiches publiques (Etalab 2.0) et des titres de fiches : aucune donnée personnelle ni secret. Ils n'ont pas accès au dépôt.
* Les modèles locaux tournent sur 127.0.0.1, hors ligne.

---

## 11. Valeurs inscrites au gel

* `data/evaluation/jeu_v2/candidats.json` : `9e323d18…` ; lots `rang_1.json` `75d99d1c…`, `rang_2.json` `99d04b90…`, `rang_3.json` `e23089bb…` ; `titres_fiches.json` `8afd2361…`.

---

## 12. Historique

* **17 novembre 2026** : rédaction et gel, avant toute génération.

---

## Annexe. Consignes, mot pour mot

**Consigne G, génération des questions du corpus.**

> Tu prépares des questions de test pour évaluer un moteur de recherche sur des fiches pratiques du droit du travail (site travail-emploi.gouv.fr). Lis uniquement le fichier indiqué, qui contient une liste de passages (passage_id, titre_fiche, entete, texte), et n'ouvre aucun autre fichier. Pour chaque passage, écris une question et un extrait. La question est celle d'un salarié ou d'un employeur qui n'a pas lu la fiche et qui décrit sa situation avec ses propres mots ; le passage doit y répondre, au moins en partie. Elle se comprend seule : pas de « selon le texte », « dans cette fiche », « ce document », ni de pronom ou de démonstratif sans antécédent. Reformule : n'emprunte pas les expressions techniques rares du passage quand un mot courant suffit, et ne recopie aucune phrase du passage. Une seule question, de 25 à 220 caractères, terminée par un unique point d'interrogation. L'extrait est une ou deux phrases du champ texte, recopiées exactement, caractère pour caractère, qui répondent à la question. Réponds uniquement par un tableau JSON, un objet par passage, dans l'ordre du fichier, de la forme {"passage_id": "...", "question": "...", "extrait": "..."}.

**Consigne J, contrôle des questions du corpus.**

> Tu contrôles des questions de test. Lis uniquement le fichier indiqué, et n'ouvre aucun autre fichier : chaque entrée donne un passage, une question et un extrait. Pour chaque entrée, indique : comprehensible_seule, « oui » si la question se comprend sans le passage, sinon « non » ; repond, « oui » si le passage répond à la question, « partiel » s'il y répond en partie, « non » sinon ; extrait_repond, « oui » si l'extrait suffit à répondre, sinon « non » ; motif, une phrase si une réponse est « non » ou « partiel ». Ne réécris pas les questions. Réponds uniquement par un tableau JSON, dans l'ordre du fichier, de la forme {"passage_id": "...", "comprehensible_seule": "...", "repond": "...", "extrait_repond": "...", "motif": "..."}.

**Consigne H, questions hors corpus.**

> Lis uniquement le fichier indiqué, et n'ouvre aucun autre fichier : il donne les titres des 261 fiches pratiques du droit du travail que couvre un assistant. Écris 60 questions réalistes, posées par des salariés ou des employeurs, sur des sujets voisins qu'aucune de ces fiches ne traite, par exemple la fonction publique, la retraite, la fiscalité, la protection sociale hors du travail, le droit de la famille, le logement, la consommation ou la création d'une entreprise individuelle. Elles sont variées et concrètes, sans piège ni question de culture générale ; chacune compte de 25 à 220 caractères et se termine par un unique point d'interrogation. Réponds uniquement par un tableau JSON de chaînes.

**Consigne V, vérification des questions hors corpus.**

> Lis uniquement le fichier indiqué, et n'ouvre aucun autre fichier : pour chaque question, il donne les 10 passages qu'un moteur de recherche a trouvés dans des fiches du droit du travail. Pour chaque question, indique un_passage_repond, « oui » si au moins un de ces passages répond à la question, même en partie, sinon « non », et passage_id, l'identifiant du passage qui répond, ou une chaîne vide. Réponds uniquement par un tableau JSON, dans l'ordre du fichier, de la forme {"question": "...", "un_passage_repond": "...", "passage_id": "..."}.
