"""Chaîne RAG B1 (#51), étape 1 : lecture contrôlée de l'index commun.

Ce module ne charge ni E5 ni Qwen. La ligne i de la matrice correspond au
passage i du JSON, dont les octets sont vérifiés avec le même manifeste.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np


RACINE = Path(__file__).resolve().parents[2]
DOSSIER_INDEX = RACINE / "front" / "public" / "index"
TOLERANCE_NORME = 1e-5  # même contrôle que le notebook 02


class ErreurIndex(ValueError):
    """Index absent, incompatible ou incohérent : ne pas poursuivre le RAG."""


@dataclass(frozen=True)
class IndexCommun:
    entete: dict
    matrice: np.ndarray
    passages: list[dict]


def _lire(chemin: Path) -> bytes:
    try:
        return chemin.read_bytes()
    except OSError as exc:
        raise ErreurIndex(f"Lecture impossible de {chemin.name} : {exc}") from exc


def _json(octets: bytes, nom: str):
    try:
        return json.loads(octets.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ErreurIndex(f"{nom} : JSON UTF-8 invalide") from exc


def _fichier_verifie(dossier: Path, description: dict) -> bytes:
    nom = description.get("fichier")
    empreinte = description.get("sha256")
    if (not isinstance(nom, str) or not nom or nom in {".", ".."}
            or "/" in nom or "\\" in nom or Path(nom).is_absolute()):
        raise ErreurIndex("Le manifeste doit désigner un fichier du dossier d'index")
    chemin = (dossier / nom).resolve()
    if chemin.parent != dossier:
        raise ErreurIndex(f"{nom} : fichier situé hors du dossier d'index")
    if not isinstance(empreinte, str) or re.fullmatch(r"[0-9a-f]{64}", empreinte) is None:
        raise ErreurIndex(f"{nom} : empreinte SHA-256 invalide dans le manifeste")
    octets = _lire(chemin)
    if hashlib.sha256(octets).hexdigest() != empreinte:
        raise ErreurIndex(f"{nom} : empreinte différente du manifeste")
    return octets


def charger_index(dossier: Path | str = DOSSIER_INDEX) -> IndexCommun:
    """Charge M2 fp32 sans régénérer, réordonner ni modifier ses fichiers.

    Les empreintes lient la matrice et les métadonnées à un même export du
    notebook 02. Elles ne prouvent pas la pertinence sémantique d'un passage.
    Le bloc « modele » décrit le navigateur ; il ne choisit pas notre E5 Python.
    """
    dossier = Path(dossier).resolve()
    entete = _json(_lire(dossier / "index_m2.json"), "index_m2.json")
    if not isinstance(entete, dict) or entete.get("format") != "index-e5-v1":
        raise ErreurIndex("Format attendu : index-e5-v1")
    for bloc in ("index", "metadonnees", "source", "requete"):
        if not isinstance(entete.get(bloc), dict):
            raise ErreurIndex(f"Bloc {bloc} absent ou invalide dans le manifeste")
    index, meta = entete["index"], entete["metadonnees"]
    n, d = index.get("nb_vecteurs"), index.get("dimension")
    if type(n) is not int or n <= 0 or type(d) is not int or d != 384:
        raise ErreurIndex("Dimensions attendues : N positif × 384")
    if type(meta.get("nb_passages")) is not int or meta["nb_passages"] != n:
        raise ErreurIndex("Nombre de passages différent du nombre de vecteurs")
    if (index.get("type") != "float32" or index.get("ordre_octets") != "little-endian"
            or index.get("disposition") != "ligne par ligne"):
        raise ErreurIndex("Matrice attendue : float32 petit-boutiste, ligne par ligne")
    if (entete["source"].get("decoupage") != "m2"
            or index.get("moteur") != "PyTorch fp32 (intfloat/multilingual-e5-small)"):
        raise ErreurIndex("Cette baseline exige l'index M2 de référence PyTorch fp32")
    requete = entete["requete"]
    if (requete.get("prefixe") != "query: " or requete.get("pooling") != "mean"
            or requete.get("normalize") is not True):
        raise ErreurIndex("Configuration E5 attendue : query: , mean, normalisation L2")

    octets = _fichier_verifie(dossier, index)
    if len(octets) != n * d * 4:
        raise ErreurIndex(f"Taille de matrice : {len(octets)} octets, attendu {n * d * 4}")
    matrice = np.frombuffer(octets, dtype="<f4").reshape(n, d)
    if not np.isfinite(matrice).all():
        raise ErreurIndex("La matrice contient des valeurs non finies")
    if np.any(np.abs(np.linalg.norm(matrice, axis=1) - 1) >= TOLERANCE_NORME):
        raise ErreurIndex("Les vecteurs ne sont pas normalisés à 1 ± 1e-5")

    passages = _json(_fichier_verifie(dossier, meta), meta["fichier"])
    if not isinstance(passages, list) or len(passages) != n:
        raise ErreurIndex(f"Le JSON des passages doit contenir {n} objets")
    ids = set()
    champs_texte = ("passage_id", "titre_fiche", "section_titre", "url", "url_citation", "date_maj", "texte")
    for i, passage in enumerate(passages):
        if not isinstance(passage, dict):
            raise ErreurIndex(f"Passage {i} : objet attendu")
        for champ in champs_texte:
            if not isinstance(passage.get(champ), str):
                raise ErreurIndex(f"Passage {i} : champ {champ} absent ou non textuel")
        for champ in ("chemin", "articles"):
            valeurs = passage.get(champ)
            if not isinstance(valeurs, list) or not all(isinstance(v, str) for v in valeurs):
                raise ErreurIndex(f"Passage {i} : champ {champ} doit être une liste de textes")
        pid = passage["passage_id"]
        if not pid.strip() or pid in ids:
            raise ErreurIndex(f"Passage {i} : passage_id vide ou dupliqué")
        if not passage["texte"].strip():
            raise ErreurIndex(f"Passage {i} : texte vide")
        ids.add(pid)
    # frombuffer s'appuie sur des bytes immuables : lecture seule, sans copie ni tri.
    return IndexCommun(entete, matrice, passages)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-index", action="store_true", required=True,
                        help="contrôler l'index commun sans charger de modèle")
    parser.add_argument("--index-dir", type=Path, default=DOSSIER_INDEX,
                        help="dossier contenant index_m2.json et ses deux fichiers")
    args = parser.parse_args(argv)
    try:
        index = charger_index(args.index_dir)
    except ErreurIndex as exc:
        print(f"Index refusé : {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "statut": "index_verifie",
        "nb_passages": len(index.passages),
        "dimension": index.matrice.shape[1],
        "sha256_index": index.entete["index"]["sha256"],
        "sha256_passages": index.entete["metadonnees"]["sha256"],
        "e5_charge": False,
        "ollama_appele": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
