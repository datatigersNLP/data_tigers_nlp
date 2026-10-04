# Validation de la chaîne de mesure de la recherche — Jeu PIAF

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES — Université Catholique de Lille  
**Ticket** Issue #45 · Branche `feat/45-metriques-piaf`  
**Responsable principal** Remy RAYANE  
**Soutien & Relecture** Mahé BEGNIS  
**Date d'exécution** 3 octobre 2026  

---

## 1. Contexte et objectif

Le sujet impose d'évaluer rigoureusement le système de recherche d'information (IR) sur le corpus du droit du travail au jalon J3 (Notebook 03 / Issue #46). 

Avant d'appliquer ces mesures à notre corpus et à notre propre jeu de questions, l'[Issue #45](https://github.com/datatigersNLP/data_tigers_nlp/issues/45) a pour but de **valider la chaîne mathématique et logicielle de mesure sur un jeu public français déjà annoté et incontestable** : **PIAF** (`AgentPublic/piaf`, licence MIT).

Cette validation préalable poursuit trois impératifs :
1. **Garantir l'exactitude des métriques** ($\text{Recall@}k$ et $\text{MRR}$) par des tests unitaires et des assertions confrontées à des calculs manuels.
2. **Fournir un module de calcul propre et réutilisable** (`scripts/evaluation/metrics.py`) pour le Notebook 03.
3. **Établir une première comparaison appariée** entre l'approche lexicale classique (**BM25**) et l'approche dense par plongements (**`multilingual-e5-small`**).

---

## 2. Données et protocole expérimental

### 2.1 Jeu de données PIAF

* **Dépôt Hugging Face :** `AgentPublic/piaf`
* **Révision figée (reproductibilité) :** `bda8c063bc7297180796cd835d1974c0bc71c521`
* **Licence :** MIT
* **Volumétrie extraite :**
  * **Passages uniques (contextes Wikipédia) :** $N = 761$
  * **Questions annotées :** $Q = 3\,835$ (chaque question est associée de manière déterministe à son contexte d'origine via son identifiant).

### 2.2 Systèmes comparés

1. **Baseline Aléatoire :** Tirage uniforme sans remise de 10 passages parmi les 761 disponibles.
2. **Baseline Lexicale BM25 :** Implémentation `BM25Okapi` (`rank_bm25`) sur les 761 contextes tokenisés en minuscules.
3. **Recherche Dense E5 :** Modèle `intfloat/multilingual-e5-small` (384 dimensions, budget maximal de 512 tokens) :
   * Préfixe strict `"passage: "` pour les 761 contextes.
   * Préfixe strict `"query: "` pour les 3 835 questions.
   * *Mean pooling* avec masque d'attention et normalisation $L_2$ des vecteurs.
   * Score de pertinence calculé par produit scalaire direct : $\mathbf{S} = \mathbf{Q} \cdot \mathbf{P}^T$.

### 2.3 Formules des métriques

* **$\text{Recall@}k$ :** Vaut $1{,}0$ si le document cible figure parmi les $k$ premiers résultats triés par score décroissant, $0{,}0$ sinon :
  $$\text{Recall@}k = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \mathbb{I}(\text{rang}_q \le k)$$
* **Mean Reciprocal Rank ($\text{MRR}$) :** Moyenne de l'inverse du rang du passage cible :
  $$\text{MRR} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{1}{\text{rang}_q}$$

### 2.4 Test statistique apparié (McNemar)

Pour comparer la supériorité de Dense E5 sur BM25 au seuil critique $\text{Recall@}5$ (cible standard pour la transmission au LLM ou à l'interface), nous appliquons le test de McNemar avec correction de continuité d'Edwards et calcul de la p-valeur binomiale exacte sur les paires de discordance :
$$\chi^2 = \frac{(|n_{10} - n_{01}| - 1)^2}{n_{10} + n_{01}}$$
où $n_{10}$ désigne les requêtes où E5 seul place la cible dans le top 5, et $n_{01}$ les requêtes où BM25 seul y parvient.

---

## 3. Résultats expérimentaux

Les mesures ont été exécutées de manière déterministe sur machine locale CPU via le script `scripts/evaluation/01_valider_sur_piaf.py`.

### 3.1 Tableau comparatif des performances (3 835 requêtes)

| Méthode | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR | Temps moy. requête (CPU) |
|---|---:|---:|---:|---:|---:|---:|
| **Aléatoire** (baseline) | 0,08 % | 0,37 % | 0,76 % | 1,30 % | 0,0036 | $< 0{,}01\text{ ms}$ |
| **BM25** (lexical) | 64,25 % | 77,00 % | 81,07 % | 85,66 % | 0,7147 | $0{,}37\text{ ms}$ |
| **Dense E5** (`multilingual-e5-small`) | **66,78 %** | **83,21 %** | **87,20 %** | **90,90 %** | **0,7567** | $6{,}08\text{ ms}$ |

*Écart Dense E5 vs BM25 sur Recall@5 :* **$+6{,}13$ points de pourcentage** en faveur de E5.

### 3.2 Résultats du test de McNemar sur le Recall@5

Table de contingence sur les 3 835 requêtes :

| | BM25 Échec | BM25 Succès (Top 5) | Total |
|---|---:|---:|---:|
| **E5 Échec** | 288 ($n_{00}$) | 203 ($n_{01}$) | 491 |
| **E5 Succès (Top 5)** | **438 ($n_{10}$)** | 2 906 ($n_{11}$) | 3 344 |
| **Total** | 726 | 3 109 | 3 835 |

* **Paires discordantes ($n_{10} + n_{01}$) :** $641$ requêtes
* **Avantage net E5 :** 438 victoires contre 203 pour BM25
* **Statistique $\chi^2$ (Edwards) :** **$85{,}42$**
* **p-valeur (test binomial exact) :** **$8{,}84 \cdot 10^{-21}$** ($p \ll 0{,}001$)

**Conclusion statistique :** L'avantage de l'encodeur dense `multilingual-e5-small` sur BM25 est hautement significatif sur le jeu PIAF.

---

## 4. Analyse qualitative d'échantillons

L'inspection de cas concrets illustre les forces respectives des deux familles de modèles :

| Question | Document cible | Rang E5 | Rang BM25 | Analyse du comportement |
|---|---|:---:|:---:|---|
| *« Combien de personnes travaillent au ministère des sports »* | `Sport` | **1** | **1** | Termes lexicaux explicites et spécifiques : les deux approches retrouvent le paragraphe immédiatement. |
| *« qui est le pere de John? »* | `Terminator 2` | **1** | **3** | Formulation concise avec mot de liaison et graphie familière : E5 capte la relation sémantique et hisse le passage au rang 1, alors que BM25 est pénalisé par le manque de densité des mots-clés. |
| *« Par quelles lois est régi un indigène musulman qui a la les droits de citoyen français ? »* | `Algérie` | **1** | **1** | Formulation juridique complexe : les deux méthodes parviennent à retrouver le texte exact. |

---

## 5. Ce que cette étude établit, et ce qu'elle n'établit pas

### Ce qui est fermement établi
1. **La justesse mathématique du code :** L'implémentation dans `scripts/evaluation/metrics.py` a été vérifiée par des calculs manuels préalables et validée sur 3 835 requêtes réelles. Les formules ne présentent aucun biais d'indexation (*off-by-one error*).
2. **La reproductibilité :** L'ensemble du banc s'exécute de bout en bout en une seule commande (`python scripts/evaluation/01_valider_sur_piaf.py`), en moins de 30 secondes sur CPU, avec des graines déterministes.
3. **Le comportement de base de E5 :** Sans aucun fine-tuning, `multilingual-e5-small` surclasse significativement une référence BM25 standard en français sur du texte encyclopédique.

### Ce qui n'est pas établi (Limites explicites)
* **Transférabilité au droit du travail :** PIAF est composé d'articles de Wikipédia rédigés dans un style journalistique/encyclopédique. Le corpus SocialGouv du projet est un corpus réglementaire et juridique, caractérisé par un vocabulaire technique strict, des articles de loi (LEGIARTI) et des sigles métiers (CDI, CDD, RTT, CSE).
* **Sensibilité aux sigles :** Comme observé lors du Notebook 02 sur l'exemple de la « période d'essai d'un CDI », l'encodeur dense peut échouer sur des acronymes non développés là où BM25 excelle. Ce point devra faire l'objet d'une attention particulière dans le Notebook 03 et justifie l'intérêt d'une référence lexicale (Issue #47) et d'un fine-tuning (Issue #49).

---

## 6. Guide de réutilisation pour le Notebook 03

Le module [`scripts/evaluation/metrics.py`](file:///c:/Users/remyr/data_tigers_nlp/scripts/evaluation/metrics.py) est autonome et directement importable dans les notebooks et scripts de l'équipe :

```python
from scripts.evaluation.metrics import evaluate_retrieval, compute_mcnemar_test

# predictions: liste de listes d'identifiants triés par pertinence décroissante
# ground_truth: liste des identifiants cibles attendus
resultats = evaluate_retrieval(predictions, ground_truth, k_values=(1, 3, 5, 10))
print(f"Recall@5: {resultats['recall@5']:.4f}, MRR: {resultats['mrr']:.4f}")

# Comparaison statistique entre deux systèmes (ex: E5 vs BM25)
test_stat = compute_mcnemar_test(preds_e5, preds_bm25, ground_truth, k=5)
print(f"p-valeur McNemar: {test_stat['p_value']:.4e} (Significatif: {test_stat['significant_5pct']})")
```
