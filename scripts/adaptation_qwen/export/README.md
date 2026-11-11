# Chaîne d'export de l'adaptateur (#140)

L'adaptateur LoRA, entraîné par mlx-lm sur la base MLX 4 bits, est fusionné dans les poids officiels bf16 de Qwen, converti en GGUF f16, vérifié tenseur par tenseur, puis quantifié en Q4_K_M. Le témoin T passe par la même conversion, sans adaptateur. Toutes les commandes tournent sur le Mac de Mahé (amendement M1 au protocole 06, #52).

## Pourquoi les poids bf16 plutôt que la base MLX déquantifiée

Une simulation sur une matrice gaussienne, avec Q4_K reproduit d'après llama.cpp, compare les deux voies :
* **fusion dans les poids bf16** : l'adaptation survit en moyenne à la requantification (gain de 0,975 à 0,999) ;
* **fusion dans la base MLX déquantifiée** : les poids retombent sur l'ancienne grille, et il n'en reste que 0,47 à 0,62.

Dans les deux cas, la requantification ajoute un bruit d'arrondi plus grand que l'adaptation, à l'échelle d'une matrice. D'où le contrôle de requantification. Par ailleurs, `--export-gguf` de mlx-lm 0.32.2 refuse l'architecture `qwen2`.

## Fichiers

* `fusionner.py` : W + 20·(`lora_a`·`lora_b`)ᵀ, calculé en fp32 et écrit en f16, dans des fragments `model-zz-lora-*` lus après les fragments d'origine. Le script rend aussi ρ = ‖ΔW‖ / ‖W‖, matrice par matrice.
* `verifier_gguf.py` : égalité exacte de chaque tenseur du GGUF avec sa source. Sans dossier fusionné, il sert de contrôle négatif.
* `controle_requantification.py` : la règle écrite sur le #140 avant l'exécution, appliquée aux 20 exemples de validation.
* `test_export.py` : 10 tests sur des tenseurs et des exemples factices. Cinq erreurs introduites une à une dans une copie (formule, échelle, seuil, abstention, lecture de la sortie) font chacune échouer au moins un test.

**Liens symboliques** : `fusionner.py` lie les fragments d'origine au lieu de les copier. Windows refuse ces liens sans mode développeur ni droits d'administrateur (`WinError 1314`, relevé par Remy sur la #147). La fusion ne peut donc pas tourner sur un tel poste, et elle n'y est pas prévue : elle se fait sur le Mac (amendement M1, #52).
* Sur un tel poste, `test_export.py` saute le test de la fusion et le test de garde, et les 8 autres tests tournent normalement.
* Ailleurs, le test de garde échoue si les liens sont refusés. Le test de la fusion ne peut donc jamais être sauté sans bruit là où la fusion tourne : une aide qui répondrait toujours « refusé » est détectée.

## Outils, vérifiés le 9 novembre

* **Poids** : `Qwen/Qwen2.5-7B-Instruct`, révision `a09a3545`. Les 12 fichiers sont contrôlés contre l'API de Hugging Face.
* **llama.cpp v0.7.0**, commit `620d2225`. Compilé sans serveur, sans interface web et sans HTTPS (`-DLLAMA_BUILD_SERVER=OFF -DLLAMA_USE_PREBUILT_UI=OFF -DLLAMA_OPENSSL=OFF`), car la cible du serveur télécharge une interface dont la version n'est pas figée. Seuls `llama-quantize` et `llama-completion` sont gardés.
* **Environnement de conversion** : venues de PyPI seul, avec torch 2.11.0, transformers 4.57.6, numpy 2.2.6, et `gguf` installé depuis les sources du tag.
* **Ollama 0.40.13**, la version épinglée : `ollama-darwin.tgz`, SHA-256 `bae29252…`, signature Apple vérifiée, sans mise à jour automatique.

## Témoin T, déjà produit le 9 novembre

`temoin-q4_k_m.gguf` : 4 683 073 696 octets, SHA-256 `5197d4a183629a34…`. Ses 339 tenseurs sont vérifiés. Il diffère du fichier officiel de la #31 par le choix des couches en Q6_K : `attn_v` et `ffn_down` sont en Q6_K sur les couches 0 à 2, 5, 8, 11, 14, 17, 20, 23 et 24 à 27, contre 9 au lieu de 8 pour `attn_v`, et 7 et 12 au lieu de 8 et 11 pour `ffn_down`, dans le fichier officiel.

## Procédure pour le modèle adapté

Avec `E=~/NLP2_local/volet_b/export`, `L=~/NLP2_local/outils/llama.cpp-v0.7.0` et `P=~/NLP2_local/venv_llamacpp/bin/python` :

```
$P -I scripts/adaptation_qwen/export/fusionner.py --base $E/qwen25-7b-instruct-bf16 --adaptateur data/volet_b/adaptateurs/lora-v2b --sortie $E/lora-v2b-fusionne
(cd $L && $P convert_hf_to_gguf.py $E/lora-v2b-fusionne --outtype f16 --outfile $E/lora-v2b-f16.gguf)
$P -I scripts/adaptation_qwen/export/verifier_gguf.py $E/lora-v2b-f16.gguf $E/qwen25-7b-instruct-bf16 $E/lora-v2b-fusionne
$P -I scripts/adaptation_qwen/export/verifier_gguf.py $E/lora-v2b-f16.gguf $E/qwen25-7b-instruct-bf16   # contrôle négatif : 112 écarts attendus
$L/build/bin/llama-quantize $E/lora-v2b-f16.gguf $E/lora-v2b-q4_k_m.gguf Q4_K_M
shasum -a 256 $E/lora-v2b-q4_k_m.gguf $E/temoin-q4_k_m.gguf
~/NLP2_local/volet_b/venv_mlx/bin/python scripts/adaptation_qwen/export/controle_requantification.py --lot v2b-20261107 --adaptateur lora-v2b --gguf-temoin $E/temoin-q4_k_m.gguf --gguf-adapte $E/lora-v2b-q4_k_m.gguf --llama-completion $L/build/bin/llama-completion
```

Le GGUF f16 et le dossier fusionné sont supprimés dès que la vérification et la quantification sont faites. Au pic, ils occupent environ 21 Gio.
* **Avant de supprimer le dossier fusionné, copier son `rapport_fusion.json`** : c'est le ρ par matrice que la règle du #140 fait rapporter. Le 11/11, il a été supprimé avec le dossier, puis régénéré par la même fusion, qui est déterministe.
* Le dossier fusionné ne sert qu'à la vérification. Le supprimer avant la quantification libère environ 7 Gio : c'est ce qui a été fait le 11/11, faute de place.

## Import dans Ollama

Pour chacun des deux modèles :
* écrire un `Modelfile` réduit à la ligne `FROM ./<fichier>.gguf`, comme pour la #31 ;
* lancer `ollama create`, le service écoutant sur 127.0.0.1 et les modèles étant stockés hors iCloud ;
* publier les digests sur le #52 avant toute mesure.
