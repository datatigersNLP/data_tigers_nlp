# Méthode du pilote pour les propositions hors corpus

Version `agent0-hors-corpus-pilote-v1`, préparée le 9 novembre 2026 pour relecture. **Aucune question n'est rédigée dans ce document, aucun hors corpus n'est confirmé.** Il s'agit du Challenge Set synthétique exploratoire ; les questions humaines de #44 et leur protocole restent inchangés.

## Production proposée, à configuration fixée

Les emplacements 21 à 25 disposent chacun d'un ancrage M2 distinct, tiré avant génération selon le plan. Cet ancrage sert uniquement d'entrée documentaire au générateur existant ; ce n'est ni une preuve attendue de réponse ni une preuve d'absence dans le corpus.

Conserver `preparer_prompt_hors_corpus`, version actuelle `agent0-hors-corpus-v2`, sans réécriture opportuniste de la consigne entre les appels. Elle demande une information différente et précisément délimitée ; elle distingue l'absence dans le passage de l'absence dans le corpus complet. Le commit, la version et les empreintes réellement retenus seront consignés avant le premier appel.

Une tentative par emplacement, incluse dans le plafond global de 25 appels. Les échecs techniques et rejets sont conservés sans nouvel appel automatique. La proposition porte `answerable_proposed: false`, `evidence: []`, un motif d'absence **à vérifier**, et aucune prémisse/correction adversarial. Le générateur n'a pas démontré que cette catégorie sera réussie : les cinq essais peuvent être rejetés ou rester incertains.

## Recherche documentaire avant admission

Le relecteur humain distinct de l'auteur reçoit la question brute et les références de corpus, sans réponse du RAG. Il conserve la formulation, y compris une ambiguïté : il n'ajoute pas une restriction pour rendre artificiellement la question hors corpus.

1. **Délimiter la demande reçue.** Noter l'information effectivement demandée, les entités, la situation et les interprétations plausibles. Une question générale sur des conditions n'exige pas une exhaustivité inventée. Si une interprétation raisonnable admet une réponse conditionnelle suffisamment sourcée, examiner cette réponse avant de conclure à l'absence.
2. **Vérifier le corpus.** Contrôler les empreintes M2 et ses 4 240 passages/261 fiches. Le texte figé est la référence ; un document externe ou le site actuel ne remplace pas une fiche absente de l'instantané.
3. **Chercher largement dans tous les textes.** Tracer les termes exacts, variantes, synonymes, sigles développés et concepts voisins définis pour cette question. Consulter l'inventaire des 261 titres et chercher aussi dans les sections, sans limiter la recherche au passage d'ancrage ou aux cinq premiers résultats d'un moteur.
4. **Lire les fiches pertinentes en entier.** Examiner tous leurs passages, notamment conditions, exceptions, renvois et procédures voisines. Rapprocher plusieurs passages lorsqu'ils peuvent ensemble répondre. Un titre, un simple thème ou un lien externe ne fournit pas l'information ; noter pourquoi les contre-preuves rencontrées sont suffisantes ou insuffisantes.
5. **Tracer le périmètre réellement examiné.** Dans la grille, renseigner méthodes, termes et variantes, couverture de l'inventaire des titres, fiches complètes lues, identifiants de passages et contre-preuves, puis limites. La trace distingue un parcours de l'inventaire d'une lecture exhaustive des 4 240 textes : aucun des deux n'est déclaré s'il n'a pas été fait.
6. **Décider avec justification humaine.** Si une réponse suffisamment sourcée est trouvée dans une ou plusieurs fiches, rejeter la proposition hors corpus, sans modifier silencieusement son type. Si les recherches sont insuffisantes, une ambiguïté persiste ou des fiches plausibles restent non examinées, conserver `pending`. Accepter seulement si l'examen documenté permet au relecteur de justifier l'absence de réponse dans ce corpus, avec ses limites.

La recherche peut être lexicale et assistée pour organiser les textes. L'avis d'un modèle, une liste vide, un faible score, l'échec du RAG ou l'insuffisance du seul passage d'ancrage ne constituent jamais une preuve d'absence. Les réponses du RAG à évaluer ne sont pas consultées avant le gel. En cas de manque de disponibilité pour la vérification, garder le cas en attente ; il n'y a pas de quota à atteindre.

## Trace et export après relecture

Les champs de [grille_relecture.json](grille_relecture.json) restent vides dans la préparation. La relecture renseigne le nom, la date, la décision et son motif, avec les recherches et limites effectivement observées. Une aide IA éventuelle est consignée séparément et ne devient pas une double annotation humaine.

Pour un cas réellement accepté, confirmer `answerable_confirmed: false` et `expected_points: []`, conserver `evidence: []` et un `out_of_corpus_reason` humainement vérifié. L'URL et l'extrait de **preuve de réponse** restent vides ; l'URL d'ancrage reste seulement dans la provenance de génération et les passages examinés dans la trace de recherche. Aucun classement provisoire n'est exporté comme confirmé.

Le lot figé peut contenir de zéro à cinq hors corpus. Si aucun n'est confirmé, signaler l'absence de cette catégorie dans le bilan ; ne pas calculer sa qualité sur les cas incertains. Un exemple rédigé ou reformulé avec une IA garde son origine synthétique et ne peut pas rejoindre le test humain.
