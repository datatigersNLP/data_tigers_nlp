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

## Avec la chaîne locale (étape 3, 10/11)

Sans le mode maquette, l'interface appelle `GET /api/etat` et `POST /api/question` sur la couche locale
(`scripts/rag/serveur_demo.py`, à écrire), relayés par Vite vers http://127.0.0.1:8765 en développement.

```powershell
npm run dev
```

## Tests

```powershell
npm test
```

Ils couvrent la mise en forme des réponses (`src/citations.js`) et le convertisseur, dont la conformité au contrat des
deux réponses versionnées.
