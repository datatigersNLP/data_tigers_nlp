# Support de la soutenance de 8 minutes

**Établi le** 21 novembre 2026 par Mahé BEGNIS, après le nouveau format annoncé par l'enseignant : 8 minutes de présentation, sans pitch, puis environ 5 minutes de questions. **Complété le** 26 novembre : annexes, script oral, questions et réponses préparées.

**Fichier à projeter** : `../presentation_8min.html`. Il fonctionne hors ligne et ne charge aucune ressource extérieure : police, logo et données sont embarqués.

## Utilisation

- **Navigation** :
  - flèche droite, espace ou clic dans les deux tiers droits : étape suivante ;
  - flèche gauche ou clic à gauche : étape précédente ;
  - Origine : première diapositive ; Fin ou M : diapositive de fin (« Merci ») ;
  - A : sommaire des annexes, dont chaque titre ouvre l'annexe.
- **Notes de l'orateur** : la touche N affiche le texte à dire et la durée prévue de la diapositive. Un chronomètre démarre au premier appui ; la touche R le remet à zéro.
- **Plein écran** : touche F.
- **Reprendre à une étape** : ouvrir `presentation_8min.html#7.3` (diapositive 7, étape 3).
- **Durée prévue** : 7 min 55 au total, pour 1 062 mots à dire (134 mots par minute). La barre du bas a un segment par diapositive, de longueur proportionnelle à sa durée.
- **Annexes** : 17 diapositives après « Merci », hors des 8 minutes, de la barre et du numéro (« A3 / 17 ») ; leurs notes donnent la réponse type.
- **Notes** : elles s'affichent sur la page projetée ; ne les ouvrir qu'en répétition, ou avec un second écran qui ne recopie pas le premier.
- **Mouvement réduit** : si le système le demande, chaque étape s'affiche sans animation.

## Contenu

| Diapositive | Sujet | Durée |
|---|---|---:|
| 1 | Couverture | 20 s |
| 2 | La question de départ et les deux volets | 40 s |
| 3 | La préparation commune : découpage, encodage, index | 35 s |
| 4 | Volet A : la recherche dans le navigateur | 45 s |
| 5 | Choix : ajuster l'encodeur | 50 s |
| 6 | Volet B : l'assistant qui cite ses sources | 40 s |
| 7 | Choix : la recherche hybride et le reclasseur | 60 s |
| 8 | Choix : 10 passages plutôt que 5 | 35 s |
| 9 | Choix : les trois modèles | 45 s |
| 10 | Choix : les données synthétiques | 50 s |
| 11 | Bilan : des règles écrites avant de mesurer | 45 s |
| 12 | Questions | 10 s |

**Annexes** : A1 démonstration du volet A en ligne ; A2 démonstration du volet B en direct ; A3 mesure de bout en bout ; A4 exactitude jugée à l'aveugle ; A5 encodeurs synthétiques ; A6 seuils d'abstention ; A7 tests statistiques ; A8 protocole du volet B ; A9 données d'adaptation ; A10 quantification et export ; A11 mesure corrigée ; A12 confidentialité ; A13 machines ; A14 organisation et usage de l'IA ; A15 cinq outils ; A16 Agent0 ; A17 glossaire. Les questions de démonstration (A1, A2) ont été essayées le 26 novembre, sur le site en ligne et sur l'assistant local.

**Pour la soutenance** :
- `script_oral.md` : le texte exact à dire, diapositive par diapositive, avec le minutage, l'ordre des apparitions et une répartition proposée des orateurs ; généré depuis les notes du support par `script_oral.py`, il ne peut pas en diverger.
- `questions_reponses.md` : 43 questions probables du jury, avec une réponse courte, chiffrée et sourcée.

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
python3 docs/soutenance/8min/verifier_chiffres.py   # 61 chiffres contre leurs sources ; aucun tiret long
python3 docs/soutenance/8min/script_oral.py         # régénère script_oral.md depuis les notes du support
```

`verifier_chiffres.py` relit les fichiers de résultats dans `data/` (option `--donnees`, par défaut la copie de mesure `~/NLP2_local/depot_v2/data`) et les documents publiés sur `dev`.

**Limite du vérificateur** : il contrôle qu'un chiffre écrit correspond à sa source et figure dans le support, pas chaque occurrence. Un chiffre répété (86,0 % apparaît deux fois) n'est donc vérifié qu'une fois. Le contrôle négatif du 21/11 a détecté une altération d'un chiffre unique (+28,9 points).

## Contrôles faits le 21/11, dans Chromium à 1920 x 1080

- Aucune erreur JavaScript, et aucun contenu ne dépasse la zone utile, sur les 12 diapositives.
- 42 appuis mènent de la première à la dernière diapositive : 11 changements de diapositive et 31 étapes.
- Le reclassement de la diapositive 7 et le nuage de la diapositive 5 s'animent en avant comme en arrière.
- Les contrastes du texte sont d'au moins 4,5:1 ; l'orange, réservé au texte grand ou gras, est d'au moins 3,5:1.
- Ouvert en fichier local, le support fonctionne, mais l'adresse ne garde pas l'étape (le navigateur l'interdit dans ce cas).

## Fichiers

- `deck.html` : gabarit (styles, diapositives, notes, moteur de navigation).
- `donnees.json` : données réelles des schémas.
- `logo-tigre.svg` : copie du logo de l'équipe (`docs/charte/logo/`, PR #177).
- `polices/` : DM Sans 5.3.0 (la police du site du volet A), sous licence SIL OFL 1.1.
- `construire.py`, `verifier_chiffres.py` : construction et vérification.
