"""Tests de la chaîne d'export (#140), sur des tenseurs et des exemples factices, sans modèle réel."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import controle_requantification as cr  # noqa: E402
import fusionner as fu  # noqa: E402
import verifier_gguf as vg  # noqa: E402


def ecrire_base(dossier: Path, torch, save_file):
    """Mini modèle bf16 en deux fragments : une couche, q_proj (4 × 6) et une norme."""
    g = torch.Generator().manual_seed(0)
    q = (torch.randn(4, 6, generator=g) * 0.02).to(torch.bfloat16)
    norme = torch.ones(6, dtype=torch.bfloat16)
    save_file({"model.layers.0.self_attn.q_proj.weight": q}, str(dossier / "model-00001-of-00002.safetensors"))
    save_file({"model.layers.0.input_layernorm.weight": norme}, str(dossier / "model-00002-of-00002.safetensors"))
    carte = {"model.layers.0.self_attn.q_proj.weight": "model-00001-of-00002.safetensors",
             "model.layers.0.input_layernorm.weight": "model-00002-of-00002.safetensors"}
    (dossier / "model.safetensors.index.json").write_text(json.dumps({"metadata": {}, "weight_map": carte}))
    (dossier / "config.json").write_text("{}")
    return q


def ecrire_adaptateur(dossier: Path, torch, save_file, cles=("a", "b"), rang=2, entree=6, sortie=4):
    g = torch.Generator().manual_seed(1)
    t = {}
    if "a" in cles:
        t["model.layers.0.self_attn.q_proj.lora_a"] = torch.randn(entree, rang, generator=g) * 0.1
    if "b" in cles:
        t["model.layers.0.self_attn.q_proj.lora_b"] = torch.randn(rang, sortie, generator=g) * 0.1
    save_file(t, str(dossier / "adapters.safetensors"))
    (dossier / "adapter_config.json").write_text(json.dumps(
        {"fine_tune_type": "lora", "lora_parameters": {"rank": rang, "scale": 20.0, "dropout": 0.0}}))
    return t


class FusionTests(unittest.TestCase):
    def setUp(self):
        import torch
        from safetensors.torch import save_file
        self.torch, self.save_file = torch, save_file
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        racine = Path(self.tmp.name)
        self.base, self.adapt, self.sortie = racine / "base", racine / "adapt", racine / "sortie"
        self.base.mkdir()
        self.adapt.mkdir()
        self.q = ecrire_base(self.base, torch, save_file)

    def test_formule_identique_a_mlx_lm(self):
        torch = self.torch
        a, b = torch.randn(6, 2), torch.randn(2, 4)
        # mlx_lm/tuner/lora.py, fuse : (scale * lora_b.T) @ lora_a.T
        self.assertTrue(torch.allclose(fu.delta(a, b, 20.0), (20.0 * b.T) @ a.T, atol=1e-5))

    def test_fusion_valeurs_index_liens(self):
        from safetensors import safe_open
        torch = self.torch
        t = ecrire_adaptateur(self.adapt, torch, self.save_file)
        rapport = fu.fusionner(self.base, self.adapt, self.sortie)
        attendu = (self.q.float() + 20.0 * (t["model.layers.0.self_attn.q_proj.lora_a"]
                                           @ t["model.layers.0.self_attn.q_proj.lora_b"]).T).to(torch.float16)
        f = safe_open(str(self.sortie / "model-zz-lora-00.safetensors"), "pt")
        obtenu = f.get_tensor("model.layers.0.self_attn.q_proj.weight")
        self.assertEqual(obtenu.dtype, torch.float16)
        self.assertTrue(torch.equal(obtenu, attendu))
        carte = json.loads((self.sortie / "model.safetensors.index.json").read_text())["weight_map"]
        self.assertEqual(carte["model.layers.0.self_attn.q_proj.weight"], "model-zz-lora-00.safetensors")
        self.assertEqual(carte["model.layers.0.input_layernorm.weight"], "model-00002-of-00002.safetensors")
        for frag in ("model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors"):
            self.assertTrue((self.sortie / frag).is_symlink())
        # les fragments « zz » sont lus après ceux d'origine (ordre alphabétique de llama.cpp)
        self.assertGreater("model-zz-lora-00.safetensors", "model-00002-of-00002.safetensors")
        d = fu.delta(t["model.layers.0.self_attn.q_proj.lora_a"], t["model.layers.0.self_attn.q_proj.lora_b"], 20.0)
        rho = (d.double().norm() / self.q.float().double().norm()).item()
        self.assertAlmostEqual(rapport["matrices"]["model.layers.0.self_attn.q_proj.weight"]["rho"], rho, places=9)

    def test_refus(self):
        torch = self.torch
        ecrire_adaptateur(self.adapt, torch, self.save_file, cles=("a",))
        with self.assertRaises(fu.ErreurFusion):
            fu.fusionner(self.base, self.adapt, self.sortie)
        ecrire_adaptateur(self.adapt, torch, self.save_file, entree=5)
        with self.assertRaises(fu.ErreurFusion):
            fu.fusionner(self.base, self.adapt, Path(self.tmp.name) / "sortie2")

    def test_refus_si_base_pas_en_bf16(self):
        torch = self.torch
        self.save_file({"model.layers.0.self_attn.q_proj.weight": self.q.float()},
                       str(self.base / "model-00001-of-00002.safetensors"))
        ecrire_adaptateur(self.adapt, torch, self.save_file)
        with self.assertRaises(fu.ErreurFusion):
            fu.fusionner(self.base, self.adapt, self.sortie)

    def test_cles_inattendues(self):
        with self.assertRaises(fu.ErreurFusion):
            fu.modules_adaptes(["model.layers.0.self_attn.q_proj.lora_c"])


class NomsTests(unittest.TestCase):
    def test_correspondance(self):
        self.assertEqual(vg.nom_hf("blk.12.attn_q.weight"), "model.layers.12.self_attn.q_proj.weight")
        self.assertEqual(vg.nom_hf("blk.3.attn_k.bias"), "model.layers.3.self_attn.k_proj.bias")
        self.assertEqual(vg.nom_hf("blk.27.ffn_down.weight"), "model.layers.27.mlp.down_proj.weight")
        self.assertEqual(vg.nom_hf("output.weight"), "lm_head.weight")
        with self.assertRaises(vg.ErreurVerification):
            vg.nom_hf("blk.0.attn_qkv.weight")


class ControleTests(unittest.TestCase):
    def test_regle(self):
        self.assertEqual(cr.decider(10, 16, 9, 12)["verdict"], "effet_conserve")          # 3 >= 6 / 2
        self.assertEqual(cr.decider(10, 16, 9, 11)["verdict"], "effet_perdu_a_la_requantification")
        self.assertEqual(cr.decider(10, 10, 9, 15)["verdict"], "effet_non_observe_en_mlx")
        self.assertEqual(cr.decider(10, 9, 9, 15)["verdict"], "effet_non_observe_en_mlx")

    def test_sortie_llama(self):
        self.assertEqual(cr.lire_sortie_llama("Réponse [P1]. [end of text]\n"), {"texte": "Réponse [P1].", "arret": "stop"})
        self.assertEqual(cr.lire_sortie_llama("Réponse coupée")["arret"], "length")

    def test_conformite(self):
        textes = {"p1": "Le contrat est écrit et signé. Il précise la durée.", "p2": "Autre passage."}
        e = {"variante": "citee", "passages": ["p1", "p2"], "passage_cible": "p1"}
        self.assertEqual(cr.conforme(e, {"texte": "Le contrat est écrit et signé. [P1]", "arret": "stop"}, textes), (True, "ok"))
        self.assertFalse(cr.conforme(e, {"texte": "Le contrat est écrit. [P1]", "arret": "stop"}, textes)[0])   # fragment
        self.assertFalse(cr.conforme(e, {"texte": "Autre passage. [P2]", "arret": "stop"}, textes)[0])          # cible non citée
        self.assertFalse(cr.conforme(e, {"texte": "Le contrat est écrit et signé. [P1]", "arret": "length"}, textes)[0])
        h = {"variante": "hors_corpus", "passages": ["p1", "p2"], "passage_cible": None}
        self.assertTrue(cr.conforme(h, {"texte": cr.rag.ABSTENTION, "arret": "stop"}, textes)[0])
        self.assertFalse(cr.conforme(h, {"texte": "Le contrat est écrit et signé. [P1]", "arret": "stop"}, textes)[0])


if __name__ == "__main__":
    unittest.main()
