# Démonstration du volet B sur le Legion (issue #111)

Procédure pour lancer la démonstration locale du volet B sur le Legion de Jibril, avec le modèle adapté et le témoin T.
Elle a été essayée de bout en bout sur le Mac de Mahé le 16 novembre 2026, avec le code de `dev` (`e0c240b`). Le
scénario est celui de la PR #158 ; l'interface et la couche locale sont celles de la PR #128 (`demo_b/README.md`).

## 1. Ce qui passe par GitHub, et ce qui n'y passe pas

- **Par GitHub** : tout le code, c'est-à-dire l'interface `demo_b/`, la couche `scripts/rag/serveur_demo.py` et la chaîne de la #85. L'index du volet B aussi : `front/public/index/`, empreinte `2ec45586…`, celle du verrou de la mesure. Le site du volet A lit un autre index (`front/public/index_ajuste/`) depuis le 15 novembre ; celui-ci n'a pas changé.
- **Hors GitHub** : les deux modèles, de 4 683 073 600 et 4 683 073 696 octets. Ils dépassent la limite de 100 Mio par fichier de GitHub, et aucun modèle n'est versionné. Mahé les transmet sur un support, avec leurs empreintes.

## 2. Le dossier transmis

Mahé le prépare sur son Mac, dans `~/NLP2_local/ollama/transfert_legion/`, et le copie sur une clé ou un disque
**formaté en exFAT ou en NTFS** : FAT32 refuse les fichiers de plus de 4 Gio.

| Fichier | Contenu |
|---|---|
| `lora-v2b-q4_k_m.gguf` | modèle adapté (export de la #140) |
| `temoin-q4_k_m.gguf` | témoin T, le modèle d'origine passé par la même chaîne d'export |
| `Modelfile.adapte` | la seule ligne `FROM ./lora-v2b-q4_k_m.gguf` |
| `Modelfile.temoin` | la seule ligne `FROM ./temoin-q4_k_m.gguf` |
| `SHA256SUMS` | les deux empreintes ci-dessous |

Empreintes SHA-256 attendues, mesurées le 16 novembre sur les fichiers servis pendant la mesure :

```
cebe1e379c2599f5b3a2e9621e1de4b5c58c12833732b9b14de91695b01bb7ed  lora-v2b-q4_k_m.gguf
5197d4a183629a34fa9a737eded9752aed1c3b0870129afff0ed2d74659dc4f6  temoin-q4_k_m.gguf
```

Le nom des fichiers compte : Ollama l'inscrit dans le manifeste du modèle, donc dans son digest. Ne pas les renommer.

## 3. Préparation sur le Legion, une seule fois

Déjà en place depuis la mesure du 9 novembre, à vérifier : Ollama 0.40.13 avec les mises à jour automatiques
coupées (`AutoUpdateEnabled`), le `.venv` du dépôt (`scripts/rag/requirements.txt` n'a pas changé depuis), et le cache
Hugging Face d'E5 et du tokeniseur Qwen. Node doit être en version 20 (20.19 ou plus) ou en version 22.12 ou plus (`engines` de `demo_b/package.json`).

Dans PowerShell, à la racine du dépôt :

```powershell
ollama --version
git fetch origin
git switch dev
git pull --ff-only
git log --oneline -1
```

Attendu : `0.40.13`, puis `e0c240b` ou un commit plus récent de `dev`.

Dans le dossier transmis, contrôler les fichiers, puis créer les deux modèles sous ces noms exacts :

```powershell
Get-FileHash -Algorithm SHA256 .\lora-v2b-q4_k_m.gguf, .\temoin-q4_k_m.gguf
ollama create qwen2.5-7b-instruct:lora-v2b-q4_k_m-local -f Modelfile.adapte
ollama create qwen2.5-7b-instruct:temoin-q4_k_m-local -f Modelfile.temoin
ollama list
```

`Get-FileHash` écrit les empreintes en majuscules ; elles doivent être celles de la section 2. Dans `ollama list`, la
colonne ID doit valoir `18cb25f099f2` pour le modèle adapté et `8a077f3d3f56` pour T : ce sont les 12 premiers
caractères des digests de la mesure.

- **Vérifié sur le Mac** : recréés le 16 novembre sous un autre nom avec ces deux Modelfile, les modèles ont exactement les digests de la mesure. Le manifeste ne contient que le fichier GGUF, son nom et une configuration minimale ; le gabarit vient du code (`generation.py` envoie l'entrée brute).
- **Non vérifié sous Windows** : si l'ID diffère, ne pas changer de référence sans contrôle. `ollama show --modelfile qwen2.5-7b-instruct:lora-v2b-q4_k_m-local` doit afficher une ligne `FROM` qui se termine par `sha256-cebe1e37…` : les poids sont alors identiques, seul le manifeste diffère. Lancer la couche une fois ; son refus affiche le digest trouvé, à passer ensuite à `--digest`. Signaler l'écart sur le #111.

Puis construire l'interface :

```powershell
cd demo_b
npm ci
npm run build
cd ..
```

## 4. Lancement, avant chaque présentation

Deux fenêtres PowerShell, à la racine du dépôt. Première fenêtre, le modèle adapté, sur le port 8765 :

```powershell
.venv\Scripts\python.exe scripts\rag\serveur_demo.py --modele qwen2.5-7b-instruct:lora-v2b-q4_k_m-local --digest 18cb25f099f2ba1b21a3bc945da6be7ce4d128cb4e579325fc0f70dfccb37174
```

Seconde fenêtre, T, sur le port 8766 :

```powershell
.venv\Scripts\python.exe scripts\rag\serveur_demo.py --port 8766 --modele qwen2.5-7b-instruct:temoin-q4_k_m-local --digest 8a077f3d3f56b636face1357eba557b21e2ba68bc72ee81e48b377272da72f27
```

Ouvrir http://127.0.0.1:8765/ et http://127.0.0.1:8766/ dans deux onglets. Chacun doit afficher « L'assistant est
prêt. », et chaque réponse indique le modèle qui l'a rédigée.

- **Pourquoi deux ports** : on passe d'un modèle à l'autre en changeant d'onglet, sans relancer de couche en direct. Sur le Mac, une couche relancée juste après son arrêt a refusé de démarrer (« Address already in use ») : la couche refuse volontairement de réutiliser un port encore occupé par les connexions précédentes.
- **Mémoire du GPU** : avec 8 Gio, le Legion ne garde sans doute qu'un des deux modèles sur le GPU. Ollama décharge alors l'un pour charger l'autre, et la première question après chaque changement inclut ce chargement : 19,1 s pour le modèle de la #31 sur le Legion (`docs/etudes/inference_locale_qwen.md`). À vérifier pendant la répétition avec `ollama ps`.
- **Mise en route** : poser une question dans chaque onglet peu avant la présentation, en finissant par celui du modèle adapté. Un modèle reste chargé 30 minutes après sa dernière question (`keep_alive` de `generation.py`).

## 5. Ce qu'a donné l'essai du 16 novembre, sur le Mac

Même code, mêmes modèles et mêmes digests, Ollama 0.40.13, température nulle et graine fixe. Sur le GPU du Legion,
les textes peuvent différer légèrement : les confirmer pendant la répétition.

| Moment | Question | Modèle | Résultat | Durée |
|---|---|---|---|---|
| 1 | Quelle est la durée maximale de la période d'essai d'un cadre en CDI ? | adapté | réponse citée `[P1]` : « de quatre mois pour les cadres » | 9,4 s, chargement compris |
| 3 | Comment est calculée la pension de retraite d'un fonctionnaire ? | adapté | abstention | 6,0 s |
| 2, en réserve | Je suis en arrêt maladie : mon employeur peut-il me licencier, et suis-je payé pendant l'arrêt ? | adapté | réponse citée `[P3]` sur le licenciement seulement ; la rémunération n'est pas traitée | 5,0 s |

Les quatre questions candidates du moment 4 :

| Question | T | Modèle adapté |
|---|---|---|
| Quelle est la durée minimale du repos entre deux journées de travail ? | 11 heures consécutives `[P1][P2]` | 11 heures consécutives `[P1][P2]` |
| Combien d'heures puis-je travailler au maximum sur une semaine ? | abstention | 48 heures par semaine `[P2]` |
| Un apprenti mineur a-t-il le droit de travailler la nuit ? | réponse plus complète `[P1]` | réponse partielle `[P2]` |
| Ma période d'essai peut-elle être renouvelée ? | abstention | « une fois si un accord de branche étendu le prévoit » `[P2]` |

- **Moment 4 proposé** : « Ma période d'essai peut-elle être renouvelée ? ». T s'abstient alors que la réponse est dans les passages, le défaut que l'adaptation visait, et le modèle adapté répond en citant le bon passage. C'est la même fiche qu'au moment 1. Question de rechange : celle des 48 heures.
- **À éviter** : l'apprenti mineur (le modèle adapté y fait moins bien que T) et le repos quotidien (aucune différence).
- **Moment 2** : il ne donne pas la réponse à deux passages qu'attend le scénario ; le garder en réserve ou le retirer.
- **Style du modèle adapté** : des réponses très courtes, parfois réduites à un fragment (au moment 1, la réponse commence par un tiret). Le dire plutôt que le découvrir en direct.

## 6. À dire et à ne pas dire

- La démonstration n'applique pas le seuil S de la mesure : c'est le modèle seul qui s'abstient (scénario de la #158, section 8).
- Le moment 4 est une illustration choisie après essai, pas une mesure. La preuve est l'analyse principale du protocole 06 : le modèle adapté cite un passage pertinent pour 18 questions sur 72 (25,0 %), contre 10 sur 72 (13,9 %) pour T, soit +11,1 points, intervalle [+2,1 ; +23,8].
- Ne pas présenter T comme « le modèle de base de la #31 » : c'est le modèle d'origine passé par la même chaîne d'export que le modèle adapté.

## 7. Solutions de repli

- **Modèles non transmis à temps** : la couche lancée sans `--modele` ni `--digest` sert le modèle de la #31, déjà sur le Legion. C'est le modèle d'origine, ni T ni le modèle adapté : le dire, et ne pas jouer le moment 4.
- **Couche ou Ollama en échec** : la maquette (`npm run maquette` dans `demo_b/`) rejoue deux essais réels sans modèle, sur http://127.0.0.1:5173/ ; sinon, la vidéo de secours prévue par le #111.

## 8. Sécurité

- Tout reste sur 127.0.0.1 : la couche n'écoute pas ailleurs, et Ollama non plus tant que `OLLAMA_HOST` n'est pas modifié. Ne pas ouvrir ces ports au réseau, y compris pour projeter depuis une autre machine.
- La démonstration fonctionne hors ligne : la couche impose `HF_HUB_OFFLINE=1`.
- Les modèles ne contiennent pas de données personnelles : ils sont adaptés sur des fiches publiques et des questions générées. Quel que soit le moyen de transfert, contrôler les empreintes à l'arrivée.
