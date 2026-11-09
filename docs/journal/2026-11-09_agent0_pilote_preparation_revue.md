# 9 novembre 2026 : revue du lanceur #96 et préparation du pilote

**Responsable :** Jibril BENSALEM. **Outil :** Codex dans ChatGPT Work, identifiant exact du modèle non attesté. **Relecture humaine indépendante :** attendue, aucun nom ou verdict attribué à sa place.

## Demande et vérification préalable

Jibril indique que le lanceur est préparé dans la PR #144, puis demande de continuer ce chat. Lecture de #95/#96, de la décision du 30/10 dans #13, des PR ouvertes et du code de #144 à `bb80096`, base `dev/a294d25`. Aucun AGENTS.md ni CONTRIBUTING dans l'arbre inspecté. Le README du dépôt impose une branche dédiée et une PR vers dev ; compte connecté JIBZZOU vérifié avant publication.

## Produit

Dossier `docs/etudes/agent0_pilote_independant/` : plan de 25 emplacements, sources provisoires pour 20 d'entre eux, 25 passages complets issus de 20 fiches distinctes et grille humaine vierge. Les trois fiches historiques sont exclues. Cinq emplacements hors corpus restent réservés à une méthode à décider. Aucun candidat n'est généré, aucun manifeste de gel d'évaluation créé.

Le tirage par SHA-256 est documenté avec sa graine et ses règles exactes, sans lecture des questions ou annotations humaines, ni utilisation des réponses du RAG pour choisir. Il établit une séparation avec les fiches de mise au point, pas encore avec le lot d'adaptation. Cette limite est explicite et bloque le gel tant qu'elle n'est pas examinée.

## Contrôles et résultats

31 tests existants de test_evaluate réussis dans la copie de revue, Python 3.12.14, Pydantic 2.13.4, NumPy 2.3.5 ; provenance Git simulée. Les 180 tests rapportés par l'auteur avec le verrou ne sont pas relancés ; cette autre configuration est distinguée.

Contre-exemple technique supplémentaire : une affirmation adversarial déclarée acceptée est admise par le lanceur sans « ? », mais refusée par le validateur de génération. Point de contrat documenté avant tout export ; aucun changement du code de #144 ou jugement sémantique réel.

Corpus complet reçu depuis le blob Git, empreintes exactes vérifiées ; 4 240 passages, 261 fiches. Sélection et grille recoupées : URLs distinctes, exclusion des trois fiches, textes et empreintes intacts, 25 emplacements, aucun champ humain rempli. Aucun chargement de matrice, E5, Qwen ou Ollama.

## Suite et limites

Relecture du contrat et du code, résolution du point technique, autorisation de reprise, séparation avec l'adaptation, méthode hors corpus, puis gel du générateur avant génération. Les décisions humaines, le gel du lot et l'essai réel ne sont pas réalisés ici. Aucune heure réelle, estimation révisée ou validation d'équipe n'est inventée ; aucun ticket n'est clos. Cette préparation ne modifie ni le jeu humain, ni la mesure officielle, ni le RAG.
