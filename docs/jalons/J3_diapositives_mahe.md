# Supports de J3 : diapositives 4, 7 et 8

**Équipe** Data Tigers  
**Ticket** #112, plan de Vaneck du 4 novembre (10 diapositives)  
**Établi le** 7 novembre 2026 par Mahé BEGNIS ; chiffres repris de `docs/jalons/J3_chiffres_verifies.md`  
**Complété le** 9 novembre par Jibril BENSALEM avec Codex : contenu de la diapositive 8 et résultats avant, d'après les sorties du Legion

**Actualisé le** 11 novembre : diapositive 8 complétée avec les résultats T et adapté publiés dans #52

**À finaliser le** 13 novembre : relecture humaine, répartition orale et assemblage

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

## Diapositive 8 : Volet B, résultats de l'adaptation (avec Jibril)

**Message.** L'adaptation augmente les réponses citant un passage pertinent. Le taux d'abstention hors corpus reste identique, avec une incertitude importante.

**Contenu à afficher.**

- 97 questions de test : 73 du corpus et 24 hors corpus.
- Comparaison principale en B2 : modèle adapté contre témoin T, tous deux mesurés le 11 novembre sur le Mac de Mahé, sous Ollama 0.40.13.
- Même récupération E5 fp32, cinq passages et seuil S = 0,8565. La récupération v2 n'intervient pas dans cette comparaison.

| Critère principal | Adapté | Témoin T | Écart en points | IC à 97,5 % |
|---|---:|---:|---:|---:|
| Réponse citant un passage pertinent (M4) | 18/72 (25,0 %) | 10/72 (13,9 %) | +11,1 | [+2,1 ; +23,8] |
| Abstention correcte hors corpus (M1) | 20/24 (83,3 %) | 20/24 (83,3 %) | 0,0 | [−20,5 ; +20,5] |

**Conclusion.** Amélioration démontrée sur M4 selon la règle prévue. Aucune amélioration démontrée sur M1. Une citation pertinente ne prouve pas l'exactitude de toute la réponse.

**Notes pour l'oral, protocole et limites.**

Le verrou consigne l'empreinte du protocole, des scripts, du jeu de questions, du seuil et de l'index. La mesure refuse de tourner si l'une des dix empreintes a changé. L'amendement M1 publié dans #52 complète le protocole sur le choix de machine sans modifier le fichier gelé ni le verrou.

Mahé rapporte une seule exécution par état et par phase, sans reprise. Les cinq états exécutés restent sous la limite de 5 % d'erreurs techniques : T B1, 2/97 ; T B2, 1/97 ; adapté B0, 0/97 ; adapté B1 et B2, 1/97 chacun. Q088 est en erreur de décompte des tokens dans les quatre états avec récupération. Q039 est aussi en erreur dans B1 de T, sa réponse étant coupée à 512 tokens. La comparaison principale B2 porte donc sur les mêmes 72 questions du corpus, Q088 exclue, et sur les 24 hors corpus.

Les deux critères principaux utilisent les intervalles bilatéraux à 97,5 % prévus en section 6, avec correction de Bonferroni. Pour M4, huit questions gagnent une citation pertinente et aucune n'en perd, avec McNemar exact p = 0,0078. Pour M1, une question change dans chaque sens, p = 1. L'intervalle de M1 ne permet pas d'exclure une perte ou un gain d'environ 20 points malgré les taux identiques. Mahé rapporte un recalcul indépendant des tables appariées et des valeurs p à partir des fichiers bruts. Ces calculs privés n'ont pas été réexécutés pour ce support.

**Résultats descriptifs, distincts de l'analyse principale.** En B2, M2 passe de 70,8 % pour T à 55,6 % pour le modèle adapté, soit −15,3 points avec IC 95 % [−26,3 ; −5,4]. Plus de la moitié des questions du corpus reçoivent donc encore une abstention. M2 rapporte l'abstention par rapport au corpus entier, sans condition sur la présence d'un passage pertinent dans le contexte. M3 passe de 25,0 % à 44,4 %, avec un écart de +19,4 points et IC 95 % [+9,8 ; +30,8]. Les sorties invalides de B2 passent de trois à zéro. M5 reste à 4/24 dans les deux phases. Ces indicateurs sont descriptifs, avec des intervalles à 95 %, sans conclusion d'amélioration selon la règle principale. En B1, M4 vaut 38,0 % pour l'adapté contre 43,7 % pour T : le résultat de B2 ne se généralise pas à B1.

**Exactitude des réponses.** M4 exige au moins une référence citée vers un passage pertinent selon D4. Il ne vérifie pas que toutes les affirmations, conditions et exceptions sont justes. Maïmouna et Vaneck doivent juger à l'aveugle 20 réponses citées de B2 tirées dans `temoin` et 20 dans `apres`, parmi respectivement 22 et 36 réponses citées. Mahé a publié ce choix avant le tirage, avec la graine 20261018, et conserve la clé. L'ajustement de l'échantillonnage remplace « avant/après » par « T/adapté » pour respecter M1 et la référence principale. Aucun verdict humain final n'est présenté ici.

**Machines et traçabilité.** La mesure avant du 9 novembre sur le Legion reste descriptive et archivée. Elle n'est pas comparée directement aux mesures du Mac. Mahé ne refait pas de phase avant sur le Mac, car le modèle de #31 n'y a pas été importé. T ne sera pas transféré et Jibril n'a plus aucune mesure à lancer. Les modèles du Mac ont les digests suivants :

- T : `8a077f3d3f56b636face1357eba557b21e2ba68bc72ee81e48b377272da72f27`.
- Adapté : `18cb25f099f2ba1b21a3bc945da6be7ce4d128cb4e579325fc0f70dfccb37174`.

### Repères historiques : mesure avant du Legion, 9 novembre

Ces chiffres décrivent uniquement le modèle de #31 sur le Legion. Ils ne forment pas la référence de l'écart adapté contre T du tableau principal.

| Indicateur | B1 | B2 |
|---|---:|---:|
| Abstention correcte hors corpus (M1) | 0/24 (0 %) | 20/24 (83,3 %) |
| Abstention à tort dans le corpus (M2) | 0/71 (0 %) | 45/72 (62,5 %) |
| Réponse citant un passage pertinent (M4) | 30/71 (42,3 %) | 12/72 (16,7 %) |

Le diagnostic complémentaire reste propre à cette mesure du Legion : sur les 45 abstentions M2, 28 surviennent sans passage pertinent fourni selon D4 (27 du modèle et une du seuil). Parmi les 33 questions avec passage pertinent fourni, 17 reçoivent une abstention (16 du modèle et une du seuil). D4 ne connaît qu'un extrait par question, donc un contexte classé sans passage pertinent peut contenir une autre réponse. Ce diagnostic ne remplace ni M2 ni la relecture humaine. Il n'est pas transposé aux phases T et adapté.

**Texte oral de Jibril.** Voir `docs/jalons/J3_diapositives_jibril.md`, partie « Diapositive 8 ». Cette section reste la source commune des chiffres pour l'assemblage.

**Sources.** Protocole 06, sections 3 à 8 ; #52, [résultats du 11 novembre et décision sur l'échantillon](https://github.com/datatigersNLP/data_tigers_nlp/issues/52#issuecomment-6797300311), [modèles et digests](https://github.com/datatigersNLP/data_tigers_nlp/issues/52#issuecomment-6795652708), [amendement M1](https://github.com/datatigersNLP/data_tigers_nlp/issues/52#issuecomment-6767903548), [réception et diagnostic du Legion](https://github.com/datatigersNLP/data_tigers_nlp/issues/52#issuecomment-6740066115) ; journal de mesure fusionné dans #142.
