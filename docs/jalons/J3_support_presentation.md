# Support de presentation - Jalon J3 (15 points)
**Module** NLP 2 . Master 2 Data & IA . FGES - Universite Catholique de Lille  
**Equipe** Data Tigers : Mahe BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maimouna SIGNATE  
**Statut** Version consolidee selon le plan de Vaneck du 4 novembre (Ticket #112, 10 diapositives)  
**Chiffres de reference** `docs/jalons/J3_chiffres_verifies.md` (PR #124) et Protocole 06 gele (PR #108, #131)  
**Responsables des supports** : Vaneck DAGAR (plan et contenu) & Remy RAYANE (assemblage et coordination)

---

## Diapositive 1 : Ou en est-on face aux trois exigences de J3

**Message.** Le volet A est finalise et deploye sans serveur, le volet B est engage avec son socle RAG et ses protocoles geles, et la demarche est integralement documentee.

**Contenu.**
- Cadrage general : deux applications complementaires sur le corpus du droit du travail (261 fiches, 4 240 passages, instantane SocialGouv du 11 septembre 2026).
- Exigence 1 (Volet A finalise et deploye) : recherche semantique dense client-side (Transformers.js), modele elague sous les 100 Mio de quota GitHub Pages (65,7 Mio), latence d'encodage de 18,3 ms, seuil d'abstention a 0,8560 et contrastes verifies au niveau AA des WCAG 2.1.
- Exigence 2 (Volet B engage) : assistant local sur Qwen2.5-7B sous Ollama 0.40.13, socle RAG fonctionnel avec sourcage formel des passages ([P1] a [P5]), protocoles de mesure et de separation geles, faisabilite materielle LoRA demontree sur Mac M4 Pro.
- Exigence 3 (Rigueur methodologique & Tracabilite) : demonstration reproductible, board tenu a jour avec suivi des charges, journal d'usage IA auditable (45 sessions, 87 erreurs documentees et corrigees) et 5 fiches d'outils novateurs pour le bonus.

**Notes pour l'oral.** J3 valide la livraison operationnelle du premier volet et l'engagement methodologique du second. Rien n'a ete improvise : chaque jalon s'appuie sur des criteres ecrits d'avance et des mesures verifiees.

**A ne pas dire.** « Volet B termine » ; « Volet B adapte » (l'adaptation est engagee, la mesure apres est attendue).

**Sources.** `README.md` ; `docs/jalons/J3_chiffres_verifies.md` ; tickets #8, #52, #107, #112.

---

## Diapositive 2 : Volet A, le site en ligne et son architecture

**Message.** Une recherche dense calculee a 100 % dans le navigateur du visiteur, sans aucun serveur applicatif ni cout d'infrastructure.

**Contenu.**
- Architecture statique : application web servie par GitHub Pages (Vite, React, Tailwind CSS), aucun backend Python en production.
- Moteur d'execution : Transformers.js adosse a ONNX Runtime Web (WebAssembly / SIMD).
- Encodeur dense : multilingual-e5-small quantifie en 8 bits (q8) pour concilier fidelite de representation et compacite.
- Asymetrie E5 preservee : prefixes obligatoires « query: » pour la requete et « passage: » pour les documents indexes, garantissant le respect de la geometrie latente.
- Optimisation matricielle : vecteurs normalises L2 permettant de reduire la similarite cosinus a un produit scalaire en O(d). Matrice d'embeddings chargee en memoire typee (Float32Array) depuis index_m2.f32 et metadonnees documentaires lues via JSON.parse.
- Reactivite utilisateur : 18,3 ms pour encoder une requete dans le navigateur (Chromium WASM) avec le modele elague de 65,7 Mio.

**Notes pour l'oral.** L'autonomie totale du site etait une contrainte majeure. Le calcul local garantit la confidentialite des requetes : aucun texte n'est transmis a un serveur externe.

**A ne pas dire.** « 18,6 ms sur le site » (18,6 ms mesurait le q8 d'origine non elague dans le notebook 02) ; « index.bin » (le fichier servi est index_m2.f32).

**Sources.** `README.md` ; `front/src/recherche/moteur.js` ; `scripts/allegement/README.md`.

---

## Diapositive 3 : Volet A, l'allegement sans perte du modele

**Message.** L'analyse des tenseurs a permis de lever le verrou technique des 100 Mio de GitHub sans aucune perte vectorielle sur les alphabets du corpus.

**Contenu.**
- Le verrou bloquant : GitHub interdit tout fichier superieur a 100 Mio. Le modele quantifie q8 d'origine pesait 112,8 Mio, imposant un CDN externe tiers contraire a l'audit d'autonomie.
- Diagnostic structurel : 81,6 % des parametres du modele resident dans la table de vocabulaire (250 037 entrees de dimension 384), dimensionnee pour couvrir plus de 100 langues.
- Recette d'elagage sans perte : suppression des sous-mots appartenant aux alphabets non utilises par le domaine (conservant l'alphabet latin et l'alphabet grec). Les couches d'attention et de feed-forward du Transformer restent strictement intactes.
- Resultats metrologiques : poids abaisse de 112,8 Mio a 65,7 Mio (-41,8 %), permettant l'hebergement direct dans le depot (front/public/modele/).
- Garantie de parite : identite vectorielle bit a bit verifiee sur 822 requetes de controle par rapport au q8 de reference dans le navigateur.

**Notes pour l'oral.** L'elagage ne retire pas de vocabulaire metier : il elague les alphabets inutiles. La reduction de 41,8 % leve le verrou de deploiement avec une fidelite mathematique parfaite.

**A ne pas dire.** « Elagage base sur les mots du corpus » (la recette retire les alphabets non latins/grecs) ; « reduction avec perte ».

**Sources.** `scripts/allegement/README.md` ; `README.md` ; ticket #50.

---

## Diapositive 4 : Volet A, mesures et limites

**Message.** Le site trouve aussi bien que la reference lexicale, sans faire mieux ; son abstention reste a regler.

**Contenu.**
- Jeu de test : 73 questions du corpus, issues de 61 fiches, et 24 questions hors corpus (jeu-questions-v1).
- Recall@5 au niveau du passage : 43,8 % pour l'encodeur servi, contre 42,5 % pour la reference BM25. L'ecart vaut +1,4 point, avec un IC 95 % de -11,5 a +14,3.
- Critere du J2 satisfait : non-inferiorite a la marge de 15 points (score de Tango : z = 2,45, p unilateral 0,007). Aucun des deux systemes n'est demontre meilleur (McNemar, p = 1,000).
- Au niveau de la fiche : 83,6 % contre 79,5 %.
- Quantification q8 : elle coute une question sur 73, sans ecart significatif.
- Abstention : le seuil de 0,8560 a ete fixe le 10 octobre, avant la mesure, au 5e centile des scores de 479 variantes du CDTN. Il rejette 9 questions hors corpus sur 24 et garde 72 questions du corpus sur 73. L'AUC du score maximal vaut 0,841 (IC 95 % de 0,747 a 0,921).
- Cout cote utilisateur : 18,3 ms par requete dans le navigateur, avec le modele elague de 65,7 Mio que sert le site.

**Notes pour l'oral.** La mesure repond a une question posee avant de la faire : le site est-il au moins aussi bon que BM25 ? Oui, a la marge fixee au J2. Dire « non demontre meilleur », c'est respecter ce que la mesure permet de conclure. La limite principale est l'abstention : 15 questions hors corpus sur 24 recoivent encore des resultats.

**A ne pas dire.** « Superiorite prouvee » ; « +26,8 points » ; « abstention active validee » ; « seuil de 0,8165 fixe par courbe ROC ».

**Sources.** `docs/etudes/evaluation/03_evaluation.md` ; `front/src/recherche/moteur.js` ; `scripts/allegement/README.md`.

---

## Diapositive 5 : Volet B, la chaine RAG locale

**Message.** Une generation locale open-weights sobre et tracee, contrainte par une injection contextuelle stricte et un sourcage formel.

**Contenu.**
- Modele generatif local : Qwen2.5-7B-Instruct quantifie en 4 bits (GGUF Q4_K_M, 4,36 Gio sur disque) servi localement sous Ollama 0.40.13.
- Index documentaire commun : reutilisation directe des 4 240 passages du corpus M2 (passages_m2.json), assurant l'alignement strict entre volet A et volet B.
- Contexte certifie (rag-b1-v1) : recuperation des 5 passages les plus proches par E5 en fp32, fenetre de contexte de 8 192 tokens et reponse bornee a 512 tokens.
- Contrat de generation : consigne systeme interdisant d'extrapoler et imposant le sourcage explicite de chaque affirmation par des reperes de citation [P1] a [P5].
- Controle de conformite : validation outillee des citations via la fonction valider_citations (PR #85).
- Debit interactif : 47 a 67 tokens/s observes lors d'essais sur prompt court sous Ollama 0.34.4 (ordre de grandeur indicatif, non benchmarke).

**Notes pour l'oral.** Le RAG s'appuie sur le meme index que le volet A. Le sourcage [Pn] permet de controler algorithmiquement l'absence d'hallucination dans les reponses du modele.

**A ne pas dire.** « 4,36 Gio en VRAM » (taille du fichier GGUF, pas occupation memoire) ; « latence premier token < 2 s » (non mesuree).

**Sources.** `docs/etudes/inference_locale_qwen.md` ; `scripts/rag/rag.py` ; PR #85.

---

## Diapositive 6 : Volet B, la demonstration en preparation

**Message.** Un contrat d'interface formalise et une maquette validee pour illustrer l'assistant local et sa politique d'abstention.

**Contenu.**
- Cadrage fonctionnel : demonstration interactive de l'assistant reglementaire local du cas B1 avec affichage des passages sources et du niveau de confiance.
- Contrat d'interface verrouille (PR #121, Ticket #111) : specification formalisee des echanges entre l'interface utilisateur et le backend RAG local (requetes, contextes, citations, reponses).
- Maquette validee (PR #128) : ecran d'accueil, fil de discussion avec rendu des sources [P1]-[P5] et mise en evidence pedagogique du refus de repondre hors perimetre.
- Integration technique : raccordement direct a l'instance locale d'Ollama 0.40.13 sur la machine de demonstration (Legion).
- Scenario de test de la soutenance : jeu d'exemples balisant questions directes, cas multi-sources et declenchement de l'abstention.

**Notes pour l'oral.** L'interface du volet B rend visible la politique d'abstention. En cas de doute ou de question hors perimetre, l'utilisateur voit explicitement pourquoi le systeme refuse d'inventer.

**A ne pas dire.** « Interface de production web » (il s'agit d'une demonstration locale pour la soutenance).

**Sources.** PR #121 ; PR #128 ; Tickets #111 et #114.

---

## Diapositive 7 : Volet B, l'adaptation LoRA

**Message.** L'adaptation est engagee : la machine a ete choisie par la mesure, et un lot de donnees refuse a la relecture a ete corrige avant tout entrainement.

**Contenu.**
- Machine : le Legion (RTX 5070 Laptop, 8 Gio) alloue 9,17 Gio pour 7,96 Gio et met 274 s par pas, ce qui est insuffisant. Le Mac (M4 Pro, 24 Gio) atteint un pic de 7,14 Gio sous un plafond Metal de 17,76 Gio, a 8,8 s par iteration : il est retenu le 30 octobre.
- Methode : LoRA de rang 8 sur les 16 dernieres couches du modele en 4 bits, perte calculee sur la seule reponse, deux epoques (PR #125).
- Lot v1 : 298 exemples, refuse a la relecture humaine le 2 novembre, avec 8 exemples faux sur 30, au-dela de la regle de 10 % ecrite d'avance. Sur les 15 exemples cites, 6 sont faux : la reponse prete au passage ce qu'il ne dit pas.
- Correctif, publie avant la generation (#107) : les reponses sont recopiees mot pour mot des passages, chaque phrase est controlee contre le passage qu'elle cite, et la variante « passage retire » est abandonnee.
- Lot v2b : 218 exemples, dont 164 cites et 54 abstentions hors corpus, en relecture humaine independante par Maimouna et Vaneck. A completer le 13/11 : accepte ou refuse, entrainement fait ou non.
- Service : Ollama refuse les adaptateurs LoRA. L'adaptateur sera fusionne, converti en GGUF et quantifie en Q4_K_M ; le modele de base suivra la meme chaine, pour servir de temoin T.

**Notes pour l'oral.** Le refus du lot v1 est un resultat, pas un echec : la regle d'acceptation etait ecrite avant la relecture, et elle a empeche d'entrainer le modele sur des reponses infideles. Le correctif a ete choisi sans lire le nouveau lot.

**A ne pas dire.** « Volet B adapte », tant que l'adaptateur n'est pas entraine et mesure ; « 16,86 Gio de memoire libre » ; « execution integrale en VRAM » : le Mac a une memoire unifiee.

**Sources.** PR #109 et #118 ; `docs/etudes/faisabilite_legion_20261026.md` ; #107 (commentaires du 4 et du 7 novembre) ; PR #130.

---

## Diapositive 8 : Volet B, protocole 06 et mesure avant

**Message.** La mesure est verrouillee avant d'etre faite : aucun reglage ne peut etre ajuste d'apres ses resultats.

**Contenu.**
- Memes 97 questions que le volet A (73 du corpus, 24 hors corpus), avant et apres adaptation.
- Cinq etats : B0, le modele nu, sans passage ; B1, la recuperation de 5 passages sans consigne d'abstention ; B2, la chaine complete, avec abstention sous le seuil S = 0,8565 ; R+ et R-, deux references degenerees, l'une qui repond toujours et l'autre qui s'abstient toujours.
- Sur les 24 questions hors corpus : M1, abstention correcte, et M5, reponse affirmative.
- Sur les 73 questions du corpus : M2, abstention a tort, M3, citation valide, et M4, citation pertinente.
- Exactitude jugee a l'aveugle, a titre descriptif, par Maimouna et Vaneck : 20 reponses citees de B2 tirees au hasard, avant puis apres.
- Analyse principale, ecrite d'avance : apres contre avant, en B2, sur M1 et sur M4. L'intervalle est bilateral a 97,5 % (correction de Bonferroni). Une amelioration n'est declaree que si la borne basse depasse 0.
- Gel : le protocole et le script ont ete fusionnes le 4 novembre (#108, #119). Ollama 0.40.13 est epingle, et B0 a ete recalibre sans erreur technique sur 8 questions. Les empreintes du verrou sont approuvees le 7 novembre (#131).
- Mesure avant : a completer le 13/11 avec M1 a M5 par etat, leurs intervalles et la part d'erreurs techniques.

**Notes pour l'oral.** Le verrou consigne l'empreinte du protocole, des scripts, du jeu de questions, du seuil et de l'index. La mesure refuse de tourner si l'un d'eux a change. Les 8 questions de calibration ont servi a mettre le script au point, et aucun taux n'en est tire.

**A ne pas dire.** Un taux de qualite tire de la calibration ; « Ollama 0.40.11 » ; des metriques sans rapport avec M1 a M5.

**Sources.** `docs/etudes/evaluation/06_protocole_volet_b.md` ; `scripts/rag/mesure.py` ; PR #119 et #131 ; #52.

---

## Diapositive 9 : Blocages et corrections a engager avant J4

**Message.** Quatre points de vigilance clairs, suivis au classeur de bord, balisent la trajectoire jusqu'a la soutenance finale.

**Contenu.**
- Calendrier officiel : confirmation ecrite formelle des jalons attendue de l'enseignant (#8). Date de soutenance avancee au 30/11 actee par l'equipe, fin des livrables fixee au 20/11.
- Point d'arret operationnel de l'adaptation : date limite fixee au 12/11. Si la mesure apres n'est pas finalisee a cette date, la soutenance presentera la mesure avant, la chaine de fabrication du lot v2b et la feuille de route.
- Chaine de deploiement Ollama : contournement de l'incompatibilite LoRA par export FP16, conversion GGUF et requantification Q4_K_M avec modele temoin T pour isoler les artefacts de quantification.
- Cloture des etudes explorees : cloture actee de l'ajustement contrastif de l'encodeur (#49), dont les enseignements et limites sont reverses au rapport final.

**Notes pour l'oral.** Nous ne cachons aucune difficulte technique : le jury apprecie la lucidite des arbitrages, la mise en place de regles de repli objectives et la tracabilite des ecarts de planning.

**A ne pas dire.** Pretendre que LoRA fonctionne nativement sous Ollama sans etape de fusion/quantification.

**Sources.** `docs/suivi/SUIVI.md` ; Tickets #8, #49, #107, #114.

---

## Diapositive 10 : Calendrier jusqu'a J4 et cinq outils novateurs

**Message.** Un calendrier de fin de projet resserre et cinq retours d'experience outilles pour valoriser la pratique de l'IA et des standards NLP.

**Contenu.**
- 10 novembre : construction du modele temoin T et deploiement du modele adapte sous Ollama.
- 12 novembre : mesure comparative apres adaptation (point d'arret operationnel strict).
- 13 novembre : jugement aveugle qualitatif, fiches des 5 outils novateurs et assemblage final des supports de J3.
- 16 novembre : Jalon officiel J3 (revue de 20 a 30 minutes, volet A fonctionnel et volet B engage).
- 19 novembre : livraison de la V1 du rapport final (#113).
- 20 novembre : fin officielle du projet, gel definitif des supports et du site web.
- 30 novembre : Jalon J4 (soutenance finale du projet).
- Cinq outils novateurs documentes (Bonus +3 points) : Transformers.js (inference in-browser), ONNX Runtime (interoperabilite des tenseurs), Playwright (tests de non-regression et accessibilite), GitHub CLI (tracabilite Git) et Assistants IA (Antigravity, Claude Code, Codex avec journal de 45 sessions et 87 erreurs documentees).

**Notes pour l'oral.** La rigueur documentaire de l'equipe et les fiches d'outils critiques fournissent un retour concret sur les defis reels du NLP embarque et de l'assistance par IA.

**A ne pas dire.** « 20/11 : V1 du rapport » (la V1 est livree le 19/11 avant la cloture du projet le 20/11) ; inventer des dates non actees dans le suivi.

**Sources.** `docs/suivi/SUIVI.md` ; `docs/suivi/OUTILS_NOVATEURS.md` ; `docs/journal/JOURNAL_USAGE_IA.md` ; Ticket #113, #114.
