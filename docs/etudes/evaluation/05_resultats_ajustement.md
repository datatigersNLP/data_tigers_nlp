# Encodeur ajusté et améliorations du site : résultats (#164)

**Date** : 15 novembre 2026. **Ticket** : #164. **Règles** : protocole 05 (`05_protocole_ajustement.md`, figé le 14 octobre) et son amendement A1 (`05_amendement_A1.md`, figé le 15 novembre, commit `7e983c5`, SHA-256 `be9b6fd7…`). **Auteur** : Mahé BEGNIS.

---

## 1. Objet

Le ticket #164 vise trois améliorations du site du volet A :

* **A1** : servir l'encodeur ajusté de la #49, si la règle écrite d'avance le permet ;
* **A2** : présenter 10 passages regroupés par fiche, au lieu de 5 passages un par un ;
* **A3** : avertir le visiteur quand la correspondance est faible, sans masquer les passages.

A1 est une décision, prise selon le protocole 05. A2 et A3 changent l'interface ; leurs effets sur le lot de test sont décrits ici, mais aucune décision n'en dépend.

---

## 2. A1 : mesure de l'encodeur ajusté

### 2.1 Mesure

Exécutée deux fois par `scripts/evaluation/ajustement_05.py mesurer --mode mesure`, avec un contenu identique (SHA-256 `d35b4936…`). Les questions sont encodées dans Chrome 155 sans interface, par la page d'encodage du notebook 03 (amendement A1, section 4).

| Jeu de l'équipe, lot de test (73 questions, 61 fiches) | Base servie | Ajusté |
|---|---:|---:|
| Recall@1 | 20,5 % | 26,0 % |
| Recall@5 (métrique principale) | 43,8 % | 63,0 % |
| Recall@10 | 57,5 % | 74,0 % |
| MRR@10 | 0,320 | 0,416 |
| Recall@5 au niveau de la fiche | 83,6 % | 86,3 % |
| AUC de l'abstention (24 questions hors corpus) | 0,841 | 0,865 |

| CDTN (494 formulations, 131 requêtes) | Base servie | Ajusté |
|---|---:|---:|
| Recall@5 | 67,4 % | 72,3 % |
| Recall@5 au niveau de la fiche | 88,3 % | 89,7 % |

Écart de Recall@5, ajusté moins base servie, avec l'intervalle du score de Tango corrigé de l'effet de plan :

| Jeu | Écart | IC 95 % | Effet de plan | Questions gagnées / perdues | McNemar exact |
|---|---:|---|---:|---:|---:|
| Équipe, lot de test | +19,2 points | +9,7 à +30,4 | 1,05 | 15 / 1 | p = 0,0005 |
| CDTN | +4,9 points | +0,6 à +9,3 | 1,73 | 45 / 21 | p = 0,004 (groupé par requête : 0,033) |

### 2.2 Contrôles

* **Reproduction du notebook 03** : la base servie, encodée de nouveau dans le navigateur, redonne bit à bit les 113 vecteurs du 13 octobre ; recalculées sur le lot de test, ses métriques (Recall@1, @5, @10, MRR@10, Recall@5 à la fiche, AUC) sont celles du notebook 03 à 10⁻¹² près.
* **Index de l'ajusté** : réencodé en fp32 par l'ajusté, avec le tokeniseur de base ; cosinus minimal de 0,99999982 avec l'index de Remy.
* **Deux exécutions** du mode développement, puis du mode mesure : contenus identiques.

### 2.3 Décision

* **Règle (protocole 05, section 4)** : servir l'ajusté si son écart observé de Recall@5 est positif ou nul sur les deux jeux, et s'il peut être hébergé (section 5). Les deux écarts sont positifs : **l'ajusté est servi**, l'hébergement ayant passé ses contrôles (section 3).
* **Conclusion statistique** : la borne basse de l'intervalle sur le jeu de l'équipe dépasse 0 ; l'ajusté est déclaré meilleur que la base servie au niveau du passage. Au niveau de la fiche, l'écart (+2,7 points sur le lot de test) n'est pas testé par le protocole.

---

## 3. Hébergement (protocole 05, section 5)

* **Élagage sans perte du vocabulaire** (`scripts/allegement/elaguer_vocabulaire.py`, #50) : le q8 ajusté passe de 118 371 400 à 68 925 256 octets (de 112,9 à 65,7 Mio), sous la limite de 100 Mio par fichier de GitHub. Deux élagages donnent des fichiers identiques octet par octet.
* **Contrôle en Python** (`scripts/allegement/verifier_elagage.py`, avec le q8 ajusté complet pour source) : découpage identique pour les 822 requêtes de contrôle, les 113 textes de la mesure, les 5 433 titres et variantes du CDTN et les 4 240 passages ; sorties du q8 identiques bit à bit sur 935 requêtes sur 935.
* **Contrôle dans le navigateur** (`scripts/allegement/controle_navigateur.html?index=index_ajuste&reference=ajuste`, Chrome 155 sans interface) : les 822 vecteurs de contrôle du modèle élagué, lu par l'en-tête du nouvel index, sont identiques bit à bit à ceux du q8 ajusté complet, en 19,7 ms par requête.
* **Seuil d'abstention recalculé** (`scripts/evaluation/cdtn_seuil.py calculer_ajuste`, règle de la section 8.2 du protocole du notebook 03) : **0,7683**, 5e centile des scores maximaux des 479 variantes du CDTN encodées dans le navigateur par l'ajusté ; intervalle à 95 % de 0,7472 à 0,7827 (rééchantillonnage des 103 requêtes, 10 000 tirages, graine 20261010). 24 variantes sur 479 sont sous le seuil.
* **Dossier séparé** : le site lit `front/public/index_ajuste/`. Le dossier `front/public/index/` reste inchangé, car la chaîne du volet B le lit et son empreinte figure dans le verrou de la #131.

---

## 4. A2 et A3 : ce que voit le visiteur

### 4.1 Règles, fixées avant cette mesure

* **A2** : 10 passages, regroupés par fiche dans l'ordre du meilleur passage de chaque fiche (ticket #164).
* **A3** : refus inchangé sous le seuil ; avertissement entre le seuil et une borne fixée sur le CDTN, le **25e centile** des mêmes 479 scores maximaux, soit 0,8140 (`cdtn_seuil.py zone_grise_ajuste`). Sur le CDTN, 96 formulations sur 479 tombent dans cette zone (20,0 %), toutes légitimes.
* **Chronologie** : la borne a été choisie et calculée le 15 novembre, après la mesure de A1, qui avait lu le lot de test mais n'en publie que l'AUC ; aucun score maximal du lot de test n'a été regardé avant ce choix. Les mesures de cette section ont été faites ensuite.

### 4.2 Mesures descriptives sur le lot de test

Calculées par `scripts/evaluation/mesures_site_164.py`, exécuté deux fois avec un contenu identique (SHA-256 `3314085a…`). Mêmes questions, mêmes vecteurs du navigateur et même règle de pertinence D4 que la mesure de A1. Intervalles de Wilson à 95 %, corrigés de l'effet de plan par fiche pour les questions du corpus.

| Configuration | Rappel au passage | Rappel à la fiche | Fiches affichées, en moyenne |
|---|---|---|---:|
| Site jusqu'au 15/11 : base, 5 passages | 43,8 % [32,9 ; 55,4] | 83,6 % [73,0 ; 90,5] | 3,0 |
| Ajusté, 5 passages (A1 seul) | 63,0 % [50,9 ; 73,6] | 86,3 % [76,5 ; 92,4] | 2,4 |
| Ajusté, 10 passages par fiche (A1 et A2) | 74,0 % [62,2 ; 83,1] | 93,2 % [85,6 ; 96,9] | 4,0 (au plus 9) |

Comparaisons par paires, intervalle du score de Tango :

* **Fiche, site actuel contre site précédent** : +9,6 points [+4,1 ; +18,5], 7 questions gagnées, aucune perdue (McNemar exact, p = 0,016).
* **Passage, site actuel contre site précédent** : +30,1 points [+20,8 ; +41,5], 22 questions gagnées, aucune perdue.
* **Fiche, effet de A2 seul** (10 passages contre 5, avec l'ajusté) : +6,8 points [+1,5 ; +15,1], 5 questions gagnées. Ce gain ne peut pas être négatif : afficher plus de passages ne retire aucune fiche. Sa contrepartie est la lecture : 4,0 fiches en moyenne au lieu de 2,4.

| Abstention, lot de test | Base, seuil 0,8560 | Ajusté, seuil 0,7683 |
|---|---|---|
| Questions du corpus conservées | 72 / 73, 98,6 % [92,6 ; 99,8] | 70 / 73, 95,9 % [89,1 ; 98,5] |
| Questions hors corpus rejetées | 9 / 24, 37,5 % [21,2 ; 57,3] | 10 / 24, 41,7 % [24,5 ; 61,2] |

| Zone grise de l'ajusté | Questions concernées |
|---|---|
| Questions du corpus | 23 / 73, 31,5 % [21,8 ; 43,1] |
| Questions hors corpus | 13 / 24, 54,2 % [35,1 ; 72,1] |

* **Hors corpus** : 10 questions sont rejetées, 13 reçoivent l'avertissement, une seule s'affiche sans aucun signal.
* **Questions du corpus** : 3 sont rejetées, 23 reçoivent l'avertissement, 47 s'affichent sans signal.
* **L'avertissement ne signale pas de moins bons résultats** pour les questions du corpus : une fiche pertinente figure parmi les 10 passages pour 22 des 23 questions en zone grise, et pour 45 des 47 questions au-dessus de la borne. Il signale une formulation éloignée des passages, pas un résultat faux.
* **Libellé** : le ticket prévoyait « hors périmètre probable ». Le site affiche « Correspondance moins nette que d'habitude », choisi avant la mesure, parce que la zone contient par construction 20 % des questions légitimes du CDTN. La mesure le confirme : sur le lot de test, 23 des 36 questions en zone grise viennent du corpus. Cette proportion dépend toutefois de la composition du lot (73 contre 24), qui n'est pas celle des visiteurs.

### 4.3 Contrôles

* **Reproduction** : le script refuse d'écrire si les métriques du site précédent ne redonnent pas celles du notebook 03 (32 et 61 questions sur 73, 72 conservées, 9 rejetées), ou si celles de l'ajusté ne redonnent pas la mesure de A1 (46 questions, AUC de 0,865). Les six contrôles passent.
* **Code du site, hors navigateur** : `classer`, `regrouperParFiche`, `horsPerimetre` et `zoneGrise` (`front/src/recherche/moteur.js`), exécutés par Node sur les 97 questions, redonnent les mêmes 10 passages, les mêmes fiches et les mêmes états que le calcul Python ; écart de score d'au plus 1,2 × 10⁻⁷.
* **Site construit, dans le navigateur** : servi sur 127.0.0.1 et piloté dans Chrome 155, le site reçoit les 97 questions dans son champ de saisie. Les 970 passages affichés (lien, score à trois décimales, ordre par fiche) et les 97 états (refus, zone grise) sont identiques à ceux du calcul Python. Aucune requête ne sort de 127.0.0.1.
* **Tests du moteur** (`node --test front/src/recherche/moteur.test.js`) : 22 tests réussis, contre 16 avant : le contrôle du modèle versionné porte désormais sur les deux modèles, et 6 tests sont nouveaux (référence de seuil de l'ajusté et croisements de modèle et d'index refusés, index ajusté accepté, zone grise aux bornes, regroupement sur un exemple et sur le corpus, 24 rejets et 96 questions en zone grise sur le CDTN). Six erreurs introduites volontairement sont toutes détectées.

---

## 5. Limites

* **Effectifs** : 73 questions du corpus, issues de 61 fiches, et 24 hors corpus ; les intervalles restent larges.
* **Lot de test déjà lu** : il a servi à la mesure de A1. Aucun paramètre de A2 ou de A3 n'y a été réglé : 10 passages viennent du ticket, la borne du CDTN.
* **Questions réelles** : les visiteurs ne posent pas les questions du lot de test ; la part des questions en zone grise sur le site peut différer des 31,5 % mesurés.
* **Volet B inchangé** : sa chaîne lit toujours l'index de base, `front/public/index/`.

---

## 6. Fichiers

| Fichier | Rôle | SHA-256 |
|---|---|---|
| `front/public/index_ajuste/index_m2.json` | en-tête de l'index servi | `d438f0254cdec966…` |
| `front/public/index_ajuste/index_m2.f32` | vecteurs des passages, encodeur ajusté | `dc8daa7243bec30c…` |
| `front/public/index_ajuste/passages_m2.json` | passages, copie de ceux de `front/public/index/` | `aee5bbdbe401de75…` |
| `front/public/modele/multilingual-e5-small-ajuste-q8-elague-13ed78c9/onnx/model_quantized.onnx` | q8 ajusté élagué | `13ed78c9bf0c4e4b…` |
| `data/evaluation/notebook03/seuil_cdtn_ajuste.json` (non versionné) | seuil de l'ajusté | `b3fca6371349b1ee…` |
| `data/evaluation/notebook03/zone_grise_ajuste.json` (non versionné) | borne de la zone grise | `c6ae7ac0c36f800b…` |
| `data/evaluation/ajustement_05/mesure_20261115T142537Z.json` (non versionné) | mesure de A1 | `d35b49365f0c36ee…` |
| `data/evaluation/ajustement_05/site_164_20261115T144406Z.json` (non versionné) | mesures de la section 4 | `3314085ae3ac54b2…` |

---

## 7. Historique

* **15 novembre 2026.** Mesure de A1, hébergement, seuil recalculé, interface A2 et A3, mesures descriptives et contrôles.
