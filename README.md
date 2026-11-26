# Projet NLP 2, équipe Data Tigers

Projet de fin de module NLP 2, Master 2 Data & IA, FGES, Université Catholique de Lille.
Année universitaire 2026-2027. Enseignant : Adrian ROSARI.

**Membres** Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE.

## Le site du volet A

**En ligne : https://datatigersnlp.github.io/data_tigers_nlp/**

- **Ce qu'il fait.** Une recherche sémantique (cas A3) dans les 261 fiches pratiques du ministère du Travail
  (travail-emploi.gouv.fr), découpées en 4 240 passages, instantané SocialGouv du 11 septembre 2026. Il ne
  génère aucun texte : pour une question, il renvoie les 10 passages les plus proches, regroupés par fiche, chacun
  avec son score de similarité, la section de la fiche dont il vient et un lien vers la fiche complète.
- **Où il calcule.** Entièrement dans le navigateur du visiteur : aucune question n'est envoyée à un serveur.
  Depuis le 15 novembre 2026 (#164), le modèle est l'encodeur `multilingual-e5-small` ajusté sur nos fiches (#49),
  quantifié en q8 et élagué sans perte de son vocabulaire (65,7 Mio, mêmes vecteurs bit à bit que le q8 complet pour
  tout texte en alphabet latin ou grec). Il est servi par le site lui-même et exécuté par Transformers.js 4.3.0.
- **Ses limites.** Un seuil de similarité, fixé sur un jeu externe, repère les saisies sans rapport avec le droit
  du travail ; il ne détecte pas toutes les questions sans réponse dans les fiches. Juste au-dessus du seuil, un
  avertissement invite à vérifier les passages, sans les masquer. Les passages ne sont pas un conseil juridique.
- **Son code.** Dans `front/`, qui explique comment le lancer en local et comment il est déployé :
  [front/README.md](front/README.md). Chaque fusion dans `dev` qui modifie `front/` redéploie le site.

## Cas d'usage retenus

| Volet | Cas | Objet |
|---|---|---|
| A, application en ligne | A3 | recherche sémantique en corpus fermé, inférence dans le navigateur |
| B, application locale | B1 | assistant réglementaire sourcé, avec abstention |

A3 constitue la couche de récupération de B1 : corpus, découpage, encodage et index sont
écrits une fois et servent aux deux volets.

## Chaîne de traitement

| Étape | Code | Document de référence |
|---|---|---|
| 1. Corpus et découpage (M2, structurel) | `scripts/decoupage/01_corpus_decoupage.ipynb` | `docs/etudes/decoupage/01_corpus_decoupage.md` |
| 2. Encodage et index du site | `scripts/indexation/02_indexation.ipynb` | `docs/etudes/indexation/02_indexation.md`, et les supports `01_encodeur_e5_small` et `03_apprentissage_contrastif` |
| 3. Évaluation sur le jeu de questions | `scripts/evaluation/03_evaluation.ipynb` | `docs/etudes/evaluation/03_evaluation.md`, avec son protocole, son audit statistique et le jeu du CDTN (`04_cdtn.md`) |
| 4. Allègement du modèle servi | `scripts/allegement/` | `scripts/allegement/README.md` |
| 5. Ajustement de l'encodeur, servi depuis le 15 novembre (#164) | `scripts/adaptation/`, mesure `scripts/evaluation/ajustement_05.py` | `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md`, protocole `docs/etudes/evaluation/05_protocole_ajustement.md`, résultats `docs/etudes/evaluation/05_resultats_ajustement.md` |
| 6. Volet B : première inférence locale (Qwen2.5-7B-Instruct, Q4_K_M), réussie le 27 septembre (#31) | `scripts/inference/` | `docs/etudes/inference_locale_qwen.md` |
| 7. Volet B : chaîne RAG (#51), adaptation du modèle (#49) et interface de démonstration | `scripts/rag/`, `scripts/adaptation_qwen/`, `demo_b/` | `docs/etudes/rag_51.md`, `demo_b/README.md` |

Les dossiers de `scripts/` déclarent leurs dépendances dans `requirements.txt`, en Python 3.12, et la plupart en
figent toutes les versions dans `requirements-lock.txt`. Les données brutes et intermédiaires vont dans `data/`, qui
n'est jamais versionné : les notebooks et les scripts les reconstruisent.

## Résultats au 17 octobre 2026

- **Critère du jalon J2 satisfait** (notebook 03, mesure unique du 13 octobre, protocole figé avant) : sur les
  73 questions du corpus du lot de test, l'encodeur servi place un passage pertinent dans ses 5 premiers résultats
  pour 43,8 % des questions, contre 42,5 % pour BM25 de référence. L'écart de +1,4 point a un intervalle à 95 % de
  -11,5 à +14,3 points, au-dessus de la marge de non-infériorité de -15 points. Aucun des deux n'est démontré
  meilleur (McNemar, p = 1,000).
- **Abstention.** Le score sépare assez bien les questions hors corpus (AUC de 0,841), mais le seuil conserve 72 des
  73 questions du corpus et ne rejette que 9 des 24 questions hors corpus.
- **Encodeur ajusté (#49).** La mesure prévue par le protocole 05 n'a pas été faite avant le 16 octobre ; la règle
  de repli écrite d'avance s'applique : le site sert l'encodeur de base pour la fin du volet A.

## Résultats au 15 novembre 2026 (#164)

- **Encodeur ajusté servi** (protocole 05 et son amendement A1, mesure faite deux fois avec un résultat identique) :
  sur le lot de test, un passage pertinent figure dans les 5 premiers résultats pour 63,0 % des questions du
  corpus, contre 43,8 % pour l'encodeur de base, soit +19,2 points [+9,7 ; +30,4] ; sur le CDTN, +4,9 points
  [+0,6 ; +9,3]. La règle écrite d'avance, un écart positif ou nul sur les deux jeux, est satisfaite.
- **Ce que voit le visiteur** (10 passages regroupés par fiche) : une fiche pertinente est affichée pour 93,2 % des
  questions du corpus, contre 83,6 % pour le site précédent (+9,6 points [+4,1 ; +18,5], aucune question perdue),
  pour 4,0 fiches affichées en moyenne au lieu de 3,0.
- **Abstention** : avec le seuil recalculé pour l'encodeur ajusté, 70 des 73 questions du corpus sont conservées
  et 10 des 24 questions hors corpus rejetées ; 13 autres reçoivent l'avertissement de la zone grise.
- Détail, contrôles et limites : `docs/etudes/evaluation/05_resultats_ajustement.md`.

## Volet B, chaîne v2 : résultats au 15 novembre 2026 (#163)

- **Chaîne v2 non adoptée** (protocole 08, figé avant la mesure, une seule exécution, analyse descriptive) : avec le
  modèle adapté, la récupération v2, la consigne v2 et l'abstention par le reclasseur, une citation pertinente est
  donnée pour 27 des 73 questions du corpus, contre 18 sur 72 pour B2. Mais seules 18 des 24 questions hors corpus
  sont refusées, contre 20 pour B2 ; la règle écrite d'avance en exigeait au moins 19. B2 reste la chaîne de
  référence.
- **Ce qui progresse** : un passage pertinent figure dans le contexte pour 53 questions sur 73, contre 33 sur 72 en
  B2 ; le modèle adapté en exploite à peu près la même part (27 sur 53 contre 18 sur 33).
- Détail, contrôles et limites : `docs/etudes/evaluation/08_resultats_chaine_v2.md`.

## Mesure corrigée au 16 novembre 2026 (#139, provisoire)

La règle D4 ne reconnaît qu'un extrait par question : elle sous-estime tous les systèmes. Le protocole 09, figé
avant tout jugement, fait juger à l'aveugle les 617 paires (question, passage montré par un système et non reconnu
par D4) par deux modèles d'IA déclarés comme tels. L'étalonnage du 17 novembre, sur 100 paires, a été fait par deux
autres modèles d'IA, pas par des humains : il confirme la règle large (kappa 0,89) mais ne permet pas de conclure sur
la règle principale, qui n'avait qu'un positif dans l'échantillon. Tout est descriptif : aucune décision passée ne change.

- **Volet A** : avec la règle principale (les deux juges jugent que le passage répond), l'encodeur ajusté place un
  passage pertinent dans les 5 premiers pour 74,0 % des questions (63,0 % selon D4), et dans les 10 passages du
  site pour 84,9 % (74,0 %). Son gain sur la base passe de +19,2 à +13,7 points [+3,2 ; +25,0].
- **Volet B** : le contexte de B2 contient un passage pertinent pour 62,5 % des questions (45,8 % selon D4), celui de
  la récupération v2 pour 89,0 % (72,6 %). M4, qui mesure la traçabilité et non l'exactitude, vaut 30,6 % pour B2 et
  52,1 % pour V2. Avec la récupération v2, la plupart des échecs restants viennent du modèle, qui s'abstient ou cite
  un autre passage alors qu'un passage pertinent est fourni.
- **CDTN, plusieurs passages pertinents par requête** : nDCG@10 de 41,5 % pour l'ajusté, 35,9 % pour la base et
  35,0 % pour BM25 ; en moyenne, un tiers seulement des passages pertinents d'une requête (32,7 %) figure dans les
  5 premiers de l'ajusté.
- Détail, contrôles et limites : `docs/etudes/evaluation/09_resultats_jugement_mutualise.md`.

## Résultats au 21 novembre 2026 (protocole 10, #171)

Mesures sur le jeu de questions v2 : 121 questions du corpus et 40 hors corpus, écrites par des sous-agents Claude
sur autorisation de l'enseignant, avec un protocole figé avant toute génération. Les résultats obtenus sur ce jeu
sont signalés comme tels et ne remplacent pas le jeu humain.

- **Chaîne de démonstration du volet B, de bout en bout** (10 passages, fusion avec BM25 et reclasseur) : la réponse
  cite un passage pertinent pour 52,9 % des questions du corpus (63 sur 119). Sur les 118 questions communes avec
  l'ancienne chaîne à 5 passages, 52,5 % contre 35,6 %, soit +16,9 points [+6,4 ; +27,3], démontré (p = 0,003).
  Abstention correcte sur les 39 questions hors corpus évaluées, hors corpus au sens du protocole (contrôle des 10
  premiers passages par un juge d'IA, pas de tout le corpus). Avec le modèle d'origine, non adapté, la même
  chaîne ne cite un passage pertinent que pour 10,1 % des questions. Prix : 11,8 s par question en médiane, contre
  4,9 s.
- **Fusion avec BM25 dans le site** (#173) : permise par la règle (+5,0 points sur le jeu v2, +2,6 sur le CDTN),
  mais aucun gain n'est démontré et les questions humaines du lot de test reculent de 6,8 points ; l'équipe y
  renonce.
- **Encodeurs nourris de questions synthétiques** (#167) : ni la v2-T (2 289 paires, questions du modèle témoin)
  ni la v3-C (2 420 paires, questions de Claude Sonnet relues par Claude Opus, amendement A3 figé avant toute
  génération) ne sont servies. La v3-C gagne 12,4 points démontrés sur le jeu v2, écrit par Claude, mais recule
  sur le CDTN (−2,2) et sur le lot de test (−5,5) : le gain tient au style des questions. L'encodeur ajusté du
  15 novembre reste servi.
- **Confidentialité** (#176, PR #177 en relecture) : le site ne contacte que son propre domaine, n'envoie rien
  après une question, ne dépose aucun cookie et ne garde en cache que les fichiers du modèle ; dans la
  configuration de la démonstration, l'assistant local ne journalise ni question ni réponse.
- Détail, contrôles et limites : `docs/etudes/evaluation/10_resultats.md` (PR #174).

## Organisation du dépôt

```
front/         site du volet A (Vite, React, Tailwind CSS), modèle et index servis dans front/public/
scripts/       découpage, indexation, évaluation, allègement, adaptation, inférence (un dossier par étape)
evaluation/    jeu de questions annoté par l'équipe ; jugements du CDTN (identifiants et verdicts seulement)
docs/
  corpus/      description du corpus
  etudes/      audit du sujet, étude comparative des cas d'usage, puis une étude par étape : découpage,
               indexation, évaluation, adaptation, inférence locale
  jalons/      rapports de jalon, en Markdown et en PDF
  journal/     journal d'usage de l'IA
  latex/       chaîne de conversion Markdown vers PDF
  rapport/     rapport du projet, en Markdown et en PDF (V0 du 19 octobre 2026, V1 avant le jalon J4)
  reunions/    supports de réunion
  suivi/       classeur de suivi des tâches et des charges, suivi des outils novateurs
```

Les PDF se régénèrent depuis les sources Markdown :

```bash
python3 docs/latex/build.py docs/jalons/J2_rapport.md
latexmk -xelatex -cd docs/jalons/J2_rapport.tex
```

## Données et licences

| Élément | Licence | Détail |
|---|---|---|
| Fiches pratiques du ministère du Travail | Licence Ouverte Etalab 2.0 | source et date à citer : `front/public/index/SOURCES.md` |
| Modèle `intfloat/multilingual-e5-small` | MIT | licence jointe au modèle servi : `front/public/modele/` |
| Requêtes du CDTN (`SocialGouv/datafiller-data`) | Apache-2.0 | lues dans `data/` ; seuls des identifiants et des verdicts sont versionnés (`docs/etudes/evaluation/04_cdtn.md`) |

Aucune licence n'est déclarée pour le code du dépôt.

## Branches, tags et jalons

| Branche | Rôle |
|---|---|
| `main` | état livrable, consultable, mis à jour depuis `dev` par pull request à chaque jalon |
| `dev` | intégration du travail en cours ; le site est déployé depuis cette branche |
| `feat/NN-sujet`, `fix/NN-sujet`, `docs/NN-sujet` | une branche par ticket, fusionnée dans `dev` |
| `observation/mi-parcours` | état figé du mi-parcours, à ne plus modifier |

| Tag | Objet |
|---|---|
| `jalon-j2` | jalon J2, 27 septembre 2026 |
| `jeu-questions-v1` | jeu de questions figé avant toute mesure, 6 octobre 2026 |
| `mi-parcours` | version du site en ligne au mi-parcours (déployée le 30 septembre), tag posé a posteriori le 17 octobre |
| `volet-a-v1` | fin du volet A, 18 octobre 2026 : `main` après la PR #84 (`8955962`) |

## Commits

Convention `type(portée): description`, avec les types `feat`, `fix`, `docs`, `chore`,
et le numéro du ticket en référence.

## Règles de conduite

- Aucune tâche engagée sans ticket créé au préalable.
- Une pull request par branche, relue par le titulaire secondaire du domaine.
- Toute production assistée par IA est relue par le binôme, et consignée dans le journal
  (`docs/journal/JOURNAL_USAGE_IA.md`).
