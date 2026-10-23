"""Contrôles techniques avec serveur et tokeniseur simulés, sans inférence."""

import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from generation import (DIGEST_QWEN_31, ErreurGeneration, MARGE_TOKENS, MODELE_QWEN,
                        NUM_CTX, NUM_PREDICT, REVISION_TOKENISEUR, TOKENISEUR_QWEN,
                        _api, charger_tokeniseur_qwen, generer_reponse, preparer_entree,
                        valider_citations, verifier_ollama)
from rag import ABSTENTION


class GenerationTests(unittest.TestCase):
    def setUp(self):
        # Documents techniques, pas de nouvelles questions d'évaluation.
        self.contexte = {"system": "Consigne technique.", "prompt": "Documents de contrôle.",
                         "sources": [{"reference": f"[P{i}]"} for i in range(1, 6)]}
        self.tokeniseur = Mock()
        self.tokeniseur.apply_chat_template.side_effect = lambda messages, **kw: (
            "<|im_start|>system\n" + messages[0]["content"] + "<|im_end|>\n"
            + "<|im_start|>user\n" + messages[1]["content"] + "<|im_end|>\n"
            + "<|im_start|>assistant\n")
        self.tokeniseur.return_value = {"input_ids": list(range(100))}
        self.infos = {"version": "0.40.5", "modele": MODELE_QWEN, "digest": DIGEST_QWEN_31,
                      "details": {"format": "gguf", "family": "qwen2", "quantization_level": "Q4_K_M"},
                      "template": "gabarit-simule", "parameters": None}
        self.reponse = {"response": "Texte de contrôle [P1][P5]", "done": True,
                        "done_reason": "stop", "prompt_eval_count": 100, "eval_count": 20}

    def executer_generation_simulee(self):
        with (patch("generation.verifier_ollama", return_value=self.infos),
              patch("generation.charger_tokeniseur_qwen", return_value=self.tokeniseur),
              patch("generation._api", return_value=self.reponse) as api):
            resultat = generer_reponse(self.contexte, ABSTENTION)
        return resultat, api

    def test_http_utf8_local_et_json(self):
        reponse = Mock()
        reponse.__enter__ = Mock(return_value=reponse)
        reponse.__exit__ = Mock(return_value=False)
        reponse.read.return_value = '{"response":"é"}'.encode()
        with patch("generation.urllib.request.urlopen", return_value=reponse) as ouvrir:
            self.assertEqual(_api("/api/generate", {"prompt": "é"})["response"], "é")
        requete = ouvrir.call_args.args[0]
        self.assertEqual(requete.full_url, "http://127.0.0.1:11434/api/generate")
        self.assertEqual(json.loads(requete.data), {"prompt": "é"})

    def test_http_erreur_et_json_invalide(self):
        with patch("generation.urllib.request.urlopen", side_effect=TimeoutError("simulation")):
            with self.assertRaises(ErreurGeneration):
                _api("/api/version")
        reponse = Mock()
        reponse.__enter__ = Mock(return_value=reponse)
        reponse.__exit__ = Mock(return_value=False)
        reponse.read.return_value = b"pas un JSON"
        with patch("generation.urllib.request.urlopen", return_value=reponse):
            with self.assertRaises(ErreurGeneration):
                _api("/api/version")

    def test_verification_version_digest_quantification_template(self):
        tags = {"models": [{"name": MODELE_QWEN, "digest": DIGEST_QWEN_31}]}
        with patch("generation._api", side_effect=[{"version": "0.40.5"}, tags, self.infos]):
            infos = verifier_ollama()
        self.assertEqual(infos["digest"], DIGEST_QWEN_31)
        self.assertEqual(infos["details"]["quantization_level"], "Q4_K_M")

    def test_modele_absent_ou_digest_different(self):
        for models in ([], [{"name": MODELE_QWEN, "digest": "autre-digest"}]):
            with self.subTest(models=models):
                with patch("generation._api", side_effect=[{"version": "0.40.5"}, {"models": models}]):
                    with self.assertRaises(ErreurGeneration):
                        verifier_ollama()

    def test_quantification_incompatible(self):
        infos = {**self.infos, "details": {**self.infos["details"], "quantization_level": "Q8_0"}}
        tags = {"models": [{"name": MODELE_QWEN, "digest": DIGEST_QWEN_31}]}
        with patch("generation._api", side_effect=[{"version": "0.40.5"}, tags, infos]):
            with self.assertRaises(ErreurGeneration):
                verifier_ollama()

    def test_tokeniseur_seul_et_revision_figee(self):
        auto = Mock()
        with patch.dict("sys.modules", {"transformers": SimpleNamespace(AutoTokenizer=auto)}):
            charger_tokeniseur_qwen()
        auto.from_pretrained.assert_called_once_with(
            TOKENISEUR_QWEN, revision=REVISION_TOKENISEUR, trust_remote_code=False)

    def test_format_et_compte_sans_tokens_speciaux_doubles(self):
        entree = preparer_entree(self.contexte, self.infos["template"], self.tokeniseur)
        self.assertEqual(entree["nb_tokens"], 100)
        self.assertTrue(entree["texte"].endswith("<|im_start|>assistant\n"))
        self.tokeniseur.assert_called_once_with(entree["texte"], add_special_tokens=False, truncation=False)

    def test_budget_limite_et_depassement_sans_generation(self):
        limite = NUM_CTX - NUM_PREDICT - MARGE_TOKENS
        self.tokeniseur.return_value = {"input_ids": list(range(limite))}
        self.assertEqual(preparer_entree(self.contexte, "gabarit", self.tokeniseur)["nb_tokens"], limite)
        self.tokeniseur.return_value = {"input_ids": list(range(limite + 1))}
        with (patch("generation.verifier_ollama", return_value=self.infos),
              patch("generation.charger_tokeniseur_qwen", return_value=self.tokeniseur),
              patch("generation._api") as api):
            with self.assertRaisesRegex(ErreurGeneration, "Budget dépassé"):
                generer_reponse(self.contexte, ABSTENTION)
            api.assert_not_called()

    def test_gabarit_inattendu_refuse(self):
        self.tokeniseur.apply_chat_template.side_effect = None
        self.tokeniseur.apply_chat_template.return_value = "gabarit incompatible"
        with self.assertRaisesRegex(ErreurGeneration, "Gabarit local différent"):
            preparer_entree(self.contexte, "gabarit", self.tokeniseur)

    def test_requete_raw_et_reponse_citee(self):
        resultat, api = self.executer_generation_simulee()
        self.assertEqual(resultat["statut"], "reponse_citee")
        self.assertEqual(resultat["reponse_brute"], self.reponse["response"])
        payload = api.call_args.args[1]
        self.assertTrue(payload["raw"])
        self.assertFalse(payload["stream"])
        self.assertNotIn("system", payload)
        self.assertNotIn("context", payload)
        self.assertEqual(payload["prompt"], resultat["entree"]["texte"])
        self.assertEqual(payload["options"]["num_ctx"], NUM_CTX)
        self.assertFalse(resultat["validation_citations"]["justification_semantique_verifiee"])

    def test_generation_incomplete_ou_compte_different_preserve_reponse(self):
        original = dict(self.reponse)
        for cle, valeur in (("done", False), ("done_reason", "length"),
                            ("prompt_eval_count", 99), ("eval_count", 0)):
            with self.subTest(cle=cle):
                self.reponse = {**original, cle: valeur}
                resultat, _ = self.executer_generation_simulee()
                self.assertEqual(resultat["statut"], "erreur_technique")
                self.assertTrue(resultat["erreurs_techniques"])
                self.assertEqual(resultat["reponse_brute"], original["response"])

    def test_abstention_exacte_seulement(self):
        self.reponse["response"] = " \n" + ABSTENTION + "\n"
        resultat, _ = self.executer_generation_simulee()
        self.assertEqual(resultat["statut"], "abstention_modele")
        melange = valider_citations(ABSTENTION + " [P1]", self.contexte["sources"], ABSTENTION)
        self.assertEqual(melange["statut"], "sortie_invalide")

    def test_citations_existantes_doublons_et_invalides(self):
        valide = valider_citations("Document [P2]. Suite [P2][P5].", self.contexte["sources"], ABSTENTION)
        self.assertEqual(valide["citations"], ["[P2]", "[P5]"])
        self.assertEqual(valide["statut"], "reponse_citee")
        for citation in ("[P8]", "[P0]", "[P01]", "[p1]", "[P1, P2]", "[P1-P2]", "[8]", "[X1]", "[P1"):
            with self.subTest(citation=citation):
                r = valider_citations("Texte [P1] " + citation, self.contexte["sources"], ABSTENTION)
                self.assertEqual(r["statut"], "sortie_invalide")
                self.assertIn(citation, r["citations_invalides"])

    def test_reponse_vide_ou_sans_citation(self):
        for texte in ("", "Texte sans référence."):
            with self.subTest(texte=texte):
                self.assertEqual(valider_citations(texte, self.contexte["sources"], ABSTENTION)["statut"],
                                 "sortie_invalide")


if __name__ == "__main__":
    unittest.main()
