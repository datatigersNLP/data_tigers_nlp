# Journal d'usage IA : préparation des diapositives 5 et 8 de J3

**Date et responsable.** 9 novembre 2026, Jibril BENSALEM (`JIBZZOU`).

**Outil.** Codex dans ChatGPT Work. Version précise du modèle non vérifiée.

**Objet.** Préparer la partie de Jibril pour les supports J3 (#112), pendant l'attente de la seconde grille humaine du lot v2b. Jibril déclare avoir reçu celle de Maïmouna ; celle de Vaneck manque encore. Aucun verdict n'a été prérempli ou attribué par l'assistant.

**Produit.** `docs/jalons/J3_diapositives_jibril.md` : contenu à afficher pour la diapositive 5, texte oral pour les diapositives 5 et 8, repères pour les questions du jury. La section 8 de `J3_diapositives_mahe.md` reçoit la mesure avant du 9 novembre et ses limites. Les sections 4 et 7 de Mahé sont conservées. Le format reste le Markdown du dépôt : Rémy assemble, Vaneck met en forme. La PR #134 n'est pas modifiée directement.

**Sources et contrôles.** Lecture de #112, du plan de Vaneck, de la PR #134 et de la revue de Mahé, des chiffres vérifiés, du protocole 06 et des fonctions de récupération, préparation du contexte et validation des citations. Les données de la mesure avant proviennent des sorties de Jibril sur le Legion et du journal de séance dans la PR #142 ; aucune lecture directe des fichiers privés n'est revendiquée. Les références à des dates officielles non confirmées restent conditionnelles.

Comparaison des sections 4 et 7 de Mahé : identiques à leur version de départ. Les six effectifs et pourcentages du tableau ainsi que les six intervalles descriptifs ont été contrôlés contre les valeurs fournies. Conversion des deux supports Markdown par `md2tex.convert` réussie, tableaux et listes équilibrés. Compilation PDF non réalisée : `fontspec.sty` et les polices du préambule sont absents de cet environnement. Aucune validation de rendu PDF n'est revendiquée.

**Résultats retenus.** Le contrôle automatique vérifie les références, sans prouver l'exactitude de la réponse. La diapositive 8 expose le compromis de B2 : davantage d'abstentions correctes hors corpus et de nombreuses abstentions à tort dans le corpus. Les dénominateurs excluent les erreurs techniques. Les intervalles à 95 % restent descriptifs, distincts de ceux à 97,5 % prévus pour l'analyse principale après adaptation. Aucun réglage du seuil, du jeu de test ou du protocole n'est proposé à partir des résultats.

**Ce qui a été écarté, et pourquoi.** Reproduire toute la diapositive 8 dans un deuxième fichier créerait deux sources à maintenir, contrairement à la revue de Mahé. Le fichier de Jibril renvoie au tableau commun. Les débits historiques sur prompts courts ne sont pas présentés comme un benchmark du RAG complet. Une citation valide n'est pas qualifiée de garantie contre les hallucinations.

**Validation de l'équipe.** Relecteur responsable : Jibril BENSALEM. Relecture humaine finale non attestée à la rédaction. Mahé doit relire les résultats et la partie commune de la diapositive 8 ; la répartition proposée de l'oral reste à convenir avec lui. Aucune acceptation du lot v2b ni aucun entraînement n'est déclaré.

**Temps d'appropriation constaté.** Non mesuré. Estimation et temps réel non inventés.

**Difficultés rencontrées.** Les supports de la PR #134 contiennent des affirmations dépassées et une affirmation erronée sur l'absence d'hallucination. Les seuls compléments de cette séance concernent les parties 5 et 8. Les autres corrections de la revue de Mahé restent à traiter dans l'assemblage.

**Ajout d'Agent0 demandé par Jibril.** Sur son accord explicite, ajout d'un passage court en fin de diapositive 5, avant la démonstration, sans ajouter de diapositive. Le contenu à afficher est bref et les précisions restent dans les notes, avec un texte oral visant 30 à 45 secondes, non chronométré. Source : bilan Agent0 au 2 novembre, déjà relu dans cette conversation. Les 18 essais, 15 candidats, 3 rejets et 149 tests sont historiques ; aucun test ou essai n'a été relancé pour cet ajout. Les candidats ne sont pas présentés comme validés, aucun hors corpus confirmé n'est revendiqué et les 15 candidats restent exclus de l'entraînement, y compris du lot v2b. Aucun gain du RAG ni benchmark indépendant réalisé n'est attribué à Agent0.
