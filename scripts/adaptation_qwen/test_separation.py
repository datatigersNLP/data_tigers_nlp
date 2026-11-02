"""Tests de la séparation des données d'adaptation (#107), sans modèle ni donnée d'entraînement."""

import json
import tempfile
import unittest
from contextlib import redirect_stdout
import io
from pathlib import Path

from separation import (ErreurSeparation, FICHES_TEST_ATTENDUES, empreinte_fiches, fiche, fiche_par_passage,
                        fiches_exclues, lire_jeu, main, normaliser, verifier)

FICHES = {"p-a1": "a", "p-a2": "a", "p-b1": "b", "p-c1": "c"}


class RegleTests(unittest.TestCase):
    def test_identifiant_de_fiche(self):
        self.assertEqual(fiche("https://travail-emploi.gouv.fr/la-demission"), "la-demission")
        self.assertEqual(fiche("https://travail-emploi.gouv.fr/la-demission/#preavis"), "la-demission")
        with self.assertRaises(ErreurSeparation):
            fiche("https://code.travail.gouv.fr/fiche-ministere-travail/la-demission")

    def test_normalisation(self):
        self.assertEqual(normaliser("  Puis-je  DÉMISSIONNER ?"), normaliser("puis-je démissionner ?"))
        self.assertNotEqual(normaliser("Puis-je démissionner ?"), normaliser("Puis-je démissionner"))

    def test_exemple_conforme(self):
        ex = [{"id": "e1", "question": "Quel préavis ?", "passages": ["p-a1", "p-c1"]}]
        self.assertEqual(verifier(ex, {"b"}, ["Autre question ?"], FICHES), [])

    def test_passage_de_contexte_dune_fiche_de_test(self):
        ex = [{"id": "e1", "question": "Quel préavis ?", "passages": ["p-a1", "p-b1"]}]
        self.assertEqual(verifier(ex, {"b"}, [], FICHES), [("e1", "passages de fiches du lot de test : ['b']")])

    def test_question_humaine_reprise(self):
        ex = [{"id": "e1", "question": "Puis-je  démissionner ?", "passages": ["p-a1"]}]
        self.assertEqual(verifier(ex, set(), ["puis-je démissionner ?"], FICHES),
                         [("e1", "question identique à une question du jeu humain")])

    def test_passage_inconnu_et_exemple_incomplet(self):
        ex = [{"id": "e1", "question": "Q ?", "passages": ["p-zz"]}, {"id": "e2", "question": "Q ?", "passages": []}]
        motifs = [m for _, m in verifier(ex, set(), [], FICHES)]
        self.assertEqual(motifs, ["passages absents de l'index : ['p-zz']", "exemple sans question ou sans passages"])

    def test_empreinte_independante_de_lordre(self):
        self.assertEqual(empreinte_fiches({"b", "a"}), empreinte_fiches({"a", "b"}))


class DepotTests(unittest.TestCase):
    """Sur le jeu figé et l'index du site, présents dans le dépôt."""

    @classmethod
    def setUpClass(cls):
        cls.lignes = lire_jeu()
        cls.exclues = fiches_exclues(cls.lignes)
        cls.fiches = fiche_par_passage()

    def test_soixante_et_une_fiches_toutes_dans_lindex(self):
        self.assertEqual(len(self.exclues), FICHES_TEST_ATTENDUES)
        self.assertLessEqual(self.exclues, set(self.fiches.values()))

    def test_les_fiches_de_calibration_restent_autorisees(self):
        calibration = {fiche(x["url"]) for x in self.lignes if x["lot"] == "calibration" and x["url"]}
        self.assertTrue(calibration)
        self.assertTrue(calibration - self.exclues)

    def test_cli_rejette_un_fichier_qui_touche_le_lot_de_test(self):
        passage_test = next(p for p, f in self.fiches.items() if f in self.exclues)
        passage_libre = next(p for p, f in self.fiches.items() if f not in self.exclues)
        with tempfile.TemporaryDirectory() as d:
            chemin = Path(d) / "ex.jsonl"
            lignes = [{"id": "ok", "question": "Q1 ?", "passages": [passage_libre]},
                      {"id": "ko", "question": "Q2 ?", "passages": [passage_libre, passage_test]}]
            chemin.write_text("".join(json.dumps(x) + "\n" for x in lignes), encoding="utf-8")
            with redirect_stdout(io.StringIO()) as sortie:
                code = main(["verifier", str(chemin)])
        self.assertEqual(code, 1)
        self.assertIn("ko : passages de fiches du lot de test", sortie.getvalue())
        self.assertIn("2 exemples, 1 violation(s)", sortie.getvalue())


if __name__ == "__main__":
    unittest.main()
