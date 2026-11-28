"""Contrôle de requantification (#140, étape 4), sur les 20 exemples de validation du lot, jamais sur le lot de test.

    python scripts/adaptation_qwen/export/controle_requantification.py --lot v2b-20261107 --adaptateur lora-v2b \\
        --gguf-temoin <temoin-q4_k_m.gguf> --gguf-adapte <adapte-q4_k_m.gguf> --llama-completion <binaire>

Quatre modèles répondent aux mêmes exemples, sans aléa (température 0), avec le prompt exact de la #85 :
- A : la base MLX 4 bits, celle de l'entraînement ;
- B : la base MLX avec l'adaptateur, le modèle effectivement entraîné ;
- C : le témoin T, en GGUF Q4_K_M (llama.cpp) ;
- D : le modèle adapté, fusionné dans les poids bf16, en GGUF Q4_K_M (llama.cpp).

Une réponse est conforme si elle passe les contrôles qui ont construit le lot : pour un exemple cité, elle cite le passage
cible (garder_citee) et recopie des unités entières des passages cités (verifier_recopie) ; pour un exemple hors corpus,
c'est exactement la phrase d'abstention.

Règle écrite avant l'exécution (#140) : l'effet de l'adaptation est le gain de réponses conformes, B moins A en MLX et
D moins C après la requantification.
- Si B moins A est nul ou négatif : « effet non observé en MLX » ; il n'y a rien à conserver.
- Sinon, si D moins C vaut au moins la moitié de B moins A : « effet conservé ».
- Sinon : « effet perdu à la requantification ».
Le contrôle est descriptif : il ne change ni la mesure du protocole 06 ni son analyse ; il est rapporté avec elle.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent))
import donnees_adaptation as da  # noqa: E402  (insère aussi scripts/rag dans le chemin)
import rag  # noqa: E402

ADAPTATEURS = da.RACINE / "data" / "volet_b" / "adaptateurs"
SORTIE = da.RACINE / "data" / "volet_b" / "export"
MARQUE_FIN = "[end of text]"
JETON_DEBUT = "151644 -> '<|im_start|>'"   # jeton spécial du gabarit Qwen, tel que llama.cpp l'affiche
OPTIONS_LLAMA = ["-n", str(da.NUM_PREDICT), "--temp", "0", "--seed", "20261018", "-c", "8192", "-ngl", "99",
                 "-no-cnv", "--no-display-prompt"]


class ErreurControle(RuntimeError):
    pass


def sources_de(exemple: dict) -> list[dict]:
    return [{"reference": f"[P{i}]", "passage_id": pid} for i, pid in enumerate(exemple["passages"], 1)]


def conforme(exemple: dict, sortie: dict, textes_passages: dict[str, str]) -> tuple[bool, str]:
    """Mêmes critères que la construction du lot ; textes_passages : passage_id vers texte original."""
    if sortie["arret"] != "stop":
        return False, "reponse_coupee"
    if exemple["variante"] == "hors_corpus":
        return (sortie["texte"].strip() == rag.ABSTENTION), "abstention_attendue"
    sources = sources_de(exemple)
    ok, motif = da.garder_citee(sortie, {"sources": sources}, exemple["passage_cible"], rag.ABSTENTION)
    if not ok:
        return False, motif
    r = da.verifier_recopie(sortie["texte"], {s["reference"]: textes_passages[s["passage_id"]] for s in sources})
    return r == "ok", r


def decider(c_a: int, c_b: int, c_c: int, c_d: int) -> dict:
    effet_mlx, effet_gguf = c_b - c_a, c_d - c_c
    if effet_mlx <= 0:
        verdict = "effet_non_observe_en_mlx"
    elif effet_gguf >= effet_mlx / 2:
        verdict = "effet_conserve"
    else:
        verdict = "effet_perdu_a_la_requantification"
    return {"effet_mlx": effet_mlx, "effet_gguf": effet_gguf, "verdict": verdict}


def lire_sortie_llama(stdout: str) -> dict:
    """Texte généré par llama-completion ; arrêt « stop » si la marque de fin d'EOS est présente."""
    texte = stdout.rstrip()
    if texte.endswith(MARQUE_FIN):
        return {"texte": texte[: -len(MARQUE_FIN)].rstrip(), "arret": "stop"}
    return {"texte": texte, "arret": "length"}


def generer_gguf(binaire: Path, gguf: Path, texte: str, verifier_gabarit: bool = False) -> dict:
    options = OPTIONS_LLAMA + (["--verbose-prompt"] if verifier_gabarit else [])
    r = subprocess.run([str(binaire), "-m", str(gguf), "-p", texte, *options], capture_output=True, text=True)
    if r.returncode != 0:
        raise ErreurControle(f"llama-completion a échoué ({r.returncode}) : {r.stderr[-400:]}")
    if verifier_gabarit and r.stderr.count(JETON_DEBUT) < 3:
        raise ErreurControle("Les jetons spéciaux du gabarit Qwen ne sont pas reconnus dans le prompt de llama.cpp")
    return lire_sortie_llama(r.stdout)


def lire_validation(lot: Path) -> list[dict]:
    manifeste = json.loads((lot / "manifeste.json").read_text(encoding="utf-8"))
    if da.sha256_fichier(lot / "valid.jsonl") != manifeste["sha256"]["valid.jsonl"]:
        raise ErreurControle("valid.jsonl diffère de l'empreinte du manifeste du lot")
    return da.lire_jsonl(lot / "valid.jsonl")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lot", required=True)
    p.add_argument("--adaptateur", required=True)
    p.add_argument("--gguf-temoin", type=Path, required=True)
    p.add_argument("--gguf-adapte", type=Path, required=True)
    p.add_argument("--llama-completion", type=Path, required=True)
    a = p.parse_args(argv)
    lot = da.DOSSIER / a.lot
    exemples = lire_validation(lot)
    textes = {q["passage_id"]: q["texte"] for q in rag.charger_index().passages}
    prompts = [da.texte_brut(e["messages"][0]["content"], e["messages"][1]["content"]) for e in exemples]
    sorties: dict[str, list[dict]] = {}

    from mlx_lm import load
    import mlx.core as mx
    for cle, chemin_adaptateur in (("A", None), ("B", ADAPTATEURS / a.adaptateur)):
        if chemin_adaptateur is None:
            modele, tok = da.charger_mlx()
        else:
            modele, tok = load(str(da.MODELE_MLX), adapter_path=str(chemin_adaptateur))
        sorties[cle] = [da.generer_mlx(modele, tok, t) for t in prompts]
        del modele, tok
        mx.clear_cache()
    for cle, gguf in (("C", a.gguf_temoin), ("D", a.gguf_adapte)):
        sorties[cle] = [generer_gguf(a.llama_completion, gguf, t, verifier_gabarit=(i == 0)) for i, t in enumerate(prompts)]

    lignes, comptes = [], {}
    for cle, liste in sorties.items():
        verdicts = [conforme(e, s, textes) for e, s in zip(exemples, liste)]
        comptes[cle] = sum(v for v, _ in verdicts)
        for e, s, (v, motif) in zip(exemples, liste, verdicts):
            lignes.append({"modele": cle, "id": e["id"], "variante": e["variante"], "conforme": v, "motif": motif,
                           "arret": s["arret"], "reponse": s["texte"]})
    accords = {"B_D_identiques": sum(b["texte"].strip() == d["texte"].strip() for b, d in zip(sorties["B"], sorties["D"])),
               "A_C_identiques": sum(x["texte"].strip() == c["texte"].strip() for x, c in zip(sorties["A"], sorties["C"]))}
    resultat = {"ecrit_le": datetime.now(timezone.utc).isoformat(timespec="seconds"), "lot": a.lot,
                "adaptateur": a.adaptateur, "exemples": len(exemples),
                "gguf": {"temoin": da.sha256_fichier(a.gguf_temoin), "adapte": da.sha256_fichier(a.gguf_adapte)},
                "conformes": comptes, **accords, **decider(comptes["A"], comptes["B"], comptes["C"], comptes["D"])}
    dossier = SORTIE / f"controle_{a.adaptateur}"
    dossier.mkdir(parents=True, exist_ok=False)
    da.ecrire_jsonl(dossier / "sorties.jsonl", lignes)
    (dossier / "resultats.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(resultat, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
