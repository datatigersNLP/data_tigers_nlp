"""Couche locale de la démonstration, chaîne v2 (#172) : vrai serveur HTTP local, récupération et Ollama simulés.

Lancement, depuis la racine du dépôt : python scripts/rag/test_serveur_demo_v2.py
Les garanties communes (routes, verrou, fichiers servis, écoute locale) sont celles de test_serveur_demo.py : la chaîne
v2 n'en redéfinit aucune. Ces tests couvrent ce qui change : l'état décrit la chaîne, la récupération donne les sources
dans l'ordre du reclasseur, le score affiché est celui de la partie dense, la consigne reste la v1.
"""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import serveur_demo_v2 as v2  # noqa: E402  (ajoute scripts/recuperation au chemin)
import rag  # noqa: E402
import recuperation as rc  # noqa: E402
import serveur_demo  # noqa: E402
import test_serveur_demo as tsd  # noqa: E402

CONTEXTE = [7, 2, 11, 0, 5, 9, 1, 3, 10, 4]   # ordre du reclasseur simulé : pas celui des scores denses
DESCRIPTION = {"etat": "R2", "configuration": "rrf+k10+bge-m3@20", "dense": "E5 ajusté v1", "seuil_S": None}


class FausseRecuperation:
    def __init__(self, erreur=None):
        self.description, self.erreur, self.questions = DESCRIPTION, erreur, []
        self.scores = np.linspace(0.9, 0.79, 12).astype(np.float32)

    def recuperer(self, question):
        self.questions.append(question)
        if self.erreur:
            raise self.erreur
        return {"contexte": list(CONTEXTE), "scores_denses": self.scores, "score_dense_max": 0.9,
                "candidats": list(range(12)), "scores_reclasseur": [0.0] * 12, "groupes_retires": 0, "tokens": 1}


class BaseV2(tsd.BaseServeur):
    def setUp(self):
        super().setUp()           # interface temporaire, Ollama simulé ; la chaîne de B2 est remplacée ci-dessous
        self.recup = FausseRecuperation()
        self.chaine = v2.ChaineV2(tsd.faux_index(12), self.recup, True, [])
        self.demarrer()

    def etat(self):
        reponse, corps = self.appel("GET", "/api/etat")
        self.assertEqual(reponse.status, 200)
        return json.loads(corps)


class EtatV2Tests(BaseV2):
    def test_etat_decrit_la_chaine(self):
        etat = self.etat()
        self.assertTrue(etat["pret"])
        self.assertEqual(etat["chaine"], DESCRIPTION)
        self.assertTrue(etat["encodeur_charge"])
        self.assertEqual(etat["index"]["nb_passages"], 12)

    def test_recuperation_absente(self):
        self.chaine = v2.ChaineV2(tsd.faux_index(12), None, False, ["Récupération v2 indisponible : test"])
        self.demarrer()
        etat = self.etat()
        self.assertFalse(etat["pret"])
        self.assertIsNone(etat["chaine"])
        self.assertIn("Récupération v2 indisponible", etat["message"])
        with patch.object(serveur_demo, "generer_reponse") as generer:
            code, r = self.question()
        generer.assert_not_called()
        self.assertEqual((code, r["statut"], r["erreur"]["type"]), (200, "erreur_preparation", "ErreurRecuperation"))

    def test_chargement_en_echec_ne_bloque_pas_la_couche(self):
        faux = rag.IndexCommun({"index": {"sha256": "a" * 64}}, np.eye(3, 384, dtype="<f4"), [])
        with patch.object(v2.rag, "charger_index", return_value=faux), \
                patch.object(v2.rd.RecuperationDemo, "charger", side_effect=OSError("bge-m3 absent du cache")):
            chaine = v2.ChaineV2.charger_v2("ajuste")
        self.assertIsNone(chaine.recuperation)
        self.assertFalse(chaine.tokeniseur_disponible)
        self.assertIn("bge-m3 absent du cache", chaine.causes[0])


class QuestionV2Tests(BaseV2):
    def test_sources_dans_l_ordre_du_reclasseur_avec_le_score_dense(self):
        with patch.object(serveur_demo, "generer_reponse", return_value=tsd.generation()) as generer:
            code, r = self.question()
        self.assertEqual((code, r["statut"]), (200, "reponse_citee"))
        self.assertEqual(set(r), tsd.CLES_REPONSE)
        self.assertEqual(self.recup.questions, [tsd.QUESTION])                       # question gardée mot pour mot
        self.assertEqual([s["passage_id"] for s in r["sources"]], [f"p{i}" for i in CONTEXTE])
        self.assertEqual([s["rang"] for s in r["sources"]], list(range(1, 11)))
        self.assertEqual([s["reference"] for s in r["sources"]], [f"[P{i}]" for i in range(1, 11)])
        self.assertEqual([s["score"] for s in r["sources"]], [float(self.recup.scores[i]) for i in CONTEXTE])
        self.assertEqual([s["citee"] for s in r["sources"]][:3], [True, False, True])
        contexte = generer.call_args.args[0]
        self.assertEqual(contexte["system"], rag.CONSIGNE_RAG)                        # consigne v1
        self.assertIn(tsd.QUESTION, contexte["prompt"])
        self.assertIn("[P10]\nFiche : Fiche 4", contexte["prompt"])
        self.assertEqual(generer.call_args.args[1:], (rag.ABSTENTION, self.chaine.modele, self.chaine.digest))

    def test_erreur_de_recuperation_sans_generation(self):
        self.recup.erreur = rc.ErreurRecuperationV2("Scores du reclasseur manquants")
        with patch.object(serveur_demo, "generer_reponse") as generer:
            code, r = self.question()
        generer.assert_not_called()
        self.assertEqual((code, r["statut"], r["sources"]), (200, "erreur_preparation", []))
        self.assertEqual(r["erreur"], {"type": "ErreurRecuperationV2", "message": "Scores du reclasseur manquants"})

    def test_question_trop_longue(self):
        self.recup.erreur = rag.ErreurRecuperation("Question de 600 tokens, limite 512")
        with patch.object(serveur_demo, "generer_reponse") as generer:
            _, r = self.question()
        generer.assert_not_called()
        self.assertEqual(r["erreur"]["type"], "ErreurRecuperation")

    def test_version_ollama_differente_ne_genere_pas(self):
        with patch.object(serveur_demo, "_api", lambda *a, **k: {"version": "0.1.0"}), \
                patch.object(serveur_demo, "generer_reponse") as generer:
            _, r = self.question()
        generer.assert_not_called()
        self.assertEqual(r["statut"], "erreur_preparation")
        self.assertEqual(len(r["sources"]), 10)


class LigneDeCommandeTests(unittest.TestCase):
    def test_modele_et_digest_ensemble(self):
        with self.assertRaises(SystemExit), patch("sys.stderr"):
            v2.main(["--modele", "adapte"])

    def test_r1_par_defaut(self):
        with patch.object(v2.ChaineV2, "charger_v2", side_effect=RuntimeError("arrêt du test")) as charger, \
                patch("sys.stderr"), self.assertRaises(RuntimeError):
            v2.main([])
        self.assertEqual(charger.call_args.args[0], "base")      # règle de maintien du protocole 10 : R1

    def test_partie_dense_connue(self):
        with self.assertRaises(SystemExit), patch("sys.stderr"):
            v2.main(["--dense", "autre"])


if __name__ == "__main__":
    unittest.main()
