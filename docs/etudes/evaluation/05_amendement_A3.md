# Protocole 05 : amendement A3, encodeur ajusté v3-C (questions écrites par Claude)

**Équipe** Data Tigers  
**Ticket** #167 (suite de #49, #164 et de l'amendement A2)  
**Responsable** Mahé BEGNIS  
**Statut** rédigé le 21 novembre 2026, avant toute génération ; audité par un sous-agent Claude Opus indépendant, corrigé, puis figé avec les valeurs de la section 9 avant le premier appel à un générateur. Le script refuse toute étape si un script ou un protocole n'est pas commité ; le commit de gel et l'empreinte de ce document sont publiés sur le #167. Le protocole 05 et les amendements A1 et A2 ne sont pas modifiés. Cet amendement modifie deux points du protocole 10 (section 7, famille E), pour la seule v3-C : le calendrier, qui excluait toute mise en service après le gel du 20 novembre, et la règle de décision, qui devient celle de la section 7 ci-dessous, plus stricte que celle de l'amendement A2.

---

## 1. Motif et décisions

La v2-T, entraînée sur 2 289 questions écrites par le témoin T, n'a pas fait mieux que la v1 servie : égalité exacte sur le CDTN, +5,8 points non démontrés sur le jeu v2, et −5,5 points, à titre descriptif, sur les questions humaines du lot de test (`10_resultats.md`, section 7). Cet amendement mesure, une seule fois, si la même recette fait mieux avec des questions écrites par un modèle plus capable.

Décisions de Mahé du 21 novembre, prises avant toute génération :

* **Générateur** : des sous-agents Claude Sonnet, en parallèle. **Relecteur et contrôleur** : Claude Opus. Aucun autre modèle.
* **Règle de mise en service durcie** (section 7), et mise en service visée le 22 novembre.
* **Ressources** : les calculs sur le Mac sont faits à priorité basse, avec un nombre limité de fils de calcul.

Par rapport à la v2-T, la recette d'entraînement, les passages, la consigne de la #49, le garde-fou et l'hébergement ne changent pas. Changent le générateur et ses conditions d'appel, et ce qu'ils imposent : les écarts sont listés à la section 8.

---

## 2. Données d'entraînement

* **Passages** : exactement ceux de la v2-T, lus dans `data/adaptation/v2/selection.json` (SHA-256 `47bc23ceffa13e422713676df821d81bf70ae78bfad84254d590d6737adb952a`). Ce sont 2 720 passages de 194 fiches, d'au moins 40 tokens : 2 442 pour l'entraînement, sur 175 fiches, et 278 pour la validation, sur 19 fiches. Les 67 fiches exclues, dont les 61 du lot de test, n'y figurent pas.
* **Lots** : 64 lots de 42 ou 43 passages. Les fiches sont rangées dans un ordre tiré par `numpy.random.default_rng(1121)`, les passages d'une fiche à la suite, puis distribués en tourniquet entre les 64 lots ; une fiche ayant au plus 60 passages, aucun lot n'en contient deux d'une même fiche. L'ordre des passages dans chaque lot est ensuite tiré au sort par le même générateur. Un lot mêle passages d'entraînement et de validation : le générateur ignore la partition.
* **Fichiers remis** : les lots sont copiés dans `~/NLP2_local/g3/`, et les 30 paires à relire dans `~/NLP2_local/r3/paires.json`, hors du dépôt. Ces deux dossiers, aux noms neutres, ne contiennent rien d'autre.
* **Générateur** : un sous-agent par lot, lancé par l'outil Agent de Claude Code (type `general-purpose`, modèle « sonnet »). L'identifiant exact `claude-sonnet-5-5` est exigé dans chaque réponse et chaque requête de son journal. L'invite est la consigne G3 de l'annexe, suivie d'une ligne vide, de « Fichier : » et du chemin absolu de son lot.
* **Consigne** : la consigne de `03_generer_paires_locales.py` (#49) mot pour mot, la même que pour la v2-T, appliquée à chaque passage entier, dans une enveloppe qui décrit le fichier du lot et le format de la réponse (consigne G3).
* **Isolement, contrôlé dans le journal** : les outils d'un sous-agent viennent de la définition de son type et des réglages de Claude Code. Le type `general-purpose` dispose des outils de la session : Bash, écriture de fichiers, appel à un autre sous-agent, et outils de connecteurs (MCP) qui agissent hors de la machine ; le mode automatique est actif. Les restreindre demanderait de modifier la configuration de Claude Code (un type d'agent limité à la lecture, des règles de refus), ce qui n'est pas fait sans l'accord exprès de Mahé. L'isolement n'est donc pas imposé ; il est contrôlé dans le journal que Claude Code tient pour chaque sous-agent. Sont exigés : une invite reçue identique à celle inscrite au registre ; un seul agent ; aucun appel d'outil autre que la lecture (Read) du fichier remis, une ou plusieurs fois, et une seule remise du rapport (SubagentHandback), en dernier ; aucun outil exécuté par le serveur. Un appel à un autre sous-agent, seul moyen de déléguer à un autre modèle, est donc refusé. Ce contrôle empêche d'utiliser une sortie obtenue autrement, mais ne défait pas une action déjà faite : ce risque est déclaré à la section 8 (n).
* **Registre** : avant chaque appel, la commande `lancer` inscrit le lancement (heure, numéro de tentative, empreinte de l'invite) dans `data/adaptation/v3/registre.jsonl`. Ce registre ne s'écrit qu'en ajout, et chaque ligne porte l'empreinte SHA-256 de la précédente : une ligne modifiée ou retirée est détectée. Le journal du sous-agent est copié dans `data/adaptation/v3/journaux/` avant tout contrôle, échecs compris, et son empreinte est inscrite au registre. Un journal commencé avant l'inscription de son lancement est refusé. Chaque résultat, conforme ou non, est inscrit avec l'empreinte de son journal ; pour un résultat conforme s'y ajoutent ce que le harnais a joint au contexte, les paramètres des requêtes et l'empreinte de leur forme (section 8). Les commandes du script s'exécutent une à une, sous un verrou exclusif ; seuls les sous-agents tournent en parallèle. Un registre incohérent (ligne modifiée ou retirée) arrête tout, et la v1 reste servie.
* **Relances** : est non conforme un lot dont le journal ou la réponse échoue à l'un des contrôles de cette section, ou dont les paramètres des requêtes (modèle, réflexion, niveau d'effort, plafond de tokens) diffèrent de ceux du premier appel conforme de l'étape, ou dont l'index de la mémoire joint au contexte diffère de celui du premier appel conforme. Un lot non conforme est relancé une seule fois, avec la même invite ; une seconde non-conformité du même lot arrête tout, et la v1 reste servie. Un lot conforme n'est jamais relancé.
* **Erreurs de l'opérateur, refusées sans rien inscrire** : un journal dont l'invite ne commence pas par la consigne de l'étape ou désigne le fichier d'un autre lot ou des juges, un agent déjà inscrit au registre, et un journal sans rapport final (agent encore en cours). Un agent arrêté sans rapport est inscrit non conforme par l'option `--echec`. Un lancement resté sans journal reconnaissable (agent jamais démarré, invite altérée dans ses premiers mots) ne peut pas être clos : il arrête tout au contrôle ci-dessous.
* **Aucun appel hors du registre** : avant l'assemblage, et de même pour les juges au bilan, le script parcourt les journaux de sous-agents de tous les projets de Claude Code. Chaque journal dont l'invite commence par la consigne G3 doit avoir son résultat au registre sous le lot que désigne son invite, et il doit y avoir autant de tels journaux que de lancements inscrits ; sinon tout s'arrête. Aucun essai avec les consignes G3 ou R3 ne peut donc être fait hors du registre.
* **Extraction** : la réponse de chaque sous-agent est lue dans son journal (rapport final), jamais recopiée à la main. Elle doit être un tableau JSON d'un objet par passage du lot, dans l'ordre, avec les seules clés `passage_id` et `question`. Seule tolérance : un bloc de code Markdown autour du tableau.
* **Filtres** : ceux de la v2-T, dans le même ordre (`09_generer_paires_v2.filtrer`). S'y ajoutent, en dernier, deux rejets au même seuil que pour le jeu v1 (indice de Jaccard supérieur à 0,40) : avec l'une des 161 questions du jeu v2 (étiquette `jeu-questions-v2`), puis avec l'un des 602 textes distincts du CDTN, réunion des 494 formulations mesurées et des 479 variantes du seuil. Les deux Jaccard maximaux sont gardés avec chaque paire.
* **Doublons** : comme pour la v2-T ; la première occurrence dans l'ordre de la sélection est gardée.
* **Volume minimal** : au moins 1 500 paires d'entraînement après filtres ; sinon tout s'arrête.
* **Relecture** : 30 paires d'entraînement tirées par `numpy.random.default_rng(20261121)` ; le fichier remis aux juges ne contient que ces paires (indice, question, passage). Elles sont jugées par deux sous-agents Claude Opus (identifiant exact `claude-opus-5-5`), avec la consigne R3 de l'annexe suivie du chemin du fichier, et les mêmes contrôles de journal que les générateurs. Les deux juges sont inscrits et lancés ensemble, avant toute ingestion de verdicts ; le bilan vérifie que les premiers journaux des deux juges ont commencé avant la première ingestion, et qu'il s'agit de deux agents et de deux journaux distincts. Chaque juge peut être relancé une seule fois après une non-conformité. Une paire est fausse si l'un des deux juges la juge fausse. **Le lot est utilisable si au plus 3 paires sur 30 sont fausses** ; sinon tout s'arrête et la v1 reste servie. L'accord des deux juges (kappa de Cohen) est rapporté. Les rapports des juges passent par l'orchestrateur, qui peut donc les lire ; aucune décision n'en dépend avant le bilan, seul à appliquer la règle.

---

## 3. Entraînement

* **Recette de la v2-T, inchangée** : modèle de départ `intfloat/multilingual-e5-small`, révision `614241f6` ; perte `MultipleNegativesRankingLoss` ; lot de 16, taux d'apprentissage 2e-5, 2 époques, échauffement de 10 %, décroissance des poids de 0,01, graine 42 ; préfixes `query: ` et `passage: ` ; processeur. Un test vérifie que la recette est celle de la v2-T.
* **Environnement exigé** : celui de la v2-T (`venv_ajustement_v2`), aux mêmes versions, contrôlées par le script : torch 2.14.0, transformers 5.17.0, sentence-transformers 6.1.0, datasets 5.0.1, accelerate 1.15.0 ; pour l'export, onnx 1.23.2 et onnxruntime 1.30.0. `HF_HUB_OFFLINE=1` est exigé : aucun téléchargement.
* **Ressources** : 4 fils de calcul, un fil d'interopération et une priorité basse, au lieu de tous les cœurs pour la v2-T. Cela allonge l'entraînement et peut changer les résultats à l'arrondi près, mais pas la recette.
* **Rapport** : nombre de paires, nombre de pas et pas d'échauffement, qui différeront de ceux de la v2-T (2 289 paires, 288 pas).
* **Modèle retenu** : celui de la fin de l'entraînement, jamais choisi sur la validation.

---

## 4. Garde-fou avant toute mesure

* **Jeu** : les questions des 19 fiches mises de côté, écrites par Sonnet, après les mêmes filtres.
* **Calcul** : comme pour la v2-T, en PyTorch fp32 avec le tokeniseur de l'encodeur de base, pour la base, la v1, la v2-T et la v3-C ; Recall@5 du passage d'origine.
* **Règle** : si le Recall@5 de la v3-C n'est pas strictement supérieur à celui de la v1, tout s'arrête, la v1 reste servie et aucun jeu d'évaluation n'est lu par la v3-C.
* **Biais connu** : les questions de validation viennent du même générateur que celles de l'entraînement, ce qui favorise la v3-C. Le garde-fou ne sert qu'à arrêter la mesure en cas de recul.

---

## 5. Hébergement

Les étapes de l'amendement A2, section 5, avec les chemins de la v3 et trois contrôles de plus. Un échec de l'un des contrôles empêche de servir la v3-C.

* **Contrôle de l'environnement d'export** : l'export rejoué sur la v1 doit redonner, bit à bit, les fichiers livrés le 14 octobre (fp32 `041a2d15…`, q8 `934a202b…`).
* **Export ONNX et q8** de la v3-C par la recette de `06_exporter_onnx.py`, seulement si le garde-fou inscrit au registre est passé et si les poids sont ceux du rapport d'entraînement.
* **Dossier au format de Transformers.js** (`data/adaptation/navigateur/ajuste_v3`), avec les fichiers du tokeniseur de la v1.
* **Élagage sans perte du vocabulaire** : `python scripts/allegement/elaguer_vocabulaire.py --dossier data/adaptation/navigateur/ajuste_v3 --nom multilingual-e5-small-ajuste-v3-q8-elague --sortie ~/NLP2_local/volet_a/elagage_v3`.
* **Contrôle en Python** : `python scripts/allegement/verifier_elagage.py <dossier élagué> --source data/adaptation/navigateur/ajuste_v3` ; découpages identiques et 935 sorties identiques bit à bit.
* **Contrôle dans le navigateur** : les 822 vecteurs de contrôle de la version élaguée sont identiques bit à bit à ceux de la version complète.
* **Index** : les 4 240 passages en fp32, encodés en PyTorch par la v3-C avec le tokeniseur de base, par `encoder_index`, copie fidèle de `ajustement_v2.construire_index` (amendement A2). Contrôle préalable : le même code, avec 4 fils, redonne l'index de la v2-T (`1bbdade6…`) ; un cosinus minimal ligne à ligne d'au moins 0,999999 est exigé, et l'identité bit à bit est rapportée.

---

## 6. Mesure

* **Commande** : `scripts/evaluation/mesures_10.py famille_e_a3`, au commit et aux empreintes de la section 9. Elle lit au registre de la v3 les empreintes du q8 exporté, de l'index et du garde-fou, et refuse de mesurer si le registre porte un arrêt, ou si l'amendement ou le script de la v3 ont changé d'une étape à l'autre.
* **Vecteurs des questions** : calculés dans Chrome par le q8 complet de la v3-C (`encoder_navigateur.py --modele ajuste_v3`, lots `jeu_v2`, `cdtn_mesure`, `navigateur` et `cdtn`), comme pour la v2-T ; recherche dense seule, aux conditions du site.
* **Jeux** : le jeu v2 (121 questions du corpus, 61 fiches) et le CDTN (494 formulations, 131 requêtes) décident ; le lot de test du jeu v1 (73 questions, 61 fiches) sert à la condition d ; les questions hors corpus du jeu v2 (40) et du lot de test (24) servent à la condition f.
* **Statistiques** : écart de Recall@5 (candidat moins v1) avec l'intervalle du score de Tango à 95 %, corrigé de l'effet de plan (par fiche ou par requête), non ajusté pour la multiplicité ; valeur p de décision égale à la plus grande des deux valeurs p, celle du test exact de McNemar et celle du test groupé d'Obuchowski ; correction de Holm sur quatre hypothèses : la v2-T et la v3-C, chacune sur le jeu v2 et sur le CDTN. Un candidat est dit démontré meilleur sur un jeu si la borne basse de l'intervalle y dépasse 0 et si sa valeur p corrigée y est inférieure à 0,05.
* **Seuils de la v3-C** : par les règles de la #164, 5e et 25e centiles (interpolation linéaire) des meilleurs scores des 479 variantes du CDTN de `cdtn_seuil.py`, encodées par la v3-C, contre l'index de la v3-C. La même fonction doit redonner exactement les seuils servis de la v1 (0,7683 et 0,8140).
* **Contrôles de reproduction**, tous exigés : la v1 redonne le Recall@5 du protocole 05 sur le CDTN ; la v2-T redonne, sur les trois jeux, exactement les chiffres du 17 novembre (`famille_e_20261117T134023Z.json` : effectifs, Recall@1, @5 et @10, MRR, rappel à la fiche, écart, intervalle, effet de plan, discordants, valeurs p exacte et groupée), sauf la valeur p corrigée, qui dépend du nombre d'hypothèses ; les seuils de la v1 sont reproduits ; deux exécutions donnent des résultats identiques : la décision ne vaut qu'à la seconde exécution, si elle est identique à la première, et une troisième est refusée. **Si un contrôle échoue, rien n'est décidé et la v1 reste servie.**
* **Code figé** : les empreintes de `mesures_10.py` et des modules qu'il utilise (`encoder_navigateur.py`, `metrics.py`, `ajustement_05.py`, `pertinence.py`, `recuperation.py`, `mesure.py`), et celle de `encodage_navigateur.html` avant l'ajout ci-dessous, sont inscrites à la section 9 ; `famille_e_a3` exige un dépôt propre, vérifie ces empreintes à chaque exécution et consigne le dernier commit de `mesures_10.py`, qui doit être celui de la section 9. Seule modification admise après le gel : l'ajout, dans `encodage_navigateur.html` (table `MODELES_LOCAUX`), de la ligne `ajuste_v3` avec l'empreinte du q8 inscrite au registre, inconnue avant l'export ; la page privée de cette seule ligne doit redonner son empreinte du gel, et son diff est publié sur le #167. Toute autre modification rend la mesure invalide.

---

## 7. Règle de mise en service, écrite d'avance

La v3-C remplace la v1 sur le site seulement si toutes les conditions suivantes sont remplies :

* **a.** le garde-fou de la section 4 est passé ;
* **b.** la règle de l'amendement A2 est satisfaite sur le jeu v2 et le CDTN : écarts de Recall@5 (v3-C moins v1) positifs ou nuls sur les deux jeux, et strictement positifs sur l'un d'eux ;
* **c.** la v3-C est démontrée meilleure que la v1 (section 6) sur le CDTN, ou bien sur le jeu v2 avec un écart strictement positif sur le CDTN : un gain démontré sur le seul jeu écrit par Claude ne suffit pas ;
* **d.** elle ne recule pas sur les questions humaines : écart de Recall@5 positif ou nul sur le lot de test du jeu v1 ;
* **e.** l'hébergement de la section 5 est validé, les seuils calculés par `famille_e_a3` sont ceux servis, les mesures descriptives du site sont refaites, et la PR est approuvée par au moins un autre membre de l'équipe, comme l'exige la protection de la branche, puis fusionnée avant le 26 novembre 2026 à 23 h 59 ;
* **f.** elle ne recule pas hors corpus : avec ses seuils recalculés, le nombre de questions hors corpus sous la borne de la zone grise (refusées ou signalées) est au moins celui de la v1 avec ses seuils servis, sur le jeu v2 et sur le lot de test. À titre indicatif, la v1 en place 39 sur 40 et 23 sur 24 sous la borne (relevé du 21 novembre, avant toute génération) : la marge est presque nulle.

`famille_e_a3` calcule les conditions a, b, c, d et f et leur conjonction ; la condition e est vérifiée et consignée sur le #167. Sinon, la v1 reste servie et la v3-C est publiée comme un résultat. La v2-T n'est pas servie.

---

## 8. Écarts déclarés et limites

* **(a) Lots** : un sous-agent écrit 42 ou 43 questions à la suite, au lieu d'un appel par passage pour la v2-T. Les passages voisins viennent de fiches différentes, mais des effets de position ou un souci de varier les questions d'un même appel restent possibles.
* **(b) Échantillonnage** : l'outil Agent ne fixe ni la température ni une graine (la v2-T : température 0,3, top_p 0,9, 75 tokens au plus, une graine par passage). Les paramètres réellement envoyés (modèle, réflexion adaptative, niveau d'effort, plafond de tokens) sont relevés dans chaque journal et inscrits au registre. La génération n'est pas rejouable ; les sorties brutes et les journaux sont conservés avec leurs empreintes.
* **(c) Nombre de paires** : il différera de celui de la v2-T, donc aussi le nombre de pas et d'échauffement ; il est rapporté.
* **(d) Filtres ajoutés** : la proximité avec le jeu v2 et avec le CDTN, qui n'existaient pas pour la v2-T. Mesuré par l'audit sur les questions de la v2-T : le premier n'en aurait rejeté aucune, le second 24 sur 2 289.
* **(e) Relecture plus stricte** : deux juges, verdict le plus sévère, au plus 3 fausses sur 30. Sous cette règle, la v2-T aurait été refusée (5 fausses dans la réunion des deux lectures, amendement A2, section 8). La relecture est faite par des modèles, et non par des humains.
* **(f) Fils de calcul** : 4, et un fil d'interopération, au lieu de tous les cœurs (section 3).
* **(g) Conditions d'appel** : l'invite système et les outils de Claude Code font partie des conditions de génération ; l'empreinte de la forme des requêtes, tenue par Claude Code, est inscrite au registre.
* **(h) Code de mesure** : `famille_e_a3` est écrit et figé avant toute génération ; la seule modification admise ensuite est déclarée à la section 6.
* **(i) Ce que reçoivent les sous-agents** : en plus de l'invite, le harnais joint au contexte de chaque sous-agent l'index de la mémoire du projet (`MEMORY.md`), l'état git du début de session, les listes des outils, compétences et agents disponibles, les instructions des serveurs MCP, l'indication du mode automatique, une description de l'environnement (dossier, plateforme), un rappel système, la date et l'identifiant de l'organisation. Les types de ces pièces sont relevés dans chaque journal, et les empreintes de l'index de la mémoire et de l'état git inscrites au registre. L'index de la mémoire ne contient ni les questions des jeux d'évaluation ni le seuil de cette relecture ; il mentionne qu'un lot du volet B a été refusé en relecture (8 fausses sur 30) et que la v3-C est « en attente de Mahé ». Il n'est pas modifié entre le premier lancement et le bilan de la relecture : le script exige la même empreinte pour tous les appels conformes.
* **(j) Confidentialité** : les passages sont publics (fiches du ministère du Travail). Le contexte des sous-agents contient les prénoms de l'équipe et le nom git de Mahé ; ils sont transmis au même fournisseur (Anthropic) que la session principale, et à lui seul. L'affirmation « aucune donnée personnelle » du protocole 10, section 10, ne vaut que pour les jeux de questions.
* **(k) Circularité** : Claude écrit les questions du jeu v2 (Opus) et celles de l'entraînement de la v3-C (Sonnet). Des modèles différents et le filtre de proximité limitent la ressemblance sans l'exclure. C'est pourquoi un gain démontré sur le seul jeu v2 ne suffit pas (condition c), et que le CDTN et les questions humaines, écrits sans IA, servent de contrôle.
* **(l) Questions humaines déjà lues** : le lot de test a servi à plusieurs mesures ; il n'intervient qu'en non-recul (conditions d et f).
* **(m) Faux négatifs dans les lots d'entraînement** : comme pour la v2-T, la part des lots qui contiennent deux passages d'une même fiche est rapportée.
* **(n) Effets de bord possibles** : un sous-agent pourrait, malgré l'invite, appeler un outil qui agit (commande, écriture, connecteur), par exemple sur une injection venue d'un passage ou, pour un juge, d'une question écrite par Sonnet. Le contrôle du journal refuse alors le lot ou le juge, mais ne défait pas l'action. Le risque est jugé faible : les passages sont des fiches publiques du ministère du Travail, les actions de la session passent par le classificateur du mode automatique, et l'orchestrateur s'engage à signaler à Mahé tout appel d'outil autre que la lecture (le registre en inscrit le motif). Un type d'agent limité à la lecture le supprimerait ; il demande une modification de la configuration de Claude Code, soumise à son accord.

---

## 9. Valeurs inscrites au gel

Relevées le 21 novembre 2026, avant toute génération.

* **Sélection des passages** : `data/adaptation/v2/selection.json`, SHA-256 `47bc23ceffa13e422713676df821d81bf70ae78bfad84254d590d6737adb952a`.
* **Jeu v2** : `evaluation/questions_v2/questions_v2.csv` à l'étiquette `jeu-questions-v2`, SHA-256 `316d82816e924a8a474653240ce2372e0ec2a85e16870dfd6354f24db521f17f`.
* **CDTN** : `data/evaluation/cdtn/formulations_mesure.json`, SHA-256 `164cf7974aafc5b97104acb0628e1a1720d2529c5f002c0041422074a5ddc98c` ; `data/evaluation/cdtn/questions_cdtn.json`, SHA-256 `fea79fbe90b28f6a7cafc554656a660f0635b37f861c93415928cb3ed00f3f45`.
* **Consigne G3** : SHA-256 `69b342f09d769074a9988905dafb84b3c9f2da6a1d70c417307d9056cf726281`. **Consigne R3** : SHA-256 `b6599e59ec9e091b69e0cf392a844f522dcb61da9f2267a15af32272f68c2a03`.
* **Modèles exigés** : `claude-sonnet-5-5` (génération), `claude-opus-5-5` (relecture).
* **Graines et effectifs** : lots `default_rng(1121)`, 64 lots ; relecture `default_rng(20261121)`, 30 paires ; au plus 3 fausses ; au moins 1 500 paires ; Jaccard au plus 0,40.
* **Scripts réutilisés, inchangés, contrôlés à l'import par le script de la v3** : `09_generer_paires_v2.py` `98aa305b232be4be270f2d54f8c36b5fdd7ec3d82b3da718a4787e919db44ca1` ; `10_ajuster_encodeur_v2.py` `4c2274bf16cbc50fed0a9975066e93f099183eab41128755954ee435f77b91c7` ; `11_exporter_v2.py` `369fb283881a551d9033095212a9f7e6ae97369655064fe5a5f5716616b0bef1` ; `06_exporter_onnx.py` `3491d0495d286b5135f2b71917d07f9b65306d8db41fe8cf5624598b62adbd7f` ; `scripts/evaluation/ajustement_05.py` `925e800adf1107fdbd7233c94ff3502f3ae83abe1f5798d2cd8716d872f9fb36` ; `scripts/evaluation/ajustement_v2.py` `af1696ee98d681644382e78a3d6ba04986b54361884c0e152c62f1cc5e68ff90` ; `scripts/evaluation/metrics.py` `1c9c28f2e0933016b32c1293c50ea1eb2d521bc91f05e69c2a2d4b26cb4f2de4` ; `scripts/rag/rag.py` `302dce21a9ce81a67f804016078e7fc2ed2868aaf920693c1b74e19719c7ca9e`.
* **Références de la v2-T** : poids `508868b82a21b6fd769636db254d90173d680188eedcd60ee9e4b8826b322e6c`, index `1bbdade6b7568f84650167d566b1eeba9f9ca180aef3481683d60bfaa57d06e3`, mesure du 17 novembre `13c474b82fc6d41eb200619b899cad822991106bfe78faaa824417d72a93f231`.
* **Code de mesure** (branche `docs/171-protocole-10`, commit `b0332774dfdc23fb7e8039426228b18172e902da`, dernier à modifier `mesures_10.py`) : `scripts/evaluation/mesures_10.py` `8c9aaebd1348869210358c759dbebd840a0e4fba8f43ec87268c9f758ef0889b` ; `scripts/evaluation/encoder_navigateur.py` `62d5be890952851c2cc8a7c67c48e7ccc3afb40a48db39eff997475d900e8625` ; `scripts/evaluation/pertinence.py` `5acd3aa98b6f035bfddfc724ed187c7dad4842950423a044d5ce2451669151fb` ; `scripts/recuperation/recuperation.py` `694c3755032fcc31e4e16b719da686359ed5312c37047fd9d2703256a34cbddb` ; `scripts/rag/mesure.py` `d6a4df6a7c1d812abed4f677ca081f4bf40f7c6a10377352e08d127c96215e38` ; `scripts/evaluation/encodage_navigateur.html`, avant l'ajout de `ajuste_v3`, `20360c5b55b98efb3f6053c845caad533cbd8c17d87fdbd85bb6323c995747ab` ; `metrics.py` et `ajustement_05.py` identiques à ceux ci-dessus.
* **Script de la v3 et ses tests** : `scripts/adaptation/12_encodeur_v3.py` et `scripts/adaptation/test_encodeur_v3.py`, au commit de gel ; le script inscrit ce commit et les empreintes de cet amendement et de lui-même à chaque étape du registre.

---

## 10. Historique

* **21 novembre 2026** : amendement rédigé ; audité par un sous-agent Claude Opus indépendant (16 constats, dont 2 bloquants : isolement des sous-agents non contrôlé, relances non bornées ni tracées ; verdict « gel possible après corrections ») ; corrigé ; essai du format des journaux sur un appel sans enjeu ; second audit (aucun constat bloquant ; trois importants : journal attribué à un autre lot, registre sans verrou, effets de bord des outils, et sept mineurs) ; corrigé, tests et mutations rejoués ; figé avant toute génération.

---

## Annexe. Consignes, mot pour mot

Chaque invite est la consigne, suivie d'une ligne vide, de « Fichier : » et du chemin absolu du fichier remis.

**Consigne G3, génération des questions (sous-agents Sonnet, un par lot).**

> Lis uniquement le fichier indiqué, et n'ouvre aucun autre fichier : c'est un tableau JSON de passages, chacun avec passage_id, titre_fiche et texte. Pour chaque passage, dans l'ordre du fichier, applique la consigne ci-dessous, en remplaçant {titre} par le titre_fiche et {texte_passage} par le texte du passage. Réponds uniquement par un tableau JSON, un objet par passage, dans l'ordre du fichier, de la forme {"passage_id": "...", "question": "..."}, sans aucun texte avant ni après.
>
> Consigne :
>
> Tu es un salarié ou un travailleur qui cherche une information précise sur ses droits ou obligations.
> À partir de l'extrait de fiche du ministère du Travail ci-dessous, formule une question réaliste, précise et naturelle en français qu'un salarié pourrait poser et dont la réponse figure dans cet extrait.
>
> Règles impératives :
> 1. Formule UNIQUEMENT la question, sans introduction, sans guillemets, ni formule de politesse.
> 2. La question doit être autonome et compréhensible sans avoir lu le texte (pas de "Selon le texte", "D'après l'extrait").
> 3. Termine par un point d'interrogation.
>
> Titre de la fiche : {titre}
> Extrait :
> {texte_passage}
>
> Question :

**Consigne R3, relecture des 30 paires tirées (deux sous-agents Opus).**

> Lis uniquement le fichier indiqué, et n'ouvre aucun autre fichier : il contient 30 paires, chacune avec un indice, une question et le passage d'où elle a été tirée. Pour chaque paire, dis si elle est juste ou fausse. Une paire est fausse si la question ne se comprend pas sans le passage (renvoi au texte ou à la fiche, pronom ou démonstratif sans antécédent), ou si le passage n'y répond pas, même en partie. Sinon, elle est juste. Réponds uniquement par un tableau JSON, dans l'ordre du fichier, de la forme {"indice": 0, "verdict": "juste", "motif": ""}, avec verdict « juste » ou « fausse » et, pour une paire fausse, un motif d'une phrase ; sans aucun texte avant ni après.
