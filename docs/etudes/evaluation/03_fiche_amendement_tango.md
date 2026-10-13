# Fiche : pourquoi et comment le test du critère du J2 a été amendé

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** Issue #46 · Branche `feat/46-notebook-03`  
**Auteur** Mahé BEGNIS  
**Date** 13 octobre 2026, avant toute mesure sur le lot de test  

---

## 1. En bref

* **Le critère du J2** demande de montrer que l'encodeur servi (E5) ne fait pas moins bien que BM25 de plus de 15 points de Recall@5, avec un risque d'erreur de 2,5 %.
* **La règle figée le 10 octobre** ne tenait pas ce risque : elle se trompait dans 3,0 à 5,2 % des cas, jusqu'à deux fois plus que promis.
* **Le score de Tango corrigé de l'effet de plan** le tient : 1,9 à 2,5 %, dans tous les scénarios simulés.
* **Le changement est prudent** : il rend la conclusion plus difficile à obtenir pour E5, jamais plus facile.
* **Il est décidé avant la mesure**, à partir d'une simulation qui n'utilise aucun résultat de système.

---

## 2. Ce que teste le critère du J2

* **Données appariées.** Les deux systèmes répondent aux mêmes 73 questions. Pour chacune, on note si chaque système retrouve un passage pertinent dans ses 5 premiers résultats.
* **Table appariée.** Elle compte quatre cas : les deux réussissent (a), E5 seul réussit (b), BM25 seul réussit (c), aucun ne réussit (d), avec a + b + c + d = n = 73.
* **Écart.** L'écart de Recall@5 vaut d = (b - c) / n. Seules les questions discordantes, b et c, distinguent les deux systèmes.
* **Hypothèses.** L'hypothèse à rejeter est « E5 est moins bon de 15 points ou plus », c'est-à-dire écart réel inférieur ou égal à -0,15. On conclut « critère satisfait » seulement si les données la rendent invraisemblable.
* **Risque d'erreur.** Le protocole promet que, si E5 était en réalité exactement 15 points moins bon, on ne conclurait à tort « critère satisfait » que dans 2,5 % des cas. C'est le risque de première espèce, noté alpha, unilatéral.
* **En pratique.** On calcule un intervalle de confiance à 95 % de l'écart, et le critère est satisfait si sa borne basse dépasse -15 points.

---

## 3. La règle du 10 octobre et son défaut

* **Le calcul.** L'intervalle de Wald vaut d plus ou moins 1,96 fois l'erreur type de d. Sans regroupement, la variance estimée de d vaut ((b + c) / n - d²) / n : elle dépend des fréquences observées des questions discordantes. Le protocole utilisait sa version robuste au regroupement par fiche, et l'intervalle d'Agresti et Min sous 10 paires discordantes.
* **Le défaut.** Prenons le cas limite, un écart réel de -15 points avec 20 % de désaccord : E5 seul réussit en moyenne 2,5 % des questions et BM25 seul 17,5 %, soit environ 2 et 13 questions sur 73. Dans un tirage où BM25 seul n'en gagne que 8, l'écart observé paraît meilleur que la réalité, et la variance estimée, calculée sur ces mêmes 8 questions, paraît plus petite. Les deux erreurs vont dans le même sens : la borne basse remonte au-dessus de -15 points plus souvent que prévu.
* **La mesure du défaut.** Une simulation de 10 000 tirages par scénario, sur la structure réelle du lot de test (73 questions réparties sur 61 fiches), donne un risque réel de 3,0 à 5,2 % (`03_audit_statistique.md`). L'intervalle d'Agresti et Min seul, ou un Wald avec quantile de Student, ne corrige pas le problème : 2,9 à 5,3 %.

---

## 4. Le score de Tango

* **Le principe.** Au lieu d'estimer la variance de l'écart avec les fréquences observées, on la calcule comme si l'hypothèse testée était vraie, c'est-à-dire avec un écart réel égal à la valeur testée d0. Un tirage chanceux ne fait donc plus fondre la variance.
* **L'estimateur contraint.** Sous la contrainte p10 - p01 = d0, où p10 est la probabilité que E5 seul réussisse et p01 que BM25 seul réussisse, l'estimateur du maximum de vraisemblance de p01 est la racine positive de l'équation 2n q² + (-(b + c) + (2n - b + c) d0) q - c d0 (1 - d0) = 0 (Tango, 1998).
* **La statistique.** Z(d0) = (d - d0) / racine(V(d0) / n), avec V(d0) = 2 p01 + d0 - d0², la variance de l'écart sous la contrainte, calculée avec l'estimateur contraint.
* **La décision.** Le critère est satisfait si Z(-0,15) dépasse 1,96, le quantile qui laisse 2,5 % au-dessus.
* **L'intervalle.** Il réunit toutes les valeurs d0 que le test ne rejette pas. Comme Z décroît avec d0, sa borne basse est le d0 tel que Z(d0) = 1,96 : la décision équivaut exactement à une borne basse supérieure à -15 points.
* **Un cas particulier.** À d0 = 0, l'estimateur contraint vaut (b + c) / 2n et la statistique devient (b - c) / racine(b + c) : c'est la statistique de McNemar, le test apparié classique.

---

## 5. La correction de l'effet de plan

* **Le problème.** Deux questions sur une même fiche se ressemblent : leurs succès sont corrélés, et elles apportent moins de deux informations indépendantes. Le score de Tango, seul, l'ignore. Sur le scénario corrélé, son risque monte à 3,1 à 3,3 %.
* **La correction.** L'effet de plan est le rapport entre la variance de l'écart estimée avec le regroupement par fiche et sa variance sans regroupement. Il est au moins égal à 1. On divise la statistique Z par la racine de l'effet de plan, ce qui revient à multiplier la variance par ce facteur.
* **La cohérence.** C'est la correction que le protocole applique déjà à l'intervalle d'une proportion, le Wilson à effectif corrigé de l'effet de plan.
* **Son ordre de grandeur.** Sur des tirages simulés corrélés, l'effet de plan vaut 1,15 en médiane, et jamais moins de 1.

---

## 6. Vérifications faites avant l'amendement

| Contrôle | Résultat |
|---|---|
| Comparaison à une implémentation tierce : paquet R PropCIs 0.3.0, fonction `scoreci.mp` (intervalle de Tango), sur neuf tables | écart maximal de 7e-8 sur les bornes |
| Estimateur contraint : formule fermée contre optimisation numérique | écart maximal de 4e-9 |
| Réduction à McNemar quand d0 = 0, exemple b = 5, c = 3 | Z = 2 / racine(8), exactement |
| Monotonie de Z(d0) sur 4 001 valeurs de d0, pour 625 tables | strictement décroissante pour toutes |
| Équivalence entre la décision et la borne basse, sur 3 000 tirages groupés par fiche | aucune différence |
| Risque à la marge, simulé (10 000 tirages par scénario) | 1,9 à 2,5 %, pour 2,5 % visés |
| Couverture de l'intervalle à 95 % | 94,6 à 95,8 % |
| Puissance quand les systèmes se valent, marge de 15 points | 62 à 87 % |
| Puissance quand les systèmes se valent, marge de 10 points | 34 à 55 % |

---

## 7. Un exemple fictif

Tables construites à la main, sans aucune donnée réelle : 73 questions, dont 50 réussies par les deux systèmes.

| Table fictive | Écart observé | Règle du 10 octobre | Score de Tango |
|---|---|---|---|
| E5 seul 1, BM25 seul 6 | -6,8 points | [-13,9 ; +0,6] : satisfait | [-15,7 ; +0,3] : non démontré |
| E5 seul 0, BM25 seul 6 | -8,2 points | [-14,7 ; -1,3] : satisfait | [-16,8 ; -2,8] : non démontré |
| E5 seul 6, BM25 seul 9 | -4,1 points | [-14,5 ; +6,3] : satisfait | [-15,2 ; +6,8] : non démontré |

Dans ces tables, BM25 gagne presque toutes les questions discordantes, mais il y en a peu. La règle du 10 octobre se dit sûre que l'écart réel dépasse -15 points ; le score de Tango répond qu'avec si peu de discordances, on ne peut pas exclure un retard de 15 points. Toutes les divergences vont dans ce sens.

---

## 8. Ce qui change en pratique

* **Protocole** (`03_protocole.md`) : sections 5 et 6, ligne D2 du tableau des décisions, historique et statut ; protocole figé à nouveau, avec une nouvelle empreinte inscrite dans le notebook.
* **Notebook 03** : le verdict utilise `noninferiority_tango` de `scripts/evaluation/metrics.py`, avec les questions groupées par fiche ; l'intervalle de la règle du 10 octobre est publié à titre descriptif.
* **Rapport** : `scripts/evaluation/rapport_tableaux.py` affiche l'intervalle du score de Tango, sa statistique, sa valeur p unilatérale et l'effet de plan.
* **Inchangé** : la marge de 15 points, les décisions D1 à D8, les familles secondaires F1 à F3 (leur test d'Obuchowski est bien calibré : 2,5 à 4,7 % pour 5 %), le seuil d'abstention, le jeu de questions.

---

## 9. Pourquoi l'amendement est légitime

* **Avant la mesure.** Modifier une règle après avoir vu les résultats permettrait de choisir celle qui arrange. Ici, la mesure n'a pas eu lieu, et la décision repose sur une simulation qui n'utilise que la structure du lot de test.
* **Plus prudent.** L'amendement ne peut que rendre la conclusion plus difficile pour E5. Il ne peut donc pas être soupçonné de favoriser l'encodeur, même après l'exposition du lot de test par la PR #63.
* **Tracé.** L'audit, cette fiche et l'historique du protocole documentent la décision et sa justification.

---

## 10. Limites

* **Effet de plan estimé.** Il est estimé sur les données elles-mêmes, et devient imprécis s'il y a très peu de questions discordantes ; il ne descend jamais sous 1.
* **Approximation.** Le score de Tango repose sur une approximation normale ; sur 73 questions, la simulation montre qu'elle tient le risque annoncé.
* **Prix.** La puissance baisse de 4 à 7 points par rapport à la règle du 10 octobre. Ce n'est pas une perte réelle : cette règle n'était plus puissante que parce qu'elle concluait trop facilement.

---

## 11. Références

* Tango, T. (1998). Equivalence test and confidence interval for the difference in proportions for the paired-sample design. Statistics in Medicine, 17, 891 à 908.
* Agresti, A. et Min, Y. (2005). Simple improved confidence intervals for comparing matched proportions. Statistics in Medicine, 24 (5), 729 à 740.
* Audit du notebook 03 : `03_audit_statistique.md`, dans ce dossier, et le script `audit_statistique.py`, dans `scripts/evaluation/`.
