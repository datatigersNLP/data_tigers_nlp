# Rapport du projet NLP 2

**Équipe** Data Tigers
**Membres** Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE
**Module** NLP 2, projet de fin de module
**Formation** Master 2 Data & IA, FGES, Université Catholique de Lille
**Année universitaire** 2026-2027
**Enseignant** Adrian ROSARI
**Version** V1, état du 26 novembre 2026 (V0 du 19 octobre), à remettre strictement avant le jalon J4

**Objet.** Ce rapport suit la section 11 du sujet : analyse technique, retour d'expérience, axes de progression et cinq outils novateurs. La V0 a été écrite à la fin du volet A, le 19 octobre. Cette V1 ajoute le volet B, adapté et mesuré, les améliorations du volet A servies depuis le 15 novembre, la justification du passage de 5 à 10 passages demandée par l'enseignant (section 2.4), les essais d'encodeurs entraînés sur des questions synthétiques, non retenus (section 2.3), et les mentions de confidentialité ajoutées aux deux interfaces (section 2.2). Ce qui reste à mesurer ou à rédiger est signalé explicitement (section 6).

**Sources.** Tous les chiffres proviennent du dépôt (`datatigersNLP/data_tigers_nlp`) : études, protocoles, mesures, classeur de suivi, journal d'usage de l'IA, historique Git et tickets GitHub. L'annexe relie chaque chiffre à sa source. Les mesures du site en ligne datées du 19 octobre 2026 ont été faites sur la version `7e2ce07`. Les questions du jeu v2 et certains jugements ont été produits par Claude, sur autorisation écrite de l'enseignant ; ils sont signalés comme tels (section 3.1).

*Ce document a été produit avec l'assistance d'outils d'intelligence artificielle. Les usages sont consignés dans le journal prévu par le sujet ; chaque chiffre a été recoupé avec sa source avant publication.*

---

## 1. Le projet en bref

| Volet | Cas | Ce qui est livré |
|---|---|---|
| A, application en ligne | A3, recherche sémantique en corpus fermé | site public https://datatigersnlp.github.io/data_tigers_nlp/, inférence dans le navigateur, aucun serveur |
| B, application locale | B1, assistant réglementaire sourcé, avec abstention | chaîne RAG locale : Qwen2.5-7B-Instruct adapté par l'équipe, récupération par fusion avec BM25 et reclasseur, démonstration sur un Mac |

Le corpus est commun : les 261 fiches pratiques du ministère du Travail, découpées en 4 240 passages, instantané SocialGouv du 11 septembre 2026, sous Licence Ouverte Etalab 2.0. Le cas A3 constitue la couche de récupération du cas B1 : le découpage, l'encodage et l'index sont écrits une fois et servent aux deux volets.

La fin du volet A est marquée par le tag annoté `volet-a-v1`, posé le 18 octobre 2026 sur `main` (`8955962`). Le site en ligne est déployé depuis `dev`. Depuis le 15 novembre, il sert l'encodeur ajusté par l'équipe et affiche 10 passages regroupés par fiche (#164, PR #165). À la demande de l'enseignant, les deux interfaces affichent le logo de l'équipe et une fenêtre de confidentialité (#176, PR #177).

## 2. Analyse technique

### 2.1 Ce que chaque volet met en œuvre

| | Volet A | Volet B |
|---|---|---|
| Modèle | `multilingual-e5-small`, encodeur de phrases | `Qwen2.5-7B-Instruct`, modèle génératif |
| Entraîné par l'équipe | oui : ajustement contrastif sur 109 paires question-passage (#49), servi depuis le 15 novembre | oui : adaptation LoRA sur 218 exemples (lot v2b, #107), fusionnée dans les poids, puis quantifiée |
| Forme servie | q8 (entiers sur 8 bits) de l'encodeur ajusté, vocabulaire élagué sans perte : 65,7 Mio | GGUF Q4_K_M : 4,36 Gio |
| Exécution | navigateur du visiteur, Transformers.js 4.3.0 et ONNX Runtime Web | Mac de l'équipe (M4 Pro, 24 Gio de mémoire unifiée), Ollama 0.40.13 ; entraînement de l'adaptateur sur le même Mac |
| Récupération | recherche dense seule | chaîne de démonstration (PR #175) : E5 de base et BM25 fusionnés, 20 candidats reclassés par `bge-reranker-v2-m3` ; 5 passages d'E5 dans la chaîne mesurée en B2 |
| Sortie | 10 passages réels, regroupés par fiche, avec score, section et lien ; avertissement si la correspondance est faible | réponse rédigée, citant les 10 passages fournis, ou abstention |

**Ce que l'équipe a entraîné.** Le sujet oppose un modèle « de faible capacité, long à entraîner, entièrement maîtrisé » (volet A) à un modèle « performant, immédiatement disponible, dont la composition n'est pas connue » (volet B). Il précise que le modèle servi du volet A « doit préférentiellement être celui que vous avez entraîné ».

**Volet A : l'encodeur ajusté est servi depuis le 15 novembre.**
- **Jusqu'au 15 novembre, la règle de repli s'appliquait.** Le protocole 05, figé avant toute mesure, gardait l'encodeur de base si une de ses conditions manquait le 16 octobre ; la mesure n'ayant pas été faite à temps, le site a servi l'encodeur de base pendant un mois.
- **Mesure du 15 novembre** (amendement A1, figé avant la mesure) : sur le lot de test, le Recall@5 passe de 43,8 % à 63,0 % (+19,2 points [+9,7 ; +30,4]) ; sur le CDTN, de 67,4 % à 72,3 %. La règle est satisfaite et l'ajusté est déclaré meilleur au niveau du passage.
- **Avec 10 passages regroupés par fiche**, une fiche pertinente est affichée pour 93,2 % des questions du lot de test, contre 83,6 % sur le site précédent.
- **Deux encodeurs nourris de questions synthétiques ne sont pas servis.** Entraînés sur 2 289 puis 2 420 questions générées, par le modèle témoin puis par Claude Sonnet, ils ne font pas mieux que l'ajusté sur les questions humaines (section 2.3).

**Volet B : un comportement, pas des connaissances.** L'adaptation apprend au modèle à citer les passages fournis et à s'abstenir hors du corpus ; les faits restent dans les passages. Les 61 fiches du lot de test sont exclues des données d'entraînement. Ollama refusant les adaptateurs LoRA, l'adaptateur est fusionné dans les poids bf16 officiels, converti en GGUF et quantifié ; le modèle de base suit la même chaîne et sert de témoin T.

**La maîtrise porte aussi sur l'exécution** :
- chaque octet servi est versionné, ou vérifié par empreinte ;
- les vecteurs du navigateur sont contrôlés contre ceux de Python ;
- à l'exécution, rien ne dépend d'un service tiers.

### 2.2 Comparaison sur les six dimensions du sujet

Pour le volet A, la qualité est celle de l'encodeur ajusté, servi depuis le 15 novembre ; le coût et la latence ont été mesurés avec l'encodeur de base, de même architecture et de même taille une fois élagué (65,7 Mio), et n'ont pas été remesurés. Pour le volet B, la latence et la qualité sont celles de la chaîne de démonstration, mesurée de bout en bout le 21 novembre sur le jeu v2 (protocole 10) ; l'exactitude jugée par des humains relève de #52.

| Dimension | Volet A, mesuré | Volet B, mesuré |
|---|---|---|
| Coût | aucun coût de service : GitHub Pages, fichiers statiques. Le coût est reporté sur le visiteur : 61,3 Mio transférés à la première visite, puis mise en cache | aucun coût de service, mais un matériel dédié : modèle de 4,36 Gio, démonstration sur un Mac M4 Pro de 24 Gio de mémoire unifiée. Sur une carte NVIDIA, le 19 octobre, 5 694 Mio de VRAM occupés après le premier appel (1 036 Mio avant) |
| Latence | recherche : 21 ms en médiane sur 10 questions (19 à 24 ms), 46 ms pour la première ; premier résultat 20,1 s après l'ouverture d'une page jamais visitée, sur la connexion de mesure | chaîne de démonstration (10 passages, reclasseur) : 11,8 s par question en médiane sur le jeu v2, contre 4,9 s pour l'ancienne chaîne à 5 passages. Le premier appel charge le modèle : 37,7 s, dont 19,1 s de chargement, le 19 octobre sur une carte NVIDIA |
| Qualité | Recall@5 de 63,0 % sur 73 questions du corpus (IC 95 % : 50,9 à 73,6), contre 43,8 % pour l'encodeur de base et 42,5 % pour BM25. Avec 10 passages regroupés par fiche, une fiche pertinente est affichée pour 93,2 % des questions | réponses citant un passage pertinent : 52,9 % (63 sur 119) avec le modèle adapté, 10,1 % avec le modèle d'origine ; +16,9 points [+6,4 ; +27,3] sur l'ancienne chaîne, démontré. Abstention correcte sur les 39 questions hors corpus évaluées, hors corpus au sens du protocole 10. Jugées à l'aveugle par deux membres, sur 20 réponses par modèle de l'ancienne chaîne : pas plus exactes, mais mieux appuyées sur leurs passages (#52) |
| Contrôle | tout est figé et vérifiable : modèle, index et passages par empreinte SHA-256, versions épinglées, vecteurs identiques bit à bit entre q8 d'origine et q8 élagué (822 sur 822) | poids et gabarit figés par empreinte, température 0, graine fixée ; mais le comportement du modèle dépend de données d'entraînement inconnues |
| Explicabilité | chaque résultat est un passage réel, avec son score de similarité, sa section et le lien vers la fiche ; rien n'est généré. Limite : le score ne se lit qu'en relatif ; les cinq passages de la question sur les congés payés vont de 0,895 à 0,889 | la réponse cite ses passages ; une citation existante ne prouve ni sa justification ni la couverture de chaque affirmation |
| Dépendance à un fournisseur | à l'exécution, aucune : seul le site est contacté, vérifié sous Chromium, Firefox et WebKit. À la construction : GitHub (Pages, Actions), npm, et Hugging Face pour l'origine du q8, recopié dans le site | Ollama, poids publiés par l'équipe Qwen (Apache 2.0) et reclasseur `bge-reranker-v2-m3` ; aucune API distante à l'exécution |

**Abstention.** Le volet A signale les questions hors du périmètre par un seuil de similarité, fixé sur un jeu externe (CDTN) avant la mesure, et avertit dans une zone grise juste au-dessus. Avec l'encodeur ajusté servi, le score sépare assez bien les questions hors corpus (AUC 0,865). Le seuil conserve 70 des 73 questions du corpus du lot de test et rejette 10 des 24 questions hors corpus ; 13 autres reçoivent l'avertissement. Il repère surtout les saisies sans rapport avec le droit du travail, et l'interface ne promet pas davantage.

**Confidentialité.** À la demande de l'enseignant, chaque interface ouvre une fenêtre de confidentialité (#176, PR #177). Elle décrit ce qui a été vérifié le 21 novembre :
- le site en ligne ne contacte que son propre domaine, n'envoie rien quand on pose une question, ne dépose aucun cookie et ne garde dans le cache du navigateur que les fichiers du modèle, environ 100 Mo ;
- l'hébergeur, GitHub Pages, journalise les adresses IP pour sa sécurité ;
- dans la configuration de la démonstration, l'assistant local ne journalise ni les questions ni les réponses ;
- les mentions légales nomment le directeur de la publication, Mahé BEGNIS, et l'hébergeur.

### 2.3 Ce que les mesures ont appris

- **Mesurer là où le modèle est servi.** Le q8 exécuté dans le navigateur ne calcule pas exactement comme le même q8 en Python. Il donne le même premier résultat que le calcul exact pour 91,8 % des requêtes, contre 96,5 % prévus par la simulation Python. Le premier résultat reste toutefois dans les 5 premiers pour 99,9 % d'entre elles. Seule la mesure dans le navigateur a révélé l'écart.
- **L'essentiel du poids était inutile.** La table des mots représente 81,6 % des paramètres de l'encodeur et couvre 250 037 pièces d'une centaine de langues. Retirer celles qui contiennent une lettre étrangère aux alphabets latin et grec ramène le q8 de 112,8 à 65,7 Mio (−42 %), avec des sorties identiques bit à bit. Le modèle passe ainsi sous la limite de 100 Mio par fichier de GitHub et peut être servi par le site lui-même.
- **Une dépendance invisible.** À son import, Transformers.js fait télécharger le moteur d'exécution ONNX Runtime depuis le CDN jsDelivr. Le site semblait autonome, et seul un essai avec ce CDN bloqué l'a montré. Le moteur est servi par le site depuis la PR #81.
- **Le parcours au clavier dépend du système.** Sur macOS, où la navigation au clavier est désactivée par défaut, Tab ne passe pas par les boutons. Dans le menu sur téléphone, le focus quittait alors le panneau. La tabulation y est désormais entièrement gérée par le code (PR #102), et vérifiée sous trois moteurs.
- **Plus de questions synthétiques ne font pas une meilleure recherche.** Deux encodeurs ont repris la recette de l'ajusté avec vingt fois plus de questions générées : 2 289 écrites par le modèle témoin T (v2-T, amendement A2), puis 2 420 écrites par des sous-agents Claude Sonnet et relues par deux juges Claude Opus (v3-C, amendement A3, figé avant toute génération). La règle de l'amendement A2 retenait la v2-T, sans gain démontré : +5,8 points de Recall@5 sur le jeu v2 (intervalle contenant 0), égalité exacte sur le CDTN, −5,5 sur les questions humaines du lot de test ; Mahé a choisi de mesurer plutôt la v3-C. Celle-ci gagne 12,4 points, démontrés, sur le jeu v2, lui aussi écrit par Claude. Elle recule en revanche sur le CDTN (−2,2) et sur le lot de test (−5,5), et laisse passer 5 questions hors corpus de plus ; la règle de l'amendement A3 l'écarte. Le gain tient au style des questions générées, pas à une meilleure recherche : aucun des deux n'est servi, l'ajusté reste celui du site.
- **La fusion avec BM25 n'a pas été portée sur le site.** La règle de la famille A du protocole 10 la permettait (+5,0 points sur le jeu v2, +2,6 sur le CDTN), mais aucun gain n'est démontré et les questions humaines vont en sens inverse (−6,8). L'équipe y a renoncé (#173).
- **Le contrôle a priori a tenu.** Le protocole d'évaluation du notebook 03 a été figé, avec son empreinte, avant la mesure unique du 13 octobre, et la règle de repli de l'encodeur ajusté avait été écrite d'avance. Les deux décisions qui en découlent, le verdict du critère du J2 et le choix de l'encodeur servi, résultent de l'application de règles fixées avant les résultats.

### 2.4 Pourquoi 10 passages au lieu de 5

La chaîne du volet B donnait d'abord 5 passages au modèle, et le site du volet A en affichait 5. Depuis novembre, le modèle en reçoit 10, et le site en affiche 10, regroupés par fiche. La raison est simple : plus de passages pertinents entrent dans le contexte avec 10 passages qu'avec 5.

**Comment le choix a été fait.** Le 9 novembre, la grille de réglage de la récupération (#138) a montré que le nombre de passages était le levier le plus fort. Sur le jeu CDTN, avec l'E5 de base, un passage pertinent figure dans le contexte pour 70,9 % des questions avec 5 passages, et pour 77,6 % avec 10. La règle de choix initiale, qui maximisait ce rappel, aurait toujours retenu le plus grand nombre de la grille, 15. L'amendement A1 a donc fixé k = 10 d'avance, avant la lecture des résultats des reclasseurs, pour deux raisons :
- **le budget du prompt** : 5 101 tokens au plus sur le CDTN, pour un plafond de 7 616 ;
- **l'écart à l'entraînement** de l'adaptateur, fait sur des contextes de 5 passages.

**Ce que les mesures confirment.** À récupération égale, passer de 5 à 10 passages ne retire aucun passage pertinent : il en ajoute.

| Un passage pertinent dans le contexte, 5 puis 10 passages | Jeu v2 (121 questions) | Lot de test (73) | CDTN (82 requêtes) |
|---|---|---|---|
| E5 de base | 57,0 % puis 66,1 % | 45,2 % puis 58,9 % | 70,9 % puis 77,6 % |
| Fusion avec BM25, sans reclasseur | 66,9 % puis 76,9 % | 57,5 % puis 68,5 % | 70,7 % puis 83,5 % |
| Fusion et reclasseur bge-m3 (chaîne retenue) | 81,0 % puis 86,0 % | 68,5 % puis 72,6 % | 78,5 % puis 85,1 % |

Le gain va de 4 à 14 points selon le jeu et la méthode. Il est plus faible après le reclasseur, qui remonte déjà les bons passages dans les 5 premiers.

**Ce qu'il coûte.**
- **Longueur du prompt** : 3 953 tokens en moyenne contre 2 179 à 5 passages, pour la chaîne retenue sur le CDTN, donc une lecture plus longue par le modèle.
- **Précision du contexte** : la part des passages fournis qui sont pertinents passe de 31,4 % à 23,4 %. Le modèle doit écarter plus de passages hors sujet.
- **Pourquoi pas 15** : l'E5 de base y atteint 85,9 % sur le CDTN, mais avec 4 805 tokens en moyenne et 6 889 au plus, près du plafond. La fusion et le reclasseur atteignent un rappel voisin, 85,1 %, avec 10 passages.

**Volet A.** Afficher 10 passages au lieu de 5, regroupés par fiche, fait gagner 6,8 points au rappel à la fiche sur le lot de test (5 questions gagnées, aucune perdue), au prix de 4,0 fiches à lire en moyenne au lieu de 2,4.

Sources : commentaire de l'amendement A1 sur le #138 ; `docs/etudes/evaluation/10_resultats.md`, section 8 ; `docs/etudes/evaluation/05_resultats_ajustement.md`, section 4.

### 2.5 Volet B : ce que les mesures ont montré

**L'adaptation, mesurée le 11 novembre** (protocole 06, chaîne B2, lot de test, modèle adapté contre témoin T, intervalles à 97,5 %) :
- **Réponses citant un passage pertinent (M4)** : 18 sur 72 contre 10 sur 72, soit +11,1 points [+2,1 ; +23,8]. Huit questions gagnent une citation pertinente, aucune n'en perd : l'amélioration est démontrée selon la règle prévue.
- **Abstention correcte hors corpus (M1)** : 20 sur 24 dans les deux cas ; aucune amélioration démontrée.
- **Abstention à tort sur le corpus (M2, descriptif)** : de 70,8 % à 55,6 %. Plus de la moitié des questions du corpus reçoivent encore une abstention.
- **Une citation pertinente ne prouve pas l'exactitude** de toute la réponse. Jugées à l'aveugle par deux membres (#52, 20 réponses citées par modèle, chaîne B2), les réponses du modèle adapté sont mieux appuyées sur leurs passages : entièrement appuyées pour 20 et 19 sur 20, contre 11 et 12 pour T, un écart démontré chez les deux juges. Elles ne sont pas plus exactes : entièrement exactes pour 6 et 5 sur 20, contre 12 et 8, un écart non démontré. L'accord entre les juges reste faible (kappa de 0,36 sur l'exactitude). Les défauts diffèrent : réponses incomplètes pour le modèle adapté, entraîné à recopier un passage ; généralisations et confusions pour T.

**La récupération v2** (#138, protocole 07, confirmée une fois sur le lot de test le 9 novembre) fait passer de 45,2 % à 72,6 % les questions dont le contexte contient un passage pertinent. Sur le jeu v2, de 57,0 % à 86,0 % (+28,9 points [+20,5 ; +38,0]).

**Ce qui n'a pas été retenu, par des règles écrites d'avance.**
- **La chaîne v2 complète** (#163, protocole 08) : nouvelle consigne et abstention décidée par le reclasseur. Elle donne plus de réponses citant un passage pertinent (27 sur 73 contre 18 sur 72), mais s'abstient sur 18 questions hors corpus sur 24 au lieu de 20, une de plus que la tolérance.
- **L'encodeur ajusté dans la récupération du volet B** (protocole 10) : 84,3 % contre 86,0 % sur le jeu v2, et 84,6 % contre 85,1 % sur le CDTN. Son avantage en recherche dense seule ne survit pas à la fusion avec BM25 et au reclasseur.

**Ce qui est servi en démonstration** : le modèle adapté, avec la récupération v2 et la consigne v1, sans seuil (PR #175). Sur le lot de test, cette récupération avec le seuil S (état V1 du protocole 08) donne 24 réponses citant un passage pertinent sur 73, et 20 abstentions correctes sur 24.

**La chaîne de démonstration, mesurée de bout en bout le 21 novembre** (protocole 10, jeu v2) :
- **Réponses citant un passage pertinent (M4)** : 52,9 % (63 sur 119). Sur les 118 questions communes, 52,5 % contre 35,6 % pour l'ancienne chaîne B2, soit +16,9 points [+6,4 ; +27,3] (31 questions gagnées, 11 perdues, p = 0,003) : le gain est démontré.
- **Abstention correcte hors corpus (M1)** : 39 sur 39 questions évaluées, contre 38 avec B2 ; la garde de la règle est respectée. Ces questions sont hors corpus au sens du protocole : un juge d'IA n'a trouvé de réponse dans aucun des 10 premiers passages d'une recherche hybride, ce qui ne prouve pas l'absence de réponse dans tout le corpus.
- **Effet de l'adaptation** : avec le modèle d'origine (témoin T), la même chaîne ne cite un passage pertinent que pour 10,1 % des questions (54 gagnées par l'adaptation, 3 perdues).
- **Prix** : 11,8 s par question en médiane, contre 4,9 s pour B2, à cause des 10 passages et du reclasseur.

## 3. Retour d'expérience

Cette partie porte sur la conduite du projet. Les faits ci-dessous sont communs et recoupés avec le dépôt ; les analyses personnelles figurent dans la section 4.

### 3.1 Méthodologie

**Organisation et décisions.** Les rôles ont été fixés à la réunion de cadrage du 19 septembre :
- Mahé, responsable technique et tenue du journal d'usage de l'IA ;
- Jibril, gestion du board, du classeur de suivi et des comptes rendus ;
- cinq domaines, chacun avec une personne principale et un soutien.

| Domaine | Principal | Soutien |
|---|---|---|
| D1, corpus et segmentation | Maïmouna, Vaneck | Jibril |
| D2, encodeur et index | Remy | Mahé |
| D3, front et déploiement du volet A | Maïmouna, Vaneck | Remy, Mahé |
| D4, socle RAG et inférence locale | Jibril | Remy |
| D5, adaptation et évaluation du volet B | Mahé | Jibril |

Les décisions se prennent en Weekly. Quand un compte rendu ne rapporte pas d'arbitrage, le responsable technique consigne les décisions par écrit dans le ticket (Weekly 4), ou les arrête après la séance en indiquant qu'elles restent discutables (Weekly 5). Les mesures ont été encadrées par des protocoles figés avant toute mesure (notebook 03, protocole 05), avec leur empreinte.

**Questions de test et jugements produits par l'IA.** Le lot de test humain (73 questions du corpus, 24 hors corpus) avait été lu par plus de six mesures en novembre : toute nouvelle comparaison y devenait descriptive. Faute de temps pour écrire un nouveau jeu humain avant cette V1, l'équipe a fait générer un jeu v2 par des sous-agents Claude indépendants, sur autorisation écrite de l'enseignant du 17 novembre (le courriel est conservé par Mahé). Le cadre est celui du protocole 10, figé avant toute génération :
- **Questions** : 121 questions du corpus, deux par fiche sur les 61 fiches du lot de test, exclues de tout entraînement, et 40 questions hors corpus vérifiées. Chaque question a passé des contrôles mécaniques et un juge de contrôle d'un autre modèle.
- **Jugements** : l'étalonnage du jugement mutualisé du #139 a été confié à deux juges d'IA d'autres modèles. Leur accord ne remplace pas un jugement humain, et il est présenté comme tel.
- **Limites déclarées** : un générateur qui part d'un passage en reprend un peu plus les mots (indice de Jaccard médian 0,111 contre 0,095 pour les questions humaines), ce qui avantage BM25. Le jeu humain v1 et le CDTN, écrits sans IA, restent les contrôles.

Cet usage s'écarte de la règle que l'équipe s'était donnée, qui réservait la génération par IA aux paires d'entraînement ; il est consigné dans le journal d'usage de l'IA (section 1 et session 68).

**Paires d'entraînement écrites par l'IA, sous registre.** Les 2 420 paires de la v3-C ont été écrites par des sous-agents Claude Sonnet, ce que la règle d'équipe permet, et relues par deux juges Claude Opus. L'amendement A3, audité trois fois par un sous-agent Claude Opus indépendant, a été figé avant toute génération. Chaque appel a été inscrit à un registre chaîné avant d'être lancé, et son journal contrôlé : consigne exacte, modèle exact, aucun outil autre que la lecture du fichier remis. Deux lots non conformes ont été relancés une fois, comme prévu (journal d'usage de l'IA, session 69).

**Réunions.** Six réunions sont documentées entre le 14 septembre et le 14 octobre, en général une par semaine :

| Date | Réunion | Compte rendu |
|---|---|---|
| 14/09 | Weekly 1, #2 | lancement et lecture du sujet ; présence non documentée |
| 19/09 | Weekly 2, cadrage, #6 | complet : cas A3 et B1, corpus, modèles, domaines ; support versé |
| 23/09 | réunion d'avancement, #26 | complet : cinq actions, responsables et échéances |
| 30/09 | Weekly 3, #9 | resté au stade du modèle : décisions non renseignées |
| 07/10 | Weekly 4, #10 | décisions consignées en commentaire par le responsable technique |
| 14/10 | Weekly 5, #11 | partiel : avancement rapporté, présents non renseignés ; décisions arrêtées après la séance |

**Supports de documentation.** Le dépôt réunit plusieurs types de documents :
- une étude par étape de la chaîne (découpage, indexation, évaluation, allègement, ajustement, inférence locale) ;
- les protocoles et l'audit statistique de l'évaluation ;
- le classeur de suivi, le journal d'usage de l'IA et une fiche par outil ;
- les rapports de jalon.

Leur utilité constatée est surtout de deux ordres :
- **Décider sans débat a posteriori** : les protocoles figés ont permis d'appliquer la règle de repli.
- **Rattraper des erreurs** : le journal recense 196 erreurs ou pièges détectés par la vérification au 26 novembre (68 au 18 octobre, dont 32 du 11 au 18 octobre).

Les PDF sont produits depuis le Markdown par une chaîne LaTeX commune (`docs/latex`).

### 3.2 Outillage

**Dépôt Git.**
- **Branches** : `main` reçoit l'état livrable, `dev` l'intégration (le site est déployé depuis `dev`), et chaque ticket a sa branche `feat/`, `fix/` ou `docs/` suivie de son numéro.
- **Jalons** : ils sont marqués par des tags annotés (`jalon-j2`, `jeu-questions-v1`, `mi-parcours`, `volet-a-v1`) et une branche d'observation (`observation/mi-parcours`).
- **Protection** : `dev` et `main` exigent depuis le 10 octobre une approbation, y compris pour les administrateurs, et un nouveau commit annule les approbations antérieures.

| Indicateur, au 19 octobre | Valeur |
|---|---|
| Pull requests | 50 : 42 fusionnées, 6 ouvertes, 2 fermées sans fusion |
| Fusionnées avec l'approbation d'un autre membre | 34 sur 42 |
| Revues déposées | 61 : 38 approbations en vigueur, 6 demandes de modification, 11 commentaires, 6 revues annulées par un commit ultérieur |
| Commits hors fusion sur `dev` | 174 ; 173 suivent le format `type(portée): sujet` (99 %) |

Les 8 PR fusionnées sans approbation enregistrée se répartissent ainsi :
- cinq, le 6 octobre (#54, #55, #58, #59, #60), avant la mise en place de la protection ;
- une dans une branche de travail (#40) ;
- une après une demande de modification traitée, sans approbation formelle (#32) ;
- une intégrée par une autre PR approuvée (#86, par la #87).

**Board de tickets.** Le board porte l'état des tickets ; le classeur de suivi le complète par les dates et les charges.

Le pilotage a été réel pour la création des tickets, mais rétrospectif pour les charges :
- **Création préalable** : les 54 tickets ont été créés par vagues de planification (19 le 20/09, 6 le 23/09, 11 le 30/09, 8 le 18/10). Les 25 PR qui citent un ticket dans leur titre ont toutes été ouvertes après la création de ce ticket.
- **Charges rétrospectives** : au 19 octobre, 45 tickets sur 54 n'ont pas d'estimation dans le classeur de suivi.
- **Capture absente** : la capture du board attendue au mi-parcours n'a pas été versionnée.

**Relecture par un tiers.** La relecture croisée a trouvé des erreurs que l'auteur n'avait pas vues. Sur les 19 erreurs des sessions de Mahé entre le 11 et le 18 octobre, 4 ont été trouvées par Jibril en relecture. Vaneck en a relevé deux dans des PR de Mahé (#76 et #78). Les revues de Jibril sur les PR documentaires (#82, #89, #102) ont vérifié les chiffres contre l'API GitHub et contre le rendu du PDF.

**Assistants d'IA.** Leur usage est consigné session par session : 73 sessions au 26 novembre. Les outils déclarés sont Claude Code, Google Antigravity avec Gemini, ChatGPT et Codex, Qwen Coder en local, et, comme sous-agents de Claude Code, d'autres modèles Claude (Sonnet, Fable et Haiku) pour écrire et juger des questions sous protocole (sessions 68 et 69). La règle d'équipe est que tout élément produit avec un assistant soit relu et vérifié par une mesure avant d'être publié. La section 5 en fait le bilan critique.

### 3.3 Difficultés

**Techniques.** Les principales, avec leur résolution :
- **Taille du modèle** : le q8 de 112,8 Mio dépassait la limite de 100 Mio par fichier de GitHub. Résolu par l'élagage sans perte.
- **Écart navigateur et Python** : le q8 du navigateur ne donne pas les mêmes résultats que celui de Python. Résolu en mesurant dans le navigateur.
- **CDN caché** : le moteur d'exécution venait de jsDelivr. Résolu en le servant depuis le site.
- **Reproductibilité entre machines** : l'index reconstruit sous Windows diffère de celui de macOS. Le site garde l'index de référence, vérifié par empreinte.
- **Tabulation sous Safari** : résolu en gérant entièrement Tab dans le menu.
- **Mesure de l'encodeur ajusté (#49)** : non faite avant l'échéance. La règle de repli s'est appliquée.

**Organisationnelles et de disponibilité.**
- **Calendrier non confirmé** : les dates du sujet et celles annoncées oralement divergent, et le calendrier n'est pas confirmé par écrit (#8). L'équipe s'est fixé le 18 octobre pour clore le volet A.
- **Journal en retard** : plusieurs sessions du journal ont été consignées a posteriori (22 à 25, 28 à 31, 33, 34 et 36), à partir des commits et des tickets, alors que la règle est de consigner le jour même.
- **Comptes rendus incomplets** : deux comptes rendus de Weekly sont restés incomplets (#9, #11).
- **Pièges d'intégration** : changer la base d'une PR annule ses approbations (#78), et une PR ouverte vers `main` au lieu de `dev` est entrée en conflit avec `dev` (#86). Les deux ont coûté des relectures supplémentaires.

**Écarts entre charge estimée et charge réelle.** Seuls 4 tickets ont à la fois une estimation et une charge réelle :

| Ticket | Estimé | Réel | Écart |
|---|---|---|---|
| #27, corpus | 8 h | 10 h | +2 h |
| #29, première page en ligne | 3 h | 1 h 30 | −1 h 30 |
| #45, validation des métriques | 4 h | 3 h 30 | −30 min |
| #47, références TF-IDF et BM25 | 4 h | 3 h 30 | −30 min |

Le seul dépassement (#27) est attribué au mauvais découpage du corpus source, repris ensuite (#35). L'échantillon est trop petit pour analyser les causes de sous-estimation. La cause principale est en amont : les estimations n'ont pas été saisies avant le travail, et une charge réelle ne se reconstitue pas après coup. C'est la lacune de méthode la plus nette du projet à ce stade.

**Charges déclarées après coup.** Les 22 et 23 novembre, des parts individuelles ont été ajoutées au classeur de suivi (PR #182 et #169) : Vaneck, 68 h sur 10 tickets, dont 24 h pour la démonstration du volet B (#111) et 10 h pour l'interface du volet A (#53) ; Remy, 14 h sur l'ajustement de l'encodeur (#49) ; Jibril, environ 21 h sur Agent0 (#91 à #95), en estimations rétrospectives non chronométrées. Ce sont des parts individuelles, sans estimation initiale comparable : elles documentent l'effort, mais ne permettent pas d'élargir l'analyse des écarts.

### 3.4 Enseignements

Propositions communes, à discuter en équipe avant la V1 :
- **Estimer avant de commencer**, dans le ticket, et saisir la charge réelle à la fermeture : c'est la seule façon de produire l'analyse des écarts que demande le sujet.
- **Consigner le jour même** les sessions d'usage de l'IA et les comptes rendus, pendant la réunion.
- **Garder les protocoles figés et les règles de repli écrites d'avance** : ils ont permis de décider sans biais et à l'heure.
- **Mesurer dans les conditions réelles et sur plusieurs plateformes** dès le premier prototype : navigateurs, systèmes, réseau bloqué.
- **Ne pas juger un modèle entraîné sur des données générées avec un jeu écrit par le même type de générateur** : la v3-C n'était meilleure que sur les questions de Claude. Un jeu humain, même petit, reste le contrôle indispensable.
- **Automatiser les contrôles** : depuis le 19 octobre, les tests du moteur passent avant chaque déploiement, et un écart de version d'une dépendance arrête la mise en ligne. Ce garde-fou aurait dû exister dès le premier déploiement.

## 4. Axes de progression

Le sujet recommande une rédaction individuelle. Chaque membre complète son encadré : compétences techniques acquises, lacunes et points à approfondir, puis positionnement dans l'équipe, délégation, demandes d'aide, arbitrages, délais.

### 4.1 Mahé BEGNIS

**Compétences techniques acquises.**
- **Mesurer avant de décider** : écrire et figer chaque protocole avant la mesure, avec son empreinte publiée (protocoles 05 à 10, amendements A1 à A3) ; comparer deux systèmes sur les mêmes questions par des tests appariés (McNemar exact, test groupé d'Obuchowski quand plusieurs questions partagent une fiche), avec des intervalles de Tango et une correction de Holm ; appliquer la règle écrite d'avance, y compris quand elle fait renoncer (repli du 16 octobre, chaîne v2 du volet B, v3-C).
- **Servir un modèle dans le navigateur** : quantification q8, élagage sans perte du vocabulaire (de 112,8 à 65,7 Mio, #50), contrôle de parité entre Python et le navigateur sur 822 vecteurs.
- **Adapter et servir un modèle génératif en local** : adaptateur LoRA entraîné sous MLX, fusion dans les poids, export GGUF et Q4_K_M avec un contrôle de requantification (#140), service par Ollama sur 127.0.0.1.
- **Récupération hybride** : fusion RRF de la recherche dense et de BM25, reclasseur, budget de tokens du contexte (protocole 07).
- **Encadrer des sous-agents d'IA** : générateurs et juges à contexte neuf, consignes publiées, registre chaîné et journaux contrôlés (protocole 10, amendement A3).

**Lacunes et points à approfondir.**
- **Comprendre tout le code produit à mon nom** : presque tout mon travail est passé par Claude Code (30 sessions consignées). Une partie de ce code, je la connais par ses tests plus que par sa lecture ligne à ligne ; c'est ce que je dois combler avant la soutenance, où chacun peut être interrogé sur n'importe quelle portion du code.
- **Vérifier plus tôt** : 11 des 19 erreurs de mes sessions du 11 au 18 octobre figuraient déjà dans une PR, une revue ou un document publiés. Le 21 novembre encore, un test est resté en échec jusqu'au lendemain, faute d'avoir relancé toute la suite après un commit : je dois relancer tous les tests après chaque commit, pas seulement ceux du changement.
- **Concevoir les échantillons de contrôle** : l'étalonnage du jugement mutualisé (#139) n'a pas pu conclure sur la règle principale, faute d'un échantillon stratifié selon les verdicts.
- **Estimer la charge** : aucun des tickets dont j'étais responsable en novembre n'a reçu d'estimation chiffrée avant son démarrage. C'est en partie pour cela que l'analyse des écarts (section 3.3) repose sur 4 tickets.

**Positionnement dans l'équipe, délégation et délais.**
- **Rôle de lead technique** : protocoles, mesures et revues de PR, et règles du dépôt (branches protégées, une approbation exigée avant toute fusion). Quand les Weekly 7 et 8 n'ont pas eu lieu en réunion, j'ai pris les décisions par écrit dans les tickets, en les déclarant comme décisions du lead, révisables par l'équipe.
- **Trop de travail concentré** : une grande partie du travail technique est passée par moi et par l'assistant. C'est efficace, mais fragile : la démonstration du volet B tourne sur mon Mac, et mes coéquipiers ont fini le projet plus souvent comme relecteurs que comme auteurs. J'aurais dû déléguer plus tôt des parties entières, avec leur mesure.
- **Demander des relectures** : elles ont rattrapé ce que l'assistant et moi avions laissé passer, par exemple les deux garde-fous et l'incohérence documentaire relevés par Jibril sur la PR #166.
- **Délais** : le jalon J3 a été tenu. La V1 du rapport, prévue le 19 novembre, ne l'a pas été : j'ai fait passer de nouvelles mesures avant la rédaction (encodeurs v2-T et v3-C, mesure de bout en bout).

### 4.2 Remy RAYANE

**Compétences techniques acquises.**
- **Architecture d'indexation vectorielle et contraintes Web** : conception et découpage de l'index en format binaire Little-Endian Float32 (`piaf_reduced_index.bin`) et métadonnées JSON (#30), puis intégration de l'index de production `index_m2.f32` (4 240 passages, 6,21 Mio) chargé via l'API `TypedArray` (`Float32Array`) sans blocage de l'interface par `JSON.parse()`. Exploitation de la normalisation L2 pour ramener la similarité cosinus à un produit scalaire en O(d) vectorisable en WebAssembly / SIMD, et respect strict de l'asymétrie d'encodage E5 (`query: ` vs `passage: `) pour prévenir la dégradation du Recall@k.
- **Évaluation quantitative en recherche d'information (IR)** : mise en place de la chaîne de métriques sur PIAF (#45) et de références lexicales TF-IDF et BM25 (#47) afin d'objectiver les écarts entre recherche dense et approches par mots-clés (notamment la variante BM25 V3 à racinisation française conservant les négations juridiques, reprise dans la récupération hybride du volet B, #138 / PR #141).
- **Apprentissage contrastif et adaptation d'encodeur** : fine-tuning de `multilingual-e5-small` avec perte contrastive (`MultipleNegativesRankingLoss`) sur 109 paires hors fiches de test (#49, PR #63), avec cloisonnement au niveau des fiches et filtre lexical Jaccard.
- **Portabilité ONNX et quantification INT8** : diagnostic de la divergence arithmétique entre Python et WebAssembly (Transformers.js), puis alignement par quantification symétrique (`ActivationSymmetric`) rétablissant 74 tenseurs sur 75 bit à bit à Xenova sur le témoin et portant la fidélité in-browser de l'ajusté à 93,55 % (769/822 concordances), avec un modèle témoin isolant l'effet de graphe opset 14 (112,9 Mio sur nos exports ; l'élagage sans perte à 65,7 Mio sur la base Xenova a ensuite été conçu et livré par Mahé en #50 / PR #78).
- **Débogage de runtime et contrôles locaux** : identification du cache réel de Transformers.js via l'API Cache (`caches.delete` sur `transformers-cache`, et non IndexedDB), sécurisation des chemins dans `serveur_controle.py`, diagnostic de sérialisation du tokeniseur Unigram sous `transformers` 5.18, et vérification du refus d'adaptateur LoRA (`errAdaptersUnsupported`) dans Ollama `v0.40.5` (#107, session 45).

**Lacunes et points à approfondir.**
- **Vérification factuelle des productions assistées par IA** : entre le 27 octobre et le 10 novembre, plusieurs erreurs factuelles ou de méthode ont dû être corrigées après revue humaine — numérotation et bilan de section 4 dans la PR #120 (session 45), perte des accents lors d'une réécriture complète (#134), puis en première version des fiches d'outils (#135) : mention d'`uv 0.4.29` alors que `uv` est absent de mon poste, attribution erronée de l'élagage de la PR #78, version d'Ollama non alignée sur l'épinglage officiel `0.40.13` (mon démon local ayant dérivé en mise à jour automatique vers `0.40.15`), et statut fermé attribué à tort au ticket #49. J'ai encore à systématiser la vérification locale de chaque version, script, attribution et statut avant publication.
- **Métrologie et garde-fous des modèles génératifs (Volet B)** : la prise en main de l'inférence locale Qwen 2.5 (#31) et la relecture de la chaîne RAG et de sa récupération v2 (#138, PR #141) ont montré que le contrôle automatique des citations (`[P1]`) porte uniquement sur la syntaxe des identifiants et ne garantit pas la justification sémantique des affirmations ; l'évaluation des réponses reste plus délicate à borner que les métriques déterministes d'embeddings.
- **Portabilité Windows des environnements et tests** : les écarts rencontrés sous Windows 11 — absence de Perl pour `latexmk`, syntaxe PowerShell incompatible avec certains scripts POSIX, variations d'arrondis CPU Python par rapport à macOS, et erreur de privilèges `WinError 1314` sur `os.symlink` relevée lors de l'exécution locale de `test_export.py` (#140, PR #147) — montrent le besoin d'anticiper les contraintes système dans nos suites de tests.
- **Optimisation bas niveau et WebGPU** : le travail est resté centré sur le CPU et WebAssembly ; l'exploitation de WebGPU constitue un prolongement technique à explorer.

**Positionnement dans l'équipe, délégation et demandes d'aide.**
- **Binôme D2 avec Mahé et coresponsabilité sur #107** : rôle principal sur l'indexation binaire, les références lexicales et l'apprentissage contrastif (#30, #45, #47, #49), en m'appuyant sur les revues exigeantes de Mahé sur les protocoles de mesure et les tests statistiques ; reprise des corrections demandées sur les supports J3 (#112 / PR #134) et les fiches d'outils (#113 / PR #135).
- **Soutien transverse sur D4 et D3** : accompagnement de Jibril sur l'inférence locale (#31) et l'intégration des passages M2 (#51), appui à l'équipe front sur la consommation des index, et contributions aux livrables communs (#105, #112, #113).
- **Relectures et transparence** : pratique des revues croisées (PR #61, #62, #73, #75, #109, #115 et #124), puis préparations des vérifications de J3 pour #141 (19/19 tests unitaires réussis), #147 (8/9 sous Windows) et la diapositive 7 de #148, en signalant les anomalies observées au fil de l'eau (cache navigateur, divergence tokeniseur, audits de la session 35).

**Arbitrages et respect des délais.**
- **Application de la règle de repli du protocole 05 et maintien de #49 ouvert** : déploiement de l'encodeur de base élagué (65,7 Mio) pour l'échéance du 18 octobre faute de mesure officielle complète avant le 16 octobre, puis acceptation le 30 octobre de la priorité donnée au volet B dans le calendrier resserré, tout en conservant le ticket **#49 ouvert** sans prétendre à une validation qui n'a pas eu lieu.
- **Estimations, réactivité et rattrapage avant J3** : tenue des charges sur les tâches estimées et clôturées (#45 et #47 à 3 h 30 pour 4 h estimées), mais retards de réponse fin octobre sur les retours de #112 et #115 et dette sur les fiches d'outils ; ces écarts ont été traités le 10 novembre par la reprise complète des demandes de revue de la PR #134 (préparée pour une fusion en squash) et la correction intégrale des fiches de la PR #135.

### 4.3 Jibril BENSALEM

**Compétences techniques acquises.** J’ai progressé dans la compréhension et la mise en œuvre d’une chaîne RAG : exécuter Qwen localement, récupérer les passages pertinents, construire le contexte et contrôler les citations. Le développement d’Agent0 Light m’a aussi permis de travailler sur la génération de questions synthétiques et la traçabilité des essais. Les relectures m’ont appris à confronter les affirmations aux résultats observés : un test réussi ou une citation existante ne garantit pas la qualité d’une réponse.

**Points à approfondir.** Je dois encore approfondir l’adaptation des modèles, les contraintes de mémoire GPU et l’évaluation des réponses générées. Je souhaite aussi gagner en autonomie dans la compréhension du code produit avec l’assistance de l’IA.

**Positionnement et organisation.** J’ai partagé mon travail entre le rôle de Scrum Master, les contributions techniques et les relectures. Un axe de progression concerne la régularité du suivi : consigner les décisions au fil de l’eau, renseigner les charges et mieux anticiper les dépendances entre tâches. Lorsqu’une réunion n’est pas nécessaire, un point écrit permet de conserver une visibilité commune sur l’avancement.

### 4.4 Vaneck DAGAR

**Compétences techniques acquises.** Avec Maïmouna, j'ai commencé par le corpus (#27). En le contrôlant, nous avons découvert que le jeu publié sur Hugging Face était mal découpé : le texte des fiches débordait d'une section sur l'autre et les intertitres étaient collés aux paragraphes. Nous avons donc refait le découpage à partir de la source officielle de SocialGouv sur GitHub, qui contient le texte complet de chaque fiche, section par section (#35). J'ai ensuite rédigé et annoté des questions pour l'évaluation (#44), puis je me suis surtout occupé de tout ce que voit l'utilisateur. Pour le volet A, j'ai mis le site en ligne sur GitHub Pages, branché la recherche dans l'interface de chat et repris le parcours et l'accessibilité (#29, #48, #53). J'ai appris à tester une interface autrement qu'en cliquant dessus : Playwright sur ordinateur et sur téléphone, Lighthouse pour le contraste, navigation au clavier. Ces tests m'ont fait trouver des défauts que je n'aurais jamais vus seul. Pour le volet B, j'ai écrit le contrat d'interface de la démonstration, puis l'interface et la couche Python qui la relie à la chaîne RAG (#121, #128). Les relectures sur cette couche m'ont rappelé qu'un code qui marche en usage normal doit aussi être éprouvé dans les cas limites.

**Lacunes et points à approfondir.** Je connais bien la partie applicative du volet B, beaucoup moins la partie modèle. Je n'ai ni Ollama ni Qwen sur ma machine, donc je n'ai jamais lancé la génération moi-même. J'ai compris la chaîne RAG en la relisant avec l'assistant, et l'adaptation comme la mesure ont été faites par d'autres. C'est le point que je dois le plus travailler. Je dois aussi être plus exigeant avec ce que produit l'assistant d'IA : quelques erreurs de mon travail ont été trouvées par Jibril ou Mahé en relecture, pas par moi.

**Positionnement dans l'équipe et délais.** J'ai porté le front des deux volets et la démonstration avec Maïmouna, et j'ai relu une quinzaine de PR des autres, parfois en les refaisant tourner sous Windows. Pour tout ce qui demandait le modèle, je dépendais des autres : c'est Maïmouna qui a fait le premier essai réel de la démo, et elle tournera sur la machine de Mahé. J'ai tenu les échéances de la démonstration et de la relecture des données d'adaptation, mais j'ai laissé glisser ce qui était moins technique : le scénario, cette section et ma fiche d'outil sont arrivés en retard.

### 4.5 Maïmouna SIGNATE

**Compétences techniques acquises.** Au volet A, avec Vaneck, j'ai travaillé sur la préparation du corpus (#27) : téléchargement d'une version figée, règles de filtrage, contrôle manuel d'un échantillon. J'ai aussi travaillé sur la mise en ligne du site (#29) et l'annotation de questions pour l'évaluation (#44, Q036 à Q070). Au volet B, j'ai appris à lire une chaîne RAG de bout en bout : la récupération des passages par E5, la génération par Qwen et le contrôle des citations. J'ai reproduit cette chaîne sur ma propre machine (#51). Mahé l'a retenue comme la reproduction indépendante du ticket, avec ses écarts déclarés : version d'Ollama et digest différents, calcul sans carte graphique. J'ai découvert à cette occasion comment faire tourner un modèle d'IA comme Qwen directement sur mon ordinateur, avec le logiciel Ollama, et vérifier qu'il s'agit bien du même modèle que celui de Jibril. J'ai surtout appris à juger une réponse en la comparant aux passages : une réponse citée peut être incomplète (Q036), et une abstention peut être injustifiée alors que le bon passage a été trouvé (Q001). Enfin, je me suis familiarisée avec Git et GitHub : branches, commits, résolution de conflits, relectures de pull requests.

**Lacunes et points à approfondir.** Au début du projet, j'avais du mal à voir comment les différentes parties s'articulaient, du corpus jusqu'à la démonstration. Pour y remédier, j'ai refait moi-même, dans des notebooks, la préparation du corpus et la recherche du site. La lecture du code Python et JavaScript reste un point à approfondir. J'ai aussi appris à ne pas prendre pour acquis ce que me dit l'assistant d'IA : plusieurs de ses affirmations se sont révélées fausses, et je ne les ai corrigées qu'en lui demandant de vérifier. Ces erreurs sont consignées dans le journal. Je souhaite prolonger ce travail dans mon entreprise, où presque tous les membres de l'équipe refont régulièrement les mêmes recherches : j'envisage d'y mettre en place une recherche par le sens sur nos documents, sur le modèle du volet A.

**Positionnement dans l'équipe et délais.** J'ai travaillé en binôme avec Vaneck sur le volet A (le corpus, la mise en ligne du site et l'évaluation), puis sur la vérification de la chaîne RAG et la démonstration du volet B. Sur les délais, mon journal a été rattrapé avec retard, et trois de mes sessions sont déclarées comme consignées a posteriori. Je retiens qu'il faut consigner le travail le jour même, tant que les difficultés sont encore en mémoire.

## 5. Cinq outils novateurs

**Cinq outils retenus le 10 novembre.** Le Weekly 8 (4 novembre), qui devait les choisir, n'a pas eu lieu. Mahé les a proposés par écrit le 30 octobre et retenus le 10 novembre, sans objection dans le ticket du Weekly 8 (#14) : c'est une décision écrite du lead, pas un vote. Ils répondent aux critères retenus par l'équipe :
- un usage réel et répété, avec des preuves dans le dépôt ;
- au moins une limite observée ;
- un retour que la documentation officielle ne donne pas.

Chaque fiche complète figure dans `docs/suivi/outils/`. Les autres candidats sont Ollama, Sentence Transformers, GitHub Actions et Pages, Vite et `uv`.

### 5.1 Transformers.js

- **Usage.** Exécution de l'encodeur dans le navigateur, pour le site et pour les pages de contrôle (PR #40, #62, #67).
- **Apport.** Une recherche sémantique sans serveur, en une vingtaine de millisecondes par question.
- **Limite.** Le poids du modèle au premier chargement, que l'élagage a réduit de 42 %.
- **Ce que la documentation ne dit pas.** La précision par défaut change selon le matériel, et l'extracteur ne fait ni moyenne ni normalisation par défaut : sans options explicites, il renvoie un vecteur par token.
- **Ce que la documentation ne dit pas non plus.** À son import, la bibliothèque fait télécharger son moteur d'exécution depuis jsDelivr.

### 5.2 ONNX Runtime, en Python et sur le Web

- **Usage.** Même fichier de modèle exécuté en Python pour construire l'index, et dans le navigateur pour le site (notebook 02, PR #40 et #81).
- **Apport.** Un format unique entre la préparation et le service.
- **Limite.** Un modèle quantifié ne se comporte pas de la même façon d'un environnement d'exécution à l'autre : critère de parité q8 échoué, puis diagnostiqué.
- **Ce que la documentation ne dit pas.** L'ampleur de l'écart entre le q8 de Python et celui du navigateur : 96,5 % contre 91,8 % de premier résultat identique au calcul exact.

### 5.3 Playwright

- **Usage.** Mesures de faisabilité du J2, parcours complets du site, contrôles d'accessibilité au clavier, essais avec réseau bloqué, sous Chromium, Firefox et WebKit.
- **Apport.** Rejouer en quelques minutes le parcours complet du site, erreurs réseau comprises.
- **Limite.** Écouter les requêtes au niveau de la page ne montre pas celles du moteur d'exécution ; il faut les écouter au niveau du contexte.
- **Limite.** Sous WebKit, l'interception du réseau capte aussi les URL `blob:` ; les bloquer par erreur fait échouer le site.
- **Limite.** Le comportement de WebKit dépend du système : le défaut de tabulation se reproduit sous macOS, pas sous Linux.
- **Ce que la documentation ne dit pas.** `playwright-core` ne télécharge aucun navigateur : il pilote ceux qui sont déjà installés.

### 5.4 GitHub CLI

- **Usage.** Toutes les opérations GitHub courantes : PR, revues, tickets, réglages et lectures de l'API, y compris pour les audits de ce rapport.
- **Apport.** Des opérations reproductibles et scriptables, y compris les réglages absents de l'interface en ligne de commande, par `gh api`.
- **Limite.** `gh api` bascule silencieusement de GET en POST dès qu'un champ `-f` est fourni.
- **Ce que la documentation ne dit pas clairement.** Les droits réels exigés par certains réglages : l'environnement `github-pages` est réservé aux administrateurs, et la lecture du board (Projects v2) exige un droit absent du jeton par défaut.

### 5.5 Assistants de développement par IA

- **Usage.** Claude Code, Google Antigravity avec Gemini, ChatGPT et Codex, Qwen Coder en local, sur l'ensemble du projet : 73 sessions consignées au 26 novembre. En fin de projet, des sous-agents Claude ont aussi écrit le jeu de test v2 et les paires d'entraînement de la v3-C, sous un protocole figé d'avance.
- **Apport.** Une capacité de production et de mesure qui a rendu possible le périmètre du projet.
- **Critique argumentée.** L'assistant produit des affirmations plausibles et fausses, y compris dans des documents publiés. Le journal recense 196 erreurs ou pièges détectés par la vérification au 26 novembre (68 au 18 octobre). Sur les 19 erreurs des sessions de Mahé du 11 au 18 octobre, 11 figuraient déjà dans une PR, une revue ou un document publiés. Deux exemples : une revue affirmant qu'aucune requête ne partait vers jsDelivr, et une description de PR affirmant que le focus ne sortait jamais du menu. Ces erreurs ont été trouvées par une mesure, un essai, une revue ou la lecture d'une source primaire, et 4 d'entre elles par un relecteur de l'équipe, non par l'assistant. L'assistant ne dispense donc ni de la vérification, ni de la compréhension du code : le sujet rappelle que tout membre peut être interrogé sur n'importe quelle portion du code produit.
- **Ce que la documentation ne dit pas.** La vérification doit être conçue pour échouer quand l'affirmation est fausse. Les essais qui ont laissé passer les erreurs ci-dessus étaient trop permissifs : requêtes écoutées au mauvais niveau, focus sur le document jugé acceptable.

## 6. Ce qui reste avant la V1

État au 26 novembre. La mesure de bout en bout de la chaîne de démonstration (section 2.5), la mesure des encodeurs v2-T et v3-C (section 2.3), l'analyse à deux juges de l'exactitude (#52, sections 2.2 et 2.5), les sections 4 et 5 sont faites. Les fiches des outils sont complètes : chaque membre y a sa ligne et sa décision. Les PR #158, #161, #162, #166, #168, #169, #174, #175, #178, #179, #181, #183 et #184 sont fusionnées ; les #180, #185 et #186 l'ont été avec la #178. L'échéance du 19 novembre pour la V1 n'a pas été tenue.

| Élément | Responsables | Échéance |
|---|---|---|
| Approbation et fusion de la PR #177 (logo et confidentialité), puis contrôle du site déployé | Jibril ou Remy ; Mahé | 27/11 |
| Approbation et fusion de la PR #187 (charges de Maïmouna), puis ajout à la section 3.3 | Mahé | 27/11 |
| Capture du board, absente à ce jour | Jibril | 27/11 |
| PR de `dev` vers `main` et tag final | Mahé | 28/11 |
| Relecture croisée de cette version, PDF régénéré, livraison de la V1 | Mahé (coordination), toute l'équipe | 28/11 |

## Annexe. Chiffres et sources

| Chiffre | Source dans le dépôt |
|---|---|
| 261 fiches, 4 240 passages, instantané du 11/09/2026 | `front/public/index/`, `docs/etudes/decoupage/01_corpus_decoupage.md` |
| q8 de 112,8 à 65,7 Mio, 822 vecteurs identiques bit à bit | `scripts/allegement/README.md` |
| table des mots : 81,6 % des paramètres, 250 037 lignes | `docs/etudes/indexation/01_encodeur_e5_small.tex` |
| 91,8 % (navigateur) contre 96,5 % (Python) de premier résultat identique | `docs/etudes/indexation/02_indexation.md` |
| Recall@5, IC, non-infériorité, bonne fiche 83,6 %, AUC, seuil | `docs/etudes/evaluation/03_evaluation.md` |
| ajustement : 109 paires, 2 époques, 185,5 s | `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md` |
| volet B : 4,36 Gio, 37,7 s, 19,1 s, 47 à 67 tokens/s, VRAM | `docs/etudes/inference_locale_qwen.md` |
| chaîne RAG, Q036 et Q003 | PR #85 (fusionnée) ; `docs/etudes/rag_51.md` |
| 61,3 Mio, 20,1 s, 21 ms (19 à 24), 46 ms | mesure du site en ligne `7e2ce07`, le 19/10/2026, Chromium, profil neuf |
| rôles, domaines, réunions, charges | `docs/suivi/SUIVI.md`, `docs/reunions/README.md`, tickets #2, #6, #9, #10, #11, #26 |
| PR, revues, commits | API GitHub et `git log` de `dev`, relevés le 19/10/2026 |
| erreurs détectées | `docs/journal/JOURNAL_USAGE_IA.md`, section 4 |
| abstention de l'encodeur ajusté : AUC 0,865, 70 sur 73, 10 sur 24, 13 avertissements | `docs/etudes/evaluation/05_resultats_ajustement.md`, section 5 |
| chaîne de démonstration de bout en bout : 52,9 %, +16,9 points, 10,1 %, 11,8 s et 4,9 s | `docs/etudes/evaluation/10_resultats.md`, section 6 (PR #174) ; `data/evaluation/protocole_10/bout_en_bout_analyse_20261121T134041Z.json` |
| fusion du volet A : +5,0, +2,6 et −6,8 points | `10_resultats.md`, section 4 (PR #174) |
| encodeurs v2-T et v3-C : 2 289 et 2 420 paires, +12,4, −2,2 et −5,5 points | `10_resultats.md`, sections 7 et 7 bis (PR #174) ; `docs/etudes/evaluation/05_amendement_A2.md` et `05_amendement_A3.md` (PR #179, fusionnée) |
| exactitude jugée à l'aveugle : 6 et 5 sur 20 contre 12 et 8, 20 et 19 sur 20 contre 11 et 12, kappa 0,36 | #52, commentaire du 26 novembre ; grilles des juges et clé hors dépôt (`data/`) |
| confidentialité des deux interfaces | PR #177 : `front/src/composants/Confidentialite.jsx`, `demo_b/src/composants/Confidentialite.jsx` |
