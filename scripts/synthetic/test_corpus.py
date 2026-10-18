"""Exports techniques artificiels ; aucun modèle ni question d'évaluation."""

import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

if __package__:
    from . import corpus
else:
    import corpus


def passages_techniques():
    return [{"passage_id": f"fixture-{fiche}-{i}", "titre_fiche": f"Fixture {fiche}",
             "section_titre": "Diagnostic", "chemin": ["Témoin"],
             "url": f"https://example.invalid/{fiche}",
             "url_citation": f"https://example.invalid/{fiche}#temoin",
             "date_maj": "2026-10-18", "texte": f"  Témoin {fiche}{i} : éteint.\n",
             "articles": []}
            for fiche, nombre in [("a", 3), ("b", 2), ("c", 1)] for i in range(nombre)]


def exporter(dossier, passages=None, octets=None):
    passages = passages_techniques() if passages is None else passages
    if octets is None:
        octets = json.dumps(passages, ensure_ascii=False).encode("utf-8")
    entete = {"format": "index-e5-v1", "source": {"decoupage": "m2"},
              "metadonnees": {"fichier": "passages_m2.json", "nb_passages": len(passages),
                              "sha256": hashlib.sha256(octets).hexdigest()}}
    (dossier / "passages_m2.json").write_bytes(octets)
    (dossier / "index_m2.json").write_text(json.dumps(entete), encoding="utf-8")
    return entete


class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dossier = Path(self.temp.name)
        self.entete = exporter(self.dossier)

    def lire(self):
        return corpus.charger_corpus(self.dossier)

    def test_charge_textes_et_ordre_exacts_sans_matrice(self):
        resultat = self.lire()
        self.assertEqual(resultat.passages, passages_techniques())
        self.assertEqual(resultat.sha256_passages, self.entete["metadonnees"]["sha256"])
        self.assertFalse((self.dossier / "index_m2.f32").exists())

    def test_fichiers_absents_et_octet_corrompu_refuses(self):
        chemin = self.dossier / "passages_m2.json"
        chemin.write_bytes(chemin.read_bytes() + b" ")
        with self.assertRaises(corpus.ErreurCorpus):
            self.lire()
        chemin.unlink()
        with self.assertRaises(corpus.ErreurCorpus):
            self.lire()

    def test_manifeste_incompatible_refuse(self):
        cas = [{"format": "autre"}, {"source": {"decoupage": "m0"}},
               {"metadonnees": {**self.entete["metadonnees"], "fichier": "../passages_m2.json"}},
               {"metadonnees": {**self.entete["metadonnees"], "nb_passages": True}},
               {"metadonnees": {**self.entete["metadonnees"], "nb_passages": 0}},
               {"metadonnees": {**self.entete["metadonnees"], "sha256": "invalide"}}]
        for changement in cas:
            with self.subTest(changement=changement), self.assertRaises(corpus.ErreurCorpus):
                (self.dossier / "index_m2.json").write_text(
                    json.dumps({**self.entete, **changement}), encoding="utf-8")
                self.lire()

    def test_compte_reel_incoherent_refuse(self):
        entete = copy.deepcopy(self.entete)
        entete["metadonnees"]["nb_passages"] += 1
        (self.dossier / "index_m2.json").write_text(json.dumps(entete), encoding="utf-8")
        with self.assertRaises(corpus.ErreurCorpus):
            self.lire()

    def test_types_champs_textes_vides_et_ids_dupliques_refuses(self):
        for champ, valeur in [("passage_id", ""), ("url", " "), ("texte", "\n"),
                              ("titre_fiche", None), ("date_maj", 2026),
                              ("chemin", "Diagnostic"), ("articles", [12])]:
            passages = passages_techniques()
            passages[0][champ] = valeur
            with self.subTest(champ=champ), self.assertRaises(corpus.ErreurCorpus):
                exporter(self.dossier, passages)
                self.lire()
        passages = passages_techniques()
        passages[1]["passage_id"] = passages[0]["passage_id"]
        exporter(self.dossier, passages)
        with self.assertRaises(corpus.ErreurCorpus):
            self.lire()

    def test_json_utf8_ou_structure_invalide_meme_avec_empreinte_conforme(self):
        for octets in [b"\xff", b"{", b"{}", b"[null]"]:
            with self.subTest(octets=octets), self.assertRaises(corpus.ErreurCorpus):
                exporter(self.dossier, octets=octets)
                self.lire()

    def test_tirage_reproductible_diversifie_et_independant_ordre_entree(self):
        source = self.lire()
        avant = copy.deepcopy(source.passages)
        un = corpus.selectionner(source, 3, 42)
        deux = corpus.selectionner(source, 3, 42)
        inverse = corpus.CorpusM2(list(reversed(source.passages)), source.sha256_entete, source.sha256_passages)
        self.assertEqual(un, deux)
        self.assertEqual(un, corpus.selectionner(inverse, 3, 42))
        self.assertEqual(len({g[0]["url"] for g in un}), 3)
        self.assertTrue(all(len(g) == 1 for g in un))
        self.assertEqual(source.passages, avant)

    def test_tirage_ne_modifie_pas_random_global(self):
        import random
        etat = random.getstate()
        corpus.selectionner(self.lire(), 2, 42)
        self.assertEqual(random.getstate(), etat)

    def test_tirage_impossible_ou_arguments_non_stricts_refuses(self):
        for nombre, graine, paires in [(0, 42, False), (4, 42, False), (True, 42, False),
                                      (1, True, False), (1, "42", False), (1, 42, 1),
                                      (3, 42, True)]:
            with self.subTest(nombre=nombre, graine=graine, paires=paires):
                with self.assertRaises(corpus.ErreurCorpus):
                    corpus.selectionner(self.lire(), nombre, graine, paires)

    def test_paires_distinctes_meme_fiche_et_reproductibles(self):
        source = self.lire()
        paires = corpus.selectionner(source, 2, 42, paires=True)
        self.assertEqual(paires, corpus.selectionner(source, 2, 42, paires=True))
        for paire in paires:
            self.assertEqual(len(paire), 2)
            self.assertNotEqual(paire[0]["passage_id"], paire[1]["passage_id"])
            self.assertEqual(paire[0]["url"], paire[1]["url"])
        self.assertEqual(len({paire[0]["url"] for paire in paires}), 2)

    def test_ids_explicites_conservent_ordre_et_textes(self):
        source = self.lire()
        ids = ["fixture-b-1", "fixture-a-0", "fixture-b-0"]
        resultat = corpus.selectionner_ids(source, ids)
        self.assertEqual([g[0]["passage_id"] for g in resultat], ids)
        self.assertEqual(resultat[1][0]["texte"], passages_techniques()[0]["texte"])

    def test_ids_vides_dupliques_inconnus_refuses(self):
        for ids in [[], ["fixture-a-0", "fixture-a-0"], ["inconnu"], [" "], [12]]:
            with self.subTest(ids=ids), self.assertRaises(corpus.ErreurCorpus):
                corpus.selectionner_ids(self.lire(), ids)

    def test_manifeste_contient_provenance_empreintes_et_sources_intactes(self):
        source = self.lire()
        groupes = corpus.selectionner(source, 2, 42)
        code = {"git_commit": "a" * 40, "git_dirty": False, "python": "fixture"}
        manifeste = corpus.creer_manifeste(source, groupes, "fiches", 42, code)
        self.assertEqual(manifeste["code"], code)
        self.assertEqual(manifeste["corpus"]["sha256_passages"], source.sha256_passages)
        self.assertEqual(manifeste["groupes"], groupes)
        self.assertFalse(manifeste["matrice_lue"])
        self.assertFalse(manifeste["ollama_appele"])

    def test_sauvegarde_utf8_sans_ecrasement_et_sans_modifier_sources(self):
        source = self.lire()
        avant = (self.dossier / "passages_m2.json").read_bytes()
        groupes = corpus.selectionner(source, 1, 42)
        manifeste = corpus.creer_manifeste(source, groupes, "fiches", 42, {})
        sortie = self.dossier / "resultat" / "selection.json"
        corpus.enregistrer_manifeste(manifeste, sortie)
        self.assertEqual(json.loads(sortie.read_text(encoding="utf-8")), manifeste)
        with self.assertRaises(FileExistsError):
            corpus.enregistrer_manifeste(manifeste, sortie)
        self.assertEqual((self.dossier / "passages_m2.json").read_bytes(), avant)

    def test_cli_controle_et_selection_sans_modele(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(corpus.main(["--check-corpus", "--index-dir", str(self.dossier)]), 0)
        self.assertEqual(json.loads(stdout.getvalue())["nb_passages"], 6)
        sortie = self.dossier / "selection.json"
        code = {"git_commit": "a" * 40, "git_dirty": False, "python": "fixture"}
        with (patch.object(corpus, "provenance_code", return_value=code),
              contextlib.redirect_stdout(io.StringIO()) as stdout):
            self.assertEqual(corpus.main(["--ids", "fixture-b-0", "fixture-a-0", "--index-dir",
                                          str(self.dossier), "--output", str(sortie)]), 0)
        resultat = json.loads(stdout.getvalue())
        self.assertEqual(resultat["identifiants"], [["fixture-b-0"], ["fixture-a-0"]])
        self.assertIsNone(resultat["graine"])
        self.assertEqual(json.loads(sortie.read_text(encoding="utf-8"))["code"], code)

    def test_cli_refuse_ecrasement_et_arguments_ambigus(self):
        sortie = self.dossier / "selection.json"
        sortie.write_bytes(b"a conserver")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(corpus.main(["--index-dir", str(self.dossier), "--output", str(sortie)]), 1)
        self.assertEqual(sortie.read_bytes(), b"a conserver")
        for arguments in [["--check-corpus", "--count", "1"],
                          ["--check-corpus", "--output", "interdit.json"],
                          ["--ids", "fixture-a-0", "--seed", "42"]]:
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as erreur:
                    corpus.main(arguments)
                self.assertEqual(erreur.exception.code, 2)

    def test_provenance_git_et_refus_hors_git(self):
        reponses = [subprocess.CompletedProcess([], 0, stdout="a" * 40 + "\n"),
                    subprocess.CompletedProcess([], 0, stdout=" M fixture\n")]
        with patch.object(corpus.subprocess, "run", side_effect=reponses):
            code = corpus.provenance_code()
        self.assertEqual(code["git_commit"], "a" * 40)
        self.assertTrue(code["git_dirty"])
        self.assertEqual(len(code["sha256_corpus_py"]), 64)
        with patch.object(corpus.subprocess, "run", side_effect=FileNotFoundError):
            with self.assertRaises(corpus.ErreurCorpus):
                corpus.provenance_code()


if __name__ == "__main__":
    unittest.main()
