# Projet NLP 2, équipe Data Tigers

Projet de fin de module NLP 2, Master 2 Data & IA, FGES, Université Catholique de Lille.
Année universitaire 2026-2027. Enseignant : Adrian ROSARI.

**Membres** Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE.

## Cas d'usage retenus

| Volet | Cas | Objet |
|---|---|---|
| A, application en ligne | A3 | recherche sémantique en corpus fermé, inférence dans le navigateur |
| B, application locale | B1 | assistant réglementaire sourcé, avec abstention |

A3 constitue la couche de récupération de B1 : corpus, découpage, encodage et index sont
écrits une fois et servent aux deux volets.

## Organisation du dépôt

```
docs/
  jalons/    rapports de jalon, en Markdown et en PDF
  journal/   journal d'usage de l'IA
  suivi/     classeur de suivi des tâches et des charges
  etudes/    audit du sujet et étude comparative des cas d'usage
  latex/     chaîne de conversion Markdown vers PDF
```

Les PDF se régénèrent depuis les sources Markdown :

```bash
python3 docs/latex/build.py docs/jalons/J2_rapport.md
latexmk -xelatex -cd docs/jalons/J2_rapport.tex
```

## Branches

| Branche | Rôle |
|---|---|
| `main` | état livrable, consultable. Tag posé à chaque jalon |
| `dev` | intégration du travail en cours |
| `feat/NN-sujet`, `fix/NN-sujet`, `docs/NN-sujet` | une branche par ticket, fusionnée dans `dev` |

À chaque jalon, `dev` est fusionnée dans `main` et un tag est posé.

## Commits

Convention `type(portée): description`, avec les types `feat`, `fix`, `docs`, `chore`,
et le numéro du ticket en référence.

## Règles de conduite

- Aucune tâche engagée sans ticket créé au préalable.
- Une pull request par branche, relue par le titulaire secondaire du domaine.
- Toute production assistée par IA est relue par le binôme, et consignée dans le journal.
