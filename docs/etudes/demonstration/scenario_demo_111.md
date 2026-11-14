# Scénario de la démonstration du volet B (issue #111)

Responsable : Vaneck DAGAR. Soutien : Maïmouna SIGNATE. Machine et modèles : Mahé BEGNIS.

**Statut** proposé le 14 novembre 2026 (étape 4 de #111). Les questions ont été choisies d'après les passages que renvoie la récupération ; les réponses des modèles restent à vérifier lors de l'essai sur le Mac de Mahé. La vidéo de secours est prévue le 18 novembre.

## 1. Objet

Montrer en 3 à 4 minutes l'assistant réglementaire local du volet B (cas B1) :
- une réponse citée, dont chaque référence ouvre son passage ;
- une réponse qui s'appuie sur deux passages ;
- une abstention sur une question hors corpus ;
- la même question posée au témoin T, puis au modèle adapté (#107).

Ce scénario sert de script pour la vidéo et pour la démonstration en soutenance. Ce n'est pas une mesure : les résultats mesurés sont ceux du protocole 06 (#52).

## 2. Préparation sur le Mac de Mahé

Depuis la racine du dépôt, sur `dev` à jour, avec l'environnement Python de `scripts/rag/requirements.txt`. La couche locale et l'interface sont décrites dans `demo_b/README.md`.

**Une fois, avec une connexion** : mettre en cache E5 et le tokeniseur Qwen, puis construire l'interface.

```bash
cd scripts/rag
python -c "from rag import charger_encodeur; from generation import charger_tokeniseur_qwen; charger_encodeur(); charger_tokeniseur_qwen()"
cd ../../demo_b
npm ci
npm run build
cd ..
```

**Lancer la couche avec le témoin T** (modèles et digests publiés sur le #52 le 11 novembre) :

```bash
python scripts/rag/serveur_demo.py --modele qwen2.5-7b-instruct:temoin-q4_k_m-local --digest 8a077f3d3f56b636face1357eba557b21e2ba68bc72ee81e48b377272da72f27
```

**Lancer la couche avec le modèle adapté** :

```bash
python scripts/rag/serveur_demo.py --modele qwen2.5-7b-instruct:lora-v2b-q4_k_m-local --digest 18cb25f099f2ba1b21a3bc945da6be7ce4d128cb4e579325fc0f70dfccb37174
```

Sans `--modele` ni `--digest`, la couche attend le modèle de la #31, qui n'est pas installé sur le Mac. Le modèle se choisit au lancement de la couche, jamais depuis le navigateur : pour passer de T au modèle adapté, arrêter la couche (Ctrl+C) et la relancer.

Ouvrir http://127.0.0.1:8765/ et vérifier que l'interface affiche « L'assistant est prêt ».

**Avant d'enregistrer** : poser une question d'échauffement avec chaque modèle. Le premier appel charge le modèle dans Ollama, ce qui a pris environ 20 s lors des essais de la #85 sur le Legion ; la durée sur le Mac n'est pas connue.

## 3. Déroulé et minutage

Les temps d'attente de la génération sont coupés au montage. L'interface affiche sous chaque réponse le modèle qui l'a rédigée et sa durée réelle : la coupe ne cache donc rien.

| Temps | Moment | Modèle | Ce qu'on montre |
|---|---|---|---|
| 0:00 à 0:20 | Introduction | adapté | l'écran d'accueil, l'état « prêt », le périmètre du corpus |
| 0:20 à 1:00 | 1. Question directe | adapté | une réponse citée, et le clic sur `[P1]` qui ouvre le passage |
| 1:00 à 1:40 | 2. Deux passages | adapté | une réponse qui cite deux passages différents |
| 1:40 à 2:15 | 3. Hors corpus | adapté | l'encadré d'abstention et les passages consultés |
| 2:15 à 3:30 | 4. T puis adapté | T, puis adapté | la même question, et la différence entre les deux réponses |
| 3:30 à 3:50 | Conclusion | | ce que montre la mesure, et ses limites |

## 4. Détail des moments

### Introduction

- **À l'écran** : l'interface ouverte, l'état « L'assistant est prêt », le message d'accueil qui décrit le corpus (261 fiches, 4 240 passages, instantané du 11 septembre 2026).
- **À dire** : « L'assistant tourne entièrement sur cet ordinateur : la recherche des passages, puis la rédaction par Qwen2.5-7B. Il ne répond qu'à partir des 261 fiches pratiques du ministère du Travail, et il cite ses sources. »

### Moment 1 : question directe

- **Question** : « Quelle est la durée maximale de la période d'essai d'un cadre en CDI ? »
- **Attendu** : une réponse citée. Le passage P1 (fiche « La période d'essai ») donne « quatre mois pour les cadres ».
- **À montrer** : cliquer sur `[P1]`, qui amène la carte du passage avec sa fiche, sa section et son lien.
- **À dire pendant l'attente** : « L'assistant récupère d'abord les cinq passages les plus proches de la question, puis le modèle rédige sa réponse à partir de ces seuls passages. »

### Moment 2 : question qui croise deux passages

- **Question** : « Je suis en arrêt maladie : mon employeur peut-il me licencier, et suis-je payé pendant l'arrêt ? »
- **Attendu** : une réponse qui cite deux passages de la fiche « Les absences liées à la maladie ou à l'accident non professionnel » : P2 pour l'indemnisation (indemnités journalières et complément de l'employeur), P3 pour le licenciement (pas pour l'état de santé en soi, sauf inaptitude ; possible si les absences imposent un remplacement définitif).
- **À montrer** : les deux références, et l'ouverture de chacune.
- **À dire** : « La question a deux volets ; chacun est justifié par un passage différent. »

### Moment 3 : question hors corpus

- **Question** : « Comment est calculée la pension de retraite d'un fonctionnaire ? »
- **Attendu** : l'abstention. Aucun des cinq passages renvoyés ne traite de la retraite des fonctionnaires.
- **À montrer** : l'encadré d'abstention, puis « Afficher les passages consultés » pour montrer qu'ils ne répondent pas.
- **À dire** : « Le corpus ne traite pas de ce sujet. Plutôt que de répondre de mémoire, le modèle s'abstient. L'interface ne prétend pas savoir pourquoi : on peut ouvrir les passages pour le vérifier. »

### Moment 4 : la même question, à T puis au modèle adapté

- **Question retenue** : à choisir lors de l'essai parmi les quatre de la section 5, celle où la différence entre les deux modèles est la plus visible.
- **Déroulé** : poser la question avec la couche lancée sur T, puis relancer la couche avec le modèle adapté et poser la même question.
- **Attendu** : un comportement que la mesure a mis en évidence. Avec un passage qui contient la réponse, T s'abstient souvent à tort, alors que le modèle adapté répond en citant.
- **À dire** : « L'adaptation visait ce défaut. Cette question a été choisie après essai : c'est une illustration, pas une mesure. »

### Conclusion

- **À dire** : « Sur les questions de test du protocole, le modèle adapté cite un passage pertinent dans 25,0 % des cas, contre 13,9 % pour le modèle de base, soit +11,1 points, une amélioration démontrée. En revanche, il ne s'abstient pas mieux sur les questions hors corpus : 20 sur 24 dans les deux cas. »

## 5. Questions candidates pour le moment 4

Par ordre de préférence. Dans les quatre cas, la réponse figure dans les passages renvoyés, mais pas de façon évidente.

| Question | Où est la réponse | Pourquoi T peut hésiter |
|---|---|---|
| « Quelle est la durée minimale du repos entre deux journées de travail ? » | P1 : « 11 heures consécutives » | la réponse est dans une fiche sur les salariés détachés, alors qu'elle vaut pour tous |
| « Combien d'heures puis-je travailler au maximum sur une semaine ? » | P2 : « 48 heures par semaine », et 44 heures en moyenne sur 12 semaines | même cas, et une règle sur le travail de nuit en P3 |
| « Un apprenti mineur a-t-il le droit de travailler la nuit ? » | P2 : interdiction selon l'âge ; P1 et P3 : dérogations de l'inspecteur du travail | réponse conditionnelle, répartie sur trois passages |
| « Ma période d'essai peut-elle être renouvelée ? » | P2 : « une fois si un accord de branche étendu le prévoit » | réponse courte mais conditionnelle ; même fiche que le moment 1 |

## 6. Choix des questions

- **Origine** : les questions ont été écrites pour la démonstration. Aucune ne figure dans le jeu annoté `jeu-questions-v1`, et leurs sujets diffèrent de ceux des réponses jugées à l'aveugle (#52).
- **Vérification** : pour chacune, les cinq passages renvoyés par la récupération de la #85 (E5 en fp32) ont été lus, le 14 novembre, sur la machine de Vaneck. Les réponses des modèles n'ont pas encore été vues.
- **Questions écartées** : congé de paternité (la récupération ne renvoie que le congé parental) ; démission ou rupture conventionnelle pour le chômage (aucun des deux passages ne parle de chômage) ; prime de précarité en fin de CDD et dates de congés imposées (passages sans la réponse) ; SMIC et règlement intérieur (réponse évidente, donc peu de différence attendue entre les modèles) ; durée maximale d'un CDD (les 18 mois n'apparaissent que dans un passage sur les CDD d'usage).

## 7. À compléter après l'essai sur le Mac

| Moment | Question gardée | Statut obtenu (T) | Statut obtenu (adapté) | Durée (adapté) |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |

Si une question ne donne pas le comportement attendu, la remplacer par une question de réserve et le consigner ici.

## 8. À ne pas dire

- « L'assistant ne se trompe jamais » ou « les citations prouvent la réponse » : une citation existante ne prouve ni que le passage justifie la réponse, ni que chaque affirmation est couverte.
- « Le modèle sait que la question est hors corpus » : il s'est abstenu à partir des passages fournis.
- « La démonstration applique le seuil S » : elle n'applique aucun seuil.
- « Le moment 4 prouve l'amélioration » : c'est une illustration choisie après essai ; la preuve est la mesure du protocole 06.

## 9. Sources

`docs/etudes/demonstration/contrat_interface_111.md` (PR #121) ; `demo_b/README.md` ; `scripts/rag/serveur_demo.py` ; #52 (amendement M1, modèles, digests et résultats du 11 novembre) ; #111 ; message de Mahé du 14 novembre (attendus du scénario).
