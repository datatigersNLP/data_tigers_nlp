# Audit du sujet — Projet NLP à 2 parties

**Module** NLP 2 · M2 Data & IA · FGES — Université Catholique de Lille · enseignant ROSARI Adrian
**Source auditée** `nlp_2/projet_doc/Projet_NLP_2_parties.pdf` — 20 pages, 626 977 octets, 4 692 mots
**Date de l'audit** 18/09/2026
**Statut** phase de pré-étude. Aucune action sur le dépôt GitHub.

---

## 0 — Méthode et périmètre

Ce qui a été fait, et seulement cela :

| Vérification | Moyen | Résultat |
|---|---|---|
| Lecture intégrale du sujet | `pdftotext -layout`, 20 pages, relecture page à page | 4 692 mots, aucune page illisible |
| Cohérence des dates | calcul des jours de la semaine et des écarts en Python | §1.2 ci-dessous |
| Cohérence du barème | somme des points, recoupement avec le texte | §1.3 |
| Couverture des notions par les supports | comptage par expression régulière sur les supports du module — 14 fichiers, dont 3 quasi-doublons écartés, soit **11 fichiers et 245 851 caractères** | §2 |
| Taille réelle des modèles ONNX | API Hugging Face, `?blobs=true`, tailles en octets | §3.1 |
| Taille réelle des modèles GGUF | idem | §3.2 |
| Limites GitHub | documentation officielle `docs.github.com` | §3.3 |
| Matériel disponible | `sysctl`, `df` | §3.4 |

**Ce qui n'a pas été vérifié** : les quotas des hébergeurs cités par l'enseignant (Hugging Face Spaces, Vercel) — non testés en compte réel ; la disponibilité effective des sites d'emploi pour le cas A2 ; les performances d'inférence en navigateur, qui demandent un prototype.

**Trois compteurs faux ont été produits puis corrigés pendant cet audit** : une recherche en sous-chaîne comptait « rag » dans « paragraphe » et « ner » dans « entraîner », et une expression régulière avec `(^|[^A-Za-z0-9_])` renvoyait 0 sur macOS là où `grep -w` renvoyait 133. Tous les chiffres de ce document proviennent de la version Python vérifiée.

---

## 1 — Ce que le sujet impose

### 1.1 Structure ferme

Le projet est **un couple obligatoire**, pas un choix :

- **Volet A — application en ligne.** Site public accessible par URL. Inférence **dans le navigateur** (Transformers.js ou ONNX Runtime Web). L'hébergeur ne sert que des fichiers statiques. Coût nul : ni hébergement payant, ni tokens facturés, ni serveur d'inférence. Ne supporte pas la génération de texte longue. **Le modèle servi doit préférentiellement être celui que vous avez entraîné.**
- **Volet B — application locale.** Modèle open-weights (Llama, Mistral, Qwen) quantifié et **adapté par vos soins**, avec architecture RAG. Aucune contrainte d'hébergement. Attendus explicites : mesure des performances **avant et après adaptation** sur un jeu de test constitué par l'équipe, identification et caractérisation des défauts, feuille de route des développements restants.

Un cas d'usage pour A, **un autre** pour B. Les deux volets sont livrés en parallèle : c'est leur comparaison qui fonde le rapport.

### 1.2 Calendrier réel — calculé, pas recopié

| Échéance | Date | Jour | Dans | Contenu |
|---|---|---|---|---|
| **Mail de proposition** | **20/09/2026** | **dimanche** | **J+2** | outils + liens d'invitation, cas A et cas B |
| J2 | 21/09/2026 | lundi | J+3 | env. déclaré, board créé, étude des 2 volets, cadrage — **10 pts** |
| Mi-parcours | 01/10/2026 | jeudi | J+13 | volet A déployé (même minimal), 1re inférence locale, tag Git — **10 pts** |
| J3 | 16/10/2026 | vendredi | J+28 | volet A fonctionnel, adaptation engagée, supports préparés — **15 pts** |
| J4 — soutenance | 07/12/2026 | lundi | J+80 | **60 pts** |

Écarts : J2 → mi-parcours **10 jours**. Mi-parcours → J3 **15 jours**. J3 → J4 **52 jours (7,4 semaines)**.

**Lecture opérationnelle.** Le projet n'est pas long, il est **frontal** : 35 des 40 points hors soutenance se jouent dans les 28 premiers jours. Le calendrier est ensuite très creux (7,4 semaines sans jalon), ce qui est le profil classique du décrochage. L'effort doit être chargé sur septembre, pas sur novembre.

### 1.3 Barème — vérifié

| Jalon | Points | Contrôle |
|---|---:|---|
| J1 (acquis) | 5 | — |
| J2 | 10 | |
| Mi-parcours | 10 | |
| J3 | 15 | |
| J4 soutenance | 60 | |
| **Total** | **100** | ✅ somme exacte |

Le sujet affirme « Les 40 points attribués aux jalons » : 5 + 10 + 10 + 15 = **40** ✅.

Détail des 60 points de soutenance :

| Critère | Points | Ce que cela implique |
|---|---:|---|
| Volet A : application livrée et accessible, **qualité du design et du parcours utilisateur** | 15 | le design pèse autant que le modèle |
| Volet B : **adaptation, mesures avant/après, feuille de route** | 20 | poste le plus lourd ; une adaptation non mesurée ne vaut rien |
| Rapport : analyse technique et retour d'expérience | 10 | |
| Présentation et démonstration | 15 | |
| **Total** | **60** | ✅ somme exacte |

Bonus : jusqu'à **+3** pour cinq outils novateurs documentés. La grille de lecture est donnée en clair page 20 : *« 3 points pour cinq descriptions instructives dont au moins une critique argumentée ; 1 à 2 pour des descriptions honnêtes mais superficielles ; 0 pour une liste recopiée. »*

**« Un jalon manqué n'est pas rattrapable. »**

---

## 2 — Ce que les supports couvrent, et ce qu'ils ne couvrent pas

Comptage sur les supports du module — 6 notebooks, 3 fiches, 5 PDF, soit 14 fichiers. Trois d'entre eux sont des quasi-doublons (la copie étudiante du TP2, le PDF du même TP, la version partielle du notebook J2 matin) et ont été **écartés** : le corpus de référence est donc de **11 fichiers et 245 851 caractères**. Expressions régulières avec frontières de mots.

Le dédoublonnage ne change aucun des zéros du §2.2 — la conclusion centrale est insensible à ce choix.

### 2.1 Acquis, réutilisable immédiatement

| Notion | Occurrences | Où | Réutilisable pour |
|---|---:|---|---|
| RNN / LSTM / BiLSTM | 112 / 105 / 36 | TP J2 matin + après-midi, TP2 IMDB, fiche 03 | A1, A2, A4 |
| Padding et masquage | 55 / 8 | TP J2, fiche 03 | tout le volet A |
| Keras / PyTorch | 57 / 33 | TP J2 parties 1-2 | tout le volet A |
| Word2Vec / embeddings | 43 / 33 | TP1, fiche 02 | A3, A5 |
| Cosinus | 44 | rappels M1, fiche 01 | A3, A5, B1 |
| BPE / tokenisation | 37 | TP1, fiche 02 | tout |
| TF-IDF | 26 | rappels M1 | A3 (référence à battre) |
| NER, format BIO/IOB | 14 / 6 | TP J2 après-midi (WikiNER) | A2, A5 |
| F1, déséquilibre des classes | 25 / 8 | rappels M1, TP J2 | A1, A4 |
| CRF, Viterbi | 23 / 6 | **deck de rappels M1** | A2 |
| seq2seq, encodeur-décodeur | 4 | fin du cours J2 | — |

### 2.2 Jamais abordé — mesuré à zéro occurrence

| Notion exigée par le sujet | Occurrences dans les supports |
|---|---:|
| **RAG** | **0** |
| **ONNX** | **0** |
| **Transformers.js** | **0** |
| **Quantisation** | **0** |
| **LoRA / adaptation de modèle** | **0** |
| CamemBERT | 0 |
| Gradio, Streamlit | 0 |
| macro-F1 | 0 |
| fine-tuning | 1 (mention isolée) |

**C'est le résultat central de cet audit.** Le volet B repose intégralement sur des notions absentes des supports disponibles au 18/09. Le volet A repose sur une notion acquise (BiLSTM) *plus* deux notions absentes (export ONNX, exécution navigateur).

Le cours à venir ne comble ce trou qu'en partie et **trop tard** : la journée 3 (16/10) porte sur BERT et l'attention, les blocs « évaluer un LLM » et « choisir son modèle » sont annoncés pour J3 ou J4. Or le jalon mi-parcours du **01/10** exige déjà « première inférence locale aboutie ».

> **Conséquence de pilotage.** L'équipe doit s'auto-former sur RAG, ONNX et l'inférence locale **avant** le cours correspondant. Ce n'est pas un défaut du sujet : c'est précisément ce que la section « Montée en compétence et bonus » valorise à +3 points. Il faut donc traiter cette auto-formation comme une tâche planifiée du projet, pas comme un aléa.

### 2.3 Correction d'une affirmation du sujet

> Sujet, cas A2 : « L'architecture BiLSTM-CRF **étudiée en journée 2** est directement applicable. »

**Mesuré.** Le CRF est traité dans le *deck de rappels M1* — théorie HMM/Viterbi, CRF linéaire, matrice de transitions, features (majuscule initiale, suffixes, mot précédent/suivant), présenté comme « la référence à battre de la journée 2 ». Dans le notebook du TP de journée 2, `CRF` apparaît **une seule fois**, dans une cellule intitulée *« Prolongements, si vous finissez en avance »* : « Ajoutez une couche CRF au-dessus du BiLSTM pour interdire les séquences invalides du type `O → I-PER` ».

**Ce qui a réellement été implémenté** : un LSTM puis un BiLSTM d'étiquetage sur WikiNER, format BIO, 4 types (PER, LOC, ORG, MISC), avec conversion IOB1→IOB2 et évaluation **F1 par entité** (fonction `f1_entite` fournie et testée dans le notebook).

**Ce que cela change** : le BiLSTM d'étiquetage est un acquis réel et immédiatement réutilisable — la boucle, le masquage `ignore_index=-100`, l'évaluation par entité, le modèle nul de référence. La couche CRF, elle, **reste entièrement à écrire**. Ce n'est pas un obstacle, c'est une charge à inscrire au backlog et non à supposer acquise.

---

## 3 — Contraintes techniques mesurées

### 3.1 Volet A — la taille des modèles est le point dur

> Sujet : « Un modèle de type DistilCamemBERT quantifié représente environ 60 Mo. »

Calcul à partir du `config.json` officiel de `cmarkea/distilcamembert-base` (vocab 32 005, hidden 768, 6 couches, intermédiaire 3 072) : **≈ 67,5 M paramètres**, dont 25,0 M d'embeddings (37 %). En int8 : **≈ 64 MiB**. **L'ordre de grandeur du sujet est juste.**

**Mais aucun export ONNX public n'existe pour ce modèle** : le dépôt `cmarkea/distilcamembert-base` ne contient que `model.safetensors` et `pytorch_model.bin`. Ce chiffre de 60 Mo suppose donc un export et une quantisation **faits par l'équipe** (via `optimum`).

Tailles réelles des modèles français prêts à l'emploi, mesurées en octets sur le Hub :

| Modèle | Fichier | Octets | MiB | Push GitHub |
|---|---|---:|---:|---|
| `Xenova/camembert-ner` | `model_quantized.onnx` | 111 284 131 | 106,1 | ❌ **bloqué** |
| `Xenova/camembert-base` | `model_quantized.onnx` | 112 015 087 | 106,8 | ❌ **bloqué** |
| `onnx-community/camembertv2-base-ftb-ner` | `model_int8.onnx` | 112 225 728 | 107,0 | ❌ **bloqué** |
| `onnx-community/camembertv2-base-ftb-ner` | `model_q4f16.onnx` | 100 270 883 | 95,6 | ⚠️ avertissement |
| `Xenova/multilingual-e5-small` | `model_quantized.onnx` | 118 308 185 | 112,8 | ❌ **bloqué** |
| `Xenova/paraphrase-multilingual-MiniLM-L12-v2` | `model_quantized.onnx` | 118 308 126 | 112,8 | ❌ **bloqué** |

### 3.2 Volet B — le matériel passe, le disque non

Tailles GGUF mesurées (quantisation Q4_K_M, le standard) :

| Modèle | Q4_K_M | Q5_K_M | Q8_0 |
|---|---:|---:|---:|
| Mistral-7B-Instruct-v0.3 | **4,07 Gio** | 4,78 | 7,17 |
| Qwen2.5-7B-Instruct | **4,36 Gio** | 5,07 | 7,54 |
| Meta-Llama-3.1-8B-Instruct | **4,58 Gio** | 5,34 | 7,95 |
| Qwen2.5-3B-Instruct | **1,80 Gio** | 2,07 | 3,06 |

### 3.3 Limites GitHub — documentation officielle, vérifiée le 18/09/2026

| Règle | Valeur | Source |
|---|---|---|
| Fichier > 50 MiB | avertissement Git | `docs.github.com` |
| Fichier > 100 MiB | **push bloqué** | `docs.github.com` |
| Ajout par le navigateur | 25 MiB max | `docs.github.com` |
| Taille de dépôt | < 1 Go recommandé, < 5 Go fortement recommandé | `docs.github.com` |
| **GitHub Pages en plan Free** | **dépôts publics uniquement** | `docs.github.com` |
| Site Pages publié | 1 Go max | `docs.github.com` |
| Bande passante Pages | 100 Go/mois (limite souple) | `docs.github.com` |
| Builds Pages | 10/heure (limite souple) | `docs.github.com` |

Recoupe une mesure faite le 11/09/2026 sur le dépôt de l'équipe (org `datatigersNLP`, plan Free, dépôt **privé**) : Pages indisponible, protection de branche indisponible (403 « Upgrade to GitHub Pro or make this repository public »).

**Conséquences d'architecture — non négociables :**

1. Aucun modèle ONNX prêt à l'emploi ne peut être versionné dans le dépôt. Trois issues seulement :
   - **charger le modèle depuis le CDN Hugging Face à l'exécution** — c'est le comportement par défaut de Transformers.js, c'est gratuit, et cela sort le poids du dépôt comme de la bande passante Pages ; en contrepartie on introduit une dépendance externe au moment de la démonstration ;
   - **exporter son propre modèle** (BiLSTM entraîné en TP → ONNX, quelques Mo) : passe sans Git LFS, sans dépendance externe, et c'est exactement ce que le sujet appelle « Valorisation » ;
   - Git LFS : 1 Go de stockage et 1 Go de bande passante par mois en gratuit — insuffisant dès quelques dizaines de visites sur un fichier de 106 MiB. **À écarter.**
2. **Le dépôt du volet A devra être public** pour utiliser GitHub Pages en plan Free. Le sujet demande d'ailleurs « Dépôts Git des deux volets » — au pluriel. Le volet B peut rester privé.
3. Prévoir **une copie locale du modèle** pour la démonstration de soutenance, le CDN étant un point de défaillance unique le jour J.

### 3.4 Machine de développement mesurée

| Élément | Valeur | Lecture |
|---|---|---|
| Processeur | Apple M4 Pro, 12 cœurs | confortable |
| Mémoire unifiée | **24 Go** | un 7-8B Q4_K_M (≈ 4,5 Go) passe largement ; un 14B Q4 aussi |
| **Disque libre** | **21 Gio sur 460 (96 % occupé)** | ⚠️ **risque** |
| Node / npm | v25.9.0 / 11.12.1 | Transformers.js opérationnel |
| Docker, git, gh | présents (gh 2.92.0) | |
| Ollama, llama.cpp, LM Studio, MLX | **absents** | tout reste à installer |

**21 Gio libres** suffisent à un modèle quantifié et à un index, mais pas à une campagne d'essais : deux ou trois modèles 7-8B, leurs variantes de quantisation et les artefacts d'une adaptation QLoRA dépassent cette marge. À traiter comme le risque matériel n° 1 — libérer de l'espace ou désigner une machine d'équipe mieux dotée.

Environnement Python existant (`nlp_2/.venv`, Python 3.12.11, arm64) : torch 2.14.0, keras 3.15.1, transformers 5.17.0, numpy 1.26.4, gensim 4.3.3, scikit-learn 1.9.0. **Ni `onnx`, ni `optimum`, ni `sentence-transformers`, ni `faiss`.** Deux contraintes à ne pas casser : Keras est installé sans TensorFlow (`KERAS_BACKEND=torch` obligatoire avant l'import) et gensim 4.3.3 exige `numpy<2` / `scipy<1.14`.

Côté navigateur, le paquet est **`@huggingface/transformers` v4.3.0, publié le 16/09/2026** (dépendances : `onnxruntime-web`, `onnxruntime-node`, `@huggingface/jinja`, `@huggingface/tokenizers`). L'ancien nom `@xenova/transformers` est figé en v2.17.2 depuis mai 2024 : **la majorité des tutoriels en ligne visent le paquet périmé.**

---

## 4 — Anomalies et points de vigilance du sujet

Classés par criticité. Le sujet contient des coquilles ; la colonne « lecture retenue » indique la lecture prudente à appliquer.

### Bloquants — à lever avant le 20/09

| # | Constat | Lecture retenue |
|---|---|---|
| 1 | **Deux échéances contradictoires pour le mail de choix.** §2 : « avant **dimanche 20 septembre** ». §5 (J2) : « Le choix du sujet se confirme par courriel **avant mercredi prochain** ». Note enseignant p. 20 : « confirmation avant mercredi prochain ». | **Viser le dimanche 20/09.** C'est la date la plus contraignante et la seule explicite. Le coût d'être en avance est nul, celui d'être en retard est que « le projet et les use cases seront imposés ». |
| 2 | **Périmètre de l'« adaptation » du volet B non défini.** Le sujet dit « modèle open-weights **adapté par vos soins** » et note 20 points sur « adaptation, mesures avant/après ». Il ne dit jamais si un RAG bien réglé plus un prompt système constituent une adaptation, ou si un fine-tuning/LoRA est exigé. | **Question à poser dans le mail du 20/09.** L'écart de charge entre les deux lectures est d'un facteur 3 à 5. L'enseignant s'engage à répondre sous 24 h : c'est le bon moment. |
| 3 | « Échéance : **deux semaines** » sous un jalon J2 daté du 21/09, alors que le sujet est transmis mi-septembre. | Incohérent avec « avant mercredi prochain ». La date chiffrée du jalon (21/09) fait foi. |

### Importants

| # | Constat | Lecture retenue |
|---|---|---|
| 4 | **« Les quatre cas proposés sont fermés »** (note enseignant, p. 20) alors que **cinq** cas A1–A5 sont listés. | A5 a vraisemblablement été ajouté après la note. Les cinq cas sont valides ; le mot « fermés » signifie que le périmètre de chaque cas n'est pas négociable. |
| 5 | **« Mi-parcours — mi-octobre »** mais daté **01/10/2026**, alors que J3 (16/10) est, lui, à la mi-octobre. | **La date chiffrée fait foi : 01/10/2026.** Se caler sur le libellé ferait perdre 10 points. |
| 6 | **Numérotation des sections** : 1, 2, 3, 4, 5, 6, 7 puis **11, 12**. Les sections 8, 9 et 10 n'existent pas. | Coquille de numérotation. Le sommaire et le corps concordent, aucun contenu ne manque. |
| 7 | **A2, mode URL.** Le sujet demande que l'application « récupère et nettoie le contenu de la page » depuis une URL LinkedIn ou Indeed. En architecture 100 % statique sans serveur, une requête vers un domaine tiers est **bloquée par CORS**, indépendamment de l'anti-bot. | Le sujet prévoit lui-même le repli copier-coller. Acter que **le mode URL sera au mieux partiel** (sites permissifs uniquement, ou proxy CORS tiers assumé et documenté) et en faire un arbitrage écrit — ce que le sujet valorise explicitement. |
| 8 | **« DistilCamemBERT quantifié ≈ 60 Mo »** : ordre de grandeur juste (64 MiB en int8), mais **aucun export ONNX public n'existe**. Les modèles français prêts à l'emploi pèsent 106 à 107 MiB. | Soit export maison via `optimum` (charge réelle, 1 à 2 jours), soit acceptation des 106 MiB servis par le CDN Hugging Face. |
| 9 | **« BiLSTM-CRF étudiée en journée 2 »** — voir §2.3. Le BiLSTM a été implémenté, le CRF est resté en théorie et en prolongement facultatif. | Le CRF est une charge à inscrire au backlog, pas un acquis. |

### À ne pas oublier

| # | Constat |
|---|---|
| 10 | **Deux supports distincts** sont exigés à J4 : un « support de **pitch** » *et* un « support de **présentation** ». Ils sont souvent confondus. Tous deux transmis par courriel. |
| 11 | Le **classeur de suivi et le journal d'usage de l'IA** sont des livrables à part entière, « partagés », « disponibles **dès maintenant** » — distincts du board de tickets. |
| 12 | « Le site du volet A doit être déployé et fonctionnel **avant** la date de soutenance. Un déploiement effectué le jour même sera considéré comme **non livré**, y compris s'il fonctionne. » |
| 13 | Le rapport doit être livré en **.pdf**, en V1 **strictement avant J4**, et son écriture **commencée au plus tard à J3** (16/10). |
| 14 | « Le choix du répondant à chaque question relève de l'enseignant » : **n'importe qui peut être interrogé sur n'importe quelle portion du code.** Une réponse insuffisante affecte l'équipe entière. |
| 15 | Une **captation vidéo de secours des deux démonstrations** est « fortement conseillée » ; son absence « peut entraîner la perte des points ». |
| 16 | Un **TP noté** est distribué aux équipes en attente ou déjà passées le jour de la soutenance, à rendre en fin de journée. La journée du 07/12 est donc chargée au-delà du passage. |
| 17 | La partie « Axes de progression » du rapport **peut et devrait être rédigée individuellement** (« Cette modalité est même recommandée »). |
| 18 | Durée de soutenance : le tableau donne 4 + 4 + 8 = **16 min** plus 5 à 10 de questions, soit 21 à 26 min ; la note enseignant annonce « 15 min de passage », soit 20 à 25. Écart d'une minute, sans conséquence — mais **préparer 16 minutes chrono, pas 20**. |
| 19 | Note enseignant : Hugging Face Spaces Gradio et Docker « requièrent un plan payant » ; Vercel Hobby « 4 h de CPU actif par mois, usage personnel non commercial ». **Ces limites concernent des serveurs d'exécution et sont hors sujet pour le volet A**, qui ne sert que des fichiers statiques. GitHub Pages, Cloudflare Pages et Netlify servent du statique gratuitement — à vérifier nous-mêmes au moment du choix, l'enseignant précisant lui-même « limites volatiles ». |
| 20 | Le bonus +3 est **non barémé mais sa grille de lecture est donnée** : cinq descriptions instructives **dont au moins une critique argumentée**. Un outil abandonné et documenté comme tel vaut mieux qu'un cinquième outil encensé. |

---

## 5 — Ce que le sujet récompense réellement

Lecture croisée du barème, des attendus du rapport et des formulations insistantes :

1. **La régularité prime sur la performance finale.** 40 points sont acquis ou perdus avant le 16/10, sans rattrapage. Un projet médiocre livré à chaque jalon bat un projet brillant livré en décembre.
2. **La mesure prime sur le résultat.** « Mesure des performances avant et après adaptation », « taux d'abstention correcte », « proportion de sorties conformes », « taux d'échec d'extraction observé », « comparer les résultats obtenus à partir d'une capture et à partir du texte ». Le sujet ne demande jamais que ça marche bien : il demande **de quoi le prouver**.
3. **L'aveu documenté prime sur la façade.** « Un projet qui documente les arbitrages est supérieur à un projet qui prétend n'en avoir fait aucun. » « Un outil qui ne tient pas ses promesses constitue un résultat exploitable, à condition d'être documenté comme tel. » Et, page 20 : *« Croiser systématiquement leurs affirmations avec le dépôt et le board. »* — **le retour d'expérience sera confronté aux traces.**
4. **Le board renseigné après coup est détecté et sans valeur.** « Des tickets créés avant la réalisation, pas après. Un board renseigné rétrospectivement est identifiable et sans valeur pour le pilotage. »
5. **Le modèle maison vaut plus que le modèle emprunté**, sur le volet A : « démontre une maîtrise que le recours à un modèle préexistant ne démontre pas ».
6. **Le design compte pour un tiers du volet A** (15 points sur « application livrée et accessible, qualité du design et du parcours utilisateur »).

---

## 6 — Questions à adresser à l'enseignant

À intégrer au mail du 20/09, qui est aussi l'occasion de démontrer la rigueur du cadrage. Réponse annoncée sous 24 h.

1. **Périmètre de l'« adaptation » (volet B).** Un RAG réglé et un prompt système constituent-ils une adaptation au sens des 20 points, ou un fine-tuning / LoRA est-il attendu ? *(Anomalie n° 2 — c'est la question la plus structurante.)*
2. **Date du mail.** « Avant dimanche 20 septembre » (§2) ou « avant mercredi prochain » (§5) ? *Nous nous alignons sur le 20/09 par défaut.*
3. **Dépôt public.** GitHub Pages exige un dépôt public en plan Free. Confirmez-vous qu'un dépôt public pour le volet A ne pose pas de difficulté, le volet B restant privé ?
4. **Modèle servi en volet A.** Le chargement du modèle depuis le CDN Hugging Face à l'exécution est-il conforme à la contrainte « aucun coût, la plateforme d'hébergement ne sert que des fichiers statiques » ?
5. **Cas A5.** La note interne évoque « quatre cas fermés » alors que cinq sont proposés : A5 est-il bien ouvert au choix ?

---

## 7 — Conclusion de l'audit

Le sujet est **exigeant, cohérent dans ses attendus, et imprécis sur trois points matériels** : la date du mail, le périmètre de l'adaptation, et la disponibilité réelle d'un DistilCamemBERT ONNX. Aucune de ces imprécisions n'empêche de démarrer ; deux d'entre elles se lèvent par un courriel.

Le vrai risque n'est ni technique ni calendaire : c'est **l'écart entre ce que les supports ont enseigné et ce que le projet exige**. RAG, ONNX, exécution navigateur, quantisation et adaptation de modèle totalisent **zéro occurrence** dans les 245 851 caractères de cours et de TP. Cet écart est assumé par le sujet, qui le rémunère au titre de la montée en compétence — mais il doit être **planifié comme une tâche**, avec des responsables et des dates, et non subi.

La décision qui engage tout le reste est le **choix du couple (cas A, cas B)**, à arrêter avant dimanche. Elle fait l'objet du document `02_ETUDE_COMPARATIVE_CAS_USAGE.md`.
