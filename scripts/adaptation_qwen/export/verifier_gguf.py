"""Vérifie un GGUF f16 de Qwen2.5 tenseur par tenseur contre ses sources (#140).

    python scripts/adaptation_qwen/export/verifier_gguf.py <fichier.gguf> <dossier HF bf16 d'origine> [<dossier fusionné>]

Attendu, à l'égalité exacte : pour une matrice fusionnée, le tenseur f16 de son fragment model-zz-lora ; pour toute autre
matrice, f16(poids bf16) ; pour les vecteurs (normes, biais), f32(poids bf16). Sans dossier fusionné, toutes les matrices
sont comparées aux poids d'origine (témoin T) ; appliqué à un GGUF fusionné, ce mode sert de contrôle négatif : il doit
signaler exactement les matrices modifiées.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

COUCHE = {"attn_norm": "input_layernorm", "ffn_norm": "post_attention_layernorm", "attn_q": "self_attn.q_proj",
          "attn_k": "self_attn.k_proj", "attn_v": "self_attn.v_proj", "attn_output": "self_attn.o_proj",
          "ffn_gate": "mlp.gate_proj", "ffn_up": "mlp.up_proj", "ffn_down": "mlp.down_proj"}
GLOBAL = {"token_embd.weight": "model.embed_tokens.weight", "output_norm.weight": "model.norm.weight",
          "output.weight": "lm_head.weight"}


class ErreurVerification(ValueError):
    pass


def nom_hf(nom: str) -> str:
    """Nom Hugging Face d'un tenseur GGUF de Qwen2 (la conversion de llama.cpp ne permute pas q et k pour Qwen2)."""
    if nom in GLOBAL:
        return GLOBAL[nom]
    m = re.fullmatch(r"blk\.(\d+)\.([a-z_]+)\.(weight|bias)", nom)
    if not m or m.group(2) not in COUCHE:
        raise ErreurVerification(f"Tenseur GGUF inattendu : {nom}")
    return f"model.layers.{m.group(1)}.{COUCHE[m.group(2)]}.{m.group(3)}"


def verifier(gguf_path: Path, base: Path, fusion: Path | None = None) -> dict:
    import numpy as np
    import torch
    from gguf import GGUFReader
    from safetensors import safe_open

    carte_base = json.loads((base / "model.safetensors.index.json").read_text())["weight_map"]
    carte_fusion = json.loads((fusion / "model.safetensors.index.json").read_text())["weight_map"] if fusion else {}
    fusionnees = {k for k, v in carte_fusion.items() if v.startswith("model-zz-lora-")}
    ouverts = {}

    def lire(dossier, fichier, nom):
        cle = (str(dossier), fichier)
        if cle not in ouverts:
            ouverts[cle] = safe_open(str(dossier / fichier), "pt")
        return ouverts[cle].get_tensor(nom)

    bilan = {"tenseurs": 0, "fusionnes_egaux": 0, "base_egaux": 0, "vecteurs_egaux": 0, "ecarts": []}
    vus = set()
    for t in GGUFReader(str(gguf_path)).tensors:
        hf = nom_hf(t.name)
        vus.add(hf)
        donnees = np.asarray(t.data)
        if hf in fusionnees:
            attendu, cle = lire(fusion, carte_fusion[hf], hf).numpy(), "fusionnes_egaux"
        else:
            w = lire(base, carte_base[hf], hf)
            attendu = (w.to(torch.float16) if w.dim() == 2 else w.to(torch.float32)).numpy()
            cle = "base_egaux" if w.dim() == 2 else "vecteurs_egaux"
        bilan["tenseurs"] += 1
        if donnees.dtype == attendu.dtype and donnees.shape == attendu.shape and np.array_equal(donnees, attendu):
            bilan[cle] += 1
        else:
            bilan["ecarts"].append([t.name, str(donnees.dtype), list(donnees.shape), str(attendu.dtype), list(attendu.shape)])
    bilan["tenseurs_hf_absents_du_gguf"] = sorted(set(carte_base) - vus)
    bilan["fusionnees_attendues"] = len(fusionnees)
    bilan["conforme"] = (not bilan["ecarts"] and not bilan["tenseurs_hf_absents_du_gguf"]
                         and bilan["fusionnes_egaux"] == len(fusionnees))
    return bilan


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) not in (2, 3):
        print(__doc__)
        return 2
    bilan = verifier(Path(argv[0]), Path(argv[1]), Path(argv[2]) if len(argv) == 3 else None)
    print(json.dumps(bilan, indent=1))
    return 0 if bilan["conforme"] else 1


if __name__ == "__main__":
    sys.exit(main())
