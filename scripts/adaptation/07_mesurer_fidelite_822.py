"""
scripts/adaptation/07_mesurer_fidelite_822.py
Mesure de fidélité du modèle quantifié (q8) vs PyTorch FP32 sur les 822 requêtes réalistes (Notebook 02).

Note méthodologique sur les moteurs d'exécution :
Les calculs ONNX Runtime CPU avec quantification dynamique INT8 dépendent des instructions
vectorielles CPU de la machine hôte (AVX2 sur x86_64 sous Windows vs NEON sur Mac ARM64), ce qui
induit de légères variations d'arrondis arithmétiques (ex. 762/822 sur PC x86 vs 791/822 sur Mac ARM).
Ces chiffres Python sont donc indicatifs de l'environnement hôte.
La mesure de référence opposable et strictement reproductible inter-machines est celle exécutée
dans le navigateur WebAssembly (WASM via scripts/adaptation/08_calculer_metriques_navigateur.py).
"""

import json
import time
from pathlib import Path
import numpy as np
import onnxruntime as ort
import torch
from transformers import AutoModel, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def mean_pooling(last_hidden_state: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    input_mask_expanded = np.expand_dims(attention_mask, -1).astype(float)
    sum_embeddings = np.sum(last_hidden_state * input_mask_expanded, axis=1)
    sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
    return sum_embeddings / sum_mask


def normalize_l2(embeddings: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / np.clip(norm, a_min=1e-12, a_max=None)


import argparse
import json
import time
from pathlib import Path
import numpy as np
import onnxruntime as ort
import torch
from transformers import AutoModel, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def mean_pooling(last_hidden_state: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    input_mask_expanded = np.expand_dims(attention_mask, -1).astype(float)
    sum_embeddings = np.sum(last_hidden_state * input_mask_expanded, axis=1)
    sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
    return sum_embeddings / sum_mask


def normalize_l2(embeddings: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / np.clip(norm, a_min=1e-12, a_max=None)


def encode_pytorch(model, tokenizer, texts, batch_size=1):
    """Encodage PyTorch FP32. batch_size=1 reflète l'usage unitaire réel du navigateur."""
    model.eval()
    all_embs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        inputs = tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            out = model(**inputs).last_hidden_state.cpu().numpy()
        mask = inputs["attention_mask"].numpy()
        embs = normalize_l2(mean_pooling(out, mask))
        all_embs.append(embs)
    return np.vstack(all_embs)


def encode_onnx(session, tokenizer, texts, batch_size=1):
    """
    Encodage ONNX q8 avec batch_size=1.
    En lots > 1, le padding influe sur les échelles de la quantification dynamique.
    Comme le site client encode une requête à la fois, batch_size=1 est la mesure rigoureuse.
    """
    all_embs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        inputs = tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="np")
        onnx_inputs = {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"],
        }
        out = session.run(None, onnx_inputs)[0]
        embs = normalize_l2(mean_pooling(out, inputs["attention_mask"]))
        all_embs.append(embs)
    return np.vstack(all_embs)


def main():
    parser = argparse.ArgumentParser(description="Mesure de fidélité q8 vs PyTorch FP32 sur les 822 requêtes.")
    parser.add_argument(
        "--modele",
        type=str,
        default="ajuste",
        help="Modèle à tester : 'ajuste' (modèle fine-tuné) ou 'base' (témoin exporté de base)"
    )
    args = parser.parse_args()

    if args.modele in ("base", "temoin"):
        source_model = "intfloat/multilingual-e5-small"
        model_dir = Path("models/multilingual-e5-small-base")
        passages_path = Path("data/adaptation/passage_embeddings_baseline.npy")
        nom_sortie = "rapport_fidelite_822_base.json"
        nom_modele = "multilingual-e5-small-base (témoin)"
    else:
        source_model = "models/multilingual-e5-small-finetuned"
        model_dir = Path("models/multilingual-e5-small-finetuned")
        passages_path = Path("data/adaptation/passage_embeddings_apres.npy")
        nom_sortie = "rapport_fidelite_822.json"
        nom_modele = "multilingual-e5-small-finetuned"

    q8_path = model_dir / "onnx" / "model_quantized.onnx"
    requetes_path = Path("data/indexation/controle/requetes_fidelite.json")

    print(f"[1/4] Chargement des 822 requêtes et du catalogue passages pour {nom_modele}...")
    req_data = json.loads(requetes_path.read_text(encoding="utf-8"))
    prefixe = req_data["prefixe"]
    raw_queries = req_data["requetes"]
    queries = [prefixe + q for q in raw_queries]
    print(f"       {len(queries)} requêtes prêtes.")

    passages_emb = np.load(passages_path)
    print(f"       Index passages chargé : {passages_path.name} shape {passages_emb.shape}")

    print(f"[2/4] Chargement des modèles (source: {source_model}, ONNX: {q8_path})...")
    REVISION_BASE = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
    load_kwargs = {"revision": REVISION_BASE} if source_model == "intfloat/multilingual-e5-small" else {}
    tokenizer = AutoTokenizer.from_pretrained(source_model, **load_kwargs)
    pt_model = AutoModel.from_pretrained(source_model, **load_kwargs)
    sess_q8 = ort.InferenceSession(str(q8_path), providers=["CPUExecutionProvider"])

    print("[3/4] Encodage unitaire (batch_size=1) des 822 requêtes...")
    t0 = time.time()
    q_ref = encode_pytorch(pt_model, tokenizer, queries, batch_size=1)
    t_pt = time.time() - t0
    print(f"       PyTorch FP32 (batch=1) : {t_pt:.2f}s ({1000 * t_pt / len(queries):.1f} ms/req)")

    t0 = time.time()
    q_q8 = encode_onnx(sess_q8, tokenizer, queries, batch_size=1)
    t_q8 = time.time() - t0
    print(f"       ONNX q8      (batch=1) : {t_q8:.2f}s ({1000 * t_q8 / len(queries):.1f} ms/req)")

    # 1. Cosinus requête par requête
    cosinus = np.sum(q_ref * q_q8, axis=1)
    cos_min = float(np.min(cosinus))
    cos_med = float(np.median(cosinus))
    cos_mean = float(np.mean(cosinus))
    print(f"\n[4/4] Métriques de fidélité sur les représentations :")
    print(f"       Cosinus minimal : {cos_min:.6f} (réf base Notebook 02 : 0.99196)")
    print(f"       Cosinus médian  : {cos_med:.6f} (réf base Notebook 02 : 0.99655)")
    print(f"       Cosinus moyen   : {cos_mean:.6f}")

    # 2. Classement sur les 4 240 passages
    print("\n       Calcul du classement sur les 4 240 passages de référence...")
    scores_ref = np.dot(q_ref, passages_emb.T)
    scores_q8 = np.dot(q_q8, passages_emb.T)

    top1_ref = np.argmax(scores_ref, axis=1)
    top1_q8 = np.argmax(scores_q8, axis=1)

    top1_concordance = float(np.mean(top1_ref == top1_q8) * 100)
    concordance_nb = int(np.sum(top1_ref == top1_q8))
    print(f"       Concordance Top-1 (même 1er résultat) : {top1_concordance:.2f} % ({concordance_nb} / {len(queries)})")
    print(f"       (Réf base Notebook 02 : 91.8 % / 755 sur 822)")

    # Présence du Top-1 ref dans le Top-5 q8
    top5_q8 = np.argsort(-scores_q8, axis=1)[:, :5]
    top1_dans_top5 = float(np.mean([top1_ref[i] in top5_q8[i] for i in range(len(queries))]) * 100)
    top1_dans_top5_nb = int(sum(top1_ref[i] in top5_q8[i] for i in range(len(queries))))
    print(f"       Premier de référence dans le Top-5 q8 : {top1_dans_top5:.2f} % ({top1_dans_top5_nb} / {len(queries)})")
    print(f"       (Réf base Notebook 02 : 99.9 % / 821 sur 822)")

    # Rang maximal où tombe le Top-1 de référence
    all_ranks_q8 = np.argsort(-scores_q8, axis=1)
    ranks_of_ref_top1 = []
    for i in range(len(queries)):
        target = top1_ref[i]
        rank = int(np.where(all_ranks_q8[i] == target)[0][0]) + 1
        ranks_of_ref_top1.append(rank)
    max_rank = int(np.max(ranks_of_ref_top1))
    p95_rank = float(np.percentile(ranks_of_ref_top1, 95))
    p99_rank = float(np.percentile(ranks_of_ref_top1, 99))
    print(f"       Rang maximal du Top-1 de référence    : {max_rank} (P95 : {p95_rank:.1f}, P99 : {p99_rank:.1f})")

    rapport = {
        "modele": nom_modele,
        "batch_size": 1,
        "nb_requetes": len(queries),
        "nb_passages": int(passages_emb.shape[0]),
        "cosinus": {
            "minimum": cos_min,
            "mediane": cos_med,
            "moyenne": cos_mean,
        },
        "classement_passages": {
            "top1_concordance_pct": top1_concordance,
            "top1_concordance_nb": concordance_nb,
            "top1_dans_top5_pct": top1_dans_top5,
            "top1_dans_top5_nb": top1_dans_top5_nb,
            "rang_maximal": max_rank,
            "p95_rang": p95_rank,
            "p99_rang": p99_rank,
        },
        "latence": {
            "pytorch_ms_par_requete": round(1000 * t_pt / len(queries), 2),
            "onnx_q8_ms_par_requete": round(1000 * t_q8 / len(queries), 2),
        },
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    out_file = Path("data/adaptation") / nom_sortie
    out_file.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRapport complet consigné dans {out_file}")


if __name__ == "__main__":
    main()
