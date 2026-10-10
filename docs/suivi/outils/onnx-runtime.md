# ONNX Runtime (Python et Web)

## Identification
- Version : 1.30.0 en Python (figée dans les fichiers `requirements-lock.txt` : identique pour tous) ; ONNX
  Runtime Web suit la version embarquée par Transformers.js
- Nature : moteur d'exécution de modèles
- Assignés : Mahé (#30, PR #40), Rémy (#49) ; prévus : Jibril (#49) ; Mahé, Rémy (#50)
- Coordination : Mahé
- Période d'utilisation : (Mahé) du 27 au 30 septembre 2026 en Python (notebook 02), et depuis dans le navigateur, à travers Transformers.js
- Besoin du projet auquel il répond : exécuter l'encodeur au format ONNX, en Python pour l'index et dans le navigateur via Transformers.js.

## Mise en place
- Temps avant le premier résultat utile :
- Installation et configuration :
- Prérequis découverts en chemin :
- Difficultés non expliquées par la documentation :

## Usage réel
- Tâche réalisée, ticket ou pull request :
  - (Mahé) Notebook 02 (#30, PR #40) : parité entre ONNX fp32 et PyTorch, puis comparaison de cinq précisions du modèle servi, mesurée dans le navigateur.
- Commande, configuration ou scénario :
  - (Mahé) Fichiers ONNX de `Xenova/multilingual-e5-small`, révision `761b726`, exécutés en Python par ONNX Runtime et dans Chromium par ONNX Runtime Web.
- Résultat obtenu :
  - (Mahé) Premier résultat identique au calcul exact, dans le navigateur : q8 91,8 % (112,8 Mio), uint8 90,8 %, int8 85,8 %, fp16 99,9 % (224,4 Mio), fp32 100 % (448,5 Mio) (notebook 02, section 8).
- Temps gagné ou perdu, s'il peut être estimé :

## Qualités observées
- (Mahé) En fp32, le même modèle donne exactement les mêmes vecteurs en Python et dans le navigateur (cosinus 1).

## Défauts et limites observés
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas :
  - (Mahé) Un critère qui a échoué : la première version du notebook 02 exigeait un cosinus d'au moins 0,9999 entre le q8 du navigateur et celui de Python ; le minimum mesuré valait 0,9942. ONNX Runtime Web n'exécute pas le modèle quantifié comme ONNX Runtime en Python. Le critère a été remplacé par une mesure sur le classement, décidée avant de mesurer (notebook 02, section 8).

## Comparaison
- Méthode ou outil utilisé auparavant :
- Différences observées :
- Cas où l'ancienne méthode reste préférable :

## Décision
(Mahé) Adopté, à travers Transformers.js dans le navigateur.
- Motif : (Mahé) le format ONNX est celui que le navigateur sait exécuter ; le q8 est servi pour son poids, et son effet sur la qualité est testé au notebook 03 (famille F3).

## À retenir pour le rapport
- Apport : (Mahé) un même fichier de modèle, exécuté en Python et dans le navigateur.
- Principale limite : (Mahé) un modèle quantifié ne se comporte pas de la même façon d'un environnement d'exécution à l'autre.
- Ce que la documentation ne dit pas : (Mahé) l'écart entre le q8 de Python et celui du navigateur ; il faut mesurer là où le modèle sera servi.

## Preuves
- Pull request #40 : parité ONNX fp32 et PyTorch, critère de parité q8 échoué puis diagnostiqué (notebook 02, section 8).
- Ticket #49 : export et quantification de l'encodeur ajusté (`scripts/adaptation/06_exporter_onnx.py`).
