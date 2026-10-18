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

## Retour local ultérieur : première réponse Q036

Jibril transmet ensuite la trace « Texte collé(1).txt », SHA-256
`1cc87a6c42eb998534cc1ba648e8a52a50e994ab485f62ed3a94d103757b322a`.
Cette exécution sur son Legion produit `reponse_citee`, `e5_charge: true`, `ollama_appele: true`.
Le modèle est Qwen local au digest prévu, servi par Ollama 0.40.5. L'entrée contient 2 317 tokens pour les deux
comptages HF/Ollama ; la sortie contient 381 tokens et se termine par `stop`. Les références `[P1]` et `[P5]`
existent parmi les cinq passages. Aucune erreur technique n'est rapportée. Ollama indique 46,2005116 s au total,
dont 21,9012127 s de chargement, 18,503807 s de traitement du prompt et 5,774473 s de génération.
Ce temps ne couvre pas toute la chaîne Python ; aucune occupation mémoire ou GPU n'est rapportée.

L'assistant compare la réponse aux passages : les huit mesures de P1 sont reprises, mais les conditions
d'application présentes dans P1 et P5 sont omises. Les citations sont regroupées en introduction, sans référence
sur chaque puce. Cette lecture qualitative est documentée dans `docs/etudes/rag_51.md` ; elle ne devient pas une
mesure systématique ni une validation juridique exhaustive. Les indicateurs sémantiques automatiques restent à false.
Le code, la réponse brute, les questions et les paramètres ne sont pas modifiés. Q003 reste à exécuter dans la même
configuration pour observer l'abstention. La relecture du binôme et la validation globale de #51 restent attendues.

## Retour local ultérieur : abstention Q003

Jibril transmet ensuite la trace « Texte collé(2).txt », SHA-256
`58a6acffbf0397ae61a7982e407700214c411cf03a00173d432fc22848f43f19`.
Le modèle local répond exactement : « Je ne peux pas répondre à cette question à partir des passages fournis. »
Le rapport indique `abstention_modele`, aucun incident technique, 1 822 tokens d'entrée pour les deux comptages
HF/Ollama et 17 tokens de sortie, fin `stop`. Ollama rapporte 1,1602394 s au total ; ce n'est pas le temps de toute
la chaîne Python. Le modèle, la consigne et les paramètres sont identiques à Q036 ; aucune question n'est modifiée.

L'assistant vérifie les cinq passages contre les métadonnées versionnées, reproduit le contrôle d'abstention et
contrôle l'empreinte de l'entrée. Les passages reçus ne fournissent pas les règles de cumul d'activités d'un
fonctionnaire. Le score maximal de similarité, environ 0,8585, ne garantit pas une réponse possible ; aucun seuil
n'est ajouté. Le résultat et ses limites sont documentés dans l'étude RAG. Les deux exemples réels ne constituent
pas une évaluation systématique et ne corrigent pas les limites de Q036. Les tests Windows, la relecture du binôme
et la présentation à l'équipe restent à confirmer. La PR #85 reste en brouillon et #51 reste ouverte.
