"""Couche locale de la démonstration (#111) : vrai serveur HTTP local, Ollama et E5 simulés, aucune inférence."""

import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

import numpy as np

from generation import DIGEST_QWEN_31, ErreurGeneration, MODELE_QWEN
from rag import ABSTENTION, IndexCommun, RACINE
import serveur_demo
from serveur_demo import Chaine, Serveur, VERSION_CONTRAT, VERSION_OLLAMA

MAQUETTE = RACINE / "demo_b" / "public" / "maquette"
CLES_REPONSE = {"version_contrat", "question", "statut", "reponse", "citations", "citations_invalides",
                "verifications", "sources", "modele", "mesures", "erreur"}
QUESTION = "  Question de contrôle, gardée telle quelle ?"


class FauxEncodeur:
    """Assez pour que encoder_question, la vraie fonction, s'exécute sans modèle."""

    def __init__(self, nb_tokens=5):
        self.nb_tokens, self.entrees = nb_tokens, []

    def tokenizer(self, texte, truncation=False):
        return {"input_ids": list(range(self.nb_tokens))}

    def encode(self, entrees, **options):
        self.entrees += entrees
        vecteur = np.zeros((1, 384), dtype=np.float32)
        vecteur[0, 0] = 1.0
        return vecteur


def faux_index(n=6):
    matrice = np.zeros((n, 384), dtype="<f4")
    matrice[np.arange(n), np.arange(n)] = 1.0
    passages = [{"passage_id": f"p{i}", "titre_fiche": f"Fiche {i}", "section_titre": f"Section {i}", "chemin": [],
                 "articles": [], "url": f"https://exemple.test/{i}", "url_citation": f"https://exemple.test/{i}#s",
                 "date_maj": "2026-01-01", "texte": f"Texte {i}"} for i in range(n)]
    return IndexCommun({"index": {"sha256": "a" * 64}}, matrice, passages)


def generation(statut="reponse_citee", texte="Réponse [P1][P3].", citations=("[P1]", "[P3]"), invalides=(), erreurs=()):
    return {"statut": statut, "erreurs_techniques": list(erreurs), "reponse_brute": texte,
            "validation_citations": {"statut": statut, "citations": list(citations),
                                     "citations_invalides": list(invalides), "motifs": [],
                                     "justification_semantique_verifiee": False,
                                     "couverture_des_affirmations_verifiee": False},
            "ollama": {"version": VERSION_OLLAMA, "modele": MODELE_QWEN, "digest": DIGEST_QWEN_31},
            "mesures_ollama": {"done": True, "done_reason": "stop", "total_duration": 4, "load_duration": 1,
                               "prompt_eval_duration": 2, "eval_duration": 1, "prompt_eval_count": 9, "eval_count": 3}}


class BaseServeur(unittest.TestCase):
    def setUp(self):
        dossier = tempfile.TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.interface = Path(dossier.name)
        (self.interface / "index.html").write_text("<!doctype html><title>Demo</title>", encoding="utf-8")
        (self.interface / "assets").mkdir()
        (self.interface / "assets" / "app.js").write_text("export {};", encoding="utf-8")
        Path(dossier.name + "_secret.txt").write_text("hors du dossier", encoding="utf-8")
        self.addCleanup(Path(dossier.name + "_secret.txt").unlink)
        self.encodeur = FauxEncodeur()
        self.chaine = Chaine(faux_index(), self.encodeur, True, [])
        self.demarrer()
        for cible, valeur in (("_api", lambda route, *a, **k: {"version": VERSION_OLLAMA}),
                              ("verifier_ollama", lambda m, d: {"version": VERSION_OLLAMA, "modele": m, "digest": d,
                                                                "template": "gabarit"})):
            rustine = patch.object(serveur_demo, cible, valeur)
            rustine.start()
            self.addCleanup(rustine.stop)

    def demarrer(self):
        self.serveur = Serveur(self.chaine, 0, self.interface)
        fil = threading.Thread(target=self.serveur.serve_forever, daemon=True)
        fil.start()
        self.addCleanup(self.serveur.server_close)
        self.addCleanup(self.serveur.shutdown)

    def appel(self, methode, route, corps=None, entetes=None):
        connexion = http.client.HTTPConnection("127.0.0.1", self.serveur.server_address[1], timeout=10)
        self.addCleanup(connexion.close)
        connexion.request(methode, route, body=corps, headers=entetes or {})
        reponse = connexion.getresponse()
        return reponse, reponse.read()

    def question(self, question=QUESTION):
        reponse, corps = self.appel("POST", "/api/question", json.dumps({"question": question}, ensure_ascii=False).encode("utf-8"),
                                    {"Content-Type": "application/json; charset=utf-8"})
        return reponse.status, json.loads(corps)


class EtatTests(BaseServeur):
    def etat(self):
        reponse, corps = self.appel("GET", "/api/etat")
        self.assertEqual(reponse.status, 200)
        return json.loads(corps)

    def test_chaine_prete(self):
        etat = self.etat()
        self.assertEqual(etat, {
            "version_contrat": VERSION_CONTRAT, "pret": True,
            "index": {"verifie": True, "nb_passages": 6, "sha256_index": "a" * 64},
            "encodeur_charge": True, "tokeniseur_disponible": True,
            "ollama": {"joignable": True, "verifie": True, "version": VERSION_OLLAMA, "modele": MODELE_QWEN,
                       "digest": DIGEST_QWEN_31},
            "occupe": False, "message": None})

    def test_ollama_injoignable(self):
        def refuse(*a, **k):
            raise ErreurGeneration("Ollama /api/version : refusé")
        with patch.object(serveur_demo, "_api", refuse):
            etat = self.etat()
        self.assertFalse(etat["pret"])
        self.assertFalse(etat["ollama"]["joignable"])
        self.assertIn("Ollama ne répond pas", etat["message"])

    def test_modele_different_ou_version_differente(self):
        def refuse(m, d):
            raise ErreurGeneration("Digest différent")
        with patch.object(serveur_demo, "verifier_ollama", refuse):
            etat = self.etat()
        self.assertTrue(etat["ollama"]["joignable"])
        self.assertFalse(etat["ollama"]["verifie"])
        self.assertIn("Digest différent", etat["message"])
        with patch.object(serveur_demo, "verifier_ollama",
                          lambda m, d: {"version": "0.1.0", "modele": m, "digest": d}):
            etat = self.etat()
        self.assertFalse(etat["pret"])
        self.assertIn("0.1.0", etat["message"])

    def test_elements_manquants_au_demarrage(self):
        self.chaine = Chaine(None, None, False, ["Index refusé : absent", "Tokeniseur absent"])
        self.demarrer()
        etat = self.etat()
        self.assertFalse(etat["pret"])
        self.assertEqual(etat["index"], {"verifie": False, "nb_passages": None, "sha256_index": None})
        self.assertFalse(etat["encodeur_charge"])
        self.assertFalse(etat["tokeniseur_disponible"])
        self.assertIn("Index refusé", etat["message"])
        code, corps = self.question()
        self.assertEqual(code, 200)
        self.assertEqual(corps["statut"], "erreur_preparation")

    def test_modele_configure_cote_serveur(self):
        self.chaine = Chaine(faux_index(), self.encodeur, True, [], modele="adapte", digest="d" * 64)
        self.demarrer()
        self.assertEqual(self.etat()["ollama"]["digest"], "d" * 64)
        with patch.object(serveur_demo, "generer_reponse", return_value=generation()) as generer:
            self.question()
        self.assertEqual(generer.call_args.args[1:], (ABSTENTION, "adapte", "d" * 64))

    def test_version_alignee_sur_la_mesure_et_mode_hors_ligne(self):
        import mesure
        self.assertEqual(VERSION_OLLAMA, mesure.VERSION_OLLAMA)
        self.assertEqual(os.environ["HF_HUB_OFFLINE"], "1")


class QuestionTests(BaseServeur):
    def test_reponse_citee(self):
        with patch.object(serveur_demo, "generer_reponse", return_value=generation()) as generer:
            code, r = self.question()
        self.assertEqual(code, 200)
        self.assertEqual(set(r), CLES_REPONSE)
        self.assertEqual((r["statut"], r["question"], r["reponse"]), ("reponse_citee", QUESTION, "Réponse [P1][P3]."))
        self.assertEqual(self.encodeur.entrees, ["query: " + QUESTION])
        self.assertIn(QUESTION, generer.call_args.args[0]["prompt"])
        self.assertEqual([s["reference"] for s in r["sources"]], [f"[P{i}]" for i in range(1, 6)])
        self.assertEqual([s["citee"] for s in r["sources"]], [True, False, True, False, False])
        self.assertEqual([s["rang"] for s in r["sources"]], [1, 2, 3, 4, 5])
        self.assertEqual(r["sources"][0]["passage_id"], "p0")
        self.assertEqual(r["sources"][0]["score"], 1.0)
        self.assertEqual(r["modele"], {"nom": MODELE_QWEN, "digest": DIGEST_QWEN_31})
        self.assertEqual(set(r["mesures"]["ollama"]), set(serveur_demo.CHAMPS_MESURES))
        self.assertGreaterEqual(r["mesures"]["duree_totale_s"], 0)
        self.assertIsNone(r["erreur"])
        self.assertFalse(any(r["verifications"].values()))

    def test_memes_champs_que_les_reponses_de_la_maquette(self):
        """L'interface a été construite sur ces fichiers : la couche ne doit pas en différer."""
        with patch.object(serveur_demo, "generer_reponse", return_value=generation()):
            _, r = self.question()
        fichiers = list(MAQUETTE.glob("*.json"))
        reponses = [d for d in (json.loads(f.read_text(encoding="utf-8")) for f in fichiers)
                    if isinstance(d, dict) and "sources" in d]
        self.assertGreaterEqual(len(reponses), 2)
        for reference in reponses:
            self.assertEqual(CLES_REPONSE - set(reference), set())
            self.assertEqual(set(r["sources"][0]), set(reference["sources"][0]))
            self.assertEqual(set(r["mesures"]), set(reference["mesures"]) & set(r["mesures"]))
            self.assertEqual(set(r["mesures"]["ollama"]), set(reference["mesures"]["ollama"]))
            self.assertEqual(set(r["verifications"]), set(reference["verifications"]))

    def test_abstention_et_sortie_invalide(self):
        with patch.object(serveur_demo, "generer_reponse",
                          return_value=generation("abstention_modele", ABSTENTION, ())):
            _, r = self.question()
        self.assertEqual((r["statut"], r["citations"]), ("abstention_modele", []))
        self.assertEqual(len(r["sources"]), 5)
        self.assertIsNone(r["erreur"])
        with patch.object(serveur_demo, "generer_reponse",
                          return_value=generation("sortie_invalide", "Faux [P9]", (), ["[P9]"])):
            _, r = self.question()
        self.assertEqual((r["statut"], r["citations_invalides"]), ("sortie_invalide", ["[P9]"]))
        self.assertIsNone(r["erreur"])

    def test_erreur_technique_garde_reponse_et_sources(self):
        retour = generation("erreur_technique", "Coupé [P1]", ("[P1]",),
                            erreurs=("generation_incomplete", "nombre_tokens_sortie_invalide"))
        with patch.object(serveur_demo, "generer_reponse", return_value=retour):
            code, r = self.question()
        self.assertEqual((code, r["statut"], r["reponse"]), (200, "erreur_technique", "Coupé [P1]"))
        self.assertEqual(r["erreur"], {"type": "erreur_technique",
                                       "message": "generation_incomplete, nombre_tokens_sortie_invalide"})
        self.assertEqual(len(r["sources"]), 5)

    def test_erreur_preparation_generation_garde_les_sources(self):
        with patch.object(serveur_demo, "generer_reponse", side_effect=ErreurGeneration("Budget dépassé")):
            code, r = self.question()
        self.assertEqual((code, r["statut"]), (200, "erreur_preparation"))
        self.assertEqual(set(r), CLES_REPONSE)
        self.assertEqual(r["erreur"], {"type": "ErreurGeneration", "message": "Budget dépassé"})
        self.assertEqual(len(r["sources"]), 5)
        self.assertIsNone(r["reponse"])
        self.assertIsNone(r["modele"])
        self.assertIsNone(r["mesures"]["ollama"])
        self.assertEqual((r["citations"], r["citations_invalides"]), ([], []))
        self.assertFalse(any(r["verifications"].values()))

    def test_question_trop_longue_pour_e5(self):
        self.encodeur.nb_tokens = 513
        with patch.object(serveur_demo, "generer_reponse") as generer:
            code, r = self.question()
        generer.assert_not_called()
        self.assertEqual((code, r["statut"], r["sources"]), (200, "erreur_preparation", []))
        self.assertEqual(r["erreur"]["type"], "ErreurRecuperation")

    def test_version_ollama_differente_ne_genere_pas(self):
        with patch.object(serveur_demo, "_api", lambda *a, **k: {"version": "0.1.0"}), \
                patch.object(serveur_demo, "generer_reponse") as generer:
            _, r = self.question()
        generer.assert_not_called()
        self.assertEqual(r["statut"], "erreur_preparation")
        self.assertEqual(len(r["sources"]), 5)

    def test_requetes_invalides(self):
        json_utf8 = {"Content-Type": "application/json"}
        for corps, entetes in ((b"pas du json", json_utf8), (b"[]", json_utf8), (b"{}", json_utf8),
                               (b'{"question": 3}', json_utf8), (b'{"question": "  \\n "}', json_utf8),
                               (b'\xff\xfe', json_utf8), (b'{"question": "ok"}', {"Content-Type": "text/plain"}),
                               (b"x" * (serveur_demo.TAILLE_MAX_CORPS + 1), json_utf8)):
            reponse, retour = self.appel("POST", "/api/question", corps, entetes)
            self.assertEqual(reponse.status, 400, corps[:30])
            retour = json.loads(retour)
            self.assertEqual(set(retour), {"version_contrat", "erreur"})
            self.assertEqual(retour["erreur"]["type"], "requete_invalide")

    def test_question_concurrente_refusee(self):
        commence, libere = threading.Event(), threading.Event()

        def lente(*a, **k):
            commence.set()
            self.assertTrue(libere.wait(5))
            return generation()
        resultats = []
        with patch.object(serveur_demo, "generer_reponse", lente):
            fil = threading.Thread(target=lambda: resultats.append(self.question()))
            fil.start()
            self.assertTrue(commence.wait(5))
            code, r = self.question()
            self.assertEqual(code, 409)
            self.assertEqual(r["erreur"]["type"], "occupe")
            self.assertTrue(json.loads(self.appel("GET", "/api/etat")[1])["occupe"])
            libere.set()
            fil.join(5)
            self.assertEqual(resultats[0][0], 200)
            self.assertFalse(json.loads(self.appel("GET", "/api/etat")[1])["occupe"])
            self.assertEqual(self.question()[0], 200)

    def test_defaut_inattendu_libere_le_verrou(self):
        with patch.object(serveur_demo, "generer_reponse", side_effect=RuntimeError("inattendu")), \
                patch("serveur_demo.traceback.print_exc"):
            code, r = self.question()
        self.assertEqual((code, r["erreur"]["type"]), (500, "erreur_interne"))
        with patch.object(serveur_demo, "generer_reponse", return_value=generation()):
            self.assertEqual(self.question()[0], 200)


class FichiersTests(BaseServeur):
    def test_interface_servie(self):
        reponse, corps = self.appel("GET", "/")
        self.assertEqual((reponse.status, reponse.getheader("Content-Type")), (200, "text/html"))
        self.assertIn(b"Demo", corps)
        reponse, _ = self.appel("GET", "/assets/app.js")
        self.assertEqual((reponse.status, reponse.getheader("Content-Type")), (200, "text/javascript"))

    def test_rien_hors_du_dossier_ni_liste(self):
        nom = self.interface.name + "_secret.txt"
        for route in (f"/../{nom}", f"/..%2f{nom}", f"/%2e%2e/{nom}", "/assets/"):
            reponse, corps = self.appel("GET", route)
            self.assertEqual(reponse.status, 404, route)
            self.assertNotIn(b"hors du dossier", corps)

    def test_routes_inconnues(self):
        self.assertEqual(self.appel("GET", "/api/autre")[0].status, 404)
        self.assertEqual(self.appel("POST", "/autre", b"{}", {"Content-Type": "application/json"})[0].status, 404)

    def test_ecoute_seulement_en_local(self):
        self.assertEqual(self.serveur.server_address[0], "127.0.0.1")


if __name__ == "__main__":
    unittest.main()
