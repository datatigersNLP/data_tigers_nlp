# Contributions mesurées, relevé du 26 novembre 2026

**Équipe** Data Tigers
**Référence** `origin/dev` au commit `ff21f4b` ; commits uniques hors fusions : 462
**Relevé par** `scripts/suivi/contributions.py` (tests : `scripts/suivi/test_contributions.py`) ; données brutes : `docs/suivi/contributions_20261126.csv`

## Pourquoi cette mesure

Le classeur de suivi contient des heures par membre et par ticket. Elles sont presque toutes des estimations rétrospectives, non chronométrées, établies par trois méthodes différentes : déclarations des intéressés, estimations proposées avec un assistant puis relues, estimations de Jibril divisées par deux à sa demande (`SUIVI.md`). Aucune charge n'a été inscrite pour Mahé. Elles ne permettent donc pas de comparer les membres. Le 26 novembre, Mahé a décidé de comparer les contributions sur des quantités comptées par GitHub et par Git : tickets, commits et lignes. Les heures restent dans `SUIVI.md`, à titre indicatif.

## Ce qui est compté

| Mesure | Définition |
|---|---|
| Tickets assignés | tickets dont le membre est l'un des responsables sur GitHub ; un ticket compte une fois pour chacun de ses responsables |
| dont terminés | parmi eux, les tickets fermés comme terminés (les tickets fermés sans suite ne comptent pas) |
| Tickets touchés | tickets cités par au moins un commit du membre, ou par une PR dont il est l'auteur (sujet, titre ou nom de branche) |
| Tickets créés | tickets dont le membre est l'auteur |
| PR fusionnées | PR dont le membre est l'auteur et que GitHub marque fusionnées |
| Relectures | revues déposées sur la PR d'un autre membre, de tout état ; les commentaires d'un auteur sur sa propre PR et ceux des robots sont exclus |
| Commits poussés | commits uniques hors fusions, sur toutes les branches du dépôt GitHub, les tags et les têtes de PR (branches supprimées comprises) ; les commits qui ne sont pas sur GitHub ne comptent pas |
| Lignes ajoutées | cumul de `git log --numstat` (renommages détectés), par catégorie de fichier |
| Lignes conservées | lignes non vides encore présentes dans `dev`, attribuées par `git blame -w -M -C` ; deux fichiers au contenu identique ne comptent qu'une fois |

Catégories de fichiers : le code (Python, JavaScript, JSX, CSS, HTML hors `docs/`, scripts shell, YAML), la documentation (Markdown, LaTeX, texte, et les pages HTML de `docs/`, qui sont des diapositives), les carnets Jupyter, les données et fichiers de verrouillage (JSON, CSV, SVG, `package-lock.json`, `requirements*.txt`). Les carnets, qui comptent leur JSON brut, sortie des cellules comprise, et les données ne sont pas comparés en lignes : ils sont donnés à part.

## Résultats

**Tickets et pull requests.**

| Membre | Tickets assignés | dont terminés | Tickets touchés | Tickets créés | PR fusionnées | Relectures des PR des autres |
|---|---:|---:|---:|---:|---:|---:|
| Mahé | 52 (26 %) | 38 (29 %) | 36 (48 %) | 37 (54 %) | 58 (51 %) | 73 (39 %) |
| Jibril | 44 (22 %) | 28 (21 %) | 17 (23 %) | 32 (46 %) | 24 (21 %) | 48 (26 %) |
| Remy | 36 (18 %) | 25 (19 %) | 8 (11 %) | 0 (0 %) | 11 (10 %) | 31 (17 %) |
| Vaneck | 33 (17 %) | 21 (16 %) | 10 (13 %) | 0 (0 %) | 15 (13 %) | 21 (11 %) |
| Maïmouna | 32 (16 %) | 20 (15 %) | 4 (5 %) | 0 (0 %) | 5 (4 %) | 13 (7 %) |
| Total | 197 | 132 | 75 | 69 | 113 | 186 |

**Commits et lignes de code.**

| Membre | Commits poussés | dont dans `dev` | Lignes de code ajoutées | Lignes de code conservées |
|---|---:|---:|---:|---:|
| Mahé | 201 (44 %) | 197 (43 %) | 19 083 (60 %) | 15 644 (61 %) |
| Jibril | 134 (29 %) | 133 (29 %) | 5 813 (18 %) | 4 993 (20 %) |
| Remy | 53 (11 %) | 53 (12 %) | 2 810 (9 %) | 1 802 (7 %) |
| Vaneck | 50 (11 %) | 50 (11 %) | 4 105 (13 %) | 3 133 (12 %) |
| Maïmouna | 24 (5 %) | 24 (5 %) | 0 (0 %) | 0 (0 %) |
| Total | 462 | 457 | 31 811 | 25 572 |

**Documentation.**

| Membre | Lignes de documentation ajoutées | Lignes de documentation conservées |
|---|---:|---:|
| Mahé | 15 616 (55 %) | 11 593 (62 %) |
| Jibril | 7 169 (25 %) | 4 809 (26 %) |
| Remy | 2 499 (9 %) | 592 (3 %) |
| Vaneck | 2 666 (9 %) | 1 720 (9 %) |
| Maïmouna | 202 (1 %) | 118 (1 %) |
| Total | 28 152 | 18 832 |

**Hors totaux, en volume brut.**

| Membre | Lignes ajoutées dans les carnets (JSON brut) | Lignes ajoutées dans les données et verrous |
|---|---:|---:|
| Mahé | 11 071 | 3 013 |
| Jibril | 0 | 6 989 |
| Remy | 0 | 13 |
| Vaneck | 0 | 4 324 |
| Maïmouna | 0 | 70 |
| Total | 11 071 | 14 409 |

## Comment lire ces chiffres

- **Un volume n'est pas une valeur.** Une ligne d'un script de mesure, une ligne d'une page de diapositives et une ligne de documentation ne se valent pas. Les pourcentages sont des parts de volume.
- **Le travail assisté par une IA est compté au membre qui commite.** Les cinq membres déclarent utiliser un assistant (journal d'usage de l'IA) ; cette mesure ne distingue pas les degrés d'assistance.
- **Le nombre de commits dépend de la taille que chacun leur donne.** Jibril a poussé 134 commits pour 5 813 lignes de code ajoutées, Vaneck 50 pour 4 105.
- **Une assignation n'est pas du travail fait.** 47 des 68 tickets assignés ont au moins deux responsables : le nombre de tickets assignés mesure la responsabilité attribuée. Les tickets touchés se rapprochent du travail effectué, mais ne couvrent que ceux dont un commit ou une PR cite le numéro ; une plage écrite « #91 à #95 » ne donne que ses deux bornes, la mesure peut donc sous-compter.
- **Ce que Git ne voit pas.** Les jugements humains du #52 et leurs grilles, qui sont hors dépôt (`data/`), les reproductions sur une machine (#51), l'annotation des questions autrement que par le fichier versionné, les réunions et les relectures faites hors GitHub. Les relectures de PR sont comptées à part. Le total de lignes de code de Maïmouna (0) ne dit rien de ce travail.
- **Un périmètre arrêté à un instant.** Relancé plus tard, le script comptera aussi les commits qui suivent le 26 novembre.

## Contrôles du relevé

- **Commits** : 462 commits uniques hors fusions ; recoupés par `git shortlog` sur les mêmes références, qui donne les mêmes totaux par membre (201, 134, 53, 50, 24) et la même somme.
- **Lignes ajoutées** : somme de toutes les catégories, 85 516, identique à celle du script de comptage utilisé le 16 novembre (non versionné), relancé sur les mêmes références avant le changement de catégories.
- **Lignes conservées** : 25 572 lignes de code et 18 832 de documentation, égales au comptage direct des lignes non vides de chaque fichier de `dev`, fait sans `blame` : aucune ligne n'est perdue ni attribuée deux fois.
- **Catégories** : la première version rangeait en code trois pages HTML de diapositives (3 380 lignes de Mahé) et en documentation les fichiers de dépendances ; l'examen des plus gros fichiers de chaque membre les a fait remonter. Les catégories ont été refaites, sans changer le total.
- **Identités** : une adresse inconnue arrête le script. Les adresses qui ne sont pas des adresses GitHub « noreply » se déclarent dans un fichier d'alias non versionné.

## Refaire le relevé

```
git fetch origin --prune --tags
git fetch origin '+refs/pull/*/head:refs/statpr/*'
python3 -I scripts/suivi/contributions.py --depot . --reference origin/dev --alias alias.json --csv contributions.csv --md contributions.md
git for-each-ref --format='%(refname)' refs/statpr | xargs -n1 git update-ref -d
```

Le script appelle `gh` pour les tickets et les PR : il faut être connecté (`gh auth status`).
