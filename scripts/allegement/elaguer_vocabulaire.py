"""
Élagage sans perte du vocabulaire du modèle servi (#50).

Le q8 de multilingual-e5-small pèse 112,9 Mio, dont 81 % pour la table des mots (250 037 lignes de 384 octets), au-delà
de la limite de 100 Mio par fichier de GitHub. Le script retire du tokeniseur et de cette table les pièces qui
contiennent une lettre d'un autre alphabet que le latin ou le grec, et recopie les lignes gardées telles quelles, sans
les requantifier.

Pourquoi c'est sans perte : le tokeniseur Unigram découpe un texte en choisissant, parmi les pièces qui en recouvrent
des morceaux, le découpage le plus probable. Une pièce retirée contient une lettre absente de tout texte écrit avec
les caractères gardés : elle ne peut jamais en recouvrir un morceau. Pour ces textes, le découpage est donc le même,
les jetons désignent les mêmes lignes de la table, et le modèle donne les mêmes sorties, bit à bit. Un texte qui
contient une lettre retirée (cyrillique, chinois, arabe…) reçoit un jeton inconnu à sa place.
verifier_elagage.py et controle_navigateur.html le vérifient sur nos textes, en Python puis dans le navigateur.

Usage, depuis la racine du dépôt :
    python scripts/allegement/elaguer_vocabulaire.py                    # Xenova/multilingual-e5-small, révision figée
    python scripts/allegement/elaguer_vocabulaire.py --dossier <modèle>  # un autre modèle exporté (l'ajusté, #49)
Le modèle élagué est écrit dans front/public/modele/<nom>-<8 premiers caractères de son empreinte>/ : chaque version
a son propre chemin, pour qu'aucun navigateur ne serve une ancienne version depuis son cache.
"""

import argparse
import copy
import hashlib
import json
import platform
import shutil
import sys
import tempfile
import unicodedata
from importlib import metadata
from pathlib import Path

import numpy as np
import onnx
from onnx import numpy_helper

RACINE = Path(__file__).resolve().parents[2]
SOURCE_HUB = {"depot": "Xenova/multilingual-e5-small", "revision": "761b726dd34fb83930e26aab4e9ac3899aa1fa78",
              "sha256_onnx": "f80102d3f2a1229f387d3c81909990d8945513e347b0eab049f7de3c6f98c193"}
FICHIERS = ["config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json",
            "onnx/model_quantized.onnx"]
REGLE = ("une pièce est gardée si chacune de ses lettres appartient à l'alphabet latin ou grec ; chiffres, "
         "ponctuation, symboles, espaces et diacritiques combinants sont toujours gardés, comme les jetons spéciaux")
# licence de multilingual-e5-small : dépôt microsoft/unilm, fichier LICENSE (commit 0e31c7c09737)
LICENCE_MIT = """The MIT License (MIT)

Copyright (c) Microsoft Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def sha256(chemin: Path) -> str:
    return hashlib.sha256(Path(chemin).read_bytes()).hexdigest()


def caractere_garde(c: str) -> bool:
    """Toute pièce dont chaque caractère passe ce test est gardée."""
    if unicodedata.category(c)[0] != "L":   # chiffres, ponctuation, symboles, espaces, ▁, diacritiques combinants
        return True
    nom = unicodedata.name(c, "")           # lettres : latin et grec (le normaliseur change « µ » en « μ »)
    return "LATIN" in nom or "GREEK" in nom


def pieces_gardees(tokenizer: dict) -> list:
    """Identifiants des pièces gardées, dans l'ordre d'origine ; les jetons spéciaux sont toujours gardés."""
    speciaux = {a["id"] for a in tokenizer["added_tokens"]}
    return [i for i, (piece, _) in enumerate(tokenizer["model"]["vocab"])
            if i in speciaux or all(caractere_garde(c) for c in piece)]


def elaguer_tokeniseur(tokenizer: dict, gardes: list) -> dict:
    """Vocabulaire réduit et renuméroté ; les jetons spéciaux et le post-traitement suivent la renumérotation."""
    nouveau = {ancien: k for k, ancien in enumerate(gardes)}
    if any(nouveau[i] != i for i in (0, 1, 2, 3)):
        raise ValueError("les jetons spéciaux 0 à 3 doivent garder leur identifiant")
    t = copy.deepcopy(tokenizer)
    t["model"]["vocab"] = [tokenizer["model"]["vocab"][i] for i in gardes]
    t["model"]["unk_id"] = nouveau[tokenizer["model"]["unk_id"]]
    for jeton in t["added_tokens"]:
        jeton["id"] = nouveau[jeton["id"]]
    for jeton in (t.get("post_processor") or {}).get("special_tokens", {}).values():
        jeton["ids"] = [nouveau[i] for i in jeton["ids"]]
    return t


def elaguer_onnx(chemin: Path, gardes: list, nb_pieces: int) -> tuple:
    """Garde les lignes de la table des mots désignées par gardes, sans les requantifier (même échelle, même zéro)."""
    modele = onnx.load(str(chemin))
    tables = [i for i in modele.graph.initializer if len(i.dims) == 2 and i.dims[1] == 384 and i.dims[0] >= nb_pieces]
    if len(tables) != 1:
        raise ValueError(f"table des mots introuvable ou ambiguë : {[(i.name, list(i.dims)) for i in tables]}")
    table = numpy_helper.to_array(tables[0])
    if table.dtype != np.uint8:
        raise ValueError(f"table des mots en {table.dtype}, attendu uint8 (q8)")
    tables[0].CopyFrom(numpy_helper.from_array(np.ascontiguousarray(table[gardes]), tables[0].name))
    return modele, table.shape[0]


def lire_source(dossier: str | None) -> tuple:
    """Dossier local du modèle, et description de sa provenance."""
    if dossier:
        d = Path(dossier).resolve()
        return d, {"dossier": str(d.relative_to(RACINE)) if d.is_relative_to(RACINE) else d.name}
    from huggingface_hub import hf_hub_download
    chemins = [hf_hub_download(SOURCE_HUB["depot"], f, revision=SOURCE_HUB["revision"]) for f in FICHIERS]
    d = Path(chemins[-1]).parents[1]
    if sha256(d / "onnx/model_quantized.onnx") != SOURCE_HUB["sha256_onnx"]:
        raise ValueError("empreinte du q8 source différente de celle figée")
    return d, {"depot": SOURCE_HUB["depot"], "revision": SOURCE_HUB["revision"]}


def main():
    parser = argparse.ArgumentParser(description="Élagage sans perte du vocabulaire du modèle servi (#50).")
    parser.add_argument("--dossier", help="modèle local exporté (config, tokeniseur, onnx/model_quantized.onnx)")
    parser.add_argument("--nom", default="multilingual-e5-small-q8-elague", help="préfixe du dossier de sortie")
    parser.add_argument("--sortie", default=str(RACINE / "front/public/modele"), help="dossier parent de sortie")
    args = parser.parse_args()

    source, provenance = lire_source(args.dossier)
    tokenizer = json.loads((source / "tokenizer.json").read_text(encoding="utf-8"))
    if tokenizer["model"]["type"] != "Unigram" or tokenizer["model"].get("byte_fallback"):
        raise ValueError("le raisonnement de l'élagage suppose un tokeniseur Unigram sans repli sur les octets")
    gardes = pieces_gardees(tokenizer)
    modele, lignes_source = elaguer_onnx(source / "onnx/model_quantized.onnx", gardes, len(tokenizer["model"]["vocab"]))

    with tempfile.TemporaryDirectory(dir=args.sortie if Path(args.sortie).exists() else None) as tmp:
        sortie = Path(tmp) / "modele"
        (sortie / "onnx").mkdir(parents=True)
        onnx.save(modele, str(sortie / "onnx/model_quantized.onnx"))
        (sortie / "tokenizer.json").write_text(
            json.dumps(elaguer_tokeniseur(tokenizer, gardes), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        config = json.loads((source / "config.json").read_text(encoding="utf-8"))
        config["vocab_size"] = len(gardes)
        (sortie / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # recopiés tels quels s'ils existent : un modèle sauvegardé par sentence-transformers n'a pas toujours
        # special_tokens_map.json, et Transformers.js n'en a pas besoin
        if not (source / "tokenizer_config.json").exists():
            raise ValueError("tokenizer_config.json manquant dans le modèle source")
        for f in ("tokenizer_config.json", "special_tokens_map.json"):
            if (source / f).exists():
                shutil.copyfile(source / f, sortie / f)
        (sortie / "LICENSE").write_text(LICENCE_MIT, encoding="utf-8")

        empreinte = sha256(sortie / "onnx/model_quantized.onnx")
        manifeste = {
            "objet": "élagage sans perte du vocabulaire (#50), scripts/allegement/elaguer_vocabulaire.py",
            "source": {**provenance, "sha256_onnx": sha256(source / "onnx/model_quantized.onnx"),
                       "sha256_tokenizer": sha256(source / "tokenizer.json")},
            "regle": REGLE,
            "pieces": {"source": len(tokenizer["model"]["vocab"]), "gardees": len(gardes)},
            "table_des_mots": {"lignes_source": lignes_source, "lignes": len(gardes)},
            "fichiers": {str(p.relative_to(sortie)): {"octets": p.stat().st_size, "sha256": sha256(p)}
                         for p in sorted(sortie.rglob("*")) if p.is_file()},
            "outils": {"python": platform.python_version(), "onnx": onnx.__version__, "numpy": np.__version__},
            "licence": "MIT (multilingual-e5-small, Microsoft), fichier LICENSE",
        }
        (sortie / "manifeste.json").write_text(json.dumps(manifeste, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        cible = Path(args.sortie) / f"{args.nom}-{empreinte[:8]}"
        if cible.exists():
            shutil.rmtree(cible)
        cible.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(sortie), str(cible))

    print(f"pièces gardées : {len(gardes)} sur {len(tokenizer['model']['vocab'])} ; écrit dans {cible}")
    for nom, f in manifeste["fichiers"].items():
        print(f"  {nom:28s} {f['octets']:>11,} octets  {f['sha256'][:16]}")


if __name__ == "__main__":
    sys.exit(main())
