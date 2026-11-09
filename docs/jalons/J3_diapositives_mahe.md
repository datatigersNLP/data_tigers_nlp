# Supports de J3 : diapositives 4, 7 et 8

**Équipe** Data Tigers  
**Ticket** #112, plan de Vaneck du 4 novembre (10 diapositives)  
**Établi le** 7 novembre 2026 par Mahé BEGNIS ; chiffres repris de `docs/jalons/J3_chiffres_verifies.md`  
**Complété le** 9 novembre par Jibril BENSALEM avec Codex : contenu de la diapositive 8 et résultats avant, d'après les sorties du Legion

**À mettre à jour le** 13 novembre : acceptation du lot v2b, état de l'entraînement et éventuels résultats après

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

**Notes pour l'oral.** La mesure répond à une question posée avant de la faire : le site est-il au moins aussi bon que BM25 ? Oui, à la marge fixée au J2. Dire « non démontré meilleur », c'est respecter ce que la mesure permet de conclure. La limite principale est l'abstention : 15 questions hors corpus sur 24 reçoivent encore des résultats.

**À ne pas dire.** « Supériorité prouvée » ; « +26,8 points » ; « abstention active validée » ; « seuil de 0,8165 fixé par courbe ROC ».

**Sources.** `docs/etudes/evaluation/03_evaluation.md` ; `front/src/recherche/moteur.js` ; `scripts/allegement/README.md`.

## Diapositive 7 : Volet B, l'adaptation (avec Remy)

**Message.** L'adaptation est engagée : la machine a été choisie par la mesure, et un lot de données refusé à la relecture a été corrigé avant tout entraînement.

**Contenu.**
- Machine : le Legion (RTX 5070 Laptop, 8 Gio) alloue 9,17 Gio pour 7,96 Gio et met 274 s par pas, ce qui est insuffisant. Le Mac (M4 Pro, 24 Gio) atteint un pic de 7,14 Gio sous un plafond Metal de 17,76 Gio, à 8,8 s par itération : il est retenu le 30 octobre.
- Méthode : LoRA de rang 8 sur les 16 dernières couches du modèle en 4 bits, perte calculée sur la seule réponse, deux époques (PR #125).
- Lot v1 : 298 exemples, refusé à la relecture humaine le 2 novembre, avec 8 exemples faux sur 30, au-delà de la règle de 10 % écrite d'avance. Sur les 15 exemples cités, 6 sont faux : la réponse prête au passage ce qu'il ne dit pas.
- Correctif, publié avant la génération (#107) : les réponses sont recopiées mot pour mot des passages, chaque phrase est contrôlée contre le passage qu'elle cite, et la variante « passage retiré » est abandonnée.
- Lot v2b : 218 exemples, dont 164 cités et 54 abstentions hors corpus, en relecture humaine indépendante par Maïmouna et Vaneck. À compléter le 13/11 : accepté ou refusé, entraînement fait ou non.
- Service : Ollama refuse les adaptateurs LoRA. L'adaptateur sera fusionné, converti en GGUF et quantifié en Q4_K_M ; le modèle de base suivra la même chaîne, pour servir de témoin T.

**Notes pour l'oral.** Le refus du lot v1 est un résultat, pas un échec : la règle d'acceptation était écrite avant la relecture, et elle a empêché d'entraîner le modèle sur des réponses infidèles. Le correctif a été choisi sans lire le nouveau lot.

**À ne pas dire.** « Volet B adapté », tant que l'adaptateur n'est pas entraîné et mesuré ; « 16,86 Gio de mémoire libre » ; « exécution intégrale en VRAM » : le Mac a une mémoire unifiée.

**Sources.** PR #109 et #118 ; `docs/etudes/faisabilite_legion_20261026.md` ; #107 (commentaires du 4 et du 7 novembre) ; PR #130.

## Diapositive 8 : Volet B, protocole 06 et mesure avant (avec Jibril)

**Message.** B2 s'abstient davantage hors corpus, mais refuse aussi beaucoup de questions auxquelles le corpus permet de répondre.

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

**Notes pour l'oral, protocole et limites.**

Les cinq états sont B0 (modèle nu), B1, B2, R+ (réponse fixe citant le premier passage) et R- (abstention systématique). B0, R+ et R- n'ont aucune erreur technique. R+ atteint par construction 100 % de citations valides, ce qui montre qu'une référence bien formée suffit peu à juger une réponse. M4 exige qu'au moins un passage cité soit pertinent selon la règle D4. Ce contrôle ne juge pas la justesse de chaque affirmation.

Les différences entre B1 et B2 restent descriptives. B2 change à la fois la consigne et le filtrage par seuil : on ne peut pas attribuer tout l'écart au seul seuil. Les erreurs techniques retirées ne sont pas des abstentions. M3 mesure les citations valides, M5 les réponses affirmatives hors corpus. Les résultats détaillés des cinq états restent dans `metriques.json`, transmis hors dépôt à Mahé.

| Indicateur | IC 95 % de B1 | IC 95 % de B2 |
|---|---:|---:|
| M1 | 0,0 à 13,8 % | 64,1 à 93,3 % |
| M2 | 0,0 à 5,1 % | 52,0 à 72,0 % |
| M4 | 30,5 à 55,0 % | 9,9 à 26,8 % |

Ces intervalles sont ceux de l'analyse avant transmise par Jibril, arrondis à un chiffre après la virgule. Le protocole emploie Wilson, avec correction de l'effet de plan des fiches pour les questions du corpus. Les effectifs sans erreur sont propres à chaque état. Une comparaison appariée utilise la population commune sans erreur dans les deux états.

L'analyse principale reste celle écrite avant la mesure : après contre la référence prévue, en B2, sur M1 et M4, avec intervalles bilatéraux à 97,5 % et correction de Bonferroni pour ces deux comparaisons. Le protocole conclut à une amélioration démontrée lorsque la borne basse de l'intervalle de l'écart dépasse zéro. Le témoin T devient la référence principale si sa chaîne diffère de celle du modèle de #31. Aucune amélioration de l'adaptation n'est encore mesurée.

Les huit questions de calibration ont servi à mettre le script au point. Les taux affichés ici viennent exclusivement des 97 questions du lot de test, dont les questions avec erreur technique sont exclues des dénominateurs.

Maïmouna et Vaneck jugeront à l'aveugle, à titre descriptif, 20 réponses citées de B2 de chaque phase. Cette relecture porte sur l'exactitude, les conditions et exceptions, et la justification par les passages. Le jeu, le seuil et le protocole restent figés après cette mesure avant.

**Texte oral de Jibril.** Voir `docs/jalons/J3_diapositives_jibril.md`, partie « Diapositive 8 ». Cette section reste la source commune du contenu de la diapositive 8, pour éviter une seconde copie des chiffres dans le support assemblé.

**Sources.** `docs/etudes/evaluation/06_protocole_volet_b.md` (sections 3 à 8) ; `scripts/rag/mesure.py` ; mesure avant du 9 novembre rapportée par Jibril, `metriques.json` SHA-256 `f28682a1418c6a97bad4c26ceb120c5149ccfb66962525e658d63540651b8c2b` ; journal de séance `docs/journal/2026-11-09_fusion_131_relectures_130_128.md` (PR #142, contenant les empreintes). La réception et l'analyse finale par Mahé restent à confirmer.
