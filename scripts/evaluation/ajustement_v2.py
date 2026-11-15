"""Mesure de l'encodeur ajusté v2 (#167) selon l'amendement A2 du protocole 05 (sections 5 à 7).

Réutilise, sans les modifier, les fonctions de `ajustement_05.py` (index, métriques, écarts) et compare trois
systèmes : la base servie, la v1 servie depuis le 15 novembre et la v2. Les vecteurs des questions viennent du
navigateur (`encoder_navigateur.py --modele ajuste_v2`) ; les index des passages sont en fp32. La mesure ne lit le
lot de test et le CDTN que si l'amendement A2 est figé et si le garde-fou de la section 4 est passé, et elle exige de
retrouver, pour la base et la v1, les chiffres publiés le 15 novembre. Il n'y a pas de mode de développement : la page
d'encodage encode le lot de test avec le lot de calibration, ce qui n'est permis qu'après le gel.

Commandes, depuis la racine du dépôt, environnement de `scripts/evaluation/requirements-lock.txt`, HF_HUB_OFFLINE=1 :
    python scripts/evaluation/ajustement_v2.py index                       # index fp32 de la v2
    python scripts/evaluation/ajustement_v2.py mesurer                      # deux exécutions identiques exigées
Comme tout fichier de `data/`, les sorties ne sont pas versionnées ; leurs empreintes sont publiées sur le #167.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
if str(ICI) not in sys.path:
    sys.path.insert(0, str(ICI))
import ajustement_05 as a05  # noqa: E402

RACINE = a05.RACINE
D = a05.D
AMENDEMENT_A2 = RACINE / "docs/etudes/evaluation/05_amendement_A2.md"
V2 = D / "adaptation/v2"
DOSSIER_V2 = V2 / "modele"
GARDE_FOU = V2 / "garde_fou_v2.json"
INDEX_V2 = a05.NAV / "index_ajuste_v2.f32"
MESURE_A1 = D / "evaluation/ajustement_05/mesure_20261115T142540Z.json"
SORTIES = D / "evaluation/ajustement_v2"

# Empreintes inscrites au gel de l'amendement A2 (section 9) ; tant qu'elles valent None, seule la calibration est lue.
SHA256_AMENDEMENT_A2: str | None = None
EMPREINTES_A2: dict[str, tuple[Path, str | None]] = {
    "mesure_a1": (MESURE_A1, "d35b49365f0c36eea556b3ad847d3cc98975b30f759f1e9f7d122cfe1a992d90"),
    "poids_v2": (DOSSIER_V2 / "model.safetensors", None),
    "q8_v2": (a05.NAV / "ajuste_v2/onnx/model_quantized.onnx", None),
    "garde_fou": (GARDE_FOU, None),
}
SYSTEMES = ("base", "v1", "v2")
COMPARAISONS = (("v2", "v1"), ("v2", "base"), ("v1", "base"))


class ErreurMesureA2(RuntimeError):
    """Précondition non remplie : rien n'est calculé ni écrit."""


def verifier_empreintes_a2() -> dict:
    sortie = {}
    for cle, (chemin, attendue) in EMPREINTES_A2.items():
        if attendue is None:
            raise ErreurMesureA2(f"{cle} : empreinte non inscrite (amendement A2 non figé)")
        if not Path(chemin).is_file() or a05.sha256_fichier(chemin) != attendue:
            raise ErreurMesureA2(f"{cle} : fichier absent ou d'empreinte différente ({chemin})")
        sortie[cle] = attendue
    return sortie


# Index de la v2 (amendement A2, section 5)

def construire_index() -> dict:
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer
    import rag
    rapport = json.loads((V2 / "rapport_entrainement_v2.json").read_text(encoding="utf-8"))
    if a05.sha256_fichier(DOSSIER_V2 / "model.safetensors") != rapport["poids"]["sha256"]:
        raise ErreurMesureA2("Poids de la v2 différents de ceux de l'entraînement")
    table, _ = a05.table_et_index_site()
    modele = SentenceTransformer(str(DOSSIER_V2), device="cpu")
    modele.float()
    modele.eval()
    base = AutoTokenizer.from_pretrained(rag.MODELE_E5, revision=rag.REVISION_E5)
    modele[0].processor = base
    if modele.tokenizer is not base:
        raise ErreurMesureA2("Le tokeniseur de base n'a pas remplacé celui de la v2")
    modele.max_seq_length = rag.BUDGET_E5
    textes = table.entree_encodeur.tolist()
    if max(len(modele.tokenizer(t, truncation=False)["input_ids"]) for t in textes) > 512:
        raise ErreurMesureA2("Passage de plus de 512 tokens : aucune troncature n'est admise")
    m = np.asarray(modele.encode(textes, batch_size=32, normalize_embeddings=True, convert_to_numpy=True,
                                 show_progress_bar=False), dtype=np.float32)
    normes = np.linalg.norm(m, axis=1)
    if m.shape != (4240, 384) or not np.isfinite(m).all() or np.abs(normes - 1).max() >= a05.TOLERANCE_NORME:
        raise ErreurMesureA2("Index v2 de forme inattendue, non fini ou non normalisé")
    with open(INDEX_V2, "xb") as f:
        f.write(m.astype("<f4").tobytes())
    v1 = a05.charger_index_ajuste()
    resultat = {"fichier": str(INDEX_V2.relative_to(RACINE)), "sha256": a05.sha256_fichier(INDEX_V2),
                "forme": list(m.shape), "poids_v2": rapport["poids"]["sha256"],
                "cosinus_avec_v1": {"min": float((m * v1).sum(axis=1).min()), "median": float(np.median((m * v1).sum(axis=1)))},
                "tokeniseur": "intfloat/multilingual-e5-small (révision de rag.py)"}
    a05.ecrire_une_fois(INDEX_V2.with_suffix(".json"), resultat)
    print(json.dumps(resultat, ensure_ascii=False, indent=1))
    return resultat


def charger_index_v2() -> np.ndarray:
    meta = json.loads(INDEX_V2.with_suffix(".json").read_text(encoding="utf-8"))
    if a05.sha256_fichier(INDEX_V2) != meta["sha256"]:
        raise ErreurMesureA2("Index v2 différent de celui construit")
    return np.fromfile(INDEX_V2, dtype="<f4").reshape(4240, 384)


def charger_vecteurs(chemin: Path, modele_local: str | None, sha_q8: str | None) -> dict:
    """Comme ajustement_05.charger_vecteurs, avec l'empreinte du q8 attendue en paramètre."""
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    if "erreur" in d:
        raise ErreurMesureA2(f"{chemin.name} : {d['erreur']}")
    if d.get("transformers_js") != "4.3.0" or d.get("dtype") != "q8":
        raise ErreurMesureA2(f"{chemin.name} : bibliothèque ou précision inattendue")
    if modele_local is not None and (d.get("modele_local") != modele_local or d.get("sha256_q8") != sha_q8):
        raise ErreurMesureA2(f"{chemin.name} : modèle local inattendu")
    v = np.asarray(d["vecteurs"], dtype=np.float32)
    if v.shape != (len(d["identifiants"]), 384) or np.abs(np.linalg.norm(v, axis=1) - 1).max() >= 1e-3:
        raise ErreurMesureA2(f"{chemin.name} : vecteurs de forme inattendue ou non normalisés")
    return dict(zip(d["identifiants"], v))


# Mesure (amendement A2, section 6)

def comparer(succes: dict, groupes: list) -> dict:
    return {f"{a} moins {b}": a05.ecart(succes[a]["r5"], succes[b]["r5"], groupes) for a, b in COMPARAISONS}


def jeu_equipe(lot: str, table, matrices: dict, vecteurs: dict) -> dict:
    import mesure
    questions = mesure.lire_jeu(lot)
    corpus = [q for q in questions if q["type"] == "dans_corpus"]
    hors = [q for q in questions if q["type"] == "hors_corpus"]
    index_p = a05.IndexPertinence(table.texte.tolist())
    url_passage = [u.rstrip("/") for u in table.url]
    pertinents = [set(index_p.pertinents(q["extrait"])) for q in corpus]
    fiches = [{url_passage[i] for i in p} for p in pertinents]
    groupes = [q["fiche"] for q in corpus]
    res = {"lot": lot, "questions_corpus": len(corpus), "fiches": len(set(groupes)), "systemes": {}}
    succes = {}
    for nom in SYSTEMES:
        v = np.stack([vecteurs[nom][q["id"]] for q in corpus])
        succes[nom] = a05.systeme(v, matrices[nom], pertinents, fiches, url_passage)
        res["systemes"][nom] = a05.resume(succes[nom])
        if hors:
            sc = [float((matrices[nom] @ vecteurs[nom][q["id"]]).max()) for q in corpus]
            sh = [float((matrices[nom] @ vecteurs[nom][q["id"]]).max()) for q in hors]
            res["systemes"][nom]["auc_abstention"] = a05.auc(sc, sh)
    res["ecarts_recall5"] = comparer(succes, groupes)
    return res


def jeu_cdtn(table, matrices: dict, vecteurs: dict) -> dict:
    pop = json.loads(a05.POPULATION_CDTN.read_text(encoding="utf-8"))
    url_passage = [u.rstrip("/") for u in table.url]
    formulations, pertinents, groupes = [], [], []
    for r in pop["requetes"]:
        for f in r["formulations"]:
            formulations.append(f["id"])
            pertinents.append(set(r["pertinents"]))
            groupes.append(r["id"])
    if len(formulations) != 494 or len(set(groupes)) != 131:
        raise ErreurMesureA2("Population du CDTN différente de 131 requêtes et 494 formulations")
    fiches = [{url_passage[i] for i in p} for p in pertinents]
    res = {"requetes": 131, "formulations": 494, "systemes": {}}
    succes = {}
    for nom in SYSTEMES:
        v = np.stack([vecteurs[nom][i] for i in formulations])
        succes[nom] = a05.systeme(v, matrices[nom], pertinents, fiches, url_passage)
        res["systemes"][nom] = a05.resume(succes[nom])
    res["ecarts_recall5"] = comparer(succes, groupes)
    return res


def controle_a1(equipe: dict, cdtn: dict) -> dict:
    """Section 6 : la base et la v1, recalculées ici, redonnent exactement la mesure publiée le 15 novembre."""
    a1 = json.loads(MESURE_A1.read_text(encoding="utf-8"))
    ecarts = {}
    for jeu, nouveau, ancien in (("lot de test", equipe, a1["jeu_equipe"]), ("CDTN", cdtn, a1["cdtn"])):
        for nom, nom_a1 in (("base", "base"), ("v1", "ajuste")):
            for k, v in ancien["systemes"][nom_a1].items():
                if abs(nouveau["systemes"][nom][k] - v) > 1e-12:
                    ecarts[f"{jeu} {nom} {k}"] = (nouveau["systemes"][nom][k], v)
        for k, v in ancien["ecart_recall5"].items():
            w = nouveau["ecarts_recall5"]["v1 moins base"][k]
            if (abs(np.asarray(w, dtype=float) - np.asarray(v, dtype=float)) > 1e-12).any():
                ecarts[f"{jeu} écart v1 moins base {k}"] = (w, v)
    if ecarts:
        raise ErreurMesureA2(f"La base et la v1 ne redonnent pas la mesure du 15 novembre : {ecarts}")
    return {"conforme": True, "fichier": str(MESURE_A1.relative_to(RACINE))}


def decision(equipe: dict, cdtn: dict) -> dict:
    """Section 7 : la v2 remplace la v1 si les deux écarts observés sont positifs ou nuls et l'un d'eux strictement
    positif (garde-fou et empreintes contrôlés avant la lecture ; hébergement validé après la décision)."""
    e = equipe["ecarts_recall5"]["v2 moins v1"]
    c = cdtn["ecarts_recall5"]["v2 moins v1"]
    servir = e["ecart"] >= 0 and c["ecart"] >= 0 and (e["ecart"] > 0 or c["ecart"] > 0)
    return {"ecart_lot_de_test": e["ecart"], "ecart_cdtn": c["ecart"],
            "regle": "servir la v2 si les deux écarts observés (v2 moins v1) sont positifs ou nuls, et l'un d'eux "
                     "strictement positif (amendement A2, section 7)",
            "verdict": "servir la v2, sous réserve de l'hébergement (section 5)" if servir else "garder la v1",
            "v2_meilleure_sur_le_lot_de_test": bool(e["ic95_tango"][0] > 0),
            "v2_meilleure_sur_le_cdtn": bool(c["ic95_tango"][0] > 0)}


def mesurer() -> dict:
    garde = json.loads(GARDE_FOU.read_text(encoding="utf-8"))
    if not garde.get("passe"):
        raise ErreurMesureA2("Garde-fou de la section 4 non passé : rien n'est mesuré")
    empreintes = {"a1": a05.verifier_empreintes()}
    if (SHA256_AMENDEMENT_A2 is None or not AMENDEMENT_A2.is_file()
            or a05.sha256_fichier(AMENDEMENT_A2) != SHA256_AMENDEMENT_A2):
        raise ErreurMesureA2("Amendement A2 non figé ou modifié : le lot de test et le CDTN ne sont pas lus")
    empreintes["a2"] = {"amendement_a2": SHA256_AMENDEMENT_A2, **verifier_empreintes_a2()}
    sha_q8_v2 = a05.sha256_fichier(EMPREINTES_A2["q8_v2"][0])
    table, index = a05.table_et_index_site()
    matrices = {"base": index.matrice, "v1": a05.charger_index_ajuste(), "v2": charger_index_v2()}
    vecteurs = {"base": charger_vecteurs(a05.VECTEURS_NB03, None, None),
                "v1": charger_vecteurs(a05.VECTEURS / "vecteurs_navigateur_ajuste.json", "ajuste", a05.EMPREINTES["q8_ajuste"][1]),
                "v2": charger_vecteurs(a05.VECTEURS / "vecteurs_navigateur_ajuste_v2.json", "ajuste_v2", sha_q8_v2)}
    vecteurs_cdtn = {
        "base": charger_vecteurs(a05.VECTEURS / "vecteurs_cdtn_mesure_base.json", "base", a05.EMPREINTES["q8_base"][1]),
        "v1": charger_vecteurs(a05.VECTEURS / "vecteurs_cdtn_mesure_ajuste.json", "ajuste", a05.EMPREINTES["q8_ajuste"][1]),
        "v2": charger_vecteurs(a05.VECTEURS / "vecteurs_cdtn_mesure_ajuste_v2.json", "ajuste_v2", sha_q8_v2)}
    contenu = {"empreintes": empreintes, "garde_fou": {k: garde[k] for k in ("passe", "regle")}}
    contenu["lot_de_test"] = jeu_equipe("test", table, matrices, vecteurs)
    contenu["cdtn"] = jeu_cdtn(table, matrices, vecteurs_cdtn)
    contenu["controle_a1"] = controle_a1(contenu["lot_de_test"], contenu["cdtn"])
    contenu["decision"] = decision(contenu["lot_de_test"], contenu["cdtn"])
    precedent = sorted(SORTIES.glob("mesure_*.json"))
    chemin = SORTIES / f"mesure_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    empreinte = a05.ecrire_une_fois(chemin, contenu)
    if precedent:
        identique = json.loads(precedent[-1].read_text(encoding="utf-8")) == contenu
        print(f"seconde exécution : contenu {'identique' if identique else 'DIFFÉRENT'} de {precedent[-1].name}")
        if not identique:
            raise ErreurMesureA2("Deux exécutions différentes : résultat non retenu")
    print(f"{chemin.relative_to(RACINE) if chemin.is_relative_to(RACINE) else chemin} SHA-256 {empreinte}")
    print(json.dumps({k: v for k, v in contenu.items() if k != "empreintes"}, ensure_ascii=False, indent=1, default=float)[:6000])
    return contenu


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = p.add_subparsers(dest="commande", required=True)
    sp.add_parser("index")
    sp.add_parser("mesurer")
    a = p.parse_args(argv)
    construire_index() if a.commande == "index" else mesurer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
