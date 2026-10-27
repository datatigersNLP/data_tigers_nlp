# Support de présentation — Jalon J3 (15 points)
**Module** NLP 2 · Master 2 Data & IA · FGES — Université Catholique de Lille  
**Équipe** Data Tigers : Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE  
**Statut** Version de cadrage pour le Weekly 7 (Ticket #112) · Projet à 2 volets

---

## Diapositive 1 — Titre, Équipe et Cadrage du Jalon J3

### Contexte & Rappel des deux volets imposés
Le projet impose la réalisation conjointe de deux applications complémentaires basées sur le corpus du droit du travail (fiches pratiques du Ministère du Travail / Code du Travail Numérique) :

* **Volet A (Application en ligne)** : Cas A3 — Moteur de recherche sémantique dense sans serveur.
  * Inférence 100 % client dans le navigateur (Transformers.js / WebAssembly).
  * Coût d'exploitation nul : hébergement statique sur GitHub Pages, aucun appel API externe.
* **Volet B (Application locale)** : Cas B1 — Assistant juridique interactif avec chaîne RAG.
  * Inférence locale sur modèle open-weights (`Qwen2.5-7B-Instruct`).
  * Adaptation du modèle par fine-tuning LoRA, sourçage formel des réponses (`[Pn]`) et évaluation rigoureuse avant/après.

### Objectifs du Jalon J3 (15 points)
1. **Volet A finalisé et déployé** : Moteur de recherche sémantique réactif, modèle élagué hébergé sous le quota strict de 100 Mio, abstention active et accessibilité validée.
2. **Volet B engagé** : Socle RAG opérationnel, protocoles de mesure et de séparation verrouillés, faisabilité matérielle du fine-tuning démontrée.
3. **Supports et méthodologie** : Démonstrations reproductibles, tenue du board et du journal d'usage IA.

---

## Diapositive 2 — Volet A : Architecture technique & Déploiement sans serveur

### Contraintes & Choix d'ingénierie
* **Inférence 100 % in-browser** : Aucun backend Python en production. L'application est servie comme site statique via GitHub Pages.
* **Moteur d'exécution** : Transformers.js adossé à ONNX Runtime Web (WebAssembly / SIMD).
* **Encodeur dense** : `multilingual-e5-small` quantifié en 8 bits (q8) pour concilier compacité et fidélité de représentation sémantique.
* **Asymétrie de l'encodage E5** : Préfixe obligatoire `query: ` pour la requête utilisateur et `passage: ` pour les documents indexés, garantissant le respect de la géométrie de l'espace latent.

### Optimisation du chargement et du calcul
* **Normalisation L2 préalable** : Les vecteurs de passages et de requêtes sont normalisés unitairement ($\|v\|_2 = 1$). La similarité cosinus est alors rigoureusement équivalente à un produit scalaire en $O(d)$ ($d = 384$).
* **Index binaire Little-Endian Float32** : Remplacement de l'index JSON initial par un format binaire direct (`index.bin`). Le chargement s'effectue via l'API `TypedArray` (`Float32Array`) en mémoire vive sans bloquer le thread UI du navigateur, supprimant les 1,2 s de latence observées avec `JSON.parse()`.
* **Réactivité mesurée** : Recherche effectuée en moins de 25 ms côté client sur Chromium et Firefox.

---

## Diapositive 3 — Volet A : Allègement du modèle & Levée du blocage d'hébergement (#50)

### Le verrou technique GitHub Pages
* **Limite stricte par fichier** : GitHub bloque tout fichier supérieur à 100 Mio.
* **Le modèle standard intenable** : Le modèle `multilingual-e5-small` quantifié q8 pèse **112,8 Mio**, interdisant son hébergement direct sur le dépôt GitHub du site sans recourir au CDN externe Hugging Face (point de défaillance tiers proscrit par l'audit du sujet).

### Analyse structurelle & Élagage sans perte
* **Diagnostic de l'architecture** : L'analyse des tenseurs révèle que **81,6 % des paramètres** de l'encodeur sont concentrés dans la table d'embeddings du vocabulaire (250 037 lignes de 384 dimensions), conçue pour couvrir plus de 100 langues.
* **Recette d'élagage ciblé** (`scripts/allegement/`) :
  * Détection de tous les sous-mots réellement requis par le corpus juridique français M2, le jeu d'évaluation et les requêtes courantes.
  * Réduction de la matrice d'embeddings aux seuls tokens nécessaires, sans modifier les couches d'attention ni de feed-forward du Transformer.
* **Résultats obtenus** :
  * Poids du modèle abaissé de **112,8 Mio à 65,7 Mio** (**-41,8 %**).
  * **Parité bit à bit stricte** : 100 % d'identité vectorielle vérifiée sur les 822 vecteurs du jeu de contrôle par rapport au q8 de référence.
  * Modèle servi directement en local depuis `front/public/modele/`, garantissant l'autonomie totale du site.

---

## Diapositive 4 — Volet A : Évaluation quantitative & Règle d'abstention (#46, #53)

### Chaîne d'évaluation de l'IR (Information Retrieval)
* **Jeu de test annoté** : 60 questions humaines annotées sur le corpus, complétées par les 155 requêtes du Code du Travail Numérique (CDTN, #56).
* **Supériorité prouvée face aux baselines lexicales** :
  * **TF-IDF** (Recall@5 : 54,2 %) et **BM25** (Recall@5 : 56,8 %).
  * **Recherche dense E5 q8** : **Recall@5 = 83,6 %** sur la bonne fiche (+26,8 points par rapport à BM25).
* **Test de non-infériorité statistique** : McNemar apparié confirmant l'absence de régression significative entre le modèle exact FP32 et le modèle quantifié q8 ($p > 0,05$).

### Mécanisme d'abstention active (#53)
* **Problématique** : Empêcher le moteur de renvoyer un passage hors-sujet en cas de question hors corpus ou absurde.
* **Calibrage du seuil d'abstention** : Détermination par courbe ROC / AUC sur jeu de requêtes pièges négatives.
* **Seuil fixé à $\theta = 0,8165$** :
  * Si la similarité cosinus maximale est inférieure à ce seuil, le moteur s'abstient explicitement d'afficher des fiches trompeuses.
  * Affichage d'un message transparent d'avertissement invitant l'utilisateur à reformuler ou à consulter les sources officielles.

---

## Diapositive 5 — Volet B : Socle RAG & Inférence locale (#31, #51, PR #85)

### Architecture de la chaîne locale
* **Modèle génératif open-weights** : `Qwen2.5-7B-Instruct` servi localement sous Ollama au format quantifié 4 bits (GGUF Q4_K_M, 4,36 Gio en VRAM).
* **Index commun et récupération** : Réutilisation stricte de l'index des 4 240 passages du corpus M2 (`passages_m2.json`), garantissant la cohérence documentaire entre Volet A et Volet B.
* **Injection contextuelle** : Récupération des 5 passages les plus pertinents et construction dynamique du prompt de contexte via la fonction certifiée `construire_contexte` (`scripts/rag/rag.py`).

### Cadrage de la génération (`rag-b1-v1`)
* **Prompt système strict** : Interdiction formelle d'extrapoler ou d'inventer des dispositions juridiques non présentes dans le contexte.
* **Obligation de sourçage** : Chaque assertion factuelle doit être adossée à une balise explicite de citation `[P1]` à `[P5]`, facilitant l'audit d'exactitude par un juriste.
* **Performances mesurées** :
  * Débit de génération : **47 à 67 tokens/s** en inférence GPU locale.
  * Latence au premier token : **< 2,0 s**.
  * Confidentialité absolue : 100 % des calculs réalisés en local, aucune dépendance réseau.

---

## Diapositive 6 — Volet B : Faisabilité de l'adaptation LoRA (Mac vs Legion, #107)

### Cadrage de l'essai de faisabilité (Étape 1 de #107)
* **Objectif** : Valider sur banc d'essai qu'un fine-tuning LoRA (rang 8) de `Qwen2.5-7B` en 4 bits tient en mémoire avec des longueurs de contexte réelles (1 115 à 2 542 tokens, médiane 1 746 tokens issus du RAG).
* **Protocole de mesure étanche** : Essai sur données factices (phrase cible fixe) mesurant exclusivement le pic de mémoire GPU et la durée incrémentale par pas (différence entre 6 et 12 itérations).

### Comparaison expérimentale des deux machines
| Métrique (LoRA 16 couches) | MacBook M4 Pro (PR #109, Mahé) | PC Legion RTX 4060 (PR #118, Jibril) |
|---|---|---|
| **Environnement** | macOS 26 · MLX 0.32 · Metal | Windows 11 · PyTorch 2.11 · CUDA 12.8 |
| **Mémoire physique** | **24 Gio unifiées** | **8 Gio VRAM** (7,96 Gio physiques) |
| **Pic mémoire GPU mesuré** | **7,14 Gio** (compteur Metal) | **9,17 Gio alloués** (PyTorch) |
| **Mémoire libre finale** | **16,86 Gio de marge** | **0 octet libre (saturation)** |
| **Comportement mémoire** | Exécution intégrale en VRAM | Déport sur RAM partagée système |
| **Temps moyen par pas** | **10,5 s** | **273,9 s (4 min 34 s)** |

### Conclusion opérationnelle
* **Arbitrage technique** : Le Legion est disqualifié pour l'entraînement (temps x26 plus long et instabilité due au swap). L'entraînement est confié au **MacBook M4 Pro** (~1 h 30 pour 1 époque de 500 exemples).
* **Répartition des rôles** : Entraînement sur Mac ; conversion, service Ollama et évaluation hébergés sur le Legion.

---

## Diapositive 7 — Volet B : Étanchéité des données & Chaîne de conversion GGUF (#107, PR #115)

### Contrôle formel de séparation des données (Étape 4 de #107)
* **Garantie anti-fuite (Data Leakage)** : Aucune donnée d'entraînement ne doit provenir des fiches du lot de test humain (`jeu-questions-v1`), et aucune question humaine ne doit être apprise.
* **Vérification outillée par script** (`scripts/adaptation_qwen/separation.py`, PR #115) :
  * Exclusion formelle des **61 fiches documentaires** touchées par le lot de test de référence.
  * Rejet automatique si un passage d'entraînement (cible ou distracteur) provient d'une fiche exclue.
  * Rejet de toute question reprenant mot pour mot une question humaine (calibration comprise).
* **Contrat d'échange validé** : Fichier JSONL au format unifié `{"id": str, "question": str, "passages": [passage_id, ...]}`.

### Chaîne d'export et Témoin T au Protocole 06
* **Contrainte Ollama 0.40.5** : L'audit du tag officiel révèle le rejet de la directive `ADAPTER` (`errAdaptersUnsupported`).
* **Méthode de déploiement retenue** :
  1. Fusion des poids de l'adaptateur LoRA dans le modèle de base en demi-précision FP16.
  2. Conversion du modèle fusionné au format GGUF.
  3. Requantification en 4 bits (Q4_K_M).
* **Nécessité méthodologique du Témoin T** :
  * La requantification GGUF introduit de légers bruits d'arrondi indépendants de l'apprentissage.
  * Pour isoler rigoureusement l'impact du fine-tuning, un **modèle témoin T** (modèle de base subissant exactement le même cycle fusion/requantification GGUF) est évalué en parallèle.






