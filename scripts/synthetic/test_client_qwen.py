"""Serveur et tokeniseur simulés : aucune inférence réelle dans les tests."""

import copy
import hashlib
import io
import json
import types
import unittest
from unittest.mock import Mock, patch
import urllib.error

if __package__:
    from . import client_qwen
else:
    import client_qwen


MESSAGES = [{"role": "system", "content": "Témoin système."},
            {"role": "user", "content": "  Témoin éteint.\n"}]
TEXTE = ("<|im_start|>system\nTémoin système.<|im_end|>\n"
         "<|im_start|>user\n  Témoin éteint.\n<|im_end|>\n<|im_start|>assistant\n")


def tokeniseur_simule(nombre=12):
    tokeniseur = Mock(return_value={"input_ids": list(range(nombre))})
    tokeniseur.apply_chat_template.return_value = TEXTE
    return tokeniseur


def metadonnees():
    return [{"version": "fixture-serveur"},
            {"models": [{"name": client_qwen.MODELE_QWEN, "digest": client_qwen.DIGEST_QWEN}]},
            {"template": "fixture-gabarit", "parameters": None,
             "details": {"format": "gguf", "family": "qwen2", "quantization_level": "Q4_K_M"}}]


class ClientQwenTests(unittest.TestCase):
    def test_api_locale_get_et_post_utf8_avec_delai(self):
        with patch.object(client_qwen.urllib.request, "urlopen") as ouvrir:
            ouvrir.return_value.__enter__.return_value.read.return_value = b'{"version":"fixture"}'
            self.assertEqual(client_qwen._api("/api/version"), {"version": "fixture"})
            requete = ouvrir.call_args.args[0]
            self.assertEqual(requete.full_url, "http://127.0.0.1:11434/api/version")
            self.assertEqual(requete.get_method(), "GET")
            self.assertEqual(ouvrir.call_args.kwargs["timeout"], 5)
            client_qwen._api("/api/show", {"model": "témoin"})
            requete = ouvrir.call_args.args[0]
            self.assertEqual(requete.get_method(), "POST")
            self.assertEqual(json.loads(requete.data.decode("utf-8")), {"model": "témoin"})

    def test_api_refuse_http_delai_utf8_et_json_invalides(self):
        for erreur in [urllib.error.HTTPError("fixture", 500, "erreur", {}, io.BytesIO()),
                       TimeoutError("délai"), urllib.error.URLError("indisponible")]:
            with self.subTest(erreur=type(erreur)), patch.object(
                    client_qwen.urllib.request, "urlopen", side_effect=erreur):
                with self.assertRaises(client_qwen.ErreurQwen):
                    client_qwen._api("/api/version")
        for octets in [b"\xff", b"{", b"[]", b'{"error":"fixture"}']:
            with self.subTest(octets=octets), patch.object(
                    client_qwen.urllib.request, "urlopen") as ouvrir:
                ouvrir.return_value.__enter__.return_value.read.return_value = octets
                with self.assertRaises(client_qwen.ErreurQwen):
                    client_qwen._api("/api/version")

    def test_api_interdit_generation_meme_avec_parametres(self):
        with patch.object(client_qwen.urllib.request, "urlopen") as ouvrir:
            with self.assertRaises(client_qwen.ErreurQwen):
                client_qwen._api("/api/generate", {"prompt": "fixture"})
        ouvrir.assert_not_called()

    def test_modele_digest_details_et_gabarit_conserves(self):
        reponses = metadonnees()
        reponses[1]["models"][0]["digest"] = "sha256:" + client_qwen.DIGEST_QWEN
        with patch.object(client_qwen, "_api", side_effect=reponses) as api:
            resultat = client_qwen.verifier_ollama()
        self.assertEqual(resultat["digest"], client_qwen.DIGEST_QWEN)
        self.assertEqual(resultat["template"], "fixture-gabarit")
        self.assertIsNone(resultat["parameters"])
        self.assertEqual([c.args[0] for c in api.call_args_list],
                         ["/api/version", "/api/tags", "/api/show"])

    def test_refuse_modele_absent_ambigu_ou_digest_different(self):
        for catalogue in [None, [], [{"name": "autre"}],
                [{"name": client_qwen.MODELE_QWEN, "digest": "autre"}],
                metadonnees()[1]["models"] * 2]:
            reponses = metadonnees()
            reponses[1]["models"] = catalogue
            with self.subTest(catalogue=catalogue), patch.object(client_qwen, "_api", side_effect=reponses):
                with self.assertRaises(client_qwen.ErreurQwen):
                    client_qwen.verifier_ollama()

    def test_refuse_details_gabarit_et_version_invalides(self):
        cas = [(0, "version", " "), (2, "template", None), (2, "template", ""),
               (2, "details", []), (2, "details", {"format": "autre", "family": "qwen2",
                                                 "quantization_level": "Q4_K_M"})]
        for position, champ, valeur in cas:
            reponses = metadonnees()
            reponses[position][champ] = valeur
            with self.subTest(champ=champ, valeur=valeur), patch.object(
                    client_qwen, "_api", side_effect=reponses):
                with self.assertRaises(client_qwen.ErreurQwen):
                    client_qwen.verifier_ollama()

    def test_tokeniseur_revision_figee_cache_par_defaut(self):
        auto = Mock()
        with patch.dict("sys.modules", {"transformers": types.SimpleNamespace(AutoTokenizer=auto)}):
            client_qwen.charger_tokeniseur_qwen()
            self.assertEqual(auto.from_pretrained.call_args.args, (client_qwen.TOKENISEUR_QWEN,))
            self.assertEqual(auto.from_pretrained.call_args.kwargs, {
                "revision": client_qwen.REVISION_TOKENISEUR, "trust_remote_code": False,
                "local_files_only": True})
            client_qwen.charger_tokeniseur_qwen(True)
            self.assertFalse(auto.from_pretrained.call_args.kwargs["local_files_only"])

    def test_tokeniseur_indisponible_explique_option_telechargement(self):
        auto = Mock()
        auto.from_pretrained.side_effect = OSError("cache absent")
        with patch.dict("sys.modules", {"transformers": types.SimpleNamespace(AutoTokenizer=auto)}):
            with self.assertRaisesRegex(client_qwen.ErreurQwen, "allow-tokenizer-download"):
                client_qwen.charger_tokeniseur_qwen()

    def test_rendu_compte_et_empreintes_du_texte_exact(self):
        tokeniseur = tokeniseur_simule()
        entree = client_qwen.preparer_entree(MESSAGES, "fixture-gabarit", tokeniseur)
        tokeniseur.assert_called_once_with(TEXTE, add_special_tokens=False, truncation=False)
        tokeniseur.apply_chat_template.assert_called_once_with(
            MESSAGES, chat_template="fixture-gabarit", tokenize=False, add_generation_prompt=True)
        self.assertEqual(entree["texte"], TEXTE)
        self.assertEqual(entree["nb_tokens_hf"], 12)
        self.assertEqual(entree["sha256_texte"], hashlib.sha256(TEXTE.encode("utf-8")).hexdigest())
        self.assertFalse(entree["comptage_ollama_compare"])

    def test_budget_a_la_limite_accepte_un_token_de_plus_refuse(self):
        limite = client_qwen.NUM_CTX - client_qwen.NUM_PREDICT - client_qwen.MARGE_TOKENS
        entree = client_qwen.preparer_entree(MESSAGES, "fixture", tokeniseur_simule(limite))
        self.assertEqual(entree["nb_tokens_hf"], limite)
        with self.assertRaisesRegex(client_qwen.ErreurQwen, "Budget dépassé"):
            client_qwen.preparer_entree(MESSAGES, "fixture", tokeniseur_simule(limite + 1))

    def test_gabarit_inattendu_refuse_avant_tokenisation(self):
        tokeniseur = tokeniseur_simule()
        tokeniseur.apply_chat_template.return_value = TEXTE + "double gabarit"
        with self.assertRaises(client_qwen.ErreurQwen):
            client_qwen.preparer_entree(MESSAGES, "fixture", tokeniseur)
        tokeniseur.assert_not_called()

    def test_messages_ou_tokens_invalides_refuses(self):
        for messages in [None, [], list(reversed(MESSAGES)), [{"role": "user", "content": "fixture"}],
                         [{"role": "system", "content": " "}, MESSAGES[1]]]:
            with self.subTest(messages=messages), self.assertRaises(client_qwen.ErreurQwen):
                client_qwen.preparer_entree(messages, "fixture", tokeniseur_simule())
        for ids in [[], None, [True], ["12"]]:
            tokeniseur = tokeniseur_simule()
            tokeniseur.return_value = {"input_ids": ids}
            with self.subTest(ids=ids), self.assertRaises(client_qwen.ErreurQwen):
                client_qwen.preparer_entree(MESSAGES, "fixture", tokeniseur)

    def test_erreur_de_rendu_ou_tokenisation_encadree(self):
        for cible in ["rendu", "compte"]:
            tokeniseur = tokeniseur_simule()
            if cible == "rendu":
                tokeniseur.apply_chat_template.side_effect = RuntimeError("fixture")
            else:
                tokeniseur.side_effect = RuntimeError("fixture")
            with self.subTest(cible=cible), self.assertRaises(client_qwen.ErreurQwen):
                client_qwen.preparer_entree(MESSAGES, "fixture", tokeniseur)

    def test_requete_raw_structuree_non_envoyee_et_objets_independants(self):
        prompt = {"messages": copy.deepcopy(MESSAGES), "response_schema": {"type": "object"}}
        avant = copy.deepcopy(prompt)
        with (patch.object(client_qwen, "_api", side_effect=metadonnees()) as api,
              patch.object(client_qwen, "charger_tokeniseur_qwen", return_value=tokeniseur_simule())):
            resultat = client_qwen.preparer_requete(prompt)
        self.assertTrue(resultat["requete"]["raw"])
        self.assertFalse(resultat["requete"]["stream"])
        self.assertFalse(resultat["generation_appelee"])
        self.assertEqual(resultat["requete"]["prompt"], TEXTE)
        self.assertEqual(resultat["requete"]["format"], prompt["response_schema"])
        self.assertTrue(all(c.args[0] != "/api/generate" for c in api.call_args_list))
        resultat["requete"]["format"]["type"] = "modifié"
        resultat["requete"]["options"]["stop"].append("modifié")
        self.assertEqual(prompt, avant)
        self.assertNotIn("modifié", client_qwen.OPTIONS["stop"])


if __name__ == "__main__":
    unittest.main()
