# Évaluation de la recherche du volet A (notebook 03)

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** Issue #46 · PR #73  
**Auteur** Mahé BEGNIS  
**Date** 13 octobre 2026, jour de la mesure unique  
**Statut** résultats de la mesure officielle, conduite selon le protocole figé `03_protocole.md` (empreinte `ab65d0b5…`)  

---

## 1. En bref

* **Le critère du J2 est satisfait.** Sur les 73 questions du corpus du lot de test, l'encodeur servi place un passage pertinent dans ses 5 premiers résultats pour 43,8 % des questions, contre 42,5 % pour BM25 de référence : un écart de +1,4 point, avec un intervalle à 95 % de -11,5 à +14,3 points. La borne basse dépasse la marge de -15 points.
* **Aucun des deux n'est démontré meilleur.** E5 réussit seul 10 questions, BM25 seul 9 : la différence n'est pas significative (McNemar, p = 1,000).
* **Les réglages du site tiennent.** Aucun autre découpage ni réglage de M2 ne fait significativement mieux, et la quantification q8 ne coûte qu'une question sur 73, sans écart significatif.
* **La bonne fiche plus souvent que le bon passage.** Une fiche pertinente figure dans les 5 premiers résultats de l'encodeur servi pour 83,6 % des questions.
* **L'abstention reste à régler.** Le score de similarité sépare assez bien les questions hors corpus (AUC de 0,841), mais le seuil fixé sur le CDTN n'en rejette que 9 sur 24.

---

## 2. Ce qui a été mesuré

* **Jeu.** Le lot de test du jeu figé `jeu-questions-v1` (#44) : 73 questions du corpus, issues de 61 fiches, et 24 questions hors corpus. Le lot de calibration n'a servi qu'à mettre au point le notebook.
* **Pertinence (D4).** Un passage est pertinent s'il partage avec l'extrait annoté un fragment contigu qui couvre au moins la moitié de l'extrait, ou au moins la moitié du passage avec un minimum de 80 caractères. Une fiche est pertinente si elle contient un passage pertinent.
* **Systèmes.** L'encodeur tel que le site le sert (questions encodées en q8 dans le navigateur, index M2 du site), l'encodeur en fp32 sur six index, BM25 de référence (variante V3 de #47), les autres références lexicales et l'aléatoire.
* **Métrique principale.** Recall@5 au niveau du passage : la part des questions dont au moins un passage pertinent figure parmi les 5 premiers résultats.
* **Exécution.** Une exécution du notebook en mode mesure, dans l'environnement figé, après contrôle des empreintes du protocole, du jeu et du seuil d'abstention.
* **Contrôles.** Une seconde exécution a donné des rangs et des résultats identiques octet par octet. L'analyse principale, recalculée à partir des rangs bruts par un code indépendant du module de métriques, concorde à 1e-14 près.

---

## 3. Analyse principale : le critère du J2

| Écart de Recall@5 (E5 servi moins BM25 V3) | IC 95 % | Intervalle | Paires discordantes | p McNemar | p groupé (Obuchowski) | Marge | Verdict |
|---|---|---|---|---|---|---|---|
| +1,4 | [-11,5 ; +14,3] | score de Tango corrigé de l'effet de plan | 19 | 1,000 | 0,829 | 15 points | satisfait |

Table de contingence : les deux réussissent 22, E5 seul 10, BM25 seul 9, aucun 32 ; 61 fiches.

Score de Tango à la marge : z = 2,45, p unilatéral 0,007, effet de plan 1,11. À titre descriptif, intervalle de la règle du 10 octobre (Wald robuste) : [-11,0 ; +13,8].

* **Ce que dit le verdict.** Avec un risque d'erreur de 2,5 %, l'encodeur servi n'est pas moins bon que BM25 de 15 points ou plus. Le verdict ne dit pas qu'il est meilleur : l'intervalle contient 0.
* **Pourquoi l'intervalle est large.** Seules les 19 questions discordantes distinguent les deux systèmes. Sur 73 questions, l'écart reste connu à environ 13 points près, ce que le dimensionnement du J2 prévoyait pour une marge de 15 points.
* **L'amendement n'a pas changé le verdict.** La règle du 10 octobre, publiée à titre descriptif, aurait aussi conclu au critère satisfait.

---

## 4. Métriques par système

| Système | R@1 | R@3 | R@5 | R@5, IC 95 % | R@10 | MRR@10 | R@5 fiche |
|---|---|---|---|---|---|---|---|
| E5 fp32, m2 | 20,5 % | 39,7 % | 45,2 % | 33,9 % à 57,0 % | 58,9 % | 0,326 | 80,8 % |
| E5 fp32, m2_sans_entete | 15,1 % | 35,6 % | 43,8 % | 33,0 % à 55,3 % | 52,1 % | 0,279 | 72,6 % |
| E5 fp32, m2_256 | 19,2 % | 38,4 % | 43,8 % | 32,5 % à 55,9 % | 52,1 % | 0,305 | 75,3 % |
| E5 fp32, m0 | 17,8 % | 34,2 % | 38,4 % | 27,8 % à 50,2 % | 53,4 % | 0,282 | 80,8 % |
| E5 fp32, m1 | 21,9 % | 42,5 % | 49,3 % | 37,1 % à 61,6 % | 63,0 % | 0,342 | 83,6 % |
| E5 fp32, m3 | 26,0 % | 41,1 % | 47,9 % | 36,6 % à 59,5 % | 63,0 % | 0,360 | 80,8 % |
| E5 servi | 20,5 % | 39,7 % | 43,8 % | 32,9 % à 55,4 % | 57,5 % | 0,320 | 83,6 % |
| BM25 V0 | 8,2 % | 21,9 % | 32,9 % | 23,1 % à 44,4 % | 43,8 % | 0,183 | 60,3 % |
| TF-IDF V0 | 9,6 % | 16,4 % | 24,7 % | 15,9 % à 36,2 % | 39,7 % | 0,163 | 63,0 % |
| BM25 V1 | 11,0 % | 31,5 % | 39,7 % | 29,5 % à 51,0 % | 50,7 % | 0,235 | 75,3 % |
| TF-IDF V1 | 12,3 % | 19,2 % | 30,1 % | 20,3 % à 42,2 % | 43,8 % | 0,196 | 68,5 % |
| BM25 V2 | 12,3 % | 30,1 % | 38,4 % | 28,3 % à 49,6 % | 50,7 % | 0,238 | 72,6 % |
| TF-IDF V2 | 11,0 % | 19,2 % | 28,8 % | 19,2 % à 40,7 % | 43,8 % | 0,191 | 68,5 % |
| BM25 de référence (V3) | 15,1 % | 32,9 % | 42,5 % | 30,9 % à 54,9 % | 56,2 % | 0,263 | 79,5 % |
| TF-IDF V3 | 12,3 % | 23,3 % | 35,6 % | 25,2 % à 47,6 % | 52,1 % | 0,218 | 71,2 % |
| BM25 V4 | 15,1 % | 32,9 % | 42,5 % | 30,9 % à 54,9 % | 56,2 % | 0,263 | 79,5 % |
| TF-IDF V4 | 12,3 % | 21,9 % | 35,6 % | 25,2 % à 47,6 % | 50,7 % | 0,215 | 72,6 % |
| Aléatoire (espérance, M2) | 0,0 % | 0,1 % | 0,2 % |  | 0,3 % | 0,001 |  |

* **Précision servie.** En fp32, l'encodeur obtient 45,2 % sur M2, contre 43,8 % pour sa version servie en q8.
* **Références lexicales.** BM25 progresse de 32,9 % (V0) à 42,5 % (V3) en Recall@5 ; V3 et V4 obtiennent les mêmes métriques sur ce lot, avec des rangs parfois différents. En Recall@5, TF-IDF reste sous BM25 à variante égale.
* **Niveau de la fiche.** Une fiche pertinente est trouvée bien plus souvent qu'un passage pertinent : 83,6 % pour l'encodeur servi, 79,5 % pour BM25 de référence. Le Recall au niveau du passage est un minorant prudent, puisqu'un autre passage valable de la même fiche compte comme un échec.
* **Aléatoire.** 0,2 % en Recall@5 : tous les systèmes en sont très loin.

---

## 5. Analyses secondaires

Chaque famille de comparaisons est corrigée par la méthode de Holm, au seuil de 5 %, en Recall@5 au niveau du passage. L'encodeur est en fp32, sauf pour la famille F3, qui compare justement sa version servie à sa version fp32.

| Famille | Comparaison | Écart | IC 95 % | Intervalle | Discordantes | p groupé | p Holm | Significatif |
|---|---|---|---|---|---|---|---|---|
| F1 découpages | E5 fp32, m0 contre E5 fp32, m2 | -6,8 | [-13,9 ; +0,6] | Agresti et Min | 7 | 0,061 | 0,183 | non |
| F1 découpages | E5 fp32, m1 contre E5 fp32, m2 | +4,1 | [-6,4 ; +14,6] | Wald robuste | 15 | 0,442 | 0,885 | non |
| F1 découpages | E5 fp32, m3 contre E5 fp32, m2 | +2,7 | [-8,1 ; +13,5] | Wald robuste | 16 | 0,620 | 0,885 | non |
| F2 réglages de M2 | E5 fp32, m2_256 contre E5 fp32, m2 | -1,4 | [-9,6 ; +6,9] | Agresti et Min | 9 | 0,741 | 1,000 | non |
| F2 réglages de M2 | E5 fp32, m2_sans_entete contre E5 fp32, m2 | -1,4 | [-9,6 ; +6,9] | Agresti et Min | 9 | 0,765 | 1,000 | non |
| F3 précision servie | E5 servi contre E5 fp32, m2 | -1,4 | [-6,6 ; +3,9] | Agresti et Min | 3 | 0,567 | 0,567 | non |

* **Aucun écart significatif après correction de Holm.** M2 reste le découpage servi, les 512 tokens et l'en-tête restent, et la quantification q8 est acceptée.
* **M0, le plus faible.** Le découpage de l'éditeur perd 6,8 points face à M2, sans écart significatif (p de Holm de 0,183). C'est le sens attendu, puisque M0 perd le chapeau des fiches, mais ce n'est pas démontré.
* **M1 et M3.** Ils obtiennent les meilleurs Recall@5 (49,3 % et 47,9 %), mais leurs écarts avec M2 ne sont pas significatifs.

---

## 6. Abstention

| AUC | IC 95 % | Seuil | Origine | Hors corpus rejetées | Dans le corpus conservées |
|---|---|---|---|---|---|
| 0,841 | [0,747 ; 0,921] | 0,8560 | CDTN (#56) | 9/24 (37,5 %), IC [21,2 % ; 57,3 %] | 72/73 (98,6 %), IC [92,6 % ; 99,8 %] |

* **Sans seuil.** Le plus grand cosinus d'une question avec les passages sépare les questions du corpus des questions hors corpus avec une AUC de 0,841.
* **Avec le seuil du CDTN.** Fixé avant la mesure, il conserve 72 des 73 questions du corpus, mais ne rejette que 9 des 24 questions hors corpus. Un message d'abstention fondé sur ce seuil laisserait passer la majorité des questions hors corpus.
* **Conséquence.** Le seuil reste exploratoire, comme le prévoit le protocole. Un autre seuil ne pourra être choisi que sur d'autres données que le lot de test, ce qui relève du volet B (#52).

---

## 7. Sigles

| question | E5 fp32 avant | E5 fp32 après | E5 servi avant | E5 servi après | BM25 avant | BM25 après |
|---|---|---|---|---|---|---|
| Q014 | 9 | 8 | au-delà de 10 | au-delà de 10 | 3 | 1 |
| Q016 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 |
| Q040 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 |
| Q046 | 1 | 1 | 2 | 1 | 5 | 10 |
| Q088 | 8 | 9 | 8 | 10 | 3 | 3 |
| Q091 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 |
| Q092 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 | au-delà de 10 |

Sur ces 7 questions, l'extension des sigles change peu l'encodeur ; elle aide BM25 pour Q014 et le pénalise pour Q046. Quatre questions restent hors des 10 premiers résultats pour tous les systèmes, avec ou sans extension. Avec si peu de questions, ce tableau ne prouve rien.

---

## 8. Fidélité de l'encodeur servi

Fidélité des vecteurs du navigateur au fp32 : cosinus minimal 0,9928, médian 0,9969 (transformers.js 4.3.0). Ces valeurs portent sur les 113 textes encodés pour la mesure ; elles concordent avec le contrôle du notebook 02.

---

## 9. Limites

* **Effectif.** 73 questions sur 61 fiches : les intervalles des écarts entre systèmes couvrent de 10 à 26 points.
* **Vérité de terrain.** Elle repose sur un extrait par question. Pour 6 des 15 questions doublement annotées, l'annotateur secondaire désignait un autre passage, ou une autre fiche pour Q051 : le Recall au niveau du passage sous-estime tous les systèmes.
* **Exposition du lot de test.** La PR #63 a publié, avant la mesure, des chiffres exploratoires sur ce lot (Weekly 4, décision 2). Les règles fixées ensuite n'utilisent aucune donnée du lot de test : le seuil d'abstention vient du CDTN, et l'amendement du 13 octobre vient d'une simulation et rend la conclusion plus difficile.
* **Trace de l'exécution.** La dernière sortie du notebook liste aussi `vecteurs_navigateur_essai_avant_mesure.json`, une copie de sauvegarde faite avant la mesure, dont le nom correspond au motif des sorties : ce n'est pas une sortie de la mesure.

---

## 10. Conséquences pour le volet A

* **Le site garde son moteur.** L'encodeur servi en q8, avec l'index M2, tient le critère du J2.
* **L'abstention ne doit pas être présentée comme fiable** avec le seuil actuel.
* **Suite.** La mesure de l'encodeur ajusté le 15 octobre (protocole 05, PR #75), puis l'analyse du CDTN le 16 octobre (#56).
