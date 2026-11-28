# Contributions mesurées, relevé du 26 novembre 2026

**Équipe** Data Tigers
**Relevé par** `scripts/suivi/contributions.py` (17 tests : `scripts/suivi/test_contributions.py`) ; données brutes : `docs/suivi/contributions_20261126.csv`
**Instant du relevé** 26 novembre 2026, 16 h 15 UTC (`--arret 2026-11-26T16:15:00Z`), après la fusion de la PR #187
**Référence figée** `ff21f4b`, le commit de `dev` après cette fusion

Le relevé n'a pas une seule source. Les lignes conservées et la colonne « dont dans la référence » viennent de `ff21f4b`. Les commits, les lignes ajoutées, les PR, les revues et les tickets viennent de toutes les branches, des tags et des têtes de PR du dépôt, et de l'API de GitHub, à l'instant du relevé. La section « Ce qui est figé » donne le détail.

## Pourquoi cette mesure

Le classeur de suivi contient des heures par membre et par ticket. Elles sont presque toutes des estimations rétrospectives, non chronométrées, établies par trois méthodes différentes : déclarations des intéressés, estimations proposées avec un assistant puis relues, estimations de Jibril divisées par deux à sa demande (`SUIVI.md`). Aucune charge n'a été inscrite pour Mahé. Elles ne permettent donc pas de comparer les membres. Le 26 novembre, Mahé a décidé de comparer les contributions sur des quantités comptées par GitHub et par Git : tickets, commits et lignes. Les heures restent dans `SUIVI.md`, à titre indicatif.

## Ce qui est compté

| Mesure | Définition |
|---|---|
| Tickets assignés | tickets dont le membre est l'un des responsables sur GitHub ; un ticket compte une fois pour chacun de ses responsables |
| dont terminés | parmi eux, les tickets fermés comme terminés (les tickets fermés sans suite ne comptent pas) |
| Tickets touchés | tickets cités par au moins un commit du membre, ou par une PR dont il est l'auteur (sujet, titre ou nom de branche) ; la citation peut être un simple contexte |
| Tickets créés | tickets dont le membre est l'auteur |
| PR fusionnées | PR dont le membre est l'auteur et que GitHub marque fusionnées |
| Revues déposées | revues déposées sur la PR d'un autre membre, de tout état ; plusieurs revues d'un même membre sur une même PR comptent chacune ; les commentaires d'un auteur sur sa propre PR et ceux des robots sont exclus |
| PR distinctes relues | nombre de PR d'un autre membre sur lesquelles le membre a déposé au moins une revue ; chaque PR compte une fois par membre |
| Commits poussés | commits uniques hors fusions, sur toutes les branches du dépôt GitHub, les tags et les têtes de PR (branches supprimées comprises) ; les commits qui ne sont pas sur GitHub ne comptent pas ; un commit compte pour son auteur, avec sa date de validation pour l'arrêt |
| Lignes ajoutées | cumul de `git log --numstat` (renommages détectés), par catégorie de fichier |
| Lignes conservées | lignes non vides encore présentes dans la référence, attribuées par `git blame -w -M -C` à l'auteur du commit qui les a introduites ; deux fichiers au contenu identique ne comptent qu'une fois |

Catégories de fichiers : le code (Python, JavaScript, JSX, CSS, HTML hors `docs/`, scripts shell, YAML), la documentation (Markdown, LaTeX, texte, et les pages HTML de `docs/`, qui sont des diapositives), les carnets Jupyter, les données et fichiers de verrouillage (JSON, CSV, SVG, `package-lock.json`, `requirements*.txt`). Les carnets, qui comptent leur JSON brut, sortie des cellules comprise, et les données ne sont pas comparés en lignes : ils sont donnés à part.

## Ce qui est figé, et ce qui ne l'est pas

| Mesure | Source | État |
|---|---|---|
| Lignes conservées, « dont dans la référence » | `git blame` et `git log` sur le commit `ff21f4b` | figé : un commit ne change pas |
| Commits, lignes ajoutées | toutes les branches, les tags et les têtes de PR du dépôt, filtrés par date de validation jusqu'à l'arrêt | rejouable tant que les commits restent dans le dépôt ; une branche supprimée sans PR, ou réécrite de force après le relevé, ne se retrouverait pas |
| PR fusionnées, revues déposées, tickets créés et fermés | API de GitHub, filtrée par `createdAt`, `mergedAt`, `submittedAt` et `closedAt` jusqu'à l'arrêt | rejouable : GitHub conserve ces dates |
| Tickets assignés, nom des branches | API de GitHub, état au moment de l'appel | non historisé : une assignation modifiée depuis le 26 novembre changerait le relevé |

Le CSV est la trace du relevé du 26 novembre. Le script permet de le rejouer ; relancé sans `--arret`, il mesure l'état du jour, et ses valeurs diffèrent (voir « Contrôles du relevé »).

## Résultats

**Tickets et pull requests.**

| Membre | Tickets assignés | dont terminés | Tickets touchés | Tickets créés | PR fusionnées | Revues déposées | PR distinctes relues |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mahé | 52 (26 %) | 38 (29 %) | 36 (48 %) | 37 (54 %) | 58 (51 %) | 73 (39 %) | 48 (36 %) |
| Jibril | 44 (22 %) | 28 (21 %) | 17 (23 %) | 32 (46 %) | 24 (21 %) | 48 (26 %) | 29 (22 %) |
| Remy | 36 (18 %) | 25 (19 %) | 8 (11 %) | 0 (0 %) | 11 (10 %) | 31 (17 %) | 25 (19 %) |
| Vaneck | 33 (17 %) | 21 (16 %) | 10 (13 %) | 0 (0 %) | 15 (13 %) | 21 (11 %) | 18 (14 %) |
| Maïmouna | 32 (16 %) | 20 (15 %) | 4 (5 %) | 0 (0 %) | 5 (4 %) | 13 (7 %) | 12 (9 %) |
| Total | 197 | 132 | 75 | 69 | 113 | 186 | 132 |

Le total des PR distinctes relues est la somme des membres : une PR relue par deux membres compte deux fois.

**Commits et lignes de code.**

| Membre | Commits poussés | dont dans la référence | Lignes de code ajoutées | Lignes de code conservées |
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
- **L'attribution est celle de Git.** Un commit est attribué à son auteur, une ligne conservée à l'auteur du commit qui l'a introduite. Cela ne dit pas qui a conçu ou écrit la ligne : une reprise, une collaboration à deux ou une génération par un assistant sont comptées au membre dont le nom figure sur le commit. Les cinq membres déclarent utiliser un assistant (journal d'usage de l'IA) ; la mesure ne distingue pas les degrés d'assistance.
- **Le nombre de commits dépend de la taille que chacun leur donne.** Jibril a poussé 134 commits pour 5 813 lignes de code ajoutées, Vaneck 50 pour 4 105.
- **Une assignation n'est pas du travail fait.** 47 des 68 tickets assignés ont au moins deux responsables : le nombre de tickets assignés mesure la responsabilité attribuée.
- **Les tickets touchés peuvent se tromper dans les deux sens.** Ils sous-comptent quand le numéro n'est pas cité : une plage écrite « #91 à #95 » ne donne que ses deux bornes. Ils sur-comptent quand le numéro est cité comme contexte, sans que l'auteur ait travaillé sur ce ticket.
- **Une revue déposée n'est pas une PR relue.** Plusieurs revues d'un même membre sur une même PR comptent chacune : Mahé a déposé 73 revues sur 48 PR distinctes, Jibril 48 sur 29, Remy 31 sur 25, Vaneck 21 sur 18, Maïmouna 13 sur 12. Les deux colonnes sont données, et le classement ne change pas. Ni l'une ni l'autre ne mesure la qualité d'une relecture.
- **Ce que Git ne voit pas.** Les jugements humains du #52 et leurs grilles, qui sont hors dépôt (`data/`), les reproductions sur une machine (#51), l'annotation des questions autrement que par le fichier versionné, les réunions et les relectures faites hors GitHub. Le total de lignes de code de Maïmouna (0) ne dit rien de ce travail.
- **Un instant, pas un état permanent.** Relancé sans `--arret`, le script compte aussi ce qui suit le 26 novembre.

## Contrôles du relevé

- **Commits** : 462 commits uniques hors fusions ; recoupés par `git shortlog` sur les mêmes références, qui donne les mêmes totaux par membre (201, 134, 53, 50, 24) et la même somme.
- **Lignes ajoutées** : somme de toutes les catégories, 85 516, identique à celle du script de comptage utilisé le 16 novembre (non versionné), relancé sur les mêmes références avant le changement de catégories.
- **Lignes conservées** : 25 572 lignes de code et 18 832 de documentation, égales au comptage direct des lignes non vides de chaque fichier de `dev`, fait sans `blame` : aucune ligne n'est perdue ni attribuée deux fois.
- **Catégories** : la première version rangeait en code trois pages HTML de diapositives (3 380 lignes de Mahé) et en documentation les fichiers de dépendances ; l'examen des plus gros fichiers de chaque membre les a fait remonter. Les catégories ont été refaites, sans changer le total.
- **Identités** : une adresse inconnue arrête le script. Les adresses qui ne sont pas des adresses GitHub « noreply » se déclarent dans un fichier d'alias non versionné.
- **Reproduction, le 27 novembre** : le relevé a été rejoué avec `--reference ff21f4b --arret 2026-11-26T16:15:00Z`. Les 20 colonnes du CSV du 26 novembre sont retrouvées sans aucun écart, sur les cinq membres et le total ; il en est de même aux arrêts essayés à 16 h 13 et à 16 h 19 UTC. La fenêtre se termine à la fusion de `dev` dans la branche de la PR #188, datée de 16 h 19 UTC, qui ajoute une fusion au décompte de Mahé. Les responsables des tickets n'étant pas historisés, ce contrôle suppose qu'aucune assignation n'a changé depuis.
- **Sans arrêt, le résultat change** : relancé le 27 novembre sans `--arret`, le même script donne 175 tickets terminés au lieu de 132 (13 tickets fermés le 26 novembre entre 19 h 19 et 19 h 26 UTC, après le relevé), 465 commits au lieu de 462 et 59 PR fusionnées de Mahé au lieu de 58 (la #177). C'est pourquoi le CSV et l'instant du relevé font foi.

## Refaire le relevé

```
git fetch origin --prune --tags
git fetch origin '+refs/pull/*/head:refs/statpr/*'
python3 -I scripts/suivi/contributions.py --depot . --reference ff21f4b --arret 2026-11-26T16:15:00Z --alias alias.json --csv contributions.csv --md contributions.md
git for-each-ref --format='%(refname)' refs/statpr | xargs -n1 git update-ref -d
```

- Cette commande rejoue le relevé du 26 novembre. Pour un relevé à une autre date, changer `--reference` (un commit de `dev` ou un tag) et `--arret` (instant en UTC) ; sans `--arret`, c'est l'état du jour.
- Le script appelle `gh` pour les tickets et les PR : il faut être connecté (`gh auth status`).
