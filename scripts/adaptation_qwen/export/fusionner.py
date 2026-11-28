"""Fusion d'un adaptateur LoRA de mlx-lm dans les poids bf16 officiels de Qwen (#140), matrice par matrice.

    python scripts/adaptation_qwen/export/fusionner.py --base <dossier HF bf16> --adaptateur <dossier mlx-lm> --sortie <dossier>

Pour chaque matrice adaptée : W' = f16( f32(W) + s · (lora_a · lora_b)ᵀ ), la formule de mlx_lm/tuner/lora.py (fuse,
ligne 52 en 0.32.2), calculée en fp32 et écrite en f16, dont la mantisse de 10 bits est plus fine que celle du bf16.
Les matrices modifiées vont dans des fragments « model-zz-lora-<couche>.safetensors » ; les fragments d'origine sont
liés sans copie. convert_hf_to_gguf.py (llama.cpp v0.7.0, conversion/base.py, index_tensors) lit tous les fragments de
l'index dans l'ordre alphabétique et garde le dernier tenseur lu : les fragments « zz » l'emportent. Le GGUF produit
doit ensuite être vérifié tenseur par tenseur (verifier_gguf.py) : ce comportement n'est pas supposé, il est contrôlé.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

CLE = re.compile(r"^model\.layers\.(\d+)\.(self_attn|mlp)\.(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)\.lora_(a|b)$")
FICHIERS_COPIES = ("config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json",
                   "vocab.json", "merges.txt", "LICENSE")
MAX_F16 = 65504.0


class ErreurFusion(ValueError):
    pass


def sha256(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 24), b""):
            h.update(bloc)
    return h.hexdigest()


def delta(lora_a, lora_b, echelle: float):
    """ΔW de forme (sortie, entrée) : s · (lora_a · lora_b)ᵀ, avec lora_a (entrée × r) et lora_b (r × sortie)."""
    return echelle * (lora_a.float() @ lora_b.float()).T


def modules_adaptes(cles) -> dict[int, list[str]]:
    """Modules adaptés par couche ; chaque module doit avoir exactement lora_a et lora_b."""
    modules: dict[str, set] = {}
    for k in cles:
        m = CLE.match(k)
        if not m:
            raise ErreurFusion(f"Clé d'adaptateur inattendue : {k}")
        modules.setdefault(k.rsplit(".", 1)[0], set()).add(m.group(4))
    if any(v != {"a", "b"} for v in modules.values()):
        raise ErreurFusion("Chaque module adapté doit avoir lora_a et lora_b")
    par_couche: dict[int, list[str]] = {}
    for mod in modules:
        par_couche.setdefault(int(mod.split(".")[2]), []).append(mod)
    return {c: sorted(v) for c, v in sorted(par_couche.items())}


def fusionner(base: Path, adaptateur: Path, sortie: Path) -> dict:
    import torch
    from safetensors import safe_open
    from safetensors.torch import save_file

    conf = json.loads((adaptateur / "adapter_config.json").read_text())
    if conf.get("fine_tune_type") != "lora" or conf.get("use_dora"):
        raise ErreurFusion("Seul un adaptateur LoRA simple est accepté")
    echelle = float(conf["lora_parameters"]["scale"])
    rang = int(conf["lora_parameters"]["rank"])
    index = json.loads((base / "model.safetensors.index.json").read_text())
    carte = index["weight_map"]
    sortie.mkdir(parents=True, exist_ok=False)
    adapt = safe_open(str(adaptateur / "adapters.safetensors"), "pt")
    ouverts, nouvelle_carte = {}, dict(carte)
    rapport = {"echelle": echelle, "rang": rang, "matrices": {}, "fragments": {}}
    for couche, mods in modules_adaptes(adapt.keys()).items():
        ecrits = {}
        for mod in mods:
            nom = mod + ".weight"
            fragment = carte[nom]
            if fragment not in ouverts:
                ouverts[fragment] = safe_open(str(base / fragment), "pt")
            w = ouverts[fragment].get_tensor(nom)
            if w.dtype != torch.bfloat16:
                raise ErreurFusion(f"{nom} : bf16 attendu, {w.dtype} trouvé")
            la, lb = adapt.get_tensor(mod + ".lora_a"), adapt.get_tensor(mod + ".lora_b")
            if tuple(la.shape) != (w.shape[1], rang) or tuple(lb.shape) != (rang, w.shape[0]):
                raise ErreurFusion(f"{mod} : formes incompatibles {tuple(la.shape)}, {tuple(lb.shape)}, {tuple(w.shape)}")
            w32 = w.float()
            d = delta(la, lb, echelle)
            fusion = w32 + d
            if not torch.isfinite(fusion).all() or fusion.abs().max().item() >= MAX_F16:
                raise ErreurFusion(f"{nom} : valeur hors de la plage du f16")
            f16 = fusion.to(torch.float16)
            rapport["matrices"][nom] = {
                "rho": (d.double().norm() / w32.double().norm()).item(),
                "part_inchangee_en_f16": (f16 == w.to(torch.float16)).double().mean().item(),
            }
            ecrits[nom] = f16.contiguous()
        fichier = f"model-zz-lora-{couche:02d}.safetensors"
        save_file(ecrits, str(sortie / fichier), metadata={"format": "pt"})
        for nom in ecrits:
            nouvelle_carte[nom] = fichier
        rapport["fragments"][fichier] = sha256(sortie / fichier)
    for fragment in sorted(set(carte.values())):
        os.symlink((base / fragment).resolve(), sortie / fragment)
    for f in FICHIERS_COPIES:
        if (base / f).exists():
            shutil.copy2(base / f, sortie / f)
    (sortie / "model.safetensors.index.json").write_text(
        json.dumps({"metadata": index.get("metadata", {}), "weight_map": nouvelle_carte}, indent=2) + "\n")
    rhos = [v["rho"] for v in rapport["matrices"].values()]
    rapport["resume"] = {"matrices": len(rhos), "rho_min": min(rhos), "rho_max": max(rhos),
                         "rho_moyen": sum(rhos) / len(rhos),
                         "adaptateur_sha256": sha256(adaptateur / "adapters.safetensors")}
    (sortie / "rapport_fusion.json").write_text(json.dumps(rapport, indent=1) + "\n")
    return rapport


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base", type=Path, required=True)
    p.add_argument("--adaptateur", type=Path, required=True)
    p.add_argument("--sortie", type=Path, required=True)
    a = p.parse_args(argv)
    try:
        rapport = fusionner(a.base, a.adaptateur, a.sortie)
    except ErreurFusion as exc:
        print(f"Fusion refusée : {exc}", file=sys.stderr)
        return 1
    print(json.dumps(rapport["resume"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
