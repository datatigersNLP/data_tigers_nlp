# 2 novembre 2026 — Intégration du socle Agent0 et exclusion de l'entraînement (#94/#95)

**Membre concerné.** Jibril BENSALEM. **Outil.** Codex dans ChatGPT Work.
**Relecteur.** Mahé BEGNIS pour les têtes approuvées ; le nouvel incrément documentaire de #106
reste à revalider indépendamment.

## Demande et références

Après les approbations de Mahé du 2 novembre sur #103/`c5e3d8d` et #106/`1defb44`,
Jibril autorise la fusion de #103, l'actualisation de #106, l'ajout de la précision excluant les
candidats des données d'entraînement, puis une nouvelle demande de relecture à Mahé.
La fusion de #106 attend cette revalidation sur la tête finale.

README, revues, fils et arbres Git complets relus ; aucun AGENTS.md ou CONTRIBUTING dans
les arbres inspectés. Les fils ne portent aucun commentaire non résolu. Aucun contrôle CI
n'est rapporté sur la tête de #103 ; les tests locaux et ceux de Mahé sont des preuves distinctes.

## Contrôles avant fusion

Dev avait avancé à `fe657f44a2ee88edcb5eb9e5b440cabd5c8960cc` depuis la revue.
Le résultat de fusion à trois versions est sans conflit et conserve exactement les 17 fichiers
de scripts/synthetic/ approuvés, y compris le verrou. Les changements récents de dev et son
journal central sont préservés.

Environnement isolé recréé depuis le verrou après nettoyage de la copie locale :
Python 3.12.14, Pydantic 2.14.0, 33 dépendances applicables compatibles selon uv pip check.
**149 tests réussis en 0,562 s**, sur fixtures et clients simulés ; aucun appel réel au modèle
ni nouvel essai Windows. La fusion réelle a ensuite été comparée au résultat préparé :
tous les chemins, modes et empreintes concordent.

## Intégration et précision documentaire

#103 fusionnée dans dev avec le commit `dcb790ddaab42bfd613de597b9cd095367c674a7`.
L'actualisation de #106 reprend cette dépendance et les contributions de dev avec les parents
conservés, sans réécriture d'historique. Les scripts restent identiques à ceux déjà testés.

Sur #106 uniquement, le guide et le README du support indiquent que huit passages proviennent
de trois fiches, dont une appartient aux 61 fiches du lot de test humain jeu-questions-v1,
selon la vérification de Mahé en revue. Les 15 candidats de ce support sont explicitement
exclus des exemples d'entraînement ou d'adaptation, pour le générateur comme pour l'encodeur,
même après relecture. Les dates et états du résumé sont actualisés.

La modification propre au nouvel incrément porte sur ces deux documents et cette note datée.
Les formulations, sources, observations, rapports, grille, scripts, dépendances, corpus et
Gold Set sont conservés. Les décisions humaines restent vierges et les 15 entrées en attente.
Aucun lot figé ou nouvelle évaluation n'est déclaré.

## Relecture restante

Mahé doit revoir la tête finale de #106 en tenant compte de l'actualisation depuis dev
**et de la précision documentaire ajoutée**, et non d'une simple reprise de dev.
Aucune approbation antérieure n'est présumée valable pour cette nouvelle tête.

Cette note date l'assistance IA sans réserver un numéro dans le journal central de la pile.
Aucun temps réel inventé, verdict humain, réemploi pour l'entraînement ou clôture de ticket.
Aucun changement de main ; seule #103 est fusionnée dans dev pour cette opération.
