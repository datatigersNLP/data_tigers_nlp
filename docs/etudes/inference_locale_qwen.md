# Première inférence locale — Qwen2.5-7B-Instruct Q4_K_M

**Issue :** #31 · **Date des essais :** 27 septembre 2026

**Responsable des essais :** Jibril Bensalem · **Soutien :** Remy Rayane

**Statut :** première inférence locale validée sur la machine de Jibril.

## 1. Objectif

Vérifier qu'un modèle Qwen2.5-7B-Instruct au format GGUF, quantifié en Q4_K_M, peut être chargé et produire une réponse complète en français sur la machine de Jibril. Relever les premiers temps d'exécution et observations de ressources, puis fournir une procédure reproductible.

## 2. Périmètre

Cet essai valide uniquement l'exécution locale du modèle. Il ne teste ni le corpus, ni le RAG, ni les citations, ni l'abstention, ni l'adaptation du modèle, ni la comparaison avec Mistral, ni l'évaluation finale de l'assistant réglementaire.

La réponse produite sert de preuve technique d'inférence. Sa justesse juridique n'a pas fait l'objet d'une évaluation.

## 3. Environnement réellement relevé

| Élément | Observation |
|---|---|
| Machine | Lenovo ; Windows remonte le modèle `83NN` |
| Référence commerciale communiquée | `83NN0021FR`, non confirmée par le relevé Windows |
| Système | Windows 11 Famille, 64 bits, version 10.0.26200, build 26200 |
| PowerShell | 5.1.26100.9444 |
| Processeur | Intel Core i9-14900HX ; 24 cœurs, 32 processeurs logiques |
| RAM détectée | 31,73 Gio |
| GPU | NVIDIA GeForce RTX 5070 Laptop GPU |
| VRAM signalée par `nvidia-smi` | 8 151 Mio |
| Pilote NVIDIA | 596.36 |
| Ollama | 0.34.4 ; API locale répondant sur `http://127.0.0.1:11434` |
| Espace libre sur `C:` avant téléchargement du modèle | 380,06 Gio |
| Espace libre sur `C:` après téléchargement et import | 368,84 Gio |

Le relevé matériel précède les essais ; les valeurs de RAM et de VRAM disponibles varient selon les autres programmes ouverts. Le chiffre `CUDA Version: 13.2` affiché par `nvidia-smi` décrit la compatibilité annoncée par le pilote et ne prouve pas l'installation d'un kit CUDA distinct.

## 4. Modèle, provenance et intégrité

- **Source officielle :** [Qwen/Qwen2.5-7B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF).
- **Tag initialement prévu :** `hf.co/Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M`.
- **Format et quantification confirmés par l'API locale :** GGUF, `Q4_K_M` ; famille `qwen2`.
- **Nom après import local :** `qwen2.5-7b-instruct:q4_k_m-local`.
- **Taille indiquée par l'API Ollama :** 4 683 073 767 octets, soit 4,36 Gio.
- **Digest du modèle local :** `6ec54444a8511aae6c2116b172eb3685d1416c523bfee0252ca33c7e55c481e4`.

Le GGUF officiel est réparti en deux fragments. Leurs empreintes SHA-256 locales ont été comparées à celles affichées par Qwen :

| Fichier | Taille locale observée | SHA-256 vérifié |
|---|---:|---|
| `qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf` | 3,72 Gio | `dfce12e3862a5283ccfb88221b48480e58745165de856439950d0f22590580db` |
| `qwen2.5-7b-instruct-q4_k_m-00002-of-00002.gguf` | 657,91 Mio | `539cf93f78e887edea1c04e2d7d8cdaca9d01dae9c9025bcb8accbe29df3d72a` |

Le digest du modèle local et les SHA-256 des fragments sont des identifiants distincts. Les fichiers GGUF ont été placés dans `Téléchargements`, hors du dépôt Git ; Ollama conserve sa copie dans son stockage local.

## 5. Anomalie et méthode d'import

La commande `ollama pull hf.co/Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M` a échoué avant le téléchargement des poids avec une erreur HTTP 400 : Ollama ne prend pas en charge le *pull* de ce tag GGUF découpé via son registre.

Les deux fragments `Q4_K_M` ont alors été téléchargés depuis le dépôt officiel Qwen, vérifiés par SHA-256 et importés avec `ollama create`. Le `Modelfile`, conservé hors du dépôt, contient :

    FROM ./qwen2.5-7b-instruct-q4_k_m-*.gguf

L'import a indiqué les deux empreintes attendues, puis `writing manifest` et `success`. Le nom local diffère donc du tag Hugging Face prévu initialement ; le modèle et la quantification restent ceux demandés.

Temps de téléchargement passif observé dans les sorties de curl.exe : 1 min 01 s pour le second fragment et 5 min 54 s pour le premier, soit 6 min 55 s de transfert au total. Cette durée est suivie séparément du travail actif.

Sources de la solution : [documentation d'import Ollama](https://docs.ollama.com/import) et [issue Ollama sur les GGUF découpés](https://github.com/ollama/ollama/issues/5245).

## 6. Protocole et paramètres

Les deux tests principaux ont appelé `POST http://127.0.0.1:11434/api/generate` depuis PowerShell, avec `stream: false`. Le premier a été lancé après vérification de l'absence du modèle dans `/api/ps` ; le second après confirmation qu'il était encore chargé.

**Prompt identique pour les deux tests :**

> Explique en français, en cinq phrases maximum, la différence entre un contrat à durée déterminée et un contrat à durée indéterminée. Si une information te manque, indique-le.

| Paramètre | Valeur |
|---|---|
| Modèle local | `qwen2.5-7b-instruct:q4_k_m-local` |
| `temperature` | `0.2` |
| `num_predict` | `200` |
| `num_ctx` | `4096` |
| `keep_alive` | `30m` |
| `stream` | `false` |

Les durées et nombres de tokens ci-dessous proviennent de l'API Ollama. Le débit est calculé par `eval_count / (eval_duration / 1 000 000 000)` ; il mesure la génération des tokens de sortie, sans inclure le chargement.

## 7. Résultats des deux tests principaux

| Mesure | Premier appel, chargement inclus | Second appel, modèle déjà chargé |
|---|---:|---:|
| `total_duration` | 37,728 s | 1,940 s |
| `load_duration` | 19,133 s | 0,001 s |
| `prompt_eval_duration` | Non relevé dans la sortie conservée | 0,189 s |
| `prompt_eval_count` | Non relevé dans la sortie conservée | 71 |
| `eval_duration` | 2,945 s | 1,732 s |
| `eval_count` | 138 tokens | 116 tokens |
| Débit calculé | 46,86 tokens/s | 66,99 tokens/s |
| `done_reason` | `stop` | `stop` |

**Réponse du premier appel :**

> Un contrat à durée déterminée (CDD) est un accord entre un employeur et un employé qui prévoit une fin précise, généralement fixée par une date ou un événement spécifique. En revanche, un contrat à durée indéterminée (CDI) n'a pas de date de fin prévue et peut être maintenu indéfiniment, sauf si une des parties le rompt conformément aux dispositions légales. Les CDD sont souvent utilisés pour des emplois temporaires ou des missions spécifiques, tandis que les CDI sont plus courants pour des emplois permanents.

**Réponse du second appel :**

> Un contrat à durée déterminée (CDD) est un contrat qui s'achève à une date précise, tandis qu'un contrat à durée indéterminée (CDI) est une relation de travail sans date de fin prévue. Les CDD sont généralement utilisés pour des missions spécifiques ou des périodes de temps limitées, contrairement aux CDI qui offrent une stabilité plus long terme. Les CDD peuvent être renouvelés, mais le CDI offre une sécurité d'emploi plus grande.

Les deux réponses sont complètes et contiennent trois phrases. Elles n'ont pas le même nombre de tokens : le changement de débit ne constitue pas, à lui seul, une comparaison de performances sur des sorties identiques. Le temps total du premier appel dépasse la somme des seuls temps de chargement et de génération affichés ; les autres phases n'ont pas toutes été relevées.

## 8. Mémoire et utilisation observées

| Relevé | Observation |
|---|---|
| VRAM utilisée avant le premier appel | 1 036 Mio ; activité GPU instantanée 7 % |
| VRAM utilisée après le premier appel | 5 694 Mio ; activité GPU instantanée 73 % |
| Différence de VRAM observée | Environ 4 658 Mio ; ne représente pas une mesure isolée du modèle |
| Après le second appel | 5 694 Mio utilisés ; activité GPU instantanée 97 % |
| `ollama ps` après les appels | `100% GPU`, contexte `4096` |
| RAM disponible, premier appel | 17,39 Gio avant ; 16,78 Gio après |
| RAM disponible, second appel | 16,66 Gio avant et après, à la précision affichée |
| Relevé ultérieur | 16,67 Gio de RAM disponibles ; CPU à 5 % |
| Processus Ollama lors du relevé ultérieur | `ollama` : 101,66 Mio de mémoire physique ; `ollama app` : 126,56 Mio |

Les pourcentages CPU/GPU et les mesures de mémoire sont des instantanés, et non des moyennes pendant la génération. Le total des deux processus affichés ne mesure pas à lui seul toute la mémoire utilisée par l'inférence. Aucun déport du modèle sur CPU n'a été indiqué par `ollama ps` lors de ces essais.

## 9. Contrôle du script versionné

Le script `scripts/inference/test_qwen.ps1` a été exécuté une fois en contrôle après les deux tests principaux. Il a retrouvé Ollama 0.34.4, le digest et la quantification `Q4_K_M`, constaté que le modèle était déjà chargé, puis produit une réponse complète avec `done_reason: stop`. Cette exécution distincte a donné 1,512 s au total, 0,001 s de chargement, 1,246 s de génération et 85 tokens à 68,20 tokens/s.

La politique d'exécution PowerShell de la machine bloquait l'appel direct au fichier `.ps1`. Le contrôle a réussi en lançant un processus PowerShell avec `-ExecutionPolicy RemoteSigned`, sans modifier durablement la politique Windows.

## 10. Reproduction sur une autre machine Windows

1. Vérifier le matériel, `nvidia-smi`, l'espace libre, puis installer Ollama depuis [la page officielle Windows](https://ollama.com/download/windows). Vérifier `ollama --version` et `http://127.0.0.1:11434/api/version`.
2. Créer un dossier de travail **hors du dépôt Git** et télécharger depuis [Qwen](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/tree/main) les deux fichiers `qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf` et `qwen2.5-7b-instruct-q4_k_m-00002-of-00002.gguf`. Conserver leurs noms originaux.
3. Vérifier chacun avec `Get-FileHash -Algorithm SHA256` et comparer aux empreintes du tableau ci-dessus. Si une empreinte diffère, ne pas importer le modèle.
4. Dans ce dossier de travail, créer un fichier `Modelfile` contenant la ligne `FROM ./qwen2.5-7b-instruct-q4_k_m-*.gguf`, puis lancer :

       ollama create qwen2.5-7b-instruct:q4_k_m-local -f .\Modelfile
       ollama list
       ollama ps

5. Depuis la racine du dépôt, exécuter le script ci-dessous une première fois lorsque `ollama ps` ne montre pas le modèle, puis une seconde fois pendant qu'il reste chargé :

       powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File .\scripts\inference\test_qwen.ps1
       powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File .\scripts\inference\test_qwen.ps1

6. Comparer les réponses et les mesures réellement obtenues. Utiliser `nvidia-smi`, `ollama ps` et les outils Windows pour observer les ressources. Ne jamais copier les fichiers GGUF ou les caches dans le dépôt Git.

Le nom local est celui retenu pour ce script. Si un autre nom est choisi lors de l'import, passer ce nom au paramètre `-Model` du script.

## 11. Limites et suite

Il s'agit de deux appels principaux avec un prompt court, plus un contrôle du script : cet échantillon ne constitue ni un benchmark statistique, ni une validation du futur assistant réglementaire. Le temps avant le premier token n'a pas été mesuré avec `stream: false`. L'activité CPU pendant la génération et une consommation de RAM isolée du modèle n'ont pas été mesurées précisément.

**Machine de démonstration orale :** Mahé prépare sa propre machine séparément. Aucun test ni aucune performance de sa machine ne sont rapportés ici. Avant l'oral, il faudra y vérifier l'installation, le chargement, la réponse, les ressources et la reproduction du script ; ses performances ne doivent pas être supposées identiques à celles du Legion de Jibril.

## 12. Conclusion

La première inférence locale de Qwen2.5-7B-Instruct GGUF `Q4_K_M` est **validée sur la machine de Jibril** : modèle chargé, deux réponses françaises complètes, fin normale, inférence via l'API locale et chargement signalé à 100 % sur GPU. Le téléchargement direct par tag Hugging Face reste une anomalie de procédure, contournée par l'import vérifié des deux fragments officiels.

Cette validation technique ne clôt pas à elle seule l'issue #31 : le résultat doit encore être relu et présenté à l'équipe selon ses critères de validation.
