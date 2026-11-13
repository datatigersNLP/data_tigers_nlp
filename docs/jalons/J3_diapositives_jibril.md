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

**Contenu et chiffres à afficher.** La source commune reste la section « Diapositive 8 » de `docs/jalons/J3_diapositives_mahe.md`. Rémy peut y reprendre le tableau T/adapté et Vaneck le mettre en forme. Le tableau n'est pas recopié ici.

**Répartition proposée.** Mahé présente le protocole et l'adaptation. Jibril présente le verrou, la distinction entre les machines, les résultats principaux et leurs limites. Cette répartition orale reste à convenir avec Mahé.

**Texte oral proposé.**

J'ai réalisé la mesure avant sur le Legion, avec le protocole verrouillé. Mahé l'a vérifiée indépendamment. Pour la comparaison de l'adaptation, il a ensuite mesuré le témoin T et le modèle adapté sur son Mac, sur les mêmes questions. On évite ainsi de mélanger un effet de modèle et un changement de machine. Le résultat principal concerne les citations pertinentes : on passe de 10 à 18 questions sur 72, soit un gain de 11,1 points. L'intervalle prévu au protocole reste au-dessus de zéro, donc l'amélioration est démontrée sur ce critère. Hors corpus, les deux modèles s'abstiennent sur 20 questions sur 24. Ce taux identique ne prouve pas l'absence de dégradation, car l'intervalle reste large. Enfin, citer un passage pertinent ne garantit pas que toute la réponse soit juste. La relecture humaine à l'aveugle reste nécessaire.

**Repères pour les questions du jury.**

- Le protocole, les scripts, le jeu, le seuil et l'index sont contrôlés par dix empreintes. L'amendement M1 précise la machine de mesure sans modifier les fichiers gelés.
- La comparaison principale porte sur B2 adapté contre B2 de T, sur le Mac. La mesure du Legion reste descriptive et n'entre pas dans cet écart.
- Les 72 questions du corpus sont communes aux deux états, avec Q088 exclue pour une erreur technique de décompte des tokens. Les 24 questions hors corpus restent dans la comparaison.
- M4 : huit questions gagnent une citation pertinente et aucune n'en perd. Le gain vaut +11,1 points, IC à 97,5 % [+2,1 ; +23,8], p exact de McNemar = 0,0078.
- M1 : 20/24 dans les deux phases, écart nul, IC à 97,5 % [−20,5 ; +20,5]. Aucune amélioration ni absence de dégradation n'est démontrée.
- M2 reste descriptif : 55,6 % d'abstentions dans le corpus pour l'adapté contre 70,8 % pour T. Cela reste plus de la moitié des questions. Le dénominateur porte sur le corpus entier, pas seulement sur les contextes pertinents.
- Le diagnostic 28/45 et 17/33 décrit la mesure avant du Legion. Il n'est pas transposé aux résultats du Mac.
- La récupération utilisée reste E5 seul avec cinq passages. Aucun gain de la récupération v2 n'est attribué à l'adaptation.
- Maïmouna et Vaneck doivent relire à l'aveugle 20 réponses citées de T et 20 de l'adapté. M4 ne remplace pas cette vérification du sens.

**Sources.** Section « Diapositive 8 » de `docs/jalons/J3_diapositives_mahe.md` ; protocole 06 et amendement M1 ; [résultats publiés par Mahé le 11 novembre](https://github.com/datatigersNLP/data_tigers_nlp/issues/52#issuecomment-6797300311). Les fichiers bruts restent hors dépôt. Aucun recalcul de ces fichiers privés n'est revendiqué pour ce support.

## Intégration et état documenté au 11 novembre

- #142 et #143 sont fusionnées dans dev, sans nouveau commit sur leurs branches approuvées. Cette actualisation relève d'une nouvelle PR.
- Pour la diapositive 5 de #134, reprendre la section ci-dessus. Son contenu technique et le bilan historique Agent0 restent inchangés.
- Pour la diapositive 8, reprendre le tableau principal T/adapté de la source commune. Le tableau du Legion devient un repère historique dans les notes.
- Mahé rapporte l'entraînement complet du lot v2b le 11 novembre, l'import des deux modèles et les mesures T/adapté. Sources : [entraînement #107](https://github.com/datatigersNLP/data_tigers_nlp/issues/107#issuecomment-6795651678) et #52. La validation indépendante du manifeste et les verdicts humains à l'aveugle ne sont pas attestés par cette contribution.
- #128 et #141 sont fusionnées. Le branchement de la récupération v2 à la démonstration et la validation réelle de celle-ci restent distincts des résultats de l'adaptation.
- #144 et #145 ont été relues et approuvées par Mahé le 11 novembre. Il confirme 184 tests du lanceur avec les versions du verrou et l'absence des 25 fiches du pilote dans les cinq lots privés de Qwen. Le contrôle des données d'entraînement de l'encodeur reste ouvert. Ces constats n'attestent ni un pilote exécuté ni la validation humaine des futurs candidats.
- Toutes les mesures restantes relèvent de Mahé sur le Mac. Jibril n'a aucune mesure à lancer et T ne sera pas transféré.
- Les supports sont attendus le 13 novembre selon #112. La date officielle du jalon J3 reste à confirmer par écrit dans #8.

**Relectures attendues.** Jibril sur son texte oral, Mahé sur les résultats et la répartition de parole, puis Rémy et Vaneck pour l'assemblage et la mise en forme.
