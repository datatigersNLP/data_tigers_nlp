# Chaîne de conversion Markdown vers LaTeX

Convertit un document Markdown en `.tex`, puis en PDF. Depuis la racine du dépôt :

```bash
python3 docs/latex/build.py docs/journal/JOURNAL_USAGE_IA.md   # écrit docs/journal/JOURNAL_USAGE_IA.tex
cd docs/journal && latexmk -xelatex JOURNAL_USAGE_IA.tex        # produit le PDF
```

Le script exige un argument. Le `.tex` produit est un fichier intermédiaire : seuls le
Markdown et le PDF sont versionnés.

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
