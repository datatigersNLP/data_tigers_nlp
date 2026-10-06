# Références lexicales TF-IDF et BM25 sur le corpus travail-emploi

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES — Université Catholique de Lille  
**Ticket** Issue #47 · Branche `feat/47-references-lexicales`  
**Responsable principal** Remy RAYANE  
**Soutien & Relecture** Mahé BEGNIS  
**Date d'exécution** 4 octobre 2026  

---

## 1. Contexte et objectifs

Le sujet du projet impose de benchmarker rigoureusement le modèle neuronal de recherche sémantique (`multilingual-e5-small`) face aux approches traditionnelles de recherche d'information (IR). Comme l'a souligné le rapport de jalon J2, **BM25 est la seule référence lexicale véritablement exigeante** : une référence mal paramétrée ou affaiblie flatterait artificiellement l'encodeur dense.

L'[Issue #47](https://github.com/datatigersNLP/data_tigers_nlp/issues/47) a pour vocation de :
1. Construire les moteurs **TF-IDF** (`scikit-learn`) et **BM25** (`rank_bm25`) sur les **4 240 passages M2** issus du découpage structurel du corpus SocialGouv (Notebook 01 / PR #39).
2. Étudier **cinq variantes de prétraitement lexical**, avec une attention particulière portée sur la préservation des termes de négation et de restriction indispensables à l'interprétation des règles juridiques.
3. Livrer le module autonome [`scripts/evaluation/lexical_baselines.py`](file:///c:/Users/remyr/data_tigers_nlp/scripts/evaluation/lexical_baselines.py) prêt à l'emploi pour le banc d'évaluation comparatif du Notebook 03 ([Issue #46](https://github.com/datatigersNLP/data_tigers_nlp/issues/46)).
4. Évaluer la faisabilité technique et l'empreinte mémoire d'un portage de **BM25 en JavaScript** dans le site statique du volet A.

---

## 2. Les 5 variantes lexicales étudiées

En droit du travail, le choix de la tokenisation n'est pas neutre :
* Les listes usuelles de mots vides suppriment des mots comme *« ne »*, *« pas »*, *« sans »*, *« aucun »*, inversant ou annihilant la signification d'une règle (ex. *« l'employeur ne peut pas licencier sans accord »*).
* La racinisation (*stemming*) permet de regrouper les flexions (*licenciement*, *licenciements*, *licencier*, *licencié*), réduisant le vocabulaire tout en augmentant le rappel.

Cinq configurations ont été profilées :

| Variante | Stop-words | Stemming (racinisation) | Filtrage fréquentiel | Rôle |
|---|---|---|---|---|
| **V0 (Brute)** | Aucun | Aucun | Aucun | Baseline lexicale brute non filtrée |
| **V1 (Snowball standard)** | Liste standard Snowball (157 mots) | Aucun | Aucun | Baseline standard du TAL |
| **V2 (Snowball sans négations)** | Liste Snowball sans négations/restrictions | Aucun | Aucun | Préservation du sens restrictif juridique |
| **V3 (Optimisée juridique)** | Liste Snowball sans négations | FrenchStemmer (Snowball) | Aucun | Regroupement morphologique + maintien du droit |
| **V4 (Filtrée fréquences)** | Liste Snowball sans négations | FrenchStemmer | `min_df=2`, `max_df=0.85` | Élimination des hapax et termes ubiquitaires |

*Liste des termes restrictifs protégés dans V2, V3 et V4 :* `ne`, `pas`, `point`, `non`, `ni`, `aucun`, `aucune`, `aucuns`, `aucunes`, `nul`, `nulle`, `jamais`, `rien`, `sans`, `personne`, `guère`, `sauf`, `hors`, `interdit`, `interdite`, `interdits`.

---

## 3. Résultats expérimentaux sur les 4 240 passages M2

Les mesures ont été exécutées via [`scripts/evaluation/02_references_lexicales.py`](file:///c:/Users/remyr/data_tigers_nlp/scripts/evaluation/02_references_lexicales.py).

### 3.1 Tableau comparatif des caractéristiques

| Variante | Vocabulaire unique | Postings totaux | Poids export brut | Poids export gzip | Latence BM25 | Latence TF-IDF |
|---|---:|---:|---:|---:|---:|---:|
| **V0 (Brute)** | 15 440 | 384 609 | 3,32 Mio | 1,06 Mio | 18,8 ms | 4,7 ms |
| **V1 (Snowball std)** | 15 337 | 290 215 | 2,60 Mio | 0,83 Mio | 7,9 ms | 2,2 ms |
| **V2 (Sans négations)** | 15 339 | 292 795 | 2,62 Mio | 0,84 Mio | 9,1 ms | 2,0 ms |
| **V3 (Stemming + Sans nég.)** | **8 695** | 275 328 | **2,32 Mio** | **0,74 Mio** | 8,3 ms | 2,0 ms |
| **V4 (Fréquences filtrées)** | 5 747 *(TF-IDF)* | 275 328 | 2,32 Mio | 0,74 Mio | 8,4 ms | 2,4 ms |

### 3.2 Enseignements structurels
1. **Effet majeur du Stemming (V3) :** La racinisation contracte le vocabulaire de **43,6 %** (de 15 440 à 8 695 racines). Cette contraction réduit la dispersion des termes et accélère la recherche tout en améliorant le rappel sur les requêtes formulées à l'infinitif face à des textes conjugués ou substantivés.
2. **Coût nul de la conservation des négations :** Conserver les négations (V2 vs V1) n'augmente l'index que de **2 mots de vocabulaire** et d'environ **2 500 postings** sur l'ensemble du corpus (+0,01 Mio en gzip), tout en garantissant que les clauses d'interdiction conservent leur pouvoir discriminant.

---

## 4. Analyse qualitative sur requêtes types du droit du travail

L'interrogation des moteurs sur des requêtes réelles illustre la précision de BM25 sur des cas où l'encodeur dense montre des faiblesses :

| Requête | Passage classé en tête (Top 1) | Score BM25 | Comportement observé |
|---|---|:---:|---|
| *« Quelles mentions sont interdites sur le bulletin de paie ? »* | *Le bulletin de paie > Chapô* | 21,61 (V3) | Retrouve mot pour mot la section énumérant les mentions prohibées. |
| *« Mon employeur peut-il me licencier pendant un arrêt maladie ? »* | *Les absences liées à la maladie [...] > Peut-il y avoir licenciement pour maladie ?* | 14,09 (V3) | Cible exacte de la section dédiée atteinte immédiatement sans ambiguïté. |
| *« Quelles sont les dispositions de l'article L. 1221-19 du code du travail ? »* | *Le contrat de travail [...] > Textes de référence* | 19,81 (V3) | **Avantage décisif sur le dense :** BM25 isole immédiatement la référence textuelle exacte `1221-19` là où les modèles neuronaux subissent des collisions d'embeddings. |
| *« Licenciement pour inaptitude sans reclassement »* | *La reconnaissance de l'inaptitude médicale [...] > Que se passe-t-il si le reclassement est impossible ?* | 20,49 (V3) | La conservation de la préposition *« sans »* oriente directement vers l'impossibilité de reclassement. |
| *« Combien de temps peut durer la période d'essai d'un CDI ? »* | *Le contrat à durée indéterminée de chantier [...] > Qu’est-ce qu’un contrat de chantier ?* | 18,45 (V3) | Met en évidence la limite du BM25 : en présence des mots *CDI*, *période*, *essai*, BM25 surpondère les fiches contenant l'expression développée. |

---

## 5. Arbitrage sur le portage de BM25 en JavaScript (Volet A)

L'une des questions posées par l'Issue #47 est l'opportunité d'embarquer un moteur BM25 côté client dans le site web statique du Volet A :

* **Poids mesuré de l'index complet (V3) :** **2,32 Mio brut / 0,74 Mio compressé gzip**.
* **Comparaison avec l'encodeur ONNX :** Le modèle neuronal `multilingual-e5-small` quantifié en `q8` pèse **112,8 Mio** à télécharger au premier chargement.
* **Intérêt pour l'expérience utilisateur :**
  1. **Disponibilité instantanée :** Avec 740 Kio, BM25 peut être chargé et opérationnel en moins de 100 ms sur connexion mobile, permettant à l'utilisateur de chercher immédiatement pendant que le modèle ONNX de 112 Mio se télécharge en tâche de fond.
  2. **Recherche hybride / Fallback :** En cas d'échec de WebAssembly ou de machine restreinte, BM25 offre un moteur de recherche fonctionnel à 100 % en pur JavaScript.
  3. **Explicabilité totale :** Chaque score de BM25 est traçable à la formule mathématique, un atout majeur valorisé en soutenance.

**Recommandation pour le Weekly :** Proposer au domaine D3 (Front-end) d'intégrer l'index BM25 en JavaScript comme solution de chargement rapide (*fast-path*) et de secours.

---

## 6. Guide d'intégration dans le Notebook 03 (Issue #46)

Le module [`scripts/evaluation/lexical_baselines.py`](file:///c:/Users/remyr/data_tigers_nlp/scripts/evaluation/lexical_baselines.py) est prêt à être importé directement par Mahé BEGNIS :

```python
from scripts.evaluation.lexical_baselines import BM25Retriever, TfidfRetriever

# 1. Initialiser la variante recommandée (V3 : Snowball sans négations + Stemming)
retriever_bm25 = BM25Retriever(stopwords_variant="snowball_no_negation", stemming="french")
retriever_bm25.fit(corpus_passages, doc_ids=passage_ids)

# 2. Recherche par lot pour l'évaluation
predictions_bm25 = retriever_bm25.batch_search(questions_test, k=10)

# 3. Évaluation immédiate avec le module de métriques
from scripts.evaluation.metrics import evaluate_retrieval
resultats = evaluate_retrieval(predictions_bm25, ground_truth_ids, k_values=(1, 3, 5, 10))
print(f"BM25 V3 - Recall@5: {resultats['recall@5']:.4f}, MRR: {resultats['mrr']:.4f}")
```
