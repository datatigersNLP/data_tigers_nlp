"""Tests d'intégrité sans modèle et sans questions d'évaluation (#51)."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

from rag import ErreurIndex, charger_index


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


if __name__ == "__main__":
    unittest.main()
