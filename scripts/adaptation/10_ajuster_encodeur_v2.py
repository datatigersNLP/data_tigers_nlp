"""Encodeur ajusté v2 (#167, amendement A2 du protocole 05) : entraînement (section 3) et garde-fou (section 4).

L'entraînement reprend la recette de `04_ajuster_encodeur.py` (#49) sans la changer : seules les paires changent
(`09_generer_paires_v2.py`). Il refuse de tourner si les paires ne sont pas celles du manifeste, si la relecture n'a
pas validé le lot, si le dépôt n'est pas commité, ou si le modèle existe déjà. Le garde-fou compare la base, la v1 et
la v2 sur les questions des 19 fiches mises de côté, en PyTorch fp32, sans lire le lot de test ni le CDTN.

Usage, depuis la racine du dépôt, environnement de `scripts/evaluation/requirements-lock.txt` plus accelerate 1.15.0 :
    HF_HUB_OFFLINE=1 python scripts/adaptation/10_ajuster_encodeur_v2.py entrainer
    HF_HUB_OFFLINE=1 python scripts/adaptation/10_ajuster_encodeur_v2.py valider
Les sorties vont dans data/adaptation/v2/, qui n'est pas versionné.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[1]
_spec = importlib.util.spec_from_file_location("generer_v2", ICI / "09_generer_paires_v2.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)

MODELE_BASE = "intfloat/multilingual-e5-small"
REVISION_BASE = "614241f622f53c4eeff9890bdc4f31cfecc418b3"      # #49 et rag.py
DOSSIER_V1 = RACINE / "data/adaptation/pack_modele_ajuste_14oct/models/multilingual-e5-small-finetuned"
SHA256_POIDS_V1 = "5b8db94ade7f3a05678a6cb36e4e49aa7d24f71aaaedfc5fcef43d811d2dee06"   # protocole 05
DOSSIER_V2 = gen.SORTIES / "modele"
RAPPORT = gen.SORTIES / "rapport_entrainement_v2.json"
GARDE_FOU = gen.SORTIES / "garde_fou_v2.json"
BUDGET = 512

# Recette de 04_ajuster_encodeur.py (#49), inchangée ; un test la compare au source de ce script.
RECETTE = {"num_train_epochs": 2, "per_device_train_batch_size": 16, "learning_rate": 2e-5, "warmup_ratio": 0.1,
           "weight_decay": 0.01, "seed": 42}


class ErreurAjustement(RuntimeError):
    """Précondition non remplie : rien n'est entraîné ni écrit."""


def sha256_fichier(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 22), b""):
            h.update(bloc)
    return h.hexdigest()


def etat_git() -> dict:
    tete = subprocess.run(["git", "-C", str(RACINE), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    sale = subprocess.run(["git", "-C", str(RACINE), "status", "--porcelain", "--", "scripts", "docs/etudes/evaluation"],
                          capture_output=True, text=True).stdout.strip()
    return {"commit": tete, "propre": not sale}


def paires_controlees() -> tuple[list[dict], dict]:
    man = json.loads(gen.MANIFESTE.read_text(encoding="utf-8"))
    if sha256_fichier(gen.TRAIN) != man["entrainement"]["sha256"]:
        raise ErreurAjustement("Paires d'entraînement différentes du manifeste")
    bilan = gen.bilan_relecture()
    if not bilan["utilisable"]:
        raise ErreurAjustement(f"Relecture : {bilan['fausses']} paires fausses sur {bilan['relues']}, lot refusé")
    paires = [json.loads(l) for l in gen.TRAIN.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not all(p["query"].startswith("query: ") and p["passage"].startswith("passage: ") for p in paires):
        raise ErreurAjustement("Préfixes E5 absents")
    return paires, {"manifeste": man["entrainement"], "relecture": bilan}


def lots_meme_fiche(fiches: list[str], taille: int, tirages: int = 2000, graine: int = 0) -> float:
    """Part attendue des lots d'entraînement (tirage aléatoire sans remise, comme l'échantillonneur par défaut) qui
    contiennent deux passages d'une même fiche : estimation par simulation, à titre descriptif (section 8)."""
    rng = np.random.default_rng(graine)
    f = np.asarray(fiches)
    n_lots = math.ceil(len(f) / taille)
    touches = 0
    for _ in range(tirages // n_lots + 1):
        ordre = f[rng.permutation(len(f))]
        for k in range(n_lots):
            lot = ordre[k * taille:(k + 1) * taille]
            touches += len(set(lot)) < len(lot)
    return touches / ((tirages // n_lots + 1) * n_lots)


def entrainer() -> dict:
    git = etat_git()
    if not git["propre"]:
        raise ErreurAjustement("scripts ou protocoles modifiés et non commités")
    if DOSSIER_V2.exists():
        raise ErreurAjustement(f"{DOSSIER_V2} existe déjà : rien n'est écrasé")
    paires, controles = paires_controlees()
    import torch
    from datasets import Dataset
    from sentence_transformers import (SentenceTransformer, SentenceTransformerTrainer,
                                       SentenceTransformerTrainingArguments, losses)
    torch.manual_seed(RECETTE["seed"])
    jeu = Dataset.from_dict({"anchor": [p["query"] for p in paires], "positive": [p["passage"] for p in paires]})
    modele = SentenceTransformer(MODELE_BASE, revision=REVISION_BASE, device="cpu")
    perte = losses.MultipleNegativesRankingLoss(modele)
    sortie_trainer = gen.SORTIES / "trainer_v2"
    args = SentenceTransformerTrainingArguments(
        output_dir=str(sortie_trainer), logging_steps=2, save_strategy="no", report_to="none", use_cpu=True,
        **RECETTE)
    trainer = SentenceTransformerTrainer(model=modele, args=args, train_dataset=jeu, loss=perte)
    t0 = time.time()
    resultat = trainer.train()
    duree = time.time() - t0
    modele.save_pretrained(str(DOSSIER_V2))
    pas = trainer.state.global_step
    import accelerate, datasets, sentence_transformers, transformers
    rapport = {
        "amendement": "A2 (#167)", "git": git, "paires": controles, "n_paires": len(paires),
        "modele_depart": {"depot": MODELE_BASE, "revision": REVISION_BASE}, "recette": RECETTE,
        "optimiseur": args.optim, "planificateur": args.lr_scheduler_type, "max_grad_norm": args.max_grad_norm,
        "pas": pas, "pas_d_echauffement": args.get_warmup_steps(pas), "appareil": str(modele.device),
        "duree_s": round(duree, 1), "perte_finale": resultat.training_loss, "journal": trainer.state.log_history,
        "lots_avec_deux_passages_d_une_fiche": lots_meme_fiche([p["url"] for p in paires],
                                                               RECETTE["per_device_train_batch_size"]),
        "versions": {"torch": torch.__version__, "transformers": transformers.__version__,
                     "sentence_transformers": sentence_transformers.__version__, "datasets": datasets.__version__,
                     "accelerate": accelerate.__version__},
        "poids": {"fichier": str((DOSSIER_V2 / "model.safetensors").relative_to(RACINE)),
                  "sha256": sha256_fichier(DOSSIER_V2 / "model.safetensors")},
        "ecrit_le": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    gen.ecrire_une_fois(RAPPORT, rapport)
    print(json.dumps({k: v for k, v in rapport.items() if k != "journal"}, ensure_ascii=False, indent=1))
    return rapport


# Garde-fou (section 4)

def encodeur(dossier_ou_depot: str, revision: str | None = None):
    """fp32 sur processeur, tokeniseur de l'encodeur de base, comme l'index de l'ajusté (#164)."""
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer
    kw = {"revision": revision} if revision else {}
    m = SentenceTransformer(dossier_ou_depot, device="cpu", **kw)
    m.float()
    m.eval()
    base = AutoTokenizer.from_pretrained(MODELE_BASE, revision=REVISION_BASE)
    m[0].processor = base
    if m.tokenizer is not base:
        raise ErreurAjustement("Le tokeniseur de base n'a pas remplacé celui du modèle")
    m.max_seq_length = BUDGET
    return m


def classements(m, questions: list[str], passages: list[str], profondeur: int = 10) -> np.ndarray:
    P = m.encode(passages, batch_size=32, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    Q = m.encode([f"query: {q}" for q in questions], batch_size=32, normalize_embeddings=True,
                 convert_to_numpy=True, show_progress_bar=False)
    s = Q.astype(np.float32) @ P.astype(np.float32).T
    return np.argsort(-s, axis=1, kind="stable")[:, :profondeur]


def metriques(ordres: np.ndarray, cibles: list[int], fiche_de: list[str], fiches_cibles: list[str]) -> dict:
    rangs = [next((r for r, i in enumerate(o.tolist(), 1) if i == c), None) for o, c in zip(ordres, cibles)]
    n = len(rangs)
    return {"questions": n,
            "recall@1": sum(r is not None and r <= 1 for r in rangs) / n,
            "recall@5": sum(r is not None and r <= 5 for r in rangs) / n,
            "recall@10": sum(r is not None for r in rangs) / n,
            "mrr@10": sum(1 / r for r in rangs if r) / n,
            "recall@5_fiche": sum(any(fiche_de[i] == f for i in o[:5].tolist()) for o, f in zip(ordres, fiches_cibles)) / n,
            "succes@5": [r is not None and r <= 5 for r in rangs]}


def valider() -> dict:
    if GARDE_FOU.exists():
        raise ErreurAjustement("Garde-fou déjà calculé : rien n'est écrasé")
    rapport = json.loads(RAPPORT.read_text(encoding="utf-8"))
    if sha256_fichier(DOSSIER_V2 / "model.safetensors") != rapport["poids"]["sha256"]:
        raise ErreurAjustement("Poids de la v2 différents de ceux de l'entraînement")
    if sha256_fichier(DOSSIER_V1 / "model.safetensors") != SHA256_POIDS_V1:
        raise ErreurAjustement("Poids de la v1 différents de ceux du protocole 05")
    man = json.loads(gen.MANIFESTE.read_text(encoding="utf-8"))
    if sha256_fichier(gen.VALIDATION) != man["validation"]["sha256"]:
        raise ErreurAjustement("Questions de validation différentes du manifeste")
    val = [json.loads(l) for l in gen.VALIDATION.read_text(encoding="utf-8").splitlines() if l.strip()]
    table = gen.charger_passages()
    site = json.loads(gen.PASSAGES_SITE.read_text(encoding="utf-8"))
    entree = dict(zip(table.passage_id, table.entree_encodeur))
    ids = [p["passage_id"] for p in site]
    passages = [entree[i] for i in ids]
    position = {i: k for k, i in enumerate(ids)}
    fiche_de = [gen.url_fiche(p["url"]) for p in site]
    cibles = [position[q["passage_id"]] for q in val]
    fiches_cibles = [gen.url_fiche(q["url"]) for q in val]
    questions = [q["question"] for q in val]
    res = {"amendement": "A2 (#167), section 4", "questions": len(val), "fiches": len(set(fiches_cibles)),
           "systemes": {}}
    succes = {}
    for nom, (source, rev) in {"base": (MODELE_BASE, REVISION_BASE), "v1": (str(DOSSIER_V1), None),
                               "v2": (str(DOSSIER_V2), None)}.items():
        m = metriques(classements(encodeur(source, rev), questions, passages), cibles, fiche_de, fiches_cibles)
        succes[nom] = m.pop("succes@5")
        res["systemes"][nom] = m
        print(nom, json.dumps(m), flush=True)
    sys.path.insert(0, str(RACINE / "scripts/evaluation"))
    from metrics import noninferiority_tango, paired_success_test
    for a, b in (("v2", "v1"), ("v2", "base"), ("v1", "base")):
        t = noninferiority_tango(succes[a], succes[b], margin=0.0, groups=fiches_cibles, level=0.95)
        p = paired_success_test(succes[a], succes[b], groups=fiches_cibles)
        res[f"{a} moins {b}"] = {"ecart": t["difference"], "ic95_tango": list(t["ci_score"]),
                                 "effet_de_plan": t["design_effect"], "a_seul": t["n_10_A_only"],
                                 "b_seul": t["n_01_B_only"], "p_mcnemar": p["p_value"]}
    r2, r1 = res["systemes"]["v2"]["recall@5"], res["systemes"]["v1"]["recall@5"]
    res["regle"] = "la mesure continue si le Recall@5 de la v2 dépasse strictement celui de la v1"
    res["passe"] = bool(r2 > r1)
    gen.ecrire_une_fois(GARDE_FOU, res)
    print(json.dumps({k: v for k, v in res.items() if k != "systemes"}, ensure_ascii=False, indent=1))
    return res


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("commande", choices=("entrainer", "valider"))
    a = p.parse_args(argv)
    entrainer() if a.commande == "entrainer" else valider()
    return 0


if __name__ == "__main__":
    sys.exit(main())
