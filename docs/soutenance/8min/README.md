# Support de la soutenance de 8 minutes

**Établi le** 21 novembre 2026 par Mahé BEGNIS, après le nouveau format annoncé par l'enseignant : 8 minutes de présentation, sans pitch, puis environ 5 minutes de questions. **Complété le** 26 novembre : annexes, script oral, questions et réponses préparées. **Mis à jour le** 27 novembre : vidéo de secours du volet A, contrôle du site déployé après la #177, répartition mesurée des contributions, 44 questions. **Le 28 novembre** : script oral et questions en PDF LaTeX, PDF de secours du support, puis **nouveau format** : l'enseignant préfère la démonstration à la présentation, qui dure 8 minutes au plus **démonstrations comprises**. Le support garde ses neuf premières diapositives, sans changement, dites plus vite (4 min 11) ; les diapositives 10 à 12 sont supprimées ; les démonstrations en direct du volet A et du volet B (3 min 15) et une clôture de 10 s remplacent la fin. Durée prévue : 7 min 36, marge de 24 s.

**Fichier à projeter** : `../presentation_8min.html`. Il fonctionne hors ligne et ne charge aucune ressource extérieure : police, logo et données sont embarqués.

## Utilisation

- **Navigation** :
  - flèche droite, espace ou clic dans les deux tiers droits : étape suivante ;
  - flèche gauche ou clic à gauche : étape précédente ;
  - Origine : première diapositive ; Fin ou M : dernière diapositive ;
  - A : sommaire des annexes, dont chaque titre ouvre l'annexe.
- **Notes de l'orateur** : la touche N affiche le texte à dire et la durée prévue de la diapositive. Un chronomètre démarre au premier appui ; la touche R le remet à zéro.
- **Plein écran** : touche F.
- **Reprendre à une étape** : ouvrir `presentation_8min.html#7.3` (diapositive 7, étape 3).
- **Durée prévue** : 7 min 36 au total sur 8 minutes au plus : 4 min 11 pour les neuf diapositives (539 mots, 129 mots par minute), 1 min 25 de démonstration du volet A, 1 min 50 de démonstration du volet B, 10 s de clôture. La barre du bas a un segment par diapositive, de longueur proportionnelle à sa durée ; elle ne compte pas les démonstrations, dont la durée figure dans les notes (touche N) et dans le chronomètre.
- **Annexes** : 17 diapositives après la dernière, hors de la barre et du numéro (« A3 / 17 ») ; leurs notes donnent la réponse type. Les annexes A1 et A2 sont les démonstrations en direct : leur texte est public, leurs notes contiennent le texte à dire, et leur durée compte dans les 8 minutes.
- **Notes** : elles s'affichent sur la page projetée ; ne les ouvrir qu'en répétition, ou avec un second écran qui ne recopie pas le premier.
- **Mouvement réduit** : si le système le demande, chaque étape s'affiche sans animation.

## Contenu

| Partie | Sujet | Durée |
|---|---|---:|
| Diapositive 1 | Couverture | 12 s |
| Diapositive 2 | La question de départ et les deux volets | 34 s |
| Diapositive 3 | La préparation commune : découpage, encodage, index | 21 s |
| Diapositive 4 | Volet A : la recherche dans le navigateur | 29 s |
| Diapositive 5 | Choix : ajuster l'encodeur | 33 s |
| Diapositive 6 | Volet B : l'assistant qui cite ses sources | 26 s |
| Diapositive 7 | Choix : la recherche hybride et le reclasseur | 37 s |
| Diapositive 8 | Choix : 10 passages plutôt que 5 | 19 s |
| Diapositive 9 | Choix : les trois modèles, avec le résultat avant et après adaptation | 40 s |
| Annexe A1 | Démonstration du volet A, en ligne | 85 s |
| Annexe A2 | Démonstration du volet B, en direct | 110 s |
| Clôture | Remerciement et questions | 10 s |

Les anciennes diapositives 10 (données synthétiques), 11 (bilan) et 12 (questions) sont supprimées depuis le 28 novembre : leur contenu reste dans les annexes A3, A5, A9 et A11, le résultat avant et après adaptation est dit et affiché à la diapositive 9 (bandeau « 10,1 % puis 52,9 % », quatrième appui).

**Annexes** : A1 démonstration du volet A en ligne ; A2 démonstration du volet B en direct ; A3 mesure de bout en bout ; A4 exactitude jugée à l'aveugle ; A5 encodeurs synthétiques ; A6 seuils d'abstention ; A7 tests statistiques ; A8 protocole du volet B ; A9 données d'adaptation ; A10 quantification et export ; A11 mesure corrigée ; A12 confidentialité ; A13 machines ; A14 organisation et usage de l'IA ; A15 cinq outils ; A16 Agent0 ; A17 glossaire. Les questions de démonstration (A1, A2) ont été essayées le 26 novembre, sur le site en ligne et sur l'assistant local.

**Pour la soutenance** :
- `script_oral.md` : le texte exact à dire, diapositive par diapositive, avec le minutage, l'ordre des apparitions et la répartition des orateurs retenue le 28/11 ; généré depuis les notes du support par `script_oral.py`, il ne peut pas en diverger. Version imprimable : `script_oral.pdf`.
- `questions_reponses.md` : 44 questions probables du jury, avec une réponse courte, chiffrée et sourcée. Version imprimable : `questions_reponses.pdf`.
- `../presentation_8min.pdf` : PDF de secours du support, une page par appui comme à l'écran (les 9 diapositives pas à pas, le sommaire des annexes et les 17 annexes), à ouvrir en plein écran si le navigateur ne peut pas afficher le HTML. Les notes de l'orateur n'y figurent pas : elles sont dans le script.

## Des schémas animés construits sur des données réelles

Ces données sont calculées le 21/11/2026 sur les données du projet et versionnées dans `donnees.json`.

- **Diapositive 4** : la question « Combien de jours de congés payés par an ? », une des questions d'exemple du site.
  - ses vrais tokens, découpés par le tokeniseur du modèle servi ;
  - son vrai vecteur de 384 nombres, calculé par l'encodeur ajusté q8 servi ;
  - ses 4 240 scores de similarité, un pixel par passage ;
  - ses 10 passages les plus proches.
- **Diapositive 7** : la question V056 du jeu v2.
  - Son passage pertinent, la fiche « Le congé sans solde », est 59e pour la recherche dense, 2e pour BM25, 6e après la fusion des rangs et 1er après le reclasseur. Le reclasseur lui donne 0,66, contre 0,09 au passage suivant.
  - Les rangs, les fiches et les scores sont ceux des listes réelles de la récupération R1, avec le cache du reclasseur de la famille B du protocole 10.
- **Diapositive 5** : un schéma. Le nuage de points illustre l'apprentissage contrastif et n'est pas une projection réelle ; les notes le disent.
- **Diapositive 8** : les barres reprennent les chiffres de `docs/etudes/evaluation/10_resultats.md` (PR #174), section 8.

## Reconstruire et vérifier

Depuis la racine du dépôt :

```
python3 docs/soutenance/8min/construire.py          # écrit docs/soutenance/presentation_8min.html
python3 docs/soutenance/8min/verifier_chiffres.py   # 57 chiffres contre leurs sources, et ceux de la diapositive 9 à l'écran ; aucun tiret long
python3 docs/soutenance/8min/script_oral.py         # régénère script_oral.md depuis les notes du support
```

Les PDF :

```
python3 docs/latex/build.py docs/soutenance/8min/script_oral.md
(cd docs/soutenance/8min && latexmk -xelatex -interaction=nonstopmode -halt-on-error script_oral.tex)     # idem pour questions_reponses
PLAYWRIGHT_CORE=<chemin de playwright-core> node docs/soutenance/8min/exporter_pdf.js docs/soutenance/presentation_8min.html docs/soutenance/presentation_8min.pdf
```

Supprimer ensuite les `.tex` intermédiaires : seuls le Markdown et le PDF sont versionnés. Contrôler dans le journal de compilation (`^! `, `Overfull`, `Underfull`, `Missing character`) qu'il n'y a rien. L'export du support exige `playwright-core` 1.60.0 avec son Chromium et `pdfunite` ; il refuse toute requête hors du fichier local.

`verifier_chiffres.py` relit les fichiers de résultats dans `data/` (option `--donnees`, par défaut la copie de mesure `~/NLP2_local/depot_v2/data`) et les documents publiés sur `dev`.

**Limite du vérificateur** : il contrôle qu'un chiffre écrit correspond à sa source et figure dans le support, pas chaque occurrence ; seuls les chiffres de la diapositive 9 sont aussi contrôlés à l'écran, hors notes. Le contrôle de chaque chiffre du texte à dire contre l'écran rendu (schémas calculés compris) a été fait le 28/11 dans Chromium. Un chiffre répété (86,0 % apparaît deux fois) n'est donc vérifié qu'une fois. Le contrôle négatif du 21/11 a détecté une altération d'un chiffre unique (+28,9 points).

## Contrôles faits le 21/11 puis le 28/11, dans Chromium à 1920 x 1080

- Aucune erreur JavaScript, et aucun contenu ne dépasse la zone utile, sur les 9 diapositives et les 18 annexes (28/11).
- 35 appuis mènent de la première à la dernière diapositive : 8 changements de diapositive et 27 étapes.
- Le reclassement de la diapositive 7 et le nuage de la diapositive 5 s'animent en avant comme en arrière.
- Les contrastes du texte sont d'au moins 4,5:1 ; l'orange, réservé au texte grand ou gras, est d'au moins 3,5:1.
- Ouvert en fichier local, le support fonctionne, mais l'adresse ne garde pas l'étape (le navigateur l'interdit dans ce cas).

## Fichiers

- `deck.html` : gabarit (styles, diapositives, notes, moteur de navigation).
- `donnees.json` : données réelles des schémas.
- `logo-tigre.svg` : copie du logo de l'équipe (`docs/charte/logo/`, PR #177).
- `polices/` : DM Sans 5.3.0 (la police du site du volet A), sous licence SIL OFL 1.1.
- `construire.py`, `verifier_chiffres.py` : construction et vérification.
