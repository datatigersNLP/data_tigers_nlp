# Contrat d'interface de la démonstration du volet B — issue #111

Responsable : Vaneck DAGAR. Soutien : Maïmouna SIGNATE. Référent de la chaîne : Jibril BENSALEM.

**Statut** proposé le 28 octobre 2026 (étape 1 de #111), à valider par Jibril. Rien n'est implémenté.

## 1. Objet

La démonstration du volet B a trois parties :

| Partie | Rôle | Responsable |
|---|---|---|
| Chaîne RAG (`scripts/rag/`, PR #85) | récupérer les passages, appeler Qwen, contrôler les citations | Jibril, inchangée |
| Couche locale mince | recevoir la question, appeler la chaîne, renvoyer un JSON | Vaneck, avec Jibril |
| Interface | saisir la question, afficher la réponse, ses citations et l'abstention | Vaneck, Maïmouna |

Ce contrat fixe le format des messages entre l'interface et la couche. Une fois validé, l'interface peut être construite
sur des sorties enregistrées (étape 2, 04/11), puis branchée sur la vraie chaîne sans changement de format (étape 3, 10/11).

## 2. Principes

- **Aucune modification de la logique de la #85.** La couche appelle les fonctions existantes de `rag.py` et
  `generation.py`, dans le même ordre que `main()` : `charger_index`, `charger_encodeur`, `encoder_question`,
  `recuperer_passages`, `construire_contexte`, `generer_reponse`.
- **Chargements une seule fois.** L'index et E5 sont chargés au démarrage de la couche, pas à chaque question.
- **Question libre.** `main()` n'accepte que les identifiants du lot de calibration ; la démonstration reçoit une
  question tapée. La couche appelle donc `encoder_question` directement, sans `lire_question_calibration`. Le texte
  est conservé mot pour mot, comme dans la #85.
- **Tout en local.** La couche écoute sur `127.0.0.1` et sert aussi les fichiers de l'interface : une seule origine,
  aucune requête vers un service externe. E5 et le tokeniseur Qwen sont lus dans le cache Hugging Face, préparé avant
  la démonstration, avec `HF_HUB_OFFLINE=1`. Ce point se contrôle comme au volet A (critère de #111).
- **Une question à la fois.** Ollama traite les appels l'un après l'autre ; l'interface n'envoie pas de nouvelle
  question tant que la précédente n'a pas reçu de réponse.

## 3. Routes

| Route | Rôle |
|---|---|
| `GET /` | fichiers de l'interface |
| `GET /api/etat` | état de la chaîne, pour afficher « prêt » ou la cause d'indisponibilité |
| `POST /api/question` | une question, une réponse au format de la section 5 |

## 4. `GET /api/etat`

```json
{
  "version_contrat": "b1-demo-v1",
  "pret": true,
  "index": {"verifie": true, "nb_passages": 4240, "sha256_index": "2ec45586…"},
  "encodeur_charge": true,
  "ollama": {"joignable": true, "version": "0.40.5", "modele": "qwen2.5-7b-instruct:q4_k_m-local", "digest": "6ec54444…"},
  "occupe": false,
  "message": null
}
```

`pret` vaut `false` si l'index est refusé, si E5 n'est pas chargé ou si Ollama ne répond pas ; `message` en donne la
cause en français. `ollama` reprend les champs de `verifier_ollama()`, sans le gabarit.

## 5. `POST /api/question`

**Entrée**

```json
{"question": "Quelles sont les obligations légales de l'employeur en période de forte chaleur ?"}
```

**Sortie** (code HTTP 200, y compris pour une abstention ou une sortie invalide)

```json
{
  "version_contrat": "b1-demo-v1",
  "question": "Quelles sont les obligations légales de l'employeur en période de forte chaleur ?",
  "statut": "reponse_citee",
  "reponse": "… [P1][P5] …",
  "citations": ["[P1]", "[P5]"],
  "citations_invalides": [],
  "verifications": {
    "justification_semantique_verifiee": false,
    "couverture_des_affirmations_verifiee": false
  },
  "sources": [
    {
      "reference": "[P1]",
      "citee": true,
      "rang": 1,
      "score": 0.8619567155838013,
      "passage_id": "m2-article115181-0002",
      "titre_fiche": "Chaleur et canicule au travail",
      "section_titre": "Un cadre réglementaire renforcé",
      "chemin": [],
      "url": "https://travail-emploi.gouv.fr/…",
      "url_citation": "https://travail-emploi.gouv.fr/…",
      "date_maj": "2025-08-11",
      "texte": "…"
    }
  ],
  "modele": {"nom": "qwen2.5-7b-instruct:q4_k_m-local", "digest": "6ec54444…"},
  "mesures": {
    "duree_totale_s": 47.9,
    "ollama": {
      "total_duration": 46200511600, "load_duration": 21901212700,
      "prompt_eval_duration": 18503807000, "eval_duration": 5774473000,
      "prompt_eval_count": 2317, "eval_count": 381
    }
  },
  "erreur": null
}
```

Les points de suspension et `duree_totale_s` sont illustratifs. Les autres valeurs viennent de l'essai Q036 de la #85
et de `front/public/index/passages_m2.json` (passage d'indice 1085). La question est celle de Q036, sans sa faute de
frappe : la démonstration accepte n'importe quel texte.

**Provenance de chaque champ**

| Champ | Source dans la #85 |
|---|---|
| `statut` | `generer_reponse()["statut"]`, ou `erreur_preparation` (section 6) |
| `reponse` | `reponse_brute`, non corrigée ; `null` si aucune génération n'a eu lieu |
| `citations`, `citations_invalides`, `verifications` | `validation_citations` |
| `sources` | les cinq `resultats` de `recuperer_passages`, dans l'ordre, avec la référence `[Pk]` de `construire_contexte` ; `citee` vaut `true` si la référence figure dans `citations` |
| `modele` | `ollama.modele` et `ollama.digest` |
| `mesures.ollama` | `mesures_ollama`, en nanosecondes comme Ollama les renvoie |
| `mesures.duree_totale_s` | mesurée par la couche, de la réception de la question à l'envoi de la réponse |

Les cinq passages sont toujours renvoyés, cités ou non, avec leur texte : l'interface peut ainsi ouvrir le passage d'une
citation et montrer ceux qui ont été consultés. Le score sert à l'affichage ; comme dans la #85, ce n'est ni une
probabilité ni une preuve que le passage justifie la réponse.

## 6. Statuts et affichage

| `statut` | Origine | Affichage |
|---|---|---|
| `reponse_citee` | `valider_citations` | réponse rédigée ; chaque `[Pk]` est un bouton qui ouvre la carte de son passage (fiche, section, lien) ; rappel que les citations ne sont pas vérifiées sur le fond |
| `abstention_modele` | phrase d'abstention exacte | encadré d'abstention distinct, comme au volet A, puis les passages consultés sur demande |
| `sortie_invalide` | référence mal formée, absente, ou abstention mêlée | avertissement « réponse non conforme », réponse brute repliée, passages consultés |
| `erreur_technique` | génération incomplète ou comptes de tokens incohérents | message d'erreur et bouton « Réessayer » ; réponse brute repliée si elle existe |
| `erreur_preparation` | exception levée avant toute réponse : `ErreurRecuperation` (question vide ou trop longue pour E5) ou `ErreurGeneration` (Ollama injoignable, modèle différent, budget de tokens dépassé) | message d'erreur et bouton « Réessayer » ; `reponse` et `sources` peuvent être vides |

`erreur_preparation` est le seul statut ajouté par la couche. Il couvre les cas où `main()` affiche « Récupération
refusée » ou « Génération impossible » et renvoie le code 1. Son champ `erreur` porte alors le type et le message de
l'exception, par exemple :

```json
{"type": "ErreurGeneration", "message": "Ollama /api/tags : …"}
```

**Codes HTTP.** 200 pour les cinq statuts ; 400 si le corps n'est pas un JSON avec une question non vide ; 409 si une
question est déjà en cours.

## 7. Durées à prévoir dans l'interface

D'après les essais de la #85, la réponse arrive en environ 46 s au premier appel (dont 21,9 s de chargement de Qwen) et
en quelques secondes ensuite, quand le modèle reste chargé (`keep_alive: 30m`). L'interface affiche donc un état « réponse
en cours de rédaction » sans limite de temps inférieure au délai de 300 s de `generation.py`.

## 8. Ce dont l'étape 2 a besoin

- **Les sorties enregistrées de Q036 et Q003** (`data/rag/Q036_rag.json` et `Q003_rag.json`, sur le Legion, hors Git),
  converties au format de la section 5 : elles alimentent la maquette sans Ollama.
- Une sortie simulée pour `sortie_invalide` et une pour `erreur_preparation`, écrites à la main et marquées comme telles.

## 9. Emplacement du code

- Couche : `scripts/rag/serveur_demo.py`, à côté de la chaîne qu'elle appelle.
- Interface : un dossier distinct, `demo_b/`. Le déploiement du site du volet A ne se déclenche que sur `front/**`
  (`.github/workflows/deploiement-volet-a.yml`) : la démonstration ne peut pas modifier le site en ligne. Les composants
  du volet A (cartes de passages, panneau, couleurs) y sont repris par copie, pour la cohérence demandée par #111.

## 10. Points à valider avec Jibril

1. Les routes et le format des sections 3 à 6.
2. Le statut `erreur_preparation`, ajouté par la couche.
3. L'appel direct à `encoder_question` pour une question libre.
4. L'emplacement du code (section 9).
5. L'envoi des deux sorties enregistrées de Q036 et Q003, pour la maquette.

Hors de ce contrat : l'état B2 et son seuil S (protocole 06, PR #108), et le choix du modèle adapté (#107). Si la vidéo
montre l'avant et l'après adaptation, le champ `modele` indique lequel a répondu ; le format ne change pas. La PR #119
rend le modèle et son digest paramétrables dans `verifier_ollama()`, avec ceux de #31 par défaut : une fois fusionnée,
la couche pourra désigner le modèle adapté sans toucher à la chaîne.
