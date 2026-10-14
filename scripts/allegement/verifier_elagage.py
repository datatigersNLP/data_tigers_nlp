"""
Vérifie qu'un modèle élagué par elaguer_vocabulaire.py est sans perte sur nos textes (#50).

1. Découpage : chaque texte, préfixé par « query: », donne les mêmes jetons avec les deux tokeniseurs, après
   renumérotation. Textes : les 822 requêtes de contrôle du notebook 02, les questions du notebook 03, les titres et
   variantes du CDTN, les 4 240 passages M2. Les fichiers absents de data/ sont signalés et sautés.
2. Sorties : les deux q8 donnent la même sortie, bit à bit, sur les requêtes de contrôle et les questions,
   requête par requête, comme le site.
Le contrôle qui fait foi pour le site est celui du navigateur : controle_navigateur.html.

Usage, depuis la racine du dépôt :
    python scripts/allegement/verifier_elagage.py front/public/modele/<dossier>             # source : Xenova, révision figée
    python scripts/allegement/verifier_elagage.py front/public/modele/<dossier> --source <modèle complet>
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from elaguer_vocabulaire import FICHIERS, SOURCE_HUB  # noqa: E402


def textes_du_depot() -> dict:
    """Jeux de textes lus dans data/ (non versionné) et dans le site ; un jeu absent est remplacé par None."""
    def lire(chemin, extraire):
        p = RACINE / chemin
        return extraire(json.loads(p.read_text(encoding="utf-8"))) if p.exists() else None
    return {
        "requêtes de contrôle du notebook 02": lire("data/indexation/controle/requetes_fidelite.json", lambda d: d["requetes"]),
        "questions du notebook 03": lire("data/evaluation/notebook03/questions_navigateur.json",
                                         lambda d: [q["texte"] for q in d["questions"]]),
        "titres et variantes du CDTN": lire("data/evaluation/cdtn/requests_6d16869.json",
                                            lambda d: [x for r in d for x in [r["title"], *(r.get("variants") or [])] if x.strip()]),
        "passages M2": lire("front/public/index/passages_m2.json", lambda d: [p["texte"] for p in d]),
    }


def main():
    parser = argparse.ArgumentParser(description="Vérifie qu'un modèle élagué est sans perte sur nos textes.")
    parser.add_argument("elague", help="dossier du modèle élagué")
    parser.add_argument("--source", help="dossier du modèle complet ; par défaut, Xenova à la révision figée")
    args = parser.parse_args()

    elague = Path(args.elague).resolve()
    if args.source:
        source = Path(args.source).resolve()
    else:
        from huggingface_hub import hf_hub_download
        source = Path([hf_hub_download(SOURCE_HUB["depot"], f, revision=SOURCE_HUB["revision"]) for f in FICHIERS][-1]).parents[1]
    t1, t2 = Tokenizer.from_file(str(source / "tokenizer.json")), Tokenizer.from_file(str(elague / "tokenizer.json"))
    # renumérotation : la k-ième pièce du vocabulaire élagué est la pièce d'origine gardes[k]
    vocab_source = [p for p, _ in json.loads((source / "tokenizer.json").read_text(encoding="utf-8"))["model"]["vocab"]]
    position = {p: i for i, p in enumerate(vocab_source)}
    gardes = [position[p] for p, _ in json.loads((elague / "tokenizer.json").read_text(encoding="utf-8"))["model"]["vocab"]]

    echecs = 0
    jeux = textes_du_depot()
    for nom, textes in jeux.items():
        if textes is None:
            print(f"{nom:40s} absent, sauté")
            continue
        differents = [t for t in textes if t1.encode("query: " + t).ids != [gardes[i] for i in t2.encode("query: " + t).ids]]
        echecs += len(differents)
        print(f"{nom:40s} {len(textes) - len(differents)}/{len(textes)} découpages identiques"
              + (f" ; différents : {[d[:40] for d in differents[:5]]}" if differents else ""))

    s1 = ort.InferenceSession(str(source / "onnx/model_quantized.onnx"), providers=["CPUExecutionProvider"])
    s2 = ort.InferenceSession(str(elague / "onnx/model_quantized.onnx"), providers=["CPUExecutionProvider"])
    noms = {i.name for i in s1.get_inputs()}
    requetes = [t for nom in ("requêtes de contrôle du notebook 02", "questions du notebook 03") for t in (jeux[nom] or [])]
    identiques = 0
    for t in requetes:
        e1, e2 = t1.encode("query: " + t), t2.encode("query: " + t)
        def entrees(e):
            d = {"input_ids": np.array([e.ids], dtype=np.int64), "attention_mask": np.array([e.attention_mask], dtype=np.int64),
                 "token_type_ids": np.zeros((1, len(e.ids)), dtype=np.int64)}
            return {k: v for k, v in d.items() if k in noms}
        identiques += int(np.array_equal(s1.run(None, entrees(e1))[0], s2.run(None, entrees(e2))[0]))
    echecs += len(requetes) - identiques
    print(f"{'sorties du q8, bit à bit':40s} {identiques}/{len(requetes)} identiques")
    print("ÉLAGAGE SANS PERTE SUR NOS TEXTES" if echecs == 0 else f"ÉCHEC : {echecs} différence(s)")
    return 0 if echecs == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
