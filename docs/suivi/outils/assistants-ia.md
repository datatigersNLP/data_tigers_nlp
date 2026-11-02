# Assistants de développement IA

## Identification
- Version : plusieurs assistants et versions selon les membres, voir « Versions utilisées »
- Nature : assistants conversationnels et de programmation
- Assignés : toute l'équipe ; prévus : toute l'équipe
- Coordination : toute l'équipe
- Période d'utilisation : à compléter
- Besoin du projet auquel il répond : expliquer, rédiger, relire du code et des documents, vérifier des données.

## Versions utilisées
Chaque membre tient sa propre ligne à jour, avec une ligne par assistant s'il en utilise plusieurs. Chaque
observation des rubriques suivantes précise l'assistant concerné, par exemple « (Vaneck, <assistant>) ».

| Membre | Assistant | Modèle ou version | Formule (gratuite, payante…) | Usages principaux |
|---|---|---|---|---|
| Vaneck | à compléter | à compléter | à compléter | à compléter |
| Mahé | Claude Code (2.1.306 au 26/10) | Claude Opus 5 (8 sessions), puis Claude Opus 5.5 (14 sessions), d'après le journal | à compléter | audits du dépôt, revues de PR, protocoles et mesures, rédaction des documents, actions GitHub en son nom |
| Rémy | Google Antigravity & Gemini 3.8 Flash | Gemini 3.8 Flash (High), agent autonome sous Antigravity IDE | formule gratuite | génération et audit de scripts Python, audits de contributions Git, revue technique de faisabilité LoRA (#109, #115), cadrage des supports J3 (#112) |
| Jibril | à compléter | à compléter | à compléter | à compléter |
| Maïmouna | à compléter | à compléter | à compléter | à compléter |

## Mise en place
- Temps avant le premier résultat utile : (Remy, Antigravity) Moins de 10 minutes sous Windows 11 pour charger le dépôt et exécuter une première analyse documentaire.
- Installation et configuration : (Remy, Antigravity) Prise en main directe via Antigravity IDE avec configuration du modèle Gemini 3.8 Flash (High).
- Prérequis découverts en chemin : (Remy, Antigravity) Environnement d'exécution sous PowerShell nécessitant d'échapper strictement les variables et les arguments pour éviter l'évaluation prématurée de syntaxe (`$var`).
- Difficultés non expliquées par la documentation : (Remy, Antigravity) Gestion des fins de ligne (CRLF sous Windows vs LF sous Linux/macOS) lors de l'appel de compilateurs ou de scripts Python manipulant des empreintes SHA-256.

## Usage réel
- Tâche réalisée, ticket ou pull request : (Remy, Antigravity) Tickets #49, #50, #107, #112 et PRs #109, #115, #120.
- Commande, configuration ou scénario : (Remy, Antigravity) Scripts Python ad-hoc pour l'interrogation de l'API REST GitHub, l'audit arithmétique des commits, le contrôle d'étanchéité des 61 fiches exclues et la compilation de documents XeLaTeX.
- Résultat obtenu : (Remy, Antigravity) Détection rapide des conflits de fusion, correction des métriques de marge mémoire et automatisation des relectures de code.
- Temps gagné ou perdu, s'il peut être estimé : (Remy, Antigravity) Gain estimé à plusieurs heures sur le diagnostic des divergences Git et l'alignement des chiffres de présentation.

## Qualités observées
- (Remy, Antigravity) Gratuité d'accès pour les membres ne disposant pas d'un abonnement payant à Claude Code.
- (Remy, Antigravity) Grande rapidité de génération avec Gemini 3.8 Flash et excellente capacité à combiner analyse de code, édition multi-fichiers et exécution de commandes locales de validation.

## Défauts et limites observés
- Cas d'échec, messages d'erreur, limites, dépendances, ce que la documentation ne dit pas : (Remy, Antigravity) Absence de terminal Bash natif sous Windows : les commandes shell conçues pour macOS/Linux (comme `latexmk` avec Perl ou certains pipes zsh) doivent être adaptées ou relayées par Python.

## Comparaison
- Méthode ou outil utilisé auparavant : ChatGPT web et édition manuelle sous VS Code.
- Différences observées : L'exécution directe d'outils et l'accès direct aux fichiers suppriment les allers-retours de copier-coller et réduisent considérablement les risques d'hallucination sur les chemins ou les commits réels.
- Cas où l'ancienne méthode reste préférable : ChatGPT reste pratique pour des synthèses rapides sans ouvrir l'environnement de développement complet.

## Décision
Adopté.
- Motif : (Remy) Solution autonome complète et gratuite, idéale sous Windows 11 pour tenir les standards de vérification du projet sans surcoût.

## À retenir pour le rapport
- Apport :
- Principale limite :
- Ce que la documentation ne dit pas :

## Preuves
- Journal d'usage de l'IA (`docs/journal/JOURNAL_USAGE_IA.md`) : chaque usage y est tracé ; cette fiche évalue les assistants dans la durée, sans dupliquer le journal.
