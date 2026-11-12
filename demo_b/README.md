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

## Tests

```powershell
npm test
```

Ils couvrent la mise en forme des réponses (`src/citations.js`) et le convertisseur, dont la conformité au contrat des
deux réponses versionnées. La couche locale a les siens, avec Ollama et E5 simulés : `python -m unittest test_serveur_demo`
depuis `scripts/rag`.
