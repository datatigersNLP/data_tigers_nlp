# Logo de l'équipe Data Tigers

Ticket #176, à la suite d'une remarque de l'enseignant.

![Logo Data Tigers](logo-tigre-512.png)

**L'idée.** Un tigre, pour le nom de l'équipe, dessiné en pixel art comme un petit personnage de jeu. Il porte une robe d'avocat, avec le rabat blanc à deux bandes, parce que le corpus est juridique. Il lit un livre ouvert, le regard baissé et la bouche entrouverte : il cherche dans les fiches et répond. La couverture du livre reprend le vert des deux interfaces (`#17604A`). Création originale de l'équipe.

**Fichiers.**
- `tigre.py` : la source unique du dessin, une grille de 32 x 32 pixels avec une lettre par couleur, et sa palette de 16 couleurs.
- `logo-tigre.svg` : produit par le script, à pixels nets (`shape-rendering="crispEdges"`), 4 041 octets.
- `logo-tigre-512.png` : agrandissement sans lissage, pour le rapport et les diapositives.

**Où il est utilisé.** Le même SVG est recopié tel quel dans les deux interfaces :
- favicon : `front/public/favicon.svg` et `demo_b/public/favicon.svg` ;
- logo du panneau latéral et avatar de l'assistant : `front/src/assets/logo-tigre.svg` et `demo_b/src/assets/logo-tigre.svg`.

**Règle d'affichage.** Afficher le logo à 32 px ou à un multiple (64, 96, 128 px...), pour que chaque pixel du dessin tombe sur des pixels entiers de l'écran. Ne pas le lisser : en CSS, `image-rendering: pixelated` pour le PNG.

**Modifier le dessin.** Changer la grille ou la palette dans `tigre.py`, puis, depuis la racine du dépôt :

```
python docs/charte/logo/tigre.py              # réécrit le SVG et le PNG
cp docs/charte/logo/logo-tigre.svg front/public/favicon.svg    # et les trois autres copies
python docs/charte/logo/tigre.py --verifier   # contrôle le SVG versionné et ses quatre copies
```

Le script refuse une grille qui n'a pas 32 rangées de 32 pixels, une lettre hors de la palette, ou une asymétrie autre que la rangée 25 (les lignes de texte des deux pages). Le PNG demande Pillow.

**Contrôles faits le 21/11.**
- Le rendu du SVG dans Chrome, à 512 px, est identique pixel pour pixel au PNG tiré de la grille.
- Le dessin a été vérifié lisible à 16, 32 et 64 px, sur fond clair et sur fond sombre.
