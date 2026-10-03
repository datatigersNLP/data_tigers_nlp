# Classeur de suivi

**Équipe :** Data Tigers  
**Module :** NLP 2, Master 2 Data & IA, FGES  
**Ouvert le :** 19 septembre 2026  
**Dernière mise à jour :** 27 septembre 2026

**Objet.** Suivre les tâches, leurs responsables et leur chronologie, comme le demande le sujet. Ce classeur complète le board GitHub, qui porte l'état opérationnel des tickets, en conservant ce que le board ne restitue pas : la charge estimée face à la charge réelle.

**Responsable de la tenue :** Jibril BENSALEM, dans le cadre de la gestion du board.

---

## Règles de suivi des charges

1. Une ligne est créée dans ce fichier en même temps que chaque ticket.
2. La charge estimée est saisie avant le démarrage de la tâche.
3. La charge réelle est saisie le jour de la clôture.
4. L'écart est calculé par : charge réelle moins charge estimée.
5. Une valeur manquante n'est jamais reconstruite a posteriori : elle reste notée **NR** afin de conserver une trace honnête de la dette de suivi.
6. Pour une tâche déjà commencée sans estimation initiale, l'équipe peut ajouter une estimation du **reste à faire**, clairement distinguée de l'estimation initiale.

> **Dette de suivi constatée le 27 septembre 2026 :** aucune charge initiale ou réelle n'avait été renseignée dans ce fichier pour les tickets existants. Les valeurs historiques restent donc notées NR. Les tâches non commencées doivent être estimées avant leur passage en `In progress`.

---

## Domaines

| Code | Domaine | Principal | Secondaire ou soutien |
|---|---|---|---|
| D1 | Corpus et segmentation | Maïmouna, Vaneck | Jibril |
| D2 | Encodeur et index | Remy | Mahé |
| D3 | Front et déploiement du volet A | Maïmouna, Vaneck | Remy, Mahé |
| D4 | Socle RAG et inférence locale | Jibril | Remy |
| D5 | Adaptation et évaluation du volet B | Mahé | Jibril |

---

## Suivi des tickets

Charges exprimées en heures. Les dates « Ouvert » et « Clôturé » correspondent aux dates GitHub et ne prétendent pas remplacer les dates réelles de début et de fin de travail.

| Ticket | Tâche | Domaine | Responsables | Jalon | État GitHub | Ouvert | Clôturé | Estimé | Réel | Écart |
|---|---|---|---|---|---|---|---|---:|---:|---:|
| #1 | Création du repo GitHub | transverse | Mahé, Remy | — | Fermé | 12/09 | 12/09 | NR | NR | NR |
| #2 | Weekly 1 | transverse | Tous | J2 | Fermé | 14/09 | 19/09 | NR | NR | NR |
| #3 | Choix des cas d'usages | transverse | Tous | J2 | Fermé | 19/09 | 20/09 | NR | NR | NR |
| #4 | Choix du modèle d'embeddings | D2 | Mahé, Remy | J2 | Fermé | 19/09 | 20/09 | NR | NR | NR |
| #5 | Livrable J2 | transverse | Tous | J2 | Fermé | 19/09 | 20/09 | NR | NR | NR |
| #6 | Weekly 2 | transverse | Tous | J2 | Fermé | 19/09 | 20/09 | NR | NR | NR |
| #7 | Choix de la chaîne front-end du volet A | D3 | Mahé, Vaneck, Maïmouna | J2 | Fermé | 20/09 | 20/09 | NR | NR | NR |
| #8 | Faire confirmer le calendrier officiel des jalons | transverse | Jibril | Mi-parcours | Ouvert | 20/09 | — | — | — | — |
| #9 | Weekly 3 - 3 octobre 2026 | transverse | Tous | J3 | Ouvert | 20/09 | — | — | — | — |
| #10 | Weekly 4 - 7 octobre 2026 | transverse | Tous | J3 | Ouvert | 20/09 | — | — | — | — |
| #11 | Weekly 5 - 10 octobre 2026 | transverse | Tous | J3 | Ouvert | 20/09 | — | — | — | — |
| #12 | Weekly 6 - 17 octobre 2026 | transverse | Tous | J3 | Ouvert | 20/09 | — | — | — | — |
| #13 | Weekly 7 - 24 octobre 2026 | transverse | Tous | J3 | Ouvert | 20/09 | — | — | — | — |
| #14 | Weekly 8 - 31 octobre 2026 | transverse | Tous | J3 | Ouvert | 20/09 | — | — | — | — |
| #15 | Weekly 9 - 7 novembre 2026 | transverse | Tous | J3 | Ouvert | 20/09 | — | — | — | — |
| #16 | Weekly 10 - 14 novembre 2026 | transverse | Tous | J3 | Ouvert | 20/09 | — | — | — | — |
| #17 | Weekly 11 - 21 novembre 2026 | transverse | Tous | J4 | Ouvert | 20/09 | — | — | — | — |
| #18 | Weekly 12 - 28 novembre 2026 | transverse | Tous | J4 | Ouvert | 20/09 | — | — | — | — |
| #19 | Weekly 13 - 5 décembre 2026 | transverse | Tous | J4 | Ouvert | 20/09 | — | — | — | — |
| #20 | Formaliser les règles de fonctionnement et les critères de validation | transverse | Tous | Mi-parcours | Ouvert | 20/09 | — | — | — | — |
| #21 | Proposer les modèles de tickets, pull requests et Weeklys | transverse | Mahé, Jibril | Mi-parcours | Ouvert | 20/09 | — | — | — | — |
| #22 | Discuter et valider les modèles de travail en Weekly 3 | transverse | Tous | Mi-parcours | Ouvert | 20/09 | — | — | — | — |
| #23 | Construire et prioriser le backlog détaillé jusqu'au mi-parcours | transverse | Tous | Mi-parcours | Ouvert | 20/09 | — | — | — | — |
| #24 | Mettre en place le registre des risques, hypothèses et décisions | transverse | Tous | Mi-parcours | Ouvert | 20/09 | — | — | — | — |
| #25 | Définir la méthode de suivi des outils novateurs | transverse | Vaneck, Maïmouna | Mi-parcours | Ouvert | 20/09 | — | — | — | — |
| #26 | Weekly 2 - 23 septembre 2026 | transverse | — | J2 | Fermé — doublon de #6 | 23/09 | 27/09 | NR | NR | NR |
| #27 | Télécharger, filtrer et contrôler le corpus | D1 | Vaneck, Jibril, Maïmouna | Mi-parcours | Ouvert | 23/09 | — | NR | — | — |
| #28 | Vérifier et garantir 40 Gio libres sur la machine de référence | D4 | Mahé, Jibril | Mi-parcours | Ouvert | 23/09 | — | — | — | — |
| #29 | Déployer une page statique à l'URL définitive | D3 | Maïmouna, Vaneck, Remy, Mahé | Mi-parcours | Ouvert | 23/09 | — | — | — | — |
| #30 | Générer un index précalculé sur un corpus réduit | D2 | Remy, Mahé | Mi-parcours | Ouvert | 23/09 | — | NR | — | — |
| #31 | Réaliser une première inférence locale | D4 | Jibril, Remy | Mi-parcours | Ouvert | 23/09 | — | — | — | — |
| #33 | Versionner les documents préparatoires du jalon J2 | transverse | Mahé | Mi-parcours | Ouvert | 27/09 | — | NR | — | — |
| #34 | Corriger la session 9 du journal d'usage IA et régénérer son PDF | transverse | Mahé, Remy | Mi-parcours | Ouvert | 27/09 | — | NR | — | — |
| #35 | Explorer le découpage du corpus depuis la source SocialGouv | D1, D5 | Mahé | J3 | Ouvert | 27/09 | — | NR | — | — |

Le numéro #32 correspond à une pull request et non à un ticket ; il n'apparaît donc pas comme une ligne autonome.

---

## Tâches prioritaires jusqu'au jalon de mi-parcours

| Échéance | Ticket | Tâche | Domaine | Situation au 27/09 |
|---|---|---|---|---|
| 26/09 | #27 | Corpus téléchargé, filtré et volumétrie confirmée | D1 | Échéance dépassée ; PR #32 en correction |
| 27/09 | #28 | Vérifier et garantir 40 Gio libres | D4 | Preuve de mesure attendue |
| 03/10 | #29 | Page statique déployée à l'URL définitive | D3 | À réaliser |
| 03/10 | #30 | Index précalculé sur un corpus réduit | D2 | Travail engagé |
| 03/10 | #31 | Première inférence locale aboutie | D4 | À réaliser |
| À confirmer | — | Jeu de 60 questions, dont 30 % hors corpus | D1, D5 | Ticket à créer avant démarrage |
| À confirmer | #8 | Jalon de mi-parcours, tag et branche d'observation | Tous | Calendrier officiel en attente |

---

## Réunions

| Date | Format | Présents | Absents | Décisions produites |
|---|---|---|---|---|
| 14/09 | Weekly 1 | Tous | Aucun | Lancement et lecture du sujet |
| 23/09 | Weekly 2 | Mahé, Remy, Jibril, Maïmouna | Vaneck — impératif familial | Validation des cinq premières tâches du séquencement, responsables et échéances |

---

## Consignes opérationnelles

1. Toute nouvelle action dispose d'un ticket avant son démarrage.
2. Le responsable renseigne l'estimation avant le passage du ticket en `In progress`.
3. Le responsable renseigne la charge réelle et la preuve de réalisation avant la clôture.
4. Jibril vérifie la cohérence du board et de ce fichier après chaque Weekly.
5. Les écarts significatifs sont commentés afin d'alimenter le retour d'expérience du rapport final.
6. Les réunions consignent les décisions et les actions produites, pas seulement leur tenue.
