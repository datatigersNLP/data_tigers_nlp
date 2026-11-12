# Contrôle du fichier réel de paires d'adaptation de l'encodeur

12 novembre 2026, contrôle technique assisté à la demande de Jibril BENSALEM. Référence du dépôt : `dev/6334581dbfcae9e2189e04c7aa06b01dea7908b7`, après fusion de #144 et #145. [Résultat structuré](verification_encodeur_20261112.json).

## Résultat

Le fichier reçu est **identique à l'artefact identifié dans l'étude de #49** : `train_paires.jsonl`, 174 552 octets, 109 paires, SHA-256 `2d377eb66e7f4ca0e8e4cf34b089e5da7c46e47ddceab9f964764df468c21698`. L'original reste intact et n'est pas ajouté au dépôt.

| Contrôle | Résultat |
|---|---:|
| Paires JSONL reçues | 109 |
| Identifiants de passages distincts | 109 |
| Fiches d'entraînement distinctes | 109 |
| Identifiants résolus dans le corpus M2 | 109/109 |
| URLs et titres cohérents avec M2 | 109/109 |
| Préfixe `query: ` et question correspondants | 109/109 |
| Positifs préfixés `passage: ` et terminés par le texte M2 exact | 109/109 |
| Identifiants communs avec les 30 passages du pilote | **0** |
| URLs de fiche communes avec les 25 fiches du pilote | **0** |
| Textes intégraux des 30 sources présents dans les positifs | **0** |
| Mêmes textes présents après normalisation NFC/casse/espaces | **0** |
| Fiches d'entraînement présentes dans les 66 exclusions encodeur calculées | **0** |

Le contrôle technique de séparation côté encodeur est donc effectué sur les octets reçus, pour ces critères. Le rapport conserve les empreintes, les effectifs et les résultats ; le fichier de paires et son inventaire détaillé ne sont pas copiés dans le dépôt.

## Méthode exécutée

Lecture UTF-8 et JSON stricte, avec refus des clés dupliquées et des constantes non finies. Le fichier est identifié par ses octets, avant toute comparaison ; un simple nom de fichier ou un effectif de 109 ne suffirait pas.

Le corpus complet est contrôlé par SHA-256 : 4 240 passages, 261 fiches, passages `aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d`. Les 30 copies de sources du pilote sont comparées au corpus, leurs empreintes individuelles vérifiées, puis leurs identifiants et les URLs de leurs 25 fiches sont rapprochés de ceux des 109 paires. Une fiche est identifiée par son URL sans ancre ni barre finale.

Pour vérifier le contenu réellement fourni à l'encodeur, chaque champ `passage` est contrôlé : préfixe attendu et texte M2 exact à sa fin. Le texte intégral de chaque source du pilote est aussi recherché dans la totalité de chacun des 109 champs `passage`, sans découper les phrases. Le contrôle est répété après normalisation NFC, mise en casse commune par `casefold` et fusion des espaces. Ces opérations servent seulement à comparer ; aucun original n'est normalisé ou réécrit.

Le script `04_ajuster_encodeur.py` utilise les champs `query` et `passage`, avec les autres passages du lot comme négatifs. Les 109 passages sont donc tous comparés, qu'ils aient servi de positif ou de négatif dans un lot. Aucun entraînement, chargement de poids ou appel au RAG n'est exécuté pour ce contrôle.

Les empreintes du plan initial de révision 2, du fichier de sources et du corpus sont dans le JSON. La sélection des 25 fiches, ses 30 textes et la grille restent inchangés. La mise à jour du plan porte uniquement sur le suivi des contrôles.

## Contrôle Qwen distinct et provenance

Dans sa [relecture du 11 novembre sur #145](https://github.com/datatigersNLP/data_tigers_nlp/pull/145#pullrequestreview-5860312884), Mahé rapporte avoir contrôlé les cinq lots Qwen privés : aucune fiche ni passage du pilote parmi leurs cibles/contextes, et aucun des 30 textes intégraux dans leurs fichiers train/valid. Ces octets Qwen ne sont pas relus ici : cette preuve est attribuée à sa relecture, distincte de la présente vérification du fichier encodeur.

L'[audit initial](audit_separation.json), daté du 9 novembre, reste intact comme état historique antérieur à ces deux contrôles. Le présent rapport et `suivi_controles_lots` du plan décrivent l'état actualisé.

## Limites et suite

L'empreinte relie le fichier reçu à la référence publiée ; elle ne constitue pas une attestation indépendante de l'exécution historique de l'entraînement. Le contrôle ne recherche pas toutes les recopies partielles ou paraphrases et ne certifie pas une indépendance sémantique absolue. Les candidats du pilote n'existent pas encore : leurs questions seront à dédupliquer après génération.

Les 25 fiches du pilote sont aussi des fiches du test humain. Les résultats synthétiques restent séparés de la mesure officielle. Aucun verdict humain, jugement de catégorie, suffisance juridique ou hors corpus confirmé n'est créé ici ; les champs humains restent vierges. La relecture indépendante du présent complément n'est pas encore attestée.

La suite est de confirmer le relecteur des futurs candidats et de préparer l'environnement et la configuration sur le Legion avant génération : commit, prompts, paramètres, modèle/digest et version d'Ollama constatée. Aucun lot figé ou résultat réel n'est déclaré par ce contrôle.
