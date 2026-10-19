"""Préparation hors ligne sur des fixtures techniques, sans question réglementaire."""

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
    from . import client_qwen, corpus, generate, prompts, schema
    from .test_corpus import exporter, passages_techniques
else:
    import client_qwen
    import corpus
    import generate
    import prompts
    import schema
    from test_corpus import exporter, passages_techniques


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dossier = Path(self.temp.name)
        exporter(self.dossier)
        self.source = corpus.charger_corpus(self.dossier)
        self.code = {"git_commit": "a" * 40, "git_dirty": False, "python": "fixture",
                     "sha256_corpus_py": "b" * 64}
        self.selection = corpus.creer_manifeste(
            self.source, corpus.selectionner(self.source, 2, 42), "fiches", 42, self.code)
        self.chemin = self.dossier / "selection.json"
        self.ecrire(self.selection)

    def ecrire(self, selection):
        self.chemin.write_text(json.dumps(selection, ensure_ascii=False), encoding="utf-8")

    def arguments(self):
        return ["--prepare-only", "--sources", str(self.chemin), "--type", "simple",
                "--index-dir", str(self.dossier)]

    def test_source_exacte_et_schema_communs_aux_deux_prompts(self):
        passage = passages_techniques()[0]
        avant = copy.deepcopy(passage)
        for categorie in ("simple", "reformulation"):
            with self.subTest(categorie=categorie):
                prompt = prompts.preparer_prompt(passage, categorie, "medium")
                self.assertEqual(prompt["version"], prompts.VERSION_PROMPT)
                self.assertEqual(prompt["response_schema"], schema.schema_generation())
                self.assertEqual([m["role"] for m in prompt["messages"]], ["system", "user"])
                texte = prompt["messages"][1]["content"]
                self.assertIn(json.dumps(passage, ensure_ascii=False, indent=2), texte)
                self.assertIn(f"Catégorie imposée : {categorie}", texte)
                self.assertIn("Difficulté cible imposée : medium", texte)
        self.assertEqual(passage, avant)

    def test_reformulation_a_une_consigne_distincte_et_aucun_exemple_de_question(self):
        passage = passages_techniques()[0]
        simple = prompts.preparer_prompt(passage, "simple")
        reformulation = prompts.preparer_prompt(passage, "reformulation")
        self.assertNotEqual(simple["messages"][1], reformulation["messages"][1])
        self.assertIn(prompts.CONSIGNES["simple"], simple["messages"][1]["content"])
        self.assertIn(prompts.CONSIGNES["reformulation"], reformulation["messages"][1]["content"])

    def test_prompt_refuse_source_ou_parametres_non_pris_en_charge(self):
        for passage, categorie, difficulte in [({}, "simple", "easy"),
                ({"passage_id": "fixture", "texte": " "}, "simple", "easy"),
                (passages_techniques()[0], "multi_passage", "easy"),
                (passages_techniques()[0], "simple", "mesuree")]:
            with self.subTest(categorie=categorie, difficulte=difficulte), self.assertRaises(ValueError):
                prompts.preparer_prompt(passage, categorie, difficulte)

    def test_selection_relue_avec_empreinte_des_octets(self):
        selection, empreinte = generate.charger_selection(self.chemin, self.source)
        self.assertEqual(selection, self.selection)
        self.assertEqual(empreinte, hashlib.sha256(self.chemin.read_bytes()).hexdigest())
        self.selection["mode"], self.selection["graine"] = "ids", None
        self.ecrire(self.selection)
        self.assertEqual(generate.charger_selection(self.chemin, self.source)[0], self.selection)

    def test_selection_refuse_autre_format_corpus_mode_ou_graine(self):
        cas = [{"format": "autre"}, {"algorithme": "autre"}, {"mode": "autre"},
               {"graine": True}, {"mode": "ids", "graine": 42},
               {"ollama_appele": True}, {"matrice_lue": 0}, {"code": None},
               {"corpus": None}, {"corpus": {**self.selection["corpus"], "sha256_passages": "c" * 64}},
               {"corpus": {**self.selection["corpus"], "nb_fiches": True}}]
        for changement in cas:
            with self.subTest(changement=changement), self.assertRaises(generate.ErreurPreparation):
                self.ecrire({**self.selection, **changement})
                generate.charger_selection(self.chemin, self.source)

    def test_selection_refuse_source_inconnue_dupliquee_ou_modifiee(self):
        for champ, valeur in [("passage_id", "absent"), ("texte", "Texte modifié"),
                              ("titre_fiche", "Titre modifié"), ("url", "https://example.invalid/autre")]:
            selection = copy.deepcopy(self.selection)
            selection["groupes"][1][0][champ] = valeur
            with self.subTest(champ=champ), self.assertRaises(generate.ErreurPreparation):
                self.ecrire(selection)
                generate.charger_selection(self.chemin, self.source)
        selection = copy.deepcopy(self.selection)
        selection["groupes"][1] = selection["groupes"][0]
        self.ecrire(selection)
        with self.assertRaises(generate.ErreurPreparation):
            generate.charger_selection(self.chemin, self.source)

    def test_selection_refuse_groupes_vides_et_structures_invalides(self):
        for groupes in [None, [], [[]], [None], [[None]], [[{"passage_id": []}]]]:
            with self.subTest(groupes=groupes), self.assertRaises(generate.ErreurPreparation):
                self.ecrire({**self.selection, "groupes": groupes})
                generate.charger_selection(self.chemin, self.source)

    def test_selection_refuse_json_utf8_ambigus_ou_incomplets(self):
        for octets in [b"\xff", b"{", b"[]", b'{"format":1,"format":2}', b'{"valeur":NaN}']:
            with self.subTest(octets=octets), self.assertRaises((ValueError, UnicodeDecodeError)):
                self.chemin.write_bytes(octets)
                generate.charger_selection(self.chemin, self.source)

    def test_preparation_reproductible_sans_troncature_ni_verdict(self):
        selection, empreinte = generate.charger_selection(self.chemin, self.source)
        avant = copy.deepcopy(selection)
        un = generate.preparer(selection, empreinte, 2, "reformulation", "hard")
        self.assertEqual(un, generate.preparer(selection, empreinte, 2, "reformulation", "hard"))
        self.assertEqual(un["source"], selection["groupes"][1][0])
        self.assertEqual(un["selection"]["code"], self.code)
        self.assertEqual(un["selection"]["sha256_fichier"], empreinte)
        self.assertEqual(len(un["sha256_prompt"]), 64)
        self.assertNotEqual(un["sha256_prompt"],
                            generate.preparer(selection, empreinte, 2, "simple", "hard")["sha256_prompt"])
        self.assertFalse(un["ollama_appele"])
        self.assertFalse(un["budget_tokens_verifie"])
        self.assertNotIn("validation", un)
        self.assertEqual(selection, avant)

    def test_refuse_groupe_hors_limites_ou_paire(self):
        for groupe in [0, -1, 3, True, "1"]:
            with self.subTest(groupe=groupe), self.assertRaises(generate.ErreurPreparation):
                generate.preparer(self.selection, "b" * 64, groupe, "simple")
        paire = corpus.creer_manifeste(self.source, corpus.selectionner(self.source, 1, 42, True),
                                      "paires", 42, self.code)
        with self.assertRaises(generate.ErreurPreparation):
            generate.preparer(paire, "b" * 64, 1, "simple")

    def test_cli_sauvegarde_et_resume_sans_reseau(self):
        sortie = self.dossier / "preparations" / "essai.json"
        avant = self.chemin.read_bytes()
        with (patch.object(corpus, "provenance_code", return_value=copy.deepcopy(self.code)),
              patch("urllib.request.urlopen", side_effect=AssertionError("Réseau interdit")) as reseau,
              contextlib.redirect_stdout(io.StringIO()) as stdout):
            self.assertEqual(generate.main(self.arguments() + ["--output", str(sortie)]), 0)
        reseau.assert_not_called()
        resume = json.loads(stdout.getvalue())
        preparation = json.loads(sortie.read_text(encoding="utf-8"))
        self.assertEqual(resume["statut"], "prompt_prepare")
        self.assertEqual(resume["sha256_prompt"], preparation["sha256_prompt"])
        self.assertEqual(preparation["source"], self.selection["groupes"][0][0])
        self.assertEqual(set(preparation["code"]["sha256_fichiers"]),
                         {"generate.py", "prompts.py", "schema.py"})
        self.assertEqual(self.chemin.read_bytes(), avant)

    def test_cli_affiche_preparation_complete_sans_sortie(self):
        with (patch.object(corpus, "provenance_code", return_value=copy.deepcopy(self.code)),
              contextlib.redirect_stdout(io.StringIO()) as stdout):
            self.assertEqual(generate.main(self.arguments()), 0)
        self.assertIn("messages", json.loads(stdout.getvalue())["prompt"])

    def test_cli_refuse_ecrasement_et_entree_absente(self):
        sortie = self.dossier / "conserver.json"
        sortie.write_bytes(b"a conserver")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(generate.main(self.arguments() + ["--output", str(sortie)]), 1)
            self.chemin.unlink()
            self.assertEqual(generate.main(self.arguments()), 1)
        self.assertEqual(sortie.read_bytes(), b"a conserver")

    def test_cli_exige_mode_explicite_et_categories_disponibles(self):
        for arguments in [self.arguments()[1:], self.arguments() + ["--type", "hors_corpus"],
                          self.arguments() + ["--difficulty", "mesuree"]]:
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as erreur:
                    generate.main(arguments)
                self.assertEqual(erreur.exception.code, 2)

    def test_cli_budget_et_requete_sauvegardes_sans_generation(self):
        sortie = self.dossier / "budget.json"
        qwen = {"ollama": {"version": "fixture", "modele": "fixture", "digest": "fixture"},
                "entree": {"texte": "fixture raw", "nb_tokens_hf": 12}, "versions": {},
                "requete": {"prompt": "fixture raw"}, "generation_appelee": False}
        arguments = ["--prepare-qwen", *self.arguments()[1:], "--output", str(sortie)]
        with (patch.object(corpus, "provenance_code", return_value=copy.deepcopy(self.code)),
              patch.object(client_qwen, "preparer_requete", return_value=qwen) as preparer,
              contextlib.redirect_stdout(io.StringIO()) as stdout):
            self.assertEqual(generate.main(arguments), 0)
        sauvegarde = json.loads(sortie.read_text(encoding="utf-8"))
        self.assertEqual(sauvegarde["statut"], "requete_preparee")
        self.assertTrue(sauvegarde["budget_tokens_verifie"])
        self.assertTrue(sauvegarde["ollama_appele"])
        self.assertFalse(sauvegarde["generation_appelee"])
        self.assertEqual(sauvegarde["qwen"], qwen)
        self.assertEqual(json.loads(stdout.getvalue())["budget"]["nb_tokens_hf"], 12)
        self.assertEqual(preparer.call_args.args[0], sauvegarde["prompt"])
        self.assertFalse(preparer.call_args.args[1])

    def test_cli_refus_budget_sans_fichier_et_sortie_existante_sans_api(self):
        sortie = self.dossier / "budget.json"
        arguments = ["--prepare-qwen", *self.arguments()[1:], "--output", str(sortie)]
        with (patch.object(corpus, "provenance_code", return_value=copy.deepcopy(self.code)),
              patch.object(client_qwen, "preparer_requete", side_effect=client_qwen.ErreurQwen("budget")),
              contextlib.redirect_stderr(io.StringIO())):
            self.assertEqual(generate.main(arguments), 1)
        self.assertFalse(sortie.exists())
        sortie.write_bytes(b"a conserver")
        with (patch.object(client_qwen, "preparer_requete") as preparer,
              contextlib.redirect_stderr(io.StringIO())):
            self.assertEqual(generate.main(arguments), 1)
        preparer.assert_not_called()
        self.assertEqual(sortie.read_bytes(), b"a conserver")

    def test_cli_refuse_telechargement_en_mode_hors_ligne(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as erreur:
                generate.main(self.arguments() + ["--allow-tokenizer-download"])
        self.assertEqual(erreur.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
