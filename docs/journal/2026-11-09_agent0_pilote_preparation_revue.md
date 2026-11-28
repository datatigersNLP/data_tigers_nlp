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

## Complément du 9 novembre : révision 2 de la préparation

**Demande.** Jibril autorise de terminer la préparation du pilote : contrôler la séparation avec l'adaptation et écrire la méthode hors corpus. Cette demande n'est pas interprétée comme une autorisation de génération, de mesure ou de gel humain.

**Sources relues.** État de #95/#107, commentaires de #107 et revue de #130, PR ouvertes, sources actuelles des deux chaînes d'adaptation et des prompts Agent0, protocole d'ajustement et préparation `377717f`. Base `dev/a294d25`, #144 au correctif `a62c9b2`. Aucun AGENTS.md/CONTRIBUTING dans l'arbre examiné. Les octets du CSV humain au tag sont contrôlés par SHA-256 puis seules les colonnes URL, lot et type sont exploitées : aucun texte de question ni extrait humain ne sert au choix des sources ou à la rédaction de cas. Le fichier lu sur la branche mutable de #44 a ici la même empreinte que le tag ; cela ne prouve pas sa version lors d'un ancien entraînement.

**Constat corrigé.** 17 des 20 fiches de la première préparation sont hors des deux listes d'exclusion. Ce constat indique un chevauchement potentiel avec les viviers autorisés, pas une présence démontrée dans les lots privés. Le README encodeur annonce 67 fiches exclues ; les données vérifiées donnent 66 URLs non vides, dont les 61 exclues côté Qwen. Contradiction consignée dans l'audit, sans changer les fichiers de l'autre domaine.

**Produit.** Révision 2 des trois JSON de préparation, du README et de cette note ; ajout de l'audit JSON, du rapport de séparation et de la méthode hors corpus. Suivi du correctif de #144 ajouté à la revue historique, sans réécrire son constat sur `bb80096`. La version 1 reste accessible au commit `377717f` et son rapprochement est conservé dans l'audit.

Nouveau tirage déterministe dans l'intersection des fiches exclues de l'adaptation, moins les fiches de mise au point : 60 fiches possibles. Filtre technique `len(texte) >= 200`, sans jugement de suffisance. Résultat : 25 fiches distinctes, 30 passages, cinq emplacements par catégorie ; les cinq hors corpus reçoivent un ancrage de génération, sans preuve positive. La méthode conserve la consigne hors corpus v2 existante et exige une recherche documentée dans le corpus complet puis une décision humaine. Aucun réglage du générateur ni question produite ; aucun quota d'acceptation, ni remplacement automatique d'un essai refusé.

**Contrôles exécutés.** Corpus M2 complet et en-tête vérifiés par empreintes ; 4 240 passages, 261 fiches. Textes des 30 passages recoupés mot pour mot et SHA-256 individuels vérifiés ; cardinalités, affectations et exclusion des fiches historiques contrôlées. Aucun des 30 textes complets n'est identique à un texte des fiches autorisées dans les viviers Qwen ou encodeur ; recopies partielles et paraphrases non évaluées. Seconde production des quatre JSON identique à l'octet près. Les 25 lignes n'ont toujours aucun candidat, question, verdict, nom, date, confirmation ou point attendu. Le dossier préparatoire reste refusé comme lot figé par le lecteur de #144. Liens internes, diff et préservation des autres fichiers contrôlés avant publication.

Contrôles documentaires et exécution locale du tirage uniquement : aucun test unitaire relancé dans cette étape. Les 184 tests de #144 restent un résultat distinct de l'étape précédente, dans son environnement documenté. Aucun appel Ollama/E5/Qwen ni lecture de matrice, entraînement ou mesure réelle.

**Limites et suite.** Les 25 fiches appartiennent aussi au test humain ; ce pilote ne constitue donc pas un benchmark humain indépendant et ses résultats ne seront pas combinés à la mesure officielle. Les lots privés Qwen v2b et encodeur ne sont pas reçus : leur contrôle d'empreintes et de passages, puis la déduplication des futures questions, restent à effectuer. L'audit contrôle les règles et les viviers, pas les octets effectivement utilisés en entraînement. Préparation soumise à la relecture humaine du code, des sources et de la méthode ; Jibril est responsable de la contribution, aucun relecteur indépendant n'est déclaré à sa place. Configuration et environnement à arrêter avant toute génération. Aucun temps réel ni validation d'équipe inventé, aucune clôture ou fusion.
