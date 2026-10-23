# Protocole de mesure du volet B, avant et après adaptation

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Tickets** #52 (mesure avant adaptation), #107 (adaptation et mesure après)  
**Responsables** Mahé BEGNIS (mesure), Jibril BENSALEM (exécution sur le Legion)  
**Statut** proposé le 23 octobre 2026, à relire par Jibril, à figer avant la mesure avant. Aucune mesure du volet B n'a été faite sur le lot de test.

---

## 1. Objet

Mesurer le comportement de la chaîne RAG du volet B (PR #85), avec des règles écrites avant toute mesure, comme l'exige #52 :
- **ce qui est mesuré** : l'abstention et les citations ;
- **quand** : avant puis après l'adaptation du modèle (#107) ;
- **sur quoi** : les mêmes questions dans les deux cas.

Ce protocole reprend les quatre métriques et les deux références dégénérées annoncées dans le rapport J2 (section 4.5).

## 2. Jeu de questions

- **Mesure** : le lot de test du jeu figé `jeu-questions-v1`, au commit et avec l'empreinte SHA-256 du CSV ci-dessous. Il compte 97 questions : 73 du corpus, issues de 61 fiches, et 24 hors corpus.

```text
commit   cdb48c97064de625df61703a9a41e106160e0f50
SHA-256  807498144fec46722ffab045a87c191b6282a86300799976869d4d6c1755fb35
```

- **Écart déclaré avec le rapport J2** : les questions hors corpus forment 24,7 % du lot, contre les 30 % visés, et le jeu figé n'a pas de catégorie « ambiguë ». Il n'est pas modifié.
- **Mise au point** : uniquement le lot de calibration (5 questions du corpus, 3 hors corpus), et des questions synthétiques s'il en faut davantage.
- **Isolement du lot de test** :
  - il ne sert à aucune décision de conception : consigne, seuil, paramètres, données d'adaptation ;
  - il n'est lu qu'en mode mesure, avec contrôle des empreintes de ce protocole, du jeu et de l'index, comme au notebook 03 ;
  - il a déjà servi une fois au volet A (notebook 03, le 13 octobre) et évalue ici un autre système ;
  - ses 61 fiches sont exclues des données d'adaptation (#107).

## 3. États mesurés

Tous les états utilisent le même modèle (`qwen2.5-7b-instruct:q4_k_m-local`, digest de #31) et les mêmes paramètres que la #85 :
- température 0 et graine 20261018 ;
- contexte de 8 192 tokens, sortie de 512 tokens ;
- `raw: true`, et aucune troncature.

| Code | État | Configuration |
|---|---|---|
| B0 | modèle nu | sans passage. Consigne : répondre en français, ou répondre uniquement par la phrase d'abstention de la #85 si la réponse n'est pas connue avec certitude |
| B1 | récupération sans consigne d'abstention | chaîne de la #85 (E5 en fp32, 5 passages, contexte `rag-b1-v1`), avec sa consigne privée des deux dernières lignes, celles qui demandent l'abstention |
| B2 | récupération avec consigne et seuil | chaîne de la #85 complète. Si le plus grand cosinus de la question avec les passages est strictement inférieur au seuil S (section 7), le système s'abstient sans appeler le modèle |
| R+ | référence qui répond toujours | même récupération que B1 et B2, puis, sans appel au modèle, une réponse fixe qui cite `[P1]`, le premier passage récupéré |
| R- | référence qui s'abstient toujours | la phrase d'abstention pour toute question |

**Après l'adaptation**, B1 et B2 sont mesurés de nouveau avec l'adaptateur de #107, et B0 à titre descriptif. Les références dégénérées ne changent pas.

## 4. Classement de chaque sortie

Le classement reprend le contrôle structurel de la #85 (`valider_citations`). Chaque sortie entre dans une seule classe :

| Classe | Règle |
|---|---|
| abstention | la réponse, sans les espaces de bord, est exactement la phrase d'abstention ; ou, en B2, la question est sous le seuil |
| réponse citée | au moins une référence `[Pk]` présente dans le contexte, aucune référence absente ou mal formée, et pas de phrase d'abstention mêlée à la réponse |
| sortie invalide | tout autre texte : réponse vide, aucune citation valide, référence mal formée, abstention mêlée |
| erreur technique | génération incomplète, décompte des tokens différent entre HF et Ollama, ou nombre de tokens de sortie invalide |

Trois précisions :
- **Crochets** : tout groupe entre crochets autre que `[Pk]` rend la sortie invalide, y compris une référence d'article écrite « [article L. 1221-19] ». Ce choix est déclaré, car il pèse sur le taux de sorties invalides.
- **État B0** : sans passage, aucune citation n'est possible. Toute sortie qui n'est ni une abstention ni une erreur technique y est comptée comme une réponse.
- **Erreurs techniques** : elles sont rapportées à part et retirées des dénominateurs. Si elles dépassent 5 % des questions d'un état, la mesure de cet état est déclarée invalide et refaite en entier.

## 5. Métriques

| Code | Métrique | Population |
|---|---|---|
| M1 | abstention correcte : part classée abstention | 24 questions hors corpus |
| M2 | abstention à tort : part classée abstention | 73 questions du corpus |
| M3 | citation valide : part classée réponse citée | 73 questions du corpus |
| M4 | citation pertinente : part classée réponse citée dont au moins une référence citée renvoie à un passage pertinent selon la règle D4 du notebook 03 (`scripts/evaluation/pertinence.py`, `est_pertinent`) | 73 questions du corpus |
| M5 | réponse affirmative hors corpus : part classée réponse citée ou sortie invalide | 24 questions hors corpus |

**Indicateurs descriptifs.**
- Part de sorties invalides.
- Couverture structurelle des réponses citées : part de leurs phrases qui portent au moins une référence `[Pk]`.
- Tokens d'entrée et de sortie, et durées rapportées par Ollama.

**Exactitude des réponses.** Elle n'est pas mesurée automatiquement. Elle est jugée à titre descriptif, sur 20 réponses citées tirées au hasard (graine 20261018) parmi celles de B2, avant et après :
- par deux membres, qui ignorent de quel état vient chaque réponse ;
- avec, pour chacune, l'exactitude, le respect des conditions et exceptions, et la justification par les passages cités.

**Ce que montrent les références dégénérées.** R+ obtient par construction M3 = 100 % et M1 = 0 %, et son M4 vaut la part des questions dont le premier passage récupéré est pertinent. Un taux élevé de citations valides ne prouve donc rien seul ; c'est M4 qui distingue un système d'une réponse fixe.

## 6. Analyse statistique

- **Intervalles à 95 %**, calculés avec `scripts/evaluation/metrics.py` :
  - questions du corpus : intervalle de Wilson sur l'effectif corrigé de l'effet de plan des fiches (`proportion_ci`), comme au notebook 03 ;
  - questions hors corpus : elles n'ont pas de fiche, donc intervalle de Wilson simple.
- **Précision attendue** : la demi-largeur de l'intervalle atteint 20 points pour une proportion de 50 % sur 24 questions, et 11,5 points sur 73. Un écart de moins de 20 points environ entre deux états ne sera pas démontrable sur les questions hors corpus. Les résultats sont donc d'abord descriptifs.
- **Comparaisons appariées** : mêmes questions, donc tables de contingence et valeur p exacte de McNemar. Pour les questions du corpus, l'écart est donné avec l'intervalle du score de Tango corrigé de l'effet de plan (`noninferiority_tango`, appliqué ici comme intervalle de l'écart).
- **Analyse principale, écrite d'avance** : après contre avant adaptation, en B2, sur M1 et sur M4. M2 sert de garde-fou et est toujours rapporté.
- **Règle de conclusion** : pour ces deux comparaisons principales, l'écart est donné avec un intervalle bilatéral à 97,5 % (correction de Bonferroni pour deux comparaisons). Le score de Tango est corrigé de l'effet de plan pour M4, et calculé sans regroupement pour M1. Une amélioration n'est déclarée démontrée que si la borne basse de cet intervalle dépasse 0. Sinon, le rapport dit seulement que l'écart n'est pas démontré.

## 7. Seuil S de l'état B2

- **Population** : celle du notebook 03 (section 8.2). Ce sont les variantes du CDTN rédigées en question (#56) pour des requêtes dont au moins une référence vise une fiche de notre corpus.
- **Encodage** : en fp32 par E5, comme dans la #85, et non en q8 comme sur le site. Le seuil de 0,8560 du site ne s'applique donc pas ici.
- **Valeur** : le 5e centile, par interpolation linéaire, des scores maximaux.
- **Moment du calcul** : une fois, avant la mesure avant. La valeur et l'empreinte du fichier de calcul sont inscrites ici avant le gel.
- **Après l'adaptation** : il n'est pas recalculé, puisque la récupération ne change pas quand Qwen est adapté.

## 8. Exécution

- **Machine** : une seule machine pour toutes les mesures, par défaut le Legion (Ollama 0.40.5), avec les versions, le digest et les empreintes consignés. Un changement de machine entre avant et après invalide la comparaison.
- **Script** : écrit sur la base de `scripts/rag/` après la fusion de la #85. En mode mesure, il refuse de lire le lot de test si les empreintes de ce protocole, du jeu ou de l'index diffèrent de celles inscrites.
- **Exécution unique** : une seule exécution par état et par phase. La seule reprise autorisée est celle de la règle des erreurs techniques (section 4).
- **Conservation** : les sorties brutes, le classement et les mesures sont conservés dans `data/`, qui n'est pas versionné. Le rapport de mesure, avec ses empreintes, est versionné.

## 9. Avant le gel

- Relecture de ce protocole par Jibril, qui exécutera la mesure, puis présentation au Weekly.
- Confirmation de la machine de mesure.
- Désignation des deux juges de l'exactitude.
- Calcul du seuil S et inscription de sa valeur et de son empreinte.
- Script de mesure écrit et relu, puis exécuté sur le seul lot de calibration.

## 10. Historique

- **23 octobre 2026** : proposition initiale (Mahé), d'après #52, le rapport J2 (section 4.5) et la chaîne de la PR #85.
