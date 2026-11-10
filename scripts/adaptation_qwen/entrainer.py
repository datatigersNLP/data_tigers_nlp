"""Entraînement de l'adaptateur LoRA du volet B (#107, étape 29), sur le Mac de Mahé, avec mlx-lm.

Depuis la racine du dépôt, avec l'environnement de scripts/adaptation_qwen/requirements.txt :
    python scripts/adaptation_qwen/entrainer.py --lot v1-20261030 --run lora-v1 2>&1 | tee data/volet_b/adaptateurs/lora-v1.journal.txt
    python scripts/adaptation_qwen/entrainer.py --lot v1-20261030 --run essai-format --essai 2   # essai court

Le script refuse de lancer l'entraînement si :
- la relecture humaine du lot (étape 28) n'a pas conclu qu'il était utilisable, selon les règles de grille_relecture.py
  écrites avant la relecture, ou si la variante « passage retiré » doit en être retirée (l'essai court s'en dispense) ;
- la grille remplie ne reprend pas exactement le tirage du lot (ligne manquante, en double, étrangère ou modifiée), ou
  un verdict obligatoire y manque ;
- l'empreinte de train.jsonl ou de valid.jsonl diffère de celle du manifeste du lot ;
- les poids du modèle ne sont pas ceux de la révision publiée (c26a38f6) ;
- un fichier du modèle ou du lot est déchargé par iCloud ;
- les versions de mlx ou de mlx-lm diffèrent de requirements.txt ;
- l'adaptateur demandé existe déjà : un adaptateur n'est jamais remplacé ;
- scripts/ contient des modifications non committées, ou l'état git ne peut pas être lu (l'essai court s'en dispense) :
  le manifeste de l'adaptateur désigne le code par son commit.

Réglages fixés avant l'entraînement, à valider par Jibril et Remy : ceux de l'essai de faisabilité de la #109 (LoRA de
rang 8 sur les 16 dernières couches, lots de 1, contexte de 3 072 tokens, point de contrôle des gradients, perte sur la
seule réponse) et les valeurs de mlx-lm 0.32.2 pour l'échelle (20) et le taux d'apprentissage (1e-5), calibrés ensemble.
Deux époques. L'adaptateur retenu est le dernier : aucun point de contrôle n'est choisi d'après la validation, dont la
perte est seulement relevée.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import grille_relecture  # noqa: E402

MODELE = RACINE / "data" / "volet_b" / "qwen25-7b-instruct-4bit-mlx"
SHA256_POIDS = "86110f368236b53cf4c2336f991a85703b17bcc60bb75f292b4002ec0219f071"   # révision c26a38f6, publiée
DONNEES = RACINE / "data" / "volet_b" / "donnees_adaptation"
ADAPTATEURS = RACINE / "data" / "volet_b" / "adaptateurs"
VERSIONS = {"mlx": "0.32.4", "mlx-lm": "0.32.2"}
EPOQUES = 2
N_EVALUATIONS = 6
REGLAGES = {
    "fine_tune_type": "lora", "optimizer": "adam", "num_layers": 16, "batch_size": 1, "learning_rate": 1.0e-5,
    "max_seq_length": 3072, "grad_checkpoint": True, "mask_prompt": True, "seed": 20261106,
    "lora_parameters": {"rank": 8, "dropout": 0.0, "scale": 20.0}, "steps_per_report": 10, "val_batches": -1,
}
SF_DATALESS = 0x40000000


class ErreurEntrainement(ValueError):
    """Condition non satisfaite : l'entraînement ne doit pas être lancé."""


def sha256_fichier(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 22), b""):
            h.update(bloc)
    return h.hexdigest()


def fichiers_decharges(*dossiers: Path) -> list[str]:
    """Fichiers « dataless » (déchargés par iCloud) : leur lecture peut bloquer ou échouer en cours d'entraînement."""
    return sorted(str(p) for d in dossiers for p in Path(d).rglob("*")
                  if p.is_file() and not p.is_symlink() and getattr(os.lstat(p), "st_flags", 0) & SF_DATALESS)


def controler_relecture(lot: Path, exemples: list[dict]) -> dict:
    """exemples : train puis valid, dont les empreintes ont été contrôlées."""
    grille = lot / "grille_relecture.csv"
    if not grille.exists():
        raise ErreurEntrainement("Relecture de l'étape 28 absente : grille_relecture.csv introuvable")
    with open(grille, encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    try:
        grille_relecture.verifier_grille(lignes, exemples)
        bilan = grille_relecture.bilan(lignes)
    except ValueError as exc:
        raise ErreurEntrainement(f"Relecture incomplète ou non conforme : {exc}") from exc
    if not bilan["utilisable"]:
        raise ErreurEntrainement(f"Lot refusé par la relecture : {bilan['faux']} exemples faux sur {bilan['relus']}")
    if not bilan["garder_passage_retire"]:
        raise ErreurEntrainement("La relecture retire la variante « passage retiré » : réassembler le lot sans elle")
    return {**bilan, "grille_sha256": sha256_fichier(grille)}


def controler_lot(lot: Path) -> dict:
    manifeste = json.loads((lot / "manifeste.json").read_text(encoding="utf-8"))
    effectifs = {}
    for nom in ("train.jsonl", "valid.jsonl"):
        if sha256_fichier(lot / nom) != manifeste["sha256"][nom]:
            raise ErreurEntrainement(f"{nom} diffère du manifeste du lot")
        effectifs[nom] = sum(1 for l in (lot / nom).read_text(encoding="utf-8").splitlines() if l.strip())
    if manifeste["separation"]["violations"] != 0:
        raise ErreurEntrainement("Le manifeste du lot signale des violations de la séparation")
    return {"manifeste_sha256": sha256_fichier(lot / "manifeste.json"), "effectifs": effectifs,
            "sha256": {n: manifeste["sha256"][n] for n in ("train.jsonl", "valid.jsonl")}}


def configuration(lot: Path, adaptateur: Path, n_train: int, essai: int | None = None) -> dict:
    """Configuration complète passée à mlx_lm.lora : tout réglage est explicite, rien n'est laissé par défaut."""
    iters = essai if essai else EPOQUES * n_train // REGLAGES["batch_size"]
    pas = max(1, math.ceil(iters / N_EVALUATIONS))
    return {**REGLAGES, "model": str(MODELE), "train": True, "data": str(lot), "adapter_path": str(adaptateur),
            "iters": iters, "steps_per_eval": pas, "save_every": pas}


def versions() -> dict:
    from importlib.metadata import PackageNotFoundError, version
    trouvees = {}
    for p in VERSIONS:
        try:
            trouvees[p] = version(p)
        except PackageNotFoundError:
            trouvees[p] = None
    if trouvees != VERSIONS:
        raise ErreurEntrainement(f"Versions {trouvees}, attendues {VERSIONS} (requirements.txt)")
    return trouvees


def etat_git() -> dict:
    tete = subprocess.run(["git", "-C", str(RACINE), "rev-parse", "--verify", "HEAD"], capture_output=True, text=True)
    statut = subprocess.run(["git", "-C", str(RACINE), "status", "--porcelain", "--", "scripts"],
                            capture_output=True, text=True)
    commit = tete.stdout.strip()
    if tete.returncode or statut.returncode or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ErreurEntrainement(f"État git illisible dans {RACINE} : {(tete.stderr or statut.stderr).strip()[:200]}")
    return {"commit": commit, "scripts_modifies": bool(statut.stdout.strip())}


def entier_positif(texte: str) -> int:
    n = int(texte)
    if n <= 0:
        raise argparse.ArgumentTypeError("nombre d'itérations strictement positif attendu")
    return n


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lot", required=True)
    parser.add_argument("--run", required=True, help="nom de l'adaptateur, dossier dans data/volet_b/adaptateurs/")
    parser.add_argument("--essai", type=entier_positif,
                        help="nombre d'itérations d'un essai court (contrôles de la relecture et de git omis)")
    args = parser.parse_args(argv)
    if not all(re.fullmatch(r"[a-z0-9_-]{1,40}", x) for x in (args.lot, args.run)):
        print("Nom de lot ou d'exécution invalide", file=sys.stderr)
        return 2
    lot, adaptateur = DONNEES / args.lot, ADAPTATEURS / args.run
    try:
        if adaptateur.exists():
            raise ErreurEntrainement(f"{adaptateur} existe déjà : un adaptateur n'est jamais remplacé")
        if not (lot / "manifeste.json").is_file():
            raise ErreurEntrainement(f"Lot {args.lot} introuvable dans {DONNEES}")
        try:
            git = etat_git()
        except ErreurEntrainement:
            if not args.essai:
                raise
            git = {"commit": None, "scripts_modifies": None}
        if not args.essai and git["scripts_modifies"]:
            raise ErreurEntrainement("scripts/ diffère du commit courant : committer avant l'entraînement")
        decharges = fichiers_decharges(MODELE, lot)
        if decharges:
            raise ErreurEntrainement(f"{len(decharges)} fichiers déchargés par iCloud, dont {decharges[0]}")
        trouvees = versions()
        donnees = controler_lot(lot)
        bilan = None if args.essai else controler_relecture(lot, grille_relecture.lire_exemples(lot))
        if sha256_fichier(MODELE / "model.safetensors") != SHA256_POIDS:
            raise ErreurEntrainement("Poids du modèle différents de la révision publiée c26a38f6")
        config = configuration(lot, adaptateur, donnees["effectifs"]["train.jsonl"], args.essai)
    except ErreurEntrainement as exc:
        print(f"Entraînement refusé : {exc}", file=sys.stderr)
        return 1

    import yaml
    import mlx.core as mx
    from mlx_lm import lora
    ADAPTATEURS.mkdir(parents=True, exist_ok=True)
    chemin_config = ADAPTATEURS / f"{args.run}.config.yaml"
    with open(chemin_config, "x", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=True)
    debut = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    sys.argv = ["mlx_lm.lora", "--config", str(chemin_config)]
    lora.main()
    duree = time.perf_counter() - t0
    manifeste = {
        "run": args.run, "essai": bool(args.essai), "debut": debut.isoformat(timespec="seconds"),
        "duree_s": round(duree, 1), "pic_memoire_gio": round(mx.get_peak_memory() / 2**30, 2),
        "configuration": config, "configuration_sha256": sha256_fichier(chemin_config),
        "lot": {"nom": args.lot, **donnees}, "relecture": bilan, "poids_sha256": SHA256_POIDS,
        "adaptateur_sha256": {p.name: sha256_fichier(p) for p in sorted(adaptateur.iterdir()) if p.is_file()},
        "versions": {**trouvees, "python": platform.python_version(), "macos": platform.mac_ver()[0]},
        "git": git,
    }
    with open(ADAPTATEURS / f"{args.run}.manifeste.json", "x", encoding="utf-8") as f:
        f.write(json.dumps(manifeste, ensure_ascii=False, indent=1) + "\n")
    print(f"Adaptateur {adaptateur} : {config['iters']} itérations en {duree:.0f} s, "
          f"pic de {manifeste['pic_memoire_gio']} Gio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
