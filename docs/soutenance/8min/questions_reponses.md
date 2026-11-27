# Questions du jury : réponses préparées

**Établi le** 26 novembre 2026 pour la soutenance du 30 novembre. Chaque réponse tient en deux à quatre phrases, avec ses chiffres et sa source ; l'annexe du support qui l'illustre est indiquée (touche A, puis le numéro). « Qui répond » suit les domaines du classeur de suivi : à ajuster en équipe.

**Règles pour répondre**
- Commencer par la réponse, puis le chiffre, puis la limite.
- Ne jamais présenter une citation comme une preuve d'exactitude, ni un résultat descriptif comme démontré.
- Si on ne sait pas : le dire, et dire où l'information se trouve (rapport, protocole, ticket).

---

## 1. Le projet et ses choix

**Pourquoi deux volets, et pas un seul assistant ?** (Mahé)
Le sujet impose de comparer un modèle maîtrisé, servi dans le navigateur, et un grand modèle emprunté, adapté par l'équipe. Les deux répondent au même besoin avec des compromis opposés : le site ne coûte rien, répond en 21 ms et tout y est vérifiable ; l'assistant rédige une réponse, mais demande une machine et une douzaine de secondes. Ils partagent le découpage, l'encodeur et l'index.

**Pourquoi les fiches du ministère, et pas le Code du travail ?** (Maïmouna)
Les fiches pratiques sont rédigées pour des salariés et des employeurs, avec des sections stables, et publiées sous Licence Ouverte Etalab 2.0 par SocialGouv. Nous en utilisons un instantané figé du 11 septembre 2026 : 261 fiches, découpées en 4 240 passages d'au plus 512 tokens, chacun précédé de son en-tête (fiche, section, intertitres). Le Code et les conventions collectives ne sont pas interrogés, et l'interface le dit.

**Pourquoi avoir refait le découpage ?** (Vaneck)
Le jeu publié sur Hugging Face débordait d'une section sur l'autre et collait les intertitres aux paragraphes. Nous avons repris la source officielle de SocialGouv, qui donne le texte de chaque fiche section par section (#35).

**Pourquoi multilingual-e5-small ?** (Remy)
Il est multilingue, assez petit pour un navigateur (118 millions de paramètres, vecteurs de 384 nombres), et sous licence MIT. 81,6 % de ses poids sont la table du vocabulaire : en retirant les alphabets non latins, le modèle compressé passe de 112,8 à 65,7 Mio, sans changer un seul résultat sur 822 requêtes de contrôle (annexe A13 pour le poids téléchargé).

**Pourquoi Qwen2.5-7B-Instruct ?** (Mahé)
Poids ouverts sous licence Apache 2.0, bon en français, et 4,36 Gio une fois compressé en 4 bits : il tient sur le Mac de 24 Gio et sur un GPU de 8 Gio pour l'inférence. Un modèle plus gros n'aurait pas pu être adapté sur nos machines (annexe A13).

**Pourquoi tout en local, sans API ?** (Jibril)
Le sujet demande un volet emprunté mais exécuté par l'équipe, et la confidentialité y gagne : aucune question ne quitte la machine. Le prix est la latence, 11,8 s par réponse en médiane, et la dépendance à une machine dédiée.

---

## 2. Volet A, la recherche dans le navigateur

**Comment le site trouve-t-il les passages ?** (Vaneck)
Le navigateur découpe la question en pièces, l'encodeur la transforme en un vecteur de 384 nombres, puis le compare par produit scalaire aux 4 240 vecteurs des passages, calculés une fois pour toutes. Les 10 plus proches sont affichés, regroupés par fiche, avec le lien vers la source. Aucune requête n'est envoyée après le chargement.

**Qu'avez-vous gagné en ajustant l'encodeur ?** (Remy)
Sur les 73 questions humaines du lot de test, le bon passage est dans les 5 premiers pour 63,0 % des questions, contre 43,8 % avec l'encodeur de base : +19,2 points [+9,7 ; +30,4], un gain démontré. Sur le CDTN, jeu externe, +4,9 points [+0,6 ; +9,3]. Avec 10 passages regroupés par fiche, une fiche pertinente est affichée pour 93,2 % des questions.

**Avec seulement 109 paires d'entraînement ?** (Remy)
Oui : 109 questions écrites par Qwen pour des passages hors des 61 fiches du test, 2 époques, 185,5 s sur processeur. Nous avons ensuite essayé 2 289 puis 2 420 questions synthétiques : aucune version n'a fait mieux sur les questions humaines (annexe A5).

**Pourquoi la version entraînée sur les questions de Claude n'est-elle pas servie, alors qu'elle gagne 12,4 points ?** (Mahé)
Elle ne gagne que sur le jeu v2, écrit par Claude lui aussi ; elle recule sur le CDTN (−2,2) et sur nos questions humaines (−5,5), et laisse passer plus de questions hors corpus. Elle a appris le style de Claude, pas nos fiches. La règle de l'amendement A3, écrite avant toute génération, l'écarte (annexe A5).

**Comment le site refuse-t-il une question hors sujet ?** (Vaneck)
Si le meilleur score de similarité est sous 0,7683, le site refuse et propose d'afficher quand même les passages ; jusqu'à 0,8140, il avertit d'une correspondance moins nette. Ce seuil est le 5e centile des scores de 479 questions externes (CDTN), fixé sans regarder le test. Sur le lot de test, il garde 70 questions couvertes sur 73 et refuse 10 questions hors corpus sur 24, 13 autres étant signalées (annexe A6).

**Votre site ne trouve pas la réponse à la question de la diapositive 2 ?** (Jibril)
Non : le site, qui ne cherche que par le sens, met une autre fiche en tête et avertit d'une correspondance moins nette (essai du 26 novembre). Dans la chaîne du volet B, la recherche par le sens classe le bon passage, sur le congé sans solde, 59e ; BM25 le classe 2e, la fusion des rangs 6e, et le reclasseur 1er (diapositive 7). C'est ce qui justifie la recherche hybride du volet B ; nous avons mesuré la même fusion pour le site, sans gain démontré, et y avons renoncé (#173).

**Pourquoi ne pas mettre BM25 dans le site ?** (Mahé)
La fusion était permise par la règle (+5,0 points sur le jeu v2, +2,6 sur le CDTN), mais aucun gain n'est démontré et nos questions humaines reculent de 6,8 points. Le portage en JavaScript n'apportait donc rien de démontré au site.

**Le modèle du navigateur calcule-t-il comme en Python ?** (Remy)
Pas exactement : avec l'encodeur de base, le même modèle compressé sur 8 bits donne le même premier résultat que le calcul exact pour 91,8 % des requêtes dans le navigateur, contre 96,5 % en Python ; 93,6 % dans le navigateur avec l'encodeur ajusté servi. Nous l'avons mesuré, et les chiffres publiés sont ceux du navigateur, là où le modèle est servi.

---

## 3. Volet B, l'assistant local

**Comment l'assistant répond-il ?** (Jibril)
Une recherche hybride fusionne les rangs de la recherche par le sens et de BM25 ; un reclasseur relit les 20 premiers candidats avec la question ; les 10 meilleurs, numérotés P1 à P10, forment le contexte. Qwen adapté rédige une réponse qui cite ses passages ; chaque citation est vérifiée dans le contexte. Si les passages ne répondent pas, il doit s'abstenir.

**Pourquoi un reclasseur ?** (Jibril)
La recherche par le sens donne des scores très proches entre passages ; le reclasseur lit la question et le passage ensemble. C'est le seul des trois reclasseurs testés qui apporte un gain : +7,7 points à 5 passages. Sur le jeu v2, la chaîne complète fournit un passage pertinent pour 86,0 % des questions, contre 57,0 % pour la recherche par le sens seule (+28,9 points, démontré).

**Pourquoi la fusion des rangs avec k = 60 ?** (Jibril)
C'est la valeur de l'article de Cormack et al. (2009), jamais réglée sur nos données : la fusion n'additionne que des inverses de rangs, sans comparer des scores d'échelles différentes.

**Pourquoi gardez-vous les négations dans BM25 ?** (Remy)
En droit, « ne », « pas » et « sans » changent le sens : nous les retirons de la liste des mots vides Snowball (BM25 V3).

**Pourquoi 10 passages et pas 5 ?** (Jibril)
Les 10 premiers contiennent les 5 premiers : aucune question n'est perdue, et le gain va de 4 à 14 points de questions avec un passage pertinent dans le contexte. Le prix : 3 953 tokens lus au lieu de 2 179, et un contexte moins précis. Le nombre a été fixé le 9 novembre, avant la mesure ; 15 passages approcheraient le plafond du prompt.

**Comment avez-vous adapté Qwen ?** (Mahé)
Par LoRA : un petit correctif de 11,5 millions de paramètres, 0,15 % du modèle, entraîné sur le Mac avec 218 exemples dans les conditions réelles, où la réponse recopie le passage et le cite, ou s'abstient. Un premier lot a été refusé à la relecture (8 faux sur 30), le second accepté (3 sur 30) (annexe A9).

**Ollama ne lit pas les LoRA : comment servez-vous l'adaptateur ?** (Mahé)
Nous fusionnons le correctif dans les poids d'origine en bf16, puis nous compressons en Q4_K_M. Simulée, l'adaptation survit à cette recompression à 97,5 à 99,9 %, contre 47 à 62 % en partant de la base déjà compressée. Le témoin T passe par exactement la même chaîne, avec un correctif nul (annexe A10).

**L'adaptation sert-elle vraiment ?** (Mahé)
Oui, sur ce qu'elle visait : dans la chaîne de démonstration, sur le jeu v2, 52,9 % des réponses citent un passage pertinent avec le modèle adapté, contre 10,1 % avec le modèle d'origine, qui s'abstient à tort sur 76,5 % des questions du corpus. Sur le lot de test, avec l'ancienne chaîne : de 13,9 à 25,0 % (+11,1 points, démontré) (annexe A3).

**Les réponses sont-elles plus exactes ?** (Maïmouna ou Vaneck)
Non. Jugées à l'aveugle par Maïmouna et Vaneck, sur 20 réponses par modèle, celles du modèle adapté sont nettement mieux appuyées sur leurs passages (20 et 19 sur 20, contre 11 et 12), mais pas plus exactes (6 et 5 sur 20 entièrement exactes, contre 12 et 8, écart non démontré). Le modèle adapté, entraîné à recopier un passage, donne des réponses plus souvent incomplètes ; le modèle d'origine généralise ou confond (annexe A4).

**Dans la vidéo, la réponse sur les congés payés donne 2,5 jours par mois, pas le nombre de jours par an ?** (Jibril)
Exact : la réponse est juste et citée, mais incomplète. Le total annuel, 30 jours ouvrables (cinq semaines) pour une année complète, figure dans un autre passage fourni au modèle (P1, relevé par Maïmouna sur la #158). C'est le défaut que les juges ont relevé chez le modèle adapté : entraîné à recopier un passage, il s'arrête souvent au premier qui répond.

**Pourquoi l'accord entre vos juges est-il si faible ?** (Vaneck)
Kappa de 0,36 sur l'exactitude : « partiellement exacte » est une notion difficile, et nous ne sommes pas juristes. Nous ne retenons donc que ce qui va dans le même sens chez les deux juges. Le critère « conditions et exceptions » est inexploitable : les juges n'ont pas compris « sans objet » de la même façon.

**L'assistant s'abstient-il quand il le faut ?** (Jibril)
Sur le jeu v2, la chaîne de démonstration s'abstient correctement sur les 39 questions hors corpus évaluées. Limite : ces questions sont hors corpus au sens du protocole, c'est-à-dire qu'un juge d'IA n'a trouvé de réponse dans aucun des 10 premiers passages d'une recherche hybride ; ce contrôle ne prouve pas l'absence de réponse dans tout le corpus. L'autre défaut est l'inverse : 27,7 % d'abstentions à tort sur les questions du corpus.

**Il ne répond pas à la question de la diapositive 2 ?** (Mahé)
Non, il s'abstient (essai du 26 novembre), alors que le reclasseur place le bon passage en tête : c'est une abstention à tort, le défaut que nous mesurons par M2. La démonstration utilise des questions choisies après essai, et nous le disons : c'est une illustration, pas une mesure.

**Pourquoi 12 secondes par réponse ?** (Jibril)
10 passages et un reclasseur : 4 121 tokens de prompt en médiane, contre environ 1 720 pour l'ancienne chaîne à 5 passages, qui répondait en 4,9 s. Le reclasseur prend environ 2 s sur le processeur ; Qwen génère environ 47 tokens par seconde sur le Mac.

---

## 4. Évaluation et statistiques

**Comment savez-vous qu'un passage est pertinent ?** (Mahé)
Nos questions humaines ont un extrait annoté ; un passage est pertinent s'il partage avec cet extrait un fragment continu couvrant au moins la moitié de l'extrait (règle D4). Cette règle ne connaît qu'un passage par question : nos chiffres sont des minorants. Le protocole 09 ajoute les passages que deux juges d'IA disent pertinents, ce qui donne une fourchette (annexe A11).

**Votre jeu v2 est écrit par Claude : n'est-ce pas circulaire ?** (Mahé)
C'est un risque réel, et nous l'avons observé : l'encodeur entraîné sur des questions de Claude ne gagne que sur ce jeu. Le jeu v2 n'a été lu par aucun système avant d'être figé, avec l'autorisation écrite de l'enseignant ; notre jeu humain (73 questions) et le CDTN restent les contrôles, et nous ne concluons que si les jeux humains vont dans le même sens.

**Quels tests statistiques utilisez-vous ?** (Remy)
Les systèmes répondent aux mêmes questions : test exact de McNemar sur les questions discordantes. Les questions d'une même fiche ne sont pas indépendantes : intervalles élargis par l'effet de plan (Obuchowski). Plusieurs hypothèses à la fois : correction de Holm. Au jalon J2, test de non-infériorité avec une marge de 15 points (annexe A7).

**Pourquoi écrire les règles avant de mesurer ?** (Mahé)
Pour ne pas choisir sur les résultats. Chaque protocole est figé avec son empreinte avant la mesure ; la règle a fait renoncer à des choix que nous aimions : l'encodeur de base est resté servi un mois, une consigne plus performante a été écartée, la v3-C n'est pas servie.

**Qu'est-ce que M4 ?** (Jibril)
La part des réponses qui citent un passage pertinent. C'est une mesure de traçabilité : elle ne dit pas que la réponse est exacte. C'est pourquoi l'exactitude a été jugée à part, par des humains.

**Pourquoi des juges d'IA ?** (Mahé)
Pour le jeu v2 et pour élargir la mesure des passages pertinents (617 paires à juger deux fois), avec l'autorisation de l'enseignant. Ils sont déclarés comme tels, contrôlés par des cas dont la réponse est connue (40 positifs sur 40, aucun négatif accepté), et leurs résultats restent des majorants provisoires. Les jugements d'exactitude, eux, sont humains.

---

## 5. Confidentialité, sécurité, organisation

**Et le RGPD ?** (Vaneck)
Le site exécute le modèle dans le navigateur : aucune question n'est envoyée, ni cookie ni statistiques ; seul GitHub Pages, l'hébergeur, journalise les adresses IP pour sa sécurité. L'assistant tourne sur la machine, et dans la configuration de la démonstration ne journalise ni question ni réponse, ce que nous avons vérifié dans ses journaux. Chaque interface a une fenêtre « Confidentialité et mentions » (annexe A12).

**Avez-vous traité la sécurité des dépendances ?** (Jibril)
Les versions sont épinglées ; une alerte récente vise le serveur de développement de Vite 8.3.0 à 8.3.2, utilisé pour construire le site : elle ne touche pas le site publié, qui est statique. La mise à jour est prévue après la soutenance.

**Comment vous êtes-vous organisés ?** (Jibril)
Un ticket et une branche par tâche, des pull requests vers dev avec une approbation obligatoire, dev et main protégées, des jalons et un classeur de suivi des charges. Les réunions qui n'ont pas eu lieu sont documentées comme telles, avec les décisions écrites qui les ont remplacées.

**Comment le travail a-t-il été réparti, et les contributions sont-elles équilibrées ?** (Mahé)
Nous avons renoncé à comparer des heures, estimées après coup par trois méthodes différentes. La répartition est mesurée dans le dépôt, au 26 novembre : sur 462 commits, Mahé 201, Jibril 134, Remy 53, Vaneck 50, Maïmouna 24 ; sur les lignes de code ajoutées, 60 %, 18 %, 9 %, 13 % et 0 %. Elle n'est pas égale : Mahé, qui coordonnait le projet, en porte la plus grande part, et son travail avec l'assistant est compté à son nom. C'est un volume, pas une valeur, et Git ne voit ni les jugements humains de Maïmouna (#52), ni les mesures faites sur machine ; les relectures sont plus partagées : 186 revues déposées sur les PR des autres, par les cinq membres. Méthode, limites et commande pour rejouer le relevé : `docs/suivi/CONTRIBUTIONS.md` et section 3.3 du rapport.

**Comment avez-vous utilisé l'IA ?** (Mahé)
Claude Code, Antigravity avec Gemini, ChatGPT et Codex, et Qwen Coder en local, pour écrire du code, mesurer et rédiger. Tout est consigné dans le journal d'usage, session par session, avec plus de 200 erreurs ou pièges détectés par la vérification. Règle : aucune affirmation d'un assistant n'est reprise sans mesure, test ou source primaire (annexe A14).

**Avez-vous compris le code écrit avec l'IA ?** (chacun, sur sa partie)
Répondre sur sa partie, concrètement : ce que fait le code, comment il a été testé, et une erreur trouvée par la vérification. Le sujet prévoit que chacun peut être interrogé sur n'importe quelle partie : relire avant la soutenance les fichiers de son domaine et ceux qu'on présente.

**Qu'est-ce qu'Agent0 ?** (Jibril)
Un générateur local de questions synthétiques traçables : Qwen propose une question et ses preuves, le programme contrôle le format, les sources et les extraits exacts. Sur 18 essais historiques, 15 candidats et 3 rejets automatiques ; les candidats attendent une relecture humaine. Le développement est gelé depuis le 23 novembre ; c'est une ouverture (annexe A16).

---

## 6. Limites et suites

**Quelle est la principale limite du projet ?** (Mahé)
L'exactitude des réponses du volet B n'est pas démontrée meilleure par l'adaptation, et nos mesures reposent sur un extrait annoté par question et sur des jeux de taille modeste (73 questions humaines). L'adaptation améliore ce qu'elle visait, la citation des sources, pas l'exactitude.

**Que feriez-vous avec plus de temps ?** (Mahé)
Un jeu humain plus grand, annoté par des juristes, avec plusieurs passages pertinents par question ; des données d'adaptation qui récompensent les réponses complètes, pas seulement la recopie ; une évaluation de l'exactitude sur la chaîne de démonstration elle-même ; et la reprise d'Agent0 pour cibler les faiblesses mesurées.

**Ce projet est-il utilisable par de vrais salariés ?** (Maïmouna)
Le site, oui, comme moteur de recherche dans les fiches, avec le lien vers la source et un avertissement : ce n'est pas un conseil juridique. L'assistant n'est pas assez fiable pour être diffusé : ses réponses citent bien leurs passages, mais sont souvent incomplètes.
