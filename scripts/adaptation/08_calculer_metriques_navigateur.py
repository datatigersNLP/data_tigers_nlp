"""
scripts/adaptation/08_calculer_metriques_navigateur.py
Calcul rigoureux des métriques de fidélité issues de l'exécution dans le navigateur (Chromium WASM)
sur l'ensemble des 822 requêtes réalistes du corpus M2 (Notebook 02, section 8).
Consigne les métriques comparatives et les empreintes SHA-256 des fichiers opposables.
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def calculer_sha256(chemin: Path) -> str:
    """Calcule l'empreinte SHA-256 hexadécimale d'un fichier."""
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def mean_pooling(last_hidden_state: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    input_mask_expanded = np.expand_dims(attention_mask, -1).astype(float)
    sum_embeddings = np.sum(last_hidden_state * input_mask_expanded, axis=1)
    sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
    return sum_embeddings / sum_mask


def normalize_l2(embeddings: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / np.clip(norm, a_min=1e-12, a_max=None)


def encode_pytorch_unitaire(model, tokenizer, texts):
    """Encodage PyTorch FP32 requête par requête (batch_size=1)."""
    model.eval()
    embs = []
    for t in texts:
        inp = tokenizer([t], padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            out = model(**inp).last_hidden_state.cpu().numpy()
        mask = inp["attention_mask"].numpy()
        embs.append(normalize_l2(mean_pooling(out, mask))[0])
    return np.array(embs)


def main():
    parser = argparse.ArgumentParser(
        description="Calcul des métriques de fidélité in-browser (822 requêtes) et empreintes SHA-256."
    )
    parser.add_argument(
        "--fichier",
        type=str,
        default="data/indexation/controle/fidelite_navigateur_ajuste.json",
        help="Chemin du fichier de résultats issu du navigateur (default: data/indexation/controle/fidelite_navigateur_ajuste.json)",
    )
    parser.add_argument(
        "--modele",
        type=str,
        default="ajuste",
        help="Type de modèle analysé : 'ajuste' ou 'temoin'/'base'",
    )
    args = parser.parse_args()

    fichier_nav = Path(args.fichier)
    if not fichier_nav.is_absolute():
        fichier_nav = PROJECT_ROOT / fichier_nav

    if not fichier_nav.exists():
        print(f"ERREUR : Fichier de résultats introuvable : {fichier_nav}")
        print("Veuillez d'abord exécuter le contrôle dans le navigateur via fidelite_navigateur.html.")
        sys.exit(1)

    est_temoin = args.modele in ("temoin", "base") or "temoin" in fichier_nav.name
    if est_temoin:
        source_model = "intfloat/multilingual-e5-small"
        model_onnx_dir = PROJECT_ROOT / "models" / "multilingual-e5-small-base"
        passages_path = PROJECT_ROOT / "data" / "adaptation" / "passage_embeddings_baseline.npy"
        nom_sortie = "rapport_metriques_navigateur_temoin.json"
        etiquette = "Modèle témoin de BASE exporté (models/multilingual-e5-small-base)"
    else:
        source_model = "models/multilingual-e5-small-finetuned"
        model_onnx_dir = PROJECT_ROOT / "models" / "multilingual-e5-small-finetuned"
        passages_path = PROJECT_ROOT / "data" / "adaptation" / "passage_embeddings_apres.npy"
        nom_sortie = "rapport_metriques_navigateur.json"
        etiquette = "Modèle AJUSTÉ (models/multilingual-e5-small-finetuned)"

    q8_onnx_path = model_onnx_dir / "onnx" / "model_quantized.onnx"
    requetes_path = PROJECT_ROOT / "data" / "indexation" / "controle" / "requetes_fidelite.json"

    print("=" * 78)
    print(f"ANALYSE DE FIDÉLITÉ NAVIGATEUR (Chromium WASM) : {etiquette}")
    print("=" * 78)

    # 1. Calcul des empreintes SHA-256
    print("\n[1/4] Empreintes cryptographiques SHA-256 des artefacts opposables :")
    sha_resultats = calculer_sha256(fichier_nav)
    print(f"   * Fichier de résultats navigateur : {fichier_nav.name}")
    print(f"     Taille    : {fichier_nav.stat().st_size:,} octets")
    print(f"     SHA-256   : {sha_resultats}")

    if q8_onnx_path.exists():
        sha_onnx = calculer_sha256(q8_onnx_path)
        print(f"   * Modèle ONNX quantifié           : {q8_onnx_path.name}")
        print(f"     Taille    : {q8_onnx_path.stat().st_size / (1024 * 1024):.2f} Mio")
        print(f"     SHA-256   : {sha_onnx}")
    else:
        sha_onnx = None
        print(f"   * Modèle ONNX : {q8_onnx_path} introuvable sur le disque.")

    # 2. Chargement des données navigateur et références
    print("\n[2/4] Chargement des données et génération des représentations PyTorch FP32...")
    data_nav = json.loads(fichier_nav.read_text(encoding="utf-8"))
    if "q8" not in data_nav.get("resultats", {}):
        print("ERREUR : Aucune section 'q8' trouvée dans le fichier de résultats.")
        sys.exit(1)

    res_q8 = data_nav["resultats"]["q8"]
    V_nav = np.array(res_q8["vecteurs"], dtype=np.float32)
    encodage_ms_total = res_q8.get("encodage_ms", 0.0)
    chargement_ms = res_q8.get("chargement_ms", 0.0)

    req_json = json.loads(requetes_path.read_text(encoding="utf-8"))
    prefixe = req_json["prefixe"]
    raw_queries = req_json["requetes"]
    queries = [prefixe + q for q in raw_queries]
    nb_queries = len(queries)
    assert len(V_nav) == nb_queries, f"Nombre de vecteurs ({len(V_nav)}) != nombre de requêtes ({nb_queries})"

    passages_emb = np.load(passages_path)
    print(f"   Index passages chargé : {passages_path.name} ({passages_emb.shape[0]} passages, dim {passages_emb.shape[1]})")

    print(f"   Calcul de la référence PyTorch FP32 unitaire sur {nb_queries} requêtes ({source_model})...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(str(PROJECT_ROOT / source_model if (PROJECT_ROOT / source_model).exists() else source_model))
    pt_model = AutoModel.from_pretrained(str(PROJECT_ROOT / source_model if (PROJECT_ROOT / source_model).exists() else source_model))
    Q_ref = encode_pytorch_unitaire(pt_model, tokenizer, queries)
    t_pt = time.time() - t0
    print(f"   Référence PyTorch calculée en {t_pt:.2f}s ({1000 * t_pt / nb_queries:.1f} ms/req).")

    # 3. Calcul des métriques de fidélité
    print("\n[3/4] Calcul des métriques de fidélité (représentations et classement)...")
    cosinus = np.sum(Q_ref * V_nav, axis=1)
    cos_min = float(np.min(cosinus))
    cos_med = float(np.median(cosinus))
    cos_mean = float(np.mean(cosinus))

    scores_ref = np.dot(Q_ref, passages_emb.T)
    scores_nav = np.dot(V_nav, passages_emb.T)

    top1_ref = np.argmax(scores_ref, axis=1)
    top1_nav = np.argmax(scores_nav, axis=1)

    top1_concordance_nb = int(np.sum(top1_ref == top1_nav))
    top1_concordance_pct = float(top1_concordance_nb / nb_queries * 100)

    top5_nav = np.argsort(-scores_nav, axis=1)[:, :5]
    top1_dans_top5_nb = int(sum(top1_ref[i] in top5_nav[i] for i in range(nb_queries)))
    top1_dans_top5_pct = float(top1_dans_top5_nb / nb_queries * 100)

    all_ranks_nav = np.argsort(-scores_nav, axis=1)
    ranks_of_ref = []
    for i in range(nb_queries):
        target = top1_ref[i]
        rank = int(np.where(all_ranks_nav[i] == target)[0][0]) + 1
        ranks_of_ref.append(rank)
    max_rank = int(np.max(ranks_of_ref))
    p95_rank = float(np.percentile(ranks_of_ref, 95))
    p99_rank = float(np.percentile(ranks_of_ref, 99))
    ms_par_req = round(encodage_ms_total / nb_queries, 1)

    # 4. Affichage du tableau de conformité
    print("\n[4/4] Synthèse comparative vs Référence q8 base du Notebook 02 :")
    print("-" * 78)
    print(f"{'Métrique (822 requêtes, 4 240 passages)':<44} | {'Navigateur WASM':<15} | {'Réf q8 base (NB 02)':<15}")
    print("-" * 78)
    print(f"{'Cosinus médian avec PyTorch FP32':<44} | {cos_med:<15.5f} | {'0.99655':<15}")
    print(f"{'Cosinus minimal avec PyTorch FP32':<44} | {cos_min:<15.5f} | {'0.99196':<15}")
    print(f"{'Concordance Top-1 (même 1er résultat)':<44} | {f'{top1_concordance_pct:.2f}% ({top1_concordance_nb}/{nb_queries})':<15} | {'91.8% (755/822)':<15}")
    print(f"{'Premier résultat réf dans le Top-5':<44} | {f'{top1_dans_top5_pct:.2f}% ({top1_dans_top5_nb}/{nb_queries})':<15} | {'99.9% (821/822)':<15}")
    print(f"{'Rang maximal de dégradation':<44} | {f'{max_rank} (P99: {p99_rank:.1f})':<15} | {'9':<15}")
    print(f"{'Temps d encodage moyen par requête':<44} | {f'{ms_par_req} ms':<15} | {'18.6 ms':<15}")
    print("-" * 78)

    rapport = {
        "etiquette": etiquette,
        "modele_source": source_model,
        "fichier_resultats": str(fichier_nav.name),
        "sha256_resultats": sha_resultats,
        "modele_onnx_quantifie": str(q8_onnx_path.name) if q8_onnx_path.exists() else None,
        "sha256_model_quantized_onnx": sha_onnx,
        "nb_requetes": nb_queries,
        "nb_passages": int(passages_emb.shape[0]),
        "cosinus": {
            "minimum": cos_min,
            "mediane": cos_med,
            "moyenne": cos_mean,
        },
        "classement": {
            "top1_concordance_pct": top1_concordance_pct,
            "top1_concordance_nb": top1_concordance_nb,
            "top1_dans_top5_pct": top1_dans_top5_pct,
            "top1_dans_top5_nb": top1_dans_top5_nb,
            "rang_maximal": max_rank,
            "p95_rang": p95_rank,
            "p99_rang": p99_rank,
        },
        "latence": {
            "chargement_ms": chargement_ms,
            "encodage_ms_total": encodage_ms_total,
            "ms_par_requete": ms_par_req,
        },
        "reference_notebook_02": {
            "cosinus_mediane": 0.99655,
            "cosinus_minimum": 0.99196,
            "top1_concordance_pct": 91.8,
            "top1_dans_top5_pct": 99.9,
            "rang_maximal": 9,
            "ms_par_requete": 18.6,
        },
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    out_path = PROJECT_ROOT / "data" / "adaptation" / nom_sortie
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRapport complet consigné dans {out_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
