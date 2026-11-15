"""Mesure de l'encodeur ajusté (#49) selon le protocole 05 et son amendement A1 (#164).

Le protocole 05 (`docs/etudes/evaluation/05_protocole_ajustement.md`), figé le 14 octobre, fixe la règle de déploiement,
les fichiers et leurs empreintes, les jeux et les métriques ; l'amendement A1 (`05_amendement_A1.md`) ne change que le
calendrier et déclare ses écarts. Les vecteurs des questions viennent du navigateur (page `encodage_navigateur.html`,
pilotée par `encoder_navigateur.py`) ; les index des passages sont en fp32.

Commandes, depuis la racine du dépôt, environnement de `scripts/evaluation/requirements-lock.txt`, HF_HUB_OFFLINE=1 :
    python scripts/evaluation/ajustement_05.py index        # index fp32 de l'ajusté, comparé à celui de Remy
    python scripts/evaluation/ajustement_05.py controle     # reproduction du notebook 03 (amendement A1, section 4)
    python scripts/evaluation/ajustement_05.py mesurer --mode developpement   # lot de calibration seulement
    python scripts/evaluation/ajustement_05.py mesurer --mode mesure          # deux exécutions identiques exigées
    python scripts/evaluation/ajustement_05.py site --modele <dossier élagué>   # front/public/index_ajuste/ (section 5)
Mesures descriptives du site qui sert l'ajusté (A2, A3) : scripts/evaluation/mesures_site_164.py.
Comme tout fichier de `data/`, les sorties ne sont pas versionnées ; leurs empreintes sont publiées sur le #164.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _sous in ("scripts/evaluation", "scripts/rag", "scripts/recuperation"):
    if str(RACINE / _sous) not in sys.path:
        sys.path.insert(0, str(RACINE / _sous))

from metrics import noninferiority_tango, paired_success_test  # noqa: E402
from pertinence import IndexPertinence  # noqa: E402

D = RACINE / "data"
PROTOCOLE_05 = RACINE / "docs/etudes/evaluation/05_protocole_ajustement.md"
AMENDEMENT_A1 = RACINE / "docs/etudes/evaluation/05_amendement_A1.md"
DOSSIER_AJUSTE = D / "adaptation/pack_modele_ajuste_14oct/models/multilingual-e5-small-finetuned"
INDEX_REMY = D / "adaptation/pack_modele_ajuste_14oct/data/adaptation/passage_embeddings_apres.npy"
NAV = D / "adaptation/navigateur"
VECTEURS = NAV / "vecteurs"
INDEX_AJUSTE = NAV / "index_ajuste.f32"
POPULATION_CDTN = D / "evaluation/recuperation/population.json"
VECTEURS_NB03 = D / "evaluation/notebook03/vecteurs_navigateur.json"
SORTIES = D / "evaluation/ajustement_05"

# Empreintes (protocole 05, section 2 ; amendement A1, section 4). SHA256_AMENDEMENT est inscrit au gel de A1.
EMPREINTES = {
    "protocole_05": (PROTOCOLE_05, "f2c8169d41823e745bcfe80eb9839691362b30e76353bb33ba9e9814b9b319f7"),
    "poids_ajuste": (DOSSIER_AJUSTE / "model.safetensors", "5b8db94ade7f3a05678a6cb36e4e49aa7d24f71aaaedfc5fcef43d811d2dee06"),
    "q8_ajuste": (NAV / "ajuste/onnx/model_quantized.onnx", "934a202bee5599fc45c0cb753414a7b2b490605bed84e72f471072e6ee53d047"),
    "q8_base": (NAV / "base/onnx/model_quantized.onnx", "f80102d3f2a1229f387d3c81909990d8945513e347b0eab049f7de3c6f98c193"),
    "index_remy": (INDEX_REMY, "94e9f52a67b8e259bf04d341338e2e51f558661fbefb1502f6b0049fe218b3ed"),
    "jugements_cdtn": (RACINE / "evaluation/cdtn/jugements.csv", "0ddf16834b9ebdb2c9c71eeb78df2f2412130473dc9f3af892c7f757cc131968"),
    "population_cdtn": (POPULATION_CDTN, "ecc13431a21ef16c70a028a746eccd687c4f5c413572e9c57552755351a832d3"),
    "vecteurs_notebook03": (VECTEURS_NB03, "db7e8d54c609940e534a6754b4de96373d25cca43e52f9d15c1060d89d451856"),
}
SHA256_AMENDEMENT: str | None = "be9b6fd731487838455f965a67beabd4b2e41932a0b8c2ba33805218f6cb48b9"   # figé le 15/11 (#164)
COSINUS_MIN_INDEX = 0.9999        # contrôle préalable du 14 octobre : 0,99999984 au minimum
TOLERANCE_NORME = 1e-5


class ErreurMesure05(RuntimeError):
    """Précondition non remplie : rien n'est calculé ni écrit."""


def sha256_fichier(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 22), b""):
            h.update(bloc)
    return h.hexdigest()


def verifier_empreintes(cles=None) -> dict:
    sortie = {}
    for cle, (chemin, attendue) in EMPREINTES.items():
        if cles is not None and cle not in cles:
            continue
        if not Path(chemin).is_file() or sha256_fichier(chemin) != attendue:
            raise ErreurMesure05(f"{cle} : fichier absent ou d'empreinte différente ({chemin})")
        sortie[cle] = attendue
    return sortie


def ecrire_une_fois(chemin: Path, contenu: dict) -> str:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    texte = json.dumps(contenu, ensure_ascii=False, indent=1, allow_nan=False) + "\n"
    with open(chemin, "x", encoding="utf-8") as f:
        f.write(texte)
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()


def table_et_index_site():
    """Table M2 alignée sur l'index du site, contrôlée comme dans la récupération v2."""
    import rag
    import recuperation as rc
    index = rag.charger_index()
    return rc.charger_passages_m2(index), index


# Index de l'ajusté (protocole 05, section 2, « Index »)

def encodeur_ajuste():
    """Poids ajustés, tokeniseur de l'encodeur de base (décision du gel), fp32 sur processeur."""
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer
    import rag
    modele = SentenceTransformer(str(DOSSIER_AJUSTE), device="cpu")
    modele.float()
    modele.eval()
    # sentence-transformers 6 : le tokeniseur est le « processor » du module Transformer (propriété tokenizer en lecture)
    base = AutoTokenizer.from_pretrained(rag.MODELE_E5, revision=rag.REVISION_E5)
    modele[0].processor = base
    if modele.tokenizer is not base:
        raise ErreurMesure05("Le tokeniseur de base n'a pas remplacé celui de l'ajusté")
    modele.max_seq_length = rag.BUDGET_E5
    return modele


def construire_index() -> dict:
    verifier_empreintes({"poids_ajuste", "index_remy"})
    table, _ = table_et_index_site()
    modele = encodeur_ajuste()
    textes = table.entree_encodeur.tolist()
    longueurs = [len(modele.tokenizer(t, truncation=False)["input_ids"]) for t in textes]
    if max(longueurs) > 512:
        raise ErreurMesure05("Passage de plus de 512 tokens : aucune troncature n'est admise")
    m = np.asarray(modele.encode(textes, batch_size=32, normalize_embeddings=True, convert_to_numpy=True,
                                 show_progress_bar=False), dtype=np.float32)
    normes = np.linalg.norm(m, axis=1)
    if m.shape != (4240, 384) or not np.isfinite(m).all() or np.abs(normes - 1).max() >= TOLERANCE_NORME:
        raise ErreurMesure05("Index ajusté de forme inattendue, non fini ou non normalisé")
    remy = np.load(INDEX_REMY).astype(np.float32)
    remy = remy / np.linalg.norm(remy, axis=1, keepdims=True)
    cosinus = (m * remy).sum(axis=1)
    plus_proche = (m @ remy.T).argmax(axis=1)
    differents = int((plus_proche != np.arange(len(m))).sum())
    if cosinus.min() < COSINUS_MIN_INDEX:
        raise ErreurMesure05(f"Index différent de celui de Remy : cosinus minimal {cosinus.min():.8f}")
    INDEX_AJUSTE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_AJUSTE, "xb") as f:
        f.write(m.astype("<f4").tobytes())
    resultat = {"fichier": str(INDEX_AJUSTE.relative_to(RACINE)), "sha256": sha256_fichier(INDEX_AJUSTE),
                "forme": list(m.shape), "cosinus_avec_remy": {"min": float(cosinus.min()), "median": float(np.median(cosinus))},
                "lignes_dont_le_plus_proche_differe": differents, "tokens_max": max(longueurs),
                "tokeniseur": "intfloat/multilingual-e5-small (révision de rag.py)"}
    ecrire_une_fois(INDEX_AJUSTE.with_suffix(".json"), resultat)
    print(json.dumps(resultat, ensure_ascii=False, indent=1))
    return resultat


def charger_index_ajuste() -> np.ndarray:
    meta = json.loads(INDEX_AJUSTE.with_suffix(".json").read_text(encoding="utf-8"))
    if sha256_fichier(INDEX_AJUSTE) != meta["sha256"]:
        raise ErreurMesure05("Index ajusté différent de celui construit")
    return np.fromfile(INDEX_AJUSTE, dtype="<f4").reshape(4240, 384)


# Vecteurs du navigateur

def charger_vecteurs(chemin: Path, modele_local: str | None) -> dict:
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    if "erreur" in d:
        raise ErreurMesure05(f"{chemin.name} : {d['erreur']}")
    if d.get("transformers_js") != "4.3.0" or d.get("dtype") != "q8":
        raise ErreurMesure05(f"{chemin.name} : bibliothèque ou précision inattendue")
    if modele_local is not None and (d.get("modele_local") != modele_local or
                                     d.get("sha256_q8") != EMPREINTES[f"q8_{modele_local}"][1]):
        raise ErreurMesure05(f"{chemin.name} : modèle local inattendu")
    v = np.asarray(d["vecteurs"], dtype=np.float32)
    if v.shape != (len(d["identifiants"]), 384) or np.abs(np.linalg.norm(v, axis=1) - 1).max() >= 1e-3:
        raise ErreurMesure05(f"{chemin.name} : vecteurs de forme inattendue ou non normalisés")
    return dict(zip(d["identifiants"], v))


def controle_reproduction() -> dict:
    """Amendement A1, section 4 : la base servie en local, sans interface, redonne bit à bit les 113 vecteurs du 13/10."""
    verifier_empreintes({"vecteurs_notebook03", "q8_base"})
    d0 = json.loads(VECTEURS_NB03.read_text(encoding="utf-8"))
    d1 = json.loads((VECTEURS / "vecteurs_navigateur_base.json").read_text(encoding="utf-8"))
    identiques = d0["identifiants"] == d1["identifiants"] and d0["vecteurs"] == d1["vecteurs"]
    resultat = {"textes": len(d0["identifiants"]), "identiques_bit_a_bit": identiques,
                "navigateur_13_octobre": d0["navigateur"], "navigateur_controle": d1["navigateur"],
                "vecteurs_differents": sum(a != b for a, b in zip(d0["vecteurs"], d1["vecteurs"]))}
    print(json.dumps(resultat, ensure_ascii=False, indent=1))
    if not identiques:
        raise ErreurMesure05("Reproduction du notebook 03 non conforme : rien n'est mesuré")
    return resultat


# Métriques (protocole 05, section 3)

def rangs_pertinents(vecteurs: np.ndarray, matrice: np.ndarray, pertinents: list[set], profondeur: int = 10) -> list[list[int]]:
    """Pour chaque question, les rangs (1 à profondeur) des passages pertinents dans le classement par produit scalaire,
    à score égal dans l'ordre de l'index (tri stable, comme rank_by_score)."""
    sortie = []
    for v, p in zip(vecteurs, pertinents):
        ordre = np.argsort(-(matrice @ v), kind="stable")[:profondeur]
        sortie.append([r for r, i in enumerate(ordre.tolist(), 1) if i in p])
    return sortie


def succes_a(rangs: list[list[int]], k: int) -> list[bool]:
    return [any(r <= k for r in rs) for rs in rangs]


def mrr10(rangs: list[list[int]]) -> float:
    return float(np.mean([1 / min(rs) if rs else 0.0 for rs in rangs]))


def systeme(vecteurs, matrice, pertinents, fiches_pertinentes, url_passage) -> dict:
    rangs = rangs_pertinents(vecteurs, matrice, pertinents)
    top5 = [np.argsort(-(matrice @ v), kind="stable")[:5].tolist() for v in vecteurs]
    fiche5 = [any(url_passage[i] in f for i in t) for t, f in zip(top5, fiches_pertinentes)]
    return {"rangs": rangs, "r1": succes_a(rangs, 1), "r5": succes_a(rangs, 5), "r10": succes_a(rangs, 10),
            "fiche5": fiche5, "mrr10": mrr10(rangs)}


def resume(s: dict) -> dict:
    n = len(s["r5"])
    return {"questions": n, "recall@1": sum(s["r1"]) / n, "recall@5": sum(s["r5"]) / n, "recall@10": sum(s["r10"]) / n,
            "mrr@10": s["mrr10"], "recall@5_fiche": sum(s["fiche5"]) / n}


def ecart(sa: list[bool], sb: list[bool], groupes: list) -> dict:
    """Recall@5 de l'ajusté moins la base servie : intervalle du score de Tango corrigé de l'effet de plan, avec le
    test de McNemar exact et le test groupé, à titre descriptif."""
    t = noninferiority_tango(sa, sb, margin=0.0, groups=groupes, level=0.95)
    m = paired_success_test(sa, sb, groups=groupes)
    return {"ecart": t["difference"], "ic95_tango": list(t["ci_score"]), "effet_de_plan": t["design_effect"],
            "ajuste_seul": t["n_10_A_only"], "base_seule": t["n_01_B_only"], "p_mcnemar": m["p_value"],
            "p_groupe": m.get("p_value_groups")}


def auc(scores_positifs, scores_negatifs) -> float:
    """Probabilité qu'une question du corpus ait un score maximal plus élevé qu'une question hors corpus (ex aequo : 1/2)."""
    p, n = np.asarray(scores_positifs), np.asarray(scores_negatifs)
    return float(((p[:, None] > n[None, :]).sum() + 0.5 * (p[:, None] == n[None, :]).sum()) / (len(p) * len(n)))


def jeu_equipe(lot: str, table, matrices: dict, vecteurs: dict) -> dict:
    import mesure
    questions = mesure.lire_jeu(lot)
    corpus = [q for q in questions if q["type"] == "dans_corpus"]
    index_p = IndexPertinence(table.texte.tolist())
    url_passage = [u.rstrip("/") for u in table.url]
    pertinents = [set(index_p.pertinents(q["extrait"])) for q in corpus]
    fiches = [{url_passage[i] for i in p} for p in pertinents]
    groupes = [q["fiche"] for q in corpus]
    res = {"lot": lot, "questions_corpus": len(corpus), "fiches": len(set(groupes)), "systemes": {}}
    succes = {}
    for nom in ("base", "ajuste"):
        v = np.stack([vecteurs[nom][q["id"]] for q in corpus])
        s = systeme(v, matrices[nom], pertinents, fiches, url_passage)
        succes[nom] = s
        res["systemes"][nom] = resume(s)
        hors = [q for q in questions if q["type"] == "hors_corpus"]
        if hors:
            sc = [float((matrices[nom] @ vecteurs[nom][q["id"]]).max()) for q in corpus]
            sh = [float((matrices[nom] @ vecteurs[nom][q["id"]]).max()) for q in hors]
            res["systemes"][nom]["auc_abstention"] = auc(sc, sh)
    res["ecart_recall5"] = ecart(succes["ajuste"]["r5"], succes["base"]["r5"], groupes)
    return res


def jeu_cdtn(table, matrices: dict, vecteurs: dict) -> dict:
    pop = json.loads(POPULATION_CDTN.read_text(encoding="utf-8"))
    url_passage = [u.rstrip("/") for u in table.url]
    formulations, pertinents, groupes = [], [], []
    for r in pop["requetes"]:
        for f in r["formulations"]:
            formulations.append(f["id"])
            pertinents.append(set(r["pertinents"]))
            groupes.append(r["id"])
    if len(formulations) != 494 or len(set(groupes)) != 131:
        raise ErreurMesure05("Population du CDTN différente de 131 requêtes et 494 formulations")
    fiches = [{url_passage[i] for i in p} for p in pertinents]
    res = {"requetes": 131, "formulations": 494, "systemes": {}}
    succes = {}
    for nom in ("base", "ajuste"):
        v = np.stack([vecteurs[nom][i] for i in formulations])
        succes[nom] = systeme(v, matrices[nom], pertinents, fiches, url_passage)
        res["systemes"][nom] = resume(succes[nom])
    res["ecart_recall5"] = ecart(succes["ajuste"]["r5"], succes["base"]["r5"], groupes)
    return res


def controle_notebook03(equipe: dict) -> dict:
    """La base servie, recalculée ici sur le lot de test, doit redonner les métriques publiées par le notebook 03
    (`resultats_mesure.json`, système « E5 servi », et l'AUC de l'abstention) ; sinon rien n'est décidé."""
    d = json.loads((D / "evaluation/notebook03/resultats_mesure.json").read_text(encoding="utf-8"))
    publie = next(m for m in d["metriques"] if m["système"] == "E5 servi")
    calcule = equipe["systemes"]["base"]
    paires = {"recall@1": "R@1", "recall@5": "R@5", "recall@10": "R@10", "mrr@10": "MRR@10", "recall@5_fiche": "R@5 fiche"}
    ecarts = {k: (calcule[k], publie[v]) for k, v in paires.items() if abs(calcule[k] - publie[v]) > 1e-12}
    if abs(calcule["auc_abstention"] - d["abstention"]["auc"]) > 1e-12:
        ecarts["auc_abstention"] = (calcule["auc_abstention"], d["abstention"]["auc"])
    if ecarts:
        raise ErreurMesure05(f"La base servie ne redonne pas le notebook 03 : {ecarts}")
    return {"conforme": True, "metriques_comparees": list(paires.values()) + ["AUC"]}


def decision(equipe: dict, cdtn: dict) -> dict:
    """Section 4 : servir l'ajusté si son écart observé de Recall@5 est positif ou nul sur les deux jeux (la parité,
    vérifiée le 14 octobre, et l'hébergement, contrôlé après la décision, sont les deux autres conditions)."""
    e, c = equipe["ecart_recall5"]["ecart"], cdtn["ecart_recall5"]["ecart"]
    servir = e >= 0 and c >= 0
    return {"ecart_jeu_equipe": e, "ecart_cdtn": c,
            "regle": "servir l'ajusté si les deux écarts observés sont positifs ou nuls (section 4)",
            "verdict": "servir l'ajusté, sous réserve de l'hébergement (section 5)" if servir else "garder l'encodeur de base",
            "ajuste_declare_meilleur": bool(equipe["ecart_recall5"]["ic95_tango"][0] > 0),
            "conclusion_statistique": ("l'ajusté est meilleur sur le jeu de l'équipe" if equipe["ecart_recall5"]["ic95_tango"][0] > 0
                                       else "écart non démontré sur le jeu de l'équipe")}


def mesurer(mode: str) -> dict:
    if mode not in ("developpement", "mesure"):
        raise ErreurMesure05("Mode inconnu")
    empreintes = verifier_empreintes()
    if mode == "mesure":
        if SHA256_AMENDEMENT is None or not AMENDEMENT_A1.is_file() or sha256_fichier(AMENDEMENT_A1) != SHA256_AMENDEMENT:
            raise ErreurMesure05("Amendement A1 non figé ou modifié : le lot de test et le CDTN ne sont pas lus")
        empreintes["amendement_a1"] = SHA256_AMENDEMENT
    table, index = table_et_index_site()
    matrices = {"base": index.matrice, "ajuste": charger_index_ajuste()}
    vecteurs = {"base": charger_vecteurs(VECTEURS_NB03, None),
                "ajuste": charger_vecteurs(VECTEURS / "vecteurs_navigateur_ajuste.json", "ajuste")}
    contenu = {"mode": mode, "empreintes": empreintes}
    if mode == "developpement":
        contenu["calibration"] = jeu_equipe("calibration", table, matrices, vecteurs)
    else:
        vecteurs_cdtn = {"base": charger_vecteurs(VECTEURS / "vecteurs_cdtn_mesure_base.json", "base"),
                         "ajuste": charger_vecteurs(VECTEURS / "vecteurs_cdtn_mesure_ajuste.json", "ajuste")}
        contenu["jeu_equipe"] = jeu_equipe("test", table, matrices, vecteurs)
        contenu["controle_notebook03"] = controle_notebook03(contenu["jeu_equipe"])
        contenu["cdtn"] = jeu_cdtn(table, matrices, vecteurs_cdtn)
        contenu["decision"] = decision(contenu["jeu_equipe"], contenu["cdtn"])
    precedent = sorted(SORTIES.glob(f"{mode}_*.json"))
    horodatage = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    chemin = SORTIES / f"{mode}_{horodatage}.json"
    empreinte = ecrire_une_fois(chemin, contenu)
    if precedent:
        # double exécution : le contenu doit être identique à celui de l'exécution précédente du même mode
        identique = json.loads(precedent[-1].read_text(encoding="utf-8")) == contenu
        print(f"seconde exécution : contenu {'identique' if identique else 'DIFFÉRENT'} de {precedent[-1].name}")
        if not identique:
            raise ErreurMesure05("Deux exécutions différentes : résultat non retenu")
    print(f"{chemin.relative_to(RACINE)} SHA-256 {empreinte}")
    print(json.dumps({k: v for k, v in contenu.items() if k != "empreintes"}, ensure_ascii=False, indent=1, default=float)[:4000])
    return contenu


# Hébergement (protocole 05, section 5) : dossier d'index du site pour l'encodeur ajusté

SITE = RACINE / "front/public"
DOSSIER_SITE_AJUSTE = SITE / "index_ajuste"


def construire_site(dossier_modele: str) -> dict:
    """Écrit front/public/index_ajuste/ : l'index fp32 de l'ajusté, les passages du site recopiés tels quels, et un
    en-tête qui ne diffère de celui de front/public/index/ que par le modèle et l'index. front/public/index/, que lit la
    chaîne du volet B et dont l'empreinte est dans son verrou (#131), n'est pas modifié."""
    modele = SITE / "modele" / dossier_modele
    onnx = modele / "onnx/model_quantized.onnx"
    if not onnx.is_file() or not dossier_modele.startswith("multilingual-e5-small-ajuste-q8-elague-"):
        raise ErreurMesure05("Dossier du modèle ajusté élagué introuvable")
    sha_onnx = sha256_fichier(onnx)
    if not dossier_modele.endswith(sha_onnx[:8]):
        raise ErreurMesure05("Le nom du dossier ne correspond pas à l'empreinte du modèle")
    entete = json.loads((SITE / "index/index_m2.json").read_text(encoding="utf-8"))
    meta = json.loads(INDEX_AJUSTE.with_suffix(".json").read_text(encoding="utf-8"))
    if sha256_fichier(INDEX_AJUSTE) != meta["sha256"]:
        raise ErreurMesure05("Index ajusté différent de celui construit")
    if sha256_fichier(SITE / "index/passages_m2.json") != entete["metadonnees"]["sha256"]:
        raise ErreurMesure05("Passages du site différents de leur en-tête")
    DOSSIER_SITE_AJUSTE.mkdir(parents=True, exist_ok=False)
    import shutil
    shutil.copyfile(INDEX_AJUSTE, DOSSIER_SITE_AJUSTE / "index_m2.f32")
    shutil.copyfile(SITE / "index/passages_m2.json", DOSSIER_SITE_AJUSTE / "passages_m2.json")
    entete["modele"] = {
        "emplacement": "site", "depot": dossier_modele, "revision": None, "dtype": "q8",
        "fichier": "onnx/model_quantized.onnx", "sha256": sha_onnx,
        "origine": {"depot": "multilingual-e5-small-finetuned (#49, PR #63)", "revision": None,
                    "sha256": EMPREINTES["q8_ajuste"][1],
                    "tokeniseur": "Xenova/multilingual-e5-small, révision 761b726dd34fb83930e26aab4e9ac3899aa1fa78",
                    "transformation": "élagage sans perte du vocabulaire (#50, scripts/allegement/elaguer_vocabulaire.py)"}}
    entete["index"] = {**entete["index"], "sha256": meta["sha256"],
                       "moteur": "PyTorch fp32 (encodeur ajusté #49, tokeniseur de intfloat/multilingual-e5-small)"}
    entete["source"] = {**entete["source"], "mesure": "protocole 05 et amendement A1 (#164)"}
    entete["produit_le"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    texte = json.dumps(entete, ensure_ascii=False, indent=1) + "\n"
    (DOSSIER_SITE_AJUSTE / "index_m2.json").write_text(texte, encoding="utf-8")
    resultat = {"dossier": str(DOSSIER_SITE_AJUSTE.relative_to(RACINE)), "modele": dossier_modele, "sha256_modele": sha_onnx,
                "fichiers": {f.name: sha256_fichier(f) for f in sorted(DOSSIER_SITE_AJUSTE.iterdir())}}
    print(json.dumps(resultat, ensure_ascii=False, indent=1))
    return resultat


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = p.add_subparsers(dest="commande", required=True)
    sp.add_parser("index")
    sp.add_parser("controle")
    pm = sp.add_parser("mesurer"); pm.add_argument("--mode", choices=("developpement", "mesure"), required=True)
    ps = sp.add_parser("site"); ps.add_argument("--modele", required=True, help="dossier du modèle élagué dans front/public/modele/")
    a = p.parse_args(argv)
    if a.commande == "index":
        construire_index()
    elif a.commande == "controle":
        controle_reproduction()
    elif a.commande == "site":
        construire_site(a.modele)
    else:
        mesurer(a.mode)
    return 0


if __name__ == "__main__":
    sys.exit(main())
