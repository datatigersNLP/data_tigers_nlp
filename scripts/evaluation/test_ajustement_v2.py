"""Tests de ajustement_v2.py (#167) : python scripts/evaluation/test_ajustement_v2.py

La règle de décision est testée sur des cas construits. Le calcul complet est rejoué en remplaçant la v2 par la v1
(puis par la base) : il ne lit le lot de test qu'avec la base et la v1, déjà mesurées et publiées le 15 novembre ;
il est sauté si data/ est absent.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import ajustement_05 as a05  # noqa: E402
import ajustement_v2 as a2  # noqa: E402


def jeu(ecart, borne=-0.1):
    return {"ecarts_recall5": {"v2 moins v1": {"ecart": ecart, "ic95_tango": [borne, 0.2]}}}


class Regle(unittest.TestCase):
    def test_servir_si_positif_ou_nul_partout_et_strict_quelque_part(self):
        self.assertEqual(a2.decision(jeu(0.0), jeu(0.01))["verdict"][:13], "servir la v2,")
        self.assertEqual(a2.decision(jeu(0.02), jeu(0.0))["verdict"][:13], "servir la v2,")
        self.assertEqual(a2.decision(jeu(0.0), jeu(0.0))["verdict"], "garder la v1")      # égalité : pas de changement
        self.assertEqual(a2.decision(jeu(-0.0137), jeu(0.05))["verdict"], "garder la v1")
        self.assertEqual(a2.decision(jeu(0.05), jeu(-0.002))["verdict"], "garder la v1")

    def test_conclusion_statistique_par_jeu(self):
        d = a2.decision(jeu(0.05, 0.01), jeu(0.03, -0.01))
        self.assertTrue(d["v2_meilleure_sur_le_lot_de_test"])
        self.assertFalse(d["v2_meilleure_sur_le_cdtn"])

    def test_mesure_refusee_avant_le_gel(self):
        if a2.SHA256_AMENDEMENT_A2 is None:
            with tempfile.TemporaryDirectory() as d:
                ancien = a2.GARDE_FOU
                a2.GARDE_FOU = Path(d) / "g.json"
                a2.GARDE_FOU.write_text(json.dumps({"passe": True, "regle": "r"}))
                try:
                    with self.assertRaises(a2.ErreurMesureA2):
                        a2.mesurer()
                finally:
                    a2.GARDE_FOU = ancien

    def test_garde_fou_non_passe_bloque_tout(self):
        with tempfile.TemporaryDirectory() as d:
            ancien = a2.GARDE_FOU
            a2.GARDE_FOU = Path(d) / "g.json"
            a2.GARDE_FOU.write_text(json.dumps({"passe": False, "regle": "r"}))
            try:
                with self.assertRaisesRegex(a2.ErreurMesureA2, "Garde-fou"):
                    a2.mesurer()
            finally:
                a2.GARDE_FOU = ancien


@unittest.skipUnless(a2.MESURE_A1.is_file() and a05.INDEX_AJUSTE.is_file(), "data/ absent")
class CalculComplet(unittest.TestCase):
    """La v2 remplacée par un système déjà mesuré : la mesure doit redonner le 15 novembre et décider sans erreur."""

    def test_controle_a1_detecte_un_ecart_infime(self):
        a1 = json.loads(a2.MESURE_A1.read_text(encoding="utf-8"))
        a1["cdtn"]["systemes"]["ajuste"]["mrr@10"] += 1e-9
        with tempfile.TemporaryDirectory() as d:
            faux = Path(d) / "a1.json"
            faux.write_text(json.dumps(a1))
            ancien = a2.MESURE_A1
            a2.MESURE_A1 = faux
            try:
                with self.assertRaisesRegex(a2.ErreurMesureA2, "ne redonnent pas"):
                    self.rejouer("ajuste")
            finally:
                a2.MESURE_A1 = ancien

    def rejouer(self, remplacant: str):
        vecteurs = {"ajuste": (a05.VECTEURS / "vecteurs_navigateur_ajuste.json", a05.VECTEURS / "vecteurs_cdtn_mesure_ajuste.json",
                               a05.EMPREINTES["q8_ajuste"][1], a05.charger_index_ajuste),
                    "base": (a05.VECTEURS_NB03, a05.VECTEURS / "vecteurs_cdtn_mesure_base.json",
                             a05.EMPREINTES["q8_base"][1], lambda: a05.table_et_index_site()[1].matrice)}[remplacant]
        anciens = (a2.SHA256_AMENDEMENT_A2, a2.verifier_empreintes_a2, a2.charger_index_v2, a2.charger_vecteurs,
                   a2.GARDE_FOU, a2.SORTIES, a2.AMENDEMENT_A2, a2.EMPREINTES_A2)
        vrai_charger = a2.charger_vecteurs

        def charger(chemin, modele_local, sha):
            if modele_local == "ajuste_v2":
                cdtn = "cdtn" in Path(chemin).name
                chemin2 = vecteurs[1] if cdtn else vecteurs[0]
                return vrai_charger(chemin2, None if remplacant == "base" and not cdtn else remplacant,
                                    None if remplacant == "base" and not cdtn else vecteurs[2])
            return vrai_charger(chemin, modele_local, sha)
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "g.json").write_text(json.dumps({"passe": True, "regle": "r"}))
            (d / "a2.md").write_text("figé")
            try:
                a2.GARDE_FOU, a2.SORTIES, a2.AMENDEMENT_A2 = d / "g.json", d / "sorties", d / "a2.md"
                a2.SHA256_AMENDEMENT_A2 = a05.sha256_fichier(d / "a2.md")
                a2.verifier_empreintes_a2 = lambda: {}
                a2.EMPREINTES_A2 = {**a2.EMPREINTES_A2, "q8_v2": (d / "a2.md", None)}
                a2.charger_index_v2 = vecteurs[3]
                a2.charger_vecteurs = charger
                a2.SORTIES.mkdir()
                c = a2.mesurer()
                c2 = a2.mesurer()                          # seconde exécution : contenu identique exigé
                self.assertEqual(c, c2)
                return c
            finally:
                (a2.SHA256_AMENDEMENT_A2, a2.verifier_empreintes_a2, a2.charger_index_v2, a2.charger_vecteurs,
                 a2.GARDE_FOU, a2.SORTIES, a2.AMENDEMENT_A2, a2.EMPREINTES_A2) = anciens

    def test_v2_egale_v1_redonne_le_15_novembre_et_garde_la_v1(self):
        c = self.rejouer("ajuste")
        self.assertTrue(c["controle_a1"]["conforme"])
        for jeu_ in ("lot_de_test", "cdtn"):
            e = c[jeu_]["ecarts_recall5"]["v2 moins v1"]
            self.assertEqual((e["ecart"], e["ajuste_seul"], e["base_seule"]), (0.0, 0, 0))
        self.assertEqual(c["decision"]["verdict"], "garder la v1")
        self.assertAlmostEqual(c["lot_de_test"]["systemes"]["v1"]["recall@5"], 46 / 73)

    def test_v2_egale_base_recule_et_garde_la_v1(self):
        c = self.rejouer("base")
        self.assertAlmostEqual(c["decision"]["ecart_lot_de_test"], -(46 - 32) / 73)
        self.assertLess(c["decision"]["ecart_cdtn"], 0)
        self.assertEqual(c["decision"]["verdict"], "garder la v1")


if __name__ == "__main__":
    unittest.main(verbosity=1)
