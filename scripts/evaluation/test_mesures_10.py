"""Tests des mesures du protocole 10 (#171) : pertinence des extraits courts et métriques des listes."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mesures_10 as m  # noqa: E402

LONG = ("Le salarié a droit à un congé de deux jours et demi ouvrables par mois de travail effectif chez le même "
        "employeur, dans la limite de trente jours ouvrables par an.")
TEXTES = [
    LONG,
    "Le congé parental a une durée initiale d'un an au maximum. Il peut être prolongé deux fois.",
    "Le congé parental est un droit. La durée initiale d'un an au maximum ne s'applique pas ici.",
    "Autre sujet sans rapport avec la question posée, sur la durée initiale de quelque chose.",
]


class TestPertinenceV2(unittest.TestCase):
    def setUp(self):
        self.p = m.PertinenceV2(TEXTES)

    def test_extrait_court_contenu_en_entier(self):
        extrait = "Le congé parental a une durée initiale d'un an au maximum."
        self.assertTrue(self.p.court(extrait))
        self.assertEqual(self.p.pertinents(extrait), {1})   # le passage 2 n'en contient qu'un fragment

    def test_extrait_long_delegue_a_d4(self):
        extrait = LONG[:120]
        self.assertFalse(self.p.court(extrait))
        self.assertIn(0, self.p.pertinents(extrait))


class TestEvaluer(unittest.TestCase):
    def test_rangs_succes_et_fiche(self):
        listes = [[5, 3, 9, 1, 2, 7, 8, 4, 6, 0, 11], [11, 10, 12, 13, 14, 15, 16, 17, 18, 19, 3]]
        pertinents = [{1}, {3}]
        url = [f"u{i // 2}" for i in range(20)]           # deux passages par fiche
        fiches = [{url[i] for i in p} for p in pertinents]
        s = m.evaluer(listes, pertinents, fiches, url)
        self.assertEqual(s["r1"], [False, False])
        self.assertEqual(s["r5"], [True, False])          # passage 1 au rang 4 ; passage 3 au rang 11, hors des 10
        self.assertEqual(s["r10"], [True, False])
        self.assertEqual(s["fiche10"], [True, False])     # fiche u1 (passages 2 et 3) absente des 10 premiers de la 2e liste
        self.assertAlmostEqual(s["mrr10"], (1 / 4 + 0) / 2)


if __name__ == "__main__":
    unittest.main()
