"""Tests des contrôles de l'entraînement (#107, étape 29), sans modèle ni mlx."""

import contextlib
import csv
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import entrainer as en


def lot_temporaire(d: Path, n_train=273, n_valid=25, violations=0) -> Path:
    lot = d / "lot"
    lot.mkdir()
    (lot / "train.jsonl").write_text("".join(json.dumps({"id": i}) + "\n" for i in range(n_train)), encoding="utf-8")
    (lot / "valid.jsonl").write_text("".join(json.dumps({"id": i}) + "\n" for i in range(n_valid)), encoding="utf-8")
    manifeste = {"sha256": {n: en.sha256_fichier(lot / n) for n in ("train.jsonl", "valid.jsonl")},
                 "separation": {"violations": violations}}
    (lot / "manifeste.json").write_text(json.dumps(manifeste), encoding="utf-8")
    return lot


def grille(lot: Path, lignes: list[dict]) -> None:
    colonnes = ["id", "variante", "question", "reponse_attendue", "passages", "question_naturelle", "reponse_juste",
                "fidele_aux_passages", "abstention_justifiee", "commentaire"]
    with open(lot / "grille_relecture.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colonnes, delimiter=";")
        w.writeheader()
        for l in lignes:
            w.writerow({c: l.get(c, "") for c in colonnes})


def cite(i, rj="oui"):
    return {"id": f"C{i}", "variante": "citee", "question_naturelle": "oui", "reponse_juste": rj,
            "fidele_aux_passages": "oui"}


def retire(i, justifiee="oui"):
    return {"id": f"R{i}", "variante": "passage_retire", "question_naturelle": "oui", "abstention_justifiee": justifiee}


class ConfigurationTests(unittest.TestCase):
    def test_deux_epoques_et_six_evaluations_tout_explicite(self):
        c = en.configuration(Path("lot"), Path("ad"), 273)
        self.assertEqual((c["iters"], c["steps_per_eval"], c["save_every"]), (546, 91, 91))
        self.assertEqual(c["lora_parameters"], {"rank": 8, "dropout": 0.0, "scale": 20.0})
        self.assertEqual((c["learning_rate"], c["num_layers"], c["batch_size"], c["max_seq_length"]),
                         (1.0e-5, 16, 1, 3072))
        self.assertTrue(c["mask_prompt"] and c["grad_checkpoint"] and c["train"])
        self.assertEqual(c["val_batches"], -1)                           # toute la validation
        essai = en.configuration(Path("lot"), Path("ad"), 273, essai=2)
        self.assertEqual((essai["iters"], essai["steps_per_eval"]), (2, 1))


class LotTests(unittest.TestCase):
    def test_empreintes_et_effectifs(self):
        with tempfile.TemporaryDirectory() as d:
            lot = lot_temporaire(Path(d))
            self.assertEqual(en.controler_lot(lot)["effectifs"], {"train.jsonl": 273, "valid.jsonl": 25})
            with open(lot / "train.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({"id": "ajout"}) + "\n")
            with self.assertRaisesRegex(en.ErreurEntrainement, "train.jsonl diffère du manifeste"):
                en.controler_lot(lot)

    def test_violation_de_separation_refusee(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(en.ErreurEntrainement, "violations"):
                en.controler_lot(lot_temporaire(Path(d), violations=1))


class RelectureTests(unittest.TestCase):
    def test_regles_de_l_etape_28(self):
        with tempfile.TemporaryDirectory() as d:
            lot = lot_temporaire(Path(d))
            with self.assertRaisesRegex(en.ErreurEntrainement, "absente"):
                en.controler_relecture(lot)
            grille(lot, [cite(i) for i in range(15)] + [{"id": "C99", "variante": "citee", "question_naturelle": "oui"}])
            with self.assertRaisesRegex(en.ErreurEntrainement, "incomplète"):
                en.controler_relecture(lot)
            grille(lot, [cite(i) for i in range(15)] + [cite(i, "non") for i in range(15, 18)] + [retire(i) for i in range(8)])
            with self.assertRaisesRegex(en.ErreurEntrainement, "refusé par la relecture"):    # 3/26 = 11,5 %
                en.controler_relecture(lot)
            grille(lot, [cite(i) for i in range(22)] + [retire(i, "non" if i < 3 else "oui") for i in range(8)])
            with self.assertRaisesRegex(en.ErreurEntrainement, "réassembler"):                 # 3/30 = 10 %
                en.controler_relecture(lot)
            grille(lot, [cite(i) for i in range(22)] + [retire(i, "non" if i < 2 else "oui") for i in range(8)])
            self.assertTrue(en.controler_relecture(lot)["utilisable"])


class MainTests(unittest.TestCase):
    def test_adaptateur_existant_jamais_remplace(self):
        with tempfile.TemporaryDirectory() as d, patch.object(en, "ADAPTATEURS", Path(d)), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            (Path(d) / "lora-v1").mkdir()
            self.assertEqual(en.main(["--lot", "v1", "--run", "lora-v1"]), 1)
        self.assertIn("jamais remplacé", err.getvalue())

    def test_lot_introuvable_et_code_non_committe(self):
        with tempfile.TemporaryDirectory() as d, patch.object(en, "ADAPTATEURS", Path(d) / "ad"), \
                patch.object(en, "DONNEES", Path(d)):
            lot_temporaire(Path(d))                                     # lot nommé « lot »
            for argv, etat, motif in ((["--lot", "absent", "--run", "r"], False, "introuvable"),
                                      (["--lot", "lot", "--run", "r"], True, "committer")):
                with patch.object(en, "etat_git", return_value={"commit": "0" * 40, "scripts_modifies": etat}), \
                        contextlib.redirect_stderr(io.StringIO()) as err:
                    self.assertEqual(en.main(argv), 1)
                self.assertIn(motif, err.getvalue())

    def test_fichier_decharge_par_icloud_detecte(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "poids.safetensors").write_bytes(b"x")
            reel = os.lstat

            def faux(p, *a, **k):                                        # même fichier, drapeau « dataless » ajouté
                s = reel(p, *a, **k)
                if not str(p).endswith(".safetensors"):
                    return s
                return type("S", (), {"st_mode": s.st_mode, "st_flags": s.st_flags | en.SF_DATALESS})()
            with patch.object(en.os, "lstat", side_effect=faux):
                self.assertEqual(len(en.fichiers_decharges(Path(d))), 1)
            self.assertEqual(en.fichiers_decharges(Path(d)), [])

    def test_versions_differentes_refusees(self):
        for attendues in ({"mlx": "0.0.0"}, {"paquet-absent-nlp2": "1.0"}):    # autre version, paquet absent
            with patch.object(en, "VERSIONS", attendues):
                with self.assertRaisesRegex(en.ErreurEntrainement, "Versions"):
                    en.versions()

    def test_noms_invalides(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(en.main(["--lot", "../x", "--run", "a"]), 2)


if __name__ == "__main__":
    unittest.main()
