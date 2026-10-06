# Étude d'ajustement contrastif de l'encodeur sémantique sur le corpus SocialGouv

**Auteur principal :** Remy RAYANE (Responsable D2 & Issue #49)  
**Soutien & Relecture :** Mahé BEGNIS, Jibril BENSALEM  
**Date :** 6 octobre 2026  
**Référence :** Issue GitHub #49 (`feat/49-ajustement-encodeur`)  
**Statut :** Exécuté intégralement, validé statistiquement, prêt pour revue

---

## 1. Contexte et Objectifs

Le sujet du projet impose que l'application de recherche sémantique du Volet A ne se contente pas d'exécuter un modèle générique sur étagère, mais s'appuie sur un modèle adapté au domaine juridique du Code du travail et des fiches pratiques du ministère du Travail (SocialGouv).

L'**Issue #49** a pour objet d'ajuster finement l'encodeur `intfloat/multilingual-e5-small` par **apprentissage contrastif** (*contrastive learning*) sur des paires `(question, passage)` représentatives du corpus, et d'en mesurer scientifiquement le gain par un protocole expérimental apparié et reproductible.

### Contraintes méthodologiques strictes
1. **Étancheité absolue (*Zero Data Leakage*)** : Aucune fiche, aucun passage et aucune question du jeu de test (Issue #44 / PR #54) ne doit servir à l'entraînement ou à la sélection du modèle.
2. **Préservation du protocole E5** : Conservation systématique des préfixes obligatoires (`query: ` pour les requêtes et `passage: ` pour les documents).
3. **Évaluation statistique appariée** : Calcul des métriques de rang (`Recall@k`, `MRR@10`) avec test exact de McNemar et test d'Obuchowski (données groupées par fiche) pour trancher la significativité statistique de l'écart.
4. **Portabilité navigateur (ONNX & Quantification)** : Export ONNX FP32, quantification dynamique INT8 (`q8`) et vérification des critères de parité et fidélité établis au Notebook 02.
5. **Gestion des artefacts hors Git** : Les poids PyTorch et les fichiers `.onnx` dépassant 100 Mio restent exclus du versionnement Git (règle stricte du projet).

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
* **Filtrage automatique** :
  * Contrôle syntaxique (interrogation finale, longueur entre 25 et 220 caractères).
  * Contrôle de non-recouvrement lexical : rejet automatique si la similarité Jaccard sur les tokens avec une question du jeu de test dépasse 0,40.
* **Résultat** : **109 paires validées**, 1 rejetée. Un échantillon de contrôle a été audité manuellement dans `data/adaptation/echantillon_controle_train.json`.

---

## 3. Ajustement Contrastif de l'Encodeur

### 3.1 Architecture et Fonction de Perte
* **Modèle de départ** : `intfloat/multilingual-e5-small` (117 millions de paramètres, dimension 384).
* **Fonction de perte** : `MultipleNegativesRankingLoss` (MNRL).
  * Pour chaque mini-batch de taille $B$, la perte maximise la similarité cosinus entre la question $\mathbf{q}_i$ et son passage cible $\mathbf{p}_i$, tout en utilisant l'ensemble des $B-1$ autres passages du lot comme négatifs implicites (*in-batch negatives*).
  * Température / facteur d'échelle : échelle standard SentenceTransformers ($s = 20.0$).

### 3.2 Hyperparamètres d'entraînement
Les hyperparamètres ont été choisis pour adapter le modèle au vocabulaire du droit du travail sans détruire sa structure multilingue pré-entraînée (*catastrophic forgetting*) :
* **Taille de lot (*batch size*)** : 16 (soit 15 négatifs par exemple).
* **Taux d'apprentissage (*learning rate*)** : $2 \times 10^{-5}$ avec optimiseur AdamW et décroissance linéaire.
* **Époques** : 2 (14 pas d'optimisation).
* **Warmup** : 10 % des étapes.
* **Durée d'entraînement** : 185,5 secondes sur CPU (16 cœurs).

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

## 4. Résultats et Validation Statistique

L'évaluation compare les performances de récupération d'information (*Information Retrieval*) avant et après ajustement, en indexant la totalité des **4 240 passages M2** et en interrogeant le modèle avec les **72 questions de test**.

### 4.1 Tableau comparatif des métriques de recherche

| Métrique | Avant (Base pré-entraîné) | Après (Modèle ajusté) | Gain absolu | Valeur *p* (McNemar / Obuchowski) | Significatif ($\alpha = 0.05$) |
|---|---|---|---|---|---|
| **Recall@1** | 19,44 % | **26,39 %** | **+6,94 %** | $p = 0.2004$ | Non |
| **Recall@3** | 37,50 % | **51,39 %** | **+13,89 %** | $p = 0.0080$ | **OUI** ($p < 0.01$) |
| **Recall@5** | 43,06 % | **62,50 %** | **+19,44 %** | $p = 0.0002$ | **OUI** ($p < 0.001$) |
| **Recall@10** | 58,33 % | **73,61 %** | **+15,28 %** | $p = 0.0048$ | **OUI** ($p < 0.01$) |
| **MRR@10** | 0,3250 | **0,4203** | **+0,0954** | — | — |

### 4.2 Analyse des résultats
1. **Bond spectaculaire sur Recall@5 (+19,44 points)** :
   Le Recall@5 passe de 43,06 % à 62,50 %. La valeur *p* du test apparié avec regroupement par fiche est de **$0.0002$**, ce qui démontre une amélioration hautement significative sur le plan statistique.
2. **Gain substantiel en précision de premier rang (MRR@10 : +0,0954)** :
   Le rang réciproque moyen passe de 0,325 à 0,420, signifiant que le passage pertinent apparaît désormais en moyenne entre la 2e et la 3e position au lieu de la 3e et 4e position.
3. **Généralisation confirmée hors fiches vues** :
   Puisque l'entraînement a été effectué exclusivement sur des fiches différentes de celles du test, ce gain atteste que l'encodeur a appris à mieux aligner le style interrogatif des citoyens français avec le formalisme juridique des fiches du ministère, sans aucun effet de mémorisation brute.

---

## 5. Export ONNX et Contrôles de Parité

Pour permettre le déploiement dans le navigateur client via **Transformers.js** (Volet A), le modèle PyTorch affiné a été converti en ONNX et quantifié selon les exigences du Notebook 02.

### 5.1 Fichiers générés

| Format | Fichier | Taille disque | Rôle applicatif |
|---|---|---|---|
| **FP32** | `models/multilingual-e5-small-finetuned/onnx/model.onnx` | 448,5 Mio | Modèle de référence ONNX haute précision |
| **INT8 (q8)** | `models/multilingual-e5-small-finetuned/onnx/model_quantized.onnx` | 112,7 Mio | Modèle compact servi au navigateur Web |

### 5.2 Contrôles de conformité

1. **Contrôle 1 : Parité numérique FP32 (PyTorch vs ONNX FP32)** :
   * **Cosinus minimal** : $1.00000000$ (seuil de parité strict : $\ge 0.99999$).
   * **Écart absolu maximal composante** : $1,17 \times 10^{-7}$.
   * **Statut** : **VALIDÉ AVEC SUCCÈS**.

2. **Contrôle 2 : Fidélité de la quantification INT8 (PyTorch FP32 vs ONNX q8)** :
   * **Cosinus médian** : $0.9834$ (seuil attendu : $\ge 0.98$).
   * **Cosinus minimal** : $0.9789$ (seuil : $\ge 0.97$).
   * **Concordance du Top-1** : $100,0\ \%$ sur le banc de validation.
   * **Statut** : **VALIDÉ AVEC SUCCÈS**.

---

## 6. Synthèse et Livrables de l'Issue #49

Tous les critères de validation et livrables de l'Issue #49 sont rigoureusement remplis :

- [x] **Génération de paires synthétiques avec le modèle local** : 109 paires question-passage générées avec Qwen2.5-7B local.
- [x] **Filtrage et contrôle d'échantillon** : Validé et consigné dans `data/adaptation/echantillon_controle_train.json`.
- [x] **Vérification d'absence de fuite du test** : 67 fiches totalement exclues du train set, contrôle Jaccard < 0.40.
- [x] **Ajustement contrastif (négatifs du lot)** : Réalisé avec `MultipleNegativesRankingLoss` et préfixes `query: ` / `passage: `.
- [x] **Mesure avant/après appariée** : Recall@5 en hausse de **+19,44 pts** ($p = 0.0002$).
- [x] **Conversion ONNX et contrôles notebook 02** : Parité FP32 ($1.00000000$) et fidélité q8 validées.
- [x] **Poids hors Git** : Dossier `models/` protégé par le `.gitignore`.
