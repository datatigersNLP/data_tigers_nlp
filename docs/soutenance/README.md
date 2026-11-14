# Supports de la soutenance J4

**Équipe** Data Tigers  
**Ticket** #114 (préparer la soutenance J4 : pitch, présentation, vidéo de secours, répétition et envoi)  
**Établi le** 14 novembre 2026 par Mahé BEGNIS ; chaque chiffre relu dans sa source à cette date  
**Usage** une seule source pour deux formats : les fichiers Marp donnent les PDF, et le même texte donne la version HTML animée.

---

## Contenu du dossier

| Fichier | Rôle |
|---|---|
| `pitch.md` | pitch, 5 diapositives, 3 min 45 visées |
| `presentation.md` | démonstration (1 diapositive, 3 min 50), présentation (10 diapositives, 7 min 57), annexes (13 diapositives, pour les questions) |
| `pitch.pdf`, `presentation.pdf` | rendus Marp de ces deux fichiers |
| `soutenance.html` | les 29 diapositives en une page animée, sans aucune ressource externe |
| `figures/*.svg` | les 8 figures, générées par `outils/figures.py` ; ne pas les modifier à la main |
| `outils/figures.py` | génère les figures ; échelles exactes et contrôle de la largeur des textes |
| `outils/construire_html.py` | construit `soutenance.html` à partir des deux fichiers Marp |
| `outils/controler_debordements.py` | vérifie qu'aucun contenu ne dépasse de sa diapositive, dans les PDF et dans la page HTML |

Chaque diapositive porte ses notes d'orateur dans un commentaire HTML : durée visée, texte à dire, questions probables et réponses. Le texte à dire est calibré à 130 mots par minute.

## Règles de rédaction

- Chaque terme technique est défini sur la diapositive où il apparaît (bandeau du bas) ou dans le glossaire (annexe 13).
- Chaque chiffre vient d'une source du dépôt : `docs/rapport/RAPPORT_FINAL.md` et son annexe des sources, `docs/jalons/J3_chiffres_verifies.md`, ou les sorties de mesure citées dans les notes.
- Aucun émoji ni tiret cadratin ou demi-cadratin ; `construire_html.py` refuse de construire la page s'il en trouve.
- Typographie française : espace insécable dans les nombres (4 240) et devant « % : ; ? ! » ; jamais dans les attributs SVG.
- Le jugement à l'aveugle de l'exactitude (diapositive des résultats et annexe 5) reprend l'analyse des grilles de Maïmouna et Vaneck rendues le 14/11, selon un plan figé avant de croiser la grille de Vaneck avec la clé. Les précisions demandées à Maïmouna peuvent modifier un chiffre : l'analyse sera alors refaite et les diapositives mises à jour.
- Aucune diapositive ni note ne décrit le comportement de T ou du modèle adapté sur une question du jeu de test : cela révélerait l'origine de réponses jugées à l'aveugle (#52). La démonstration suit donc le scénario de la #158, dont les questions sont hors du jeu de test, resserré pour tenir dans les 4 minutes prévues avec le volet A.

## Reconstruire

Ordre : figures, puis PDF, puis HTML, puis contrôle. Les commandes se lancent depuis la racine du dépôt, sauf l'étape 2.

1. Figures : `python3 -I docs/soutenance/outils/figures.py` (bibliothèque standard seulement).
2. PDF, depuis `docs/soutenance/` : `marp --html --allow-local-files --pdf pitch.md -o pitch.pdf < /dev/null`, puis de même pour `presentation.md`.
3. HTML : `python docs/soutenance/outils/construire_html.py`, avec un Python qui dispose de `markdown-it-py` (version 4.2.0 utilisée).
4. Contrôle : `MARP=<chemin de marp> CHROME_PATH=<chemin de Chrome> python3 -I docs/soutenance/outils/controler_debordements.py` ; il faut aussi `pdftotext` (poppler). Code de sortie 1 au moindre dépassement.

Points d'attention pour l'étape 2 :

- **Entrée standard** : marp-cli lit l'entrée standard quand elle n'est pas un terminal. Lancé depuis un script sans `< /dev/null`, il attend indéfiniment (blocage constaté le 14/11, plus d'une heure et demie sans sortie).
- **Images locales** : `--allow-local-files` est nécessaire pour que Chrome lise les figures SVG du dossier. Marp le signale par un avertissement, sans conséquence ici puisque les sources sont les nôtres.
- **Navigateur** : Chrome est désigné par la variable `CHROME_PATH`. Versions utilisées le 14/11 : marp-cli 4.5.1, Node 25.9.0, Chrome 155.

## Installation de marp-cli et risque accepté

marp-cli est installé hors du dépôt, dans un dossier local, avec `npm install @marp-team/marp-cli@4.5.1 --ignore-scripts` : aucun script d'installation n'est exécuté. `npm audit` signale 12 vulnérabilités dans des dépendances indirectes (téléchargement FTP, extraction d'archives, agents proxy, validation de schémas, rendu KaTeX). Aucune n'est atteinte par notre usage : conversion locale de nos propres fichiers, sans réseau, sans formule mathématique. Le risque est accepté pour cet usage seulement ; ne pas exposer marp-cli en serveur.

## Version HTML

`soutenance.html` s'ouvre dans n'importe quel navigateur récent, hors ligne.

- **Clavier** : flèches, Espace ou Entrée pour avancer ; N pour les notes avec la durée cumulée de la partie ; M pour le sommaire ; F pour le plein écran ; Échap pour fermer un panneau.
- **Adresse** : l'adresse se termine par `#dN`, qui ouvre directement la diapositive N.
- **Animations** : apparition progressive des éléments, tracé des flèches et croissance des barres. Elles ne jouent qu'à l'arrivée sur une diapositive par la navigation, et jamais si le système demande de réduire les animations.
- **Polices** : aucune police n'est téléchargée. La page utilise la même pile que les PDF (IBM Plex Sans si elle est installée, sinon Helvetica Neue ou Arial). Les retours à la ligne restent proches de ceux des PDF sans être identiques, car Chrome ne compose pas tout à fait de la même façon à l'écran et à l'impression : chaque format est donc contrôlé séparément. Aucune adresse IP de spectateur ne part chez un tiers.

Contrôles faits le 14/11 sur la page construite, dans Chrome sans interface :

- aucun débordement, d'après `controler_debordements.py`, sur les 29 diapositives de la page et sur les 5 et 24 pages des PDF. Pour les PDF, le script lit la position de chaque mot, car le HTML exporté par Marp ne compose pas comme son PDF. Contrôle négatif : sur une copie qui reprend une version fautive de la diapositive des résultats, il signale bien le débordement ;
- aucune erreur de console ;
- navigation, sommaire, notes et bornes vérifiés par un script qui simule les touches ;
- affichage vérifié à 400 et à 900 pixels de large.

## Durées visées

| Partie | Durée visée | Texte à dire, à 130 mots par minute |
|---|---|---|
| Pitch | 3 min 45 | 3 min 32 |
| Démonstration | 3 min 50 | scénario, sans texte rédigé |
| Présentation | 7 min 57 | 7 min 54 |

Les annexes ne sont pas présentées : elles servent à répondre aux questions.
