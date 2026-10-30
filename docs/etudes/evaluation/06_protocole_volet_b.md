# Protocole de mesure du volet B, avant et après adaptation

**Équipe** Data Tigers  
**Projet** NLP 2 · Master 2 Data & IA · FGES, Université Catholique de Lille  
**Tickets** #52 (mesure avant adaptation), #107 (adaptation et mesure après)  
**Responsables** Mahé BEGNIS (mesure), Jibril BENSALEM (exécution sur le Legion)  
**Statut** proposé le 23 octobre 2026, complété le 26 octobre (seuil S, témoin de la chaîne d'export), puis après la revue de Jibril du même jour, et le 30 octobre après la calibration du 29 (consigne de B0, version d'Ollama, machines), à figer avant la mesure avant. Aucune mesure du volet B n'a été faite sur le lot de test.

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
| B0 | modèle nu | sans passage. Consigne : répondre en français, brièvement avec la phrase de la #85 que B1 conserve (« Réponds brièvement et conserve les conditions et exceptions nécessaires. »), ou répondre uniquement par la phrase d'abstention de la #85 si la réponse n'est pas connue avec certitude. B0 et B1 ne diffèrent ainsi que par les passages |
| B1 | récupération sans consigne d'abstention | chaîne de la #85 (E5 en fp32, 5 passages, contexte `rag-b1-v1`), avec sa consigne privée des deux dernières lignes, celles qui demandent l'abstention |
| B2 | récupération avec consigne et seuil | chaîne de la #85 complète. Si le plus grand cosinus de la question avec les passages est strictement inférieur au seuil S (section 7), le système s'abstient sans appeler le modèle |
| R+ | référence qui répond toujours | même récupération que B1 et B2, puis, sans appel au modèle, une réponse fixe qui cite `[P1]`, le premier passage récupéré |
| R- | référence qui s'abstient toujours | la phrase d'abstention pour toute question |

**Après l'adaptation**, B1 et B2 sont mesurés de nouveau avec le modèle adapté de #107, et B0 à titre descriptif. Les références dégénérées ne changent pas.

**Témoin de la chaîne d'export.** Ollama refuse les adaptateurs LoRA : `server/create.go` définit `errAdaptersUnsupported` et rejette toute création qui en contient. C'est vérifié au tag `v0.40.5` le 26 octobre 2026, puis au tag `v0.40.11`, la version de référence (section 8), le 30 octobre : le code est identique. Le modèle adapté sera donc fusionné, converti en GGUF et quantifié en Q4_K_M avec llama.cpp. Il diffère du modèle de #31 par l'adaptation, mais aussi par cette chaîne. Pour séparer les deux effets, comme pour l'encodeur ajusté de #49 :
- le témoin T est le modèle de base passé par la même chaîne, avec les mêmes outils et versions, sans adaptateur ;
- T et le modèle de #31 ne se confondent que si tout ce qui détermine la génération est identique, contrôlé par script : tenseurs bit à bit, tokeniseur, métadonnées GGUF, gabarit de conversation et paramètres du modèle Ollama. Une graine fixe ne garantit pas à elle seule l'identité de la chaîne ;
- à défaut, T reste une référence distincte : B1 et B2 sont aussi mesurés avec T, l'analyse principale (section 6) compare le modèle adapté à T, et l'écart entre T et le modèle de #31 est rapporté à titre descriptif.

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
- **Erreurs techniques** : elles sont rapportées à part et retirées des dénominateurs. Si elles dépassent 5 % des questions d'un état, la mesure de cet état est déclarée invalide et refaite en entier. Leur effet sur les comparaisons appariées est réglé en section 6. La génération étant déterministe (température 0, graine fixe), une erreur liée au texte, comme une réponse coupée à 512 tokens, peut se reproduire à la reprise : seule une erreur passagère, un serveur injoignable par exemple, disparaît ainsi. Un état qui reste invalide est rapporté comme tel ; si c'est B2, l'analyse principale n'est pas conclue.

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
- par deux membres, Maïmouna SIGNATE et Vaneck DAGAR, désignés le 25 octobre : ils ont annoté le jeu humain (#44), n'écrivent ni la chaîne ni l'adaptation, et ignorent de quel état vient chaque réponse ;
- avec, pour chacune, l'exactitude, le respect des conditions et exceptions, et la justification par les passages cités.

**Ce que montrent les références dégénérées.** R+ obtient par construction M3 = 100 % et M1 = 0 %, et son M4 vaut la part des questions dont le premier passage récupéré est pertinent. Un taux élevé de citations valides ne prouve donc rien seul ; c'est M4 qui distingue un système d'une réponse fixe.

## 6. Analyse statistique

- **Intervalles à 95 %**, calculés avec `scripts/evaluation/metrics.py` :
  - questions du corpus : intervalle de Wilson sur l'effectif corrigé de l'effet de plan des fiches (`proportion_ci`), comme au notebook 03 ;
  - questions hors corpus : elles n'ont pas de fiche, donc intervalle de Wilson simple.
- **Précision attendue** : la demi-largeur de l'intervalle atteint 20 points pour une proportion de 50 % sur 24 questions, et 11,5 points sur 73. Un écart de moins de 20 points environ entre deux états ne sera pas démontrable sur les questions hors corpus. Les résultats sont donc d'abord descriptifs.
- **Population des comparaisons appariées** : pour chaque comparaison, les questions sans erreur technique dans les deux états comparés, désignées par leur identifiant. Les effectifs sont rapportés pour chaque population, hors corpus pour M1 et du corpus pour M4, avec la liste des questions exclues et la raison de chaque exclusion. Les proportions descriptives de chaque état portent sur ses propres questions sans erreur ; les écarts appariés, sur la seule population commune. Les questions ne sont jamais appariées par leur position après des exclusions distinctes.
- **Comparaisons appariées** : mêmes questions, donc tables de contingence et valeur p exacte de McNemar. Pour les questions du corpus, l'écart est donné avec l'intervalle du score de Tango corrigé de l'effet de plan (`noninferiority_tango`, appliqué ici comme intervalle de l'écart).
- **Analyse principale, écrite d'avance** : après contre avant adaptation, en B2, sur M1 et sur M4. « Avant » désigne le témoin T s'il diffère du modèle de #31 (section 3). M2 sert de garde-fou et est toujours rapporté.
- **Règle de conclusion** : pour ces deux comparaisons principales, l'écart est donné avec un intervalle bilatéral à 97,5 % (correction de Bonferroni pour deux comparaisons). Le score de Tango est corrigé de l'effet de plan pour M4, et calculé sans regroupement pour M1. Une amélioration n'est déclarée démontrée que si la borne basse de cet intervalle dépasse 0. Sinon, le rapport dit seulement que l'écart n'est pas démontré.
- **Autres comparaisons** : toutes descriptives, à 95 %, sans conclusion d'amélioration, y compris celles du lot de calibration, celles de B1 et celle du modèle de #31 avec T. Le script ne désigne l'analyse principale que pour B2, en mode mesure, après contre la référence désignée.

## 7. Seuil S de l'état B2

- **Population** : celle du protocole du notebook 03 (section 8.2). Ce sont les variantes du CDTN rédigées en question (#56) pour des requêtes dont au moins une référence vise une fiche de notre corpus.
- **Encodage** : en fp32 par E5, comme dans la #85, et non en q8 comme sur le site. Le seuil de 0,8560 du site ne s'applique donc pas ici.
- **Valeur** : le 5e centile, par interpolation linéaire, des scores maximaux.
- **Moment du calcul** : une fois, avant la mesure avant. La valeur et l'empreinte du fichier de calcul sont inscrites ici avant le gel.
- **Valeur calculée le 26 octobre 2026** : **S = 0,8565**, par `scripts/evaluation/seuil_b2.py`, sur 479 variantes issues de 103 requêtes. Les scores maximaux vont de 0,832 à 0,948 ; 24 variantes sont sous le seuil. Intervalle à 95 % du seuil, par rééchantillonnage des requêtes (10 000 tirages) : 0,8464 à 0,8653. Pour comparaison, le seuil du site, calculé en q8 dans le navigateur, vaut 0,8560.
- **Contrôle** : les 479 scores, recalculés par les fonctions de la chaîne de la #85 elle-même (commit `df91b85`), sont identiques au bit près, et le seuil aussi.
- **Valeur utilisée par la mesure** : la valeur complète du champ `seuil` de `seuil_b2.json`, lue après contrôle de l'empreinte du fichier ci-dessous, sans arrondi. La valeur 0,8565 n'en est que l'affichage. La même valeur sert avant et après l'adaptation, sans recalcul :

```text
0.856489074230194
```

- **Machine** : S a été calculé sur un Mac (arm64), alors que la mesure encodera les questions sur la machine de mesure. Deux machines peuvent différer dans les dernières décimales : le script de mesure signale toute question dont le score est à moins de 1e-5 de S, pour qu'un écart de machine ne puisse pas changer une abstention sans être vu.
- **Empreinte SHA-256** du fichier de calcul `data/evaluation/volet_b/seuil_b2.json` :

```text
7ba7230e5e8cda87fa1eb8dda2adc01d73c6702d542c27a4e3dc620464939936
```

- **Après l'adaptation** : il n'est pas recalculé, puisque la récupération ne change pas quand Qwen est adapté.

## 8. Exécution

- **Machine de mesure** : le Legion, pour toutes les mesures, avant comme après, avec les versions, le digest et les empreintes consignés. Décision du 30 octobre 2026 (#107).
- **Version d'Ollama** : 0.40.11, épinglée. Le script refuse toute génération venue d'une autre version, et toute comparaison de deux phases mesurées avec des versions différentes. Les mises à jour automatiques d'Ollama sont désactivées sur le Legion du gel à la mesure après ; si l'option manque, aucune mise à jour proposée n'est appliquée. Un changement de machine ou de version entre avant et après invalide la comparaison.
- **Entraînement et chaîne d'export** : sur le Mac de Mahé, la seule des deux machines où l'entraînement tient en mémoire (PR #109 et #118). La fusion, la conversion en GGUF et la quantification en Q4_K_M y sont faites avec les mêmes outils et versions pour le modèle adapté et pour T. Les deux fichiers GGUF sont transférés au Legion avec leur empreinte SHA-256, contrôlée à l'arrivée, puis importés dans Ollama.
- **Script** : écrit sur la base de `scripts/rag/` après la fusion de la #85. En mode mesure, il refuse de lire le lot de test si les empreintes de ce protocole, des scripts, du jeu, de l'index ou du seuil diffèrent de celles du verrou écrit au gel. Les empreintes du protocole et des scripts sont calculées sur leur contenu tel que Git le stocke, fins de ligne normalisées : le verrou vaut ainsi sur le Mac comme sur le Legion, où Git pour Windows peut convertir les fins de ligne.
- **Exécution unique** : une seule exécution par état et par phase. La seule reprise autorisée est celle de la règle des erreurs techniques (section 4).
- **Conservation** : les sorties brutes, le classement et les mesures sont conservés dans `data/`, qui n'est pas versionné. Le rapport de mesure, avec ses empreintes, est versionné.

## 9. Avant le gel

- Relecture de ce protocole par Jibril, qui exécutera la mesure, puis présentation au Weekly.
- Machines décidées le 30 octobre (section 8).
- Juges de l'exactitude désignés le 25 octobre : Maïmouna SIGNATE et Vaneck DAGAR. À partir de leurs relectures, ils rédigent aussi les défauts caractérisés sur des exemples, livrable de #52.
- Seuil S calculé et inscrit le 26 octobre, avec son empreinte (section 7).
- Script de mesure écrit et relu, exécuté le 29 octobre sur le seul lot de calibration (Jibril, sur le Legion), puis corrigé (PR #119). B0 est recalibré avec sa nouvelle consigne ; la première sortie et son analyse sont conservées.

## 10. Historique

- **23 octobre 2026** : proposition initiale (Mahé), d'après #52, le rapport J2 (section 4.5) et la chaîne de la PR #85.
- **25 octobre 2026** : juges de l'exactitude désignés, avec l'accord de Mahé ; aucune autre règle modifiée.
- **26 octobre 2026** : seuil S calculé et inscrit (section 7). Témoin T de la chaîne d'export ajouté (sections 3 et 6), après la vérification qu'Ollama 0.40.5 refuse les adaptateurs LoRA. Aucune mesure n'a été faite.
- **26 octobre 2026, après la revue de Jibril** : population commune des comparaisons appariées après les erreurs techniques (sections 4 et 6) ; valeur complète de S, sans arrondi (section 7) ; conditions pour confondre T et le modèle de #31 (section 3) ; rejet des valeurs non finies par le script du seuil, dont le résultat est inchangé octet par octet. Aucune mesure n'a été faite.
- **30 octobre 2026, après la calibration du 29 octobre** (Jibril, sur le Legion, 8 questions du lot de calibration) : B0 était invalide, avec une réponse coupée à 512 tokens sur 8 (12,5 %). Sa consigne reprend désormais la phrase de brièveté de la #85, que B1 conserve (section 3). Version de référence d'Ollama : 0.40.11, rapportée par le Legion le 29 octobre au lieu de la 0.40.5 consignée, désormais épinglée et contrôlée par le script (sections 3 et 8). Machines décidées (section 8). Erreurs reproductibles et comparaisons descriptives précisées (sections 4 et 6). Empreintes du verrou indépendantes des fins de ligne (section 8). Aucune mesure n'a été faite sur le lot de test.
