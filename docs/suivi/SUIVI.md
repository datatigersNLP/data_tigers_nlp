# Classeur de suivi

**Équipe** Data Tigers
**Module** NLP 2, Master 2 Data & IA, FGES
**Ouvert le** 19 septembre 2026
**Dernière mise à jour** 18 octobre 2026 (fermeture de #43 et #53, statuts de #11, #46, #50 et #56 alignés sur GitHub, tag `volet-a-v1` ; fermeture de #23, tickets #91 à #98 ajoutés, par Mahé ; 25 octobre 2026 : Vaneck ajouté à #51, tickets #107 et #111 ajoutés ; calendrier jusqu'à J4 reporté dans les tickets, tickets #112 à #114 ajoutés, jalons de #8, #52, #107 et #91 à #97, Maïmouna et Vaneck assignés à #52, par Mahé ; 26 octobre 2026 : début du travail sur #52 daté, points opérationnels de #49, #52 et #107 ; soutenance avancée au 30/11 : jalon J4 au 30/11, #52 en J3, échéances resserrées ; revue de la #108 traitée, format des données d'adaptation proposé, PR #116, par Mahé ; 27 octobre 2026 : #85, #100, #101, #109 et #118 fusionnées, faisabilité du Legion, script de mesure, premier jet des supports de J3, par Mahé ; 30 octobre 2026 : #105, #116 et #117 fusionnées, décisions sur les machines, Agent0, #49 et le Weekly 9, protocole et script après la calibration, charges de #51 et #111, par Mahé)

**Objet.** Suivre les tâches, leurs responsables et leur chronologie, comme le demande le sujet. Ce classeur complète le board GitHub, qui porte l'état des tickets, en conservant ce que le board ne restitue pas : la charge estimée face à la charge réelle.

**Pourquoi cette colonne compte.** Le rapport final devra traiter « les écarts entre charge estimée et charge réelle, et analyse des causes de sous-estimation ». Cette information ne se reconstitue pas en décembre. Elle se note au moment où la tâche se termine, ou elle est perdue.

**Responsable de la tenue** Jibril BENSALEM.

---

## Règles de suivi

1. Toute action dispose d'un ticket et d'une ligne de suivi avant son démarrage.
2. L'estimation initiale se note avant le démarrage ; une estimation manquante ne se reconstruit jamais après coup. Pour un travail engagé, une estimation du reste à faire peut être ajoutée, datée et distincte de l'estimation initiale.
3. La charge réelle se note à la clôture. Elle représente le travail actif déclaré ; le temps d'attente passif se distingue si nécessaire.
4. L'écart vaut charge réelle moins charge estimée. Il n'est calculé que si les deux valeurs sont connues et comparables, sans mélanger charge individuelle et charge d'équipe.
5. Les dates de travail sont déclarées par les personnes concernées. Les dates d'ouverture et de clôture GitHub restent séparées.
6. Après chaque Weekly, Jibril vérifie le suivi et le board ; les réunions consignent décisions, actions, responsables, échéances et blocages.
7. Les valeurs sont conservées avec leur provenance. Une fermeture GitHub n'est pas à elle seule une preuve de validation du dernier livrable.

**Légende.** NR = information non renseignée dans les sources consultées, sans conclusion sur sa valeur réelle. « non estimée » = absence d'estimation initiale explicitement déclarée. P = estimation provisoire de planification, à réviser ; elle n'est pas une charge réelle. Dans la colonne Clôturé, « - » = ticket ouvert. Dans la colonne Réel, « - » = ticket ouvert sans charge réelle déclarée ; cela ne signifie pas qu'aucun travail n'a commencé. Dans la colonne Jalon, « - » = aucun milestone GitHub affecté. Un écart NR ne vaut pas zéro.

## Domaines

| Code | Domaine | Principal | Secondaire ou soutien |
|---|---|---|---|
| D1 | Corpus et segmentation | Maïmouna, Vaneck | Jibril |
| D2 | Encodeur et index | Remy | Mahé |
| D3 | Front et déploiement du volet A | Maïmouna, Vaneck | Remy, Mahé |
| D4 | Socle RAG et inférence locale | Jibril | Remy |
| D5 | Adaptation et évaluation du volet B | Mahé | Jibril |

La répartition par domaine est conservée. Les responsabilités d'un ticket peuvent être plus précises : ses consignes font foi. #35 reste rattaché à D1, comme son corps le demande ; la présence d'un label d'évaluation ne le transforme pas en responsabilité D5.

## Jalons enregistrés dans GitHub

| Jalon | État GitHub | Échéance enregistrée | Portée de la date |
|---|---|---|---|
| J2 Cadrage et étude des volets | Fermé | 21/09/2026 | Livrable remis ; jalon fermé, commentaire de #8. |
| Mi-parcours Volet A en ligne | Ouvert | Aucune | Date officielle en attente (#8) ; ancienne échéance du 01/10 retirée. Aucun ticket ouvert depuis le 25/10, #8 étant passé en J3 ; fermeture laissée à la décision du lead technique. |
| J3 Volet A fonctionnel | Ouvert | 16/11/2026 | Date à confirmer par écrit (#8), malgré la date enregistrée dans GitHub. |
| J4 Soutenance | Ouvert | 30/11/2026 | Avancée du 07/12 au 30/11 : information transmise par Mahé le 26/10, confirmation écrite à joindre à #8. L'équipe fixe la fin du projet au 20/11. |

Le calendrier officiel reste à confirmer par écrit dans #8. L'échéance opérationnelle du volet A, retenue au Weekly 4, est le 18/10/2026 ; elle ne remplace pas une confirmation officielle des jalons.

**Tags et branche d'observation** (#43). `jalon-j2` (27/09/2026) ; `jeu-questions-v1` (06/10/2026, jeu figé) ; `mi-parcours`, tag annoté posé a posteriori le 17/10/2026 sur `ac84ed3`, version du site en ligne du 30/09 au 11/10 (PR #32 et #42 livrées ; PR #41, première inférence locale, fusionnée le 03/10) ; branche d'observation `observation/mi-parcours` créée depuis ce tag, à ne plus modifier. `volet-a-v1`, tag annoté de fin du volet A posé le 18/10/2026 sur `8955962`, fusion dans `main` de la PR #84 approuvée par Jibril ; il contient la première inférence locale (PR #41).

## Inventaire des tickets au 25/10/2026

Les 59 lignes ci-dessous reprennent les issues du dépôt, sans les pull requests. Titres, assignés, milestones, états et dates proviennent de l'API GitHub. Les dates sont affichées à l'heure de Paris. L'état Ouvert/Fermé est celui de l'issue, pas le statut du Project Board ; il ne permet pas de conclure Todo, In progress ou Done.

La colonne « Assignés GitHub » inclut les responsables et les soutiens sans les confondre avec les rôles définis dans le corps du ticket. NR signifie ici qu'aucun assigné n'est enregistré, pas que la réunion n'avait aucun participant.

| Ticket | Tâche | Domaine | Assignés GitHub | Jalon | État GitHub | Ouvert | Clôturé |
|---|---|---|---|---|---|---|---|
| #1 | Création du repo GitHub | transverse | Mahé, Remy | - | Fermé | 12/09/2026 | 12/09/2026 |
| #2 | Weekly 1 | transverse | Tous | J2 | Fermé | 14/09/2026 | 19/09/2026 |
| #3 | Choix des cas d'usages | transverse | Tous | J2 | Fermé | 19/09/2026 | 20/09/2026 |
| #4 | Choix du modèle d'embeddings | D2 | Mahé, Remy | J2 | Fermé | 19/09/2026 | 20/09/2026 |
| #5 | Livrable J2 | transverse | Tous | J2 | Fermé | 19/09/2026 | 20/09/2026 |
| #6 | Weekly 2 | transverse | Tous | J2 | Fermé | 19/09/2026 | 20/09/2026 |
| #7 | Choix de la chaîne front-end du volet A | D3 | Mahé, Vaneck, Maïmouna | J2 | Fermé | 20/09/2026 | 20/09/2026 |
| #8 | Faire confirmer le calendrier officiel des jalons | transverse | Jibril | J3 | Ouvert | 20/09/2026 | - |
| #9 | Weekly 3 - 30 septembre 2026 | transverse | Tous | J3 | Fermé | 20/09/2026 | 05/10/2026 |
| #10 | Weekly 4 - 7 octobre 2026 | transverse | Tous | J3 | Fermé | 20/09/2026 | 07/10/2026 |
| #11 | Weekly 5 - 14 octobre 2026 | transverse | Tous | J3 | Fermé | 20/09/2026 | 14/10/2026 |
| #12 | Weekly 6 - 21 octobre 2026 | transverse | Tous | J3 | Fermé | 20/09/2026 | 26/10/2026 |
| #13 | Weekly 7 - 28 octobre 2026 | transverse | Tous | J3 | Ouvert | 20/09/2026 | - |
| #14 | Weekly 8 - 4 novembre 2026 | transverse | Tous | J3 | Ouvert | 20/09/2026 | - |
| #15 | Weekly 9 - 11 novembre 2026 | transverse | Tous | J3 | Ouvert | 20/09/2026 | - |
| #16 | Weekly 10 - 18 novembre 2026 | transverse | Tous | J3 | Ouvert | 20/09/2026 | - |
| #17 | Weekly 11 - 25 novembre 2026 | transverse | Tous | J4 | Ouvert | 20/09/2026 | - |
| #18 | Weekly 12 - 2 décembre 2026 | transverse | Tous | J4 | Ouvert | 20/09/2026 | - |
| #19 | Weekly 13 - 9 décembre 2026 | transverse | Tous | J4 | Ouvert | 20/09/2026 | - |
| #20 | Formaliser les règles de fonctionnement et les critères de validation | transverse | Tous | Mi-parcours | Fermé | 20/09/2026 | 30/09/2026 |
| #21 | Proposer les modèles de tickets, pull requests et Weeklys | transverse | Mahé, Jibril | Mi-parcours | Fermé | 20/09/2026 | 30/09/2026 |
| #22 | Discuter et valider les modèles de travail en Weekly 3 | transverse | Tous | Mi-parcours | Fermé | 20/09/2026 | 05/10/2026 |
| #23 | Construire et prioriser le backlog détaillé jusqu'au mi-parcours | transverse | Tous | Mi-parcours | Fermé | 20/09/2026 | 18/10/2026 |
| #24 | Mettre en place le registre des risques, hypothèses et décisions | transverse | Tous | Mi-parcours | Fermé | 20/09/2026 | 30/09/2026 |
| #25 | Définir la méthode de suivi des outils novateurs | transverse | Vaneck, Maïmouna | Mi-parcours | Fermé | 20/09/2026 | 10/10/2026 |
| #26 | Réunion d'avancement - 23 septembre 2026 | transverse | NR | J2 | Fermé | 23/09/2026 | 27/09/2026 |
| #27 | Télécharger, filtrer et contrôler le corpus | D1 | Vaneck, Jibril, Maïmouna | Mi-parcours | Fermé | 23/09/2026 | 28/09/2026 |
| #28 | Vérifier et garantir 40 Gio libres sur la machine de référence | D4 | Mahé, Jibril | Mi-parcours | Fermé | 23/09/2026 | 30/09/2026 |
| #29 | Déployer une page statique à l'URL définitive | D3 | Mahé, Vaneck, Remy, Maïmouna | Mi-parcours | Fermé | 23/09/2026 | 30/09/2026 |
| #30 | Générer un index précalculé sur un corpus réduit | D2 | Mahé, Remy | Mi-parcours | Fermé | 23/09/2026 | 30/09/2026 |
| #31 | Réaliser une première inférence locale | D4 | Remy, Jibril | Mi-parcours | Fermé | 23/09/2026 | 28/09/2026 |
| #33 | Versionner les documents préparatoires du jalon J2 | transverse | Mahé | Mi-parcours | Fermé | 27/09/2026 | 06/10/2026 |
| #34 | Corriger la session 9 du journal d'usage IA et régénérer son PDF | transverse | Mahé, Remy | Mi-parcours | Fermé | 27/09/2026 | 28/09/2026 |
| #35 | Explorer le découpage du corpus depuis la source SocialGouv | D1 | Mahé | J3 | Fermé | 27/09/2026 | 28/09/2026 |
| #43 | Poser le jalon de mi-parcours : tag Git et branche d'observation | transverse | Mahé, Jibril | Mi-parcours | Fermé | 30/09/2026 | 18/10/2026 |
| #44 | Construire le jeu de questions annotées pour évaluer la recherche | D1, D5 | Vaneck, Jibril, Maïmouna | J3 | Fermé | 30/09/2026 | 07/10/2026 |
| #45 | Valider la chaîne de mesure de la recherche sur le jeu PIAF | D2 | Mahé, Remy | J3 | Fermé | 30/09/2026 | 06/10/2026 |
| #46 | Évaluer la recherche du volet A sur le jeu de questions (notebook 03) | D2, D5 | Mahé, Remy | J3 | Fermé | 30/09/2026 | 17/10/2026 |
| #47 | Construire les références lexicales TF-IDF et BM25 | D2 | Mahé, Remy | J3 | Fermé | 30/09/2026 | 13/10/2026 |
| #48 | Brancher la recherche sémantique dans le site du volet A | D3 | Mahé, Vaneck, Remy, Maïmouna | J3 | Fermé | 30/09/2026 | 12/10/2026 |
| #49 | Ajuster finement l'encodeur sur le corpus | D2, D5 | Mahé, Remy, Jibril | J4 | Ouvert | 30/09/2026 | - |
| #50 | Réduire le poids du modèle servi par réduction du vocabulaire | D2 | Mahé, Remy | J3 | Fermé | 30/09/2026 | 17/10/2026 |
| #51 | Construire la chaîne RAG du volet B sur l'index commun | D4 | Remy, Jibril, Maïmouna, Vaneck | J3 | Ouvert | 30/09/2026 | - |
| #52 | Mesurer le volet B avant adaptation | D5 | Mahé, Jibril, Maïmouna, Vaneck | J3 | Ouvert | 30/09/2026 | - |
| #53 | Peaufiner l'interface et le parcours utilisateur du site du volet A | D3 | Vaneck, Jibril | J3 | Fermé | 30/09/2026 | 18/10/2026 |
| #56 | Préparer le jeu complémentaire de requêtes du CDTN | D5 | Mahé, Vaneck, Jibril, Maïmouna | J3 | Fermé | 04/10/2026 | 14/10/2026 |
| #91 | [Agent0 Light] A1 — Définir le schéma et les règles du Challenge Set | D5 | Jibril | J3 | Ouvert | 18/10/2026 | - |
| #92 | [Agent0 Light] A2 — Sélectionner et tracer les passages sources M2 | D5 | Jibril | J3 | Ouvert | 18/10/2026 | - |
| #93 | [Agent0 Light] A3 — Générer localement des questions simples et reformulées | D5 | Jibril | J3 | Ouvert | 18/10/2026 | - |
| #94 | [Agent0 Light] A4 — Ajouter les cas multi-passages, pièges et hors corpus | D5 | Jibril | J4 | Ouvert | 18/10/2026 | - |
| #95 | [Agent0 Light] A5 — Relire et figer un premier Challenge Set pilote | D5 | Jibril | J4 | Ouvert | 18/10/2026 | - |
| #96 | [Agent0 Light] B1 — Exécuter le RAG sur un Challenge Set figé | D5 | Jibril | J4 | Ouvert | 18/10/2026 | - |
| #97 | [Agent0 Light] B2 — Mesurer les résultats et diagnostiquer les erreurs du RAG | D5 | Jibril | J4 | Ouvert | 18/10/2026 | - |
| #98 | [Agent0 Light] C1 — Générer un nouveau lot ciblé sur les faiblesses détectées | D5 | Jibril | - | Ouvert | 18/10/2026 | - |
| #107 | Adapter le modèle du volet B (Qwen2.5-7B) et le mesurer avant et après | D5 | Mahé, Remy, Jibril | J4 | Ouvert | 23/10/2026 | - |
| #111 | Démonstration locale du volet B : interface de l'assistant et vidéo | D3, D4 | Vaneck, Maïmouna | J4 | Ouvert | 25/10/2026 | - |
| #112 | Préparer les supports de présentation du jalon J3 | transverse | Tous | J3 | Ouvert | 25/10/2026 | - |
| #113 | Rapport final : V1 livrée strictement avant J4 | transverse | Tous | J4 | Ouvert | 25/10/2026 | - |
| #114 | Préparer la soutenance J4 : pitch, présentation, vidéo de secours du volet A, répétition et envoi | transverse | Tous | J4 | Ouvert | 25/10/2026 | - |

## Charges et dates de travail

Charges en heures, dates de travail en 2026. Chaque issue possède une ligne, même lorsque sa charge n'est pas renseignée. Les dates de clôture GitHub de l'inventaire ne sont pas recopiées comme dates de fin de travail.

| Ticket | Début du travail | Fin du travail | Estimé | Réel | Écart |
|---|---|---|---|---|---|
| #1 | 12/09 | 12/09 | NR | NR | NR |
| #2 | 14/09 | 14/09 | NR | NR | NR |
| #3 | 19/09 | 19/09 | NR | NR | NR |
| #4 | 19/09 | 19/09 | NR | NR | NR |
| #5 | 19/09 | NR | NR | NR | NR |
| #6 | 19/09 | NR | NR | NR | NR |
| #7 | NR | NR | NR | NR | NR |
| #8 | NR | NR | NR | - | NR |
| #9 | NR | NR | NR | NR | NR |
| #10 | NR | NR | NR | NR | NR |
| #11 | NR | NR | NR | - | NR |
| #12 | NR | NR | NR | - | NR |
| #13 | NR | NR | NR | - | NR |
| #14 | NR | NR | NR | - | NR |
| #15 | NR | NR | NR | - | NR |
| #16 | NR | NR | NR | - | NR |
| #17 | NR | NR | NR | - | NR |
| #18 | NR | NR | NR | - | NR |
| #19 | NR | NR | NR | - | NR |
| #20 | NR | NR | NR | NR | NR |
| #21 | NR | NR | NR | NR | NR |
| #22 | NR | NR | NR | NR | NR |
| #23 | NR | NR | NR | - | NR |
| #24 | NR | NR | NR | NR | NR |
| #25 | 06/10 | 07/10 | non estimée | 2 | NR |
| #26 | NR | NR | NR | NR | NR |
| #27 | 26/09 | 28/09 | 8 | 10 | +2 |
| #28 | NR | NR | NR | NR | NR |
| #29 | 30/09 | 30/09 | 3 | 1.5 | -1.5 |
| #30 | NR | NR | NR | NR | NR |
| #31 | NR | NR | 4 | NR | NR |
| #33 | NR | NR | NR | NR | NR |
| #34 | NR | NR | NR | NR | NR |
| #35 | NR | NR | NR | NR | NR |
| #43 | NR | NR | NR | - | NR |
| #44 | 03/10 | 07/10 | non estimée | 18 | NR |
| #45 | 03/10 | 03/10 | 4 | 3.5 | -0.5 |
| #46 | NR | NR | NR | - | NR |
| #47 | 04/10 | 04/10 | 4 | 3.5 | -0.5 |
| #48 | NR | NR | NR | NR | NR |
| #49 | NR | NR | NR | - | NR |
| #50 | NR | NR | NR | - | NR |
| #51 | NR | NR | 16, plus 6 pour Vaneck et Maïmouna (28/10) | relectures de la #85 : Vaneck 2 h, Maïmouna 2 h 30 | NR |
| #52 | 23/10 | NR | non estimée | - | NR |
| #53 | NR | NR | 16 (P) | - | NR |
| #56 | NR | NR | NR | - | NR |
| #91 | 18/10 | NR | NR | - | NR |
| #92 | 18/10 | NR | NR | - | NR |
| #93 | 18/10 | NR | NR | - | NR |
| #94 | NR | NR | NR | - | NR |
| #95 | NR | NR | NR | - | NR |
| #96 | NR | NR | NR | - | NR |
| #97 | NR | NR | NR | - | NR |
| #98 | NR | NR | NR | - | NR |
| #107 | 23/10 | NR | NR | - | NR |
| #111 | NR | NR | 24, cumulées pour Vaneck et Maïmouna (28/10) | - | NR |
| #112 | NR | NR | NR | - | NR |
| #113 | NR | NR | NR | - | NR |
| #114 | NR | NR | NR | - | NR |

### Provenance des valeurs connues

- #1 à #6 : dates déjà présentes dans le suivi de dev, conservées. Elles ne sont pas déduites de l'API ; les cellules historiquement vides sont NR. Les dates des réunions se lisent également dans la section Réunions.
- #25 : du 06/10 au 07/10, « non estimée », 2 h ; ligne existante de dev conservée.
- #27 et #29 : données déclarées par Vaneck, transmises par Jibril le 11/10 et reprises dans la PR #69. #27 : 8 h estimées, 10 h réelles, du 26 au 28/09, Vaneck et Maïmouna, soutien Jibril. #29 : 3 h estimées, 1 h 30 réelle, le 30/09, Vaneck et Maïmouna. Pour #27, Vaneck attribue les 2 h supplémentaires au mauvais découpage du corpus source (#35, PR #39). 1.5 h = 1 h 30.
- #31 : estimation initiale de 4 h de travail actif dans le commentaire de Jibril sur le ticket ; aucune charge réelle n'a été trouvée. Le téléchargement passif est suivi séparément.
- #44 : 18 h cumulées pour Jibril, Maïmouna et Vaneck, déjà dans le ticket ; dates du 03/10 au 07/10 et mention « non estimée » demandées dans la revue de la PR #69 et confirmées par Jibril le 13/10. Aucune répartition individuelle ni estimation historique reconstruite.
- #45 et #47 : lignes existantes de dev conservées, 4 h estimées et 3.5 h réelles chacune, écart -0.5 h ; dates du 03/10 pour #45 et du 04/10 pour #47.
- #51 : 16 h cumulées pour Jibril et Maïmouna, validées par Jibril le 12/10 avant le développement, selon le corps du ticket. Répartition indicative de 8 h chacun, à ajuster.
- #53 : 16 h cumulées provisoires pour Vaneck et Jibril, inscrites le 13/10 à la demande de Jibril. Proposition assistée par IA : 4 h d'analyse et de choix UI/UX, 8 h de réalisation, 4 h de contrôles et documentation. Aucune répartition individuelle imposée ; à réviser après le cadrage et à distinguer du reste à faire si le travail a commencé.

- #52 : travail commencé le 23/10, à l'ouverture de la PR #108 qui en écrit le protocole ; aucune estimation n'avait été déclarée avant, dans le ticket ni dans ses commentaires (vérifié le 26/10).

Les charges déclarées cumulées pour plusieurs membres ne sont pas divisées automatiquement. Les durées d'exécution d'un modèle ou d'un script ne sont pas des charges de travail humain.

## Points opérationnels à suivre

Cette section reprend les dates et dépendances écrites ; elle ne décide pas de nouvelles priorités.

| Ticket | Date ou condition écrite | Situation vérifiée et point à suivre |
|---|---|---|
| #8 | Confirmation écrite attendue | Ouvert ; J3 et J4 gardent une date GitHub à confirmer. Au 25/10 : relance de l'enseignant prévue le 26/10 par Mahé (dates de J3 et J4, risque R4) ; ticket passé au jalon J3. Au 26/10 : J4 avancée au 30/11 (information de Mahé), jalon GitHub corrigé ; fin du projet fixée au 20/11 par l'équipe. Le 27/10 : relance abandonnée par Mahé, l'enseignant communiquera. |
| #23 | 03/10, cible provisoire dans le corps | Fermé le 18/10 comme non réalisé, par décision du lead technique : horizon du mi-parcours dépassé ; 37 tickets sur 46 sans estimation, aucune validation collective du backlog, aucune capture du board versionnée. |
| #43 | Date officielle du mi-parcours | Au 18/10 : tag `mi-parcours` et branche `observation/mi-parcours` posés a posteriori le 17/10 ; `main` mise à jour par la PR #74 (Jibril). **Critère de #43 non satisfait par ce tag historique** : la première inférence locale, réussie le 27/09 (#31), n'a été fusionnée dans `dev` que le 03/10 (PR #41), après `ac84ed3`. Écart déclaré dans le message du tag ; arbitrage du 18/10 (Mahé) : le tag n'est pas déplacé, #43 est validé avec cette réserve et fermé le 18/10. Le jalon de fin du volet A est le tag `volet-a-v1`, posé sur `main` après la PR #84 ; il contient la première inférence locale. |
| #44 | Ticket fermé | Le jeu figé reste la référence ; ce suivi ne modifie ni les questions ni le protocole. |
| #46 | 14/10, proposition dans le ticket | Fermé le 17/10 à 15 h 52 : mesure unique faite le 13/10, rapport fusionné le 14/10 (PR #73). |
| #49 | Corps : 31/10 proposé ; commentaires : gel 13/10, Weekly 14/10, mesure 15/10, cible 18/10 | Au 17/10 : PR #63 et protocole 05 fusionnés le 14/10 ; mesure non faite au 16/10, donc règle de repli : encodeur de base servi pour le 18/10. Mesure possible ensuite, pour le rapport. Corps actualisé le 25/10 : notebook 05 et mesure descriptive par Mahé, relus par Remy, pour le 20/11, sans effet sur le modèle servi. Audit du 26/10 : poids, q8 et index de l'ajusté conformes aux empreintes du protocole 05 ; q8 du témoin à régénérer ; notebook 05 et extension de la page d'encodage jamais réalisés. Le 26/10 : maintien ou abandon à décider au Weekly 7, la mesure ne tenant plus dans le calendrier resserré (option : Remy, pour le 13/11). Le 30/10 : mesure non maintenue, décision de Mahé révisable au Weekly 8 ; ticket ouvert jusque-là. |
| #50 | 24/10, proposition dans le ticket | Au 17/10 : élagage sans perte livré le 14/10 (PR #78), modèle de 65,7 Mio servi par le site ; la réduction avec perte sort du volet A. |
| #51 | 10/10, proposition historique ; corps actualisé le 25/10 : PR #85 fusionnée le 27/10, reproduction et exemples commentés au Weekly 8 (04/11) | Ouvert ; chaîne RAG complète non déduite du test d'inférence de #31. La fusion de la PR #85 conditionne la mesure (#52), les données d'adaptation (#107) et le branchement de la démonstration (#111). Le 27/10 : PR #85 fusionnée par Jibril. |
| #52 | Corps resserré le 26/10 : seuil S fait le 26/10, script 30/10, gel 02/11, mesure avant 03/11, jugement et défauts 13/11 | Ouvert ; dépend du jeu figé, de la chaîne RAG (PR #85) et du gel du protocole (PR #108). Seuil S calculé le 26/10 (0,8565). Revenu au jalon J3 le 26/10, sa clôture étant prévue le 13/11. Revue de Jibril du 26/10 traitée dans la #108 (`c8eb115`), relecture redemandée. Le 27/10 : #108 approuvée par Jibril ; script de mesure en PR #119. Le 30/10 : calibration du 29/10 par Jibril ; #119 corrigée (`f501793`) et #108 complétée (`a612c20`), relectures redemandées ; gel le 02/11 si tout est prêt, sinon le 03/11. Verrou indépendant des fins de ligne (`f170903`, `f231c17`). |
| #53 | 17/10, demandé à Jibril avec Vaneck | Au 18/10 : interface B livrée par Vaneck (PR #80), puis focus du menu sur téléphone et périmètre du corpus affiché (PR #83, revue de Jibril) ; ticket fermé à la fusion de la PR #83. Estimation provisoire de 16 h non révisée. |
| #56 | Avant la première mesure de #46 | Fermé le 14/10 ; les trois relectures sont importées (PR #79, fusionnée le 17/10) : 182 jugements, 155 requêtes. |
| #91 à #98 | Échéances proposées en commentaire le 25/10 : #91 et #92 le 27/10, #93 le 30/10, fusion des #103 et #106 le 06/11 ; la suite de #94 à #97, prévue jusqu'au 30/11, est à décider au Weekly 7 (commentaires du 26/10) ; #98 facultatif | Jalons : J3 pour #91 à #93, J4 pour #94 à #97, aucun pour #98. Agent0 passe après l'adaptation (#107) et la mesure (#52). Le 27/10 : #100 (A2) et #101 (A3) fusionnées par Jibril, après la #99 (A1) le 26/10 ; #91 à #93 restent ouverts, une fusion dans `dev` ne fermant pas les tickets ; #103 et #106 à mettre à jour avec `dev`. Le 30/10 : livrable limité au socle et aux #103 et #106 ; #96 à #98 hors du périmètre, décision de Mahé révisable au Weekly 8. |
| #107 | Corps resserré le 26/10 : Legion 27/10, gel 02/11, mesure avant et données 03/11, échantillon 05/11, entraînement 06/11, adaptateur et témoin T 10/11, mesure après 12/11, rapport et feuille de route 17/11 | « Adaptation engagée » à J3. Point d'arrêt le 12/11 : sans mesure après ce jour-là, la soutenance présente l'avant, l'entraînement et la feuille de route. Ollama 0.40.5 refuse les adaptateurs LoRA (vérifié le 26/10) : fusion puis GGUF, témoin au protocole. Remy coresponsable des étapes 4 et 5 et du témoin. Contrôle de séparation en PR #115. Format des exemples d'adaptation proposé à Remy dans la #115. Le 27/10 : faisabilité du Legion mesurée (PR #118) : insuffisante, Mac proposé pour l'entraînement, à acter au Weekly 7. #109 et #118 fusionnées ; plafond Metal du Mac mesuré à 17,76 Gio, soit une marge d'environ 10,6 Gio (commentaire sur #13). Préalables à l'entraînement dans le même commentaire : mesure de la #109 à refaire sous macOS 27, `data/volet_b` à sortir d'iCloud. Le 30/10 : machines décidées ; `data/volet_b` sorti d'iCloud ; mesure de la #109 refaite sous macOS 27 : pic de 7,14 Gio, inchangé. Générateur des données d'adaptation dans la #115, pilotes réels sur le Mac. |
| #111 | Corps resserré le 26/10 : contrat 28/10, maquette 04/11, branchement 10/11, scénario 12/11, vidéo 18/11 | Le branchement dépend de la fusion de la PR #85 et du choix de la machine de démonstration (Weekly 7). |
| #112 | Plan au Weekly 8 (04/11), supports le 13/11 | Exigés à J3 « même incomplets ». Le 27/10 : premier jet de Remy (branche `docs/112-supports-j3`, sans PR) ; chiffres confrontés aux sources, corrections demandées dans le ticket. Le 30/10 : sans réponse de Remy, relancé dans la #115. Chiffres vérifiés en PR #124. |
| #113 | Axes de progression et fiches le 13/11, mesures le 17/11, V1 le 19/11 | Le sujet exige une V1 strictement avant J4, dont l'écriture a commencé au plus tard à J3. Lignes de Mahé dans trois fiches : PR #116. Le 30/10 : ligne Playwright de Mahé en PR #123 ; cinq outils proposés dans #14. |
| #114 | Vidéo de secours du volet A le 18/11 ; supports, site figé et suivi le 20/11 ; révision croisée le 24/11 ; répétitions les 25 et 28/11 ; contrôle final du site le 27/11 ; envoi le 29/11 | Un déploiement le jour de J4 vaut non livré. |

Les échéances anciennes encore écrites dans les tickets ne sont pas corrigées implicitement par ce classeur. Le jeu de 60 questions figurant dans l'ancien planning n'est plus une tâche à créer : #44 existe et est fermé. Les détails du jeu et de son gel font foi dans ses documents de référence.

## Réunions

Les dates de tenue, les participants et les décisions proviennent des comptes rendus, des commentaires et de l'index des réunions. Les assignés GitHub ne sont pas une liste de présents.

| Date | Réunion et ticket | Présents | Absents | Résultat documenté |
|---|---|---|---|---|
| 14/09 | Weekly 1, #2 | NR | NR | Lancement et lecture du sujet selon l'index des réunions ; présence non documentée dans le ticket. |
| 19/09 | Weekly 2, #6 | Mahé, Remy, Jibril, Vaneck, Maïmouna | Aucun selon le compte rendu | Cas A3 et B1, corpus et modèles envisagés, domaines D1 à D5, gestion du board par Jibril. |
| 23/09 | Réunion d'avancement, #26 | Mahé, Remy, Jibril, Maïmouna | Vaneck | Cinq actions #27 à #31, responsables, soutiens et échéances confirmés. Réunion distincte du 19/09 ; aucun motif personnel d'absence repris. |
| 30/09 | Weekly 3, #9 | NR | NR | Issue fermée, mais le compte rendu reste au stade du modèle : décisions et récapitulatif non renseignés. |
| 07/10 | Weekly 4, #10 | NR | NR | Décisions documentées par Mahé en commentaire : protocole de #46, traitement des mesures exploratoires de #49, seuil CDTN, mesure après relecture, approbation obligatoire, noreply, suivi des charges. Volet A attendu le 18/10. |
| 28/10 | Weekly 7, #13 | sans objet | sans objet | Réunion remplacée par un suivi écrit, rédigé le 29/10 par Jibril dans le ticket, sans décision. Décisions prises le 30/10 par Mahé (machines, Agent0, #49, Weekly 9), révisables au Weekly 8. |
| 21/10 | Weekly 6, #12 | sans objet | sans objet | Réunion non tenue. Consigné le 26/10 par Jibril dans le ticket, avec un état des lieux rétrospectif au 21/10, sans présence ni décision inventée ; ticket fermé comme non planifié. |

La revue de #69 demande « non estimée » pour #44 ; cette précision est retenue malgré la case vide mentionnée dans le commentaire initial du Weekly 4. Les comptes rendus de #6 et #26 ont été rétablis : aucune nouvelle réouverture ou reconstruction n'est nécessaire ici.

Le Weekly 5 (#11) est prévu le 14/10/2026. Jibril doit renseigner pendant la réunion les présents et absents, les résultats présentés, les décisions, les actions, les responsables, les dates et les blocages, puis le récapitulatif. Aucun contenu de cette réunion future n'est anticipé.

## Vérification et limites

- Sources : API des issues au 13/10/2026, commentaires des tickets, suivi existant de dev au commit `c5ea1e097e989dfb25d68a332ba09ea9adab796e`, revue de #38 et corrections de #69.
- Les titres et états sont un instantané daté. La PR #38 est synchronisée avec dev ; les lignes de #25, #45 et #47 et les données déclarées de #69 sont conservées.
- Pas de lecture du statut du Project Board dans cette mise à jour : aucune équivalence Ouvert = Todo ou Fermé = validé.
- Aucun temps manquant, participant, verdict CDTN, résultat de mesure ou décision collective n'est inventé.
- Les dates officielles des jalons et la cohérence des plannings restent suivies dans #8 et les tickets concernés.
- Travail assisté par Codex dans ChatGPT Work ; Jibril a autorisé la reprise de #38 et l'estimation provisoire de #53. Relecture indépendante du dernier diff encore attendue avant fusion.

