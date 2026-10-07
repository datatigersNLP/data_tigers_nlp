# Suivi des outils novateurs

Ticket #25. Le sujet accorde jusqu'à trois points bonus pour une analyse substantielle de **cinq outils
novateurs réellement employés** pendant le projet. Une liste ou une reprise de la documentation officielle n'a
aucune valeur : ce qui compte, ce sont les observations faites au moment de l'usage, difficultés et échecs
compris. Ce fichier présente la méthode et le tableau de suivi ; chaque outil a sa fiche dans
`docs/suivi/outils/`.

Méthode, répartition et calendrier validés par l'équipe en Weekly 4 (7 octobre 2026).

## Organisation

```
docs/suivi/
  OUTILS_NOVATEURS.md        méthode, règles, calendrier et tableau de suivi (ce fichier)
  outils/
    MODELE_FICHE.md          modèle vide, à copier pour un nouvel outil
    <outil>.md               une fiche par outil
```

Une fiche par fichier : chacun écrit dans la fiche des outils qui lui sont assignés, et les fusions se font
sans conflit tant que deux personnes ne modifient pas les mêmes lignes.

**Répartition.** Un outil est assigné à **tout membre qui l'a déjà utilisé ou qui sera amené à l'utiliser**
pour un ticket. Chaque fiche a aussi un ou deux **coordinateurs**, les référents validés en Weekly : ils
veillent à ce qu'elle soit complète et la relisent avant chaque pull request. Les outils utilisés par tous
sont assignés et coordonnés par toute l'équipe.

## Règles à respecter

### Contenu des fiches

1. **Un outil n'entre au tableau que s'il a été réellement utilisé** pour une tâche du projet. Un outil
   seulement évoqué ou installé n'est jamais présenté comme testé.
2. **Écrire au moment de l'usage**, tant que les difficultés sont encore en mémoire.
3. **Chaque observation est signée et prouvée** : prénom de l'auteur entre parenthèses, et renvoi à une
   preuve (ticket, pull request, commit, commande, mesure ou capture). Par exemple :
   `- (Vaneck) Sans le bon chemin de base, la page reste blanche une fois en ligne (#29).`
4. **On ajoute, on ne réécrit pas** les observations des autres. Un désaccord s'ajoute en nouvelle ligne.
5. **Les échecs et les abandons sont conservés**, jamais supprimés : la décision passe à « abandonné », avec le
   motif. Ce sont souvent les retours les plus instructifs.
6. **Comparer à la méthode utilisée auparavant** lorsque c'est pertinent.
7. **Pas de doublon** : deux outils presque identiques ne font pas deux retours si les observations sont les
   mêmes.

### Travail avec Git

1. **Mettre sa branche à jour avant d'écrire** : `git pull origin dev`.
2. **Écrire sur la branche du ticket** où l'outil a servi, ou sur une branche dédiée
   `docs/25-fiche-<outil>`, jamais sur `main` ni directement sur `dev`.
3. **Petites pull requests fréquentes vers `dev`**, relues par un autre membre avant la fusion.
4. **Le tableau de suivi ci-dessous ne change que si la décision ou les assignés changent**, pour limiter les
   modifications simultanées de ce fichier commun.
5. **Deux personnes sur la même fiche se préviennent** avant de la modifier.
6. **En cas de conflit**, garder les deux contributions : chacun n'a ajouté que ses propres lignes.

### Différence avec le journal d'usage de l'IA

Le journal (`docs/journal/JOURNAL_USAGE_IA.md`) consigne chaque usage d'un assistant d'IA, session par session,
pour la traçabilité exigée par le sujet. Les fiches évaluent un outil dans la durée : mise en place, qualités,
défauts, décision. La fiche des assistants d'IA renvoie au journal sans le dupliquer.

## Calendrier

| Étape | Moment |
|---|---|
| Revue courte du tableau, une phrase par outil | à chaque Weekly, cinq minutes au plus |
| Présélection des cinq outils | Weekly 8 (4 novembre), avant le jalon J3 |
| Fiches des cinq outils finalisées | avant la rédaction du rapport final |

**Critères de sélection** : un usage réel et répété, des preuves disponibles, au moins une difficulté ou une
limite observée, et un retour qui dit quelque chose que la documentation officielle ne dit pas.

## Tableau de suivi

Assignés : déjà utilisateurs, puis utilisateurs prévus avec le ticket concerné. Coordination : référents validés en Weekly.

| Outil | Fiche | Assignés | Coordination | Intérêt du retour | Décision |
|---|---|---|---|---|---|
| GitHub CLI (`gh`) | [github-cli.md](outils/github-cli.md) | toute l'équipe | toute l'équipe | élevé : pièges d'API et de droits observés | adopté |
| Assistants de développement IA | [assistants-ia.md](outils/assistants-ia.md) | toute l'équipe | toute l'équipe | à évaluer | à compléter |
| GitHub Actions et Pages | [github-actions-pages.md](outils/github-actions-pages.md) | Vaneck ; prévus : Maïmouna, Mahé, Rémy (#48), Jibril (#53) | Vaneck | moyen : chemin de base et droits de l'environnement | adopté |
| Vite (avec React et Tailwind CSS) | [vite.md](outils/vite.md) | Vaneck, Maïmouna ; prévus : Mahé, Rémy (#48), Jibril (#53) | Vaneck, Jibril | moyen : chemin de base et page blanche | adopté |
| Playwright | [playwright.md](outils/playwright.md) | Mahé ; prévus : Vaneck, Jibril (#53) | Vaneck, Jibril | à évaluer | à compléter |
| Transformers.js | [transformers-js.md](outils/transformers-js.md) | Mahé ; prévus : Vaneck, Maïmouna, Rémy (#48) | à désigner | élevé : écart entre navigateur et Python mesuré | à compléter |
| ONNX Runtime (Python et Web) | [onnx-runtime.md](outils/onnx-runtime.md) | Mahé, Rémy ; prévus : Jibril (#49) | Mahé | élevé : critère de parité échoué puis diagnostiqué | à compléter |
| `uv` | [uv.md](outils/uv.md) | Mahé, Vaneck ; prévu : Rémy (#46, #47) | Mahé | moyen : reproductibilité entre Windows et macOS | à compléter |
| Ollama | [ollama.md](outils/ollama.md) | Jibril, Rémy ; prévus : Maïmouna (#51), Mahé (#52) | Jibril | élevé : échec d'import contourné | à compléter |
| Sentence Transformers | [sentence-transformers.md](outils/sentence-transformers.md) | Rémy ; prévus : Mahé, Jibril (#49) | Rémy | élevé : mesure avant et après ajustement | à compléter |

Pour ajouter un outil : copier [MODELE_FICHE.md](outils/MODELE_FICHE.md) sous `outils/<outil>.md`, le remplir
dès le premier usage, puis ajouter sa ligne au tableau dans la même pull request.
