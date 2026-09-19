# Chaîne de conversion Markdown vers LaTeX

Convertit un document Markdown du dossier en `.tex`, puis en PDF.

```bash
python3 latex/build.py 05_RAPPORT_J2.md      # écrit 05_RAPPORT_J2.tex
latexmk -xelatex 05_RAPPORT_J2.tex           # produit le PDF
```

Sans argument, le script traite `03_SUPPORT_REUNION_J2.md`.

## Fichiers

- `preambule.tex` : mise en page (fontes Libertinus, Inter, Fira Mono, palette,
  titres, tableaux, encadrés, en-tête courant paramétrable).
- `md2tex.py` : conversion du Markdown (titres, tableaux, listes, citations,
  blocs de code, symboles). Les titres commençant par « Annexe » ne sont pas
  numérotés mais figurent au sommaire.
- `build.py` : assemblage, bandeau de titre et en-tête courant par document
  (tables `BANDEAU` et `ENTETE`), plus une **passe de mesure** : avant de
  générer le document, XeLaTeX mesure la largeur réelle du plus large fragment
  insécable de chaque colonne, ce qui permet de dimensionner les tableaux sans
  débordement.

## Ajouter un document

Créer une entrée dans `BANDEAU` et dans `ENTETE` de `build.py`, avec la clé
égale au nom du fichier sans extension.

## Contrôle de qualité après compilation

```bash
grep -c '^! '               <doc>.log    # 0 erreur
grep -c 'Overfull \\hbox'   <doc>.log    # 0 débordement
grep -c 'Underfull \\hbox'  <doc>.log    # 0
grep -c 'Missing character' <doc>.log    # 0
```
