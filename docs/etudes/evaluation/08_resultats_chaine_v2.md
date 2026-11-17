# Chaîne v2 du volet B : résultats sur le lot de test (#163)

**Date** : 15 novembre 2026. **Ticket** : #163. **Règles** : protocole 08 (`08_protocole_chaine_v2.md`, figé au commit `569bf0e`, SHA-256 `9168a3c9…`). **Auteur** : Mahé BEGNIS.

---

## 1. Objet et décision

Le protocole 08 mesure, une seule fois et à titre exploratoire, deux états de la chaîne du volet B, avec le témoin T et le modèle adapté :

* **V1** : la récupération v2 (`rrf+k10+bge-m3@20`, 10 passages) avec la consigne v1 et l'abstention sur le score E5 (seuil S) ;
* **V2** : la même récupération, avec la consigne v2 et l'abstention sur le score du reclasseur bge-m3 (seuil τ).

La règle d'adoption, écrite d'avance (protocole 08, section 6), adopte V2 avec le modèle adapté si son M4 dépasse strictement celui de B2 (18 sur 72) et si son M1 n'est pas inférieur de plus d'une question à celui de B2 (20 sur 24).

**Décision : la règle n'est pas satisfaite, B2 reste la chaîne de référence.** M4 vaut 27 sur 73 (condition remplie), mais M1 vaut 18 sur 24, soit deux questions de moins que B2, alors que la règle en tolère une.

---

## 2. Exécution

* **Code** : commit de gel `569bf0e`, publié sur le #163 avant la mesure, avec les empreintes du protocole, de `chaine_v2.py`, de `recuperation.py` et du fichier de τ. Ces quatre empreintes sont inchangées à la fin de la mesure et au moment de l'analyse.
* **Lancement** : `chaine_v2.py preparer --lot test`, puis `executer` pour les quatre états dans l'ordre du protocole (T en V1 puis V2, puis le modèle adapté en V1 puis V2), par un lanceur local qui régule le client (30 s de marche, 30 s de pause), le 15 novembre 2026 de 15 h 09 à 17 h 16 UTC. Chaque état a pris de 27 à 31 minutes.
* **Contrôle préalable** : les contextes préparés retrouvent, pour les 73 questions du corpus, la présence ou non d'un passage pertinent et le nombre de tokens publiés par la confirmation du 9 novembre (protocole 07). Aucun écart. Contextes : SHA-256 `dbdf49b3…`.
* **Modèles et serveur** : Ollama 0.40.13 sur 127.0.0.1 ; T `8a077f3d…` et modèle adapté `18cb25f0…`, les digests publiés sur le #52.
* **Erreurs techniques** : aucune, sauf une pour T en V2 (1 sur 97, 1,0 %) : la question Q093, dont la réponse a été coupée à 512 tokens. L'état reste valide, sous le plafond de 5 % (protocole 08, section 5) ; cette question est retirée de ses populations et des comparaisons qui portent sur cet état.
* **Analyse** : `python scripts/recuperation/chaine_v2.py analyser --lot test`, fichier `analyse_20261115T171700Z.json`.

---

## 3. Résultats par état

Proportions sur les questions sans erreur technique, avec l'intervalle de Wilson à 95 %, corrigé de l'effet de plan par fiche pour les questions du corpus.

* **M1** : abstention sur une question hors corpus (24 questions) ; plus haut est meilleur.
* **M2** : abstention sur une question du corpus, donc à tort ; plus bas est meilleur.
* **M3** : réponse citée valide, sur les questions du corpus.
* **M4** : réponse citée dont une citation renvoie à un passage pertinent selon la règle D4 ; c'est la mesure de réussite.
* **M5** : réponse donnée à une question hors corpus ; plus bas est meilleur.

**Modèle adapté**

| | B2 (11 novembre) | V1 | V2 |
|---|---|---|---|
| M1 | 20/24 (83,3 %) [64,1 ; 93,3] | 20/24 (83,3 %) [64,1 ; 93,3] | 18/24 (75,0 %) [55,1 ; 88,0] |
| M2 | 40/72 (55,6 %) [43,8 ; 66,7] | 30/73 (41,1 %) [30,4 ; 52,7] | 21/73 (28,8 %) [19,5 ; 40,2] |
| M3 | 32/72 (44,4 %) [33,3 ; 56,2] | 43/73 (58,9 %) [47,3 ; 69,6] | 52/73 (71,2 %) [59,8 ; 80,5] |
| M4 | 18/72 (25,0 %) [16,0 ; 36,9] | 24/73 (32,9 %) [23,1 ; 44,4] | 27/73 (37,0 %) [26,4 ; 48,9] |
| M5 | 4/24 (16,7 %) [6,7 ; 35,9] | 4/24 (16,7 %) [6,7 ; 35,9] | 6/24 (25,0 %) [12,0 ; 44,9] |

**Témoin T**

| | B2 (11 novembre) | V1 | V2 |
|---|---|---|---|
| M1 | 20/24 (83,3 %) [64,1 ; 93,3] | 20/24 (83,3 %) [64,1 ; 93,3] | 14/24 (58,3 %) [38,8 ; 75,5] |
| M2 | 51/72 (70,8 %) [60,4 ; 79,4] | 47/73 (64,4 %) [53,7 ; 73,8] | 7/72 (9,7 %) [4,9 ; 18,3] |
| M3 | 18/72 (25,0 %) [16,8 ; 35,5] | 21/73 (28,8 %) [20,0 ; 39,4] | 39/72 (54,2 %) [42,0 ; 65,9] |
| M4 | 10/72 (13,9 %) [7,7 ; 23,7] | 13/73 (17,8 %) [11,0 ; 27,4] | 25/72 (34,7 %) [24,9 ; 46,1] |
| M5 | 4/24 (16,7 %) [6,7 ; 35,9] | 4/24 (16,7 %) [6,7 ; 35,9] | 10/24 (41,7 %) [24,5 ; 61,2] |

Les effectifs de 72 viennent d'une erreur technique : Q088 en B2 pour les deux modèles (mesure du 11 novembre), et Q093 pour T en V2. Une comparaison appariée exclut les questions en erreur dans l'un ou l'autre état : T en V2 contre T en B2 porte donc sur 71 questions (Q088 et Q093 exclues) ; elle ne figure pas dans la section 4, dont toutes les comparaisons portent sur 72 ou 73 questions. Correction du 17 novembre, après la revue de Jibril sur la #166.

---

## 4. Comparaisons appariées

Écart A moins B, en points, sur les questions sans erreur technique dans les deux états, avec l'intervalle du score de Tango à 95 % (corrigé de l'effet de plan par fiche pour M2 à M4, sans regroupement pour M1) et la valeur p exacte de McNemar. « Gagnées » : questions réussies par A seul ; « perdues » : par B seul.

| Comparaison | Mesure | Écart | Intervalle à 95 % | Gagnées / perdues | McNemar |
|---|---|---:|---|---:|---:|
| Adapté, V2 moins B2 | M4 | +11,1 | [+0,2 ; +22,6] | 12 / 4 | p = 0,077 |
| Adapté, V2 moins B2 | M1 | -8,3 | [-28,0 ; +10,6] | 1 / 3 | p = 0,625 |
| Adapté, V2 moins B2 | M2 | -26,4 | [-38,3 ; -15,7] | 1 / 20 | p < 0,001 |
| Adapté, V1 moins B2 | M4 | +6,9 | [-3,9 ; +18,2] | 10 / 5 | p = 0,302 |
| Adapté, V1 moins B2 | M1 | 0,0 | [-17,0 ; +17,0] | 1 / 1 | p = 1,000 |
| Adapté, V1 moins B2 | M2 | -13,9 | [-25,2 ; -3,9] | 2 / 12 | p = 0,013 |
| Adapté, V2 moins V1 | M4 | +4,1 | [-5,5 ; +14,2] | 7 / 4 | p = 0,549 |
| Adapté, V2 moins V1 | M1 | -8,3 | [-28,0 ; +10,6] | 1 / 3 | p = 0,625 |
| V1, adapté moins T | M4 | +15,1 | [+5,2 ; +26,1] | 13 / 2 | p = 0,007 |
| V2, adapté moins T | M4 | +2,8 | [-10,0 ; +15,6] | 10 / 8 | p = 0,815 |
| V2, adapté moins T | M1 | +16,7 | [+0,6 ; +35,9] | 4 / 0 | p = 0,125 |

Pour M2, un écart négatif est une amélioration : moins d'abstentions à tort.

**Lecture.** Aucune de ces comparaisons ne démontre une amélioration : le protocole 08 est descriptif, le lot de test avait déjà été lu par le notebook 03 et les protocoles 05, 06 et 07 (le protocole 08, figé avant la mesure A1 du 15 novembre, n'en cite que trois), et une quarantaine d'écarts sont calculés. Pour M4 en V2 contre B2, l'intervalle de Tango exclut tout juste 0 alors que le test exact de McNemar ne rejette pas l'égalité (p = 0,077) : avec 16 paires discordantes, le résultat dépend de la méthode, et ne permet pas de conclure. La seule baisse nette d'abstentions à tort (M2) est attendue : la consigne v2 autorise les réponses partielles.

---

## 5. Décomposition de M4

Questions du corpus sans erreur technique, selon qu'un passage pertinent (règle D4) figure ou non dans le contexte, croisées avec la sortie du modèle adapté.

| | B2 | V1 | V2 |
|---|---:|---:|---:|
| Passage pertinent fourni | 33 sur 72 | 53 sur 73 | 53 sur 73 |
| dont M4 (citation pertinente) | 18 | 24 | 27 |
| dont réponse citée, citation non pertinente | 3 | 9 | 13 |
| dont abstention du modèle | 11 | 18 | 9 |
| dont abstention sous le seuil | 1 | 2 | 4 |
| Aucun passage pertinent fourni | 39 sur 72 | 20 sur 73 | 20 sur 73 |
| dont réponse citée | 11 | 10 | 12 |
| dont abstention du modèle | 27 | 10 | 5 |
| dont abstention sous le seuil | 1 | 0 | 3 |

**Lecture.** La récupération v2 relève le plafond de M4 de 45,8 % (33 sur 72) à 72,6 % (53 sur 73), comme l'avait montré la confirmation du 9 novembre. Le modèle adapté exploite ce plafond à peu près dans la même proportion : il cite un passage pertinent pour 18 des 33 questions en B2 (54,5 %), 24 des 53 en V1 (45,3 %) et 27 des 53 en V2 (50,9 %). Le gain de M4 vient donc de la récupération, pas d'une meilleure exploitation des passages. La hausse des réponses citées sans citation pertinente (3, puis 9, puis 13) peut tenir à la règle D4, qui ne reconnaît qu'un extrait par question alors que 10 passages peuvent répondre ; seul un jugement humain trancherait.

---

## 6. Pourquoi M1 baisse en V2

Sorties du modèle adapté pour les 24 questions hors corpus :

| | B2 | V1 | V2 |
|---|---:|---:|---:|
| Abstention sous le seuil, sans appeler le modèle | 9 | 9 | 14 |
| Abstention du modèle | 11 | 11 | 4 |
| Réponse citée | 4 | 4 | 6 |

Le seuil τ, appliqué au score de bge-m3, rejette cinq questions hors corpus de plus que S. Mais la consigne v2, qui autorise une réponse partielle, fait chuter les abstentions du modèle de 11 à 4. Le solde est négatif :

* **Gagnée** : Q104, à laquelle B2 répondait, est rejetée par τ (score 0,037).
* **Perdues** : Q029 et Q063, sur lesquelles le modèle s'abstenait en B2, reçoivent une réponse citée en V2 ; Q070, rejetée par S en B2, dépasse τ (score 0,207) et reçoit une réponse citée.

τ coûte aussi sur le corpus : 7 questions du corpus tombent sous τ, contre 2 sous S.

---

## 7. Témoin T et consigne v2

Avec la consigne v2, T produit 31 sorties invalides sur 96 (32,3 %), contre 8 sur 97 en V1 : 29 sans aucune citation valide, 14 qui mêlent la phrase d'abstention à une réponse malgré la consigne, et 5 qui écrivent les références entre parenthèses (une sortie peut cumuler plusieurs défauts). Son M2 tombe à 7 sur 72 : T ne s'abstient presque plus. Le modèle adapté n'a aucune sortie invalide, en V1 comme en V2.

En V1, l'écart de M4 entre les deux modèles (+15,1 points) va avec un écart d'abstentions à tort : T s'abstient sur 47 questions du corpus sur 73, le modèle adapté sur 30. En V2, T ne s'abstient presque plus et cite davantage ; l'écart de M4 n'est plus que de +2,8 points [-10,0 ; +15,6].

---

## 8. Règle d'adoption

| Condition (protocole 08, section 6) | Valeur de V2 adapté | Exigence | Remplie |
|---|---|---|---|
| M4 strictement supérieur à B2 adapté | 27 sur 73 (37,0 %) | plus de 18 sur 72 (25,0 %) | oui |
| M1 inférieur d'au plus une question à B2 adapté | 18 sur 24 | au moins 19 sur 24 | non |

**B2 reste la chaîne de référence** de la démonstration et du rapport. V1 avec le modèle adapté atteint 24 sur 73 en M4 et 20 sur 24 en M1, mais la règle ne porte que sur V2 : le retenir maintenant serait un choix fait après lecture du lot de test, et il n'est pas proposé. Les résultats de V1 et V2 sont rapportés comme exploratoires.

---

## 9. Contrôles

* **Recalcul indépendant** : un script qui n'importe aucun module du dépôt recode chaque règle à partir de sa spécification écrite, puis compare ses résultats à l'analyse officielle. Résultat : 0 écart.
* **Classes et citations** recalculées à partir des réponses brutes et des mesures d'Ollama (sortie coupée, comptes de tokens).
* **Pertinence D4** recalculée par programmation dynamique sur le plus long fragment commun, sans présélection, pour 517 paires de question et passage.
* **M1 à M5, intervalles et 40 comparaisons** recalculés : effectifs, écarts, intervalles de Tango (estimateur contraint obtenu numériquement), effets de plan et valeurs p exactes.
* **Sensibilité du recalcul** : trois erreurs injectées dans une copie de l'analyse (un effectif, une borne d'intervalle, une case de la décomposition) sont toutes détectées.
* **Contextes** : pour les 97 questions, le score maximal de bge-m3 est bien le plus grand des 20 candidats, le contexte suit l'ordre du reclasseur, et les passages de chaque sortie sont exactement ceux du contexte de sa question.
* **Seuils** : chaque abstention sans appel au modèle a un score strictement inférieur au seuil de son état (S en V1, τ en V2), et chaque appel un score au moins égal.
* **Verrou de la #131 et gel** : la chaîne a contrôlé les empreintes verrouillées et celles du gel avant la préparation des contextes et avant chaque état ; la fusion de `dev` dans la branche ne modifie aucun fichier verrouillé.
* **Tests** : `test_chaine_v2.py` (14 tests) et `test_recuperation.py` (19 tests) réussis après la fusion de `dev` dans la branche.

---

## 10. Limites

* **Lot de test déjà exploité** et comparaisons multiples : les écarts sont exploratoires.
* **Règle D4** : un seul extrait par question, ce qui sous-estime M4, davantage avec 10 passages.
* **Consigne v2 non réglée**, et adaptateur entraîné avec la consigne v1 et 5 passages : V2 change ses conditions d'entraînement.
* **Exactitude non jugée** : les réponses de V2 sont plus longues (68 tokens médians contre 35 en V1) et leur fidélité n'a pas été évaluée par un humain.
* **Une seule exécution par état**, à température 0 et graine fixe ; le déterminisme n'a pas été recontrôlé ici.

---

## 11. Fichiers

Les sorties sont dans `data/evaluation/volet_b/chaine_v2/test/`, qui n'est pas versionné.

| Fichier | SHA-256 |
|---|---|
| `contextes.json` | `dbdf49b35fcc8271e22f7bede6abe01c0d011da36c4e6bade052364bca51c672` |
| `temoin/V1.jsonl` | `d54b44043cd3f7ab7afbc1bfa37330da06f42e11a749544018a9e48f82be6bf3` |
| `temoin/V2.jsonl` | `cab5f841a40f0c7cfce53b7ec731a8514073ba3c15b16d01f35f19484383ea6b` |
| `apres/V1.jsonl` | `72868e82ab1c20aa4939ae557287ac8eea3db724adad07b0fe70b25fc03580cc` |
| `apres/V2.jsonl` | `78f51dc2c4da34395c6ab82b71eb5f66d6079fd2102e0366e60722ffe37dcd39` |
| `analyse_20261115T171700Z.json` | `5968995179ba8e415e0e142562b5b0647a9edc885a78c919e5943b51b9721516` |
| B2 du 11 novembre, `data/evaluation/volet_b/mesure/apres/B2.jsonl` | `dae33de7c521950179724934a8e264e270cff4cdd93f39b8379e0715055e33a1` |
| B2 du 11 novembre, `data/evaluation/volet_b/mesure/temoin/B2.jsonl` | `032b60a8888a8993c2516a47d3ee2df8f68ebdcf4e4d4e2c47f402c04b59ff3a` |

---

## 12. Historique

* **15 novembre 2026** : mesure du lot de test au commit de gel `569bf0e`, analyse, recalcul indépendant et application de la règle d'adoption : B2 reste la chaîne de référence.
