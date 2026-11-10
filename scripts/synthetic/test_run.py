"""Génération simulée et stockage sur fixtures techniques, sans question juridique."""

import base64
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

if __package__:
    from . import client_qwen, corpus, generate, prompts, run, schema, validation
    from .test_corpus import exporter, passages_techniques
else:
    import client_qwen
    import corpus
    import generate
    import prompts
    import run
    import schema
    import validation
    from test_corpus import exporter, passages_techniques


def preparation_technique():
    source = passages_techniques()[0]
    return {"source": source, "type": "simple", "difficulty_target": "easy",
            "prompt": prompts.preparer_prompt(source, "simple")}


def proposition_technique():
    return {"question": "Où se trouve le témoin ?", "type": "simple", "difficulty_target": "easy",
            "answerable_proposed": True, "generation_reason": "Fixture technique",
            "evidence": [{"passage_id": "fixture-a-0",
                          "excerpt": passages_techniques()[0]["texte"].strip()}]}


def requete_technique():
    return {"requete": {"model": client_qwen.MODELE_QWEN, "prompt": "fixture raw",
                       "options": copy.deepcopy(client_qwen.OPTIONS), "format": schema.schema_generation(),
                       "raw": True, "stream": False, "keep_alive": "30m"},
            "entree": {"nb_tokens_hf": 12}, "ollama": {"version": "fixture"}, "versions": {}}


def reponse_technique(proposition=None):
    texte = json.dumps(proposition_technique() if proposition is None else proposition, ensure_ascii=False)
    return {"response": texte, "model": client_qwen.MODELE_QWEN, "done": True, "done_reason": "stop",
            "prompt_eval_count": 12, "eval_count": 40, "total_duration": 123}


class ValidationTests(unittest.TestCase):
    def valider(self, proposition, vues=None, preparation=None):
        return validation.valider_proposition(json.dumps(proposition, ensure_ascii=False),
            preparation_technique() if preparation is None else preparation,
            "fixture", set() if vues is None else vues)

    def test_candidat_source_identite_et_humain_en_attente(self):
        proposition = proposition_technique()
        avant = copy.deepcopy(proposition)
        candidat = self.valider(proposition)
        self.assertEqual(candidat.id, "SYN_fixture_0001")
        self.assertEqual(candidat.generation_source_ids, ["fixture-a-0"])
        self.assertEqual(candidat.validation.automatic, "passed")
        self.assertEqual(candidat.validation.human, "pending")
        self.assertIsNone(candidat.validation.answerable_confirmed)
        self.assertEqual(candidat.validation.expected_points, [])
        self.assertEqual(proposition, avant)

    def test_mauvaise_categorie_ou_difficulte_refusee(self):
        for champ, valeur in [("type", "reformulation"), ("difficulty_target", "hard")]:
            proposition = proposition_technique()
            proposition[champ] = valeur
            with self.subTest(champ=champ), self.assertRaisesRegex(ValueError, "différente"):
                self.valider(proposition)

    def test_source_absente_et_extrait_modifie_refuses(self):
        extrait = proposition_technique()["evidence"][0]["excerpt"]
        for champ, valeur in [("passage_id", "fixture-absente"),
                              ("excerpt", extrait.replace("é", "e")),
                              ("excerpt", extrait + "\n\n"),
                              ("excerpt", "Autre texte suffisamment long.")]:
            proposition = proposition_technique()
            proposition["evidence"][0][champ] = valeur
            with self.subTest(champ=champ, valeur=valeur), self.assertRaises(ValueError):
                self.valider(proposition)

    def test_fragments_courts_refuses_meme_presents(self):
        preparation = preparation_technique()
        preparation["source"]["texte"] = (
            "Le voyant technique est long et mentionné dans le diagnostic. Voyant technique ba.")
        for extrait in ["ng", "le", "nn", "Voyant technique ba"]:
            proposition = proposition_technique()
            proposition["evidence"][0]["excerpt"] = extrait
            self.assertIn(extrait, preparation["source"]["texte"])
            with self.subTest(extrait=extrait), self.assertRaisesRegex(ValueError, "20 caractères"):
                self.valider(proposition, preparation=preparation)

    def test_extrait_vingt_caracteres_et_ponctuation_conserves(self):
        minimum = "Voyant technique bas"
        self.assertEqual(len(minimum), 20)
        for extrait in [minimum, "Voyant technique [OK]."]:
            preparation = preparation_technique()
            preparation["source"]["texte"] = f"Diagnostic : « {extrait} » ; fin."
            proposition = proposition_technique()
            proposition["evidence"][0]["excerpt"] = extrait
            avant = copy.deepcopy(preparation)
            with self.subTest(extrait=extrait):
                candidat = self.valider(proposition, preparation=preparation)
                self.assertEqual(candidat.evidence[0].excerpt, extrait)
                self.assertEqual(candidat.validation.human, "pending")
                self.assertEqual(preparation, avant)

    def test_limites_mots_unicode_et_espaces_bord_controles(self):
        extrait = "Voyant technique bas"
        cas = [(extrait, "pré" + extrait), (extrait, extrait + "é"),
               (extrait, extrait + "_suite"), (" " + extrait, " " + extrait),
               (extrait + " ", extrait + " "), ("\u00a0" + extrait, "\u00a0" + extrait)]
        for preuve, texte in cas:
            preparation = preparation_technique()
            preparation["source"]["texte"] = texte
            proposition = proposition_technique()
            proposition["evidence"][0]["excerpt"] = preuve
            self.assertIn(preuve, texte)
            with self.subTest(preuve=preuve, texte=texte), self.assertRaises(ValueError):
                self.valider(proposition, preparation=preparation)

    def test_occurrence_alignee_apres_fragment_dans_un_mot_acceptee(self):
        extrait = "Voyant technique bas"
        preparation = preparation_technique()
        preparation["source"]["texte"] = "pré" + extrait + ". Puis : " + extrait + "."
        proposition = proposition_technique()
        proposition["evidence"][0]["excerpt"] = extrait
        self.assertEqual(self.valider(proposition, preparation=preparation).evidence[0].excerpt,
                         extrait)

    def test_multiligne_lf_crlf_exacts_sans_normalisation(self):
        for separateur, autre in [("\n", "\r\n"), ("\r\n", "\n")]:
            extrait = separateur.join(["Voyant rouge éteint.", "Voyant vert allumé."])
            preparation = preparation_technique()
            preparation["source"]["texte"] = extrait
            proposition = proposition_technique()
            proposition["evidence"][0]["excerpt"] = extrait
            with self.subTest(separateur=repr(separateur)):
                self.assertEqual(self.valider(proposition, preparation=preparation).evidence[0].excerpt,
                                 extrait)
                for modifie in [extrait.replace(separateur, autre), extrait.replace(separateur, " ")]:
                    proposition["evidence"][0]["excerpt"] = modifie
                    with self.subTest(modifie=repr(modifie)), self.assertRaises(ValueError):
                        self.valider(proposition, preparation=preparation)
                self.assertEqual(preparation["source"]["texte"], extrait)

    def test_json_entoure_ambigu_et_metadonnees_qwen_refuses(self):
        valide = json.dumps(proposition_technique(), ensure_ascii=False)
        cas = ["```json\n" + valide + "\n```", valide[:-1],
               valide[:-1] + ',"question":"autre"}',
               json.dumps({**proposition_technique(), "validation": {"human": "accepted"}})]
        for texte in cas:
            with self.subTest(texte=texte[:20]), self.assertRaises(ValueError):
                validation.valider_proposition(texte, preparation_technique(), "fixture", set())

    def test_doublon_normalise_et_question_vide_refuses_sans_changer_le_texte(self):
        normalisee = validation.normaliser_question("Où se trouve le témoin ?")
        proposition = proposition_technique()
        proposition["question"] = "  OÙ  SE TROUVE LE TÉMOIN？？ "
        with self.assertRaisesRegex(ValueError, "doublon"):
            self.valider(proposition, {normalisee})
        proposition["question"] = " ??? "
        with self.assertRaises(ValueError):
            self.valider(proposition)
        proposition["question"] = "  Où est placé ce témoin ?\n"
        self.assertEqual(self.valider(proposition, {normalisee}).question, proposition["question"])

    def test_chargement_candidats_tracable_et_fichier_corrompu_refuse(self):
        with tempfile.TemporaryDirectory() as temp:
            dossier = Path(temp)
            chemin = dossier / "fixture" / "candidates.jsonl"
            chemin.parent.mkdir()
            candidat = self.valider(proposition_technique())
            chemin.write_text(candidat.model_dump_json() + "\n", encoding="utf-8")
            vues, fichiers = validation.charger_questions_vues(dossier)
            self.assertEqual(vues, {validation.normaliser_question(candidat.question)})
            self.assertEqual(fichiers, [{"fichier": "fixture/candidates.jsonl",
                "sha256": hashlib.sha256(chemin.read_bytes()).hexdigest()}])
            self.assertEqual(validation.charger_questions_vues(dossier, chemin.parent), (set(), []))
            chemin.write_text("corrompu", encoding="utf-8")
            with self.assertRaises(ValueError):
                validation.charger_questions_vues(dossier)


class GenerationClientTests(unittest.TestCase):
    def test_un_appel_local_raw_structure_avec_delai_et_sortie_intacte(self):
        reponse = reponse_technique()
        with patch.object(client_qwen.urllib.request, "urlopen") as ouvrir:
            ouvrir.return_value.__enter__.return_value.read.return_value = json.dumps(reponse).encode("utf-8")
            resultat = client_qwen.generer(requete_technique())
        ouvrir.assert_called_once()
        requete = ouvrir.call_args.args[0]
        self.assertEqual(requete.full_url, "http://127.0.0.1:11434/api/generate")
        self.assertEqual(json.loads(requete.data), requete_technique()["requete"])
        self.assertEqual(ouvrir.call_args.kwargs["timeout"], 300)
        self.assertEqual(resultat["reponse_ollama"], reponse)
        self.assertEqual(resultat["reponse_brute"], reponse["response"])
        self.assertEqual(resultat["erreurs_techniques"], [])

    def test_sorties_interrompues_comptes_et_modeles_incoherents_refuses(self):
        for changement, motif in [({"done": False}, "generation_incomplete"),
                ({"done_reason": "length"}, "generation_incomplete"),
                ({"prompt_eval_count": 13}, "comptage_hf_ollama_different"),
                ({"prompt_eval_count": True}, "comptage_hf_ollama_different"),
                ({"eval_count": 0}, "nombre_tokens_sortie_invalide"),
                ({"eval_count": 513}, "nombre_tokens_sortie_invalide"),
                ({"model": "autre"}, "modele_retourne_inattendu"),
                ({"response": None}, "reponse_textuelle_absente")]:
            reponse = {**reponse_technique(), **changement}
            with self.subTest(changement=changement), patch.object(client_qwen, "_http", return_value=reponse):
                resultat = client_qwen.generer(requete_technique())
            self.assertIn(motif, resultat["erreurs_techniques"])
            self.assertEqual(resultat["reponse_ollama"], reponse)

    def test_http_invalide_et_corps_non_utf8_conserves(self):
        erreur = urllib.error.HTTPError("fixture", 503, "indisponible", {}, io.BytesIO(b"corps erreur"))
        with patch.object(client_qwen.urllib.request, "urlopen", side_effect=erreur):
            with self.assertRaises(client_qwen.ErreurQwen) as contexte:
                client_qwen.generer(requete_technique())
        self.assertEqual(contexte.exception.diagnostic["http_status"], 503)
        self.assertEqual(base64.b64decode(contexte.exception.diagnostic["corps_http_base64"]), b"corps erreur")
        for octets in [b"\xff", b"{", b'{"error":"fixture"}']:
            with self.subTest(octets=octets), patch.object(client_qwen.urllib.request, "urlopen") as ouvrir:
                ouvrir.return_value.__enter__.return_value.read.return_value = octets
                with self.assertRaises(client_qwen.ErreurQwen) as contexte:
                    client_qwen.generer(requete_technique())
                self.assertEqual(base64.b64decode(contexte.exception.diagnostic["corps_http_base64"]), octets)


class RunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.racine = Path(self.temp.name) / "runs"

    def executer(self, run_id="fixture", reponse=None, preparation=None):
        with (patch.object(client_qwen, "preparer_requete", return_value=requete_technique()),
              patch.object(client_qwen, "_http", return_value=reponse_technique() if reponse is None else reponse) as http):
            resultat = run.executer(preparation_technique() if preparation is None else preparation, run_id, self.racine)
        return resultat, http

    def lire_lignes(self, run_id, nom):
        return [json.loads(ligne) for ligne in (self.racine / run_id / nom).read_text(encoding="utf-8").splitlines()]

    def test_succes_cinq_fichiers_sources_et_entrees_sorties_conserves(self):
        resultat, http = self.executer()
        http.assert_called_once()
        self.assertEqual(resultat["statut"], "candidat_prepare")
        self.assertEqual(resultat["nb_candidats"], 1)
        self.assertEqual(resultat["nb_rejets"], 0)
        dossier = self.racine / "fixture"
        self.assertEqual({p.name for p in dossier.iterdir()},
                         {"manifest.json", "traces.jsonl", "candidates.jsonl", "rejected.jsonl", "summary.json"})
        manifeste = json.loads((dossier / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifeste["preparation"], preparation_technique())
        candidat = schema.CasSynthetique.model_validate(self.lire_lignes("fixture", "candidates.jsonl")[0])
        self.assertEqual(candidat.validation.human, "pending")
        self.assertEqual(self.lire_lignes("fixture", "rejected.jsonl"), [])
        traces = self.lire_lignes("fixture", "traces.jsonl")
        self.assertEqual(traces[1]["qwen"]["requete"], requete_technique()["requete"])
        self.assertEqual(next(t["resultat"] for t in traces if "resultat" in t)["reponse_ollama"],
                         reponse_technique())
        self.assertEqual(resultat["mesures"]["nb_tokens_hf"], resultat["mesures"]["prompt_eval_count"])

    def test_reformulation_egalement_generee_avec_controles_simules(self):
        preparation = preparation_technique()
        preparation["type"] = "reformulation"
        proposition = {**proposition_technique(), "type": "reformulation"}
        resultat, _ = self.executer(reponse=reponse_technique(proposition), preparation=preparation)
        self.assertEqual(resultat["statut"], "candidat_prepare")
        self.assertEqual(self.lire_lignes("fixture", "candidates.jsonl")[0]["type"], "reformulation")

    def test_rejets_json_source_et_extrait_conservent_sortie_brute(self):
        for i, changement in enumerate([{"response": "```json\n{}\n```"},
                {"response": json.dumps({**proposition_technique(), "evidence": [
                    {"passage_id": "absent", "excerpt": "éteint."}]})},
                {"response": json.dumps({**proposition_technique(), "evidence": [
                    {"passage_id": "fixture-a-0", "excerpt": "inventé"}]})},
                {"response": json.dumps({**proposition_technique(), "evidence": [
                    {"passage_id": "fixture-a-0", "excerpt": "éteint."}]})}]):
            run_id = f"rejet_{i}"
            reponse = {**reponse_technique(), **changement}
            resultat, http = self.executer(run_id, reponse)
            http.assert_called_once()
            self.assertEqual(resultat["statut"], "rejet_automatique")
            self.assertEqual(self.lire_lignes(run_id, "candidates.jsonl"), [])
            self.assertEqual(len(self.lire_lignes(run_id, "rejected.jsonl")), 1)
            traces = self.lire_lignes(run_id, "traces.jsonl")
            self.assertEqual(next(t["resultat"] for t in traces if "resultat" in t)["reponse_brute"],
                             reponse["response"])

    def test_erreur_technique_prioritaire_sur_json_valide(self):
        resultat, _ = self.executer(reponse={**reponse_technique(), "done_reason": "length"})
        self.assertEqual(resultat["statut"], "erreur_technique")
        self.assertEqual(self.lire_lignes("fixture", "candidates.jsonl"), [])
        self.assertIn("generation_incomplete", self.lire_lignes("fixture", "rejected.jsonl")[0]["motif"])

    def test_erreur_preparation_et_delai_conserves_sans_relance(self):
        with patch.object(client_qwen, "preparer_requete", side_effect=client_qwen.ErreurQwen("cache")):
            resultat = run.executer(preparation_technique(), "cache", self.racine)
        self.assertFalse(resultat["generation_tentee"])
        self.assertEqual(self.lire_lignes("cache", "rejected.jsonl")[0]["phase"], "preparation_qwen")
        with (patch.object(client_qwen, "preparer_requete", return_value=requete_technique()),
              patch.object(client_qwen.urllib.request, "urlopen", side_effect=TimeoutError("fixture")) as ouvrir):
            resultat = run.executer(preparation_technique(), "delai", self.racine)
        ouvrir.assert_called_once()
        self.assertTrue(resultat["generation_tentee"])
        self.assertFalse(resultat["generation_reponse_recue"])
        rejet = self.lire_lignes("delai", "rejected.jsonl")[0]
        self.assertEqual(rejet["diagnostic"]["requete"], requete_technique()["requete"])

    def test_dossier_existant_et_run_id_invalide_refuses_avant_api(self):
        self.executer()
        avant = {p.name: p.read_bytes() for p in (self.racine / "fixture").iterdir()}
        with patch.object(client_qwen, "preparer_requete") as preparer:
            with self.assertRaises(FileExistsError):
                run.executer(preparation_technique(), "fixture", self.racine)
            for run_id in ["../sortie", "", "a" * 65]:
                with self.subTest(run_id=run_id), self.assertRaises(ValueError):
                    run.executer(preparation_technique(), run_id, self.racine)
        preparer.assert_not_called()
        self.assertEqual(avant, {p.name: p.read_bytes() for p in (self.racine / "fixture").iterdir()})

    def test_doublon_d_un_autre_run_refuse_et_instantane_trace(self):
        self.executer("premier")
        resultat, _ = self.executer("second")
        self.assertEqual(resultat["statut"], "rejet_automatique")
        self.assertIn("doublon", resultat["motif"])
        antecedents = self.lire_lignes("second", "traces.jsonl")[0]["fichiers"]
        self.assertEqual([p["fichier"] for p in antecedents], ["premier/candidates.jsonl"])

    def test_ancien_fichier_corrompu_bloque_avant_modele(self):
        chemin = self.racine / "ancien" / "candidates.jsonl"
        chemin.parent.mkdir(parents=True)
        chemin.write_bytes(b"corrompu")
        with patch.object(client_qwen, "preparer_requete") as preparer:
            resultat = run.executer(preparation_technique(), "nouveau", self.racine)
        preparer.assert_not_called()
        self.assertEqual(resultat["statut"], "erreur_technique")
        self.assertEqual(self.lire_lignes("nouveau", "rejected.jsonl")[0]["phase"], "deduplication")

    def test_cli_generation_et_arguments_exclusifs(self):
        index = Path(self.temp.name) / "index"
        index.mkdir()
        exporter(index)
        source = corpus.charger_corpus(index)
        selection = corpus.creer_manifeste(source, [[source.passages[0]]], "ids", None, {})
        chemin = Path(self.temp.name) / "selection.json"
        corpus.enregistrer_manifeste(selection, chemin)
        arguments = ["--generate", "--run-id", "cli", "--sources", str(chemin),
                     "--index-dir", str(index), "--type", "simple"]
        with (patch.object(corpus, "provenance_code", return_value={"git_commit": "a" * 40}),
              patch.object(generate, "DOSSIER_RUNS", self.racine),
              patch.object(client_qwen, "preparer_requete", return_value=requete_technique()),
              patch.object(client_qwen, "_http", return_value=reponse_technique()),
              contextlib.redirect_stdout(io.StringIO()) as stdout):
            self.assertEqual(generate.main(arguments), 0)
        self.assertEqual(json.loads(stdout.getvalue())["statut"], "candidat_prepare")
        for cas in [arguments + ["--output", "interdit.json"],
                    [a for a in arguments if a not in ("--run-id", "cli")],
                    ["--prepare-only", *arguments[1:]]]:
            with self.subTest(cas=cas), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as erreur:
                    generate.main(cas)
                self.assertEqual(erreur.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
