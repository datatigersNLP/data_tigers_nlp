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
