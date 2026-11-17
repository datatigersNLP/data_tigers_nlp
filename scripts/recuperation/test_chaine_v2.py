"""Tests de la chaîne v2 (#163), sans modèle de langage et sans question du lot de test.

Lancement, depuis la racine du dépôt : python scripts/recuperation/test_chaine_v2.py
Le test de bout en bout lit l'index du site et le lot de calibration (comme test_mesure.py), avec un générateur factice.
"""

import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import unittest.mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chaine_v2 as cv  # noqa: E402
import mesure  # noqa: E402
import rag  # noqa: E402
import recuperation as rc  # noqa: E402


def passages_factices(n=12):
    return [{"passage_id": f"m2-x-{i:04d}", "titre_fiche": f"Fiche {i}", "section_titre": "Section", "chemin": [],
             "url": f"https://exemple/{i}", "url_citation": f"https://exemple/{i}#c", "date_maj": "2026-09-11",
             "texte": f"Texte du passage {i}."} for i in range(n)]


class TestConsigne(unittest.TestCase):
    def test_abstention_identique_et_finale(self):
        self.assertEqual(cv.CONSIGNE_V2.count(rag.ABSTENTION), 1)
        self.assertTrue(cv.CONSIGNE_V2.endswith(rag.ABSTENTION))
        self.assertEqual(cv.CONSIGNE_V2.split("\n")[-1], rag.ABSTENTION)

    def test_seules_brievete_et_regle_d_abstention_changent(self):
        v1, v2 = rag.CONSIGNE_RAG.split("\n"), cv.CONSIGNE_V2.split("\n")
        self.assertNotIn("brièvement", cv.CONSIGNE_V2)
        retirees = [l for l in v1 if l not in v2]
        ajoutees = [l for l in v2 if l not in v1]
        self.assertEqual(len(retirees), 2, retirees)
        self.assertTrue(retirees[0].startswith("Réponds brièvement"))
        self.assertTrue(retirees[1].startswith("Si les passages ne permettent pas"))
        self.assertEqual(len(ajoutees), 3, ajoutees)
        # les consignes de citation sont reprises mot pour mot
        for l in v1:
            if "[P1]" in l or "identifiants" in l or "N'invente" in l:
                self.assertIn(l, v2)

    def test_longueur_bornee_sous_num_predict(self):
        self.assertIn("200 mots au plus", cv.CONSIGNE_V2)

    def test_protocole_reprend_la_consigne_exacte(self):
        texte = cv.PROTOCOLE_08.read_text(encoding="utf-8")
        bloc = texte.split("Texte exact :\n\n```\n", 1)[1].split("\n```", 1)[0]
        self.assertEqual(bloc, cv.CONSIGNE_V2)


class TestSeuils(unittest.TestCase):
    def test_centile_lineaire_comme_seuil_b2(self):
        self.assertEqual(cv.centile(np.arange(21.0)), 1.0)
        self.assertAlmostEqual(cv.centile([0.0, 10.0, 20.0, 30.0]), 1.5)
        with self.assertRaises(cv.ErreurChaineV2):
            cv.centile([])
        with self.assertRaises(cv.ErreurChaineV2):
            cv.centile([0.1, float("nan")])

    def test_v1_compare_e5_a_s_et_v2_le_reclasseur_a_tau(self):
        self.assertEqual(cv.abstenir("V1", 0.80, 9.0, 0.85, 0.1)[0], True)
        self.assertEqual(cv.abstenir("V1", 0.90, -9.0, 0.85, 0.1)[0], False)
        self.assertEqual(cv.abstenir("V2", 0.10, 0.05, 0.85, 0.1)[0], True)
        self.assertEqual(cv.abstenir("V2", 0.10, 0.50, 0.85, 0.1)[0], False)

    def test_inegalite_stricte_et_signalement(self):
        sous, proche, seuil = cv.abstenir("V2", 0.0, 0.1, 0.85, 0.1)
        self.assertEqual((sous, proche, seuil), (False, True, 0.1))
        with self.assertRaises(cv.ErreurChaineV2):
            cv.abstenir("B2", 0.0, 0.0, 0.0, 0.0)


class TestContexte(unittest.TestCase):
    def test_v1_est_le_contexte_v2_confirme_et_v2_ne_change_que_la_consigne(self):
        p = passages_factices()
        base = rc.construire_contexte_v2("Question ?", [3, 1, 7], p)
        v1 = cv.contexte_etat("V1", "Question ?", [3, 1, 7], p)
        v2 = cv.contexte_etat("V2", "Question ?", [3, 1, 7], p)
        self.assertEqual(v1, base)
        self.assertEqual(v1["system"], rag.CONSIGNE_RAG)
        self.assertEqual(v2["system"], cv.CONSIGNE_V2)
        self.assertEqual({k: v for k, v in v2.items() if k != "system"}, {k: v for k, v in v1.items() if k != "system"})

    def test_preparees_par_etat(self):
        p = passages_factices()
        questions = [{"id": "Q1", "type": "dans_corpus", "fiche": "f", "question": "A ?"},
                     {"id": "Q2", "type": "hors_corpus", "fiche": None, "question": "B ?"}]
        contextes = [{"id": "Q1", "contexte": [0, 1], "score_e5_max": 0.90, "score_reclasseur_max": 0.02},
                     {"id": "Q2", "contexte": [2], "score_e5_max": 0.80, "score_reclasseur_max": 0.70}]
        v1 = cv.preparees_etat("V1", questions, contextes, p, seuil_s=0.85, tau=0.1)
        v2 = cv.preparees_etat("V2", questions, contextes, p, seuil_s=0.85, tau=0.1)
        self.assertEqual([q["sous_le_seuil"] for q in v1], [False, True])
        self.assertEqual([q["sous_le_seuil"] for q in v2], [True, False])
        self.assertEqual([r["passage"]["passage_id"] for r in v1[0]["resultats"]], ["m2-x-0000", "m2-x-0001"])
        with self.assertRaises(cv.ErreurChaineV2):
            cv.preparees_etat("V1", questions[:1], contextes, p, 0.85, 0.1)


class TestGel(unittest.TestCase):
    def test_lot_de_test_refuse_tant_que_le_protocole_n_est_pas_fige(self):
        with unittest.mock.patch.object(cv, "SHA256_PROTOCOLE_08", None):
            with self.assertRaises(cv.ErreurChaineV2):
                cv.verifier_gel("test")
        self.assertEqual(cv.verifier_gel("calibration"), {"protocole_08": None})

    def test_lot_de_test_refuse_si_le_protocole_a_change(self):
        with unittest.mock.patch.object(cv, "SHA256_PROTOCOLE_08", "0" * 64), \
                unittest.mock.patch.object(cv, "SHA256_TAU", "0" * 64):
            with self.assertRaises(cv.ErreurChaineV2):
                cv.verifier_gel("test")


class TestControleConfirmation(unittest.TestCase):
    def test_conforme_et_ecart(self):
        extrait = ("le salarié a droit à un congé de naissance de trois jours ouvrables, "
                   "accordé par l'employeur sans condition d'ancienneté")
        textes = ["alpha " * 30, "Début du passage. " + extrait + ". Fin du passage.", "gamma " * 30]
        questions = [{"id": "Q1", "type": "dans_corpus", "extrait": extrait},
                     {"id": "Q2", "type": "hors_corpus", "extrait": None}]
        lignes = [{"contexte": [1, 2], "tokens": 1000}, {"contexte": [0], "tokens": 900}]
        with tempfile.TemporaryDirectory() as d:
            chemin = Path(d) / "questions.csv"
            with open(chemin, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["question", "succes_v2", "tokens_v2"])
                w.writeheader()
                w.writerow({"question": "Q1", "succes_v2": 1, "tokens_v2": 1000})
            with unittest.mock.patch.object(cv, "CONFIRMATION", chemin):
                r = cv.controle_confirmation(lignes, questions, textes)
                self.assertEqual(r["ecarts"], [])
                self.assertFalse(r["conforme"])        # 73 questions publiées attendues
                lignes[0]["tokens"] = 999
                self.assertEqual(len(cv.controle_confirmation(lignes, questions, textes)["ecarts"]), 1)


class TestAnalyse(unittest.TestCase):
    def test_decomposition_et_reetiquetage(self):
        pertinents = {"Q1": {"p1"}, "Q2": {"p9"}, "Q3": {"p5"}}
        lignes = [
            {"id": "Q1", "type": "dans_corpus", "classe": "reponse_citee", "passages": ["p1", "p2"], "passages_cites": ["p1"], "appel_modele": True},
            {"id": "Q2", "type": "dans_corpus", "classe": "abstention", "passages": ["p3"], "passages_cites": [], "appel_modele": False},
            {"id": "Q3", "type": "dans_corpus", "classe": "reponse_citee", "passages": ["p5", "p6"], "passages_cites": ["p6"], "appel_modele": True},
            {"id": "Q4", "type": "hors_corpus", "classe": "abstention", "passages": ["p7"], "passages_cites": [], "appel_modele": True},
        ]
        self.assertEqual(cv.decomposition(lignes, pertinents),
                         {"pertinent_fourni": {"M4": 1, "citee_non_pertinente": 1}, "aucun_pertinent": {"abstention_seuil": 1}})
        self.assertEqual({l["etat"] for l in cv.meme_etiquette([{"etat": "V1"}, {"etat": "B2"}])}, {"comparaison"})


class TestExecutionFactice(unittest.TestCase):
    """De bout en bout sur le lot de calibration, avec un générateur factice qui cite toujours [P1]."""

    def test_executer_calibration(self):
        index = rag.charger_index()
        questions = mesure.lire_jeu("calibration")
        appels = []

        def generer(contexte, abstention, modele, digest):
            appels.append(contexte["system"])
            return {"statut": "reponse_citee", "erreurs_techniques": [], "reponse_brute": "Réponse [P1].",
                    "validation_citations": {"statut": "reponse_citee", "citations": ["[P1]"], "motifs": []},
                    "ollama": {"version": mesure.VERSION_OLLAMA}, "entree": {"nb_tokens": 10, "sha256_texte": "x"},
                    "mesures_ollama": {"eval_count": 3}}

        with tempfile.TemporaryDirectory() as d:
            sorties = Path(d)
            tau_fichier = sorties / "seuil_reclasseur.json"
            tau_fichier.write_text(json.dumps({"seuil": 0.5}), encoding="utf-8")
            sha_tau = hashlib.sha256(tau_fichier.read_bytes()).hexdigest()
            contextes = [{"id": q["id"], "contexte": [0, 1, 2], "score_e5_max": 0.99,
                          "score_reclasseur_max": 0.1 if q["type"] == "hors_corpus" else 0.9} for q in questions]
            (sorties / "calibration").mkdir()
            (sorties / "calibration" / "contextes.json").write_text(json.dumps(
                {"seuil_reclasseur_sha256": sha_tau, "protocole_08": None, "questions": contextes}), encoding="utf-8")
            with unittest.mock.patch.object(cv, "FICHIER_TAU", tau_fichier):
                chemin = cv.executer("calibration", "temoin", "V2", "modele", "digest", generer=generer, sorties=sorties)
                lignes = mesure.lire_etat(chemin)
                self.assertEqual(len(lignes), len(questions))
                self.assertEqual({l["etat"] for l in lignes}, {"V2"})
                hors = [l for l in lignes if l["type"] == "hors_corpus"]
                self.assertTrue(all(l["classe"] == "abstention" and not l["appel_modele"] for l in hors))
                self.assertEqual(len(appels), len(questions) - len(hors))
                self.assertTrue(all(s == cv.CONSIGNE_V2 for s in appels))
                self.assertTrue(all(len(l["passages"]) == 3 for l in lignes))
                appels_avant = len(appels)
                with self.assertRaises(cv.ErreurChaineV2):        # une seule exécution par état et par phase
                    cv.executer("calibration", "temoin", "V2", "modele", "digest", generer=generer, sorties=sorties)
                self.assertEqual(len(appels), appels_avant)       # refus avant tout appel au générateur (#166)
        self.assertEqual(index.matrice.shape[0], 4240)


class TestGardesDeLAnalyse(unittest.TestCase):
    """Revue de la #166 : l'analyse contrôle le gel et le verrou avant de lire le jeu."""

    def test_gel_controle_avant_lecture(self):
        with unittest.mock.patch.object(cv, "verifier_gel", side_effect=cv.ErreurChaineV2("gel")), \
                unittest.mock.patch.object(mesure, "lire_jeu") as lire_jeu, tempfile.TemporaryDirectory() as d:
            with self.assertRaises(cv.ErreurChaineV2):
                cv.analyser("test", sorties=Path(d))
            lire_jeu.assert_not_called()

    def test_verrou_controle_avant_lecture(self):
        with unittest.mock.patch.object(cv, "verifier_gel", return_value={}), \
                unittest.mock.patch.object(cv, "verifier_verrou_chaine", side_effect=cv.ErreurChaineV2("verrou")), \
                unittest.mock.patch.object(mesure, "lire_jeu") as lire_jeu, tempfile.TemporaryDirectory() as d:
            with self.assertRaises(cv.ErreurChaineV2):
                cv.analyser("test", sorties=Path(d))
            lire_jeu.assert_not_called()


if __name__ == "__main__":
    unittest.main()
