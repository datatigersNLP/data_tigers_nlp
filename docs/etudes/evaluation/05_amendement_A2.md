# Protocole 05 : amendement A2, encodeur ajusté v2

**Équipe** Data Tigers  
**Ticket** #167 (suite de #49 et #164)  
**Responsable** Mahé BEGNIS  
**Statut** rédigé le 15 novembre 2026, avant la génération des données d'entraînement. Il sera figé, avec les empreintes du modèle et de l'index inscrites à la section 9, avant toute lecture du lot de test ou du CDTN par l'encodeur v2 ; le commit de gel sera publié sur le #167. Le protocole 05 et l'amendement A1 ne sont pas modifiés : cet amendement les complète.

---

## 1. Motif

L'encodeur ajusté servi depuis le 15 novembre (v1, #164) a été entraîné sur 109 paires question-passage, en 14 pas d'optimisation, et gagne +19,2 points de Recall@5 sur le lot de test [+9,7 ; +30,4] et +4,9 points sur le CDTN [+0,6 ; +9,3] (`05_resultats_ajustement.md`). Cet amendement mesure, une seule fois, si la même recette nourrie de beaucoup plus de questions synthétiques fait mieux que la v1. Un seul facteur change : le volume des données d'entraînement.

---

## 2. Données d'entraînement

* **Passages** : le découpage M2 (`data/decoupage/passages/passages_m2.parquet`, SHA-256 `a7eabb62…`), 4 240 passages, les mêmes que l'index du site.
* **Fiches exclues** : celles de la #49, recalculées à l'identique. Ce sont les 66 fiches des questions du corpus de `jeu-questions-v1` (lot de test et lot de calibration), plus `les-heures-supplementaires-contreparties`, retirée du jeu après l'extraction de la #49. Soit 67 fiches et 1 463 passages, comme le documente `scripts/adaptation/README.md`.
* **Passages retenus** : tous les passages des 194 autres fiches qui comptent au moins 40 tokens, soit 2 720 passages. Les 57 plus courts sont des titres ou des renvois sans contenu à interroger.
* **Validation synthétique** : 19 fiches, soit 10 % des 194 arrondi à l'entier, tirées par `numpy.random.default_rng(20261115)` dans la liste triée des fiches, sont mises de côté avec leurs 278 passages. Leurs questions ne servent qu'au garde-fou de la section 4. Restent 2 442 passages pour l'entraînement.
* **Génération** : une question par passage, avec la consigne de `03_generer_paires_locales.py` (#49) mot pour mot. Seule différence : le passage est donné en entier au lieu d'être tronqué à 900 caractères, pour que la question puisse porter sur toute sa longueur. Les options de la #49 sont reprises : température 0,3, top_p 0,9, 75 tokens au plus. On y ajoute une graine par passage, 20261115 plus son rang dans la liste triée des passages, pour que la génération soit rejouable.
* **Générateur** : le témoin T (`qwen2.5-7b-instruct:temoin-q4_k_m-local`, digest `8a077f3d…`, #52), servi par Ollama 0.40.13 sur 127.0.0.1, dont le digest et la version sont contrôlés avant chaque appel de lot.
* **Filtres** : ceux de la #49, dans le même ordre. Nettoyage des guillemets et première ligne seulement ; coupe après le premier point d'interrogation, et rejet s'il n'y en a pas ; longueur de 25 à 220 caractères ; rejet des méta-formulations (« selon le texte », etc.) ; rejet si l'indice de Jaccard avec l'une des 105 questions de `jeu-questions-v1` dépasse 0,40. La #49 ne comparait qu'aux questions du test : la comparaison aux deux lots est plus stricte.
* **Filtre ajouté après le pilote** : un pilote de 20 passages, jamais utilisé pour l'entraînement, a donné des questions qui renvoient à leur source (« mentionnés dans la fiche », « selon la fiche »), que les filtres de la #49 laissent passer. Sont donc aussi rejetées, après les méta-formulations, les questions où « dans », « selon » ou « d'après » précède « ce texte », « cet extrait », « la fiche » ou une forme voisine, sauf si le mot est suivi de « de », « du » ou « des » : « la fiche de paie », « la fiche de poste » ou « l'extrait de casier judiciaire » sont des termes du droit du travail.
* **Doublons** : après les filtres, les doublons exacts, à la casse et aux espaces près, sont retirés ; la première occurrence dans l'ordre des passages est gardée.
* **Relecture** : 30 paires d'entraînement tirées par la graine 20261116 sont relues contre leur passage. Une paire est fausse si la question ne se comprend pas sans le passage (renvoi au texte ou à la fiche, pronom ou démonstratif sans antécédent), ou si le passage n'y répond pas, même en partie. **Le lot est utilisable si au plus 3 paires sur 30 sont fausses** ; sinon, tout s'arrête. Cette relecture est faite par l'assistant d'IA de Mahé, pas par un humain, et elle est déclarée comme telle.
* **Volume minimal** : au moins 1 500 paires d'entraînement après filtres ; sinon, tout s'arrête.

---

## 3. Entraînement

* **Recette de la #49, inchangée** (`04_ajuster_encodeur.py`) : modèle de départ `intfloat/multilingual-e5-small`, révision `614241f6` ; perte `MultipleNegativesRankingLoss` ; lot de 16, taux d'apprentissage 2e-5, 2 époques, échauffement de 10 %, décroissance des poids de 0,01, graine 42.
* **Paires** : préfixes `query: ` et `passage: `, le positif étant le texte d'entrée de l'encodeur du passage (`entree_encodeur`).
* **Exécution** : sur processeur, avec les versions figées de `scripts/evaluation/requirements-lock.txt`, plus `accelerate`, qu'exige l'entraîneur de sentence-transformers.
* **Modèle retenu** : celui de la fin de l'entraînement. Il n'est jamais choisi sur la validation synthétique.

---

## 4. Garde-fou avant toute mesure

* **Jeu** : les questions des 19 fiches mises de côté, après les mêmes filtres.
* **Calcul** : pour la base, la v1 et la v2, les questions et les 4 240 passages sont encodés en PyTorch fp32, avec le tokeniseur de l'encodeur de base, comme l'index de l'ajusté (#164). La mesure est le Recall@5 du passage d'origine de chaque question.
* **Règle** : si le Recall@5 de la v2 n'est pas strictement supérieur à celui de la v1, tout s'arrête. Le lot de test et le CDTN ne sont alors pas lus, et la v1 reste servie.
* **Biais connu** : les paires de la v1 ne sont pas sur le Mac de Mahé, et la v1 a peut-être vu des passages de ces 19 fiches. Ce biais favorise la v1 : le garde-fou est conservateur.

---

## 5. Hébergement

Les mêmes étapes que pour la v1 (`scripts/allegement/README.md`, section « Pour l'encodeur ajusté ») :

* **Export ONNX et q8** : export fp32, puis quantification q8 avec la recette de `06_exporter_onnx.py`, qui a produit le q8 de la v1.
* **Dossier au format de Transformers.js**, avec le tokeniseur de la v1.
* **Élagage sans perte du vocabulaire**, puis deux contrôles, dont un échec empêche de servir la v2.
* **Contrôle en Python** : le découpage est identique et les 935 sorties sont identiques bit à bit.
* **Contrôle dans le navigateur** : les 822 vecteurs de contrôle de la version élaguée sont identiques bit à bit à ceux de la version complète.
* **Index** : les 4 240 passages en fp32, encodés en PyTorch par la v2 avec le tokeniseur de base.

---

## 6. Mesure

* **Identique au protocole 05 (section 3) et à l'amendement A1** : vecteurs des questions calculés dans le navigateur avec le q8 complet ; lot de test (73 questions du corpus, 24 hors corpus, règle D4) et CDTN (494 formulations, 131 requêtes).
* **Métrique principale** : le Recall@5 au niveau du passage.
* **Écart principal** : v2 moins v1, avec l'intervalle du score de Tango corrigé de l'effet de plan (par fiche pour le lot de test, par requête pour le CDTN) et la valeur p exacte de McNemar.
* **Rapportés aussi** : Recall@1 et @10, MRR@10, niveau de la fiche, AUC de l'abstention, et, à titre descriptif, l'écart de la v2 à la base.
* **Contrôle de reproduction** : les métriques de la base et de la v1, recalculées par la mesure, doivent être identiques à celles publiées le 15 novembre (`05_resultats_ajustement.md`) ; sinon, rien n'est décidé.
* **Deux exécutions**, au contenu identique.

---

## 7. Règle de décision, écrite d'avance

* **Servir la v2 à la place de la v1** si le garde-fou de la section 4 est passé, si l'hébergement de la section 5 est validé, et si l'écart observé de Recall@5 (v2 moins v1) est positif ou nul sur le CDTN et sur le lot de test, et strictement positif sur au moins l'un des deux jeux.
* **Sinon, la v1 reste servie.** À égalité sur les deux jeux, on ne change pas le modèle servi : un changement sans gain n'apporte que du risque.
* **Conclusion statistique** : la v2 n'est déclarée meilleure que la v1 sur un jeu que si la borne basse de l'intervalle de Tango y dépasse 0.
* **Si la v2 est servie** : le seuil d'abstention et la borne de la zone grise sont recalculés par les règles de la #164 (5e et 25e centiles des scores maximaux des variantes du CDTN, encodées dans le navigateur par la v2), et les mesures descriptives du site (`mesures_site_164.py`) sont refaites.

---

## 8. Écarts déclarés et limites

* **Lot de test exploité pour la cinquième fois** (notebook 03, protocoles 07, 06, 05 et 08) : l'écart sur ce lot est descriptif et ne sert qu'à vérifier que la v2 ne recule pas.
* **Générateur** : le témoin T remplace le modèle de la #31, qui n'est plus sur le Mac. Les deux sont Qwen2.5-7B-Instruct quantifié en Q4_K_M ; T a été produit par notre propre export (#140).
* **Sélection des passages** : tous ceux d'au moins 40 tokens, sans troncature, au lieu d'un passage par fiche de 120 à 420 tokens tronqué à 900 caractères.
* **Filtres** : ceux de la #49, plus le rejet des renvois à la source décidé sur le pilote (section 2), et la comparaison aux 105 questions du jeu au lieu des seules questions du test.
* **Relecture faite par une IA**, et non par un humain (section 2).
* **Faux négatifs dans le lot** : deux passages d'une même fiche peuvent se retrouver dans un même lot d'entraînement et servir de négatifs l'un pour l'autre. La part de lots concernés sera rapportée.
* **Volet B non concerné** : son index reste celui de l'encodeur de base, verrouillé par la #131.

---

## 9. Valeurs inscrites au gel

À compléter au gel, avant la mesure : empreintes des données générées, de la v2, de son q8 complet, de sa version élaguée et de son index ; résultat du garde-fou.

---

## 10. Historique

* **15 novembre 2026** : amendement rédigé avant la génération des données ; filtre des renvois à la source ajouté après un pilote de 20 passages, jamais utilisé pour l'entraînement.
