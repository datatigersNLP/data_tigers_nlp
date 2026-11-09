# Revue assistée du lanceur #144 et de son contrat d'entrée

Référence relue : [PR #144](https://github.com/datatigersNLP/data_tigers_nlp/pull/144), tête `bb80096aa2164e60f7db4ad703e0f2957bb65ebf`, le 9 novembre 2026. Base : `dev/a294d252d1ecc285dfd7df88e43a3ec5df891fe7`. Revue de code et contre-essais assistés par Codex à la demande de Jibril ; **ce n'est pas une approbation humaine indépendante**. Aucune review GitHub n'était déposée au début de ce contrôle.

## Ce qui a été vérifié

- Le contrat impose un effectif de 1 à 25, des empreintes, une date de gel passée avec fuseau, un booléen strict et des déclarations de séparation.
- Le lecteur conserve les octets du lot, refuse les identifiants historiques inventoriés et les doublons normalisés, et exige les acceptations humaines déclarées.
- Le RAG reçoit le texte exact de la question, sans catégorie, correction, preuve ou point attendu. Les annotations sont conservées séparément.
- L'index est chargé et contrôlé avant E5/Ollama ; les preuves sont ancrées dans les sources. Réservation d'un nouveau dossier, conservation des événements et erreurs, absence de relance automatique.
- `termine` signifie traitement achevé, même en présence d'erreurs techniques. Le README le précise ; lire aussi leur nombre. Le lanceur ne prétend pas exécuter B0/B1/B2 ou produire les métriques de #97.

## Point de contrat à traiter avant export : contrôle automatique partiellement déclaratif

**Contre-exemple confirmé sur une fixture technique :** un cas adversarial déclaré `automatic: passed` et `human: accepted`, avec preuve exacte et champs de relecture factices cohérents, peut contenir une affirmation sans « ? ». `charger_lot` puis `verifier_sources` l'acceptent. La même proposition est refusée par le validateur de génération : « Une question adversarial doit être terminée par '?' ».

Références : [evaluate.py, tête relue](https://github.com/datatigersNLP/data_tigers_nlp/blob/bb80096aa2164e60f7db4ad703e0f2957bb65ebf/scripts/synthetic/evaluate.py), fonctions `charger_lot` et `verifier_sources` ; [validation.py](https://github.com/datatigersNLP/data_tigers_nlp/blob/bb80096aa2164e60f7db4ad703e0f2957bb65ebf/scripts/synthetic/validation.py), fonction `valider_proposition`.

Ce cas ne démontre ni fuite d'annotation ni appel réel de modèle. Il montre que le drapeau `passed` n'est pas une réexécution complète des règles techniques actuelles. Le lecteur revalide déjà la structure et les extraits, mais pas toutes les règles du générateur.

Avant de considérer le format comme accepté, trancher explicitement : rejouer les règles techniques applicables à l'entrée, ou exiger et examiner la preuve de leur exécution dans la provenance du lot. Recommandation : partager ces contrôles avec le générateur, en conservant la question et les verdicts humains intacts, et ajouter la régression de ce contre-exemple. Ne pas assimiler cette vérification à un jugement sur la fausseté de la prémisse.

## Contrôles réellement exécutés pour cette revue

Les **31 tests de `test_evaluate.py` réussissent** dans la copie de revue. Environnement présent : Python 3.12.14, Pydantic 2.13.4, NumPy 2.3.5. La provenance Git est simulée dans cette exécution pour la copie de fichiers ; index, E5, tokeniseur et API du modèle sont simulés par les fixtures. Les vrais helpers de contexte sont exercés par les tests existants. Un contre-essai supplémentaire compare l'admission du cas sans « ? » au refus par le validateur de génération.

Le résultat initial de **180 tests avec le verrou** est celui rapporté par l'auteur de #144 ; les 180 n'ont pas été relancés pour cette revue. Les versions présentes ici diffèrent du verrou de la PR : cette passe de contrôle ne s'y substitue pas. Aucun modèle réel ni aucune question du pilote n'a été généré.

Les empreintes du corpus source complet sont également contrôlées pour la préparation : 4 240 passages, 261 fiches, en-tête `586cf190…`, passages `aee5bbdb…`. La matrice n'a pas été lue et aucune génération RAG n'a été appelée.

## Limites et suite

L'identité du relecteur et l'indépendance ne peuvent pas être certifiées par les booléens du manifeste. Il faut des traces de génération, des sources distinctes de la mise au point, une vraie grille humaine et un gel avant réponses du RAG. Les dates de relecture et la provenance du générateur ne figurent pas comme champs structurés dédiés dans le manifeste proposé : les pièces à examiner doivent être rattachées à la note de séparation et conservées.

Le [dossier préparatoire](README.md) fournit des sources provisoires et une grille vierge. Aucun nouveau cas n'est accepté et la PR #144 reste inchangée par cette revue. La relecture humaine du lanceur et du contrat, le traitement du point ci-dessus, puis l'essai réel restent nécessaires.
