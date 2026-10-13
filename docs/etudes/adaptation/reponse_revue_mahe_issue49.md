# Synthèse et Contrôle de Recette — Issue #49

**Destinataires :** Mahé BEGNIS & Agent de vérification  
**Auteur :** Remy RAYANE (Responsable D2 & Issue #49)  
**Date :** 13 octobre 2026 (révision finale avant Weekly 5)  
**Branche Git :** `feat/49-ajustement-encodeur`  
**Commit de référence :** [`42aaa41`](https://github.com/datatigersNLP/data_tigers_nlp/commit/42aaa41) (`origin/feat/49-ajustement-encodeur`)  
**Statut :** Poussé sur GitHub, recette d'entraînement et d'export figée, prêt pour la mesure officielle conjointe au Weekly 5 (15 octobre 2026).

---

## 1. Vue d'ensemble des 8 points traités

| # | Point demandé par Mahé | Fichier(s) impacté(s) | Statut & Résultat technique |
|---|---|---|---|
| **P1** | **Quantification symétrique des tables d'embeddings** | `scripts/adaptation/06_exporter_onnx.py` | Ajout de `extra_options={"ActivationSymmetric": True}`. 74/75 tenseurs identiques bit à bit à Xenova sur le modèle de base. Poids réduit à **112,89 Mio** (calibré Xenova). |
| **P2** | **Modèle TÉMOIN de base (isolation du graphe opset 14)** | `scripts/adaptation/06_exporter_onnx.py`, `scripts/indexation/fidelite_navigateur.html` | Export du modèle pré-entraîné avec la recette opset 14 (`models/multilingual-e5-small-base`). Exécution navigateur Chromium WASM validée : **92,58 %** Top-1. |
| **P3** | **Retrait des seuils statiques et alignement Notebook 02** | `06_exporter_onnx.py`, `07_mesurer_fidelite_822.py`, rapport PDF/MD | Seuils arbitraires (0,98, 0,97, rang 25) supprimés. Remplacés par la règle comparative face au `q8` officiel Xenova (91,8 %, 821/822 dans Top-5). |
| **P4** | **Versionnement du calcul des métriques navigateur** | `scripts/adaptation/08_calculer_metriques_navigateur.py` | Script dédié automatisant le calcul complet (753/822...), comparant à la baseline et consignant les empreintes SHA-256 opposables. |
| **R5** | **Correction `fidelite_navigateur.html` et `serveur_controle.py`** | `scripts/indexation/fidelite_navigateur.html`, `scripts/adaptation/serveur_controle.py` | Test de `res.ok` sur le POST (évite les faux positifs sur HTTP 501). Serveur sécurisé : vérification `Content-Type`, `Origin`, et sanctuarisation de `fidelite_navigateur.json`. |
| **R6** | **Encodage unitaire dans le Script 07 (`batch_size=1`)** | `scripts/adaptation/07_mesurer_fidelite_822.py` | Suppression du padding dynamique qui biaise les échelles INT8. Concordance Top-1 Python : **93,67 %** (ajusté) et **92,70 %** (témoin). |
| **R7** | **Génération dynamique de `quant_config.json`** | `scripts/adaptation/06_exporter_onnx.py` | Généré par introspection du graphe effectif (`onnx.load`), décrivant les 32 types d'opérateurs réels. |
| **R8** | **Requirements épinglés et rapport PDF actualisé** | `scripts/adaptation/requirements.txt`, `docs/etudes/adaptation/` | `onnx==1.23.2`, `onnxruntime==1.30.0`. Formulation rectifiée : authentification unique par empreinte SHA-256 (artefact conservé). PDF 8 pages recompilé au 13/10/2026. |

---

## 2. Tableau comparatif opposable (Navigateur Chromium WASM)

Mesures issues de l'exécution in-browser sur les **822 requêtes réalistes** du corpus M2 face aux **4 240 passages** de référence :

| Métrique de fidélité | Modèle Ajusté (WASM) | Témoin de BASE (WASM) | Réf. q8 Hub Xenova (Notebook 02) | Simulation Python (`batch=1`) |
|---|---:|---:|---:|---:|
| **Cosinus médian vs PyTorch FP32** | **0,99389** | **0,99653** | 0,99655 | 0,99653 |
| **Cosinus minimal vs PyTorch FP32** | **0,98627** | **0,99044** | 0,99196 | 0,99045 |
| **Concordance Top-1 (même 1er résultat)** | **91,61 %** (753 / 822) | **92,58 %** (761 / 822) | **91,8 %** (755 / 822) | **93,67 %** (770 / 822) |
| **Top-1 référence présent dans le Top-5** | **99,88 %** (821 / 822) | **99,88 %** (821 / 822) | **99,9 %** (821 / 822) | **100,00 %** (822 / 822) |
| **Rang maximal de dégradation** | **10** (P99 : 2,8) | **7** (P99 : 3,0) | **9** | **5** |
| **Temps d'encodage moyen / requête** | **78,7 ms** | **73,7 ms** | 18,6 ms | 15,2 ms |

> **Conclusion sur le témoin de base :**  
> L'écart d'environ 3 % sur le premier résultat par rapport au graphe Xenova existe déjà sur le modèle de base exporté sous opset 14. Le modèle ajusté (91,61 %) présente une fidélité strictement comparable à ce témoin (92,58 %), confirmant que l'ajustement sémantique n'a induit aucune régression de quantification.

---

## 3. Empreintes cryptographiques SHA-256 des artefacts opposables

| Rôle de l'artefact | Chemin du fichier | Taille | Empreinte SHA-256 |
|---|---|---:|---|
| **Paires d'entraînement** | `data/adaptation/train_paires.jsonl` | 174 552 octets | `2d377eb66e7f4ca0e8e4cf34b089e5da7c46e47ddceab9f964764df468c21698` |
| **ONNX q8 Ajusté** | `models/multilingual-e5-small-finetuned/onnx/model_quantized.onnx` | 112,89 Mio | `934a202bee5599fc45c0cb753414a7b2b490605bed84e72f471072e6ee53d047` |
| **Résultats navigateur Ajusté** | `data/indexation/controle/fidelite_navigateur_ajuste.json` | 9,97 Mio | `72baf3e4011aa610a99c19a36768c1e13703e0d197f721db4c422554d95f26d0` |
| **ONNX q8 Témoin base** | `models/multilingual-e5-small-base/onnx/model_quantized.onnx` | 112,89 Mio | `30ae0f2153f7e14ce5afe082c68ee251d0cce6c26e8caa71307fbd8ebf4bcb90` |
| **Résultats navigateur Témoin** | `data/indexation/controle/fidelite_navigateur_temoin.json` | 9,96 Mio | `72a612ea392dce707fd1b59c9a7b1bc200dcfaea8bf585d1ef97c21953330a63` |

*Note sur la reproductibilité :* `train_paires.jsonl` ayant été produit sous Ollama sans graine déterministe fixe, l'empreinte SHA-256 authentifie l'artefact de manière opposable et non révocable. Le fichier est conservé dans l'environnement local (exclu de Git conformément à la politique d'exclusion de `data/`).

---

## 4. Procédure de vérification pour l'agent de Mahé

Toutes les étapes suivantes peuvent être rejouées de manière autonome dans le terminal du projet :

### Étape 1 : Récupérer le commit et examiner l'historique
```bash
git checkout feat/49-ajustement-encodeur
git pull origin feat/49-ajustement-encodeur
git log -1 --stat
```

### Étape 2 : Vérifier les métriques navigateur opposables
```bash
# Pour le modèle ajusté :
python scripts/adaptation/08_calculer_metriques_navigateur.py \
  --fichier data/indexation/controle/fidelite_navigateur_ajuste.json \
  --modele ajuste

# Pour le modèle témoin de base :
python scripts/adaptation/08_calculer_metriques_navigateur.py \
  --fichier data/indexation/controle/fidelite_navigateur_temoin.json \
  --modele temoin
```

### Étape 3 : Vérifier l'encodage unitaire Python (batch_size=1)
```bash
# Mesure Python CPU pour le modèle ajusté :
python scripts/adaptation/07_mesurer_fidelite_822.py --modele ajuste

# Mesure Python CPU pour le modèle témoin :
python scripts/adaptation/07_mesurer_fidelite_822.py --modele base
```

### Étape 4 : Vérifier l'intégrité du rapport PDF
Consulter le PDF recompilé dans `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.pdf` (8 pages, daté du 13 octobre 2026, incluant les tableaux comparatifs et les hashs SHA-256).

---

## 5. Règle de décision pour le Weekly 5 (15 octobre 2026)

* Le modèle ajusté reste sur sa branche de travail et **n'est pas déployé sur le front de production**.
* L'arbitrage final pour le déploiement sera opéré conjointement au Weekly 5 selon le protocole officiel `05_protocole_ajustement.md` (gain de Recall@5 positif ou nul à la fois sur le banc d'équipe et sur le CDTN).
