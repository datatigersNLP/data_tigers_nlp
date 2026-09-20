# Rapport de jalon J2

**Équipe** Data Tigers
**Membres** Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE
**Module** NLP 2, projet de fin de module
**Formation** Master 2 Data & IA
**Établissement** FGES, Université Catholique de Lille
**Année universitaire** 2026-2027
**Enseignant** Adrian ROSARI
**Date de remise** 21 septembre 2026

**Objet.** Ce document restitue les cinq éléments attendus au jalon J2 : environnement de développement déclaré, board de tickets créé, étude du volet A, étude du volet B, éléments de cadrage.

Sauf mention contraire, tous les chiffres de ce rapport proviennent d'une mesure effectuée les 18 et 19 septembre 2026. La méthode est décrite en annexe.

*Ce document a été produit avec l'assistance d'outils d'intelligence artificielle. Chaque élément a été relu et validé par un membre de l'équipe, et les usages sont consignés dans le journal prévu par le sujet.*

---

## 1. Environnement de développement

### 1.1 Socle commun

L'équipe converge sur un socle unique. Python est déclaré en version minimale, les autres outils dans la version effectivement relevée sur la machine de référence.

| Outil | Version | Usage |
|---|---|---|
| VS Code | 1.137.0 | éditeur commun |
| Python | 3.12 ou supérieur (environnement virtuel dédié) | volet B, préparation du corpus, export ONNX |
| PyTorch | 2.14.0 | encodeur, bancs d'essai |
| Node.js et npm | 25.9.0 et 11.12.1 | volet A, Transformers.js, chaîne de construction du site |
| Vite | 8.3.0 | volet A, construction du site et serveur de développement |
| React | 19.3.0 | volet A, interface et gestion de l'état de l'application |
| Tailwind CSS | 4.3.3 | volet A, système visuel de l'interface |
| Git et GitHub CLI | 2.50.1 et 2.92.0 | versionnage, board, intégration continue |
| uv | 0.11.0 | gestion des dépendances Python |

Point de vigilance relevé : le Python du système est en version 3.9.6 sur la machine de référence. Tout le travail passe par l'environnement virtuel. Un script lancé avec l'interpréteur système échoue sur des dépendances absentes.

Les trois outils du volet A ont été retenus après une construction d'essai. React, Tailwind et le code applicatif représentent 69,5 Kio compressés dans le site livré, et l'application construite charge l'encodeur puis produit un résultat sans erreur. Le choix suppose une configuration explicite du chemin de base du site, faute de quoi la construction réussit mais la page reste vide une fois déployée.

### 1.2 Divergence déclarée

Une seule divergence est déclarée, sur l'assistant de développement.

| Assistant | Membres concernés | Motif |
|---|---|---|
| Claude Code | membres disposant d'un abonnement | abonnement payant, non détenu par toute l'équipe |
| Google Antigravity | les autres membres | téléchargement gratuit, version Apple Silicon disponible |

Cette divergence ne touche ni le code produit, ni les dépendances, ni les conventions de commit. Les deux assistants écrivent dans le même dépôt avec les mêmes règles.

Règle commune adoptée : toute portion de code produite avec assistance passe en revue par le binôme, et le relecteur doit savoir l'expliquer. Cette règle répond directement à la clause du sujet selon laquelle n'importe quel membre peut être interrogé sur n'importe quelle portion du code.

---

## 2. Board de tickets

Toute la conduite de projet est hébergée sur GitHub, dans l'organisation `datatigersNLP`. Le dépôt `data_tigers_nlp` est créé et les cinq membres de l'équipe y sont inscrits.

**Tickets ouverts à ce jour.** Les six tickets ci-dessous ont été créés au fil du travail, et non après coup.

| Ticket | Création | État | Labels |
|---|---|---|---|
| Création du dépôt GitHub | 12/09 | fermé | transverse |
| Weekly 1 | 14/09 | fermé | transverse |
| Choix des cas d'usage | 19/09 | ouvert | transverse, arbitrage |
| Choix du modèle d'embeddings | 19/09 | ouvert | volet-a, encodeur, arbitrage |
| Livrable J2 | 19/09 | ouvert | transverse, documentation |
| Weekly 2 | 19/09 | ouvert | transverse |

Tous sont assignés nominativement. Les cinq tickets postérieurs à la création du dépôt sont rattachés au milestone J2.

**Milestones créés.** Un par jalon noté, chacun portant son échéance et son barème. Le milestone agrège l'avancement, ce qu'un label ne sait pas faire.

| Milestone | Échéance | Points |
|---|---|---|
| J2 Cadrage et étude des volets | 21/09/2026 | 10 |
| Mi-parcours Volet A en ligne | 01/10/2026 | 10 |
| J3 Volet A fonctionnel | 16/10/2026 | 15 |
| J4 Soutenance | 07/12/2026 | 60 |

**Labels créés.** Trois axes indépendants, pour qu'un ticket porte un volet, un domaine et un marqueur de pilotage sans ambiguïté.

| Axe | Labels | Rôle |
|---|---|---|
| Volet | volet-a, volet-b, transverse | à quel livrable la tâche appartient |
| Domaine | corpus, encodeur, front, rag, eval | reprend exactement les cinq domaines de la section 5.5 |
| Pilotage | bloquant, bonus-outils, arbitrage | priorité, alimentation du bonus, décisions tranchées |

Le label `documentation`, fourni par défaut, est réutilisé plutôt que dupliqué. Les cinq labels de domaine portent les mêmes noms que les domaines de la répartition des tâches, ce qui permet de vérifier directement la cohérence entre organisation déclarée et travail réalisé.

**Colonnes du board.** Les tickets, labels et milestones décrits ci-dessus sont en place et directement vérifiables sur le dépôt. Le board GitHub Projects les agrège selon six colonnes, retenues pour coller au déroulement réel du travail plutôt qu'à un modèle générique.

| Colonne | Ce qu'elle contient |
|---|---|
| Todo | tâche identifiée, pas encore commencée |
| In progress | tâche en cours |
| Besoin d'aide | tâche bloquée, à reprendre en binôme ou en réunion |
| A discuter | tâche dont le périmètre ou la méthode ne fait pas consensus |
| Test | travail terminé, en attente de vérification par un autre membre |
| Done | tâche terminée et vérifiée |

Deux colonnes méritent un mot. **Besoin d'aide** et **A discuter** rendent visibles les blocages et les désaccords, qui sont précisément ce que le sujet demande de traiter dans le retour d'expérience. Une tâche qui y stationne est un point d'ordre du jour pour la réunion hebdomadaire. **Test** matérialise la revue par un tiers : une tâche ne passe pas directement de In progress à Done, ce qui applique la règle selon laquelle toute production est relue par le binôme du domaine.

Le board porte un champ **Estimate**, utilisé pour la charge estimée et repris dans le classeur de suivi.

**Traçabilité des abandons.** Le sujet valorise le fait de documenter les arbitrages, y compris les abandons de fonctionnalité. Plutôt qu'une colonne dédiée, nous utilisons le label `arbitrage` posé sur le ticket, fermé avec son motif écrit. La décision reste ainsi retrouvable par recherche, sans encombrer le board.

Règle de tenue adoptée : aucune tâche n'est engagée sans ticket créé au préalable. Le contrôle est fait en revue hebdomadaire.

**Contraintes techniques du dépôt, mesurées le 11 septembre 2026** (organisation en plan Free, dépôt privé) :

| Fonction | État | Contournement retenu |
|---|---|---|
| Protection de branche | indisponible en plan Free | convention écrite et contrôle en revue de PR |
| GitHub Pages | indisponible sur dépôt privé | le dépôt du volet A sera public |
| Automatisations Projects v2 | 4 workflows natifs seulement | déplacement manuel, vérifié chaque semaine |
| GitHub Actions | minutes comptées sur dépôt privé | intégration continue sur pull request uniquement |

**Organisation du dépôt.** Le sujet annonce que le dépôt sera consulté et que la stratégie de branches sera évaluée. Nous retenons une organisation volontairement simple, pour qu'elle tienne onze semaines.

| Branche | Rôle |
|---|---|
| `main` | état livrable, ce que l'enseignant consulte. Tag posé à chaque jalon |
| `dev` | intégration du travail en cours |
| `feat/NN-sujet`, `fix/NN-sujet`, `docs/NN-sujet` | une branche par ticket, fusionnée dans `dev` |

À chaque jalon, `dev` est fusionnée dans `main` et un tag est posé. Pour le jalon de mi-parcours, le sujet demande de préparer une branche permettant d'observer le travail réalisé : la branche `jalon/mi-parcours` sera figée à cette date, en plus du tag.

**Messages de commit.** Convention `type(portée): description`, avec les types `feat`, `fix`, `docs`, `chore`, et le numéro du ticket en référence.

**Revue.** Une pull request par branche, relue par le titulaire secondaire du domaine concerné. Cette règle fait coïncider la revue de code avec la répartition déclarée en section 5.5, ce que le sujet annonce vouloir vérifier.

**Documentation.** Les documents de jalon et le journal d'usage de l'IA sont versionnés dans un répertoire `docs/` sur `main`, et non sur une branche séparée. Une branche de documentation permanente ne fusionnerait jamais et deviendrait invisible depuis la branche consultée par l'enseignant.

Accès au board : lien communiqué par courriel avec le présent rapport. Le classeur de suivi et le journal d'usage de l'IA sont versionnés dans le dépôt et accessibles aux mêmes conditions.

---

## 3. Étude du volet A

### 3.1 Cas d'usage retenu

Nous retenons le cas **A3, recherche sémantique en corpus fermé**. Le système retourne les passages pertinents d'un corpus normatif en réponse à une question en langage naturel, avec le score de similarité, la référence de la section d'origine et le lien vers le document complet. Aucune génération n'est produite.

Ce choix est fait conjointement avec le cas B1 du volet B. A3 constitue la couche de récupération de B1 : corpus, découpage, encodage et index sont écrits une fois et servent aux deux volets. L'économie estimée est de 5 à 8 jours-homme par rapport à deux cas sans recouvrement.

### 3.2 Corpus

Nous partons sur le jeu de données public **`AgentPublic/travail-emploi`**, publié par l'administration française.

| Caractéristique | Valeur mesurée |
|---|---|
| Volumétrie | 5 702 passages |
| Taille | 29,6 Mio |
| Licence | Etalab 2.0 |
| Dernière mise à jour | 11 septembre 2026 |
| Colonnes | `title`, `url`, `text` |
| Adresse | `https://huggingface.co/datasets/AgentPublic/travail-emploi` |

Trois raisons à ce choix. La volumétrie correspond à la cible fixée. Le corpus est déjà découpé en passages porteurs de leur URL source, ce qui fournit directement les trois éléments de sortie exigés par le cas A3. Le contenu est normatif et francophone, et la recherche par mot-clé y est notoirement inefficace, ce qui rend le gain de la recherche sémantique démontrable.

Une vérification a écarté les documents internes de la formation : le règlement des études et les syllabus ne figurent pas dans le sitemap public du site de l'établissement, et le domaine `fges.fr` renvoie une erreur HTTP 468. Ils sont accessibles sur l'intranet, mais doivent être rassemblés manuellement.

Nous nous laissons la possibilité de changer de corpus dans la semaine qui vient si une contrainte l'impose. Le basculement serait alors documenté comme un arbitrage.

### 3.3 Modèle envisagé

Le modèle retenu est **`Xenova/multilingual-e5-small`**, encodeur multilingue quantifié en 384 dimensions, exécuté par Transformers.js.

Sept candidats ont été mesurés. La limite dure de GitHub est de 100 Mio par fichier.

| Modèle | Poids quantifiés | Verdict |
|---|---:|---|
| `Xenova/multilingual-e5-small` | 112,8 Mio | retenu |
| `Xenova/paraphrase-multilingual-MiniLM-L12-v2` | 112,8 Mio | équivalent, sans avantage |
| `Xenova/distiluse-base-multilingual-cased-v2` | 129,0 Mio | plus lourd |
| `Xenova/multilingual-e5-base` | 265,7 Mio | 2,4 fois plus lourd |
| `onnx-community/embeddinggemma-300m-ONNX` | 294,6 Mio | hors budget |
| `Xenova/bge-m3` | 543,3 Mio | hors budget |
| `Xenova/all-MiniLM-L6-v2` | 21,9 Mio | anglais uniquement |

Deux écueils rencontrés pendant cette comparaison méritent d'être signalés. Le modèle `embeddinggemma-300m` était annoncé par l'API à 0,5 Mio, alors que ses poids, stockés dans des fichiers externes, représentent en réalité 294,6 Mio. Par ailleurs, deux dépôts couramment cités, `Xenova/sentence-camembert-base` et `Xenova/gte-multilingual-base`, n'existent pas.

**Architecture retenue.** Les passages du corpus sont encodés hors ligne, une seule fois, et l'index est livré en fichier statique. Seule la requête de l'utilisateur est encodée dans le navigateur. L'encodeur ne traite donc jamais plus de quelques dizaines de tokens.

Taille de l'index pour 5 702 passages en 384 dimensions : 8,35 Mio en float32, 2,09 Mio en int8. L'index n'est pas un problème de volume.

**Référence de comparaison.** Un index TF-IDF est construit en JavaScript pur, entièrement maîtrisé, et sert de référence à battre. Cette comparaison alimente directement l'analyse technique demandée au rapport final.

**Réponse à la valorisation demandée par le sujet.** Le sujet indique que « le modèle servi doit préférentiellement être celui que vous avez entraîné ». Pour un cas de recherche sémantique, entraîner un encodeur depuis zéro n'est pas réaliste : cela supposerait un corpus et une supervision hors de portée en onze semaines. Trois voies cumulables rendent néanmoins le modèle servi réellement nôtre.

| Voie | Nature | Coût mesuré |
|---|---|---|
| Ajustement fin contrastif sur notre corpus | le modèle est réentraîné sur nos données | 89 ms par pas, lot de 32 paires |
| Réduction du vocabulaire aux tokens du corpus | l'artefact servi est produit par nous | à mesurer |
| Index TF-IDF et BM25 écrits en JavaScript | modèle entièrement maîtrisé, sans dépendance | quelques dizaines de kilo-octets |

**L'ajustement fin est le point central, et son coût a été mesuré.** Des paires question-passage sont générées à partir du corpus par le modèle local du volet B, puis l'encodeur est ajusté par apprentissage contrastif. Sur la machine de référence, un pas d'entraînement sur un lot de 32 paires prend 89 ms. Trois époques sur 17 106 paires, soit trois questions par passage, demandent 2,4 minutes. Le temps de calcul n'est donc pas un obstacle.

Le relevé confirme au passage le calcul du paragraphe précédent : le modèle chargé compte 117,7 millions de paramètres, contre 117,3 millions prédits, soit un écart de 0,3 pour cent.

**Ce que cela produit comme mesure.** Recall@5 avant et après ajustement, sur le même jeu de référence. C'est un avant-après sur le volet A, symétrique de celui que le sujet exige sur le volet B.

**Précaution à prendre.** Les paires d'entraînement étant générées par un modèle, le jeu de référence doit être rédigé par des humains. Sans cette séparation, la mesure porterait sur la capacité de l'encodeur à retrouver le style de questions du générateur, et non sur sa pertinence réelle.

### 3.4 Faisabilité de l'exécution navigateur

La faisabilité a été vérifiée par la mesure, et non par estimation. Protocole : page statique servie en local, bibliothèque `@huggingface/transformers` 4.3.0 chargée depuis un CDN, modèle quantifié en 8 bits, encodage d'une question en français, 20 passes après chauffe, navigateur Chromium piloté par Playwright sur la machine de référence.

| Mesure | Première visite | Visite suivante |
|---|---:|---:|
| Import de la bibliothèque | 87 ms | 5 ms |
| Chargement du modèle | 3 052 ms | 568 ms |
| Inférence d'une requête, médiane sur 20 | 19,8 ms | 19,2 ms |
| Dispersion de l'inférence | min 18,8 ms, max 20,7 ms | |
| Octets transférés | 135,6 Mio | 0,16 Mio |

La sortie a été contrôlée : tenseur de dimensions 1 par 384, norme euclidienne de 1,0000 après normalisation. Le vecteur est directement exploitable pour un calcul de similarité cosinus. WebGPU est disponible sur la machine de test, avec l'adaptateur `apple / metal-3`, ce qui ouvre une piste d'optimisation sans être nécessaire.

**Conclusion de faisabilité.** L'inférence n'est pas un obstacle : 19,8 ms pour encoder une question. Le point dur est le premier téléchargement de 135,6 Mio, soit environ 114 secondes sur une connexion à 10 Mbit/s. Les visites suivantes sont gratuites, le modèle étant mis en cache.

**Réduction prévue.** Le calcul montre que 81,8 pour cent du poids du modèle est la matrice d'embedding, qui couvre 250 037 tokens répartis sur une centaine de langues. Notre corpus est fermé et francophone. En réduisant le vocabulaire aux tokens réellement présents dans le corpus et les requêtes, le modèle passe à environ 33 Mio pour 32 000 tokens conservés, et à environ 27 Mio pour 16 000. Le modèle entre alors dans le dépôt, la dépendance au CDN disparaît, et la première visite tombe à environ 40 Mio.

Ce calcul a été recoupé avec la mesure : la taille prédite pour le modèle complet est de 112,0 Mio, contre 112,83 Mio relevés sur le fichier, l'écart correspondant aux biais conservés en flottant.

### 3.5 Protocole d'évaluation

Aucune génération n'étant produite, l'évaluation porte sur la récupération.

**Baselines, par ordre de difficulté croissante.** Tirage aléatoire, puis TF-IDF, puis BM25. BM25 est la référence lexicale standard et constitue la seule baseline réellement exigeante : battre TF-IDF ne prouve pas grand-chose. Cette exigence reprend la pratique du TP de journée 2, qui calcule systématiquement un modèle nul de référence.

**Métriques.** Recall@k et MRR, pour k valant 1, 3, 5 et 10.

**Jeu de référence à deux étages.** Le jeu `AgentPublic/piaf`, qui compte 3 835 questions-réponses françaises avec leurs contextes sous licence MIT, sert à valider la chaîne et à calibrer les attentes. Il est disponible à l'adresse `https://huggingface.co/datasets/AgentPublic/piaf`. Un jeu de référence construit par l'équipe sur notre propre corpus sert à l'évaluation qui compte.

**Dimensionnement.** Le calcul de puissance statistique impose une contrainte que nous prenons en compte dès maintenant. Sur une proportion observée de 0,80, l'intervalle de confiance à 95 pour cent vaut plus ou moins 10,1 points avec 60 questions, et plus ou moins 6,4 points avec 150. Autrement dit, 60 questions ne permettent pas de distinguer 0,80 de 0,85.

Nous adoptons donc une **évaluation appariée** : mêmes questions, deux systèmes comparés, test de McNemar. Avec un taux de désaccord de 0,20, détecter un écart de 10 points demande 155 questions, et un écart de 15 points en demande 68. L'appariement divise l'effectif requis par 3 à 5 par rapport à deux mesures indépendantes.

Conséquence sur la formulation des seuils : ils sont exprimés en **écarts appariés face à une baseline**, et non en niveaux absolus. Motif : aucun benchmark de recherche documentaire en français n'est publié pour cet encodeur. Sur les 838 résultats publiés du modèle, 23 portent sur de la récupération, tous en anglais. Un seuil absolu fixé a priori serait arbitraire.

Enfin, le jeu de référence étant rédigé par plusieurs personnes, un accord entre annotateurs sera mesuré sur un échantillon.

---

## 4. Étude du volet B

### 4.1 Cas d'usage retenu

Nous retenons le cas **B1, assistant réglementaire sourcé**. Le système répond à des questions portant sur le même corpus que le volet A, en citant systématiquement les passages sources, et produit une réponse d'abstention lorsque le corpus ne contient pas l'information demandée.

### 4.2 Modèle open-weights identifié

Le modèle retenu est **`Qwen2.5-7B-Instruct`**, quantifié en Q4_K_M.

| Modèle | Licence | Accès | Q4_K_M | Cache KV par token |
|---|---|---|---:|---:|
| `Qwen2.5-7B-Instruct` | Apache 2.0 | libre | 4,36 Gio | 56,0 Kio |
| `Mistral-7B-Instruct-v0.3` | Apache 2.0 | libre | 4,07 Gio | 128,0 Kio |
| `Qwen3-8B` | Apache 2.0 | libre | 4,68 Gio | 144,0 Kio |
| `Ministral-8B-Instruct-2410` | licence de recherche | libre | 4,57 Gio | 144,0 Kio |
| `Qwen2.5-14B-Instruct` | Apache 2.0 | libre | 8,37 Gio | 192,0 Kio |
| `Llama-3.1-8B-Instruct` | licence Llama 3.1 | approbation manuelle | 4,58 Gio | non retenu |

Trois raisons à ce choix, par ordre d'importance.

Le cache KV de ce modèle est 2,3 à 3,4 fois plus petit que celui de tous les autres candidats, grâce à 4 têtes clé-valeur seulement réparties sur 28 couches. Pour une architecture RAG qui injecte des passages cités dans le contexte, la longueur de contexte est la ressource critique, et c'est précisément là que ce modèle est avantagé.

La licence Apache 2.0 n'impose aucune restriction d'usage.

`Llama-3.1-8B-Instruct` est soumis à une approbation manuelle de délai inconnu. À douze jours du jalon de mi-parcours, ce risque de calendrier n'est pas justifié. `Ministral-8B` est écarté pour sa licence de recherche.

**Second modèle retenu pour comparaison : `Mistral-7B-Instruct-v0.3`.** Le choix est délibéré et repose sur trois arguments.

Il s'agit d'un modèle conçu par un éditeur français, sur un corpus normatif francophone. Le rapport final devra traiter la dépendance à un fournisseur : comparer un modèle chinois et un modèle français sur la même tâche donne à cette question une réponse mesurée plutôt qu'une opinion.

Il appartient à la même classe de taille que le modèle principal, 7 milliards de paramètres, et sera quantifié de la même façon. La comparaison ne fait donc varier que le modèle, ce qui est la condition pour qu'elle mesure quelque chose.

Il tient dans le budget mémoire à toutes les longueurs de contexte, y compris 32 768 tokens, ce que `Mistral-Nemo-Instruct-2407` ne permet pas malgré un meilleur français attendu : ses 6,96 Gio de poids et ses 160 Kio de cache par token portent le total à 12,6 Gio à 32 768 tokens, au-delà de la mémoire disponible.

**Ce que la comparaison mettra en évidence.** Le cache KV de Mistral est 2,3 fois plus gros que celui du modèle principal. À 32 768 tokens de contexte, cela représente 4,00 Gio contre 1,75. Autrement dit, un modèle aux poids plus légers coûte plus cher dès que le contexte s'allonge, ce qui est exactement le régime d'un RAG avec citations. Ce point sera mesuré, pas supposé.

`Qwen3-8B` est conservé en réserve si l'un des deux modèles se révèle insuffisant.

Les valeurs de cache KV sont calculées comme deux fois le nombre de couches, multiplié par le nombre de têtes clé-valeur, par la dimension de tête, par deux octets, à partir des fichiers de configuration officiels de chaque modèle.

### 4.3 Machine cible

La machine cible est la **machine 1**. Son relevé complet :

| Caractéristique | Valeur |
|---|---|
| Modèle | MacBook Pro, identifiant `Mac16,8` |
| Puce | Apple M4 Pro |
| Processeur | 12 cœurs, 8 performance et 4 efficience |
| Graphique | 16 cœurs, Metal 4 |
| Mémoire unifiée installée | 24,0 Gio |
| Mémoire réellement disponible | 10,3 Gio, en session de travail normale |
| Disque libre | 21 Gio sur 460, soit 96 pour cent occupé |

La distinction entre mémoire installée et mémoire disponible est importante. C'est le second chiffre qui contraint le choix du modèle, et c'est celui retenu pour le budget de la section suivante.

Une **machine 2** est conservée comme solution de repli. Elle dispose de 32 Go de mémoire d'après déclaration, le relevé restant à effectuer. En cas de bascule, deux éléments devront être relevés en plus de la capacité mémoire : la variante exacte de la puce et le nombre de cœurs graphiques. En génération, un modèle de langage est limité par la bande passante mémoire et non par la capacité installée. Une machine disposant de plus de mémoire peut faire tourner un modèle plus grand tout en étant plus lente.

Critère de bascule retenu : nous basculons si un modèle plus grand devient nécessaire et si la vitesse mesurée sur la machine 2 reste acceptable au regard du confort de démonstration.

### 4.4 Contrainte mémoire estimée

Empreinte de `Qwen2.5-7B-Instruct` en Q4_K_M, selon la longueur de contexte, encodeur de récupération et index inclus.

| Contexte | Poids | Cache KV | Encodeur et index | Exécution | Total | Marge sur 10,3 Gio |
|---:|---:|---:|---:|---:|---:|---:|
| 4 096 | 4,36 | 0,22 | 0,15 | 0,50 | 5,23 Gio | 5,07 Gio |
| 8 192 | 4,36 | 0,44 | 0,15 | 0,50 | 5,45 Gio | 4,85 Gio |
| 16 384 | 4,36 | 0,88 | 0,15 | 0,50 | 5,89 Gio | 4,41 Gio |
| 32 768 | 4,36 | 1,75 | 0,15 | 0,50 | 6,76 Gio | 3,54 Gio |

Le modèle passe confortablement, y compris à 32 768 tokens de contexte.

Même calcul pour le second modèle, `Mistral-7B-Instruct-v0.3`, dont le cache KV est 2,3 fois plus lourd.

| Contexte | Poids | Cache KV | Encodeur et index | Exécution | Total | Marge sur 10,3 Gio |
|---:|---:|---:|---:|---:|---:|---:|
| 4 096 | 4,07 | 0,50 | 0,15 | 0,50 | 5,22 Gio | 5,08 Gio |
| 8 192 | 4,07 | 1,00 | 0,15 | 0,50 | 5,72 Gio | 4,58 Gio |
| 16 384 | 4,07 | 2,00 | 0,15 | 0,50 | 6,72 Gio | 3,58 Gio |
| 32 768 | 4,07 | 4,00 | 0,15 | 0,50 | 8,72 Gio | 1,58 Gio |

Les deux modèles tiennent donc à toutes les longueurs de contexte prévues, mais l'écart se creuse à mesure que le contexte s'allonge : 1,58 Gio de marge pour Mistral contre 3,54 pour Qwen à 32 768 tokens. C'est le résultat que la comparaison doit rendre visible.

Deux écarts sont à signaler. `Qwen2.5-14B-Instruct` demanderait 10,5 Gio à 8 192 tokens, donc au-delà de la mémoire disponible sans fermer les applications. `Mistral-Nemo-Instruct-2407`, dont le français est attendu meilleur, atteint 12,6 Gio à 32 768 tokens et sort du budget. Tous deux restent des options à tester si la qualité des modèles retenus s'avère insuffisante, mais aucun ne peut être un choix par défaut.

Côté disque, les deux modèles retenus occupent ensemble 8,43 Gio, ce qui confirme la nécessité de libérer de l'espace avant de les télécharger.

La contrainte réellement bloquante est le disque et non la mémoire. Vingt et un Gio libres doivent accueillir le modèle retenu à 4,36 Gio, le modèle de comparaison à 4,68 Gio, le corpus et les index. Libérer 40 Gio est inscrit comme première tâche du volet B.

### 4.5 Protocole d'évaluation

Le sujet prescrit la mesure du taux d'abstention correcte sur un jeu de questions comportant une proportion de questions hors corpus. Nous retenons la répartition suivante.

| Catégorie | Proportion | Ce qu'elle mesure |
|---|---:|---|
| Questions couvertes par le corpus | 60 pour cent | exactitude de la réponse et validité des citations |
| Questions hors corpus, plausibles | 30 pour cent | taux d'abstention correcte |
| Questions ambiguës ou partiellement couvertes | 10 pour cent | comportement en zone grise |

Quatre métriques, toutes calculables automatiquement une fois le jeu annoté : taux d'abstention correcte sur les questions hors corpus, taux d'abstention à tort sur les questions couvertes, taux de citations valides, taux de réponse affirmative sur question hors corpus.

Deux baselines dégénérées encadrent la mesure : un système qui répond toujours, et un système qui s'abstient toujours. Elles jouent le rôle du modèle nul.

Les mesures sont produites avant et après adaptation, sur au moins trois états comparés : modèle nu sans récupération, récupération sans consigne d'abstention, récupération avec consigne et seuil de similarité calibré.

**Question adressée à l'enseignant.** Le sujet demande un modèle adapté par nos soins et note l'adaptation ainsi que les mesures avant et après. Il ne précise pas si une architecture RAG réglée accompagnée d'une consigne système constitue une adaptation au sens du barème, ou si un ajustement fin de type LoRA est attendu. L'écart de charge entre les deux lectures est d'un facteur 3 à 5. Cette question a été posée par courriel.

---

## 5. Éléments de cadrage

### 5.1 Périmètre

| Livré | Explicitement hors périmètre |
|---|---|
| Site public statique, recherche sémantique sur corpus fermé | Aucune génération de texte dans le volet A |
| Affichage du périmètre du corpus interrogeable | Aucun dépôt de document par le visiteur |
| Résultats classés avec score, référence de section et lien source | Français uniquement, pas de multilingue |
| Index précalculé hors ligne, livré en fichier statique | Pas d'authentification ni de compte utilisateur |
| Comparaison mesurée entre encodeur neuronal, TF-IDF et BM25 | Pas de persistance ni de journalisation des requêtes |
| Assistant local sourcé avec abstention, sur le même corpus | Pas de traitement de documents scannés ni de reconnaissance optique |
| Mesures avant et après adaptation, feuille de route des développements restants | Pas de mise à jour automatique du corpus |

### 5.2 Hypothèses

Ce que nous tenons pour acquis et qui pourrait se révéler faux. Chaque hypothèse porte la conduite à tenir si elle tombe.

| Hypothèse | Statut | Si elle est fausse |
|---|---|---|
| La réduction du vocabulaire fait passer le modèle sous 100 Mio sans perte notable de qualité | calculée, non mesurée | le modèle est servi depuis le CDN Hugging Face, avec une copie locale pour la démonstration |
| Le corpus retenu permet de construire un jeu de questions non trivial, dont 30 pour cent hors corpus | non vérifiée | changement de corpus, la décision reste ouverte une semaine |
| Le modèle du volet B produit des citations fiables en français | non mesurée | essai de Qwen3-8B, puis de Qwen2.5-14B si la mémoire le permet |
| Une architecture RAG réglée constitue une adaptation au sens du barème | question posée par courriel | facteur 3 à 5 sur la charge du volet B |
| La machine 2 peut réellement servir de repli | 32 Go déclarés, relevé non effectué | la démonstration repose entièrement sur la machine 1 |
| Les cinq membres restent disponibles jusqu'au 7 décembre | acquise à ce jour | domaine principal et secondaire pour chacun, voir section 5.5 |

**Deux hypothèses ont déjà été levées par la mesure**, ce qui montre que le cadrage a produit un effet avant même le premier jalon. La faisabilité de l'exécution navigateur, vérifiée le 19 septembre à 19,8 ms par requête. L'accessibilité du corpus, résolue par le choix d'un jeu de données public dont la volumétrie et la licence sont relevées.

### 5.3 Risques identifiés

| Identifiant | Risque | Probabilité | Impact | Parade |
|---|---|---|---|---|
| R1 | Disque saturé, 21 Gio libres pour un modèle de 4,36 Gio | élevée | bloque le volet B | libérer 40 Gio avant le 25 septembre |
| R2 | Première visite à 135,6 Mio, soit 114 s à 10 Mbit/s | certaine sans action | qualité du volet A | réduction du vocabulaire, cible de 50 Mio |
| R3 | Notions non enseignées, la journée 3 arrive après le jalon du 1er octobre | certaine | retard sur les deux volets | auto formation planifiée avec responsable et date |
| R4 | Périmètre de l'adaptation du volet B non défini par le sujet | élevée | 20 points | question posée par courriel |
| R5 | Corpus insuffisant ou inadapté | moyenne | bloque les deux volets | corpus public retenu et vérifié, repli documenté |
| R6 | Réduction du vocabulaire dégradant la qualité sans le signaler | moyenne | qualité du volet A | mesure du taux de tokens inconnus et scores avant et après |
| R7 | Jeu de référence rédigé par ceux qui construisent l'index | élevée | crédibilité des résultats | questions rédigées par des membres non impliqués dans l'index |
| R8 | Indisponibilité d'un membre | moyenne | jalon manqué | domaine principal et secondaire pour chacun |
| R9 | Déploiement tardif, un déploiement le jour même étant considéré comme non livré | moyenne | 15 points | page en ligne dès cette semaine, URL vérifiée 48 h avant la soutenance |
| R10 | Board renseigné après coup | moyenne | points de jalons | aucun commit sans ticket créé avant, contrôle hebdomadaire |
| R11 | Échec de la démonstration le jour de la soutenance | moyenne | 15 points | captation vidéo de secours des deux démonstrations |

### 5.4 Critères de réussite

Les seuils sont formulés en deux étages, pour une raison que nous assumons et documentons.

**Plancher, opposable dès maintenant.** Trois conditions indépendantes de tout étalonnage.

| Critère | Seuil |
|---|---|
| L'encodeur neuronal ne fait pas moins bien que BM25 sur le même jeu de questions | comparaison appariée |
| Le taux d'abstention correcte dépasse celui d'un système qui répond toujours | comparaison appariée |
| Le site du volet A est en ligne et interrogeable | avant le 1er octobre |

**Cible, calibrée au jalon de mi-parcours**, après une première mesure sur vingt questions, et écrite dans le dépôt à cette date.

**Motif de ce choix.** Aucun résultat de recherche documentaire en français n'est publié pour l'encodeur retenu. Sur ses 838 mesures publiées, 23 portent sur de la récupération, toutes en anglais. Un seuil absolu fixé aujourd'hui serait arbitraire, et invérifiable au vu du dimensionnement ci-dessous.

**Baselines retenues, par difficulté croissante.** Tirage aléatoire, puis TF-IDF, puis BM25. BM25 est la référence lexicale standard et la seule réellement exigeante. Pour le volet B, deux baselines dégénérées encadrent la mesure : un système qui répond toujours, et un système qui s'abstient toujours. Cette exigence reprend la pratique du TP de journée 2, qui calcule systématiquement un modèle nul de référence.

**Jeu de référence à deux étages.** Le jeu public `AgentPublic/piaf`, 3 835 questions-réponses françaises sous licence MIT, sert à valider la chaîne et à calibrer les attentes. Un jeu construit par l'équipe sur notre propre corpus sert à l'évaluation qui compte. Un accord entre annotateurs est mesuré sur un échantillon, le jeu étant rédigé par plusieurs personnes.

**Dimensionnement.** Sur une proportion observée de 0,80, l'intervalle de confiance à 95 pour cent vaut plus ou moins 10,1 points avec 60 questions, et plus ou moins 6,4 points avec 150. Soixante questions ne permettent donc pas de distinguer 0,80 de 0,85. En comparaison appariée par test de McNemar, avec un taux de désaccord de 0,20, détecter un écart de 10 points demande 155 questions et un écart de 15 points en demande 68. L'appariement divise l'effectif requis par 3 à 5.

### 5.5 Répartition initiale des tâches

Cinq domaines, chacun couvert par au moins deux personnes, et chaque membre engagé sur deux domaines. Maïmouna et Vaneck travaillent en binôme permanent et portent ensemble deux domaines en principal, ce qui est une décision assumée de l'équipe. Les trois autres membres portent un domaine principal et un domaine secondaire, conformément à la forme recommandée par le sujet.

| Domaine | Principal | Secondaire | Soutien |
|---|---|---|---|
| D1, corpus et segmentation | Maïmouna, Vaneck | | Jibril |
| D2, encodeur et index | Remy | Mahé | |
| D3, front et déploiement du volet A | Maïmouna, Vaneck | | Remy, Mahé |
| D4, socle RAG et inférence locale | Jibril | Remy | |
| D5, adaptation et évaluation du volet B | Mahé | Jibril | |

La charge résultante est équilibrée, avec un rapport de 1,5 entre le membre le plus chargé et le moins chargé, rôles transverses inclus.

**Rôles transverses.**

| Rôle | Titulaire | Charge |
|---|---|---|
| Gestion du board | Jibril | environ 1 h par semaine |
| Journal d'usage de l'IA et classeur de suivi | Mahé | environ 30 min par semaine |
| Lead technique | Mahé | au fil de l'eau |
| Fiche des outils novateurs | Vaneck, Maïmouna | environ 30 min par semaine |
| Coordination du rapport final | attribution le 16 octobre | à partir du 16 octobre |
| Supports de soutenance | attribution début novembre | à partir de novembre |

Le rôle de lead technique consiste à trancher les désaccords techniques et à garantir la cohérence d'architecture entre les deux volets. Il n'emporte aucune autorité sur la répartition des tâches, qui reste collective, et chaque arbitrage rendu est écrit dans le dépôt.

**Rituels adoptés.**

- Un point hebdomadaire de 45 minutes, avec compte rendu écrit.
- Une mini démonstration obligatoire du travail de chacun à chaque point, avec explication du fonctionnement.
- Un document de documentation au format Markdown produit par domaine et maintenu dans le dépôt.

Ces trois règles répondent à une contrainte précise du sujet : le choix du répondant à chaque question de soutenance relève de l'enseignant, et une réponse insuffisante affecte l'évaluation de toute l'équipe. Aucun membre ne peut donc ignorer le domaine des autres.

### 5.6 Séquencement

Le sujet laisse la forme libre mais demande que la séquence soit pensée et exposable. Les jalons notés sont portés par les milestones du dépôt. Le tableau ci-dessous expose la séquence interne jusqu'au jalon de mi-parcours, qui tombe dans douze jours.

| Échéance | Action | Domaine |
|---|---|---|
| 23/09 | corpus téléchargé, volumétrie réelle confirmée par filtrage | D1 |
| 25/09 | 40 Gio libérés sur la machine de référence, risque R1 | D4 |
| 25/09 | page statique déployée à l'URL définitive, même vide, risque R9 | D3 |
| 27/09 | index précalculé sur un corpus réduit | D2 |
| 27/09 | première inférence locale aboutie | D4 |
| 29/09 | jeu de 60 questions rédigé, dont 30 pour cent hors corpus | D1 et D5 |
| 01/10 | jalon de mi-parcours, tag Git et branche d'observation figée | tous |
| 16/10 | jalon J3, rédaction du rapport final engagée | tous |

---

## Annexe. Méthode de mesure

| Élément mesuré | Moyen |
|---|---|
| Tailles des modèles ONNX et GGUF | API Hugging Face, tailles en octets |
| Configurations des modèles | fichiers `config.json` officiels |
| Licences et restrictions d'accès | API Hugging Face |
| Cache KV | calcul à partir des configurations, recoupé entre modèles |
| Part de la matrice d'embedding | calcul recoupé avec la taille de fichier mesurée |
| Faisabilité navigateur | page statique servie en local, Chromium piloté par Playwright, 20 passes après chauffe |
| Charge utile réseau | mesure par fichier, recoupée avec le journal réseau du navigateur |
| Matériel et mémoire disponible | `sysctl`, `vm_stat`, `system_profiler`, `df` |
| Volumétrie du corpus | API Hugging Face datasets |
| Dimensionnement du jeu de référence | calcul de puissance statistique, intervalle de Wald et test de McNemar |

Deux mesures erronées ont été produites puis corrigées au cours de ce travail, et sont signalées ici par souci de traçabilité. L'API annonçait un modèle à 0,5 Mio alors que ses poids, stockés dans des fichiers externes, représentent 294,6 Mio. Le navigateur rapportait 5,5 Mio transférés pour un modèle de 112,8 Mio, les ressources d'origine tierce ne déclarant pas leur taille sans en-tête dédié ; la charge utile réelle de 135,6 Mio a été obtenue en mesurant chaque fichier séparément.

Points non vérifiés à ce stade : le relevé matériel de la machine 2, le gain effectif de la réduction du vocabulaire, et la qualité des citations produites par le modèle retenu en français.
