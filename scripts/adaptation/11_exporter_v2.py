"""Export ONNX et q8 de l'encodeur ajusté v2 (#167, amendement A2 du protocole 05, section 5).

Mêmes étapes et mêmes réglages que `06_exporter_onnx.py`, qui a produit le q8 de la v1 : export fp32 (opset 14, mêmes
entrées d'exemple), quantification dynamique q8 (QInt8, par canal, plage réduite, activations symétriques), puis
contrôles de parité. Seuls les dossiers d'entrée et de sortie deviennent des paramètres. La commande `controle-v1`
rejoue l'export sur les poids de la v1 et exige de retrouver, octet pour octet, les fichiers livrés le 14 octobre :
c'est ce qui valide l'environnement avant d'exporter la v2.

Usage, depuis la racine du dépôt, environnement de l'entraînement (onnx 1.23.2, onnxruntime 1.30.0) :
    HF_HUB_OFFLINE=1 python scripts/adaptation/11_exporter_v2.py controle-v1
    HF_HUB_OFFLINE=1 python scripts/adaptation/11_exporter_v2.py v2      # puis dossier navigateur ajuste_v2
Les sorties vont dans data/adaptation/, qui n'est pas versionné.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[1]
_spec = importlib.util.spec_from_file_location("exporter_06", ICI / "06_exporter_onnx.py")
e06 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e06)

DOSSIER_V1 = RACINE / "data/adaptation/pack_modele_ajuste_14oct/models/multilingual-e5-small-finetuned"
LIVRES_V1 = {"onnx/model.onnx": "041a2d15f0455becdc684262f1139c45b6766402eb80da27cece9c7a7bb3666f",
             "onnx/model_quantized.onnx": "934a202bee5599fc45c0cb753414a7b2b490605bed84e72f471072e6ee53d047"}
V2 = RACINE / "data/adaptation/v2"
DOSSIER_V2 = V2 / "modele"
NAVIGATEUR = RACINE / "data/adaptation/navigateur"
NAV_V1 = NAVIGATEUR / "ajuste"
NAV_V2 = NAVIGATEUR / "ajuste_v2"
FICHIERS_XENOVA = ("config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json")
ENTREES_EXEMPLE = ["query: exemple de question pour test", "passage: exemple de texte d'un passage juridique"]
TEXTES_CONTROLE = [
    "query: Quelle est la durée maximale de la période d'essai pour un cadre ?",
    "query: Comment démissionner sans préavis en cas de grossesse ?",
    "query: Quelles sont les sanctions en cas de harcèlement moral au travail ?",
    "passage: La rupture conventionnelle individuelle permet à l'employeur et au salarié de convenir d'un commun accord des conditions de la rupture.",
    "passage: Le travail de nuit est tout travail effectué entre 21 heures et 6 heures du matin. Il doit rester exceptionnel.",
]


class ErreurExport(RuntimeError):
    """Précondition ou contrôle non rempli."""


def sha256_fichier(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 22), b""):
            h.update(bloc)
    return h.hexdigest()


def exporter(source: Path, sortie: Path) -> dict:
    """Les étapes de 06_exporter_onnx.py, dans le même ordre et avec les mêmes réglages."""
    import onnx
    import onnxruntime as ort
    import torch
    from onnxruntime.quantization import QuantType, quantize_dynamic
    from transformers import AutoModel, AutoTokenizer
    if sortie.exists():
        raise ErreurExport(f"{sortie} existe déjà : rien n'est écrasé")
    (sortie / "onnx").mkdir(parents=True)
    fp32, q8 = sortie / "onnx/model.onnx", sortie / "onnx/model_quantized.onnx"
    tokeniseur = AutoTokenizer.from_pretrained(str(source))
    modele = AutoModel.from_pretrained(str(source))
    enveloppe = e06.OnnxEncoderWrapper(modele)
    enveloppe.eval()
    tokeniseur.save_pretrained(str(sortie))
    modele.config.save_pretrained(str(sortie))
    exemple = tokeniseur(ENTREES_EXEMPLE, padding=True, truncation=True, return_tensors="pt")
    torch.onnx.export(
        enveloppe, (exemple["input_ids"], exemple["attention_mask"]), str(fp32),
        input_names=["input_ids", "attention_mask"], output_names=["last_hidden_state"],
        dynamic_axes={"input_ids": {0: "batch_size", 1: "sequence_length"},
                      "attention_mask": {0: "batch_size", 1: "sequence_length"},
                      "last_hidden_state": {0: "batch_size", 1: "sequence_length"}},
        opset_version=14, do_constant_folding=True, dynamo=False)
    quantize_dynamic(model_input=str(fp32), model_output=str(q8), weight_type=QuantType.QInt8,
                     per_channel=True, reduce_range=True, extra_options={"ActivationSymmetric": True})
    operateurs = sorted({n.op_type for n in onnx.load(str(q8)).graph.node})
    with open(sortie / "quant_config.json", "w", encoding="utf-8") as f:
        json.dump({"per_channel": True, "reduce_range": True, "extra_options": {"ActivationSymmetric": True},
                   "per_model_config": {"model": {"op_types": operateurs, "weight_type": "QInt8"}}}, f, indent=4)
    # Contrôles de 06 : parité fp32 (cosinus minimal au moins 0,99999) et fidélité du q8
    entrees = tokeniseur(TEXTES_CONTROLE, padding=True, truncation=True, return_tensors="pt")
    masque = entrees["attention_mask"].numpy()
    with torch.no_grad():
        pt = e06.normalize_l2(e06.mean_pooling(enveloppe(entrees["input_ids"], entrees["attention_mask"]).numpy(), masque))
    feed = {"input_ids": entrees["input_ids"].numpy(), "attention_mask": masque}
    o32 = e06.normalize_l2(e06.mean_pooling(ort.InferenceSession(str(fp32), providers=["CPUExecutionProvider"])
                                            .run(None, feed)[0], masque))
    o8 = e06.normalize_l2(e06.mean_pooling(ort.InferenceSession(str(q8), providers=["CPUExecutionProvider"])
                                           .run(None, feed)[0], masque))
    cos32, cos8 = (pt * o32).sum(axis=1), (pt * o8).sum(axis=1)
    if cos32.min() < 0.99999:
        raise ErreurExport(f"Parité fp32 non atteinte : cosinus minimal {cos32.min():.8f}")
    return {"source": str(source.relative_to(RACINE)), "sortie": str(sortie.relative_to(RACINE)),
            "fp32": {"sha256": sha256_fichier(fp32), "octets": fp32.stat().st_size, "cosinus_min": float(cos32.min())},
            "q8": {"sha256": sha256_fichier(q8), "octets": q8.stat().st_size, "cosinus_min": float(cos8.min()),
                   "cosinus_median": float(np.median(cos8))},
            "operateurs": operateurs}


def controle_v1() -> dict:
    r = exporter(DOSSIER_V1, V2 / "export_v1_controle")
    identiques = {"onnx/model.onnx": r["fp32"]["sha256"] == LIVRES_V1["onnx/model.onnx"],
                  "onnx/model_quantized.onnx": r["q8"]["sha256"] == LIVRES_V1["onnx/model_quantized.onnx"]}
    r["identiques_aux_fichiers_livres"] = identiques
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if not all(identiques.values()):
        raise ErreurExport("L'export rejoué sur la v1 ne redonne pas les fichiers livrés : environnement non validé")
    return r


def exporter_v2() -> dict:
    r = exporter(DOSSIER_V2, V2 / "export")
    if NAV_V2.exists():
        raise ErreurExport(f"{NAV_V2} existe déjà")
    (NAV_V2 / "onnx").mkdir(parents=True)
    for f in FICHIERS_XENOVA:            # mêmes fichiers que le dossier navigateur de la v1 (Xenova, révision 761b726d)
        shutil.copyfile(NAV_V1 / f, NAV_V2 / f)
        if sha256_fichier(NAV_V2 / f) != sha256_fichier(NAV_V1 / f):
            raise ErreurExport(f"Copie de {f} différente")
    shutil.copyfile(V2 / "export/onnx/model_quantized.onnx", NAV_V2 / "onnx/model_quantized.onnx")
    r["navigateur"] = {"dossier": str(NAV_V2.relative_to(RACINE)),
                       "fichiers": {str(p.relative_to(NAV_V2)): sha256_fichier(p)
                                    for p in sorted(NAV_V2.rglob("*")) if p.is_file()}}
    print(json.dumps(r, ensure_ascii=False, indent=1))
    with open(V2 / "export_v2.json", "x", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    return r


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("commande", choices=("controle-v1", "v2"))
    a = p.parse_args(argv)
    controle_v1() if a.commande == "controle-v1" else exporter_v2()
    return 0


if __name__ == "__main__":
    sys.exit(main())
