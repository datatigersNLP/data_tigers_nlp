"""
scripts/adaptation/03_generer_paires_locales.py
Génération rigoureuse de paires d'entraînement synthétiques via Qwen2.5-7B local (Ollama).
Garantie d'étanchéité stricte : exclusion des fiches du test et filtrage anti-fuite.
"""

import json
import os
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path
import pandas as pd

# Standard d'import du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def normalize_tokens(text: str) -> set:
    """Normalise et extrait les mots pour le calcul de recouvrement."""
    text = unicodedata.normalize("NFKC", text).lower()
    tokens = set(re.findall(r"\b\w{3,}\b", text))
    return tokens


def jaccard_overlap(tokens_a: set, tokens_b: set) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def call_ollama_qwen(prompt: str, api_url: str = "http://127.0.0.1:11434") -> str:
    payload = {
        "model": "qwen2.5-7b-instruct:q4_k_m-local",
        "prompt": prompt,
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 75,
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{api_url}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    return res.get("response", "").strip()


def main():
    print("[1/5] Chargement du corpus M2 et de la liste d'exclusion...")
    with open("data/adaptation/exclusions_train.json", "r", encoding="utf-8") as f:
        exclusions = json.load(f)
    excluded_urls = set(exclusions["excluded_urls"])

    # Charger le benchmark de test pour le contrôle de non-chevauchement
    with open("data/adaptation/benchmark_test.json", "r", encoding="utf-8") as f:
        benchmark_test = json.load(f)

    test_tokens_list = [normalize_tokens(item["question"]) for item in benchmark_test]

    df_m2 = pd.read_parquet("data/decoupage/passages/passages_m2.parquet")

    # Filtrage strict des passages éligibles
    eligible_df = df_m2[
        (~df_m2["url"].isin(excluded_urls)) &
        (df_m2["n_tokens"] >= 120) &
        (df_m2["n_tokens"] <= 420) &
        (df_m2["texte"].str.len() > 100)
    ].copy()

    print(f"       Passages éligibles hors test : {len(eligible_df)} répartis sur {eligible_df['url'].nunique()} fiches")

    # Sélection stratifiée : 1 passage par fiche pour maximiser la diversité
    print("[2/5] Sélection stratifiée d'un sous-ensemble diversifié...")
    # On sélectionne les passages les plus proches de la taille médiane (250 tokens) pour chaque fiche
    eligible_df["taille_diff"] = (eligible_df["n_tokens"] - 250).abs()
    selected_passages = (
        eligible_df.sort_values("taille_diff")
        .groupby("url")
        .first()
        .reset_index()
    )

    # Cibler environ 100-110 passages de fiches distinctes
    n_cible = min(110, len(selected_passages))
    selected_passages = selected_passages.sample(n=n_cible, random_state=42).reset_index(drop=True)
    print(f"       Sélection de {len(selected_passages)} passages représentatifs de fiches distinctes.")

    print("[3/5] Génération locale des questions avec Qwen2.5-7B (Ollama)...")
    paires_valides = []
    rejetees = 0
    t0_global = time.time()

    for idx, row in selected_passages.iterrows():
        titre = row["titre_fiche"]
        texte_passage = row["texte"][:900]

        prompt = f"""Tu es un salarié ou un travailleur qui cherche une information précise sur ses droits ou obligations.
À partir de l'extrait de fiche du ministère du Travail ci-dessous, formule une question réaliste, précise et naturelle en français qu'un salarié pourrait poser et dont la réponse figure dans cet extrait.

Règles impératives :
1. Formule UNIQUEMENT la question, sans introduction, sans guillemets, ni formule de politesse.
2. La question doit être autonome et compréhensible sans avoir lu le texte (pas de "Selon le texte", "D'après l'extrait").
3. Termine par un point d'interrogation.

Titre de la fiche : {titre}
Extrait :
{texte_passage}

Question :"""

        try:
            t0_q = time.time()
            raw_response = call_ollama_qwen(prompt)
            dt_q = time.time() - t0_q

            # Nettoyage
            question = raw_response.strip().strip('"').strip("'").strip("«»").strip()
            # Prendre la première ligne si plusieurs lignes générées
            lines = [l.strip() for l in question.split("\n") if l.strip()]
            question = lines[0] if lines else ""

            # Filtres de qualité stricts
            if not question.endswith("?"):
                # Si le point d'interrogation manque à la fin mais est présent dans la phrase
                if "?" in question:
                    question = question[:question.index("?") + 1]
                else:
                    rejetees += 1
                    continue

            if len(question) < 25 or len(question) > 220:
                rejetees += 1
                continue

            # Vérifier l'absence de méta-formulations
            lower_q = question.lower()
            if any(forbidden in lower_q for forbidden in ["selon le texte", "d'après le texte", "selon cet extrait", "ce document"]):
                rejetees += 1
                continue

            # Contrôle strict d'anti-fuite (Jaccard lexical face à toutes les questions de test)
            q_tokens = normalize_tokens(question)
            max_jaccard = max([jaccard_overlap(q_tokens, t_tokens) for t_tokens in test_tokens_list]) if test_tokens_list else 0.0

            if max_jaccard > 0.40:
                print(f"       [ALERTE FUITE] Question rejetée pour similarité ({max_jaccard:.2f}) avec le test set: {question}")
                rejetees += 1
                continue

            # Paire acceptée
            paire = {
                "passage_id": row["passage_id"],
                "url": row["url"],
                "titre_fiche": titre,
                "question": question,
                "query": f"query: {question}",
                "passage": row["entree_encodeur"],  # Contient "passage: <titre> | <texte>"
                "max_jaccard_test": round(max_jaccard, 4),
                "generation_time_s": round(dt_q, 2),
            }
            paires_valides.append(paire)
            print(f"       [{len(paires_valides):03d}/{n_cible}] ({dt_q:.1f}s) {question}")

        except Exception as e:
            print(f"       Erreur lors de la génération passage {row['passage_id']}: {e}")
            rejetees += 1
            time.sleep(1)

    t_total = time.time() - t0_global
    print(f"\n[4/5] Fin de la génération en {t_total:.1f}s.")
    print(f"       Paires validées : {len(paires_valides)}")
    print(f"       Paires rejetées : {rejetees}")

    # Sauvegarde en JSONL pour l'entraînement
    output_path = "data/adaptation/train_paires.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for p in paires_valides:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"       Paires sauvegardées dans {output_path}")

    # Sauvegarde d'un échantillon de contrôle qualité pour audit manuel
    echantillon = paires_valides[:15]
    with open("data/adaptation/echantillon_controle_train.json", "w", encoding="utf-8") as f:
        json.dump(echantillon, f, ensure_ascii=False, indent=2)
    print("       Échantillon de contrôle sauvegardé dans data/adaptation/echantillon_controle_train.json")


if __name__ == "__main__":
    main()
