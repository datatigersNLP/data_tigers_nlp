"""
scripts/adaptation/01_preparer_benchmark.py
Préparation rigoureuse du banc de test (ground truth) à partir des questions annotées
et identification de la liste d'exclusion stricte pour l'entraînement.
"""

import io
import json
import os
import re
import subprocess
import unicodedata
import pandas as pd


def normalize(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[\s\W_]+", "", text)
    return text


def main():
    os.makedirs("data/adaptation", exist_ok=True)

    # 1. Charger les annotations depuis origin/feat/44-jeu-questions-annotees
    print("[1/4] Extraction des questions annotées (#44)...")
    csv_bytes = subprocess.check_output(
        ["git", "show", "origin/feat/44-jeu-questions-annotees:evaluation/questions/questions_annotees.csv"]
    )
    df_q = pd.read_csv(io.BytesIO(csv_bytes))

    # Sauvegarde locale sous data/ (ignoré par git)
    df_q.to_csv("data/adaptation/questions_annotees_reference.csv", index=False)
    print(f"       Total questions trouvées : {len(df_q)}")

    # 2. Charger les passages M2
    print("[2/4] Chargement des passages M2...")
    df_m2 = pd.read_parquet("data/decoupage/passages/passages_m2.parquet")
    print(f"       Total passages M2 : {len(df_m2)}")

    df_m2["norm_texte"] = df_m2["texte"].apply(normalize)

    # 3. Filtrer les questions du test dans_corpus
    test_q = df_q[(df_q["lot"] == "test") & (df_q["type"] == "dans_corpus")].copy()
    print(f"       Questions du test dans_corpus : {len(test_q)}")

    benchmark_items = []
    excluded_urls = set()

    # Toutes les fiches du test et de calibration sont exclues de l'entraînement
    all_evaluated_urls = set(df_q["url"].dropna().unique())
    excluded_urls.update(all_evaluated_urls)

    for _, row in test_q.iterrows():
        q_id = row["id"]
        question = row["question"]
        url = row["url"]
        extrait = row["extrait"] if pd.notna(row["extrait"]) else ""
        norm_ext = normalize(extrait)

        # Recherche des passages correspondants
        passages_url = df_m2[df_m2["url"] == url]
        gt_ids = []

        if norm_ext:
            # Chercher le préfixe ou sous-chaîne représentative de l'extrait
            pattern_len = min(len(norm_ext), 60)
            pattern = norm_ext[:pattern_len]
            matches = passages_url[passages_url["norm_texte"].str.contains(pattern, regex=False)]
            if len(matches) > 0:
                gt_ids = matches["passage_id"].tolist()
            else:
                # Si l'extrait commence plus loin ou variation d'en-tête
                for _, p_row in passages_url.iterrows():
                    if pattern[:40] in p_row["norm_texte"]:
                        gt_ids.append(p_row["passage_id"])

        # Si pas trouvé par sous-chaîne, fallback sur les passages de la section/url
        if not gt_ids and len(passages_url) > 0:
            gt_ids = passages_url["passage_id"].tolist()

        if not gt_ids:
            print(f"ATTENTION: Pas de passage trouvé pour {q_id} ({url})")

        benchmark_items.append({
            "id": q_id,
            "question": question,
            "url": url,
            "extrait": extrait,
            "ground_truth_passage_ids": gt_ids,
            "group": url,  # Pour test d'Obuchowski groupé par fiche
            "redacteur": row.get("redacteur", ""),
        })

    # 4. Sauvegarder benchmark_test.json et exclusions_train.json
    print("[3/4] Sauvegarde du benchmark de test...")
    with open("data/adaptation/benchmark_test.json", "w", encoding="utf-8") as f:
        json.dump(benchmark_items, f, ensure_ascii=False, indent=2)

    # Identifier tous les passage_id et url exclus de l'entraînement
    excluded_passages = df_m2[df_m2["url"].isin(excluded_urls)]["passage_id"].tolist()
    exclusions = {
        "excluded_urls": sorted(list(excluded_urls)),
        "excluded_passages_count": len(excluded_passages),
        "excluded_passage_ids": excluded_passages,
        "n_fiches_exclues": len(excluded_urls),
    }

    with open("data/adaptation/exclusions_train.json", "w", encoding="utf-8") as f:
        json.dump(exclusions, f, ensure_ascii=False, indent=2)

    print("[4/4] Bilan de préparation :")
    print(f"       Benchmark constitué : {len(benchmark_items)} questions de test")
    print(f"       Fiches strictement exclues du train set : {len(excluded_urls)}")
    print(f"       Passages M2 exclus de l'entraînement : {len(excluded_passages)} / {len(df_m2)} ({len(excluded_passages)/len(df_m2)*100:.1f}%)")
    print(f"       Passages M2 disponibles pour l'entraînement : {len(df_m2) - len(excluded_passages)}")


if __name__ == "__main__":
    main()
