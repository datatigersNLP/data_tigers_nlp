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

Le volet A renvoie des passages. Le volet B ajoute une réponse rédigée à partir de ces passages. On peut le comparer à un lecteur auquel on donne cinq pages d'un dossier avant de lui poser une question. E5 choisit les pages, puis Qwen reçoit leur texte, avec des repères de P1 à P5. Toute la chaîne de recherche et de génération s'exécute localement. La consigne demande au modèle de citer ses passages et de s'abstenir quand ils ne suffisent pas. Dans l'état B2, un seuil peut aussi arrêter la demande avant la génération. Notre contrôle automatique vérifie que les références existent et respectent le format attendu. Pour savoir si elles justifient réellement la réponse, il faut relire le contenu. C'est justement ce que l'évaluation distingue.

**Repères pour les questions du jury.**

- RAG signifie génération augmentée par récupération : on fournit des documents au modèle au moment de répondre.
- E5 produit un vecteur de recherche. Qwen reçoit le texte original des passages, pas leurs vecteurs ni leurs scores.
- Le volet A encode les requêtes dans le navigateur. Le volet B utilise la référence E5 en Python fp32 sur CPU, avec le même index M2 fp32.
- Le contexte de Qwen est limité à 8 192 tokens, avec une sortie de 512 tokens au plus et une marge contrôlée. Le script refuse un budget dépassé sans tronquer silencieusement les passages.
- Une citation bien formée donne un passage à vérifier. Elle ne prouve ni l'exactitude de la réponse, ni le respect de toutes les conditions et exceptions du droit.
- Les débits historiques de deux appels courts sous Ollama 0.34.4 ne mesurent pas les performances de ce RAG complet sous 0.40.13.

**Sources.** `scripts/rag/rag.py` (`charger_encodeur`, `recuperer_passages`, `construire_contexte`) ; `scripts/rag/generation.py` (`preparer_entree`, `valider_citations`) ; `docs/jalons/J3_chiffres_verifies.md` ; protocole 06, sections 3 à 5 et 8. Cette version corrige l'affirmation de la PR #134 selon laquelle les citations permettraient de contrôler l'absence d'hallucination.

### Agent0 Light, complément en fin de diapositive 5

**Complément à afficher.** Agent0 Light : générateur de cas exploratoires, avec contrôles et support de relecture. Sur 18 essais : 15 candidats, 3 rejets automatiques. Relecture humaine des candidats à faire.

**Passage oral proposé, 30 à 45 secondes visées.** Durée à vérifier en répétition.

J'ai aussi développé Agent0 Light pour proposer des questions complémentaires à partir du corpus. Il couvre cinq catégories et garde une trace des sources et des rejets. Sur 18 essais historiques, nous avons obtenu 15 candidats et 3 rejets automatiques. Passer les contrôles automatiques ne suffit pas à valider le sens des questions. La relecture humaine reste à faire. Ces candidats restent séparés du jeu humain et exclus de l'entraînement, y compris du lot v2b. Aucun gain du RAG n'est démontré par ces essais.

**Détails à garder dans les notes.**

- Les cinq catégories sont simple, reformulation, multi-passage, piège à fausse prémisse et hors corpus.
- Le bilan documente 149 tests réussis sur le générateur et ses contrôles. Aucun test n'est relancé pour cet ajout au support.
- Les 15 candidats ont franchi les contrôles historiques de leur run. Cela ne signifie pas qu'ils ont été revalidés par tous les contrôles finaux, ni qu'ils sont corrects à 83 %.
- Aucun cas hors corpus n'est confirmé humainement dans le bilan. Une question classée hors corpus par le modèle reste une proposition à examiner.
- Le générateur et le support de relecture sont intégrés. Le pilote indépendant et le benchmark synthétique restent reportés. Agent0 relève de l'évaluation exploratoire, distincte de l'adaptation de la diapositive 7 et de la mesure officielle de la diapositive 8.
- Ce passage termine la diapositive 5 avant la démonstration de la diapositive 6. Le plan reste à dix diapositives.

**Sources.** `docs/etudes/agent0_bilan_rapport_oral.md`, état vérifié du 2 novembre, sections 1 à 6 ; `docs/etudes/agent0_relecture/verification_archive.md` ; `docs/etudes/agent0_relecture/grille_relecture.json`. Ces sources distinguent les essais historiques, les contrôles techniques et la validation humaine encore attendue.

## Diapositive 8 : contribution orale de Jibril

**Contenu et chiffres à afficher.** La source commune reste la section « Diapositive 8 » de `docs/jalons/J3_diapositives_mahe.md`, complétée dans la même PR. Rémy peut y reprendre le tableau et Vaneck le mettre en forme. Le tableau n'est pas recopié ici.

**Répartition proposée.** Mahé présente le protocole et la comparaison avant/après prévue. Jibril présente l'exécution sur le Legion et ce que montre la mesure avant. Cette répartition orale reste à convenir avec Mahé.

**Texte oral proposé.**

J'ai exécuté la mesure avant le 9 novembre sur le Legion, avec les 97 questions de test. Le verrou empêche de modifier les éléments figés avant la mesure. Mahé a vérifié les fichiers et retrouvé les mêmes métriques. B2 s'abstient sur 20 des 24 questions hors corpus. Pour comprendre ses 45 abstentions sur les questions du corpus, il faut regarder les passages fournis : 28 surviennent sans passage pertinent selon D4. Parmi les 33 questions avec un passage pertinent, 17 reçoivent encore une abstention. Ce diagnostic distingue les difficultés de récupération des refus malgré un contexte pertinent, avec les limites de la règle D4. La suite se fera sur le Mac de Mahé : le modèle adapté sera comparé au témoin T sur cette même machine. La mesure du Legion restera descriptive, sans comparaison directe avec les résultats du Mac.

**Repères pour les questions du jury.**

- Les 71 et 72 questions dans les dénominateurs de B1 et B2 viennent des erreurs techniques exclues. Le jeu compte toujours 73 questions du corpus et 24 hors corpus.
- B2 change la consigne et ajoute le seuil par rapport à B1. Cette mesure ne permet pas d'attribuer tout l'écart au seul seuil.
- « Passage pertinent » signifie pertinent selon la règle D4. Une citation pertinente ne prouve pas que chaque affirmation de la réponse est juste.
- M2 reste 45/72 par rapport au corpus entier. Le diagnostic conditionnel au contexte est distinct : 28 de ces abstentions sans passage pertinent selon D4, et 17/33 avec passage pertinent (16 du modèle, une du seuil). D4 ne garantit pas qu'aucune autre réponse existe dans les contextes classés sans passage pertinent.
- Le seuil déclenche 11 abstentions sur 65, les 54 autres viennent du modèle. Parmi les questions du corpus, il déclenche deux abstentions.
- La mesure avant du Legion reste descriptive. L'analyse principale compare B2 adapté à B2 de T sur le Mac, avec des intervalles à 97,5 % sur M1 et M4, conformément à l'amendement M1 du 10 novembre dans #52.
- Le réglage reste celui du protocole gelé. Nous ne déplaçons pas le seuil pour améliorer les résultats du lot de test.

**Sources.** Section « Diapositive 8 » de `docs/jalons/J3_diapositives_mahe.md` ; protocole 06 ; journal de mesure du 9 novembre dans la PR #142. Les fichiers bruts et l'archive restent hors dépôt.

## Intégration et état documenté au 10 novembre

- Pour la diapositive 5 de la PR #134, reprendre la section correspondante ci-dessus et son texte oral.
- Pour la diapositive 8, renvoyer à la source commune de Mahé et utiliser le texte oral proposé ici, afin de garder un seul tableau de résultats à maintenir.
- Les deux grilles du lot v2b ont été reçues. Mahé a publié le 10 novembre une décision d'acceptation sans arbitrage commun, en retenant la sévérité maximale case par case (3 faux sur 30). Cette décision déroge à l'arbitrage initialement prévu et conserve le risque déclaré sur les abstentions injustifiées. Le lancement du 10 novembre a été interrompu avant toute sauvegarde et tout manifeste, puis reporté au 11 novembre (#107).
- Les PR #131 et #130 sont fusionnées. Mahé confirme la réception des sept fichiers de la mesure avant et les mêmes métriques après recalcul indépendant. Le ZIP avait été décompressé automatiquement : son empreinte globale n'a pas été recalculée à réception.
- Vaneck a corrigé le verrou du serveur et mis Vite à jour dans #128, au commit 8ba4524. La contre-relecture du 10 novembre approuve ces corrections après tests automatisés et reproduction du cas HTTP, sans inférence réelle. L'essai de démonstration sur la machine de présentation reste à réaliser.
- #141 a été fusionnée par Mahé le 10 novembre. La contre-relecture du 10 novembre ne relève pas d'incompatibilité bloquante sur le format du contexte, les sources et le budget, avec 19 tests réussis et des contrôles complémentaires sur fixtures. Le branchement à la démonstration et le contrôle complet de l'abstention restent distincts ; aucun gain de récupération n'est assimilé à un gain de qualité des réponses.
- Les phases de mesure restantes se font sur le Mac de Mahé. T ne sera pas transféré et Jibril ne lance plus de mesure (#52, amendement M1).
- Les travaux Agent0 #144 et #145 restent en attente de revue après le 12 novembre. Le passage de la diapositive 5 présente le socle historique livré et ses limites, sans annoncer ce lanceur préparatoire comme validé.
- Les supports sont attendus le 13 novembre selon #112. La date officielle de J3 reste à confirmer par écrit dans #8.

**Relectures attendues.** Jibril sur son texte et les formulations techniques, Mahé sur les résultats et la diapositive 8, puis Rémy et Vaneck pour l'assemblage et la mise en forme.
