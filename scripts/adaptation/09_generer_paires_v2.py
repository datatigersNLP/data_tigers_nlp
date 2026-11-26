"""Paires d'entraînement de l'encodeur ajusté v2 (#167, amendement A2 du protocole 05, section 2).

Une question par passage entraînable, générée par le témoin T (Qwen2.5-7B-Instruct Q4_K_M) servi par Ollama sur
127.0.0.1, avec la consigne de `03_generer_paires_locales.py` (#49) mot pour mot, sans troncature du passage ; puis les
filtres de la #49 dans le même ordre, et le retrait des doublons. Rien n'est écrasé : chaque question générée s'ajoute
à un fichier partiel, qui permet de reprendre une génération interrompue ; `assembler` contrôle ce fichier avant
d'écrire, une seule fois, les paires d'entraînement et de validation.

Usage, depuis la racine du dépôt, environnement de `scripts/evaluation/requirements-lock.txt` :
    python scripts/adaptation/09_generer_paires_v2.py preparer             # sélection et partition des passages
    python scripts/adaptation/09_generer_paires_v2.py generer --pilote 20   # essai de durée, jamais utilisé ensuite
    python scripts/adaptation/09_generer_paires_v2.py generer               # reprend là où le fichier partiel s'arrête
    python scripts/adaptation/09_generer_paires_v2.py assembler            # paires finales et manifeste
    python scripts/adaptation/09_generer_paires_v2.py relecture            # 30 paires tirées pour la relecture
Les sorties vont dans data/adaptation/v2/, qui n'est pas versionné.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
PASSAGES = RACINE / "data/decoupage/passages/passages_m2.parquet"
SHA256_PASSAGES = "a7eabb623c9b4bbb7d9625bc86032439d6e90c76ff800de5099b42ecaaab61a4"
PASSAGES_SITE = RACINE / "front/public/index/passages_m2.json"
# Jeu figé, comme scripts/rag/mesure.py (tag jeu-questions-v1)
JEU_COMMIT = "cdb48c97064de625df61703a9a41e106160e0f50"
FICHIER_JEU = "evaluation/questions/questions_annotees.csv"
SHA256_JEU = "807498144fec46722ffab045a87c191b6282a86300799976869d4d6c1755fb35"
# Fiche exclue par la #49 avant la réaffectation de Q018 (scripts/adaptation/README.md)
URL_RETIREE_DU_JEU = "https://travail-emploi.gouv.fr/les-heures-supplementaires-contreparties"
FICHES_EXCLUES, PASSAGES_EXCLUS = 67, 1463
TOKENS_MIN = 40
GRAINE = 20261115
PART_VALIDATION = 0.10

API = "http://127.0.0.1:11434"
MODELE = "qwen2.5-7b-instruct:temoin-q4_k_m-local"
DIGEST = "8a077f3d3f56b636face1357eba557b21e2ba68bc72ee81e48b377272da72f27"
VERSION_OLLAMA = "0.40.13"
OPTIONS = {"temperature": 0.3, "top_p": 0.9, "num_predict": 75}      # #49, plus une graine par passage

JACCARD_MAX = 0.40
LONGUEUR_MIN, LONGUEUR_MAX = 25, 220
META = ["selon le texte", "d'après le texte", "selon cet extrait", "ce document"]
# Ajout de l'amendement A2, décidé sur le pilote de 20 passages : renvoi à la source (« dans la fiche », « selon cet
# extrait »), sauf s'il s'agit d'un terme du droit du travail (« la fiche de paie », « l'extrait de casier »).
RENVOI_A_LA_SOURCE = re.compile(r"\b(?:dans|selon|d'après|d’après) (?:ce |cet |cette |la |le |l'|l’)"
                                r"(?:texte|extrait|fiche)\b(?!\s*(?:de|d'|d’|du|des)\b)")
PAIRES_MIN = 1500
N_RELECTURE, FAUX_MAX = 30, 3

# Consigne de 03_generer_paires_locales.py (#49), mot pour mot ; un test la compare au source de ce script.
GABARIT = """Tu es un salarié ou un travailleur qui cherche une information précise sur ses droits ou obligations.
À partir de l'extrait de fiche du ministère du Travail ci-dessous, formule une question réaliste, précise et naturelle en français qu'un salarié pourrait poser et dont la réponse figure dans cet extrait.

Règles impératives :
1. Formule UNIQUEMENT la question, sans introduction, sans guillemets, ni formule de politesse.
2. La question doit être autonome et compréhensible sans avoir lu le texte (pas de "Selon le texte", "D'après l'extrait").
3. Termine par un point d'interrogation.

Titre de la fiche : {titre}
Extrait :
{texte_passage}

Question :"""

SORTIES = RACINE / "data/adaptation/v2"
SELECTION = SORTIES / "selection.json"
PARTIEL = SORTIES / "generation.partiel.jsonl"
TRAIN = SORTIES / "train_paires_v2.jsonl"
VALIDATION = SORTIES / "validation_v2.jsonl"
MANIFESTE = SORTIES / "manifeste_paires_v2.json"
RELECTURE = SORTIES / "relecture_30.json"
VERDICTS = SORTIES / "relecture_30_verdicts.json"


class ErreurPaires(RuntimeError):
    """Précondition non remplie : rien n'est écrit."""


def sha256_octets(octets: bytes) -> str:
    return hashlib.sha256(octets).hexdigest()


def sha256_fichier(chemin: Path) -> str:
    return sha256_octets(Path(chemin).read_bytes())


def ecrire_une_fois(chemin: Path, contenu) -> str:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    texte = json.dumps(contenu, ensure_ascii=False, indent=1) + "\n"
    with open(chemin, "x", encoding="utf-8") as f:
        f.write(texte)
    return sha256_octets(texte.encode("utf-8"))


def ecrire_jsonl_une_fois(chemin: Path, lignes: list[dict]) -> str:
    texte = "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lignes)
    with open(chemin, "x", encoding="utf-8") as f:
        f.write(texte)
    return sha256_octets(texte.encode("utf-8"))


def url_fiche(url: str) -> str:
    return url.split("#", 1)[0].rstrip("/")


# Filtres de la #49 (03_generer_paires_locales.py), dans le même ordre

def normalize_tokens(text: str) -> set:
    return set(re.findall(r"\b\w{3,}\b", unicodedata.normalize("NFKC", text).lower()))


def jaccard_overlap(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def filtrer(brut: str, jetons_jeu: list[set]) -> tuple[str | None, str, float | None]:
    """(question gardée ou None, motif, Jaccard maximal) ; motif « gardee » si la question passe tous les filtres."""
    question = brut.strip().strip('"').strip("'").strip("«»").strip()
    lignes = [l.strip() for l in question.split("\n") if l.strip()]
    question = lignes[0] if lignes else ""
    if not question.endswith("?"):
        if "?" in question:
            question = question[:question.index("?") + 1]
        else:
            return None, "sans_point_d_interrogation", None
    if len(question) < LONGUEUR_MIN or len(question) > LONGUEUR_MAX:
        return None, "longueur", None
    if any(m in question.lower() for m in META):
        return None, "meta_formulation", None
    if RENVOI_A_LA_SOURCE.search(question.lower()):
        return None, "renvoi_a_la_source", None
    jetons = normalize_tokens(question)
    jmax = max((jaccard_overlap(jetons, t) for t in jetons_jeu), default=0.0)
    if jmax > JACCARD_MAX:
        return None, "jaccard", jmax
    return question, "gardee", jmax


def cle_doublon(question: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", question).lower().split())


# Entrées figées

def lire_jeu() -> list[dict]:
    try:
        octets = subprocess.run(["git", "-C", str(RACINE), "show", f"{JEU_COMMIT}:{FICHIER_JEU}"],
                                check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ErreurPaires("Jeu figé indisponible ; lancer git fetch origin --tags") from exc
    if sha256_octets(octets) != SHA256_JEU:
        raise ErreurPaires("Empreinte du jeu différente de celle du protocole")
    return list(csv.DictReader(io.StringIO(octets.decode("utf-8"), newline="")))


def fiches_exclues(jeu: list[dict]) -> set[str]:
    fiches = {url_fiche(q["url"]) for q in jeu if q["type"] == "dans_corpus"} | {URL_RETIREE_DU_JEU}
    if len(fiches) != FICHES_EXCLUES:
        raise ErreurPaires(f"{len(fiches)} fiches exclues au lieu de {FICHES_EXCLUES}")
    return fiches


def charger_passages():
    import pandas as pd
    if sha256_fichier(PASSAGES) != SHA256_PASSAGES:
        raise ErreurPaires("Passages M2 différents de ceux de l'amendement A2")
    table = pd.read_parquet(PASSAGES)
    site = json.loads(PASSAGES_SITE.read_text(encoding="utf-8"))
    if sorted(table.passage_id) != sorted(p["passage_id"] for p in site):
        raise ErreurPaires("Les passages M2 ne sont pas ceux de l'index du site")
    if not table.entree_encodeur.str.startswith("passage: ").all():
        raise ErreurPaires("Texte d'entrée de l'encodeur sans le préfixe passage:")
    return table


def selectionner(table, exclues: set[str]) -> dict:
    """Passages entraînables triés par identifiant, rang, graine et partition (amendement A2, section 2)."""
    fiche = table.url.map(url_fiche)
    exclus = int(fiche.isin(exclues).sum())
    if exclus != PASSAGES_EXCLUS:
        raise ErreurPaires(f"{exclus} passages exclus au lieu de {PASSAGES_EXCLUS}")
    garde = table[~fiche.isin(exclues) & (table.n_tokens >= TOKENS_MIN)].sort_values("passage_id", kind="stable")
    fiches = sorted(garde.url.map(url_fiche).unique())
    n_val = round(PART_VALIDATION * len(fiches))
    validation = set(np.random.default_rng(GRAINE).choice(fiches, size=n_val, replace=False).tolist())
    passages = [{"rang": r, "passage_id": p.passage_id, "fiche": url_fiche(p.url), "graine": GRAINE + r,
                 "partition": "validation" if url_fiche(p.url) in validation else "entrainement"}
                for r, p in enumerate(garde.itertuples(index=False))]
    return {"amendement": "A2 (#167)", "tokens_min": TOKENS_MIN, "graine": GRAINE, "fiches_exclues": len(exclues),
            "passages_exclus": exclus, "fiches": len(fiches), "fiches_validation": sorted(validation),
            "passages": passages,
            "effectifs": {"entrainement": sum(p["partition"] == "entrainement" for p in passages),
                          "validation": sum(p["partition"] == "validation" for p in passages)}}


def preparer() -> dict:
    sel = selectionner(charger_passages(), fiches_exclues(lire_jeu()))
    sel["sha256_passages"] = SHA256_PASSAGES
    sel["sha256_jeu"] = SHA256_JEU
    empreinte = ecrire_une_fois(SELECTION, sel)
    print(f"{len(sel['passages'])} passages sur {sel['fiches']} fiches ; {sel['effectifs']} ; "
          f"{len(sel['fiches_validation'])} fiches de validation ; {SELECTION.relative_to(RACINE)} SHA-256 {empreinte}")
    return sel


# Ollama, sur 127.0.0.1 seulement

def _api(chemin: str, donnees: dict | None = None, delai: int = 120) -> dict:
    if not API.startswith("http://127.0.0.1:"):
        raise ErreurPaires("Ollama doit être joint sur 127.0.0.1")
    corps = None if donnees is None else json.dumps(donnees).encode("utf-8")
    req = urllib.request.Request(API + chemin, data=corps, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=delai) as r:
        return json.loads(r.read().decode("utf-8"))


def verifier_ollama() -> dict:
    version = _api("/api/version").get("version")
    if version != VERSION_OLLAMA:
        raise ErreurPaires(f"Ollama {version} au lieu de {VERSION_OLLAMA}")
    modeles = {m["name"]: m["digest"] for m in _api("/api/tags")["models"]}
    if modeles.get(MODELE) != DIGEST:
        raise ErreurPaires(f"{MODELE} absent ou de digest différent")
    return {"version": version, "modele": MODELE, "digest": DIGEST}


def appeler_ollama(prompt: str, graine: int) -> dict:
    r = _api("/api/generate", {"model": MODELE, "prompt": prompt, "stream": False, "keep_alive": "30m",
                               "options": {**OPTIONS, "seed": graine}})
    if not isinstance(r.get("response"), str):
        raise ErreurPaires("Ollama n'a pas renvoyé de texte")
    return {"brut": r["response"], "done_reason": r.get("done_reason"), "eval_count": r.get("eval_count")}


def lire_selection() -> dict:
    sel = json.loads(SELECTION.read_text(encoding="utf-8"))
    if sel.get("sha256_passages") != SHA256_PASSAGES or sel.get("sha256_jeu") != SHA256_JEU:
        raise ErreurPaires("Sélection préparée sur d'autres entrées")
    return sel


def lire_partiel(chemin: Path) -> list[dict]:
    if not chemin.is_file():
        return []
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


def generer(pilote: int | None = None, appeler=appeler_ollama, verifier=verifier_ollama,
            chemin_partiel: Path | None = None) -> Path:
    """Génère, dans l'ordre des rangs, les questions des passages qui n'en ont pas encore ; chaque ligne est écrite et
    synchronisée sur le disque avant la suivante. En mode pilote, écrit dans un fichier à part, jamais réutilisé."""
    sel = lire_selection()
    table = charger_passages().set_index("passage_id")
    jetons_jeu = [normalize_tokens(q["question"]) for q in lire_jeu()]
    ollama = verifier()
    if pilote is not None:
        chemin = SORTIES / f"pilote_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonl"
        a_faire = sel["passages"][:pilote]
        mode = "x"
    else:
        chemin = chemin_partiel or PARTIEL
        faits = lire_partiel(chemin)
        attendus = [p["passage_id"] for p in sel["passages"][:len(faits)]]
        if [f["passage_id"] for f in faits] != attendus:
            raise ErreurPaires("Fichier partiel hors de l'ordre de la sélection : reprise refusée")
        a_faire = sel["passages"][len(faits):]
        mode = "a"
    debut = time.time()
    with open(chemin, mode, encoding="utf-8") as f:
        for i, p in enumerate(a_faire, 1):
            ligne = table.loc[p["passage_id"]]
            prompt = GABARIT.format(titre=ligne.titre_fiche, texte_passage=ligne.texte)
            t0 = time.time()
            rep = appeler(prompt, p["graine"])
            question, motif, jmax = filtrer(rep["brut"], jetons_jeu)
            f.write(json.dumps({**p, "brut": rep["brut"], "done_reason": rep["done_reason"],
                                "eval_count": rep["eval_count"], "question": question, "motif": motif,
                                "max_jaccard_jeu": jmax, "duree_s": round(time.time() - t0, 3),
                                "ollama": ollama}, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
            if i % 50 == 0 or i == len(a_faire):
                print(f"{i}/{len(a_faire)} en {time.time() - debut:.0f} s", flush=True)
    return chemin


def assembler(chemin_partiel: Path | None = None) -> dict:
    """Contrôle le fichier partiel (une ligne par passage, dans l'ordre), retire les doublons, puis écrit une seule
    fois les paires d'entraînement et de validation, et le manifeste."""
    sel = lire_selection()
    chemin = chemin_partiel or PARTIEL
    lignes = lire_partiel(chemin)
    if [l["passage_id"] for l in lignes] != [p["passage_id"] for p in sel["passages"]]:
        raise ErreurPaires("Génération incomplète ou dans un autre ordre que la sélection")
    if any(l["ollama"]["digest"] != DIGEST for l in lignes):
        raise ErreurPaires("Une question vient d'un autre modèle que T")
    table = charger_passages().set_index("passage_id")
    vues, sortie, motifs = set(), {"entrainement": [], "validation": []}, {}
    for l in lignes:
        motif = l["motif"]
        if motif == "gardee":
            cle = cle_doublon(l["question"])
            if cle in vues:
                motif = "doublon"
            else:
                vues.add(cle)
                t = table.loc[l["passage_id"]]
                sortie[l["partition"]].append({
                    "passage_id": l["passage_id"], "url": t.url, "titre_fiche": t.titre_fiche,
                    "question": l["question"], "query": f"query: {l['question']}", "passage": t.entree_encodeur,
                    "max_jaccard_jeu": round(l["max_jaccard_jeu"], 4)})
        motifs[motif] = motifs.get(motif, 0) + 1
    if len(sortie["entrainement"]) < PAIRES_MIN:
        raise ErreurPaires(f"{len(sortie['entrainement'])} paires d'entraînement, moins que {PAIRES_MIN}")
    manifeste = {
        "amendement": "A2 (#167)", "ecrit_le": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "selection": {"fichier": str(SELECTION.relative_to(RACINE)), "sha256": sha256_fichier(SELECTION)},
        "partiel": {"fichier": str(chemin.relative_to(RACINE)), "sha256": sha256_fichier(chemin)},
        "generateur": lignes[0]["ollama"], "options": OPTIONS, "motifs": motifs,
        "coupees_a_75_tokens": sum(l["done_reason"] == "length" for l in lignes),
        "paires": {k: len(v) for k, v in sortie.items()},
        "fiches": {k: len({p["url"] for p in v}) for k, v in sortie.items()},
    }
    manifeste["entrainement"] = {"fichier": str(TRAIN.relative_to(RACINE)),
                                 "sha256": ecrire_jsonl_une_fois(TRAIN, sortie["entrainement"])}
    manifeste["validation"] = {"fichier": str(VALIDATION.relative_to(RACINE)),
                               "sha256": ecrire_jsonl_une_fois(VALIDATION, sortie["validation"])}
    print(json.dumps(manifeste, ensure_ascii=False, indent=1))
    ecrire_une_fois(MANIFESTE, manifeste)
    return manifeste


def relecture() -> dict:
    """Tire 30 paires d'entraînement (graine GRAINE + 1) pour la relecture de l'amendement A2, section 2."""
    paires = [json.loads(l) for l in TRAIN.read_text(encoding="utf-8").splitlines()]
    man = json.loads(MANIFESTE.read_text(encoding="utf-8"))
    if sha256_fichier(TRAIN) != man["entrainement"]["sha256"]:
        raise ErreurPaires("Paires d'entraînement différentes du manifeste")
    idx = sorted(np.random.default_rng(GRAINE + 1).choice(len(paires), size=N_RELECTURE, replace=False).tolist())
    tirage = {"sha256_entrainement": man["entrainement"]["sha256"], "indices": idx,
              "paires": [{"indice": i, "passage_id": paires[i]["passage_id"], "question": paires[i]["question"],
                          "passage": paires[i]["passage"]} for i in idx]}
    print(f"{RELECTURE.relative_to(RACINE)} SHA-256 {ecrire_une_fois(RELECTURE, tirage)}")
    return tirage


def bilan_relecture() -> dict:
    """Verdicts de la relecture (fichier écrit à part) : mêmes paires que le tirage, au plus 3 fausses sur 30."""
    tirage = json.loads(RELECTURE.read_text(encoding="utf-8"))
    verdicts = json.loads(VERDICTS.read_text(encoding="utf-8"))
    if [v["indice"] for v in verdicts["verdicts"]] != tirage["indices"]:
        raise ErreurPaires("Les verdicts ne portent pas sur les paires tirées")
    if any(v["verdict"] not in ("juste", "fausse") for v in verdicts["verdicts"]):
        raise ErreurPaires("Verdict inconnu")
    faux = sum(v["verdict"] == "fausse" for v in verdicts["verdicts"])
    return {"fausses": faux, "relues": len(verdicts["verdicts"]), "utilisable": faux <= FAUX_MAX,
            "relecteur": verdicts.get("relecteur")}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = p.add_subparsers(dest="commande", required=True)
    sp.add_parser("preparer")
    pg = sp.add_parser("generer"); pg.add_argument("--pilote", type=int)
    sp.add_parser("assembler")
    sp.add_parser("relecture")
    sp.add_parser("bilan")
    a = p.parse_args(argv)
    if a.commande == "preparer":
        preparer()
    elif a.commande == "generer":
        print(generer(a.pilote))
    elif a.commande == "assembler":
        assembler()
    elif a.commande == "relecture":
        relecture()
    else:
        print(json.dumps(bilan_relecture(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
