# Script oral de la soutenance (8 minutes)

**Généré** par `script_oral.py` depuis `deck.html` : le texte à dire est celui des notes du support, mot pour mot. Ne pas modifier ce fichier à la main : modifier le support, puis relancer le script.

**Durée prévue** : 7:55 pour 12 diapositives ; 1062 mots, soit 134 mots par minute (à 130 mots par minute, 8:10). Marge restante sur 8 minutes : 5 s, pour les changements d'orateur.

**Orateurs** : répartition proposée par domaine du classeur de suivi, à valider en équipe.

## Avant de commencer

- Ouvrir `docs/soutenance/presentation_8min.html` (hors ligne), touche F pour le plein écran.
- Les notes (touche N) s'affichent sur la page projetée : ne les ouvrir qu'en répétition, ou avec un second écran qui ne recopie pas le premier.
- Ouvrir à l'avance, dans un autre onglet, le site du volet A, et y poser une première question : la première visite télécharge le modèle.
- Avoir les deux vidéos de secours prêtes (volet A, 70 s ; volet B, 64 s), et, si une démonstration en direct est prévue, l'assistant lancé sur le Mac cinq minutes avant.
- Avancer d'un appui (flèche droite ou espace) à chaque nouvel élément évoqué : l'ordre des apparitions est indiqué sous chaque diapositive.

## Déroulé

| Diapositive | Début | Durée | Orateur |
|---|---:|---:|---|
| 1. Code du travail, en clair | 0:00 | 20 s | Maïmouna |
| 2. Une question de travail, 261 fiches officielles | 0:20 | 40 s | Maïmouna |
| 3. Une préparation commune aux deux volets | 1:00 | 35 s | Vaneck |
| 4. Volet A : tout se calcule dans le navigateur | 1:35 | 45 s | Vaneck |
| 5. Ajuster l'encodeur à nos fiches | 2:20 | 50 s | Remy |
| 6. Volet B : un assistant qui cite ses sources | 3:10 | 40 s | Jibril |
| 7. Chercher par le sens et par les mots | 3:50 | 60 s | Jibril |
| 8. Pourquoi 10 passages plutôt que 5 | 4:50 | 35 s | Jibril |
| 9. Trois modèles, choisis pour la machine qui les exécute | 5:25 | 45 s | Mahé |
| 10. Des questions écrites par des modèles, toujours contrôlées | 6:10 | 50 s | Mahé |
| 11. Des règles écrites avant de mesurer | 7:00 | 45 s | Mahé |
| 12. Merci. Vos questions ? | 7:45 | 10 s | Mahé |
| Fin | 7:55 | | |

### 1. Code du travail, en clair

**Maïmouna**, de 0:00 à 0:20 (20 s, 41 mots).

> Bonjour, nous sommes l'équipe Data Tigers. Notre projet retrouve, dans les fiches officielles du ministère du Travail, la réponse à une question de droit du travail : un site trouve les passages, un assistant local rédige une réponse qui les cite.

### 2. Une question de travail, 261 fiches officielles

**Maïmouna**, de 0:20 à 1:00 (40 s, 87 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : Répondre depuis les sources les fiches pratiques du ministère, pas la mémoire d'un modèle Montrer d'où vient l…
- Appui 2 : 261 fiches pratiques de travail-emploi.gouv.fr, découpées en 4 240 passages. Instantané du 11 septembre 2026, … ; puis Volet A, en ligne Un petit modèle que nous maîtrisons, exécuté dans le navigateur du visiteur, trouve les pass…

> Prenez cette question, tirée de notre jeu de test. La réponse existe : elle est dans une fiche du ministère. Le défi est de la retrouver parmi 261 fiches, de montrer d'où elle vient, et de se taire quand la question sort du sujet, plutôt que d'inventer.
>
> Le sujet impose deux volets. Le volet A, en ligne, sert un petit modèle que nous maîtrisons entièrement, dans le navigateur. Le volet B, local, emprunte un grand modèle de langage, que nous adaptons pour qu'il rédige des réponses sourcées.

### 3. Une préparation commune aux deux volets

**Vaneck**, de 1:00 à 1:35 (35 s, 70 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : 4 240 passages 512 tokens au plus, avec leur en-tête
- Appui 2 : Encodage E5 un vecteur de 384 nombres par passage
- Appui 3 : Index contrôlé par empreinte
- Appui 4 : Un choix de conception : la recherche du volet A est la première moitié du volet B. Le découpage, l'encodage e… ; puis Volet A le site, dans le navigateur Volet B l'assistant, sur le Mac

> Les deux volets partagent leur préparation. Nous découpons les 261 fiches selon leurs sections, en 4 240 passages d'au plus 512 tokens, chacun précédé de son en-tête : fiche, section, intertitres. Chaque passage est encodé une fois en un vecteur de 384 nombres, et l'index est contrôlé par empreinte. Le site du volet A cherche dans cet index ; l'assistant du volet B part de la même recherche, puis génère.

### 4. Volet A : tout se calcule dans le navigateur

**Vaneck**, de 1:35 à 2:20 (45 s, 114 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : 1. La question découpée en pièces par le tokeniseur
- Appui 2 : 2. Son vecteur de 384 nombres, calculé par l'encodeur ajusté (un pixel par nombre)
- Appui 3 : 3. Comparé aux 4 240 passages (un pixel par passage, foncé si proche) proche de la question
- Appui 4 : 4. Les 10 passages les plus proches, regroupés par fiche

> Voici le volet A, réellement calculé pour une question du site. Le navigateur découpe la question en pièces, puis notre encodeur la transforme en 384 nombres : un pixel par nombre. Il compare ce vecteur aux 4 240 passages, un pixel par passage, plus foncé quand il est proche. Les dix plus proches sont affichés, regroupés par fiche ; ici, tous viennent de la fiche sur les congés payés.
>
> Tout se passe dans le navigateur : aucun serveur, aucune requête après le chargement. Pour y tenir, le modèle est quantifié sur 8 bits et allégé du vocabulaire des alphabets non latins : 65,7 mébioctets, sans changer un seul résultat. Une recherche prend 21 millisecondes.

À savoir si on vous interrompt :

- Les 21 ms ont été mesurées le 19/10 sur le site, avec l'encodeur de base, de même architecture et de même taille.
- Les scores vont de 0,525 à 0,859 pour cette question ; sous 0,7683, le site refuse de répondre.

### 5. Ajuster l'encodeur à nos fiches

**Remy**, de 2:20 à 3:10 (50 s, 118 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : 109 paires question et passage : Qwen écrit une question pour un passage tiré de nos fiches. Apprentissage con…
- Appui 2 : animation du schéma, sans nouvel élément
- Appui 3 : 43,8 % 63,0 % des questions de test trouvent un bon passage dans les 5 premiers : +19,2 points , intervalle à … ; puis Servi sur le site depuis le 15 novembre, selon une règle écrite avant la mesure. Deux versions nourries de 2 2…

> Premier choix : adapter l'encodeur à nos fiches. Nous avons fait écrire par Qwen une question pour 109 passages, hors des fiches du test. L'apprentissage contrastif rapproche chaque question de son passage et l'éloigne des autres. Sur nos questions de test, le bon passage est dans les cinq premiers pour 63 % des questions, contre 43,8 % : 19 points de plus, un gain démontré. Avec dix passages regroupés par fiche, une fiche pertinente est affichée pour 93 % des questions.
>
> Vingt fois plus de questions synthétiques, écrites par Qwen puis par Claude, n'ont pas fait mieux sur les questions humaines : la version de Claude a appris son style, pas nos fiches. La règle écrite d'avance l'écarte.

À savoir si on vous interrompt :

- Perte : MultipleNegativesRankingLoss, lot de 16, taux 2e-5.
- Sur le CDTN, jeu externe : 67,4 % puis 72,3 %.
- Le nuage de points est un schéma, pas une projection réelle.
- v2-T, 2 289 paires de Qwen : +5,8 points sur le jeu v2, non démontré ; égalité sur le CDTN.
- v3-C, 2 420 paires écrites par Claude Sonnet et relues par deux juges Claude Opus, règle figée avant toute génération : jeu v2 +12,4 [+5,5 ; +20,3], démontré ; CDTN −2,2 ; lot de test −5,5 ; 5 questions hors corpus de plus au-dessus de la borne.

### 6. Volet B : un assistant qui cite ses sources

**Jibril**, de 3:10 à 3:50 (40 s, 78 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : Recherche hybride sens (E5) et mots (BM25), rangs fusionnés Reclasseur relit les 20 premiers avec la question …
- Appui 2 : Qwen2.5-7B, adapté par nous quantifié en 4 bits : 4,36 Gio servi par Ollama, sur le Mac
- Appui 3 : Réponse citée chaque phrase suivie de [Pk] chaque [Pk] vérifié dans le contexte
- Appui 4 : Ou abstention si les passages ne répondent pas

> Le volet B part de la même question. Une recherche hybride, par le sens et par les mots, propose des passages ; un reclasseur relit les vingt premiers avec la question ; les dix meilleurs, numérotés de P1 à P10, forment le contexte avec une consigne. Qwen, adapté par nous et servi par Ollama sur un Mac, rédige une réponse qui cite ses passages ; chaque citation est vérifiée. Si les passages ne répondent pas, il doit s'abstenir.

À savoir si on vous interrompt :

- La consigne interdit de compléter avec des connaissances générales.
- Pas de seuil d'abstention dans la démonstration : le modèle décide seul.

### 7. Chercher par le sens et par les mots

**Jibril**, de 3:50 à 4:50 (60 s, 125 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : Sens (E5) vecteurs proches
- Appui 2 : Mots (BM25) termes en commun
- Appui 3 : Fusion des rangs
- Appui 4 : 45,2 % 72,6 % lot de test : un passage pertinent dans le contexte 57,0 % 86,0 % jeu v2, 121 questions : +28,9 … ; puis Reclasseur lit question et passage

> Deuxième choix : ne pas chercher seulement par le sens. Sur cette question réelle, la recherche par le sens classe le bon passage, la fiche sur le congé sans solde, 59e : ses scores sont tous très proches. BM25, qui cherche les mots en commun, le place 2e. La fusion des rangs additionne les inverses des rangs, sans aucun réglage : il remonte au 6e rang. Le reclasseur lit la question et chaque passage ensemble : il le place en tête, avec un score de 0,66 contre 0,09 pour le suivant.
>
> Sur l'ensemble, la part des questions dont le contexte contient un passage pertinent passe de 45 à 73 % sur nos questions de test, et de 57 à 86 % sur le jeu v2.

À savoir si on vous interrompt :

- Fusion RRF : k = 60, la valeur de l'article de Cormack et al. (2009), jamais réglée.
- Nos mots vides gardent les négations (ne, pas, sans) : elles comptent en droit.
- Les trois écarts sont démontrés (McNemar exact, p < 0,001 sur le jeu v2 et le lot de test).

### 8. Pourquoi 10 passages plutôt que 5

**Jibril**, de 4:50 à 5:25 (35 s, 82 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : élément du schéma
- Appui 2 : Aucune question perdue : les 10 premiers contiennent les 5 premiers. Le gain va de 4 à 14 points selon le jeu …

> Nous avons étendu le contexte de cinq à dix passages : plus de passages pertinents y entrent. À méthode égale, aucune question n'est perdue, puisque les dix premiers contiennent les cinq premiers, et le gain va de 4 à 14 points. Le prix : le modèle lit deux fois plus de tokens et doit écarter plus de passages hors sujet. Quinze passages approcheraient le plafond du prompt. Le nombre a été fixé avant la mesure, pour ne pas choisir sur les résultats.

À savoir si on vous interrompt :

- Coût et précision mesurés sur le CDTN, pour la chaîne retenue.
- Sur le lot de test : E5 seul 45,2 puis 58,9 % ; chaîne retenue 68,5 puis 72,6 %.

### 9. Trois modèles, choisis pour la machine qui les exécute

**Mahé**, de 5:25 à 6:10 (45 s, 106 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : dans le navigateur multilingual-e5-small Taille 118 millions de paramètres, vecteurs de 384 nombres Pourquoi l…
- Appui 2 : sur le Mac bge-reranker-v2-m3 Rôle lit la question et un passage ensemble, et note leur accord Pourquoi lui le…
- Appui 3 : sur le Mac, servi par Ollama Qwen2.5-7B-Instruct Pourquoi lui poids ouverts sous licence Apache 2.0, bon en fr…

> Chaque modèle est choisi pour la machine qui l'exécute. Dans le navigateur, E5-small : multilingue, 118 millions de paramètres ; l'essentiel de son poids est son vocabulaire, dont nous retirons les alphabets non latins sans changer un résultat. Sur le Mac, le reclasseur bge-m3, le seul des trois testés qui apporte un gain. Et Qwen2.5-7B : poids ouverts, bon en français, et quatre gigas en 4 bits. Nous l'adaptons par LoRA, en n'apprenant que 0,15 % de ses paramètres. Ollama refusant les LoRA, nous fusionnons le correctif dans les poids avant de compresser, et un témoin passe par la même chaîne pour isoler l'effet de l'adaptation.

À savoir si on vous interrompt :

- Génération mesurée : 46,9 tokens par seconde en médiane sur le Mac.
- Le témoin T : modèle d'origine, même fusion et même compression, sans correctif.

### 10. Des questions écrites par des modèles, toujours contrôlées

**Mahé**, de 6:10 à 7:00 (50 s, 120 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : pour entraîner l'encodeur Une question par passage Qwen écrit la question qu'un salarié poserait ; des filtres…
- Appui 2 : pour adapter Qwen Répondre en recopiant, ou s'abstenir 218 exemples dans les conditions réelles : la réponse r…
- Appui 3 : pour évaluer Un jeu de test neuf 161 questions écrites par Claude et vérifiées par un second modèle, sur autor…

> Nous manquions de données annotées : nous en avons fait produire par des modèles, sans jamais les croire sur parole. Pour l'encodeur, Qwen écrit une question par passage. Pour adapter Qwen, 218 exemples reproduisent l'usage réel : la réponse recopie le passage et le cite, ou s'abstient. Deux membres les relisent : le premier lot a été refusé, car le modèle faisait dire aux passages ce qu'ils ne disent pas. L'adaptation fait passer les réponses citant un passage pertinent de 14 à 25 %, un gain démontré ; jugées à l'aveugle, elles sont mieux appuyées, mais pas plus exactes. Enfin, pour évaluer sur un jeu neuf, Claude a écrit 161 questions, contrôlées par un second modèle, avec l'autorisation de l'enseignant.

À savoir si on vous interrompt :

- Dans la chaîne de démonstration, sur le jeu v2 : 52,9 % de réponses citant un passage pertinent pour le modèle adapté, 10,1 % pour le modèle d'origine (54 questions gagnées, 3 perdues) ; +16,9 points sur l'ancienne chaîne, démontré.
- Abstention correcte hors corpus : 83,3 % avant et après adaptation (lot de test).
- Intervalle à 97,5 % de l'écart : de +2,1 à +23,8 points ; 8 questions gagnées, aucune perdue.

### 11. Des règles écrites avant de mesurer

**Mahé**, de 7:00 à 7:45 (45 s, 105 mots).

Apparitions, dans l'ordre des appuis :

- Appui 1 : Base servie jusqu'au 15 novembre l'encodeur ajusté n'était pas mesuré à temps : la règle de repli s'est appliq…
- Appui 2 : Volet A, recherche Volet B, assistant Coût aucun serveur une machine dédiée Latence 21 ms par recherche 11,8 s…

> Notre méthode tient en une phrase : écrire la règle avant de mesurer. Elle nous a fait renoncer à des choix que nous aimions : la base est restée servie un mois, une consigne plus performante a été écartée, et l'encodeur ajusté n'apporte rien au volet B. Elle confirme aussi la chaîne de démonstration : 17 points de plus que l'ancienne.
>
> Les deux volets ont des compromis opposés. Le site ne coûte rien, répond en vingt millisecondes, et tout y est vérifiable. L'assistant rédige une réponse, mais demande une machine, une douzaine de secondes, et son comportement vient de données que nous ne connaissons pas.

À savoir si on vous interrompt :

- Latence du volet B : 11,8 s en médiane par question, chaîne de la démonstration (10 passages, reclasseur), mesurée le 21/11 sur le jeu v2 ; 4,9 s avec l'ancienne chaîne à 5 passages.
- Les deux chiffres de qualité ne mesurent pas la même chose, ni sur le même jeu.

### 12. Merci. Vos questions ?

**Mahé**, de 7:45 à 7:55 (10 s, 16 mots).

> Merci. Nous pouvons montrer le site en direct, et la vidéo de l'assistant, pendant les questions.

À savoir si on vous interrompt :

- Touche A : sommaire des annexes ; touche M : revenir ici.

## Pendant les questions : la démonstration

- **Volet A, en direct** : annexe A1 du support (touche A, puis A1). Taper les questions telles quelles ; la dernière montre la limite de la recherche par le sens seule. Sans Internet : lire la vidéo de secours du volet A (70 s).
- **Volet B** : lire la vidéo de secours (64 s). En direct seulement si le jury le demande et si l'assistant est déjà lancé : annexe A2, questions et réponses attendues.
- **Autres questions** : sommaire des annexes (touche A) ; réponses préparées dans `questions_reponses.md`.

## Chronométrage

- Faire au moins deux répétitions complètes, chronomètre lancé (touche R pour le remettre à zéro).
- Repères : la diapositive 7 (Chercher par le sens et par les mots) commence à 3:50 ; le bilan (diapositive 11) à 7:00.
- En cas de retard, raccourcir la diapositive 9 (trois modèles) et la diapositive 8 (10 passages), pas le bilan.
