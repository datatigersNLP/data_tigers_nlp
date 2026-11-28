"""Tests d'intégrité sans modèle et sans questions d'évaluation (#51)."""

import copy
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np

from rag import (ErreurIndex, ErreurRecuperation, IndexCommun, JEU_COMMIT,
                 ABSTENTION, MODELE_E5, REVISION_E5, charger_encodeur, charger_index, construire_contexte,
                 encoder_question, lire_question_calibration, main, recuperer_passages)


class LectureIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dossier = Path(self.temp.name)
        self.matrice = np.eye(2, 384, dtype="<f4")
        # Documents artificiels : aucun nouvel exemple d'évaluation n'est créé.
        self.passages = [dict(
            passage_id=f"fixture-{i}", titre_fiche="Fiche technique",
            section_titre="Section", chemin=[], url="https://example.org/fiche",
            url_citation="https://example.org/fiche#section", date_maj="2026-10-18",
            texte=f"Document artificiel {i} pour le contrôle des fichiers.", articles=[],
        ) for i in range(2)]
        self.entete = {
            "format": "index-e5-v1",
            # Même situation que le site actuel : le modèle q8 du navigateur
            # n'est pas le moteur qui a produit la matrice de référence fp32.
            "modele": {"emplacement": "site", "depot": "modele-q8", "dtype": "q8"},
            "index": {"fichier": "index_m2.f32", "type": "float32",
                      "ordre_octets": "little-endian", "disposition": "ligne par ligne",
                      "nb_vecteurs": 2, "dimension": 384,
                      "moteur": "PyTorch fp32 (intfloat/multilingual-e5-small)"},
            "metadonnees": {"fichier": "passages_m2.json", "nb_passages": 2},
            "source": {"decoupage": "m2"},
            "requete": {"prefixe": "query: ", "pooling": "mean", "normalize": True},
        }
        self.ecrire_export()

    def ecrire_entete(self):
        (self.dossier / "index_m2.json").write_text(
            json.dumps(self.entete, ensure_ascii=False), encoding="utf-8")

    def ecrire_export(self):
        for description, octets in (
            (self.entete["index"], self.matrice.tobytes()),
            (self.entete["metadonnees"], json.dumps(self.passages, ensure_ascii=False).encode()),
        ):
            (self.dossier / description["fichier"]).write_bytes(octets)
            description["sha256"] = hashlib.sha256(octets).hexdigest()
        self.ecrire_entete()

    def test_export_valide_conserve_ordre_texte_et_matrice(self):
        index = charger_index(self.dossier)
        self.assertEqual(index.passages, self.passages)
        np.testing.assert_array_equal(index.matrice, self.matrice)
        self.assertFalse(index.matrice.flags.writeable)
        with self.assertRaises(ValueError):
            index.matrice[0, 0] = 0

    def test_fichier_absent(self):
        (self.dossier / "index_m2.f32").unlink()
        with self.assertRaisesRegex(ErreurIndex, "Lecture impossible"):
            charger_index(self.dossier)

    def test_octet_matrice_altere(self):
        chemin = self.dossier / "index_m2.f32"
        octets = bytearray(chemin.read_bytes())
        octets[0] ^= 1
        chemin.write_bytes(octets)
        with self.assertRaisesRegex(ErreurIndex, "empreinte différente"):
            charger_index(self.dossier)

    def test_passages_reordonnes_sans_manifeste_correspondant(self):
        (self.dossier / "passages_m2.json").write_text(
            json.dumps(self.passages[::-1], ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(ErreurIndex, "empreinte différente"):
            charger_index(self.dossier)

    def test_matrice_tronquee_meme_avec_empreinte_recalculee(self):
        chemin = self.dossier / "index_m2.f32"
        octets = chemin.read_bytes()[:-1]
        chemin.write_bytes(octets)
        self.entete["index"]["sha256"] = hashlib.sha256(octets).hexdigest()
        self.ecrire_entete()
        with self.assertRaisesRegex(ErreurIndex, "Taille de matrice"):
            charger_index(self.dossier)

    def test_nan_et_inf_refuses(self):
        for valeur in (np.nan, np.inf, -np.inf):
            with self.subTest(valeur=valeur):
                self.matrice[0, 0] = valeur
                self.ecrire_export()
                with self.assertRaisesRegex(ErreurIndex, "non finies"):
                    charger_index(self.dossier)

    def test_vecteurs_nuls_et_non_normalises(self):
        for valeur in (0, 2):
            with self.subTest(valeur=valeur):
                self.matrice[0, 0] = valeur
                self.ecrire_export()
                with self.assertRaisesRegex(ErreurIndex, "pas normalisés"):
                    charger_index(self.dossier)

    def test_identifiant_duplique(self):
        self.passages[1]["passage_id"] = self.passages[0]["passage_id"]
        self.ecrire_export()
        with self.assertRaisesRegex(ErreurIndex, "dupliqué"):
            charger_index(self.dossier)

    def test_texte_vide(self):
        self.passages[0]["texte"] = "  \n"
        self.ecrire_export()
        with self.assertRaisesRegex(ErreurIndex, "texte vide"):
            charger_index(self.dossier)

    def test_schema_metadonnees_incomplet_ou_invalide(self):
        original = copy.deepcopy(self.passages)
        for champ, valeur in (("url", None), ("chemin", "Section"), ("articles", [3])):
            with self.subTest(champ=champ):
                self.passages = copy.deepcopy(original)
                self.passages[0][champ] = valeur
                self.ecrire_export()
                with self.assertRaisesRegex(ErreurIndex, champ):
                    charger_index(self.dossier)

    def test_nombre_reel_de_passages_incorrect(self):
        self.passages.pop()
        self.ecrire_export()
        with self.assertRaisesRegex(ErreurIndex, "contenir 2 objets"):
            charger_index(self.dossier)

    def test_entete_incompatible(self):
        original = copy.deepcopy(self.entete)
        cas = [
            ("format", None, "autre-format"),
            ("index", "dimension", 383),
            ("index", "nb_vecteurs", True),
            ("metadonnees", "nb_passages", 3),
            ("index", "type", "float64"),
            ("index", "ordre_octets", "big-endian"),
            ("index", "disposition", "colonne par colonne"),
            ("index", "moteur", "ONNX q8"),
            ("source", "decoupage", "m1"),
            ("requete", "prefixe", "passage: "),
            ("requete", "normalize", False),
            ("requete", "pooling", "cls"),
        ]
        for bloc, cle, valeur in cas:
            with self.subTest(bloc=bloc, cle=cle):
                self.entete = copy.deepcopy(original)
                if cle is None:
                    self.entete[bloc] = valeur
                else:
                    self.entete[bloc][cle] = valeur
                self.ecrire_entete()
                with self.assertRaises(ErreurIndex):
                    charger_index(self.dossier)

    def test_chemins_hors_dossier_refuses(self):
        for nom in ("../index.f32", "sous/index.f32", "..\\index.f32", "/tmp/index.f32"):
            with self.subTest(nom=nom):
                self.entete["index"]["fichier"] = nom
                self.ecrire_entete()
                with self.assertRaisesRegex(ErreurIndex, "dossier d'index"):
                    charger_index(self.dossier)

    def test_json_invalide_meme_avec_empreinte_recalculee(self):
        for octets in (b"{", b"\xff"):
            with self.subTest(octets=octets):
                (self.dossier / "passages_m2.json").write_bytes(octets)
                self.entete["metadonnees"]["sha256"] = hashlib.sha256(octets).hexdigest()
                self.ecrire_entete()
                with self.assertRaisesRegex(ErreurIndex, "JSON UTF-8 invalide"):
                    charger_index(self.dossier)

    def test_cli_succes_et_echec_depuis_un_autre_dossier(self):
        commande = [sys.executable, str(Path(__file__).with_name("rag.py").resolve()),
                    "--check-index", "--index-dir", str(self.dossier)]
        resultat = subprocess.run(commande, cwd=self.dossier, capture_output=True, text=True)
        self.assertEqual(resultat.returncode, 0, resultat.stderr)
        sortie = json.loads(resultat.stdout)
        self.assertEqual(sortie["nb_passages"], 2)
        self.assertFalse(sortie["e5_charge"])
        self.assertFalse(sortie["ollama_appele"])
        (self.dossier / "index_m2.f32").unlink()
        resultat = subprocess.run(commande, capture_output=True, text=True)
        self.assertEqual(resultat.returncode, 1)
        self.assertIn("Index refusé", resultat.stderr)

    def test_cli_sauvegarde_utf8_sans_ecrasement(self):
        cible = self.dossier / "traces" / "controle.json"
        commande = [sys.executable, str(Path(__file__).with_name("rag.py").resolve()),
                    "--check-index", "--index-dir", str(self.dossier), "--output", str(cible)]
        resultat = subprocess.run(commande, capture_output=True, text=True)
        self.assertEqual(resultat.returncode, 0, resultat.stderr)
        octets = cible.read_bytes()
        self.assertEqual(json.loads(octets.decode("utf-8"))["statut"], "index_verifie")
        resultat = subprocess.run(commande, capture_output=True, text=True)
        self.assertEqual(resultat.returncode, 2)
        self.assertEqual(cible.read_bytes(), octets)


class RecuperationTests(unittest.TestCase):
    """Calcul contrôlé et doubles de test : aucune inférence E5 réelle."""

    def setUp(self):
        self.question_humaine = "Quelles sont les obligations légales de l'empoyeur en période de forte chaleur ?"
        self.vecteur = np.eye(1, 384, dtype=np.float32)[0]
        matrice = np.eye(6, 384, dtype=np.float32)
        # Trois scores identiques en tête : le tri doit garder l'ordre des lignes.
        matrice[1] = matrice[0]
        matrice[2] = matrice[0]
        self.index = IndexCommun({}, matrice, [{"passage_id": f"fixture-{i}", "texte": f"Document {i}"}
                                             for i in range(6)])
        self.modele = Mock()
        self.modele.tokenizer.return_value = {"input_ids": [0, 1, 2]}
        self.modele.encode.return_value = self.vecteur[None, :]

    def csv_humain(self, lot="calibration"):
        # Texte existant de Q036, copié mot pour mot, dans un CSV temporaire simulé.
        return ("id,lot,type,question\nQ036," + lot + ",dans_corpus,"
                + self.question_humaine + "\n").encode("utf-8")

    @patch("rag.subprocess.run")
    def test_lecture_au_commit_fige_sans_reformulation(self, git):
        git.return_value.stdout = self.csv_humain()
        q = lire_question_calibration("Q036")
        self.assertEqual(q["question"], self.question_humaine)
        self.assertEqual(q["commit_jeu"], JEU_COMMIT)
        self.assertNotIn("url", q)
        self.assertNotIn("extrait", q)
        self.assertIn(JEU_COMMIT + ":evaluation/questions/questions_annotees.csv", git.call_args.args[0])

    @patch("rag.subprocess.run")
    def test_lot_test_refuse_avant_chargement_modele(self, git):
        git.return_value.stdout = self.csv_humain(lot="test")
        with patch("rag.charger_encodeur") as charger, redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--retrieve-only", "--question-id", "Q036"]), 1)
            charger.assert_not_called()

    @patch("rag.subprocess.run")
    def test_question_absente_ou_commit_indisponible(self, git):
        git.return_value.stdout = self.csv_humain()
        with self.assertRaisesRegex(ErreurRecuperation, "absente"):
            lire_question_calibration("Q003")
        git.side_effect = subprocess.CalledProcessError(128, ["git"])
        with self.assertRaisesRegex(ErreurRecuperation, "Jeu figé indisponible"):
            lire_question_calibration("Q036")

    def test_chargement_reference_revision_cpu_fp32(self):
        # Le double vérifie le contrat ; ce test ne télécharge pas le modèle.
        classe = Mock(return_value=self.modele)
        module = Mock(SentenceTransformer=classe)
        with patch.dict(sys.modules, {"sentence_transformers": module}):
            self.assertIs(charger_encodeur(), self.modele)
        classe.assert_called_once_with(MODELE_E5, revision=REVISION_E5, device="cpu")
        self.modele.float.assert_called_once()
        self.modele.eval.assert_called_once()
        self.assertEqual(self.modele.max_seq_length, 512)

    def test_encodage_prefixe_texte_et_options_notebook(self):
        vecteur = encoder_question(self.modele, self.question_humaine)
        entree = "query: " + self.question_humaine
        self.modele.tokenizer.assert_called_once_with(entree, truncation=False)
        self.modele.encode.assert_called_once_with(
            [entree], batch_size=32, normalize_embeddings=True,
            convert_to_numpy=True, show_progress_bar=False)
        np.testing.assert_array_equal(vecteur, self.vecteur)

    def test_aucune_troncature_silencieuse(self):
        self.modele.tokenizer.return_value = {"input_ids": list(range(513))}
        with self.assertRaisesRegex(ErreurRecuperation, "aucune troncature"):
            encoder_question(self.modele, self.question_humaine)
        self.modele.encode.assert_not_called()

    def test_question_vide_refusee(self):
        with self.assertRaisesRegex(ErreurRecuperation, "Question vide"):
            encoder_question(self.modele, " \n")
        self.modele.encode.assert_not_called()

    def test_mauvaise_sortie_encodeur_refusee(self):
        for sortie in (np.zeros((1, 383)), np.zeros((2, 384)), np.zeros((1, 384)),
                       np.full((1, 384), np.nan)):
            with self.subTest(shape=sortie.shape):
                self.modele.encode.return_value = sortie
                with self.assertRaises(ErreurRecuperation):
                    encoder_question(self.modele, self.question_humaine)

    def test_top5_scores_egalites_et_correspondance(self):
        resultats = recuperer_passages(self.index, self.vecteur)
        self.assertEqual([r["indice"] for r in resultats], [0, 1, 2, 3, 4])
        self.assertEqual([r["rang"] for r in resultats], [1, 2, 3, 4, 5])
        self.assertEqual([r["score"] for r in resultats], [1, 1, 1, 0, 0])
        for r in resultats:
            self.assertIs(r["passage"], self.index.passages[r["indice"]])

    def test_meilleur_passage_au_milieu_de_la_matrice(self):
        vecteur = np.eye(5, 384, dtype=np.float32)[4]
        resultats = recuperer_passages(self.index, vecteur)
        self.assertEqual([r["indice"] for r in resultats], [4, 0, 1, 2, 3])
        self.assertEqual([r["score"] for r in resultats], [1, 0, 0, 0, 0])

    def test_vecteur_ou_topk_incompatibles(self):
        for vecteur in (np.zeros(384, dtype=np.float32), np.ones(383, dtype=np.float32),
                        self.vecteur.astype(np.float64), np.full(384, np.inf, dtype=np.float32)):
            with self.subTest(shape=vecteur.shape, dtype=vecteur.dtype):
                with self.assertRaises(ErreurRecuperation):
                    recuperer_passages(self.index, vecteur)
        for k in (0, 7, True, 2.5):
            with self.subTest(k=k):
                with self.assertRaises(ErreurRecuperation):
                    recuperer_passages(self.index, self.vecteur, k)

    def test_cli_recuperation_sans_modele_reel(self):
        # Câblage de la commande uniquement : index et encodeur contrôlés.
        sortie = io.StringIO()
        with (patch("rag.lire_question_calibration", return_value={"question": self.question_humaine}),
              patch("rag.charger_index", return_value=IndexCommun(
                  {"index": {"sha256": "matrice-test"}, "metadonnees": {"sha256": "meta-test"}},
                  self.index.matrice, self.index.passages)),
              patch("rag.charger_encodeur", return_value=self.modele),
              patch("rag.version", return_value="double-de-test"),
              redirect_stdout(sortie), redirect_stderr(io.StringIO())):
            self.assertEqual(main(["--retrieve-only", "--question-id", "Q036"]), 0)
        resultat = json.loads(sortie.getvalue())
        self.assertEqual(resultat["statut"], "recuperation_effectuee")
        self.assertEqual(len(resultat["resultats"]), 5)
        self.assertFalse(resultat["ollama_appele"])


class ContexteTests(unittest.TestCase):
    def setUp(self):
        # Question humaine de calibration ; documents artificiels de test.
        self.question = "Quelles sont les obligations légales de l'empoyeur en période de forte chaleur ?"
        self.resultats = [{"rang": i, "score": 0.5, "passage": {
            "passage_id": f"fixture-{i}", "titre_fiche": "Fiche de contrôle",
            "section_titre": "Section", "chemin": ["Intertitre"], "date_maj": "2026-10-18",
            "texte": f"  Texte original {i}.\n- Liste conservée.\n",
            "url": "https://example.org/source", "url_citation": "https://example.org/source#texte",
        }} for i in range(1, 6)]

    def test_numerotation_textes_question_et_sources(self):
        contexte = construire_contexte(self.question, self.resultats)
        self.assertIn(self.question, contexte["prompt"])
        self.assertEqual([s["reference"] for s in contexte["sources"]],
                         [f"[P{i}]" for i in range(1, 6)])
        for i, resultat in enumerate(self.resultats, 1):
            self.assertIn(resultat["passage"]["texte"], contexte["prompt"])
            self.assertEqual(contexte["sources"][i-1]["passage_id"], resultat["passage"]["passage_id"])
        self.assertEqual(contexte["sha256_prompt"], hashlib.sha256(contexte["prompt"].encode()).hexdigest())
        self.assertEqual(contexte["sha256_system"], hashlib.sha256(contexte["system"].encode()).hexdigest())
        self.assertIn(ABSTENTION, contexte["system"])

    def test_scores_et_metadonnees_de_reponse_exclus_du_prompt(self):
        self.resultats[0]["passage"]["annotation_attendue"] = "SECRET_DE_TEST"
        contexte = construire_contexte(self.question, self.resultats)
        self.assertNotIn("SECRET_DE_TEST", contexte["prompt"])
        self.assertNotIn("https://example.org/source", contexte["prompt"])
        self.assertNotIn("0.5", contexte["prompt"])

    def test_nombre_rangs_et_doublons_refuses(self):
        with self.assertRaises(ErreurRecuperation):
            construire_contexte(self.question, self.resultats[:4])
        self.resultats[1]["rang"] = 3
        with self.assertRaises(ErreurRecuperation):
            construire_contexte(self.question, self.resultats)
        self.resultats[1]["rang"] = 2
        self.resultats[1]["passage"]["passage_id"] = "fixture-1"
        with self.assertRaises(ErreurRecuperation):
            construire_contexte(self.question, self.resultats)


if __name__ == "__main__":
    unittest.main()
