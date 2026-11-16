# Séparation du pilote et des données d'adaptation

Contrôle du 9 novembre 2026, `dev/a294d25`, révision initiale du pilote `377717f`. Résultats détaillés et ensembles d'URLs dans [audit_separation.json](audit_separation.json).

**Mise à jour du 12 novembre :** le [contrôle du fichier réel des paires encodeur](verification_encodeur_20261112.md) est désormais disponible. Les mentions de données non reçues ci-dessous décrivent l'état historique du 9 novembre ; le rapport et le suivi du plan distinguent ce nouveau contrôle technique de celui des lots Qwen rapporté par Mahé en revue de #145.

## Ce qui a été vérifié

| Chaîne | Sources examinées | Règle constatée |
|---|---|---|
| Qwen, #107/#130 | `scripts/adaptation_qwen/separation.py` et `donnees_adaptation.py` | 61 fiches du test humain exclues des cibles et des contextes ; contrôle final des exemples assemblés |
| Encodeur, #49 | `scripts/adaptation/01_preparer_benchmark.py` et `03_generer_paires_locales.py` | URLs du jeu humain, calibration comprise, retirées du vivier avant le tirage des paires |

Le jeu est épinglé au tag `jeu-questions-v1`, commit `cdb48c97064de625df61703a9a41e106160e0f50`, SHA-256 `807498144fec46722ffab045a87c191b6282a86300799976869d4d6c1755fb35`. Seules les colonnes `url`, `lot` et `type` sont exploitées pour ce contrôle ; aucun texte de question ou extrait humain n'est utilisé pour choisir les sources ou rédiger des cas.

Le script de préparation de l'encodeur lit une branche mutable, `origin/feat/44-jeu-questions-annotees`. Son fichier a ici la même empreinte que le tag. Ce constat est daté ; il ne prouve pas quel fichier a été utilisé lors d'une exécution ancienne. L'audit garde cette limite explicite.

Le calcul donne 61 URLs côté Qwen et 66 URLs non vides côté encodeur ; les 61 sont incluses dans les 66. Le README encodeur en annonce 67. Cette contradiction est signalée, sans inventer une URL supplémentaire ou modifier la documentation de l'autre domaine.

## Conséquence sur le tirage

Dans la première préparation, 17 des 20 fiches sont hors des deux listes d'exclusion. Elles sont donc potentiellement autorisées dans les viviers d'adaptation, **sans preuve ici de leur sélection réelle**. Trois sont exclues : le versement du salaire, la modification du contrat de travail et les documents remis à la rupture du contrat.

La révision 2 choisit ses fiches dans l'intersection des exclusions. Après retrait de la fiche historique du congé sans solde, il reste 60 fiches possibles ; les deux autres fiches historiques ne sont pas dans cette intersection. Le tirage déterministe donne 25 fiches et 30 passages : zéro fiche dans les viviers autorisés par les règles examinées. Le plan et le rapport décrivent le filtre technique de longueur et tous les identifiants.

Les 30 textes complets sélectionnés ont aussi été comparés à ceux des fiches autorisées de chaque vivier : aucun texte intégral identique n'est trouvé. Ce contrôle ne recherche pas les recopies partielles ou les paraphrases et ne remplace pas le contrôle des fichiers privés.

Ce changement précède toute génération. La première version reste au commit `377717f` ; ses sources ne sont pas réinterprétées comme des candidats rejetés. Les questions humaines, leur annotation et leur protocole restent inchangés.

## Ce que ce contrôle ne démontre pas

Les fichiers privés de paires encodeur et du lot Qwen `v2b-20261107` ne sont pas disponibles ici. Les nombres et empreintes abrégées rapportés dans #107/#130 constituent des déclarations sourcées, pas une relecture de leurs octets. Aucun entraînement réel, acceptation de lot ou adaptateur utilisé n'est déduit de la fusion de #130.

La séparation des viviers ne prouve pas l'absence de recopie entre textes proches de fiches différentes, de doublon de question ou d'un ancien jeu de données non conforme aux règles. Les futurs candidats n'existent pas encore : leur déduplication contre les données synthétiques d'adaptation n'est donc pas possible à ce stade.

Les 25 fiches choisies appartiennent au test humain. La réserve documentaire les protège de l'adaptation selon les règles, mais le pilote ne constitue pas une nouvelle évaluation indépendante du jeu humain. Aucun résultat synthétique ne doit être ajouté à ses effectifs ou servir à régler son seuil/protocole. Le RAG conserve l'accès au corpus complet : présence dans l'index et présence dans l'entraînement sont deux contrôles distincts.

## Contrôle des lots locaux avant génération et gel

Sur la machine qui détient les données, ou à partir d'un rapport complet dont les entrées sont vérifiables :

1. Identifier les lots effectivement retenus, leur commit, configuration et manifeste. Contrôler les empreintes complètes des fichiers contre les manifestes ; ne pas substituer un ancien lot v2 au v2b.
2. Pour Qwen, inventorier au minimum les fichiers `1_sources.jsonl`, `3_contextes.jsonl`, `train.jsonl` et `valid.jsonl` du lot retenu sous `data/volet_b/donnees_adaptation/`. Comparer tous les passages cibles et de contexte, pas seulement les réponses attendues. Relever aussi les questions synthétiques/pilotes déjà utilisés pour préparer la déduplication future.
3. Pour l'encodeur, examiner les `excluded_urls` de `data/adaptation/exclusions_train.json` et les passages/URLs de `train_paires.jsonl`, ainsi que toute autre entrée réellement utilisée. Confirmer la provenance du fichier de référence lu par le script.
4. Résoudre chaque identifiant avec le corpus M2 vérifié ; un identifiant inconnu, une entrée manquante, une empreinte incohérente ou une configuration non identifiée bloque le constat. Comparer les ensembles aux 25 fiches de ce plan. Rechercher aussi les textes exactement dupliqués entre sources choisies et sources d'adaptation ; toute proximité sémantique importante est à examiner humainement.
5. Conserver dans le rapport les chemins relatifs, empreintes complètes, nombres d'exemples, intersections et limites. Ne pas publier les questions humaines ou les réponses de relecture privées. Tant que ce rapport n'est pas disponible, `lots_prives_controles` reste `false` et le champ humain de la grille reste vide.
6. Après génération, comparer les questions exactes et normalisées aux questions synthétiques d'adaptation et aux essais antérieurs, puis examiner les doublons de sens. Un résultat nul ne certifie pas à lui seul l'indépendance sémantique. Aucun cas nouveau n'est ajouté à l'entraînement.

La validation humaine de ces contrôles, du plan et de ses limites reste à consigner. Aucun message à l'équipe n'est envoyé par cette préparation.
