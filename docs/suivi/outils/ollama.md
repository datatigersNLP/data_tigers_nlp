# Ollama

## Identification
- Version : variable selon les membres, voir « Versions utilisées »
- Nature : application d'exécution locale de modèles de langage
- Assignés : Jibril (#31, PR #41), Rémy (#49), Maïmouna (#51), Mahé (#52)
- Coordination : Jibril
- Période d'utilisation : (Remy) du 3 au 6 octobre 2026 pour la génération locale dans #49 (PR #63) ; audits documentaires ultérieurs sur #107/#108 et #52
- Besoin du projet auquel il répond : faire tourner le modèle de langage du volet B en local, sans service externe.

## Versions utilisées
Chaque membre tient sa propre ligne à jour.

| Membre | Version | Système | Remarque |
|---|---|---|---|
| Jibril | 0.34.4 | Windows | GPU NVIDIA, Qwen2.5-7B Q4_K_M (PR #41) |
| Rémy | 0.40.15 (non épinglée sur poste Windows 11) | Windows 11 | usage sous #49 (PR #63) : génération locale de paires sur `qwen2.5-7b-instruct:q4_k_m-local` ; mise à jour automatique constatée jusqu'en 0.40.15 sur ce poste (la version officielle épinglée par le protocole 06 pour #52 est **0.40.13**) |
| Maïmouna | 0.40.15 | Windows 11, ARM (Snapdragon X Plus), sans GPU NVIDIA | reproduction de la chaîne de la #85 (#51) : import des deux fragments GGUF officiels par `ollama create`, digest différent de celui de la #31 malgré des fragments identiques ; Q036 en 3 min 45 sur processeur seul |
| Mahé | non installé | macOS 27.0.1, arm64 | la mesure de #52 s'exécute sur le Legion ; la faisabilité de l'adaptation sur Mac passe par MLX (PR #109) |

## Mise en place
- Temps avant le premier résultat utile : (Remy) prise en main rapide via l'API HTTP locale (`http://127.0.0.1:11434`) en réutilisant le modèle `qwen2.5-7b-instruct:q4_k_m-local` créé lors du ticket #31 (`PR #41`).
- Installation et configuration : (Remy) instance Ollama sous Windows 11 ; sans verrouillage explicite des mises à jour automatiques, le démon a dérivé vers `0.40.15`, illustrant concrètement l'exigence d'épinglage à `0.40.13` du protocole 06 (#108).
- Prérequis découverts en chemin : (Remy) l'export local sans graine pseudo-aléatoire (`seed`) produit des tirages non reproductibles, imposant de hacher en SHA-256 tout jeu synthétique produit (`01_ajustement_encodeur_contrastif.md`, section 2.3).
- Difficultés non expliquées par la documentation :

## Usage réel
- Tâche réalisée, ticket ou pull request : (Remy) Ticket #49, PR #63 : script `scripts/adaptation/03_generer_paires_locales.py` générant des paires `(question, passage)` synthétiques en droit du travail sur corpus filtré.
- Commande, configuration ou scénario : (Remy) requêtes HTTP JSON vers `http://127.0.0.1:11434/api/generate` avec `qwen2.5-7b-instruct:q4_k_m-local`, suivies de filtres syntaxiques et d'un filtre anti-fuite Jaccard `< 0,40`.
- Résultat obtenu : (Remy) sur 110 passages échantillonnés issus de fiches hors évaluation, **109 paires valides** générées (`data/adaptation/train_paires.jsonl`, SHA-256 `2d377eb6...`).
- Temps gagné ou perdu, s'il peut être estimé :

## Qualités observées
- (Remy) API HTTP locale (`127.0.0.1:11434`) simple à appeler depuis Python sans dépendance cloud ni fuite des données du corpus (#49, PR #63).

## Défauts et limites observés
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas :
  - (Remy) Rejet de la directive `ADAPTER` (`errAdaptersUnsupported`) et contrainte d'export : confirmé lors des audits documentaires (#109, session 45 du journal, PR #120) suite au constat établi sur Ollama `v0.40.5` (#107, session 42). Ollama refuse de charger à chaud un adaptateur LoRA externe sur un GGUF quantifié, ce qui impose une fusion préalable dans les poids bf16 et une reconversion GGUF Q4_K_M avec contrôle d'un témoin T (chaîne implémentée par Mahé dans `#140`).
  - (Remy) Risque de dérive silencieuse de version : l'auto-mise à jour sous Windows 11 (poste observé en `0.40.15` au 10/11) contrevient aux protocoles figés si elle n'est pas désactivée explicitement (d'où la version **0.40.13** épinglée et documentée au protocole 06).

## Comparaison
- Méthode ou outil utilisé auparavant : (Remy) exécution manuelle de prompts ou scripts Hugging Face `transformers` directs sans serveur GGUF local.
- Différences observées : (Remy) Ollama simplifie l'inférence locale sur machine dotée d'une VRAM modeste grâce aux poids GGUF `Q4_K_M` (~4,36 Gio), mais masque les différences entre révisions mineures et n'accepte pas les adaptateurs LoRA externes.
- Cas où l'ancienne méthode reste préférable : (Remy) pendant l'entraînement et l'évaluation fine en Python/MLX (#109, PR #125), les bibliothèques natives restent indispensables.

## Décision
À compléter : adopté / conservé pour certains usages / abandonné / à réévaluer.
- Motif :

## À retenir pour le rapport
- Apport : (Remy) service local de `Qwen2.5-7B-Instruct` via une API HTTP stable sans recours à un serveur tiers.
- Principale limite : (Remy) refus des adaptateurs LoRA (`errAdaptersUnsupported`) nécessitant une fusion bf16 et une reconversion GGUF complète.
- Ce que la documentation ne dit pas : (Remy) le comportement non déterministe des mises à jour automatiques (dérive constatée vers `0.40.15` face au `0.40.13` épinglé) et le besoin d'empreinte SHA-256 pour authentifier une génération locale sans `seed`.

## Preuves
- Pull request #41 : première inférence locale de Qwen2.5-7B (`docs/etudes/inference_locale_qwen.md`, `scripts/inference/test_qwen.ps1`) ; échec du téléchargement direct (HTTP 400) contourné par `ollama create`.
- Ticket #49, PR #63 : génération de 109 paires d'entraînement avec Qwen local (`scripts/adaptation/03_generer_paires_locales.py`, `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md`).
- Protocole 06 (PR #108) et #52 : version officielle épinglée `0.40.13` ; session 42 (rejet `v0.40.5`) et session 45 (#120, journal d'usage IA).
