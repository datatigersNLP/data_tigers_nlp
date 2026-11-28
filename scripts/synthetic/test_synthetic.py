"""Fixtures techniques uniquement : aucune question du Gold/Challenge Set n'est créée."""

import copy
import json
import unittest

from pydantic import ValidationError

if __package__:
    from .schema import (CasSynthetique, Proposition, ValidationCas, creer_candidat,
                         lire_proposition, schema_generation)
else:
    from schema import (CasSynthetique, Proposition, ValidationCas, creer_candidat,
                        lire_proposition, schema_generation)


def donnees_proposition():
    return {
        "question": "  Fixture technique, hors jeu d'évaluation.\n",
        "type": "simple",
        "difficulty_target": "easy",
        "answerable_proposed": True,
        "evidence": [{"passage_id": "fixture-a", "excerpt": "Le témoin est vert."}],
        "generation_reason": "Contrôle technique du contrat, sans contenu réglementaire.",
    }


def donnees_hors_corpus():
    return {**donnees_proposition(), "type": "hors_corpus", "answerable_proposed": False,
            "evidence": [], "out_of_corpus_reason": "Absence proposée pour cette fixture."}


class PropositionTests(unittest.TestCase):
    def test_texte_et_unicode_conserves(self):
        donnees = donnees_proposition()
        proposition = lire_proposition(json.dumps(donnees, ensure_ascii=False))
        self.assertEqual(proposition.question, donnees["question"])
        self.assertEqual(proposition.evidence[0].excerpt, "Le témoin est vert.")

    def test_champs_obligatoires(self):
        for champ in donnees_proposition():
            with self.subTest(champ=champ):
                donnees = donnees_proposition()
                del donnees[champ]
                with self.assertRaises(ValidationError):
                    Proposition.model_validate(donnees)

    def test_qwen_ne_fournit_pas_les_metadonnees(self):
        for champ, valeur in {"id": "Q001", "run_id": "lot", "set": "gold",
                              "schema_version": "synthetic-v1",
                              "validation": {"human": "accepted"}}.items():
            with self.subTest(champ=champ), self.assertRaises(ValidationError):
                Proposition.model_validate({**donnees_proposition(), champ: valeur})

    def test_types_stricts_et_valeurs_interdites(self):
        for champ, valeur in [("question", 12), ("question", " \n"),
                              ("answerable_proposed", "true"), ("answerable_proposed", 1),
                              ("evidence", {}), ("type", "gold"),
                              ("difficulty_target", "observed_easy")]:
            with self.subTest(champ=champ, valeur=valeur), self.assertRaises(ValidationError):
                Proposition.model_validate({**donnees_proposition(), champ: valeur})

    def test_preuves_non_vides_et_strictes(self):
        for preuve in [{"passage_id": "", "excerpt": "texte"},
                       {"passage_id": "a", "excerpt": " "},
                       {"passage_id": "a", "excerpt": "texte", "verified": True}]:
            with self.subTest(preuve=preuve), self.assertRaises(ValidationError):
                Proposition.model_validate({**donnees_proposition(), "evidence": [preuve]})

    def test_repondable_exige_preuve_sans_motif_absence(self):
        for changements in [{"evidence": []}, {"out_of_corpus_reason": "Absent"}]:
            with self.subTest(changements=changements), self.assertRaises(ValidationError):
                Proposition.model_validate({**donnees_proposition(), **changements})

    def test_hors_corpus_separe_proposition_et_confirmation(self):
        proposition = Proposition.model_validate(donnees_hors_corpus())
        candidat = creer_candidat(proposition, "lot", 1, ["fixture-a"])
        self.assertFalse(candidat.answerable_proposed)
        self.assertEqual(candidat.evidence, [])
        self.assertEqual(candidat.generation_source_ids, ["fixture-a"])
        self.assertIsNone(candidat.validation.answerable_confirmed)

    def test_hors_corpus_incoherent_refuse(self):
        for changements in [{"answerable_proposed": True},
                            {"out_of_corpus_reason": None},
                            {"evidence": donnees_proposition()["evidence"]}]:
            with self.subTest(changements=changements), self.assertRaises(ValidationError):
                Proposition.model_validate({**donnees_hors_corpus(), **changements})

    def test_multi_passage_exige_deux_sources_distinctes(self):
        donnees = {**donnees_proposition(), "type": "multi_passage"}
        donnees["evidence"].append({"passage_id": "fixture-a", "excerpt": "Autre extrait."})
        with self.assertRaises(ValidationError):
            Proposition.model_validate(donnees)
        donnees["evidence"][1]["passage_id"] = "fixture-b"
        self.assertEqual(len(Proposition.model_validate(donnees).evidence), 2)

    def test_simple_et_reformulation_utilisent_un_passage(self):
        for categorie in ["simple", "reformulation"]:
            donnees = {**donnees_proposition(), "type": categorie}
            Proposition.model_validate(donnees)
            donnees["evidence"].append({"passage_id": "fixture-b", "excerpt": "Autre."})
            with self.subTest(categorie=categorie), self.assertRaises(ValidationError):
                Proposition.model_validate(donnees)

    def test_preuve_identique_dupliquee_refusee(self):
        donnees = donnees_proposition()
        donnees["evidence"] *= 2
        with self.assertRaises(ValidationError):
            Proposition.model_validate(donnees)

    def test_piege_repondable_exige_premisse_et_correction(self):
        donnees = {**donnees_proposition(), "type": "adversarial",
                   "adversarial_premise": "Prémisse technique à vérifier.",
                   "correction_proposed": "Correction technique proposée."}
        Proposition.model_validate(donnees)
        for champ in ["adversarial_premise", "correction_proposed"]:
            with self.subTest(champ=champ), self.assertRaises(ValidationError):
                Proposition.model_validate({**donnees, champ: None})

    def test_piege_non_repondable_ne_fabrique_pas_de_correction(self):
        donnees = {**donnees_hors_corpus(), "type": "adversarial",
                   "adversarial_premise": "Prémisse non vérifiable dans cette fixture."}
        Proposition.model_validate(donnees)
        with self.assertRaises(ValidationError):
            Proposition.model_validate({**donnees, "correction_proposed": "Invention."})

    def test_correction_reservee_aux_pieges(self):
        with self.assertRaises(ValidationError):
            Proposition.model_validate({**donnees_proposition(), "correction_proposed": "Texte."})

    def test_json_invalide_ou_ambigu_refuse_sans_reparation(self):
        texte = json.dumps(donnees_proposition())
        cas = [texte[:-1], "```json\n" + texte + "\n```", texte + " {}", "[]",
               texte[:-1] + ', "type": "hors_corpus"}',
               texte.replace('"easy"', 'NaN'), texte.replace('"easy"', 'Infinity'),
               texte.replace(
                   '"excerpt": "Le t', '"excerpt": "doublon", "excerpt": "Le t', 1)]
        for entree in cas:
            with self.subTest(entree=entree), self.assertRaises(ValueError):
                lire_proposition(entree)

    def test_schema_exportable_sans_metadonnees_et_sans_reseau(self):
        schema = schema_generation()
        json.dumps(schema)
        self.assertFalse(schema["additionalProperties"])
        self.assertIn("question", schema["required"])
        self.assertNotIn("validation", schema["properties"])
        self.assertNotIn("generation_source_ids", schema["properties"])
        self.assertFalse(schema["$defs"]["Preuve"]["additionalProperties"])


class CandidatTests(unittest.TestCase):
    def setUp(self):
        self.proposition = Proposition.model_validate(donnees_proposition())
        self.candidat = creer_candidat(self.proposition, "lot_technique-1", 1, ["fixture-a"])

    def test_identite_attribuee_et_controles_en_attente(self):
        self.assertEqual(self.candidat.id, "SYN_lot_technique-1_0001")
        self.assertEqual(self.candidat.set, "synthetic_challenge")
        self.assertEqual(self.candidat.validation.automatic, "pending")
        self.assertEqual(self.candidat.validation.human, "pending")
        self.assertIsNone(self.candidat.validation.answerable_confirmed)
        self.assertEqual(self.candidat.question, self.proposition.question)

    def test_identifiants_incoherents_et_mauvais_numeros_refuses(self):
        for numero in [0, -1, True, "1"]:
            with self.subTest(numero=numero), self.assertRaises(ValueError):
                creer_candidat(self.proposition, "lot", numero, ["fixture-a"])
        for changements in [{"id": "Q001"}, {"id": "SYN_autre_0001"},
                            {"id": "SYN_lot_technique-1_0000"}, {"run_id": "../lot"},
                            {"set": "gold"}, {"schema_version": "inconnue"}]:
            with self.subTest(changements=changements), self.assertRaises(ValidationError):
                CasSynthetique.model_validate({**self.candidat.model_dump(), **changements})

    def test_preuve_hors_sources_et_sources_dupliquees_refusees(self):
        for sources in [[], ["fixture-b"], ["fixture-a", "fixture-a"]]:
            with self.subTest(sources=sources), self.assertRaises(ValidationError):
                creer_candidat(self.proposition, "lot", 1, sources)

    def test_serialisation_json_sans_perte(self):
        copie = CasSynthetique.model_validate_json(self.candidat.model_dump_json())
        self.assertEqual(copie, self.candidat)

    def test_controle_automatique_ne_confirme_pas_la_reponse(self):
        validation = ValidationCas(automatic="passed")
        self.assertEqual(validation.human, "pending")
        self.assertIsNone(validation.answerable_confirmed)

    def test_verdict_humain_interdit_tant_que_relecture_en_attente(self):
        for changements in [{"answerable_confirmed": True}, {"reviewer": "fixture"},
                            {"review_note": "Texte"}, {"expected_points": ["Point"]}]:
            with self.subTest(changements=changements), self.assertRaises(ValidationError):
                ValidationCas(**changements)

    def test_acceptation_exige_controles_relecteur_note_et_attentes(self):
        valide = {"automatic": "passed", "human": "accepted", "answerable_confirmed": True,
                  "reviewer": "Relecteur fictif de test", "review_note": "Fixture seulement.",
                  "expected_points": ["Point technique attendu."]}
        donnees = self.candidat.model_dump()
        donnees["validation"] = valide
        CasSynthetique.model_validate(donnees)
        for champ, valeur in [("automatic", "pending"), ("automatic", "failed"),
                              ("reviewer", None), ("review_note", None),
                              ("answerable_confirmed", None), ("expected_points", [])]:
            with self.subTest(champ=champ, valeur=valeur), self.assertRaises(ValidationError):
                ValidationCas(**{**valide, champ: valeur})

    def test_acceptation_hors_corpus_sans_points_de_reponse(self):
        candidat = creer_candidat(Proposition.model_validate(donnees_hors_corpus()), "lot", 1, [])
        donnees = candidat.model_dump()
        donnees["validation"] = {"automatic": "passed", "human": "accepted",
                                 "answerable_confirmed": False, "reviewer": "Fixture",
                                 "review_note": "Vérification fictive.", "expected_points": []}
        CasSynthetique.model_validate(donnees)
        donnees["validation"]["expected_points"] = ["Réponse inventée"]
        with self.assertRaises(ValidationError):
            CasSynthetique.model_validate(donnees)

    def test_confirmation_en_contradiction_avec_proposition_refusee(self):
        donnees = self.candidat.model_dump()
        donnees["validation"] = {"automatic": "passed", "human": "accepted",
                                 "answerable_confirmed": False, "reviewer": "Fixture",
                                 "review_note": "Mauvais classement.", "expected_points": []}
        with self.assertRaises(ValidationError):
            CasSynthetique.model_validate(donnees)

    def test_rejet_documente_sans_fausse_confirmation(self):
        validation = ValidationCas(human="rejected", reviewer="Fixture", review_note="Insuffisant.")
        self.assertIsNone(validation.answerable_confirmed)
        with self.assertRaises(ValidationError):
            ValidationCas(human="rejected")

    def test_creation_ne_modifie_pas_la_proposition(self):
        avant = copy.deepcopy(self.proposition.model_dump())
        creer_candidat(self.proposition, "autre_lot", 2, ["fixture-a"])
        self.assertEqual(self.proposition.model_dump(), avant)


if __name__ == "__main__":
    unittest.main()
