"""Controles sans GPU du benchmark ; pas de mesure de faisabilite du 7B."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from faisabilite_legion import RACINE, construire_exemples, empreinte, plan_mesure, tokeniser, sauver


class DonneesTests(unittest.TestCase):
    def test_parite_avec_les_28_exemples_des_pr_85_et_109(self):
        # Empreinte obtenue en comparant les 28 messages au constructeur de
        # contexte df91b859 et au tirage de a0bceb72, pas depuis le benchmark.
        exemples = construire_exemples(RACINE / "front/public/index/passages_m2.json")
        self.assertEqual(len(exemples), 28)
        self.assertEqual(empreinte(exemples), "261167b7c1a9c01829943114ce5b78e6b1d9b40bbe7a1c5881de678f8c61190f")

    def test_refus_corpus_modifie(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "passages.json"
            p.write_text("[]")
            with self.assertRaisesRegex(ValueError, "Passages differents"):
                construire_exemples(p)

    def test_prompt_exclu_de_la_perte_reponse_et_fin_conservees(self):
        class Tok:
            def apply_chat_template(self, messages, **kwargs):
                return [11, 12, 13] if len(messages) == 2 else [11, 12, 13, 21, 22, 99]
        ids, labels = tokeniser(Tok(), [{"messages": [{}, {}, {}]}], 6)[0]
        self.assertEqual(ids, [11, 12, 13, 21, 22, 99])
        self.assertEqual(labels, [-100, -100, -100, 21, 22, 99])
        with self.assertRaisesRegex(ValueError, "aucune troncature"):
            tokeniser(Tok(), [{"messages": [{}, {}, {}]}], 5)

    def test_refus_gabarit_sans_prefixe_commun(self):
        class Tok:
            def apply_chat_template(self, messages, **kwargs):
                return [1, 2] if len(messages) == 2 else [1, 3, 4]
        with self.assertRaisesRegex(ValueError, "Gabarit"):
            tokeniser(Tok(), [{"messages": [{}, {}, {}]}], 10)

    def test_plus_long_inclus_et_deux_cycles_identiques(self):
        prepares = [([0] * n, []) for n in range(28, 0, -1)]
        chauffe, mesures = plan_mesure(prepares)
        self.assertEqual(len(prepares[chauffe[0]][0]), 28)
        self.assertEqual(mesures[:6], mesures[6:])
        self.assertIn(0, mesures)
        self.assertIn(27, mesures)

    def test_json_refuse_nan(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                sauver(Path(d) / "mesure.json", {"perte": float("nan")})


@unittest.skipUnless(importlib.util.find_spec("torch") and importlib.util.find_spec("peft"),
                     "Test CPU Qwen requiert torch, transformers et peft")
class CalculTests(unittest.TestCase):
    def test_perte_reponse_seule_equivaut_au_masquage_complet_et_gradients_lora(self):
        import torch
        from transformers import Qwen2Config, Qwen2ForCausalLM
        from peft import LoraConfig, get_peft_model
        torch.manual_seed(7)
        config = Qwen2Config(vocab_size=64, hidden_size=32, intermediate_size=64,
            num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2)
        model = Qwen2ForCausalLM(config)
        model.requires_grad_(False)
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.config.use_cache = False
        model = get_peft_model(model, LoraConfig(task_type="CAUSAL_LM", r=8,
            lora_alpha=160, target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            layers_to_transform=[1], layers_pattern="layers"))
        model.train()
        ids = torch.tensor([[1, 2, 3, 4, 5, 6]])
        labels = torch.tensor([[-100, -100, -100, 4, 5, 6]])
        full = model(input_ids=ids, labels=labels, use_cache=False).loss
        full.backward()
        gradients = {n: p.grad.clone() for n, p in model.named_parameters() if p.requires_grad}
        model.zero_grad(set_to_none=True)
        logits = model(input_ids=ids, logits_to_keep=4, use_cache=False).logits[:, :-1, :]
        tail = torch.nn.functional.cross_entropy(logits.reshape(-1, 64), ids[:, 3:].reshape(-1))
        tail.backward()
        torch.testing.assert_close(full, tail)
        for n, p in model.named_parameters():
            if p.requires_grad:
                torch.testing.assert_close(p.grad, gradients[n])
                self.assertTrue(n.startswith("base_model.model.model.layers.1."))
        self.assertTrue(any(p.grad.abs().sum() > 0 for p in model.parameters() if p.requires_grad))


if __name__ == "__main__":
    unittest.main()
