"""Tests de la mesure de l'encodeur ajusté (#164), sur données synthétiques, sans modèle ni question d'évaluation.

Lancement, depuis la racine du dépôt : python scripts/evaluation/test_ajustement_05.py
"""

import json
from pathlib import Path
import sys
import tempfile
import unittest
import unittest.mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ajustement_05 as a  # noqa: E402


class TestRangs(unittest.TestCase):
    def setUp(self):
        # 4 passages unitaires ; la question 0 est la plus proche du passage 2, puis du passage 0
        self.matrice = np.eye(4, dtype=np.float32)
        self.vecteurs = np.array([[0.6, 0.0, 0.8, 0.0], [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)

    def test_rangs_et_succes(self):
        rangs = a.rangs_pertinents(self.vecteurs, self.matrice, [{0}, {1}], profondeur=3)
        self.assertEqual(rangs[0], [2])
        self.assertEqual(rangs[1], [3])           # passage 3 premier, puis ex aequo à 0 dans l'ordre de l'index : 0, 1, 2
        self.assertEqual(a.succes_a(rangs, 1), [False, False])
        self.assertEqual(a.succes_a(rangs, 2), [True, False])
        self.assertAlmostEqual(a.mrr10(rangs), (1 / 2 + 1 / 3) / 2)

    def test_tri_stable_des_ex_aequo(self):
        rangs = a.rangs_pertinents(np.array([[0.5, 0.5, 0.5, 0.5]], dtype=np.float32), self.matrice, [{3}], profondeur=4)
        self.assertEqual(rangs, [[4]])


class TestStatistiques(unittest.TestCase):
    def test_auc(self):
        self.assertEqual(a.auc([0.9, 0.8], [0.1, 0.2]), 1.0)
        self.assertEqual(a.auc([0.1], [0.9]), 0.0)
        self.assertEqual(a.auc([0.5], [0.5]), 0.5)
        self.assertAlmostEqual(a.auc([0.9, 0.3], [0.5, 0.1]), 0.75)

    def test_ecart_signe_et_comptes(self):
        sa = [True] * 6 + [False] * 4
        sb = [True] * 4 + [False] * 6
        e = a.ecart(sa, sb, groupes=list(range(10)))
        self.assertAlmostEqual(e["ecart"], 0.2)
        self.assertEqual((e["ajuste_seul"], e["base_seule"]), (2, 0))
        self.assertLess(e["ic95_tango"][0], e["ecart"])

    def test_regle_de_decision(self):
        def jeu(d, bas):
            return {"ecart_recall5": {"ecart": d, "ic95_tango": [bas, 0.5]}}
        self.assertTrue(a.decision(jeu(0.0, -0.1), jeu(0.0, -0.1))["verdict"].startswith("servir"))
        self.assertTrue(a.decision(jeu(0.05, -0.1), jeu(-0.01, -0.1))["verdict"].startswith("garder"))
        self.assertTrue(a.decision(jeu(-0.01, -0.1), jeu(0.2, 0.1))["verdict"].startswith("garder"))
        self.assertTrue(a.decision(jeu(0.1, 0.01), jeu(0.1, 0.0))["ajuste_declare_meilleur"])
        self.assertFalse(a.decision(jeu(0.1, -0.01), jeu(0.1, 0.0))["ajuste_declare_meilleur"])


class TestEntrees(unittest.TestCase):
    def test_vecteurs_refuses_si_modele_inattendu(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "v.json"
            f.write_text(json.dumps({"transformers_js": "4.3.0", "dtype": "q8", "identifiants": ["Q1"],
                                     "vecteurs": [[1.0] + [0.0] * 383], "modele_local": "base",
                                     "sha256_q8": a.EMPREINTES["q8_base"][1]}), encoding="utf-8")
            self.assertEqual(list(a.charger_vecteurs(f, "base")), ["Q1"])
            with self.assertRaises(a.ErreurMesure05):
                a.charger_vecteurs(f, "ajuste")

    def test_vecteurs_refuses_si_erreur_ou_non_normes(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "v.json"
            f.write_text(json.dumps({"erreur": "panne"}), encoding="utf-8")
            with self.assertRaises(a.ErreurMesure05):
                a.charger_vecteurs(f, None)
            f.write_text(json.dumps({"transformers_js": "4.3.0", "dtype": "q8", "identifiants": ["Q1"],
                                     "vecteurs": [[2.0] + [0.0] * 383]}), encoding="utf-8")
            with self.assertRaises(a.ErreurMesure05):
                a.charger_vecteurs(f, None)

    def test_mesure_refusee_sans_amendement_fige(self):
        with unittest.mock.patch.object(a, "SHA256_AMENDEMENT", None), \
                unittest.mock.patch.object(a, "verifier_empreintes", return_value={}):
            with self.assertRaises(a.ErreurMesure05):
                a.mesurer("mesure")

    def test_empreinte_refusee_si_fichier_modifie(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "x"
            f.write_bytes(b"contenu")
            with unittest.mock.patch.dict(a.EMPREINTES, {"essai": (f, "0" * 64)}, clear=True):
                with self.assertRaises(a.ErreurMesure05):
                    a.verifier_empreintes()


if __name__ == "__main__":
    unittest.main()
