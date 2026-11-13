# Préparer le pilote exploratoire Agent0

Révision 2 du 9 novembre 2026, #95/#96, préparée à la demande de Jibril. **25 emplacements, aucune question générée, aucun verdict humain, aucun gel ni essai RAG.** Le dossier est prêt pour examiner les sources, la méthode et le contrat ; la validation humaine reste à effectuer.

## Relecteurs et règle de validation Agent0

Décision de Jibril du 12 novembre 2026 : **Mahé BEGNIS (`mahebegnis`) et Remy RAYANE (`Remynou`) sont les relecteurs désignés de cette contribution et des prochaines tâches Agent0. Une seule validation explicite de l'un des deux suffit** pour le livrable concerné, sur sa version finale ; leurs deux approbations ne sont pas cumulativement requises. Le relecteur doit être distinct de l'auteur de la contribution.

Les prochaines PR Agent0 demandent la relecture aux deux personnes ; la validation effective peut venir de Mahé ou de Remy. Pour les futurs candidats, l'un des deux peut effectuer la relecture sémantique et consigner les décisions dans la grille. Une approbation du code ou de la procédure ne vaut pas acceptation des candidats : leurs questions, preuves, catégories et répondabilité doivent être effectivement examinées. Cette règle ne change pas le protocole ni les doubles annotations du jeu humain officiel.

## Contenu à relire

| Fichier | Contenu |
|---|---|
| [preparation.json](preparation.json) | Plan versionné, sélection et conditions de démarrage |
| [sources_m2.json](sources_m2.json) | 30 passages exacts sur 25 fiches, avec empreintes ; cinq paires |
| [grille_relecture.json](grille_relecture.json) | 25 lignes vierges, dont la trace de recherche hors corpus |
| [separation_adaptation.md](separation_adaptation.md) | Contrôle des exclusions, limites des lots privés et vérifications restantes |
| [audit_separation.json](audit_separation.json) | Références, ensembles d'URLs, rapprochement initial et tirage révisé |
| [verification_encodeur_20261112.md](verification_encodeur_20261112.md) et [JSON](verification_encodeur_20261112.json) | Contrôle du fichier réel de 109 paires, empreinte conforme et intersections vides |
| [methode_hors_corpus.md](methode_hors_corpus.md) | Procédure opérationnelle soumise à relecture, sans question préécrite |
| [revue_lanceur_144.md](revue_lanceur_144.md) | Constat historique sur bb80096 et suivi du correctif a62c9b2 |

La [révision 1](https://github.com/datatigersNLP/data_tigers_nlp/tree/377717f477abd8d85eb80b1f2ee9157692c3a6c7/docs/etudes/agent0_pilote_independant) reste accessible dans Git. Elle excluait seulement les trois fiches de mise au point. Le contrôle montre que 17 de ses 20 fiches sont hors des listes d'exclusion de l'adaptation ; ce n'est pas une preuve de leur utilisation réelle. La révision 2 change les sources **avant toute génération ou réponse RAG**. La première version et son motif de remplacement restent traçables par le commit et l'audit.

## Sélection reproductible de la révision 2

Corpus M2 de `dev/a294d252d1ecc285dfd7df88e43a3ec5df891fe7` : 4 240 passages, 261 fiches, empreintes intégrales dans `sources_m2.json`. La matrice n'est pas lue ; son empreinte est celle de l'en-tête.

Algorithme `sha256-fiches-reservees-puis-passages-v2`, graine textuelle `20261109` :

1. Extraire seulement URL, lot et type du jeu humain figé après contrôle de son SHA-256. Les questions et extraits humains ne servent pas au tirage.
2. Prendre l'intersection des fiches exclues par les deux chaînes d'adaptation : 61 fiches côté Qwen, incluses dans les 66 URLs non vides constatées côté encodeur. Retirer les trois fiches historiques ; une seule appartient à cette intersection. Le vivier restant comporte 60 fiches.
3. Grouper les passages par URL sans ancre ni barre finale, conserver ceux dont `len(texte) >= 200` caractères Unicode. Ce filtre technique écarte les fragments très courts ; il ne certifie pas la suffisance des textes.
4. Trier les fiches par SHA-256 de l'UTF-8 `20261109|fiche|URL`, puis URL en cas d'égalité.
5. Parcourir cinq emplacements de chaque catégorie dans cet ordre : simple, reformulation, multi_passage, adversarial, hors_corpus. Prendre la première fiche restante ayant un passage admissible, ou deux pour multi_passage, et retirer la fiche.
6. Dans la fiche, trier les passages admissibles par SHA-256 de `20261109|passage|passage_id`, puis identifiant ; prendre un ou deux passages.

Résultat : **25 fiches distinctes, 30 passages, aucune fiche du vivier autorisé par les règles d'adaptation examinées**. Les cinq sources hors corpus sont des ancrages de génération, jamais des preuves positives d'absence ou de réponse. Une paire ne prouve pas la nécessité sémantique de ses deux passages.

**Suivi du 12 novembre.** Les 109 paires réelles de l'encodeur ont été reçues avec l'empreinte publiée ; leur contrôle ne trouve aucun identifiant, fiche ou texte source intégral du pilote dans les passages d'entraînement, même après normalisation NFC/casse/espaces. Le rapport distingue ce résultat technique de la relecture de Mahé sur #145, qui rapporte le contrôle des cinq lots privés Qwen le 11 novembre. L'audit initial daté du 9 novembre reste inchangé comme référence historique. La relecture indépendante du nouveau complément encodeur est attendue ; les limites sur les recopies partielles, paraphrases et la future déduplication des questions sont explicites.

Les 25 fiches appartiennent aussi au test humain ; ce pilote partage donc ses fiches et n'est pas un nouveau benchmark humain indépendant. Ses futures questions resteront synthétiques, séparées et non représentatives ; leurs résultats ne seront pas combinés à la mesure officielle. Aucune question humaine ni sortie RAG n'a guidé le tirage. Les futurs candidats sont exclus de l'entraînement.

Le README d'adaptation annonce 67 fiches exclues alors que les octets vérifiés en donnent 66. Cet écart est consigné dans l'audit ; aucun fichier d'adaptation n'est corrigé ici.

## Ordre d'exécution après relecture

### 1. Examiner la préparation et la séparation

Le code et le format de la [PR #144](https://github.com/datatigersNLP/data_tigers_nlp/pull/144), ainsi que la préparation #145, ont été approuvés par Mahé le 11 novembre sur `a62c9b2` et `56f9cbf`, puis fusionnés le 12 novembre. Le nouveau rapport de contrôle des paires encodeur reste à relire. L'indépendance sémantique ne se déduit pas des seuls contrôles techniques.

Examiner les preuves de séparation actualisées, puis consigner le responsable de la relecture indépendante des futurs candidats. La décision du 30/10 conserve la priorité de l'adaptation et de la mesure officielle. La préparation ne déclare pas un lancement réel.

### 2. Consigner la configuration avant génération

Épingler le commit retenu après revue, les versions exactes des cinq prompts, les paramètres et la graine des appels, le digest du modèle et la version d'Ollama constatée sur le Legion. La graine des sources ne remplace pas celle de génération. Conserver l'environnement de mesure officielle et préparer un environnement distinct. Mahé rapporte 184 tests réussis sur Mac avec les versions verrouillées ; la préparation de l'environnement sur le Legion reste à effectuer, sans transposer cette mesure à Windows.

Préparer les sélections dans le format attendu par `generate.py` à partir des identifiants du plan et du corpus vérifié. Les présents JSON sont des documents préparatoires, pas des sélections de génération ni un lot d'évaluation. Aucun gel ou acceptation n'est fabriqué pour contourner les contrôles.

### 3. Générer puis relire les candidats

Budget maximal : **25 appels, un par emplacement**, sans relance automatique pour remplacer un échec ou remplir une catégorie. Les nombres sont des objectifs de préparation, pas des quotas d'acceptation. Conserver les sorties brutes, prompts, traces, erreurs et rejets, avec de nouveaux identifiants de runs ; ne pas écraser les anciens.

Chaque futur candidat est rattaché à son emplacement et à son empreinte. Le relecteur humain distinct de l'auteur vérifie la question exacte, les conditions, exceptions, preuves, doublons de sens et catégorie. Pour multi_passage, chaque source doit être nécessaire et leur ensemble suffisant ; pour adversarial, la question doit effectivement présupposer une prémisse fausse corrigible par les sources. La procédure hors corpus est détaillée dans son document ; elle ne fournit encore aucun verdict.

Les champs humains restent vides jusqu'à la relecture. Un cas incertain reste `pending` ; un classement erroné conduit au rejet, sans changement silencieux de type. La difficulté est seulement visée. Les originaux ne sont pas réécrits à partir des résultats du RAG.

### 4. Figer les seuls cas acceptés, puis vérifier le lanceur

Après acceptation du contrat, exporter hors Git `questions.jsonl` et `manifest.json` au format `agent0-challenge-v1`, avec entre 1 et 25 cas acceptés. Si aucun ne l'est, déclarer qu'aucun lot évaluable n'est disponible. Garder rejets et incertains à part. Documenter provenance, séparation, relectures, configuration, empreintes exactes, effectif et date de gel avec fuseau avant toute réponse du RAG.

Ce dossier n'est pas cet export. `--check-lot` vérifie les déclarations, les contraintes d'entrée et le JSONL ; le corpus et les extraits sont contrôlés au début de l'exécution, avant E5/Ollama. Aucun de ces contrôles ne remplace la validation sémantique.

Après revue du code, du lot et autorisation de l'essai réel borné, utiliser un nouveau run dans l'environnement distinct. L'analyse de #97 reste une étape ultérieure ; #98 n'est pas engagé.

## État des points de préparation

- [x] Exclusions des viviers d'adaptation reproduites et limites des données privées consignées.
- [x] Tirage révisé, ancrages hors corpus, textes et empreintes préparés.
- [x] Méthode hors corpus écrite et grille de recherche prête, sans question ni verdict.
- [x] Correctif technique de #144 référencé.
- [x] Contrat, sources et méthode approuvés dans #144/#145 ; ce complément conserve sa propre relecture à effectuer.
- [x] Contrôle technique du fichier encodeur conforme et contrôle Qwen rapporté par Mahé, avec sources et limites distinctes.
- [x] Mahé et Remy désignés comme relecteurs ; une validation de l'un des deux suffit pour chaque livrable examiné.
- [ ] Relecture effective du complément encodeur, puis des futurs candidats une fois générés.
- [ ] Configuration du générateur et environnement arrêtés avant génération.
- [ ] Candidats produits, relus, puis lot figé avant RAG.

**Traçabilité IA :** [note du 9 novembre](../../journal/2026-11-09_agent0_pilote_preparation_revue.md) et [contrôle du 12 novembre](../../journal/2026-11-12_agent0_controle_encodeur.md). Aucun temps réel, verdict sur les candidats ni résultat de benchmark n'est déclaré.
