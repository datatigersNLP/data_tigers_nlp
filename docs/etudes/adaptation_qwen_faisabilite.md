# Adaptation du volet B : faisabilité mesurée sur Mac

**Équipe** Data Tigers  
**Ticket** #107, étape 1 (faisabilité), alternative sur Mac  
**Mesure** Mahé BEGNIS, le 23 octobre 2026  
**Statut** essai de faisabilité. Aucun entraînement utile n'a été fait : les données sont factices et la réponse apprise est une phrase fixe. Seuls la mémoire et le temps sont mesurés.

---

## 1. Question posée

Un ajustement fin par LoRA de `Qwen2.5-7B-Instruct` quantifié en 4 bits tient-il sur le MacBook de Mahé, avec la longueur de contexte réelle de la chaîne RAG (#85) ? À quelle vitesse ?

La mesure sur le Legion (GPU NVIDIA, 8 Gio de VRAM), qui sert les essais du volet B, reste à faire. C'est l'autre branche de l'étape 1 de #107.

## 2. Montage

| Élément | Valeur |
|---|---|
| Machine | MacBook, Apple M4 Pro, 24 Gio de mémoire unifiée, macOS 26.6.2 |
| Bibliothèques | `mlx` 0.32.4, `mlx-metal` 0.32.4, `mlx-lm` 0.32.2, `transformers` 5.20.2 (`scripts/adaptation_qwen/requirements.txt`) |
| Modèle | `mlx-community/Qwen2.5-7B-Instruct-4bit`, révision `c26a38f6`, 4 bits par groupes de 64, 28 couches, 4,0 Gio, empreinte du fichier de poids identique à celle publiée (`86110f36…`) |
| Données | 24 exemples d'entraînement et 4 de validation, au format exact du contexte de la #85 (sa fonction `construire_contexte`, consigne `rag-b1-v1`, 5 passages réels tirés au hasard, graine 20261023) ; de 1 115 à 2 542 tokens, médiane 1 746, à comparer aux 2 317 et 1 822 tokens des essais Q036 et Q003 |
| Réponse | phrase fixe citant `[P1]` ; c'est une donnée factice, pas une donnée d'entraînement |
| Réglages | LoRA de rang 8, lots de 1, longueur maximale 3 072, point de contrôle des gradients, prompt masqué dans la perte, taux d'apprentissage 1e-5, graine 20261023 |
| Scripts | `scripts/adaptation_qwen/construire_jeu_faisabilite.py`, `scripts/adaptation_qwen/mesurer_faisabilite.py` |

**Mesure de la mémoire.** C'est le pic de mémoire du GPU, relevé dans le même processus par `mx.get_peak_memory()`. La taille résidente du processus ne compte pas toute la mémoire allouée par Metal et sous-estime donc l'usage réel.

**Mesure du temps.** Chaque configuration est lancée avec 6 puis 12 itérations. La différence de durée, divisée par 6, donne le temps d'une itération, sans les coûts fixes : chargement du modèle et deux passes de validation.

## 3. Résultats

| LoRA appliqué à | Paramètres entraînés | Pic de mémoire GPU | Temps par itération | Coûts fixes |
|---|---|---|---|---|
| 16 couches (réglage par défaut) | 11,5 millions (0,15 %) | 7,14 Gio | 10,5 s | 25 s |
| 28 couches (toutes) | 20,2 millions (0,27 %) | 7,56 Gio | 14,3 s | 30 s |

Durées brutes : 16 couches, 88,2 s pour 6 itérations et 151,4 s pour 12 ; 28 couches, 115,2 s et 200,9 s. Les deux entraînements ont produit leur adaptateur (44,0 Mio pour 16 couches) sans erreur.

## 4. Lecture

- **Faisable sur ce Mac.** Le pic de 7,1 à 7,6 Gio laisse une large marge sous les 24 Gio.
- **Durée d'une époque.** Elle est d'environ 1 h 30 pour 500 exemples sur 16 couches, à ce rythme d'une itération de 10,5 s pour des contextes de 1 750 tokens environ. C'est une extrapolation linéaire, à vérifier sur le vrai jeu.
- **Legion.** Ces 7,1 Gio sont mesurés avec MLX sur Mac. Sur le Legion, avec une autre bibliothèque (PEFT et bitsandbytes, par exemple), la consommation diffère. Elle doit être mesurée là-bas, car 8 Gio de VRAM laissent peu de marge.
- **Ce que l'essai ne dit pas.** Rien sur la qualité. La perte qui tombe vers 0,04 en dix itérations montre seulement que le modèle apprend par cœur la phrase fixe.
- **Écart de quantification à traiter.** L'adaptateur est entraîné sur le 4 bits de MLX, alors que le volet B sert un GGUF Q4_K_M dans Ollama. Il faut choisir et mesurer l'une des deux voies :
  - fusion de l'adaptateur dans le modèle en 16 bits, conversion en GGUF, puis quantification Q4_K_M ;
  - adaptateur chargé par Ollama, avec la directive `ADAPTER` du Modelfile.

## 5. Suite proposée dans #107

1. Mesurer la même configuration sur le Legion (Jibril).
2. Choisir la machine d'entraînement, et garder une seule machine de mesure, comme le demande le protocole de #52 (PR #108).
3. Préparer les vraies données, avec séparation par fiche vérifiée par script, avant tout entraînement utile.

## 6. Reproduire

```bash
python3.12 -m venv data/volet_b/venv_mlx
data/volet_b/venv_mlx/bin/pip install -r scripts/adaptation_qwen/requirements.txt
# modèle à la révision figée, dans data/ (non versionné)
data/volet_b/venv_mlx/bin/python -I -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/Qwen2.5-7B-Instruct-4bit', revision='c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed', local_dir='data/volet_b/qwen25-7b-instruct-4bit-mlx')"
# jeu factice, au format de la #85 (scripts/rag doit être présent)
data/volet_b/venv_mlx/bin/python -I scripts/adaptation_qwen/construire_jeu_faisabilite.py scripts/rag front/public/index/passages_m2.json data/volet_b/essai_faisabilite
# mesure : nombre de couches, nombre d'itérations, dossier de l'adaptateur
data/volet_b/venv_mlx/bin/python -I scripts/adaptation_qwen/mesurer_faisabilite.py 16 6 data/volet_b/essai_faisabilite/mesure_16_6
```
