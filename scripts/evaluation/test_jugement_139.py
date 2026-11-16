"""Tests de jugement_139.py (#139, protocole 09) : python scripts/evaluation/test_jugement_139.py

Les règles sont testées sur des cas construits. Les tests sur données réelles (sautés si data/ est absent) tirent le
vivier dans un dossier temporaire et contrôlent les feuilles, les contrôles et la reproduction sous D4 ; ils ne
lisent aucun verdict et n'affichent aucune métrique nouvelle.
"""

import csv
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import jugement_139 as j  # noqa: E402


def cle_construite(n_pos=40, n_neg=40, n_viv=3):
    paires = [{"id": f"P{k}", "nature": "controle_positif", "question": "Q1", "passage": 100 + k} for k in range(n_pos)]
    paires += [{"id": f"N{k}", "nature": "controle_negatif", "question": "Q1", "passage": 200 + k} for k in range(n_neg)]
    paires += [{"id": f"V{k}", "nature": "vivier", "question": "Q1", "passage": k} for k in range(n_viv)]
    return {"paires": paires}


def verdicts_construits(cle, pos_ok, neg_ko, vivier):
    v = {}
    pos = [c for c in cle["paires"] if c["nature"] == "controle_positif"]
    neg = [c for c in cle["paires"] if c["nature"] == "controle_negatif"]
    for k, c in enumerate(pos):
        v[c["id"]] = "en_partie" if k < pos_ok else "ne_repond_pas"
    for k, c in enumerate(neg):
        v[c["id"]] = "repond" if k < neg_ko else "ne_repond_pas"
    for c, x in zip([c for c in cle["paires"] if c["nature"] == "vivier"], vivier):
        v[c["id"]] = x
    return v


class Outils(unittest.TestCase):
    def test_kappa(self):
        self.assertEqual(j.kappa([0, 1, 2, 2], [0, 1, 2, 2]), 1.0)
        self.assertAlmostEqual(j.kappa([1, 1, 0, 0], [1, 0, 0, 0], k=2), 0.5)
        # pondération linéaire, calcul à la main : poids 1, 0,5, 0 ; observé (1 + 0,5 + 1) / 3 ; marges (1, 1, 1) et
        # (1, 0, 2), donc attendu (1/3 + 1/2 + 2/3) / 3 = 0,5 ; kappa (0,8333 - 0,5) / 0,5 = 2/3
        a, b = [0, 1, 2], [0, 2, 2]
        po, pe = 2.5 / 3, 0.5
        self.assertAlmostEqual(j.kappa(a, b, ponderation="lineaire"), (po - pe) / (1 - pe))
        # exemple non symétrique, à la main : marges (2, 1, 2) et (2, 2, 1) ; observé 3,5 / 5 ; attendu 13,5 / 25
        self.assertAlmostEqual(j.kappa([0, 0, 1, 2, 2], [0, 1, 1, 2, 0], ponderation="lineaire"), (0.7 - 0.54) / 0.46)
        bas, haut = j.kappa_ic([0, 1, 2] * 30, [0, 1, 2] * 30, tirages=200)
        self.assertEqual((bas, haut), (1.0, 1.0))

    def test_ndcg(self):
        attendu = (1 / math.log2(3) + 1 / math.log2(4)) / (1 + 1 / math.log2(3))
        self.assertAlmostEqual(j.ndcg10([5, 1, 9], {1, 9}), attendu)
        self.assertAlmostEqual(j.ndcg10(list(range(10)), set(range(20))), 1.0)       # idéal borné à 10 pertinents
        self.assertEqual(j.ndcg10([1, 2], set()), 0.0)


class Regles(unittest.TestCase):
    def test_fiabilite_aux_bornes(self):
        cle = cle_construite()
        self.assertTrue(j.fiabilite(cle, {"J1": verdicts_construits(cle, 32, 2, [])})["J1"]["fiable"])
        self.assertFalse(j.fiabilite(cle, {"J1": verdicts_construits(cle, 31, 2, [])})["J1"]["fiable"])
        self.assertFalse(j.fiabilite(cle, {"J1": verdicts_construits(cle, 40, 3, [])})["J1"]["fiable"])

    def test_regle_principale_et_large(self):
        cle = cle_construite()
        v1 = verdicts_construits(cle, 40, 0, ["repond", "repond", "en_partie"])
        v2 = verdicts_construits(cle, 40, 0, ["repond", "en_partie", "ne_repond_pas"])
        verdicts = {"J1": v1, "J2": v2}
        r = j.pertinence_jugee(cle, verdicts, j.fiabilite(cle, verdicts))
        self.assertEqual(r["principale"], {("Q1", 0)})                           # les deux juges : repond
        self.assertEqual(r["large"], {("Q1", 0), ("Q1", 1), ("Q1", 2)})          # au moins un : repond ou en partie
        self.assertNotIn(("Q1", 100), r["large"])                                # les contrôles n'entrent pas

    def test_un_seul_juge_fiable(self):
        cle = cle_construite()
        v1 = verdicts_construits(cle, 40, 0, ["repond", "ne_repond_pas", "ne_repond_pas"])
        v2 = verdicts_construits(cle, 10, 0, ["ne_repond_pas", "repond", "repond"])      # J2 non fiable
        verdicts = {"J1": v1, "J2": v2}
        r = j.pertinence_jugee(cle, verdicts, j.fiabilite(cle, verdicts))
        self.assertEqual(r["juges_retenus"], ["J1"])
        self.assertEqual(r["principale"], {("Q1", 0)})

    def test_aucun_juge_fiable(self):
        cle = cle_construite()
        v = verdicts_construits(cle, 0, 0, ["repond"] * 3)
        r = j.pertinence_jugee(cle, {"J1": v, "J2": v}, j.fiabilite(cle, {"J1": v, "J2": v}))
        self.assertEqual((r["juges_retenus"], r["principale"]), ([], set()))


def donnees_construites():
    """Deux questions, six passages sur trois fiches ; Q1 : passage 0 pertinent selon D4 (fiche a)."""
    slug = ["a", "a", "b", "b", "c", "c"]
    qs = [{"id": "Q1", "fiche": "a"}, {"id": "Q2", "fiche": "b"}]
    d4 = {"Q1": {0}, "Q2": {2}}
    classements = {"base": {"Q1": [1, 4, 5, 3, 2, 0, 0, 0, 0, 0], "Q2": [2, 0, 1, 3, 4, 5, 0, 0, 0, 0]},
                   "ajuste": {"Q1": [4, 5, 2, 3, 1, 0, 0, 0, 0, 0], "Q2": [0, 1, 4, 5, 3, 2, 0, 0, 0, 0]}}
    etats = {"B2": {"Q1": {"classe": "reponse_citee", "appel_modele": True, "contexte": [1, 4], "cites": [4]},
                    "Q2": {"classe": "erreur_technique", "appel_modele": True, "contexte": [0, 1], "cites": []}},
             "V1": {"Q1": {"classe": "abstention", "appel_modele": True, "contexte": [0, 1], "cites": []},
                    "Q2": {"classe": "abstention", "appel_modele": False, "contexte": [3], "cites": []}},
             "V2": {"Q1": {"classe": "reponse_citee", "appel_modele": True, "contexte": [0, 5], "cites": [5]},
                    "Q2": {"classe": "reponse_citee", "appel_modele": True, "contexte": [2], "cites": [2]}}}
    return {"slug": slug, "questions": qs, "d4": d4, "classements": classements, "etats": etats}


class Vivier(unittest.TestCase):
    def test_vivier_construit(self):
        d = donnees_construites()
        v = j.construire_vivier(d)
        # base et ajusté : Q1 échoue à 5 et réussit à 10 ; Q2 : l'ajusté échoue à 5 seulement
        self.assertIn("A_base@5", v[("Q1", 1)])
        self.assertNotIn(("Q1", 0), v)                                   # pertinent selon D4 : jamais dans le vivier
        self.assertIn("A_ajuste@5", v[("Q2", 4)])
        self.assertIn("B_B2_contexte", v[("Q1", 4)])
        self.assertIn("B_B2_cite", v[("Q1", 4)])
        self.assertNotIn(("Q2", 1), {k for k, s in v.items() if any("B_B2" in x for x in s)})   # erreur technique exclue
        self.assertIn("B_V1_contexte", v[("Q2", 3)])
        self.assertIn("B_V2_cite", v[("Q1", 5)])

    def test_taxonomies(self):
        d = donnees_construites()
        defs = {"minorant_d4": d["d4"], "majorant_principal": {"Q1": {0, 4}, "Q2": {2}},
                "majorant_large": {"Q1": {0, 4, 5}, "Q2": {2}}}
        ta = j.taxonomie_a(d, defs)
        self.assertEqual(ta["base"]["par_question"], {"Q1": "autre passage valable"})
        self.assertEqual(ta["ajuste"]["par_question"], {"Q1": "autre passage valable", "Q2": "bonne fiche, passage insuffisant"})
        tb = j.taxonomie_b(d, defs)
        self.assertEqual(tb["B2"]["echecs"], 0)                          # cite 4, jugé pertinent ; Q2 en erreur
        self.assertEqual(tb["V1"]["categories"]["abstention du modèle"], 1)
        self.assertEqual(tb["V1"]["categories"]["récupération"], 1)     # Q2 : contexte [3] sans passage pertinent
        self.assertEqual(tb["V2"]["categories"]["citation non pertinente"], 1)


class Controles(unittest.TestCase):
    def test_negatifs_hors_fiche_et_hors_vivier(self):
        """40 questions sur la fiche a ; le passage 1 (fiche b) est dans le vivier de chacune : seul le 2 est permis."""
        qs = [{"id": f"Q{k}", "fiche": "a"} for k in range(40)]
        d = {"questions": qs, "slug": ["a", "b", "c"], "d4": {q["id"]: {0} for q in qs}}
        vivier = {(q["id"], 1): {"A_base@5"} for q in qs}
        pos, neg = j.tirer_controles(d, vivier, j.np.random.default_rng(1))
        self.assertEqual({i for _, i in pos}, {0})
        self.assertEqual({i for _, i in neg}, {2})


class Gel(unittest.TestCase):
    def test_refus_avant_le_gel(self):
        ancien = j.SHA256_PROTOCOLE_09
        j.SHA256_PROTOCOLE_09 = None
        try:
            with self.assertRaisesRegex(j.ErreurJugement, "non figé"):
                j.verifier_gel()
            with self.assertRaises(j.ErreurJugement):
                j.mesurer()
        finally:
            j.SHA256_PROTOCOLE_09 = ancien

    def test_protocole_modifie_refuse(self):
        ancien = j.SHA256_PROTOCOLE_09
        j.SHA256_PROTOCOLE_09 = "0" * 64
        try:
            with self.assertRaisesRegex(j.ErreurJugement, "modifié"):
                j.verifier_gel()
        finally:
            j.SHA256_PROTOCOLE_09 = ancien


@unittest.skipUnless(j.MESURE_A1.is_file() and j.ETATS_B["V2"].is_file(), "data/ absent")
class DonneesReelles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = j.donnees_test()
        cls.vivier = j.construire_vivier(cls.d)
        cls.tmp = tempfile.TemporaryDirectory()
        t = Path(cls.tmp.name)
        cls.anciens = (j.SORTIES, j.CLE, j.FEUILLES, j.VERDICTS, j.ETALONNAGE, j.SHA256_PROTOCOLE_09)
        j.SORTIES, j.CLE, j.FEUILLES, j.VERDICTS, j.ETALONNAGE = t, t / "vivier.json", t / "feuilles", t / "verdicts", t / "etalonnage"
        j.SHA256_PROTOCOLE_09 = j.sha256_fichier(j.PROTOCOLE_09)
        cls.cle = j.vivier_et_feuilles()

    @classmethod
    def tearDownClass(cls):
        j.SORTIES, j.CLE, j.FEUILLES, j.VERDICTS, j.ETALONNAGE, j.SHA256_PROTOCOLE_09 = cls.anciens
        cls.tmp.cleanup()

    def test_effectifs(self):
        e = self.cle["effectifs"]
        self.assertEqual((e["vivier"], e["questions_du_vivier"], e["paires"]), (617, 53, 697))
        self.assertEqual(len(self.cle["feuilles"]), 7)

    def test_controles(self):
        d = self.d
        pos = [c for c in self.cle["paires"] if c["nature"] == "controle_positif"]
        neg = [c for c in self.cle["paires"] if c["nature"] == "controle_negatif"]
        self.assertEqual((len(pos), len(neg)), (40, 40))
        self.assertTrue(all(c["passage"] in d["d4"][c["question"]] for c in pos))
        fiche_q = {q["id"]: q["fiche"] for q in d["questions"]}
        for c in neg:
            self.assertNotEqual(d["slug"][c["passage"]], fiche_q[c["question"]])
            self.assertNotIn(d["slug"][c["passage"]], {d["slug"][i] for i in d["d4"][c["question"]]})
            self.assertNotIn((c["question"], c["passage"]), self.vivier)
        self.assertEqual(len({(c["question"], c["passage"]) for c in self.cle["paires"]}), 697)

    def test_feuilles_a_l_aveugle(self):
        ids = []
        for f in sorted(j.FEUILLES.glob("lot_*.json")):
            feuille = json.loads(f.read_text(encoding="utf-8"))
            self.assertEqual(feuille["consigne"], j.CONSIGNE)
            self.assertLessEqual(len(feuille["paires"]), 100)
            for p in feuille["paires"]:
                self.assertEqual(set(p), {"id", "question", "passage"})
                self.assertNotIn("travail-emploi.gouv.fr", p["passage"])
                self.assertNotIn("m2-article", p["passage"])
                ids.append(p["id"])
        self.assertEqual(ids, [f"J{n:04d}" for n in range(1, 698)])
        texte = "".join(f.read_text(encoding="utf-8") for f in j.FEUILLES.glob("lot_*.json"))
        for mot in ("controle_", "vivier", "A_base", "A_ajuste", "B_B2", "B_V1", "B_V2", "passage_id"):
            self.assertNotIn(mot, texte)

    def test_etalonnage(self):
        with open(j.ETALONNAGE / "feuille_etalonnage.csv", encoding="utf-8", newline="") as f:
            lignes = list(csv.DictReader(f))
        self.assertEqual([x["id"] for x in lignes], [f"H{n:03d}" for n in range(1, 101)])
        nature = {c["id"]: c["nature"] for c in self.cle["paires"]}
        compte = {}
        for h in self.cle["etalonnage"]:
            compte[nature[h["paire"]]] = compte.get(nature[h["paire"]], 0) + 1
        self.assertEqual(compte, {"vivier": 80, "controle_positif": 10, "controle_negatif": 10})

    def test_reproduction_sous_d4(self):
        defs = {"minorant_d4": self.d["d4"], "majorant_principal": self.d["d4"], "majorant_large": self.d["d4"]}
        ra, _ = j.mesures_a(self.d, defs)
        rb = j.mesures_b(self.d, defs)
        self.assertEqual(j.controle_reproduction(self.d, ra, rb), {"conforme": True, "ecarts": []})

    def test_importer(self):
        lot = [c["id"] for c in self.cle["paires"] if c["lot"] == "07"]
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "v.json"
            f.write_text(json.dumps({"verdicts": [{"id": i, "verdict": "repond", "motif": "m"} for i in lot[:-1]]}))
            with self.assertRaisesRegex(j.ErreurJugement, "exactement"):
                j.importer("J1", "07", f)
            f.write_text(json.dumps({"verdicts": [{"id": i, "verdict": "oui", "motif": "m"} for i in lot]}))
            with self.assertRaisesRegex(j.ErreurJugement, "inconnu"):
                j.importer("J1", "07", f)
            f.write_text(json.dumps({"verdicts": [{"id": i, "verdict": "repond", "motif": " "} for i in lot]}))
            with self.assertRaisesRegex(j.ErreurJugement, "motif"):
                j.importer("J1", "07", f)
            f.write_text(json.dumps({"verdicts": [{"id": i, "verdict": "repond", "motif": "m"} for i in reversed(lot)]}))
            j.importer("J1", "07", f)
            with self.assertRaises(FileExistsError):
                j.importer("J1", "07", f)


if __name__ == "__main__":
    unittest.main(verbosity=1)
