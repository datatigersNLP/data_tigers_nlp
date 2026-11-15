"""Tests des mesures descriptives du site (#164), sur données synthétiques, sans modèle ni question d'évaluation.

Lancement, depuis la racine du dépôt : python scripts/evaluation/test_mesures_site_164.py
"""

from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mesures_site_164 as m  # noqa: E402


class TestFiches(unittest.TestCase):
    def test_fiches_dans_l_ordre_du_meilleur_passage(self):
        url = ["a", "b", "a", "c", "b"]
        self.assertEqual(m.fiches_affichees([0, 1, 2, 3, 4], url), ["a", "b", "c"])
        self.assertEqual(m.fiches_affichees([3, 2, 0], url), ["c", "a"])
        self.assertEqual(m.fiches_affichees([], url), [])


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        # 6 passages unitaires, 3 fiches : a (0, 1), b (2, 3), c (4, 5)
        self.matrice = np.eye(6, dtype=np.float32)
        self.url = ["a", "a", "b", "b", "c", "c"]
        # question 0 : passages 1 > 4 > 0 > reste ; question 1 : passages 5 > 3 > reste
        self.vecteurs = np.array([[0.4, 0.7, 0, 0, 0.5, 0], [0, 0, 0, 0.5, 0, 0.8]], dtype=np.float32)
        self.pertinents = [{0}, {2}]
        self.fiches = [{"a"}, {"b"}]

    def test_classement_stable(self):
        self.assertEqual(m.classements(self.vecteurs, self.matrice, 3), [[1, 4, 0], [5, 3, 0]])
        # 40 passages, un sur sept à 0,5 et les autres à 0 : à score égal, l'ordre de l'index, comme le site ; le tri
        # par défaut de numpy, non stable au-delà de 16 éléments, donnerait 0, 14, 28, 7…
        scores = np.zeros(40, dtype=np.float32)
        scores[::7] = 0.5
        self.assertEqual(m.classements(scores[None, :], np.eye(40, dtype=np.float32), 8)[0], [0, 7, 14, 21, 28, 35, 1, 2])

    def test_rappels_et_fiches_affichees(self):
        c2 = m.configuration(self.vecteurs, self.matrice, 2, self.pertinents, self.fiches, self.url, None)
        # k = 2 : question 0 voit les passages 1 et 4 (fiches a, c) ; question 1 les passages 5 et 3 (fiches c, b)
        self.assertEqual(c2["_passage"], [False, False])
        self.assertEqual(c2["_fiche"], [True, True])
        self.assertEqual(c2["fiches_affichees"], {"moyenne": 2.0, "mediane": 2.0, "min": 2, "max": 2})
        c3 = m.configuration(self.vecteurs, self.matrice, 3, self.pertinents, self.fiches, self.url, None)
        # k = 3 : le passage 0 entre pour la question 0 ; à score nul, la question 1 reçoit le passage 0, pas le 2
        self.assertEqual(c3["_passage"], [True, False])
        self.assertEqual(c3["rappel_passage"]["succes"], 1)
        self.assertEqual(c3["fiches_affichees"]["max"], 3)

    def test_proportion_wilson(self):
        p = m.proportion([True, True, True, False, False, False], None)
        self.assertEqual((p["succes"], p["n"]), (3, 6))
        self.assertAlmostEqual(p["ic95"][0], 0.1876, places=4)    # Wilson(3, 6), calculé à la main
        self.assertAlmostEqual(p["ic95"][1], 0.8124, places=4)
        # une fiche par question : l'intervalle corrigé de l'effet de plan est le Wilson classique
        q = m.proportion([True, True, True, False, False, False], ["f1", "f2", "f3", "f4", "f5", "f6"])
        self.assertAlmostEqual(q["ic95"][0], p["ic95"][0], places=12)


if __name__ == "__main__":
    unittest.main()
