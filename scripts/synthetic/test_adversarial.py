"""Aperçu des pièges sur des sources techniques ; aucune question juridique générée."""

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


class PreparationAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dossier = Path(self.temp.name)
        exporter(self.dossier)
        self.corpus = corpus.charger_corpus(self.dossier)
        self.code = {"git_commit": "a" * 40, "git_dirty": False, "python": "fixture",
                     "sha256_corpus_py": "b" * 64}
        self.selection = corpus.creer_manifeste(
            self.corpus, corpus.selectionner(self.corpus, 1, 42), "fiches", 42, self.code)
        self.passage = self.selection["groupes"][0][0]
        self.chemin = self.dossier / "selection.json"
        self.chemin.write_text(json.dumps(self.selection, ensure_ascii=False), encoding="utf-8")

    def arguments(self, mode="--prepare-only"):
        return [mode, "--sources", str(self.chemin), "--type", "adversarial",
                "--difficulty", "medium", "--index-dir", str(self.dossier)]

    def test_prompt_conserve_source_complete_et_schema_sans_mutation(self):
        passage = {**self.passage, "texte": "  Témoin : éteint.\n\u0001 Diagnostic complet.\n"}
        avant = copy.deepcopy(passage)
        prompt = prompts.preparer_prompt_adversarial(passage)
        self.assertEqual(prompt["version"], prompts.VERSION_ADVERSARIAL)
        self.assertNotIn(prompt["version"], [prompts.VERSION_PROMPT, prompts.VERSION_MULTI_PASSAGE])
        self.assertEqual([m["role"] for m in prompt["messages"]], ["system", "user"])
        self.assertIn(json.dumps(passage, ensure_ascii=False, indent=2), prompt["messages"][1]["content"])
        self.assertEqual(prompt["response_schema"], schema.schema_generation())
        self.assertEqual(passage, avant)

    def test_prompt_refuse_source_vide_ou_difficulte_inconnue(self):
        for passage in [None, [], {}, {**self.passage, "texte": "\n"},
                        {**self.passage, "passage_id": " "}, {**self.passage, "texte": True}]:
            with self.subTest(passage=passage), self.assertRaises(ValueError):
                prompts.preparer_prompt_adversarial(passage)
        with self.assertRaises(ValueError):
            prompts.preparer_prompt_adversarial(self.passage, "mesuree")

    def test_preparation_reproductible_source_unique_sans_verdict(self):
        selection, empreinte = generate.charger_selection(self.chemin, self.corpus)
        avant = copy.deepcopy(selection)
        preparation = generate.preparer(selection, empreinte, 1, "adversarial", "medium")
        self.assertEqual(preparation, generate.preparer(selection, empreinte, 1, "adversarial", "medium"))
        self.assertEqual(preparation["format"], "agent0-preparation-v1")
        self.assertEqual(preparation["type"], "adversarial")
        self.assertEqual(preparation["difficulty_target"], "medium")
        self.assertEqual(preparation["source"], self.passage)
        self.assertNotIn("sources", preparation)
        self.assertEqual(preparation["selection"]["sha256_fichier"], empreinte)
        octets = json.dumps(preparation["prompt"], ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.assertEqual(preparation["sha256_prompt"], hashlib.sha256(octets).hexdigest())
        self.assertFalse(preparation["ollama_appele"])
        self.assertFalse(preparation["budget_tokens_verifie"])
        self.assertNotIn("validation", preparation)
        self.assertNotIn("question", preparation)
        self.assertEqual(selection, avant)

    def test_cli_apercu_enregistre_sans_modele_ni_reseau(self):
        sortie = self.dossier / "preparations" / "adversarial.json"
        avant = {p: p.read_bytes() for p in [self.chemin, self.dossier / "passages_m2.json"]}
        with (patch.object(corpus, "provenance_code", return_value=copy.deepcopy(self.code)),
              patch.object(client_qwen, "preparer_requete") as preparer,
              patch.object(run, "executer") as executer,
              patch("urllib.request.urlopen", side_effect=AssertionError("Réseau interdit")) as reseau,
              contextlib.redirect_stdout(io.StringIO()) as stdout):
            self.assertEqual(generate.main(self.arguments() + ["--output", str(sortie)]), 0)
        preparer.assert_not_called()
        executer.assert_not_called()
        reseau.assert_not_called()
        resume = json.loads(stdout.getvalue())
        sauvegarde = json.loads(sortie.read_text(encoding="utf-8"))
        self.assertEqual(resume["statut"], "prompt_prepare")
        self.assertEqual(resume["passage_id"], self.passage["passage_id"])
        self.assertEqual(resume["version_prompt"], prompts.VERSION_ADVERSARIAL)
        self.assertEqual(resume["sha256_prompt"], sauvegarde["sha256_prompt"])
        self.assertEqual(sauvegarde["source"], self.passage)
        self.assertFalse(resume["ollama_appele"])
        self.assertFalse(resume["budget_tokens_verifie"])
        self.assertEqual({p: p.read_bytes() for p in avant}, avant)

    def test_cli_budget_transmet_prompt_sans_generation(self):
        sortie = self.dossier / "budget.json"
        qwen = {"ollama": {"version": "fixture", "modele": "fixture", "digest": "fixture"},
                "entree": {"texte": "fixture raw", "nb_tokens_hf": 24}, "versions": {}}
        with (patch.object(corpus, "provenance_code", return_value=copy.deepcopy(self.code)),
              patch.object(client_qwen, "preparer_requete", return_value=qwen) as preparer,
              patch.object(client_qwen, "generer") as generer,
              patch.object(run, "executer") as executer,
              contextlib.redirect_stdout(io.StringIO()) as stdout):
            self.assertEqual(generate.main(self.arguments("--prepare-qwen")
                                           + ["--output", str(sortie)]), 0)
        generer.assert_not_called()
        executer.assert_not_called()
        sauvegarde = json.loads(sortie.read_text(encoding="utf-8"))
        self.assertEqual(preparer.call_args.args, (sauvegarde["prompt"], False))
        self.assertEqual(sauvegarde["source"], self.passage)
        self.assertTrue(sauvegarde["budget_tokens_verifie"])
        self.assertFalse(json.loads(stdout.getvalue())["generation_appelee"])

    def test_cli_generation_bloquee_avant_tout_effet(self):
        racine = self.dossier / "runs_interdits"
        with (patch.object(generate, "DOSSIER_RUNS", racine),
              patch.object(corpus, "charger_corpus") as charger,
              patch.object(corpus, "provenance_code") as provenance,
              patch.object(client_qwen, "preparer_requete") as preparer,
              patch.object(run, "executer") as executer,
              contextlib.redirect_stderr(io.StringIO()) as stderr):
            with self.assertRaises(SystemExit) as erreur:
                generate.main(self.arguments("--generate") + ["--run-id", "fixture_adversarial"])
        self.assertEqual(erreur.exception.code, 2)
        self.assertIn("Génération adversarial non activée", stderr.getvalue())
        charger.assert_not_called()
        provenance.assert_not_called()
        preparer.assert_not_called()
        executer.assert_not_called()
        self.assertFalse(racine.exists())

    def test_cli_sortie_existante_preservee_avant_lecture_du_corpus(self):
        sortie = self.dossier / "conserver.json"
        sortie.write_bytes(b"a conserver")
        with (patch.object(corpus, "charger_corpus") as charger,
              contextlib.redirect_stderr(io.StringIO())):
            self.assertEqual(generate.main(self.arguments() + ["--output", str(sortie)]), 1)
        charger.assert_not_called()
        self.assertEqual(sortie.read_bytes(), b"a conserver")

    def test_cli_refuse_paire_sans_troncature_ni_appel_modele(self):
        selection = corpus.creer_manifeste(
            self.corpus, corpus.selectionner(self.corpus, 1, 42, paires=True),
            "paires", 42, self.code)
        octets = json.dumps(selection, ensure_ascii=False).encode("utf-8")
        self.chemin.write_bytes(octets)
        sortie = self.dossier / "interdit.json"
        with (patch.object(corpus, "provenance_code") as provenance,
              patch.object(client_qwen, "preparer_requete") as preparer,
              contextlib.redirect_stderr(io.StringIO()) as stderr):
            self.assertEqual(generate.main(self.arguments() + ["--output", str(sortie)]), 1)
        self.assertIn("un seul passage", stderr.getvalue())
        provenance.assert_not_called()
        preparer.assert_not_called()
        self.assertFalse(sortie.exists())
        self.assertEqual(self.chemin.read_bytes(), octets)


if __name__ == "__main__":
    unittest.main()
