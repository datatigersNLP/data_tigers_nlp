"""
Expérimentation, comparaison des variantes lexicales et évaluation du portage client (Issue #47).

Ce script :
1. Contrôle le module (calculs à la main, recoupement avec rank_bm25), puis charge les 4 240 passages M2 du
   corpus travail-emploi (SocialGouv) en vérifiant leur empreinte contre le manifeste du notebook 01.
2. Construit et compare 5 variantes de TF-IDF et BM25 :
   - V0 : Sans filtrage de mots vides, sans racinisation
   - V1 : Mots vides Snowball (liste figée du notebook 01)
   - V2 : Mots vides Snowball SANS les négations/restrictions (« ne », « pas », « sans » conservés)
   - V3 : Racinisation Snowball + Mots vides sans négations
   - V4 : Coupure par fréquence (min_df=2, max_df=0.85) + Racinisation + Mots vides sans négations
3. Vérifie, sur le corpus entier, que la formule de rank_bm25 réimplantée redonne ses scores.
4. Mesure le vocabulaire, le poids réel d'un export JSON (brut et gzip) et le temps de réponse.
5. Montre les premiers résultats de BM25 sur des requêtes types. La comparaison avec l'encodeur n'est pas faite
   ici : elle relève du notebook 03 (#46), selon un protocole écrit avant la mesure.
6. Sauvegarde les résultats structurés dans data/evaluation/lexical/.

Dépendances : scripts/evaluation/requirements.txt. Depuis n'importe quel dossier :
    python scripts/evaluation/02_references_lexicales.py
"""

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi

# Import des modules locaux
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lexical_baselines import BM25Retriever, TfidfRetriever, LexicalTokenizer, sanity_check

# chemins ancrés à la racine du dépôt, quel que soit le dossier de lancement
RACINE = Path(__file__).resolve().parents[2]
FICHIER_M2 = RACINE / "data" / "decoupage" / "passages" / "passages_m2.parquet"
MANIFESTE = RACINE / "data" / "decoupage" / "passages" / "manifeste.json"
SORTIES_DIR = RACINE / "data" / "evaluation" / "lexical"
REPETITIONS_LATENCE = 20

REQUETES_TEST = [
    {"id": "q1_interdiction", "texte": "Quelles mentions sont interdites sur le bulletin de paie ?"},
    {"id": "q2_negation", "texte": "Mon employeur peut-il me licencier pendant un arrêt maladie ?"},
    {"id": "q3_sigle_cdi", "texte": "Combien de temps peut durer la période d'essai d'un CDI ?"},
    {"id": "q4_article_loi", "texte": "Quelles sont les dispositions de l'article L. 1221-19 du code du travail ?"},
    {"id": "q5_retractation", "texte": "Quel est le délai de rétractation lors d'une rupture conventionnelle ?"},
    {"id": "q6_restriction", "texte": "Licenciement pour inaptitude sans reclassement"},
]

# Définition des 5 variantes à étudier ; BM25 avec la formule de Lucene (k1 = 1,2, b = 0,75)
VARIANTES = {
    "V0_brut": {"nom": "V0 : Brut (sans mots vides, sans racinisation)",
                "stopwords": None, "stemming": None, "min_df": 1, "max_df": 1.0},
    "V1_snowball_std": {"nom": "V1 : Mots vides Snowball (sans racinisation)",
                        "stopwords": "snowball", "stemming": None, "min_df": 1, "max_df": 1.0},
    "V2_snowball_no_neg": {"nom": "V2 : Mots vides Snowball sans négations (sans racinisation)",
                           "stopwords": "snowball_no_negation", "stemming": None, "min_df": 1, "max_df": 1.0},
    "V3_stemming_no_neg": {"nom": "V3 : Racinisation + mots vides sans négations",
                           "stopwords": "snowball_no_negation", "stemming": "french", "min_df": 1, "max_df": 1.0},
    "V4_frequence_filtree": {"nom": "V4 : Coupure par fréquence (min_df=2, max_df=0.85) + V3",
                             "stopwords": "snowball_no_negation", "stemming": "french", "min_df": 2, "max_df": 0.85},
}


def charger_passages() -> pd.DataFrame:
    """Passages M2, refusés si leur empreinte diffère de celle que le notebook 01 a écrite dans son manifeste."""
    if not FICHIER_M2.exists() or not MANIFESTE.exists():
        raise FileNotFoundError(f"{FICHIER_M2} ou {MANIFESTE} introuvable : exécuter d'abord le notebook 01.")
    attendu = json.loads(MANIFESTE.read_text(encoding="utf-8"))["methodes"]["m2"]
    empreinte = hashlib.sha256(FICHIER_M2.read_bytes()).hexdigest()
    if empreinte != attendu["sha256_fichier"]:
        raise RuntimeError("passages_m2.parquet ne correspond pas au manifeste du notebook 01.")
    df = pd.read_parquet(FICHIER_M2)
    assert len(df) == attendu["passages"] == 4240, len(df)
    return df


def latence_ms(fonction, requetes) -> float:
    """Temps moyen par requête, en millisecondes, sur plusieurs répétitions (Python, un cœur)."""
    debut = time.perf_counter()
    for _ in range(REPETITIONS_LATENCE):
        fonction(requetes)
    return (time.perf_counter() - debut) / (REPETITIONS_LATENCE * len(requetes)) * 1000


def run_experiments():
    print("=" * 75)
    print("0. Contrôles du module")
    print("=" * 75)
    sanity_check()
    print("-> Calculs à la main et recoupement avec rank_bm25 : VALIDÉS.")

    print("\n" + "=" * 75)
    print("1. Chargement du corpus M2 SocialGouv")
    print("=" * 75)
    df_m2 = charger_passages()
    print(f"Total passages M2 chargés : {len(df_m2)} (empreinte conforme au manifeste du notebook 01)")
    # Textes indexés : en-tête (fiche > section) et corps, soit l'entrée de l'encodeur sans son préfixe
    corpus_textes = (df_m2.entete + "\n" + df_m2.texte).tolist()
    assert (df_m2.entree_encodeur == "passage: " + pd.Series(corpus_textes, index=df_m2.index)).all()
    passage_ids = df_m2.passage_id.tolist()
    requetes = [q["texte"] for q in REQUETES_TEST]

    print("\n" + "=" * 75)
    print("2. Recoupement de la formule de rank_bm25 sur le corpus entier")
    print("=" * 75)
    tok = LexicalTokenizer()
    okapi = BM25Okapi([tok(t) for t in corpus_textes])
    atire = BM25Retriever(k1=1.5, b=0.75, idf="atire").fit(corpus_textes, doc_ids=passage_ids)
    ecart = max(float(np.abs(atire.score_matrix([q])[0] - okapi.get_scores(tok(q))).max()) for q in requetes)
    assert ecart < 1e-9, ecart
    print(f"Écart maximal avec rank_bm25 sur les {len(requetes)} requêtes : {ecart:.1e}")

    print("\n" + "=" * 75)
    print("3. Construction et profilage des variantes lexicales")
    print("=" * 75)
    statistiques_variantes: Dict[str, Any] = {}
    moteurs_bm25: Dict[str, BM25Retriever] = {}
    for code, cfg in VARIANTES.items():
        print(f"\n--- {code} : {cfg['nom']} ---")
        retriever_bm25 = BM25Retriever(stopwords_variant=cfg["stopwords"], stemming=cfg["stemming"],
                                       min_df=cfg["min_df"], max_df=cfg["max_df"])
        retriever_bm25.fit(corpus_textes, doc_ids=passage_ids)
        retriever_tfidf = TfidfRetriever(stopwords_variant=cfg["stopwords"], stemming=cfg["stemming"],
                                         min_df=cfg["min_df"], max_df=cfg["max_df"])
        retriever_tfidf.fit(corpus_textes, doc_ids=passage_ids)
        moteurs_bm25[code] = retriever_bm25
        taille = retriever_bm25.export_size_bytes()
        vocab_tfidf = len(retriever_tfidf.vectorizer.vocabulary_)
        statistiques_variantes[code] = {
            "nom": cfg["nom"],
            "vocab_bm25": taille["vocab_size"],
            "vocab_tfidf": vocab_tfidf,
            "total_postings": taille["total_postings"],
            "json_raw_mb": round(taille["json_raw_mb"], 2),
            "json_gzip_mb": round(taille["json_gzip_mb"], 2),
            "latence_bm25_ms": round(latence_ms(retriever_bm25.batch_search, requetes), 2),
            "latence_tfidf_ms": round(latence_ms(retriever_tfidf.batch_search, requetes), 2),
        }
        s = statistiques_variantes[code]
        assert s["vocab_bm25"] == s["vocab_tfidf"], "BM25 et TF-IDF doivent avoir le même vocabulaire"
        print(f"  Vocabulaire : {s['vocab_bm25']} termes | postings : {s['total_postings']:,}")
        print(f"  Export JSON mesuré : {s['json_raw_mb']} Mio brut, {s['json_gzip_mb']} Mio en gzip")
        print(f"  Temps par requête : BM25 {s['latence_bm25_ms']} ms | TF-IDF {s['latence_tfidf_ms']} ms")

    print("\n" + "=" * 75)
    print("4. Premiers résultats de BM25 sur les requêtes types")
    print("=" * 75)
    resultats_requetes = []
    indexe = df_m2.set_index("passage_id")
    for q_item in REQUETES_TEST:
        print(f"\nRequête : '{q_item['texte']}'")
        row = {"id": q_item["id"], "question": q_item["texte"], "classements": {}}
        for code, moteur in moteurs_bm25.items():
            top = moteur.search(q_item["texte"], k=3)
            row["classements"][code] = [{"rang": r + 1, "passage_id": pid, "score": round(sc, 2),
                                         "fiche": indexe.loc[pid, "titre_fiche"],
                                         "section": indexe.loc[pid, "section_titre"]}
                                        for r, (pid, sc) in enumerate(top)]
            first = row["classements"][code][0]
            print(f"  [{code}] -> 1er : '{first['fiche']}' > '{first['section']}' (score {first['score']})")
        resultats_requetes.append(row)

    SORTIES_DIR.mkdir(parents=True, exist_ok=True)
    out_file = SORTIES_DIR / "lexical_baselines_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"statistiques_variantes": statistiques_variantes, "ecart_rank_bm25": ecart,
                   "resultats_requetes": resultats_requetes}, f, indent=2, ensure_ascii=False)
    print(f"\nRésultats complets sauvegardés dans : {out_file}")

    print("\n" + "=" * 75)
    print("TABLEAU SYNTHÉTIQUE DES VARIANTES LEXICALES (SUR 4 240 PASSAGES M2)")
    print("=" * 75)
    print(f"{'Variante':<22} | {'Vocabulaire':<11} | {'JSON brut':<9} | {'JSON gzip':<9} | {'BM25':<8} | TF-IDF")
    print("-" * 75)
    for code, s in statistiques_variantes.items():
        print(f"{code:<22} | {s['vocab_bm25']:<11} | {s['json_raw_mb']:<5} Mio | {s['json_gzip_mb']:<5} Mio | "
              f"{s['latence_bm25_ms']:<5} ms | {s['latence_tfidf_ms']} ms")
    print("=" * 75)


if __name__ == "__main__":
    run_experiments()
