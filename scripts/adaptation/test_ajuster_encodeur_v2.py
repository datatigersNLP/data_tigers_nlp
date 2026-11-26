"""Tests de 10_ajuster_encodeur_v2.py et 11_exporter_v2.py (#167), sans entraîner ni exporter :
python scripts/adaptation/test_ajuster_encodeur_v2.py (environnement de l'entraînement, onnx et onnxruntime compris)
"""

import importlib.util
import re
import sys
import unittest
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent


def charger(nom, fichier):
    spec = importlib.util.spec_from_file_location(nom, ICI / fichier)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nom] = m
    spec.loader.exec_module(m)
    return m


aj = charger("ajuster_v2", "10_ajuster_encodeur_v2.py")
SOURCE_04 = (ICI / "04_ajuster_encodeur.py").read_text(encoding="utf-8")
SOURCE_06 = (ICI / "06_exporter_onnx.py").read_text(encoding="utf-8")


class Recette(unittest.TestCase):
    def test_recette_identique_a_celle_de_la_49(self):
        valeurs = {"epochs": "num_train_epochs", "batch_size": "per_device_train_batch_size",
                   "learning_rate": "learning_rate"}
        for nom_04, cle in valeurs.items():
            m = re.search(rf"^\s*{nom_04} = ([0-9.e-]+)\s*$", SOURCE_04, re.M)
            self.assertEqual(float(m.group(1)), aj.RECETTE[cle], nom_04)
        for cle in ("warmup_ratio", "weight_decay", "seed"):
            m = re.search(rf"{cle}=([0-9.]+),", SOURCE_04)
            self.assertEqual(float(m.group(1)), aj.RECETTE[cle], cle)
        self.assertIn("MultipleNegativesRankingLoss(model)", SOURCE_04)
        self.assertIn(f'REVISION_BASE = "{aj.REVISION_BASE}"', SOURCE_04)
        self.assertIn(f'model_id = "{aj.MODELE_BASE}"', SOURCE_04)


class Metriques(unittest.TestCase):
    def test_rangs_et_niveau_fiche(self):
        ordres = np.array([[3, 1, 2, 0, 4, 5, 6, 7, 8, 9],      # cible 1 au rang 2
                           [0, 2, 3, 4, 5, 6, 7, 8, 9, 10],     # cible 1 absente, même fiche au rang 1
                           [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],      # cible 0 au rang 10
                           [5, 6, 7, 8, 1, 0, 2, 3, 4, 9]])     # cible 1 au rang 5 exactement
        fiche_de = ["a", "b", "b", "c", "c", "c", "d", "d", "d", "e", "e"]
        m = aj.metriques(ordres, [1, 1, 0, 1], fiche_de, ["b", "b", "a", "b"])
        self.assertEqual(m["recall@1"], 0)
        self.assertAlmostEqual(m["recall@5"], 2 / 4)
        self.assertAlmostEqual(m["recall@10"], 3 / 4)
        self.assertAlmostEqual(m["mrr@10"], (1 / 2 + 1 / 10 + 1 / 5) / 4)
        self.assertAlmostEqual(m["recall@5_fiche"], 3 / 4)
        self.assertEqual(m["succes@5"], [True, False, False, True])

    def test_lots_d_une_meme_fiche(self):
        self.assertEqual(aj.lots_meme_fiche([f"f{i}" for i in range(64)], 16, tirages=50), 0.0)
        self.assertEqual(aj.lots_meme_fiche(["f"] * 64, 16, tirages=50), 1.0)
        p = aj.lots_meme_fiche([f"f{i // 2}" for i in range(400)], 16, tirages=4000)
        # 200 fiches de 2 passages, lots de 16 tirés sans remise : P(aucune paire) = prod_{j=1}^{15} (400 - 2j) / (400 - j)
        exact = 1 - np.prod([(400 - 2 * j) / (400 - j) for j in range(1, 16)])
        self.assertAlmostEqual(p, exact, delta=0.03)


class Export(unittest.TestCase):
    def test_reglages_identiques_a_06(self):
        ex = charger("exporter_v2", "11_exporter_v2.py")
        for t in ex.ENTREES_EXEMPLE + ex.TEXTES_CONTROLE:
            self.assertIn(t, SOURCE_06)
        for motif in ("opset_version=14", "do_constant_folding=True", "dynamo=False", "weight_type=QuantType.QInt8",
                      "per_channel=True", "reduce_range=True", 'extra_options={"ActivationSymmetric": True}'):
            self.assertIn(motif, SOURCE_06)
            self.assertIn(motif, (ICI / "11_exporter_v2.py").read_text(encoding="utf-8"))
        self.assertEqual(ex.LIVRES_V1["onnx/model_quantized.onnx"][:8], "934a202b")


if __name__ == "__main__":
    unittest.main(verbosity=1)
