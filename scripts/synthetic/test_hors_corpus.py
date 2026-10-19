"""Préparation et génération hors corpus simulée ; aucune absence confirmée."""

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
    from . import client_qwen, corpus, generate, prompts, run, schema, validation
    from .test_corpus import exporter
    from .test_run import reponse_technique, requete_technique
else:
    import client_qwen
    import corpus
    import generate
    import prompts
    import run
    import schema
    import validation
    from test_corpus import exporter
    from test_run import reponse_technique, requete_technique


class PreparationHorsCorpusTests(unittest.TestCase):
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
        return [mode, "--sources", str(self.chemin), "--type", "hors_corpus",
                "--difficulty", "medium", "--index-dir", str(self.dossier)]

    def preparation(self):
        return generate.preparer(self.selection, "b" * 64, 1, "hors_corpus", "medium")

    def proposition(self):
        return {"question": "Quelle est la masse de l'appareil ?", "type": "hors_corpus",
                "difficulty_target": "medium", "answerable_proposed": False, "evidence": [],
                "generation_reason": "Proposer un besoin voisin du diagnostic technique.",
                "out_of_corpus_reason": "La masse manque dans ce passage ; corpus complet à vérifier.",
                "adversarial_premise": None, "correction_proposed": None}

    def valider(self, proposition, preparation=None, vues=None):
        return validation.valider_proposition(json.dumps(proposition, ensure_ascii=False),
            self.preparation() if preparation is None else preparation, "fixture_hors_corpus",
            set() if vues is None else vues)

    def test_prompt_conserve_source_complete_schema_et_absence_de_verdict(self):
        passage = {**self.passage, "texte": "  Témoin : éteint.\n\u0001 Diagnostic complet.\n"}
        avant = copy.deepcopy(passage)
        prompt = prompts.preparer_prompt_hors_corpus(passage)
        self.assertEqual(prompt["version"], prompts.VERSION_HORS_CORPUS)
        self.assertEqual([m["role"] for m in prompt["messages"]], ["system", "user"])
        self.assertIn(json.dumps(passage, ensure_ascii=False, indent=2), prompt["messages"][1]["content"])
        self.assertEqual(prompt["response_schema"], schema.schema_generation())
        self.assertNotIn("validation", prompt)
        self.assertEqual(passage, avant)

    def test_prompt_refuse_source_invalide_et_difficulte_inconnue(self):
        for passage in [None, [], {}, {**self.passage, "texte": "\n"},
                        {**self.passage, "passage_id": " "}, {**self.passage, "texte": True}]:
            with self.subTest(passage=passage), self.assertRaises(ValueError):
                prompts.preparer_prompt_hors_corpus(passage)
        with self.assertRaises(ValueError):
            prompts.preparer_prompt_hors_corpus(self.passage, "mesuree")

    def test_preparation_reproductible_provenance_sans_classement_confirme(self):
        selection, empreinte = generate.charger_selection(self.chemin, self.corpus)
        avant = copy.deepcopy(selection)
        preparation = generate.preparer(selection, empreinte, 1, "hors_corpus", "medium")
        self.assertEqual(preparation, generate.preparer(selection, empreinte, 1, "hors_corpus", "medium"))
        self.assertEqual(preparation["format"], "agent0-preparation-v1")
        self.assertEqual(preparation["type"], "hors_corpus")
        self.assertEqual(preparation["source"], self.passage)
        self.assertNotIn("sources", preparation)
        self.assertEqual(preparation["selection"]["sha256_fichier"], empreinte)
        self.assertEqual(preparation["corpus"], selection["corpus"])
        octets = json.dumps(preparation["prompt"], ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.assertEqual(preparation["sha256_prompt"], hashlib.sha256(octets).hexdigest())
        for champ in ("validation", "answerable_confirmed", "question", "out_of_corpus_reason"):
            self.assertNotIn(champ, preparation)
        self.assertFalse(preparation["ollama_appele"])
        self.assertFalse(preparation["budget_tokens_verifie"])
        self.assertEqual(selection, avant)

    def test_cli_apercu_enregistre_source_sans_reseau_ni_generation(self):
        sortie = self.dossier / "preparations" / "hors_corpus.json"
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
        self.assertEqual(resume["version_prompt"], prompts.VERSION_HORS_CORPUS)
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

    def test_cli_generation_un_appel_et_absence_non_confirmee(self):
        racine = self.dossier / "runs"
        reponse = reponse_technique(self.proposition())
        with (patch.object(generate, "DOSSIER_RUNS", racine),
              patch.object(corpus, "provenance_code", return_value=copy.deepcopy(self.code)),
              patch.object(client_qwen, "preparer_requete", return_value=requete_technique()) as preparer,
              patch.object(client_qwen, "_http", return_value=reponse) as http,
              contextlib.redirect_stdout(io.StringIO()) as stdout):
            self.assertEqual(generate.main(self.arguments("--generate")
                                          + ["--run-id", "fixture_hors_corpus"]), 0)
        http.assert_called_once()
        self.assertEqual(json.loads(stdout.getvalue())["statut"], "candidat_prepare")
        dossier = racine / "fixture_hors_corpus"
        manifeste = json.loads((dossier / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(preparer.call_args.args, (manifeste["preparation"]["prompt"], False))
        self.assertEqual(manifeste["preparation"]["source"], self.passage)
        candidat = json.loads((dossier / "candidates.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(candidat["generation_source_ids"], [self.passage["passage_id"]])
        self.assertEqual(candidat["out_of_corpus_reason"], self.proposition()["out_of_corpus_reason"])
        self.assertFalse(candidat["answerable_proposed"])
        self.assertEqual(candidat["evidence"], [])
        self.assertEqual(candidat["validation"]["human"], "pending")
        self.assertIsNone(candidat["validation"]["answerable_confirmed"])
        self.assertEqual(candidat["validation"]["expected_points"], [])
        self.assertEqual((dossier / "rejected.jsonl").read_bytes(), b"")
        traces = [json.loads(l) for l in (dossier / "traces.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(next(t["resultat"] for t in traces if "resultat" in t)["reponse_brute"],
                         reponse["response"])

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
            self.corpus, corpus.selectionner(self.corpus, 1, 42, paires=True), "paires", 42, self.code)
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

    def test_validation_preserve_textes_source_et_absence_de_verdict(self):
        proposition = self.proposition()
        proposition["question"] = "  Quelle est la masse de l'appareil ?\n"
        proposition["out_of_corpus_reason"] = "  Information manquante ici ; corpus complet à vérifier.\n"
        preparation = self.preparation()
        avant = copy.deepcopy((proposition, preparation))
        candidat = self.valider(proposition, preparation)
        for champ in ("question", "out_of_corpus_reason", "generation_reason"):
            self.assertEqual(getattr(candidat, champ), proposition[champ])
        self.assertFalse(candidat.answerable_proposed)
        self.assertEqual(candidat.evidence, [])
        self.assertEqual(candidat.generation_source_ids, [self.passage["passage_id"]])
        self.assertEqual(candidat.validation.automatic, "passed")
        self.assertEqual(candidat.validation.human, "pending")
        for champ in ("answerable_confirmed", "reviewer", "review_note"):
            self.assertIsNone(getattr(candidat.validation, champ))
        self.assertEqual(candidat.validation.expected_points, [])
        self.assertEqual((proposition, preparation), avant)

    def test_validation_refuse_repondable_ou_preuves_positives(self):
        preuve = {"passage_id": self.passage["passage_id"], "excerpt": "éteint."}
        cas = [{"answerable_proposed": True, "evidence": [preuve], "out_of_corpus_reason": None},
               {"answerable_proposed": "false"}, {"answerable_proposed": 0},
               {"evidence": [preuve]},
               {"evidence": [{"passage_id": "source-inventee", "excerpt": "absent"}]}]
        for changement in cas:
            with self.subTest(changement=changement), self.assertRaises(ValueError):
                self.valider({**self.proposition(), **changement})

    def test_validation_exige_motif_sans_champs_adversarial(self):
        cas = [{"out_of_corpus_reason": valeur} for valeur in (None, "", " \n", True)]
        cas += [{"adversarial_premise": "Le témoin est allumé."},
                {"correction_proposed": "Le témoin est éteint."}]
        for changement in cas:
            with self.subTest(changement=changement), self.assertRaises(ValueError):
                self.valider({**self.proposition(), **changement})

    def test_validation_refuse_preparation_ambigue_ou_source_invalide(self):
        cas = [{"format": "agent0-preparation-v2"}, {"source": None},
               {"sources": [self.passage]}, {"source": {**self.passage, "texte": " "}},
               {"source": {**self.passage, "passage_id": " "}},
               {"source": {**self.passage, "texte": True}}]
        for changement in cas:
            with self.subTest(changement=changement), self.assertRaisesRegex(ValueError, "préparation hors_corpus"):
                self.valider(self.proposition(), {**self.preparation(), **changement})
        preparation = self.preparation()
        preparation.pop("source")
        with self.assertRaisesRegex(ValueError, "préparation hors_corpus"):
            self.valider(self.proposition(), preparation)

    def test_validation_refuse_verdict_injecte_categorie_ou_difficulte_differente(self):
        simple = {"type": "simple", "answerable_proposed": True, "out_of_corpus_reason": None,
                  "evidence": [{"passage_id": self.passage["passage_id"], "excerpt": "éteint."}]}
        for changement in [{"validation": {"human": "accepted"}}, {"answerable_confirmed": False},
                           {"difficulty_target": "hard"}, simple]:
            with self.subTest(changement=changement), self.assertRaises(ValueError):
                self.valider({**self.proposition(), **changement})

    def test_validation_refuse_doublon_normalise(self):
        vues = {validation.normaliser_question(self.proposition()["question"].upper())}
        with self.assertRaisesRegex(ValueError, "doublon"):
            self.valider(self.proposition(), vues=vues)

    def test_run_rejet_conserve_brut_sans_reparation_ni_relance(self):
        proposition = {**self.proposition(), "out_of_corpus_reason": None}
        reponse = reponse_technique(proposition)
        racine = self.dossier / "runs"
        with (patch.object(client_qwen, "preparer_requete", return_value=requete_technique()),
              patch.object(client_qwen, "_http", return_value=reponse) as http):
            resume = run.executer(self.preparation(), "rejet_hors_corpus", racine)
        http.assert_called_once()
        self.assertEqual(resume["statut"], "rejet_automatique")
        dossier = racine / "rejet_hors_corpus"
        self.assertEqual((dossier / "candidates.jsonl").read_bytes(), b"")
        rejet = json.loads((dossier / "rejected.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(rejet["phase"], "validation_automatique")
        traces = [json.loads(l) for l in (dossier / "traces.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(next(t["resultat"] for t in traces if "resultat" in t)["reponse_brute"],
                         reponse["response"])

    def test_run_sortie_tronquee_reste_erreur_technique(self):
        reponse = {**reponse_technique(self.proposition()), "done_reason": "length"}
        racine = self.dossier / "runs"
        with (patch.object(client_qwen, "preparer_requete", return_value=requete_technique()),
              patch.object(client_qwen, "_http", return_value=reponse) as http):
            resume = run.executer(self.preparation(), "tronque_hors_corpus", racine)
        http.assert_called_once()
        self.assertEqual(resume["statut"], "erreur_technique")
        self.assertIn("generation_incomplete", resume["motif"])
        self.assertEqual((racine / "tronque_hors_corpus" / "candidates.jsonl").read_bytes(), b"")


if __name__ == "__main__":
    unittest.main()
