# Récupération v2 : réglage sur le jeu CDTN

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** #138 (récupération v2 du volet B)  
**Responsable** Mahé BEGNIS  
**Statut** réglage fait le 9 novembre 2026, sur le seul jeu CDTN ; règle de choix corrigée par l'amendement A1 avant la lecture des résultats des reclasseurs ; confirmation sur le lot de test à faire selon le protocole 07.

---

## 1. Objet

La chaîne B1 donne au modèle les 5 premiers passages d'E5. Sur le lot de test, le Recall@5 d'E5 vaut 45,2 % au niveau du passage, contre 80,8 % au niveau de la fiche (notebook 03) : le bon document remonte souvent, le bon passage moins. Le 9 novembre, Mahé a retenu quatre leviers, chacun à régler par l'essai :

* le nombre k de passages donnés au modèle ;
* un reclasseur, c'est-à-dire un cross-encoder qui relit chaque couple question et passage ;
* l'ajout des passages voisins de la même section ;
* la fusion des rangs d'E5 et de BM25 V3 (RRF).

Cette étude règle ces leviers sur le jeu CDTN, sans lire les questions du lot de test.

## 2. Données et garde-fous

* **Population** : la règle figée de l'étude 04 (section 6), soit les requêtes jugées « oui » ou « partiel », sans les formulations écartées. Le script retrouve exactement les comptes publiés (131 requêtes, 494 formulations, dont 131 titres) et refuse de tourner sinon. Il contrôle aussi l'empreinte de `evaluation/cdtn/jugements.csv`, et l'accord du jeu local avec `evaluation/cdtn/identifiants.csv`.
* **Population principale** : les formulations en forme de question, plus proches du lot de test. Elles couvrent **82 requêtes**. Les titres (131 requêtes) forment l'analyse secondaire.
* **Analyse de sensibilité** : les requêtes dont aucune fiche n'est parmi les 61 fiches du lot de test, soit **22 requêtes** seulement. Seules les URL du lot de test sont utilisées pour les reconnaître, comme dans `scripts/adaptation_qwen/separation.py`.
* **Pertinence** : celle du CDTN, par section. Tous les passages d'une section citée par la requête sont pertinents, soit 5 en médiane par requête.
* **Chaîne verrouillée intacte** : aucun des dix fichiers du verrou de la mesure n'est modifié. Un test recalcule leurs empreintes et les compare à celles de la PR #131.
* **Budget** : la règle de `generation.preparer_entree`, soit 8 192 − 512 − 64 = **7 616 tokens** de prompt au plus. Le #138 annonçait 7 680, en oubliant la marge de 64 tokens. Au-delà, les derniers passages sont retirés ; aucun passage n'est tronqué.

## 3. Méthode

* **E5** : `intfloat/multilingual-e5-small`, en fp32, avec les fonctions de `scripts/rag/rag.py` (révision `614241f6`).
* **BM25 V3** : la classe du notebook 03, avec mots vides Snowball sans négations et racinisation, sur l'en-tête et le texte des passages M2. Seuls les scores positifs sont classés.
* **Fusion RRF** : score de chaque passage = somme de 1 / (60 + rang) sur les deux classements, calculée en fractions exactes. Départage : meilleur rang, puis indice. La valeur 60 est celle de l'article (Cormack et al., 2009), non réglée ici.
* **Reclasseurs**, à révision épinglée, sans code distant, sur CPU, sur les 20 ou 50 premiers candidats : `BAAI/bge-reranker-v2-m3` (568 millions de paramètres), `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` et `antoinelouis/crossencoder-camembert-base-mmarcoFR`.
* **Contexte** : le format exact de `rag.construire_contexte`, et des tokens comptés avec le tokeniseur de Qwen (révision `a09a3545`).
* **Métrique principale** : le rappel du contexte, c'est-à-dire la part de formulations dont le contexte contient au moins un passage pertinent.
* **Agrégation** : moyenne par requête, puis moyenne sur les requêtes. Intervalles à 95 % par bootstrap sur les requêtes (2 000 tirages, graine 20261109), y compris pour l'écart apparié à la référence.
* **Grille** : 2 sources × (sans reclasseur, ou 3 reclasseurs × 2 nombres de candidats) × 4 valeurs de k × voisins ou non, soit **112 configurations**, toutes publiées.

## 4. Règle de choix et amendement A1

La règle écrite dans le #138 avant toute mesure était de prendre le meilleur rappel du contexte ; à un point près, la configuration la moins coûteuse. La grille sans reclasseur a révélé son défaut.

* **Le défaut** : à classement égal, le rappel du contexte ne peut que croître avec k. La règle choisit donc toujours le plus grand k de la grille. Appliquée à toute la grille, elle aurait retenu `e5+k15+bge-m3@50`.
* **L'amendement A1**, décidé par Mahé et publié sur le #138 avant la lecture des résultats des reclasseurs, fixe k = 10 d'avance, pour le budget et pour rester proche des 5 passages de l'entraînement de l'adaptateur. Le classement est choisi par la même règle, à k = 10 et sans voisins.
* **Les voisins ne sont pas évaluables sur ce jeu.** Un voisin est toujours dans la section de son ancre : sous une pertinence par section, il est pertinent exactement quand l'ancre l'est. Le levier ne peut donc pas changer le rappel du contexte ; les petits écarts observés ne viennent que des coupes de budget. L'évaluer demande une pertinence par passage (#139).

## 5. Résultats

### 5.1 Sans reclasseur

| Configuration | Rappel du contexte | Écart à la référence | Tokens (moyenne / max) |
|---|---|---|---|
| E5, 5 passages (référence, chaîne B1) | 70,9 % [62,9 ; 79,2] | référence | 1 693 / 2 903 |
| Fusion, 5 passages | 70,7 % [61,8 ; 79,2] | −0,2 [−6,1 ; +5,1] | 1 911 / 2 893 |
| E5, 8 passages | 76,9 % [69,0 ; 84,7] | +6,0 [+3,6 ; +8,7] | 2 642 / 4 145 |
| Fusion, 8 passages | 78,5 % [70,1 ; 86,0] | +7,6 [+2,1 ; +13,3] | 2 897 / 4 214 |
| E5, 10 passages | 77,6 % [69,9 ; 85,3] | +6,8 [+4,1 ; +9,7] | 3 244 / 4 811 |
| Fusion, 10 passages | 83,5 % [76,0 ; 90,3] | +12,6 [+7,5 ; +18,4] | 3 563 / 5 101 |
| E5, 15 passages | 85,9 % [79,1 ; 92,2] | +15,0 [+10,0 ; +20,5] | 4 805 / 6 889 |
| Fusion, 15 passages | 86,6 % [79,9 ; 92,6] | +15,7 [+10,4 ; +21,8] | 5 278 / 7 212 |

Population principale : 82 requêtes, formulations en question.

### 5.2 À 10 passages, avec reclasseur

| Configuration | Rappel du contexte | Écart à la référence | nDCG@10 | Tokens (moyenne) |
|---|---|---|---|---|
| E5, bge-m3 sur 50 | 85,7 % [78,8 ; 92,1] | +14,8 [+9,6 ; +20,5] | 0,456 | 3 992 |
| **Fusion, bge-m3 sur 20 (retenue)** | **85,1 % [78,5 ; 91,2]** | **+14,2 [+8,9 ; +19,9]** | **0,460** | **3 953** |
| Fusion, bge-m3 sur 50 | 85,1 % [78,2 ; 91,3] | +14,2 [+8,5 ; +20,2] | 0,459 | 4 086 |
| E5, bge-m3 sur 20 | 83,8 % [77,1 ; 90,1] | +12,9 [+8,2 ; +18,2] | 0,446 | 3 699 |
| Fusion, sans reclasseur | 83,5 % [76,0 ; 90,3] | +12,6 [+7,5 ; +18,4] | 0,417 | 3 563 |
| Fusion, mMiniLM sur 20 | 81,1 % [73,6 ; 87,9] | +10,2 [+3,9 ; +16,7] | 0,448 | 4 123 |
| Fusion, CamemBERT sur 20 | 80,7 % [73,7 ; 87,5] | +9,8 [+3,6 ; +16,3] | 0,422 | 3 846 |
| E5, sans reclasseur | 77,6 % [69,9 ; 85,3] | +6,8 [+4,1 ; +9,7] | 0,380 | 3 244 |
| E5, CamemBERT sur 50 | 73,2 % [65,2 ; 81,0] | +2,3 [−4,3 ; +9,0] | 0,382 | 3 762 |

Les trois premières sont à un point du meilleur, et sont donc éligibles. Le départage par le nombre moyen de tokens retient **la fusion d'E5 et de BM25 V3, suivie de bge-m3 sur 20 candidats, à 10 passages** (`rrf+k10+bge-m3@20`).

### 5.3 À budget égal de 5 passages

| Configuration | Rappel du contexte | Écart à la référence | nDCG@10 |
|---|---|---|---|
| Fusion, bge-m3 sur 20 | 78,5 % [71,3 ; 85,8] | +7,7 [+2,0 ; +13,9] | 0,460 |
| E5, bge-m3 sur 50 | 76,9 % [69,3 ; 84,2] | +6,0 [+0,0 ; +12,4] | 0,456 |
| Fusion, mMiniLM sur 20 | 72,4 % [63,9 ; 80,2] | +1,5 [−5,8 ; +8,8] | 0,448 |
| E5, CamemBERT sur 50 | 67,8 % [60,0 ; 75,9] | −3,1 [−9,9 ; +3,7] | 0,382 |

### 5.4 Configuration retenue, autres populations

| Population | Requêtes | Rappel du contexte | Référence | Précision du contexte (retenue, référence) |
|---|---|---|---|---|
| Questions (principale) | 82 | 85,1 % [78,5 ; 91,2] | 70,9 % | 23,4 %, 25,9 % |
| Titres | 131 | 87,0 % [80,9 ; 92,4] | 69,5 % | 22,6 %, 24,3 % |
| Questions hors fiches du lot de test | 22 | 90,9 % [80,8 ; 99,3] | 81,3 % | 27,8 %, 29,1 % |

Aucune formulation de la configuration retenue n'est coupée par le budget : 5 311 tokens au plus. Les coupes ne touchent que les configurations à 15 passages et celles avec voisins.

## 6. Lecture

* **Le nombre de passages est le levier le plus fort.** Il fait passer le rappel du contexte de 70,9 % à 77,6 % (10 passages) et à 85,9 % (15 passages) avec E5 seul. La précision baisse en contrepartie : 25,9 % à 5 passages, 20,6 % à 10 passages.
* **La fusion avec BM25 ne sert qu'à partir de 8 passages.** À 5 passages, son écart est nul (−0,2) ; à 10 passages, elle double le gain d'E5 seul (+12,6 contre +6,8). BM25 apporte des passages que E5 classe plus bas.
* **bge-m3 est le seul reclasseur utile.** À budget égal de 5 passages, il ajoute de 5,9 à 7,7 points ; à 10 passages, il en ajoute 1,6 de plus que la fusion seule, mais améliore nettement le haut du classement (nDCG@10 de 0,417 à 0,460).
* **Les petits reclasseurs dégradent souvent le classement.** mMiniLM et CamemBERT, entraînés sur mMARCO (une traduction automatique de MS MARCO), font moins bien que la fusion seule à 10 passages, et CamemBERT sur 50 candidats fait à peine mieux que la référence. Plus de candidats ne les aide pas : ils promeuvent davantage de passages non pertinents.
* **Les écarts entre les trois configurations éligibles ne sont pas significatifs.** Ils sont bien plus petits que les intervalles, et le choix entre elles relève du départage par le coût, écrit d'avance.

## 7. Coûts

| Reclasseur | Paires notées | Durée sur le CPU du Mac | Débit |
|---|---|---|---|
| mMiniLM | 32 479 | 357 s | 90,9 paires/s |
| CamemBERT | 32 479 | 834 s | 39,0 paires/s |
| bge-m3 | 32 479 | 3 058 s | 10,6 paires/s |

Les durées ont été mesurées alors que d'autres calculs tournaient sur la machine : elles majorent le coût. Pour la configuration retenue, bge-m3 note 20 candidats par question, soit de l'ordre de 2 s par question sur ce CPU. Le contexte passe de 1 693 à 3 953 tokens en moyenne, ce qui allonge le préremplissage du modèle mais tient largement dans le budget.

## 8. Limites

* **Jugements du CDTN** : ils datent de 2021 et ne sont pas exhaustifs. Un passage qui répond sans être cité compte comme non pertinent, et le rappel est sous-estimé pour tous les systèmes.
* **Malédiction du gagnant** : la configuration retenue est la meilleure parmi 112, sur 82 requêtes. Son rappel sur le CDTN est donc probablement optimiste ; seule la confirmation sur le lot de test, faite une fois, le corrige.
* **Recouvrement des fiches** : les requêtes du CDTN portent en partie sur les fiches du lot de test. L'analyse de sensibilité qui les exclut ne garde que 22 requêtes et reste très imprécise.
* **Lot de test déjà exploité** : le notebook 03 y a publié le Recall@10 d'E5 et les rangs d'E5 et de BM25 jusqu'au 10e passage. Le protocole 07 le déclare.
* **Adaptateur** : il est entraîné sur des contextes de 5 passages d'E5. Un contexte de 10 passages, classés autrement, crée un décalage, que seule la mesure de la chaîne complète évaluera.

## 9. Reproduction

* **Environnement** : `scripts/evaluation/requirements-lock.txt`, Python 3.12.11, macOS sur arm64.
* **Commandes** : voir `scripts/recuperation/README.md`.
* **Empreintes SHA-256 des sorties** (`data/evaluation/recuperation/`, non versionné) : classements `c183aa20e787146a…`, scores de mMiniLM `57395025602894f1…`, de CamemBERT `88830edbe7e3741f…` et de bge-m3 `f40cae84eb6d5857…`, résultats de la grille `2c8619caf32d043c…`.
* **Contrôle indépendant** : le rappel du contexte de deux configurations (E5 à 5 passages, fusion à 10 passages) a été recalculé hors du script, à partir des classements seuls, avec le même résultat.

## 10. Suite

* **Protocole 07** : confirmation unique sur le lot de test, avec la règle D4 et un test apparié groupé par fiche.
* **#139** : jugement manuel des passages pour évaluer les voisins et corriger le biais de l'extrait unique.
* **Après la mesure du protocole 06** : la chaîne complète avec la récupération v2, modèle de base et modèle adapté, à titre exploratoire.

## 11. Historique

* **9 novembre 2026** : préparation, grille sans reclasseur, amendement A1, scores des trois reclasseurs, grille complète.
