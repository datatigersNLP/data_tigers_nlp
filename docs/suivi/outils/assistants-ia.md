# Assistants de développement IA

## Identification
- Version : plusieurs assistants et versions selon les membres, voir « Versions utilisées »
- Nature : assistants conversationnels et de programmation
- Assignés : toute l'équipe ; prévus : toute l'équipe
- Coordination : toute l'équipe
- Période d'utilisation : (Remy) depuis le 25 septembre 2026 (session 9 du journal)
- Besoin du projet auquel il répond : expliquer, rédiger, relire du code et des documents, vérifier des données.

## Versions utilisées
Chaque membre tient sa propre ligne à jour, avec une ligne par assistant s'il en utilise plusieurs. Chaque
observation des rubriques suivantes précise l'assistant concerné, par exemple « (Vaneck, <assistant>) ».

| Membre | Assistant | Modèle ou version | Formule (gratuite, payante…) | Usages principaux |
|---|---|---|---|---|
| Vaneck | Claude Code dans VS Code (2.1.322 au 14/11) | Claude Opus 5.5 | payante | préparation et contrôle du corpus (#27), interface du site du volet A et tests Playwright (#48, #53), démonstration du volet B (#111), relectures de pull requests |
| Mahé | Claude Code (2.1.306 au 26/10) | Claude Opus 5 (8 sessions), puis Claude Opus 5.5 (14 sessions), d'après le journal | à compléter | audits du dépôt, revues de PR, protocoles et mesures, rédaction des documents, actions GitHub en son nom |
| Rémy | Google Antigravity | Gemini 3.8 Flash (High) | formule gratuite | métriques et références lexicales (#45, #47), étude d'ajustement contrastif (#49), revues et audits (#109, #115, #120, #124), cadrage des supports J3 (#112) et rapport (#113) |
| Jibril | à compléter | à compléter | à compléter | à compléter |
| Maïmouna | Claude Code dans VS Code (2.1.322 au 12/11) | Claude Opus 5.5 | payante | compréhension des tâches et du code, relectures de pull requests, vérification de la chaîne RAG, rédaction du journal et des fiches |

## Mise en place
- Temps avant le premier résultat utile : (Remy, Antigravity) moins d'une heure lors de la première session sur PIAF et le journal (#30, #34, session 9).
- Installation et configuration : (Remy, Antigravity) utilisé sous Windows 11 avec accès direct aux fichiers du dépôt et exécution de scripts Python de contrôle.
- Prérequis découverts en chemin : (Remy, Antigravity) le shell par défaut sous Windows étant PowerShell et non Bash, les commandes contenant des variables `$` ou des blocs heredoc (`<< 'EOF'`) échouent ou sont interprétées prématurément : nécessité de passer par des scripts Python dédiés.
- Difficultés non expliquées par la documentation : (Remy, Antigravity) compilation PDF documentée en session 35 du journal : `latexmk` échoue sous Windows en l'absence d'interpréteur Perl installé, imposant d'enchaîner directement `python docs/latex/build.py` puis deux passes manuelles de `xelatex -interaction=nonstopmode`.

## Usage réel
- Tâche réalisée, ticket ou pull request : (Remy, Antigravity) tickets #30, #34, #45, #47, #49, #107, #112 et #113 ; PR #63, #75, #86/#87, #105, #120, #134 et #135.
- Commande, configuration ou scénario : (Remy, Antigravity) génération des scripts d'évaluation et d'export ONNX (`scripts/adaptation/`), vérification de métriques et de cohérence documentaire par scripts Python, préparation des supports J3 (#112) et des fiches outils (#113).
- Résultat obtenu : (Remy, Antigravity) production rapide des chaînes de calcul et de revue, mais plusieurs dérives factuelles ont dû être détectées et corrigées par contrôle croisé ou revue humaine : export `q8` initial sans `ActivationSymmetric` (`753/822`) et divergence de tokeniseur corrigés avant gel (sessions 33–34), renumérotation et bilan de la section 4 corrigés en revue de la PR #120 (session 45), perte des accents lors de la consolidation du support J3 (`917cf6c`, PR #134) et affirmations non fondées en première version de la PR #135 (version d'`uv` inexistante sur poste, attribution de #50/PR #78, statut de #49 et version d'Ollama).
- Temps gagné ou perdu, s'il peut être estimé : non mesuré au moment de l'usage (aucune reconstitution rétrospective).

## Qualités observées
- (Remy, Antigravity) Accès gratuit permettant à un membre sans abonnement Claude Code d'employer un agent intégré dans l'IDE (divergence documentée dans le préambule du journal d'usage IA et au jalon J2).
- (Remy, Antigravity) Réactivité élevée pour écrire des scripts de vérification et croiser localement les sources du dépôt (commits, tests unitaires, compilation LaTeX).

## Défauts et limites observés
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas :
  - (Remy, Antigravity) Propension à produire des informations plausibles mais fausses dès lors qu'elles ne sont pas vérifiées par une commande locale ou la lecture des commits/issues (exemple critique lors des fiches de la PR #135 : mention de `uv 0.4.29` alors qu'`uv` est absent du poste, confusion de paternité sur #50/PR #78, ou perte silencieuse des caractères accentués lors d'une réécriture complète sous #134).
  - (Remy, Antigravity) Scripts shell proposés initialement en syntaxe POSIX/Bash (pipes ou `latexmk`) inutilisables tels quels dans un environnement PowerShell Windows sans adaptation.
  - (Maïmouna, Claude Code) Il affirme parfois avec assurance des choses fausses, qu'il ne corrige qu'après une question de ma part : une phrase de réponse de Qwen présentée comme inventée alors que son contenu figurait dans trois passages, et le refus d'un lien attribué au site du ministère alors que la coupure venait de ma connexion (journal, section 4, 08/11).
  - (Maïmouna, Claude Code) Il a ouvert dans l'éditeur le fichier d'annotation complet, lot de test compris, au lieu des seules questions de calibration. J'ai fermé l'onglet sans le lire (journal, section 4, 08/11) : il faut lui indiquer à l'avance les fichiers à ne pas ouvrir.

## Comparaison
- Méthode ou outil utilisé auparavant : (Remy) interface web conversationnelle (copier-coller manuel vers VS Code).
- Différences observées : (Remy) l'agent exécutant les lectures de fichiers et les tests réduit les erreurs de recopie, mais transfère le risque d'erreur vers la validation des faits générés (dates, versions locales réelles, périmètre exact des tickets).
- Cas où l'ancienne méthode reste préférable : (Remy) l'édition manuelle directe est plus sûre pour les retouches ciblées sur un texte déjà relu ou la saisie stricte d'une donnée d'environnement vérifiée.

## Décision
À compléter : adopté / conservé pour certains usages / abandonné / à réévaluer.
- Motif :

## À retenir pour le rapport
- Apport : (Remy) capacité de prototypage, de vérification et d'audit multi-fichiers accessible sans coût d'abonnement pour l'équipe.
- Principale limite : (Remy) production récurrente de détails vraisemblables mais faux (versions, attributions, états de tickets) si l'auteur ne vérifie pas chaque fait sur le poste et dans l'historique Git avant publication.
- Ce que la documentation ne dit pas : (Remy) les erreurs typiques d'un agent sous Windows 11 (réflexes shell Bash vs PowerShell, encodages/accents lors de réécritures complètes) exigent des garde-fous explicites et une relecture humaine indépendante.

## Preuves
- Journal d'usage de l'IA (`docs/journal/JOURNAL_USAGE_IA.md`) : chaque usage y est tracé (notamment sessions 9, 10, 11, 33 à 35 et 44–45) ; cette fiche évalue les assistants dans la durée, sans dupliquer le journal.
- PR #134 et PR #135 : corrections post-revue illustrant la détection d'hallucinations factuelles et d'attribution sur la documentation.
