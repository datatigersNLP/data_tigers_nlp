# Supports de J3 : partie de Jibril

**Équipe** Data Tigers

**Ticket** #112, plan de Vaneck du 4 novembre (10 diapositives)

**Préparé le** 9 novembre 2026 avec Codex, pour relecture par Jibril BENSALEM

**Périmètre** contenu de la diapositive 5 et texte oral de Jibril pour la diapositive 8

**Assemblage** Rémy RAYANE ; mise en forme par Vaneck DAGAR, selon la charte du site

**Statut** proposition de contenu, relecture humaine finale à faire

---

## Diapositive 5 : Volet B, la chaîne RAG locale

**Message.** Le système récupère cinq passages du corpus et les fournit à Qwen pour rédiger une réponse avec des références vérifiables.

**Contenu à afficher.**

- Corpus fermé : 261 fiches, 4 240 passages dans l'index commun M2.
- Recherche locale : E5 en Python, sur CPU et en fp32, sélectionne les cinq passages les plus proches de la question.
- Rédaction : Qwen2.5-7B-Instruct Q4_K_M reçoit la question et le texte des passages balisés de `[P1]` à `[P5]`, via Ollama 0.40.13.
- Abstention : la consigne demande de refuser une réponse insuffisamment documentée. B2 ajoute un refus avant génération si le meilleur score est sous le seuil fixé.
- Contrôle automatique : forme des références et présence dans le contexte. La vérification du sens demande une relecture des réponses.

**Texte oral proposé.**

Le volet A renvoie des passages. Le volet B ajoute une réponse rédigée à partir de ces passages. On peut le comparer à un lecteur auquel on donne cinq pages d'un dossier avant de lui poser une question. E5 choisit les pages, puis Qwen reçoit leur texte, avec des repères de P1 à P5. Toute la chaîne de recherche et de génération s'exécute sur le Legion. La consigne demande au modèle de citer ses passages et de s'abstenir quand ils ne suffisent pas. Dans l'état B2, un seuil peut aussi arrêter la demande avant la génération. Notre contrôle automatique vérifie que les références existent et respectent le format attendu. Pour savoir si elles justifient réellement la réponse, il faut relire le contenu. C'est justement ce que l'évaluation distingue.

**Repères pour les questions du jury.**

- RAG signifie génération augmentée par récupération : on fournit des documents au modèle au moment de répondre.
- E5 produit un vecteur de recherche. Qwen reçoit le texte original des passages, pas leurs vecteurs ni leurs scores.
- Le volet A encode les requêtes dans le navigateur. Le volet B utilise la référence E5 en Python fp32 sur CPU, avec le même index M2 fp32.
- Le contexte de Qwen est limité à 8 192 tokens, avec une sortie de 512 tokens au plus et une marge contrôlée. Le script refuse un budget dépassé sans tronquer silencieusement les passages.
- Une citation bien formée donne un passage à vérifier. Elle ne prouve ni l'exactitude de la réponse, ni le respect de toutes les conditions et exceptions du droit.
- Les débits historiques de deux appels courts sous Ollama 0.34.4 ne mesurent pas les performances de ce RAG complet sous 0.40.13.

**Sources.** `scripts/rag/rag.py` (`charger_encodeur`, `recuperer_passages`, `construire_contexte`) ; `scripts/rag/generation.py` (`preparer_entree`, `valider_citations`) ; `docs/jalons/J3_chiffres_verifies.md` ; protocole 06, sections 3 à 5 et 8. Cette version corrige l'affirmation de la PR #134 selon laquelle les citations permettraient de contrôler l'absence d'hallucination.

## Diapositive 8 : contribution orale de Jibril

**Contenu et chiffres à afficher.** La source commune reste la section « Diapositive 8 » de `docs/jalons/J3_diapositives_mahe.md`, complétée dans la même PR. Rémy peut y reprendre le tableau et Vaneck le mettre en forme. Le tableau n'est pas recopié ici.

**Répartition proposée.** Mahé présente le protocole et la comparaison avant/après prévue. Jibril présente l'exécution sur le Legion et ce que montre la mesure avant. Cette répartition orale reste à convenir avec Mahé.

**Texte oral proposé.**

J'ai exécuté la mesure avant le 9 novembre sur le Legion, avec le protocole verrouillé et les 97 questions de test. Les cinq états restent sous la limite d'erreurs techniques. Le résultat à retenir est le compromis de B2 : il s'abstient sur 20 des 24 questions hors corpus, mais aussi sur 45 des 72 questions du corpus sans erreur technique. Il refuse donc souvent une question pour laquelle le corpus contient une réponse. En parallèle, 12 réponses sur ces 72 citent au moins un passage pertinent. Cela ne suffit pas à dire qu'elles sont exactes. Ces résultats constituent notre référence avant adaptation. Nous conservons le même jeu et les mêmes règles pour la mesure après, puis une relecture à l'aveugle jugera le sens des réponses.

**Repères pour les questions du jury.**

- Les 71 et 72 questions dans les dénominateurs de B1 et B2 viennent des erreurs techniques exclues. Le jeu compte toujours 73 questions du corpus et 24 hors corpus.
- B2 change la consigne et ajoute le seuil par rapport à B1. Cette mesure ne permet pas d'attribuer tout l'écart au seul seuil.
- « Passage pertinent » signifie pertinent selon la règle D4. Une citation pertinente ne prouve pas que chaque affirmation de la réponse est juste.
- Les résultats avant sont descriptifs. L'analyse principale porte sur B2 après adaptation contre la référence prévue, avec des intervalles à 97,5 % sur M1 et M4.
- Le réglage reste celui du protocole gelé. Nous ne déplaçons pas le seuil pour améliorer les résultats du lot de test.

**Sources.** Section « Diapositive 8 » de `docs/jalons/J3_diapositives_mahe.md` ; protocole 06 ; journal de mesure du 9 novembre dans la PR #142. Les fichiers bruts et l'archive restent hors dépôt.

## Intégration et état des dépendances au 9 novembre

- Pour la diapositive 5 de la PR #134, reprendre la section correspondante ci-dessus et son texte oral.
- Pour la diapositive 8, renvoyer à la source commune de Mahé et utiliser le texte oral proposé ici, afin de garder un seul tableau de résultats à maintenir.
- Jibril déclare avoir reçu la grille de Maïmouna. Celle de Vaneck manque encore. Cette réception partielle ne permet pas de déclarer le lot v2b accepté ou l'entraînement réalisé.
- Les PR #131 et #130 sont fusionnées. La mesure avant et son analyse sont exécutées, et Jibril confirme l'envoi de l'archive à Mahé. Sa réception reste à confirmer.
- La PR #128 attend une correction du verrou du serveur. Le branchement final de la démonstration reste à valider sur le Legion.
- Les supports sont attendus le 13 novembre selon #112. La date officielle de J3 reste à confirmer par écrit dans #8.

**Relectures attendues.** Jibril sur son texte et les formulations techniques, Mahé sur les résultats et la diapositive 8, puis Rémy et Vaneck pour l'assemblage et la mise en forme.
