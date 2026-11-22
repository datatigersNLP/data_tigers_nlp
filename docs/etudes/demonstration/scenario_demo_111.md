# Scénario de la démonstration du volet B (issue #111)

Responsable : Vaneck DAGAR. Soutien : Maïmouna SIGNATE. Modèles, chaîne et essais : Mahé BEGNIS.

**Statut** proposé le 14 novembre 2026, revu le 16 novembre après la relecture de Mahé, puis le 22 novembre pour la chaîne de démonstration v2 (état R1, PR #175, #172). Les questions et les comportements attendus sont ceux de l'essai et de la vidéo de secours faits par Mahé sur son Mac le 22 novembre (commentaire du #111).

## 1. Objet

Montrer en 2 min 40 l'assistant réglementaire local du volet B (cas B1) :
- une réponse citée, dont la référence ouvre son passage ;
- la même question posée au témoin T, puis au modèle adapté (#107) ;
- une abstention sur une question hors corpus.

Le sujet prévoit environ 4 minutes de démonstration pour les deux volets : le volet A en ligne (environ 1 min 10), puis le volet B en local. Il n'y a ni introduction ni conclusion : la présentation qui suit porte les résultats (#114). La vidéo de secours suit le même déroulé.

Ce scénario sert de script pour la démonstration en soutenance. Ce n'est pas une mesure : les résultats mesurés sont ceux des protocoles 06 (#52) et 10 (#174).

## 2. La chaîne montrée

La couche `scripts/rag/serveur_demo_v2.py` (PR #175) sert la même interface que `serveur_demo.py` ; seule la récupération change (état R1 du protocole 10) :
- **récupération hybride** : E5 de base et BM25, fusionnés (RRF), puis les 20 premiers candidats reclassés par `BAAI/bge-reranker-v2-m3` ;
- **contexte** : jusqu'à 10 passages dans le budget de tokens du prompt, consigne v1 ;
- **abstention** : pas de seuil S, le modèle seul s'abstient.

L'interface est celle de la PR #177 : logo de l'équipe et fenêtre « Confidentialité et mentions ».

## 3. Préparation

Sur le Mac de Mahé, depuis `dev` à jour, une fois les PR #175 et #177 fusionnées. Le cache (E5, tokeniseur Qwen, reclasseur, mots vides de BM25) se prépare une fois avec une connexion : voir la section « Avec la chaîne v2 » de `demo_b/README.md`.

**Deux couches en même temps**, dans deux terminaux : le modèle adapté sur le port 8765, T sur le port 8766. On passe d'un modèle à l'autre en changeant d'onglet, sans relancer de couche en direct.

```bash
python scripts/rag/serveur_demo_v2.py --modele qwen2.5-7b-instruct:lora-v2b-q4_k_m-local --digest 18cb25f099f2ba1b21a3bc945da6be7ce4d128cb4e579325fc0f70dfccb37174
python scripts/rag/serveur_demo_v2.py --port 8766 --modele qwen2.5-7b-instruct:temoin-q4_k_m-local --digest 8a077f3d3f56b636face1357eba557b21e2ba68bc72ee81e48b377272da72f27
```

- **Deux onglets** : http://127.0.0.1:8765/ (adapté) et http://127.0.0.1:8766/ (T). Chacun doit afficher « L'assistant est prêt. ».
- **Mise en route** : poser une question d'échauffement dans chaque onglet peu avant de commencer, en finissant par le modèle adapté. Le premier appel est plus lent : il charge le modèle dans Ollama et le reclasseur en mémoire.
- **Exemples du panneau** : les trois questions du scénario y figurent ; un clic remplit la question sans risque de faute de frappe.

## 4. Déroulé et minutage

L'interface affiche sous chaque réponse le modèle qui l'a rédigée et sa durée réelle. Sur le Mac, une question prend une dizaine de secondes en médiane (11,8 s sur le jeu v2, protocole 10) ; parler pendant la génération.

| Temps | Moment | Onglet | Ce qu'on montre |
|---|---|---|---|
| 0:00 à 0:50 | 1. Question directe | adapté (8765) | une réponse citée, et le clic sur la citation qui ouvre le passage |
| 0:50 à 2:00 | 2. T puis adapté | T (8766), puis adapté (8765) | la même question, et la différence entre les deux réponses |
| 2:00 à 2:40 | 3. Hors corpus | adapté (8765) | l'encadré d'abstention et les passages consultés |
| s'il reste du temps | Confidentialité | adapté (8765) | la fenêtre « Confidentialité et mentions » : tout reste sur cet ordinateur |

## 5. Détail des moments

### Moment 1 : question directe

- **Question** : « Combien de jours de congés payés ai-je par an ? »
- **Attendu, d'après l'essai du 22 novembre** : une réponse citée `[P2]`.
- **À montrer** : cliquer sur la citation, qui amène la carte du passage avec sa fiche, sa section et son lien.
- **À dire** : « L'assistant tourne entièrement sur cet ordinateur. Il retrouve d'abord les passages des fiches du ministère du Travail les plus proches de la question, puis le modèle rédige sa réponse à partir de ces seuls passages, en les citant. »

### Moment 2 : la même question, à T puis au modèle adapté

- **Question** : « Ma période d'essai peut-elle être renouvelée ? »
- **Déroulé** : poser la question dans l'onglet de T (8766), puis la même dans l'onglet du modèle adapté (8765).
- **Attendu, d'après l'essai du 22 novembre** : T s'abstient ; le modèle adapté répond en citant `[P1]`. Les deux ont reçu les mêmes passages.
- **À dire** : « T est le modèle d'origine, passé par la même chaîne d'export que le modèle adapté, et il reçoit les mêmes passages. Ici, il s'abstient alors que la réponse s'y trouve : c'est le défaut que visait l'adaptation. Le modèle adapté répond, en citant le passage. Cette question a été choisie après essai : c'est une illustration, pas une mesure. »

### Moment 3 : question hors corpus

- **Question** : « Comment est calculée la pension de retraite d'un fonctionnaire ? »
- **Attendu** : l'abstention. Les fiches du ministère du Travail ne traitent pas de la retraite des fonctionnaires.
- **À montrer** : l'encadré d'abstention, puis le bouton « Afficher les … passages consultés », pour montrer qu'ils ne répondent pas.
- **À dire** : « Le corpus ne traite pas de ce sujet. Plutôt que de répondre de mémoire, le modèle s'abstient. L'interface ne prétend pas savoir pourquoi : on peut ouvrir les passages pour le vérifier. »

## 6. Choix des questions

- **Origine** : les trois questions ont été écrites pour la démonstration. Aucune ne figure dans le jeu de test `jeu-questions-v1` ni dans le jeu v2 (`evaluation/questions_v2/`).
- **Historique** : le 14 novembre, les questions candidates ont été choisies d'après les passages renvoyés par la chaîne de la #85 (E5 de base, 5 passages). Les essais de Mahé, le 16 novembre puis le 22 novembre avec la chaîne R1, ont conduit à en écarter plusieurs.
- **Écartées après essai** :
  - « Quelle est la durée maximale de la période d'essai d'un cadre en CDI ? » : avec la chaîne R1, la réponse sort en fragment qui commence par un tiret ;
  - « Combien d'heures puis-je travailler au maximum sur une semaine ? » : la dérogation est attribuée à l'inspecteur du travail, alors que le passage dit la DREETS ;
  - « Je suis en arrêt maladie : mon employeur peut-il me licencier, et suis-je payé pendant l'arrêt ? » : une seule citation, la rémunération n'est pas traitée (essai du 16 novembre) ;
  - « Quelle est la durée minimale du repos entre deux journées de travail ? » : aucune différence entre T et le modèle adapté (essai du 16 novembre) ;
  - « Un apprenti mineur a-t-il le droit de travailler la nuit ? » : le modèle adapté fait moins bien que T (essai du 16 novembre).

## 7. Essais

| Date | Machine et chaîne | Moment | Modèle | Résultat |
|---|---|---|---|---|
| 22/11 | Mac de Mahé, R1 | 1. congés payés | adapté | réponse citée `[P2]` |
| 22/11 | Mac de Mahé, R1 | 2. période d'essai renouvelée | T | abstention |
| 22/11 | Mac de Mahé, R1 | 2. période d'essai renouvelée | adapté | réponse citée `[P1]` |
| 22/11 | Mac de Mahé, R1 | 3. retraite d'un fonctionnaire | adapté | abstention |
| à refaire | Mac de Mahé, R1 depuis `dev` | 1 à 3 | T et adapté | après la fusion des #175 et #177 |

À température nulle, les réponses filmées le 22 novembre étaient identiques mot pour mot à une répétition préalable. Si une question ne donne plus le comportement attendu, le consigner ici avant de la remplacer.

## 8. À ne pas dire

- « L'assistant ne se trompe jamais » ou « les citations prouvent la réponse » : une citation existante ne prouve ni que le passage justifie la réponse, ni que chaque affirmation est couverte.
- « Le modèle sait que la question est hors corpus » : il s'est abstenu à partir des passages fournis.
- « La démonstration applique le seuil S » : elle n'applique aucun seuil.
- « Le moment 2 prouve l'amélioration » : c'est une illustration choisie après essai ; la preuve est la mesure (protocoles 06 et 10).
- « T est le modèle de base de la #31 » : T est le modèle d'origine passé par la même chaîne d'export que le modèle adapté.
- « Le volet B utilise l'encodeur ajusté du site » : la chaîne R1 garde l'E5 de base ; l'état R2, avec l'encodeur ajusté, n'a pas été retenu par la règle du protocole 10.

## 9. Sources

#111 (essais du 16 et du 22 novembre, vidéo de secours) ; #172 et PR #175 (chaîne R1, `demo_b/README.md`, section « Avec la chaîne v2 ») ; PR #174 (protocole 10, `docs/etudes/evaluation/10_resultats.md`) ; PR #177 (interface) ; `docs/etudes/demonstration/contrat_interface_111.md` (PR #121) ; #52 (modèles et digests) ; relecture de Mahé du 14 novembre sur la PR #158.
