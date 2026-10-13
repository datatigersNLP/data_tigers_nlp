# Étude d'ajustement contrastif de l'encodeur sémantique sur le corpus SocialGouv

**Auteur principal :** Remy RAYANE (Responsable D2 & Issue #49)  
**Soutien & Relecture :** Mahé BEGNIS, Jibril BENSALEM  
**Date :** 13 octobre 2026 (révision finale avant Weekly 5)  
**Référence :** Issue GitHub #49 (`Refs #49`, branche `feat/49-ajustement-encodeur`)  
**Statut :** Recette d'entraînement figée le 13 octobre 2026 ; mesures préliminaires étiquetées exploratoires et hors protocole (décision Weekly 4) ; en attente de la mesure officielle conjointe au Weekly 5

---

## 1. Contexte et Objectifs

Le sujet du projet impose que l'application de recherche sémantique du Volet A ne se contente pas d'exécuter un modèle générique sur étagère, mais s'appuie sur un modèle adapté au domaine juridique du Code du travail et des fiches pratiques du ministère du Travail (SocialGouv).

L'**Issue #49** a pour objet d'ajuster finement l'encodeur `intfloat/multilingual-e5-small` par **apprentissage contrastif** (*contrastive learning*) sur des paires `(question, passage)` représentatives du corpus, et d'en préparer l'évaluation rigoureuse par un protocole expérimental apparié et reproductible.

### Contraintes méthodologiques strictes
1. **Étancheité absolue (*Zero Data Leakage*)** : Aucune fiche, aucun passage et aucune question du jeu de test (Issue #44 / PR #54) ne doit servir à l'entraînement ou à la sélection du modèle.
2. **Préservation du protocole E5** : Conservation systématique des préfixes obligatoires (`query: ` pour les requêtes et `passage: ` pour les documents).
3. **Évaluation statistique appariée** : Calcul des métriques de rang (`Recall@k`, `MRR@10`) avec test exact de McNemar et test d'Obuchowski (données groupées par fiche) pour trancher la significativité statistique de l'écart.
4. **Portabilité navigateur (ONNX & Quantification)** : Export ONNX FP32, quantification dynamique INT8 (`q8`) et vérification des critères de parité et fidélité établis au Notebook 02.
5. **Gestion des artefacts hors Git** : Les dossiers `data/` et `models/` (données d'entraînement, index `.npy`, poids PyTorch et modèles `.onnx`) restent intégralement exclus du versionnement Git (règle stricte du projet).
6. **Non-déploiement sans validation officielle** : Le modèle ajusté n'est pas déployé en production tant que la mesure officielle n'a pas validé la règle d'arbitrage à deux jeux.

---

## 2. Protocole expérimental et Découpage des données

### 2.1 Le Banc de Test de Référence (Ground Truth)
Le benchmark d'évaluation est constitué à partir du jeu de 105 questions annotées de l'équipe (Issue #44, PR #54) :
* **72 questions de test `dans_corpus`** ont été appariées à leurs passages cibles dans le découpage structurel **M2** (`data/decoupage/passages/passages_m2.parquet`, 4 240 passages).
* Le jeu couvre 67 fiches pratiques distinctes du ministère du Travail.

### 2.2 Cloisonnement Anti-Fuite (Train Exclusion Set)
Pour empêcher toute mémorisation de surface ou surapprentissage sur les questions évaluées :
* **Exclusion au niveau de la fiche (URL)** : Les 67 fiches associées au jeu de test et au lot de calibration ont été **totalement proscrites** de la phase d'entraînement.
* **Volume exclu** : 1 463 passages exclus sur 4 240 (soit **34,5 % du corpus**).
* **Vivier d'entraînement** : 2 777 passages issus de **194 fiches vierges** de toute évaluation.

### 2.3 Génération synthétique locale (Qwen2.5-7B)
L'inférence locale validée dans le cadre de l'Issue #31 (`qwen2.5-7b-instruct:q4_k_m-local` exécuté via Ollama) a été mise à profit pour générer des questions d'utilisateurs réalistes :
* **Échantillonnage stratifié** : 110 passages candidats représentatifs sélectionnés sur 110 fiches distinctes (longueur médiane ~250 tokens).
* **Prompting de rôle** : Requêtes formulées du point de vue d'un salarié ou citoyen cherchant une réponse concrète, sans méta-références (« selon le texte », etc.).
* **Filtrage automatique et documentation du filtre de Jaccard** :
  * Contrôle syntaxique (interrogation finale, longueur entre 25 et 220 caractères).
  * **Filtre de non-recouvrement lexical Jaccard** : Rejet automatique si l'indice de Jaccard sur les ensembles de tokens entre une question générée et n'importe quelle question du jeu de test dépasse **0,40**. Ce seuil a été calibré empiriquement comme filtre heuristique anti-fuite : il tolère le lexique juridique inévitable (« contrat », « salarié », « préavis ») tout en interdisant toute proximité thématique ou calque de formulation avec les requêtes de test.
* **Résultat et empreinte d'authentification** : **109 paires validées**, 1 rejetée. Un échantillon de contrôle a été audité manuellement dans `data/adaptation/echantillon_controle_train.json`.
  * **Fichier de données** : `data/adaptation/train_paires.jsonl` (exclu du suivi Git : le dossier `data/` n'est jamais versionné dans le dépôt).
  * **Empreinte SHA-256** : `2d377eb66e7f4ca0e8e4cf34b089e5da7c46e47ddceab9f964764df468c21698` (174 552 octets).
  * **Rôle de l'empreinte cryptographique** : La génération locale via Ollama ayant été exécutée sans graine pseudo-aléatoire explicite (`seed`), cette empreinte identifie de manière unique et opposable le fichier exact utilisé pour l'entraînement. L'empreinte authentifie le fichier sans permettre de le recréer de novo sans la source, ce qui impose de conserver précieusement cet artefact d'entraînement.


---

## 3. Ajustement Contrastif de l'Encodeur

### 3.1 Architecture et Fonction de Perte
* **Modèle de départ** : `intfloat/multilingual-e5-small` (117 millions de paramètres, dimension 384).
* **Fonction de perte** : `MultipleNegativesRankingLoss` (MNRL).
  * Pour chaque mini-batch de taille $B$, la perte maximise la similarité cosinus entre la question $\mathbf{q}_i$ et son passage cible $\mathbf{p}_i$, tout en utilisant l'ensemble des $B-1$ autres passages du lot comme négatifs implicites (*in-batch negatives*).
  * Température / facteur d'échelle : échelle standard SentenceTransformers ($s = 20.0$).

### 3.2 Hyperparamètres d'entraînement et déclaration de la recette (figée au 13/10)
Les hyperparamètres suivants constituent la recette d'entraînement déclarée et figée au 13 octobre 2026. Ils ont été choisis pour adapter le modèle au vocabulaire du droit du travail sans détruire sa structure multilingue pré-entraînée (*catastrophic forgetting*) :
* **Données d'entraînement figées** : `data/adaptation/train_paires.jsonl` (109 paires, SHA-256 : `2d377eb66e7f4ca0e8e4cf34b089e5da7c46e47ddceab9f964764df468c21698`).
* **Taille de lot (*batch size*)** : 16 (soit 15 négatifs par exemple).
* **Taux d'apprentissage (*learning rate*)** : $2 \times 10^{-5}$ avec optimiseur AdamW et décroissance linéaire.
* **Époques** : 2 (14 pas d'optimisation).
* **Warmup** : 10 % des étapes.
* **Durée d'entraînement** : 185,5 secondes sur CPU (16 cœurs).

> **Déclaration des choix d'entraînement (Weekly 4 / #10) :**  
> Conformément à l'exigence de transparence méthodologique, cette configuration d'entraînement a été arrêtée lors de la phase préliminaire (PR #63) et reste strictement figée sans aucun réajustement ultérieur sur le jeu de test.

### 3.3 Convergence de la perte
| Étape (sur 14) | Époque | Training Loss | Norme du Gradient |
|---|---|---|---|
| 2 | 0.29 | 1.5610 | 12.11 |
| 4 | 0.57 | 1.3730 | 8.47 |
| 6 | 0.86 | 0.8857 | 7.60 |
| 8 | 1.14 | 0.7160 | 6.74 |
| 10 | 1.43 | 0.4952 | 6.66 |
| 12 | 1.71 | 0.6111 | 7.29 |
| 14 | 2.00 | **0.4717** | **5.75** |

La perte a décru de manière régulière et robuste (de 1,56 à 0,47), confirmant un apprentissage efficace sans instabilité.

---

## 4. Résultats préliminaires (Mesures exploratoires, hors protocole)

> **Avertissement méthodologique (Décision 2 du Weekly 4, Ticket #10) :**  
> Les chiffres ci-dessous proviennent du banc d'essai préliminaire exécuté le 6 octobre 2026 (ex-PR #63). Conformément aux décisions du Weekly 4, ces résultats sont expressément étiquetés **« exploratoires et hors protocole »** car ils ont été obtenus avant le gel officiel du protocole d'évaluation du Notebook 03 (Issue #46) et de la règle de pertinence D4 amendée.  
> **Ils ne préjugent pas de la mesure officielle.** L'évaluation opposable et définitive de l'encodeur ajusté sera effectuée selon le protocole `docs/etudes/evaluation/05_protocole_ajustement.md` au Weekly 5 (15 octobre).

### 4.1 Tableau comparatif des métriques de recherche préliminaires

| Métrique | Avant (Base pré-entraîné) | Après (Modèle ajusté) | Gain absolu | Valeur *p* (McNemar / Obuchowski) | Significatif ($\alpha = 0.05$) |
|---|---|---|---|---|---|
| **Recall@1** | 19,44 % | **26,39 %** | **+6,94 %** | $p = 0.2004$ | Non |
| **Recall@3** | 37,50 % | **51,39 %** | **+13,89 %** | $p = 0.0080$ | **OUI** ($p < 0.01$) |
| **Recall@5** | 43,06 % | **62,50 %** | **+19,44 %** | $p = 0.0002$ | **OUI** ($p < 0.001$) |
| **Recall@10** | 58,33 % | **73,61 %** | **+15,28 %** | $p = 0.0048$ | **OUI** ($p < 0.01$) |
| **MRR@10** | 0,3250 | **0,4203** | **+0,0954** | — | — |

### 4.2 Analyse exploratoire
1. **Tendance nette sur le Recall@5 (+19,44 points)** :  
   Dans ce cadre exploratoire, le Recall@5 passe de 43,06 % à 62,50 % ($p = 0.0002$), montrant que l'apprentissage contrastif a bien orienté les représentations.
2. **Gain de premier rang (MRR@10 : +0,0954)** :  
   Le rang réciproque moyen progresse de 0,325 à 0,420.
3. **Généralisation hors fiches vues** :  
   L'entraînement ayant été réalisé exclusivement sur des fiches vierges de toute évaluation, ce comportement préliminaire atteste que le modèle s'adapte au vocabulaire administratif sans surapprentissage direct.

---

## 5. Export ONNX et Contrôles de Parité et Fidélité Navigateur

Pour permettre le déploiement ultérieur dans le navigateur client via **Transformers.js** (Volet A), le modèle PyTorch affiné a été converti en ONNX et quantifié selon les exigences rigoureuses du Notebook 02.

### 5.1 Fichiers générés et alignement de quantification Xenova

| Format | Fichier | Taille disque | Spécification technique | Rôle applicatif |
|---|---|---|---|---|
| **FP32** | `models/multilingual-e5-small-finetuned/onnx/model.onnx` | 448,5 Mio | Opset 14, pooling mean, FP32 complet | Modèle de référence ONNX haute précision |
| **q8 (Ajusté)** | `models/multilingual-e5-small-finetuned/onnx/model_quantized.onnx` | 112,9 Mio | `per_channel=True`, `reduce_range=True`, `ActivationSymmetric=True` | Modèle ajusté pour le navigateur Web (WASM) |
| **q8 (Témoin base)** | `models/multilingual-e5-small-base/onnx/model_quantized.onnx` | 112,9 Mio | Même recette d'export opset 14 sur `intfloat/multilingual-e5-small` | Modèle témoin isolant le graphe de l'ajustement |

> **Alignement sur la quantification Xenova et tables d'embeddings symétriques :**  
> Au Notebook 02, une conversion INT8 dynamique basique (`per_tensor`) dégradait la fidélité de premier résultat dans le navigateur à 85,8 %, contre **91,8 %** pour la conversion `q8` de Xenova (`model_quantized.onnx`).  
> Pour combler l'écart structural, le script `scripts/adaptation/06_exporter_onnx.py` a été aligné sur les hyperparamètres de Xenova avec `per_channel=True`, `reduce_range=True` et l'option `extra_options={"ActivationSymmetric": True}`. Cette option force la quantification symétrique des 3 tables d'embeddings (`word_embeddings`, `position_embeddings`, `token_type_embeddings`) : sur le modèle de base, **74 tenseurs sur 75 deviennent strictement identiques bit à bit à ceux de Xenova**, le 75e ne différant que d'une seule valeur sur 96 millions. Les dépendances sont rigoureusement épinglées dans `scripts/adaptation/requirements.txt` (`onnx==1.23.2`, `onnxruntime==1.30.0`).

### 5.2 Contrôles de conformité et protocole comparatif

#### Contrôle 1 : Parité numérique FP32 (PyTorch vs ONNX FP32)
* **Cosinus minimal** : $1.00000000$ (tolérance : $\ge 0.99999$).
* **Écart absolu maximal composante** : $1,17 \times 10^{-7}$.
* **Statut** : **VALIDÉ AVEC SUCCÈS**.

#### Contrôle 2 : Fidélité navigateur du modèle quantifié q8 (Protocole Notebook 02)
Conformément au protocole méthodologique du Notebook 02 (section 8), la mesure de fidélité opposable a été exécutée **directement dans le navigateur** à l'aide de la page de contrôle du projet (`scripts/indexation/fidelite_navigateur.html`) servie par `scripts/adaptation/serveur_controle.py` :
* **Moteur d'exécution** : Chromium, moteur ONNX Runtime WebAssembly (`device: "wasm"`), bibliothèque `@huggingface/transformers@4.3.0`.
* **Jeu de test** : Les **822 requêtes réalistes** du corpus M2 (`data/indexation/controle/requetes_fidelite.json`, titres de section interrogatifs).
* **Index de référence** : Les **4 240 passages** du corpus M2 encodés en PyTorch FP32 (`data/adaptation/passage_embeddings_apres.npy` pour le modèle ajusté, `passage_embeddings_baseline.npy` pour le témoin).
* **Règle de décision méthodologique** : Le Notebook 02 ne définit aucun seuil statique arbitraire, mais une **règle comparative** : la fidélité de la variante quantifiée doit être évaluée par rapport au modèle de référence `q8` de Xenova.
* **Besoin d'un témoin de base** : Même avec des poids quasi identiques, l'export PyTorch vers ONNX (opset 14) produit un ordonnancement de graphe légèrement distinct de Xenova (environ 3 % de requêtes dont le premier résultat diffère sur le modèle de base). Le passage du modèle de base dans le script 06 (`models/multilingual-e5-small-base`) fournit le **témoin méthodologique indispensable** pour isoler l'effet du graphe de celui de l'ajustement sémantique.

| Métrique de fidélité (822 requêtes, 4 240 passages) | Modèle Ajusté (Navigateur WASM) | Témoin de BASE (Navigateur WASM) | Réf. q8 Hub Xenova (Notebook 02) |
|---|---:|---:|---:|
| **Cosinus médian avec la référence PyTorch** | **0,99389** | **0,99653** | 0,99655 |
| **Cosinus minimal avec la référence PyTorch** | **0,98627** | **0,99044** | 0,99196 |
| **Concordance Top-1 (même 1er résultat)** | **91,61 %** (753 / 822) | **92,58 %** (761 / 822) | 91,8 % (755 / 822) |
| **Premier résultat de référence dans le Top-5** | **99,88 %** (821 / 822) | **99,88 %** (821 / 822) | 99,9 % (821 / 822) |
| **Rang maximal de dégradation** | **10** (99e percentile : 2,8) | **7** (99e percentile : 3,0) | 9 |
| **Temps d'encodage moyen par requête** | **78,7 ms** (WASM) | **73,7 ms** (WASM) | 18,6 ms (WASM) |

#### Versionnement du calcul et empreintes SHA-256 opposables
Le calcul des métriques in-browser ci-dessus est intégralement versionné et automatisé dans le script [`08_calculer_metriques_navigateur.py`](../../scripts/adaptation/08_calculer_metriques_navigateur.py). Les empreintes cryptographiques SHA-256 des fichiers opposables sont consignées dans le tableau suivant :

| Modèle & Artefact | Fichier | Taille | Empreinte cryptographique SHA-256 |
|---|---|---:|---|
| **Modèle ajusté (ONNX q8)** | `model_quantized.onnx` | 112,89 Mio | `934a202bee5599fc45c0cb753414a7b2b490605bed84e72f471072e6ee53d047` |
| **Résultats navigateur ajusté** | `fidelite_navigateur_ajuste.json` | 9,97 Mio | `72baf3e4011aa610a99c19a36768c1e13703e0d197f721db4c422554d95f26d0` |
| **Modèle témoin de base (ONNX q8)** | `model_quantized.onnx` | 112,89 Mio | `30ae0f2153f7e14ce5afe082c68ee251d0cce6c26e8caa71307fbd8ebf4bcb90` |
| **Résultats navigateur témoin** | `fidelite_navigateur_temoin.json` | 9,96 Mio | `72a612ea392dce707fd1b59c9a7b1bc200dcfaea8bf585d1ef97c21953330a63` |

*Note sur la simulation locale Python :* En inférence CPU Python directe avec `batch_size=1` ([`07_mesurer_fidelite_822.py`](../../scripts/adaptation/07_mesurer_fidelite_822.py)), la concordance Top-1 atteint **93,67 %** (770 / 822) pour le modèle ajusté et **92,70 %** (762 / 822) pour le témoin de base, avec un recouvrement Top-5 de 100,00 % (822 / 822) et un rang maximal de 5. L'encodage unitaire (`batch_size=1`) évite les artefacts de quantification dynamique induits par le remplissage (*padding*) sur les lots de 32.

> **Statut de déploiement (Règle d'arbitrage) :**  
> Le modèle ajusté n'est **pas déployé sur le site en ligne** à ce stade. Son intégration éventuelle pour le 18 octobre (remplacement de l'encodeur de base sur GitHub Pages) est conditionnée au résultat de la mesure officielle conjointe selon la règle de décision du protocole `05_protocole_ajustement.md` (gain de Recall@5 positif ou nul à la fois sur le jeu de l'équipe et sur le CDTN).

---

## 6. Synthèse et État d'avancement de l'Issue #49

- [x] **Génération de paires synthétiques avec le modèle local** : 109 paires question-passage générées avec Qwen2.5-7B local.
- [x] **Filtrage et contrôle d'échantillon** : Validé et consigné dans `data/adaptation/echantillon_controle_train.json`.
- [x] **Empreinte d'authentification des données** : SHA-256 de `train_paires.jsonl` consigné (`2d377eb6...`) pour authentifier de manière unique le jeu d'entraînement.
- [x] **Vérification d'absence de fuite du test** : 67 fiches totalement exclues du train set, contrôle heuristique Jaccard < 0,40 documenté.
- [x] **Ajustement contrastif (négatifs du lot)** : Réalisé avec `MultipleNegativesRankingLoss`, recette déclarée figée au 13 octobre.
- [x] **Banc exploratoire documenté** : Chiffres préliminaires étiquetés « exploratoires, hors protocole » selon la décision du Weekly 4.
- [x] **Quantification ONNX q8 alignée Xenova** : Export avec `per_channel=True`, `reduce_range=True` et `ActivationSymmetric=True` (112,9 Mio, 74/75 tenseurs identiques bit à bit).
- [x] **Modèle témoin de BASE exporté** : Export du modèle pré-entraîné avec la même recette pour isoler les effets de graphe opset 14.
- [x] **Contrôle de fidélité dans le navigateur (Notebook 02)** : 91,61 % de concordance Top-1 et 99,88 % dans le Top-5 sur les 822 requêtes mesurées dans Chromium WASM via `scripts/indexation/fidelite_navigateur.html`.
- [x] **Calcul automatisé et empreintes SHA-256 versionnés** : Script `scripts/adaptation/08_calculer_metriques_navigateur.py` consignant les métriques et empreintes cryptographiques.
- [x] **Dépendances épinglées** : Fichier `scripts/adaptation/requirements.txt` (`onnx==1.23.2`, `onnxruntime==1.30.0`).
- [x] **Poids et données hors Git** : Dossiers `models/` et `data/` intégralement protégés par le `.gitignore`.
- [ ] **Mesure officielle et décision de déploiement** : Planifiée au Weekly 5 (15 octobre) selon le protocole officiel commun `05_protocole_ajustement.md`.

