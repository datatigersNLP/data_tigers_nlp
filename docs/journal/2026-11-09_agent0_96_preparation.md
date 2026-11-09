# Journal d'usage IA : préparation anticipée du lanceur Agent0 #96

**Date et responsable.** 9 novembre 2026, Jibril BENSALEM (`JIBZZOU`).

**Outil.** Codex dans ChatGPT Work, version précise du modèle non vérifiée.

**Objet.** Jibril demande d'avancer sur Agent0 pendant l'attente des autres travaux. Préparation du lanceur de #96 et de ses tests, sur branche dédiée, sans nouveau pilote, appel réel de modèle ou modification du protocole de mesure. Le report du périmètre complet reste distinct de cette préparation autorisée.

**Vérification préalable.** Lecture de #95/#96, de la décision du 30 octobre, des PR ouvertes et des sources actuelles de génération, du schéma et des helpers RAG. Base `dev/a294d25`. Aucun autre développement de #96 n'apparaît dans les PR ouvertes. La grille historique reste en attente humaine et le pilote n'est pas figé. L'estimation historique de #96 reste 4 h actives pour son périmètre initial, à réexaminer avant une reprise complète ; aucune durée réelle n'est attribuée.

**Produit.** `scripts/synthetic/evaluate.py`, tests sur fixtures et `README_evaluation.md`. Format d'entrée proposé `agent0-challenge-v1`, avec JSONL de cas `synthetic-v1`, déclarations de gel/séparation, empreintes et acceptations humaines déclarées. Le code vérifie leur cohérence et ne certifie pas l'identité des relecteurs ni l'indépendance réelle. Les identifiants historiques de mise au point sont exclus du pilote évalué.

Le lanceur réutilise les helpers de #85 sans modifier `rag.py`, `generation.py` ou `mesure.py`. L'index et E5 fp32/CPU sont chargés une fois pour le run, le Top 5 est calculé pour chaque question et Qwen utilise les contrôles de génération existants. Seul le texte de la question entre dans le retrieval et le prompt. Les résultats conservent les passages, références, réponses brutes, diagnostics, versions et empreintes. Une interruption et les erreurs restent tracées, sans écrasement ni nouvel essai automatique. Cette baseline exploratoire ne reproduit pas les états du protocole 06 et n'ajoute aucun seuil.

**Contrôles exécutés.** Python 3.12.14, Pydantic 2.14.0, NumPy 2.5.3, environnement dédié Linux. Suite synthétique : 180 tests réussis, soit les 149 existants et 31 nouveaux. Les tests du lanceur couvrent les lots incomplets, non acceptés ou altérés, l'exclusion des candidats historiques, les doublons, les caractères des questions, la séparation des annotations, les cinq passages avec les vrais helpers de contexte, les erreurs, les snapshots, les empreintes et le refus d'écrasement. Aide du CLI exécutée avec succès depuis son chemin de script. Aucun test ne revendique une génération réelle sur le Legion.

**Résultats retenus.** Le lanceur est prêt pour revue de code et vérification du contrat d'entrée. La grille historique ne peut pas servir directement d'entrée. Les données synthétiques et leurs traces restent hors du jeu humain et de la mesure officielle.

**Ce qui reste à faire.** Relecture indépendante du code et du contrat, nouveau pilote de #95 réellement relu et figé, environnement complet préparé, puis petit essai réel borné. Le diagnostic de #97 et la boucle facultative de #98 ne sont pas réalisés. Aucun ticket n'est fermé et aucun résultat de benchmark n'est déclaré.

**Validation humaine.** Relecteur responsable : Jibril BENSALEM. Relecture finale du code et acceptation du format d'entrée non attestées à la rédaction. Aucune grille humaine n'est préremplie par l'assistant et aucun exemple officiel d'évaluation n'est généré ou modifié.

**Temps d'appropriation constaté.** Non mesuré. Aucun temps réel ni gain de temps inventé.

**Difficultés rencontrées.** Il n'existe pas encore de contrat de lot indépendant gelé livré par #95 : le nouveau format est donc une proposition de cette PR, soumise à revue. Le premier lecteur JSONL utilisait `splitlines`, qui coupait aussi des séparateurs Unicode légaux dans une chaîne JSON ; découpage limité au LF et régression technique ajoutée. Les déclarations booléennes strictes, les erreurs de digest en CLI et l'exclusion des identifiants de mise au point sont vérifiées explicitement.
