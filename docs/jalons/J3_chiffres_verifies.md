# Chiffres vérifiés pour les supports de J3

**Équipe** Data Tigers  
**Ticket** #112 (supports de présentation du jalon J3)  
**Établi le** 30 octobre 2026 par Mahé BEGNIS, chaque chiffre relu dans sa source à cette date ; mis à jour le 2 novembre (version d'Ollama, calendrier, sources des 822 requêtes et des temps d'encodage), puis le 4 novembre (gel, lots d'adaptation, réserve sur J4)  
**Usage** reprendre ces chiffres et leurs formulations dans les supports ; un chiffre absent d'ici n'y figure qu'avec sa source.

---

## Volet A : le site de recherche

| Chiffre | Formulation juste | Source | À ne pas écrire |
|---|---|---|---|
| 261 fiches, 4 240 passages | corpus des fiches pratiques du ministère du Travail, instantané SocialGouv du 11 septembre 2026 | `README.md` | |
| 112,8 puis 65,7 Mio | modèle `multilingual-e5-small` en q8 : 112,8 Mio chez Xenova, 65,7 Mio après élagage sans perte du vocabulaire (-41,8 %) | `README.md`, `docs/etudes/evaluation/05_protocole_ajustement.md` | |
| 822 requêtes | vecteurs du modèle élagué identiques bit à bit au q8 d'origine dans le navigateur, sur les 822 requêtes de contrôle ; l'élagage garde intact tout texte en alphabet latin ou grec | `scripts/allegement/README.md` (lignes 42 et 44) ; `README.md` pour l'alphabet | |
| 18,3 ms | temps d'encodage d'une requête par le modèle élagué, celui que sert le site, dans le navigateur | `scripts/allegement/README.md` (ligne 44) | « moins de 25 ms sur Chromium et Firefox », sans source |
| 18,6 ms | même mesure avec le q8 d'origine non élagué (112,8 Mio), dans Chromium en WASM, au notebook 02 ; les temps varient d'une session du navigateur à l'autre | `docs/etudes/indexation/02_indexation.md` | 18,6 ms attribués au site |
| 73 et 24 questions | lot de test de `jeu-questions-v1` : 73 questions du corpus, issues de 61 fiches, et 24 hors corpus | `docs/etudes/evaluation/03_evaluation.md` | « 60 questions complétées par les 155 requêtes du CDTN » |
| 43,8 % contre 42,5 % | Recall@5 au niveau du passage : encodeur servi contre BM25 de référence (V3), écart +1,4 point, IC 95 % de -11,5 à +14,3 | `03_evaluation.md` | « supériorité prouvée », « +26,8 points » |
| critère du J2 satisfait | non-infériorité à la marge de 15 points (score de Tango : z = 2,45, p unilatéral 0,007) ; aucun des deux systèmes n'est démontré meilleur (McNemar p = 1,000) | `03_evaluation.md` | |
| 83,6 % contre 79,5 % | Recall@5 au niveau de la fiche : une fiche pertinente parmi les 5 premiers résultats | `03_evaluation.md` | |
| une question sur 73 | coût de la quantification q8, sans écart significatif | `03_evaluation.md` | « absence de régression confirmée » |
| 0,8560 | seuil d'abstention : 5e centile des scores maximaux de 479 variantes du CDTN, fixé le 10 octobre avant la mesure | `front/src/recherche/moteur.js`, `front/src/recherche/README.md` | « 0,8165, fixé par courbe ROC » |
| 0,841 | AUC du score maximal pour séparer corpus et hors corpus (IC 95 % de 0,747 à 0,921) : c'est un résultat, pas la méthode du seuil | `03_evaluation.md` | |
| 9 sur 24, 72 sur 73 | le seuil rejette 9 questions hors corpus sur 24 et garde 72 questions du corpus sur 73 : l'abstention reste à régler | `03_evaluation.md` | « abstention active validée » |

## Volet B : l'assistant local

| Chiffre | Formulation juste | Source | À ne pas écrire |
|---|---|---|---|
| 4,36 Gio | taille du modèle Qwen2.5-7B-Instruct en GGUF Q4_K_M, donnée par l'API d'Ollama | `docs/etudes/inference_locale_qwen.md` | « 4,36 Gio en VRAM » |
| 47 à 67 tokens/s | débit de deux appels avec un prompt court, sous Ollama 0.34.4 : « ni un benchmark statistique » | `inference_locale_qwen.md` | « latence au premier token inférieure à 2 s » : non mesurée |
| 5 passages | contexte `rag-b1-v1` de la #85 : 5 passages récupérés par E5 en fp32, contexte de 8 192 tokens, sortie de 512 | `scripts/rag/rag.py`, protocole 06 (PR #108) | |
| 0,8565 | seuil S de l'état B2 (valeur complète 0,856489074230194), IC 95 % de 0,8464 à 0,8653 par rééchantillonnage des 103 requêtes du CDTN (479 variantes) | protocole 06 (PR #108), section 7 | |
| M1 à M5 | abstention correcte et réponse affirmative sur les 24 hors corpus ; abstention à tort, citation valide et citation pertinente (règle D4) sur les 73 du corpus ; exactitude jugée à l'aveugle sur un échantillon | protocole 06 (PR #108), section 5 | trois « critères » sans rapport avec M1 à M5 |
| 8 questions | calibration du 29 octobre sur le Legion : elle valide le parcours, mais aucun taux de qualité ne se tire de 8 questions | revue de Jibril, PR #119 | un taux présenté comme résultat |
| 7,14 Gio | pic de mémoire du GPU de l'adaptation LoRA sur le Mac (16 couches), identique le 23 et le 30 octobre | PR #109 ; mesure du 30 octobre, session 46 du journal (#122, `963bf9e`) | « 16,86 Gio de mémoire libre » |
| 17,76 Gio, marge d'environ 10,6 Gio | plafond de mémoire recommandé par Metal sur ce Mac de 24 Gio, et marge sous le pic | mesure du 27 octobre (#13) | « exécution intégrale en VRAM » : le Mac a une mémoire unifiée |
| 10,5 puis 8,8 s par itération | Mac, 16 couches, le 23 (macOS 26.6.2) puis le 30 octobre (macOS 27.0.1) ; une exécution par configuration, écart non distinguable du bruit | PR #109 ; mesure du 30 octobre, session 46 du journal (#122, `963bf9e`) | |
| 9,17 Gio pour 7,96 Gio, 274 s par pas | Legion, RTX 5070 Laptop de 8 Gio : mémoire allouée au-delà de la mémoire physique, 0 octet libre ; le débordement vers la mémoire partagée est une hypothèse forte, pas une mesure | `docs/etudes/faisabilite_legion_20261026.md` | « RTX 4060 », « instabilité due au swap » |
| 0.40.13 | version d'Ollama épinglée pour toutes les mesures, avant comme après (arbitrage du 2 novembre) ; le protocole exige de couper les mises à jour automatiques, et Jibril déclare l'avoir fait sur le Legion, sans inspection à distance ; elle refuse les adaptateurs LoRA, d'où le témoin T | protocole 06 (PR #108), sections 3 et 8 | « 0.40.11 », version retenue le 30 octobre puis abandonnée |

## Calendrier

| Date | Étape et état | Source |
|---|---|---|
| 30/10 | réalisé : lot d'adaptation v1 généré, 298 exemples (273 pour l'entraînement, 25 pour la validation), 24,8 % d'abstentions ; refusé à la relecture du 02/11, 8 exemples faux sur 30 : il ne sert pas à l'entraînement | #107, PR #115 |
| 02/11 | réalisé : B0 recalibré sur le Legion, 0 erreur technique sur 8, sous Ollama 0.40.13 | PR #119 |
| 04/11 | réalisé : gel du protocole de mesure, #108 et #119 fusionnées | #52, #108 |
| 04/11 | réalisé : lot v2 décidé, puis amendé avant sa génération (réponses recopiées des passages, variante « passage retiré » retirée) ; génération en cours, effectifs non connus | #107 |
| après le verrou | prévu : mesure avant adaptation, sur le Legion, une fois le verrou de mesure versionné | #52 |
| 05/11 | prévu : relecture du lot v2 par deux relecteurs séparés, condition de l'entraînement | #107 |
| 06/11 | conditionnel : entraînement de l'adaptateur sur le Mac, si le lot v2 est accepté | #107, PR #125 |
| 12/11 | prévu : mesure après adaptation ; point d'arrêt | #107, #15 |
| 16/11 | J3, à confirmer par écrit | #8 |
| 19/11 | V1 du rapport | #113 |
| 20/11 | fin du projet : supports, site figé | #114 |
| 30/11 | J4, soutenance annoncée au 30/11, confirmation écrite attendue | #8 |

## À recompter le 13 novembre

Les chiffres qui changent d'ici J3 sont à relever le jour de l'assemblage, dans le dépôt :
- le nombre de sessions du journal et de lignes de sa section 4 ;
- les résultats de la mesure avant, puis après, s'ils sont disponibles, avec leurs intervalles.
