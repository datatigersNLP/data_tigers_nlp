# ONNX Runtime (Python et Web)

## Identification
- Version : 1.30.0 en Python (figée dans les fichiers `requirements-lock.txt` : identique pour tous) ; ONNX
  Runtime Web suit la version embarquée par Transformers.js
- Nature : moteur d'exécution de modèles
- Assignés : Mahé (#30, PR #40), Rémy (#49) ; prévus : Jibril (#49) ; Mahé, Rémy (#50)
- Coordination : Mahé
- Période d'utilisation : (Mahé) du 27 au 30 septembre 2026 en Python (notebook 02), et depuis dans le navigateur, à travers Transformers.js ; (Remy) du 6 au 14 octobre 2026 en Python et sous Chromium WASM pour l'export de #49 (PR #63)
- Besoin du projet auquel il répond : exécuter l'encodeur au format ONNX, en Python pour l'index et dans le navigateur via Transformers.js.

## Mise en place
- Temps avant le premier résultat utile : (Remy) moins d'une demi-journée pour exporter l'encodeur ajusté de #49 en ONNX FP32 et `q8` (`scripts/adaptation/06_exporter_onnx.py`, PR #63).
- Installation et configuration : (Remy) dépendances épinglées dans `scripts/adaptation/requirements.txt` (`onnx==1.23.2`, `onnxruntime==1.30.0`, Python 3.12.10 sous Windows 11).
- Prérequis découverts en chemin : (Remy) la règle `.gitignore` du projet masque par défaut les fichiers `.onnx` ; nécessité d'autoriser explicitement le suivi hors `models/` si un modèle de contrôle est servi localement (PR #63, commit `66b593a`), et d'aligner la quantification sur `per_channel=True`, `reduce_range=True` et `extra_options={"ActivationSymmetric": True}`.
- Difficultés non expliquées par la documentation : (Remy) dans les essais locaux sous Transformers.js / ONNX Runtime Web, le modèle et le tokeniseur sont mis en cache par l'API Cache du navigateur (`caches.delete("transformers-cache")`) et non par IndexedDB (PR #63, commit `bd0639f`).

## Usage réel
- Tâche réalisée, ticket ou pull request :
  - (Mahé) Notebook 02 (#30, PR #40) : parité entre ONNX fp32 et PyTorch, puis comparaison de cinq précisions du modèle servi, mesurée dans le navigateur.
  - (Remy) Ticket #49 (PR #63) : export ONNX FP32, quantification dynamique INT8 (`q8`) de l'encodeur ajusté et d'un modèle témoin de base (`scripts/adaptation/06_exporter_onnx.py`), puis contrôle de fidélité dans le navigateur (`08_calculer_metriques_navigateur.py`).
- Commande, configuration ou scénario :
  - (Mahé) Fichiers ONNX de `Xenova/multilingual-e5-small`, révision `761b726`, exécutés en Python par ONNX Runtime et dans Chromium par ONNX Runtime Web.
  - (Remy) Export en opset 14 et quantification `quantize_dynamic` avec `per_channel=True`, `reduce_range=True` et `ActivationSymmetric=True`, exécutés en Python (`07_mesurer_fidelite_822.py`) puis dans Chromium WASM via `scripts/indexation/fidelite_navigateur.html` sur les 822 requêtes de contrôle et 4 240 passages M2.
- Résultat obtenu :
  - (Mahé) Premier résultat identique au calcul exact, dans le navigateur : q8 91,8 % (112,8 Mio), uint8 90,8 %, int8 85,8 %, fp16 99,9 % (224,4 Mio), fp32 100 % (448,5 Mio) (notebook 02, section 8).
  - (Remy) Parité FP32 validée (cosinus minimal `1,00000000`, écart max `1,17 × 10⁻⁷`). En `q8`, l'option `ActivationSymmetric=True` rend 74 tenseurs sur 75 du témoin strictement identiques bit à bit à Xenova et porte la concordance Top-1 dans Chromium WASM à **769/822 (93,55 %)** pour l'ajusté (cosinus médian 0,99384) et **761/822 (92,58 %)** pour le témoin (`01_ajustement_encodeur_contrastif.md`, section 5).
- Temps gagné ou perdu, s'il peut être estimé : (Remy) temps passé sur le diagnostic initial d'un export `q8` sans `ActivationSymmetric` (753/822 avant correction le 14/10, commit `42aaa41`).

## Qualités observées
- (Mahé) En fp32, le même modèle donne exactement les mêmes vecteurs en Python et dans le navigateur (cosinus 1).
- (Remy) Permet de tracer finement, tenseur par tenseur, l'effet des options de quantification et d'isoler la part liée au graphe d'export opset 14 face aux poids réels : le témoin de base et Xenova divergent en premier résultat sur 52 requêtes sur 822 malgré une fidélité globale comparable (PR #63).

## Défauts et limites observés
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas :
  - (Mahé) Un critère qui a échoué : la première version du notebook 02 exigeait un cosinus d'au moins 0,9999 entre le q8 du navigateur et celui de Python ; le minimum mesuré valait 0,9942. ONNX Runtime Web n'exécute pas le modèle quantifié comme ONNX Runtime en Python. Le critère a été remplacé par une mesure sur le classement, décidée avant de mesurer (notebook 02, section 8).
  - (Remy) En exécution Python CPU (`07_mesurer_fidelite_822.py`), le modèle quantifié présente de légers écarts d'arrondi selon le processeur hôte (762/822 sur PC Windows contre 791/822 sur Mac), alors que le moteur WebAssembly (WASM) du navigateur redonne exactement 761/822 sur les deux machines pour le modèle témoin (`01_ajustement_encodeur_contrastif.md`, section 5.2).

## Comparaison
- Méthode ou outil utilisé auparavant : (Remy) inférence directe PyTorch / Sentence Transformers sur CPU/GPU en Python.
- Différences observées : (Remy) portabilité sans backend dans le navigateur via WebAssembly et division par quatre du poids disque en `q8` (448,5 Mio vers 112,9 Mio sur nos exports ; le modèle de base Xenova de 112,8 Mio a ensuite été ramené à 65,7 Mio par l'élagage sans perte de Mahé en #50 / PR #78), au prix d'une perte de déterminisme arithmétique entre CPU Python et WASM.
- Cas où l'ancienne méthode reste préférable : (Remy) en Python côté serveur ou chaîne hors ligne (Volet B), l'encodeur `fp32` reste préférable pour éviter l'erreur de quantification.

## Décision
(Mahé) Adopté, à travers Transformers.js dans le navigateur.
- Motif : (Mahé) le format ONNX est celui que le navigateur sait exécuter ; le q8 est servi pour son poids, et son effet sur la qualité est testé au notebook 03 (famille F3).

## À retenir pour le rapport
- Apport : (Mahé) un même fichier de modèle, exécuté en Python et dans le navigateur.
- Principale limite : (Mahé) un modèle quantifié ne se comporte pas de la même façon d'un environnement d'exécution à l'autre.
- Ce que la documentation ne dit pas : (Mahé) l'écart entre le q8 de Python et celui du navigateur ; il faut mesurer là où le modèle sera servi.
- Précision complémentaire : (Remy) la quantification symétrique explicite (`ActivationSymmetric=True`) des tables d'embeddings est déterminante pour aligner un export maison sur la référence Xenova (74/75 tenseurs identiques bit à bit sur le témoin, PR #63).

## Preuves
- Pull request #40 : parité ONNX fp32 et PyTorch, critère de parité q8 échoué puis diagnostiqué (notebook 02, section 8).
- Ticket #49 et PR #63 : export et quantification de l'encodeur ajusté et du témoin (`scripts/adaptation/06_exporter_onnx.py`, `08_calculer_metriques_navigateur.py`, `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md`, section 5).
