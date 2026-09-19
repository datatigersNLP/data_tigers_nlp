# Journal d'usage de l'IA

**Équipe** Data Tigers
**Membres** Mahé BEGNIS, Remy RAYANE, Jibril BENSALEM, Vaneck DAGAR, Maïmouna SIGNATE
**Module** NLP 2, projet de fin de module
**Formation** Master 2 Data & IA, FGES, Université Catholique de Lille
**Année universitaire** 2026-2027
**Ouvert le** 18 septembre 2026
**Dernière mise à jour** 19 septembre 2026, session 8

**Objet.** Ce journal consigne l'usage des assistants IA sur le projet, conformément à la règle du sujet : « L'usage d'assistants IA est autorisé et encouragé. En contrepartie, le journal des usages doit être tenu, et tout membre de l'équipe peut être interrogé en soutenance sur n'importe quelle portion du code produit. »

**Responsable de la tenue** Mahé BEGNIS. Chaque membre renseigne ses propres sessions selon le modèle donné en section 5.

---

## 1. Principes d'usage retenus par l'équipe

L'équipe utilise l'IA pour trois choses, et refuse de l'utiliser pour une quatrième.

**Ce pour quoi nous l'utilisons.**

1. **Réflexion sur l'architecture et les décisions.** Explorer les options, en peser les conséquences, faire émerger les contraintes que nous n'avions pas vues. Exemple concret : le choix du couple de cas d'usage A3 et B1 a été instruit en comparant les dix cas proposés sur sept critères, ce qui a fait apparaître que A3 constitue la couche de récupération de B1 et économise 5 à 8 jours-homme.
2. **Challenger nos idées.** Nous soumettons nos décisions à une critique argumentée avant de les figer. Exemple : notre première répartition des tâches présentait un écart de charge d'un facteur 3,3 entre le membre le plus chargé et le moins chargé, et plaçait le même binôme sur les trois domaines les plus critiques. Le chiffrage de cette répartition nous a conduits à la revoir.
3. **Accélérer les tâches à faible valeur ajoutée.** Recherche de jeux de données, relevé de tailles de fichiers, lecture de documentations, mise en forme. Exemple : l'identification du corpus a comparé en quelques minutes une dizaine de sources publiques avec leur volumétrie, leur licence et leur date de mise à jour, là où la recherche manuelle aurait pris plusieurs heures sans garantie d'exhaustivité.

**Ce pour quoi nous refusons de l'utiliser.** Produire du code ou une analyse que personne dans l'équipe ne saurait expliquer. Le sujet prévient qu'une réponse insuffisante en soutenance affecte l'évaluation de toute l'équipe. Toute production assistée passe donc en revue par le binôme du domaine concerné, et le relecteur doit savoir l'exposer sans support.

**Règle de vérification.** Aucune affirmation produite par l'assistant n'est reprise sans mesure. Les chiffres des livrables proviennent de commandes exécutées, dont la méthode est décrite en annexe de chaque document. Cette exigence a permis de détecter plusieurs erreurs, listées en section 4.

---

## 2. Outils déclarés

| Outil | Nature | Membres | Usage |
|---|---|---|---|
| Claude Opus 5 | modèle de langage, fenêtre de contexte de 1 million de tokens | Mahé BEGNIS | architecture, décisions, recherches, critique, rédaction assistée |
| Claude Code | environnement de développement augmenté, exécute le modèle ci-dessus | membres disposant d'un abonnement | exécution de commandes, lecture de fichiers, mesures |
| Google Antigravity | plateforme d'agents, alternative gratuite | les autres membres | même usage, divergence déclarée au jalon J2 |

La divergence entre Claude Code et Google Antigravity est déclarée dans le rapport de jalon J2. Elle est motivée par le fait que l'abonnement Claude n'est pas détenu par toute l'équipe. Elle constitue aussi un terrain de comparaison qui alimentera la section des cinq outils novateurs du rapport final.

---

## 3. Sessions

### Session 1, 18 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Audit du sujet, étude comparative des dix cas d'usage, préparation de la réunion de cadrage.

**Produit.** `01_AUDIT_SUJET_PROJET.md` (4 180 mots), `02_ETUDE_COMPARATIVE_CAS_USAGE.md` (4 877 mots), `03_SUPPORT_REUNION_J2.md` (7 962 mots).

**Mesures exécutées.** Lecture intégrale du sujet (20 pages, 4 692 mots). Comptage des notions du module sur 11 fichiers de cours et de TP dédoublonnés, soit 245 851 caractères. Relevé des tailles de modèles ONNX et GGUF par l'API Hugging Face. Lecture des limites GitHub dans la documentation officielle. Relevé matériel du poste de travail.

**Résultats retenus.** Les notions RAG, ONNX, Transformers.js, quantisation et adaptation de modèle totalisent zéro occurrence dans les supports du module, alors que le projet les exige. Aucun modèle ONNX multilingue prêt à l'emploi ne tient sous la limite GitHub de 100 Mio. Le sujet affirme que l'architecture BiLSTM-CRF a été étudiée en journée 2, alors que le CRF n'apparaît qu'une fois dans le notebook, dans une cellule de prolongements facultatifs.

**Ce que l'équipe a validé.** Le choix du couple A3 et B1, après confrontation des trois scénarios proposés.

**Temps d'appropriation.** Immédiat pour la lecture et le comptage. La mise au point du protocole de mesure a demandé plusieurs itérations, décrites en section 4.

### Session 2, 18 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Conversion du support de réunion en PDF composé avec LaTeX.

**Produit.** Chaîne de conversion dans `latex/` : `md2tex.py` (259 lignes), `build.py` (123 lignes), `preambule.tex` (149 lignes), plus le PDF de 19 pages.

**Choix technique.** Un convertisseur dédié a été écrit plutôt que d'utiliser un outil générique, afin de dimensionner les tableaux par mesure. Avant de produire le document, XeLaTeX mesure la largeur réelle du plus large fragment insécable de chaque colonne, et ces largeurs pilotent la répartition. Le nombre de débordements est passé de 63, dont un de 116 points, à zéro.

**Ce que l'équipe a validé.** Le rendu, par relecture visuelle page par page. Trois défauts invisibles dans le journal de compilation ont été trouvés à cette occasion, listés en section 4.

### Session 3, 18 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Évaluation du dépôt `affaan-m/ECC`, proposé comme outil candidat pour la section des cinq outils novateurs.

**Mesures exécutées.** Licence, nombre de contributeurs, cadence des publications, étoiles, forks, téléchargements npm, contenu de `install.sh` et de `.env.example`.

**Résultats retenus.** Projet sain : licence MIT, 336 contributeurs, publications régulières. Mais 261 879 étoiles pour seulement 8 840 téléchargements npm hebdomadaires, alors que des bibliothèques comparables en font plusieurs millions. Conclusion transmise à l'équipe : cet outil ne nous distinguera pas, puisqu'il est au 16e rang mondial des dépôts les plus étoilés et que ses voisins immédiats au classement sont deux concurrents du même créneau. Ce qui distinguera notre rapport est la qualité de la critique, non le choix de l'outil.

**Décision de l'équipe.** Report du choix du panier d'outils, qui n'est pas un attendu du jalon J2.

### Session 4, 19 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Instruction des décisions du jalon J2, puis rédaction du rapport.

**Produit.** `04_JALON_J2_DECISIONS.md` (6 703 mots), `05_RAPPORT_J2.md` (4 104 mots) et son PDF de 12 pages.

**Mesures exécutées.**

| Mesure | Méthode | Résultat retenu |
|---|---|---|
| Faisabilité de l'exécution navigateur | page statique servie en local, Chromium piloté par Playwright, 20 passes après chauffe | 19,8 ms par requête, 3 052 ms au premier chargement, 568 ms en cache, 135,6 Mio de charge utile |
| Empreinte mémoire des modèles locaux | calcul du cache KV à partir des fichiers de configuration officiels | Qwen2.5-7B à 56,0 Kio par token, soit 2,3 à 3,4 fois moins que les autres candidats |
| Recherche de corpus | interrogation des API Hugging Face et data.gouv.fr, contrôle d'accessibilité de dix sources | `AgentPublic/travail-emploi`, 5 702 passages, 29,6 Mio, licence Etalab 2.0 |
| Dimensionnement du jeu de référence | calcul de puissance statistique | 60 questions donnent un intervalle de plus ou moins 10,1 points, insuffisant pour distinguer 0,80 de 0,85 |

**Apport le plus net.** La recherche de corpus. Dix sources publiques ont été testées pour leur accessibilité réelle, leur volumétrie, leur licence et leur fraîcheur, en quelques minutes. Cette recherche a écarté les documents internes de la formation, absents du sitemap public, et fait émerger un jeu de données administratif français dont la structure correspond exactement aux besoins du cas A3.

**Ce que l'équipe a validé.** Le corpus, le modèle du volet B, la machine cible, le protocole d'évaluation et la répartition des tâches, après discussion point par point.

### Session 5, 19 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Vérification en lecture seule de l'état réel du dépôt GitHub, avant envoi du rapport.

**Résultats.** Organisation et dépôt créés, cinq membres inscrits, enseignant collaborateur en lecture, six tickets ouverts et assignés. En revanche, aucun milestone n'existe et un seul label personnalisé est défini, alors que le rapport en annonçait respectivement trois et dix.

**Conséquence.** La section 2 du rapport a été reprise pour décrire l'état vérifié, et la structure du board y figure désormais comme structure retenue et non comme état de fait. Une procédure de création des milestones et des labels a été établie.

**Enseignement.** C'est la vérification qui a évité d'envoyer un document contenant deux affirmations que l'enseignant aurait pu infirmer en un clic.

### Session 6, 19 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Création des milestones et des labels du board, en écriture sur le dépôt.

**Vérification préalable.** L'identité du jeton a été contrôlée avant toute écriture : compte `mahebegnis`, aucune variable d'environnement ne la surchargeant. Les opérations passent par l'API et non par des commits, donc sans attribution de co-auteur.

**Produit.** Quatre milestones, un par jalon noté, avec échéance et barème. Onze labels de projet répartis sur trois axes indépendants. Six tickets rattachés et étiquetés. Le label `Jalon 2`, rendu redondant par le milestone du même nom, a été retiré.

**Difficulté rencontrée, et ce qu'elle apprend.** Deux pièges se sont présentés.

Le premier : après le retrait d'un label, la requête de contrôle a renvoyé un état périmé indiquant que deux tickets le portaient encore. Un garde-fou conditionnait la suppression du label à un décompte nul, et a donc refusé d'agir. Une lecture directe a montré que le retrait avait bien eu lieu. **Une lecture immédiatement consécutive à une écriture n'est pas fiable sur cette API**, et une condition de sécurité doit échouer vers l'inaction, ce qui a été le cas.

Le second : la commande `gh api` bascule silencieusement de GET en POST dès qu'un champ `-f` est fourni. Une requête destinée à lire les tickets d'un label a donc tenté d'en créer un, et n'a échoué que parce que le titre manquait. **Ce comportement n'est pas signalé à l'usage**, et il aurait pu écrire dans le dépôt sans intention. À retenir pour la section des outils novateurs.

**Ce que l'équipe a validé.** La liste des milestones, celle des labels, et le choix de réutiliser le label `documentation` existant plutôt que d'en créer un doublon.

**Temps d'appropriation.** Quelques minutes pour la syntaxe, vérifiée sur l'aide en ligne avant exécution. L'essentiel du temps est allé aux contrôles après écriture.

### Session 7, 19 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Mise en place de la structure du dépôt, publication des livrables du jalon J2.

**Vérification préalable.** Identité du jeton contrôlée avant toute écriture. Les commits portent l'auteur et le validateur Mahé Begnis, avec l'adresse sans réponse du compte GitHub, ce qui les rattache au compte sans exposer d'adresse personnelle. L'identité a été passée commande par commande, sans modifier la configuration git de la machine.

**Produit.** Répertoire `docs/` organisé en jalons, journal, suivi, études et chaîne LaTeX. Fichier `README.md` décrivant l'organisation, les branches et les conventions de commit. Trois branches publiées, `main`, `dev` et `docs/5-rapport-jalon-j2`, et le tag `jalon-j2`.

**Deux difficultés rencontrées.**

Le système de fichiers de macOS est insensible à la casse. La commande destinée à supprimer l'ancien `readme.md` a détruit le `README.md` écrit quelques secondes plus tôt, les deux noms désignant le même fichier. Détecté par le contrôle systématique qui suit chaque écriture, le fichier a été réécrit, et le changement de casse forcé en deux étapes avec `git mv`, seule méthode fiable sur ce type de système.

Le clone local pointait encore vers l'ancienne adresse personnelle du dépôt, périmée depuis son transfert à l'organisation. GitHub redirige silencieusement, ce qui rend l'erreur invisible à l'usage. L'adresse a été corrigée avant toute publication.

**Ce que l'équipe a validé.** La structure du dépôt, la stratégie de branches, et le choix de ne pas créer de branche de documentation permanente.

**Temps d'appropriation.** Faible pour les commandes, l'essentiel du temps allant aux contrôles après chaque écriture.

### Session 8, 19 septembre 2026, Mahé BEGNIS, Claude Opus 5 via Claude Code

**Objet.** Deux questions soulevées par l'équipe à la relecture du rapport. Le sujet valorise un modèle entraîné par nous, or le volet A repose sur un encodeur préexistant. Et l'équipe souhaite intégrer un modèle français au volet B.

**Mesure exécutée.** Faisabilité d'un ajustement fin contrastif de l'encodeur sur la machine de référence. Chargement du modèle, construction d'un lot de 32 paires question-passage, passe avant et arrière avec optimiseur, dix pas chronométrés après chauffe, sur le processeur graphique.

**Résultat.** Un pas prend 89 ms. Trois époques sur 17 106 paires demandent 2,4 minutes. Le coût de calcul ne fait pas obstacle, ce qui ouvre une voie que nous pensions fermée. Le relevé confirme au passage un calcul antérieur : 117,7 millions de paramètres mesurés contre 117,3 prédits, soit 0,3 pour cent d'écart.

**Second point, le modèle français.** Quatre modèles Mistral ont été comparés sur leur licence, leur taille quantifiée et leur cache par token. `Mistral-7B-Instruct-v0.3` est retenu comme second modèle : même classe de taille que le principal, ce qui rend la comparaison valide, et tient dans le budget mémoire à toutes les longueurs de contexte. `Mistral-Nemo-Instruct-2407`, au français probablement meilleur, atteint 12,6 Gio à 32 768 tokens et sort du budget.

**Difficulté rencontrée.** Le premier lancement du banc d'essai s'est terminé sans aucune sortie, le tube vers une commande de filtrage ayant retenu l'affichage jusqu'à la fin du processus, lequel a été interrompu. Relancé en écriture directe vers un fichier, avec vidage explicite du tampon, il a produit le résultat. **Un banc d'essai long ne doit jamais écrire à travers un tube.**

**Ce que l'équipe a validé.** L'ajustement fin comme réponse à la valorisation du sujet, et l'ajout du modèle français en comparaison.

---

## 4. Erreurs détectées par la vérification

Cette section est tenue volontairement. Elle documente ce que la relecture systématique a permis de rattraper, et constitue le principal argument en faveur de notre méthode.

| Date | Erreur | Détection | Correction |
|---|---|---|---|
| 18/09 | Comptage des notions faussé par une recherche en sous-chaîne, qui comptait « rag » dans « paragraphe » | incohérence des ordres de grandeur | comptage refait avec frontières de mots |
| 18/09 | Expression régulière renvoyant zéro occurrence de LSTM alors qu'il y en avait 133 | contradiction avec un autre compteur | passage à une implémentation Python vérifiée |
| 18/09 | Nombre de fichiers audités annoncé à 12, réel 14 dont 3 quasi-doublons | recomptage explicite | corpus de référence ramené à 11 fichiers dédoublonnés |
| 18/09 | Classification des paquets Python ignorant les roues `universal2`, donc deux paquets déclarés à tort incompatibles | contrôle manuel des étiquettes | reclassement complet |
| 18/09 | Rang mondial du dépôt ECC annoncé au 13e, réel 16e | comptage des dépôts plus étoilés | corrigé, et l'argument en est sorti renforcé |
| 18/09 | Tirets cadratins rendus en « --- » dans les tableaux du PDF | relecture visuelle du rendu | caractères Unicode utilisés directement |
| 19/09 | Taille d'un modèle annoncée par l'API à 0,5 Mio, réelle 294,6 Mio, les poids étant dans des fichiers externes | invraisemblance pour un modèle de 300 millions de paramètres | mesure des fichiers externes |
| 19/09 | Charge utile du navigateur relevée à 5,5 Mio pour un modèle de 112,8 Mio | invraisemblance | les ressources d'origine tierce ne déclarent pas leur taille, mesure refaite fichier par fichier, résultat 135,6 Mio |
| 19/09 | Seuil de réussite Recall@5 proposé à 0,80 sans fondement | recherche des résultats publiés du modèle : 23 mesures de récupération, toutes en anglais | seuils reformulés en écarts appariés face à une baseline |
| 19/09 | Conclusion hâtive sur l'absence de board, tirée d'une sortie vide | la sortie vide masquait une erreur de périmètre d'autorisation | aucune conclusion tirée, limite déclarée dans le rapport |
| 19/09 | Rapport annonçant trois milestones et dix labels inexistants | consultation du dépôt | section 2 alignée sur l'état vérifié |
| 19/09 | Lecture immédiatement consécutive à une écriture renvoyant un état périmé | garde-fou conditionnant la suppression à un décompte nul | suppression refusée puis reprise après contrôle direct |
| 19/09 | `gh api` basculant de GET en POST dès qu'un champ `-f` est fourni | échec en 422 sur un titre manquant | requêtes de lecture écrites sans `-f` |
| 19/09 | Suppression de `readme.md` détruisant le `README.md` écrit juste avant, le système de fichiers étant insensible à la casse | contrôle systématique après écriture | fichier réécrit, casse forcée en deux étapes avec `git mv` |
| 19/09 | Clone local pointant vers l'ancienne adresse du dépôt, périmée depuis son transfert à l'organisation | lecture de l'adresse distante avant publication | adresse corrigée avant tout envoi |
| 19/09 | Banc d'essai terminé sans aucune sortie, le tube de filtrage retenant l'affichage | fichier de sortie vide alors que le processus était terminé | écriture directe vers un fichier, tampon vidé explicitement |

**Bilan intermédiaire.** Seize erreurs ou pièges détectés et traités en deux jours. **Cinq d'entre elles figuraient déjà dans un livrable rédigé** et ont été rattrapées avant l'envoi : le nombre de fichiers audités, le rang du dépôt ECC, le seuil de réussite sans fondement, les milestones et labels inexistants, et le rendu des tirets dans le PDF composé.

Aucune n'a été trouvée par simple relecture du texte. Toutes l'ont été par confrontation à une mesure, à un calcul indépendant ou à l'inspection visuelle du rendu. C'est la méthode qui les a fait apparaître, pas l'attention.

---

## 5. Modèle de saisie

Chaque membre ajoute ses sessions selon ce modèle, le jour de l'usage. Les éléments ne se reconstituent pas après coup.

```
### Session N, date, prénom NOM, outil et modèle

**Objet.**
**Produit.**
**Mesures exécutées.**
**Résultats retenus.**
**Ce qui a été écarté, et pourquoi.**
**Ce que l'équipe a validé, et par qui.**
**Temps d'appropriation constaté.**
**Difficultés rencontrées.**
```

Deux règles de tenue :

1. Une session non consignée le jour même est considérée comme non consignée. Le sujet valorise le temps d'appropriation constaté et les conditions dans lesquelles un outil échoue, qui sont les premiers éléments oubliés.
2. Toute production assistée porte le nom de son relecteur. Sans relecteur nommé, elle n'entre pas dans un livrable.

---

## 6. Ce que ce journal alimentera

Trois sections du rapport final s'appuieront directement sur ce document.

- **Analyse technique.** Les mesures consignées ici fournissent les chiffres de coût, de latence et de qualité demandés.
- **Retour d'expérience.** La section 4 documente les difficultés réelles et leur résolution, que le sujet demande de traiter de façon factuelle.
- **Cinq outils novateurs.** Les temps d'appropriation, les échecs et les comparaisons entre outils consignés au fil de l'eau constituent la matière de cette section, qui vaut jusqu'à trois points et dont la grille valorise au moins une critique argumentée.
