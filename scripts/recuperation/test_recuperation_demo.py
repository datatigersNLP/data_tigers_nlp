"""Tests de la récupération de la démonstration v2 (#172).

Lancement, depuis la racine du dépôt : python scripts/recuperation/test_recuperation_demo.py
Les tests sur les fichiers versionnés (index ajusté, q8 servi) tournent partout ; celui de l'en-tête contre le parquet M2
et ceux qui construisent BM25 V3 sont sautés si data/ ne contient pas ces fichiers. Aucun accès réseau.
"""

import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recuperation_demo as rd  # noqa: E402
import recuperation as rc  # noqa: E402
import rag  # noqa: E402

PASSAGES_VERSIONNES = rag.DOSSIER_INDEX / "passages_m2.json"


def passage(i, titre="Fiche", section="Section", chemin=(), texte=None):
    return {"passage_id": f"p{i}", "titre_fiche": titre, "section_titre": section, "chemin": list(chemin),
            "url": f"https://exemple.test/{i}", "url_citation": f"https://exemple.test/{i}#s",
            "date_maj": "2026-01-01", "texte": texte or f"Texte du passage {i} sur le congé numéro {i}.",
            "articles": []}


def mots_vides_disponibles() -> bool:
    import lexical_baselines
    return lexical_baselines.MOTS_VIDES_CACHE.exists()


class TestEntete(unittest.TestCase):
    def test_regle_du_notebook_01(self):
        self.assertEqual(rd.entete(passage(0, "Le congé", "Chapô")), "Le congé")
        self.assertEqual(rd.entete(passage(0, "Le congé", "Le congé", ["Durée"])), "Le congé > Durée")
        self.assertEqual(rd.entete(passage(0, "Le congé", "Durée", ["A", "B"])), "Le congé > Durée > A > B")
        self.assertEqual(rd.textes_lexicaux([passage(0, "T", "S", texte="x")]), ["T > S\nx"])

    def test_identique_au_parquet_m2(self):
        manifeste = rc.MANIFESTE_M2
        if not manifeste.exists():
            self.skipTest("parquet M2 absent de data/")
        index = rag.charger_index()
        table = rc.charger_passages_m2(index)
        self.assertEqual(rd.textes_lexicaux(index.passages), rc.textes_lexicaux(table))
        self.assertEqual(len(index.passages), 4240)


class TestIndexAjuste(unittest.TestCase):
    def test_index_servi(self):
        index = rag.charger_index()
        aj = rd.IndexAjuste(index)
        self.assertEqual(aj.matrice.shape, index.matrice.shape)
        self.assertEqual(aj.sha256, "dc8daa7243bec30c28ea4830daeb10970bcd3de8d819f71a602b5d0b306ea8f1")
        self.assertFalse(np.array_equal(aj.matrice, index.matrice))

    def faux(self, d: Path, matrice: np.ndarray, passages: list, base_passages: list | None = None):
        (d / "aj").mkdir()
        (d / "base").mkdir()
        octets = matrice.astype("<f4").tobytes()
        (d / "aj" / "index_m2.f32").write_bytes(octets)
        (d / "aj" / "index_m2.json").write_text(json.dumps({"index": {
            "fichier": "index_m2.f32", "sha256": hashlib.sha256(octets).hexdigest(),
            "nb_vecteurs": matrice.shape[0], "dimension": matrice.shape[1]}}), encoding="utf-8")
        (d / "aj" / "passages_m2.json").write_text(json.dumps(passages), encoding="utf-8")
        (d / "base" / "passages_m2.json").write_text(json.dumps(base_passages or passages), encoding="utf-8")
        return rag.IndexCommun({}, np.eye(3, 384, dtype="<f4"), passages)

    def test_refus(self):
        m = np.eye(3, 384, dtype="<f4")
        ps = [passage(i) for i in range(3)]
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            base = self.faux(d, m, ps)
            self.assertEqual(rd.IndexAjuste(base, d / "aj", d / "base").matrice.shape, (3, 384))
            octets = bytearray((d / "aj" / "index_m2.f32").read_bytes())
            octets[0] ^= 1
            (d / "aj" / "index_m2.f32").write_bytes(bytes(octets))
            with self.assertRaisesRegex(rc.ErreurRecuperationV2, "empreinte"):
                rd.IndexAjuste(base, d / "aj", d / "base")
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            base = self.faux(d, m, ps, [passage(i) for i in (0, 2, 1)])
            with self.assertRaisesRegex(rc.ErreurRecuperationV2, "passages"):
                rd.IndexAjuste(base, d / "aj", d / "base")
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            base = self.faux(d, 2 * m, ps)
            with self.assertRaisesRegex(rc.ErreurRecuperationV2, "normalisés"):
                rd.IndexAjuste(base, d / "aj", d / "base")


class TestEncodeurQ8(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.enc = rd.EncodeurQ8()
        except ImportError as exc:
            raise unittest.SkipTest(f"onnxruntime ou tokenizers absent : {exc}")

    def test_vecteur_normalise_et_deterministe(self):
        v = self.enc.encoder("Combien de jours de congés payés par mois ?")
        self.assertEqual((v.shape, v.dtype), ((384,), np.float32))
        self.assertAlmostEqual(float(np.linalg.norm(v)), 1.0, places=5)
        self.assertTrue(np.array_equal(v, self.enc.encoder("Combien de jours de congés payés par mois ?")))

    def test_proche_de_la_question(self):
        index = rag.charger_index()
        aj = rd.IndexAjuste(index)
        s = aj.matrice @ self.enc.encoder("Combien de jours de congés payés acquiert-on par mois de travail ?")
        meilleurs = [index.passages[i]["titre_fiche"] for i in np.argsort(-s)[:5]]
        self.assertTrue(any("congé" in t.lower() for t in meilleurs), meilleurs)

    def test_refus(self):
        with self.assertRaises(rag.ErreurRecuperation):
            self.enc.encoder("   ")
        with self.assertRaisesRegex(rag.ErreurRecuperation, "limite"):
            self.enc.encoder("mot " * 600)
        with self.assertRaisesRegex(rag.ErreurRecuperation, "empreinte"):
            rd.EncodeurQ8(sha256_attendu="0" * 64)
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / "modele"
            shutil.copytree(rd.MODELE_Q8, d)
            (d / "tokenizer.json").write_bytes((d / "tokenizer.json").read_bytes() + b" ")
            with self.assertRaisesRegex(rag.ErreurRecuperation, "tokeniseur"):
                rd.EncodeurQ8(d)


@unittest.skipUnless(mots_vides_disponibles(), "liste de mots vides Snowball absente de data/ (téléchargée au 1er lancement)")
class TestRecuperer(unittest.TestCase):
    """Chaîne complète sur 30 passages synthétiques, encodeur, reclasseur et tokeniseur simulés."""

    def setUp(self):
        self.passages = [passage(i) for i in range(30)]
        self.matrice = np.eye(30, 384, dtype=np.float32)
        q = np.zeros(384, dtype=np.float32)
        q[:30] = np.linspace(1, 0.1, 30)          # dense : p0 > p1 > ... > p29
        q /= np.linalg.norm(q)
        self.q = q

        class Reclasseur:
            def __init__(self):
                self.recus = []

            def scores(self, question, textes):
                self.recus.append(list(textes))
                return [float(int(t.split("numéro ")[1].rstrip(".").split()[0])) for t in textes]   # inverse le dense

        self.rcl = Reclasseur()
        self.tokens = {"par_passage": 100}

    def demo(self):
        return rd.RecuperationDemo(self.passages, lambda question: self.q, self.matrice, self.rcl,
                                   lambda question, ind: self.tokens["par_passage"] * len(ind), {"etat": "test"})

    def test_ordre_du_reclasseur_et_k(self):
        r = self.demo().recuperer("congé")
        self.assertEqual(len(r["candidats"]), 20)
        self.assertEqual(len(self.rcl.recus[0]), 20)
        self.assertTrue(self.rcl.recus[0][0].startswith("Fiche > Section\n"))   # en-tête et texte, comme au protocole 07
        self.assertEqual(len(r["contexte"]), 10)
        self.assertTrue(set(r["contexte"]) <= set(r["candidats"]))
        attendus = sorted(r["candidats"], key=lambda i: -i)[:10]               # score du reclasseur = numéro du passage
        self.assertEqual(r["contexte"], attendus)
        self.assertAlmostEqual(r["score_dense_max"], float(self.q[0]), places=6)
        self.assertEqual(r["groupes_retires"], 0)

    def test_budget_retire_les_derniers(self):
        self.tokens["par_passage"] = rc.PLAFOND_PROMPT // 4
        r = self.demo().recuperer("congé")
        self.assertEqual(len(r["contexte"]), 4)
        self.assertEqual(r["groupes_retires"], 6)
        self.assertLessEqual(r["tokens"], rc.PLAFOND_PROMPT)


class TestConfiguration(unittest.TestCase):
    def test_celle_du_protocole_07_retenue(self):
        self.assertEqual(rd.CONFIGURATION.nom, "rrf+k10+bge-m3@20")
        self.assertEqual((rd.PROFONDEUR, rc.RRF_K), (100, 60))
        self.assertEqual(rc.RECLASSEURS["bge-m3"][1], "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e")

    def test_r1_par_defaut(self):
        import inspect
        self.assertEqual(rd.DENSES[0], "base")
        self.assertEqual(inspect.signature(rd.RecuperationDemo.charger).parameters["dense"].default, "base")

    def test_partie_dense_inconnue(self):
        with self.assertRaises(rc.ErreurRecuperationV2):
            rd.RecuperationDemo.charger("autre")


if __name__ == "__main__":
    unittest.main()
