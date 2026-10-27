# Support de présentation — Jalon J3 (15 points)
**Module** NLP 2 · Master 2 Data & IA · FGES — Université Catholique de Lille  
**Équipe** Data Tigers : Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE  
**Statut** Version de cadrage pour le Weekly 7 (Ticket #112) · Projet à 2 volets

---

## Diapositive 1 — Titre, Équipe et Cadrage du Jalon J3

### Contexte & Rappel des deux volets imposés
Le projet impose la réalisation conjointe de deux applications complémentaires basées sur le corpus du droit du travail (fiches pratiques du Ministère du Travail / Code du Travail Numérique) :

* **Volet A (Application en ligne)** : Cas A3 — Moteur de recherche sémantique dense sans serveur.
  * Inférence 100 % client dans le navigateur (Transformers.js / WebAssembly).
  * Coût d'exploitation nul : hébergement statique sur GitHub Pages, aucun appel API externe.
* **Volet B (Application locale)** : Cas B1 — Assistant juridique interactif avec chaîne RAG.
  * Inférence locale sur modèle open-weights (`Qwen2.5-7B-Instruct`).
  * Adaptation du modèle par fine-tuning LoRA, sourçage formel des réponses (`[Pn]`) et évaluation rigoureuse avant/après.

### Objectifs du Jalon J3 (15 points)
1. **Volet A finalisé et déployé** : Moteur de recherche sémantique réactif, modèle élagué hébergé sous le quota strict de 100 Mio, abstention active et accessibilité validée.
2. **Volet B engagé** : Socle RAG opérationnel, protocoles de mesure et de séparation verrouillés, faisabilité matérielle du fine-tuning démontrée.
3. **Supports et méthodologie** : Démonstrations reproductibles, tenue du board et du journal d'usage IA.

---

## Diapositive 2 — Volet A : Architecture technique & Déploiement sans serveur

### Contraintes & Choix d'ingénierie
* **Inférence 100 % in-browser** : Aucun backend Python en production. L'application est servie comme site statique via GitHub Pages.
* **Moteur d'exécution** : Transformers.js adossé à ONNX Runtime Web (WebAssembly / SIMD).
* **Encodeur dense** : `multilingual-e5-small` quantifié en 8 bits (q8) pour concilier compacité et fidélité de représentation sémantique.
* **Asymétrie de l'encodage E5** : Préfixe obligatoire `query: ` pour la requête utilisateur et `passage: ` pour les documents indexés, garantissant le respect de la géométrie de l'espace latent.

### Optimisation du chargement et du calcul
* **Normalisation L2 préalable** : Les vecteurs de passages et de requêtes sont normalisés unitairement ($\|v\|_2 = 1$). La similarité cosinus est alors rigoureusement équivalente à un produit scalaire en $O(d)$ ($d = 384$).
* **Index binaire Little-Endian Float32** : Remplacement de l'index JSON initial par un format binaire direct (`index.bin`). Le chargement s'effectue via l'API `TypedArray` (`Float32Array`) en mémoire vive sans bloquer le thread UI du navigateur, supprimant les 1,2 s de latence observées avec `JSON.parse()`.
* **Réactivité mesurée** : Recherche effectuée en moins de 25 ms côté client sur Chromium et Firefox.

