# Agent0 Light : bilan pour le rapport et l'oral

**État vérifié :** 2 novembre 2026.  
**Contribution :** Jibril BENSALEM, avec l'assistance de Codex dans ChatGPT Work.  
**Destination :** rapport final (#113), supports de présentation (#112, puis #114).  
**Statut :** version initiale approuvée par Mahé le 4 novembre sur `f854e54` ; précisions documentaires du même jour à revalider. Les revues des PR techniques restent distinctes de celle de ce bilan.

## 1. Message à retenir

**Le générateur et le support de relecture sont livrés ; les questions produites restent des candidats, pas un benchmark validé.**

Agent0 propose des cas synthétiques traçables pour préparer une éventuelle évaluation exploratoire du RAG. Ce travail ne constitue ni l'adaptation du modèle du volet B (#107), ni la mesure officielle sur le jeu humain (#52). Aucun gain de qualité du RAG n'est établi par ces essais.

## 2. Texte proposé pour le rapport

À reprendre dans l'analyse technique et le retour d'expérience du [rapport final](../rapport/RAPPORT_FINAL.md), après relecture.

### Réalisation et résultats

Agent0 Light est un outil de génération locale de questions synthétiques à partir du corpus M2 figé, composé de 4 240 passages issus de 261 fiches. Son objectif est de préparer des cas complémentaires pour une évaluation exploratoire du RAG, séparée du jeu de référence humain. Le périmètre livré comprend un contrat de données strict, une sélection reproductible des sources, un générateur utilisant Qwen2.5-7B-Instruct quantifié en Q4_K_M via Ollama, cinq catégories de questions et un support de relecture.

Les catégories sont simple, reformulation, multi-passage, piège à fausse prémisse et hors corpus. Le programme vérifie notamment le JSON, les identifiants de sources, la présence mot pour mot des extraits d'au moins 20 caractères sur des limites de mots et les doublons exacts après normalisation. Pour les pièges, il contrôle aussi le point d'interrogation final. Les sorties brutes, paramètres, empreintes et rejets sont conservés ; aucun nouvel essai ou nettoyage silencieux ne masque un échec.

La suite commune atteint 149 tests réussis, également vérifiés indépendamment par Mahé. Les essais réels ont été exécutés par Jibril sur son Legion sous Windows. Ils totalisent 18 runs : 15 candidats ont franchi les contrôles de leur version de génération et 3 sorties ont été rejetées automatiquement. Les originaux reçus ont été recoupés avec les sources et les versions de code. Le générateur et le support sont intégrés dans `dev` après relecture des PR #99, #100, #101, #103 et #106.

### Limites et enseignements

Ces résultats attestent le fonctionnement des contrôles dans les cas testés, sans valider la pertinence des questions. Les 15 candidats sont encore en attente de relecture humaine ; aucun cas hors corpus n'est confirmé. Les observations assistées et la revue de Mahé du 23 octobre sur #103 relèvent des défauts de sens malgré un JSON conforme : interrogation neutre présentée comme piège, comparaison non documentée ou information déclarée absente alors qu'elle figure dans la source. Ces observations ne valent pas décisions humaines dans la grille.

Les prompts ont été retouchés sur les mêmes trois fiches. Ces essais servent donc à la mise au point et ne permettent pas d'estimer une qualité générale ou un gain du RAG. La présence d'un extrait exact ne prouve pas qu'il suffit à répondre ; l'absence de preuve proposée ne démontre pas l'absence d'une réponse dans le corpus.

Le principal enseignement est de séparer la proposition du modèle, les contrôles automatiques et la décision humaine. Les 15 candidats sont exclus de l'entraînement ou de l'adaptation du générateur et de l'encodeur, même après relecture. Une des trois fiches sources appartient au test humain figé. Le pilote indépendant de 25 candidats, son gel et le benchmark synthétique sont reportés selon le périmètre retenu le 30 octobre. Une reprise demanderait une nouvelle décision, des fiches distinctes de la mise au point, un protocole figé et une relecture humaine effective.

Sources du texte : [étude et bilan par catégorie](agent0_light.md), [rapport de vérification des originaux](agent0_relecture/verification_archive.md), [grille humaine](agent0_relecture/grille_relecture.json), [approbation de #103](https://github.com/datatigersNLP/data_tigers_nlp/pull/103#pullrequestreview-5735781157), [approbation finale de #106](https://github.com/datatigersNLP/data_tigers_nlp/pull/106#pullrequestreview-5736081101) et preuves d'intégration en section 6.

À l'intégration dans le rapport PDF, reprendre ces sources comme références écrites : le convertisseur md2tex ne conserve pas les liens Markdown de ce paragraphe. Ajouter les observations assistées (`docs/etudes/agent0_relecture/observations_assistees.md`) et la revue de #103 du 23 octobre, n° 5629789477.

## 3. Trame orale, environ deux minutes

Durée indicative à vérifier lors d'une répétition ; aucun chronométrage n'est revendiqué.

> J'ai développé Agent0 Light pour proposer des questions supplémentaires à partir de notre corpus, avec une trace des sources et des sorties du modèle. L'idée est de préparer une évaluation exploratoire complémentaire au jeu humain.
>
> L'outil fonctionne localement avec Qwen et couvre cinq catégories : questions simples, reformulations, questions multi-passages, pièges et questions supposées hors corpus.
>
> Le programme vérifie la structure des sorties, les sources, les extraits exacts et les doublons. La suite atteint 149 tests réussis. Mais ces tests contrôlent le fonctionnement du programme, pas la qualité des questions.
>
> Sur les 18 essais réalisés sur mon Legion, nous avons obtenu 15 candidats et 3 rejets automatiques. Les 15 candidats attendent encore une relecture humaine. Aucun hors corpus n'est confirmé.
>
> Par exemple, le modèle a proposé une question sur les conditions d'utilisation du compte épargne-temps en affirmant que l'information manquait. Pourtant, ces conditions figuraient dans le passage fourni. La sortie était conforme au format, mais son classement restait problématique.
>
> C'est le principal enseignement : un extrait exact ou un JSON valide ne suffit pas à valider le sens. Nous avons livré le générateur et le support de relecture, puis reporté le pilote indépendant. Nous ne revendiquons donc aucun gain de qualité du RAG. Les candidats de mise au point restent séparés du jeu humain et exclus de l'entraînement.

## 4. Contenu d'une diapositive

**Titre :** Agent0 Light : générer des cas traçables, puis les faire relire

- **Livré et intégré :** générateur local, cinq catégories, contrôles et support de relecture.
- **Contrôles :** 149 tests ; cohérence des 18 originaux vérifiée, exécution non attestée indépendamment ; 15 candidats, 3 rejets automatiques.
- **Limite centrale :** 15 candidats en attente humaine ; aucun hors corpus confirmé.
- **Conclusion :** outil disponible pour explorer l'évaluation ; pilote indépendant et mesure de qualité reportés.

**À dire à l'oral :** les 15 candidats ont passé les contrôles historiques de leur run ; ce nombre n'est pas un taux de qualité et ne signifie pas qu'ils satisfont tous les contrôles renforcés ajoutés ensuite.

## 5. Questions probables du jury

| Question | Réponse courte |
|---|---|
| Les 149 tests prouvent-ils que les questions sont bonnes ? | Ils vérifient les comportements techniques couverts par les tests, avec des clients simulés. La pertinence, la catégorie et la suffisance des preuves nécessitent une relecture humaine. |
| Pourquoi les 15 candidats ne sont-ils pas déjà un benchmark ? | Ils ont servi à ajuster les prompts sur trois fiches et leurs décisions humaines sont vierges. Il manque un lot indépendant, relu et figé avant l'évaluation. |
| Comment démontrer qu'une question est hors corpus ? | Le modèle ne peut pas le décider seul. Il faut examiner le corpus figé, tracer les recherches et contre-preuves, puis faire statuer un relecteur ; une recherche sans résultat ne suffit pas. |
| Avez-vous amélioré le RAG avec Agent0 ? | Aucun gain n'a été mesuré dans ce chantier. Agent0 prépare des candidats ; l'évaluation officielle et l'adaptation sont des travaux distincts. |
| Pourquoi exclure ces candidats de l'entraînement ? | Ils ont servi à la mise au point d'un outil d'évaluation et une fiche source appartient au test humain. Leur réemploi brouillerait la séparation entraînement/évaluation ; l'exclusion s'applique aux 15 candidats, pas indistinctement aux deux autres fiches. |
| Qui a fait quoi ? | Jibril a piloté et exécuté les essais Windows ; Codex a assisté le développement, les tests, l'analyse des sorties et la documentation ; Mahé a relu et approuvé les PR techniques et le support. Les décisions sémantiques sur les candidats ne sont pas remplies. |

### Exemple de limite à montrer

Le cas [`hors_corpus_001`](agent0_relecture/questions_et_sources.md#hors_corpus_001) demande les conditions d'utilisation du CET pendant un congé sans solde, tout en déclarant ces informations absentes. Les [observations assistées](agent0_relecture/observations_assistees.md#hors_corpus_001) renvoient aux conditions présentes dans le passage. Cela illustre une justification du modèle contredite par sa source, sans attribuer une décision humaine au candidat. Cet exemple décrit le corpus figé, pas une vérification du droit en vigueur.

Autre illustration : [`adversarial_002`](agent0_relecture/questions_et_sources.md#adversarial_002) est une question neutre, malgré la fausse prémisse annoncée dans un champ séparé. Le contrôle du « ? » ne peut pas résoudre ce défaut de sens.

## 6. Chiffres et preuves à conserver avec le bilan

### Essais historiques

| Catégorie | Runs | Candidats préparés | Rejets automatiques |
|---|---:|---:|---:|
| Simple | 1 | 1 | 0 |
| Reformulation | 1 | 1 | 0 |
| Multi-passage | 6 | 4 | 2 |
| Pièges (`adversarial`) | 4 | 3 | 1 |
| Hors corpus | 6 | 6 | 0 |
| **Total** | **18** | **15** | **3** |

Source : [synthèse de l'étude](agent0_light.md), [inventaire des originaux](agent0_relecture/verification_archive.md) et [grille](agent0_relecture/grille_relecture.json). Les trois rejets sont `multi_passage_001`, `multi_passage_005` et `adversarial_004`. Les 15 candidats ont franchi leurs contrôles historiques ; aucun résultat de revalidation de ces 15 cas par le validateur final n'est déduit de ce tableau.

| Indicateur | Valeur vérifiée | Portée et preuve |
|---|---|---|
| Corpus de référence | 4 240 passages, 261 fiches | Métadonnées du corpus figé dans la grille et contrôle de sources #100. |
| Suite commune finale | 149 tests réussis | Revue indépendante de #103 du 02/11, Python 3.12.11 / Pydantic 2.14.0, versions du verrou et `uv pip check` ; contrôles locaux également consignés dans la note du 02/11. Aucune nouvelle exécution pour ce bilan. |
| Relecture sémantique consignée | 0 décision ; 15 entrées `pending` | Grille relue au snapshot ci-dessous ; relecteurs, points attendus et confirmations vierges. Ce n'est pas une mesure de qualité à 0 %. |
| Support documentaire | 8 passages complets, issus de 3 fiches | Revue finale de #106 ; une seule fiche, `le-conge-sans-solde`, appartient aux 61 fiches de test. |
| Originaux historiques | Cohérence des 18 originaux vérifiée ; exécution non attestée indépendamment | Rapport de vérification de l'archive reçue : rapprochement des données et déclarations, pas attestation indépendante de l'exécution sur le Legion. |
| Gel du pilote | `lot_pilote_fige: false` | Grille ; pas de lot indépendant de 25 candidats livré. |

### Intégrations vérifiées dans GitHub

| Ticket / livrable | PR fusionnée dans `dev` | Date | Commit de fusion |
|---|---|---|---|
| #91 : contrat | [#99](https://github.com/datatigersNLP/data_tigers_nlp/pull/99) | 26/10/2026 | `aad08f6` |
| #92 : sources | [#100](https://github.com/datatigersNLP/data_tigers_nlp/pull/100) | 27/10/2026 | `b61873b` |
| #93 : génération simple/reformulation | [#101](https://github.com/datatigersNLP/data_tigers_nlp/pull/101) | 27/10/2026 | `a74f9a1` |
| #94 : trois catégories ajoutées, cinq au total, et contrôles | [#103](https://github.com/datatigersNLP/data_tigers_nlp/pull/103) | 02/11/2026 | `dcb790d` |
| #95 : support vérifié de relecture | [#106](https://github.com/datatigersNLP/data_tigers_nlp/pull/106) | 02/11/2026 | `5753b86` |

Les approbations finales de Mahé sur #103 et #106 portent respectivement sur `c5e3d8d` et `506ffc1`. La fusion du support est distincte de la validation des candidats.

**Référence de lecture :** snapshot `dev/73b9693e048071b4842054d22bd5140ff1bf350e`, le 02/11/2026, et états GitHub des PR relus le même jour. Certaines synthèses historiques de l'étude et du support indiquent encore une relecture de #106 en attente ; pour l'intégration finale, les approbations et commits de fusion ci-dessus font foi. La [note du 02/11](../journal/2026-11-02_agent0_light_integration.md) décrit l'étape précédant la réapprobation de #106. La consolidation du journal en [#126](https://github.com/datatigersNLP/data_tigers_nlp/pull/126) est une PR distincte, encore ouverte au moment de cette préparation.

## 7. Suites possibles, hors du bilan réalisé

La décision de périmètre du 30/10 dans [#13](https://github.com/datatigersNLP/data_tigers_nlp/issues/13) reste révisable en équipe. La priorité demeure la mesure officielle et l'adaptation du volet B. Si un pilote synthétique est repris, il faudra décider de sa méthode, figer les prompts et le code avant génération sur de nouvelles fiches correctement séparées, organiser une relecture indépendante avec recherches et contre-preuves, puis figer les seuls cas retenus avant les réponses du RAG. Les étapes #96 à #98 ne sont pas réalisées par la livraison d'Agent0.

**Formulations à éviter :** « 15 questions validées », « 83 % de questions correctes », « six vrais hors corpus », « le RAG est amélioré », « Agent0 remplace l'adaptation du modèle ». Les résultats disponibles ne les établissent pas.
