# Projet NLP 2, équipe Data Tigers

Projet de fin de module NLP 2, Master 2 Data & IA, FGES, Université Catholique de Lille.
Année universitaire 2026-2027. Enseignant : Adrian ROSARI.

**Membres** Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE.

## Le site du volet A

**En ligne : https://datatigersnlp.github.io/data_tigers_nlp/**

- **Ce qu'il fait.** Une recherche sémantique (cas A3) dans les 261 fiches pratiques du ministère du Travail
  (travail-emploi.gouv.fr), découpées en 4 240 passages, instantané SocialGouv du 11 septembre 2026. Il ne
  génère aucun texte : pour une question, il renvoie les 5 passages les plus proches, chacun avec son score de
  similarité, la section de la fiche dont il vient et un lien vers la fiche complète.
- **Où il calcule.** Entièrement dans le navigateur du visiteur : aucune question n'est envoyée à un serveur. Le
  modèle `multilingual-e5-small`, quantifié en q8 et élagué sans perte de son vocabulaire (65,7 Mio, mêmes vecteurs
  bit à bit que le q8 d'origine pour tout texte en alphabet latin ou grec), est servi par le site lui-même et exécuté
  par Transformers.js 4.3.0.
- **Ses limites.** Un seuil de similarité, fixé sur un jeu externe, repère les saisies sans rapport avec le droit
  du travail ; il ne détecte pas toutes les questions sans réponse dans les fiches. Les passages ne sont pas un
  conseil juridique.
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
| 5. Ajustement de l'encodeur (étude) | `scripts/adaptation/` | `docs/etudes/adaptation/01_ajustement_encodeur_contrastif.md`, protocole `docs/etudes/evaluation/05_protocole_ajustement.md` |
| 6. Volet B : première inférence locale (Qwen2.5-7B-Instruct, Q4_K_M), réussie le 27 septembre (#31) | `scripts/inference/` | `docs/etudes/inference_locale_qwen.md` |
| 7. Volet B : chaîne RAG complète (#51) | à intégrer | en cours |

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
