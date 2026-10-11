# Classeur de suivi

**Équipe** Data Tigers
**Module** NLP 2, Master 2 Data & IA, FGES
**Ouvert le** 19 septembre 2026

**Objet.** Suivre les tâches, leurs responsables et leur chronologie, comme le demande le sujet. Ce classeur complète le board GitHub, qui porte l'état des tickets, en conservant ce que le board ne restitue pas : la charge estimée face à la charge réelle.

**Pourquoi cette colonne compte.** Le rapport final devra traiter « les écarts entre charge estimée et charge réelle, et analyse des causes de sous-estimation ». Cette information ne se reconstitue pas en décembre. Elle se note au moment où la tâche se termine, ou elle est perdue.

**Règle de tenue.** Une ligne par tâche, créée en même temps que son ticket. La charge réelle est saisie à la clôture. Responsable de la tenue : Jibril BENSALEM, qui gère déjà le board.

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

## Suivi des tâches

Charges en heures. La colonne Écart sert à la section retour d'expérience du rapport final.

| Ticket | Tâche | Domaine | Responsable | Début | Fin | Estimé | Réel | Écart |
|---|---|---|---|---|---|---|---|---|
| 1 | Création du dépôt GitHub | transverse | Mahé, Remy | 12/09 | 12/09 | | | |
| 2 | Weekly 1 | transverse | tous | 14/09 | 14/09 | | | |
| 3 | Choix des cas d'usage | transverse | tous | 19/09 | 19/09 | | | |
| 4 | Choix du modèle d'embeddings | D2 | Mahé, Remy | 19/09 | 19/09 | | | |
| 5 | Livrable J2 | transverse | tous | 19/09 | | | | |
| 6 | Weekly 2 | transverse | tous | 19/09 | | | | |
| 25 | Définir la méthode de suivi des outils novateurs | transverse | Vaneck, Maïmouna | 06/10 | 07/10 | non estimée | 2 | |
| 27 | Télécharger, filtrer et contrôler le corpus | D1 | Vaneck, Maïmouna ; soutien : Jibril | 26/09 | 28/09 | 8 | 10 | +2 |
| 29 | Déployer une page statique à l'URL définitive | D3 | Vaneck, Maïmouna | 30/09 | 30/09 | 3 | 1.5 | -1.5 |
| 44 | Construire le jeu de questions annotées | D1, D5 | Jibril, Maïmouna, Vaneck | | | | 18 | |
| 45 | Valider la chaîne de mesure sur PIAF | D2 | Remy, Mahé | 03/10 | 03/10 | 4 | 3.5 | -0.5 |
| 47 | Construire les références lexicales TF-IDF et BM25 | D2 | Remy, Mahé | 04/10 | 04/10 | 4 | 3.5 | -0.5 |

**#27 et #29 — charges déclarées :** estimations, charges réelles, dates et responsables communiqués par Vaneck à Jibril et reportés le 11/10/2026. Pour #29, 1.5 h correspond à 1 h 30, et l'écart de -1.5 h à -1 h 30. Vaneck attribue le dépassement de 2 h sur #27 au mauvais découpage du corpus source, documenté dans [#35](https://github.com/datatigersNLP/data_tigers_nlp/issues/35) et la [PR #39](https://github.com/datatigersNLP/data_tigers_nlp/pull/39).

**#44 — charge réelle :** 18 h cumulées pour Jibril, Maïmouna et Vaneck, confirmées par Jibril le 11/10/2026 et déjà consignées dans le ticket. Répartition individuelle non renseignée. Charge **non estimée avant le début** : la cellule Estimé reste vide et aucun écart n'est calculé. Les dates réelles de début et de fin ne sont pas renseignées.

---

## Tâches planifiées jusqu'au jalon de mi-parcours

À convertir en tickets avant engagement, conformément à la règle adoptée.

| Échéance | Tâche | Domaine | Estimé |
|---|---|---|---|
| 23/09 | Téléchargement du corpus et confirmation de la volumétrie | D1 | |
| 25/09 | Libération de 40 Gio sur la machine de référence | D4 | |
| 25/09 | Déploiement d'une page statique à l'URL définitive | D3 | |
| 27/09 | Index précalculé sur un corpus réduit | D2 | |
| 27/09 | Première inférence locale aboutie | D4 | |
| 29/09 | Jeu de 60 questions, dont 30 pour cent hors corpus | D1, D5 | |
| 01/10 | Jalon de mi-parcours, tag et branche d'observation | tous | |

---

## Réunions

| Date | Format | Présents | Décisions produites |
|---|---|---|---|
| 14/09 | Weekly 1 | tous | lancement, lecture du sujet |
| 19/09 | Weekly 2 | tous | cas A3 et B1, environnement, corpus, machine cible, répartition |

---

## Consignes de saisie

1. Une ligne par tâche, créée en même temps que le ticket. Une tâche sans ligne est une tâche non suivie.
2. La charge estimée se note avant de commencer, jamais après. Une estimation écrite après coup ne mesure rien.
3. La charge réelle se note à la clôture, le jour même.
4. Les réunions se consignent avec les décisions produites, pas seulement leur tenue. Le rapport final demandera « fréquence, format, résultats produits ».
