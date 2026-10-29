# QLoRA sur le Legion : résultat du 26 octobre 2026

**Exécution** Jibril BENSALEM, Windows 11, RTX 5070 Laptop 8 Gio  
**Ticket** #107, étape 1 ; script de la PR #118 au commit `b8a74f4`  
**Statut** essai factice terminé sur 16 couches ; critère de marge mémoire non satisfait. Proposition : retenir le Mac pour l'entraînement, à valider par l'équipe.

## Source et traçabilité

Jibril a transmis les 14 lignes de progression et la ligne finale `MESURE`.
La copie structurée est conservée dans
[`faisabilite_legion_20261026.json`](faisabilite_legion_20261026.json).
Ce n'est pas le fichier complet `mesure_16.json` : les pertes, les normes des
gradients et les durées non arrondies de chaque pas n'ont pas été reçues.
Les agrégats ci-dessous sont ceux de la ligne `MESURE`.

Les empreintes du modèle, des passages et des 28 exemples sont celles de la
préparation. L'empreinte du script exécuté correspond exactement au fichier
du commit `b8a74f4` avec des fins de ligne CRLF sous Windows. Il n'y a pas de
différence de code : la version LF a pour SHA-256
`be694c43320bb3475780934447a768b44c929f6f753caf6f2594176f6d819d04`.
L'horodatage `date_utc` est celui de l'initialisation du rapport, pas de la fin.

## Mesures retenues

Montage : Qwen2.5-7B-Instruct, NF4 avec double quantification, calcul BF16,
LoRA de rang 8 sur les 16 dernières couches, 11 534 336 paramètres entraînés.
Deux échauffements puis douze pas mesurés ; six exemples répétés deux fois,
de 1 115 à 2 542 tokens. Aucun adaptateur n'a été sauvegardé.

| Indicateur | Valeur |
|---|---|
| Mémoire physique annoncée par CUDA | 7,960 Gio (8 546 484 224 octets) |
| Mémoire libre avant chargement | 6,849 Gio |
| Pic alloué aux tenseurs par PyTorch | 9,168 Gio |
| Pic réservé par l'allocateur PyTorch | 10,352 Gio |
| Mémoire libre en fin d'essai | 0 octet |
| Temps moyen d'un pas, hors échauffements | 273,887 s, soit 4 min 34 s |
| Temps médian d'un pas | 260,224 s |
| Moyenne des six derniers pas | 272,017 s |
| Douze pas mesurés | 54 min 47 s environ |

`chargement_s = 1 137,939 s` inclut la préparation et peut inclure le premier
téléchargement des poids. Ce n'est pas une mesure isolée du chargement à chaud.
La durée reste élevée au second cycle : il ne s'agit pas du seul échauffement.

Versions : Python 3.12.15, PyTorch 2.11.0+cu128, CUDA 12.8, Transformers 5.20.2,
PEFT 0.21.2, Accelerate 1.15.0, bitsandbytes 0.50.2 et huggingface-hub 2.3.0.
Le pilote relevé avant l'essai par Jibril était NVIDIA 596.36, modèle WDDM.

## Interprétation et limites

**Une exécution terminée ne prouve pas que le montage tient en VRAM.** Le pic
alloué dépasse de 1,209 Gio la mémoire physique annoncée ; la mémoire libre
termine à zéro. Le montage ne satisfait donc pas la marge de 10 % proposée
dans #107 pour le choix de machine.

**Hypothèse forte, pas mesure directe : débordement vers la RAM système.**
NVIDIA documente un mécanisme de repli vers la mémoire partagée sous Windows,
qui permet de continuer au prix d'un ralentissement. Il est cohérent avec ces
chiffres, mais ni la mémoire partagée pendant l'essai ni la politique du
pilote n'ont été enregistrées. `offload_cpu=false` décrit l'absence de déport
explicite des paramètres par le script ; cela n'interdit pas la gestion
mémoire du pilote et de Windows. Les compteurs PyTorch ne décrivent pas à eux
seuls la résidence physique de tous les octets en VRAM.

Le script conserve une portée de diagnostic : pas de calcul de qualité, pas
de modèle adapté utile et pas de conclusion sur toute autre configuration
possible du Legion. Le mode d'alimentation et la télémétrie pendant le calcul
n'ont pas été enregistrés non plus.

## Comparaison pour le choix de machine

| Montage, LoRA sur 16 couches | Pic publié | Temps par pas publié |
|---|---|---|
| Mac M4 Pro, 24 Gio, MLX (#109) | 7,14 Gio, compteur Metal | 10,5 s |
| Legion, 8 Gio, NF4/BF16 (#118) | 9,168 Gio alloués, compteur PyTorch | 273,887 s |

Les montages diffèrent : quantification, précisions et noyaux, parcours des
exemples, instruments mémoire et méthode de chronométrage. Le rapport des
temps, environ 26, est descriptif de ces essais ; ce n'est pas un classement
intrinsèque des deux GPU. La marge mémoire du Mac était large dans #109 ;
elle n'est pas obtenue ici.

**Proposition pour le Weekly 7 : retenir le Mac pour l'entraînement.** La
conversion, le service Ollama et les mesures du volet B restent prévus sur le
Legion selon #107 et le protocole. Ne pas lancer les 28 couches dans l'état
actuel : le cas à 16 couches suffit déjà à écarter ce montage pour le critère
de marge. Cette proposition ne clôt pas #107 et ne vaut pas décision d'équipe.

## Sources techniques

- [NVIDIA : System Memory Fallback](https://nvidia.custhelp.com/app/answers/detail/a_id/5490/~/system-memory-fallback-for-stable-diffusion).
- [PyTorch : maximum alloué aux tenseurs](https://docs.pytorch.org/docs/2.11/generated/torch.cuda.memory.max_memory_allocated.html).
- [PyTorch : maximum réservé par l'allocateur](https://docs.pytorch.org/docs/2.11/generated/torch.cuda.memory.max_memory_reserved.html).
- [Essai Mac, PR #109](https://github.com/datatigersNLP/data_tigers_nlp/pull/109).
