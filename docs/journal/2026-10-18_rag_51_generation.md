# Usage de l'IA — #51, génération locale et citations, 18 octobre 2026

**Membre :** Jibril BENSALEM. **Outil :** ChatGPT / Codex, avec connecteur GitHub.

## Configuration fournie par Jibril

La sortie de ses requêtes locales `/api/show` et `/api/version` indique Ollama 0.40.5, Qwen2 GGUF 7.6B Q4_K_M,
parent `qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf`, gabarit Jinja Qwen avec rôles et marqueurs ChatML,
et `parameters: null`. Cette version est distincte de celle de #31 ; aucune performance ancienne n'est transposée.

## Travail assisté

Ajout d'un module `scripts/rag/generation.py` pour garder le script d'orchestration lisible : vérification du modèle,
tokeniseur officiel figé (poids génératifs non téléchargés par Python), rendu du gabarit local et contrôle du budget,
appel `/api/generate` en raw pour éviter le double gabarit, contrôle de la fin de génération et des comptes de tokens,
validation structurelle des citations et de la phrase d'abstention. Le mode `--generate` et l'enregistrement UTF-8
sans écrasement sont ajoutés au script principal.

La baseline fixe avant le premier essai local : température 0.0, graine 20261018, contexte 8192, sortie 512,
marge 64 tokens, keep_alive 30m, stream false. Ces paramètres ne sont pas présentés comme optimaux.
Le modèle local est comparé au digest de #31. Le tokeniseur est `Qwen/Qwen2.5-7B-Instruct`, révision
`a09a35458c702b33eeacc393d103063234e8bc28`, vérifiée dans l'API officielle du modèle.

Sources techniques : documentation officielle Ollama (generate/raw/show/version), documentation Transformers
sur les gabarits et le comptage sans ajout de tokens spéciaux en double, notebook 02, script et rapport de #31.
Ni corpus, index, questions figées, seuil, entraînement ni protocole d'évaluation ne sont modifiés.

## Contrôles et limites

45 tests réussis sous Python 3.12.14 et NumPy 2.3.5, compilation Python et contrôle du diff.
Les nouveaux tests utilisent un serveur et un tokeniseur simulés et des réponses techniques artificielles ; ce ne
sont pas des questions d'évaluation et ils ne prouvent aucune abstention réelle de Qwen.
Aucun appel au modèle sur la machine de Jibril n'est réalisé par l'assistant. Les commandes pour Q036 et Q003 sont
fournies ; les sorties réelles, la concordance des tokens HF/GGUF, les ressources et la relecture humaine restent
attendues. La validité structurelle d'une citation ne prouve pas sa justification sémantique.
La PR #85 reste en brouillon, sans fusion ni clôture de #51. Aucune charge réelle n'est inventée.
