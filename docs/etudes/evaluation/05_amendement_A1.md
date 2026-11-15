# Protocole 05 : amendement A1, calendrier de la mesure

**Équipe** Data Tigers  
**Ticket** #49, #164  
**Responsable** Mahé BEGNIS  
**Statut** décidé et publié le 15 novembre 2026, avant toute mesure de l'encodeur ajusté. Le protocole 05 (`05_protocole_ajustement.md`) n'est pas modifié : cet amendement le complète.

---

## 1. Motif

Le protocole 05, figé le 14 octobre, prévoyait la mesure le 15 octobre et interdisait toute dérogation au calendrier : faute de mesure avant le 16 octobre, la règle de repli a servi l'encodeur de base pour le 18 octobre. Le 30 octobre, la mesure a été suspendue pour laisser la priorité au chemin critique du volet B (#49). Ce chemin critique est terminé depuis le 11 novembre. L'audit des performances du 15 novembre (#164) désigne l'encodeur ajusté comme le levier le plus fort compatible avec le navigateur : la mesure est donc faite maintenant.

---

## 2. Ce qui change

* **Calendrier.** Mesure, décision et, si l'encodeur ajusté est retenu, élagage, contrôle d'identité, nouveau seuil et index du site, entre le 15 et le 19 novembre, avant le gel du projet le 20 novembre. Si une condition manque le 19 novembre, l'encodeur de base reste servi.
* **Responsable.** Mahé BEGNIS fait seul la mesure, la décision et l'intégration.

---

## 3. Ce qui ne change pas

La règle de déploiement (section 4), la recette, les fichiers et leurs empreintes (section 2), les jeux, la règle de pertinence D4, la métrique principale, l'écart et son intervalle (section 3), et les conditions d'hébergement (section 5).

---

## 4. Écarts déclarés

* **Témoin descriptif omis.** Ses fichiers (`models/multilingual-e5-small-base`) ne figurent pas dans le paquet conservé. Le protocole précise qu'il ne décide de rien.
* **Navigateur sans interface.** L'encodage se fait dans Chrome 155 sur le Mac, comme la mesure du notebook 03, mais piloté sans interface. **Contrôle de reproduction, préalable à toute mesure de l'ajusté** : la page réencode les 113 textes du notebook 03 avec l'encodeur de base, servi en local à partir des fichiers de la révision `761b726d` ; les vecteurs doivent être identiques bit à bit à ceux du 13 octobre (`vecteurs_navigateur.json`). Sinon, rien n'est mesuré.
* **Modèles servis en local.** La page d'encodage charge les q8 depuis `data/adaptation/navigateur/` (paramètre `modele`), après contrôle de leur empreinte : `f80102d3…` pour la base, `934a202b…` pour l'ajusté, tous deux avec le tokeniseur de l'encodeur de base, comme décidé au gel.
* **Population du CDTN.** Les 131 requêtes jugées `oui` ou `partiel` et leurs 494 formulations, avec leurs passages pertinents, telles que construites par la règle figée de l'étude 04 (`data/evaluation/recuperation/population.json`).
* **Mode développement.** Il ne lit que le lot de calibration ; aucune métrique du CDTN n'y est calculée.
* **Script plutôt que notebook.** La mesure est faite par `scripts/evaluation/ajustement_05.py`, avec ses tests, plutôt que par le notebook `05_ajustement.ipynb`, qui n'a jamais été créé. Comme le prévoyait le protocole, elle est exécutée deux fois : la seconde exécution doit redonner un contenu identique, sinon le résultat n'est pas retenu.
* **Contrôle ajouté.** Avant toute décision, la base servie, recalculée sur le lot de test, doit redonner à 10⁻¹² près les métriques publiées par le notebook 03 (Recall@1, @5 et @10, MRR@10, Recall@5 à la fiche, AUC de l'abstention).

---

## 5. Contrôles faits avant le gel

* **Reproduction du notebook 03** : 113 vecteurs identiques bit à bit à ceux du 13 octobre (Chrome 155 sans interface, base servie en local).
* **Index de l'ajusté** : 4 240 passages réencodés en fp32 avec le tokeniseur de base, cosinus minimal de 0,99999982 avec l'index de Remy ; seules 3 lignes ont un autre plus proche voisin, les trois passages en double déjà signalés par le protocole.
* **Mode développement** sur le lot de calibration : deux exécutions identiques. Ses chiffres, sur 5 questions, ne servent à rien.

---

## 6. Historique

* **15 novembre 2026** : amendement décidé et publié avant toute mesure de l'encodeur ajusté.
