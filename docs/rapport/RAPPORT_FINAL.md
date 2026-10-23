# Rapport du projet NLP 2

**Équipe** Data Tigers
**Membres** Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE
**Module** NLP 2, projet de fin de module
**Formation** Master 2 Data & IA, FGES, Université Catholique de Lille
**Année universitaire** 2026-2027
**Enseignant** Adrian ROSARI
**Version** V0 du 19 octobre 2026, à compléter jusqu'à la V1, à remettre strictement avant le jalon J4

**Objet.** Ce rapport suit la section 11 du sujet : analyse technique, retour d'expérience, axes de progression et cinq outils novateurs. Cette V0 est écrite à la fin du volet A. Elle rédige ce qui est déjà établi et signale explicitement ce qui reste à mesurer ou à rédiger, principalement le volet B et les axes de progression individuels.

**Sources.** Tous les chiffres proviennent du dépôt (`datatigersNLP/data_tigers_nlp`) : études, protocoles, mesures, classeur de suivi, journal d'usage de l'IA, historique Git et tickets GitHub. L'annexe relie chaque chiffre à sa source. Les mesures du site en ligne datées du 19 octobre 2026 ont été faites sur la version `7e2ce07`.

*Ce document a été produit avec l'assistance d'outils d'intelligence artificielle. Les usages sont consignés dans le journal prévu par le sujet ; chaque chiffre a été recoupé avec sa source avant publication.*

---

## 1. Le projet en bref

| Volet | Cas | Ce qui est livré |
|---|---|---|
| A, application en ligne | A3, recherche sémantique en corpus fermé | site public https://datatigersnlp.github.io/data_tigers_nlp/, inférence dans le navigateur, aucun serveur |
| B, application locale | B1, assistant réglementaire sourcé, avec abstention | chaîne RAG locale avec Qwen2.5-7B-Instruct, en cours (PR #85) |

Le corpus est commun : les 261 fiches pratiques du ministère du Travail, découpées en 4 240 passages, instantané SocialGouv du 11 septembre 2026, sous Licence Ouverte Etalab 2.0. Le cas A3 constitue la couche de récupération du cas B1 : le découpage, l'encodage et l'index sont écrits une fois et servent aux deux volets.

La fin du volet A est marquée par le tag annoté `volet-a-v1`, posé le 18 octobre 2026 sur `main` (`8955962`). Le site en ligne est déployé depuis `dev` ; il intègre depuis le 19 octobre deux changements postérieurs au tag (PR #88 et #102).

## 2. Analyse technique

### 2.1 Ce que chaque volet met en œuvre

| | Volet A | Volet B |
|---|---|---|
| Modèle | `multilingual-e5-small`, encodeur de phrases | `Qwen2.5-7B-Instruct`, modèle génératif |
| Forme servie | q8 (entiers sur 8 bits), vocabulaire élagué sans perte : 65,7 Mio | GGUF Q4_K_M : 4,36 Gio |
| Exécution | navigateur du visiteur, Transformers.js 4.3.0 et ONNX Runtime Web | PC portable, Ollama, GPU NVIDIA RTX 5070 Laptop (8 Gio de VRAM) |
| Sortie | 5 passages réels, ordonnés, avec score, section et lien | réponse rédigée, citant les passages fournis |
| Entraîné par l'équipe | non : encodeur pré-entraîné ; ajustement étudié (#49), non servi | non : adaptation à engager (section 6) |

**Un point à dire d'emblée.** Le sujet oppose un modèle « de faible capacité, long à entraîner, entièrement maîtrisé » (volet A) à un modèle « performant, immédiatement disponible, dont la composition n'est pas connue » (volet B). Il précise que le modèle servi du volet A « doit préférentiellement être celui que vous avez entraîné ». Ce n'est pas notre cas. Le site sert un encodeur pré-entraîné ouvert, dont les poids, le tokeniseur et la licence (MIT) sont connus. Nous l'avons quantifié, élagué, indexé et servi nous-mêmes, mais pas entraîné.

L'équipe a tenté de l'adapter (#49) : apprentissage contrastif sur 109 paires question-passage générées en local avec Qwen, 2 époques, 185,5 secondes sur processeur. Le protocole 05, figé avant toute mesure, ne servait l'encodeur ajusté qu'à trois conditions : sa parité entre Python et navigateur vérifiée, un écart de Recall@5 avec la base positif ou nul sur les deux jeux d'évaluation, et un hébergement possible avant le 17 octobre. Il gardait la base si une condition manquait le 16 octobre. La mesure n'ayant pas été faite à temps, cette règle écrite d'avance s'est appliquée : le site sert l'encodeur de base.

La maîtrise porte donc sur l'exécution, pas sur l'apprentissage :
- chaque octet servi est versionné et vérifié par empreinte ;
- les vecteurs du navigateur sont contrôlés contre ceux de Python ;
- à l'exécution, rien ne dépend d'un service tiers.

### 2.2 Comparaison sur les six dimensions du sujet

Les mesures du volet B sont celles des essais réels consignés à ce jour ; la mesure systématique relève de #52.

| Dimension | Volet A, mesuré | Volet B, état au 19 octobre |
|---|---|---|
| Coût | aucun coût de service : GitHub Pages, fichiers statiques. Le coût est reporté sur le visiteur : 61,3 Mio transférés à la première visite, puis mise en cache | aucun coût de service, mais un matériel dédié : modèle de 4,36 Gio, 5 694 Mio de VRAM occupés après le premier appel (1 036 Mio avant) |
| Latence | recherche : 21 ms en médiane sur 10 questions (19 à 24 ms), 46 ms pour la première ; premier résultat 20,1 s après l'ouverture d'une page jamais visitée, sur la connexion de mesure | premier appel 37,7 s, dont 19,1 s de chargement ; génération de 47 à 67 tokens par seconde. Chaîne RAG, question Q036 : 46,2 s au total, dont 21,9 s de chargement, 18,5 s de lecture du prompt et 5,8 s de génération |
| Qualité | Recall@5 de 43,8 % sur 73 questions du corpus (IC 95 % : 32,9 à 55,4), contre 42,5 % pour BM25 ; non-infériorité démontrée (marge de 15 points), supériorité non démontrée. La bonne fiche est dans les 5 résultats pour 83,6 % des questions | non mesurée. Deux essais : Q036, réponse citée mais conditions d'application omises ; Q003, abstention correcte |
| Contrôle | tout est figé et vérifiable : modèle, index et passages par empreinte SHA-256, versions épinglées, vecteurs identiques bit à bit entre q8 d'origine et q8 élagué (822 sur 822) | poids et gabarit figés par empreinte, température 0, graine fixée ; mais le comportement du modèle dépend de données d'entraînement inconnues |
| Explicabilité | chaque résultat est un passage réel, avec son score de similarité, sa section et le lien vers la fiche ; rien n'est généré. Limite : le score ne se lit qu'en relatif ; les cinq passages de la question sur les congés payés vont de 0,895 à 0,889 | la réponse cite ses passages ; une citation existante ne prouve ni sa justification ni la couverture de chaque affirmation |
| Dépendance à un fournisseur | à l'exécution, aucune : seul le site est contacté, vérifié sous Chromium, Firefox et WebKit. À la construction : GitHub (Pages, Actions), npm, et Hugging Face pour l'origine du q8, recopié dans le site | Ollama, poids publiés par l'équipe Qwen (Apache 2.0), pilote et GPU NVIDIA ; aucune API distante à l'exécution |

**Abstention.** Le volet A signale les questions hors du périmètre par un seuil de similarité, fixé sur un jeu externe (CDTN) avant la mesure. Le score sépare assez bien les questions hors corpus (AUC 0,841, IC 95 % : 0,747 à 0,921). Mais le seuil conserve 72 des 73 questions du corpus et ne rejette que 9 des 24 questions hors corpus. Il repère surtout les saisies sans rapport avec le droit du travail, et l'interface ne promet pas davantage.

### 2.3 Ce que les mesures ont appris

- **Mesurer là où le modèle est servi.** Le q8 exécuté dans le navigateur ne calcule pas exactement comme le même q8 en Python. Il donne le même premier résultat que le calcul exact pour 91,8 % des requêtes, contre 96,5 % prévus par la simulation Python. Le premier résultat reste toutefois dans les 5 premiers pour 99,9 % d'entre elles. Seule la mesure dans le navigateur a révélé l'écart.
- **L'essentiel du poids était inutile.** La table des mots représente 81,6 % des paramètres de l'encodeur et couvre 250 037 pièces d'une centaine de langues. Retirer celles qui contiennent une lettre étrangère aux alphabets latin et grec ramène le q8 de 112,8 à 65,7 Mio (−42 %), avec des sorties identiques bit à bit. Le modèle passe ainsi sous la limite de 100 Mio par fichier de GitHub et peut être servi par le site lui-même.
- **Une dépendance invisible.** À son import, Transformers.js fait télécharger le moteur d'exécution ONNX Runtime depuis le CDN jsDelivr. Le site semblait autonome, et seul un essai avec ce CDN bloqué l'a montré. Le moteur est servi par le site depuis la PR #81.
- **Le parcours au clavier dépend du système.** Sur macOS, où la navigation au clavier est désactivée par défaut, Tab ne passe pas par les boutons. Dans le menu sur téléphone, le focus quittait alors le panneau. La tabulation y est désormais entièrement gérée par le code (PR #102), et vérifiée sous trois moteurs.
- **Le contrôle a priori a tenu.** Le protocole d'évaluation du notebook 03 a été figé, avec son empreinte, avant la mesure unique du 13 octobre, et la règle de repli de l'encodeur ajusté avait été écrite d'avance. Les deux décisions qui en découlent, le verdict du critère du J2 et le choix de l'encodeur servi, résultent de l'application de règles fixées avant les résultats.

### 2.4 À compléter pour la V1

- Mesures du volet B avant et après adaptation (#52), sur le jeu humain et dans les conditions du volet A pour la récupération.
- Comparaison finale des deux volets sur les six dimensions, avec les mêmes questions.
- Coût réel en temps de calcul de l'adaptation du volet B.

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
- **Rattraper des erreurs** : le journal recense 68 erreurs ou pièges détectés par la vérification au 18 octobre, dont 32 du 11 au 18 octobre.

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

**Assistants d'IA.** Leur usage est consigné session par session : 37 sessions au 18 octobre, et la session 38 du 19 octobre en relecture (PR #104). Les outils déclarés sont Claude Code, Google Antigravity avec Gemini, ChatGPT et Codex. La règle d'équipe est que tout élément produit avec un assistant soit relu et vérifié par une mesure avant d'être publié. La section 5 en fait le bilan critique.

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

### 3.4 Enseignements

Propositions communes, à discuter en équipe avant la V1 :
- **Estimer avant de commencer**, dans le ticket, et saisir la charge réelle à la fermeture : c'est la seule façon de produire l'analyse des écarts que demande le sujet.
- **Consigner le jour même** les sessions d'usage de l'IA et les comptes rendus, pendant la réunion.
- **Garder les protocoles figés et les règles de repli écrites d'avance** : ils ont permis de décider sans biais et à l'heure.
- **Mesurer dans les conditions réelles et sur plusieurs plateformes** dès le premier prototype : navigateurs, systèmes, réseau bloqué.
- **Automatiser les contrôles** : depuis le 19 octobre, les tests du moteur passent avant chaque déploiement, et un écart de version d'une dépendance arrête la mise en ligne. Ce garde-fou aurait dû exister dès le premier déploiement.

## 4. Axes de progression

Le sujet recommande une rédaction individuelle. Chaque membre complète son encadré : compétences techniques acquises, lacunes et points à approfondir, puis positionnement dans l'équipe, délégation, demandes d'aide, arbitrages, délais.

### 4.1 Mahé BEGNIS

> À rédiger par Mahé.

### 4.2 Remy RAYANE

**Compétences techniques acquises.**
- **Architecture d'indexation vectorielle et contraintes Web** : conception et découpage de l'index en format binaire Little-Endian Float32 (`piaf_reduced_index.bin`) et métadonnées JSON (#30), permettant un chargement direct en mémoire via l'API `TypedArray` (`Float32Array`) côté navigateur sans blocage de l'UI par `JSON.parse()`. Exploitation de la normalisation L2 pour ramener la similarité cosinus à un produit scalaire en O(d) vectorisable en WebAssembly / SIMD. Respect strict de l'asymétrie d'encodage E5 (`query: ` vs `passage: `) pour prévenir la dégradation du Recall@k.
- **Évaluation quantitative en recherche d'information (IR)** : mise en place de la chaîne de métriques sur PIAF (#45) et de références lexicales TF-IDF et BM25 (#47) afin d'objectiver les gains de la recherche dense par rapport aux approches par mots-clés.
- **Apprentissage contrastif et adaptation d'encodeur** : fine-tuning de `multilingual-e5-small` avec perte contrastive (MultipleNegativesRankingLoss / infoNCE) sous contraintes matérielles (#49, PR #63), ciblant l'alignement sémantique sur corpus juridique.
- **Portabilité ONNX et quantification INT8** : diagnostic de la divergence arithmétique entre l'environnement Python et l'exécution WASM de Transformers.js. Démonstration expérimentale de la nécessité d'une quantification symétrique (`ActivationSymmetric`), rétablissant 74 tenseurs sur 75 strictement identiques bit à bit à Xenova et portant la fidélité in-browser à 93,55 % (769/822 concordances). Construction d'un modèle témoin de base pour dissocier méthodologiquement l'impact de l'export ONNX de celui de l'ajustement.
- **Débogage de runtime navigateur** : identification du cache réel de Transformers.js (API Cache et non IndexedDB, nécessitant `caches.delete("transformers-cache")`), sécurisation des serveurs locaux de contrôle et gestion des variations de sérialisation des tokeniseurs Unigram sous `transformers` 5.18.

**Lacunes et points à approfondir.**
- **Métrologie et garde-fous des modèles génératifs (Volet B)** : si la prise en main de l'inférence locale Qwen 2.5 sous Ollama a été réussie (#31, #85), l'évaluation automatique de la fidélité sémantique des citations (distinguer la présence formelle d'une balise `[P1]` de la justification juridique réelle de l'affirmation) reste bien plus complexe à certifier que les métriques déterministes d'embeddings.
- **Optimisation bas niveau et WebGPU** : le travail d'optimisation s'est concentré sur le CPU et WebAssembly. L'exploitation de WebGPU (shaders de calcul matriciel direct, formats FP16/FP8 sur accélérateurs graphiques clients) constitue un axe technique à explorer pour réduire encore la latence et la consommation énergétique.
- **Automatisation continue des tests d'export** : les pièges rencontrés lors de l'intégration (divergence d'arrondis CPU Mac vs Windows, règle de `.gitignore` masquant initialement les fichiers `.onnx`) soulignent la nécessité de formaliser des pipelines d'intégration continue multi-environnements plus tôt dans le projet.

**Positionnement dans l'équipe, délégation et demandes d'aide.**
- **Binôme D2 avec Mahé** : rôle moteur sur l'expérimentation, l'indexation binaire et l'entraînement contrastif, s'appuyant sur les revues exigeantes de Mahé pour la rigueur des protocoles de mesure, les tests statistiques (McNemar apparié) et le verrouillage des critères de validation.
- **Soutien transverse sur D4 (RAG) et D3 (Front)** : accompagnement de Jibril sur l'inférence locale et l'intégration des passages M2 dans le RAG (#51), et appui à l'équipe front pour la consommation des index et le comportement du moteur sémantique.
- **Culture de relecture et transparence** : pratique régulière de la revue croisée (PR #37, #61, #62, #73, #75) et remontée immédiate des anomalies constatées (cache navigateur, divergence tokeniseur, audits contradictoires d'achèvement de la session 35) au lieu de masquer les écarts.

**Arbitrages et respect des délais.**
- **Application rigoureuse de la règle de repli du protocole 05** : face au calendrier contraint ne permettant pas d'exécuter la double mesure officielle de l'ajusté dans les règles avant le 16 octobre, acceptation et application de la règle de repli écrite à l'avance : déployer l'encodeur de base élagué (65,7 Mio) pour sécuriser l'échéance du 18 octobre. Primauté accordée à la fiabilité opérationnelle et à l'intégrité de la production sur l'affichage d'un modèle imparfaitement validé.
- **Tenue des estimations** : respect des charges prévues sur les tâches clôturées sous ma responsabilité (#45 à 3 h 30 pour 4 h estimées, #47 à 3 h 30 pour 4 h estimées), tout en partageant le constat collectif d'un manque d'estimations préalables systématiques sur les phases d'exploration imprévues.

### 4.3 Jibril BENSALEM

> À rédiger par Jibril.

### 4.4 Vaneck DAGAR

> À rédiger par Vaneck.

### 4.5 Maïmouna SIGNATE

> À rédiger par Maïmouna.

## 5. Cinq outils novateurs

**Présélection proposée, à valider au Weekly 8.** La méthode de suivi prévoit de choisir les cinq outils au Weekly 8 (4 novembre). Les cinq ci-dessous sont proposés parce qu'ils répondent aux critères retenus par l'équipe :
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

- **Usage.** Claude Code, Google Antigravity avec Gemini, ChatGPT et Codex, sur l'ensemble du projet : 37 sessions consignées au 18 octobre.
- **Apport.** Une capacité de production et de mesure qui a rendu possible le périmètre du projet.
- **Critique argumentée.** L'assistant produit des affirmations plausibles et fausses, y compris dans des documents publiés. Le journal recense 68 erreurs ou pièges détectés par la vérification au 18 octobre. Sur les 19 erreurs des sessions de Mahé du 11 au 18 octobre, 11 figuraient déjà dans une PR, une revue ou un document publiés. Deux exemples : une revue affirmant qu'aucune requête ne partait vers jsDelivr, et une description de PR affirmant que le focus ne sortait jamais du menu. Ces erreurs ont été trouvées par une mesure, un essai, une revue ou la lecture d'une source primaire, et 4 d'entre elles par un relecteur de l'équipe, non par l'assistant. L'assistant ne dispense donc ni de la vérification, ni de la compréhension du code : le sujet rappelle que tout membre peut être interrogé sur n'importe quelle portion du code produit.
- **Ce que la documentation ne dit pas.** La vérification doit être conçue pour échouer quand l'affirmation est fausse. Les essais qui ont laissé passer les erreurs ci-dessus étaient trop permissifs : requêtes écoutées au mauvais niveau, focus sur le document jugé acceptable.

## 6. Ce qui reste avant la V1

| Élément | Responsables | Échéance |
|---|---|---|
| Adaptation du modèle du volet B, exigée au jalon J3 : aucun ticket ne la porte encore | Mahé et Jibril (domaine D5), à confirmer | J3 |
| Supports de présentation, exigés au jalon J3 « même incomplets » | toute l'équipe | J3 |
| Mesures du volet B avant et après adaptation (#52), puis comparaison finale des deux volets | Mahé, Jibril | avant la V1 |
| Axes de progression individuels (section 4) | chaque membre | avant la V1 |
| Validation des cinq outils, fiches finalisées | toute l'équipe | Weekly 8, puis avant la V1 |
| Capture du board | Jibril | avant la V1 |

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
| chaîne RAG, Q036 et Q003 | PR #85 (brouillon), `docs/etudes/rag_51.md` sur sa branche |
| 61,3 Mio, 20,1 s, 21 ms (19 à 24), 46 ms | mesure du site en ligne `7e2ce07`, le 19/10/2026, Chromium, profil neuf |
| rôles, domaines, réunions, charges | `docs/suivi/SUIVI.md`, `docs/reunions/README.md`, tickets #2, #6, #9, #10, #11, #26 |
| PR, revues, commits | API GitHub et `git log` de `dev`, relevés le 19/10/2026 |
| erreurs détectées | `docs/journal/JOURNAL_USAGE_IA.md`, section 4 |
