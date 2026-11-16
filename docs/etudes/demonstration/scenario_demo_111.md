# Scénario de la démonstration du volet B (issue #111)

Responsable : Vaneck DAGAR. Soutien : Maïmouna SIGNATE. Modèles et essai : Mahé BEGNIS. Machine de la démonstration : le Legion de Jibril BENSALEM.

**Statut** proposé le 14 novembre 2026, revu le 16 novembre après la relecture de Mahé et l'essai de bout en bout fait sur son Mac (PR #170). Les réponses restent à confirmer pendant la répétition sur le Legion. La vidéo de secours est prévue le 18 novembre.

## 1. Objet

Montrer en 2 min 40 l'assistant réglementaire local du volet B (cas B1) :
- une réponse citée, dont la référence ouvre son passage ;
- une abstention sur une question hors corpus ;
- la même question posée au témoin T, puis au modèle adapté (#107).

Le sujet prévoit environ 4 minutes de démonstration pour les deux volets : le volet A en ligne (environ 1 min 10), puis le volet B en local. Il n'y a ni introduction ni conclusion : la présentation qui suit porte les résultats (#114). La vidéo de secours tient dans la même durée.

Ce scénario sert de script pour la vidéo et pour la démonstration en soutenance. Ce n'est pas une mesure : les résultats mesurés sont ceux du protocole 06 (#52).

## 2. Préparation

La procédure complète est dans `docs/etudes/demonstration/demo_legion_111.md` (PR #170) : transfert des deux modèles, contrôle des empreintes, création des modèles dans Ollama, construction de l'interface. L'essentiel pour le scénario :

- **Deux couches en même temps**, dans deux fenêtres PowerShell : le modèle adapté sur le port 8765, T sur le port 8766. On passe d'un modèle à l'autre en changeant d'onglet, sans relancer de couche en direct.

  ```powershell
  .venv\Scripts\python.exe scripts\rag\serveur_demo.py --modele qwen2.5-7b-instruct:lora-v2b-q4_k_m-local --digest 18cb25f099f2ba1b21a3bc945da6be7ce4d128cb4e579325fc0f70dfccb37174
  .venv\Scripts\python.exe scripts\rag\serveur_demo.py --port 8766 --modele qwen2.5-7b-instruct:temoin-q4_k_m-local --digest 8a077f3d3f56b636face1357eba557b21e2ba68bc72ee81e48b377272da72f27
  ```

- **Deux onglets** : http://127.0.0.1:8765/ (adapté) et http://127.0.0.1:8766/ (T). Chacun doit afficher « L'assistant est prêt. ».
- **Mise en route** : poser une question d'échauffement dans chaque onglet peu avant de commencer, en finissant par le modèle adapté.
- **Mémoire du GPU** : avec 8 Gio, le Legion ne garde sans doute qu'un modèle à la fois. La première question après un changement de modèle inclut alors le chargement, environ 20 s d'après la #31. Au moment 4, cela peut arriver deux fois. À vérifier en répétition avec `ollama ps` ; si c'est le cas, parler pendant le chargement (texte prévu au moment 4).

## 3. Déroulé et minutage

Dans la vidéo, les temps d'attente de la génération sont coupés au montage. L'interface affiche sous chaque réponse le modèle qui l'a rédigée et sa durée réelle : la coupe ne cache donc rien.

| Temps | Moment | Onglet | Ce qu'on montre |
|---|---|---|---|
| 0:00 à 0:50 | 1. Question directe | adapté (8765) | une réponse citée, et le clic sur `[P1]` qui ouvre le passage |
| 0:50 à 1:30 | 3. Hors corpus | adapté (8765) | l'encadré d'abstention et les passages consultés |
| 1:30 à 2:40 | 4. T puis adapté | T (8766), puis adapté (8765) | la même question, et la différence entre les deux réponses |
| s'il reste du temps | 2. Réserve | adapté (8765) | une question à deux volets |

La numérotation des moments est gardée pour rester alignée avec la PR #170 et la diapositive Démonstration.

## 4. Détail des moments

### Moment 1 : question directe

- **Question** : « Quelle est la durée maximale de la période d'essai d'un cadre en CDI ? »
- **Attendu** : une réponse citée `[P1]`. Le passage P1 (fiche « La période d'essai ») donne « quatre mois pour les cadres ».
- **À montrer** : cliquer sur `[P1]`, qui amène la carte du passage avec sa fiche, sa section et son lien.
- **À dire** : « L'assistant tourne entièrement sur cet ordinateur. Il récupère d'abord les cinq passages des fiches du ministère du Travail les plus proches de la question, puis le modèle rédige sa réponse à partir de ces seuls passages, en les citant. »
- **À savoir** : le modèle adapté répond très court, parfois par un simple fragment. À l'essai, sa réponse commençait par un tiret, que l'interface affiche comme une liste d'un élément.

### Moment 3 : question hors corpus

- **Question** : « Comment est calculée la pension de retraite d'un fonctionnaire ? »
- **Attendu** : l'abstention. Aucun des cinq passages renvoyés ne traite de la retraite des fonctionnaires.
- **À montrer** : l'encadré d'abstention, puis le bouton « Afficher les 5 passages consultés », pour montrer qu'ils ne répondent pas.
- **À dire** : « Le corpus ne traite pas de ce sujet. Plutôt que de répondre de mémoire, le modèle s'abstient. L'interface ne prétend pas savoir pourquoi : on peut ouvrir les passages pour le vérifier. »

### Moment 4 : la même question, à T puis au modèle adapté

- **Question** : « Ma période d'essai peut-elle être renouvelée ? »
- **Déroulé** : poser la question dans l'onglet de T (8766), puis la même dans l'onglet du modèle adapté (8765).
- **Attendu, d'après l'essai du 16 novembre** : T s'abstient, alors que la réponse est dans les passages ; le modèle adapté répond « une fois si un accord de branche étendu le prévoit », en citant `[P2]`.
- **À dire** : « T est le modèle d'origine, passé par la même chaîne d'export que le modèle adapté. Ici, il s'abstient alors que le passage P2 contient la réponse : c'est le défaut que visait l'adaptation. Le modèle adapté répond, en citant ce passage. Cette question a été choisie après essai : c'est une illustration, pas une mesure. »
- **Si un chargement a lieu** : « Le modèle se charge en mémoire du GPU, ce qui prend une vingtaine de secondes la première fois. »
- **Question de rechange** : « Combien d'heures puis-je travailler au maximum sur une semaine ? » (à l'essai : T s'abstient, le modèle adapté répond « 48 heures par semaine » en citant `[P2]`).

### Moment 2, en réserve : question à deux volets

- **Question** : « Je suis en arrêt maladie : mon employeur peut-il me licencier, et suis-je payé pendant l'arrêt ? »
- **Attendu au départ** : une réponse qui cite deux passages de la fiche « Les absences liées à la maladie ou à l'accident non professionnel », P2 pour l'indemnisation et P3 pour le licenciement.
- **Obtenu à l'essai** : une seule citation, `[P3]`, sur le licenciement ; la rémunération n'est pas traitée. À ne jouer que s'il reste du temps, en le disant : « La question a deux volets ; le modèle n'en traite qu'un. Les deux passages consultés montrent que l'information sur l'indemnisation était disponible. »

## 5. Les quatre questions candidates du moment 4

Résultats de l'essai du 16 novembre sur le Mac de Mahé (PR #170), même code, mêmes modèles et mêmes digests que sur le Legion. Sur le GPU du Legion, les textes peuvent différer légèrement.

| Question | Où est la réponse | T | Modèle adapté | Décision |
|---|---|---|---|---|
| « Ma période d'essai peut-elle être renouvelée ? » | P2 : « une fois si un accord de branche étendu le prévoit » | abstention | réponse citée `[P2]` | **retenue** |
| « Combien d'heures puis-je travailler au maximum sur une semaine ? » | P2 : « 48 heures par semaine », et 44 heures en moyenne sur 12 semaines | abstention | « 48 heures par semaine » `[P2]` | rechange |
| « Quelle est la durée minimale du repos entre deux journées de travail ? » | P1 : « 11 heures consécutives » | réponse citée `[P1][P2]` | réponse citée `[P1][P2]` | écartée : aucune différence |
| « Un apprenti mineur a-t-il le droit de travailler la nuit ? » | P2 : interdiction selon l'âge ; P1 et P3 : dérogations | réponse plus complète `[P1]` | réponse partielle `[P2]` | écartée : le modèle adapté fait moins bien |

## 6. Choix des questions

- **Origine** : les questions ont été écrites pour la démonstration. Aucune ne figure dans le jeu de test `jeu-questions-v1`.
- **Vérification** : pour chacune, les cinq passages renvoyés par la récupération de la #85 (E5 de base en fp32, index `front/public/index/`) ont été lus le 14 novembre, sur la machine de Vaneck. Les réponses des modèles ont été obtenues lors de l'essai de Mahé, le 16 novembre.
- **Questions écartées dès le 14 novembre** : congé de paternité (la récupération ne renvoie que le congé parental) ; démission ou rupture conventionnelle pour le chômage (aucun des deux passages ne parle de chômage) ; prime de précarité en fin de CDD et dates de congés imposées (passages sans la réponse) ; SMIC et règlement intérieur (réponse évidente, donc peu de différence attendue entre les modèles) ; durée maximale d'un CDD (les 18 mois n'apparaissent que dans un passage sur les CDD d'usage).

## 7. Résultats des essais

| Moment | Question | Machine | Modèle | Résultat | Durée |
|---|---|---|---|---|---|
| 1 | période d'essai d'un cadre | Mac, 16/11 | adapté | réponse citée `[P1]` | 9,4 s, chargement compris |
| 3 | retraite d'un fonctionnaire | Mac, 16/11 | adapté | abstention | 6,0 s |
| 4 | renouvellement de la période d'essai | Mac, 16/11 | T | abstention | |
| 4 | renouvellement de la période d'essai | Mac, 16/11 | adapté | réponse citée `[P2]` | |
| 2 | arrêt maladie | Mac, 16/11 | adapté | une seule citation `[P3]`, rémunération non traitée | 5,0 s |
| 1 | période d'essai d'un cadre | Legion | adapté | à compléter en répétition | |
| 3 | retraite d'un fonctionnaire | Legion | adapté | à compléter en répétition | |
| 4 | renouvellement de la période d'essai | Legion | T | à compléter en répétition | |
| 4 | renouvellement de la période d'essai | Legion | adapté | à compléter en répétition | |

Si une question ne donne pas le comportement attendu sur le Legion, passer à la question de rechange et le consigner ici.

## 8. À ne pas dire

- « L'assistant ne se trompe jamais » ou « les citations prouvent la réponse » : une citation existante ne prouve ni que le passage justifie la réponse, ni que chaque affirmation est couverte.
- « Le modèle sait que la question est hors corpus » : il s'est abstenu à partir des passages fournis.
- « La démonstration applique le seuil S » : elle n'applique aucun seuil.
- « Le moment 4 prouve l'amélioration » : c'est une illustration choisie après essai ; la preuve est la mesure du protocole 06.
- « T est le modèle de base de la #31 » : T est le modèle d'origine passé par la même chaîne d'export que le modèle adapté.

## 9. Sources

`docs/etudes/demonstration/contrat_interface_111.md` (PR #121) ; `docs/etudes/demonstration/demo_legion_111.md` (PR #170, essai du 16 novembre) ; `demo_b/README.md` ; `demo_b/src/composants/Reponse.jsx` (libellé du bouton) ; `scripts/rag/serveur_demo.py` ; #52 (amendement M1, modèles, digests et résultats du 11 novembre) ; #111 ; relecture de Mahé du 14 novembre sur la PR #158.
