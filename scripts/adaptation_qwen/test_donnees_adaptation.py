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


class RecopieTests(unittest.TestCase):
    """Lot v2 : chaque phrase ou ligne citée reprend une unité entière de chacun des passages qu'elle cite."""
    textes = {"[P1]": "L'employeur doit consulter le CSE. Le délai est d'un mois.\n- Premier cas ;\n- Second cas.",
              "[P2]": "Une autre fiche, sans rapport avec la question posée."}

    def verdict(self, reponse):
        return da.verifier_recopie(reponse, self.textes)

    def test_recopies_acceptees(self):
        for r in ("L'employeur doit consulter le CSE. [P1]",
                  "L'employeur doit consulter le CSE [P1].",                              # référence avant le point
                  "l’employeur DOIT consulter le CSE [P1].",                              # casse et apostrophe
                  "Le délai est d'un mois. [P1]\nL'employeur doit consulter le CSE. [P1]",  # ordre libre
                  "Le délai est d'un mois.\n- Premier cas ;\n- Second cas. [P1]"):          # lignes d'une liste
            self.assertEqual(self.verdict(r), "ok", r)

    def test_recopies_refusees(self):
        cas = {"Le délai est d'un [P1].": "non_recopiee",                                   # fragment
               "L'employeur consulte le comité. [P1]": "non_recopiee",                      # reformulation
               "Voici la réponse : L'employeur doit consulter le CSE. [P1]": "non_recopiee",  # introduction
               "L'employeur doit consulter le CSE. [P1][P2]": "non_recopiee",               # citation superflue
               "L'employeur doit consulter le CSE. [P1] Bonne journée.": "texte_apres_la_derniere_reference",
               "Oui [P1].": "segment_trop_court",
               "L'employeur doit consulter le CSE. [P6]": "reference_inconnue",
               "L'employeur doit consulter le CSE.": "aucune_reference"}
        for r, motif in cas.items():
            self.assertEqual(self.verdict(r), motif, r)

    def test_consigne_de_recopie_seulement_pour_les_exemples_cites_d_un_lot_v2(self):
        c = {"variante": "citee", "contexte": {"system": "S85", "prompt": "U"}}
        v2 = {"reponses_citees": "recopiees"}
        self.assertEqual(da.entree_reponse(c, {}), da.texte_brut("S85", "U"))                   # lot v1
        self.assertEqual(da.entree_reponse(c, v2), da.texte_brut("S85\n\n" + da.CONSIGNE_RECOPIE, "U"))
        for v in ("passage_retire", "hors_corpus"):                                            # abstentions : la #85
            self.assertEqual(da.entree_reponse({**c, "variante": v}, v2), da.texte_brut("S85", "U"))

    def test_contextes_ecartes_d_un_lot_v2(self):
        v2 = {"variantes": list(da.VARIANTES_V2), "questions_exclues": ["Ma question relue ?"]}
        c = lambda v, q="Une autre question ?": {"variante": v, "question": q}
        self.assertEqual([da.ecarte(c(v), v2) for v in ("citee", "passage_retire", "hors_corpus")],
                         [None, "variante_retiree", None])
        self.assertEqual(da.ecarte(c("citee", "ma question  RELUE ?"), v2), "question_relue")   # normalisée
        self.assertIsNone(da.ecarte(c("passage_retire"), {}))                                  # lot v1 : tout est gardé


class RepriseTests(unittest.TestCase):
    def lot_v1(self, d: Path) -> Path:
        lot = d / "v1"
        lot.mkdir()
        for n in da.REPRIS:
            (lot / n).write_text(f"contenu de {n}\n", encoding="utf-8")
        variantes = ["citee"] * 40 + ["passage_retire"] * 10 + ["hors_corpus"] * 10
        ex = [{"id": f"A{i:04d}", "variante": v, "question": f"Question {i} ?"} for i, v in enumerate(variantes)]
        da.ecrire_jsonl(lot / "train.jsonl", ex[:54])
        da.ecrire_jsonl(lot / "valid.jsonl", ex[54:])
        noms = da.REPRIS + ("train.jsonl", "valid.jsonl")
        (lot / "manifeste.json").write_text(json.dumps({"sha256": {n: da.sha256_fichier(lot / n) for n in noms}}),
                                            encoding="utf-8")
        return lot

    def test_reprise_controlee_et_questions_relues_exclues(self):
        with tempfile.TemporaryDirectory() as d:
            v1 = self.lot_v1(Path(d))
            v2 = Path(d) / "v2"
            da.etape_reprendre(v2, v1)
            for n in da.REPRIS:
                self.assertEqual((v2 / n).read_bytes(), (v1 / n).read_bytes())
            config = da.lire_config(v2)
            exemples = da.lire_jsonl(v1 / "train.jsonl") + da.lire_jsonl(v1 / "valid.jsonl")
            relues = set(da.tirage_relecture(exemples))
            self.assertEqual(len(relues), 30)
            self.assertEqual(config["questions_exclues"], sorted(e["question"] for e in exemples if e["id"] in relues))
            self.assertEqual((config["depuis"], config["reponses_citees"], config["version"], config["variantes"]),
                             ("v1", "recopiees", da.VERSION, ["citee", "hors_corpus"]))
            with self.assertRaisesRegex(da.ErreurDonnees, "existe déjà"):          # jamais remplacé
                da.etape_reprendre(v2, v1)
            pilote = Path(d) / "pilote.jsonl"
            da.ecrire_jsonl(pilote, [{"question": "Question du pilote ?"}, {"question": config["questions_exclues"][0]}])
            da.etape_reprendre(Path(d) / "v2b", v1, pilote)
            c2 = da.lire_config(Path(d) / "v2b")
            self.assertEqual((len(c2["questions_exclues"]), c2["questions_relues"], c2["questions_du_pilote"]), (31, 30, 2))
            self.assertIn("Question du pilote ?", c2["questions_exclues"])
            self.assertEqual(c2["pilote_sha256"], da.sha256_fichier(pilote))

    def test_lot_source_modifie_refuse(self):
        with tempfile.TemporaryDirectory() as d:
            v1 = self.lot_v1(Path(d))
            with open(v1 / "3_contextes.jsonl", "a", encoding="utf-8") as f:
                f.write("ajout\n")
            with self.assertRaisesRegex(da.ErreurDonnees, "diffère de son manifeste"):
                da.etape_reprendre(Path(d) / "v2", v1)
            self.assertFalse((Path(d) / "v2").exists())


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

    def test_lot_v2_recopie_et_questions_exclues(self):
        autorises = [p["passage_id"] for p in self.index.passages if self.fiches[p["passage_id"]] not in self.exclues]
        texte = next(p["texte"] for p in self.index.passages if p["passage_id"] == autorises[0])
        unite = next(u for u in da.SEPARATEUR_UNITES.split(texte) if len(da.mots(u)) >= 3).strip()
        cas = ((f"{unite} [P1]", [], {"citee": 1}, {}),
               ("Une phrase reformulée qui ne vient pas du passage [P1].", [], {"citee": 0}, {"citee:non_recopiee": 1}),
               (f"{unite} [P1]", ["Question de test ?"], {"citee": 0}, {}))
        for reponse_texte, exclues, effectifs, rejets in cas:
            with self.subTest(reponse_texte[:30], exclues=exclues), tempfile.TemporaryDirectory() as d:
                lot = self.preparer(d, autorises[:5], reponse_texte=reponse_texte)
                (lot / "config.json").write_text(json.dumps({"reponses_citees": "recopiees",
                                                             "questions_exclues": exclues}), encoding="utf-8")
                da.etape_assembler(lot)
                m = json.loads((lot / "manifeste.json").read_text())
                self.assertEqual(m["effectifs"]["citee"], effectifs["citee"])
                self.assertEqual(m["rejets"], rejets)
                self.assertEqual(m["questions_relues_exclues"], len(exclues))
                self.assertEqual(m["ecartes_a_l_assemblage"], {"question_relue": 1} if exclues else {})
                self.assertIn("config.json", m["sha256"])

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
