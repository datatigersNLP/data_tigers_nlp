"""Tests du générateur de données d'adaptation (#107, étape 22), sans modèle génératif ni encodeur."""

import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

import donnees_adaptation as da
import rag
import separation


def reponse(texte, arret="stop"):
    return {"texte": texte, "arret": arret, "tokens_entree": 100, "tokens_sortie": 10}


class FormatTests(unittest.TestCase):
    def test_texte_brut_identique_au_format_controle_par_la_85(self):
        self.assertEqual(da.texte_brut("S", "U"),
                         "<|im_start|>system\nS<|im_end|>\n<|im_start|>user\nU<|im_end|>\n<|im_start|>assistant\n")


class QuestionsTests(unittest.TestCase):
    passage = ("L'employeur doit prendre les mesures nécessaires pour assurer la sécurité et protéger la santé "
               "physique et mentale des travailleurs pendant les fortes chaleurs.")

    def test_question_acceptee(self):
        q, motif = da.nettoyer_question("Que doit faire mon employeur quand il fait très chaud au bureau ?\n",
                                        self.passage)
        self.assertEqual((q, motif), ("Que doit faire mon employeur quand il fait très chaud au bureau ?", "ok"))

    def test_questions_refusees(self):
        cas = {"Première ligne ?\nSeconde ligne ?": "plusieurs_lignes", "": "vide",
               "Une affirmation sans point d'interrogation.": "forme",
               "Selon le passage, que doit faire l'employeur ?": "renvoi_au_passage",
               "Est-il vrai que l'employeur doit prendre les mesures nécessaires pour assurer la sécurité ?": "recopie"}
        for sortie, motif in cas.items():
            self.assertEqual(da.nettoyer_question(sortie, self.passage), (None, motif), sortie)

    def test_questions_enchainees_sur_une_ligne(self):
        sortie = "Quand puis-je partir à la retraite ? Comment est calculée ma pension ? Puis-je cumuler emploi et retraite ?"
        self.assertEqual(da.questions_listees(sortie), ["Quand puis-je partir à la retraite ?",
                                                        "Comment est calculée ma pension ?",
                                                        "Puis-je cumuler emploi et retraite ?"])

    def test_questions_listees_sans_numero_ni_doublon(self):
        sortie = "1. Quand puis-je partir à la retraite ?\n- Quand puis-je partir à la retraite ?\n2) Comment est calculée ma pension ?\nTexte libre."
        self.assertEqual(da.questions_listees(sortie),
                         ["Quand puis-je partir à la retraite ?", "Comment est calculée ma pension ?"])


class SourcesTests(unittest.TestCase):
    def setUp(self):
        self.passages = [{"passage_id": f"p{i}", "texte": "x" * (400 if i != 3 else 50)} for i in range(12)]
        self.fiches = {f"p{i}": f"f{i % 3}" for i in range(12)}          # f0, f1, f2, quatre passages chacune

    def test_exclusion_longueur_quota_et_reproductibilite(self):
        s = da.choisir_sources(self.passages, self.fiches, {"f2"}, n=10)
        self.assertTrue(all(x["fiche_cible"] != "f2" for x in s))           # fiche exclue
        self.assertNotIn("p3", [x["passage_cible"] for x in s])              # passage trop court
        self.assertTrue(all(sum(y["fiche_cible"] == f for y in s) <= da.MAX_PAR_FICHE for f in ("f0", "f1")))
        self.assertEqual(s, da.choisir_sources(self.passages, self.fiches, {"f2"}, n=10))

    def test_fiches_de_validation(self):
        fiches = {f"p{i}": f"f{i}" for i in range(50)}
        v = da.fiches_validation(fiches, {"f0", "f1"})
        self.assertEqual(len(v), round(0.10 * 48))
        self.assertFalse({"f0", "f1"} & set(v))
        self.assertEqual(v, da.fiches_validation(fiches, {"f0", "f1"}))


class RecuperationTests(unittest.TestCase):
    def test_index_restreint_garde_le_classement_de_la_85(self):
        rng = np.random.default_rng(0)
        m = rng.normal(size=(40, 384)).astype(np.float32)
        m /= np.linalg.norm(m, axis=1, keepdims=True)
        passages = [{"passage_id": f"p{i}", "fiche": f"f{i % 4}"} for i in range(40)]
        index = rag.IndexCommun({}, m, passages)
        restreint = da.sous_index(index, lambda p: p["fiche"] != "f1")
        for _ in range(20):
            v = rng.normal(size=384).astype(np.float32)
            v /= np.linalg.norm(v)
            complet = [r["passage"]["passage_id"] for r in rag.recuperer_passages(index, v, top_k=40)]
            attendu = [p for p in complet if passages[int(p[1:])]["fiche"] != "f1"][:5]
            self.assertEqual([r["passage"]["passage_id"] for r in rag.recuperer_passages(restreint, v, 5)], attendu)


class ConservationTests(unittest.TestCase):
    contexte = {"sources": [{"reference": f"[P{k}]", "passage_id": f"p{k}"} for k in range(1, 6)]}

    def test_exemple_cite(self):
        g = lambda t, arret="stop": da.garder_citee(reponse(t, arret), self.contexte, "p2", rag.ABSTENTION)
        self.assertEqual(g("L'employeur doit agir [P2]."), (True, "ok"))
        self.assertEqual(g("L'employeur doit agir [P1]."), (False, "cible_non_citee"))
        self.assertEqual(g("Réponse coupée [P2]", "length"), (False, "reponse_coupee"))
        self.assertEqual(g(rag.ABSTENTION)[0], False)
        self.assertEqual(g("Sans aucune référence.")[0], False)

    def test_passage_retire_garde_seulement_si_qwen_s_abstient(self):
        self.assertEqual(da.garder_retire(reponse(rag.ABSTENTION), rag.ABSTENTION), (True, "ok"))
        self.assertEqual(da.garder_retire(reponse("Oui [P1]."), rag.ABSTENTION), (False, "qwen_repond_sans_la_fiche"))

    def test_equilibrage_a_la_part_du_lot_de_test(self):
        def ex(nc, na):
            return ([{"id": f"C{i}", "type": "citee"} for i in range(nc)]
                    + [{"id": f"A{i}", "type": "abstention"} for i in range(na)])
        for nc, na in ((300, 40), (300, 200), (73, 24)):
            e = da.equilibrer(ex(nc, na))
            part = sum(x["type"] == "abstention" for x in e) / len(e)
            self.assertAlmostEqual(part, 24 / 97, delta=0.005, msg=(nc, na))
            self.assertEqual(len({x["id"] for x in e}), len(e))               # ni doublon ni création
            self.assertTrue({x["id"] for x in e} <= {x["id"] for x in ex(nc, na)})
            self.assertEqual(e, da.equilibrer(ex(nc, na)))                     # reproductible
        self.assertEqual(len(da.equilibrer(ex(5, 0))), 5)                      # une classe vide : rien n'est retiré

    def test_tirage_de_relecture_stratifie(self):
        ex = ([{"id": f"C{i:03d}", "variante": "citee"} for i in range(224)]
              + [{"id": f"R{i:03d}", "variante": "passage_retire"} for i in range(40)]
              + [{"id": f"H{i:03d}", "variante": "hors_corpus"} for i in range(34)])     # lot du 30/10
        t = da.tirage_relecture(ex)
        compte = lambda p: sum(i.startswith(p) for i in t)
        self.assertEqual((len(t), compte("C"), compte("R"), compte("H")), (30, 15, 8, 7))
        self.assertEqual(t, da.tirage_relecture(ex))                                     # reproductible
        grand = ex * 1
        grand += [{"id": f"C{i:03d}x", "variante": "citee"} for i in range(500)]
        self.assertEqual(len(da.tirage_relecture(grand)), round(0.10 * len(grand)))     # 10 % au-delà de 300
        peu = ex[:224] + ex[224:226] + ex[264:300]                                      # 2 « passage retiré » seulement
        self.assertEqual(sum(i.startswith("R") for i in da.tirage_relecture(peu)), 2)


class AssemblageTests(unittest.TestCase):
    """Bout en bout sur le vrai index et le vrai jeu, avec des réponses fabriquées."""

    def setUp(self):
        self.index = rag.charger_index()
        self.exclues, self.fiches, _ = da.contexte_separation(self.index)

    def preparer(self, d, ids, variante="citee", reponse_texte=None):
        lot = Path(d)
        for n in ("1_sources.jsonl", "2_questions.jsonl", "3_contextes.jsonl"):
            (lot / n).write_text("", encoding="utf-8")
        (lot / "fiches_validation.json").write_text("[]", encoding="utf-8")
        par_id = {p["passage_id"]: p for p in self.index.passages}
        resultats = [{"rang": k, "passage": par_id[i]} for k, i in enumerate(ids, 1)]
        contexte = rag.construire_contexte("Question de test ?", resultats)
        ligne = {"type": "citee", "variante": variante, "question": "Question de test ?",
                 "passage_cible": ids[0], "fiche_cible": self.fiches[ids[0]], "passages": ids, "score_max": 0.9,
                 "contexte": contexte, "reponse_qwen": reponse(reponse_texte or "Réponse [P1].")}
        da.ecrire_jsonl(lot / "4_reponses.jsonl", [ligne])
        return lot

    def test_assemblage_format_et_separation(self):
        autorises = [p["passage_id"] for p in self.index.passages if self.fiches[p["passage_id"]] not in self.exclues]
        with tempfile.TemporaryDirectory() as d:
            lot = self.preparer(d, autorises[:5])
            da.etape_assembler(lot)
            train = da.lire_jsonl(lot / "train.jsonl")
            self.assertEqual(len(train), 1)
            e = train[0]
            self.assertEqual([m["role"] for m in e["messages"]], ["system", "user", "assistant"])
            self.assertEqual(e["messages"][0]["content"], rag.CONSIGNE_RAG)
            self.assertNotIn("prompt", e)                       # sinon mlx-lm changerait de format
            self.assertEqual(json.loads((lot / "manifeste.json").read_text())["separation"]["violations"], 0)
            with self.assertRaises(FileExistsError):             # une sortie n'est jamais remplacée
                da.etape_assembler(lot)

    def test_passage_d_une_fiche_du_lot_de_test_arrete_tout(self):
        interdit = next(p["passage_id"] for p in self.index.passages if self.fiches[p["passage_id"]] in self.exclues)
        autorises = [p["passage_id"] for p in self.index.passages if self.fiches[p["passage_id"]] not in self.exclues]
        with tempfile.TemporaryDirectory() as d:
            lot = self.preparer(d, autorises[:4] + [interdit], reponse_texte="Réponse [P1].")
            with self.assertRaisesRegex(da.ErreurDonnees, "séparation"):
                da.etape_assembler(lot)
            self.assertFalse((lot / "train.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
