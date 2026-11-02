# Support de présentation — Jalon J3 (15 points)
**Module** NLP 2 · Master 2 Data & IA · FGES — Université Catholique de Lille  
**Équipe** Data Tigers : Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE  
**Statut** Version consolidée pour le Weekly 8 (Ticket #112) · Base chiffrée issue de la PR #124  
**Responsables des supports** : Vaneck DAGAR (plan et contenu) & Remy RAYANE (assemblage et coordination)

---

## Diapositive 1 — Titre, Équipe et Cadrage du Jalon J3

### Contexte & Rappel des deux volets imposés
Le projet impose la réalisation conjointe de deux applications complémentaires basées sur le corpus du droit du travail (fiches pratiques du Ministère du Travail, instantané SocialGouv du 11 septembre 2026 : 261 fiches, 4 240 passages) :

* **Volet A (Application en ligne)** : Cas A3 — Moteur de recherche sémantique dense sans serveur.
  * Inférence 100 % client dans le navigateur (Transformers.js / WebAssembly / ONNX Runtime Web).
  * Coût d'exploitation nul : hébergement statique sur GitHub Pages, aucun appel API externe.
* **Volet B (Application locale)** : Cas B1 — Assistant juridique interactif avec chaîne RAG.
  * Inférence locale sur modèle open-weights (`Qwen2.5-7B-Instruct` sous Ollama 0.40.13, version épinglée par l'arbitrage du 02/11).
  * Adaptation du modèle par fine-tuning LoRA (MLX 4 bits sur Mac M4 Pro), sourçage formel des réponses (`[Pn]`) et évaluation rigoureuse avant/après.

### Objectifs du Jalon J3 (15 points)
1. **Volet A finalisé et déployé** : Moteur de recherche sémantique réactif, modèle élagué hébergé sous le quota strict de 100 Mio, seuil d'abstention 0,8560 et contrastes vérifiés au niveau AA des WCAG 2.1.
2. **Volet B engagé** : Socle RAG opérationnel, protocoles de mesure (Protocole 06, #108) et de séparation (#115) verrouillés, faisabilité matérielle du fine-tuning démontrée.
3. **Supports et méthodologie** : Démonstrations reproductibles, tenue rigoureuse du board et journal d'usage IA auditable (45 sessions, 87 erreurs documentées).

---

## Diapositive 2 — Volet A : Architecture technique & Déploiement sans serveur

### Contraintes & Choix d'ingénierie
* **Inférence 100 % in-browser** : Aucun backend Python en production. L'application est servie comme site statique via GitHub Pages.
* **Moteur d'exécution** : Transformers.js adossé à ONNX Runtime Web (WebAssembly / SIMD).
* **Encodeur dense** : `multilingual-e5-small` quantifié en 8 bits (q8) pour concilier compacité et fidélité de représentation sémantique.
* **Asymétrie de l'encodage E5** : Préfixe obligatoire `query: ` pour la requête utilisateur et `passage: ` pour les documents indexés, garantissant le respect de la géométrie de l'espace latent.

### Optimisation du chargement et du calcul
* **Normalisation L2 préalable** : Les vecteurs de passages et de requêtes sont normalisés unitairement (norme euclidienne égale à 1). La similarité cosinus est alors rigoureusement équivalente à un produit scalaire en O(d) (d = 384).
* **Index binaire Float32 & Métadonnées** : `moteur.js` lit la matrice des vecteurs directement en mémoire typée (`Float32Array`) via `index.bin` et charge les métadonnées documentaires via `JSON.parse`.
* **Réactivité mesurée** :
  * **18,3 ms** pour encoder une requête avec le modèle élagué dans le navigateur (`scripts/allegement/README.md`, ligne 44) ; les 18,6 ms mesuraient le q8 d'origine non élagué (notebook 02).
  * Recherche par produit scalaire matriciel quasi-instantanée côté client.

---

## Diapositive 3 — Volet A : Allègement du modèle & Levée du blocage d'hébergement (#50)

### Le verrou technique GitHub Pages
* **Limite stricte par fichier** : GitHub bloque tout fichier supérieur à 100 Mio.
* **Le modèle standard intenable** : Le modèle `multilingual-e5-small` quantifié q8 d'origine pèse **112,8 Mio**, interdisant son hébergement direct sur le dépôt GitHub du site sans recourir au CDN externe Hugging Face (point de défaillance tiers proscrit par l'audit du sujet).

### Analyse structurelle & Élagage sans perte
* **Diagnostic de l'architecture** : L'analyse des tenseurs révèle que **81,6 % des paramètres** de l'encodeur sont concentrés dans la table d'embeddings du vocabulaire (250 037 lignes de 384 dimensions), conçue pour couvrir plus de 100 langues.
* **Recette d'élagage ciblé** (`scripts/allegement/`) :
  * Détection de tous les sous-mots réellement requis par le corpus juridique français M2 (261 fiches, 4 240 passages), le jeu d'évaluation et les requêtes courantes.
  * Réduction de la matrice d'embeddings aux seuls tokens nécessaires, sans modifier les couches d'attention ni de feed-forward du Transformer.
* **Résultats obtenus** :
  * Poids du modèle abaissé de **112,8 Mio à 65,7 Mio** (**-41,8 %**).
  * **Parité bit à bit stricte** : 100 % d'identité vectorielle vérifiée sur les 822 requêtes de contrôle par rapport au q8 de référence dans le navigateur (source : `scripts/allegement/README.md`, ligne 44, et non le README racine ; pour tout texte en alphabet latin ou grec).
  * Modèle servi directement en local depuis `front/public/modele/`, garantissant l'autonomie totale du site.

---

## Diapositive 4 — Volet A : Évaluation quantitative & Règle d'abstention (#46, #53)

### Chaîne d'évaluation de l'Information Retrieval (IR)
* **Jeu de test annoté figé** (`jeu-questions-v1`, tag `cdb48c9`) :
  * **73 questions du corpus** (couvrant 61 fiches) et **24 questions hors corpus**, totalisant 97 questions de référence.
  * Les 155 requêtes du Code du Travail Numérique (CDTN, #56) forment un second jeu indépendant analysé à part (`04_cdtn.md`) pour calibrer le seuil et comparer E5 à BM25 V3.
* **Comparaison appariée face à la baseline BM25 V3** :
  * **Au niveau du passage** : Recall@5 de **43,8 %** pour l'encodeur servi contre **42,5 %** pour BM25 de référence (+1,4 point, IC 95 % de -11,5 à +14,3, test exact de McNemar p = 1,000).
  * **Au niveau de la fiche** : Recall@5 de **83,6 %** pour l'encodeur contre **79,5 %** pour BM25 (+4,1 points).
  * **Critère de validation du J2** : La **non-infériorité** à la marge de 15 points est statistiquement démontrée (score de Tango : z = 2,45, p unilatéral 0,007). Aucun des deux systèmes n'est démontré supérieur.
* **Fidélité de la quantification** : Le passage de FP32 à q8 ne coûte qu'**une question sur 73**, sans écart statistiquement significatif.

### Mécanisme d'abstention active (#53)
* **Seuil d'abstention fixé à 0,8560** : 5e centile des scores maximaux de 479 variantes du CDTN, figé le 10 octobre avant toute mesure (`moteur.js`).
* **Séparation corpus vs hors corpus** : L'AUC atteint **0,841** (IC 95 % : [0,747 ; 0,921]), mesurant la capacité discriminante du score maximal.
* **Comportement effectif** : Le seuil rejette 9 questions hors corpus sur 24 et conserve 72 questions du corpus sur 73. L'affichage d'un message d'avertissement invite l'utilisateur à reformuler si le score maximal passe sous 0,8560.

---

## Diapositive 5 — Volet B : Socle RAG & Inférence locale (#31, #51, PR #85)

### Architecture de la chaîne locale
* **Modèle génératif open-weights** : `Qwen2.5-7B-Instruct` servi localement sous Ollama (version épinglée **0.40.13**, arbitrage du 02/11, mises à jour automatiques coupées) au format quantifié 4 bits (GGUF Q4_K_M, 4,36 Gio sur disque).
* **Index commun et récupération** : Réutilisation stricte de l'index des 4 240 passages du corpus M2 (`passages_m2.json`), garantissant la cohérence documentaire entre Volet A et Volet B.
* **Injection contextuelle certifiée** (`rag-b1-v1`) :
  * Récupération des 5 passages les plus pertinents par E5 en FP32.
  * Construction dynamique du prompt de contexte (fenêtre de 8 192 tokens, réponse bornée à 512 tokens) via la fonction `construire_contexte` (`scripts/rag/rag.py`).

### Cadrage de la génération & Sourçage
* **Consigne système stricte** : Interdiction formelle d'extrapoler ; obligation d'appuyer chaque assertion sur une citation explicite `[P1]` à `[P5]`.
* **Performances indicatives relevées** : Débit de **47 à 67 tokens/s** mesuré sur deux appels avec prompt court sous Ollama (débit d'inférence interactif).
* **Auditabilité** : Contrôle automatique de la conformité des citations via `valider_citations` (PR #85).

---

## Diapositive 6 — Volet B : Faisabilité de l'adaptation LoRA (Mac vs Legion, #107)

### Cadrage expérimental (Étape 1 de #107)
* **Objectif** : Vérifier sur banc d'essai qu'un fine-tuning LoRA (rang 8) de `Qwen2.5-7B` en 4 bits tient en mémoire avec des longueurs réelles de contexte RAG (1 115 à 2 542 tokens, médiane 1 746 tokens).
* **Protocole d'isolation métrologique** : Mesure sur données cibles fixes évaluant le pic GPU et la durée incrémentale par itération (différence entre 6 et 12 pas).

### Comparaison métrologique des deux machines
| Métrique (LoRA 16 couches) | MacBook M4 Pro (PR #109, Mahé) | PC Legion RTX 5070 Laptop (PR #118, Jibril) |
|---|---|---|
| **Environnement matériel** | Apple M4 Pro · 24 Gio unifiées | Intel i7 · RTX 5070 Laptop (8 Gio VRAM) |
| **Logiciel & Pilotes** | macOS 27.0.1 · MLX 0.32.4 · Metal | Windows 11 · PyTorch 2.11 · CUDA 12.8 · NF4 |
| **Pic de mémoire GPU** | **7,14 Gio** (compteur Metal) | **9,17 Gio alloués** (PyTorch) |
| **Capacité & Marge** | Plafond Metal à 17,76 Gio (**~10,6 Gio de marge**) | 7,96 Gio physiques (**0 octet libre**, dépassement) |
| **Comportement mémoire** | Exécution unifiée fluide sans contention | Débordement vers RAM système (hypothèse forte) |
| **Durée par itération** | **10,5 s** (23/10) puis **8,8 s** (30/10) | **273,9 s (4 min 34 s)** — facteur x26 |

### Arbitrage opérationnel
* **Machine retenue pour l'entraînement** : Le **MacBook M4 Pro** est la seule des deux machines mesurées adaptée à l'entraînement LoRA (~1 h 30 pour 1 époque de 500 exemples).
* **Répartition des tâches** : Entraînement LoRA sur Mac M4 Pro ; conversion, déploiement Ollama et chaîne de mesure hébergés sur le PC Legion.

---

## Diapositive 7 — Volet B : Étanchéité des données & Chaîne de conversion GGUF (#107, PR #115)

### Contrôle formel de séparation des données (PR #115)
* **Règle d'étanchéité absolue** : Aucune donnée d'apprentissage ne doit provenir des fiches du lot de test humain, et aucune question humaine ne doit être apprise.
* **Validation outillée par script** (`scripts/adaptation_qwen/separation.py`) :
  * Exclusion formelle des **61 fiches documentaires** touchées par le lot de test (empreinte SHA-256 : `ba0135f4f3acfc2901a43b90dc0bf521bccf5e83b91bf2cb63e9ff526d498ea7`).
  * Rejet automatique si un passage (cible ou distracteur E5) provient d'une fiche exclue.
  * Rejet de toute question reprenant mot pour mot une question humaine (calibration comprise).
* **Format d'entraînement** : Fichiers JSONL (`train.jsonl`, `valid.jsonl`) au format `messages` standard compatible `mlx_lm.lora` avec prompt `rag-b1-v1`.
* **Équilibrage** : Ratio d'abstentions calé sur la part exacte du lot de test (24 / 97 ≈ 24,7 %), combinant questions hors corpus (8 thèmes) et passages retirés.

### Chaîne d'export et Modèle Témoin T
* **Contrainte Ollama 0.40.13** : Rejet de la directive `ADAPTER` (`errAdaptersUnsupported`) imposant une fusion en amont.
* **Chaîne de déploiement** :
  1. Fusion des poids LoRA dans le modèle de base en demi-précision FP16.
  2. Conversion du modèle fusionné en GGUF.
  3. Requantification 4 bits (Q4_K_M).
* **Nécessité du Modèle Témoin T** : Pour isoler le gain sémantique propre à LoRA sans le confondre avec les artefacts d'arrondi de la requantification, un **témoin T** (modèle de base subissant exactement le même cycle fusion/requantification GGUF sans LoRA) est évalué en parallèle.

---

## Diapositive 8 — Volet B : Protocole d'évaluation comparative avant/après (#52, PR #108)

### Le Protocole 06 (PR #108)
* **Comparaison appariée stricte** : Évaluation conjointe du modèle de base nu (B0), du RAG sans consigne (B1), du RAG avec consigne et seuil (B2), face au modèle adapté et au témoin T sur les mêmes 97 questions d'évaluation.
* **Les 5 métriques officielles (M1 à M5)** :
  * **M1** : Taux d'abstention correcte sur les 24 questions hors corpus.
  * **M2** : Taux de fausse réponse affirmative sur les 24 questions hors corpus.
  * **M3** : Taux d'abstention à tort sur les 73 questions du corpus.
  * **M4** : Taux de citation valide et pertinente selon la règle D4 du notebook 03 sur les 73 questions du corpus.
  * **M5** : Exactitude juridique jugée à l'aveugle par deux annotateurs sur échantillon.

### Métrologie & Évaluation humaine aveugle
* **Seuil de décision S = 0,8565** : 5e centile des scores maximaux calculé sur les 103 requêtes du CDTN (479 variantes), IC 95 % par rééchantillonnage bootstrap : [0,8464 ; 0,8653].
* **Double évaluation à l'aveugle** : Attribution de l'évaluation qualitative à deux juges indépendants (Vaneck et Maïmouna) sans indication du modèle source.
* **Statut à J3** : Protocole 06 figé, seuil S calculé ; la mesure avant aura eu lieu à J3, à recompter le 13/11.

---

## Diapositive 9 — Méthodologie, 5 Outils Novateurs & Feuille de route jusqu'à J4

### Rigueur méthodologique & Traçabilité de l'usage de l'IA
* **Traçabilité totale** : **45 sessions** d'assistance IA consignées à date au fil de l'eau ([docs/journal/JOURNAL_USAGE_IA.md](docs/journal/JOURNAL_USAGE_IA.md)).
* **Culture de la preuve** : **87 erreurs**, hallucinations ou pièges matériels documentés et rectifiés par confrontation aux sources primaires et mesures réelles.
* **Cinq outils novateurs (Bonus +3 points)** :
  1. *Transformers.js* : Moteur d'inférence sémantique client-side WebAssembly sans serveur.
  2. *ONNX Runtime (Web / Python)* : Pivot d'interopérabilité et garantie de parité des tenseurs.
  3. *Playwright* : Automatisation des tests de non-régression multi-navigateurs et audit d'accessibilité.
  4. *GitHub CLI (`gh`)* : Traçabilité des issues, revues de PR et audits de contribution.
  5. *Assistants IA (Antigravity, Claude Code, Codex)* : Retours d'expérience comparatifs et critiques argumentées.

### Calendrier resserré jusqu'à la Soutenance (30/11)
* **30/10 (acté le 02/11)** : Données d'adaptation générées (#107, lot v1 à 298 exemples) ; PR #115 validée et fusionnée le 02/11.
* **03/11 au plus tôt** : Gel du protocole de mesure, reporté du 02/11 (#108, section 9 : B0 doit être recalibré sous Ollama 0.40.13).
* **04/11 au plus tôt** : Mesure avant adaptation (#52), consécutive au gel du protocole.
* **04/11 (Weekly 8)** : Plan arrêté des supports de J3 (Vaneck & Remy) et clôture actée du ticket #49.
* **05/11** : Relecture d'un échantillon de 30 exemples des données d'adaptation (#107, PR #125).
* **06/11** : Entraînement LoRA sur Mac M4 Pro (#107, étape 5, PR #125).
* **10/11** : Construction du témoin T et déploiement du modèle adapté sous Ollama.
* **12/11** : Mesure comparative après adaptation (point d'arrêt opérationnel).
* **13/11** : Jugement humain qualitatif, assemblage final des supports et fiches d'outils.
* **16/11 (Jalon officiel J3)** : Volet A fonctionnel et Volet B adapté présentés.
* **19/11** : Livraison de la **V1 du rapport final** (#113).
* **20/11** : Fin du projet : supports et site figés.
* **30/11 (Jalon J4)** : Soutenance finale du projet.
