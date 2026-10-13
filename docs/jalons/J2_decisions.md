# Jalon J2 — décisions et éléments de cadrage

**Équipe** Mahé BEGNIS · Remy RAYANE · Jibril BENSALEM · Vaneck DAGAR · Maïmouna SIGNATE
**Module** NLP 2 · M2 Data & IA · FGES — Université Catholique de Lille · enseignant ROSARI Adrian
**Date** 19/09/2026 — J2 le **21/09/2026** (lundi), courriel de confirmation le **20/09/2026** (dimanche)
**Statut** document de travail du 19/09/2026, antérieur au rapport de jalon J2 (`docs/jalons/J2_rapport.md`), qui fait foi. Trois points y ont été révisés depuis : le corpus (`AgentPublic/travail-emploi`), les seuils de réussite (exprimés en écarts appariés face à une baseline) et le second modèle du volet B (`Mistral-7B-Instruct-v0.3`, `Qwen3-8B` passant en réserve). Versé tel quel le 27/09/2026 (#33) pour la traçabilité des mesures.

---

## 0 — Conformité aux attendus du jalon

Le sujet §5 énonce cinq attendus. Voici où chacun est traité.

| Attendu J2 (texte du sujet) | Traité en | État |
|---|---|---|
| « Environnement de développement déclaré. Une convergence au sein de l'équipe est préférable ; une divergence déclarée n'est pas pénalisée. » | §2 | ✅ déclaré, divergence assumée |
| « Board de tickets créé : colonnes définies, membres ajoutés. Le remplissage n'est pas exigé à ce stade. » | §3 | ☐ à créer avant le 21/09 |
| « Étude du volet A : cas d'usage retenu, modèle envisagé, faisabilité de l'exécution navigateur » | §4 | ✅ **faisabilité mesurée en navigateur réel** |
| « Étude du volet B : modèle open-weights identifié, machine cible, contrainte mémoire estimée » | §5 | ✅ modèle et budget mémoire calculés ; ☐ seconde machine à mesurer |
| « Éléments de cadrage : périmètre, risques identifiés, répartition initiale des tâches » | §6, §7, §8 | ✅ |

**Le panier des cinq outils novateurs ne fait pas partie des attendus de J2.** Vérification faite dans le sujet : la section « Montée en compétence et bonus » (§4 du sujet) décrit **une section du rapport**, et la liste des attendus J2 ne la mentionne pas. Nous la traitons donc en §10, comme un chantier à ouvrir immédiatement mais à livrer au rapport.

---

## 1 — Équipe, rôles et modalités de décision

### 1.1 Rôles transverses

| Rôle | Titulaire | Ce que cela recouvre |
|---|---|---|
| **Gestion du board** | **Jibril BENSALEM** | création et tenue du board, contrôle que chaque tâche a un ticket **créé avant** la réalisation, revue hebdomadaire |
| **Journal d'usage de l'IA** | **Mahé BEGNIS** | tenue du journal exigé par le sujet, classeur de suivi, rappel de la règle à l'équipe |
| **Lead technique** | **Mahé BEGNIS** | arbitrage des choix techniques en cas de désaccord, cohérence d'architecture entre les deux volets, revue des PR touchant le cœur du système |

Le rôle de lead technique est attribué sur un critère factuel : expérience professionnelle antérieure sur des chaînes de recherche sémantique et de RAG, c'est-à-dire exactement les deux cas retenus.

### 1.2 Faut-il déclarer le lead technique dans le rapport de J2 ?

**Oui, et voici pourquoi.** Le sujet demande, au titre du retour d'expérience : « Organisation retenue et **modalités de décision** ». Un arbitre technique désigné *est* une modalité de décision. Ne pas l'écrire reviendrait à masquer une partie de notre organisation réelle, ce que le sujet sanctionne implicitement en annonçant qu'il croisera nos affirmations avec le dépôt et le board.

**Mais avec trois précautions, sans lesquelles le rôle devient un handicap :**

1. **Arbitrage, pas monopole.** Le sujet impose que « chaque tâche a au moins un responsable identifié » et vérifiera « une répartition des contributions cohérente avec la répartition des tâches déclarée ». Un lead technique dont les commits couvrent tout le dépôt contredirait la répartition en binômes que nous déclarons.
2. **Le lead porte aussi un domaine technique nommé** (§8), au même titre que les autres. Le rôle transverse s'ajoute à un domaine, il ne le remplace pas.
3. **Le rôle se documente par ses effets**, pas par son titre : chaque arbitrage rendu donne lieu à une décision écrite dans le dépôt (une ADR courte, ou un commentaire de ticket). C'est ce qui rendra le rôle crédible en soutenance — et ce qui alimente la section « arbitrages » que le sujet valorise explicitement.

> Formulation retenue pour le rapport : *« Un lead technique est désigné pour trancher les désaccords techniques et garantir la cohérence d'architecture entre les deux volets. Il n'a pas autorité sur la répartition des tâches, qui reste collective, et chaque arbitrage rendu est écrit. »*

### 1.3 Mode de travail

Travail **en binômes**, chaque membre ayant **un domaine principal et un domaine secondaire** — la forme explicitement recommandée par le sujet : « Une répartition efficace attribue à chacun un domaine principal et un domaine secondaire, en binôme avec un autre membre. » Détail en §8.

---

## 2 — Environnement de développement déclaré

### 2.1 Socle commun — convergence

| Outil | Version mesurée sur la machine de référence | Rôle |
|---|---|---|
| **VS Code** | 1.137.0 | éditeur commun |
| **Python** | **3.12.11** (venv dédié) | volet B, préparation du corpus, export ONNX |
| **PyTorch** | 2.14.0 | encodeur, export ONNX, bancs d'essai |
| **Node.js / npm** | v25.9.0 / 11.12.1 | volet A, Transformers.js, chaîne de build du site |
| **Git / GitHub CLI** | 2.50.1 / 2.92.0 | versionnage, board, CI |
| **uv** | 0.11.0 | gestion des dépendances Python |

> ⚠️ **Point à ne pas rater** : le `python3` du système est en **3.9.6**. Tout le travail passe par le venv en 3.12.11. Un script lancé avec le Python système échouera sur des dépendances absentes — c'est une cause de perte de temps classique, à annoncer à l'équipe.

### 2.2 Divergence déclarée — assistants de développement

Le sujet autorise explicitement la divergence dès lors qu'elle est déclarée. Nous en déclarons **une seule**, sur l'IDE augmenté par IA :

| Assistant | Qui | Pourquoi la divergence |
|---|---|---|
| **Claude Code** | les membres disposant d'un abonnement | abonnement payant, non détenu par toute l'équipe |
| **Google Antigravity** | les autres membres | plateforme d'agents de Google, téléchargement gratuit, build **Apple Silicon** disponible — vérifié le 19/09/2026 sur `antigravity.google` |

**Ce que cette divergence n'affecte pas** : le code produit, les dépendances, les formats de fichiers, les conventions de commit. Les deux assistants écrivent dans le même dépôt avec les mêmes règles.

**Ce qu'elle nous apporte** : un terrain de comparaison réel entre deux harnais sur les mêmes tâches — matière directe pour la section « outils novateurs » du rapport (§10), qui valorise précisément « la comparaison avec l'outil précédemment utilisé ».

**Règle commune, non négociable** : quel que soit l'assistant, *« tout membre de l'équipe peut être interrogé en soutenance sur n'importe quelle portion du code produit. Une réponse insuffisante affecte l'évaluation de l'équipe entière. »* Toute portion produite avec assistance passe en revue par le binôme, et le relecteur doit savoir l'expliquer.

---

## 3 — Board de tickets

### 3.1 Ce qui doit exister au 21/09

Le sujet : « colonnes définies, membres ajoutés. **Le remplissage n'est pas exigé à ce stade.** »

- ☐ Projet GitHub Projects v2 créé, **les 5 membres ajoutés**
- ☐ Colonnes `Status` : `Backlog` · `Ready` · `In progress` · `In review` · `Done` · **`Abandonné`**
- ☐ Champs personnalisés : `Volet` (A / B / Transverse) · `Jalon` · `Charge estimée` · `Responsable` · `Binôme`
- ☐ Milestones alignés sur les jalons notés : `Mi-parcours 01/10` · `J3 16/10` · `J4 07/12`
- ☐ Labels : `volet-a` · `volet-b` · `corpus` · `encodeur` · `front` · `rag` · `eval` · `doc` · `bonus-outils` · `bloquant`

La colonne **`Abandonné`** n'est pas décorative : le sujet écrit qu'« un projet qui documente les arbitrages (ie abandons de features) est supérieur à un projet qui prétend n'en avoir fait aucun ». Une fonctionnalité abandonnée se ferme avec le motif écrit.

### 3.2 Contraintes GitHub mesurées le 11/09/2026 (org `datatigersNLP`, plan Free, dépôt privé)

| Fonction | État mesuré | Contournement retenu |
|---|---|---|
| Protection de branche, rulesets | ❌ 403 « Upgrade to GitHub Pro or make this repository public » | convention écrite + Action refusant une PR sans ticket lié |
| **GitHub Pages** | ❌ indisponible sur dépôt privé en plan Free | **le dépôt du volet A sera public** (voir §4.2) |
| Automatisations Projects v2 | ⚠️ 4 workflows natifs seulement ; « issue assignée → Ready » n'existe pas | déplacement manuel, vérifié en revue hebdomadaire |
| GitHub Actions | ⚠️ minutes comptées sur dépôt privé | CI sur `pull_request` uniquement |

---

## 4 — Étude du volet A : **A3 — Recherche sémantique en corpus fermé**

### 4.1 Cas retenu et raison du choix

Le système retourne les passages pertinents d'un corpus normatif en réponse à une question en langage naturel, avec **score de similarité, référence de section et lien vers le document complet**. **Aucune génération** — le sujet l'exige, et l'architecture navigateur l'impose.

Trois raisons :

1. **Mutualisation maximale avec B1.** Corpus, découpage et couche de récupération sont écrits **une fois** et servis deux fois. A3 *est* la couche de récupération de B1. C'est le couple le plus économe des cinq étudiés (30–40 j·h contre 49–64 pour A5+B5).
2. **Pertinence professionnelle.** La recherche sémantique en corpus fermé est un besoin d'entreprise réel, et l'équipe dispose d'une expérience antérieure sur ce type de chaîne.
3. **Le point dur est le bon.** Le sujet le désigne lui-même : « La stratégie de découpage du corpus constitue un paramètre déterminant de la qualité des résultats. » C'est un problème d'ingénierie mesurable, pas un problème de puissance de calcul.

**La faiblesse connue de A3, et comment nous la traitons.** Le sujet valorise le modèle entraîné par l'équipe ; A3 utilise un encodeur pré-entraîné. Deux réponses, toutes deux mesurables : l'**élagage du vocabulaire** (§4.5) qui fait de l'encodeur servi un artefact que nous avons produit, et le **comparatif TF-IDF** (§4.6) qui oppose un index entièrement maîtrisé à l'encodeur neuronal.

### 4.2 Architecture retenue

```
hors ligne (Python)                     |   navigateur (JavaScript)
  corpus normatif                       |
    -> nettoyage, segmentation          |     requête utilisateur
    -> encodage des passages            |       -> encodeur ONNX (Transformers.js)
    -> index vectoriel (fichier .bin)   |       -> vecteur 384 dimensions
    -> publication en fichier statique  |       -> cosinus contre l'index chargé
                                        |       -> passages classés + score + référence
```

**Conséquence décisive : seule la requête est encodée dans le navigateur.** Les passages sont encodés hors ligne, une fois. Le navigateur ne fait donc jamais tourner l'encodeur sur plus de quelques dizaines de tokens.

**Hébergement** : fichiers statiques uniquement, conformément au sujet (« La plateforme d'hébergement ne sert que des fichiers statiques »). **Le dépôt du volet A sera public**, GitHub Pages en plan Free l'exigeant.

### 4.3 Modèle envisagé — comparatif mesuré le 19/09/2026

Tailles relevées en octets sur l'API Hugging Face. La limite dure de GitHub est de **100 MiB par fichier** (documentation officielle).

| Modèle ONNX | Poids quantifiés | Tokenizer | Total | Dim. | Vocab. | Versionnable ? |
|---|---:|---:|---:|---:|---:|---|
| **`Xenova/multilingual-e5-small`** | **112,8 Mio** | 16,3 Mio | **129,1 Mio** | 384 | 250 037 | ❌ > 100 MiB |
| `Xenova/paraphrase-multilingual-MiniLM-L12-v2` | 112,8 Mio | 16,3 Mio | 129,1 Mio | 384 | 250 037 | ❌ |
| `Xenova/distiluse-base-multilingual-cased-v2` | 129,0 Mio | 3,7 Mio | 132,8 Mio | — | 119 547 | ❌ |
| `Xenova/multilingual-e5-base` | 265,7 Mio | 21,1 Mio | 286,9 Mio | 768 | 250 002 | ❌ |
| `onnx-community/embeddinggemma-300m-ONNX` | 294,6 Mio | 19,4 Mio | 314,0 Mio | 768 | 262 144 | ❌ |
| `Xenova/bge-m3` | 543,3 Mio | 21,1 Mio | 564,4 Mio | 1024 | 250 002 | ❌ |
| `Xenova/all-MiniLM-L6-v2` | 21,9 Mio | 0,9 Mio | 22,8 Mio | 384 | 30 522 | ✅ mais **anglais uniquement** |

> **Piège évité.** L'API annonçait `embeddinggemma-300m` à 0,5 Mio : ses poids sont stockés dans des fichiers externes `.onnx_data`. La taille réelle est **294,6 Mio**. Un chiffre lu sans vérification aurait orienté le choix vers un modèle six fois plus lourd que celui retenu.

**Deux dépôts cités dans la littérature n'existent pas** : `Xenova/sentence-camembert-base` et `Xenova/gte-multilingual-base` renvoient tous deux une erreur 401.

**Modèle retenu : `Xenova/multilingual-e5-small`.** C'est le plus léger des encodeurs multilingues de qualité, en 384 dimensions — ce qui divise par deux la taille de l'index par rapport aux modèles en 768.

**Pourquoi aucun encodeur multilingue ne tient sous 100 MiB — calculé.** Le poids est dominé par la matrice d'embedding du vocabulaire XLM-R :

| Composant | Paramètres | Part |
|---|---:|---:|
| Matrice d'embedding (250 037 × 384) | 96,0 M | **81,8 %** |
| 12 couches d'encodeur | 21,3 M | 18,1 % |
| **Total** | **117,3 M** | |

En int8 : 117,3 Mo ≈ **112,0 Mio**, à comparer aux **112,83 Mio** mesurés — l'écart correspond aux biais et aux LayerNorm conservés en flottant. Le calcul est donc validé par la mesure.

### 4.4 Faisabilité de l'exécution navigateur — **mesurée, pas estimée**

Protocole : page statique servie en local, `@huggingface/transformers@4.3.0` chargé depuis jsDelivr, modèle `Xenova/multilingual-e5-small` en `dtype: 'q8'`, encodage d'une question en français, 20 passes après chauffe. Navigateur Chromium piloté par Playwright, sur la machine de référence (M4 Pro, 24 Gio).

| Mesure | Première visite | Visite suivante (cache) |
|---|---:|---:|
| Import de la bibliothèque | 87 ms | 5 ms |
| **Chargement du modèle** | **3 052 ms** | **568 ms** |
| **Inférence d'une requête (médiane sur 20)** | **19,8 ms** | 19,2 ms |
| Dispersion de l'inférence | min 18,8 ms · max 20,7 ms | — |
| Octets transférés | **135,6 Mio** | 0,16 Mio |

Sortie vérifiée : tenseur de dimensions `1 × 384`, **norme euclidienne = 1,0000** après normalisation — le vecteur est directement exploitable pour un cosinus.

**Détail de la charge utile de première visite**, mesurée fichier par fichier :

| Fichier | Octets | Mio |
|---|---:|---:|
| `onnx/model_quantized.onnx` | 118 308 185 | 112,83 |
| `tokenizer.json` | 17 082 730 | 16,29 |
| Runtime ONNX (WASM, compressé par le CDN) | ≈ 5 600 000 | ≈ 5,3 |
| Bibliothèque `transformers.js` (ESM) | ≈ 450 000 | ≈ 0,43 |
| **Total** | **≈ 142 200 000** | **≈ 135,6** |

**Capacités du navigateur détectées** : **WebGPU disponible** (adaptateur `apple / metal-3`), 12 fils d'exécution matériels. L'exécution ci-dessus est en WASM ; le passage à WebGPU est une piste d'optimisation, non une nécessité — 19,8 ms pour une requête est déjà très au-delà du confort.

**Verdict de faisabilité.**

- ✅ **L'inférence n'est pas le problème.** 19,8 ms pour encoder une question, sur une seule séquence courte. Le calcul du cosinus contre l'index se fait en JavaScript pur, en quelques millisecondes pour quelques milliers de passages.
- ⚠️ **Le problème est le premier téléchargement : 135,6 Mio.** Sur la connexion de test, 3 secondes. Sur une connexion à 10 Mbit/s, environ **110 secondes** — inacceptable pour un premier visiteur. **C'est le vrai risque du volet A**, et il est mesuré.
- ✅ **Les visites suivantes sont gratuites** : 0,16 Mio et 568 ms, le modèle étant mis en cache par la bibliothèque.

### 4.5 La réponse au problème : élagage du vocabulaire

Puisque 81,8 % du poids est une matrice d'embedding couvrant 250 037 tokens de **cent langues**, et que notre corpus est **fermé et francophone**, la quasi-totalité de cette matrice est inutile.

**Plan** : relever les tokens réellement produits par le tokenizer sur (corpus + jeu de questions), conserver ces lignes de la matrice, réindexer, réécrire le `tokenizer.json` en conséquence, ré-exporter en ONNX.

Gain calculé, à confirmer par la mesure une fois le corpus figé :

| Vocabulaire conservé | Matrice d'embedding | Modèle total | Tokenizer | Total | Versionnable ? |
|---:|---:|---:|---:|---:|---|
| 250 037 (actuel) | 91,6 Mio | 112,8 Mio | 16,3 Mio | 129,1 Mio | ❌ |
| 32 000 | 11,7 Mio | ≈ 33 Mio | ≈ 2,2 Mio | **≈ 35 Mio** | ✅ |
| 16 000 | 5,9 Mio | ≈ 27 Mio | ≈ 1,1 Mio | **≈ 28 Mio** | ✅ |

**Ce que cela change, concrètement :**

- le modèle **entre dans le dépôt** (< 100 MiB), donc plus aucune dépendance à un service tiers le jour de la soutenance ;
- la première visite passe d'environ 135,6 Mio à environ **40 Mio** (modèle élagué + runtime), soit **3,4× moins** ;
- l'artefact servi devient **un modèle que nous avons produit**, ce que le sujet valorise expressément.

**Risque associé, à mesurer et non à supposer** : un token du corpus absent de la liste retenue, ou une requête utilisateur contenant un mot hors vocabulaire, dégrade silencieusement le résultat. **Parade** : conserver le token `<unk>`, et mesurer le taux de tokens inconnus sur un jeu de questions écrit par des membres qui n'ont pas construit le vocabulaire.

### 4.6 Le comparatif TF-IDF — le modèle entièrement maîtrisé

En parallèle de l'encodeur neuronal, nous construisons un **index TF-IDF en JavaScript pur** — quelques dizaines de kilo-octets, entièrement écrit par nous, sans dépendance.

Ce n'est pas un travail redondant : c'est **la référence à battre**, et la comparaison sur le même jeu de questions produit exactement la matière que le rapport réclame (coût, latence, qualité, degré de contrôle, explicabilité, dépendance à un fournisseur). Le TF-IDF vient des rappels M1 (26 occurrences relevées dans les supports), ce qui raccroche le volet A au cours.

### 4.7 Corpus et volumétrie — ☐ à figer avant le 21/09

Le sujet impose que « le corpus est embarqué dans l'application, n'est pas fourni par le visiteur, et **son périmètre doit être affiché** ». La note de l'enseignant ajoute : « Exiger la même fermeture d'une proposition libre : **corpus et volumétrie dès le courriel**. »

| À décider | Cible proposée |
|---|---|
| Nature du corpus | documents normatifs de la formation : règlement des études, syllabus, FAQ scolarité |
| Volumétrie visée | **1 500 à 5 000 passages** après segmentation |
| Stratégie de segmentation | segmentation par section, avec recouvrement — **à faire varier et à mesurer**, c'est le paramètre que le sujet désigne comme déterminant |
| Jeu de questions d'évaluation | **≥ 60 questions**, rédigées par des membres n'ayant pas construit l'index |

**Taille de l'index livré**, calculée à partir de la dimension mesurée (384) :

| Passages | float32 | int8 |
|---:|---:|---:|
| 1 500 | 2,2 Mio | 0,55 Mio |
| 3 000 | 4,4 Mio | 1,10 Mio |
| 5 000 | 7,3 Mio | 1,83 Mio |

L'index n'est donc **jamais** un problème de taille : c'est le modèle qui l'est.

### 4.8 Protocole d'évaluation du volet A

Aucune génération n'étant produite, l'évaluation porte sur la **récupération** :

- **Recall@k** et **MRR** sur le jeu de questions, pour k ∈ {1, 3, 5, 10} ;
- **comparaison systématique** encodeur neuronal / TF-IDF sur le même jeu ;
- **effet de la segmentation** : au moins trois stratégies de découpage comparées ;
- **effet de l'élagage** : scores avant et après réduction du vocabulaire, plus le taux de tokens inconnus ;
- **latence mesurée** dans le navigateur, pas estimée.

---

## 5 — Étude du volet B : **B1 — Assistant réglementaire sourcé**

### 5.1 Cas retenu

Le système répond à des questions portant sur le même corpus normatif, **en citant systématiquement les passages sources**, et produit **une réponse d'abstention lorsque le corpus ne contient pas l'information**.

Le sujet prescrit l'évaluation : « un jeu de questions comportant une proportion de questions hors corpus, destinée à mesurer le **taux d'abstention correcte** ».

### 5.2 Modèle open-weights identifié — comparatif mesuré le 19/09/2026

Configurations relevées sur les `config.json` officiels, tailles GGUF relevées en octets.

| Modèle | Licence | Accès | Q4_K_M | Couches | Têtes KV | **Cache KV** | Contexte max |
|---|---|---|---:|---:|---:|---:|---:|
| **`Qwen/Qwen2.5-7B-Instruct`** | **Apache-2.0** | libre | **4,36 Gio** | 28 | **4** | **56,0 Kio/token** | 32 768 |
| `mistralai/Mistral-7B-Instruct-v0.3` | Apache-2.0 | libre | 4,07 Gio | 32 | 8 | 128,0 Kio/token | 32 768 |
| `Qwen/Qwen3-8B` | Apache-2.0 | libre | 4,68 Gio | 36 | 8 | 144,0 Kio/token | 40 960 |
| `mistralai/Ministral-8B-Instruct-2410` | *other* ⚠️ | libre | 4,57 Gio | 36 | 8 | 144,0 Kio/token | 32 768 |
| `Qwen/Qwen2.5-14B-Instruct` | Apache-2.0 | libre | 8,37 Gio | 48 | 8 | 192,0 Kio/token | 32 768 |
| `meta-llama/Llama-3.1-8B-Instruct` | llama3.1 | ⚠️ **`gated: manual`** | 4,58 Gio | — | — | — | — |

Cache KV calculé comme `2 × couches × têtes_KV × dim_tête × 2 octets` (fp16), par token.

**Modèle retenu : `Qwen2.5-7B-Instruct`.** Trois raisons, dans l'ordre :

1. **Son cache KV est 2,3 à 3,4 fois plus petit** que celui de tous les autres candidats (56 Kio/token contre 128 à 192), grâce à 4 têtes KV seulement et 28 couches. Pour un RAG qui injecte des passages cités dans le contexte, **la longueur de contexte est la ressource critique** — c'est précisément là que ce modèle est avantagé.
2. **Apache 2.0, sans restriction d'accès.**
3. Llama-3.1-8B est **`gated: manual`** : son téléchargement suppose une approbation manuelle de délai inconnu. À 12 jours du jalon mi-parcours, c'est un risque de calendrier que rien ne justifie de prendre.

**Second candidat pour comparaison : `Qwen3-8B`** (Apache 2.0, 12,9 M téléchargements sur 30 jours, contexte 40 960). **`Ministral-8B` est écarté** : sa licence « other » est une licence de recherche, incompatible avec une diffusion sans précaution.

### 5.3 Machine cible

| | **Machine 1 — Mahé BEGNIS** | **Machine 2 — Jibril BENSALEM** |
|---|---|---|
| Modèle | Apple M4 Pro (`Mac16,8`) | ☐ **à mesurer** |
| CPU | 12 cœurs (8 performance + 4 efficience) | ☐ |
| GPU | 16 cœurs, Metal 4 | ☐ |
| Mémoire unifiée | **24,0 Gio** | ☐ |
| **Mémoire réellement disponible** | **10,3 Gio** *(mesuré en session de travail normale)* | ☐ |
| Disque libre | **21 Gio sur 460 (96 % occupé)** ⚠️ | ☐ |

> **La mémoire disponible n'est pas la mémoire installée.** 24 Gio installés, **10,3 Gio réellement disponibles** avec une session de travail ouverte. C'est ce second chiffre qui contraint le choix du modèle, et c'est celui que nous retenons pour le budget du §5.4.

**Protocole de relevé pour la machine 2**, à exécuter avant le 21/09 et à coller dans le ticket correspondant :

```bash
sysctl -n hw.model hw.memsize hw.ncpu                  # modèle, RAM, cœurs
system_profiler SPDisplaysDataType | grep -E "Chipset|Cores|Metal"
df -h /System/Volumes/Data | tail -1                   # disque libre
vm_stat                                                # mémoire réellement disponible
```

**Pourquoi deux machines.** Sélectionner celle qui fera la démonstration du 07/12. **Règle méthodologique** : pour comparer deux machines, on exécute **le même modèle, la même quantisation, le même contexte et le même jeu de questions**. On ne fait varier que la machine — sans quoi la comparaison ne mesure rien.

### 5.4 Contrainte mémoire estimée

Empreinte de `Qwen2.5-7B-Instruct` en Q4_K_M, selon la longueur de contexte :

| Poste | 4 k | 8 k | 16 k | 32 k |
|---|---:|---:|---:|---:|
| Poids du modèle (Q4_K_M) | 4,36 Gio | 4,36 Gio | 4,36 Gio | 4,36 Gio |
| Cache KV (fp16) | 0,22 Gio | 0,44 Gio | 0,88 Gio | 1,75 Gio |
| Encodeur de récupération + index | ≈ 0,15 Gio | ≈ 0,15 Gio | ≈ 0,15 Gio | ≈ 0,15 Gio |
| Surcouche d'exécution | ≈ 0,50 Gio | ≈ 0,50 Gio | ≈ 0,50 Gio | ≈ 0,50 Gio |
| **Total** | **≈ 5,2 Gio** | **≈ 5,5 Gio** | **≈ 5,9 Gio** | **≈ 6,8 Gio** |
| **Marge sur 10,3 Gio disponibles** | 5,1 Gio | 4,8 Gio | 4,4 Gio | 3,5 Gio | 

**Conclusion : le modèle passe confortablement, même à 32 k de contexte.** À titre de comparaison, `Qwen2.5-14B-Instruct` demanderait 8,37 + 1,50 + 0,65 ≈ **10,5 Gio à 8 k**, c'est-à-dire **au-delà des 10,3 Gio disponibles** sans fermer les applications. Il reste une option à tester si la qualité de Qwen2.5-7B s'avère insuffisante, mais il ne peut pas être le choix par défaut.

**Contrainte réellement bloquante : le disque, pas la mémoire.** 21 Gio libres pour un Q4_K_M à 4,36 Gio, un Q5_K_M à 5,07 Gio, un second modèle de comparaison à 4,68 Gio, plus le corpus et les index. Cela tient, mais sans marge pour une campagne d'essais. **Libérer 40 Gio est la première tâche du volet B.**

### 5.5 Ce qui est mutualisé entre A3 et B1

C'est la raison d'être du couple. Écrit une fois, servi deux fois :

| Brique | A3 | B1 |
|---|---|---|
| Corpus nettoyé et segmenté | ✅ | ✅ |
| Stratégie de découpage | ✅ | ✅ |
| Encodeur `multilingual-e5-small` | navigateur (ONNX) | local (Python) |
| Index vectoriel | statique, dans le site | en mémoire |
| Jeu de questions d'évaluation | partie « dans le corpus » | + questions **hors corpus** |

**Économie estimée : 5 à 8 jours-homme** par rapport à deux cas sans recouvrement.

**Ce qui n'est pas mutualisé, et fonde la comparaison du rapport** : A3 **restitue** des passages sans rien générer ; B1 **génère** une réponse en citant, ou s'abstient. La comparaison porte donc exactement sur ce que la génération apporte et sur ce qu'elle coûte — en latence, en contrôle, en explicabilité, et en risque d'hallucination.

### 5.6 L'abstention est le vrai sujet, et le protocole de mesure

Récupérer des passages et les faire résumer est un exercice connu. **Refuser de répondre quand le corpus est muet ne l'est pas.** C'est là que se jouent les 20 points de « adaptation, mesures avant/après ».

Jeu de test à construire :

| Catégorie | Proportion visée | Ce qu'elle mesure |
|---|---:|---|
| Questions **couvertes** par le corpus | 60 % | exactitude de la réponse et **justesse des citations** |
| Questions **hors corpus**, plausibles | 30 % | **taux d'abstention correcte** |
| Questions **ambiguës ou partiellement couvertes** | 10 % | comportement en zone grise |

Quatre métriques, toutes calculables automatiquement une fois le jeu annoté :

1. **Taux d'abstention correcte** sur les questions hors corpus ;
2. **Taux d'abstention à tort** sur les questions couvertes — l'erreur symétrique, celle que l'on oublie ;
3. **Taux de citations valides** : le passage cité contient-il effectivement la réponse ;
4. **Taux d'hallucination** : réponse affirmative sur question hors corpus.

**Mesures avant / après adaptation**, comme le sujet l'exige, avec au minimum trois états comparés : modèle nu sans RAG · RAG sans consigne d'abstention · RAG avec consigne et seuil de similarité calibré.

> ☐ **Question à poser à l'enseignant dans le courriel du 20/09** : le sujet demande un modèle « **adapté par vos soins** » et note « adaptation, mesures avant/après » sur 20 points, sans préciser si un RAG réglé et une consigne système constituent une adaptation, ou si un ajustement fin de type LoRA est attendu. **L'écart de charge entre les deux lectures est d'un facteur 3 à 5.** L'enseignant s'engage à répondre sous 24 h : c'est le bon moment.

---

## 6 — Cadrage

### 6.1 Périmètre

| Livré | Explicitement **hors périmètre** |
|---|---|
| Site public statique, recherche sémantique sur corpus normatif fermé | Aucune génération de texte dans le volet A |
| Affichage du périmètre du corpus interrogeable | Aucun dépôt de document par le visiteur |
| Résultats classés : score de similarité, référence de section, lien vers le document | Pas de multilingue — **français uniquement** |
| Index précalculé hors ligne, livré en fichier statique | Pas d'authentification, pas de compte utilisateur |
| Comparatif encodeur neuronal / TF-IDF, mesuré | Pas de persistance côté serveur ni de journalisation des requêtes |
| Assistant local sourcé avec abstention, sur le même corpus | Pas de traitement de PDF scannés ni d'OCR |
| Mesures avant/après adaptation, feuille de route des développements restants | Pas de mise à jour automatique du corpus |

### 6.2 Hypothèses — ce que nous tenons pour acquis et qui pourrait être faux

| Hypothèse | Statut | Si elle est fausse |
|---|---|---|
| Un encodeur multilingue quantifié s'exécute dans le navigateur en un temps acceptable | ✅ **vérifiée le 19/09** : 19,8 ms | — |
| L'élagage du vocabulaire fait passer le modèle sous 100 MiB sans perte notable de qualité | ⚠️ **calculée, non vérifiée** | on sert le modèle depuis le CDN Hugging Face, avec une copie locale de secours pour la démonstration |
| Le corpus normatif visé est accessible et exploitable en volume suffisant | ☐ **à vérifier avant le 21/09** | repli sur un corpus public équivalent, décision à documenter |
| `Qwen2.5-7B-Instruct` produit des citations fiables en français | ☐ à mesurer | essai de `Qwen3-8B`, puis de `Qwen2.5-14B` si la mémoire le permet |
| Un RAG réglé constitue une « adaptation » au sens du barème | ☐ **question au professeur** | facteur 3 à 5 sur la charge du volet B |
| Les 5 membres restent disponibles jusqu'au 07/12 | — | binôme principal/secondaire sur chaque domaine (§8) |

### 6.3 Critères de réussite — chiffrés

Formulés en nombres, pas en adjectifs, afin de pouvoir constater l'échec autant que la réussite.

| Jalon | Critère | Seuil |
|---|---|---|
| **Mi-parcours 01/10** | URL publique en ligne, même minimale | site accessible, recherche fonctionnelle sur un corpus réduit |
| | Première inférence locale aboutie | une réponse sourcée produite par le modèle local |
| | Tag Git posé + branche dédiée pour l'enseignant | ✅ / ❌ |
| **J3 16/10** | Volet A fonctionnel | Recall@5 ≥ 0,80 sur le jeu de questions |
| | Latence de recherche en navigateur | < 100 ms après chargement |
| | Adaptation du volet B engagée | mesures avant/après disponibles sur ≥ 30 questions |
| **J4 07/12** | Taux d'abstention correcte | ≥ 0,85 sur les questions hors corpus |
| | Taux de citations valides | ≥ 0,90 |
| | Première visite du site | ≤ 50 Mio |
| **Conduite** | Tickets créés **avant** réalisation | 100 % des tâches réalisées |

---

## 7 — Risques identifiés

| # | Risque | Probabilité | Impact | Parade | Responsable |
|---|---|---|---|---|---|
| **R1** | **Disque saturé** — 21 Gio libres, un modèle Q4 en consomme 4,4 | élevée | bloque le volet B | libérer **40 Gio avant le 25/09** ; une seule variante de modèle à la fois | ☐ |
| **R2** | **Première visite à 135,6 Mio** — inacceptable sur connexion lente (≈ 110 s à 10 Mbit/s) | **certaine** sans action | 15 points du volet A | élagage du vocabulaire (§4.5), cible ≤ 50 Mio ; mesure du temps de chargement sur bande passante bridée | ☐ |
| **R3** | **Notions non enseignées** — RAG, ONNX, quantisation : 0 occurrence dans les supports ; la J3 arrive **après** le jalon du 01/10 | **certaine** | retard sur les deux volets | tâches d'auto-formation **datées et assignées** dès cette semaine ; elles alimentent le bonus | ☐ |
| **R4** | **Périmètre de l'« adaptation » non défini** par le sujet | élevée | 20 points | question dans le courriel du 20/09, réponse sous 24 h | Mahé |
| **R5** | **Corpus indisponible ou trop maigre** | moyenne | bloque les deux volets | vérification avant le 21/09 ; repli sur corpus public documenté | ☐ |
| **R6** | **Élagage du vocabulaire dégradant la qualité** silencieusement | moyenne | qualité du volet A | mesure du taux de tokens inconnus + scores avant/après ; repli CDN | ☐ |
| **R7** | **Jeu de questions écrit par ceux qui construisent l'index** → score flatteur, échec en démonstration | élevée | crédibilité | questions rédigées par des membres n'ayant pas construit l'index | ☐ |
| **R8** | **Indisponibilité d'un membre** | moyenne | jalon manqué | domaine principal **et** secondaire pour chacun (§8) | — |
| **R9** | **Déploiement tardif** — « un déploiement effectué le jour même sera considéré comme non livré » | moyenne | 15 points | page en ligne **dès cette semaine**, enrichie ensuite ; URL vérifiée 48 h avant J4 | ☐ |
| **R10** | **Board renseigné après coup** — « identifiable et sans valeur » | moyenne | points de jalons | aucun commit sans ticket créé avant ; contrôle hebdomadaire | Jibril |
| **R11** | **Échec de la démonstration le 07/12** | moyenne | 15 points | **captation vidéo de secours des deux démonstrations** — le sujet prévient que son absence « peut entraîner la perte des points » | ☐ |

---

## 8 — Répartition initiale des tâches

Cinq domaines, un titulaire principal et un secondaire par domaine, en binôme — la forme recommandée par le sujet.

### 8.1 Domaines et binômes

| Domaine | Contenu | Principal | Secondaire |
|---|---|---|---|
| **D1 — Corpus & segmentation** | collecte, nettoyage, stratégies de découpage, jeu de questions | ☐ | ☐ |
| **D2 — Encodeur & index** | ONNX, quantisation, **élagage du vocabulaire**, précalcul de l'index, TF-IDF de référence | ☐ | ☐ |
| **D3 — Front & déploiement (volet A)** | interface, parcours utilisateur, Transformers.js, GitHub Pages, affichage du périmètre du corpus | ☐ | ☐ |
| **D4 — Volet B : socle RAG & inférence locale** | installation du runtime, quantisation, récupération, consigne système, citations | ☐ | ☐ |
| **D5 — Volet B : adaptation & évaluation** | abstention, calibration du seuil, jeu de test, **mesures avant/après** | ☐ | ☐ |

> ☐ **À remplir nominativement en séance.** Deux contraintes à respecter : chaque membre apparaît **une fois comme principal et une fois comme secondaire**, et les deux titulaires d'un même domaine ne sont pas les mêmes personnes sur deux domaines consécutifs — pour éviter qu'une absence emporte un domaine entier.
>
> **D5 porte les 20 points les plus lourds du barème** et demande la plus grande rigueur de mesure. **D2 porte le risque R2**, le plus critique du volet A.

### 8.2 Rôles transverses — attribués

| Rôle | Titulaire | Charge |
|---|---|---|
| Gestion du board | **Jibril BENSALEM** | ≈ 1 h/semaine |
| Journal d'usage de l'IA + classeur de suivi | **Mahé BEGNIS** | ≈ 30 min/semaine |
| Lead technique (arbitrage, cohérence d'architecture) | **Mahé BEGNIS** | au fil de l'eau, chaque arbitrage écrit |
| `OUTILS.md` — les cinq outils novateurs | ☐ | ≈ 30 min/semaine |
| Coordination du rapport — **commencé au plus tard à J3 (16/10)** | ☐ | à partir du 16/10 |
| Soutenance — support de **pitch** *et* support de **présentation** (deux fichiers distincts) | ☐ | à partir de novembre |

### 8.3 Rituels

- **Un point hebdomadaire de 45 minutes**, avec compte rendu écrit même court — le rapport demandera « fréquence, format, résultats produits ».
- **Une mini-démonstration par membre à chaque point.** Le sujet le recommande nommément, et c'est la seule parade au fait que « le choix du répondant à chaque question relève de l'enseignant ».

---

## 9 — Prochaines étapes, du 19/09 au 01/10

Le jalon mi-parcours est dans **12 jours** et exige déjà un site en ligne et une première inférence locale.

| Échéance | Action | Qui |
|---|---|---|
| **20/09** dimanche | Courriel de confirmation : outils, liens d'invitation, cas A3 et B1, **corpus et volumétrie annoncés**, + la question sur le périmètre de l'« adaptation » | Mahé |
| **21/09** lundi (J2) | Board créé, membres ajoutés, colonnes et milestones définis | Jibril |
| **21/09** | Relevé matériel de la machine 2 collé dans un ticket | Jibril |
| **21/09** | Répartition nominative des domaines D1–D5 actée | tous |
| **avant le 23/09** | Corpus vérifié : accessibilité, volumétrie réelle, droits d'usage | D1 |
| **avant le 25/09** | **40 Gio libérés** sur la machine de référence — risque R1 | D4 |
| **avant le 25/09** | Page statique déployée, même vide, à l'URL définitive — risque R9 | D3 |
| **avant le 27/09** | Première version de l'index précalculé sur un corpus réduit | D2 |
| **avant le 27/09** | Première inférence locale aboutie sur `Qwen2.5-7B-Instruct` | D4 |
| **avant le 29/09** | Jeu de 60 questions rédigé, dont 30 % hors corpus | D1 + D5 |
| **01/10** jeudi | **Jalon mi-parcours** : volet A en ligne, inférence locale, **tag Git + branche dédiée à l'enseignant** | tous |

---

## 10 — Les cinq outils novateurs : pourquoi c'est différé, et ce qui commence maintenant

**Ce n'est pas un attendu de J2** — vérifié dans le sujet, la liste des attendus du jalon ne le mentionne pas. C'est une **section du rapport**, rémunérée jusqu'à **+3 points**.

**Mais rien ne serait plus coûteux que d'y penser en décembre.** La grille de l'enseignant valorise « le temps d'appropriation constaté », « les conditions dans lesquelles l'outil échoue », « ce que la documentation omet », et exige **au moins une critique argumentée**. Ces éléments ne se reconstituent pas après coup : ils se notent le jour de l'usage.

**Ce que nous faisons dès maintenant, sans choisir le panier :**

- ☐ ouvrir `OUTILS.md` dans le dépôt, avec une fiche vierge par outil ;
- ☐ **y consigner dès aujourd'hui** la divergence Claude Code / Antigravity (§2.2), qui est déjà un usage réel et comparatif ;
- ☐ y consigner l'outillage que le projet nous **oblige** à employer — export ONNX, runtime d'inférence locale, index vectoriel — au fur et à mesure de leur première utilisation.

**Le choix définitif du panier de cinq se fera dans les prochains jours**, une fois que nous saurons lesquels nous utilisons réellement — le sujet disqualifiant explicitement « la citation d'un outil non installé ». Le comparatif préparatoire figure au §8 du support de réunion (`03_SUPPORT_REUNION_J2.md`).

---

## Annexe — Méthode et reproductibilité

Tous les chiffres de ce document proviennent d'une mesure faite le 19/09/2026, non d'une estimation ni d'une documentation recopiée.

| Mesure | Moyen |
|---|---|
| Tailles des modèles ONNX et GGUF | API Hugging Face `?blobs=true`, tailles en octets |
| Configurations des modèles (couches, têtes KV, dimensions) | `config.json` officiels de chaque dépôt |
| Licences et restrictions d'accès | API Hugging Face, champs `tags` et `gated` |
| Cache KV | calcul `2 × couches × têtes_KV × dim_tête × 2 octets` |
| Part de la matrice d'embedding | calcul `vocab × hidden`, **recoupé avec la taille de fichier mesurée** (112,0 Mio calculés contre 112,83 mesurés) |
| **Faisabilité navigateur** | page statique servie en local, Chromium piloté par Playwright, `performance.now()`, 20 passes après chauffe |
| Charge utile réseau | `curl --compressed`, taille par fichier, recoupée avec le journal réseau du navigateur |
| Matériel et mémoire disponible | `sysctl`, `vm_stat`, `system_profiler`, `df` |
| Versions de l'environnement | exécution de chaque binaire |

**Deux mesures fausses ont été produites puis corrigées pendant ce travail**, et sont signalées ici parce que le sujet valorise ce type de transparence :

1. L'API annonçait `embeddinggemma-300m` à **0,5 Mio** ; ses poids étant dans des fichiers externes, la taille réelle est **294,6 Mio**.
2. Le navigateur rapportait **5,5 Mio** transférés pour un modèle de 112,8 Mio : les ressources d'origine tierce ne déclarent pas leur taille sans l'en-tête `Timing-Allow-Origin`. La charge utile réelle, **135,6 Mio**, a été obtenue en mesurant chaque fichier séparément.

**Ce qui n'a pas été vérifié** et reste à faire : la machine de Jibril BENSALEM, l'accessibilité réelle du corpus normatif visé, le gain effectif de l'élagage du vocabulaire, et la qualité des citations produites par `Qwen2.5-7B-Instruct` en français.
