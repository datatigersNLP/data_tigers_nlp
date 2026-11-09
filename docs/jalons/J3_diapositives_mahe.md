# Supports de J3 : diapositives 4, 7 et 8

**Équipe** Data Tigers  
**Ticket** #112, plan de Vaneck du 4 novembre (10 diapositives)  
**Établi le** 7 novembre 2026 par Mahé BEGNIS ; chiffres repris de `docs/jalons/J3_chiffres_verifies.md`  
**À mettre à jour le** 13 novembre : résultats de la mesure avant, issue de la relecture du lot v2b, état de l'entraînement

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

**Message.** La mesure est verrouillée avant d'être faite : aucun réglage ne peut être ajusté d'après ses résultats.

**Contenu.**
- Mêmes 97 questions que le volet A (73 du corpus, 24 hors corpus), avant et après adaptation.
- Cinq états : B0, le modèle nu, sans passage ; B1, la récupération de 5 passages sans consigne d'abstention ; B2, la chaîne complète, avec abstention sous le seuil S = 0,8565 ; R+ et R-, deux références dégénérées, l'une qui répond toujours et l'autre qui s'abstient toujours.
- Sur les 24 questions hors corpus : M1, abstention correcte, et M5, réponse affirmative.
- Sur les 73 questions du corpus : M2, abstention à tort, M3, citation valide, et M4, citation pertinente.
- Exactitude jugée à l'aveugle, à titre descriptif, par Maïmouna et Vaneck : 20 réponses citées de B2 tirées au hasard, avant puis après.
- Analyse principale, écrite d'avance : après contre avant, en B2, sur M1 et sur M4. L'intervalle est bilatéral à 97,5 % (correction de Bonferroni). Une amélioration n'est déclarée que si la borne basse dépasse 0.
- Gel : le protocole et le script ont été fusionnés le 4 novembre (#108, #119). Ollama 0.40.13 est épinglé, et B0 a été recalibré sans erreur technique sur 8 questions. Les empreintes du verrou sont approuvées le 7 novembre (#131).
- Mesure avant : à compléter le 13/11 avec M1 à M5 par état, leurs intervalles et la part d'erreurs techniques.

**Notes pour l'oral.** Le verrou consigne l'empreinte du protocole, des scripts, du jeu de questions, du seuil et de l'index. La mesure refuse de tourner si l'un d'eux a changé. Les 8 questions de calibration ont servi à mettre le script au point, et aucun taux n'en est tiré.

**À ne pas dire.** Un taux de qualité tiré de la calibration ; « Ollama 0.40.11 » ; des métriques sans rapport avec M1 à M5.

**Sources.** `docs/etudes/evaluation/06_protocole_volet_b.md` (sections 3, 5, 6 et 8) ; `scripts/rag/mesure.py` ; PR #119 et #131 ; #52.
