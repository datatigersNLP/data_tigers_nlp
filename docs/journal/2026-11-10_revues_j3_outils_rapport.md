# Journal d'usage IA : reprise des PR #134/#135, section 4.2 du rapport et contrôles de relecture (#141, #147, #148)

**Date et membre.** 10 novembre 2026, Remy RAYANE (`Remynou`).  
**Outil.** Google Antigravity.  
**Relecture humaine attendue.** Remy RAYANE avant publication des revues GitHub, fusion des PR #134/#135 et soumission de la PR du rapport (#113).

## Demande et produit

Suite aux demandes de Mahé pour l'échéance du 11/11 (#141) et du 13/11 (#134, #135, #112/#113), préparation et vérification locales sur trois branches :
1. **`docs/112-supports-j3` (PR #134, commit `7642777`)** : fusion propre avec `origin/dev`, traitement complet des retours de revue de Mahé du 09/11 sur `docs/jalons/J3_support_presentation.md` (rétablissement de 553 accents, suppression de chemins locaux `file:///`, correction de toutes les attributions et statuts au 10/11, renvoi vers `J3_diapositives_mahe.md` et `J3_diapositives_jibril.md` sans duplication des diapositives 4, 5, 7 et 8). Document prêt pour fusion en squash (historique préalable contenant `dc2c8b0`).
2. **`docs/113-fiches-outils-remy` (PR #135, commit `8cdabdf`)** : fusion propre avec `origin/dev`, rétablissement de `docs/suivi/OUTILS_NOVATEURS.md` à l'identique d'`origin/dev`, correction des six fiches de `docs/suivi/outils/` (`assistants-ia.md`, `github-cli.md`, `ollama.md`, `onnx-runtime.md`, `sentence-transformers.md`, `uv.md`) sans toucher aux lignes de Maïmouna, Vaneck, Jibril ou Mahé (absence de conflit avec #137).
3. **`docs/113-rapport-section-remy` (à partir d'`origin/dev`)** : actualisation de la seule section individuelle `### 4.2 Remy RAYANE` dans `docs/rapport/RAPPORT_FINAL.md`, recompilation de `docs/rapport/RAPPORT_FINAL.pdf` et consignation de cette note datée (`docs/journal/2026-11-10_revues_j3_outils_rapport.md`) sans toucher au fichier consolidé `JOURNAL_USAGE_IA.md` ni aux sections des autres membres.

## Contrôles exécutés et résultats vérifiés

- **PR #141 (`origin/feat/138-recuperation-v2`, Récupération v2)** : exécution locale sous Windows 11 / Python 3.12.10 de `python scripts/recuperation/test_recuperation.py` — **19 tests sur 19 réussis (`OK`)** en 36,452 s. Vérification des 10 empreintes de `scripts/rag/verrou_mesure.json` contre `VERROU_131`, de la réutilisation de `BM25Retriever` V3 / D4, de l'amendement A1 (`k = 10`, `voisins = False`, plafond `7 616` tokens) et du protocole 07 (`paired_success_test`, Obuchowski, Agresti-Min, Holm).
- **PR #147 (`origin/feat/140-export`, Export GGUF)** : exécution locale de `python scripts/adaptation_qwen/export/test_export.py` sous Windows 11 — **8 tests sur 9 réussis**, échec isolé de `test_fusion_valeurs_index_liens` sur `OSError: [WinError 1314]` (`os.symlink` restreint sans privilèges administrateur ni Mode Développeur activé sous Windows ; non bloquant pour l'exécution cible macOS de #140).
- **PR #148 (`origin/docs/112-diapositives-4-7`, Diapo 7)** : relecture croisée contre `#52`, `#107`, `#140`, PR `#141` et PR `#147` ; cohérence des chiffres du lot v2b (3/30 = 10,0 % au 10/11) et du témoin T vérifiée. Les propositions de commentaires pour #141, #147 et #148 sont préparées pour publication manuelle par Remy sur GitHub.
- **Environnement Windows 11 local** : `python -m pip list`, `ollama --version` et `git` ont vérifié les versions réelles (`Python 3.12.10`, `ollama 0.40.15` non épinglé face à `0.40.13` officiel du protocole 06, `onnx 1.23.2`, `onnxruntime 1.30.0`, `sentence-transformers 6.1.0`, `torch 2.14.0`, `transformers 5.18.0`, `uv` et `gh` non installés). Quota anonyme HTTP 403 constaté sur l'API REST GitHub dès enchaînement de requêtes.
- **Chaîne LaTeX et verrouillage** : `J3_support_presentation.md` compilé temporairement via `docs/latex/build.py` + deux passes `xelatex` (0 erreur, 0 `Overfull`, 0 `Underfull`, 0 `Missing character`, fichiers temporaires nettoyés car le PDF n'est pas suivi) ; `RAPPORT_FINAL.pdf` régénéré par la même chaîne. Aucun des fichiers protégés de `scripts/rag/verrou_mesure.json` n'est modifié.

## Erreurs générées détectées et corrigées avant livraison

- **Première version de la PR #135** : affirmations fausses corrigées avant nouveau commit (`uv 0.4.29` inventé alors qu'`uv` est absent du poste ; attribution erronée à Remy de l'élagage `#50 / PR #78` réalisé par Mahé ; script nommé `exporter_onnx.py` au lieu de `scripts/adaptation/06_exporter_onnx.py` ; mention `0.40.11` au lieu de l'épinglage officiel Ollama `0.40.13` et de `0.40.15` observé localement ; `#49` présenté à tort comme clos ; décisions `## Décision` retirées pour respecter l'arbitrage collectif ; référence erronée à un supposé oubli de préfixe en session 9 supprimée après vérification dans `JOURNAL_USAGE_IA.md` ; taille `112,8 Mio` de la base Xenova distinguée des `112,9 Mio` des exports de #49).
- **Consolidation de la PR #134 (`917cf6c`)** : perte de 553 accents et affirmations excessives sur `valider_citations` ou les performances RAG éliminées après relecture sur le code réel (`O(d)` sans `$`, récriture pour supprimer un débordement `Overfull \hbox` sur `\code{errAdaptersUnsupported}` et `\code{JOURNAL_USAGE_IA.md}`).

## Limites et temps

- Aucune revue GitHub ni fusion de PR n'a été postée automatiquement depuis cette session : la publication finale sur GitHub relève du compte de Remy.
- Temps de séance et d'appropriation non chronométrés (`non mesuré`, aucune reconstitution rétrospective).
