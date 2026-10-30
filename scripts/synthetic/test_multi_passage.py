"""Préparation et génération simulée sur deux documents techniques, sans question juridique."""

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

    def preparation(self):
        return generate.preparer(self.selection, "b" * 64, 1, "multi_passage", "medium")

    def proposition(self):
        return {"question": "Quels témoins sont éteints dans les deux sections du diagnostic ?",
                "type": "multi_passage", "difficulty_target": "medium", "answerable_proposed": True,
                "generation_reason": "Croiser les deux diagnostics techniques.",
                "evidence": [{"passage_id": p["passage_id"], "excerpt": p["texte"].strip()}
                             for p in self.passages]}

    def valider(self, proposition, preparation=None, vues=None):
        return validation.valider_proposition(json.dumps(proposition, ensure_ascii=False),
            self.preparation() if preparation is None else preparation, "fixture_multi",
            set() if vues is None else vues)

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

    def test_cli_generation_un_appel_sources_et_traces_conservees(self):
        racine = self.dossier / "runs"
        reponse = reponse_technique(self.proposition())
        with (patch.object(corpus, "provenance_code", return_value=copy.deepcopy(self.code)),
              patch.object(generate, "DOSSIER_RUNS", racine),
              patch.object(client_qwen, "preparer_requete", return_value=requete_technique()) as preparer,
              patch.object(client_qwen, "_http", return_value=reponse) as http,
              contextlib.redirect_stdout(io.StringIO()) as stdout):
            self.assertEqual(generate.main(self.arguments("--generate")
                                           + ["--run-id", "fixture_multi"]), 0)
        http.assert_called_once()
        self.assertEqual(json.loads(stdout.getvalue())["statut"], "candidat_prepare")
        dossier = racine / "fixture_multi"
        manifeste = json.loads((dossier / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifeste["preparation"]["sources"], self.passages)
        self.assertEqual(preparer.call_args.args[0], manifeste["preparation"]["prompt"])
        candidat = schema.CasSynthetique.model_validate_json(
            (dossier / "candidates.jsonl").read_text(encoding="utf-8").strip())
        self.assertEqual(candidat.generation_source_ids, [p["passage_id"] for p in self.passages])
        self.assertEqual(candidat.validation.human, "pending")
        traces = [json.loads(l) for l in (dossier / "traces.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(next(t["resultat"] for t in traces if "resultat" in t)["reponse_brute"],
                         reponse["response"])
        self.assertEqual((dossier / "rejected.jsonl").read_bytes(), b"")

    def test_cli_apercu_existant_protege_avant_lecture_du_corpus(self):
        sortie = self.dossier / "a_conserver.json"
        sortie.write_bytes(b"a conserver")
        with (patch.object(corpus, "charger_corpus") as charger,
              contextlib.redirect_stderr(io.StringIO())):
            self.assertEqual(generate.main(self.arguments() + ["--output", str(sortie)]), 1)
        charger.assert_not_called()
        self.assertEqual(sortie.read_bytes(), b"a conserver")

    def test_validation_conserve_ordre_sources_et_verdict_humain_en_attente(self):
        proposition = self.proposition()
        proposition["evidence"].reverse()
        preparation = self.preparation()
        avant = copy.deepcopy((proposition, preparation))
        candidat = self.valider(proposition, preparation)
        self.assertEqual(candidat.id, "SYN_fixture_multi_0001")
        self.assertEqual(candidat.generation_source_ids, [p["passage_id"] for p in self.passages])
        self.assertEqual([p.model_dump() for p in candidat.evidence], proposition["evidence"])
        self.assertEqual(candidat.validation.automatic, "passed")
        self.assertEqual(candidat.validation.human, "pending")
        self.assertIsNone(candidat.validation.answerable_confirmed)
        self.assertIsNone(candidat.validation.reviewer)
        self.assertEqual(candidat.validation.expected_points, [])
        self.assertEqual((proposition, preparation), avant)

    def test_validation_refuse_preparation_ambigue_incomplete_ou_dupliquee(self):
        cas = [{"format": "agent0-preparation-v1"}, {"source": self.passages[0]},
               {"sources": None}, {"sources": []}, {"sources": self.passages[:1]},
               {"sources": [self.passages[0], self.passages[0]]},
               {"sources": [self.passages[0], None]},
               {"sources": [self.passages[0], {**self.passages[1], "texte": " "}]}]
        for changement in cas:
            with self.subTest(changement=changement), self.assertRaises(ValueError):
                self.valider(self.proposition(), {**self.preparation(), **changement})

    def test_validation_refuse_source_manquante_dupliquee_ou_non_fournie(self):
        preuves = self.proposition()["evidence"]
        cas = [preuves[:1], [preuves[0], preuves[0]],
               [preuves[0], {**preuves[1], "passage_id": "fixture-absente"}],
               preuves + [{"passage_id": "fixture-absente", "excerpt": "Témoin absent"}]]
        for evidence in cas:
            with self.subTest(evidence=evidence), self.assertRaises(ValueError):
                self.valider({**self.proposition(), "evidence": evidence})

    def test_validation_exige_extrait_exact_dans_sa_propre_source(self):
        preuves = self.proposition()["evidence"]
        cas = [preuves[1]["excerpt"], preuves[0]["excerpt"].replace("é", "e"),
               preuves[0]["excerpt"] + "\n\n", "extrait inventé", "éteint."]
        for excerpt in cas:
            proposition = self.proposition()
            proposition["evidence"][0]["excerpt"] = excerpt
            with self.subTest(excerpt=excerpt), self.assertRaisesRegex(ValueError, "mot pour mot"):
                self.valider(proposition)

    def test_validation_refuse_doublon_normalise_meme_dans_autre_categorie(self):
        vues = {validation.normaliser_question(self.proposition()["question"].upper())}
        with self.assertRaisesRegex(ValueError, "doublon"):
            self.valider(self.proposition(), vues=vues)

    def test_liste_aplatie_refusee_et_extrait_multiligne_exact_accepte(self):
        preparation = self.preparation()
        texte = "Diagnostic :\n- voyant rouge éteint ;\n- voyant vert allumé."
        preparation["sources"] = copy.deepcopy(preparation["sources"])
        preparation["sources"][1]["texte"] = texte
        proposition = self.proposition()
        proposition["evidence"][1]["excerpt"] = texte
        candidat = self.valider(proposition, preparation)
        self.assertEqual(candidat.evidence[1].excerpt, texte)
        self.assertEqual(candidat.validation.human, "pending")
        proposition["evidence"][1]["excerpt"] = texte.replace("\n", " ")
        with self.assertRaisesRegex(ValueError, "mot pour mot"):
            self.valider(proposition, preparation)

    def test_validation_refuse_verdict_injecte_et_parametres_differents(self):
        for changement in [{"validation": {"human": "accepted"}}, {"answerable_proposed": False},
                           {"difficulty_target": "hard"}, {"type": "adversarial"}]:
            with self.subTest(changement=changement), self.assertRaises(ValueError):
                self.valider({**self.proposition(), **changement})

    def test_run_rejet_multi_conserve_sortie_brute_et_ne_relance_pas(self):
        proposition = self.proposition()
        proposition["evidence"][1]["excerpt"] = "Texte absent"
        reponse = reponse_technique(proposition)
        racine = self.dossier / "runs"
        with (patch.object(client_qwen, "preparer_requete", return_value=requete_technique()),
              patch.object(client_qwen, "_http", return_value=reponse) as http):
            resultat = run.executer(self.preparation(), "rejet_multi", racine)
        http.assert_called_once()
        self.assertEqual(resultat["statut"], "rejet_automatique")
        dossier = racine / "rejet_multi"
        self.assertEqual((dossier / "candidates.jsonl").read_bytes(), b"")
        rejet = json.loads((dossier / "rejected.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(rejet["phase"], "validation_automatique")
        traces = [json.loads(l) for l in (dossier / "traces.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(next(t["resultat"] for t in traces if "resultat" in t)["reponse_brute"],
                         reponse["response"])

    def test_run_multi_tronque_reste_erreur_technique_avant_validation(self):
        reponse = {**reponse_technique(self.proposition()), "done_reason": "length"}
        with (patch.object(client_qwen, "preparer_requete", return_value=requete_technique()),
              patch.object(client_qwen, "_http", return_value=reponse) as http):
            resultat = run.executer(self.preparation(), "tronque_multi", self.dossier / "runs")
        http.assert_called_once()
        self.assertEqual(resultat["statut"], "erreur_technique")
        self.assertIn("generation_incomplete", resultat["motif"])
        dossier = self.dossier / "runs" / "tronque_multi"
        self.assertEqual((dossier / "candidates.jsonl").read_bytes(), b"")


if __name__ == "__main__":
    unittest.main()
