"""
scripts/adaptation/07_mesurer_fidelite_822.py
Mesure rigoureuse de fidélité du modèle quantifié (q8) vs PyTorch FP32
sur l'ensemble des 822 requêtes réalistes du corpus M2 (Notebook 02).
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


def encode_pytorch(model, tokenizer, texts, batch_size=32):
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


def encode_onnx(session, tokenizer, texts, batch_size=32):
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
    model_dir = Path("models/multilingual-e5-small-finetuned")
    q8_path = model_dir / "onnx" / "model_quantized.onnx"
    passages_path = Path("data/adaptation/passage_embeddings_apres.npy")
    requetes_path = Path("data/indexation/controle/requetes_fidelite.json")

    print("[1/4] Chargement des 822 requêtes et du catalogue des 4 240 passages...")
    req_data = json.loads(requetes_path.read_text(encoding="utf-8"))
    prefixe = req_data["prefixe"]
    raw_queries = req_data["requetes"]
    queries = [prefixe + q for q in raw_queries]
    print(f"       {len(queries)} requêtes prêtes.")

    passages_emb = np.load(passages_path)
    print(f"       Index passages chargé : shape {passages_emb.shape}")

    print("[2/4] Chargement des modèles...")
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    pt_model = AutoModel.from_pretrained(str(model_dir))
    sess_q8 = ort.InferenceSession(str(q8_path), providers=["CPUExecutionProvider"])

    print("[3/4] Encodage des 822 requêtes...")
    t0 = time.time()
    q_ref = encode_pytorch(pt_model, tokenizer, queries, batch_size=32)
    t_pt = time.time() - t0
    print(f"       PyTorch FP32 : {t_pt:.2f}s ({1000 * t_pt / len(queries):.1f} ms/req)")

    t0 = time.time()
    q_q8 = encode_onnx(sess_q8, tokenizer, queries, batch_size=32)
    t_q8 = time.time() - t0
    print(f"       ONNX q8      : {t_q8:.2f}s ({1000 * t_q8 / len(queries):.1f} ms/req)")

    # 1. Cosinus requête par requête
    cosinus = np.sum(q_ref * q_q8, axis=1)
    cos_min = float(np.min(cosinus))
    cos_med = float(np.median(cosinus))
    cos_mean = float(np.mean(cosinus))
    print(f"\n[4/4] Métriques de fidélité sur les représentations :")
    print(f"       Cosinus minimal : {cos_min:.6f}")
    print(f"       Cosinus médian  : {cos_med:.6f}")
    print(f"       Cosinus moyen   : {cos_mean:.6f}")

    # 2. Classement sur les 4 240 passages
    print("\n       Calcul du classement sur les 4 240 passages de référence...")
    # Scores de similarité
    scores_ref = np.dot(q_ref, passages_emb.T)
    scores_q8 = np.dot(q_q8, passages_emb.T)

    top1_ref = np.argmax(scores_ref, axis=1)
    top1_q8 = np.argmax(scores_q8, axis=1)

    top1_concordance = float(np.mean(top1_ref == top1_q8) * 100)
    print(f"       Concordance Top-1 (même 1er résultat) : {top1_concordance:.2f} % ({np.sum(top1_ref == top1_q8)} / {len(queries)})")

    # Présence du Top-1 ref dans le Top-5 q8
    top5_q8 = np.argsort(-scores_q8, axis=1)[:, :5]
    top1_dans_top5 = float(np.mean([top1_ref[i] in top5_q8[i] for i in range(len(queries))]) * 100)
    print(f"       Premier de référence dans le Top-5 q8 : {top1_dans_top5:.2f} %")

    # Rang maximal où tombe le Top-1 de référence
    all_ranks_q8 = np.argsort(-scores_q8, axis=1)
    ranks_of_ref_top1 = []
    for i in range(len(queries)):
        target = top1_ref[i]
        rank = int(np.where(all_ranks_q8[i] == target)[0][0]) + 1
        ranks_of_ref_top1.append(rank)
    max_rank = int(np.max(ranks_of_ref_top1))
    p99_rank = float(np.percentile(ranks_of_ref_top1, 99))
    print(f"       Rang maximal du Top-1 de référence    : {max_rank} (99e percentile : {p99_rank:.1f})")

    rapport = {
        "modele": "multilingual-e5-small-finetuned",
        "nb_requetes": len(queries),
        "nb_passages": int(passages_emb.shape[0]),
        "cosinus": {
            "minimum": cos_min,
            "mediane": cos_med,
            "moyenne": cos_mean,
        },
        "classement_passages": {
            "top1_concordance_pct": top1_concordance,
            "top1_dans_top5_pct": top1_dans_top5,
            "rang_maximal": max_rank,
            "p99_rang": p99_rank,
        },
        "latence": {
            "pytorch_ms_par_requete": round(1000 * t_pt / len(queries), 2),
            "onnx_q8_ms_par_requete": round(1000 * t_q8 / len(queries), 2),
        },
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    out_file = Path("data/adaptation/rapport_fidelite_822.json")
    out_file.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRapport complet consigné dans {out_file}")


if __name__ == "__main__":
    main()
