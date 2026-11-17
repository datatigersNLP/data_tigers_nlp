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


class TestHolm(unittest.TestCase):
    def test_valeurs_connues(self):
        h = m.holm({"a": 0.01, "b": 0.04, "c": 0.03})
        self.assertAlmostEqual(h["a"], 0.03)
        self.assertAlmostEqual(h["c"], 0.06)
        self.assertAlmostEqual(h["b"], 0.06)       # monotonie : jamais sous la valeur ajustée précédente

    def test_plafond(self):
        self.assertEqual(m.holm({"a": 0.6, "b": 0.7})["a"], 1.0)


class TestScoresReclasseur(unittest.TestCase):
    def test_un_passage_note_ne_l_est_jamais_deux_fois(self):
        import tempfile
        appels = []

        class Faux:
            def scores(self, question, textes):
                appels.append(list(textes))
                return [float(len(t)) for t in textes]

        with tempfile.TemporaryDirectory() as d:
            rs = m.ScoresReclasseur(["a", "bb", "ccc"], Path(d) / "cache.json")
            rs.modele = Faux()
            self.assertEqual(rs.noter("q", [2, 0, 2]), {2: 3.0, 0: 1.0})
            rs.noter("q", [0, 1])
            self.assertEqual(appels, [["ccc", "a"], ["bb"]])
            rs.ecrire()
            relu = m.ScoresReclasseur(["a", "bb", "ccc"], Path(d) / "cache.json")
            self.assertEqual(relu.cache, {"q": {2: 3.0, 0: 1.0, 1: 2.0}})


class TestGardeM1(unittest.TestCase):
    @staticmethod
    def lignes(classes):
        return [{"id": f"H{i}", "type": "hors_corpus", "classe": c} for i, c in enumerate(classes)] + \
               [{"id": "C0", "type": "dans_corpus", "classe": "reponse_citee"}]

    def test_baisse_d_une_question_toleree_pas_deux(self):
        b = self.lignes(["abstention", "abstention", "abstention", "reponse_citee"])
        g = m.garde_m1(self.lignes(["abstention", "abstention", "reponse_citee", "reponse_citee"]), b)
        self.assertEqual((g["baisse"], g["respectee"]), (1, True))
        g = m.garde_m1(self.lignes(["abstention", "reponse_citee", "reponse_citee", "reponse_citee"]), b)
        self.assertEqual((g["baisse"], g["respectee"]), (2, False))

    def test_erreur_technique_exclue_des_deux_cotes(self):
        a = self.lignes(["erreur_technique", "abstention"])
        b = self.lignes(["abstention", "abstention"])
        g = m.garde_m1(a, b)
        self.assertEqual((g["effectif_commun"], g["abstentions_a"], g["abstentions_b"]), (1, 1, 1))

    def test_questions_differentes_refusees(self):
        with self.assertRaises(m.ErreurMesure10):
            m.garde_m1(self.lignes(["abstention"]), self.lignes(["abstention", "abstention"]))


if __name__ == "__main__":
    unittest.main()
