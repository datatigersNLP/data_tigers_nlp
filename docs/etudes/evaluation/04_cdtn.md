# Jeu complémentaire du CDTN : règle, plan d'analyse et limites

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Ticket** Issue #56, analyse secondaire du notebook 03 (#46)  
**Responsable principal** Mahé BEGNIS  
**Relecture des requêtes** Jibril BENSALEM, Maïmouna SIGNATE, Vaneck DAGAR  
**Statut** règle et plan figés le 10 octobre 2026, avant la mesure du notebook 03 ; relecture des requêtes à faire  

---

## 1. Objet

Le jeu de l'équipe (#44) tranche le critère du rapport J2 ; il compte 73 questions du corpus dans son lot de test. Le Code du travail numérique (CDTN) a publié, en 2021, des requêtes réelles d'usagers avec les fiches et sections qui y répondent. Ce jeu complémentaire donne une seconde mesure, plus large mais plus approximative, de la recherche du volet A. Il est analysé à part et n'est jamais fusionné avec le jeu de l'équipe.

---

## 2. Source

* **Dépôt** `SocialGouv/datafiller-data`, archivé, commit `6d16869` du 19 avril 2021 (hash complet dans le script), fichier `data/requests.json`.
* **Contrôle** : SHA-256 `02ee32bfb6359bc5d061b769fd10e42a0b288d441381c725fddbd3a64d579a7c`, vérifié avant toute lecture.
* **Licence** : aucune n'est déclarée. Les données sont lues dans `data/`, qui n'est pas versionné ; seuls le code, des identifiants et des verdicts le sont.
* **Contenu** : 298 requêtes, 5 135 variantes, 2 086 références classées, dont 652 vers des fiches du ministère du Travail.

---

## 3. Règle d'appariement, figée

* **Fiche.** L'identifiant de la référence (`/fiche-ministere-travail/` suivi de l'identifiant) doit être exactement celui de l'une de nos 261 fiches. Aucun rapprochement approximatif : une fiche renommée depuis 2021 est écartée plutôt que devinée.
* **Section.** L'ancre de la référence et le titre de chaque section de la fiche sont ramenés à leurs lettres et chiffres, sans accents, en minuscules, sans le résidu « nbsp » d'une espace insécable. La section est appariée si les deux sont égaux. À défaut, si l'ancre compte au moins 30 caractères et qu'elle est le début du titre d'une seule section de la fiche, cette section est appariée : le CDTN tronque les titres longs.
* **Passages pertinents.** Les passages M2 qui couvrent au moins une section appariée de la requête.
* **Formulations.** Pour chaque requête appariée : son titre, tirets remplacés par des espaces, et ses variantes rédigées en question, c'est-à-dire contenant un point d'interrogation (règle du 4 octobre). Toutes héritent des passages pertinents de leur requête : le jugement porte sur la requête, pas sur la formulation.
* **Implémentation.** `scripts/evaluation/cdtn_jeu.py construire`, en une commande ; contrôles calculés à la main dans le script.

---

## 4. Ce que donne la règle

| Élément | Valeur |
|---|---:|
| Références vers une fiche de notre corpus, par identifiant exact | 371 |
| Sections appariées exactement | 296 |
| Sections appariées par le début du titre | 32 |
| Sections absentes de la fiche actuelle | 24 |
| Références sans ancre de section | 19 |
| Requêtes retenues | 155 |
| Formulations : titres et variantes en question | 607 (155 et 452) |
| Passages M2 pertinents par requête | 5 en médiane, de 1 à 22 ; 12 requêtes en ont un seul |

Les 32 appariements par le début du titre ont été contrôlés un à un : ce sont tous des titres tronqués par le CDTN, et chacun désigne une seule section. Le fichier versionné `evaluation/cdtn/identifiants.csv` donne, pour chaque formulation, sa requête, son type et ses passages pertinents, sans aucun texte du CDTN ; son empreinte d'identifiants vaut `ec538870` (début).

---

## 5. Relecture humaine, avant l'analyse

* **Répartition.** Les 155 requêtes sont réparties à tour de rôle : Jibril 52 (232 formulations), Maïmouna 52 (194), Vaneck 51 (181).
* **Fiche de relecture.** `data/evaluation/cdtn/relecture_<identifiant GitHub>.csv`, générée par le script et transmise hors du dépôt, puisqu'elle contient les textes du CDTN. Elle donne pour chaque requête ses formulations, les sections de notre corpus appariées et leurs liens profonds.
* **Deux jugements.** Sur la première ligne de chaque requête, `verdict_requete` : `oui` si les sections citées répondent à la requête, `partiel` si elles n'y répondent qu'en partie, `non` sinon. Sur chaque ligne, `formulation_a_ecarter` : `oui` si la formulation ne correspond pas à la requête.
* **Indépendance.** La règle de #56 interdisait de consulter le CDTN avant le tag du jeu de l'équipe, posé le 6 octobre ; la source n'a été téléchargée que le 10 octobre. La relecture se fait avant toute mesure sur ce jeu.
* **Import.** `scripts/evaluation/cdtn_jeu.py importer` écrit `evaluation/cdtn/jugements.csv`, avec seulement des identifiants et des verdicts. Une remarque ne recopie jamais un texte du CDTN.

---

## 6. Plan d'analyse, figé

* **Population.** Les requêtes jugées `oui` ou `partiel`, sans les formulations écartées. En sensibilité, les 155 requêtes.
* **Systèmes.** E5 servi (questions encodées dans le navigateur en q8, index M2 du site) et BM25 de référence (V3) sur les passages M2 ; E5 en fp32 à titre descriptif.
* **Métriques.** Recall@1, 5 et 10 au niveau du passage, avec la pertinence de la section ; Recall@5 au niveau de la fiche.
* **Comparaison.** L'écart de Recall@5 entre E5 servi et BM25 V3, apparié par formulation, avec les formulations groupées par requête : test d'Obuchowski et intervalle robuste aux groupes. L'effectif utile est le nombre de requêtes, pas celui des formulations.
* **Sous-ensembles descriptifs.** Titres, souvent des mots-clés, contre variantes rédigées en question.
* **Statut.** Analyse secondaire : aucune règle de décision ; les résultats éclairent ceux du jeu de l'équipe sans jamais les remplacer.

---

## 7. Limites

* **Jugements de 2021.** Ils ont été faits pour le corpus du CDTN, pas pour le nôtre, et ne sont pas exhaustifs : un passage qui répond sans être cité compte comme non pertinent, et le Recall est sous-estimé.
* **Pertinence large.** Une section entière est pertinente, d'où 5 passages pertinents en médiane, contre 1 dans le jeu de l'équipe : les chiffres ne sont pas comparables entre les deux jeux.
* **Couverture partielle.** Seules 371 des 652 références vers des fiches du ministère visent une fiche de notre corpus par son identifiant exact ; 24 sections ont disparu depuis 2021.
* **Mots-clés.** Les titres de requête sont surtout des mots-clés, qui peuvent avantager BM25 : d'où leur analyse à part.
* **Pas de question hors corpus.** Ce jeu ne mesure pas l'abstention ; il sert seulement à fixer son seuil (protocole du notebook 03, section 8.2).
