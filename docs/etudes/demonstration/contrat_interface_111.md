# Contrat d'interface de la démonstration du volet B — issue #111

Responsable : Vaneck DAGAR. Soutien : Maïmouna SIGNATE. Référent de la chaîne : Jibril BENSALEM.

**Statut** proposé le 28 octobre 2026 (étape 1 de #111), à valider par Jibril. Rien n'est implémenté.

Précisions du 30 octobre après relecture de Jibril avec l'assistance de Codex : état prêt,
format des erreurs, conservation des traces et configuration du modèle. La validation porte
sur le contrat documentaire ; aucun serveur ou écran n'est testé par cette relecture.

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
  "tokeniseur_disponible": true,
  "ollama": {"joignable": true, "verifie": true, "version": "0.40.11", "modele": "qwen2.5-7b-instruct:q4_k_m-local", "digest": "6ec54444…"},
  "occupe": false,
  "message": null
}
```

`pret` exige un index vérifié, E5 chargé, le tokeniseur Qwen disponible en cache hors ligne et
les contrôles de `verifier_ollama()` réussis pour le modèle configuré : nom, digest, GGUF qwen2
Q4_K_M et gabarit. Pour le Legion, la version cible est Ollama 0.40.11 (décision #107 du 30/10) ;
un écart rend la chaîne indisponible jusqu'à vérification de sa configuration.
`message` donne en français la cause de toute indisponibilité. Aucun appel de génération n'est
nécessaire à ce contrôle. `ollama` sélectionne les champs utiles de `verifier_ollama()`, sans
gabarit, et la couche ajoute `joignable` et `verifie`. Ces deux booléens ne sont pas des champs
renvoyés directement par le helper. Les empreintes abrégées de cet exemple seront complètes
dans les réponses réelles. `occupe` décrit séparément l'appel déjà en cours : POST renvoie alors 409.

## 5. `POST /api/question`

**Entrée**

```json
{"question": "Quelles sont les obligations légales de l'empoyeur en période de forte chaleur ?"}
```

**Sortie** (code HTTP 200, y compris pour une abstention ou une sortie invalide)

```json
{
  "version_contrat": "b1-demo-v1",
  "question": "Quelles sont les obligations légales de l'empoyeur en période de forte chaleur ?",
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
et de `front/public/index/passages_m2.json` (passage d'indice 1085). La question historique Q036
est conservée mot pour mot, y compris « empoyeur ». Les fixtures issues de Q036/Q003 gardent
aussi les réponses, textes, références et mesures originales ; seule leur structure est adaptée.
L'exemple d'état de la section 4 décrit la configuration cible du 30/10, pas la version d'Ollama
de l'essai historique. Les mesures historiques ne sont jamais présentées comme une nouvelle exécution.

**Provenance de chaque champ**

| Champ | Source dans la #85 |
|---|---|
| `statut` | `generer_reponse()["statut"]`, ou `erreur_preparation` (section 6) |
| `reponse` | `reponse_brute`, non corrigée ; `null` si aucun texte de réponse n'a été reçu |
| `citations`, `citations_invalides`, `verifications` | `validation_citations` |
| `sources` | les cinq `resultats` de `recuperer_passages`, dans l'ordre, avec la référence `[Pk]` de `construire_contexte` ; `citee` vaut `true` si la référence figure dans `citations` |
| `modele` | `ollama.modele` et `ollama.digest` |
| `mesures.ollama` | `mesures_ollama`, en nanosecondes comme Ollama les renvoie |
| `mesures.duree_totale_s` | mesurée par la couche avec une horloge monotone, de la réception de la question à la préparation du JSON de réponse ; hors chargements au démarrage et transport HTTP |

Après une récupération réussie, les cinq passages sont renvoyés, cités ou non, avec leur texte : l'interface peut ainsi ouvrir le passage d'une
citation et montrer ceux qui ont été consultés. Le score sert à l'affichage ; comme dans la #85, ce n'est ni une
probabilité ni une preuve que le passage justifie la réponse.

## 6. Statuts et affichage

| `statut` | Origine | Affichage |
|---|---|---|
| `reponse_citee` | `valider_citations` | réponse rédigée ; chaque `[Pk]` est un bouton qui ouvre la carte de son passage (fiche, section, lien) ; rappel que les citations ne sont pas vérifiées sur le fond |
| `abstention_modele` | phrase d'abstention exacte | encadré d'abstention distinct, comme au volet A, puis les passages consultés sur demande |
| `sortie_invalide` | référence mal formée, absente, ou abstention mêlée | avertissement « réponse non conforme », réponse brute repliée, passages consultés |
| `erreur_technique` | génération incomplète ou comptes de tokens incohérents | message d'erreur et bouton « Réessayer » ; réponse brute repliée si elle existe |
| `erreur_preparation` | exception sans résultat structuré de génération : `ErreurRecuperation` (question trop longue pour E5) ou `ErreurGeneration` (Ollama injoignable, modèle différent, budget dépassé ou échec HTTP) | message d'erreur et bouton « Réessayer » ; champs conservés selon les règles ci-dessous |

`erreur_preparation` est le seul statut ajouté par la couche. Il couvre les cas où `main()` affiche « Récupération
refusée » ou « Génération impossible » et renvoie le code 1. Son champ `erreur` porte alors le type et le message de
l'exception, par exemple :

```json
{"type": "ErreurGeneration", "message": "Ollama /api/tags : …"}
```

**Structure stable des cinq statuts.** Toutes les clés de la section 5 sont présentes.
`citations`, `citations_invalides` et `sources` sont toujours des listes, vides si leurs données
ne sont pas disponibles. Les deux booléens de `verifications` restent à `false`. `reponse`
vaut `null` en l'absence de texte reçu ; `modele` vaut `null` si son identité n'a pas été vérifiée.
`mesures` conserve `duree_totale_s` et `ollama`, ce dernier valant `null` sans mesures reçues.
Sur `erreur_technique` ou `erreur_preparation`, `erreur` contient un type et un message ; elle
vaut `null` pour les autres statuts. En cas de génération retournée comme `erreur_technique`,
les motifs de `erreurs_techniques` alimentent ce message. Une validation structurelle réussie
ne doit jamais masquer ce statut d'erreur. Les sources déjà récupérées sont conservées même
si la génération échoue. L'absence de réponse reçue, notamment après expiration du délai HTTP,
ne prouve pas qu'Ollama n'a jamais commencé le calcul ; aucune relance automatique n'est prévue.

**Codes HTTP.** 200 pour les cinq statuts ; 400 si le corps n'est pas un JSON avec une question non vide ; 409 si une
question est déjà en cours.

Pour 400 et 409, le JSON minimal est `version_contrat` et `erreur` (`type`, `message`).
L'interface traite d'abord le code HTTP avant de lire une réponse complète de la section 5.
Le refus d'un appel concurrent est aussi assuré par la couche locale, même avec deux onglets ;
le bouton désactivé dans un seul onglet ne suffit pas.

## 7. Durées à prévoir dans l'interface

Les deux essais de la #85 rapportent 46,2 s pour Q036 (dont 21,9 s de chargement de Qwen),
puis 1,16 s pour l'abstention Q003. Ce sont des durées Ollama sur des entrées et sorties différentes,
pas une promesse de latence générale ou une mesure de la chaîne entière. `keep_alive: 30m`
peut éviter un rechargement. L'interface affiche un état d'attente pendant les différentes étapes ;
son délai laisse terminer la récupération, puis l'appel HTTP de génération (300 s maximum dans
`generation.py`), avec une marge pour le traitement local. Elle ne présente pas la durée de Q003
comme le temps attendu de toutes les réponses suivantes.

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

**Point 5 confirmé le 29/10.** Jibril a transmis les deux JSON complets à Vaneck par Discord,
comme consigné dans la conversation de #121. Ils restent hors Git. Les quatre choix techniques
sont relus dans cette version précisée ; leur mise en œuvre et leur contrôle viendront dans #111.

Hors de ce contrat : l'état B2 et son seuil S (protocole 06, PR #108), et le choix du modèle adapté (#107). Si la vidéo
montre l'avant et l'après adaptation, le champ `modele` indique lequel a répondu ; le format ne change pas. La PR #119
rend le modèle et son digest paramétrables dans `verifier_ollama()`, avec ceux de #31 par défaut : une fois fusionnée,
la couche pourra désigner le modèle adapté sans toucher à la chaîne. Le couple nom/digest
est fixé par la configuration locale du serveur et n'est pas fourni librement par le navigateur.
La baseline de démonstration ne reçoit pas silencieusement le seuil B2 de la mesure.
