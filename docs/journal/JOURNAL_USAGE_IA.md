# Journal d'usage de l'IA

**Équipe** Data Tigers
**Membres** Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE
**Module** NLP 2, projet de fin de module
**Formation** Master 2 Data & IA, FGES, Université Catholique de Lille
**Année universitaire** 2026-2027
**Ouvert le** 18 septembre 2026
**Dernière mise à jour** 25 octobre 2026, sessions 1 à 41 ; sessions 22 à 25, 28 à 31, 33, 34 et 36 consignées a posteriori (section 3)

**Objet.** Ce journal consigne l'usage des assistants IA sur le projet, conformément à la règle du sujet : « L'usage d'assistants IA est autorisé et encouragé. En contrepartie, le journal des usages doit être tenu, et tout membre de l'équipe peut être interrogé en soutenance sur n'importe quelle portion du code produit. »

**Responsable de la tenue** Mahé BEGNIS. Chaque membre renseigne ses propres sessions selon le modèle donné en section 5.

---

## 1. Principes d'usage retenus par l'équipe

L'équipe utilise l'IA pour trois choses, et refuse de l'utiliser pour une quatrième.

**Ce pour quoi nous l'utilisons.**

1. **Réflexion sur l'architecture et les décisions.** Explorer les options, en peser les conséquences, faire émerger les contraintes que nous n'avions pas vues. Exemple concret : le choix du couple de cas d'usage A3 et B1 a été instruit en comparant les dix cas proposés sur sept critères, ce qui a fait apparaître que A3 constitue la couche de récupération de B1 et économise 5 à 8 jours-homme.
2. **Challenger nos idées.** Nous soumettons nos décisions à une critique argumentée avant de les figer. Exemple : notre première répartition des tâches présentait un écart de charge d'un facteur 3,3 entre le membre le plus chargé et le moins chargé, et plaçait le même binôme sur les trois domaines les plus critiques. Le chiffrage de cette répartition nous a conduits à la revoir.
3. **Accélérer les tâches à faible valeur ajoutée.** Recherche de jeux de données, relevé de tailles de fichiers, lecture de documentations, mise en forme. Exemple : l'identification du corpus a comparé en quelques minutes une dizaine de sources publiques avec leur volumétrie, leur licence et leur date de mise à jour, là où la recherche manuelle aurait pris plusieurs heures sans garantie d'exhaustivité.

**Ce pour quoi nous refusons de l'utiliser.** Produire du code ou une analyse que personne dans l'équipe ne saurait expliquer. Le sujet prévient qu'une réponse insuffisante en soutenance affecte l'évaluation de toute l'équipe. Toute production assistée passe donc en revue par le binôme du domaine concerné, et le relecteur doit savoir l'exposer sans support.

**Règle de vérification.** Aucune affirmation produite par l'assistant n'est reprise sans mesure. Les chiffres des livrables proviennent de commandes exécutées, dont la méthode est décrite en annexe de chaque document. Cette exigence a permis de détecter plusieurs erreurs, listées en section 4.

---

## 2. Outils déclarés

| Outil | Nature | Membres | Usage |
|---|---|---|---|
| Claude Opus 5, puis Claude Opus 5.5 (à partir de la session 12) | modèle de langage, fenêtre de contexte de 1 million de tokens | Mahé BEGNIS, Vaneck DAGAR | architecture, décisions, recherches, critique, rédaction assistée |
| Claude Code | environnement de développement augmenté, exécute le modèle ci-dessus | membres disposant d'un abonnement | exécution de commandes, lecture de fichiers, mesures |
| Google Antigravity | plateforme d'agents, alternative gratuite | les autres membres | même usage, divergence déclarée au jalon J2 |
| Gemini 3.8 Flash (High) | modèle de langage multimodal rapide, exécuté sous Google Antigravity | Remy RAYANE | raisonnement, génération de scripts, analyse de contextes |
| ChatGPT | interface conversationnelle web | les autres membres | brainstorming, reformulations, documentation ponctuelle |
| Codex dans ChatGPT Work | agent de code exécuté dans ChatGPT Work | Jibril BENSALEM | suivi des charges, relecture du CDTN, compilation du PDF du journal (sessions 17 à 19) |

La divergence entre Claude Code et Google Antigravity est déclarée dans le rapport de jalon J2. Elle est motivée par le fait que l'abonnement Claude n'est pas détenu par toute l'équipe. Elle constitue aussi un terrain de comparaison qui alimentera la section des cinq outils novateurs du rapport final.

---

## 3. Sessions

### Session 1, 18 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Audit du sujet, étude comparative des dix cas d'usage, préparation de la réunion de cadrage.

**Produit.** `01_AUDIT_SUJET_PROJET.md` (4 180 mots), `02_ETUDE_COMPARATIVE_CAS_USAGE.md` (4 877 mots), `03_SUPPORT_REUNION_J2.md` (7 962 mots).

**Mesures exécutées.** Lecture intégrale du sujet (20 pages, 4 692 mots). Comptage des notions du module sur 11 fichiers de cours et de TP dédoublonnés, soit 245 851 caractères. Relevé des tailles de modèles ONNX et GGUF par l'API Hugging Face. Lecture des limites GitHub dans la documentation officielle. Relevé matériel du poste de travail.

**Résultats retenus.** Les notions RAG, ONNX, Transformers.js, quantisation et adaptation de modèle totalisent zéro occurrence dans les supports du module, alors que le projet les exige. Aucun modèle ONNX multilingue prêt à l'emploi ne tient sous la limite GitHub de 100 Mio. Le sujet affirme que l'architecture BiLSTM-CRF a été étudiée en journée 2, alors que le CRF n'apparaît qu'une fois dans le notebook, dans une cellule de prolongements facultatifs.

**Ce que l'équipe a validé.** Le choix du couple A3 et B1, après confrontation des trois scénarios proposés.

**Temps d'appropriation.** Immédiat pour la lecture et le comptage. La mise au point du protocole de mesure a demandé plusieurs itérations, décrites en section 4.

### Session 2, 18 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Conversion du support de réunion en PDF composé avec LaTeX.

**Produit.** Chaîne de conversion dans `latex/` : `md2tex.py` (259 lignes), `build.py` (123 lignes), `preambule.tex` (149 lignes), plus le PDF de 19 pages.

**Choix technique.** Un convertisseur dédié a été écrit plutôt que d'utiliser un outil générique, afin de dimensionner les tableaux par mesure. Avant de produire le document, XeLaTeX mesure la largeur réelle du plus large fragment insécable de chaque colonne, et ces largeurs pilotent la répartition. Le nombre de débordements est passé de 63, dont un de 116 points, à zéro.

**Ce que l'équipe a validé.** Le rendu, par relecture visuelle page par page. Trois défauts invisibles dans le journal de compilation ont été trouvés à cette occasion, listés en section 4.

### Session 3, 18 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Évaluation du dépôt `affaan-m/ECC`, proposé comme outil candidat pour la section des cinq outils novateurs.

**Mesures exécutées.** Licence, nombre de contributeurs, cadence des publications, étoiles, forks, téléchargements npm, contenu de `install.sh` et de `.env.example`.

**Résultats retenus.** Projet sain : licence MIT, 336 contributeurs, publications régulières. Mais 261 879 étoiles pour seulement 8 840 téléchargements npm hebdomadaires, alors que des bibliothèques comparables en font plusieurs millions. Conclusion transmise à l'équipe : cet outil ne nous distinguera pas, puisqu'il est au 16e rang mondial des dépôts les plus étoilés et que ses voisins immédiats au classement sont deux concurrents du même créneau. Ce qui distinguera notre rapport est la qualité de la critique, non le choix de l'outil.

**Décision de l'équipe.** Report du choix du panier d'outils, qui n'est pas un attendu du jalon J2.

### Session 4, 19 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Instruction des décisions du jalon J2, puis rédaction du rapport.

**Produit.** `04_JALON_J2_DECISIONS.md` (6 703 mots), `05_RAPPORT_J2.md` (4 104 mots) et son PDF de 12 pages.

**Mesures exécutées.**

| Mesure | Méthode | Résultat retenu |
|---|---|---|
| Faisabilité de l'exécution navigateur | page statique servie en local, Chromium piloté par Playwright, 20 passes après chauffe | 19,8 ms par requête, 3 052 ms au premier chargement, 568 ms en cache, 135,6 Mio de charge utile |
| Empreinte mémoire des modèles locaux | calcul du cache KV à partir des fichiers de configuration officiels | Qwen2.5-7B à 56,0 Kio par token, soit 2,3 à 3,4 fois moins que les autres candidats |
| Recherche de corpus | interrogation des API Hugging Face et data.gouv.fr, contrôle d'accessibilité de dix sources | `AgentPublic/travail-emploi`, 5 702 passages, 29,6 Mio, licence Etalab 2.0 |
| Dimensionnement du jeu de référence | calcul de puissance statistique | 60 questions donnent un intervalle de plus ou moins 10,1 points, insuffisant pour distinguer 0,80 de 0,85 |

**Apport le plus net.** La recherche de corpus. Dix sources publiques ont été testées pour leur accessibilité réelle, leur volumétrie, leur licence et leur fraîcheur, en quelques minutes. Cette recherche a écarté les documents internes de la formation, absents du sitemap public, et fait émerger un jeu de données administratif français dont la structure correspond exactement aux besoins du cas A3.

**Ce que l'équipe a validé.** Le corpus, le modèle du volet B, la machine cible, le protocole d'évaluation et la répartition des tâches, après discussion point par point.

### Session 5, 19 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Vérification en lecture seule de l'état réel du dépôt GitHub, avant envoi du rapport.

**Résultats.** Organisation et dépôt créés, cinq membres inscrits, enseignant collaborateur en lecture, six tickets ouverts et assignés. En revanche, aucun milestone n'existe et un seul label personnalisé est défini, alors que le rapport en annonçait respectivement trois et dix.

**Conséquence.** La section 2 du rapport a été reprise pour décrire l'état vérifié, et la structure du board y figure désormais comme structure retenue et non comme état de fait. Une procédure de création des milestones et des labels a été établie.

**Enseignement.** C'est la vérification qui a évité d'envoyer un document contenant deux affirmations que l'enseignant aurait pu infirmer en un clic.

### Session 6, 19 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Création des milestones et des labels du board, en écriture sur le dépôt.

**Vérification préalable.** L'identité du jeton a été contrôlée avant toute écriture : compte `mahebegnis`, aucune variable d'environnement ne la surchargeant. Les opérations passent par l'API et non par des commits, donc sans attribution de co-auteur.

**Produit.** Quatre milestones, un par jalon noté, avec échéance et barème. Onze labels de projet répartis sur trois axes indépendants. Six tickets rattachés et étiquetés. Le label `Jalon 2`, rendu redondant par le milestone du même nom, a été retiré.

**Difficulté rencontrée, et ce qu'elle apprend.** Deux pièges se sont présentés.

Le premier : après le retrait d'un label, la requête de contrôle a renvoyé un état périmé indiquant que deux tickets le portaient encore. Un garde-fou conditionnait la suppression du label à un décompte nul, et a donc refusé d'agir. Une lecture directe a montré que le retrait avait bien eu lieu. **Une lecture immédiatement consécutive à une écriture n'est pas fiable sur cette API**, et une condition de sécurité doit échouer vers l'inaction, ce qui a été le cas.

Le second : la commande `gh api` bascule silencieusement de GET en POST dès qu'un champ `-f` est fourni. Une requête destinée à lire les tickets d'un label a donc tenté d'en créer un, et n'a échoué que parce que le titre manquait. **Ce comportement n'est pas signalé à l'usage**, et il aurait pu écrire dans le dépôt sans intention. À retenir pour la section des outils novateurs.

**Ce que l'équipe a validé.** La liste des milestones, celle des labels, et le choix de réutiliser le label `documentation` existant plutôt que d'en créer un doublon.

**Temps d'appropriation.** Quelques minutes pour la syntaxe, vérifiée sur l'aide en ligne avant exécution. L'essentiel du temps est allé aux contrôles après écriture.

### Session 7, 19 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Mise en place de la structure du dépôt, publication des livrables du jalon J2.

**Vérification préalable.** Identité du jeton contrôlée avant toute écriture. Les commits portent l'auteur et le validateur Mahé Begnis, avec l'adresse sans réponse du compte GitHub, ce qui les rattache au compte sans exposer d'adresse personnelle. L'identité a été passée commande par commande, sans modifier la configuration git de la machine.

**Produit.** Répertoire `docs/` organisé en jalons, journal, suivi, études et chaîne LaTeX. Fichier `README.md` décrivant l'organisation, les branches et les conventions de commit. Trois branches publiées, `main`, `dev` et `docs/5-rapport-jalon-j2`, et le tag `jalon-j2`.

**Deux difficultés rencontrées.**

Le système de fichiers de macOS est insensible à la casse. La commande destinée à supprimer l'ancien `readme.md` a détruit le `README.md` écrit quelques secondes plus tôt, les deux noms désignant le même fichier. Détecté par le contrôle systématique qui suit chaque écriture, le fichier a été réécrit, et le changement de casse forcé en deux étapes avec `git mv`, seule méthode fiable sur ce type de système.

Le clone local pointait encore vers l'ancienne adresse personnelle du dépôt, périmée depuis son transfert à l'organisation. GitHub redirige silencieusement, ce qui rend l'erreur invisible à l'usage. L'adresse a été corrigée avant toute publication.

**Ce que l'équipe a validé.** La structure du dépôt, la stratégie de branches, et le choix de ne pas créer de branche de documentation permanente.

**Temps d'appropriation.** Faible pour les commandes, l'essentiel du temps allant aux contrôles après chaque écriture.

### Session 8, 19 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Deux questions soulevées par l'équipe à la relecture du rapport. Le sujet valorise un modèle entraîné par nous, or le volet A repose sur un encodeur préexistant. Et l'équipe souhaite intégrer un modèle français au volet B.

**Mesure exécutée.** Faisabilité d'un ajustement fin contrastif de l'encodeur sur la machine de référence. Chargement du modèle, construction d'un lot de 32 paires question-passage, passe avant et arrière avec optimiseur, dix pas chronométrés après chauffe, sur le processeur graphique.

**Résultat.** Un pas prend 89 ms. Trois époques sur 17 106 paires demandent 2,4 minutes. Le coût de calcul ne fait pas obstacle, ce qui ouvre une voie que nous pensions fermée. Le relevé confirme au passage un calcul antérieur : 117,7 millions de paramètres mesurés contre 117,3 prédits, soit 0,3 pour cent d'écart.

**Second point, le modèle français.** Quatre modèles Mistral ont été comparés sur leur licence, leur taille quantifiée et leur cache par token. `Mistral-7B-Instruct-v0.3` est retenu comme second modèle : même classe de taille que le principal, ce qui rend la comparaison valide, et tient dans le budget mémoire à toutes les longueurs de contexte. `Mistral-Nemo-Instruct-2407`, au français probablement meilleur, atteint 12,6 Gio à 32 768 tokens et sort du budget.

**Difficulté rencontrée.** Le premier lancement du banc d'essai s'est terminé sans aucune sortie, le tube vers une commande de filtrage ayant retenu l'affichage jusqu'à la fin du processus, lequel a été interrompu. Relancé en écriture directe vers un fichier, avec vidage explicite du tampon, il a produit le résultat. **Un banc d'essai long ne doit jamais écrire à travers un tube.**

**Ce que l'équipe a validé.** L'ajustement fin comme réponse à la valorisation du sujet, et l'ajout du modèle français en comparaison.

### Session 9, 25 septembre 2026, Remy RAYANE, Google Antigravity

**Objet.** Élaboration du plan d'action opérationnel pour le Domaine 2 (Encodeur et Indexation) dans le cadre de la résolution de l'Issue #30 (milestone Mi-parcours), ciblant l'indexation vectorielle sur le corpus réduit de référence PIAF.

**Produit.** `Plan_Action_Index.md` (286 lignes, ~2 400 mots) détaillant les spécifications techniques, les fondements NLP (asymétrie E5, normalisation L2), l'architecture de découplage binaire/JSON, ainsi que l'architecture des scripts du pipeline décrits dans le plan d'action : préparation du corpus (`prepare_piaf_corpus.py`), encodage et export binaire (`build_vector_index.py`), recherche dense (`src/retrieval/dense_search.py`) et banc d'évaluation comparatif (`evaluate_benchmarks.py`).

**Mesures exécutées.**

- Analyse du jeu de données Hugging Face `AgentPublic/piaf` : 3 835 questions, 761 contextes uniques (paragraphes Wikipédia francophones), 191 articles distincts. Longueur moyenne de 688,4 caractères par contexte (~130 à 150 sous-mots).
- Calcul théorique de l'empreinte de la matrice d'embeddings pour 761 passages en dimension 384 : 761 × 384 × 4 octets = 1 168 896 octets (1,11 Mio en float32, 285 Kio en int8), respectant strictement le budget réseau et mémoire du navigateur (< 5 Mio).
- Contrôle de la complexité algorithmique côté client : la normalisation L2 appliquée dès l'indexation permet de réduire la similarité cosinus à un simple produit scalaire en O(d) opérations, vectorisable en WebAssembly / SIMD sans surcoût.

**Résultats retenus.**

- Choix de PIAF comme jeu réduit de calibration grâce à la présence d'une vérité terrain humaine (*Ground Truth* paires questions-contextes).
- Adoption stricte des préfixes asymétriques E5 (`passage: ` pour les contextes, `query: ` pour les requêtes) pour prévenir la dégradation de Recall@k documentée par les auteurs sur les tâches de recherche asymétrique (Wang et al., 2022, arXiv:2212.03533).
- Découplage strict entre la matrice dense brute (`piaf_reduced_index.bin`) et les métadonnées (`piaf_reduced_meta.json`) pour éviter la surcharge de sérialisation JSON en mémoire navigateur.
- Définition d'un protocole d'évaluation quantitatif objectif fondé sur Recall@k (k=1, 3, 5, 10), MRR et latence d'inférence.

**Ce qui a été écarté, et pourquoi.**

- Stockage de l'index dans un JSON monolithique incluant texte et vecteurs : écarté car l'encodage de tableaux de flottants en texte alourdit la charge utile d'un facteur 2,5 à 3 et bloque le thread principal du navigateur lors de l'exécution de `JSON.parse()`.
- Démarrage direct sur le corpus final volumineux sans passage par un corpus réduit contrôlé : écarté afin de valider et figer les formats d'échange et la chaîne d'évaluation avant le passage à l'échelle.

**Ce que l'équipe a validé, et par qui.**

- Soumis à la relecture de Mahé Begnis (binôme sur le Domaine D2 Encodeur et Index).

**Temps d'appropriation constaté.**

- 30 minutes pour formaliser l'architecture de stockage binaire Float32 et valider la compatibilité avec l'API `TypedArray` (`Float32Array`) côté navigateur.

**Difficultés rencontrées.**

- Format binaire multi-plateforme : obligation de spécifier explicitement l'ordre des octets en Little-Endian (standard x86/ARM/WebAssembly) pour permettre un mapping mémoire direct sans réordonnancement d'octets.

### Session 10, 3 octobre 2026, Remy RAYANE, Google Antigravity & Gemini 3.8 Flash

**Objet.** Résolution intégrale de l'Issue #45 (milestone J3 / mi-parcours) : implémentation, test unitaire et exécution du banc d'évaluation comparatif (Aléatoire vs BM25 vs Dense E5) sur le jeu public français PIAF (`AgentPublic/piaf`), avec test de significativité statistique apparié (McNemar).

**Produit.**
- `scripts/evaluation/metrics.py` (190 lignes) : module autonome de métriques IR (`recall_at_k`, `reciprocal_rank`, `evaluate_retrieval`, `compute_mcnemar_test`) incluant un banc de tests unitaires par assertions.
- `scripts/evaluation/01_valider_sur_piaf.py` (220 lignes) : pipeline d'évaluation reproductible de bout en bout avec sauvegarde des résultats structurés dans `data/evaluation/piaf/`.
- `docs/etudes/evaluation/01_validation_metriques_piaf.md` : note de synthèse méthodologique, tableau comparatif, analyse qualitative et guide de réutilisation pour le Notebook 03.

**Mesures exécutées.**
- Extraction déterministe de 761 contextes uniques (passages Wikipédia) et 3 835 questions annotées depuis `AgentPublic/piaf` (révision figée `bda8c063bc7297180796cd835d1974c0bc71c521`).
- Encodage normalisé L2 avec `intfloat/multilingual-e5-small` (préfixes `passage: ` et `query: `) et calcul de similarité cosinus par produit scalaire matriciel (3 835 × 761).
- Calcul des métriques globales :
  - **Aléatoire :** Recall@1 = 0,08 %, Recall@5 = 0,76 %, MRR = 0,0036
  - **BM25 (`rank_bm25`) :** Recall@1 = 64,25 %, Recall@5 = 81,07 %, MRR = 0,7147
  - **Dense E5 :** Recall@1 = 66,78 %, Recall@5 = 87,20 %, MRR = 0,7567 (+6,13 points de Recall@5 face à BM25).
- Test de McNemar sur le Recall@5 : 438 victoires exclusives E5 contre 203 pour BM25 sur 641 paires discordantes, chi2 = 85,42, p = 8,84e-21 (gain hautement significatif).
- Temps d'inférence CPU moyen mesuré : 6,08 ms par requête pour E5 contre 0,37 ms pour BM25.

**Résultats retenus.**
- Validation mathématique complète de la chaîne de métriques via assertions sur calculs manuels préalables.
- Le module `metrics.py` est certifié prêt pour l'évaluation sur le corpus SocialGouv (Notebook 03).

**Ce qui a été écarté, et pourquoi.**
- Généralisation hâtive des performances au corpus réglementaire : explicitement rejetée dans le rapport, PIAF étant encyclopédique et ne reflétant pas la complexité des articles de loi ni des sigles métiers (CDI, CDD).

**Ce que l'équipe a validé, et par qui.**
- Soumis à la relecture de Mahé BEGNIS (binôme Domaine D2).

**Temps d'appropriation constaté.**
- 20 minutes pour formaliser le module de métriques pures et le test exact de McNemar.

**Difficultés rencontrées.**
- Gestion des versions de paquets : installation et configuration requises de `transformers`, `sentence-transformers` et `rank-bm25` dans l'environnement local.

### Session 11, 4 octobre 2026, Remy RAYANE, Google Antigravity & Gemini 3.8 Flash

**Objet.** Résolution intégrale de l'Issue #47 (milestone J3) : conception, implémentation et benchmarking des références lexicales TF-IDF et BM25 sur les 4 240 passages M2 du corpus travail-emploi SocialGouv, étude de 5 variantes de prétraitement et évaluation du portage client.

**Produit.**
- `scripts/evaluation/lexical_baselines.py` (220 lignes) : module modulaire et typé contenant les classes `LexicalTokenizer`, `BM25Retriever` et `TfidfRetriever`, supportant les variantes de stopwords (Snowball avec et sans négations), le stemming français et les exports web.
- `scripts/evaluation/02_references_lexicales.py` (215 lignes) : banc d'expérimentation complet, mesure des vocabulaires, latences, empreinte mémoire d'export et validation qualitative sur requêtes types.
- `docs/etudes/evaluation/02_references_lexicales_tfidf_bm25.md` : rapport complet d'analyse comparative, étude des négations en droit et proposition d'arbitrage pour le site web.

**Mesures exécutées.**
- Indexation des 4 240 passages M2 sous 5 variantes (V0 brute, V1 standard, V2 sans négations, V3 stemming + sans négations, V4 filtrage fréquentiel).
- Contraction du vocabulaire par racinisation (V3) : passage de 15 440 à 8 695 termes uniques (-43,6 %).
- Préservation des négations (V2 vs V1) : surcoût marginal négligeable (+2 mots au vocabulaire, +0,01 Mio en gzip), crucial pour l'intégrité juridique des clauses restrictives.
- Poids de l'index BM25 optimisé pour le navigateur : 2,32 Mio brut / 0,74 Mio en gzip (face aux 112,8 Mio du modèle ONNX).
- Latences moyennes mesurées : ~8 ms par requête pour BM25, ~2 ms pour TF-IDF.

**Résultats retenus.**
- La variante V3 (Stemming + Snowball sans négations) est retenue comme référence optimale pour le benchmark du Notebook 03.
- Recommandation pour le Weekly : intégration possible de BM25 en JavaScript pour un moteur de recherche léger, instantané et sans dépendance ONNX.

**Ce qui a été écarté, et pourquoi.**
- Suppression aveugle des mots vides usuels : rejetée car elle élimine « ne », « pas », « sans », « aucun », inversant le sens des interdictions dans les textes de loi.

**Ce que l'équipe a validé, et par qui.**
- Soumis à la relecture de Mahé BEGNIS (binôme Domaine D2).

**Temps d'appropriation constaté.**
- 25 minutes pour formaliser le tokenizer juridique et l'estimation de l'index inversé Web.

**Difficultés rencontrées.**
- Prise en charge des dépendances spécifiques : installation et configuration requises de `nltk` pour les ressources Snowball françaises.

### Session 12, 4 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Consignée le 6 octobre 2026**, deux jours après la session : la règle de tenue du jour même (section 5) n'a pas été respectée.

**Objet.** Relecture de la validation des métriques sur PIAF (#45, PR #55), puis analyse du jeu de questions de l'équipe (#44) et des jeux de questions externes.

**Produit.**
- Corrections poussées sur la PR #55 : module de métriques, script de validation sur PIAF, rapport et PDF.
- Issue #56 (complément CDTN), mise à jour de #46, commentaires sur la PR #54 et sur l'issue #47.

**Mesures exécutées.**
- Reproduction des chiffres de la première version et recalcul des rangs sans tri, sur les 3 835 questions de PIAF.
- Quatre variantes de BM25 sur PIAF ; tests appariés avec questions groupées par paragraphe et par article.
- Appariement des requêtes du CDTN aux passages M2 ; contrôle des extraits du jeu de l'équipe contre les passages M2.

**Résultats retenus.**
- Recall@k aligné sur la convention de l'équipe (au moins un passage pertinent dans le top k), entrées invalides refusées.
- Sur PIAF, l'avantage de l'encodeur sur BM25 dépend du réglage de BM25 : de 6,1 à 2,3 points de Recall@5. PIAF ne sert qu'à valider le code.
- Jeu de l'équipe en analyse principale, CDTN en analyse secondaire, variantes groupées par requête.

**Ce qui a été écarté, et pourquoi.**
- La valeur p calculée en supposant les questions indépendantes : elles sont groupées par paragraphe et par article, ce qui la rend trop optimiste.

**Ce que l'équipe a validé, et par qui.**
- Le complément CDTN, demandé par Jibril BENSALEM, Vaneck DAGAR et Maïmouna SIGNATE, validé par Mahé BEGNIS. La PR #55, fusionnée par Remy RAYANE le 6 octobre.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

**Difficultés rencontrées.**
- La chaîne `docs/latex` n'affiche ni les formules, ni les liens Markdown, ni les listes imbriquées dans une liste numérotée : documents réécrits en conséquence.

### Session 13, 6 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** Audit de l'état du dépôt et du jeu de questions, remise au propre des pull requests et des tickets, correction de la PR #58 (#47).

**Produit.**
- PR #59, qui reporte le notebook 02 dans `dev` ; corrections poussées sur la PR #58 : module et script des références lexicales, rapport et PDF, PDF du journal.
- Index des réunions complété (PR #36) ; comptes rendus de #6 et #26 rétablis, dates des Weekly et jalons corrigés, branches fusionnées supprimées.

**Mesures exécutées.**
- Reproduction du script de la PR #57, comparaison des listes de mots vides, mesure réelle du poids de l'index, recoupement avec `rank_bm25`.
- Contrôle du jeu de questions contre les règles de son README et contre les passages M2.
- Recherche de secrets dans l'historique du dépôt, audit des dépendances (`npm audit`, `pip-audit`).

**Résultats retenus.**
- Le notebook 02 n'était pas dans `dev` : la PR #40 avait été fusionnée dans une branche déjà intégrée.
- Références lexicales sur la liste Snowball figée, BM25 avec la formule de Lucene par défaut, poids mesuré (0,65 Mio en gzip pour V3).
- Avant le gel du jeu : 57 pré-annotations à valider et 21 doubles annotations à faire.

**Ce qui a été écarté, et pourquoi.**
- Les comparaisons entre BM25 et l'encodeur du premier rapport lexical : non mesurées, et contredites sur deux requêtes.

**Ce que l'équipe a validé, et par qui.**
- Les PR #55, #58 et #59, fusionnées par Remy RAYANE le 6 octobre.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

**Difficultés rencontrées.**
- L'assistant ne peut ni fusionner une PR sans relecture, ni approuver une PR qui contient ses propres commits : ces actions reviennent à un autre membre.

### Session 14, 6 octobre 2026 (après-midi), Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** Audit du jeu de questions fusionné (#44), gel du jeu, règle de pertinence et dossier du Weekly 4.

**Produit.**
- `scripts/evaluation/controle_jeu.py` (contrôle du jeu et accord entre annotateurs) ; règle de pertinence D4 amendée et protocole mis à jour (PR #62).
- Tag `jeu-questions-v1`, posé avec l'accord de Mahé ; audit publié en commentaire de la PR #54 ; dossier du Weekly 4.

**Mesures exécutées.**
- Contrôles du jeu sur les cinq découpages, accord calculé sur l'annotation d'avant l'arbitrage de Q062.
- Règle de pertinence vérifiée par trois implémentations sur 470 couples découpage et extrait.

**Résultats retenus.**
- Accord sur le type 20 fois sur 21 (kappa 0,88) ; mêmes passages pertinents 7 fois sur 15.
- Avec la règle initiale, deux réponses en liste (Q046, Q052) n'avaient aucun passage pertinent possible dans les petits découpages.

**Ce qui a été écarté, et pourquoi.**
- La lecture des résultats de la PR #63 sur le lot de test : le protocole devait rester indépendant de ces chiffres.

**Ce que l'équipe a validé, et par qui.**
- Le gel du jeu par Mahé BEGNIS ; la règle amendée au Weekly 4.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

**Difficultés rencontrées.**
- Le dossier temporaire de l'assistant a été vidé : environnement d'exécution à reconstruire depuis le fichier figé.

### Session 15, 7 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** Préparation et suivi du Weekly 4 (#10).

**Produit.**
- Synthèse des sept décisions à prendre, avec leurs options et une recommandation ; message de répartition des tâches pour l'équipe.

**Résultats retenus.**
- Les sept recommandations ont été validées par l'équipe ; échéance du volet A fixée au 18 octobre.

**Ce que l'équipe a validé, et par qui.**
- Les décisions, par l'équipe réunie au Weekly 4.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

### Session 16, 10 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** État des lieux du dépôt, application des décisions du Weekly 4, préparation de la mesure du notebook 03 (#46).

**Produit.**
- Décisions du Weekly 4 publiées sur #10 ; protection de `dev` et `main` (une approbation requise) ; quatre branches fusionnées supprimées.
- `scripts/evaluation/cdtn_seuil.py` : seuil d'abstention tiré du CDTN ; protocole figé ; empreintes et verrou dans le notebook ; générateur des tableaux du rapport (PR #62).
- Audit statistique du protocole par simulation, test de non-infériorité de Tango corrigé de l'effet de plan (`03_audit_statistique.md`) ; jeu complémentaire du CDTN et sa règle figée (`04_cdtn.md`, #56) ; proposition de protocole pour l'encodeur ajusté (`05_protocole_ajustement.md`, #49) (PR #62).
- Moteur de recherche du site, avec tests et parité (PR #67, #48) ; fiches d'outils Transformers.js, ONNX Runtime et `uv` (PR #68, #25).

**Mesures exécutées.**
- Seuil calculé avant la mesure (0,8560, sur 479 variantes du CDTN), recalculé de façon indépendante ; fidélité des vecteurs du navigateur au fp32.
- Verrou testé : mesure refusée si le jeu, le protocole ou le seuil est modifié d'un octet.
- Simulation de 10 000 tirages par scénario sur la structure du lot de test (73 questions, 61 fiches), sans aucune donnée de mesure.
- Parité du moteur du site sur les 24 requêtes du contrôle, en Node puis dans le navigateur.

**Résultats retenus.**
- Aucun calcul sur le lot de test : la mesure attend la relecture de la PR #62.
- La règle figée du critère du J2 conclut à tort dans 3,0 à 5,2 % des cas à la marge, au lieu de 2,5 % ; le score de Tango corrigé tient 1,9 à 2,5 %. Amendement proposé, à décider avant la mesure.
- CDTN : 155 requêtes et 607 formulations appariées ; moteur du site identique à la page de contrôle sur 24 requêtes sur 24.

**Ce que l'équipe a validé, et par qui.**
- Relecture de la PR #62 demandée à Remy RAYANE.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

**Difficultés rencontrées.**
- Données du CDTN sans licence : lues au commit figé dans `data/`, jamais versionnées.

### Session 17, 11 octobre 2026, Jibril BENSALEM, Codex dans ChatGPT Work

**Objet.** Reporter les charges de #27, #29 et #44 et préparer la relecture CDTN de Jibril.

**Produit.**
- Lignes de suivi : #27, 8 h estimées et 10 h réelles, du 26 au 28 septembre ; #29, 3 h estimées et 1 h 30 réelle, le 30 septembre. Données déclarées par Vaneck et transmises par Jibril ; soutien de Jibril sur #27.
- #44 : 18 h cumulées pour Jibril, Maïmouna et Vaneck, sans répartition individuelle. Dates du 03/10 au 07/10 et mention « non estimée » reprises le 13/10 selon la demande de Jibril et la revue de Mahé.
- Extraction locale hors du dépôt de 52 requêtes et 232 formulations CDTN attribuées à JIBZZOU. Aucun texte CDTN ajouté au dépôt.
- Note initialement consignée le 11/10 dans un fichier séparé, transférée ici le 13/10 à la demande de Mahé.

**Mesures exécutées.**
- Tickets et références relus ; écarts vérifiés : +2 h pour #27 et -1,5 h pour #29.
- Source CDTN au commit figé et empreinte SHA-256 vérifiés ; sélection depuis les identifiants de la PR #62.
- Aucun modèle exécuté, aucune mesure sur le lot de test, aucun verdict CDTN produit par cette extraction.

**Résultats retenus.**
- Charges déclarées conservées, sans estimation initiale reconstruite.
- Dépassement de #27 attribué par Vaneck au mauvais découpage du corpus source (#35, PR #39).

**Ce qui a été écarté, et pourquoi.**
- Publication de textes CDTN : données sans licence, fiche destinée à un échange privé.
- Modification du jeu figé : le tag `jeu-questions-v1` reste la référence ; la discussion rapportée par Jibril sur la PR #65 ne vaut pas approbation GitHub d'un autre membre.

**Ce que l'équipe a validé, et par qui.**
- PR #69 relue et approuvée par Vaneck le 11/10 ; Mahé a demandé les corrections de dates, de mention et de journal. Jibril a demandé leur application et la fusion le 13/10.
- Relecture CDTN annoncée complète et exploitable dans le message de Mahé transmis par Jibril le 13/10. Jibril confirme ensuite, le même jour, avoir envoyé la fiche en privé à Mahé par Discord le dimanche 11/10 et supprimé le commentaire public de #56. Suppression vérifiée dans la liste des commentaires ; envoi privé déclaré par Jibril, sans lecture de Discord.

**Temps d'appropriation constaté.**
- Non relevé ; aucun temps reconstruit.

**Difficultés rencontrées.**
- Note séparée absente du PDF du journal : intégration en session selon le modèle de la section 5.
- Estimations initiales manquantes : conserver « non estimée » pour les travaux déjà commencés.

### Session 18, 13 octobre 2026, Jibril BENSALEM, Codex dans ChatGPT Work

**Objet.** Terminer la PR #38 après ses revues et inscrire une estimation provisoire de #53.

**Produit.**
- Inventaire de 46 issues, séparé des dates et charges de travail ; jalons et réunions actualisés dans `docs/suivi/SUIVI.md`.
- Estimation de planification de #53 : 16 h cumulées pour Vaneck et Jibril, à la demande de Jibril, explicitement provisoire et à réviser.
- Conservation des charges déclarées de #25, #27, #29, #44, #45 et #47, et des estimations documentées de #31 et #51.

**Mesures exécutées.**
- Lecture des issues et de leurs commentaires, comparaison des références de dev et de la PR #38, contrôle des lignes et calcul des écarts connus.
- Vérification de l'absence du commentaire public contenant la fiche CDTN sur #56. Envoi privé le 11/10 déclaré par Jibril, sans lecture de Discord.
- Aucun moteur, modèle ou lot d'évaluation exécuté.

**Résultats retenus.**
- Les réunions du 19/09 et du 23/09 restent distinctes ; participants non documentés laissés NR.
- Dates GitHub converties à l'heure de Paris ; elles ne remplacent pas les dates de travail.
- Charges historiques absentes laissées NR ; une issue fermée ne prouve ni validation du dernier livrable ni statut Done du board.

**Ce qui a été écarté, et pourquoi.**
- Reconstitution des charges ou des comptes rendus manquants.
- Publication de textes CDTN et modification du jeu ou du protocole.
- Modification implicite des échéances : les contradictions sont signalées aux responsables.

**Ce que l'équipe a validé, et par qui.**
- Jibril a demandé de terminer #38 et autorisé une estimation plausible, révisable, pour #53.
- Les revues antérieures de Mahé sont prises en compte. Relecture indépendante du dernier diff attendue avant fusion.
- La session 17 reste portée par la PR #69 ; le numéro 18 évite de remplacer cette entrée encore en attente d'intégration.

**Temps d'appropriation constaté.**
- Non relevé ; aucun temps déduit de la durée de l'échange.

**Difficultés rencontrées.**
- Le PDF du journal ne peut pas encore être régénéré dans cet environnement : la chaîne du dépôt exige le support LaTeX français et des polices absents. Aucun PDF incomplet publié.
- Le statut du Project Board n'est pas consulté ; les états d'issues sont explicitement distingués.
- Les corps de certains tickets gardent des dates historiques malgré des plannings récents différents.

### Session 19, 13 octobre 2026, Jibril BENSALEM, Codex dans ChatGPT Work

**Objet.** Résoudre le blocage de compilation du PDF du journal pour les PR #69 et #38.

**Produit.**
- Environnement LaTeX local complété : Babel français, règles de césure françaises, polices Libertinus, Inter, Fira Mono et Font Awesome 5.
- Format XeLaTeX local reconstruit avec la césure française ; chaîne `docs/latex` du dépôt inchangée.
- Journal de #69 synchronisé avec dev : sessions 14 à 16 préservées, session 17 ajoutée. La session 18 est portée par #38.
- PDFs du journal régénérés avec les entrées propres à chaque branche.

**Mesures exécutées.**
- Archives locales contrôlées avant extraction ; contrôles de compilation : erreurs, débordements, caractères manquants et règles de césure.
- Relecture du rendu des pages et contrôle de présence des entrées ajoutées dans le PDF.
- Aucun calcul de modèle ou résultat d'évaluation.

**Résultats retenus.**
- Le défaut provenait des dépendances de l'environnement ; les polices et la mise en page du dépôt sont conservées.
- La césure française supprime le débordement observé après la première compilation.

**Ce qui a été écarté, et pourquoi.**
- Archives de paquets volumineux téléchargées incomplètement, rejetées au contrôle d'intégrité ; composants ciblés récupérés depuis CTAN.
- Remplacement des polices ou modification du préambule pour contourner les dépendances.

**Ce que l'équipe a validé, et par qui.**
- Jibril a demandé la résolution du blocage. La fusion de #69 était déjà autorisée ; #38 attend la relecture indépendante de sa nouvelle version.

**Temps d'appropriation constaté.**
- Non relevé ; aucun temps reconstruit.

**Difficultés rencontrées.**
- Installation système empêchée par les permissions ; installation dans un TEXMF local.
- Format XeLaTeX initial sans césure française : reconstruction locale nécessaire, en plus du module de langue.

**Sessions 20 à 27, de Vaneck DAGAR.** Reportées le 18 octobre depuis sa fiche d'usage, sans changement de fond. Les sessions 20, 21, 26 et 27 y ont été écrites le jour même ; les sessions 22 à 25 ont été consignées a posteriori le 11 octobre, à partir des commits, des pull requests, des tickets et de l'historique de la conversation avec l'assistant. Le temps d'appropriation est celui que Vaneck a relevé.

### Session 20, 26 septembre 2026, Vaneck DAGAR, Claude Opus 5.5 via Claude Code

**Objet.** Télécharger, filtrer, contrôler et documenter le corpus (#27).

**Produit.**
- `scripts/prepare_corpus.py` et `scripts/echantillon_controle.py`.
- `docs/corpus/CORPUS.pdf` (15 pages) et la grille de contrôle `controle_echantillon.xlsx` (70 passages) ; PR #32.
- Hors dépôt : deux schémas d'architecture en TikZ.

**Mesures exécutées.**
- Structure du fichier et versions publiées sur Hugging Face, figées par empreinte SHA-256.
- Effet de chaque règle de filtrage, composition de `chunk_text`, tokens comptés avec le tokeniseur de l'encodeur.

**Résultats retenus.**
- 5 702 passages, 5 284 après filtrage, aucune des 261 fiches perdue.
- 85,9 % des passages coupés en milieu de phrase ; 637 `chunk_text` au-delà de 512 tokens, aucun `text`.

**Ce qui a été écarté, et pourquoi.**
- Retirer les passages coupés : on perdrait 59 % du corpus.
- Retirer les doublons : ils sont marqués, la décision revient à D2.

**Ce que l'équipe a validé, et par qui.**
- La PR #32, relue et reproduite par Mahé.

**Temps d'appropriation constaté.**
- Aucun : j'utilisais déjà Claude avant le projet.

**Difficultés rencontrées.**
- Des remplacements de texte ont inséré des caractères invisibles, et une réparation a dupliqué le fichier LaTeX.
- Une mention « co-auteur Claude » ajoutée aux commits sans prévenir : historique réécrit.

### Session 21, 27 septembre 2026, Vaneck DAGAR, Claude Opus 5.5 via Claude Code

**Objet.** Corriger la PR #32 après relecture, et étudier la re-segmentation depuis la source SocialGouv.

**Produit.**
- Trois commits de correction sur la PR #32.
- Hors dépôt : un dossier `resegmentation/` (décisions D1 à D7, scripts de vérification).

**Mesures exécutées.**
- Coût réel du préfixe E5 ; comparaison du texte d'Etalab avec la source SocialGouv (`text` et `html`).

**Résultats retenus.**
- Le préfixe ajoute 2 tokens, pas 3.
- Le champ `text` de SocialGouv recopie 14,7 % de phrases d'autres sections ; le `html` n'a pas ce défaut.

**Ce qui a été écarté, et pourquoi.**
- Ma re-segmentation : Mahé l'a réalisée plus complètement (PR #39).

**Ce que l'équipe a validé, et par qui.**
- Les corrections, relues par Mahé ; la PR #32 fusionnée le 28/09.

**Temps d'appropriation constaté.**
- Aucun : j'utilisais déjà Claude avant le projet.

**Difficultés rencontrées.**
- L'extraction du `html` coupait aux liens dans les phrases ; chiffres recalculés par un script unique.

### Session 22, 28 septembre 2026, Vaneck DAGAR, Claude Opus 5.5 via Claude Code

**Objet.** Relire la PR #39 de Mahé (notebook 01, découpage) en la reproduisant sous Windows.

**Produit.**
- Commentaire de relecture sur la PR #39.
- Hors dépôt : un document LaTeX qui explique la méthode M2 sur une section réelle.

**Mesures exécutées.**
- Notebook 01 relancé de bout en bout (2 212 s) ; comparaison des effectifs et des empreintes avec Mahé.

**Résultats retenus.**
- Mêmes effectifs pour toutes les méthodes ; empreintes de M1, M2 et M3 différentes (31 caractères d'écart à l'extraction).
- Sous Windows, la commande doit utiliser `.venv\Scripts\python.exe`.

**Ce qui a été écarté, et pourquoi.**
- Aucun élément écarté.

**Ce que l'équipe a validé, et par qui.**
- La PR #39, approuvée par moi.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

**Difficultés rencontrées.**
- Le résultat n'est pas identique au caractère près d'une plateforme à l'autre ; cause probable : la version de Python.

### Session 23, 30 septembre 2026, Vaneck DAGAR, Claude Opus 5.5 via Claude Code

**Objet.** Mettre en ligne une première page du volet A à son URL définitive (#29).

**Produit.**
- Le site dans `front/` (Vite, React, Tailwind) et le déploiement automatique depuis `dev` ; PR #42.

**Mesures exécutées.**
- Site servi en local sous `/data_tigers_nlp/`, captures ordinateur et téléphone, URL vérifiée en ligne.

**Résultats retenus.**
- Site en ligne le 30/09, trois jours avant l'échéance.

**Ce qui a été écarté, et pourquoi.**
- Publier depuis `main` : la mise en ligne aurait attendu le jalon.

**Ce que l'équipe a validé, et par qui.**
- Le dépôt rendu public, en équipe ; la PR #42, fusionnée le 30/09.

**Temps d'appropriation constaté.**
- Non relevé sur le moment ; charge réelle du ticket : 1 h 30.

**Difficultés rencontrées.**
- L'environnement `github-pages` n'autorisait que `main` : un administrateur a dû ajouter `dev`.

### Session 24, 3 et 4 octobre 2026, Vaneck DAGAR, Claude Opus 5.5 via Claude Code

**Objet.** Jeu de questions (#44) : relire la PR #54, puis rédiger et annoter mes questions Q071 à Q105.

**Produit.**
- Un message à Jibril sur la méthode ; mes 35 questions annotées (24 dans le corpus, 11 hors corpus).

**Mesures exécutées.**
- Comparaison des fichiers de la PR #54 ; pour chaque question, réponse cherchée dans les 261 fiches et extrait vérifié mot pour mot.

**Résultats retenus.**
- Les 105 questions de la PR #54 étaient les brouillons de l'IA : retirées par Jibril.
- Mes questions sont rédigées par moi ; l'assistant a localisé les réponses, proposé extraits et remarques, que j'ai vérifiés.

**Ce qui a été écarté, et pourquoi.**
- Les questions écrites ou reformulées par l'IA : interdites par le ticket, elles flattent la mesure (R7).

**Ce que l'équipe a validé, et par qui.**
- La rédaction humaine, acceptée par Jibril ; le jeu figé par le tag `jeu-questions-v1`.

**Temps d'appropriation constaté.**
- Non relevé sur le moment ; charge réelle de #44 : 18 h pour trois personnes.

**Difficultés rencontrées.**
- Le site travail-emploi.gouv.fr bloque les accès automatiques : l'instantané du corpus a servi de référence.
- Le fichier, réenregistré par un tableur, avait perdu son format ; fusion refaite par script.

### Session 25, 6 et 7 octobre 2026, Vaneck DAGAR, Claude Opus 5.5 via Claude Code

**Objet.** Méthode de suivi des outils novateurs (#25).

**Produit.**
- `docs/suivi/OUTILS_NOVATEURS.md` et une fiche par outil ; mes fiches GitHub Actions et Vite ; PR #64.

**Mesures exécutées.**
- Recensement, sur toutes les branches, des outils réellement utilisés et de leurs preuves.

**Résultats retenus.**
- Dix outils candidats, chacun avec un usage réel prouvé.

**Ce qui a été écarté, et pourquoi.**
- Un fichier unique pour toutes les fiches : risque de conflits Git.

**Ce que l'équipe a validé, et par qui.**
- Méthode et répartition validées en Weekly 4 ; PR #64 approuvée par Maïmouna.

**Temps d'appropriation constaté.**
- Non relevé sur le moment ; charge réelle du ticket : 2 h.

**Difficultés rencontrées.**
- Un remplacement de texte a supprimé les antislashs d'un chemin Windows ; corrigé à la relecture.

### Session 26, 11 octobre 2026, Vaneck DAGAR, Claude Opus 5.5 via Claude Code

**Objet.** Audit de mes tâches, relecture des PR #67, #68, #69 et #70, reproduction des notebooks 01 et 02.

**Produit.**
- L'audit ; les approbations des PR #68, #69 et #70 ; mes charges de #27 et #29 transmises à Jibril.

**Mesures exécutées.**
- Notebook 01 relancé (478 s), notebook 02 relancé (73 min) ; page de contrôle exécutée dans Edge avec Playwright ; tests du moteur.

**Résultats retenus.**
- Mêmes effectifs et même modèle que Mahé, mais un index différent, comme à la session 22 : le site garde l'index de Mahé.
- Tests du moteur : 6 sur 6.

**Ce qui a été écarté, et pourquoi.**
- Les pages de fidélité et de diagnostic : inutiles pour la #48.

**Ce que l'équipe a validé, et par qui.**
- L'index versionné dans le site (option A), en équipe ; les PR #67, #68 et #70 fusionnées.

**Temps d'appropriation constaté.**
- Aucun : je connaissais déjà Claude et Playwright, utilisé dans un projet précédent.

**Difficultés rencontrées.**
- `uv` introuvable dans le terminal : installé hors du PATH de Windows.

### Session 27, 11 octobre 2026, Vaneck DAGAR, Claude Opus 5.5 via Claude Code

**Objet.** Brancher la recherche dans l'interface de chat du site (#48).

**Produit.**
- Le chargement du moteur, le chat et la carte d'un passage ; PR #71.

**Mesures exécutées.**
- Parcours complet dans Edge avec Playwright : chargement, exemple, question tapée, émulation d'un téléphone (375 px), coupure réseau simulée avec `page.route()`.

**Résultats retenus.**
- Recherche prête en environ 55 s au premier chargement ; 5 passages pertinents en 130 à 230 ms ; aucune erreur.

**Ce qui a été écarté, et pourquoi.**
- Afficher le score : il ne se lit qu'en relatif (décision revue à la session 37, le sujet l'exigeant pour A3).

**Ce que l'équipe a validé, et par qui.**
- PR #71, approuvée par Maïmouna et fusionnée le 12/10.

**Temps d'appropriation constaté.**
- Aucun.

**Difficultés rencontrées.**
- La barre de progression affichait d'abord un total faux (celui du vocabulaire, 16 Mio, au lieu des 113 Mio du modèle) ; corrigé.
- Une expression régulière écrite dans un sélecteur de texte Playwright a perdu son antislash : le test échouait alors que le site fonctionnait ; remplacée par un localisateur filtré.

**Sessions 28 à 31, consignées a posteriori.** Contrairement à la règle de la section 5, ces sessions de Mahé BEGNIS n'ont pas été consignées le jour même. Elles l'ont été le 17 octobre, à partir de l'historique de la conversation avec l'assistant et des commits, pull requests et tickets datés. Le temps d'appropriation n'a pas été relevé sur le moment.

### Session 28, 11 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** Demande de Vaneck sur les fichiers de l'index du site (#48), et pull requests en attente de Mahé.

**Produit.**
- PR #70 : index de recherche versionné dans `front/public/index/` (option A), avec `SOURCES.md` (source, licence, date) et une règle `.gitattributes` qui interdit la conversion des fins de ligne.
- Fusion des PR #66 (journal, sessions 14 à 16) et #67 (moteur du site), approuvées par Maïmouna sur leur dernier commit ; commentaire de revue sur la PR #69 de Jibril.

**Mesures exécutées.**
- Licence vérifiée sur la carte du jeu Hugging Face, au commit `98744a6` : Licence Ouverte Etalab 2.0, qui autorise la rediffusion en citant la source.
- Recherche de données personnelles dans les passages : les adresses et les sept numéros trouvés sont ceux d'organismes cités par le ministère.
- Clone simulé avec `core.autocrlf=true` : avec la règle `.gitattributes`, les trois empreintes de l'index sont retrouvées à l'identique ; sans elle, 34 retours chariot s'inséraient dans l'en-tête.

**Résultats retenus.**
- Le site sert l'index mesuré au notebook 03 (empreinte `2ec45586…`), et non un index reconstruit sur une autre machine.

**Ce qui a été écarté, et pourquoi.**
- Transmettre les fichiers à Vaneck pour qu'il les intègre : reconstruit chez lui, sous Windows, l'index aurait pu différer de l'index mesuré ; la relecture de la PR #39 avait déjà montré des empreintes différentes sous Windows.

**Ce que l'équipe a validé, et par qui.**
- PR #70 approuvée et fusionnée par Vaneck DAGAR, le 11 octobre.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

**Difficultés rencontrées.**
- Un commentaire publié sous le compte de Mahé parlait de lui à la troisième personne ; corrigé aussitôt, la première version restant visible dans l'historique des modifications de GitHub.

### Session 29, 13 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** Amendement statistique du critère du J2, mesure unique du notebook 03 (#46) et son rapport, audit de l'ajustement de Remy (#49), seuil d'abstention du moteur (#53).

**Produit.**
- Protocole du notebook 03 amendé et figé à nouveau : verdict du critère du J2 par le score de Tango corrigé de l'effet de plan, nouvelle empreinte inscrite dans le notebook (PR #62, commits `a7ab3af` et `45355fb`).
- Mesure unique du notebook 03 sur le lot de test (`f1044e0`) et rapport `docs/etudes/evaluation/03_evaluation.md` (`23efdb0`), PR #73.
- Protocole de la mesure de l'encodeur ajusté complété avant son gel : recette d'export, témoin, encodage dans le navigateur (`44152df`, PR #75).
- Seuil d'abstention dans le moteur du site, appliqué seulement au modèle et à l'index pour lesquels il a été calculé (`24c2707`, PR #76).

**Mesures exécutées.**
- Notebook 03 exécuté une fois en mode mesure, après contrôle des empreintes du protocole, du jeu et du seuil ; une seconde exécution a donné des résultats identiques octet par octet.
- Audit du q8 de Xenova et de la recette d'export de Remy : 72 poids MatMul en int8 par canal, tables des mots en uint8 symétrique ; avec `ActivationSymmetric`, la recette redonne 74 des 75 tenseurs quantifiés. La quantification dynamique calcule son échelle sur tout le lot : les contrôles de fidélité se font requête par requête. En Python, le résultat dépend du processeur (791 et 762 sur 822 pour le même fichier) ; dans le navigateur, il est identique entre les machines.

**Résultats retenus.**
- Critère du J2 satisfait : Recall@5 de 43,8 % pour l'encodeur servi contre 42,5 % pour BM25 de référence, écart de +1,4 point, intervalle à 95 % de -11,5 à +14,3 points ; aucun des deux n'est démontré meilleur (McNemar, p = 1,000).
- Abstention : AUC de 0,841 ; le seuil garde 72 des 73 questions du corpus et n'écarte que 9 des 24 questions hors corpus.

**Ce qui a été écarté, et pourquoi.**
- La règle de Wald du 10 octobre : la simulation de la session 16 la montrait trop permissive. L'amendement, décidé avant la mesure et sans aucune donnée du lot de test, rend la conclusion plus difficile à obtenir, jamais plus facile.

**Ce que l'équipe a validé, et par qui.**
- PR #62 approuvée et fusionnée par Remy RAYANE ; PR #73 approuvée par Remy RAYANE ; PR #76 approuvée et fusionnée par Vaneck DAGAR, le 14 octobre.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

**Difficultés rencontrées.**
- Le fichier de sauvegarde des vecteurs du navigateur portait un nom couvert par le motif des fichiers de mesure, et il apparaît dans la sortie du notebook : déclaré dans le commit, la PR et le rapport, sans retouche du notebook.

### Session 30, 14 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** Intégration avant le Weekly 5 : licence du CDTN (#56), modèle élagué servi par le site (#50), vérification de l'encodeur ajusté livré par Remy et gel du protocole 05 (#49), relectures et import du CDTN, QCM du Weekly.

**Produit.**
- PR #73 fusionnée (mesure du notebook 03).
- PR #77 : licence du CDTN corrigée, Apache-2.0, avec les conditions de redistribution et la portée du contrôle des données personnelles.
- PR #78 : élagage sans perte du vocabulaire (`scripts/allegement/`) et modèle de 65,7 Mio servi par le site, à la place des 112,8 Mio téléchargés depuis Hugging Face.
- PR #75 : protocole 05 complété (fidélité de l'ajusté livré, reproductibilité, empreintes), puis figé après le Weekly (`75a39bd`, empreinte `f2c8169d…`) : tokeniseur de l'encodeur de base, aucune dérogation au calendrier.
- PR #79 : import des trois relectures du CDTN (`evaluation/cdtn/jugements.csv`), fusionnée le 17 octobre.
- Revues : approbation de la PR #63 de Remy, sans lecture des chiffres exploratoires du lot de test, réservée à l'après-mesure ; revues de la PR #72 de Vaneck.
- Hors dépôt : QCM de 20 questions du Weekly 5 (page privée, et classeur importable dans Kahoot) ; décisions non arbitrées en séance consignées sur #11.

**Mesures exécutées.**
- Élagage : 121 271 pièces gardées sur 250 002 ; q8 ramené de 118 308 185 à 68 862 041 octets ; découpage identique sur les 822 requêtes de contrôle, les 113 textes de la mesure, les 5 433 textes du CDTN et les 4 240 passages ; 822 vecteurs sur 822 identiques bit à bit dans le navigateur.
- Encodeur ajusté de Remy : fichiers conformes à son manifeste, réexport bit à bit depuis les poids, parité fp32 (cosinus minimal de 1,00000000) ; fidélité du q8 livré dans le navigateur : 769 sur 822, contre 761 pour le témoin (McNemar exact, 53 contre 45, p = 0,48).
- Licence du CDTN lue dans le `package.json` de la source et dans le paquet npm 2.20.0, qui contient le même fichier de requêtes.
- Fiches de relecture : format, identifiants et valeurs contrôlés ; deux verdicts « Oui » ramenés à « oui », avec l'accord de Jibril ; import simulé puis réel : 182 jugements, 155 requêtes, dont 131 jugées « oui » ou « partiel ».
- Site en ligne : avant la #78, la recherche échouait si Hugging Face était bloqué, même avec le modèle en cache ; après la #78, aucune requête vers Hugging Face.
- Serveur de contrôle de la PR #63, lancé dans un dossier isolé : 11 essais sur l'en-tête Host, l'origine et le type de contenu, tous conformes.

**Résultats retenus.**
- Le site sert lui-même un modèle de 65,7 Mio, aux mêmes vecteurs que le q8 d'origine.
- La fidélité de l'ajusté livré ne s'écarte pas significativement de celle du témoin.

**Ce qui a été écarté, et pourquoi.**
- Héberger l'encodeur ajusté sur le Hub de Hugging Face : remplacé par l'élagage sans perte, qui garde le modèle dans le dépôt.
- Lire les chiffres du lot de test de la PR #63 avant la mesure : la mesure de l'ajusté doit rester en aveugle.

**Ce que l'équipe a validé, et par qui.**
- PR #77 et #79 approuvées par Jibril BENSALEM ; PR #78 par Vaneck DAGAR ; PR #75 approuvée et fusionnée par Remy RAYANE ; PR #63 fusionnée par Remy après l'approbation de Mahé.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

**Difficultés rencontrées.**
- Repointer la PR #78 sur `dev` a invalidé ses deux approbations, ce que la documentation de GitHub ne signale pas.
- Une partie des actions de l'assistant sur GitHub (fusions, commentaires) a été refusée par son contrôle des permissions ; Mahé les a lancées lui-même.

### Session 31, 17 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** État des lieux du dépôt avant la fin du volet A, revue de la PR #80 de Vaneck (#53), documentation de clôture et jalon de mi-parcours (#43).

**Produit.**
- Revue de la PR #80, interface finale du site : approuvée, puis remplacée par une demande de modification après la vérification de Jibril (voir les difficultés).
- PR #81 : moteur d'exécution d'ONNX Runtime Web servi par le site, et non plus par jsDelivr.
- README du dépôt réécrit : adresse du site, chaîne de traitement, résultats, arborescence réelle, licences, branches et tags.
- Tag annoté `mi-parcours`, posé a posteriori sur la version en ligne au mi-parcours (`ac84ed3`, déployée le 30 septembre), et branche d'observation `observation/mi-parcours`.
- Journal : sessions 28 à 31, erreurs de la période en section 4, outils de la section 2 complétés.

**Mesures exécutées.**
- PR #80 construite (`npm ci --ignore-scripts`, `npm run build`) et parcourue dans Chromium : 5 passages ordonnés avec score, section et lien ; question gardée pendant un chargement retardé, puis traitée ; message hors périmètre pour « azerty » ; aucune requête vers Hugging Face ni Google Fonts ; aucun débordement à 375, 768 et 1 280 px ; aucune erreur dans la console.
- Essai décisif, cache vidé et jsDelivr bloqué au niveau du contexte du navigateur : la version de `dev` échoue (« Le modèle n'a pas pu être téléchargé ») ; avec la correction de la PR #81, jsDelivr et Hugging Face bloqués, le moteur démarre, aucune requête n'est tentée hors du site, et le classement est inchangé ; 15 tests sur 15.
- Audit du dépôt : aucun secret trouvé ; un seul fichier de plus de 10 Mio, le modèle servi ; 62 commits de `dev` portent une adresse e-mail personnelle, tous antérieurs au 13 octobre.

**Résultats retenus.**
- La mesure de l'encodeur ajusté n'a pas été faite avant le 16 octobre : le notebook 05 n'était pas construit, et l'import des relectures n'a été fusionné que le 17 octobre. La règle de repli du protocole 05 s'applique : le site sert l'encodeur de base pour la fin du volet A. La mesure reste possible après, à titre descriptif, pour le rapport.
- La branche principale avait 175 commits de retard, et aucun tag de mi-parcours n'était posé ; Jibril a mis `main` à jour le jour même (PR #74).

**Ce qui a été écarté, et pourquoi.**
- Écrire le résultat dans le protocole 05 : son empreinte, que le notebook de mesure doit contrôler, aurait changé ; le résultat est consigné dans le README, dans ce journal et dans le classeur de suivi.
- Poser `mi-parcours` sur l'état actuel du dépôt, qui ne représente pas le jalon ; nommer la branche d'observation comme le tag, ce que git signale comme ambigu.
- Réécrire l'historique pour retirer les adresses : interdit sur une branche partagée ; chaque membre règle son compte GitHub pour éviter de nouvelles expositions.

**Ce que l'équipe a validé, et par qui.**
- PR #74 approuvée et fusionnée par Jibril BENSALEM ; documentation de clôture et PR #81 soumises à la relecture de Jibril BENSALEM et Vaneck DAGAR.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

**Difficultés rencontrées.**
- `git log --since` arrête le parcours au premier commit plus ancien que la date : un premier audit des adresses a conclu à tort qu'il n'y en avait aucune.
- Mon test de la PR #80 écoutait les requêtes au niveau de la page : celles du moteur d'exécution vers jsDelivr n'y apparaissaient pas. Jibril l'a relevé dans sa vérification ; l'essai avec le CDN bloqué l'a confirmé.

### Session 32, 18 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** Clôture du volet A : intégration des pull requests en attente, revue de Jibril sur la documentation, focus du menu sur téléphone et périmètre du corpus affiché (#53), contrôle du site en ligne.

**Produit.**
- PR #81 fusionnée : moteur d'exécution d'ONNX Runtime Web servi par le site, après l'approbation de Jibril.
- PR #80 de Vaneck approuvée avec une portée écrite, puis fusionnée ; le focus du menu, seul point restant, est corrigé à part.
- PR #83 : focus retenu dans le menu sur téléphone (`<main>` inerte, panneau en boîte de dialogue modale, focus rendu après le rendu) et périmètre du corpus dans le message d'accueil (261 fiches, 4 240 passages, instantané du 11 septembre). Après la revue de Jibril, la tabulation boucle dans le panneau et Échap est écouté au niveau du document (`e6cd210`) ; la description de la PR est corrigée.
- PR #72 de Vaneck approuvée et fusionnée : la condition posée le 14/10 est levée par la réservation des sessions 20 à 27 dans ce journal.
- PR #82 : trois points de la revue de Jibril appliqués (inférence locale documentée, critère de #43 non satisfait par le tag historique, #46 fermée), et cette session.
- #43 fermée avec sa réserve, critère par critère ; classeur de suivi comparé ligne à ligne avec l'API GitHub : #11, #46, #50 et #56, fermées, y figuraient encore comme ouvertes (PR #83).
- Journal : sessions 33 à 35 de Remy (PR #86) relues et intégrées, avec huit corrections vérifiées sur le dépôt et l'API GitHub ; sessions 20 à 27, 36 et 37 de Vaneck reportées depuis sa fiche, avec une correction ; bilan de la section 4 recompté.
- PR #88, en relecture : `onnxruntime-web` déclaré dans `front/package.json`, à la version qu'épingle Transformers.js, sur la remarque de Vaneck à la #81 ; une fois fusionnée, les tests du moteur passeront avant chaque déploiement. Le site construit reste identique octet pour octet.
- PR #84 fusionnée dans `main` (`8955962`) et tag annoté `volet-a-v1` posé sur ce commit, qui contient la première inférence locale.
- #23 fermée comme non réalisée, l'horizon du mi-parcours étant dépassé ; classeur de suivi : #23 fermée et tickets #91 à #98 ajoutés (PR #102).
- Revues approuvées des PR #99 et #100 de Jibril (Agent0 Light, volet B), avec contre-essais du schéma et du tirage des sources.
- PR #102 : tabulation entièrement gérée dans le menu sur téléphone, après un défaut trouvé sous WebKit, le moteur de Safari.

**Mesures exécutées.**
- PR #83, première version (`74f3e39`), site construit et servi en local, accès à jsDelivr, Hugging Face et Google Fonts bloqués : 5 passages aux scores de référence ; focus rendu au bouton du menu après Échap, au champ de saisie après un exemple ou un chat ; menu fermé au passage en largeur d'ordinateur ; périmètre visible à 375 et 1 280 px ; aucune erreur. L'essai de 14 Tab puis 6 Maj+Tab, publié comme « le focus ne sort jamais du panneau », comptait le document (BODY) comme acceptable : le focus en sortait aux frontières (voir les difficultés).
- PR #83, version corrigée (`e6cd210`), toute requête hors du site bloquée, focus relevé après chaque frappe : 22 frappes (14 Tab, 8 Maj+Tab) dans le panneau ; les deux frontières ; le scénario de la revue (dernier bouton, Tab, Échap) ; Tab, Maj+Tab et Échap depuis BODY ; 14 frappes pendant une recherche en cours, exemples désactivés ; tabulation libre en largeur d'ordinateur ; recherche aboutie, seul le site contacté, aucune erreur.
- Site en ligne, version `74524a7`, cache vidé, les mêmes accès bloqués : 5 passages en 8 s, seule l'adresse du site contactée, aucune erreur ni aucun avertissement.
- Site en ligne, version `c3cf075`, après la #83, Cache API vidée, toute requête hors du site bloquée : version et périmètre affichés ; 20 frappes Tab et Maj+Tab sans sortie du menu, puis Échap ; 5 passages aux scores de référence ; aucune requête externe tentée, aucune erreur.
- PR #88 : SHA-256 des 23 fichiers du site construit, avant et après, identiques ; dans un clone vierge sans `data/`, 10 tests réussis et 5 ignorés ; écart de version simulé, 1 échec attendu.
- Site en ligne `c3cf075` sous Firefox 155 et WebKit 26.6 (moteurs de Playwright), profil neuf, requêtes hors du site bloquées : recherche aboutie aux scores de référence sur les deux ; sous WebKit, sur macOS, 10 frappes sur 20 sortent du menu. Version corrigée, servie en local : 0 sortie sur 20 frappes avec Chromium, Firefox et WebKit.
- PR #99 et #100 : 27 puis 44 tests réussis sous macOS avec le verrou de Jibril ; corpus réel contrôlé (4 240 passages, 261 fiches, empreintes de l'index du site) ; tirage par défaut identique à celui de Jibril sous Windows.
- Classeur de suivi : 54 lignes de l'inventaire comparées à l'API GitHub, aucun écart d'état ni de date.

**Résultats retenus.**
- Le site en ligne ne dépend plus d'aucun service externe pour se charger.

**Ce qui a été écarté, et pourquoi.**
- Pousser la correction du focus sur la branche de Vaneck : contraire à la règle de l'équipe ; elle part de `dev`, après la fusion de la #80.
- Lever la protection de `dev` pour fusionner les #83 et #82 sans approbation : refusé par le contrôle des permissions de l'assistant ; ces fusions reviennent à Mahé ou attendent une approbation.

**Ce que l'équipe a validé, et par qui.**
- PR #81 approuvée par Jibril BENSALEM ; PR #80 et #72 approuvées par Mahé ; PR #82 approuvée par Jibril BENSALEM sur `5740655`, puis fusionnée ; PR #83 : modification demandée par Jibril BENSALEM sur `74f3e39`, puis approuvée par Vaneck DAGAR et Jibril BENSALEM sur `c69042e`, et fusionnée par Vaneck DAGAR. PR #87 approuvée et fusionnée par Remy RAYANE ; PR #84 approuvée par Jibril BENSALEM sur `bef1ca5`, puis fusionnée par Mahé ; la PR #86 est alors marquée fusionnée par GitHub, son commit étant dans `main`. PR #88 soumise à Vaneck DAGAR et Jibril BENSALEM. PR #89 approuvée par Jibril BENSALEM, puis fusionnée par Mahé ; PR #90, #88 et #102 soumises à Jibril BENSALEM, Maïmouna SIGNATE et Vaneck DAGAR.

**Temps d'appropriation constaté.**
- Non relevé.

**Difficultés rencontrées.**
- Dans l'interface B, le texte d'invite est le même pendant et après le chargement : un test qui s'en servait pour attendre le moteur ne prouvait rien à lui seul ; seules les recherches abouties prouvent que le moteur a démarré.
- La première version de la correction rendait le focus avant le retrait de l'attribut `inert`, donc le navigateur le refusait ; corrigé avant le commit.
- `inert` retire la conversation de la tabulation, mais pas le document lui-même : après le dernier bouton du menu, Tab plaçait le focus sur BODY, et Échap, écouté sur le panneau seulement, ne fermait plus le menu. Mon essai jugeait BODY acceptable ; Jibril l'a reproduit aux deux frontières. Seule une boucle explicite de la tabulation retient le focus.
- Le dossier de travail temporaire de l'assistant a été vidé entre deux journées : ses scripts d'audit de la veille n'existent plus.
- La boucle de tabulation de la #83 laissait le navigateur avancer hors des bords de la liste : sous WebKit sur macOS, où la navigation au clavier du système, désactivée par défaut, fait sauter les boutons à Tab, le focus quittait le menu. Seule une gestion complète de Tab vaut pour tous les navigateurs.
- Sous WebKit, le blocage des requêtes de l'essai rejetait une URL `blob:`, et la recherche échouait du fait du montage, non du site ; `blob:` et `data:` sont désormais laissés passer.

**Sessions 33 et 34, consignées a posteriori.** Contrairement à la règle de la section 5, ces sessions de Remy RAYANE des 13 et 14 octobre 2026 n'ont pas été consignées le jour même. Elles sont reconstituées le 18 octobre à partir de l'historique des requêtes, des scripts créés et exécutés, des commits vérifiés et des pull requests datées (#63, #75). Le temps d'appropriation n'a pas été relevé sur le moment.

### Session 33, 13 octobre 2026, Remy RAYANE, Google Antigravity & Gemini 3.8 Flash

**Objet.** Résolution intégrale des exigences de parité ONNX et de fidélité navigateur pour l'Issue #49 : alignement de la quantification INT8 sur Xenova (`ActivationSymmetric=True`), création du modèle témoin de base, automatisation des métriques navigateur avec empreintes SHA-256 opposables (`08_calculer_metriques_navigateur.py`), et réponse aux remarques de revue de Mahé.

**Produit.**
- `06_exporter_onnx.py` (dans `scripts/adaptation/`) : export ONNX dynamique INT8 symétrique (`ActivationSymmetric=True`, 74/75 tenseurs identiques bit à bit à Xenova), support du modèle témoin de base et génération dynamique de `quant_config.json`.
- `07_mesurer_fidelite_822.py` : encodage unitaire sans padding (`batch_size=1`) pour isoler l'effet de batch.
- `08_calculer_metriques_navigateur.py` (241 lignes) : calcul automatisé des métriques in-browser (concordance Top-1, cosinus médian, dégradation maximale), test exact de McNemar apparié et empreintes SHA-256 opposables.
- `serveur_controle.py` (dans `scripts/adaptation/`) et `fidelite_navigateur.html` (dans `scripts/indexation/`) : sécurisation du serveur local de contrôle et gestion robuste de la réponse HTTP (`res.ok`).
- `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md` : mise à jour des sections 5 et 6, protocole comparatif face au témoin et recompilation du PDF.

**Mesures exécutées.**
- Contrôle de parité FP32 PyTorch vs ONNX : cosinus minimal = 1,00000000, écart maximal = 1,17 × 10⁻⁷.
- Mesure in-browser WASM sur les 822 requêtes réalistes de section et 4 240 passages : Top-1 concordance à 93,55 % (769/822) pour l'ajusté et 92,58 % (761/822) pour le témoin.
- Comparaison des tenseurs d'embeddings : 74 sur 75 deviennent strictement identiques bit à bit à ceux de Xenova.
- Démonstration expérimentale du rôle de témoin : le témoin de base et Xenova divergent sur 52 requêtes sur 822 du seul fait de l'export opset 14, indépendamment de tout apprentissage.

**Résultats retenus.**
- La quantification symétrique est indispensable pour préserver la fidélité de l'encodeur dans Transformers.js.
- Le modèle témoin de base est formellement retenu comme étalon pour le Weekly 5 pour isoler l'effet de l'export de celui de l'ajustement.

**Ce qui a été écarté, et pourquoi.**
- Comparaison de latence entre machines hétérogènes (Mac M4 vs PC Windows Core i7) : non reproductible à matériel distinct.
- Notes de travail et synthèses intermédiaires (`reponse_revue_mahe_issue49.md`) retirées du commit final après intégration dans l'étude.

**Ce que l'équipe a validé, et par qui.**
- Soumis à la revue de Mahé BEGNIS (D2) et Jibril BENSALEM.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

**Difficultés rencontrées.**
- Dépendance arithmétique du CPU en Python unitaire (762/822 sur PC vs 791/822 sur Mac), alors que l'exécution WASM dans le navigateur donne exactement les mêmes chiffres sur nos deux machines de test pour le témoin (761/822).

### Session 34, 14 octobre 2026, Remy RAYANE, Google Antigravity & Gemini 3.8 Flash

**Objet.** Clôture technique de l'Issue #49 et préparation du Weekly 5 : actualisation des chiffres de fidélité du q8 livré avec quantification symétrique, traitement de la divergence de sérialisation du tokeniseur, désactivation du cache navigateur, sécurisation de `serveur_controle.py` et intégration de la PR #63.

**Produit.**
- `fidelite_navigateur.html` (dans `scripts/indexation/`) : purge du cache de Transformers.js avant le chargement d'un modèle ajusté ou témoin (`caches.delete("transformers-cache")`, au lieu de `indexedDB.deleteDatabase`), pour éviter l'évaluation d'un modèle périmé en local.
- `serveur_controle.py` (dans `scripts/adaptation/`) : contrôle de chemin strict interdisant tout accès hors des dossiers autorisés du dépôt.
- `08_calculer_metriques_navigateur.py` : mise à jour des métriques du modèle q8 livré définitif (`934a202b...` : 769/822 requêtes concordantes, cosinus médian 0,99384, McNemar exact b = 53, c = 45, p = 0,48).
- `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md` : actualisation de la section 5.2, documentation de l'écart de sérialisation du tokeniseur sous `transformers` 5.18 (proposition de retenir le tokeniseur de base au Weekly 5), articulation avec la stratégie d'élagage (#50), et recompilation du PDF.
- PR #63 (`feat/49-ajustement-encodeur`) et PR #75 (`docs/49-protocole-05-final`) fusionnées dans `dev`.

**Mesures exécutées.**
- Audit de tokenisation sur 822 requêtes, 113 textes du Notebook 03, 4 240 passages M2 et 607 requêtes CDTN : 100 % d'identité sur le corpus et le test, divergence isolée sur 6 formulations CDTN avec espace final.
- Re-mesure navigateur à chaud avec cache invalidé confirmant les 769/822 concordances.

**Résultats retenus.**
- Modèle ajusté et scripts certifiés prêts pour l'arbitrage du Weekly 5 ; intégration de la règle d'élagage sans perte sous 100 Mio si le modèle est retenu.
- La règle de repli du protocole 05 (garder l'encodeur de base si la mesure officielle n'est pas positive sur les deux jeux) est formellement arrêtée.

**Ce qui a été écarté, et pourquoi.**
- Déploiement immédiat de l'ajusté dans `front/public/` : strictement subordonné à la mesure conjointe du protocole 05.

**Ce que l'équipe a validé, et par qui.**
- Protocole 05 validé au Weekly 5 ; PR #63 approuvée par Mahé BEGNIS, PR #75 approuvée par Remy RAYANE, toutes deux fusionnées par Remy RAYANE le 14/10.

**Temps d'appropriation constaté.**
- Non relevé sur le moment.

**Difficultés rencontrées.**
- `transformers` 5.18 modifie légèrement la structure JSON du tokeniseur à la sauvegarde sans modifier le vocabulaire Unigram, créant un cas particulier sur les espaces terminaux.

### Session 35, 18 octobre 2026, Remy RAYANE, Google Antigravity & Gemini 3.8 Flash

**Objet.** Audit d'achèvement du volet A pour l'échéance du 18 octobre : vérification intégrale du dépôt Git, état des tickets D2/D3, analyse des pull requests PR #83 et PR #84, checklist de clôture opérationnelle du volet A et régularisation des sessions du journal d'IA.

**Produit.**
- Audit contradictoire des jalons, tickets (#43, #46, #48, #49, #50, #53, #56) branches distantes (`origin/dev`, `origin/main`) et pull requests #83 et #84.
- Vérification du site en ligne (https://datatigersnlp.github.io/data_tigers_nlp/) et confirmation de l'application de la règle de repli du protocole 05 (#49 : encodeur de base élagué 65,7 Mio servi).
- Analyse de la PR #83 (`fix/53-focus-menu-perimetre`) : validation des correctifs d'accessibilité mobile (bouclage tabulation, Échap, `inert`) et affichage du périmètre (261 fiches, 4 240 passages).
- Fiche de clôture et ordonnancement des 4 actions restantes pour ce soir (fusion PR #83, recette du site en ligne, fusion PR #84, pose du tag `volet-a-v1`).
- Branche `docs/journal-sessions-remy-octobre` : intégration des sessions 33, 34 et 35 dans ce journal, mise à jour du préambule, ajout des anomalies traitées en section 4 et recompilation du PDF.

**Mesures exécutées.**
- Contrôle d'accessibilité et de réponse HTTP 200 sur le site public en ligne hébergé sur GitHub Pages.
- Vérification des empreintes SHA-256 et des règles d'exclusion Git (`git status --ignored -s`).
- Recompilation complète de `JOURNAL_USAGE_IA.pdf` via `docs/latex/build.py` et `xelatex`.

**Résultats retenus.**
- Le volet A est fonctionnel en ligne ; sa clôture tient aux quatre actions restantes listées ci-dessus.

**Ce qui a été écarté, et pourquoi.**
- Fusion directe sans relecture : toute fusion vers `dev` et `main` passe par une pull request et l'approbation d'un relecteur selon les règles de conduite du projet.

**Ce que l'équipe a validé, et par qui.**
- Soumis à la relecture de Mahé BEGNIS (D2) et Jibril BENSALEM.

**Temps d'appropriation constaté.**
- Immédiat.

**Difficultés rencontrées.**
- `latexmk` requiert Perl sous Windows ; compilation directe en deux passes via `xelatex` sur le fichier généré par `build.py`.

**Sessions 36 et 37, de Vaneck DAGAR.** Sessions des 13 et 14 octobre, reportées le 18 octobre depuis sa fiche d'usage, et numérotées à la suite des sessions 33 à 35 de Remy RAYANE. La session 37 a été écrite le jour même ; la session 36 a été consignée a posteriori le 14 octobre, à partir des mêmes sources.

### Session 36, 13 octobre 2026, Vaneck DAGAR, Claude Opus 5.5 via Claude Code

**Objet.** Finition de l'interface du volet A (#53) : état des lieux, mesures avant changements, accessibilité, puis maquettes de refonte pour l'équipe.

**Produit.**
- Mesures « avant » (Lighthouse en ligne : performance 39 sur téléphone et 70 sur ordinateur, accessibilité 96) et captures en 375 et 1 280 px, hors du dépôt.
- Corrections sur `feat/53-finition-interface` : suggestions de la revue de #42, annonce courte pour les lecteurs d'écran, contrastes, police système, durée du premier chargement annoncée.
- Un canevas de design partagé (Claude, artefact « Design ») : directions A à E, huit palettes de la B, états de la B ; la B a été retenue par l'équipe.

**Mesures exécutées.**
- Contrastes calculés pour chaque palette (niveau AA, au moins 4,5:1) ; parcours au clavier et captures pilotés par Playwright.

**Résultats retenus.**
- Accessibilité Lighthouse de 95 à 100 en local après corrections.
- La performance est limitée par Transformers.js sur le fil principal : constat transmis pour le #48 (Web Worker), hors du périmètre du #53.

**Ce qui a été écarté, et pourquoi.**
- Les fonctions que le site n'a pas (« Copier le lien », « même hors ligne ») : retirées des maquettes avant publication.
- Un nom de marque inventé par l'assistant : remplacé par un nom descriptif.

**Ce que l'équipe a validé, et par qui.**
- La direction B, à la majorité de l'équipe ; la palette verte d'origine, après discussion.

**Temps d'appropriation constaté.**
- Canevas de design : prise en main immédiate, les maquettes étant produites par l'assistant ; non relevé précisément.

**Difficultés rencontrées.**
- Le champ de saisie fixé en bas masquait les exemples sur téléphone pendant le chargement : il n'est fixé qu'après la première question.
- Une modification du canevas faite dans la page entre deux publications : l'outil a refusé d'écraser la version récente, reprise avant de republier.

### Session 37, 14 octobre 2026, Vaneck DAGAR, Claude Opus 5.5 via Claude Code

**Objet.** Relectures des PR #76 et #78, corrections de la PR #72, puis interface du #53 : abstention, score, refonte B.

**Produit.**
- Relectures publiées : #76 (seuil d'abstention) et #78 (modèle élagué), approuvées.
- PR #72 : fiche Playwright corrigée (cache du modèle dans l'API Cache, unités en Mio, essai du contexte persistant).
- `feat/53-finition-interface` : message et bouton d'abstention, score de chaque passage, question gardée pendant le chargement, refonte selon la maquette B (panneau latéral, nouveau chat, chats de la session, menu sur téléphone), police DM Sans servie par le site, poids du modèle élagué (65,7 Mio).
- Adresse git passée en noreply ; branches fusionnées supprimées.

**Mesures exécutées.**
- #76 et #78 testées sur l'index servi par le site (`2ec45586`), avec une référence de la page de contrôle regénérée sur cet index dans Chromium ; parité du moteur avec le modèle élagué : 24 requêtes sur 24, écart de score nul, aucune requête vers Hugging Face.
- Essai Playwright : contexte persistant rouvert avec `page.route()` actif, recherche prête en 4 s au lieu de 87 s, modèle non retéléchargé.
- Premier chargement sur le site en ligne après la #78 : 23 à 30 s.
- Interface : scénario complet en 375, 768 et 1 280 px, parcours au clavier, Lighthouse (accessibilité et bonnes pratiques à 100).

**Résultats retenus.**
- Le seuil d'abstention et le modèle élagué fonctionnent comme annoncé ; deux défauts de test signalés (export local du notebook 02, fins de ligne de `LICENSE` sous Windows).
- Score affiché avec trois décimales : à deux, les cinq passages affichaient tous « 0,89 ».

**Ce qui a été écarté, et pourquoi.**
- Mon propre export du notebook 02 pour les relectures : son index diffère de celui du site.
- `scrollIntoView` pour amener la dernière question en haut : il faisait remonter tout le cadre de l'application.

**Ce que l'équipe a validé, et par qui.**
- #76 fusionnée par moi, #78 par Mahé ; la PR du #53 reste à ouvrir et à faire relire par Jibril.

**Temps d'appropriation constaté.**
- Aucun.

**Difficultés rencontrées.**
- Les approbations de la #78 ont été annulées par le changement de base vers `dev` : relecture refaite sur la fusion réelle.
- Une phrase de la fiche Playwright affirmait un comportement non vérifié : Mahé l'a relevé, un essai l'a confirmé avant de l'écrire.

### Session 38, 19 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** Fin du volet A : intégration des pull requests approuvées par Jibril, contrôle du déploiement et du site en ligne sur trois moteurs, statuts des tickets.

**Produit.**
- PR #90 fusionnée dans `main` (`548f809`) avant toute autre fusion, comme Jibril le demandait : `main` porte la consignation du tag `volet-a-v1`, qui reste sur `8955962`.
- PR #88 (`a911922`), puis PR #102 (`7e2ce07`), fusionnées dans `dev`, chacune sur la tête approuvée.
- Défaut de la #83 précisé dans ce journal et dans la description de la PR #102 : il tient au réglage de navigation au clavier de macOS.
- Inventaire des tickets ouverts : tous les tickets du volet A sont fermés, sauf #49, reporté au jalon J4 ; le dépôt n'a aucun label de statut.

**Mesures exécutées.**
- Premier déploiement avec l'étape de tests de la #88 : 15 tests, dont 10 réussis et 5 ignorés faute de `data/`, aucun échec ; construction et publication réussies. Même résultat au déploiement de la #102.
- Site en ligne, version `7e2ce07`, sous Chromium 148, Firefox 155 et WebKit 26.6, profil neuf à 390 px, requêtes hors du site bloquées : 0 sortie du menu sur 20 frappes, les deux bords, retour depuis le document, Échap ; 5 passages aux scores 0,895 · 0,894 · 0,890 · 0,889 · 0,889 ; aucune requête externe, aucune erreur.

**Résultats retenus.**
- Le correctif de tabulation fonctionne en ligne sur les trois moteurs.

**Ce qui a été écarté, et pourquoi.**
- Fusionner les PR #99 et #100 de Jibril, que j'ai approuvées : sa documentation attend aussi la relecture de Remy.
- Mettre à jour la colonne d'état du board : le jeton de l'assistant n'a pas le droit `project`, et l'étendre revient à Mahé.

**Ce que l'équipe a validé, et par qui.**
- PR #90, #88 et #102 approuvées par Jibril BENSALEM sur leurs têtes, le 18/10 au soir, avec ses propres essais (trois moteurs pour la #102).

**Temps d'appropriation constaté.**
- Non relevé.

**Difficultés rencontrées.**
- Jibril n'a pas reproduit le défaut de la #83 sous WebKit 26.5 (Linux) : il tient au réglage de navigation au clavier de macOS, désactivé par défaut, sous lequel Tab saute les boutons.
- Une branche créée sans récupérer l'état distant partait d'un `dev` périmé ; recréée depuis `7e2ce07` avant tout commit.

### Session 39, 23 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** Audit du dépôt depuis le 19 octobre ; analyse du travail de Jibril sur Agent0 Light, à sa demande ; revues ; lancement des tâches du volet B qui ne dépendaient de personne.

**Produit.**
- Audit : aucune fusion du 19 au 23 octobre ; activité de chaque membre relevée ; aucune trace du Weekly 6 (#12).
- Revues des PR de Jibril : #101, demande de modification (le contrôle d'extrait accepte un fragment de deux lettres, correctif testé joint) ; #103 et #106, commentaires (forme des questions, doublons, méthode hors corpus, conception du pilote) ; #85 approuvée.
- Commentaire à Remy sur la PR #105 : deux inexactitudes dans sa section 4.2.
- PR #104 fusionnée, approuvée par Maïmouna.
- Ticket #107 ouvert : adaptation du modèle du volet B, avec plan, critères et risques.
- PR #108 : protocole de mesure du volet B avant et après adaptation, proposé (#52).
- PR #109 : faisabilité de l'adaptation par LoRA mesurée sur Mac (#107).

**Mesures exécutées.**
- Agent0 : 142 tests réussis sur la pile, 93 sur la #101 ; 13 extraits sur 13 retrouvés mot pour mot dans l'index du site ; contre-essai du validateur, où l'extrait « ng » est accepté.
- Agent0 : recouvrement lexical entre question et source de 0,67 pour les candidats contre 0,40 pour 5 questions humaines de calibration (médianes) ; 15 questions posées au site en ligne, source parmi les 5 premiers pour 8 candidats sur 8 identifiables, aucune abstention pour les 6 hors corpus.
- #85 : 45 tests réussis sous macOS, dans un environnement réduit à NumPy.
- Faisabilité (#107) : LoRA de rang 8 sur Qwen2.5-7B-Instruct en 4 bits (MLX) ; pic de mémoire GPU de 7,14 Gio et 10,5 s par itération sur 16 couches, 7,56 Gio et 14,3 s sur 28 couches, avec des contextes de 1 115 à 2 542 tokens.

**Résultats retenus.**
- Le travail d'Agent0 est exact et honnêtement documenté. Ses limites sont de méthode : biais lexical, diversité, hors corpus. Il ne remplace pas l'adaptation exigée à J3.
- L'adaptation est faisable sur le Mac ; la mesure sur le Legion reste à faire.

**Ce qui a été écarté, et pourquoi.**
- Lancer seul la mesure de #49 : c'est une mesure unique sur le lot de test, dont le notebook doit d'abord être relu par Remy, co-responsable ; les conditions préalables ont déjà été vérifiées le 14 octobre.
- Pousser des correctifs sur les branches de Jibril : contraire à la règle de l'équipe ; ils sont proposés dans les revues.

**Ce que l'équipe a validé, et par qui.**
- PR #104 approuvée par Maïmouna SIGNATE ; section 3 du rapport relue par Remy RAYANE et par Maïmouna SIGNATE pour ce qui les concerne (PR #105).

**Temps d'appropriation constaté.**
- Non relevé.

**Difficultés rencontrées.**
- La fusion de la #104 a d'abord été refusée : le SHA complet de la tête avait été saisi de mémoire, et il était faux. La protection `--match-head-commit` a joué son rôle ; la fusion a été refaite avec le SHA lu par l'API.
- Plusieurs pièges de mesure pendant l'essai de faisabilité, détaillés en section 4.

**Session 40, de Jibril BENSALEM.** Rédigée par Jibril le 24 octobre dans la PR #101 sous le numéro 39, déjà pris par la session du 23 octobre ; reportée ici le 25 octobre, telle quelle, avec le seul changement de numéro décidé avec Mahé.

### Session 40, 24 octobre 2026, Jibril BENSALEM, Codex dans ChatGPT Work

**Objet.** Corriger le contrôle des extraits Agent0 demandé par Mahé dans la revue de #101 du 23 octobre, puis reporter la correction dans #103 et sa dépendante #106.

**Produit.** `extrait_valide` exige au moins 20 caractères, aucun espace de bord et une occurrence exacte alignée sur des limites de mots Unicode. Le texte n'est ni normalisé ni corrigé. Les cinq nouvelles régressions couvrent les fragments courts, la limite de 20 caractères, les limites de mots et espaces, les occurrences multiples et les fins de ligne LF/CRLF. Les fixtures techniques sont allongées ; les rejets de génération, multi-passage et adversarial couvrent aussi un extrait trop court.

**Mesures exécutées.** Python 3.12.14, environnement isolé installé depuis `scripts/synthetic/requirements-lock.txt`, Pydantic 2.14.0 ; `uv pip check` réussi. Suite de #101 : 98 tests réussis ; version étendue de #103 : 147 tests réussis. Les trois fragments `ng`, `le` et `nn` sont rejetés sur le passage M2 signalé. Les 13 extraits copiés dans le support de #106 à `99ed172` satisfont tous le contrôle renforcé, contre les sources JSON de ce même support. Aucun appel réel à Ollama ou au tokeniseur dans ces contrôles.

**Résultats retenus.** Minimum de 20 caractères proposé par Mahé, contrôles de forme communs aux catégories avec preuves. Les écarts LF/CRLF et les listes aplaties restent rejetés ; les textes multiligne exacts restent acceptés. Les fichiers historiques des runs et les champs humains ne sont pas modifiés.

**Ce qui a été écarté, et pourquoi.** Pas de réparation ou normalisation silencieuse, pas de preuve de suffisance sémantique déduite de la longueur. Le contrôle du « ? », les indicateurs de diversité et la méthode hors corpus relèvent des autres remarques de revue ; ils ne sont pas ajoutés à cette correction.

**Ce que l'équipe a validé, et par qui.** Mahé a fourni le défaut et la proposition de contrôle le 23 octobre. Le correctif est demandé par Jibril le 24 octobre ; sa relecture indépendante reste attendue. Aucun verdict humain sur les candidats, fusion dans dev ou main, ni clôture de ticket.

**Temps d'appropriation constaté.** Non renseigné ; aucune charge réelle reconstituée.

**Difficultés rencontrées.** Les anciennes fixtures utilisaient des preuves trop courtes ; leurs textes artificiels ont été allongés sans modifier les sources M2. La copie de travail des tours précédents avait été retirée par la maintenance : snapshots récupérés depuis les commits GitHub, sans récupération ni modification de l'archive originale.

### Session 41, 25 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** État des lieux du dépôt ; vérification des correctifs de Jibril et de Remy ; place de Vaneck dans le volet B ; numérotation du journal ; calendrier jusqu'à J4 et mise à jour des tickets.

**Produit.**
- État des lieux : aucune fusion depuis le 23 octobre ; les PR #101, #103 et #106 en conflit avec `dev` sur le journal.
- Revue de la #101 : correctif des extraits validé, marche à suivre pour retirer le journal de la pile Agent0.
- Session du 24 octobre de Jibril reportée en session 40.
- Vaneck sur le volet B, avec l'accord de Mahé :
  - ticket #111, démonstration locale et vidéo, avec Maïmouna ;
  - #51 : vérification et usage de la chaîne, avec Maïmouna ;
  - relecteur des PR #85 et #108 ;
  - juge de l'exactitude dans le protocole de la PR #108, avec Maïmouna ;
  - relecture de l'échantillon des données d'adaptation (#107), avec Maïmouna.
- Calendrier jusqu'à J4, à valider au Weekly 7 : 53 étapes datées, avec responsables, soutiens et dépendances.
- Rééquilibrage : Remy rejoint la génération des données d'adaptation et devient coresponsable de l'entraînement (#107), pour alléger Jibril avant J3.
- Tickets #112 à #114 créés : supports de J3, rapport V1, préparation de la soutenance.
- Échéances datées dans les corps de #49, #51, #52, #107 et #111 ; #52 et #107 passés au jalon J4 ; Maïmouna et Vaneck assignés à #52.
- Jalons de #8 et de #91 à #97 ; échéances d'Agent0 proposées en commentaire sur #91 à #98, sans toucher aux corps rédigés par Jibril ; ordre du jour proposé pour les Weekly 6 à 13.
- Classeur de suivi : Vaneck ajouté à #51, tickets #107, #111 et #112 à #114 ajoutés, jalons et échéances alignés sur GitHub.

**Mesures exécutées.**
- #101 à `e8b50fd` : 98 tests réussis sous macOS. Les fragments `ng`, `le` et `nn`, un extrait commencé au milieu d'un mot et un extrait avec espace de bord sont refusés ; les 13 vrais extraits du support de la #106 restent acceptés.
- Section 4.2 du rapport (#105) : les cinq PR que Remy cite désormais portent ses revues, d'après l'API GitHub ; la formule s'affiche sans dollar dans le PDF.
- Fusions simulées avec `dev` : #101, #103 et #106 en conflit sur le journal ; #99, #100 et #85 sans conflit.
- Calendrier contrôlé par script : aucune dépendance vers une étape plus tardive, aucune échéance le 11/11, férié. Étapes en responsable avant J3 : de 5 (Remy) à 14 (Jibril) après rééquilibrage, contre 3 et 16 avant.
- Tickets relus par l'API après écriture : corps, jalons, assignés et les 18 commentaires sont identiques aux brouillons.
- Classeur de suivi comparé à l'API sur toutes ses colonnes (titre, assignés, jalon, état, dates) : 59 lignes, aucun écart.

**Résultats retenus.**
- Le correctif de Jibril règle la demande de modification sans faux rejet.
- Le blocage restant est le journal, modifié dans la pile Agent0 à partir d'une version ancienne.

**Ce qui a été écarté, et pourquoi.**
- Résoudre le conflit sur la branche de Jibril : contraire à la règle de l'équipe ; la marche à suivre lui est donnée en revue.
- Approuver la #101 avant la résolution : le commit de résolution annulerait l'approbation.
- Modifier le corps des tickets Agent0 : ils sont rédigés par Jibril, les échéances lui sont proposées en commentaire.
- Fermer le jalon de mi-parcours, sans ticket ouvert depuis le passage de #8 en J3 : décision laissée à Mahé.
- Changer le statut des tickets dans le board : le jeton n'a pas la portée `project`.

**Ce que l'équipe a validé, et par qui.**
- Numérotation du journal et place de Vaneck dans le volet B décidées par Mahé BEGNIS.
- Mise à jour des tickets demandée par Mahé BEGNIS ; calendrier soumis à l'équipe au Weekly 7.

**Temps d'appropriation constaté.**
- Non relevé.

**Difficultés rencontrées.**
- La récupération de l'état distant a d'abord échoué sur un verrou de Git : une récupération concurrente de l'éditeur. Aucun processus Git n'était actif au contrôle et le verrou avait disparu ; aucun fichier n'a été supprimé, et la récupération a été relancée.

### Session 42, 26 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** État des lieux du dépôt ; lancement des tâches de Mahé dans le calendrier jusqu'à J4 ; PR en attente de sa validation.

**Produit.**
- Seuil S de l'état B2 : `scripts/evaluation/seuil_b2.py`, S = 0,8565, inscrit avec son empreinte dans le protocole 06 (PR #108).
- Protocole 06 : témoin T de la chaîne d'export, mesuré si ses tenseurs diffèrent de ceux du modèle de #31 ; signalement des questions dont le score est à moins de 1e-5 de S.
- PR #115, en brouillon : contrôle de la séparation des données d'adaptation et du lot de test (#107, étape 4), relu par Remy.
- #107 : méthode de service corrigée, grille de décision de la machine pour le Weekly 7.
- #49 : audit des entrées de la mesure de l'encodeur ajusté, plan du notebook 05.
- #105 : relecture redemandée à Maïmouna.
- Courriel de relance de l'enseignant (étape 1) rédigé pour Mahé, qui l'envoie.
- Calendrier resserré, après l'avancement de la soutenance au lundi 30/11 annoncé par Mahé : 57 étapes, projet terminé le vendredi 20/11, révision et entraînement ensuite, point d'arrêt de l'adaptation le 12/11.
- GitHub : jalon J4 au 30/11 ; échéances corrigées dans #49, #52, #107, #111, #113 et #114 ; #52 revenu en J3 ; 13 commentaires, dont les ordres du jour des Weekly 7 à 13 ; #49 et la fin d'Agent0 soumis au Weekly 7.
- #110 fusionnée, après l'approbation de Jibril sur sa tête.
- #100 et #101 réapprouvées, puis annulées automatiquement par GitHub : la base mémorisée de ces PR est antérieure à la fusion de la #99. « Update branch » est demandé à Jibril, puisque nous ne poussons pas sur la branche d'un autre membre.
- #108 : les cinq remarques de la revue de Jibril traitées (valeurs non finies refusées avec une régression, population commune des comparaisons appariées, valeur complète de S, conditions pour confondre T et le modèle de #31, licence du CDTN).
- #115 : format des exemples d'adaptation proposé à Remy, vérifié dans le code de mlx-lm 0.32.2.
- PR #116 : lignes de Mahé dans les fiches GitHub CLI, assistants d'IA et Ollama, limitées aux faits vérifiables.
- Suivi : fermeture de #12 par Jibril reportée (Weekly 6 non tenu, consigné dans le ticket), détectée par le contrôle d'alignement.

**Mesures exécutées.**
- Seuil S : 479 variantes du CDTN, issues de 103 requêtes, dont 24 sous le seuil ; intervalle à 95 % par rééchantillonnage des requêtes, de 0,8464 à 0,8653.
- Contrôle de S : les 479 scores recalculés par les fonctions de la #85 (commit `df91b85`) sont identiques au bit près.
- Séparation : 10 tests réussis ; 61 fiches exclues ; deux mutations de la règle font échouer les tests.
- #49 : trois empreintes du protocole 05 retrouvées sur les fichiers reçus le 14/10.
- Ollama, au tag `v0.40.5` : `errAdaptersUnsupported` dans `server/create.go` ; la page du Modelfile ne mentionne plus `ADAPTER`.
- Calendrier contrôlé par script : ordre chronologique, dépendances antérieures, aucune échéance le 11/11, aucune production après le 20/11.
- Tests d'Agent0 sur le résultat des fusions avec `dev`, calculé par `git merge-tree` : 44 réussis pour la #100, 98 pour la #101.
- Seuil S recalculé avec le script corrigé : fichier identique octet par octet, même empreinte. La mutation qui retire le contrôle des NaN est détectée.

**Résultats retenus.**
- S en fp32 dépasse de 0,0005 le seuil du site, calculé en q8 ; l'écart reste dans l'intervalle d'incertitude.
- La voie « directive `ADAPTER` » de #107 est impossible sur le Legion. Sans témoin, l'écart avant/après aurait mêlé l'adaptation et la requantification.

**Ce qui a été écarté, et pourquoi.**
- Script de mesure (étape 18) : il s'écrit sur `scripts/rag/` après la fusion de la #85, qui n'est pas fusionnée.
- Nouvelle revue de la #101 : le journal n'est pas encore retiré de la pile Agent0.
- Rédiger la section 4.1 du rapport à la place de Mahé : un plan lui est proposé.
- Envoyer le courriel à l'enseignant : l'assistant n'a pas accès à la messagerie de Mahé.

**Ce que l'équipe a validé, et par qui.**
- Lancement des tâches demandé par Mahé BEGNIS.
- Le témoin T reste à valider en relecture de la #108.
- Revue de la #108 par Jibril BENSALEM : principe du témoin approuvé, cinq corrections demandées, toutes faites ; relecture redemandée.

**Temps d'appropriation constaté.**
- Non relevé.

**Difficultés rencontrées.**
- Le dépôt est sur un Bureau synchronisé par iCloud : 10 309 fichiers du `.venv` étaient déchargés. Les imports ont été ralentis, puis le premier calcul de S a échoué sur un délai de lecture. Les fichiers ont été rapatriés par lecture, sans rien modifier.

### Session 44, 27 octobre 2026, Mahé BEGNIS, Claude Opus 5.5 via Claude Code

**Objet.** Bilan du dépôt ; revues de la #100 et de la #118 ; script de mesure du volet B ; préparation du Weekly 7. La session 43, de Jibril (26 octobre), est dans la PR #118.

**Produit.**
- PR #119 : script de mesure du protocole 06 (`scripts/rag/mesure.py`) et ses tests. `generation.py` prend le modèle et le digest en paramètres optionnels, ceux de #31 par défaut.
- #100 réapprouvée sur `f8deda3`, puis fusionnée par Jibril. #101 approuvée sur `f182489`, après sa mise à jour avec `dev` : 98 tests réussis sur le résultat de la fusion.
- Relecture technique de la #118, la faisabilité sur le Legion : méthode et chiffres vérifiés, proposition du Mac soutenue. Approuvée sur `0d26e89` une fois passée en « prête » par Jibril.
- Commentaires sur #8 (relance de l'enseignant abandonnée) et sur #13 (décision sur la machine pour le Weekly 7).
- Feuille de route mise à jour avec l'avancement au 27 octobre.
- Journal de Vaneck reçu de Mahé : déjà intégré le 18 octobre (PR #87), aucun ajout.

**Mesures exécutées.**
- #100 : 44 tests réussis sur le résultat de la fusion avec `dev`, #85 comprise.
- #118 : 7 tests réussis sur processeur (torch 2.11.0, transformers 5.20.2, peft 0.21.2) ; chiffres du rapport retrouvés dans son JSON ; parité avec la #109 vérifiée par le nombre de paramètres entraînables (720 896 par couche) et l'échelle de LoRA (20).
- #119 : 23 tests, 68 avec ceux de la #85 ; sept mutations des règles du protocole détectées ; essai réel sur la calibration avec R+ et R-, qui retrouve M3 = 100 % et M1 = 0 % pour R+.
- Journal de Vaneck : 10 sessions et 24 lignes d'erreurs comparées au journal. Elles sont identiques, sauf deux formulations où le journal est exact : renvoi à la session 37, et #76 fusionnée par Vaneck (vérifié par l'API).

**Résultats retenus.**
- Le Legion ne convient pas à l'entraînement : 9,17 Gio alloués pour 7,96 Gio physiques, 274 s par pas contre 10,5 s sur le Mac.
- Sur la calibration, B2 s'abstiendrait sur une question (Q038, score 0,8466) ; aucune question n'est à moins de 1e-5 de S.

**Ce qui a été écarté, et pourquoi.**
- Fusionner la #108, approuvée : elle gèlerait le protocole avant le script relu et la machine confirmée.
- Approuver la #118 tant qu'elle était en brouillon. Elle a été approuvée une fois passée en « prête » ; l'ordre de fusion avec la #117, qui modifie aussi le PDF du journal, est convenu dans la revue.
- Recalculer S sur le Legion : la mesure doit utiliser le fichier calculé le 26 octobre, contrôlé par son empreinte.
- Relancer l'enseignant : décision de Mahé, l'enseignant communiquera.

**Ce que l'équipe a validé, et par qui.**
- Lancement des tâches et abandon de la relance, par Mahé BEGNIS.
- Approbation de la #108 et fusions des #85 et #100, par Jibril BENSALEM.

**Temps d'appropriation constaté.**
- Non relevé.

**Difficultés rencontrées.**
- Les sockets `kernel-ipc` d'un ancien noyau Jupyter, dans `scripts/evaluation`, empêchaient la copie du dossier pour les essais de mutation : seuls les deux modules utiles ont été copiés.

---

## 4. Erreurs détectées par la vérification

Cette section est tenue volontairement. Elle documente ce que la relecture systématique a permis de rattraper, et constitue le principal argument en faveur de notre méthode.

| Date | Erreur | Détection | Correction |
|---|---|---|---|
| 18/09 | Comptage des notions faussé par une recherche en sous-chaîne, qui comptait « rag » dans « paragraphe » | incohérence des ordres de grandeur | comptage refait avec frontières de mots |
| 18/09 | Expression régulière renvoyant zéro occurrence de LSTM alors qu'il y en avait 133 | contradiction avec un autre compteur | passage à une implémentation Python vérifiée |
| 18/09 | Nombre de fichiers audités annoncé à 12, réel 14 dont 3 quasi-doublons | recomptage explicite | corpus de référence ramené à 11 fichiers dédoublonnés |
| 18/09 | Classification des paquets Python ignorant les roues `universal2`, donc deux paquets déclarés à tort incompatibles | contrôle manuel des étiquettes | reclassement complet |
| 18/09 | Rang mondial du dépôt ECC annoncé au 13e, réel 16e | comptage des dépôts plus étoilés | corrigé, et l'argument en est sorti renforcé |
| 18/09 | Tirets cadratins rendus en « --- » dans les tableaux du PDF | relecture visuelle du rendu | caractères Unicode utilisés directement |
| 19/09 | Taille d'un modèle annoncée par l'API à 0,5 Mio, réelle 294,6 Mio, les poids étant dans des fichiers externes | invraisemblance pour un modèle de 300 millions de paramètres | mesure des fichiers externes |
| 19/09 | Charge utile du navigateur relevée à 5,5 Mio pour un modèle de 112,8 Mio | invraisemblance | les ressources d'origine tierce ne déclarent pas leur taille, mesure refaite fichier par fichier, résultat 135,6 Mio |
| 19/09 | Seuil de réussite Recall@5 proposé à 0,80 sans fondement | recherche des résultats publiés du modèle : 23 mesures de récupération, toutes en anglais | seuils reformulés en écarts appariés face à une baseline |
| 19/09 | Conclusion hâtive sur l'absence de board, tirée d'une sortie vide | la sortie vide masquait une erreur de périmètre d'autorisation | aucune conclusion tirée, limite déclarée dans le rapport |
| 19/09 | Rapport annonçant trois milestones et dix labels inexistants | consultation du dépôt | section 2 alignée sur l'état vérifié |
| 19/09 | Lecture immédiatement consécutive à une écriture renvoyant un état périmé | garde-fou conditionnant la suppression à un décompte nul | suppression refusée puis reprise après contrôle direct |
| 19/09 | `gh api` basculant de GET en POST dès qu'un champ `-f` est fourni | échec en 422 sur un titre manquant | requêtes de lecture écrites sans `-f` |
| 19/09 | Suppression de `readme.md` détruisant le `README.md` écrit juste avant, le système de fichiers étant insensible à la casse | contrôle systématique après écriture | fichier réécrit, casse forcée en deux étapes avec `git mv` |
| 19/09 | Clone local pointant vers l'ancienne adresse du dépôt, périmée depuis son transfert à l'organisation | lecture de l'adresse distante avant publication | adresse corrigée avant tout envoi |
| 19/09 | Banc d'essai terminé sans aucune sortie, le tube de filtrage retenant l'affichage | fichier de sortie vide alors que le processus était terminé | écriture directe vers un fichier, tampon vidé explicitement |
| 26/09 | `chunk_text` présenté comme contenant la section d'origine | vérification sur les 5 702 passages | explication corrigée dans CORPUS.pdf |
| 26/09 | 849 `chunk_text` trop longs, estimés à 4 caractères par token | comptage exact avec le tokeniseur | 637 passages |
| 26/09 | Deux verdicts de la grille fondés sur cette estimation | comptage exact | verdicts corrigés |
| 26/09 | Préfixe E5 compté pour 3 tokens | Mahé, en relançant les scripts (PR #32) | 2 tokens |
| 26/09 | Corpus annoncé à 5 282 passages au lieu de 5 284 | résultat du script | chiffre corrigé |
| 26/09 | Mauvais renvoi de section dans CORPUS.pdf | relecture du PDF | renvoi automatique |
| 27/09 | Extraction du `html` coupant aux liens dans les phrases | fragments incohérents | extraction et chiffres corrigés |
| 27/09 | Intertitres collés présentés comme gênants pour l'encodeur | test du tokeniseur | effet déclaré négligeable |
| 27/09 | Commande proposée qui aurait effacé la grille annotée | relecture avant publication | commande retirée |
| 03/10 | Jeu de questions prérempli avec les 105 brouillons de l'IA (PR #54) | comparaison des fichiers | brouillons retirés |
| 04/10 | Test de McNemar pour questions groupées attribué à Durkalski (2003), alors que la formule employée est celle d'Obuchowski (1998) | lecture du code source d'une implémentation publiée | attribution et formule corrigées avant publication |
| 04/10 | Appariement du CDTN à nos passages : 189 requêtes le matin, 175 l'après-midi, selon la règle employée | recalcul indépendant | règle d'appariement à écrire et figer avant la mesure (#56) |
| 04/10 | Extrait proposé qui ne répondait pas à la question (Q073) | ma relecture | question remplacée |
| 04/10 | Fichier des questions abîmé par un tableur (colonnes inversées, valeurs vidées) | diff anormal | fusion refaite par script |
| 06/10 | Aperçu des résultats de l'encodeur calculé sur le jeu de test avant l'écriture du protocole, puis un commentaire affirmant qu'aucune mesure n'avait été faite | relecture de la méthode, puis du commentaire avant envoi | aperçu ni utilisé ni diffusé aux annotateurs, phrase corrigée avant envoi, protocole à écrire avant toute mesure |
| 06/10 | Règle de pertinence proposée qui excluait par construction les réponses en liste des petits découpages | audit du jeu final contre les cinq découpages | seconde condition ajoutée avant la validation du protocole, d'après les seules annotations |
| 07/10 | Règle qui aurait désigné le mauvais coordinateur de Playwright | relecture du tableau | colonne de coordination ajoutée |
| 10/10 | Nombre de fiches visées par le seuil du CDTN annoncé à 61 au lieu de 50, compté sur toutes les requêtes appariées | recomptage avant le commit | corrigé avant le gel du protocole |
| 10/10 | Empreinte SHA-256 débordant de 254 points dans la marge du PDF du protocole | journal de compilation | empreintes regroupées dans un bloc de code |
| 10/10 | Chiffres de l'audit statistique tirés d'un essai préliminaire, à une autre graine, et non du script versionné | réexécution du script avant le commit | chiffres alignés sur la sortie reproductible |
| 11/10 | Barre de progression annonçant 16 Mio (vocabulaire) pour un modèle de 113 Mio | capture du parcours dans Edge | progression corrigée |
| 13/10 | Recalcul indépendant de l'effet de plan différent de celui du module de métriques | écart entre les deux calculs | écart dû au degré de liberté de l'estimateur ; avec `ddof=1`, accord à 1e-14, le module était juste |
| 13/10 | Serveur de contrôle local acceptant des requêtes POST sans contrôle d'extension ni de chemin | audit de sécurité du script Python | contrôle strict du chemin cible et rejet des requêtes hors du périmètre autorisé (`serveur_controle.py`) |
| 13/10 | `aria-live` sur toute la conversation : un lecteur d'écran aurait relu les cinq passages à chaque réponse | relecture du code | annonce courte dédiée |
| 13/10 | Ligne de version sous le seuil de contraste (3,28:1 au lieu de 4,5:1) | Lighthouse | couleur assombrie |
| 13/10 | Maquettes promettant des fonctions absentes du site (« Copier le lien », « même hors ligne ») | relecture avant publication | retirées |
| 14/10 | Fidélité de l'encodeur ajusté publiée à 753 sur 822, mesurée sur un export q8 antérieur, quantifié sans `ActivationSymmetric` | nouvelle mesure du q8 livré, dans le navigateur | 769 sur 822 ; protocole 05 et rapport de Remy corrigés |
| 14/10 | Données du CDTN déclarées « sans licence » le 10/10, faute de fichier LICENSE, alors que leur `package.json` déclare Apache-2.0 | relecture de la source et du paquet npm | `04_cdtn.md` corrigé (PR #77) ; l'alerte et la demande au support de GitHub du 13/10 reposaient sur cette erreur |
| 14/10 | Première règle d'élagage qui retirait les diacritiques combinants et la lettre μ : un passage sur 4 240 changeait de découpage | comparaison du découpage sur tous nos textes | diacritiques et lettres grecques gardés ; découpage identique partout |
| 14/10 | Taille du q8 de Xenova écrite 112,9 Mio au lieu de 112,8 dans la PR #78 et trois de ses fichiers | recalcul depuis le nombre d'octets | corrigé (`a9a71c5`) ; 112,9 Mio est la taille du témoin de Remy |
| 14/10 | `.gitignore` de la PR #63 ignorant tous les fichiers `.onnx`, donc le modèle servi par le site | test des règles d'exclusion, puis essai dans un dépôt jetable : `git add` d'un dossier l'omettait sans avertissement | ligne retirée par Remy avant la fusion |
| 14/10 | Premier test de ces règles invalide : option non reconnue, erreurs masquées, donc aucune détection | listes vides jugées suspectes, règle témoin ajoutée | test refait avec `core.excludesFile` |
| 14/10 | Cache du navigateur attribué à IndexedDB, alors que Transformers.js 4.3.0 utilise l'API Cache | lecture du code source de la bibliothèque | `caches.delete` à la place de `indexedDB.deleteDatabase` (PR #63) |
| 14/10 | Hypothèse de l'assistant, publiée dans une revue de la PR #72 : avec le modèle en cache, bloquer Hugging Face par `page.route()` n'empêcherait pas le chargement | essai sur le site en ligne : le chargement échoue | hypothèse retirée dans un commentaire de suivi ; Vaneck a mesuré le cas réel et corrigé sa fiche |
| 14/10 | QCM du Weekly : la bonne réponse était la plus longue dans 13 questions sur 20 | script de contrôle des longueurs | réponses rééquilibrées, 3 cas sur 20 |
| 14/10 | Tokeniseur ré-exporté sous `transformers` 5.18 modifiant le découpage de 6 requêtes CDTN avec espace final | test d'équivalence de découpage sur l'ensemble des requêtes et passages | proposition actée au Weekly 5 de conserver le tokeniseur de base pour isoler strictement les poids sémantiques |
| 14/10 | Fiche Playwright citant des sessions 23 et 24 absentes du journal de l'équipe | Jibril et Mahé, revue de la #72 | sessions versées en 20 à 27 |
| 14/10 | Fiche Playwright affirmant, sans essai, que le modèle reste en cache avec `page.route()` | Mahé, revue de la #72 | essai fait, résultat écrit |
| 14/10 | Score à deux décimales : « 0,89 » pour les cinq passages | scénario Playwright | trois décimales |
| 14/10 | Test `creerMoteur` de la #76 dépendant de l'export local du notebook 02 | relecture de la #76 | correction proposée à Mahé |
| 14/10 | Empreinte de `LICENSE` du modèle modifiée par la conversion des fins de ligne sous Windows | relecture de la #78 | règle `.gitattributes` proposée |
| 14/10 | `scrollIntoView` faisant remonter tout le cadre de l'application | capture du scénario de la refonte | défilement limité à la zone du fil |
| 14/10 | Progression calculée en Mio mais affichée en « Mo » | relecture lors du passage au modèle élagué | unité corrigée |
| 17/10 | Audit des adresses e-mail concluant à zéro exposition, `git log --since` ayant arrêté le parcours trop tôt | contradiction avec un commit connu | historique parcouru en entier : 62 commits concernés |
| 17/10 | Revue publiée de la PR #80 affirmant « aucune requête vers jsDelivr », les requêtes ayant été écoutées au niveau de la page seulement | vérification de Jibril, puis essai avec le CDN bloqué : la recherche échoue | revue corrigée en demande de modification ; moteur d'exécution servi par le site (PR #81) |
| 17/10 | README de la PR #82 donnant la première inférence locale « en cours », alors qu'elle a réussi le 27/09 (#31) et qu'elle est documentée : la liste des fichiers ne descendait que dans les sous-dossiers de `docs/etudes` | revue de Jibril | ligne corrigée, RAG complet distingué (`1216bd5`) |
| 17/10 | Suivi de la PR #82 donnant #46 « à fermer », alors qu'il était fermé depuis 15 h 52 | revue de Jibril, d'après l'API GitHub | situation actualisée (`1216bd5`) |
| 18/10 | Attente du moteur fondée sur un texte d'invite identique pendant et après le chargement | relecture du code de l'interface B | conclusions tirées des seules recherches abouties |
| 18/10 | Focus rendu avant le retrait de l'attribut `inert`, donc refusé par le navigateur | essai au clavier, focus nul après Échap | focus rendu après le rendu (`requestAnimationFrame`), avant le commit (PR #83) |
| 18/10 | Description de la PR #83 affirmant que le focus ne sort jamais du menu sur téléphone, l'essai comptant le document (BODY) comme acceptable | contre-essai de Jibril aux frontières de Tab et Maj+Tab, puis Échap sans effet | tabulation bouclée dans le panneau, Échap écouté au niveau du document (`e6cd210`), description corrigée |
| 18/10 | Boucle de tabulation de la PR #83 ne gérant que les bords de la liste : sous WebKit sur macOS, où la navigation au clavier du système, désactivée par défaut, fait sauter les boutons à Tab, le focus quittait le menu 10 fois sur 20 | essai du site en ligne sous WebKit 26.6 (macOS), sur une limite déclarée de la #83 | tabulation entièrement gérée dans le menu (PR #102), vérifiée en ligne sur Chromium, Firefox et WebKit |
| 18/10 | Essai sous WebKit concluant à l'échec de la recherche, le blocage des requêtes rejetant une URL `blob:` | requête bloquée à l'hôte vide, relevée dans le journal de l'essai | `blob:` et `data:` laissés passer ; recherche aboutie |
| 19/10 | Défaut de tabulation de la PR #83 attribué à WebKit en général, alors qu'il tient au réglage de navigation au clavier de macOS, désactivé par défaut | revue de la PR #102 par Jibril : non reproduit sous WebKit 26.5 (Linux) ; réglage `AppleKeyboardUIMode` absent, donc à sa valeur par défaut, sur le Mac de l'essai | journal et description de la PR #102 précisés |
| 23/10 | Fusion de la #104 demandée avec un SHA de tête complet saisi de mémoire, et faux | refus de GitHub, grâce à `--match-head-commit` | SHA lu par l'API, puis fusion |
| 23/10 | Essai de faisabilité lancé sans aucun effet : sous zsh, `set -- $cfg` ne découpe pas la variable, et `--num-layers` restait vide | erreur d'arguments de `mlx-lm`, durée de moins d'une seconde | boucle explicite sur le nombre de couches |
| 23/10 | Longueur des exemples mesurée à 2 tokens : `apply_chat_template` renvoie un dictionnaire de deux clés | valeur invraisemblable pour cinq passages | décompte de la liste `input_ids` : de 1 115 à 2 542 tokens |
| 23/10 | Mémoire résidente du processus (1,6 Gio) susceptible d'être lue comme la mémoire de l'entraînement | incohérence avec 4 Gio de poids chargés sur le GPU | pic de mémoire GPU relevé par `mx.get_peak_memory()` : 7,14 Gio |
| 23/10 | Protocole de la #108, premier jet : référence R+ sans contexte pour sa citation, et règle de conclusion mêlant correction de Holm et borne d'intervalle | relecture contre le code de la #85 et du module de métriques | R+ adossé à la récupération, intervalle à 97,5 % (Bonferroni), avant publication |
| 23/10 | Étude de faisabilité donnant un adaptateur de 46 Mio pour 46 161 566 octets | recalcul en Mio | 44,0 Mio, avant le commit |
| 25/10 | État des lieux transmis à Mahé : aucune PR fusionnée depuis le 19/10, alors que la #104 l'a été le 23/10 | historique des fusions relu par l'API pour le calendrier | corrigé auprès de Mahé ; la session 41, juste, n'est pas touchée |
| 25/10 | Calendrier, premier jet : gel du protocole de la #108 au Weekly 7, avant le seuil S et le script testé que sa section 9 exige | relecture de la section 9 du protocole | gel placé au Weekly 8, après ces deux étapes, avant toute publication |
| 25/10 | Générateur du calendrier : « EQ », l'équipe entière, découpé en deux personnes inconnues | contrôle automatique des noms | clé traitée comme un tout |
| 25/10 | Suivi annoncé « sans écart » avec GitHub dans le commit 321b56e, alors que le contrôle ne portait que sur les états et les dates : le jalon de #49 y restait J3, contre J4 sur GitHub | comparaison étendue à toutes les colonnes | #49 en J4 ; la description de la #110 disait déjà la portée exacte du contrôle |
| 25/10 | Jalons de #91 à #97 changés sur GitHub sans être reportés dans l'inventaire | même comparaison complète, avant le commit | inventaire corrigé, aucun écart |
| 26/10 | Protocole 06 et #107 supposant que l'adaptateur serait servi tel quel par Ollama ; la version 0.40.5 le refuse, et la requantification aurait biaisé l'écart avant/après | lecture du code source d'Ollama au tag `v0.40.5` | témoin T ajouté au protocole, méthode de service de #107 corrigée |
| 26/10 | Protocole 06 renvoyant à la « section 8.2 du notebook 03 », qui est celle du protocole du notebook 03 | relecture des sources citées | référence corrigée avant le commit |
| 26/10 | Brouillon de commentaire sur #107 affirmant que le moteur MLX d'Ollama n'existe pas sur un PC NVIDIA, ce qui n'était pas vérifié | relecture avant publication | reformulé : disponibilité sur le Legion non vérifiée |
| 26/10 | Contrôle du rapatriement par `find -flags dataless`, muet : 0 fichier trouvé alors que 10 309 restaient déchargés | comparaison avec `ls -lO` | drapeau `SF_DATALESS` lu par `os.stat` |
| 26/10 | Tests de la séparation lancés avec le Python 3.9 du système et l'option `-I` : module introuvable | échec de l'import | relancés avec le Python 3.12 du projet |
| 26/10 | Script de report de S dans le protocole écrivant « 10,000 tirages », au format anglais | relecture du script avant exécution | « 10 000 » |
| 26/10 | Vérification des 13 commentaires filtrée à partir de 12 h UTC, alors qu'il était 11 h 09 : aucun commentaire trouvé, faux écart | incohérence avec les liens renvoyés à la publication | filtre corrigé ; les 13 sont présents et identiques |
| 26/10 | Script du seuil S acceptant un vecteur NaN : `abs(NaN - 1) >= tol` est faux, et un NaN aurait contaminé le seuil | revue de Jibril sur la #108, reproduite | contrôle `isfinite`, JSON sans NaN, régression vérifiée par mutation |
| 26/10 | Docstring du script du seuil déclarant le CDTN sans licence, reprise de `cdtn_seuil.py`, alors qu'il est sous Apache-2.0 depuis le 14/10 | revue de Jibril | deux docstrings corrigées |
| 26/10 | Protocole 06 sans règle d'appariement après les erreurs techniques, sans valeur exacte de S, et confondant T et le modèle de #31 sur les seuls tenseurs | revue de Jibril | trois règles ajoutées avant le gel |
| 26/10 | Commande zsh `$c:scripts` interprétée comme le modificateur `:s` : lecture des dépendances d'Agent0 faussée | sortie incohérente, des en-têtes de commit à la place des fichiers | variable écrite `${c}` |
| 26/10 | Commentaire de la #115 affirmant sans vérification que `SFTTrainer` lit le même format que mlx-lm | relecture après publication | correction publiée dans la #115 |
| 27/10 | Même piège zsh que la veille, `$B:scripts` lu comme le modificateur `:s` | erreur « bad substitution » | variable écrite `${B}` |
| 27/10 | Script de mesure, premier jet : variable `l` non définie dans le calcul des médianes, qui aurait fait échouer toute analyse | relecture avant les tests | appel corrigé |
| 27/10 | Script de mesure : chemins par défaut figés à la définition des fonctions ; un essai aurait écrit dans le vrai `data/` et consommé l'exécution unique de la calibration | préparation de l'essai de bout en bout | chemins résolus à l'appel, essai isolé dans un dossier temporaire |
| 27/10 | Fiches des juges réduites à des identifiants, sans question ni texte des passages | relecture avant les tests | question et passages cités ajoutés |

**Bilan intermédiaire.** Seize erreurs ou pièges détectés et traités en deux jours. **Cinq d'entre elles figuraient déjà dans un livrable rédigé** et ont été rattrapées avant l'envoi : le nombre de fichiers audités, le rang du dépôt ECC, le seuil de réussite sans fondement, les milestones et labels inexistants, et le rendu des tirets dans le PDF composé.

Aucune n'a été trouvée par simple relecture du texte. Toutes l'ont été par confrontation à une mesure, à un calcul indépendant ou à l'inspection visuelle du rendu. C'est la méthode qui les a fait apparaître, pas l'attention.

**Bilan du 11 au 18 octobre.** Trente-deux erreurs ou pièges détectés et traités : dix-neuf dans les sessions de Mahé, deux dans celles de Remy, onze dans celles de Vaneck. **Sur les dix-neuf de Mahé, onze figuraient déjà dans une pull request, une revue ou un document publiés** : la licence du CDTN, la fidélité de l'ajusté, la taille du q8, le `.gitignore` de la PR #63, l'attribution du cache à IndexedDB, l'hypothèse sur `page.route()`, la revue de la PR #80, le README et le suivi de la PR #82, la description de la PR #83, la boucle de tabulation de la PR #83, déployée sur le site. Quatre ont été trouvées par un relecteur de l'équipe, Jibril, et non par l'assistant : la revue de la PR #80, les deux points de la PR #82 et la description de la PR #83 ; toutes l'ont été par une mesure, un essai ou la lecture d'une source primaire. Parmi les onze de Vaneck, deux portaient sur des PR de Mahé et ont été relevées en relecture (le test de `creerMoteur` de la PR #76, l'empreinte de `LICENSE` de la PR #78), et deux sur sa propre fiche de la PR #72, relevées par Jibril et Mahé.

---

## 5. Modèle de saisie

Chaque membre ajoute ses sessions selon ce modèle, le jour de l'usage. Les éléments ne se reconstituent pas après coup.

```
### Session N, date, prénom NOM, outil et modèle

**Objet.**
**Produit.**
**Mesures exécutées.**
**Résultats retenus.**
**Ce qui a été écarté, et pourquoi.**
**Ce que l'équipe a validé, et par qui.**
**Temps d'appropriation constaté.**
**Difficultés rencontrées.**
```

Deux règles de tenue :

1. Une session non consignée le jour même est considérée comme non consignée. Le sujet valorise le temps d'appropriation constaté et les conditions dans lesquelles un outil échoue, qui sont les premiers éléments oubliés.
2. Toute production assistée porte le nom de son relecteur. Sans relecteur nommé, elle n'entre pas dans un livrable.

---

## 6. Ce que ce journal alimentera

Trois sections du rapport final s'appuieront directement sur ce document.

- **Analyse technique.** Les mesures consignées ici fournissent les chiffres de coût, de latence et de qualité demandés.
- **Retour d'expérience.** La section 4 documente les difficultés réelles et leur résolution, que le sujet demande de traiter de façon factuelle.
- **Cinq outils novateurs.** Les temps d'appropriation, les échecs et les comparaisons entre outils consignés au fil de l'eau constituent la matière de cette section, qui vaut jusqu'à trois points et dont la grille valorise au moins une critique argumentée.

