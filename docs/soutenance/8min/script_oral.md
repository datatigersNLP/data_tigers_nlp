# Script oral de la soutenance (8 minutes, démonstrations comprises)

**Source** le texte à dire est celui des notes de `deck.html`, mot pour mot ; ce fichier est généré par `script_oral.py` : ne pas le modifier à la main, modifier le support puis relancer le script.

**Durée prévue** 7:36 sur 8:00 au plus, marge de 24 s : présentation de 9 diapositives 4:11 (539 mots, 129 mots par minute), démonstration du volet A 1:25, démonstration du volet B 1:50, clôture 0:10.

**Orateurs** répartition retenue par Mahé le 28 novembre : Remy les diapositives 1 à 4, Mahé les diapositives 5 à 7, Jibril les diapositives 8 et 9, Vaneck la démonstration du volet A, Maïmouna la démonstration du volet B, Remy la clôture ; Mahé tient le clavier pendant toute la soutenance.

---

## Avant de commencer

- Ouvrir `Soutenance_Data_Tigers_8min.html` (hors ligne), touche F pour le plein écran.
- Les notes (touche N) s'affichent sur la page projetée : ne les ouvrir qu'en répétition, ou avec un second écran qui ne recopie pas le premier.
- Ouvrir à l'avance, dans un autre onglet, le site du volet A, et y poser une première question : la première visite télécharge le modèle.
- Lancer l'assistant du volet B sur le Mac cinq minutes avant (`lancer_demo_volet_b.zsh`), ouvrir les deux onglets, le modèle adapté sur le port 8765 et le témoin T sur le port 8766, et poser une question d'échauffement dans chacun, en finissant par le modèle adapté.
- Avoir les deux vidéos de secours prêtes (volet A, 70 s ; volet B, 64 s), sans les lancer.
- Avancer d'un appui (flèche droite ou espace) à chaque nouvel élément évoqué : l'ordre des apparitions est indiqué sous chaque diapositive.
- À éviter en direct : la question de la diapositive 2 (le modèle adapté s'abstient alors que le bon passage est en tête), la période d'essai d'un cadre (réponse en fragment), les 48 heures (dérogation attribuée à l'inspecteur du travail, alors que le passage dit la DREETS).

## Déroulé

| Partie | Début | Durée | Orateur |
|---|---:|---:|---|
| Diapositive 1. Code du travail, en clair | 0:00 | 12 s | Remy |
| Diapositive 2. Une question de travail, 261 fiches officielles | 0:12 | 34 s | Remy |
| Diapositive 3. Une préparation commune aux deux volets | 0:46 | 21 s | Remy |
| Diapositive 4. Volet A : tout se calcule dans le navigateur | 1:07 | 29 s | Remy |
| Diapositive 5. Ajuster l'encodeur à nos fiches | 1:36 | 33 s | Mahé |
| Diapositive 6. Volet B : un assistant qui cite ses sources | 2:09 | 26 s | Mahé |
| Diapositive 7. Chercher par le sens et par les mots | 2:35 | 37 s | Mahé |
| Diapositive 8. Pourquoi 10 passages plutôt que 5 | 3:12 | 19 s | Jibril |
| Diapositive 9. Trois modèles, choisis pour la machine qui les exécute | 3:31 | 40 s | Jibril |
| Démonstration du volet A, en direct | 4:11 | 85 s | Vaneck |
| Démonstration du volet B, en direct | 5:36 | 110 s | Maïmouna |
| Clôture | 7:26 | 10 s | Remy |
| Fin | 7:36 | | |

### Diapositive 1 : Code du travail, en clair

**Remy**, de 0:00 à 0:12 (12 s, 25 mots).

> Bonjour, nous sommes l'équipe Data Tigers. Notre projet retrouve, dans les fiches du ministère du Travail, la réponse à une question de droit du travail.

### Diapositive 2 : Une question de travail, 261 fiches officielles

**Remy**, de 0:12 à 0:46 (34 s, 75 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : Répondre depuis les sources les fiches pratiques du ministère, pas la mémoire d'un modèle Montrer d'où vient …
- Appui 2 : 261 fiches pratiques de travail-emploi.gouv.fr, découpées en 4 240 passages. Instantané du 11 septembre 2026 … ; puis Volet A, en ligne Un petit modèle que nous maîtrisons, exécuté dans le navigateur du visiteur, trouve les …

> Prenez cette question de notre jeu de test : la réponse existe, dans une fiche du ministère. Le défi est de la retrouver parmi 261 fiches, de montrer d'où elle vient, et de se taire quand la question sort du sujet, plutôt que d'inventer.
>
> Le volet A, en ligne, sert un petit modèle que nous maîtrisons, dans le navigateur. Le volet B, local, adapte un grand modèle de langage pour qu'il rédige des réponses sourcées.

### Diapositive 3 : Une préparation commune aux deux volets

**Remy**, de 0:46 à 1:07 (21 s, 45 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : 4 240 passages 512 tokens au plus, avec leur en-tête
- Appui 2 : Encodage E5 un vecteur de 384 nombres par passage
- Appui 3 : Index contrôlé par empreinte
- Appui 4 : Un choix de conception : la recherche du volet A est la première moitié du volet B. Le découpage, l'encodage … ; puis Volet A le site, dans le navigateur Volet B l'assistant, sur le Mac

> Les deux volets partagent leur préparation : 261 fiches découpées en 4 240 passages, chacun encodé une fois en un vecteur de 384 nombres, dans un index contrôlé par empreinte. Le site cherche dans cet index ; l'assistant part de la même recherche, puis génère.

### Diapositive 4 : Volet A : tout se calcule dans le navigateur

**Remy**, de 1:07 à 1:36 (29 s, 59 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : 1. La question découpée en pièces par le tokeniseur
- Appui 2 : 2. Son vecteur de 384 nombres, calculé par l'encodeur ajusté (un pixel par nombre)
- Appui 3 : 3. Comparé aux 4 240 passages (un pixel par passage, foncé si proche) proche de la question
- Appui 4 : 4. Les 10 passages les plus proches, regroupés par fiche

> Voici le volet A, calculé pour une question du site. Le navigateur découpe la question en pièces, notre encodeur la transforme en 384 nombres, puis la compare aux 4 240 passages : plus foncé, plus proche. Les dix meilleurs sont regroupés par fiche.
>
> Tout se passe dans le navigateur, sans serveur : 65,7 mébioctets, une recherche en 21 millisecondes.

À savoir si on vous interrompt :

- Les 21 ms ont été mesurées le 19/10 sur le site, avec l'encodeur de base, de même architecture et de même taille.
- Les scores vont de 0,525 à 0,859 pour cette question ; sous 0,7683, le site refuse de répondre.

### Diapositive 5 : Ajuster l'encodeur à nos fiches

**Mahé**, de 1:36 à 2:09 (33 s, 70 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : 109 paires question et passage : Qwen écrit une question pour un passage tiré de nos fiches. Apprentissage …
- Appui 2 : animation du schéma, sans nouvel élément
- Appui 3 : 43,8 % 63,0 % des questions de test trouvent un bon passage dans les 5 premiers : +19,2 points , intervalle à … ; puis Servi sur le site depuis le 15 novembre, selon une règle écrite avant la mesure. Deux versions nourries de 2 …

> Premier choix : adapter l'encodeur à nos fiches. Qwen écrit une question pour 109 passages, et l'apprentissage contrastif rapproche chaque question de son passage. Sur nos questions de test, le bon passage est dans les cinq premiers pour 63 % des questions, contre 43,8 % : un gain démontré.
>
> Vingt fois plus de questions synthétiques n'ont pas fait mieux sur les questions humaines : la règle écrite d'avance les écarte.

À savoir si on vous interrompt :

- Perte : MultipleNegativesRankingLoss, lot de 16, taux 2e-5.
- Sur le CDTN, jeu externe : 67,4 % puis 72,3 %.
- Le nuage de points est un schéma, pas une projection réelle.
- v2-T, 2 289 paires de Qwen : +5,8 points sur le jeu v2, non démontré ; égalité sur le CDTN.
- v3-C, 2 420 paires écrites par Claude Sonnet et relues par deux juges Claude Opus, règle figée avant toute génération : jeu v2 +12,4 [+5,5 ; +20,3], démontré ; CDTN −2,2 ; lot de test −5,5 ; 5 questions hors corpus de plus au-dessus de la borne.

### Diapositive 6 : Volet B : un assistant qui cite ses sources

**Mahé**, de 2:09 à 2:35 (26 s, 57 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : Recherche hybride sens (E5) et mots (BM25), rangs fusionnés Reclasseur relit les 20 premiers avec la question …
- Appui 2 : Qwen2.5-7B, adapté par nous quantifié en 4 bits : 4,36 Gio servi par Ollama, sur le Mac
- Appui 3 : Réponse citée chaque phrase suivie de [Pk] chaque [Pk] vérifié dans le contexte
- Appui 4 : Ou abstention si les passages ne répondent pas

> Le volet B part de la même question. Une recherche hybride propose des passages, un reclasseur relit les vingt premiers, et les dix meilleurs forment le contexte. Qwen, adapté par nous et servi par Ollama sur un Mac, rédige une réponse qui cite ses passages, chaque citation étant vérifiée. Si les passages ne répondent pas, il s'abstient.

À savoir si on vous interrompt :

- La consigne interdit de compléter avec des connaissances générales.
- Pas de seuil d'abstention dans la démonstration : le modèle décide seul.

### Diapositive 7 : Chercher par le sens et par les mots

**Mahé**, de 2:35 à 3:12 (37 s, 79 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : Sens (E5) vecteurs proches
- Appui 2 : Mots (BM25) termes en commun
- Appui 3 : Fusion des rangs
- Appui 4 : 45,2 % 72,6 % lot de test : un passage pertinent dans le contexte 57,0 % 86,0 % jeu v2, 121 questions : +28,9 … ; puis Reclasseur lit question et passage

> Deuxième choix : ne pas chercher seulement par le sens. Sur cette question, la recherche par le sens classe le bon passage 59e. BM25, qui cherche les mots, le place 2e ; la fusion des rangs le remonte au 6e ; le reclasseur le place en tête.
>
> Sur l'ensemble, les questions dont le contexte contient un passage pertinent passent de 45 à 73 % sur nos questions de test, et de 57 à 86 % sur le jeu v2.

À savoir si on vous interrompt :

- Le reclasseur donne 0,66 à ce passage, contre 0,09 au suivant.
- Fusion RRF : k = 60, la valeur de l'article de Cormack et al. (2009), jamais réglée.
- Nos mots vides gardent les négations (ne, pas, sans) : elles comptent en droit.
- Les trois écarts sont démontrés (McNemar exact, p < 0,001 sur le jeu v2 et le lot de test).

### Diapositive 8 : Pourquoi 10 passages plutôt que 5

**Jibril**, de 3:12 à 3:31 (19 s, 42 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : élément du schéma
- Appui 2 : Aucune question perdue : les 10 premiers contiennent les 5 premiers. Le gain va de 4 à 14 points selon le jeu …

> Nous avons étendu le contexte de cinq à dix passages : aucune question n'est perdue, et le gain va de 4 à 14 points. Le prix : deux fois plus de tokens à lire. Le nombre a été fixé avant la mesure.

À savoir si on vous interrompt :

- Coût et précision mesurés sur le CDTN, pour la chaîne retenue.
- Sur le lot de test : E5 seul 45,2 puis 58,9 % ; chaîne retenue 68,5 puis 72,6 %.

### Diapositive 9 : Trois modèles, choisis pour la machine qui les exécute

**Jibril**, de 3:31 à 4:11 (40 s, 87 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : dans le navigateur multilingual-e5-small Taille 118 millions de paramètres, vecteurs de 384 nombres Pourquoi …
- Appui 2 : sur le Mac bge-reranker-v2-m3 Rôle lit la question et un passage ensemble, et note leur accord Pourquoi lui …
- Appui 3 : sur le Mac, servi par Ollama Qwen2.5-7B-Instruct Pourquoi lui poids ouverts sous licence Apache 2.0, bon en …
- Appui 4 : 10,1 % 52,9 % des réponses citent un passage pertinent, sans l'adaptation (témoin T), puis avec : 12 sur 119 …

> Chaque modèle est choisi pour sa machine. Dans le navigateur, E5-small, dont nous retirons les alphabets non latins sans changer un résultat. Sur le Mac, le reclasseur bge-m3, le seul des trois testés qui apporte un gain, et Qwen2.5-7B, adapté par LoRA, fusionné puis compressé.
>
> Sur le jeu v2, avec la chaîne de la démonstration, le témoin sans adaptation cite un passage pertinent dans 10,1 % de ses réponses, le modèle adapté dans 52,9 %. C'est une mesure de traçabilité, pas d'exactitude : la démonstration le montre.

À savoir si on vous interrompt :

- Génération mesurée : 46,9 tokens par seconde en médiane sur le Mac.
- Le témoin T : modèle d'origine, même fusion et même compression, sans correctif.
- 52,9 % (63 sur 119) pour le modèle adapté, 10,1 % (12 sur 119) pour le modèle d'origine : 54 questions gagnées, 3 perdues ; chaîne de la démonstration, jeu v2 (annexe A3).

### Démonstration du volet A, en ligne

**Vaneck**, de 4:11 à 5:36 (85 s, 114 mots ; Mahé tape les questions). Annexe A1 du support.

Questions, dans l'ordre :

- 1. Combien de jours de congés payés par an ? (une seule fiche, « Les congés payés », et ses 10 passages regroupés)
- 2. Ma période d'essai peut-elle être renouvelée ? (le passage exact en tête : renouvelable une fois si un accord de branche étendu le prévoit (similarité 0,888))
- 3. Comment est calculée la pension de retraite d'un fonctionnaire ? (refus : hors du périmètre des fiches ; bouton « Afficher quand même »)
- 4. Combien de jours de congé pour un mariage ? (la bonne fiche (« quatre jours pour le mariage »), avec l'avertissement « correspondance moins nette ») : en réserve, pour les questions du jury
- 5. J'aimerais m'absenter trois mois pour voyager sans être payé : mon employeur est-il obligé d'accepter ? (la limite : la recherche par le sens seule ne trouve pas la bonne fiche ; la recherche hybride du volet B la place en tête (diapositive 7)) : en réserve, pour les questions du jury

> Voici le volet A, tel qu'il est en ligne sur GitHub Pages. Première question : combien de jours de congés payés par an ? Le résultat arrive en quelques millisecondes : une seule fiche, « Les congés payés », et ses dix passages, regroupés. Deuxième question : ma période d'essai peut-elle être renouvelée ? Le passage qui répond est en tête : une fois, si un accord de branche étendu le prévoit. Troisième question, hors du sujet : la pension de retraite d'un fonctionnaire. Le site refuse plutôt que d'inventer, mais laisse voir les passages les plus proches si on le demande. Tout est calculé dans le navigateur : aucune question ne quitte l'appareil.

À savoir si on vous interrompt :

- La première visite télécharge le modèle, 65,7 Mio, que le navigateur garde ensuite en cache.
- Les deux autres questions du tableau servent aux questions du jury : le mariage montre l'avertissement « correspondance moins nette » (similarité 0,814) ; le voyage montre la limite de la recherche par le sens seule, que corrige la recherche hybride du volet B (diapositive 7).

### Démonstration du volet B, en direct

**Maïmouna**, de 5:36 à 7:26 (110 s, 155 mots ; Mahé tape les questions). Annexe A2 du support.

Questions, dans l'ordre :

- 1. Combien de jours de congés payés ai-je par an ? (adapté ; réponse qui cite P2 : 2,5 jours ouvrables par mois de travail effectif)
- 2. Ma période d'essai peut-elle être renouvelée ? (T, puis adapté ; T s'abstient ; l'adapté répond et cite P1 : une fois, si un accord de branche étendu le prévoit)
- 3. Comment est calculée la pension de retraite d'un fonctionnaire ? (adapté ; abstention : la question sort du corpus)
- 4. Combien de jours de congé pour un mariage ? (adapté ; réserve : quatre jours pour le mariage ou un PACS, cite P1) : en réserve, pour les questions du jury

> Voici le volet B, qui tourne sur ce Mac : aucune requête ne part sur Internet. L'interface affiche sous chaque réponse le modèle qui l'a rédigée et sa durée réelle. Première question : combien de jours de congés payés ai-je par an ? Le modèle adapté cite le passage P2 : deux jours et demi ouvrables par mois de travail effectif. La réponse est juste et citée, mais incomplète : elle ne donne pas le total annuel.
>
> Deuxième question, d'abord au témoin, le modèle d'origine passé par la même chaîne : ma période d'essai peut-elle être renouvelée ? Il s'abstient, alors que le bon passage était dans son contexte. Le modèle adapté répond et cite P1 : une fois, si un accord de branche étendu le prévoit.
>
> Troisième question, hors du corpus : la pension de retraite d'un fonctionnaire. Il s'abstient, comme attendu. La température est nulle : une même question redonne la même réponse.

À savoir si on vous interrompt :

- Les quatre questions du tableau ont été essayées les 22 et 26 novembre ; la dernière, le mariage, sert aux questions du jury.
- Limites connues du modèle adapté : la question de la diapositive 2 (il s'abstient alors que le bon passage est en tête), la période d'essai d'un cadre (réponse en fragment), les 48 heures (dérogation attribuée à l'inspecteur du travail, alors que le passage dit la DREETS).

### Clôture

**Remy**, de 7:26 à 7:36 (10 s, 19 mots).

> Merci de votre attention. Nous sommes prêts à répondre à vos questions, et à revenir sur n'importe quelle démonstration.

## Si quelque chose ne se passe pas comme prévu

- **Le site du volet A ne répond pas, ou pas d'Internet** : lire la vidéo de secours du volet A (70 s), filmée sur le site en ligne, en le disant.
- **L'assistant du volet B ne démarre pas, ou la génération est lente** : lire la vidéo de secours du volet B (64 s). Si la génération est seulement lente, passer la troisième question : l'abstention hors corpus est déjà montrée par le volet A.
- **Une réponse en direct est mauvaise** : dire que les questions ont été choisies après essai, que c'est une illustration et non une mesure, puis passer à la vidéo.
- **Le support ne s'ouvre pas** : le même fichier sur le second ordinateur ou sur la clé, sinon le PDF de secours, une page par appui.

## Pendant les questions

- **Autres questions** : sommaire des annexes (touche A) ; réponses préparées dans `questions_reponses.md`.
- **Reprendre une démonstration** : annexes A1 et A2 (touche A, puis le numéro).

## Chronométrage

- Faire au moins deux répétitions complètes, chronomètre lancé (touche R pour le remettre à zéro), démonstrations comprises, sur le Mac de la soutenance.
- Repères : la diapositive 7 (Chercher par le sens et par les mots) commence à 2:35 ; la présentation finit à 4:11 ; la démonstration du volet B commence à 5:36 ; la clôture à 7:26.
- En cas de retard, raccourcir les diapositives 8 (10 passages) et 3 (préparation commune), puis passer la troisième question de la démonstration du volet B.
