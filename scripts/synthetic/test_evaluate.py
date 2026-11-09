"""Fixtures techniques hors évaluation : aucun modèle ni question juridique."""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np

if __package__:
    from . import evaluate
else:
    import evaluate

from scripts.rag import generation, rag


def index_technique():
    matrice = np.zeros((6, 384), dtype=np.float32)
    matrice[np.arange(6), np.arange(6)] = 1
    passages = [{"passage_id": f"fixture-{i}", "titre_fiche": f"Banc {i}",
                 "section_titre": "Contrôle", "chemin": [], "articles": [],
                 "url": f"https://exemple.test/banc/{i}", "url_citation": f"https://exemple.test/banc/{i}#s",
                 "date_maj": "2000-01-01", "texte": f"Le témoin technique numéro {i} est allumé sur ce banc."}
                for i in range(6)]
    return rag.IndexCommun({"index": {"sha256": "a" * 64},
                            "metadonnees": {"sha256": "b" * 64}}, matrice, passages)


def cas_technique(numero=1):
    # Toutes les mentions de revue sont des fixtures, jamais des décisions réelles.
    return {"schema_version": "synthetic-v1", "set": "synthetic_challenge",
            "id": f"SYN_fixture_{numero:04d}", "run_id": "fixture",
            "question": f"  Position du témoin technique {numero} ?\n", "type": "simple",
            "difficulty_target": "hard", "answerable_proposed": True,
            "generation_reason": "SENTINELLE_RAISON", "generation_source_ids": ["fixture-5"],
            "evidence": [{"passage_id": "fixture-5", "excerpt": index_technique().passages[5]["texte"]}],
            "validation": {"automatic": "passed", "human": "accepted", "answerable_confirmed": True,
                           "reviewer": "Relecteur fictif de test", "review_note": "SENTINELLE_REVUE",
                           "expected_points": ["SENTINELLE_ATTENDU"]}}


def reponse_technique(statut="reponse_citee"):
    return {"statut": statut, "erreurs_techniques": [] if statut != "erreur_technique" else ["generation_incomplete"],
            "reponse_brute": "Témoin technique [P1].", "validation_citations": {
                "statut": "reponse_citee", "citations": ["[P1]"], "citations_invalides": [],
                "justification_semantique_verifiee": False, "couverture_des_affirmations_verifiee": False},
            "ollama": {"version": "fixture", "modele": "fixture", "digest": "c" * 64},
            "entree": {"nb_tokens": 4}, "mesures_ollama": {"done": True, "eval_count": 4}}


class FausseChaine:
    def __init__(self):
        self.index = index_technique()
        self.questions = []
        self.preparations = 0

    def preparer(self):
        self.preparations += 1
        return {"simulation": True, "index": self.index.entete}

    def repondre(self, question):
        self.questions.append(question)
        return {"statut": "abstention_modele", "generation": {"reponse_brute": rag.ABSTENTION}}


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.racine = Path(self.temp.name)
        self.lot = self.racine / "lot"
        self.lot.mkdir()
        self.sorties = self.racine / "resultats"
        self.cas = [cas_technique()]
        self.chaine = FausseChaine()
        self.creer = Mock(return_value=self.chaine)
        self.ecrire()

    def ecrire(self, cas=None, changements=None):
        contenu = b"".join((json.dumps(c, ensure_ascii=False) + "\n").encode("utf-8")
                           for c in (self.cas if cas is None else cas))
        self.manifeste = {"format": "agent0-challenge-v1", "set": "synthetic_challenge",
                          "fige_le": "2000-01-01T00:00:00+00:00", "pilote_independant": True,
                          "note_separation": "Fixture de test, aucun lot réel déclaré",
                          "nb_questions": len(self.cas if cas is None else cas),
                          "sha256_questions": hashlib.sha256(contenu).hexdigest(),
                          "sha256_index": "a" * 64, "sha256_passages": "b" * 64,
                          **(changements or {})}
        (self.lot / "questions.jsonl").write_bytes(contenu)
        (self.lot / "manifest.json").write_text(json.dumps(self.manifeste), encoding="utf-8")

    def executer(self, nom="run"):
        return evaluate.executer(self.lot, nom, self.sorties, self.creer)

    def lire(self, nom, run="run"):
        return json.loads((self.sorties / run / nom).read_text(encoding="utf-8"))

    def lignes(self, nom, run="run"):
        return [json.loads(l) for l in (self.sorties / run / nom).read_text(encoding="utf-8").splitlines()]

    def test_lot_lu_sans_ecriture_et_question_mot_pour_mot(self):
        lot = evaluate.charger_lot(self.lot)
        self.assertEqual(lot.cas[0].question, self.cas[0]["question"])
        self.assertEqual(lot.cas[0].validation.expected_points, ["SENTINELLE_ATTENDU"])
        self.assertFalse(self.sorties.exists())

    def test_separateur_unicode_dans_question_ne_decoupe_pas_le_jsonl(self):
        self.cas[0]["question"] = "  Position\u2028du témoin\u0085technique ?\n"
        self.ecrire()
        self.executer()
        self.assertEqual(self.chaine.questions,[self.cas[0]["question"]])

    def test_grille_historique_vierge_refusee(self):
        historique = evaluate.RACINE / "docs/etudes/agent0_relecture/grille_relecture.json"
        (self.lot / "manifest.json").write_bytes(historique.read_bytes())
        with self.assertRaises(evaluate.ErreurEvaluation):
            self.executer()
        self.creer.assert_not_called()
        self.assertFalse(self.sorties.exists())

    def test_candidat_de_mise_au_point_refuse_meme_marque_accepte(self):
        cas = cas_technique()
        cas.update(id="SYN_simple_001_0001",run_id="simple_001")
        self.ecrire([cas])
        with self.assertRaisesRegex(evaluate.ErreurEvaluation,"mise au point"):
            self.executer()
        self.creer.assert_not_called()
        self.assertFalse(self.sorties.exists())

    def test_inventaire_exclusions_absent_refuse_sans_factory(self):
        with patch.object(evaluate,"RACINE",self.racine), self.assertRaises(evaluate.ErreurEvaluation):
            self.executer()
        self.creer.assert_not_called()

    def test_declarations_incompletes_non_strictes_et_effectifs_refuses(self):
        changements = [{"format": "autre"}, {"set": "gold"}, {"pilote_independant": False},
                       {"pilote_independant": 1}, {"pilote_independant": "true"}, {"note_separation": " "},
                       {"fige_le": "2000-01-01"}, {"fige_le": "2999-01-01T00:00:00Z"},
                       {"nb_questions": True}, {"nb_questions": 0}, {"nb_questions": 26},
                       {"nb_questions": 2}, {"sha256_index": "invalide"}, {"inconnu": 1}]
        for modification in changements:
            with self.subTest(modification=modification):
                self.ecrire(changements=modification)
                with self.assertRaises(evaluate.ErreurEvaluation):
                    self.executer()
                self.creer.assert_not_called()
                self.assertFalse(self.sorties.exists())

    def test_champ_manquant_refuse(self):
        for cle in self.manifeste:
            with self.subTest(cle=cle):
                self.ecrire()
                modifie = {k: v for k, v in self.manifeste.items() if k != cle}
                (self.lot / "manifest.json").write_text(json.dumps(modifie), encoding="utf-8")
                with self.assertRaises(evaluate.ErreurEvaluation):
                    evaluate.charger_lot(self.lot)

    def test_fichier_questions_altere_ou_absent_refuse_avant_factory(self):
        p = self.lot / "questions.jsonl"
        p.write_bytes(p.read_bytes() + b" ")
        with self.assertRaisesRegex(evaluate.ErreurEvaluation, "Empreinte"):
            self.executer()
        p.unlink()
        with self.assertRaises(evaluate.ErreurEvaluation):
            self.executer()
        self.creer.assert_not_called()

    def test_pending_rejected_et_acceptation_incoherente_refuses(self):
        for validation in [{"automatic": "passed", "human": "pending"},
                           {**self.cas[0]["validation"], "human": "rejected"},
                           {**self.cas[0]["validation"], "automatic": "failed"},
                           {**self.cas[0]["validation"], "reviewer": None},
                           {**self.cas[0]["validation"], "expected_points": []},
                           {**self.cas[0]["validation"], "answerable_confirmed": False}]:
            with self.subTest(validation=validation):
                self.ecrire([{**self.cas[0], "validation": validation}])
                with self.assertRaises(evaluate.ErreurEvaluation):
                    self.executer()
        self.creer.assert_not_called()

    def test_lot_vide_identifiants_et_questions_dupliques_refuses(self):
        cas2 = cas_technique(2)
        cas2["question"] = "POSITION DU TÉMOIN TECHNIQUE 1 ?"
        for cas in [[], self.cas * 2, [self.cas[0], cas2]]:
            with self.subTest(cas=cas):
                self.ecrire(cas)
                with self.assertRaises(evaluate.ErreurEvaluation):
                    self.executer()
        self.creer.assert_not_called()

    def test_json_ambigu_utf8_et_constantes_non_finies_refuses(self):
        for nom in ("manifest.json", "questions.jsonl"):
            for contenu in (b"\xff", b"{", b'{"x":1,"x":2}', b'{"x":NaN}'):
                with self.subTest(nom=nom,contenu=contenu):
                    self.ecrire()
                    (self.lot / nom).write_bytes(contenu)
                    if nom == "questions.jsonl":
                        self.manifeste["sha256_questions"] = hashlib.sha256(contenu).hexdigest()
                        (self.lot / "manifest.json").write_text(json.dumps(self.manifeste), encoding="utf-8")
                    with self.assertRaises(evaluate.ErreurEvaluation):
                        self.executer()
        self.creer.assert_not_called()

    def test_factory_recoit_aucun_cas_et_repondre_seulement_le_texte(self):
        resume = self.executer()
        self.creer.assert_called_once_with()
        self.assertEqual(self.chaine.questions, [self.cas[0]["question"]])
        self.assertEqual(self.chaine.preparations, 1)
        self.assertEqual(resume["nb_resultats"], 1)
        self.assertEqual(resume["statut"], "termine")
        self.assertNotIn("evidence", self.lignes("results.jsonl")[0])

    def test_index_et_passages_differents_refuses_avant_preparation_et_generation(self):
        for champ in ("sha256_index", "sha256_passages"):
            with self.subTest(champ=champ):
                self.ecrire(changements={champ: "c" * 64})
                resume = self.executer(champ)
                self.assertEqual(resume["statut"], "erreur_preparation")
                self.assertEqual(self.chaine.preparations, 0)
                self.assertEqual(self.chaine.questions, [])

    def test_source_ou_extrait_altere_refuse_avant_preparation(self):
        for changement in [{"generation_source_ids": ["absent"],
                             "evidence": [{"passage_id": "absent", "excerpt": "Texte absent du corpus technique"}]},
                            {"evidence": [{"passage_id": "fixture-5", "excerpt": "Texte absent du corpus technique"}]}]:
            with self.subTest(changement=changement):
                self.ecrire([{**self.cas[0], **changement}])
                resume = self.executer(str(len(changement)))
                self.assertEqual(resume["statut"], "erreur_preparation")
                self.assertEqual(self.chaine.preparations, 0)
                self.assertEqual(self.chaine.questions, [])

    def test_run_existant_refuse_sans_factory_et_sans_modifier_octets(self):
        self.executer()
        self.creer.reset_mock()
        avant = {p.name:p.read_bytes() for p in (self.sorties / "run").iterdir()}
        with self.assertRaises(FileExistsError):
            self.executer()
        self.creer.assert_not_called()
        self.assertEqual(avant,{p.name:p.read_bytes() for p in (self.sorties / "run").iterdir()})

    def test_run_id_invalide_refuse_sans_ecriture(self):
        for nom in ("../autre", "", "a/b", "a\\b", "a" * 65):
            with self.subTest(nom=nom), self.assertRaises(ValueError):
                self.executer(nom)
        self.assertFalse(self.sorties.exists())

    def test_snapshots_et_empreintes_traces_conformes(self):
        manifeste = (self.lot / "manifest.json").read_bytes()
        questions = (self.lot / "questions.jsonl").read_bytes()
        resume = self.executer()
        self.assertEqual((self.sorties / "run/jeu_manifest.json").read_bytes(), manifeste)
        self.assertEqual((self.sorties / "run/questions.jsonl").read_bytes(), questions)
        for nom,sha in resume["sha256_fichiers"].items():
            self.assertEqual(sha,hashlib.sha256((self.sorties / "run" / nom).read_bytes()).hexdigest())
        self.assertFalse(self.lire("manifest.json")["mesure_officielle"])
        self.assertIn("scripts/rag/generation.py",self.lire("manifest.json")["sha256_code_lf"])
        self.assertEqual([e["evenement"] for e in self.lignes("events.jsonl")],
                         ["debut_question","fin_question"])

    def test_changement_du_lot_apres_lecture_ne_change_pas_snapshot_ni_question(self):
        questions = (self.lot / "questions.jsonl").read_bytes()
        def creer():
            (self.lot / "questions.jsonl").write_bytes(b"modifie apres verification")
            return self.chaine
        self.creer.side_effect = creer
        self.executer()
        self.assertEqual((self.sorties / "run/questions.jsonl").read_bytes(),questions)
        self.assertEqual(self.chaine.questions,[self.cas[0]["question"]])

    def test_exception_par_question_conservee_et_pas_de_nouvel_essai(self):
        self.ecrire([cas_technique(1),cas_technique(2)])
        self.chaine.repondre = Mock(side_effect=[RuntimeError("panne fictive"),
                                                {"statut":"abstention_modele"}])
        resume = self.executer()
        self.assertEqual(self.chaine.repondre.call_count,2)
        self.assertEqual(resume["erreurs_techniques"],1)
        lignes = self.lignes("results.jsonl")
        self.assertEqual(lignes[0]["statut"],"erreur_technique")
        self.assertEqual(lignes[0]["erreur"]["message"],"panne fictive")
        self.assertEqual(lignes[1]["statut"],"abstention_modele")

    def test_preparation_en_echec_conserve_resume_et_snapshots(self):
        self.chaine.preparer = Mock(side_effect=RuntimeError("cache absent"))
        resume = self.executer()
        self.assertEqual(resume["statut"],"erreur_preparation")
        self.assertEqual(resume["nb_resultats"],0)
        self.assertEqual(self.chaine.questions,[])
        self.assertTrue((self.sorties / "run/questions.jsonl").is_file())
        self.assertEqual(self.lire("summary.json"),resume)

    def test_interruption_garde_traces_sans_admission_ni_nouvel_essai(self):
        self.chaine.repondre = Mock(side_effect=KeyboardInterrupt)
        with self.assertRaises(KeyboardInterrupt):
            self.executer()
        self.assertEqual(self.chaine.repondre.call_count,1)
        self.assertEqual(self.lire("summary.json")["statut"],"interrompu")
        self.assertEqual(len(self.lignes("events.jsonl")),1)
        self.assertEqual(self.lignes("results.jsonl"),[])

    def test_cli_check_sans_chaine_ni_modele_ni_dossier_sortie(self):
        with patch.object(evaluate,"ChaineRag") as chaine, contextlib.redirect_stdout(io.StringIO()) as out:
            code = evaluate.main(["--lot",str(self.lot),"--check-lot"])
        self.assertEqual(code,0)
        chaine.assert_not_called()
        self.assertFalse(json.loads(out.getvalue())["ollama_appele"])

    def test_cli_run_et_modele_digest_paires_exiges(self):
        for args in [[],["--modele","autre"],["--digest","c"*64],
                     ["--check-lot","--run-id","essai"],
                     ["--run-id","essai","--modele","autre","--digest","invalide"]]:
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                evaluate.main(["--lot",str(self.lot),*args])

    def test_cli_execution_complete_simulee_et_configuration_modele_transmise(self):
        with patch.object(evaluate,"ChaineRag",return_value=self.chaine) as creer, \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = evaluate.main(["--lot",str(self.lot),"--run-id","cli", "--output-root",str(self.sorties),
                                  "--modele","modele-fixture","--digest","c"*64])
        self.assertEqual(code,0)
        self.assertEqual(json.loads(out.getvalue())["nb_resultats"],1)
        creer.assert_called_once_with(modele="modele-fixture",digest="c"*64)
        self.assertTrue(self.lire("chaine.json","cli")["simulation"])

    def test_cli_echec_preparation_retourne_un_echec_avec_traces(self):
        self.chaine.preparer = Mock(side_effect=RuntimeError("cache absent"))
        with patch.object(evaluate,"ChaineRag",return_value=self.chaine), \
                contextlib.redirect_stdout(io.StringIO()):
            code = evaluate.main(["--lot",str(self.lot),"--run-id","cli","--output-root",str(self.sorties)])
        self.assertEqual(code,1)
        self.assertEqual(self.lire("summary.json","cli")["statut"],"erreur_preparation")

    def test_hors_corpus_confirme_par_fixture_accepte_sans_preuve_positive(self):
        c = cas_technique()
        c.update(type="hors_corpus",answerable_proposed=False,evidence=[],
                 out_of_corpus_reason="Déclaration fictive du test, aucun cas réel",
                 validation={"automatic":"passed","human":"accepted","answerable_confirmed":False,
                             "reviewer":"Relecteur fictif de test","review_note":"Fixture uniquement",
                             "expected_points":[]})
        self.ecrire([c])
        self.assertEqual(self.executer()["statut"],"termine")


class AdaptateurTests(unittest.TestCase):
    def setUp(self):
        self.index = index_technique()
        with patch.object(rag,"charger_index",return_value=self.index):
            self.chaine = evaluate.ChaineRag()
        self.encodeur = Mock()
        self.encodeur.tokenizer.return_value = {"input_ids":[1,2]}
        vecteur = np.zeros((1,384),dtype=np.float32)
        vecteur[0,0] = 1
        self.encodeur.encode.return_value = vecteur
        self.chaine.encodeur = self.encodeur

    def test_vrais_helpers_cinq_passages_et_aucune_annotation_attendue_dans_prompt(self):
        question = cas_technique()["question"]
        with patch.object(generation,"generer_reponse",return_value=reponse_technique()) as generer:
            retour = self.chaine.repondre(question)
        self.assertEqual([r["passage"]["passage_id"] for r in retour["resultats"]],
                         [f"fixture-{i}" for i in range(5)])
        contexte = generer.call_args.args[0]
        self.assertIn(question,contexte["prompt"])
        self.assertEqual([s["reference"] for s in contexte["sources"]],[f"[P{i}]" for i in range(1,6)])
        self.assertEqual(self.encodeur.encode.call_args.args[0],["query: "+question])
        for sentinelle in ["SENTINELLE_ATTENDU","SENTINELLE_REVUE","SENTINELLE_RAISON","fixture-5"]:
            self.assertNotIn(sentinelle,contexte["prompt"])
        self.assertEqual(retour["generation"]["reponse_brute"],"Témoin technique [P1].")
        self.assertEqual(retour["statut"],"reponse_citee")

    def test_generation_interrompue_prime_sur_citations_et_garde_brut(self):
        g = reponse_technique("erreur_technique")
        with patch.object(generation,"generer_reponse",return_value=g):
            retour = self.chaine.repondre("Fixture de contrôle ?")
        self.assertEqual(retour["statut"],"erreur_technique")
        self.assertEqual(retour["generation"],g)

    def test_budget_ou_api_en_echec_garde_recuperation_et_contexte(self):
        with patch.object(generation,"generer_reponse",side_effect=generation.ErreurGeneration("Budget dépassé")):
            retour = self.chaine.repondre("Fixture de contrôle ?")
        self.assertEqual(retour["statut"],"erreur_technique")
        self.assertEqual(len(retour["resultats"]),5)
        self.assertIsNotNone(retour["contexte"])
        self.assertEqual(retour["erreur"]["phase"],"generation")

    def test_e5_en_echec_ne_lance_pas_generation(self):
        self.encodeur.tokenizer.side_effect = rag.ErreurRecuperation("fixture trop longue")
        with patch.object(generation,"generer_reponse") as generer:
            retour = self.chaine.repondre("Fixture de contrôle ?")
        generer.assert_not_called()
        self.assertEqual(retour["statut"],"erreur_technique")
        self.assertEqual(retour["erreur"]["phase"],"recuperation")

    def test_preparer_versions_et_configuration_modele_explicitement_tracees(self):
        infos = {"version":"fixture","modele":"fixture-modele","digest":"c"*64,"template":"fixture-template"}
        with patch.object(rag,"charger_encodeur",return_value=self.encodeur), \
                patch.object(generation,"verifier_ollama",return_value=infos) as verifier:
            meta = self.chaine.preparer()
        verifier.assert_called_once_with(generation.MODELE_QWEN,generation.DIGEST_QWEN_31)
        self.assertEqual(meta["ollama"],infos)
        self.assertEqual(meta["precision_e5"],"fp32")
        self.assertEqual(meta["top_k"],5)
        self.assertIsNone(meta["seuil"])


if __name__ == "__main__":
    unittest.main()
