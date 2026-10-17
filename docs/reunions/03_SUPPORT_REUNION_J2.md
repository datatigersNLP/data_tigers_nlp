# Réunion de cadrage — Projet NLP 2

**Objet** arrêter les décisions du jalon **J2 (10 points)** et rédiger le courriel de choix du sujet.
**À tenir avant le** **samedi 19/09/2026** — le courriel part **dimanche 20/09 au plus tard**.
**Durée** 2 h 35, chronométrée.
**Participants** les 5 membres. Aucune décision valable sans les 5.

> **Pourquoi c'est urgent.** Le sujet §2 : *« Par mail, avant dimanche 20 septembre, une première proposition doit être faite ; si cela n'est pas fait, le projet et les use cases seront imposés pour les groupes. »*
> Le §5 mentionne « avant mercredi prochain ». **En cas de doute, on retient la date la plus contraignante** : dimanche 20/09. Être en avance ne coûte rien ; l'enseignant s'engage à répondre sous 24 h, ce qui nous laisse encore le temps de corriger avant J2.

---

## 1 — Le cadre, en une page

### Ce qui est noté, et quand

| Date | Jalon | Points | Ce qui est contrôlé |
|---|---|---:|---|
| — | J1 | **5** | acquis (équipe constituée, dépôt créé) |
| **21/09** lundi | **J2** | **10** | environnement déclaré · board créé · étude des 2 volets · cadrage |
| **01/10** jeudi | Mi-parcours | **10** | volet A **déployé** même minimal · 1re inférence locale · tag Git · branche dédiée pour l'enseignant |
| **16/10** vendredi | J3 | **15** | volet A fonctionnel · adaptation engagée · supports préparés · **rédaction du rapport commencée** |
| **07/12** lundi | J4 | **60** | soutenance |
| | | **100** | + **3 points bonus** (cinq outils novateurs documentés) |

**« Un jalon manqué n'est pas rattrapable. Les points correspondants sont perdus et le projet se poursuit. »**

### Les trois chiffres qui doivent guider nos arbitrages

1. **35 des 40 points hors soutenance se jouent dans les 28 prochains jours.** Ensuite, 7,4 semaines sans aucun jalon. L'effort se charge maintenant, pas en novembre.
2. **Le volet B vaut 20 points, le volet A 15.** Sur le volet A, les 15 points portent sur « application livrée et accessible, **qualité du design et du parcours utilisateur** » — le design compte autant que le modèle.
3. **Le volet B est noté sur « adaptation, mesures avant/après, feuille de route ».** Une adaptation non mesurée ne rapporte rien.

### Ce que le sujet récompense, en clair

- **La régularité**, pas le sprint final. Les 40 points de jalons « évaluent la régularité de la conduite, qui ne peut être simulée par un effort de fin de période ».
- **La mesure**, pas la réussite. Le sujet ne demande jamais que ça marche bien : il demande de quoi le prouver.
- **L'aveu documenté.** *« Un projet qui documente les arbitrages est supérieur à un projet qui prétend n'en avoir fait aucun. »*
- **Le board tenu en temps réel.** *« Des tickets créés avant la réalisation, pas après. Un board renseigné rétrospectivement est identifiable et sans valeur pour le pilotage. »* Nos affirmations du rapport **seront croisées avec le dépôt et le board**.
- **Le modèle entraîné par nous** plutôt qu'emprunté, sur le volet A.

---

## 2 — Ce que nous avons vérifié avant cette réunion

Rien de ce qui suit n'est une impression : tout a été mesuré. Détail dans `01_AUDIT_SUJET_PROJET.md`.

### 2.1 L'écart entre le cours et le projet

Comptage sur les supports du module, quasi-doublons écartés — **11 fichiers, 245 851 caractères** :

| Acquis, réutilisable tout de suite | | Jamais abordé | |
|---|---:|---|---:|
| RNN / LSTM / BiLSTM | 112 / 105 / 36 | **RAG** | **0** |
| Padding et masquage | 55 | **ONNX** | **0** |
| Keras / PyTorch | 57 / 33 | **Transformers.js** | **0** |
| Word2Vec, embeddings | 43 / 33 | **Quantisation** | **0** |
| Cosinus, TF-IDF | 44 / 26 | **LoRA / adaptation** | **0** |
| NER, format BIO | 14 / 6 | CamemBERT | 0 |
| F1, déséquilibre | 25 / 8 | fine-tuning | 1 |

**Conséquence.** Tout le volet B et la moitié du volet A reposent sur des notions absentes des supports. La journée 3 (16/10) n'arrivera **qu'après** le jalon mi-parcours du 01/10, qui exige déjà une inférence locale.

**Ce n'est pas un problème, c'est le bonus.** La section « Montée en compétence » rémunère jusqu'à +3 points exactement cette auto-formation. Mais elle doit être **planifiée comme une tâche, avec un responsable et une date** — pas subie.

### 2.2 Ce que la journée 2 nous a réellement donné

Le sujet annonce « l'architecture BiLSTM-CRF étudiée en journée 2 ». Vérification faite dans le notebook : **le CRF n'a pas été implémenté**. Il apparaît une seule fois, dans la cellule « Prolongements, si vous finissez en avance ».

**Ce que nous avons vraiment** : un LSTM puis un BiLSTM d'étiquetage sur WikiNER, format BIO, conversion IOB1→IOB2, masquage `ignore_index=-100`, évaluation **F1 par entité** (fonction `f1_entite`, déjà écrite et testée) et un modèle nul de référence. Tout cela se récupère tel quel. **La couche CRF, elle, est à écrire** — environ 2 jours-homme.

### 2.3 Les contraintes matérielles, mesurées

| Constat | Mesure | Conséquence |
|---|---|---|
| Fichier > 100 MiB | **push GitHub bloqué** (doc officielle) | |
| Modèles ONNX français prêts à l'emploi | **106 à 113 MiB** | ❌ **impossible à versionner** |
| DistilCamemBERT « ≈ 60 Mo » du sujet | juste (64 MiB en int8) mais **aucun export ONNX public n'existe** | export à faire nous-mêmes |
| BiLSTM entraîné par nous, exporté ONNX | **quelques Mo** | ✅ tient dans le dépôt, sans LFS |
| GitHub Pages en plan Free | **dépôts publics uniquement** | le dépôt du volet A devra être **public** |
| Git LFS gratuit | 1 Go stockage / 1 Go de bande passante par mois | ❌ insuffisant, à écarter |
| Machine de dev | **M4 Pro, 24 Go RAM** | ✅ un 7-8B quantifié passe largement |
| Disque libre | **21 Gio sur 460 (96 % plein)** | ⚠️ **risque n° 1**, voir §6 |
| Modèles locaux | Mistral-7B **4,07 Gio** · Qwen2.5-7B **4,36** · Llama-3.1-8B **4,58** (Q4_K_M) | on n'en tient pas trois |

**Deux architectures possibles pour servir le modèle du volet A**, à trancher aujourd'hui :

| | Modèle entraîné par nous, exporté ONNX | Modèle du CDN Hugging Face |
|---|---|---|
| Poids | quelques Mo, dans le dépôt | 106–113 MiB, hors dépôt |
| « Valorisation » du sujet | ✅ satisfaite | ❌ non |
| Dépendance le jour de la démo | aucune | ⚠️ un service tiers |
| Qualité brute attendue | inférieure | supérieure |
| Charge | entraînement + export + tokenizer JS | quasi nulle |

> **Recommandation** : modèle maison, avec **une copie locale du modèle prévue pour la soutenance**. Le sujet le récompense, et cela supprime un point de défaillance unique le 07/12.

---

## 3 — DÉCISION N° 1 : le couple de cas d'usage

**C'est la seule décision qui structure tout le reste.** Analyse complète dans `02_ETUDE_COMPARATIVE_CAS_USAGE.md`. Voici la synthèse.

### 3.1 Volet A — les cinq cas

| | **A1** Routeur | **A2** Offres de stage | **A3** Recherche sém. | **A4** Retours étudiants | **A5** Cooptation |
|---|:---:|:---:|:---:|:---:|:---:|
| Tâche | classification | **NER** | retrieval | 2 classifications | NER + normalisation |
| Annotation *(coût)* | 3 | **5** | **1** | 3 | 4 |
| Modélisation *(difficulté)* | 2 | 4 | **1** | 3 | **5** |
| Intégration *(difficulté)* | 2 | 4 | 2 | 2 | **5** |
| Réemploi TP *(bénéfice)* | **5** | **5** | 3 | **5** | 3 |
| Modèle maison *(bénéfice)* | **5** | **5** | 2 | **5** | 3 |
| UX/design *(potentiel)* | 3 | **5** | 4 | **5** | **5** |
| **Charge (j·h)** | 14–18 | 20–26 | **12–16** | 15–19 | 24–32 |
| **Risque n° 1** | corpus artificiel | **CORS sur l'URL** | ambition faible | étiquettes subjectives | **5 briques à chaîner** |

> Échelles : *Annotation, Modélisation, Intégration* → 1 facile, 5 difficile. *Réemploi, Modèle maison, UX* → 1 faible, 5 fort.

### 3.2 Volet B — les cinq cas

| | **B1** Assistant régl. | **B2** Questions révision | **B3** Doc. sur dépôt | **B4** Profileur | **B5** Chaîne auto. |
|---|:---:|:---:|:---:|:---:|:---:|
| Technique centrale | RAG + abstention | fine-tuning de style | RAG sur code | **décodage contraint** | pipeline complet |
| Corpus disponible | ✅ | ✅ **déjà sur disque** | ❌ **n'existe pas** | ✅ | ⚠️ à réunir |
| Coût de la mesure | 3 | **5** | **5** | **1** | 3 |
| Objectivité de la métrique | 4 | 3 | **1** | **5** | 4 |
| Avant/après démontrable | 3 | **5** | 2 | **5** | 4 |
| **Charge (j·h)** | 18–24 | 18–24 | 16–22 | **15–20** | 25–32 |

> **B3 est à écarter** : le corpus, c'est notre dépôt — il contient aujourd'hui **un fichier de 16 octets et un commit**. Il n'y aura pas de matière avant la mi-octobre, alors que le 01/10 exige déjà une inférence locale aboutie.

### 3.3 Les couples

| Couple | Mutualisation | Comparaison finale | Charge | Risque dominant |
|---|---|---|:---:|---|
| **A2 + B4** *emploi* | **forte** — un corpus d'offres, un schéma, un jeu de test pour les deux volets | **maximale** — même tâche d'extraction : notre BiLSTM-CRF *contre* un LLM 7B en décodage contraint | 35–46 j·h | CORS ; annotation NER lourde |
| **A3 + B1** *corpus normatif* | **très forte** — A3 **est** la couche retrieval de B1 | bonne — restituer *contre* générer en citant ou s'abstenir | **30–40 j·h** | ambition A faible ; adaptation B jugée légère |
| **A5 + B5** *cooptation* | forte | **maximale** — recommandé nommément par le sujet | **49–64 j·h** | les deux charges maximales en même temps |
| A4 + B2 *pédagogique* | moyenne | moyenne | 33–43 j·h | 2 corpus à fabriquer, éval coûteuse |

### 3.4 Recommandation soumise au vote

| Scénario | Couple | Pour qui |
|---|---|---|
| **Recommandé** | **A2 + B4** | équipe de 5 disponible, meilleur rapport note/charge |
| **Sécurisé** | **A3 + B1** | disponibilité incertaine, priorité à la tenue des jalons |
| **Ambitieux** | **A5 + B5** | équipe complète et décidée à charger sept./oct. |

**Pourquoi A2 + B4 est recommandé.** On garde l'intégralité de ce que la journée 2 nous a appris (BiLSTM d'étiquetage, BIO, F1 par entité déjà codé). On sert un modèle maison de quelques mégaoctets — « Valorisation » satisfaite *et* limite des 100 MiB contournée. Et le volet B repose sur la technique dont **la mesure ne coûte rien** : le décodage contraint se valide contre un schéma JSON, automatiquement, et l'avant/après est spectaculaire. Surtout, **les deux volets traitent la même tâche d'extraction sur le même corpus et le même jeu de test** : les six axes que le rapport exige — coût, latence, qualité, contrôle, explicabilité, dépendance — se remplissent alors avec des chiffres des deux côtés.

**Son risque, connu et borné.** Le mode URL de A2 se heurte à CORS : le navigateur ne peut pas aller chercher une page LinkedIn sans serveur. Le sujet prescrit lui-même le repli copier-coller. On en fait une mesure — taux de récupération réussie par domaine — et cela devient un résultat de rapport au lieu d'un échec.

> ☐ **Décision actée :** volet A = ............ · volet B = ............

---

## 4 — Les six autres décisions à acter aujourd'hui

| # | Décision | Options | Acté |
|---|---|---|---|
| 2 | **Environnement de développement déclaré** *(noté à J2)* | convergence préférable ; une divergence déclarée n'est pas pénalisée. Proposition : Python 3.12 + venv, PyTorch, Node 20+, VS Code | ☐ |
| 3 | **Dépôt du volet A public** (obligatoire pour GitHub Pages en Free) ou autre hébergeur statique | GitHub Pages / Cloudflare Pages / Netlify | ☐ |
| 4 | **Modèle servi en volet A** | maison exporté ONNX *(recommandé)* / CDN Hugging Face | ☐ |
| 5 | **Modèle local volet B** | Mistral-7B 4,07 Gio / Qwen2.5-7B 4,36 / Llama-3.1-8B 4,58 — **un seul**, le disque ne suit pas | ☐ |
| 6 | **Machine cible volet B** *(noté à J2 : « machine cible, contrainte mémoire estimée »)* | qui héberge ? quelle RAM ? quel disque libre ? | ☐ |
| 7 | **Les cinq outils novateurs du bonus** | à choisir **maintenant** — comparatif par cas d'usage au **§8** | ☐ |

**Sur le point 7.** La grille de notation est donnée en clair par l'enseignant : *« 3 points pour cinq descriptions instructives dont au moins une critique argumentée ; 1 à 2 pour des descriptions honnêtes mais superficielles ; 0 pour une liste recopiée. »* Et ce qui est valorisé : les conditions dans lesquelles l'outil échoue, ce que la documentation omet, le temps d'appropriation constaté, la comparaison avec l'outil précédent, **un abandon argumenté**. Ce qui ne vaut rien : la reprise de la documentation, l'énumération de fonctionnalités, un avis non étayé, la citation d'un outil non installé.

> **Il nous faut donc au moins un outil que nous abandonnerons en le documentant.** Et un fichier `OUTILS.md` ouvert dès aujourd'hui, renseigné au fil de l'eau — en décembre, plus personne ne se souviendra du temps d'appropriation.

---

## 5 — Le cadrage exigé à J2

Le sujet est formel : *« Ce cadrage est absolument nécessaire, et aura un impact sur les notes. »* Quatre volets à remplir en séance.

### 5.1 Périmètre — et surtout ce qui ne sera pas livré

Le sujet demande explicitement de dire **ce qui ne sera pas livré**. C'est la partie que les équipes oublient, et celle qui distingue un cadrage d'une liste de vœux.

| Livré | Explicitement hors périmètre |
|---|---|
| … | … |
| … | … |

*Exemples de hors-périmètre défendables (si A2+B4) : pas de mode URL au-delà des domaines permissifs · pas de multilingue, français uniquement · pas d'authentification · pas de persistance côté serveur · pas de traitement de PDF scannés.*

### 5.2 Hypothèses — ce que nous tenons pour acquis et qui pourrait être faux

| Hypothèse | Si elle est fausse |
|---|---|
| Un BiLSTM maison exporté en ONNX s'exécute dans le navigateur en un temps acceptable | tout le volet A est à revoir → **à prototyper avant le 01/10** |
| Nous pouvons annoter N documents en X jours | le corpus glisse, le modèle glisse |
| Le décodage contraint fonctionne avec le runtime local retenu | la métrique principale du volet B disparaît |
| Les 5 membres sont disponibles jusqu'au 07/12 | voir §6 |

### 5.3 Risques — voir §6

### 5.4 Critères de réussite — « comment saurez-vous que le projet a abouti »

À formuler en chiffres, pas en adjectifs. Trame :

- Volet A : URL publique en ligne **avant le 01/10**, réponse en moins de N secondes sur machine de bureau, macro-F1 ≥ X sur le jeu de test.
- Volet B : taux de sorties conformes au schéma ≥ X % après adaptation, contre Y % avant.
- Conduite : 100 % des tâches réalisées ont eu un ticket **créé avant** la réalisation.

---

## 6 — Registre des risques

| # | Risque | Probabilité | Impact | Parade | Responsable |
|---|---|---|---|---|---|
| R1 | **Disque saturé** — 21 Gio libres, un modèle Q4 en consomme 4 à 5, les essais davantage | élevée | bloque le volet B | libérer 40 Gio **avant le 25/09** ; une seule variante de modèle à la fois ; désigner une machine de secours | |
| R2 | **Notions non enseignées** (RAG, ONNX, quantisation = 0 occurrence dans les supports) ; la J3 arrive après le jalon du 01/10 | **certaine** | retard sur les 2 volets | tâches d'auto-formation **datées et assignées** dès cette semaine ; elles alimentent le bonus +3 | |
| R3 | **Périmètre de l'« adaptation » non défini** par le sujet — facteur 3 à 5 sur la charge du volet B | élevée | 20 points | **question n° 1 du courriel**, réponse sous 24 h | |
| R4 | **CORS / anti-bot** sur le mode URL de A2 | **certaine** si A2 | fonctionnalité dégradée | repli copier-coller (prescrit par le sujet) + mesure du taux de succès par domaine | |
| R5 | **Corpus fabriqué par ceux qui l'évaluent** → score flatteur, échec en démo | élevée | crédibilité | jeu de test écrit par des membres qui n'ont pas écrit l'entraînement ; double annotation d'un échantillon | |
| R6 | **Indisponibilité d'un membre** (le sujet cite ce risque) | moyenne | jalon manqué | domaine principal **et** secondaire pour chacun, en binôme — imposé par le sujet | |
| R7 | **Déploiement tardif du volet A** — « un déploiement effectué le jour même sera considéré comme non livré » | moyenne | 15 points | page vide en ligne **dès cette semaine**, enrichie ensuite ; URL vérifiée 48 h avant J4 | |
| R8 | **Board renseigné après coup** — « identifiable et sans valeur » | moyenne | points de jalons | aucun commit sans ticket créé avant ; contrôle en revue hebdomadaire | |
| R9 | **Échec de la démo le 07/12** | moyenne | 15 points | **captation vidéo de secours des deux démonstrations** — « son absence peut entraîner la perte des points » | |

---

## 7 — Répartition des tâches

Le sujet impose : *« Chaque tâche a au moins un responsable identifié »*, et *« Une répartition efficace attribue à chacun un domaine principal et un domaine secondaire, en binôme avec un autre membre. »*

### 7.1 Cinq domaines, cinq binômes

| Membre | Domaine **principal** | Domaine **secondaire** | Binôme avec |
|---|---|---|---|
| ……… | **Corpus & annotation** — collecte, guide d'annotation, accord inter-annotateurs, jeux train/dev/test | Front & déploiement A | ……… |
| ……… | **Modèle volet A** — entraînement BiLSTM(-CRF), export ONNX, quantisation, tokenizer JS | Corpus & annotation | ……… |
| ……… | **Front & déploiement volet A** — UI/UX, Transformers.js, hébergement statique, modes unitaire et lot | Modèle volet A | ……… |
| ……… | **Volet B — socle** : modèle local, quantisation, découpage, index, récupération | Adaptation & évaluation | ……… |
| ……… | **Volet B — adaptation & évaluation** : décodage contraint ou fine-tuning, jeu de test, mesures avant/après | Socle volet B | ……… |

### 7.2 Responsabilités transversales — à attribuer nommément

| Rôle | Charge | Titulaire |
|---|---|---|
| **Pilotage du board** — tickets créés avant la réalisation, revue hebdomadaire | 1 h/semaine | ……… |
| **Journal d'usage de l'IA** + classeur de suivi *(livrables « disponibles dès maintenant »)* | 30 min/semaine | ……… |
| **`OUTILS.md`** — les cinq outils novateurs, renseignés au fil de l'eau | 30 min/semaine | ……… |
| **Rapport** — coordination ; rédaction **commencée au plus tard à J3 (16/10)** | à partir du 16/10 | ……… |
| **Soutenance** — support de **pitch** *et* support de **présentation** (deux fichiers distincts) | à partir de novembre | ……… |

### 7.3 Rituels

- **Un point hebdomadaire de 45 min**, même quand tout va bien. Le sujet demande au rapport « Tenue de réunions : fréquence, format, résultats produits » — donc un compte rendu écrit à chaque fois, même court.
- **Une mini-démo interne par membre à chaque point.** Le sujet le recommande explicitement : *« Profitez de vos meetings pour partager ce que vous faites, quitte à faire des mini démos entre vous, cela vous aidera pour la soutenance notamment. »*
- **Motif impératif** : en soutenance, *« le choix du répondant à chaque question relève de l'enseignant »*, et **n'importe qui peut être interrogé sur n'importe quelle portion du code**. Une réponse insuffisante **affecte l'équipe entière**. Personne ne peut ignorer le domaine des autres.

---

## 8 — Les cinq outils novateurs : comparatif par cas d'usage

### 8.1 Ce qui est noté — littéralement

Sujet §4. Cinq outils, entendus **largement** : « application, connexion MCP, serveur MCP, agent, sous-agent, environnement de développement, bibliothèque, ou mode d'orchestration de plusieurs de ces éléments ». Ils **n'ont pas à être de natures différentes** — « trois connexions MCP, un agent et un environnement de développement constituent un ensemble recevable ». Pour chacun : « sa nature, ses qualités, ses défauts, et votre retour d'expérience — usage effectif, résultats obtenus, difficultés rencontrées ».

| Valorisé | Sans valeur |
|---|---|
| Les conditions dans lesquelles l'outil **échoue** | La reprise de la documentation officielle |
| Ce que la documentation **omet** | L'énumération de fonctionnalités |
| Le **temps d'appropriation** constaté | Une appréciation sans usage documenté |
| La **comparaison** avec l'outil précédemment utilisé | **La citation d'un outil non installé** |
| Un **abandon argumenté** | Un avis non étayé |

Grille de l'enseignant, page 20 : *« 3 points pour cinq descriptions instructives **dont au moins une critique argumentée** ; 1 à 2 pour des descriptions honnêtes mais superficielles ; 0 pour une liste recopiée. »* Et : « L'appréciation porte sur la qualité du retour d'expérience, **non sur le succès de l'outil**. »

**Trois conséquences qui dictent notre choix :**

1. **Un outil non installé ne compte pas.** On ne choisit donc pas cinq outils à la mode : on choisit cinq postes que notre couple de cas d'usage **rend obligatoires**. L'usage devient inévitable, donc le REX s'écrit tout seul.
2. **L'échec rapporte autant que la réussite.** Il nous faut au moins un outil éprouvé puis **abandonné avec argument** — c'est la condition explicite des 3 points.
3. **Le REX se perd si on ne l'écrit pas au moment de l'usage.** Le temps d'appropriation et les messages d'erreur ne se reconstituent pas en décembre. `OUTILS.md` s'ouvre aujourd'hui.

### 8.2 Catalogue mesuré le 18/09/2026

Versions relevées sur les registres PyPI et npm ; installabilité déduite des étiquettes de roues (`macosx_*_arm64`, `universal2` ou `any`) pour **macOS ARM64 / Python 3.12**. Ce n'est pas une garantie de fonctionnement : c'est une garantie d'installation. La distinction est faite au §8.5.

| Poste de la chaîne | Candidats (version au 18/09/2026) | macOS ARM64 | Ce que ça apporte | Cas concernés |
|---|---|---|---|---|
| **1. Environnement & dépendances** | `uv` 0.12.17 *(0.11.0 déjà installé ici)* · `ruff` 0.16.8 | ✅ roues | résolution et installation très rapides, verrouillage reproductible | tous |
| **2. Annotation** | Label Studio 1.23.0 · doccano 1.8.4 · Argilla 2.8.0 | ✅ pur python | interface d'étiquetage, accord inter-annotateurs, export | **A1 A2 A4 A5** |
| **3. Export & quantisation ONNX** | `optimum` 2.3.0 **+ `optimum-onnx` 0.1.0** · `onnx` 1.23.0 · `onnxruntime` 1.30.0 | ✅ | transformer notre modèle entraîné en fichier servable au navigateur | **tout le volet A** |
| **4. Exécution navigateur** | `@huggingface/transformers` 4.3.0 *(16/09/2026)* · `onnxruntime-web` 1.30.0 · `vite` 8.3.0 | ✅ npm | inférence côté client, WebGPU/WASM, zéro serveur | **tout le volet A** |
| **5. Entrées documentaires** | `pdfjs-dist` 6.3.289 · `tesseract.js` 7.0.0 | ✅ npm | lecture PDF et OCR **dans le navigateur** | **A2 A5 B5** |
| **6. Inférence locale** | Ollama *(absent de la machine)* · `llama-cpp-python` 0.3.35 · `mlx-lm` 0.31.3 / `mlx` 0.32.2 · LM Studio | ⚠️ / ✅ | exécuter un 7-8B quantifié en local | **tout le volet B** |
| **7. Décodage contraint** | `outlines` 1.3.3 · `lm-format-enforcer` 0.11.3 · `guidance` 0.3.1 · `instructor` 1.17.0 · grammaires GBNF *(natives llama.cpp)* | ✅ | forcer une sortie conforme à un schéma — **la métrique de B4** | **B4 B5** |
| **8. Index & orchestration RAG** | `lancedb` 0.39.0 · `chromadb` 1.5.9 · `faiss-cpu` 1.15.1 · `llama-index` 0.14.24 · `haystack-ai` 3.1.1 · `langchain` 1.4.2 | ✅ | stockage vectoriel, découpage, chaîne de récupération | **A3 B1 B3** |
| **9. Adaptation du modèle** | `peft` 0.21.0 · `trl` 1.13.0 · `mlx-lm` (LoRA) · `unsloth` 2026.9.7 ⚠️ · `bitsandbytes` 0.50.2 ⚠️ | voir §8.5 | LoRA / QLoRA — **les 20 points du volet B** | **tout le volet B** |
| **10. Évaluation & suivi** | `ragas` 0.4.3 · `deepeval` 4.2.3 · `seqeval` 1.2.2 ⚠️ · `mlflow` 3.16.1 · `wandb` 0.30.0 | ✅ / ⚠️ | mesurer l'avant/après, tracer les runs | **tous** |
| **11. Agents, MCP, IDE, harnais** | Claude Code *(déjà en usage)* · **ECC `affaan-m/ECC` v2.2.1** *(voir §8.4)* · serveurs MCP configurés ici : `n8n-mcp`, `datagouv`, `kaggle` · MCP GitHub *(configuré, **non autorisé**)* · MCP Playwright | ✅ | assistance, sous-agents, squelettes, connexion aux outils du projet | tous |
| **12. Automatisation périodique** | n8n · GitHub Actions · `launchd` (natif macOS) | ✅ | le déclencheur de la chaîne **B5** | **B5** |

### 8.3 Trois paniers, un par couple

Chaque panier compte **cinq outils que le couple rend obligatoires**, plus un candidat à l'abandon argumenté — la pièce qui déclenche les 3 points.

#### Panier « A2 + B4 » — couple recommandé

| # | Outil | Poste | Pourquoi il est inévitable ici | Matière de REX attendue |
|---|---|---|---|---|
| 1 | **`optimum` + `optimum-onnx`** | 3 | sans lui, notre BiLSTM ne devient jamais un fichier servable | le paquet a été **scindé** (§8.6 piège 1) ; `optimum-onnx` est en **v0.1.0** |
| 2 | **`@huggingface/transformers`** (Transformers.js) | 4 | c'est l'exécution navigateur elle-même | 480 Mo installés dont 287 inutiles (§8.6 piège 3) ; le paquet a changé de nom (piège 2) |
| 3 | **`outlines`** *ou* **`lm-format-enforcer`** | 7 | le décodage contraint **est** la métrique de B4 | comparaison directe des deux sur le même schéma : temps d'appropriation, taux de conformité, échecs |
| 4 | **Label Studio** *ou* **doccano** | 2 | l'annotation NER token par token est ingérable sans interface | comparer les deux ; mesurer l'accord inter-annotateurs |
| 5 | **ECC** *(§8.4)*, **Claude Code + sous-agents**, ou une **connexion MCP GitHub** | 11 | la conduite de projet passe par GitHub, et le harnais sert tous les jours | le MCP GitHub est configuré mais **non autorisé** : le faire fonctionner *est* le REX. Pour ECC : le protocole de comparaison du §8.4 |
| ✂ | **`unsloth`** | 9 | candidat à l'abandon | classifiers PyPI `NVIDIA CUDA`, noyaux `triton`/`xformers` réservés à Linux/Windows, README qui annonce macOS → **trancher par installation réelle** |

#### Panier « A3 + B1 » — couple sécurisé

| # | Outil | Poste | Pourquoi il est inévitable ici | Matière de REX attendue |
|---|---|---|---|---|
| 1 | **`@huggingface/transformers`** | 4 | encodage de la requête côté client | idem ci-dessus |
| 2 | **`lancedb`** *ou* **`chromadb`** | 8 | l'index vectoriel de A3, réutilisé par B1 | comparer les deux sur le même corpus : temps d'indexation, empreinte disque, qualité |
| 3 | **`llama-index`** *ou* **`haystack-ai`** | 8 | orchestration de la chaîne RAG | deux philosophies opposées, comparaison argumentée |
| 4 | **`ragas`** | 10 | mesurer l'abstention et la fidélité aux sources — **le cœur de B1** | ce que ragas mesure vraiment, et ce qu'il ne mesure pas |
| 5 | **Ollama** *ou* **`mlx-lm`** | 6 | l'inférence locale de B1 | Ollama absent de la machine → temps d'installation réel ; `mlx-lm` est natif Apple Silicon |
| ✂ | **`langchain`** | 8 | candidat à l'abandon | l'éprouver puis argumenter son abandon au profit de `llama-index` — ou l'inverse |

#### Panier « A5 + B5 » — couple ambitieux

| # | Outil | Poste | Pourquoi il est inévitable ici | Matière de REX attendue |
|---|---|---|---|---|
| 1 | **`pdfjs-dist` + `tesseract.js`** | 5 | les trois modalités d'entrée de A5 | **le sujet exige déjà de mesurer l'effet de l'OCR** : le REX est un livrable |
| 2 | **`@huggingface/transformers`** | 4 | NER et normalisation côté client | idem |
| 3 | **`outlines`** *ou* **GBNF** | 7 | l'extraction contrainte de B5 | grammaire native llama.cpp *contre* bibliothèque Python |
| 4 | **`mlx-lm`** | 6 | inférence native Apple Silicon | le seul chemin conçu pour ce matériel |
| 5 | **n8n** *(déjà configuré en MCP ici)* ou **`launchd`** | 12 | le déclencheur périodique de B5 | le sujet prévient : l'orchestration est « le support de la démonstration, non son objet » — un abandon de n8n au profit de `launchd` serait **un excellent arbitrage documenté** |
| ✂ | **un proxy CORS tiers** | — | candidat à l'abandon | l'éprouver sur A5/A2, mesurer son taux d'échec, puis l'abandonner pour le copier-coller |

> **Constante des trois paniers** : `@huggingface/transformers` et un outil de décodage contraint ou d'index. Ce sont les deux briques que le sujet impose de fait, et dont aucun support de cours ne parle.

### 8.4 Cas examiné à la demande de l'équipe : ECC

**Ce que c'est — vérifié le 18/09/2026.** `affaan-m/ECC` (*Everything Claude Code*), licence **MIT**. Description officielle : « The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond. » Le dépôt fournit des répertoires `skills/`, `agents/`, `commands/`, `hooks/`, `workflows/`, `rules/`, `scaffolds/`, `mcp-configs/`, et des adaptateurs pour une vingtaine de harnais (`.claude`, `.codex`, `.cursor`, `.zed`, `.gemini`, `.opencode`, `.qwen`…). Deux paquets npm : `ecc-universal` **2.2.1** et `ecc-agentshield` **1.6.0**.

**Il entre bien dans la catégorie du bonus.** Le sujet admet « agent, sous-agent, environnement de développement, ou **mode d'orchestration** de plusieurs de ces éléments ». ECC est précisément un mode d'orchestration. La question n'est donc pas son admissibilité, mais son intérêt pour nous.

#### Santé du projet — mesurée

| Signal | Mesure | Lecture |
|---|---|---|
| Licence | MIT | ✅ aucune contrainte |
| Créé le / dernier push | 18/01/2026 · **17/09/2026** | ✅ vivant, poussé hier |
| Publications | v2.1.0 (27/07) · v2.2.0 (28/08) · v2.2.1 (08/09) | ✅ cadence régulière |
| Contributeurs | **336** | ✅ communauté réelle, pas un projet solo |
| Tickets ouverts | 228 | à lire avant d'adopter |
| Étoiles / forks | 261 879 · 39 184 (**15,0 %**) | ratio normal pour cette tranche |
| **Téléchargements npm `ecc-universal`** | **8 840 / semaine** | ⚠️ voir ci-dessous |
| README | **105 230 caractères**, 13 langues | temps d'appropriation non négligeable |

#### Non, cela ne nous démarquera pas — et c'est mesurable

261 879 étoiles placent ECC au **16ᵉ rang mondial** de GitHub — 15 dépôts seulement sont plus étoilés. Son README arbore un badge « GitHub Trending Repository of the Day ».

Plus parlant encore : **ses voisins immédiats au classement appartiennent à la même famille** — `obra/superpowers` 288 502 ★ et `mattpocock/skills` 265 198 ★, tous deux des dépôts de *skills* pour agents. Ce n'est pas un outil isolé que nous aurions dénichés : c'est une **catégorie encombrée et très visible**. D'autres équipes de la promotion peuvent parfaitement l'avoir trouvée aussi.

Second constat, plus instructif : **l'écart entre visibilité et usage**. 261 879 étoiles pour **8 840 téléchargements npm hebdomadaires**, quand `pdfjs-dist` en fait 25 039 480 et `@huggingface/transformers` 2 652 518. Une partie de l'écart s'explique — beaucoup installent par clone Git plutôt que par npm — mais l'ordre de grandeur invite à ne pas confondre notoriété et adoption.

> **Ce qui nous démarquera, ce n'est pas l'outil : c'est la critique.** La grille de l'enseignant exige « cinq descriptions instructives **dont au moins une critique argumentée** ». Un ECC encensé rapporte moins qu'un ECC mesuré.

#### Quatre points à connaître avant de l'adopter

1. **`.env.example` réclame `ANTHROPIC_API_KEY` et `GITHUB_TOKEN`.** La clé Anthropic implique des jetons facturés. Cela ne contrevient pas à la contrainte du volet A — « aucun coût » porte sur l'application livrée, pas sur nos outils de développement — mais il faut le dire, et savoir qui paie.
2. **Le `GITHUB_TOKEN` est un jeton personnel confié à un harnais tiers**, sur des dépôts qui portent une note. À restreindre au strict nécessaire, et à révoquer en fin de projet.
3. **`.env.example` propose aussi des fournisseurs tiers compatibles OpenAI** (Astraflow/UModelVerse, Atlas Cloud) via des liens à paramètres de campagne. Neutre en soi ; à connaître avant de s'étonner.
4. **`install.sh` n'est pas un `curl | sh` distant.** Lecture faite : 30 lignes qui résolvent le chemin réel, lancent `npm install` si besoin, puis délèguent à `scripts/install-apply.js`. Rien de suspect. *(C'est le point que nous soupçonnions le plus, et la lecture le dément — à noter tel quel dans le REX.)*

#### Les deux risques propres à NOTRE projet — plus importants que tout le reste

- **La soutenance.** Le sujet : « tout membre de l'équipe peut être interrogé en soutenance sur n'importe quelle portion du code produit. **Une réponse insuffisante affecte l'évaluation de l'équipe entière.** » Un harnais qui accélère la production augmente mécaniquement le volume de code que personne n'a raisonné. **C'est le risque n° 1 d'ECC pour nous.** Il se traite : toute portion produite avec assistance passe en revue par un binôme, dont l'un doit savoir l'expliquer au tableau.
- **La traçabilité.** Le sujet vérifie « une répartition des contributions cohérente avec la répartition des tâches déclarée », et croisera nos affirmations avec le dépôt et le board. Des commits ou des PR générés automatiquement brouillent cette lecture. Si ECC est adopté, **les commits restent manuels et nominatifs.**

#### Comment en tirer les 3 points plutôt qu'une ligne de plus

Ne pas l'ajouter comme sixième outil décoratif. Le placer au **poste 11** et le **mesurer**, puisque le sujet valorise « la comparaison avec l'outil précédemment utilisé » :

> Prendre **une tâche réelle du backlog** — par exemple l'export ONNX du BiLSTM, ou l'écriture du schéma de décodage contraint — et la faire **deux fois** : une fois avec le harnais nu, une fois avec ECC. Chronométrer, compter les allers-retours, compter les erreurs introduites, et noter **ce que chacun comprend du résultat**.
> Ce protocole produit un retour d'expérience chiffré **qu'ECC gagne ou qu'il perde** — et le sujet est explicite : « L'appréciation porte sur la qualité du retour d'expérience, non sur le succès de l'outil. »

#### Verdict pour les paniers du §8.3

ECC prend la **ligne 5 du panier A2+B4** (poste 11), aux côtés ou à la place de « Claude Code + sous-agents ». Il ne remplace **aucun** outil technique : il ne fait ni export ONNX, ni décodage contraint, ni RAG. Les paniers A3+B1 et A5+B5 n'ayant pas de ligne « harnais », l'y ajouter suppose d'en retirer un autre — **le panier reste à cinq**.

Coût d'entrée à provisionner : dépôt d'environ **50 Mo**, plus ses dépendances npm, sur **20 Gio libres** (§6, risque R1).

### 8.5 Installable ≠ fonctionnel — la distinction qui rapporte les points

Le tableau du §8.2 mesure ce qui **s'installe**. Quatre outils méritent une vérification d'exécution, et ce sont précisément ceux dont le REX sera le plus instructif.

| Outil | Ce que disent les métadonnées | Ce qu'il faut vérifier par l'usage |
|---|---|---|
| **`unsloth` 2026.9.7** | classifiers `Environment :: GPU :: NVIDIA CUDA` ; `triton` conditionné à Linux, `xformers` à Linux/Windows ; mais le README annonce « Windows, Linux, WSL **and macOS** » | contradiction nette. Sur Apple Silicon, y a-t-il un chemin accéléré, ou une retombée silencieuse sur CPU ? **Mesurer le temps par pas.** |
| **`bitsandbytes` 0.50.2** | classifier `Operating System :: MacOS` **et** roue `macosx_14_0_arm64` ; le tableau du README donne macOS 14+ arm64 en CPU ✅* et Metal/`mps` avec un 🚧 | le 4-bit QLoRA fonctionne-t-il réellement, ou seulement une partie des fonctions ? |
| **`llama-cpp-python` 0.3.35** | **aucune roue** — source uniquement, compilation obligatoire ; Metal via `CMAKE_ARGS="-DGGML_METAL=on"` | durée de compilation réelle, et accélération Metal effectivement active |
| **`seqeval` 1.2.2** | source uniquement, version figée depuis longtemps | encore utile, ou remplacer par la fonction `f1_entite` déjà écrite dans notre TP de journée 2 ? |

**Mesure déjà faite, et qui oriente le volet B.** PyTorch 2.14.0 voit bien le GPU de la machine : `torch.backends.mps.is_available() = True`, `torch.cuda.is_available() = False`. Sur un pas d'entraînement BiLSTM réaliste (embedding 20 000 × 128, hidden 128 bidirectionnel, lot 64 × 200 tokens) : **CPU 118 ms/pas, MPS 17 ms/pas — soit 6,9×**. Sur un produit matriciel fp32 2048² : 3 262 contre 5 516 GFLOP/s.

> ⚠️ **Et voici le piège, que nous avons nous-mêmes rencontré.** Sans préchauffage, la même mesure donnait MPS *plus lent* que le CPU (1 696 contre 3 047 GFLOP/s) — un artefact de compilation des noyaux au premier appel. **Toute comparaison de vitesse sans phase de préchauffage est fausse.** C'est exactement le genre de constat que la grille du bonus valorise, et il vaut pour tous nos futurs bancs d'essai.

### 8.6 Les huit pièges déjà mesurés

Utilisables tels quels dans `OUTILS.md` — chacun relève de « ce que la documentation omet ».

1. **`pip install optimum` ne suffit plus pour exporter en ONNX.** Depuis `optimum` 2.3.0, l'exporteur vit dans un paquet séparé, `optimum-onnx`, tiré par l'extra : `pip install "optimum[onnxruntime]"`. Et `optimum-onnx` est en **v0.1.0** — paquet très jeune, à surveiller.
2. **Transformers.js a changé de nom.** `@xenova/transformers` est figé en **v2.17.2 (mai 2024)** ; le paquet vivant est **`@huggingface/transformers` v4.3.0 (16/09/2026)**. La majorité des tutoriels en ligne visent le paquet périmé — API et modèles pris en charge diffèrent.
3. **Le coût disque d'un `npm install` de Transformers.js : 480 Mo** — mesuré, 46 paquets en 3 s. Dont **`onnxruntime-node` 287 Mo**, inutile pour une application navigateur, et `onnxruntime-web` 140 Mo. Sur une machine à **21 Gio libres**, ce n'est pas anodin ; le bundle *livré* reste petit, mais l'environnement de développement, non.
4. **Deux paquets seulement ne fournissent pas de roue macOS** sur les 33 examinés : `llama-cpp-python` et `seqeval`. Tous deux exigent une compilation.
5. **`unsloth` se présente comme un outil NVIDIA dans ses métadonnées et comme multiplateforme dans son README.** À trancher par l'essai, pas par la lecture.
6. **Aucune mesure de vitesse n'est valable sans préchauffage** (§8.5).
7. **Le serveur MCP GitHub est configuré mais non autorisé** dans notre session ; `plugin:data:definite` échoue à se connecter. Un outil configuré n'est pas un outil disponible.
8. **La popularité affichée n'est pas l'adoption.** ECC affiche 261 879 étoiles — **16ᵉ rang mondial** — pour **8 840 téléchargements npm par semaine** sur `ecc-universal`. Au même moment, `pdfjs-dist` fait 25 039 480 téléchargements hebdomadaires. Une étoile se donne en un clic ; une installation, non. **Vérifier les téléchargements avant de conclure à l'adoption d'un outil.**

### 8.7 Protocole de qualification — 30 minutes par outil

Sans protocole, on obtient cinq paragraphes d'impressions. Avec, on obtient cinq REX chiffrés.

1. **Chronométrer** de la première commande au premier résultat utile. C'est le « temps d'appropriation constaté » que le sujet valorise.
2. **Noter le premier message d'erreur**, verbatim, et ce qui l'a résolu.
3. **Exécuter une tâche minimale réelle** du projet — pas l'exemple du README.
4. **Comparer** à ce qu'on faisait avant, ou à l'outil concurrent du même poste.
5. **Conclure** : on garde, on garde sous condition, ou on abandonne — avec le motif.

Fiche type de `OUTILS.md`, à remplir **le jour de l'usage** :

```markdown
## <nom> <version> — poste <n>
- Nature :
- Installé le :            par :        temps jusqu'au 1er résultat :
- Tâche réelle exécutée :
- Résultat obtenu (chiffré) :
- Premier échec rencontré (message exact) + résolution :
- Ce que la documentation omet :
- Comparé à : ……   verdict : gardé / gardé sous condition / abandonné
- Motif :
```

### 8.8 Ce qu'il faut décider aujourd'hui

| # | Décision | Acté |
|---|---|---|
| a | Le panier de cinq outils, une fois le couple choisi (§3) | ☐ |
| b | Le **candidat à l'abandon** — sans lui, plafond à 2 points sur 3 | ☐ |
| c | Le titulaire de `OUTILS.md` (§7.2) | ☐ |
| d | Les deux vérifications d'exécution à lancer cette semaine (§8.5) | ☐ |
| e | **Adopter ECC ou non**, et à quelle place — avec le protocole de comparaison (§8.4) | ☐ |

---

## 9 — Gestion de projet sur GitHub

Nous avons choisi GitHub pour toute la conduite de projet. Le plan détaillé est dans `PLAN_GESTION_PROJET_GITHUB_NLP_Version3.md` — voici seulement ce qui change nos décisions.

### 9.1 Ce qui ne marche pas — mesuré le 11/09/2026 sur notre dépôt (org Free, dépôt privé)

| Fonction | État | Contournement |
|---|---|---|
| Protection de branche, rulesets | ❌ 403 « Upgrade to GitHub Pro or make this repository public » | convention écrite + Action qui refuse une PR sans ticket lié |
| **GitHub Pages** | ❌ indisponible sur dépôt privé en Free | **dépôt du volet A public**, ou Cloudflare Pages / Netlify |
| Automatisations Projects v2 | ⚠️ 4 workflows natifs seulement : item fermé → Done, PR mergée → Done, auto-add, auto-archive. « Issue assignée → Ready » et « PR ouverte → In Review » **n'existent pas** | déplacement manuel, vérifié en revue hebdomadaire |
| GitHub Actions | ⚠️ minutes comptées sur dépôt privé | CI sur `pull_request` uniquement |

### 9.2 Ce qu'il faut avoir **créé** pour J2 (noté)

Le sujet : *« Board de tickets créé : colonnes définies, membres ajoutés. Le remplissage n'est pas exigé à ce stade. »*

- ☐ Projet GitHub Projects v2 créé, **les 5 membres ajoutés**
- ☐ Colonnes `Status` : `Backlog` · `Ready` · `In progress` · `In review` · `Done` · `Abandonné`
- ☐ Champs personnalisés : `Volet` (A / B / Transverse) · `Jalon` · `Charge estimée` · `Responsable`
- ☐ **Milestones = les jalons notés** : `J2 21/09` · `Mi-parcours 01/10` · `J3 16/10` · `J4 07/12`
- ☐ Labels : `volet-a` · `volet-b` · `corpus` · `modele` · `front` · `rag` · `eval` · `doc` · `bonus-outils` · `bloquant`
- ☐ **Deux dépôts** (le sujet parle de « dépôts Git des deux volets », au pluriel) — volet A **public**, volet B privé

> **La colonne `Abandonné` n'est pas cosmétique.** *« Un projet qui documente les arbitrages (ie abandons de features) est supérieur à un projet qui prétend n'en avoir fait aucun. »* Une feature abandonnée se ferme avec un commentaire expliquant pourquoi — c'est de la matière de rapport.

### 9.3 Règles Git, non négociables

- **Aucune tâche sans ticket créé avant.** Le sujet détecte et sanctionne le board rétrospectif.
- Branche par ticket : `feat/42-export-onnx`, `fix/57-padding-masque`.
- Commits informatifs. Le dépôt **sera consulté** et les contributions **doivent être cohérentes avec la répartition déclarée** : si quelqu'un est responsable du volet A et n'a aucun commit dessus, cela se voit.
- Une PR par branche, un relecteur désigné — ce sera la réponse à « stratégie de branches, revues, qualité des messages de commit » du rapport.

---

## 10 — Le courriel du 20/09

Le sujet demande deux éléments : **les outils utilisés avec les liens d'invitation** (Git est déjà fait, le reste est à fournir) et **les cas d'usage des volets A et B**.

Trame :

```
Objet : [NLP 2] Équipe ……… — proposition de sujet (volets A et B)

Bonjour,

Outils et accès
- Dépôt volet A : <lien>   (public, pour GitHub Pages)
- Dépôt volet B : <lien>   (privé, invitation jointe)
- Board de suivi : <lien d'invitation>
- Journal d'usage de l'IA et classeur de suivi : <lien>

Volet A — <A?> : <titre>
Problématique · corpus et volumétrie · modèle envisagé · faisabilité
de l'exécution navigateur · indicateur de réussite · pourquoi cela
pourrait échouer.

Volet B — <B?> : <titre>
Problématique · modèle open-weights identifié · machine cible et
contrainte mémoire estimée · protocole de mesure avant/après.

Questions
1. Périmètre de l'« adaptation » du volet B : un RAG réglé et un prompt
   système suffisent-ils, ou un fine-tuning / LoRA est-il attendu ?
2. Le courriel de choix est-il attendu pour le dimanche 20/09 (§2) ou
   pour mercredi (§5) ? Nous nous alignons sur le 20/09.
3. Le dépôt du volet A doit être public pour GitHub Pages en plan Free :
   cela vous convient-il ?
4. Le chargement du modèle depuis le CDN Hugging Face à l'exécution
   est-il conforme à la contrainte de coût nul du volet A ?

Cordialement,
```

> **La note interne de l'enseignant indique** : *« Exiger la même fermeture d'une proposition libre : corpus et volumétrie dès le courriel. »* Même en retenant un cas de la liste, **annoncer notre corpus et sa volumétrie chiffrée** est ce qui distinguera notre courriel.
> Elle indique aussi : *« Une réponse est apportée sous 24 heures »* — donc envoyer tôt permet encore de corriger avant J2.

---

## 11 — Checklist J2 (10 points)

| Attendu du sujet | Notre livrable | ☐ |
|---|---|---|
| Environnement de développement déclaré | fiche `ENVIRONNEMENT.md` | ☐ |
| Board créé : colonnes définies, membres ajoutés | lien du projet | ☐ |
| **Volet A** : cas retenu, modèle envisagé, **faisabilité de l'exécution navigateur** | §3 + §2.3 de ce document | ☐ |
| **Volet B** : modèle open-weights identifié, **machine cible, contrainte mémoire estimée** | §4 décisions 5 et 6 | ☐ |
| Cadrage : périmètre, risques identifiés, répartition initiale | §5, §6, §7 | ☐ |
| *(hors barème, mais exigé)* courriel envoyé | §10 | ☐ |

---

## 12 — Ordre du jour chronométré

| | Durée | Point | Sortie attendue |
|---|---:|---|---|
| 1 | 10 min | Le cadre : barème, calendrier, ce qui est noté à J2 (§1) | tout le monde a les mêmes chiffres |
| 2 | 15 min | Ce qui a été vérifié : écart cours/projet, contraintes mesurées (§2) | conscience partagée du trou de compétences |
| 3 | **35 min** | **Décision n° 1 : le couple de cas d'usage** (§3) | **décision actée et écrite** |
| 4 | 20 min | Les six autres décisions (§4) | 6 lignes remplies |
| 5 | 20 min | Cadrage : périmètre, hors-périmètre, hypothèses, critères chiffrés (§5) | tableaux remplis |
| 6 | 15 min | Risques et répartition des tâches (§6, §7) | un responsable par ligne |
| 7 | 15 min | **Les cinq outils novateurs** : panier, candidat à l'abandon, titulaire (§8) | 4 lignes du §8.8 remplies |
| 8 | 10 min | GitHub : board, milestones, labels, deux dépôts (§9) | créés en séance |
| 9 | 15 min | Rédaction du courriel (§10) | **envoyé avant la fin de la réunion** |

**Trois choses doivent être vraies en sortant de cette salle :** le couple est choisi, le courriel est parti, et chaque ligne du §7 porte un nom.
