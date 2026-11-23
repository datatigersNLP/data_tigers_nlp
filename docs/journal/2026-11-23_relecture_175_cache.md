# 23 novembre 2026 — Relecture et correctif du cache de la démonstration

- **Contexte :** Jibril demande la relecture de la PR #175 et le traitement du comportement hors ligne de la chaîne R1.
- **Assistant utilisé :** ChatGPT / Codex, pour lire le code et la documentation, préparer le correctif et exécuter les vérifications ci-dessous. La version exacte du modèle et la formule sont à confirmer par Jibril.
- **Constat :** en l'absence du fichier de mots vides, le chargeur de références lexicales tente un téléchargement au démarrage. La préparation préalable du cache avec connexion est déjà documentée.
- **Correctif proposé :** lire une seule fois la liste locale et vérifier son empreinte ; si elle est absente ou modifiée, remonter une erreur sans téléchargement. Construire BM25 avec les mêmes mots vides et négations conservées. Aucune modification des fichiers verrouillés de mesure ni exécution réelle sur le jeu de test.
- **Vérifications :** 12 tests de la couche v2 réussis avec récupération et Ollama simulés ; absence, empreinte incorrecte et absence d'appel au téléchargeur testées ; 3 requêtes factices donnent les mêmes tokens et scores BM25 avant/après avec racinisation simulée. Compilation Python et contrôle des espaces du diff réussis.
- **Limites :** dépendances scikit-learn et snowballstemmer absentes du venv de test : suite complète de récupération et parité avec la racinisation réelle non exécutées. Aucun essai réel sur le Mac de Mahé.
- **Diffusion :** branche de travail `fix/175-cache-snowball-hors-ligne`, issue de la tête de #175. Correctif à relire et à tester avec les dépendances réelles ; la PR #175 n'est pas modifiée.
