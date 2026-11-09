# Préparer un pilote Agent0 indépendant

Préparation du 9 novembre 2026 pour #95/#96. **Aucune question générée, aucun verdict humain et aucun lot figé.** Le lanceur proposé reste dans la [PR #144](https://github.com/datatigersNLP/data_tigers_nlp/pull/144). Ce dossier prépare les éléments à examiner pendant l'attente ; il ne déclare pas la livraison complète de #96 et ne remplace pas la décision de reprise de l'évaluation.

## Contenu prêt à examiner

| Fichier | Contenu | État |
|---|---|---|
| [preparation.json](preparation.json) | Plan de 25 emplacements, algorithme de sélection et points à confirmer | Non figé ; zéro candidat |
| [sources_m2.json](sources_m2.json) | 25 passages complets répartis sur 20 fiches nouvelles pour la mise au point | Sources provisoires, textes et empreintes contrôlés |
| [grille_relecture.json](grille_relecture.json) | 25 lignes avec champs humains vierges | Aucun nom, verdict ou attente prérempli |
| [revue_lanceur_144.md](revue_lanceur_144.md) | Revue assistée et contre-exemple du contrat d'entrée | Un point technique à traiter avant l'export du lot |

Les trois fiches historiques (congé sans solde, médaille du travail et attributions du CSE en santé/sécurité) sont exclues. Les 15 anciens candidats restent exclus de toute réutilisation, même renommés ou relus.

La répartition vise cinq emplacements par catégorie : 5 simples, 5 reformulations, 5 multi-passages, 5 pièges et 5 hors corpus. **Ce ne sont pas des quotas d'acceptation.** Les 20 premiers emplacements ont des sources provisoires distinctes par fiche. Les cinq hors corpus n'ont volontairement ni source affectée ni question : la méthode doit être revue avant leur construction. Le générateur historique qui part d'un passage couvert n'a pas démontré une méthode hors corpus fiable.

## Comment les sources ont été préparées

Référence : corpus M2 de `dev/a294d252d1ecc285dfd7df88e43a3ec5df891fe7`, 4 240 passages, 261 fiches. Les octets de l'en-tête et du JSON complet ont les empreintes `586cf190…` et `aee5bbdb…` consignées intégralement dans le fichier de sources. La matrice n'a pas été chargée ; son empreinte est reprise de l'en-tête.

Sélection déterministe `sha256-fiches-puis-passages-v1`, graine textuelle `20261109` :

1. Grouper les passages par URL de fiche sans ancre ni barre finale ; retirer les trois URLs du support de mise au point.
2. Trier les fiches par SHA-256 de l'UTF-8 `20261109|fiche|URL`, puis URL en cas d'égalité.
3. Parcourir les catégories dans l'ordre déclaré dans `preparation.json`. Prendre la première fiche restante avec au moins un passage, ou deux pour multi-passage, puis retirer cette fiche des possibilités suivantes.
4. Dans chaque fiche, trier les passages par SHA-256 de `20261109|passage|passage_id`, puis identifiant ; prendre un passage, ou deux pour multi-passage.

Aucune question ou annotation du jeu humain n'a été lue pour ce tirage ; aucune sortie RAG n'a guidé le choix. Les textes sont copiés exactement du corpus figé. La paire tirée ne prouve pas que ses deux passages sont nécessaires à une réponse : ce sera un contrôle humain.

**Portée de l'indépendance :** seules les trois fiches de mise au point sont exclues par cette préparation. Le chevauchement avec les données d'adaptation n'a pas été vérifié. Avant le gel, documenter ce rapprochement et décider du périmètre de comparaison ; ne pas annoncer un jeu entièrement inconnu de l'adaptation. Les candidats futurs ne doivent pas alimenter l'entraînement. Le jeu humain et son protocole restent inchangés.

Le tirage n'établit ni représentativité ni puissance statistique. Ne pas remplacer silencieusement une fiche ou un candidat après lecture des réponses du RAG. Une modification du plan avant génération crée une nouvelle version avec son motif et ses empreintes.

## Étapes restantes, dans l'ordre

### 1. Arrêter le protocole de ce petit pilote

Relire le lanceur et son format, traiter le point sur la revalidation des contrôles automatiques, confirmer le responsable de la relecture indépendante et la disponibilité de l'équipe. La décision du 30/10 dans #13 garde la mesure officielle et l'adaptation prioritaires ; elle ne devient pas une autorisation d'inférence par la création de ce dossier.

Définir la méthode hors corpus et ses contre-preuves avant de produire ces cinq emplacements. Une catégorie peut rester sans cas retenu. Il n'y a pas de tentative supplémentaire automatique pour remplir les cases.

### 2. Figer le générateur et préparer les appels

Avant toute génération, consigner le commit exact du générateur, les versions des prompts, les paramètres, le digest du modèle et la version d'Ollama constatée sur le Legion. La graine de sélection des sources ne remplace pas la graine des appels de génération.

Créer des sélections de génération avec les outils existants à partir des identifiants préparés ; les comparer au corpus complet. Utiliser de nouveaux identifiants de runs. Le nombre maximal visé reste 25 candidats, avec un appel par emplacement et conservation des rejets et erreurs ; pas de réparation ou remplacement silencieux. L'efficacité des nouveaux cas n'est pas présumée.

### 3. Produire les candidats, puis faire relire

Conserver les originaux, les prompts, les paramètres et les traces. Rattacher chaque fichier de candidat à son emplacement et à son empreinte ; aucun emplacement vide de cette grille n'est déjà un `CasSynthetique`.

Le relecteur humain distinct de l'auteur examine la question exacte, les conditions et exceptions, les preuves, les doublons de sens et la difficulté seulement visée. Pour multi-passage : chaque source doit être nécessaire et l'ensemble suffisant. Pour piège : la fausse prémisse doit réellement être présupposée par la question et corrigible par les sources. Pour hors corpus : examiner le corpus figé, tracer méthodes, termes, passages et contre-preuves ; l'échec d'une recherche ou l'avis du modèle ne prouve pas une absence.

Remplir nom, date, décision, répondabilité, justification et points attendus seulement après cette intervention. Les décisions possibles sont accepté, rejeté ou incertain ; un incertain reste `pending`. Une erreur de classement ne se corrige pas en changeant silencieusement le type. Les décisions ne sont ni créées ni appliquées automatiquement par ce dossier.

### 4. Exporter et figer les seuls cas acceptés

Exporter vers un dossier hors Git distinct : `questions.jsonl` et `manifest.json` du format proposé `agent0-challenge-v1`, seulement après acceptation du contrat de #144. Conserver aussi tous les rejets et incertains à part, sans les faire évaluer comme acceptés.

Renseigner les empreintes exactes du JSONL final, des passages et de la matrice, l'effectif entre 1 et 25, la date de gel avec fuseau, et une note de séparation vérifiable. La note renvoie au générateur figé, à ses traces, aux sources, à la grille signée par les relecteurs et aux vérifications de séparation. Le champ `pilote_independant: true` ne remplace pas ces éléments.

Ce dossier préparatoire n'est pas cet export : il ne contient pas de `questions.jsonl` ni de manifeste de gel accepté, et son format est volontairement distinct.

### 5. Vérifier puis exécuter, après autorisation

Le contrôle `--check-lot` de #144 est un contrôle des déclarations et du JSONL ; le contrôle du corpus et des extraits intervient au début de l'exécution, avant E5 et Ollama. Ne pas présenter le premier comme un contrôle complet du corpus ou une validation sémantique.

Après la vraie relecture du lanceur et du lot, préparer l'environnement isolé, puis effectuer un essai réel borné avec un nouveau run. Le manifeste et le lot à comparer sont figés avant toute réponse du RAG. Les paramètres d'un essai ne sont pas ajustés sur les réponses du lot. Les métriques et conclusions de #97 restent un travail distinct.

## Points ouverts

- [ ] Revalidation des contrôles de génération dans #144 ou décision explicite sur le contrat d'entrée.
- [ ] Autorisation et périmètre de reprise, disponibilité et relecteur indépendant confirmés.
- [ ] Séparation avec les données d'adaptation vérifiée et documentée.
- [ ] Méthode hors corpus arrêtée.
- [ ] Générateur, prompts, paramètres et environnement figés avant génération.
- [ ] Candidats effectivement produits, relus et lot final figé avant RAG.

**Traçabilité IA :** [note du 9 novembre](../../journal/2026-11-09_agent0_pilote_preparation_revue.md). La préparation ne déclare ni charge réelle, ni validation humaine, ni résultat de benchmark.
