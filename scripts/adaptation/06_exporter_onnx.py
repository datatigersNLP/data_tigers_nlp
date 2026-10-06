"""
scripts/adaptation/06_exporter_onnx.py
Export du modèle ajusté en format ONNX (FP32) et quantification INT8 (q8) pour Transformers.js.
Contrôles de parité et fidélité numériques conformément au protocole du notebook 02.
"""

import json
import os
import sys
import time
from pathlib import Path
import numpy as np
import onnxruntime as ort
import torch
from onnxruntime.quantization import QuantType, quantize_dynamic
from transformers import AutoModel, AutoTokenizer

# Standard d'import du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class OnnxEncoderWrapper(torch.nn.Module):
    """Wrapper propre pour isoler les entrées/sorties pour l'export ONNX."""
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask):
        out = self.model(input_ids=input_ids, attention_mask=attention_mask)
        return out.last_hidden_state


def mean_pooling(last_hidden_state: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    """Moyenne masquée identique à Transformers.js et notebook 02."""
    input_mask_expanded = np.expand_dims(attention_mask, -1).astype(float)
    sum_embeddings = np.sum(last_hidden_state * input_mask_expanded, axis=1)
    sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
    return sum_embeddings / sum_mask


def normalize_l2(embeddings: np.ndarray) -> np.ndarray:
    """Normalisation L2 Euclidienne."""
    norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / np.clip(norm, a_min=1e-12, a_max=None)


def main():
    model_dir = Path("models/multilingual-e5-small-finetuned")
    onnx_dir = model_dir / "onnx"
    onnx_dir.mkdir(parents=True, exist_ok=True)

    fp32_path = onnx_dir / "model.onnx"
    q8_path = onnx_dir / "model_quantized.onnx"

    print("[1/5] Chargement du modèle PyTorch ajusté...")
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    base_model = AutoModel.from_pretrained(str(model_dir))
    wrapper = OnnxEncoderWrapper(base_model)
    wrapper.eval()

    print("[2/5] Export ONNX FP32...")
    dummy_input = tokenizer(
        ["query: exemple de question pour test", "passage: exemple de texte d'un passage juridique"],
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    t0 = time.time()
    torch.onnx.export(
        wrapper,
        (dummy_input["input_ids"], dummy_input["attention_mask"]),
        str(fp32_path),
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "last_hidden_state": {0: "batch_size", 1: "sequence_length"},
        },
        opset_version=14,
        do_constant_folding=True,
        dynamo=False,
    )
    t_export = time.time() - t0
    fp32_size_mb = fp32_path.stat().st_size / (1024 * 1024)
    print(f"       Export FP32 réussi en {t_export:.2f}s : {fp32_path.name} ({fp32_size_mb:.1f} Mio)")

    print("[3/5] Quantification dynamique INT8 (q8)...")
    t0 = time.time()
    quantize_dynamic(
        model_input=str(fp32_path),
        model_output=str(q8_path),
        weight_type=QuantType.QInt8,
    )
    t_quant = time.time() - t0
    q8_size_mb = q8_path.stat().st_size / (1024 * 1024)
    print(f"       Quantification q8 réussie en {t_quant:.2f}s : {q8_path.name} ({q8_size_mb:.1f} Mio)")

    print("[4/5] Contrôle 1 : Parité numérique ONNX FP32 vs PyTorch FP32...")
    test_texts = [
        "query: Quelle est la durée maximale de la période d'essai pour un cadre ?",
        "query: Comment démissionner sans préavis en cas de grossesse ?",
        "query: Quelles sont les sanctions en cas de harcèlement moral au travail ?",
        "passage: La rupture conventionnelle individuelle permet à l'employeur et au salarié de convenir d'un commun accord des conditions de la rupture.",
        "passage: Le travail de nuit est tout travail effectué entre 21 heures et 6 heures du matin. Il doit rester exceptionnel.",
    ]

    inputs = tokenizer(test_texts, padding=True, truncation=True, return_tensors="pt")

    # Inférence PyTorch
    with torch.no_grad():
        pt_out = wrapper(inputs["input_ids"], inputs["attention_mask"]).cpu().numpy()
    pt_emb = normalize_l2(mean_pooling(pt_out, inputs["attention_mask"].numpy()))

    # Inférence ONNX FP32
    sess_fp32 = ort.InferenceSession(str(fp32_path), providers=["CPUExecutionProvider"])
    onnx_inputs = {
        "input_ids": inputs["input_ids"].numpy(),
        "attention_mask": inputs["attention_mask"].numpy(),
    }
    onnx_fp32_out = sess_fp32.run(None, onnx_inputs)[0]
    onnx_fp32_emb = normalize_l2(mean_pooling(onnx_fp32_out, inputs["attention_mask"].numpy()))

    # Métriques de parité
    cos_parite = np.sum(pt_emb * onnx_fp32_emb, axis=1)
    max_abs_diff = np.max(np.abs(pt_emb - onnx_fp32_emb))
    min_cos_fp32 = float(np.min(cos_parite))

    print(f"       Cosinus minimal (ONNX FP32 vs PyTorch) : {min_cos_fp32:.8f} (seuil: 0.99999)")
    print(f"       Écart absolu maximal composante        : {max_abs_diff:.2e}")
    assert min_cos_fp32 >= 0.99999, f"Échec du test de parité FP32 : cosinus min {min_cos_fp32} < 0.99999"
    print("       -> Contrôle 1 (Parité FP32) : VALIDÉ AVEC SUCCÈS")

    print("[5/5] Contrôle 2 : Fidélité du modèle quantifié (q8 vs PyTorch FP32)...")
    sess_q8 = ort.InferenceSession(str(q8_path), providers=["CPUExecutionProvider"])
    onnx_q8_out = sess_q8.run(None, onnx_inputs)[0]
    onnx_q8_emb = normalize_l2(mean_pooling(onnx_q8_out, inputs["attention_mask"].numpy()))

    cos_fidelite = np.sum(pt_emb * onnx_q8_emb, axis=1)
    min_cos_q8 = float(np.min(cos_fidelite))
    med_cos_q8 = float(np.median(cos_fidelite))

    print(f"       Cosinus médian (ONNX q8 vs PyTorch)   : {med_cos_q8:.6f} (seuil: >= 0.98)")
    print(f"       Cosinus minimal (ONNX q8 vs PyTorch)  : {min_cos_q8:.6f} (seuil: >= 0.97)")
    assert min_cos_q8 >= 0.97, f"Échec du test de fidélité q8 : cosinus min {min_cos_q8} < 0.97"
    assert med_cos_q8 >= 0.98, f"Échec du test de fidélité q8 : cosinus médian {med_cos_q8} < 0.98"
    print("       -> Contrôle 2 (Fidélité q8) : VALIDÉ AVEC SUCCÈS")

    # Évaluation de la concordance de classement (Top-1 et Top-5)
    # Simuler le classement des 5 textes tests entre PyTorch et ONNX q8
    sims_pt = np.dot(pt_emb, pt_emb.T)
    sims_q8 = np.dot(onnx_q8_emb, pt_emb.T)
    top1_concordance = np.mean([np.argmax(sims_pt[i]) == np.argmax(sims_q8[i]) for i in range(len(test_texts))]) * 100
    print(f"       Concordance Top-1 PyTorch vs ONNX q8  : {top1_concordance:.1f}%")

    rapport_onnx = {
        "modele": "multilingual-e5-small-finetuned",
        "fp32": {
            "fichier": str(fp32_path.name),
            "taille_Mio": round(fp32_size_mb, 2),
            "parite_cosinus_min": min_cos_fp32,
            "parite_max_abs_diff": float(max_abs_diff),
            "valide": bool(min_cos_fp32 >= 0.99999),
        },
        "q8": {
            "fichier": str(q8_path.name),
            "taille_Mio": round(q8_size_mb, 2),
            "fidelite_cosinus_median": med_cos_q8,
            "fidelite_cosinus_min": min_cos_q8,
            "top1_concordance_pct": top1_concordance,
            "valide": bool(min_cos_q8 >= 0.97 and med_cos_q8 >= 0.98),
        },
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open("data/adaptation/rapport_onnx_parite.json", "w", encoding="utf-8") as f:
        json.dump(rapport_onnx, f, ensure_ascii=False, indent=2)

    print("\nRapport d'export et de contrôles enregistré dans data/adaptation/rapport_onnx_parite.json")


if __name__ == "__main__":
    main()
