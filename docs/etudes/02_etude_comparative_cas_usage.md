# Étude comparative des cas d'usage — Projet NLP 2

**Objet** éclairer la décision du couple (cas volet A, cas volet B), à arrêter **avant le dimanche 20/09/2026**.
**Base** `Projet_NLP_2_parties.pdf` audité le 18/09/2026 → voir `01_AUDIT_SUJET_PROJET.md`.
**Statut** document de travail. Les chiffres de charge sont des **estimations de premier ordre**, à réviser en réunion.

---

## 0 — Méthode

### 0.1 Ce qui contraint le choix, avant toute préférence

Cinq contraintes mesurées encadrent la décision. Elles ne se négocient pas.

1. **Le volet A ne fait pas de génération.** L'inférence tourne dans le navigateur : classification, extraction d'entités, recherche sémantique, similarité. Le sujet l'écrit : « Elle ne supporte pas la génération de texte longue. »
2. **Aucun modèle ONNX prêt à l'emploi ne tient dans un dépôt GitHub** (106–113 MiB mesurés, limite dure 100 MiB). Voir audit §3.1 et §3.3.
3. **Le modèle maison est explicitement mieux noté** que le modèle emprunté, sur le volet A.
4. **Le volet B vaut 20 points sur « adaptation, mesures avant/après, feuille de route »** — le poste le plus lourd de la soutenance. Un cas dont la métrique est coûteuse à produire met ces 20 points en danger.
5. **RAG, ONNX, quantisation et adaptation totalisent 0 occurrence dans les supports du module.** Quel que soit le choix, il y a une auto-formation à planifier.

### 0.2 Grille d'évaluation

Chaque cas est noté de 1 à 5 sur sept critères. **La direction change selon le critère** et est rappelée sous chaque tableau.

| Critère | Ce qu'il mesure |
|---|---|
| **Annotation** | volume et coût du corpus à constituer et étiqueter par l'équipe |
| **Modélisation** | difficulté technique du modèle lui-même |
| **Intégration** | difficulté de la chaîne autour du modèle (navigateur, PDF, OCR, pipeline) |
| **Réemploi TP** | part du travail déjà faite en TP et directement récupérable |
| **Modèle maison** | possibilité réaliste de servir un modèle entraîné par l'équipe (volet A) |
| **Métrique** | objectivité et coût de la mesure — un critère décisif pour le volet B |
| **UX/design** | matière offerte aux 15 points « design et parcours utilisateur » |

---

# Partie I — Volet A : les cinq cas

---

## A1 — Routeur de demandes étudiantes

**Tâche** classification multi-classe de phrases courtes, 6 à 10 classes fixées par l'équipe (scolarité, stages, informatique, bibliothèque, vie étudiante…).

**Ce que le sujet exige précisément.** Corpus constitué **et annoté par l'équipe**, « quelques centaines de messages ». Distribution déséquilibrée assumée, « ce dont le choix des métriques devra tenir compte ». Deux modes d'entrée : saisie libre **et** dépôt d'un fichier texte ou CSV pour traitement par lot. Deux modes de sortie : en unitaire le service identifié **avec indice de confiance et les deux services suivants par vraisemblance** ; en lot un tableau ligne à ligne **avec export**.

**Lien avec les TP — direct et fort.** C'est la tâche du TP2 IMDB (RNN/LSTM/BiLSTM en classification de séquence) transposée du binaire au multi-classe, et la partie 4 du TP de journée 2 est littéralement intitulée « Un LSTM en classification multi-classe », avec la section « Regardez la distribution avant de modéliser » et la bascule `BCEWithLogits` → `CrossEntropy`. Les métriques et le traitement du déséquilibre viennent des rappels M1 (mesuré : 25 occurrences de F1, 8 de « déséquilibre »).

**Architecture.** BiLSTM entraîné sur le corpus maison → export ONNX (`torch.onnx.export`) → **quelques Mo**, versionnable dans le dépôt, sans LFS ni CDN. C'est le cas qui coche le mieux la « Valorisation » du sujet.

**Le piège technique réel.** Un modèle maison impose de **réimplémenter la tokenisation en JavaScript, à l'identique de l'entraînement Python**. Vocabulaire, normalisation, troncature, indice `<unk>`, padding : le moindre écart dégrade silencieusement les prédictions sans lever d'erreur. À traiter par un jeu de non-régression : N phrases, les identifiants de tokens attendus, comparés des deux côtés.

**Risque principal.** Le corpus est fabriqué par ceux qui l'évaluent : on obtient un score flatteur en test et un échec en démonstration. **Parade** : le jeu de test est rédigé par des membres qui n'ont pas rédigé le jeu d'entraînement, et on ajoute des messages réels ou ambigus.

**Charge estimée** ≈ **14 à 18 jours-homme**.

---

## A2 — Extracteur d'offres de stage

**Tâche** reconnaissance d'entités sur une annonce de stage : entreprise, lieu, durée, compétences requises. Schéma d'annotation défini par l'équipe.

**Ce que le sujet exige précisément.** Entrée par **URL** d'une annonce (LinkedIn, Indeed ou autre), l'application « récupère et nettoie le contenu de la page », avec **mode de repli par copier-coller** explicitement demandé. Sortie : le texte restitué avec **entités surlignées par code couleur**, plus une fiche structurée et un export.

**Lien avec les TP — le plus direct de tous.** Les parties 4 et 5 du TP de journée 2 font exactement cela sur WikiNER : étiquetage BIO, 4 types, LSTM puis BiLSTM, conversion IOB1→IOB2, et surtout une fonction d'évaluation **F1 par entité** (`f1_entite`) déjà écrite, testée par assertions, et accompagnée d'un modèle nul de référence. Tout ce bloc se récupère tel quel.

**Correction à porter au sujet.** « L'architecture BiLSTM-CRF étudiée en journée 2 » : mesuré, le CRF n'a **pas** été implémenté en journée 2. Il est traité en théorie dans le deck de rappels (HMM, Viterbi, matrice de transitions, « la référence à battre ») et listé comme *prolongement facultatif* du TP. **La couche CRF est une charge à prévoir, pas un acquis** — environ 2 jours-homme, avec un gain réel : elle interdit les séquences invalides du type `O → I-PER`.

**Le point dur : l'entrée par URL est en grande partie condamnée.** En architecture 100 % statique, sans serveur, une requête du navigateur vers `linkedin.com` est **bloquée par CORS** avant même que l'anti-bot n'intervienne. Trois issues, à arbitrer et à écrire :
- repli copier-coller — prescrit par le sujet, fiable, appauvrit la démonstration ;
- proxy CORS tiers — réintroduit une dépendance externe et un point de défaillance le jour J ;
- restreindre le mode URL aux sites permissifs, et **mesurer le taux de succès par domaine**. C'est la voie la plus honnête, et elle produit un résultat chiffré exploitable au rapport.

Le sujet valorise explicitement ce type d'arbitrage documenté.

**Coût caché : l'annotation.** Étiqueter du NER se fait **token par token**, pas par document. Pour `ENTREPRISE` et `LIEU`, un modèle pré-entraîné peut pré-annoter (`Xenova/camembert-ner` couvre ORG et LOC) et l'équipe corrige. Pour `DURÉE` et `COMPÉTENCES`, tout est à faire — et « compétence » est une catégorie aux frontières floues, qui impose un guide d'annotation et une mesure d'accord entre annotateurs.

**UX.** Le surlignage coloré par type est un rendu immédiatement lisible et convaincant. Bon terrain pour les 15 points de design.

**Charge estimée** ≈ **20 à 26 jours-homme**.

---

## A3 — Recherche sémantique en corpus fermé

**Tâche** retourner les passages pertinents d'un corpus normatif (règlement, syllabus, FAQ) en réponse à une question en langage naturel. **Aucune génération.**

**Ce que le sujet exige précisément.** Corpus **embarqué** dans l'application, pas fourni par le visiteur, **et son périmètre doit être affiché**. Sortie : liste ordonnée, chaque passage avec **score de similarité, référence de sa section d'origine, et lien vers le document complet**. Le sujet désigne le point dur : « La stratégie de découpage du corpus constitue un paramètre déterminant de la qualité des résultats. »

**Lien avec les TP.** Similarité cosinus et recherche documentaire viennent des rappels M1 ; le deck de rappels annonce d'ailleurs « Similarité cosinus — J1, J3, **projet** — Analogies, puis recherche de fragments dans le chatbot ». Les embeddings viennent de la journée 1 (Word2Vec). **En revanche rien ne vient de la journée 2** : c'est le seul cas du volet A qui n'exploite pas le BiLSTM.

**L'architecture la plus élégante du volet A.** Les embeddings du corpus se **précalculent hors ligne** et se livrent en fichier statique ; le navigateur n'encode que la requête. Pour 1 000 passages en 384 dimensions, float32 : `1000 × 384 × 4 = 1,54 Mo`. En int8 : 0,4 Mo. Le site reste minuscule, la recherche est instantanée, et rien ne dépasse aucune limite. C'est aussi **la couche de récupération d'un RAG** : entièrement mutualisable avec B1.

**La faiblesse, et comment la retourner.** La « Valorisation » du sujet est mal servie : on utilisera presque certainement un encodeur pré-entraîné (`Xenova/multilingual-e5-small`, 112,8 MiB via CDN), pas un modèle maison. **Parade qui transforme le défaut en résultat** : construire en parallèle un index TF-IDF maison — quelques dizaines de Ko, calculable en JavaScript, entièrement maîtrisé — et **comparer les deux sur le même jeu de questions**. On obtient une mesure du gain réel des embeddings sur un corpus fermé et francophone, ce qui est exactement la matière que le rapport réclame (coût, latence, qualité, contrôle, dépendance). Le TF-IDF vient des rappels M1 : le lien au cours est rétabli.

**Risque principal.** Paraître trop simple. La difficulté de modélisation est la plus faible du volet A ; le travail se déplace vers le découpage, l'évaluation et l'interface. Récupérable, puisque les 15 points portent sur « application livrée et accessible, qualité du design et du parcours utilisateur » — mais à compenser par un volet B ambitieux.

**Charge estimée** ≈ **12 à 16 jours-homme** — la plus faible du volet A.

---

## A4 — Analyseur de retours étudiants

**Tâche** sur un verbatim d'évaluation de cours, restituer **une polarité** et **une thématique** parmi rythme, contenu, support, évaluation.

**Ce que le sujet exige précisément.** Deux classifications parallèles sur une même entrée. **L'équipe décide si la thématique est multi-classe ou multi-label, et justifie ce choix** — c'est une décision notée, pas un détail. Deux modes d'entrée (saisie unitaire, dépôt CSV exporté d'un formulaire). En mode lot : tableau, **visualisation de la répartition thématique × polarité**, export.

**Lien avec les TP — direct.** La polarité, c'est le TP2 IMDB transposé au français : même tâche, même architecture, même protocole. Le pipeline BiLSTM de classification de sentiment existe déjà et tourne. La thématique ajoute une seconde tête sur le même encodeur.

**Architecture.** Un encodeur partagé, deux têtes — architecture multi-tâche, simple à expliquer en soutenance et élégante à présenter. Export ONNX d'un modèle maison de quelques Mo : « Valorisation » satisfaite, dépôt GitHub satisfait.

**Décision à documenter.** Multi-classe ou multi-label ? Un verbatim comme « le rythme est soutenable mais les supports sont illisibles » porte deux thématiques et deux polarités opposées. Le multi-label est plus juste et plus difficile (seuil par classe, métriques par label, sous-ensembles exacts). **Le sujet demande la justification, pas la facilité** — et un multi-classe assumé, argumenté et mesuré vaut mieux qu'un multi-label bâclé.

**UX.** La visualisation croisée thématique × polarité est le meilleur potentiel graphique du volet A.

**Risque principal.** Identique à A1 : corpus fabriqué, donc artificiel. Aggravé ici par la subjectivité de la polarité sur des verbatims courts. **Parade** : double annotation d'un échantillon et mesure de l'accord entre annotateurs — un chiffre qui a sa place dans le rapport.

**Charge estimée** ≈ **15 à 19 jours-homme**.

---

## A5 — Évaluateur de potentiel de cooptation

**Tâche** l'utilisateur donne un poste visé et une entreprise cible, soumet des profils, le système évalue pour chacun la probabilité de cooptation selon trois règles fournies par le sujet.

**Ce que le sujet exige précisément.** Trois modalités d'entrée au choix de l'équipe : **PDF** (export LinkedIn ou CV), **copier-coller**, **capture d'écran avec OCR exécuté côté client**. Sortie par profil : score, **règle appliquée**, et **éléments extraits ayant fondé la décision** — pour que l'utilisateur repère une erreur d'extraction. Trois contraintes imposées : les limites de l'export PDF LinkedIn (navigateur seulement, profil en anglais, 100 documents/mois pour un tiers), **la mesure de l'effet de l'OCR** en comparant capture et texte sur un même profil — « cette comparaison constitue un résultat à part entière » —, et **aucune collecte automatisée**, point à traiter dans le rapport.

**Lien avec les TP — combinatoire.** NER (journée 2) plus embeddings et cosinus (journée 1). Aucun TP ne couvre l'ensemble, mais les deux briques centrales sont acquises.

**La difficulté centrale est nommée par le sujet, et c'est la bonne.** « Lead Data Engineer » et « Responsable de l'ingénierie des données » désignent le même poste sans partager un seul terme : la correspondance exacte échoue, le rapprochement par embeddings aboutit. La hiérarchisation des niveaux (équivalent, n+1, n+2) relève de la même méthode appliquée à des intitulés de référence. C'est un problème de **normalisation sémantique** réel, bien posé, et directement traitable avec les outils du module.

**Le vrai risque : l'empilement.** Cinq briques indépendantes doivent fonctionner ensemble dans le navigateur — extraction PDF (pdf.js), OCR (tesseract.js), NER, normalisation par embeddings, moteur de règles — plus une interface qui **explique** sa décision. Chacune est faisable ; c'est leur chaînage qui consomme le temps, et chaque maillon peut faire échouer la démonstration.

**La contrepartie.** Le sujet indique explicitement que ce cas « se combine naturellement avec B5 », et qu'une équipe retenant les deux « dispose d'un terrain de comparaison direct entre un modèle léger exécuté en navigateur et un modèle de grande taille exécuté localement, **sur une tâche identique** ». C'est la formulation même de la thèse que le rapport doit défendre.

**Charge estimée** ≈ **24 à 32 jours-homme** — la plus élevée du volet A.

---

## Synthèse comparative — Volet A

| | **A1** Routeur | **A2** Offres de stage | **A3** Recherche sém. | **A4** Retours étudiants | **A5** Cooptation |
|---|:---:|:---:|:---:|:---:|:---:|
| **Tâche NLP** | classification multi-classe | NER | retrieval par embeddings | 2 classifications // | NER + normalisation + règles |
| **Annotation** *(coût)* | 3 | **5** | **1** | 3 | 4 |
| **Modélisation** *(difficulté)* | 2 | 4 | **1** | 3 | **5** |
| **Intégration** *(difficulté)* | 2 | 4 | 2 | 2 | **5** |
| **Réemploi TP** *(bénéfice)* | **5** | **5** | 3 | **5** | 3 |
| **Modèle maison** *(bénéfice)* | **5** | **5** | 2 | **5** | 3 |
| **Métrique** *(qualité)* | **5** | 4 | 3 | 4 | 3 |
| **UX/design** *(potentiel)* | 3 | **5** | 4 | **5** | **5** |
| **Charge estimée (j·h)** | 14–18 | 20–26 | **12–16** | 15–19 | 24–32 |
| **Modèle servi** | BiLSTM maison, qq Mo | BiLSTM-CRF maison ou CDN 106 MiB | encodeur CDN 113 MiB + index précalculé | BiLSTM 2 têtes maison, qq Mo | encodeur CDN + NER maison |
| **Risque n° 1** | corpus artificiel | **CORS sur le mode URL** | ambition jugée faible | subjectivité des étiquettes | **empilement de 5 briques** |

> **Direction des échelles.** *Annotation, Modélisation, Intégration* : 1 = facile, 5 = difficile. *Réemploi TP, Modèle maison, Métrique, UX* : 1 = faible, 5 = fort. Charges : estimations de premier ordre pour une équipe de 5, à réviser.

---

# Partie II — Volet B : les cinq cas

**Rappel du barème** : 20 points sur « adaptation, mesures avant/après, feuille de route ». **Le critère décisif n'est pas la difficulté du cas, c'est le coût de sa mesure.** Un cas dont l'évaluation exige un jugement humain consomme le temps qui devait servir à l'adaptation.

---

## B1 — Assistant réglementaire sourcé

**Tâche** répondre sur un corpus normatif en **citant systématiquement les passages sources**, et produire une **réponse d'abstention** quand l'information n'y est pas.

**Évaluation prescrite** un jeu de questions comportant une **proportion de questions hors corpus**, pour mesurer le **taux d'abstention correcte**. Métrique objective, automatisable une fois le jeu construit.

**Le vrai sujet n'est pas le RAG, c'est l'abstention.** Récupérer des passages et les faire résumer est un exercice connu. Refuser de répondre quand le corpus est muet suppose un seuil de similarité calibré, un prompt qui autorise le refus, et une mesure de deux erreurs opposées : l'hallucination sur question hors corpus, et l'abstention à tort sur question couverte. C'est un beau problème, et il produit des chiffres.

**Mutualisation.** Corpus, découpage et couche de récupération **identiques à A3**. Le couple A3+B1 fait un seul travail de corpus pour deux volets.

**Ambiguïté à lever.** Si « adaptation » exige un fine-tuning, B1 s'y prête moins bien que B2 ou B4 : l'essentiel du gain vient du RAG et du prompt. Une LoRA sur le style de citation et le format d'abstention est possible, mais c'est un ajustement de forme. *→ Question n° 1 du mail au professeur.*

**Charge estimée** ≈ **18 à 24 jours-homme**.

---

## B2 — Générateur de questions de révision

**Tâche** produire, à partir d'un support de cours, des questions d'examen **et leur corrigé**. Le modèle est adapté sur un **style de questionnement défini par l'équipe**.

**Évaluation prescrite** « le taux de corrigés exacts, **et non la forme des questions produites** ».

**C'est le cas où l'adaptation est la plus clairement exigée et la plus démontrable.** « Le modèle est adapté sur un style » : le fine-tuning n'est pas optionnel, il est dans l'énoncé. L'avant/après se voit à l'œil nu et se mesure. Cela cadre parfaitement avec les 20 points.

**Corpus disponible immédiatement.** Les supports du module sont sur le disque : 5 PDF de cours, 3 fiches de synthèse, 6 notebooks — environ 246 000 caractères de texte utile. Aucune collecte à faire.

**Le point dur : mesurer.** « Taux de corrigés exacts » suppose une vérité de référence. Il faut soit rédiger des corrigés de référence à la main (coûteux mais honnête), soit recourir à un modèle juge (rapide mais qu'il faut alors valider contre un échantillon humain). **C'est le cas dont la métrique coûte le plus cher**, et ce coût pèse sur les 20 points.

**Charge estimée** ≈ **18 à 24 jours-homme**, dont une part notable en évaluation.

---

## B3 — Assistant documentaire sur dépôt de code

**Tâche** répondre à des questions sur le code source et les tickets du projet de l'équipe.

**Attrait annoncé** le corpus est le dépôt lui-même, donc les réponses se vérifient directement. Et « le découpage de code obéit à des règles distinctes de celles applicables à la prose » — un vrai sujet technique (découper par fonction et par classe, pas par nombre de caractères ; conserver signatures et docstrings).

**Défaut rédhibitoire de calendrier, à soulever explicitement.** *Le corpus n'existe pas encore.* Au 18/09, le dépôt de l'équipe contient **un fichier `readme.md` de 16 octets et un unique commit**. Le corpus se remplit au fil du projet : il n'y aura pas de matière avant la mi-octobre, alors que le jalon mi-parcours du 01/10 exige déjà « première inférence locale aboutie ». On construirait l'évaluation d'un système sur une cible mouvante.

**Second défaut.** L'évaluation est la plus molle des cinq : aucune métrique n'est prescrite, et « la vérification directe des réponses » est un jugement humain, pas une mesure.

**Charge estimée** ≈ **16 à 22 jours-homme** — mais non démarrable avant la mi-octobre. **À écarter.**

---

## B4 — Profileur de compétences

**Tâche** produire, à partir d'une offre d'emploi, un profil structuré : compétences requises, niveau attendu, **écart avec un profil fourni**.

**Évaluation prescrite** « la proportion de sorties **conformes au schéma** », ce qui « conduit à examiner les techniques de **décodage contraint** ».

**C'est le meilleur rapport mesure/coût des cinq cas.** La conformité au schéma est **binaire, automatique et instantanée** : on valide la sortie JSON contre le schéma, on compte. Aucun juge humain, aucune vérité de référence à rédiger pour la métrique principale. Le taux passe typiquement de très médiocre en génération libre à quasi parfait en décodage contraint : **l'avant/après est spectaculaire et gratuit à produire**. Exactement ce que les 20 points demandent.

**Compétence professionnelle réelle.** Le décodage contraint — grammaires GBNF côté llama.cpp, JSON Schema côté serveurs d'inférence — est une technique utilisée en production et peu enseignée. Elle fait un excellent sujet de soutenance.

**Nuance honnête.** La conformité au schéma mesure la *forme*, pas la *justesse*. Un JSON parfaitement conforme peut contenir des compétences inventées. Il faut donc une seconde métrique sur l'exactitude du contenu, sur un échantillon annoté — plus coûteuse, mais limitée à un échantillon puisque la métrique principale couvre déjà le volume.

**Mutualisation.** Domaine « emploi » commun avec A2 (offres de stage) et A5 (profils).

**Charge estimée** ≈ **15 à 20 jours-homme** — la plus faible du volet B.

---

## B5 — Chaîne automatisée de qualification de profils

**Tâche** un traitement périodique **sans intervention humaine** : lecture d'un lot de profils, extraction structurée (postes, entreprises, périodes) en décodage contraint, normalisation des intitulés, score selon les règles de cooptation de A5, écriture dans une table SQL ou un classeur.

**Ce que le sujet précise, et qui change tout.** « L'objet évalué reste la qualité de l'extraction et de la normalisation. **L'ordonnancement, la persistance et l'orchestration constituent le support de la démonstration, non son objet.** » Autrement dit : ne pas investir dans l'infrastructure. Un répertoire surveillé suffit comme déclencheur — le sujet le suggère lui-même.

**Difficulté supplémentaire annoncée.** L'extraction textuelle des PDF conditionne toute la chaîne, et « les CV présentent une difficulté supérieure aux exports LinkedIn : mise en page sur plusieurs colonnes, tableaux, encarts ». **L'équipe doit documenter le taux d'échec d'extraction par type de document** — c'est un livrable, donc une tâche.

**Le pairing que le sujet recommande.** B5 est « le prolongement automatisé » de A5. Le couple donne une comparaison directe modèle léger navigateur / grand modèle local sur tâche identique.

**Charge estimée** ≈ **25 à 32 jours-homme** — la plus élevée du volet B.

---

## Synthèse comparative — Volet B

| | **B1** Assistant régl. | **B2** Questions de révision | **B3** Doc. sur dépôt | **B4** Profileur | **B5** Chaîne auto. |
|---|:---:|:---:|:---:|:---:|:---:|
| **Technique centrale** | RAG + abstention calibrée | fine-tuning de style | RAG sur code | **décodage contraint** | pipeline + extraction contrainte |
| **Corpus disponible** | ✅ règlements, syllabus | ✅ **déjà sur disque** | ❌ **n'existe pas encore** | ✅ offres publiques | ⚠️ profils/CV à réunir |
| **Annotation** *(coût)* | 3 | 4 | 2 | 2 | 4 |
| **Difficulté technique** | 3 | 4 | 3 | 3 | **5** |
| **Coût de la mesure** | 3 | **5** | **5** | **1** | 3 |
| **Objectivité de la métrique** | 4 | 3 | **1** | **5** | 4 |
| **Avant/après démontrable** | 3 | **5** | 2 | **5** | 4 |
| **Charge estimée (j·h)** | 18–24 | 18–24 | 16–22 | **15–20** | 25–32 |
| **Risque n° 1** | adaptation jugée trop légère | **évaluation chronophage** | **corpus absent avant mi-oct.** | conformité ≠ justesse | empilement + extraction PDF |

> **Direction des échelles.** *Annotation, Difficulté, Coût de la mesure* : 1 = facile, 5 = difficile. *Objectivité, Avant/après* : 1 = faible, 5 = fort.

---

# Partie III — Le vrai objet de la décision : le couple

Choisir A et B séparément est une erreur de méthode. Le rapport est noté sur **la comparaison des deux volets**, et la charge réelle dépend de ce que les deux volets partagent. Un couple bien apparié économise un corpus, un schéma d'annotation et un jeu de test — soit, en ordre de grandeur, **5 à 8 jours-homme**.

## Grille des couples

| Couple | Mutualisation | Qualité de la comparaison finale | Charge cumulée | Risque dominant |
|---|---|---|:---:|---|
| **A2 + B4** *emploi* | **forte** — un seul corpus d'offres, un seul schéma d'extraction, un seul jeu de test annoté | **maximale** — même tâche d'extraction, BiLSTM-CRF maison *contre* LLM 7B en décodage contraint : coût, latence, contrôle, explicabilité, dépendance se mesurent tous les cinq | 35–46 j·h | CORS sur le mode URL ; annotation NER lourde |
| **A3 + B1** *corpus normatif* | **très forte** — corpus, découpage et récupération identiques ; A3 **est** la couche retrieval de B1 | **bonne** — « restituer sans générer » *contre* « générer en citant, ou s'abstenir » : la comparaison porte sur la génération et l'hallucination | **30–40 j·h** | ambition technique du volet A jugée faible ; adaptation B1 possiblement jugée légère |
| **A5 + B5** *cooptation* | **forte** — règles, schéma et corpus de profils communs | **maximale** — le sujet la recommande nommément : tâche identique, navigateur *contre* local | **49–64 j·h** | **charge la plus élevée des deux volets simultanément** |
| **A4 + B2** *pédagogique* | moyenne — domaine commun (cours et évaluations), corpus distincts | moyenne | 33–43 j·h | deux corpus à fabriquer ; évaluation B2 coûteuse |
| **A1 + B4** *service étudiant* | faible — domaines sans recouvrement | moyenne — classification maison *contre* extraction LLM, tâches différentes | 29–38 j·h | aucune économie d'échelle |

## Lecture

**A3 + B1** est le couple le plus économe et le plus sûr. Un seul corpus, un seul découpage, une couche de récupération écrite une fois et servie deux fois. La livraison du volet A au 01/10 est quasi garantie, ce qui sécurise les 10 points du jalon mi-parcours. Sa faiblesse est double et connue : le volet A n'utilise pas les acquis de la journée 2 et ne sert pas de modèle maison, et l'adaptation du volet B risque de se réduire à du réglage de RAG — or ce sont 20 points.

**A5 + B5** est le couple que le sujet recommande et le plus payant *sur le papier*. Il est aussi le plus lourd des cinq, et il concentre les deux charges maximales sur la même équipe et le même calendrier — alors que 35 des 40 points hors soutenance se jouent en 28 jours. À ne retenir que si l'équipe est complète, disponible et déjà à l'aise sur les deux volets.

**A2 + B4** est l'équilibre. Il conserve l'intégralité du réemploi du TP de journée 2 (BiLSTM d'étiquetage, format BIO, F1 par entité déjà codé), permet de servir un modèle maison de quelques mégaoctets — donc de satisfaire la « Valorisation » *et* de contourner la limite des 100 MiB —, et confie au volet B la technique dont **la mesure est la moins chère et l'avant/après le plus net** : le décodage contraint. Surtout, les deux volets attaquent **la même tâche d'extraction sur le même corpus d'offres, avec le même jeu de test annoté**. La comparaison demandée par le rapport — coût, latence, qualité, degré de contrôle, explicabilité, dépendance à un fournisseur — se remplit alors avec des chiffres mesurés des deux côtés, et non avec des impressions.

Son risque est identifié et borné : le mode URL de A2 se heurte à CORS. Le sujet prescrit lui-même le repli, et transformer cette limite en mesure — taux de succès de récupération par domaine — produit un résultat de rapport plutôt qu'un échec.

## Recommandation

| Scénario | Couple | Quand le retenir |
|---|---|---|
| **Recommandé** | **A2 + B4** | équipe de 5 disponible, volonté de servir un modèle maison, recherche du meilleur rapport entre note et charge |
| **Sécurisé** | **A3 + B1** | disponibilité incertaine, ou priorité absolue donnée à la tenue des jalons — à compléter par un volet B ambitieux pour ne pas perdre sur les 20 points |
| **Ambitieux** | **A5 + B5** | équipe complète, à l'aise, et décidée à charger septembre et octobre |

**Dans les trois cas, deux décisions restent identiques :**

1. **Le volet A sert un modèle exporté par l'équipe** chaque fois que c'est possible — quelques mégaoctets d'ONNX versionnés dans le dépôt, sans Git LFS, sans CDN. C'est ce que le sujet récompense, et c'est ce qui rend la démonstration du 07/12 indépendante d'un service tiers.
2. **Le jeu de test est écrit avant le modèle**, par des membres qui ne l'entraînent pas. Le sujet note la mesure plus que le résultat ; un jeu de test rédigé après coup se voit.

---

## Ce qui reste à trancher en réunion

| # | Décision | Impact si mal tranchée |
|---|---|---|
| 1 | Le couple (A, B) | structure tout le reste — **à arrêter avant le 20/09** |
| 2 | Périmètre de l'« adaptation » du volet B | facteur 3 à 5 sur la charge — *question au professeur* |
| 3 | Modèle maison exporté ONNX **ou** modèle du CDN Hugging Face | conditionne le dépôt, la « Valorisation » et la robustesse de la démo |
| 4 | Dépôt du volet A public (obligatoire pour GitHub Pages en plan Free) ou autre hébergeur statique | bloque le déploiement du 01/10 |
| 5 | Modèle local : Mistral-7B (4,07 Gio), Qwen2.5-7B (4,36 Gio) ou Llama-3.1-8B (4,58 Gio) | 24 Go de RAM les acceptent tous ; **21 Gio de disque libre n'en acceptent pas trois** |
| 6 | Qui annote, selon quel guide, et comment on mesure l'accord entre annotateurs | qualité de tout le volet A |
| 7 | Les cinq outils novateurs du bonus, choisis **maintenant** pour être documentés au fil de l'eau | +3 points, perdus si documentés en décembre |
