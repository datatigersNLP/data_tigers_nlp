# Notebook 01 : corpus travail-emploi et découpages comparés

**Ticket** #35, découpage du corpus depuis la source SocialGouv
**Notebook** `scripts/decoupage/01_corpus_decoupage.ipynb`
**Auteur** Mahé BEGNIS
**Équipe** Data Tigers, NLP 2, Master 2 Data & IA, FGES
**Date** 27 septembre 2026
**Statut** exécuté intégralement ; M2 proposé comme méthode de travail, décision collective en Weekly, à confirmer au notebook 03

**Objet.** Ce document explique ce que fait le notebook 01, ce qu'il établit et ce qu'il laisse ouvert, pour que chaque membre de l'équipe puisse le reprendre, le réexécuter et le défendre en soutenance.

Tous les chiffres cités proviennent de l'exécution du 27 septembre 2026. Les numéros de section renvoient aux sections du notebook.

*Ce document a été produit avec l'assistance d'outils d'intelligence artificielle. Il est relu par l'équipe dans la pull request qui l'introduit, et les usages seront consignés dans le journal prévu par le sujet.*

---

## 1. En bref

| Question | Réponse | Section |
|---|---|---|
| D'où vient le texte ? | des fiches complètes publiées par SocialGouv, figées sur un commit et contrôlées par empreinte | 2 |
| Quelles fiches ? | les 261 fiches du jeu Hugging Face, jointes par identifiant | 4 |
| L'extraction perd-elle du texte ? | non : 2 121 sections sur 2 121 reproduisent exactement leur html | 7 |
| Quelle méthode est proposée ? | M2, le découpage structurel : 4 240 passages de 259,1 tokens en moyenne | 11 |
| Pourquoi M2 ? | c'est la seule méthode dont la référence de section est exacte | 14 |
| Et les mots vides ? | ils sont gardés : le texte affiché doit rester intact, et les listes usuelles retirent « ne », « pas », « sans » | 14 |
| Qu'est-ce qui n'est pas établi ? | laquelle des méthodes donne la meilleure recherche : il faut pour cela le jeu de questions | notebook 03 |

## 2. Place dans la chaîne

Le notebook 01 produit les passages. Le notebook 02 les encode en vecteurs et exporte l'index du site. Le notebook 03 comparera les découpages sur le jeu de questions annotées, en préparation.

| Entrée | Sortie |
|---|---|
| fiches SocialGouv (JSON) et jeu Hugging Face (Parquet), téléchargés et contrôlés par le notebook | `data/decoupage/passages/passages_m0.parquet` à `passages_m3.parquet`, plus `passages_m2_256.parquet` |
| aucun fichier du dépôt n'est lu | `data/decoupage/passages/manifeste.json` : sources, révisions, paramètres, effectifs, empreintes |

Le dossier `data/` n'est jamais versionné. Le notebook vérifie que git l'ignore avant d'écrire quoi que ce soit.

## 3. Sources

| Source | Version figée | Fichier | Rôle |
|---|---|---|---|
| `SocialGouv/fiches-travail-data` | commit `fbf639f`, 11 septembre 2026 | `data/fiches-travail.json`, 16,4 Mio | texte complet des fiches, avec leur html |
| `AgentPublic/travail-emploi` | commit `98744a6` | `travail_emploi_part_0.parquet`, 29,6 Mio | liste des 261 fiches et découpage de l'éditeur (M0) |
| `Xenova/multilingual-e5-small` | révision `761b726` | tokeniseur | comptage exact des tokens |
| `intfloat/multilingual-e5-small` | révision `614241f` | modèle | encodage des phrases pour M3 |

Les empreintes SHA-256 complètes figurent dans le code et dans le manifeste. Un fichier local dont l'empreinte diffère est retéléchargé ; si le téléchargement diffère encore, le notebook s'arrête.

**Pourquoi partir de SocialGouv et non du texte Hugging Face.** Le texte Hugging Face dérive du champ `text` de SocialGouv, qui a deux défauts lus dans le code du scraper et mesurés :

- il colle chaque intertitre au paragraphe suivant (« obligatoires ?Le salarié ») ;
- il déborde sur les sections suivantes : il contient 34 % de lettres et de chiffres de plus que le champ `html` (4 335 412 contre 3 236 472).

Le découpage part donc du champ `html` de chaque section.

## 4. De la page aux blocs

**Trois pièges de la source**, lus dans le code du scraper puis vérifiés :

- le champ `text` colle les intertitres, comme vu plus haut ;
- le champ `anchor` n'est pas un identifiant du site : c'est un slug calculé à partir du titre. Sur le site, les intertitres portent des identifiants tirés au hasard à chaque chargement (772 puis 605 pour le même intertitre) ;
- les références juridiques sont extraites du texte par expressions régulières, donc de façon heuristique.

**Jointure.** Elle se fait sur l'identifiant (`pubId` côté SocialGouv, `doc_id` côté Hugging Face) : 261 fiches sur 261. Une jointure par URL en trouverait 265, car quatre URL figurent deux fois dans SocialGouv sous deux identifiants.

**Extraction.** Le html de chaque section est parcouru dans l'ordre de lecture et converti en blocs typés : intertitre, paragraphe, élément de liste, ligne de tableau. Chaque bloc garde son chemin d'intertitres. Une règle par composant du système de design de l'État (DSFR), chacune justifiée par une mesure :

| Composant | Traitement |
|---|---|
| carte de lien (`fr-card`) | exclue : c'est l'aperçu tronqué d'une autre fiche |
| accordéon (`fr-accordion`) | titre traité comme un intertitre, contenu parcouru dessous |
| encadré, mise en exergue | contenu ordinaire |
| tableau | une ligne par bloc, chaque cellule précédée de son en-tête de colonne |
| `h2` à l'intérieur d'une section | ouvre une nouvelle section |

Le résultat compte 2 451 sections :

- 254 chapôs, placés en tête de fiche, car 2 seulement sur 254 figurent déjà dans une section SocialGouv ;
- 2 121 sections SocialGouv ;
- 76 sections ouvertes par un `h2` interne, que le scraper avait agglomérées.

Le contenu que le scraper a laissé hors de tout `html` est récupéré depuis `text`, phrase par phrase : 18 suites de phrases, 29 709 caractères, dans 8 fiches.

**Réparations.** Le scraper ajoute une espace après chaque point, y compris au milieu d'un nombre ou d'un nom de domaine. Seuls les motifs où cette espace ne peut pas exister sur la page sont réparés : 439 nombres coupés (« 23-21. 640 »), 255 noms de domaine (« gouv. fr ») et 40 préfixes web (« www. »).

**Filtres.** Les règles de la PR #32 sont transposées du passage au bloc, et les cartes de liens sont retirées partout.

| Motif | Blocs | Part des caractères |
|---|---:|---:|
| contenu conservé | 19 767 | 96,05 % |
| carte de lien | 579 | 3,14 % |
| R1, bouton de navigation | 175 | 0,41 % |
| R2, section de liens | 229 | 0,37 % |
| en-tête de tableau repris dans chaque ligne | 21 | 0,04 % |

Un garde-fou compare les cartes exclues aux cartes non vides du html : 579 sur 579. Parmi elles, 91 se trouvent hors des sections de liens de R2, ce qui justifie de les retirer partout.

**Retranscriptions de vidéos.** Elles sont gardées : ce sont de vraies retranscriptions, à leur place et au contenu juridique réel. Elles représentent 1 910 blocs, soit 8,8 % du contenu conservé, dans 30 fiches, et sont signalées par un drapeau.

## 5. Contrôles de couverture

Une extraction qui perd du texte en silence fausserait toute la suite. Les contrôles comparent uniquement les lettres et les chiffres, en minuscules.

| Contrôle | Ce qu'il vérifie | Résultat |
|---|---|---|
| C1, l'extracteur | les blocs de chaque section, conservés ou exclus, reproduisent exactement son html | 2 121 sections sur 2 121 |
| C2, le chapô | les blocs du chapô reproduisent le champ `intro` | 254 sur 254 |
| C3, le périmètre | chaque passage Hugging Face se retrouve dans notre extraction complète | 5 665 sur 5 702 à 100 %, couverture moyenne 99,934 % |
| périmètre de M0 | les passages M0 se retrouvent dans notre contenu conservé | 4 825 sur 5 284 à 100 %, couverture moyenne 94,80 % |

L'écart du dernier contrôle vient du contenu que nous excluons et que M0 garde : les passages les moins couverts appartiennent à des sections de liens (« Pour en savoir plus », « Articles associés », « Pour aller plus loin »).

## 6. Métadonnées de citation

Le cas A3 exige, pour chaque passage, la référence de sa section d'origine et un lien vers le document complet. Trois niveaux sont fournis :

1. l'URL de la fiche, toujours valide ;
2. le titre de section et le chemin d'intertitres, affichables comme un fil d'Ariane ;
3. un lien profond vers le passage, par fragment de texte : l'URL de la fiche, suivie de `#:~:text=` et des premiers mots du passage.

Le fragment de texte est un standard du web, reconnu par Chromium, par Safari depuis la version 16.1 et par Firefox depuis la version 131. Il remplace les ancres SocialGouv, qui ne pointent sur rien.

**Vérification à la main sur 18 liens.** Sur un premier tirage de 12 liens, 9 menaient au passage. Les échecs avaient deux causes : un passage masqué dans un accordéon fermé (2 cas) et une URL renommée depuis l'instantané (1 cas). D'où une règle : un passage qui commence dans un accordéon pointe vers le titre de l'accordéon, qui reste visible. Sur 6 autres liens, 4 menaient au bon endroit, dont un lien d'accordéon qui échouait auparavant. En cas d'échec, le navigateur ouvre la page en haut : le lien se dégrade sans casser. Ces taux portent sur 18 liens et indiquent des causes, pas une fréquence.

**Références juridiques.** Chaque passage reçoit les identifiants LEGIARTI des articles qu'il cite et que SocialGouv a résolus pour sa section. Le lien Légifrance `https://www.legifrance.gouv.fr/codes/article_lc/<LEGIARTI>` a été vérifié sur un exemple.

## 7. Les quatre découpages

| Méthode | Principe | Passages | Tokens moyenne | Médiane | Max |
|---|---|---:|---:|---:|---:|
| M0 | découpage de l'éditeur, filtré comme la PR #32 | 5 284 | 253,1 | 294 | 440 |
| M1 | fenêtre fixe de 235 tokens, pas de 188 (chevauchement de 20 %) | 5 317 | 258,7 | 263 | 329 |
| M2 | découpage structurel depuis le html | 4 240 | 259,1 | 235 | 512 |
| M3 | coupure sémantique au seuil τ = 0,0592 | 4 229 | 260,8 | 231 | 493 |

Les tokens sont comptés sur la chaîne exacte que l'encodeur recevra : préfixe `passage: `, en-tête, texte et tokens spéciaux. Aucun passage ne dépasse la limite de 512 tokens de l'encodeur.

**M0** reproduit le filtrage de la PR #32 : ses effectifs sont contrôlés par assertion, et ses identifiants sont identiques à la sortie de `prepare_corpus.py` sur la branche de Vaneck. C'est la référence à battre.

**M2** applique cinq règles, dans l'ordre :

1. une section ne partage jamais un passage avec une autre ;
2. un intertitre ferme le passage en cours, sauf si celui-ci compte moins de 64 tokens de contenu ;
3. les blocs sont regroupés tant que le passage tient dans le budget de 512 tokens ; une liste ou un tableau forment une unité, avec leur phrase d'introduction ;
4. une unité trop longue est scindée par éléments, puis par phrases, puis en dernier recours par fenêtres de tokens (5 cas) ;
5. chaque passage reçoit un en-tête « fiche > section > intertitres », compté dans le budget.

M2 s'exécute en 2,3 secondes, sans modèle, et un contrôle vérifie qu'aucun bloc conservé n'est perdu.

**M1 et M3** sont calibrés pour avoir la même taille moyenne que M2, à 2 % près. Sans cela, on comparerait des tailles et non des méthodes. Les deux reçoivent un en-tête « fiche > section », comme M2, pour isoler l'effet des frontières.

**M3** encode chaque phrase avec ses voisines et coupe là où la distance cosinus entre deux positions consécutives dépasse τ. Le préfixe `query: ` est mis des deux côtés, parce que la tâche est symétrique, comme l'indique la documentation du modèle. Le signal est faible sur ce corpus : la distance médiane entre positions voisines vaut 0,037, et le seuil calibré tombe au quantile 83,6 %.

**Deux variantes de M2** sont exportées pour l'évaluation : `m2_256`, au budget de 256 tokens (7 009 passages, 174,1 tokens en moyenne), et l'entrée sans en-tête, dans la colonne `entree_sans_entete`. Elles permettront de mesurer au notebook 03 l'effet du budget et celui de l'en-tête.

## 8. Comparaison intrinsèque

Ces indicateurs décrivent les découpages ; ils ne disent pas lequel cherche le mieux.

| Indicateur | M0 | M1 | M2 | M3 |
|---|---:|---:|---:|---:|
| début coupé en milieu de phrase, critère de la PR #32 | 58,9 % | 75,1 % | 0,3 % | 0,4 % |
| fin coupée en milieu de phrase, même critère | 73,7 % | 93,8 % | 11,7 % | 21,1 % |
| passages sur plusieurs sections | non mesuré | 34,1 % | 0 % | 29,0 % |
| texte rattaché à une autre section que celle citée | 23,4 % | 17,9 % | 0 % | 14,2 % |
| redondance dans la fiche | 41,9 % | 36,8 % | 7,6 % | 7,3 % |
| caractères rapportés au contenu | 1,332 | 1,310 | 1,015 | 1,055 |
| index en fp32 | 7,74 Mio | 7,79 Mio | 6,21 Mio | 6,19 Mio |

Lecture :

- le critère textuel de fin coupée surestime les coupures des listes, dont les éléments finissent souvent sans ponctuation. Le critère structurel, qui compare chaque frontière aux fins de bloc et de phrase de l'extraction, ne trouve que 0,1 % de passages M2 coupés en milieu de phrase, au début comme à la fin ;
- pour M0, la référence de section fausse est mesurée sur les passages, par le champ `context` (section 10 du notebook) ; pour M1 et M3, sur les caractères ;
- la redondance de M0 vient du débordement de `text`, celle de M1 de son chevauchement, voulu.

## 9. Proposition : M2 comme méthode de travail

**Ce qui est établi en faveur de M2**, par les mesures ci-dessus :

- la citation est exacte : M2 ne franchit jamais une frontière de section, alors que M1 et M3 citent la mauvaise section pour 14 à 18 % de leur texte, et M0 pour 23,4 % de ses passages. Or la référence de section est une sortie exigée par le cas A3 ;
- les coupures suivent la structure du texte : 0,3 % de passages commencent en milieu de phrase ;
- le coût est nul : aucun modèle, 2,3 secondes, un résultat déterministe ;
- les règles sont simples à expliquer et à défendre.

**Ce qui n'est pas établi** : que M2 donne la meilleure recherche. Le notebook 03 le vérifiera par un test de non-infériorité sur le jeu de questions : M2 reste la méthode de travail, sauf si une autre méthode fait significativement mieux (test exact de McNemar, apparié). Il mesurera aussi l'effet du budget (512 contre 256 tokens) et celui de l'en-tête.

**Gouvernance.** Comme le prévoit le ticket #35, la décision finale reste collective : ces indicateurs et ce protocole sont présentés en Weekly, et les variantes de découpage de Vaneck et de Maïmouna, sur leurs propres branches, pourront être comparées sur le même jeu de questions.

## 10. Mots vides : pourquoi le texte est gardé intact

Aucune méthode ne retire les mots vides. Le texte d'un passage est celui qu'on affiche, qu'on cite et que le lien profond cherche dans la page : il doit rester intact. Un retrait ne pourrait porter que sur une copie, au moment de l'encodage, et il n'est pas souhaitable pour l'encodeur :

- le modèle a été entraîné sur du texte naturel, jamais sur du texte privé de ses mots vides ;
- dans l'étude de Dai et Callan (SIGIR 2019, tableau 3), retirer mots vides et ponctuation des requêtes de description dégrade un modèle BERT (nDCG@20 de 0,529 à 0,503) et améliore un modèle par sac de mots (de 0,404 à 0,427). Leur modèle reclasse des documents en anglais : c'est une indication, pas une preuve ;
- aucun passage ne dépasse la limite de 512 tokens : le gain de tokens ne servirait à rien.

**Mesures du notebook** sur les 4 240 passages M2, avec deux listes courantes figées sur un commit :

| Liste | Mots | Part des mots du corpus retirés | Tokens économisés | Mots décisifs retirés, sur 24 testés |
|---|---:|---:|---:|---|
| Snowball | 154 | 43,4 % | 32,7 % | 6 : ne, pas, sans, sur, pour, par |
| stopwords-iso | 691 | 52,5 % | 39,0 % | 24, dont plus, moins, avant, après, sauf, aucun, peut, doit |

Or 1 202 passages sur 4 240 (28,3 %) contiennent une négation, 478 contiennent « sans » et 523 « au moins ». Sur cinq paires de questions de sens différent, construites à la main, Snowball en confond 2 et stopwords-iso les 5. Par exemple, « Licenciement sans cause réelle et sérieuse » et « Licenciement pour cause réelle et sérieuse » deviennent toutes deux « Licenciement cause réelle sérieuse ». Ces paires illustrent l'effet ; elles ne mesurent pas sa fréquence.

Une liste fondée sur la fréquence ne fait pas mieux : les mots présents dans plus de 30 % des passages incluent « employeur », « salarié », « salariés », « entreprise », « code » et « travail », absents des deux listes. Ce sont les mots qui distinguent « l'employeur peut-il » de « le salarié peut-il ».

La question ne se pose que pour les références lexicales (TF-IDF, BM25) du notebook 03, qui comparera plusieurs variantes sur le jeu de questions : sans liste, Snowball, Snowball sans les négations, coupure par fréquence, avec et sans racinisation.

## 11. Défauts de M0 établis

La PR #32 signalait des passages M0 « mal attribués ». La cause est mesurée : le débordement du champ `text` sur les sections suivantes.

- Pour 1 235 passages sur 5 284 (23,4 %), la section où se trouve réellement le texte n'est pas celle qu'indique le champ `context`. C'est plus que l'estimation d'environ 13,5 % reprise au ticket #35 : notre mesure localise le texte de chaque passage dans le html de la page, par fenêtres de 40 caractères, et retient la section qui en contient le plus.
- 793 passages sont rattachés à une section vidéo, dont 251 seulement s'y trouvent réellement.
- Selon le critère textuel de la PR #32, reproduit à l'identique, 4 537 passages M0 (85,9 %) commencent ou finissent en milieu de phrase.

## 12. Limites connues

- **Indicateurs intrinsèques seulement.** Aucune mesure de qualité de recherche n'est faite ici.
- **Découpeur de phrases.** Une phrase qui finit par une lettre isolée (« catégorie A. ») n'est pas coupée, et certaines vraies frontières après un numéro sont refusées : le tirage aléatoire du notebook en montre des exemples.
- **Liens profonds.** Vérifiés à la main sur 18 liens seulement ; un contrôle automatique sur un échantillon plus large reste à faire. Une URL renommée depuis l'instantané perd le fragment.
- **Références juridiques.** Elles héritent de l'heuristique de SocialGouv.
- **Réparations.** Limitées aux motifs sûrs : des restes d'espaces ajoutées subsistent, par exemple dans des noms de fichiers.
- **Doublons.** 57 passages M2 reprennent mot pour mot le texte d'un autre, mais 3 seulement ont aussi la même entrée d'encodeur, grâce à l'en-tête.
- **Budget.** 5 % des passages M2 dépassent 495 tokens ; la variante à 256 tokens permettra de mesurer si des passages plus courts cherchent mieux.
- **Instantané.** Le corpus date du 11 septembre 2026 ; le site a pu changer depuis.

## 13. Reproduire

Depuis la racine du dépôt, avec `uv` :

```
uv venv --seed --python 3.12 .venv
uv pip sync --python .venv/bin/python scripts/decoupage/requirements-lock.txt
```

Le dossier `.venv` n'est pas dans le `.gitignore` : l'ajouter à `.git/info/exclude` avant tout commit. Le fichier `scripts/indexation/requirements-lock.txt` contient les mêmes dépendances, plus celles du notebook 02 : un seul environnement suffit pour les deux notebooks.

Ouvrir ensuite le notebook dans VS Code, choisir le noyau `.venv` (*Select Kernel*, *Python Environments*), puis tout exécuter. La première cellule affiche l'interpréteur utilisé : un noyau global nommé « python3 » peut pointer vers un autre environnement.

L'exécution prend environ 130 secondes quand les sources et les encodages de M3 sont en cache. Le premier lancement est plus long : il télécharge les sources (46 Mio) et le modèle de M3 (470 Mio dans le cache Hugging Face), puis encode les 28 012 fenêtres de M3, mises en cache ensuite dans `data/decoupage/cache/`.

**Déterminisme.** Deux exécutions donnent les mêmes empreintes de contenu, vérifié le 27 septembre 2026 entre une exécution en script et une exécution dans le noyau Jupyter.

## 14. Schéma des tables exportées

Toutes les méthodes produisent la même table, pour que le notebook 02 les traite de façon identique.

| Colonne | Contenu |
|---|---|
| `passage_id` | identifiant stable : méthode, fiche, rang |
| `pubId`, `titre_fiche`, `url`, `date_maj` | la fiche source |
| `section_idx`, `section_titre`, `section_origine`, `chemin` | la place du passage dans la fiche |
| `sections_couvertes` | sections traversées, plusieurs possibles pour M1 et M3 |
| `entete`, `texte` | à afficher ; `texte` est le contenu seul |
| `entree_encodeur` | chaîne exacte à encoder, préfixe `passage: ` compris |
| `entree_sans_entete` | variante sans en-tête |
| `n_tokens` | tokens de `entree_encodeur`, tokens spéciaux compris |
| `url_citation` | lien profond par fragment de texte |
| `articles` | identifiants LEGIARTI cités et résolus |
| `retranscription` | le passage contient une retranscription de vidéo |
