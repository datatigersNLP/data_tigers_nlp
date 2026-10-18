"""Préparation de deux documents techniques ; aucune inférence ni question juridique."""

import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

if __package__:
    from . import client_qwen, corpus, generate, prompts, run, schema
    from .test_corpus import exporter
else:
    import client_qwen
    import corpus
    import generate
    import prompts
    import run
    import schema
    from test_corpus import exporter


class PreparationMultipleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dossier = Path(self.temp.name)
        exporter(self.dossier)
        self.corpus = corpus.charger_corpus(self.dossier)
        self.code = {"git_commit": "a" * 40, "git_dirty": False, "python": "fixture",
                     "sha256_corpus_py": "b" * 64}
        self.selection = corpus.creer_manifeste(
            self.corpus, corpus.selectionner(self.corpus, 1, 42, paires=True),
            "paires", 42, self.code)
        self.passages = self.selection["groupes"][0]
        self.chemin = self.dossier / "paires.json"
        self.chemin.write_text(json.dumps(self.selection, ensure_ascii=False), encoding="utf-8")

    def arguments(self, mode="--prepare-only"):
        return [mode, "--sources", str(self.chemin), "--type", "multi_passage",
                "--difficulty", "medium", "--index-dir", str(self.dossier)]

    def test_prompt_conserve_sources_completes_ordre_et_schema_sans_mutation(self):
        avant = copy.deepcopy(self.passages)
        prompt = prompts.preparer_prompt_multiple(self.passages)
        texte = prompt["messages"][1]["content"]
        self.assertIn(json.dumps(self.passages, ensure_ascii=False, indent=2), texte)
        self.assertEqual(prompt["response_schema"], schema.schema_generation())
        self.assertEqual([m["role"] for m in prompt["messages"]], ["system", "user"])
        self.assertIn("multi_passage", texte)
        self.assertIn("medium", texte)
        self.assertIn("nécessaires et suffisantes", prompt["messages"][0]["content"])
        self.assertEqual(self.passages, avant)

    def test_prompt_refuse_nombre_invalide_sources_vides_ou_dupliquees(self):
        un, deux = self.passages
        cas = [None, un, [], [un], [un, deux, un], [un, un],
               [un, None], [un, {**deux, "texte": " "}],
               [un, {**deux, "passage_id": " "}]]
        for passages in cas:
            with self.subTest(passages=passages), self.assertRaises(ValueError):
                prompts.preparer_prompt_multiple(passages)
        with self.assertRaises(ValueError):
            prompts.preparer_prompt_multiple(self.passages, "mesuree")

    def test_preparation_versionnee_reproductible_et_sources_intactes(self):
        selection, empreinte = generate.charger_selection(self.chemin, self.corpus)
        avant = copy.deepcopy(selection)
        preparation = generate.preparer(selection, empreinte, 1, "multi_passage", "medium")
        self.assertEqual(preparation,
                         generate.preparer(selection, empreinte, 1, "multi_passage", "medium"))
        self.assertEqual(preparation["format"], "agent0-preparation-v2")
        self.assertNotIn("source", preparation)
        self.assertEqual(preparation["sources"], self.passages)
        self.assertEqual(preparation["selection"]["sha256_fichier"], empreinte)
        octets = json.dumps(preparation["prompt"], ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.assertEqual(preparation["sha256_prompt"], hashlib.sha256(octets).hexdigest())
        self.assertFalse(preparation["ollama_appele"])
        self.assertFalse(preparation["budget_tokens_verifie"])
        self.assertNotIn("validation", preparation)
        self.assertEqual(selection, avant)

    def test_cardinalite_selon_categorie_et_ancien_format_conserve(self):
        for passages in [[self.passages[0]], self.passages + [self.corpus.passages[-1]]]:
            selection = {**self.selection, "groupes": [passages]}
            with self.subTest(nombre=len(passages)), self.assertRaises(generate.ErreurPreparation):
                generate.preparer(selection, "b" * 64, 1, "multi_passage")
        for categorie in ("simple", "reformulation"):
            with self.subTest(categorie=categorie):
                with self.assertRaises(generate.ErreurPreparation):
                    generate.preparer(self.selection, "b" * 64, 1, categorie)
                selection = {**self.selection, "groupes": [[self.passages[0]]]}
                preparation = generate.preparer(selection, "b" * 64, 1, categorie)
                self.assertEqual(preparation["format"], "agent0-preparation-v1")
                self.assertEqual(preparation["source"], self.passages[0])
                self.assertNotIn("sources", preparation)
                self.assertEqual(preparation["prompt"]["version"], prompts.VERSION_PROMPT)

    def test_cli_hors_ligne_enregistre_les_deux_sources_sans_reseau(self):
        sortie = self.dossier / "apercu.json"
        avant = self.chemin.read_bytes()
        with (patch.object(corpus, "provenance_code", return_value=copy.deepcopy(self.code)),
              patch("urllib.request.urlopen", side_effect=AssertionError("Réseau interdit")) as reseau,
              contextlib.redirect_stdout(io.StringIO()) as stdout):
            self.assertEqual(generate.main(self.arguments() + ["--output", str(sortie)]), 0)
        reseau.assert_not_called()
        resume = json.loads(stdout.getvalue())
        sauvegarde = json.loads(sortie.read_text(encoding="utf-8"))
        self.assertEqual(resume["source_ids"], [p["passage_id"] for p in self.passages])
        self.assertEqual(resume["version_prompt"], prompts.VERSION_MULTI_PASSAGE)
        self.assertEqual(sauvegarde["sources"], self.passages)
        self.assertFalse(resume["ollama_appele"])
        self.assertEqual(avant, self.chemin.read_bytes())

    def test_cli_budget_transmet_deux_sources_sans_appel_de_generation(self):
        sortie = self.dossier / "budget.json"
        qwen = {"ollama": {"version": "fixture", "modele": "fixture", "digest": "fixture"},
                "entree": {"texte": "fixture raw", "nb_tokens_hf": 24}, "versions": {}}
        with (patch.object(corpus, "provenance_code", return_value=copy.deepcopy(self.code)),
              patch.object(client_qwen, "preparer_requete", return_value=qwen) as preparer,
              patch.object(client_qwen, "generer") as generer,
              contextlib.redirect_stdout(io.StringIO())):
            self.assertEqual(generate.main(self.arguments("--prepare-qwen")
                                           + ["--output", str(sortie)]), 0)
        generer.assert_not_called()
        sauvegarde = json.loads(sortie.read_text(encoding="utf-8"))
        self.assertEqual(preparer.call_args.args[0], sauvegarde["prompt"])
        self.assertEqual(sauvegarde["sources"], self.passages)
        self.assertTrue(sauvegarde["budget_tokens_verifie"])
        self.assertFalse(sauvegarde["generation_appelee"])

    def test_cli_generation_bloquee_avant_sources_api_et_stockage(self):
        with (patch.object(corpus, "charger_corpus") as charger,
              patch.object(client_qwen, "preparer_requete") as preparer,
              patch.object(run, "executer") as executer,
              contextlib.redirect_stderr(io.StringIO())):
            with self.assertRaises(SystemExit) as erreur:
                generate.main(self.arguments("--generate") + ["--run-id", "fixture_multi"])
        self.assertEqual(erreur.exception.code, 2)
        charger.assert_not_called()
        preparer.assert_not_called()
        executer.assert_not_called()

    def test_cli_apercu_existant_protege_avant_lecture_du_corpus(self):
        sortie = self.dossier / "a_conserver.json"
        sortie.write_bytes(b"a conserver")
        with (patch.object(corpus, "charger_corpus") as charger,
              contextlib.redirect_stderr(io.StringIO())):
            self.assertEqual(generate.main(self.arguments() + ["--output", str(sortie)]), 1)
        charger.assert_not_called()
        self.assertEqual(sortie.read_bytes(), b"a conserver")


if __name__ == "__main__":
    unittest.main()
