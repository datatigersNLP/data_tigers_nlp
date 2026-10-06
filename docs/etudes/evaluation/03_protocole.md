# Protocole d'évaluation de la recherche du volet A (notebook 03)

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** Issue #46 · Branche `feat/46-notebook-03`  
**Responsable principal** Mahé BEGNIS  
**Soutien** Remy RAYANE  
**Statut** proposé le 6 octobre 2026, à valider au Weekly 4 du 7 octobre, puis figé avant toute mesure  

---

## 1. Objet et règle d'emploi

Ce protocole fixe, avant toute mesure sur le lot de test, la règle de pertinence, les systèmes comparés, les métriques, l'analyse principale, les analyses secondaires et leurs règles de décision.

* **Figé avant la mesure.** Une fois validé, il est figé par un commit, et son empreinte SHA-256 est inscrite dans le notebook 03. Le notebook refuse de lire le lot de test si l'empreinte ne correspond pas.
* **Rien d'autre n'est conclusif.** Toute analyse absente de ce document est présentée comme exploratoire.
* **Déclaration.** Le 6 octobre 2026, un aperçu de l'encodeur sur le jeu de questions a été calculé pendant un audit, hors protocole (journal d'usage de l'IA, section 4). Aucune décision ci-dessous ne s'appuie sur lui : chacune est justifiée par le rapport J2, par la validation sur PIAF (#45), par les annotations seules ou par un calcul de puissance.

---

## 2. Données

### 2.1 Jeu de questions (#44)

* **Fichier.** `evaluation/questions/questions_annotees.csv`, dans la version figée par le tag du jeu. Le tag et l'empreinte du fichier sont inscrits ici au moment du gel.
* **Recherche.** Elle se mesure sur les questions du lot de test classées `dans_corpus` : 72 au 4 octobre, nombre à reconfirmer après le gel.
* **Abstention.** Elle se mesure sur toutes les questions du lot de test, celles du corpus comme celles hors corpus.
* **Lot de calibration.** Il ne sert qu'à mettre au point le notebook et, à défaut du CDTN, à fixer le seuil d'abstention (section 8.2).
* **Annotation secondaire.** L'accord entre annotateurs est calculé et publié ; l'annotation principale fait foi.

### 2.2 Corpus et index

* **Passages.** Les découpages M0, M1, M2, M2 à 256 tokens et M3 du notebook 01, contrôlés par les empreintes de `data/decoupage/passages/manifeste.json`.
* **Index.** Ceux d'évaluation du notebook 02, dans `data/indexation/variantes/`, contrôlés par les empreintes de `variantes.json`. L'index M2 est celui du site : même empreinte SHA-256, qui commence par `2ec45586`.

### 2.3 Complément CDTN (#56)

Analyse secondaire, rapportée à part (section 8.3).

---

## 3. Règle de pertinence (D4)

* **Normalisation.** Appliquée à l'extrait comme au passage : minuscules, apostrophe typographique remplacée par l'apostrophe droite, puis seuls les lettres, y compris accentuées, et les chiffres sont conservés ; les tirets de liste disparaissent ainsi. La comparaison est faite deux fois, avec et sans retrait des marques de liste numérotées (un nombre suivi d'un point et d'une espace), car la copie depuis le site les perd parfois, mais les retirer partout effacerait aussi une année en fin de phrase. Un passage est pertinent si l'une des deux comparaisons le déclare tel.
* **Passage pertinent.** Un passage est pertinent pour une question si son texte normalisé contient un fragment contigu de l'extrait normalisé long d'au moins la moitié de l'extrait, arrondie à l'entier supérieur.
* **Fiche pertinente (D8).** Une fiche est pertinente si elle contient au moins un passage pertinent.
* **Longueur minimale.** Un extrait normalisé, sans retrait des marques, compte au moins 80 caractères ; au 6 octobre, le plus court en compte 83.
* **Contrôle avant la mesure.** Chaque question du corpus doit avoir au moins un passage pertinent dans chaque découpage. Sinon, elle est signalée, comptée comme un échec pour ce découpage, et leur nombre est publié.

Pourquoi un fragment et non l'extrait entier : au 6 octobre, d'après les seules annotations, les 77 extraits tiennent entiers dans un passage M2, mais seulement 74 en M2 à 256 tokens, 70 en M1, et 69 en M0 comme en M3. Exiger l'extrait entier avantagerait M2 par construction.

Application au 6 octobre, sur les 77 questions du corpus et d'après les seules annotations : en M2, en M2 à 256 tokens et en M3, chaque question a au moins un passage pertinent, et 64 en ont un seul ; en M1 aussi, avec 53 questions à un seul passage ; en M0, une question n'en a aucun. La règle est implémentée dans `scripts/evaluation/pertinence.py`, dont la présélection est contrôlée contre une recherche exhaustive.

---

## 4. Systèmes comparés

| Code | Système | Configuration |
|---|---|---|
| E5 servi | l'encodeur tel que le site le sert | questions encodées dans le navigateur en q8 (`Xenova/multilingual-e5-small`, révision `761b726d`, transformers.js 4.3.0) ; index M2 avec en-tête, en fp32, celui du site |
| E5 fp32 | l'encodeur de référence | questions encodées en Python en fp32 (`intfloat/multilingual-e5-small`, révision `614241f6`), sur chacun des six index : M0, M1, M2, M2 à 256 tokens, M2 sans en-tête, M3 |
| BM25 de référence | la référence lexicale (D3) | V3 de #47 : formule de Lucene, k1 = 1,2, b = 0,75, mots vides Snowball sans négations, racinisation Snowball, sur l'en-tête et le texte des passages M2 |
| Autres références | BM25 V0, V1, V2, V4 et TF-IDF V0 à V4 de #47 | mêmes passages ; résultats descriptifs |
| Aléatoire | tirage uniforme | espérance exacte, sans tirage |

Règles communes :

* préfixe `query: ` devant chaque question pour l'encodeur ;
* classement par `rank_by_score`, les ex aequo dans l'ordre de l'index ;
* une question sans aucun passage de score positif, pour une référence lexicale, compte comme un échec (D5).

---

## 5. Métriques

* **Au niveau du passage :** Recall@k pour k = 1, 3, 5 et 10, et MRR@10. Une question est réussie à k si au moins un passage pertinent figure parmi les k premiers.
* **Au niveau de la fiche (D8) :** Recall@5, une question étant réussie si l'un des 5 premiers passages appartient à une fiche pertinente.
* **Intervalles à 95 % :** robustes au regroupement des questions par fiche annotée (`proportion_ci` et `compute_mcnemar_test` de `scripts/evaluation/metrics.py`, avec la fiche en `groups`).

---

## 6. Analyse principale (D1, D2, D3)

* **Question.** E5 servi est-il non inférieur à BM25 de référence, en Recall@5 au niveau du passage, sur les questions du corpus du lot de test ? C'est le critère du rapport J2.
* **Statistique.** L'écart d = Recall@5 (E5 servi) moins Recall@5 (BM25 de référence), avec son intervalle de confiance à 95 %, robuste aux groupes.
* **Critère satisfait (D2)** si la borne basse de l'intervalle dépasse -15 points : c'est un test de non-infériorité, au risque unilatéral de 2,5 %.
* **E5 servi déclaré meilleur** si, en outre, la borne basse dépasse 0.
* **Critère non démontré** dans les autres cas, ce qui ne prouve pas pour autant une infériorité.
* **Pourquoi 15 points.** Avec 72 questions et un écart réel nul, le test de non-infériorité a une puissance de 72 à 93 % pour une marge de 15 points, selon que le taux de désaccord entre systèmes vaut 0,25 ou 0,14 (0,14 est celui de PIAF entre E5 et BM25 V3). Pour une marge de 10 points, elle n'est que de 40 à 62 %. Le rapport J2 dimensionnait déjà le jeu pour 15 points.
* **Également rapportés :** la table de contingence, la valeur p exacte de McNemar et celle d'Obuchowski avec les questions groupées par fiche.

---

## 7. Analyses secondaires (D7)

Chaque famille est corrigée par la méthode de Holm, au seuil de 5 %. Sauf mention contraire, la métrique est Recall@5 au niveau du passage, avec l'encodeur en fp32.

| Famille | Comparaisons | Règle de décision |
|---|---|---|
| F1, découpages | M0, M1 et M3, chacun contre M2 : 3 tests bilatéraux | M2 reste le découpage servi, sauf si un autre fait significativement mieux (règle du notebook 01) |
| F2, réglages de M2 | M2 à 256 tokens contre M2 ; M2 sans en-tête contre M2 : 2 tests | le réglage actuel reste, sauf écart significatif en faveur de l'autre |
| F3, précision servie | E5 servi (q8) contre E5 fp32 sur M2 : 1 test | la quantification est acceptée si l'écart n'est pas significatif ; l'intervalle est publié |
| F4, références | TF-IDF, variantes de BM25, aléatoire | descriptif : valeurs et intervalles, sans test |

Les autres métriques (Recall@1, Recall@3, Recall@10, MRR@10, niveau fiche) sont descriptives. Chaque découpage est jugé avec sa propre application de la règle D4.

---

## 8. Sigles, abstention et CDTN

### 8.1 Sigles

* **Sous-ensemble.** Les questions du corpus du lot de test qui contiennent un sigle de la liste ci-dessous : 7 au 4 octobre, donc une analyse descriptive seulement.
* **Extension des sigles, fixée ici.** CDI : contrat à durée indéterminée ; CDD : contrat à durée déterminée ; RTT : réduction du temps de travail ; CSE : comité social et économique ; SMIC : salaire minimum interprofessionnel de croissance ; VAE : validation des acquis de l'expérience ; CPF : compte personnel de formation.
* **Mesure.** Le rang du premier passage pertinent avant et après extension, question par question, sans test.

### 8.2 Abstention (D6)

* **Score d'une question.** Le plus grand cosinus avec les passages M2, pour E5 servi.
* **Sans seuil.** L'AUC entre les questions du corpus et les questions hors corpus du lot de test, avec un intervalle à 95 % par rééchantillonnage stratifié (10 000 tirages, graine fixée).
* **Avec seuil, à titre exploratoire.** Le seuil vaut le 5e centile des scores maximaux des variantes du CDTN rédigées en question (#56). À défaut, il vaut le plus petit score maximal des questions du corpus du lot de calibration. Sur le test, on rapporte la part des questions hors corpus rejetées et celle des questions du corpus conservées, avec leurs intervalles de Wilson.

### 8.3 CDTN

Analyse secondaire séparée (#56) : pertinence jugée à la section, variantes groupées par requête, résultats jamais fusionnés avec ceux du jeu de l'équipe.

---

## 9. Mise en œuvre et reproductibilité

* **Notebook.** `scripts/evaluation/03_evaluation.ipynb`, exécuté en entier par `nbclient` sur un noyau privé, dans l'environnement figé du dossier (`requirements-lock.txt`).
* **Verrou.** Le lot de test n'est lu qu'en mode mesure, et seulement si les empreintes de ce protocole et du jeu sont celles inscrites.
* **Une seule exécution de mesure.** Les rangs bruts, par question et par système, sont sauvegardés dans `data/evaluation/notebook03/`.
* **Contrôles.** Rangs recalculés sans tri ; deux exécutions identiques ; fidélité des vecteurs q8 du navigateur contrôlée comme au notebook 02.
* **Interdits.** Modifier le lot de test après la mesure ; régler un paramètre sur le lot de test ; ajouter une analyse sans l'étiqueter « exploratoire ».

---

## 10. Décisions à valider au Weekly 4

| N° | Décision | Proposition | Justification |
|---|---|---|---|
| D1 | Comparaison principale | Recall@5 au niveau du passage, E5 servi contre BM25 de référence | le site affiche 5 résultats ; c'est la configuration que voit l'utilisateur |
| D2 | Marge de non-infériorité | 15 points | puissance de 72 à 93 %, contre 40 à 62 % pour 10 points ; dimensionnement du J2 |
| D3 | Référence BM25 | V3, formule de Lucene | meilleure variante sur PIAF, qui est indépendant de notre jeu |
| D4 | Règle de pertinence | fragment contigu d'au moins la moitié de l'extrait normalisé | équitable entre découpages |
| D5 | Question sans résultat lexical | échec | aucun passage n'est montré à l'utilisateur |
| D6 | Abstention | AUC sans seuil, et seuil tiré du CDTN ou de la calibration | lot de calibration trop petit pour un seuil fiable |
| D7 | Comparaisons multiples | Holm par famille, sinon exploratoire | une seule analyse principale |
| D8 | Niveau fiche | Recall@5 au niveau de la fiche, en métrique secondaire | le site affiche la fiche du passage |

---

## 11. Historique

* **6 octobre 2026 :** version proposée (Mahé BEGNIS).
