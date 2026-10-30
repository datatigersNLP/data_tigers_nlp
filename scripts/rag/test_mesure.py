"""Tests de la mesure du volet B (protocole 06), sans modèle, sans Ollama et sans lecture du lot de test."""

import contextlib
import hashlib
import io
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

import mesure
from generation import ErreurGeneration, valider_citations
from rag import ABSTENTION, CONSIGNE_RAG, IndexCommun


def faux_index(n=6, dimension=4):
    lignes = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 0]][:n]
    matrice = np.array(lignes, dtype=np.float32)
    matrice /= np.linalg.norm(matrice, axis=1, keepdims=True)
    passages = [{"passage_id": f"p{i}", "titre_fiche": f"Fiche {i}", "section_titre": "Section", "chemin": [],
                 "url": f"https://travail-emploi.gouv.fr/f{i}", "url_citation": f"https://travail-emploi.gouv.fr/f{i}#s",
                 "date_maj": "2026-09-11", "texte": f"Texte du passage {i}."} for i in range(n)]
    entete = {"index": {"sha256": "i" * 64}, "metadonnees": {"sha256": "m" * 64}}
    return IndexCommun(entete, matrice, passages)


def encodeur_score(scores: dict):
    """Encodeur factice : la question vaut un vecteur dont le cosinus avec p0 est le score demandé."""
    def encoder(texte):
        s = scores[texte]
        return np.array([s, math.sqrt(1 - s * s), 0, 0], dtype=np.float32)
    return encoder


def question(id_, type_="dans_corpus", texte=None, fiche="f0"):
    return {"id": id_, "type": type_, "question": texte or f"Question {id_} ?",
            "fiche": fiche if type_ == "dans_corpus" else None, "extrait": None}


def empreinte_dossier(dossier: Path) -> dict:
    """Chemins et empreintes de tous les fichiers d'un dossier, vide s'il n'existe pas."""
    if not dossier.exists():
        return {}
    return {str(p.relative_to(dossier)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(dossier.rglob("*")) if p.is_file()}


class FauxGenerateur:
    def __init__(self, reponse="Réponse [P1].", exception=False, version=None):
        self.appels, self.reponse, self.exception = [], reponse, exception
        self.version = version or mesure.VERSION_OLLAMA

    def __call__(self, contexte, abstention, modele, digest):
        self.appels.append({"contexte": contexte, "modele": modele, "digest": digest})
        if self.exception:
            raise ErreurGeneration("Ollama indisponible")
        validation = valider_citations(self.reponse, contexte["sources"], abstention)
        return {"statut": validation["statut"], "erreurs_techniques": [], "reponse_brute": self.reponse,
                "validation_citations": validation, "mesures_ollama": {"prompt_eval_count": 100, "eval_count": 10,
                                                                      "total_duration": 5},
                "entree": {"nb_tokens": 100, "sha256_texte": "t"}, "ollama": {"digest": digest, "version": self.version}}


class ConsignesTests(unittest.TestCase):
    def test_b1_est_la_consigne_de_la_85_sans_ses_deux_lignes_d_abstention(self):
        lignes = CONSIGNE_RAG.split("\n")
        self.assertEqual(mesure.consigne_b1(), "\n".join(lignes[:-2]))
        self.assertNotIn(ABSTENTION, mesure.consigne_b1())

    def test_b0_reprend_mot_pour_mot_la_phrase_de_brievete_de_b1(self):
        phrase = "Réponds brièvement et conserve les conditions et exceptions nécessaires."
        self.assertIn(phrase, mesure.consigne_b1().split("\n"))
        self.assertIn(phrase, mesure.CONSIGNE_B0.split("\n"))
        self.assertTrue(mesure.CONSIGNE_B0.endswith("\n" + ABSTENTION))
        self.assertIn(ABSTENTION, mesure.CONSIGNE_B0)

    def test_reponse_fixe_de_r_plus_est_une_reponse_citee(self):
        sources = [{"reference": "[P1]"}]
        v = valider_citations(mesure.REPONSE_R_PLUS, sources, ABSTENTION)
        self.assertEqual((v["statut"], v["citations"]), ("reponse_citee", ["[P1]"]))


class ClassementTests(unittest.TestCase):
    def test_classes_de_la_section_4(self):
        self.assertEqual(mesure.classer("abstention_modele", "B2"), "abstention")
        self.assertEqual(mesure.classer("reponse_citee", "B1"), "reponse_citee")
        self.assertEqual(mesure.classer("sortie_invalide", "B2"), "sortie_invalide")
        self.assertEqual(mesure.classer("erreur_technique", "B0"), "erreur_technique")
        # sans passage, toute sortie autre qu'une abstention ou une erreur est une réponse
        self.assertEqual(mesure.classer("sortie_invalide", "B0"), "reponse")
        self.assertEqual(mesure.classer("abstention_modele", "B0"), "abstention")
        with self.assertRaises(mesure.ErreurMesure):
            mesure.classer("autre", "B1")


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.index = faux_index()
        self.qs = [question("Q1", texte="haut"), question("Q2", texte="bas"), question("Q3", "hors_corpus", "hors")]
        self.encoder = encodeur_score({"haut": 0.9, "bas": 0.8, "hors": 0.8})
        self.preparees = mesure.preparer_questions(self.qs, self.index, self.encoder, seuil=0.85)

    def test_b2_sous_le_seuil_s_abstient_sans_appeler_le_modele(self):
        gen = FauxGenerateur()
        lignes = {l["id"]: l for l in mesure.executer_etat("B2", self.preparees, gen, "m", "d")}
        self.assertEqual(len(gen.appels), 1)                      # seule Q1 dépasse le seuil
        self.assertEqual(gen.appels[0]["contexte"]["system"], CONSIGNE_RAG)
        self.assertEqual((lignes["Q2"]["classe"], lignes["Q2"]["appel_modele"]), ("abstention", False))
        self.assertEqual(lignes["Q2"]["motifs"], ["sous_le_seuil"])
        self.assertEqual(lignes["Q1"]["classe"], "reponse_citee")
        self.assertEqual(lignes["Q1"]["passages_cites"], ["p0"])

    def test_inegalite_stricte_et_signalement_a_1e_5(self):
        score = float(np.float32(0.9))
        egal = mesure.preparer_questions(self.qs[:1], self.index, self.encoder, seuil=score)[0]
        self.assertFalse(egal["sous_le_seuil"])
        self.assertTrue(egal["proche_du_seuil"])
        proche = mesure.preparer_questions(self.qs[:1], self.index, self.encoder, seuil=score + 5e-6)[0]
        self.assertTrue(proche["sous_le_seuil"] and proche["proche_du_seuil"])
        loin = mesure.preparer_questions(self.qs[:1], self.index, self.encoder, seuil=score + 2e-5)[0]
        self.assertFalse(loin["proche_du_seuil"])

    def test_b0_et_b1_appellent_le_modele_avec_leur_consigne(self):
        gen = FauxGenerateur()
        mesure.executer_etat("B0", self.preparees, gen, "m", "d")
        self.assertTrue(all(a["contexte"]["system"] == mesure.CONSIGNE_B0 and a["contexte"]["sources"] == []
                            for a in gen.appels))
        self.assertTrue(gen.appels[0]["contexte"]["prompt"].startswith(mesure.ENTETE_B0))
        gen1 = FauxGenerateur()
        mesure.executer_etat("B1", self.preparees, gen1, "m", "d")
        self.assertEqual(len(gen1.appels), 3)                     # B1 ignore le seuil
        self.assertTrue(all(a["contexte"]["system"] == mesure.consigne_b1() for a in gen1.appels))

    def test_references_degenerees_sans_appel(self):
        gen = FauxGenerateur()
        plus = mesure.executer_etat("R+", self.preparees, gen, "m", "d")
        moins = mesure.executer_etat("R-", self.preparees, gen, "m", "d")
        self.assertEqual(gen.appels, [])
        self.assertTrue(all(l["classe"] == "reponse_citee" and l["citations"] == ["[P1]"] for l in plus))
        self.assertTrue(all(l["classe"] == "abstention" for l in moins))

    def test_exception_de_generation_est_une_erreur_technique(self):
        lignes = mesure.executer_etat("B1", self.preparees, FauxGenerateur(exception=True), "m", "d")
        self.assertTrue(all(l["classe"] == "erreur_technique" and l["citations"] == [] for l in lignes))

    def test_version_d_ollama_autre_que_l_epinglee_interrompt_la_mesure(self):
        self.assertEqual(mesure.VERSION_OLLAMA, "0.40.11")
        for etat in ("B0", "B1", "B2"):
            with self.assertRaisesRegex(mesure.ErreurMesure, "version épinglée"):
                mesure.executer_etat(etat, self.preparees, FauxGenerateur(version="0.40.13"), "m", "d")
        lignes = mesure.executer_etat("B1", self.preparees, FauxGenerateur(), "m", "d")
        self.assertEqual(mesure.versions_ollama(lignes), ["0.40.11"])
        # références dégénérées et abstentions sous le seuil : aucun appel, donc rien à contrôler
        self.assertEqual(mesure.versions_ollama(mesure.executer_etat("R+", self.preparees,
                                                                     FauxGenerateur(version="x"), "m", "d")), [])

    def test_modele_et_digest_transmis(self):
        gen = FauxGenerateur()
        mesure.executer_etat("B1", self.preparees, gen, "adapte", "abc")
        self.assertEqual({(a["modele"], a["digest"]) for a in gen.appels}, {("adapte", "abc")})


class EcritureTests(unittest.TestCase):
    def test_une_seule_execution_et_reprise_d_un_etat_invalide(self):
        with tempfile.TemporaryDirectory() as d:
            chemin = Path(d) / "B2.jsonl"
            bonnes = [{"classe": "abstention"}] * 20
            mesure.ecrire_etat(chemin, bonnes)
            with self.assertRaisesRegex(mesure.ErreurMesure, "une seule exécution"):
                mesure.ecrire_etat(chemin, bonnes)
            with self.assertRaisesRegex(mesure.ErreurMesure, "pas invalide"):
                mesure.ecrire_etat(chemin, bonnes, reprendre=True)
            chemin.write_text("".join(json.dumps(l) + "\n" for l in [{"classe": "erreur_technique"}] * 2
                                      + [{"classe": "abstention"}] * 18), encoding="utf-8")
            mesure.ecrire_etat(chemin, bonnes, reprendre=True)       # 10 % d'erreurs : état invalide
            self.assertTrue((Path(d) / "B2.invalide-1.jsonl").exists())
            self.assertEqual(mesure.part_erreurs(mesure.lire_etat(chemin)), 0.0)


class VerrouTests(unittest.TestCase):
    def test_verrou_absent_modifie_ou_reecrit(self):
        index = faux_index()
        with tempfile.TemporaryDirectory() as d:
            protocole, verrou = Path(d) / "protocole.md", Path(d) / "verrou.json"
            protocole.write_text("version gelée", encoding="utf-8")
            with patch.object(mesure, "PROTOCOLE", protocole):
                with self.assertRaisesRegex(mesure.ErreurMesure, "Verrou absent"):
                    mesure.verifier_verrou(index.entete, verrou)
                mesure.verrouiller(index.entete, verrou)
                self.assertEqual(mesure.verifier_verrou(index.entete, verrou)["protocole"],
                                 mesure.sha256_fichier(protocole))
                with self.assertRaisesRegex(mesure.ErreurMesure, "déjà écrit"):
                    mesure.verrouiller(index.entete, verrou)
                protocole.write_text("version modifiée", encoding="utf-8")
                with self.assertRaisesRegex(mesure.ErreurMesure, "protocole"):
                    mesure.verifier_verrou(index.entete, verrou)

    def test_mode_mesure_refuse_sans_verrou_et_sans_lire_le_lot_de_test(self):
        index = faux_index()
        with tempfile.TemporaryDirectory() as d, \
                patch.object(mesure, "VERROU", Path(d) / "absent.json"), \
                patch.object(mesure, "lire_jeu", side_effect=AssertionError("lot lu")) as lecture:
            code = mesure.main(["executer", "--mode", "mesure", "--phase", "avant"],
                               outils=lambda: (index, encodeur_score({}), FauxGenerateur()))
        self.assertEqual(code, 1)
        lecture.assert_not_called()

    def test_phase_avant_reservee_au_modele_de_31_et_phases_suivantes_a_leur_modele(self):
        self.assertEqual(mesure.main(["executer", "--mode", "calibration", "--phase", "avant",
                                      "--modele", "autre"], outils=lambda: None), 1)
        self.assertEqual(mesure.main(["executer", "--mode", "calibration", "--phase", "apres"],
                                     outils=lambda: None), 1)


class BoutEnBoutTests(unittest.TestCase):
    @unittest.skipUnless(mesure.FICHIER_SEUIL.exists(), "seuil_b2.json absent de data/")
    def test_calibration_complete_dans_un_dossier_temporaire(self):
        # Les sorties réelles de data/, s'il y en a (la calibration du Legion, par exemple), restent intactes.
        reelles = empreinte_dossier(mesure.SORTIES)
        index = faux_index()
        encoder = lambda texte: np.array([0.9, math.sqrt(1 - 0.81), 0, 0], dtype=np.float32)
        outils = lambda: (index, encoder, FauxGenerateur())
        sortie = io.StringIO()
        with tempfile.TemporaryDirectory() as d, patch.object(mesure, "SORTIES", Path(d)), \
                contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(io.StringIO()):
            avant = Path(d) / "calibration" / "avant"
            self.assertEqual(mesure.main(["executer", "--mode", "calibration", "--phase", "avant"], outils=outils), 0)
            fichiers = sorted(p.name for p in avant.iterdir())
            self.assertEqual([f for f in fichiers if f.endswith(".jsonl")],
                             ["B0.jsonl", "B1.jsonl", "B2.jsonl", "Rmoins.jsonl", "Rplus.jsonl"])
            self.assertEqual(len(mesure.lire_etat(avant / "B2.jsonl")), 8)
            execution = empreinte_dossier(avant)
            self.assertEqual(mesure.main(["executer", "--mode", "calibration", "--phase", "avant"], outils=outils), 1)
            self.assertEqual(empreinte_dossier(avant), execution)            # dossier déjà présent : rien ne change
            # Analyse : jamais d'écrasement ; une nouvelle analyse s'écrit à côté
            self.assertEqual(mesure.main(["analyser", "--mode", "calibration", "--phase", "avant"], outils=outils), 0)
            premiere = (avant / "metriques.json").read_bytes()
            analyse = json.loads(premiere)
            self.assertEqual(set(analyse["sources"]), set(mesure.ETATS))
            self.assertEqual(analyse["sources"]["B2"]["sha256"], mesure.sha256_fichier(avant / "B2.jsonl"))
            self.assertEqual(mesure.main(["analyser", "--mode", "calibration", "--phase", "avant"], outils=outils), 1)
            self.assertEqual((avant / "metriques.json").read_bytes(), premiere)
            self.assertEqual(mesure.main(["analyser", "--mode", "calibration", "--phase", "avant",
                                          "--nouvelle-analyse"], outils=outils), 0)
            self.assertEqual((avant / "metriques.json").read_bytes(), premiere)
            self.assertTrue((avant / "metriques-2.json").exists())
            # Comparaisons : une phase avec elle-même est refusée ; la calibration n'est jamais l'analyse principale
            self.assertEqual(mesure.main(["comparer", "--mode", "calibration", "--a", "avant", "--b", "avant"],
                                         outils=outils), 1)
            self.assertEqual(mesure.main(["executer", "--mode", "calibration", "--phase", "apres",
                                          "--modele", "adapte", "--digest", "d" * 64], outils=outils), 0)
            sortie.truncate(0), sortie.seek(0)
            self.assertEqual(mesure.main(["comparer", "--mode", "calibration", "--a", "apres", "--b", "avant",
                                          "--reference", "avant"], outils=outils), 0)
            comparaison = json.loads(sortie.getvalue())
            self.assertEqual(comparaison["analyse"], "descriptive")
            self.assertFalse(any(comparaison[m]["analyse_principale"] for m in ("M1", "M2", "M3", "M4", "M5")))
            self.assertFalse(any("amelioration_demontree" in comparaison[m] for m in ("M1", "M4")))
        self.assertEqual(empreinte_dossier(mesure.SORTIES), reelles)

    def test_analyse_principale_exige_sa_reference_en_mode_mesure(self):
        with contextlib.redirect_stderr(io.StringIO()):
            code = mesure.main(["comparer", "--mode", "mesure", "--a", "apres", "--b", "avant"],
                               outils=lambda: (_ for _ in ()).throw(AssertionError("index chargé")))
        self.assertEqual(code, 1)


class JeuEtSeuilTests(unittest.TestCase):
    def test_lot_de_calibration_et_refus_d_un_jeu_modifie(self):
        qs = mesure.lire_jeu("calibration")
        self.assertEqual((sum(q["type"] == "dans_corpus" for q in qs), sum(q["type"] == "hors_corpus" for q in qs)),
                         (5, 3))
        self.assertTrue(all(q["fiche"] and q["extrait"] for q in qs if q["type"] == "dans_corpus"))
        faux = type("R", (), {"stdout": b"id,lot\n"})()
        with patch.object(mesure.subprocess, "run", return_value=faux):
            with self.assertRaisesRegex(mesure.ErreurMesure, "Empreinte du jeu"):
                mesure.lire_jeu("calibration")

    def test_seuil_lu_en_valeur_complete_et_refus_d_un_fichier_modifie(self):
        with tempfile.TemporaryDirectory() as d:
            faux = Path(d) / "seuil.json"
            faux.write_text('{"seuil": 0.8565}', encoding="utf-8")
            with self.assertRaisesRegex(mesure.ErreurMesure, "Empreinte du fichier du seuil"):
                mesure.charger_seuil(faux)
        if mesure.FICHIER_SEUIL.exists():
            self.assertEqual(repr(mesure.charger_seuil()), "0.856489074230194")


class MetriquesTests(unittest.TestCase):
    def ligne(self, id_, type_, classe, cites=(), fiche="f0", etat="B2"):
        return {"id": id_, "type": type_, "fiche": fiche if type_ == "dans_corpus" else None, "etat": etat,
                "classe": classe, "passages_cites": list(cites), "proche_du_seuil": False, "reponse": "x [P1].",
                "mesures_ollama": None}

    def test_metriques_et_exclusion_des_erreurs_techniques(self):
        lignes = [self.ligne("C1", "dans_corpus", "reponse_citee", ["p0"], "f0"),
                  self.ligne("C2", "dans_corpus", "reponse_citee", ["p9"], "f1"),
                  self.ligne("C3", "dans_corpus", "abstention", fiche="f2"),
                  self.ligne("C4", "dans_corpus", "erreur_technique", fiche="f3"),
                  self.ligne("H1", "hors_corpus", "abstention"),
                  self.ligne("H2", "hors_corpus", "sortie_invalide")]
        m = mesure.metriques(lignes, {"C1": {"p0"}, "C2": {"p1"}, "C3": {"p0"}, "C4": {"p0"}})
        self.assertEqual((m["M2"]["succes"], m["M2"]["effectif"]), (1, 3))     # C4 retirée du dénominateur
        self.assertEqual((m["M3"]["succes"], m["M4"]["succes"]), (2, 1))       # C2 cite un passage non pertinent
        self.assertEqual((m["M1"]["succes"], m["M5"]["succes"], m["M5"]["effectif"]), (1, 1, 2))
        self.assertAlmostEqual(m["part_erreurs"], 1 / 6)
        self.assertTrue(m["etat_invalide"])
        bas, haut = m["M3"]["ic95"]
        self.assertTrue(0 <= bas <= 2 / 3 <= haut <= 1)

    def test_b0_sans_m3_ni_m4_et_reponse_comptee_en_m5(self):
        lignes = [self.ligne("C1", "dans_corpus", "reponse", etat="B0"),
                  self.ligne("H1", "hors_corpus", "reponse", etat="B0")]
        m = mesure.metriques(lignes, {"C1": set()})
        self.assertIsNone(m["M3"])
        self.assertIsNone(m["M4"])
        self.assertEqual(m["M5"]["succes"], 1)

    def test_couverture_structurelle(self):
        self.assertEqual(mesure.couverture("Un [P1]. Deux sans référence. Trois [P2]."), 2 / 3)


class ComparaisonTests(unittest.TestCase):
    def lignes(self, classes):
        return [{"id": i, "type": t, "fiche": f, "etat": "B2", "classe": c, "passages_cites": ["p0"]}
                for i, t, f, c in classes]

    def test_population_commune_par_identifiant_et_analyse_principale(self):
        a = self.lignes([("H1", "hors_corpus", None, "abstention"), ("H2", "hors_corpus", None, "abstention"),
                         ("H3", "hors_corpus", None, "erreur_technique"), ("C1", "dans_corpus", "f0", "reponse_citee"),
                         ("C2", "dans_corpus", "f1", "reponse_citee")])
        b = self.lignes([("C2", "dans_corpus", "f1", "abstention"), ("H3", "hors_corpus", None, "abstention"),
                         ("H2", "hors_corpus", None, "reponse_citee"), ("C1", "dans_corpus", "f0", "reponse_citee"),
                         ("H1", "hors_corpus", None, "abstention")])
        r = mesure.comparer(a, b, {"C1": {"p0"}, "C2": {"p0"}}, principale=True)
        self.assertEqual(r["analyse"], "principale (section 6)")
        self.assertEqual((r["M1"]["effectif_commun"], r["M1"]["exclus"]), (2, ["H3"]))
        self.assertEqual((r["M1"]["proportion_a"], r["M1"]["proportion_b"]), (1.0, 0.5))
        self.assertEqual((r["M1"]["niveau"], r["M4"]["niveau"], r["M2"]["niveau"]), (0.975, 0.975, 0.95))
        self.assertIn("amelioration_demontree", r["M4"])
        self.assertNotIn("amelioration_demontree", r["M2"])
        b_inverse = list(reversed(b))
        self.assertEqual(mesure.comparer(a, b_inverse, {"C1": {"p0"}, "C2": {"p0"}}, principale=True)["M1"], r["M1"])
        # Hors de l'analyse principale : tout est descriptif, à 95 %, sans conclusion
        d = mesure.comparer(a, b, {"C1": {"p0"}, "C2": {"p0"}})
        self.assertEqual(d["analyse"], "descriptive")
        self.assertTrue(all(d[m]["niveau"] == 0.95 and not d[m]["analyse_principale"]
                            and "amelioration_demontree" not in d[m] for m in ("M1", "M2", "M3", "M4", "M5")))
        self.assertEqual({k: v for k, v in d["M1"].items() if k not in ("niveau", "analyse_principale", "intervalle")},
                         {k: v for k, v in r["M1"].items()
                          if k not in ("niveau", "analyse_principale", "intervalle", "amelioration_demontree")})

    def test_designation_de_l_analyse_principale(self):
        p = mesure.est_principale
        self.assertTrue(p("mesure", "B2", "apres", "avant", "avant"))
        self.assertTrue(p("mesure", "B2", "apres", "temoin", "temoin"))
        self.assertFalse(p("calibration", "B2", "apres", "avant", "avant"))     # la calibration n'est jamais principale
        self.assertFalse(p("mesure", "B1", "apres", "avant", "avant"))          # B1 est décrit
        self.assertFalse(p("mesure", "B2", "avant", "apres", "avant"))          # sens inverse
        self.assertFalse(p("mesure", "B2", "avant", "avant", "avant"))
        self.assertFalse(p("mesure", "B2", "apres", "avant", "temoin"))         # T distinct : avant n'est que décrit
        self.assertFalse(p("mesure", "B2", "apres", "avant", None))

    def test_versions_d_ollama_differentes_refusees(self):
        q = [("H1", "hors_corpus", None, "abstention"), ("H2", "hors_corpus", None, "reponse_citee")]
        a, b = self.lignes(q), self.lignes(q)
        for l in a + b:
            l["ollama"] = {"version": "0.40.11"}
        b[1]["ollama"] = {"version": "0.40.13"}                    # une seule ligne d'une autre version suffit
        with self.assertRaisesRegex(mesure.ErreurMesure, "Versions d'Ollama différentes"):
            mesure.comparer(a, b, {})
        b[1]["ollama"] = {"version": "0.40.11"}
        self.assertEqual(mesure.comparer(a, b, {})["versions_ollama"], ["0.40.11"])

    def test_questions_differentes_refusees(self):
        a = self.lignes([("H1", "hors_corpus", None, "abstention")])
        b = self.lignes([("H2", "hors_corpus", None, "abstention")])
        with self.assertRaises(mesure.ErreurMesure):
            mesure.comparer(a, b, {})


class EchantillonTests(unittest.TestCase):
    def test_tirage_fixe_a_l_aveugle_et_cle_a_part(self):
        def lignes(n, prefixe):
            return [{"id": f"{prefixe}{i:02d}", "classe": "reponse_citee" if i % 3 else "abstention",
                     "reponse": f"r{prefixe}{i}", "passages_cites": ["p0"]} for i in range(n)]
        a, b = lignes(40, "Q"), lignes(10, "Q")
        questions = {l["id"]: f"Question {l['id']}" for l in a}
        f1, c1 = mesure.echantillon(a, b, ("avant", "apres"), questions, {"p0": "texte"})
        f2, c2 = mesure.echantillon(a, b, ("avant", "apres"), questions, {"p0": "texte"})
        self.assertEqual((f1, c1), (f2, c2))                     # graine fixe
        self.assertEqual(sum(v["phase"] == "avant" for v in c1.values()), 20)
        self.assertEqual(sum(v["phase"] == "apres" for v in c1.values()), 6)   # 6 réponses citées seulement
        self.assertTrue(all("phase" not in f and "etat" not in f for f in f1))
        self.assertEqual(f1[0]["passages_cites"], [{"passage_id": "p0", "texte": "texte"}])


class PertinenceTests(unittest.TestCase):
    def test_regle_d4_sur_les_textes_de_l_index(self):
        extrait = "Le salarié qui démissionne doit respecter un préavis fixé par la convention collective applicable."
        passages = [{"passage_id": "a", "texte": "Sans rapport avec la question posée par le salarié."},
                    {"passage_id": "b", "texte": "Règle générale. " + extrait + " Fin du passage."}]
        q = [{"id": "C1", "type": "dans_corpus", "extrait": extrait}, {"id": "H1", "type": "hors_corpus"}]
        self.assertEqual(mesure.passages_pertinents(q, passages), {"C1": {"b"}})


if __name__ == "__main__":
    unittest.main()
