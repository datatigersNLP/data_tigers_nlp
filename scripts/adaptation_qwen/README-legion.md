# Faisabilité QLoRA sur le Legion (#107)

Préparation du 26 octobre 2026. **La mesure du 7B sur le Legion reste à exécuter.**
Jibril a confirmé le calcul BF16, puis le calcul et la rétropropagation NF4,
sur la RTX 5070 Laptop (8 Gio), avec Python 3.12.15 et les versions de
`requirements-legion.txt`. Les avertissements de comptage FLOP Triton et de
redirection des processus ne sont pas utilisés par ce benchmark.

## Ce qui est mesuré

- Qwen2.5-7B-Instruct officiel, révision figée dans le script, chargé en NF4
  avec double quantification, calcul BF16, entièrement sur CUDA.
- LoRA de rang 8 sur les sept projections des **16 dernières couches**, puis
  des **28 couches**. Alpha 160 donne un facteur alpha/r de 20, comme le
  `scale=20` de MLX-LM 0.32.2 ; dropout nul, Adam à 1e-5, lot de 1.
- Base gelée, normes FP32, embeddings et tête de sortie BF16, adaptateurs FP32.
  La préparation k-bit est explicite : elle évite la conversion temporaire des
  grands embeddings en FP32 sur les 8 Gio. Checkpointing non réentrant, sans
  `torch.compile`, sans FlashAttention externe ni déport de paramètres sur CPU.
- Les **28 exemples identiques** au tirage de #109 : même corpus vérifié par
  SHA-256, même graine, même constructeur de contexte de #85, cinq passages et
  réponse fixe. Empreinte des messages contrôlée par test. Le code est autonome
  en attendant la fusion de #85 et #109 ; il ne change pas le RAG.
- Prompt masqué. Seuls les logits qui prédisent la réponse sont matérialisés :
  sur un petit Qwen CPU, la perte **et les gradients LoRA** ont été comparés à
  ceux de la perte complète avec prompt masqué, et sont identiques à la
  tolérance numérique de PyTorch. Cela évite un gros tableau de logits inutile.
- Aucun exemple n'est tronqué ; limite de 3 072 tokens, comme #109. Le
  tokeniseur est celui de la même révision que les poids ; les longueurs sont
  enregistrées. Les 2 048 tokens évoqués dans le ticket ne doivent pas masquer
  le coût des exemples plus longs de l'essai Mac.

**Ce sont des données factices de coût.** Aucune annotation humaine n'est lue,
aucune qualité de réponse n'est évaluée et aucun poids ni adaptateur entraîné
n'est sauvegardé. Ne pas réutiliser ces exemples comme jeu d'adaptation validé.

## Exécuter sous PowerShell

Depuis le clone habituel, avec `.venv-qlora` déjà installé :

```powershell
git fetch origin feat/107-faisabilite-legion
git worktree add --detach ..\data_tigers_nlp-faisabilite-legion origin/feat/107-faisabilite-legion

# Décharger le modèle d'Ollama pour libérer la VRAM ; brancher le PC au secteur.
ollama stop qwen2.5-7b-instruct:q4_k_m-local

.\.venv-qlora\Scripts\python.exe ..\data_tigers_nlp-faisabilite-legion\scripts\adaptation_qwen\faisabilite_legion.py --couches 16 --sortie .\data\volet_b\faisabilite_legion\mesure_16.json

# Seulement après lecture du premier résultat ; processus neuf.
.\.venv-qlora\Scripts\python.exe ..\data_tigers_nlp-faisabilite-legion\scripts\adaptation_qwen\faisabilite_legion.py --couches 28 --sortie .\data\volet_b\faisabilite_legion\mesure_28.json
```

Le premier lancement télécharge environ 15 Go de poids Hugging Face dans le
cache. Le GGUF déjà importé dans Ollama ne remplace pas ces poids pour PEFT.
Le worktree conserve la branche habituelle du clone intacte. Si le dossier
de worktree ou une sortie existe, choisir un autre nom ; ne rien effacer pour
relancer. Les résultats et les caches ne sont pas versionnés.

## Lire le résultat

Deux échauffements, dont l'exemple le plus long, précèdent douze pas mesurés.
Six exemples répartis sur la plage des longueurs sont parcourus deux fois.
Chaque durée inclut calcul, rétropropagation, contrôle des gradients et pas
d'Adam, avec synchronisation CUDA, sans chargement ni écriture JSON.

Le JSON conserve les versions, la configuration, les empreintes, les longueurs,
les durées individuelles, les pics CUDA alloués/réservés **depuis avant le
chargement**, et la mémoire libre au départ et à la fin. Il refuse les valeurs
non finies et conserve aussi une trace d'erreur ou d'épuisement mémoire.
Une sortie existante est refusée pour préserver les essais.

Le temps Mac de #109 est déduit de deux durées globales (6 puis 12 itérations).
Ici les pas sont chronométrés directement après échauffement. Les messages
sont identiques, mais les noyaux, la quantification, les précisions des
adaptateurs, le parcours des exemples et les instruments mémoire diffèrent :
il s'agit de comparer deux montages utilisables, pas de départager les GPU seuls.

Ne pas déduire la marge de 10 % du seul pic alloué : le cache CUDA, le pilote
et l'affichage consomment aussi de la VRAM. Sous WDDM, vérifier aussi dans le
Gestionnaire des tâches qu'une éventuelle mémoire GPU partagée ne remplace pas
la VRAM pendant l'essai. Une exécution terminée n'est pas à elle seule une
décision de machine ; rapporter les données dans #107 avant cette décision.

## Vérifications de préparation

```powershell
.\.venv-qlora\Scripts\python.exe -m unittest discover -s ..\data_tigers_nlp-faisabilite-legion\scripts\adaptation_qwen -p test_faisabilite_legion.py -v
```

Sept tests exécutés sur CPU lors de la préparation, dont un petit Qwen avec
checkpointing et LoRA. Cela ne remplace pas la mesure réelle du 7B en NF4 sur
le Legion. Relecture technique du script attendue par Mahé (D5) ; branche en
brouillon tant que cette relecture et les mesures ne sont pas consignées.

## Sources

- [Essai Mac, PR #109](https://github.com/datatigersNLP/data_tigers_nlp/pull/109),
  scripts au commit `a0bceb7203113dc66551f3a23629a5a0fd4d7133`.
- [Contexte RAG, PR #85](https://github.com/datatigersNLP/data_tigers_nlp/pull/85),
  fonction au commit `df91b85981607c722f191f0205fc3072f0a62b8c`.
- [PEFT : LoRA et sélection des couches](https://huggingface.co/docs/peft/v0.21.0/en/package_reference/lora).
- [Transformers : bitsandbytes et NF4](https://huggingface.co/docs/transformers/v5.20.2/en/quantization/bitsandbytes).
