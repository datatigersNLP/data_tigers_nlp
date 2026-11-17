# Démonstration du volet B : interface de l'assistant local

Ticket #111, étape 2 (maquette). Contrat d'interface : `docs/etudes/demonstration/contrat_interface_111.md` (PR #121).

L'interface reprend le parcours et la charte du site du volet A (#53) : panneau latéral, fil de conversation, champ
fixé en bas. Elle affiche la réponse rédigée par Qwen ; chaque référence `[Pk]` est un bouton qui amène la carte de son
passage. L'abstention, la réponse non conforme et les erreurs ont chacune leur affichage (contrat, section 6).

Ce dossier est indépendant de `front/` : le déploiement du site du volet A ne se déclenche que sur `front/**`.

## Lancer la maquette

La maquette n'appelle aucun modèle. Elle rejoue deux essais réels de la chaîne de la #85 (Q036, réponse citée ; Q003,
abstention), et deux cas simulés à la main (réponse non conforme, chaîne indisponible).

```powershell
cd demo_b
npm ci
npm run maquette
```

Puis ouvrir http://127.0.0.1:5173/ et choisir une question d'exemple dans le panneau.

Les réponses rejouées sont dans `public/maquette/`. Elles ont été converties des traces de Jibril (`data/rag/` sur le
Legion, hors Git) par `outils/convertir_traces.mjs`, et versionnées avec son accord (02/11/2026). Seule la structure
change : question, réponse, références, textes et mesures sont ceux de la trace. Pour les régénérer :

```powershell
npm run convertir -- <dossier des traces>
```

## Avec la chaîne locale (étape 3)

La couche locale `scripts/rag/serveur_demo.py` relie l'interface à la chaîne de la #85 : elle sert l'interface construite
et les routes `GET /api/etat` et `POST /api/question`, sur http://127.0.0.1:8765/ uniquement. Elle fonctionne hors ligne :
E5 et le tokeniseur Qwen doivent donc être en cache, et Ollama lancé, en version 0.40.13, avec le modèle de la #31.

Préparer le cache une fois, avec une connexion, depuis `scripts/rag` :

```powershell
..\..\.venv\Scripts\python.exe -c "from rag import charger_encodeur; from generation import charger_tokeniseur_qwen; charger_encodeur(); charger_tokeniseur_qwen()"
```

Puis construire l'interface et lancer la couche :

```powershell
cd demo_b
npm ci
npm run build
cd ..
.venv\Scripts\python.exe scripts\rag\serveur_demo.py
```

Ouvrir http://127.0.0.1:8765/. Si un élément manque, la couche démarre quand même et l'interface en affiche la cause. Une
fois le manque corrigé, relancer la couche si c'est l'index, E5 ou le tokeniseur ; pour Ollama, cliquer sur « Réessayer ».

Le modèle servi se règle sur le serveur, jamais depuis le navigateur : `--modele <nom> --digest <empreinte>` pour le modèle
adapté (#107). Pour modifier l'interface, `npm run dev` dans `demo_b/` relaie `/api` vers cette couche.

## Avec la chaîne v2 (#172)

`scripts/rag/serveur_demo_v2.py` sert la même interface, avec le même contrat ; seule la récupération change
(`scripts/recuperation/recuperation_demo.py`). Par défaut, c'est l'état R1 du protocole 10, famille B :

* **Partie dense** : l'E5 de base, comme la chaîne de la #85.
* **Partie lexicale** : BM25 V3, sur l'en-tête et le texte des passages.
* **Fusion et reclassement** : fusion RRF des 100 premiers rangs de chaque liste ; les 20 premiers candidats sont
  reclassés par `BAAI/bge-reranker-v2-m3`.
* **Contexte** : les 10 premiers passages, dans le budget de tokens du prompt, avec la consigne v1.
* **Abstention** : pas de seuil S, le modèle seul s'abstient. L'ordre des passages suit le reclasseur ; le score affiché
  reste la similarité cosinus de la partie dense.

Sur le jeu v2, un passage pertinent entre dans le contexte pour 86,0 % des questions, contre 57,0 % avec la chaîne de
la #85 (`docs/etudes/evaluation/10_resultats.md`, section 5). `--dense ajuste` sert l'état R2, où la partie dense est
l'encodeur ajusté du volet A (question encodée par le q8 que sert le site, avec onnxruntime ; passages par l'index du
site) : mesuré à 84,3 %, il n'a pas été retenu par la règle du protocole.

Aucun fichier de `data/` n'est lu : l'en-tête des passages est reconstruit depuis l'index versionné. La liste de mots
vides Snowball de BM25 V3 est téléchargée une fois, à une révision figée et contrôlée par son empreinte, dans
`data/evaluation/`.

Préparer le cache une fois, avec une connexion, depuis la racine du dépôt (environ 2,3 Go pour le reclasseur) :

```powershell
.venv\Scripts\python.exe -m pip install -r scripts\rag\requirements.txt
.venv\Scripts\python.exe -c "import sys; sys.path[:0] = ['scripts/rag', 'scripts/recuperation', 'scripts/evaluation']; import recuperation as rc, lexical_baselines as lb; rc.Reclasseur('bge-m3'); rc.generation.charger_tokeniseur_qwen(); rc.rag.charger_encodeur(); lb.load_snowball_stopwords()"
```

Puis, l'interface construite et Ollama lancé :

```powershell
.venv\Scripts\python.exe scripts\rag\serveur_demo_v2.py --modele <nom> --digest <empreinte>
```

`GET /api/etat` décrit la chaîne servie (clé `chaine` : état R1 ou R2, partie dense, empreinte de son index et, pour R2,
du q8, reclasseur).
Le premier appel est plus lent : le reclasseur se charge en mémoire.

## Tests

```powershell
npm test
```

Ils couvrent la mise en forme des réponses (`src/citations.js`) et le convertisseur, dont la conformité au contrat des
deux réponses versionnées. La couche locale a les siens, avec Ollama et E5 simulés : `python -m unittest test_serveur_demo`
depuis `scripts/rag`. La chaîne v2 a les siens : `python scripts/rag/test_serveur_demo_v2.py` et
`python scripts/recuperation/test_recuperation_demo.py`, depuis la racine du dépôt.
