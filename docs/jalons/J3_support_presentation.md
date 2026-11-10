# Support de présentation - Jalon J3 (15 points)

**Module** NLP 2 · Master 2 Data & IA · FGES - Université Catholique de Lille  
**Équipe** Data Tigers : Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE  
**Statut** Version consolidée selon le plan de Vaneck du 4 novembre (Ticket #112, 10 diapositives), corrigée le 10 novembre après revue de la PR #134  
**Chiffres et sources de référence** `docs/jalons/J3_chiffres_verifies.md` (PR #124), Protocole 06 gelé (PR #108, #119 ; verrou fusionné le 9 novembre en PR #131), `docs/jalons/J3_diapositives_mahe.md` (PR #132 ; compléments PR #143 et #148 à fusionner) et `docs/jalons/J3_diapositives_jibril.md` (PR #143 à fusionner)  
**Responsables des supports** Vaneck DAGAR (plan et mise en forme), Remy RAYANE (assemblage et coordination) ; diapositives relues par leurs auteurs respectifs (Vaneck et Maïmouna : 2, 6 ; Remy et Mahé : 1, 3, 9, 10 ; Mahé et Remy : 7 ; Jibril : 5, 8 ; Mahé : 4, 7, 8)  
**À mettre à jour le 13 novembre** recomptage du journal et de sa section 4, état de l'entraînement LoRA sur Mac, validation des cinq outils (#14) et éventuelle mesure après adaptation

---

## Diapositive 1 : Où en est-on face aux trois exigences de J3

**Message.** Le volet A est finalisé et déployé sans serveur, le volet B est engagé avec son socle RAG, son protocole verrouillé et ses premières mesures avant adaptation, et la démarche est intégralement documentée.

**Contenu.**
- Cadrage général : deux applications complémentaires sur le corpus du droit du travail (261 fiches pratiques du ministère du Travail, 4 240 passages, instantané SocialGouv du 11 septembre 2026).
- Exigence 1 (Volet A finalisé et déployé) : recherche sémantique dense client-side (Transformers.js), modèle élagué sans perte sous la limite de 100 Mio par fichier de GitHub (65,7 Mio), latence d'encodage de 18,3 ms, seuil d'abstention à 0,8560 et contrastes vérifiés au niveau AA des WCAG 2.1.
- Exigence 2 (Volet B engagé) : assistant local sur `Qwen2.5-7B-Instruct` (Q4_K_M) sous Ollama 0.40.13 (version épinglée), socle RAG fonctionnel avec repères de citation (`[P1]` à `[P5]`), protocole 06 et verrou de mesure gelés (#108, #119, #131), contrôle d'étanchéité appliqué par le générateur (#115, #107), faisabilité LoRA démontrée sur Mac M4 Pro et mesure avant exécutée le 9 novembre sur Legion (sous réserve de confirmation de l'analyse).
- Exigence 3 (Rigueur méthodologique et traçabilité) : démonstration en cours de finalisation, classeur de suivi tenu à jour avec historique des arbitrages, journal d'usage IA auditable (décompte à actualiser le 13/11, plus de 56 sessions consignées) et cinq fiches d'outils novateurs à valider sur le ticket #14 pour le bonus (jusqu'à 3 points).

**Notes pour l'oral.** J3 valide la livraison opérationnelle du premier volet et l'engagement méthodologique du second. Rien n'a été improvisé : chaque jalon s'appuie sur des critères écrits d'avance et des mesures vérifiées. Le lot d'adaptation v2b a été accepté le 10 novembre (3 exemples faux sur 30, soit 10,0 %) et l'entraînement LoRA, transféré exclusivement sur Mac (amendement M1, #52), est relancé pour le 11 novembre avant le point d'arrêt du 12 novembre.

**À ne pas dire.** « Volet B terminé » ; « Volet B adapté » (tant que l'adaptateur n'est pas entraîné et mesuré après adaptation).

**Sources.** `README.md` ; `docs/jalons/J3_chiffres_verifies.md` ; tickets #8, #14, #52, #107, #112 ; PR #108, #115, #119, #131.

---

## Diapositive 2 : Volet A, le site en ligne et son architecture

*(Relecture attendue : Vaneck DAGAR et Maïmouna SIGNATE.)*

**Message.** Une recherche dense calculée à 100 % dans le navigateur du visiteur, sans aucun serveur applicatif ni coût d'infrastructure.

**Contenu.**
- Architecture statique : application web servie par GitHub Pages (`front/`, Vite, React, Tailwind CSS), aucun backend Python en production.
- Moteur d'exécution : Transformers.js 4.3.0 adossé à ONNX Runtime Web (WebAssembly / SIMD), entièrement servi depuis le site sans requête vers un CDN tiers.
- Encodeur dense : `multilingual-e5-small` quantifié en 8 bits (`q8`) pour concilier fidélité de représentation et compacité.
- Asymétrie E5 préservée : préfixes obligatoires `query: ` pour la requête et `passage: ` pour les documents indexés, garantissant le respect de la géométrie latente.
- Optimisation matricielle et intégrité : vecteurs normalisés L2 ramenant la similarité cosinus à un produit scalaire en O(d). Matrice d'embeddings chargée en mémoire typée (`Float32Array`) depuis `index_m2.f32`, métadonnées lues dans `passages_m2.json` via `JSON.parse`, et empreintes SHA-256 vérifiées au chargement (`front/src/recherche/moteur.js`).
- Réactivité utilisateur : 18,3 ms pour encoder une requête dans le navigateur avec le modèle élagué de 65,7 Mio.

**Notes pour l'oral.** L'autonomie totale du site était une contrainte majeure. Le calcul local garantit la confidentialité des requêtes : aucun texte n'est transmis à un serveur externe.

**À ne pas dire.** « 18,6 ms sur le site » (18,6 ms mesurait le `q8` d'origine non élagué de 112,8 Mio dans Chromium au notebook 02) ; « `index.bin` » (le fichier servi est `index_m2.f32`).

**Sources.** `README.md` ; `front/src/recherche/moteur.js` ; `front/src/index.css` ; `scripts/allegement/README.md`.

---

## Diapositive 3 : Volet A, l'allègement sans perte du modèle

**Message.** L'analyse des tenseurs a permis de lever le verrou technique des 100 Mio par fichier de GitHub sans aucune perte vectorielle sur l'alphabet latin ou grec.

**Contenu.**
- Le verrou bloquant : GitHub impose une limite de 100 Mio par fichier. Le modèle quantifié `q8` d'origine chez Xenova pesait 112,8 Mio, imposant un hébergement externe tiers contraire à l'audit d'autonomie.
- Diagnostic structurel : 81,6 % des paramètres du modèle résident dans la table des mots (250 037 entrées de dimension 384), dimensionnée pour couvrir une centaine de langues.
- Recette d'élagage sans perte (#50, PR #78 réalisée par Mahé) : suppression dans le tokeniseur et la table de vocabulaire des pièces contenant un caractère d'un autre alphabet que le latin ou le grec (121 271 pièces gardées sur 250 002), en recopiant les tenseurs conservés sans requantification. Les couches d'attention et de feed-forward restent intactes.
- Résultats métrologiques : poids du modèle `q8` abaissé de 112,8 Mio à 65,7 Mio (−41,8 %), et tokeniseur réduit de 75 %, permettant l'hébergement direct dans le dépôt (`front/public/modele/`).
- Garantie de parité : découpage identique sur les textes de contrôle et identité vectorielle bit à bit vérifiée dans le navigateur sur les 822 requêtes de contrôle par rapport au `q8` d'origine de Xenova.

**Notes pour l'oral.** L'élagage ne retire pas de vocabulaire métier : il retire les sous-mots d'alphabets non utilisés par le corpus (cyrillique, arabe, idéogrammes), et la garantie bit à bit vaut pour tout texte écrit en alphabet latin ou grec. La réduction de 41,8 % lève le verrou d'hébergement tout en préservant l'exactitude mathématique des sorties du modèle `q8`.

**À ne pas dire.** « Élagage basé sur les mots du corpus » (la recette retire les alphabets hors latin/grec) ; « identique bit à bit sur toutes les langues » (la parité exacte porte sur l'alphabet latin ou grec) ; « réduction avec perte ».

**Sources.** `scripts/allegement/README.md` ; `README.md` ; `docs/jalons/J3_chiffres_verifies.md` ; ticket #50, PR #78.

---

## Diapositive 4 : Volet A, mesures et limites

**Source commune.** Voir directement `docs/jalons/J3_diapositives_mahe.md`, section « Diapositive 4 : Volet A, mesures et limites » (ne pas dupliquer le contenu ici afin d'éviter toute divergence lors des mises à jour du 13/11).

**Rôle dans l'assemblage (rappel de synthèse).** Présente le bilan officiel du notebook 03 sur `jeu-questions-v1` (73 questions du corpus issues de 61 fiches, 24 hors corpus) : non-infériorité satisfaite au seuil du J2 (43,8 % contre 42,5 % pour BM25 V3 au passage, +1,4 pt [−11,5 ; +14,3], Tango z = 2,45, p = 0,007 ; 83,6 % contre 79,5 % à la fiche ; aucun des deux systèmes démontré meilleur, McNemar p = 1,000), coût de `q8` (1/73), limite de l'abstention au seuil 0,8560 (9/24 hors corpus rejetées, 72/73 du corpus gardées, AUC = 0,841) et 18,3 ms in-browser.

**Complément en cours d'intégration (PR #148, à relire/fusionner).** Ajoute l'explication sur l'absence de `précision@k` (un seul extrait annoté par question) et mentionne l'ouverture côté Volet B vers la récupération v2 (#138, PR #141, confirmée le 9 novembre de 45,2 % à 72,6 % en récupération seule — non servie par le site web).

---

## Diapositive 5 : Volet B, la chaîne RAG locale

*(Relecture et texte oral : Jibril BENSALEM ; voir le support dédié `docs/jalons/J3_diapositives_jibril.md` en PR #143.)*

**Message.** Le système récupère cinq passages du corpus M2 et les fournit à `Qwen2.5-7B-Instruct` pour rédiger une réponse sourcée avec des références vérifiables.

**Contenu.**
- Modèle génératif local : `Qwen2.5-7B-Instruct` quantifié en 4 bits (GGUF `Q4_K_M`, 4,36 Gio sur disque) servi localement via Ollama 0.40.13 (version épinglée ; les 47 à 67 tokens/s mesurés sur deux prompts courts en 0.34.4 ne constituent pas un benchmark du RAG complet).
- Index documentaire commun : réutilisation des 4 240 passages du corpus M2 (`passages_m2.json`), garantissant le même corpus fermé que le volet A.
- Chaîne `rag-b1-v1` (#85) : récupération par E5 (`fp32`, Python) des 5 passages les plus proches, fenêtre de contexte de 8 192 tokens, sortie bornée à 512 tokens avec marge de 64 tokens (plafond prompt de 7 616 tokens ; refus en cas de dépassement sans troncature silencieuse).
- Contrat de génération et abstention : consigne système imposant de s'appuyer uniquement sur les passages balisés `[P1]` à `[P5]` et de s'abstenir hors périmètre ; en B2, filtrage préalable sous le seuil S = 0,8565.
- Contrôle outillé de forme (`valider_citations` dans `scripts/rag/generation.py`, PR #85) : vérifie automatiquement le format des citations et l'appartenance des repères `[P1]` à `[P5]` au contexte fourni, tout en renvoyant explicitement `justification_semantique_verifiee: False`.
- Complément exploratoire en fin de diapositive (Agent0 Light, `docs/jalons/J3_diapositives_jibril.md`) : générateur de cas de test exploratoires et support de relecture ; sur 18 essais historiques, 15 candidats et 3 rejets automatiques ; relecture humaine à faire, candidats séparés du jeu humain et exclus de l'entraînement (y compris du lot v2b).

**Notes pour l'oral.** Une citation syntaxiquement valide indique quel passage vérifier, mais ne prouve ni l'absence d'hallucination ni l'exactitude juridique de l'énoncé (le lot d'adaptation v1 passait le contrôle formel avec 6 réponses citées fausses sur 15). L'exactitude sémantique et le respect des conditions/exceptions relèvent de l'évaluation humaine à l'aveugle prévue au protocole 06. Pour le texte oral complet et les réponses aux questions du jury (dont Agent0 Light, 30 à 45 s à chronométrer), suivre `docs/jalons/J3_diapositives_jibril.md`.

**À ne pas dire.** « Le sourçage `[Pn]` empêche algorithmiquement les hallucinations » ; « 4,36 Gio en VRAM » (taille du fichier GGUF sur disque) ; « latence premier token < 2 s » (non mesurée) ; « Agent0 validé à 83 % » ou inclus dans l'entraînement.

**Sources.** `docs/etudes/inference_locale_qwen.md` ; `scripts/rag/rag.py` ; `scripts/rag/generation.py` (`preparer_entree`, `valider_citations`) ; `docs/jalons/J3_chiffres_verifies.md` ; `docs/jalons/J3_diapositives_jibril.md` (PR #143) ; `docs/etudes/agent0_bilan_rapport_oral.md`.

---

## Diapositive 6 : Volet B, la démonstration en préparation

*(Relecture attendue : Vaneck DAGAR et Maïmouna SIGNATE.)*

**Message.** Le contrat d'interface est verrouillé (#121), tandis que la maquette (#128) est en cours de finalisation pour illustrer l'assistant local et sa politique d'abstention.

**Contenu.**
- Cadrage fonctionnel : démonstration interactive de l'assistant réglementaire local du cas B1 avec affichage des passages sources `[P1]`–`[P5]` et du **score de similarité** (le contrat #121 précise que ce score « n'est ni une probabilité ni une preuve »).
- Contrat d'interface verrouillé (PR #121, ticket #111) : spécification formalisée des échanges entre l'interface utilisateur et le backend RAG local (requêtes, contextes, citations, réponses, refus d'abstention).
- Maquette en cours de relecture (PR #128, non encore validée) : écran d'accueil, fil de discussion avec rendu des sources et mise en évidence pédagogique du refus de répondre hors périmètre ; des modifications restent demandées (notamment sur le verrou du serveur) avant fusion.
- Intégration technique prévue (#111) : le raccordement direct à l'instance locale d'Ollama 0.40.13 sur la machine de démonstration (Legion) interviendra après validation et fusion de la PR #128 ; l'opportunité d'intégrer la récupération v2 (`bge-m3`, ~2 s sur CPU Mac d'après #138) fera l'objet d'un essai préalable sur le Legion.
- Scénario de test de la soutenance : un jeu d'exemples balisant questions directes, cas multi-sources et déclenchement de l'abstention sera préparé pour la soutenance (prévu le 12 novembre selon #111).

**Notes pour l'oral.** L'interface du volet B rend visible la politique d'abstention. En cas de doute ou de question hors périmètre, l'utilisateur voit pourquoi le système refuse d'inventer et peut lire les passages sources ou constater le seuil de similarité. Présenter l'état réel de la maquette (#128 en finalisation) sans anticiper son intégration avant fusion.

**À ne pas dire.** « Interface de production web » (c'est une démonstration locale pour la soutenance) ; « niveau de confiance » ; « maquette validée et branchée » tant que #128 n'est pas fusionnée.

**Sources.** `docs/etudes/demonstration/contrat_interface_111.md` (PR #121) ; PR #128 (en relecture) ; `docs/etudes/recuperation/02_confirmation_test.md` ; tickets #111 et #114.

---

## Diapositive 7 : Volet B, l'adaptation LoRA

**Source commune.** Voir directement `docs/jalons/J3_diapositives_mahe.md`, section « Diapositive 7 : Volet B, l'adaptation (avec Remy) » (ne pas recopier ici pour garder une source unique maintenue jusqu'au 13/11).

**État d'assemblage au 10 novembre (PR #132 complétée par PR #148 en relecture).**
- Couvre la sélection du Mac M4 Pro face au Legion, la méthode LoRA (rang 8, 16 dernières couches en 4 bits, 2 époques, PR #125), le refus humain du lot v1 (298 exemples, 8/30 faux), le correctif (#107) et le caractère comportemental de l'adaptation (type RAFT : copier, citer, s'abstenir ; 61 fiches du lot de test exclues par `separation.py`).
- Actes du 9–10 novembre intégrés en PR #148 : acceptation du **lot v2b** le 10 novembre sur la grille la plus sévère (3 faux sur 30, soit 10,0 %, à la limite de la règle, avec risque déclaré d'environ 11/54 abstentions injustifiées), production et vérification du **témoin T** le 9 novembre (#140, PR #147), et **amendement M1 (#52)** plaçant l'entraînement, l'export et les mesures exclusivement sur Mac. L'entraînement réel est relancé pour le 11 novembre et l'état final sera complété le **13 novembre**.

---

## Diapositive 8 : Volet B, protocole 06 et mesure avant

**Source commune.** Voir directement `docs/jalons/J3_diapositives_mahe.md`, section « Diapositive 8 : Volet B, protocole 06 et mesure avant (avec Jibril) » et `docs/jalons/J3_diapositives_jibril.md` pour le texte oral de Jibril (ne pas recopier les tableaux ici afin d'éviter une double source).

**État d'assemblage au 10 novembre (PR #132 complétée par PR #143 en relecture).**
- Protocole 06 gelé (#108, #119) avec Ollama 0.40.13 épinglé, calibration technique B0 sans erreur sur 8 questions et verrou fusionné le 9 novembre (#131).
- Mesure **avant** exécutée le 9 novembre sur le Legion (sous réserve de confirmation de réception et d'analyse finale par Mahé) : sur les 97 questions (erreurs techniques exclues des dénominateurs : 2 en B1, 1 en B2), B1 obtient 0/24 (0 %) en M1 et 30/71 (42,3 %) en M4, tandis que B2 obtient 20/24 (83,3 %) en M1 mais s'abstient à tort sur 45/72 (62,5 %, M2) avec 12/72 (16,7 %) en M4.
- L'analyse confirmatoire principale prévue reste B2 après adaptation contre la référence prévue (ou témoin T), sur M1 et M4, avec intervalles bilatéraux à 97,5 % (Bonferroni).

---

## Diapositive 9 : Blocages, risques et arbitrages jusqu'à J4

**Message.** Les blocages techniques et organisationnels sont suivis au fil de l'eau avec des règles de repli écrites d'avance jusqu'au terme fixé au 20 novembre.

**Contenu.**
- Calendrier officiel (#8) : la confirmation écrite des dates officielles de **J3 (16/11 en GitHub) et J4 (30/11)** reste attendue de l'enseignant — à ne pas présenter comme actée collectivement ; seule la **fin des livrables** a été fixée par l'équipe au **20 novembre** (#114).
- Entraînement LoRA et point d'arrêt du 12/11 (#52, #107) : après le blocage du verrou avant le 09/11 (#131 fusionné ce 09/11) et la relecture humaine du lot v2b (accepté le 10/11 à 3/30 = 10,0 % avec risque déclaré ~11/54 abstentions injustifiées), l'entraînement sur Mac seul (amendement M1 du 10/11) a été interrompu le 10/11 et est relancé pour le 11/11. Si la mesure comparative `après` n'est pas finalisée au **point d'arrêt du 12 novembre**, la règle de repli présente la mesure `avant`, la chaîne d'entraînement/export et la feuille de route.
- Service Ollama et export (#140, PR #147) : Ollama 0.40.13 rejette la directive `ADAPTER` avec l'erreur `errAdaptersUnsupported` et exige de bloquer ses mises à jour automatiques (dérive constatée vers 0.40.15 sur un poste Windows non épinglé). Le contournement fusionne les poids en bf16 puis convertit en GGUF Q4_K_M avec contrôle de requantification et comparaison au témoin T (produit et vérifié le 09/11).
- Démonstration (#111, PR #128) : la maquette attend la correction du verrou serveur demandée en revue avant le branchement sur le Legion et la rédaction du scénario de soutenance.
- Étude contrastive d'encodeur (#49) : **le ticket #49 reste ouvert**. En application de la règle de repli du protocole 05 (16/10), le site sert l'encodeur de base élagué ; le 30/10, la poursuite de sa mesure officielle n'a pas été maintenue dans le calendrier resserré afin de prioriser le volet B, et ses enseignements sont versés au rapport final.

**Notes pour l'oral.** Nous assumons nos échecs et nos garde-fous : un lot v1 refusé, un lot v2b accepté à la borne exacte de 10 % avec un biais d'abstention déclaré, une règle de repli écrite d'avance sur #49 comme sur #107, et une traçabilité honnête des dépendances encore ouvertes (#128, #8).

**À ne pas dire.** « La #49 est close » ; « J4 est confirmé officiellement au 30/11 par l'équipe » ; « LoRA tourne nativement sous Ollama ».

**Sources.** `docs/suivi/SUIVI.md` ; `docs/jalons/J3_chiffres_verifies.md` ; tickets #8, #49, #52, #107, #111, #114, #140 ; PR #128, #147, #148.

---

## Diapositive 10 : Calendrier jusqu'à J4 et cinq outils novateurs

**Message.** Un calendrier de fin de projet resserré au 20 novembre et une évaluation critique de cinq outils novateurs issus de l'usage réel.

**Contenu.**
- **9 novembre (réalisé)** : fusion du verrou `#131` ; exécution de la mesure `avant` sur Legion (réception/analyse finale à confirmer par Mahé, PR `#142`/`#143`) ; construction et vérification du témoin T (`#140`, PR `#147`) ; confirmation de la récupération v2 sur le lot de test en récupération seule (`45,2 % -> 72,6 %`, `#138`, PR `#141`).
- **10 novembre (réalisé / en cours)** : acceptation du lot v2b (`3/30 = 10,0 %`) ; amendement M1 concentrant entraînement, export et mesures sur Mac (`#52`) ; préparation de la chaîne d'export `#140` et révision des supports J3 et fiches d'outils.
- **11 novembre (prévu)** : relance de l'entraînement LoRA et export GGUF de l'adaptateur sur Mac (`#107`, `#140`).
- **12 novembre (point d'arrêt strict)** : mesure comparative `après` sur Mac (`#52`, `#107`), scénario de démonstration si `#128` fusionnée.
- **13 novembre (échéance supports `#112` & axes `#113`)** : jugement aveugle des 20 réponses B2 (Maïmouna et Vaneck), finalisation collective des 5 fiches d'outils (#14), recomptage du journal et assemblage final des supports de J3 (`docs/jalons/J3_diapositives_mahe.md`, `J3_diapositives_jibril.md`, ce fichier).
- **16 novembre (à confirmer par écrit, #8)** : Jalon officiel J3 (revue de 20 à 30 minutes : volet A livré, volet B engagé).
- **19 novembre** : livraison de la V1 du rapport final (`#113`).
- **20 novembre** : fin des livrables fixée par l'équipe (supports, site et suivi figés, `#114`).
- **30 novembre (à confirmer par écrit, #8)** : Jalon J4 (soutenance finale).
- **Cinq outils novateurs (bonus jusqu'à 3 points, sélection à valider par l'équipe sur `#14`)** : fiches documentées dans `docs/suivi/outils/` avec retours d'échec, versions et preuves — présélection de la V0 du rapport : Transformers.js (inférence navigateur), ONNX Runtime (Python et Web), Playwright (tests navigateur et accessibilité), GitHub CLI (API REST et droits) et Assistants de développement IA (avec journal de sessions : décompte des sessions et erreurs **à actualiser le 13 novembre**, aux côtés des autres fiches tenues à jour dont Ollama, Sentence Transformers et `uv`).

**Notes pour l'oral.** La rigueur documentaire et les fiches d'outils apportent des retours concrets issus de blocages réels (parité q8 en WASM, rejet `ADAPTER` sous Ollama, interception réseau WebKit, permissions `gh api`, hallucinations ou décalages factuels détectés en revue sur les livrables assistés par IA).

**À ne pas dire.** « 20/11 : V1 du rapport » (la V1 est prévue le 19/11 avant le gel du 20/11) ; « 45 sessions et 87 erreurs » (chiffre périmé, à recompter le 13/11) ; « sélection déjà actée » tant que l'équipe n'a pas validé les 5 outils sur `#14`.

**Sources.** `SUIVI.md` et `OUTILS_NOVATEURS.md` (`docs/suivi/`) ; `J3_chiffres_verifies.md` (`docs/jalons/`) ; `RAPPORT_FINAL.md` (section 5) ; `JOURNAL_USAGE_IA.md` ; tickets #8, #14, #112, #113, #114.
