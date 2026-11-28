# Support de présentation - Jalon J3 (15 points)

**Module** NLP 2 · Master 2 Data & IA · FGES - Université Catholique de Lille  
**Équipe** Data Tigers : Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE  
**Statut** Version consolidée selon le plan de Vaneck du 4 novembre (Ticket #112, 10 diapositives), actualisée le 13 novembre après retours de Maïmouna (#134) et résultats #52  
**Chiffres et sources de référence** `docs/jalons/J3_chiffres_verifies.md` (PR #124), Protocole 06 gelé (PR #108, #119 ; verrou fusionné le 9 novembre en PR #131), `docs/jalons/J3_diapositives_mahe.md` (PR #132 et #148 fusionnées, PR #152) et `docs/jalons/J3_diapositives_jibril.md` (PR #143 fusionnée, PR #152)  
**Responsables des supports** Vaneck DAGAR (plan et mise en forme), Remy RAYANE (assemblage et coordination) ; diapositives relues par leurs auteurs respectifs (Vaneck et Maïmouna : 2, 6 ; Remy et Mahé : 1, 3, 9, 10 ; Mahé et Remy : 7 ; Jibril : 5, 8 ; Mahé : 4, 7, 8)  
**À mettre à jour d'ici le 14-15 novembre** recomptage du journal et de sa section 4, retour du jugement à l'aveugle attendu le 14/11 (#52), état du raccordement de la démonstration (#111) et validation des cinq outils (#14)

---

## Diapositive 1 : Où en est-on face aux trois exigences de J3

**Message.** Le volet A est finalisé et déployé sans serveur, le volet B est engagé avec son socle RAG, son protocole verrouillé et ses mesures avant, témoin et après adaptation, et la démarche est intégralement documentée.

**Contenu.**
- Cadrage général : deux applications complémentaires sur le corpus du droit du travail (261 fiches pratiques du ministère du Travail, 4 240 passages, instantané SocialGouv du 11 septembre 2026).
- Exigence 1 (Volet A finalisé et déployé) : recherche sémantique dense client-side (Transformers.js), modèle élagué sans perte sous la limite de 100 Mio par fichier de GitHub (65,7 Mio), latence d'encodage de 18,3 ms, seuil d'abstention à 0,8560 et contrastes vérifiés au niveau AA des WCAG 2.1.
- Exigence 2 (Volet B engagé) : assistant local sur `Qwen2.5-7B-Instruct` (Q4_K_M) sous Ollama 0.40.13 (version épinglée), socle RAG fonctionnel avec repères de citation (`[P1]` à `[P5]`), protocole 06 et verrou de mesure gelés (#108, #119, #131), contrôle d'étanchéité appliqué par le générateur (#115, #107), faisabilité LoRA démontrée sur Mac M4 Pro, mesure avant exécutée le 9 novembre sur Legion et vérifiée à l'identique (#52), puis entraînement v2b, export GGUF et mesures témoin T et après adaptation exécutés le 11 novembre sur Mac (#52, #140 ; jugement humain à l'aveugle en attente).
- Exigence 3 (Rigueur méthodologique et traçabilité) : maquette de démonstration fusionnée (#128, raccordement final sur Mac à terminer), classeur de suivi tenu à jour avec historique des arbitrages, journal d'usage IA auditable (décompte à actualiser le 13/11, plus de 56 sessions consignées) et cinq fiches d'outils novateurs à valider sur le ticket #14 pour le bonus (jusqu'à 3 points).

**Notes pour l'oral.** J3 valide la livraison opérationnelle du premier volet et l'engagement méthodologique du second. Rien n'a été improvisé : chaque jalon s'appuie sur des critères écrits d'avance et des mesures vérifiées. Le lot d'adaptation v2b a été accepté le 10 novembre (3 exemples faux sur 30, soit 10,0 %) ; transféré exclusivement sur Mac (amendement M1, #52), l'entraînement LoRA, l'export GGUF et la mesure comparative après adaptation face au témoin T ont été menés le 11 novembre (+11,1 points sur M4 en B2, p = 0,0078), avant le jugement humain à l'aveugle attendu le 14 novembre (#52).

**À ne pas dire.** « Volet B terminé » ; « exactitude juridique validée » (le jugement humain à l'aveugle de 20 réponses B2 par camp reste à faire) ; « amélioration démontrée sur M1 hors corpus » (M1 reste à 20/24 de part et d'autre, p = 1).

**Sources.** `README.md` ; `docs/jalons/J3_chiffres_verifies.md` ; tickets #8, #14, #52, #107, #112 ; PR #108, #115, #119, #131.

---

## Diapositive 2 : Volet A, le site en ligne et son architecture

*(Relecture : Vaneck DAGAR et Maïmouna SIGNATE ; remarques de Maïmouna du 12/11 intégrées.)*

**Message.** Une recherche dense calculée à 100 % dans le navigateur du visiteur, sans aucun serveur applicatif ni coût d'infrastructure.

**Contenu.**
- Architecture statique : application web servie par GitHub Pages (`front/`, Vite, React, Tailwind CSS), aucun backend Python en production.
- Mise en ligne automatique (#29) : à chaque modification de `front/` sur `dev`, GitHub Actions construit le site et le publie sur GitHub Pages (`.github/workflows/deploiement-volet-a.yml`) ; le chemin de base `/data_tigers_nlp/` (`front/vite.config.js`) évite la page blanche.
- Moteur d'exécution : Transformers.js 4.3.0 adossé à ONNX Runtime Web (exécution locale dans le navigateur via WebAssembly), entièrement servi depuis le site sans requête vers un CDN tiers.
- Encodeur dense : `multilingual-e5-small` quantifié en 8 bits (`q8`) pour concilier fidélité de représentation et compacité.
- Asymétrie E5 préservée : préfixes obligatoires `query: ` pour la requête et `passage: ` pour les documents indexés, indispensables pour projeter questions et passages dans le même espace vectoriel.
- Optimisation matricielle et intégrité : les vecteurs ont une longueur de 1 (normalisés L2), où un simple produit scalaire donne la similarité avec chacun des 4 240 passages. Matrice d'embeddings chargée en mémoire typée (`Float32Array`) depuis `index_m2.f32`, métadonnées lues dans `passages_m2.json` via `JSON.parse`, et empreintes SHA-256 vérifiées au chargement (`front/src/recherche/moteur.js`).
- Réactivité utilisateur : 18,3 ms pour encoder une requête dans le navigateur avec le modèle élagué de 65,7 Mio.

**Notes pour l'oral.** L'autonomie totale du site était une contrainte majeure. Le calcul local garantit la confidentialité des requêtes : aucun texte n'est transmis à un serveur externe. Pour l'oral, expliquer simplement l'optimisation : les vecteurs étant de norme 1, la similarité cosinus se réduit au produit scalaire direct, calculable en quelques millisecondes dans le navigateur sans composant serveur.

**À ne pas dire.** « 18,6 ms sur le site » (18,6 ms mesurait le `q8` d'origine non élagué de 112,8 Mio dans Chromium au notebook 02) ; « `index.bin` » (le fichier servi est `index_m2.f32`).

**Sources.** `README.md` ; `front/src/recherche/moteur.js` ; `front/src/index.css` ; `scripts/allegement/README.md` ; ticket #29 ; `.github/workflows/deploiement-volet-a.yml` ; `front/vite.config.js`.

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

**Complément intégré (PR #148, fusionnée le 10 novembre).** Ajoute l'explication sur l'absence de `précision@k` (un seul extrait annoté par question) et mentionne l'ouverture côté Volet B vers la récupération v2 (#138, PR #141, confirmée le 9 novembre de 45,2 % à 72,6 % en récupération seule, non servie par le site web).

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

*(Relecture : Vaneck DAGAR et Maïmouna SIGNATE ; remarques de Maïmouna du 12/11 intégrées.)*

**Message.** L'interface et la couche locale de l'assistant sont livrées et ont tourné avec le vrai Qwen ; restent l'essai sur le Mac avec le témoin T et le modèle adapté, le scénario et la vidéo.

**Contenu.**
- Ce que voit l'utilisateur : la réponse rédigée, chaque référence `[P1]` à `[P5]` ouvrant la carte de son passage (fiche, section, lien, score de similarité), un encadré distinct quand le modèle s'abstient, et le nom du modèle qui a rédigé la réponse.
- Contrat d'interface validé (PR #121) : deux routes d'API, l'état de la chaîne et la question ; réponse citée, abstention, réponse non conforme et erreurs sont signalées chacune à sa façon.
- Interface et couche locale livrées (PR #128, fusionnée le 11 novembre) : la couche relie l'interface à la chaîne de la #85 sans en changer la logique, sur 127.0.0.1 uniquement, une question à la fois. Le modèle servi se choisit au lancement de la couche, jamais depuis le navigateur.
- Premier essai avec le vrai Qwen (Maïmouna, 8 novembre), sur sa machine Windows avec le modèle de base : abstention et réponses citées s'affichent, et les citations ouvrent leurs passages. Une abstention a pris 88 s.
- Machine de la démonstration : le Mac de Mahé, avec Ollama 0.40.13 (amendement M1, #52), le témoin T (`temoin-q4_k_m-local`) et le modèle adapté (`lora-v2b-q4_k_m-local`). Essai à faire avec Mahé ce week-end.
- Scénario de 3 à 4 minutes (#111), en cours : une question directe, une question qui croise deux passages, une question hors corpus (abstention), et la même question posée à T puis au modèle adapté. Vidéo de secours le 18 novembre.

**Notes pour l'oral.** L'abstention est rendue visible, mais l'interface ne prétend pas en connaître la raison : elle indique que le modèle s'est abstenu à partir des passages fournis, et que la question sort peut-être du périmètre. L'utilisateur peut ouvrir les passages consultés pour vérifier. La démonstration n'applique pas le seuil S de la mesure : c'est le modèle seul qui décide de s'abstenir. Pour comparer T et le modèle adapté, la couche est relancée avec l'autre modèle, et la réponse indique lequel l'a rédigée. Une réponse peut prendre plus d'une minute : la vidéo est plus sûre qu'une démonstration en direct.

**À ne pas dire.** « Interface de production web » (c'est une démonstration locale pour la soutenance) ; « niveau de confiance » ; « l'utilisateur voit pourquoi le système refuse » ; « seuil de similarité » à propos de la démonstration ; « démonstration testée sur le Mac » ou « avec le modèle adapté » tant que l'essai n'est pas fait ; « démonstration branchée sur `bge-m3` ».

**Sources.** `docs/etudes/demonstration/contrat_interface_111.md` (PR #121) ; PR #128 (fusionnée le 11 novembre) et revue de Maïmouna du 8 novembre ; `demo_b/src/composants/Reponse.jsx` et `Passage.jsx` ; `scripts/rag/serveur_demo.py` ; #52 (amendement M1, modèles et digests du 11 novembre) ; #111 ; #134.

---

## Diapositive 7 : Volet B, l'adaptation LoRA

**Source commune.** Voir directement `docs/jalons/J3_diapositives_mahe.md`, section « Diapositive 7 : Volet B, l'adaptation (avec Remy) » (ne pas recopier ici pour garder une source unique maintenue jusqu'au 13/11).

**État d'assemblage au 11 novembre (PR #132 et #148 fusionnées, résultats du #52).**
- Couvre la sélection du Mac M4 Pro face au Legion, la méthode LoRA (rang 8, 16 dernières couches en 4 bits, 2 époques, PR #125), le refus humain du lot v1 (298 exemples, 8/30 faux), le correctif (#107) et le caractère comportemental de l'adaptation (type RAFT : copier, citer, s'abstenir ; 61 fiches du lot de test exclues par `separation.py`).
- Actes du 9 au 11 novembre : acceptation du **lot v2b** le 10 novembre sur la grille la plus sévère (3 faux sur 30, soit 10,0 %, à la limite de la règle, avec risque déclaré d'environ 11/54 abstentions injustifiées), production et vérification du **témoin T** le 9 novembre (#140, PR #147), **amendement M1 (#52)** plaçant l'entraînement, l'export et les mesures exclusivement sur Mac, puis entraînement LoRA et export GGUF exécutés le 11 novembre (modèle adapté `cebe1e37…`, digest Ollama `18cb25f0…`).

---

## Diapositive 8 : Volet B, résultats de l'adaptation (avec Jibril)

**Source commune.** Voir directement `docs/jalons/J3_diapositives_mahe.md`, section « Diapositive 8 : Volet B, résultats de l'adaptation (avec Jibril) » (PR #152) et `docs/jalons/J3_diapositives_jibril.md` pour le texte oral de Jibril (ne pas recopier les tableaux ici afin d'éviter une double source).

**État d'assemblage au 13 novembre (PR #132, #143, #148 fusionnées, PR #152, résultats du #52).**
- Protocole 06 gelé (#108, #119) avec Ollama 0.40.13 épinglé, calibration technique B0 sans erreur sur 8 questions et verrou fusionné le 9 novembre (#131).
- Mesure **avant** exécutée le 9 novembre sur le Legion (archive reçue, vérifiée fichier par fichier et analyse reproduite à l'identique par Mahé le 9 novembre sur #52 ; référence descriptive non comparée directement au Mac selon l'amendement M1) : sur les 97 questions (erreurs techniques exclues des dénominateurs : 2 en B1, 1 en B2), B1 obtient 0/24 (0 %) en M1 et 30/71 (42,3 %) en M4, tandis que B2 obtient 20/24 (83,3 %) en M1 mais s'abstient à tort sur 45/72 (62,5 %, M2) avec 12/72 (16,7 %) en M4.
- Mesures **témoin T** et **après** exécutées le 11 novembre sur le Mac de Mahé (amendement M1, #52, Ollama 0.40.13, une seule exécution par état, au plus 2,1 % d'erreurs techniques, Q088 en erreur dans les quatre états avec récupération). Sur l'analyse confirmatoire principale (**B2 adapté contre B2 du témoin T**, intervalles bilatéraux à 97,5 %) : **M4** (citation pertinente sur 72 questions) progresse de **10/72 (13,9 %) à 18/72 (25,0 %)**, soit **+11,1 points** ([+2,1 ; +23,8], McNemar exact `p = 0,0078`, **amélioration démontrée**) ; **M1** (abstention correcte hors corpus) reste à **20/24 (83,3 %) contre 20/24 (83,3 %)** (0,0 pt [−20,5 ; +20,5], `p = 1`, amélioration non démontrée). En descriptif (IC 95 %), l'abstention à tort en B2 (M2) recule de 70,8 % à 55,6 % (−15,3 pts [−26,3 ; −5,4]) et les citations valides (M3) montent de 25,0 % à 44,4 % (+19,4 pts [+9,8 ; +30,8], sorties invalides de 3 à 0), avec M5 inchangé à 4/24. Le retour du jugement humain à l'aveugle de 20 réponses citées de B2 par camp (`temoin` contre `apres`, graine 20261018, par Maïmouna et Vaneck) est attendu le 14 novembre (#52).

---

## Diapositive 9 : Blocages, risques et arbitrages jusqu'à J4

**Message.** Les blocages techniques et organisationnels sont suivis au fil de l'eau avec des règles de repli écrites d'avance jusqu'au terme fixé au 20 novembre.

**Contenu.**
- Calendrier officiel (#8) : la confirmation écrite des dates officielles de **J3 (16/11 en GitHub) et J4 (30/11)** reste attendue de l'enseignant, à ne pas présenter comme actée collectivement ; seule la **fin des livrables** a été fixée par l'équipe au **20 novembre** (#114).
- Entraînement LoRA et mesure après adaptation (#52, #107) : après le verrou du 09/11 (#131), l'acceptation du lot v2b le 10/11 (3/30 = 10,0 % avec risque déclaré ~11/54 abstentions injustifiées) et une interruption le 10/11 sous l'amendement M1, l'entraînement sur Mac, l'export GGUF (#140) et les mesures `temoin` et `apres` ont été menés le 11/11 (+11,1 pts en B2 M4 contre T, `p = 0,0078` ; M1 inchangé à 20/24). Le retour du jugement humain à l'aveugle de 20 réponses B2 par camp est attendu le 14 novembre (#52).
- Service Ollama et export (#140, PR #147 et #151) : Ollama 0.40.13 rejette la directive `ADAPTER` avec l'erreur `errAdaptersUnsupported` et exige de bloquer ses mises à jour automatiques (dérive constatée vers 0.40.15 sur un poste Windows non épinglé). Le contournement fusionne les poids en bf16 puis convertit en GGUF Q4_K_M avec contrôle de requantification et comparaison au témoin T (produit et vérifié le 09/11 ; PR #151 adapte `test_export.py` au refus de liens symboliques `WinError 1314` sous Windows 11).
- Démonstration (#111, PR #128 fusionnée le 11 novembre) : depuis l'amendement M1 (#52), la démonstration tourne sur le Mac de Mahé avec Ollama 0.40.13 en local ; restent le raccordement local final, l'essai de `bge-m3` sur ce Mac et la rédaction du scénario de soutenance.
- Étude contrastive d'encodeur (#49) : **le ticket #49 reste ouvert**. En application de la règle de repli du protocole 05 (16/10), le site sert l'encodeur de base élagué ; le 30/10, la poursuite de sa mesure officielle n'a pas été maintenue dans le calendrier resserré afin de prioriser le volet B, et ses enseignements sont versés au rapport final.

**Notes pour l'oral.** Nous assumons nos échecs et nos garde-fous : un lot v1 refusé, un lot v2b accepté à la borne exacte de 10 % avec un biais d'abstention déclaré, une règle de repli écrite d'avance sur #49 comme sur #107, et une traçabilité honnête des dépendances encore ouvertes (#111, #52, #14, #8).

**À ne pas dire.** « La #49 est close » ; « J4 est confirmé officiellement au 30/11 par l'équipe » ; « LoRA tourne nativement sous Ollama ».

**Sources.** `docs/suivi/SUIVI.md` ; `docs/jalons/J3_chiffres_verifies.md` ; tickets #8, #49, #52, #107, #111, #114, #140 ; PR #128, #147, #148, #151.

---

## Diapositive 10 : Calendrier jusqu'à J4 et cinq outils novateurs

**Message.** Un calendrier de fin de projet resserré au 20 novembre et une évaluation critique de cinq outils novateurs issus de l'usage réel.

**Contenu.**
- **9 novembre (réalisé)** : fusion du verrou `#131` ; exécution de la mesure `avant` sur Legion (archive vérifiée fichier par fichier et analyse reproduite à l'identique par Mahé sur `#52`, PR `#142`/`#143`) ; construction et vérification du témoin T (`#140`, PR `#147`) ; confirmation de la récupération v2 sur le lot de test en récupération seule (`45,2 % -> 72,6 %`, `#138`, PR `#141`).
- **10 novembre (réalisé)** : acceptation du lot v2b (`3/30 = 10,0 %`) ; amendement M1 concentrant entraînement, export et mesures sur Mac (`#52`) ; fusions de la chaîne d'export (`#140`, PR `#147`) et des compléments de diapositives (PR `#148`), et révision des supports J3 et fiches d'outils.
- **11 novembre (réalisé)** : fusions de la maquette de démonstration (`#128`) et de la section rapport (`#150`) ; entraînement LoRA, export GGUF et mesures `temoin` et `apres` sur le Mac de Mahé (`#52`, B2 M4 +11,1 pts contre T à `p = 0,0078`).
- **12 novembre (point d'arrêt strict)** : finalisation du raccordement local de la démonstration, essai `bge-m3` et scénario de soutenance sur le Mac de Mahé (`#111`), et suite des relectures ouvertes (`#143`, `#145`, `#146`, `#151`).
- **13 novembre** : finalisation collective des 5 fiches d'outils (#14), recomptage du journal d'usage IA et de sa section 4.
- **14 novembre** : retour attendu du jugement humain à l'aveugle de 20 réponses citées de B2 par camp (`temoin` contre `apres`, Maïmouna et Vaneck, #52).
- **15-16 novembre (échéance supports `#112`)** : assemblage final des supports de J3 avec Vaneck (`docs/jalons/J3_diapositives_mahe.md`, `J3_diapositives_jibril.md`, ce fichier).
- **16 novembre (à confirmer par écrit, #8)** : Jalon officiel J3 (revue de 20 à 30 minutes : volet A livré, volet B engagé).
- **19 novembre** : livraison de la V1 du rapport final (`#113`).
- **20 novembre** : fin des livrables fixée par l'équipe (supports, site et suivi figés, `#114`).
- **30 novembre (à confirmer par écrit, #8)** : Jalon J4 (soutenance finale).
- **Cinq outils novateurs (bonus jusqu'à 3 points, sélection à valider par l'équipe sur `#14`)** : fiches documentées dans `docs/suivi/outils/` avec retours d'échec, versions et preuves (présélection de la V0 du rapport : Transformers.js pour l'inférence navigateur, ONNX Runtime en Python et Web, Playwright pour les tests navigateur et l'accessibilité, GitHub CLI face à l'API REST et ses droits, et Assistants de développement IA avec journal de sessions, dont le décompte des sessions et erreurs est **à actualiser le 13 novembre**, aux côtés des autres fiches tenues à jour dont Ollama, Sentence Transformers et `uv`).

**Notes pour l'oral.** La rigueur documentaire et les fiches d'outils apportent des retours concrets issus de blocages réels (parité q8 en WASM, rejet `ADAPTER` sous Ollama, interception réseau WebKit, permissions `gh api`, hallucinations ou décalages factuels détectés en revue sur les livrables assistés par IA).

**À ne pas dire.** « 20/11 : V1 du rapport » (la V1 est prévue le 19/11 avant le gel du 20/11) ; « 45 sessions et 87 erreurs » (chiffre périmé, à recompter le 13/11) ; « sélection déjà actée » tant que l'équipe n'a pas validé les 5 outils sur `#14`.

**Sources.** `SUIVI.md` et `OUTILS_NOVATEURS.md` (`docs/suivi/`) ; `J3_chiffres_verifies.md` (`docs/jalons/`) ; `RAPPORT_FINAL.md` (section 5) ; `JOURNAL_USAGE_IA.md` ; tickets #8, #14, #112, #113, #114.
