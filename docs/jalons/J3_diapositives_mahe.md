# Supports de J3 : diapositives 4, 7 et 8

**Équipe** Data Tigers  
**Ticket** #112, plan de Vaneck du 4 novembre (10 diapositives)  
**Établi le** 7 novembre 2026 par Mahé BEGNIS ; chiffres repris de `docs/jalons/J3_chiffres_verifies.md`  
**Complété le** 9 novembre par Jibril BENSALEM avec Codex : contenu de la diapositive 8 et résultats avant, d'après les sorties du Legion

**Actualisé le** 10 novembre avec les confirmations de #52 et l'amendement M1 sur la machine de mesure

**À mettre à jour le** 13 novembre : état de l'entraînement et éventuels résultats après

---

## Diapositive 4 : Volet A, mesures et limites

**Message.** Le site trouve aussi bien que la référence lexicale, sans faire mieux ; son abstention reste à régler.

**Contenu.**
- Jeu de test : 73 questions du corpus, issues de 61 fiches, et 24 questions hors corpus (`jeu-questions-v1`).
- Recall@5 au niveau du passage : 43,8 % pour l'encodeur servi, contre 42,5 % pour la référence BM25. L'écart vaut +1,4 point, avec un IC 95 % de -11,5 à +14,3.
- Critère du J2 satisfait : non-infériorité à la marge de 15 points (score de Tango : z = 2,45, p unilatéral 0,007). Aucun des deux systèmes n'est démontré meilleur (McNemar, p = 1,000).
- Au niveau de la fiche : 83,6 % contre 79,5 %.
- Quantification q8 : elle coûte une question sur 73, sans écart significatif.
- Abstention : le seuil de 0,8560 a été fixé le 10 octobre, avant la mesure, au 5e centile des scores de 479 variantes du CDTN. Il rejette 9 questions hors corpus sur 24 et garde 72 questions du corpus sur 73. L'AUC du score maximal vaut 0,841 (IC 95 % de 0,747 à 0,921).
- Coût côté utilisateur : 18,3 ms par requête dans le navigateur, avec le modèle élagué de 65,7 Mio que sert le site.
- Pourquoi pas de précision@k : chaque question n'a qu'un extrait de référence, et les autres passages pertinents ne sont pas connus. La précision serait sous-estimée de façon arbitraire ; pour la même raison, le Recall au niveau du passage sous-estime les deux systèmes, d'où le Recall au niveau de la fiche, qui le complète.
- Suite pour le volet B : la même récupération, enrichie d'une fusion avec BM25 et d'un reclasseur, fait passer de 45,2 % à 72,6 % les questions dont les passages fournis au modèle contiennent un passage pertinent (#138, confirmé une fois sur le lot de test le 9 novembre).

**Notes pour l'oral.** La mesure répond à une question posée avant de la faire : le site est-il au moins aussi bon que BM25 ? Oui, à la marge fixée au J2. Dire « non démontré meilleur », c'est respecter ce que la mesure permet de conclure. La limite principale est l'abstention : 15 questions hors corpus sur 24 reçoivent encore des résultats. Sur la précision, montrer que nous connaissons les limites de notre jeu : un seul extrait par question rend la précision@k non interprétable, et c'est pourquoi le Recall est donné à deux niveaux. Les 45,2 % de la suite concernent la chaîne Python du volet B (E5 en fp32), et non le site (43,8 %, encodeur q8).

**À ne pas dire.** « Supériorité prouvée » ; « +26,8 points » ; « abstention active validée » ; « seuil de 0,8165 fixé par courbe ROC » ; « le site trouve 72,6 % » : la récupération v2 n'est pas servie par le site.

**Sources.** `docs/etudes/evaluation/03_evaluation.md` ; `front/src/recherche/moteur.js` ; `scripts/allegement/README.md` ; `docs/etudes/recuperation/02_confirmation_test.md` (PR #141).

## Diapositive 7 : Volet B, l'adaptation (avec Remy)

**Message.** L'adaptation est engagée : la machine a été choisie par la mesure, et un lot de données refusé à la relecture a été corrigé avant tout entraînement.

**Contenu.**
- Machine : le Legion (RTX 5070 Laptop, 8 Gio) alloue 9,17 Gio pour 7,96 Gio et met 274 s par pas, ce qui est insuffisant. Le Mac (M4 Pro, 24 Gio) atteint un pic de 7,14 Gio sous un plafond Metal de 17,76 Gio, à 8,8 s par itération : il est retenu le 30 octobre.
- Méthode : LoRA de rang 8 sur les 16 dernières couches du modèle en 4 bits, perte calculée sur la seule réponse, deux époques (PR #125).
- Lot v1 : 298 exemples, refusé à la relecture humaine le 2 novembre, avec 8 exemples faux sur 30, au-delà de la règle de 10 % écrite d'avance. Sur les 15 exemples cités, 6 sont faux : la réponse prête au passage ce qu'il ne dit pas.
- Correctif, publié avant la génération (#107) : les réponses sont recopiées mot pour mot des passages, chaque phrase est contrôlée contre le passage qu'elle cite, et la variante « passage retiré » est abandonnée.
- Ce que l'adaptation apprend : un comportement, pas des connaissances. Le modèle apprend à recopier les passages fournis, à les citer et à s'abstenir hors corpus ; les faits restent dans les passages, et la récupération reste indispensable. Les 61 fiches du lot de test sont exclues des données d'entraînement.
- Lot v2b : 218 exemples, dont 164 cités et 54 abstentions hors corpus, relus séparément par Maïmouna et Vaneck. Accepté le 10 novembre avec la grille la plus sévère des deux : 3 exemples faux sur 30, soit 10,0 %, à la limite de la règle. Risque déclaré : environ 11 des 54 abstentions pourraient être injustifiées (#107). À compléter le 13/11 : entraînement et mesure après.
- Service : Ollama refuse les adaptateurs LoRA. L'adaptateur est fusionné dans les poids bf16 officiels, converti en GGUF et quantifié en Q4_K_M ; le modèle de base suit la même chaîne, pour servir de témoin T (produit et vérifié le 9 novembre, #140). Depuis le 10 novembre, entraînement, export et mesures se font sur le seul Mac (amendement M1, #52).

**Notes pour l'oral.** Le refus du lot v1 est un résultat, pas un échec : la règle d'acceptation était écrite avant la relecture, et elle a empêché d'entraîner le modèle sur des réponses infidèles. Le correctif a été choisi sans lire le nouveau lot. Si l'on demande pourquoi adapter un modèle qui a déjà un RAG : injecter le corpus dans les poids remplacerait la récupération, et la littérature la juge moins fiable que le RAG pour apporter des connaissances (Ovadia et al., 2023). Nous adaptons au contraire la manière d'utiliser les passages, dans l'esprit de RAFT (Zhang et al., 2024) : c'est la récupération qui apporte les faits, et l'adaptation qui apprend à les citer fidèlement ou à s'abstenir.

**À ne pas dire.** « Volet B adapté », tant que l'adaptateur n'est pas entraîné et mesuré ; « 16,86 Gio de mémoire libre » ; « exécution intégrale en VRAM » : le Mac a une mémoire unifiée ; « le modèle connaît le droit du travail » : il apprend un comportement, pas le contenu des fiches.

**Sources.** PR #109 et #118 ; `docs/etudes/faisabilite_legion_20261026.md` ; #107 (commentaires du 4, du 7 et du 10 novembre) ; PR #130 ; #52 (amendement M1) ; #140 et PR #147.

## Diapositive 8 : Volet B, protocole 06 et mesure avant (avec Jibril)

**Message.** B2 s'abstient sur 20 des 24 questions hors corpus. Sur les 33 questions dont le contexte contient un passage pertinent selon D4, 17 reçoivent aussi une abstention.

**Contenu à afficher.**

- Mesure avant du 9 novembre sur le Legion, sous Ollama 0.40.13. Protocole, scripts et données verrouillés avant l'exécution.
- 97 questions de test : 73 du corpus et 24 hors corpus.
- B1 : cinq passages, sans consigne d'abstention. B2 : consigne d'abstention et seuil de similarité S = 0,8565.

| Indicateur | B1 | B2 |
|---|---:|---:|
| Abstention correcte hors corpus (M1) | 0/24 (0 %) | 20/24 (83,3 %) |
| Abstention à tort dans le corpus (M2) | 0/71 (0 %) | 45/72 (62,5 %) |
| Réponse citant un passage pertinent (M4) | 30/71 (42,3 %) | 12/72 (16,7 %) |

Les dénominateurs excluent les erreurs techniques : deux en B1, une en B2. Les cinq états restent valides selon le seuil de 5 %.

M2 classe l'abstention par rapport au corpus entier. L'analyse complémentaire du contexte distingue 28 des 45 abstentions sans passage pertinent fourni selon D4, et 17 abstentions sur 33 questions avec passage pertinent fourni. Ce diagnostic reste distinct de M2.

**Notes pour l'oral, protocole et limites.**

Le verrou consigne l'empreinte du protocole, des scripts, du jeu de questions, du seuil et de l'index. La mesure refuse de tourner si l'une des dix empreintes a changé. L'amendement M1 publié dans #52 complète le protocole sur le choix de machine sans modifier le fichier gelé ni le verrou.

La décomposition publiée par Mahé le 9 novembre est descriptive, hors protocole 06. Sur les 45 abstentions de M2, 28 surviennent sans passage pertinent fourni selon D4 (27 du modèle, une du seuil). Parmi les 33 questions avec passage pertinent fourni, 17 conduisent à une abstention (16 du modèle, une du seuil), soit 51,5 %. On distingue donc un défaut de récupération et des abstentions malgré un contexte pertinent selon cette règle. D4 ne connaît qu'un extrait par question : un contexte classé sans passage pertinent peut contenir une autre réponse. Ce croisement ne remplace pas une vérification humaine du sens.

Sur les 65 abstentions de B2, le seuil en déclenche 11 (deux dans le corpus, neuf hors corpus). Les 54 autres viennent du modèle. Le constat ne permet pas d'attribuer les abstentions au seul seuil.

Les cinq états sont B0 (modèle nu), B1, B2, R+ (réponse fixe citant le premier passage) et R- (abstention systématique). B0, R+ et R- n'ont aucune erreur technique. R+ atteint par construction 100 % de citations valides, ce qui montre qu'une référence bien formée suffit peu à juger une réponse. M4 exige qu'au moins un passage cité soit pertinent selon la règle D4. Ce contrôle ne juge pas la justesse de chaque affirmation.

Les différences entre B1 et B2 restent descriptives. B2 change à la fois la consigne et le filtrage par seuil : on ne peut pas attribuer tout l'écart au seul seuil. Les erreurs techniques retirées ne sont pas des abstentions. M3 mesure les citations valides, M5 les réponses affirmatives hors corpus. Les résultats détaillés des cinq états restent dans `metriques.json`, transmis hors dépôt à Mahé.

| Indicateur | IC 95 % de B1 | IC 95 % de B2 |
|---|---:|---:|
| M1 | 0,0 à 13,8 % | 64,1 à 93,3 % |
| M2 | 0,0 à 5,1 % | 52,0 à 72,0 % |
| M4 | 30,5 à 55,0 % | 9,9 à 26,8 % |

Ces intervalles sont ceux de l'analyse avant transmise par Jibril, arrondis à un chiffre après la virgule. Le protocole emploie Wilson, avec correction de l'effet de plan des fiches pour les questions du corpus. Les effectifs sans erreur sont propres à chaque état. Une comparaison appariée utilise la population commune sans erreur dans les deux états.

L'analyse principale compare B2 du modèle adapté à B2 du témoin T, tous deux mesurés sur le Mac de Mahé, sur M1 et M4, avec intervalles bilatéraux à 97,5 % et correction de Bonferroni. Le protocole conclut à une amélioration démontrée lorsque la borne basse de l'intervalle de l'écart dépasse zéro. Le témoin T diffère structurellement du modèle de #31 (#140), ce qui en fait la référence principale prévue par la section 3. Aucune amélioration de l'adaptation n'est encore mesurée.

L'amendement M1 du 10 novembre confie toutes les mesures restantes à Mahé sur son Mac, sous Ollama 0.40.13. La mesure avant du Legion reste une référence descriptive archivée, sans comparaison directe avec une phase sur le Mac. Jibril n'a plus de mesure à lancer et T ne sera pas transféré sur le Legion. Une phase avant sur le Mac n'est envisagée que si l'import du modèle de #31 y donne le digest exigé par le script.

Les huit questions de calibration ont servi à mettre le script au point. Les taux affichés ici viennent exclusivement des 97 questions du lot de test, dont les questions avec erreur technique sont exclues des dénominateurs.

Maïmouna et Vaneck jugeront à l'aveugle l'exactitude, les conditions et exceptions, et la justification par les passages, selon l'échantillonnage de 20 réponses citées de B2 par phase prévu au protocole. L'organisation de cet échantillon doit être alignée avec Mahé sur la référence T du Mac. Le jeu et le seuil restent figés.

**Texte oral de Jibril.** Voir `docs/jalons/J3_diapositives_jibril.md`, partie « Diapositive 8 ». Cette section reste la source commune du contenu de la diapositive 8, pour éviter une seconde copie des chiffres dans le support assemblé.

**Sources.** `docs/etudes/evaluation/06_protocole_volet_b.md` (sections 3 à 8) ; `scripts/rag/mesure.py` ; mesure avant du 9 novembre rapportée par Jibril, `metriques.json` SHA-256 `f28682a1418c6a97bad4c26ceb120c5149ccfb66962525e658d63540651b8c2b` ; journal de séance `docs/journal/2026-11-09_fusion_131_relectures_130_128.md` (PR #142, contenant les empreintes). Mahé a confirmé la réception des sept fichiers et un recalcul indépendant identique de l'analyse. Sources complémentaires : #52, commentaires https://github.com/datatigersNLP/data_tigers_nlp/issues/52#issuecomment-6740066115 (réception et diagnostic) et https://github.com/datatigersNLP/data_tigers_nlp/issues/52#issuecomment-6767903548 (amendement M1).
