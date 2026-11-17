"""Mesures du protocole 10 (#171, section 7).

    python scripts/evaluation/mesures_10.py famille_a      # volet A : recherche dense servie contre fusion avec BM25 V3
    python scripts/evaluation/mesures_10.py famille_b      # volet B : récupération R0, R1, R2 (jeu v2, CDTN, jeu v1)
    python scripts/evaluation/mesures_10.py effet_k        # descriptif : 5 contre 10 passages (justification de k = 10)
    python scripts/evaluation/mesures_10.py bout_en_bout --etat B2 --phase adapte   # puis R1 adapte, R1 temoin (Ollama)
    python scripts/evaluation/mesures_10.py analyser_bout_en_bout

Famille A : D, la recherche dense du site (encodeur ajusté v1, requête q8 encodée dans le navigateur, index fp32) ;
F, la fusion RRF (k = 60, profondeur 100) de D et de BM25 V3. Critère principal : Recall@5 au passage selon D4.
Secondaire : une fiche pertinente parmi les fiches des 10 passages affichés. Règle (section 7) : F est adoptée si son
écart de Recall@5 avec D est positif ou nul sur le jeu v2 et sur le CDTN, et strictement positif sur l'un des deux.

Contrôle de reproduction préalable : D, recalculé ici sur le CDTN, doit redonner question par question le Recall@5
de l'ajusté publié par le protocole 05 (`mesure_20261115T142537Z.json`) ; sinon rien n'est conclu.

Famille B : R0 (E5 de base, 5 passages, B2), R1 (fusion RRF de l'E5 de base et de BM25 V3, bge-reranker-v2-m3 sur
20 candidats, 10 passages dans le budget) et R2 (la même avec l'encodeur ajusté v1, requête q8 servie). Critère : rappel
du contexte. Règle : R2 reste en production si son critère est au moins celui de R1 sur le jeu v2 et sur le CDTN.
Contrôle préalable : R0 et R1 doivent redonner, formulation par formulation, la grille du protocole 07.
Sorties écrites une seule fois dans `data/evaluation/protocole_10/`.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _sous in ("scripts/evaluation", "scripts/rag", "scripts/recuperation"):
    if str(RACINE / _sous) not in sys.path:
        sys.path.insert(0, str(RACINE / _sous))

import ajustement_05 as a5  # noqa: E402  (fonctions du protocole 05, inchangées)
import recuperation as rc  # noqa: E402
from pertinence import IndexPertinence  # noqa: E402

D = RACINE / "data"
JEU_V2 = RACINE / "evaluation" / "questions_v2" / "questions_v2.csv"
SHA256_JEU_V2 = "316d82816e924a8a474653240ce2372e0ec2a85e16870dfd6354f24db521f17f"   # étiquette jeu-questions-v2
VECTEURS = {"jeu_v2": a5.VECTEURS / "vecteurs_jeu_v2_ajuste.json", "cdtn": a5.VECTEURS / "vecteurs_cdtn_mesure_ajuste.json",
            "jeu_v1": a5.VECTEURS / "vecteurs_navigateur_ajuste.json"}
FORMULATIONS_CDTN = D / "evaluation" / "cdtn" / "formulations_mesure.json"
RESULTATS_05 = D / "evaluation" / "ajustement_05" / "mesure_20261115T142537Z.json"
INDEX_SERVI = RACINE / "front" / "public" / "index_ajuste" / "index_m2.f32"
SHA256_INDEX_SERVI = "dc8daa7243bec30c28ea4830daeb10970bcd3de8d819f71a602b5d0b306ea8f1"
PROFONDEUR = 100
AFFICHES = 10
SORTIES = D / "evaluation" / "protocole_10"


class ErreurMesure10(RuntimeError):
    pass


def sha256(chemin: Path) -> str:
    return hashlib.sha256(Path(chemin).read_bytes()).hexdigest()


def lire_jeu_v2() -> list[dict]:
    if sha256(JEU_V2) != SHA256_JEU_V2:
        raise ErreurMesure10("Jeu v2 différent de celui étiqueté jeu-questions-v2")
    return list(csv.DictReader(JEU_V2.open(encoding="utf-8")))


def matrice_ajuste() -> np.ndarray:
    if sha256(INDEX_SERVI) != SHA256_INDEX_SERVI:
        raise ErreurMesure10("Index servi par le site différent de celui du 15 novembre")
    m = a5.charger_index_ajuste()
    if not np.array_equal(m, np.fromfile(INDEX_SERVI, dtype="<f4").reshape(4240, 384)):
        raise ErreurMesure10("Index de mesure du protocole 05 différent de l'index servi")
    return m


def bm25(table):
    from lexical_baselines import BM25Retriever
    return BM25Retriever(stopwords_variant="snowball_no_negation", stemming="french").fit(
        rc.textes_lexicaux(table), doc_ids=table.passage_id.tolist())


def listes_d_et_f(vecteurs: np.ndarray, matrice: np.ndarray, lexical, textes: list[str]) -> tuple[list, list]:
    dense, fusion = [], []
    for v, q in zip(vecteurs, textes):
        d = rc.classement(matrice @ v)[:PROFONDEUR].tolist()
        l = rc.classement(lexical.score_matrix([q])[0], positifs=True)[:PROFONDEUR].tolist()
        dense.append(d)
        fusion.append(rc.fusion_rrf([d, l])[:PROFONDEUR])
    return dense, fusion


def evaluer(listes: list[list[int]], pertinents: list[set], fiches: list[set], url_passage: list[str]) -> dict:
    rangs = [[r for r, i in enumerate(l[:AFFICHES], 1) if i in p] for l, p in zip(listes, pertinents)]
    return {"r1": a5.succes_a(rangs, 1), "r5": a5.succes_a(rangs, 5), "r10": a5.succes_a(rangs, 10),
            "fiche10": [any(url_passage[i] in f for i in l[:AFFICHES]) for l, f in zip(listes, fiches)],
            "mrr10": a5.mrr10(rangs)}


def resume(s: dict) -> dict:
    n = len(s["r5"])
    return {"questions": n, "recall@1": sum(s["r1"]) / n, "recall@5": sum(s["r5"]) / n, "recall@10": sum(s["r10"]) / n,
            "mrr@10": s["mrr10"], "fiche_parmi_les_10_affiches": sum(s["fiche10"]) / n}


def comparer(nom: str, ids: list, vecteurs: np.ndarray, textes: list[str], pertinents: list[set], groupes: list,
             matrice, lexical, url_passage) -> dict:
    fiches = [{url_passage[i] for i in p} for p in pertinents]
    dense, fusion = listes_d_et_f(vecteurs, matrice, lexical, textes)
    sd, sf = evaluer(dense, pertinents, fiches, url_passage), evaluer(fusion, pertinents, fiches, url_passage)
    return {"jeu": nom, "questions": len(ids), "groupes": len(set(groupes)),
            "D": resume(sd), "F": resume(sf),
            "ecart_recall5_F_moins_D": a5.ecart(sf["r5"], sd["r5"], groupes),
            "ecart_fiche10_F_moins_D": a5.ecart(sf["fiche10"], sd["fiche10"], groupes),
            "_r5_D": sd["r5"]}


MODELE_SERVI = RACINE / "front" / "public" / "modele" / "multilingual-e5-small-ajuste-q8-elague-13ed78c9"
SHA256_Q8_SERVI = "13ed78c9bf0c4e4ba2d36d0f715568edfb341a44051225f0b0a0e0214bf991d4"


class EncodeurQ8:
    """Requête encodée par le q8 élagué servi par le site, avec onnxruntime en Python (production du volet B, #172) :
    préfixe `query: `, moyenne des vecteurs des tokens pondérée par le masque, normalisation. Les poids fp32 de l'ajusté
    (470 Mo) ne peuvent pas être versionnés ; ce modèle-ci l'est (65,7 Mio) et son index est celui du site."""

    def __init__(self, dossier: Path = MODELE_SERVI):
        import onnxruntime as ort
        from tokenizers import Tokenizer
        onnx = dossier / "onnx" / "model_quantized.onnx"
        if sha256(onnx) != SHA256_Q8_SERVI:
            raise ErreurMesure10("q8 servi différent de celui du 15 novembre")
        self.tok = Tokenizer.from_file(str(dossier / "tokenizer.json"))
        self.session = ort.InferenceSession(str(onnx), providers=["CPUExecutionProvider"])
        self.entrees = {i.name for i in self.session.get_inputs()}

    def encoder(self, question: str) -> np.ndarray:
        e = self.tok.encode("query: " + question)
        if len(e.ids) > 512:
            raise ErreurMesure10("Question de plus de 512 tokens")
        d = {"input_ids": np.array([e.ids], dtype=np.int64), "attention_mask": np.array([e.attention_mask], dtype=np.int64),
             "token_type_ids": np.zeros((1, len(e.ids)), dtype=np.int64)}
        h = self.session.run(None, {k: v for k, v in d.items() if k in self.entrees})[0][0]
        m = np.array(e.attention_mask, dtype=np.float32)[:, None]
        v = (h * m).sum(axis=0) / m.sum()
        return (v / np.linalg.norm(v)).astype(np.float32)


class PertinenceV2:
    """Écart déclaré au protocole 10, décidé le 17/11 avant tout résultat : D4 (IndexPertinence) exige un extrait d'au
    moins 80 caractères normalisés, que les extraits du jeu v1 respectaient tous. Pour les extraits plus courts du jeu
    v2 (14 sur 121), un passage est pertinent s'il contient l'extrait entier, normalisé avec ou sans les marques de
    liste : plus strict que D4, ce qui évite qu'un fragment commun de quelques mots suffise. Le passage source est
    toujours pertinent, puisque l'extrait y figure mot pour mot."""

    def __init__(self, textes: list[str]):
        from pertinence import LONGUEUR_MINIMALE, normaliser
        self.min, self.normaliser = LONGUEUR_MINIMALE, normaliser
        self.index = IndexPertinence(textes)
        self.textes = {r: [normaliser(t, r) for t in textes] for r in (False, True)}

    def court(self, extrait: str) -> bool:
        return len(self.normaliser(extrait, False)) < self.min

    def pertinents(self, extrait: str) -> set[int]:
        if not self.court(extrait):
            return set(self.index.pertinents(extrait))
        return {i for r in (False, True) for i, t in enumerate(self.textes[r]) if self.normaliser(extrait, r) in t}


def famille_a() -> dict:
    table, _ = a5.table_et_index_site()
    matrice = matrice_ajuste()
    lexical = bm25(table)
    url_passage = [u.rstrip("/") for u in table.url]
    index_p = IndexPertinence(table.texte.tolist())
    res = {"protocole": "10, section 7, famille A", "sha256_protocole": sha256(RACINE / "docs/etudes/evaluation/10_protocole_jeu_v2.md"),
           "jeux": {}}

    # jeu v2, questions du corpus
    corpus = [q for q in lire_jeu_v2() if q["type"] == "dans_corpus"]
    v = a5.charger_vecteurs(VECTEURS["jeu_v2"], "ajuste")
    pv2 = PertinenceV2(table.texte.tolist())
    pertinents = [pv2.pertinents(q["extrait"]) for q in corpus]
    pid = {p: i for i, p in enumerate(table.passage_id)}
    absents = [q["id"] for q, p in zip(corpus, pertinents) if pid[q["passage_id"]] not in p]
    if absents:
        raise ErreurMesure10(f"Passage source non reconnu : {absents}")
    res["pertinence_jeu_v2"] = {"extraits_courts": [q["id"] for q in corpus if pv2.court(q["extrait"])],
                                "passages_pertinents_par_question": {"min": min(map(len, pertinents)),
                                                                     "max": max(map(len, pertinents)),
                                                                     "moyenne": float(np.mean([len(p) for p in pertinents]))}}
    vecteurs_v2 = np.stack([v[q["id"]] for q in corpus])
    res["jeux"]["jeu_v2"] = comparer("jeu_v2", [q["id"] for q in corpus], vecteurs_v2, [q["question"] for q in corpus],
                                     pertinents, [q["url"] for q in corpus], matrice, lexical, url_passage)
    # sensibilité : le seul passage source comme passage pertinent (minorant pur)
    res["jeux"]["jeu_v2_source_seule"] = comparer("jeu_v2_source_seule", [q["id"] for q in corpus], vecteurs_v2,
                                                  [q["question"] for q in corpus], [{pid[q["passage_id"]]} for q in corpus],
                                                  [q["url"] for q in corpus], matrice, lexical, url_passage)

    # CDTN, population du protocole 05 (131 requêtes, 494 formulations)
    pop = json.loads(a5.POPULATION_CDTN.read_text(encoding="utf-8"))
    if sha256(a5.POPULATION_CDTN) != a5.EMPREINTES["population_cdtn"][1]:
        raise ErreurMesure10("Population du CDTN différente de celle du protocole 05")
    textes_cdtn = {q["id"]: q["texte"] for q in json.loads(FORMULATIONS_CDTN.read_text(encoding="utf-8"))["questions"]}
    ids, pert, grp = [], [], []
    for r in pop["requetes"]:
        for f in r["formulations"]:
            ids.append(f["id"]); pert.append(set(r["pertinents"])); grp.append(r["id"])
    vc = a5.charger_vecteurs(VECTEURS["cdtn"], "ajuste")
    cdtn = comparer("cdtn", ids, np.stack([vc[i] for i in ids]), [textes_cdtn[i] for i in ids], pert, grp,
                    matrice, lexical, url_passage)

    # contrôle de reproduction : D sur le CDTN doit redonner le protocole 05, question par question
    publie = json.loads(RESULTATS_05.read_text(encoding="utf-8"))
    r5_publie = publie["cdtn"]["systemes"]["ajuste"]["recall@5"]
    ref = a5.systeme(np.stack([vc[i] for i in ids]), matrice, pert, [{url_passage[i] for i in p} for p in pert], url_passage)
    if cdtn["_r5_D"] != ref["r5"] or abs(cdtn["D"]["recall@5"] - r5_publie) > 1e-12:
        raise ErreurMesure10(f"D ne reproduit pas le protocole 05 sur le CDTN : {cdtn['D']['recall@5']} contre {r5_publie}")
    res["controle_reproduction_05"] = {"cdtn_recall5_ajuste_publie": r5_publie, "recalcule": cdtn["D"]["recall@5"],
                                       "identique_question_par_question": True}
    res["jeux"]["cdtn"] = cdtn

    # jeu v1 (lot de test humain), à titre secondaire et descriptif
    import mesure
    v1 = [q for q in mesure.lire_jeu("test") if q["type"] == "dans_corpus"]
    vv1 = a5.charger_vecteurs(VECTEURS["jeu_v1"], "ajuste")
    res["jeux"]["jeu_v1_test"] = comparer("jeu_v1_test", [q["id"] for q in v1], np.stack([vv1[q["id"]] for q in v1]),
                                          [q["question"] for q in v1], [set(index_p.pertinents(q["extrait"])) for q in v1],
                                          [q["fiche"] for q in v1], matrice, lexical, url_passage)
    for j in res["jeux"].values():
        j.pop("_r5_D", None)

    e2, ec = (res["jeux"][k]["ecart_recall5_F_moins_D"]["ecart"] for k in ("jeu_v2", "cdtn"))
    adoptee = e2 >= 0 and ec >= 0 and (e2 > 0 or ec > 0)
    res["decision"] = {"regle": "F adoptée si l'écart de Recall@5 est positif ou nul sur le jeu v2 et le CDTN, et strictement positif sur l'un",
                       "ecart_jeu_v2": e2, "ecart_cdtn": ec, "F_adoptee": adoptee,
                       "F_dite_meilleure_jeu_v2": res["jeux"]["jeu_v2"]["ecart_recall5_F_moins_D"]["ic95_tango"][0] > 0,
                       "F_dite_meilleure_cdtn": res["jeux"]["cdtn"]["ecart_recall5_F_moins_D"]["ic95_tango"][0] > 0}
    SORTIES.mkdir(parents=True, exist_ok=True)
    chemin = SORTIES / f"famille_a_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    print(f"écrit {chemin.name}, SHA-256 {a5.ecrire_une_fois(chemin, res)}")
    return res


# ---------------------------------------------------------------------------------------------------------------
# Famille B : récupération du volet B (section 7)
# ---------------------------------------------------------------------------------------------------------------
CONFIG_R0 = rc.Configuration(k=5)                                                    # B2 : E5 de base, 5 passages
CONFIG_V2 = rc.Configuration(k=10, source="rrf", reclasseur="bge-m3", candidats=20)  # R1 (V1) et R2 (démonstration)
# Rappel du contexte publié par le protocole 07 (#138) sur la population « questions » du CDTN (resultats_grille.json)
PUBLIE_07 = {"e5+k5": 0.708925221120343, "rrf+k10+bge-m3@20": 0.850524137109503}
CACHE_RECLASSEUR = SORTIES / "reclasseur_bge-m3_famille_b.json"


def holm(p: dict) -> dict:
    """Valeurs p ajustées par la méthode de Holm (1979) : max cumulé de min(1, (m - j + 1) p_(j)), p croissants."""
    ordre = sorted(p, key=lambda k: (p[k], k))
    m, cumul, sortie = len(ordre), 0.0, {}
    for j, k in enumerate(ordre):
        cumul = max(cumul, min(1.0, (m - j) * p[k]))
        sortie[k] = cumul
    return sortie


class ScoresReclasseur:
    """Scores de bge-reranker-v2-m3 par (question, passage), sur l'entrée du protocole 07 (en-tête et texte), mis en
    cache dans data/ (non versionné) pour qu'une reprise ne recalcule rien. Un passage déjà noté n'est jamais renoté."""

    def __init__(self, textes_passages: list[str], chemin: Path = CACHE_RECLASSEUR):
        self.textes, self.chemin, self.modele, self.calcules = textes_passages, chemin, None, 0
        self.revision = rc.RECLASSEURS["bge-m3"][1]
        self.cache: dict[str, dict[int, float]] = {}
        if chemin.exists():
            d = json.loads(chemin.read_text(encoding="utf-8"))
            if d["revision"] != self.revision or d["entree"] != "entete+texte":
                raise ErreurMesure10("Cache du reclasseur incompatible")
            self.cache = {q: {int(i): v for i, v in s.items()} for q, s in d["scores"].items()}

    def noter(self, question: str, indices) -> dict[int, float]:
        connus = self.cache.setdefault(question, {})
        manquants = [int(i) for i in dict.fromkeys(indices) if int(i) not in connus]
        if manquants:
            if self.modele is None:
                self.modele = rc.Reclasseur("bge-m3")
            s = self.modele.scores(question, [self.textes[i] for i in manquants])
            connus.update({i: float(v) for i, v in zip(manquants, s)})
            self.calcules += len(manquants)
        return connus

    def ecrire(self) -> None:
        tmp = self.chemin.with_suffix(".tmp")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps({"modele": rc.RECLASSEURS["bge-m3"][0], "revision": self.revision, "entree": "entete+texte",
                                   "scores": {q: {str(i): v for i, v in s.items()} for q, s in self.cache.items()}},
                                  ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.chemin)


class Contextes:
    """Contexte d'une configuration : classement final, k ancres sans voisins, puis budget du prompt (tokens Qwen)."""

    def __init__(self, index, table):
        self.passages, self.cles = index.passages, rc.sections(table)
        self.tok = rc.generation.charger_tokeniseur_qwen()
        self._tokens: dict = {}

    def tokens(self, question: str, indices) -> int:
        cle = (question, tuple(indices))
        if cle not in self._tokens:
            self._tokens[cle] = rc.compter_tokens(self.tok, rc.construire_contexte_v2(question, indices, self.passages))
        return self._tokens[cle]

    def contexte(self, config, question: str, liste_e5, liste_bm25, scores=None) -> dict:
        ordre = rc.classement_final(config, liste_e5, liste_bm25, scores, profondeur=PROFONDEUR)
        groupes = rc.groupes_du_contexte(ordre[:config.k], self.cles, False)
        indices, retires = rc.dans_le_budget(groupes, lambda ind: self.tokens(question, ind))
        return {"indices": indices, "retires": retires, "tokens": self.tokens(question, indices)}


def listes_premier_niveau(vecteur: np.ndarray, matrice: np.ndarray) -> list[int]:
    return rc.classement(matrice @ vecteur)[:PROFONDEUR].tolist()


def systemes_b_jeu(questions: list[str], pertinents: list[set], groupes: list, outils: dict, avec_fp32: bool) -> dict:
    """R0, R1, R2 (et R2 à requête fp32 si demandé) pour un jeu de questions : contexte et rappel du contexte."""
    import rag
    index, lexical, ctx, rs = outils["index"], outils["lexical"], outils["ctx"], outils["rs"]
    vb = [rag.encoder_question(outils["base"], q) for q in questions]
    va = [outils["q8"].encoder(q) for q in questions]            # une question à la fois, comme le service
    vf = [outils["fp32"].encode(["query: " + q], normalize_embeddings=True, convert_to_numpy=True,
                                show_progress_bar=False)[0] for q in questions] if avec_fp32 else []
    noms = ("R0", "R0_avec_S", "R1", "R2") + (("R2_requete_fp32",) if avec_fp32 else ())
    lignes = {n: [] for n in noms}
    for n, q in enumerate(questions):
        bm = rc.classement(lexical.score_matrix([q])[0], positifs=True)[:PROFONDEUR].tolist()
        scores_base = index.matrice @ vb[n]
        e5 = rc.classement(scores_base)[:PROFONDEUR].tolist()
        aj = listes_premier_niveau(va[n], outils["matrice_aj"])
        listes = {"R1": e5, "R2": aj}
        if avec_fp32:
            listes["R2_requete_fp32"] = listes_premier_niveau(np.asarray(vf[n], dtype=np.float32), outils["matrice_aj"])
        candidats = [i for l in listes.values() for i in rc.fusion_rrf([l, bm])[:CONFIG_V2.candidats]]
        scores = rs.noter(q, candidats)
        c = {"R0": ctx.contexte(CONFIG_R0, q, e5, bm)}
        refuse = float(scores_base.max()) < outils["seuil"]
        c["R0_avec_S"] = {"indices": [] if refuse else c["R0"]["indices"], "retires": 0,
                          "tokens": 0 if refuse else c["R0"]["tokens"], "refus_S": refuse}
        for nom, l in listes.items():
            c[nom] = ctx.contexte(CONFIG_V2, q, l, bm, scores)
        for nom in noms:
            lignes[nom].append({**c[nom], "rappel": bool(pertinents[n] & set(c[nom]["indices"]))})
    sortie = {"questions": len(questions), "groupes": len(set(groupes)), "systemes": {}, "comparaisons": {}}
    for nom in noms:
        l = lignes[nom]
        sortie["systemes"][nom] = {"rappel_contexte": sum(x["rappel"] for x in l) / len(l),
                                   "passages_moyen": float(np.mean([len(x["indices"]) for x in l])),
                                   "tokens_moyen": float(np.mean([x["tokens"] for x in l])),
                                   "tokens_max": max(x["tokens"] for x in l),
                                   "contextes_tronques": sum(x["retires"] > 0 for x in l)}
    sortie["systemes"]["R0_avec_S"]["refus_S"] = sum(x["refus_S"] for x in lignes["R0_avec_S"])
    for a, b in (("R2", "R1"), ("R1", "R0"), ("R2", "R0")):
        sortie["comparaisons"][f"{a}_moins_{b}"] = a5.ecart([x["rappel"] for x in lignes[a]], [x["rappel"] for x in lignes[b]], groupes)
    p_holm = holm({k: v["p_mcnemar"] for k, v in sortie["comparaisons"].items()})
    for k, v in sortie["comparaisons"].items():
        v["p_holm"] = p_holm[k]
    sortie["_lignes"] = lignes
    return sortie


def famille_b_cdtn(outils: dict) -> dict:
    """Population « questions » du protocole 07 : rappel du contexte moyen par requête, puis sur les requêtes."""
    import reglage_cdtn as rg
    manifeste, classements, population = rg.charger_caches()
    if sha256(a5.POPULATION_CDTN) != a5.EMPREINTES["population_cdtn"][1]:
        raise ErreurMesure10("Population du CDTN différente de celle du protocole 07")
    d = rg.lire_json(rg.SORTIE / "reclasseur_bge-m3.json")
    if d["classements_sha256"] != manifeste["classements_sha256"] or d["revision"] != rc.RECLASSEURS["bge-m3"][1]:
        raise ErreurMesure10("Cache du reclasseur du protocole 07 incohérent avec ses classements")
    cache_07 = {fid: {int(i): v for i, v in s.items()} for fid, s in d["scores"].items()}
    formulations = {fo["id"]: (r, fo) for r in population["requetes"] for fo in r["formulations"]}
    ctx, rs, lexical = outils["ctx"], outils["rs"], outils["lexical"]

    # contrôle du lot du reclasseur : les 20 candidats de R1 des 5 premières questions, renotés d'un seul appel
    temoins = [(n, fid) for n, fid in enumerate(classements["formulations"]) if formulations[fid][1]["type"] == "question"][:5]
    if rs.modele is None:
        rs.modele = rc.Reclasseur("bge-m3")
    ecart_lot = 0.0
    for n, fid in temoins:
        cand = rc.fusion_rrf([classements["e5"][n], classements["bm25"][n]])[:CONFIG_V2.candidats]
        s = rs.modele.scores(formulations[fid][1]["texte"], [rs.textes[i] for i in cand])
        ecart_lot = max(ecart_lot, float(np.max(np.abs(s - np.array([cache_07[fid][i] for i in cand])))))

    lignes, completes = [], 0
    for n, fid in enumerate(classements["formulations"]):
        r, fo = formulations[fid]
        if fo["type"] != "question":
            continue
        q, e5, bm = fo["texte"], classements["e5"][n], classements["bm25"][n]
        if bm != rc.classement(lexical.score_matrix([q])[0], positifs=True)[:PROFONDEUR].tolist():
            raise ErreurMesure10(f"BM25 recalculé différent du cache du protocole 07 : {fid}")
        aj = listes_premier_niveau(outils["q8"].encoder(q), outils["matrice_aj"])
        cand_r2 = rc.fusion_rrf([aj, bm])[:CONFIG_V2.candidats]
        scores = dict(cache_07[fid])
        manquants = [i for i in cand_r2 if i not in scores]
        if manquants:
            completes += len(manquants)
            scores.update({i: rs.noter(q, manquants)[i] for i in manquants})
        rel = set(r["pertinents"])
        ligne = {"formulation": fid, "requete": r["id"], "hors_fiches_test": r["hors_fiches_test"]}
        for nom, config, liste in (("R0", CONFIG_R0, e5), ("R1", CONFIG_V2, e5), ("R2", CONFIG_V2, aj)):
            c = ctx.contexte(config, q, liste, bm, scores if config.reclasseur else None)
            ligne[nom] = int(bool(rel & set(c["indices"])))
            ligne[f"{nom}_tokens"] = c["tokens"]
        lignes.append(ligne)

    # contrôle de reproduction : R0 et R1 doivent redonner le protocole 07, formulation par formulation
    with open(rg.SORTIE / "formulations_grille.csv", encoding="utf-8", newline="") as f:
        grille = {(x["configuration"], x["formulation"]): int(x["rappel_contexte"]) for x in csv.DictReader(f)}
    for nom, conf in (("R0", "e5+k5"), ("R1", "rrf+k10+bge-m3@20")):
        diff = [l["formulation"] for l in lignes if l[nom] != grille[(conf, l["formulation"])]]
        if diff:
            raise ErreurMesure10(f"{nom} ne reproduit pas le protocole 07 ({conf}) : {diff[:5]}")

    def par_requete(nom, filtre=None):
        groupes: dict = {}
        for l in lignes:
            if filtre is None or l["hors_fiches_test"] == filtre:
                groupes.setdefault(l["requete"], []).append(l[nom])
        return {k: float(np.mean(v)) for k, v in groupes.items()}

    sortie = {"population": "questions du protocole 07", "formulations": len(lignes),
              "requetes": len({l["requete"] for l in lignes}), "systemes": {}, "ecarts": {}, "sous_populations": {},
              "controle_lot_reclasseur": {"formulations": len(temoins), "ecart_max_absolu": ecart_lot},
              "paires_reclasseur_completees_pour_R2": completes}
    for nom in ("R0", "R1", "R2"):
        m = par_requete(nom)
        sortie["systemes"][nom] = rg.agreger(m, sorted(m), np.random.default_rng(rg.GRAINE))
        sortie["systemes"][nom]["tokens_moyen"] = float(np.mean([l[f"{nom}_tokens"] for l in lignes]))
    for nom, conf in (("R0", "e5+k5"), ("R1", "rrf+k10+bge-m3@20")):
        if abs(sortie["systemes"][nom]["moyenne"] - PUBLIE_07[conf]) > 1e-12:
            raise ErreurMesure10(f"{nom} : {sortie['systemes'][nom]['moyenne']} contre {PUBLIE_07[conf]} publié")
    sortie["controle_reproduction_07"] = {"R0_e5+k5": PUBLIE_07["e5+k5"], "R1_rrf+k10+bge-m3@20": PUBLIE_07["rrf+k10+bge-m3@20"],
                                          "identique_formulation_par_formulation": True}
    for a, b in (("R2", "R1"), ("R1", "R0"), ("R2", "R0")):
        ma, mb = par_requete(a), par_requete(b)
        sortie["ecarts"][f"{a}_moins_{b}"] = rg.agreger({k: ma[k] - mb[k] for k in ma}, sorted(ma),
                                                       np.random.default_rng(rg.GRAINE))
    for nom_sp, filtre in (("requetes_hors_fiches_test", True), ("requetes_sur_fiches_test", False)):
        ma, mb = par_requete("R2", filtre), par_requete("R1", filtre)
        sortie["sous_populations"][nom_sp] = {
            "requetes": len(ma), "R1": float(np.mean(list(mb.values()))), "R2": float(np.mean(list(ma.values()))),
            "R2_moins_R1": rg.agreger({k: ma[k] - mb[k] for k in ma}, sorted(ma), np.random.default_rng(rg.GRAINE))}
    return sortie


def famille_b() -> dict:
    import mesure
    import rag
    table, index = a5.table_et_index_site()
    if table.passage_id.tolist() != [p["passage_id"] for p in index.passages]:
        raise ErreurMesure10("Table M2 et index commun désalignés")
    a5.verifier_empreintes({"poids_ajuste"})
    rs = ScoresReclasseur(rc.textes_lexicaux(table))
    outils = {"index": index, "table": table, "lexical": bm25(table), "ctx": Contextes(index, table), "rs": rs,
              "matrice_aj": matrice_ajuste(), "q8": EncodeurQ8(), "base": rag.charger_encodeur(),
              "fp32": a5.encodeur_ajuste(), "seuil": mesure.charger_seuil()}
    res = {"protocole": "10, section 7, famille B", "sha256_protocole": sha256(RACINE / "docs/etudes/evaluation/10_protocole_jeu_v2.md"),
           "configurations": {"R0": CONFIG_R0.nom, "R1": CONFIG_V2.nom + " (E5 de base)",
                              "R2": CONFIG_V2.nom + " (E5 ajusté v1, requête q8 servie, onnxruntime)",
                              "R2_requete_fp32": CONFIG_V2.nom + " (E5 ajusté v1, requête fp32 : la démonstration du 16/11)"},
           "seuil_S": outils["seuil"], "jeux": {}}
    try:
        # jeu v2, questions du corpus (critère principal)
        corpus = [q for q in lire_jeu_v2() if q["type"] == "dans_corpus"]
        pv2 = PertinenceV2(table.texte.tolist())
        jv2 = systemes_b_jeu([q["question"] for q in corpus], [pv2.pertinents(q["extrait"]) for q in corpus],
                             [q["url"] for q in corpus], outils, avec_fp32=True)
        jv2["detail"] = [{"id": q["id"], **{n: {"rappel": l[k]["rappel"],
                                                "passages": [index.passages[i]["passage_id"] for i in l[k]["indices"]]}
                                            for n, l in jv2["_lignes"].items()}} for k, q in enumerate(corpus)]
        res["jeux"]["jeu_v2"] = jv2
        rs.ecrire()
        # CDTN
        res["jeux"]["cdtn"] = famille_b_cdtn(outils)
        rs.ecrire()
        # jeu v1 (lot de test humain), descriptif
        v1 = [q for q in mesure.lire_jeu("test") if q["type"] == "dans_corpus"]
        ip = IndexPertinence(table.texte.tolist())
        res["jeux"]["jeu_v1_test"] = systemes_b_jeu([q["question"] for q in v1], [set(ip.pertinents(q["extrait"])) for q in v1],
                                                    [q["fiche"] for q in v1], outils, avec_fp32=False)
    finally:
        rs.ecrire()
    for j in res["jeux"].values():
        j.pop("_lignes", None)
    res["paires_reclasseur_calculees"] = rs.calcules
    v2, cd = res["jeux"]["jeu_v2"], res["jeux"]["cdtn"]
    r2_v2, r1_v2 = v2["systemes"]["R2"]["rappel_contexte"], v2["systemes"]["R1"]["rappel_contexte"]
    r2_cd, r1_cd = cd["systemes"]["R2"]["moyenne"], cd["systemes"]["R1"]["moyenne"]
    res["decision"] = {"regle": "R2 reste en production si son rappel du contexte est au moins celui de R1 sur le jeu v2 et sur le CDTN",
                       "jeu_v2": {"R1": r1_v2, "R2": r2_v2}, "cdtn": {"R1": r1_cd, "R2": r2_cd},
                       "R2_maintenue": r2_v2 >= r1_v2 and r2_cd >= r1_cd}
    SORTIES.mkdir(parents=True, exist_ok=True)
    chemin = SORTIES / f"famille_b_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    print(f"écrit {chemin.name}, SHA-256 {a5.ecrire_une_fois(chemin, res)}")
    return res


def effet_k() -> dict:
    """Descriptif, demandé par l'enseignant le 17/11 : effet de k seul (5 contre 10 passages) sur le rappel du contexte,
    pour l'E5 de base, la fusion RRF sans reclasseur et R1, sur le jeu v2 et le lot de test du jeu v1. Les scores du
    reclasseur sont ceux du cache de la famille B (aucun recalcul) ; le budget de tokens n'est jamais atteint à k = 10."""
    import mesure
    import rag
    table, index = a5.table_et_index_site()
    lexical, e5 = bm25(table), rag.charger_encodeur()
    rs = ScoresReclasseur(rc.textes_lexicaux(table))   # cache seulement : aucun score n'est recalculé ici

    def jeu(questions, pertinents, groupes):
        succes = {}
        for q, p in zip(questions, pertinents):
            d = listes_premier_niveau(rag.encoder_question(e5, q), index.matrice)
            f = rc.fusion_rrf([d, rc.classement(lexical.score_matrix([q])[0], positifs=True)[:PROFONDEUR].tolist()])[:PROFONDEUR]
            connus = rs.cache.get(q, {})
            if any(i not in connus for i in f[:CONFIG_V2.candidats]):
                raise ErreurMesure10("Scores du reclasseur absents du cache : lancer famille_b d'abord")
            r = rc.reclasser(f[:CONFIG_V2.candidats], [connus[i] for i in f[:CONFIG_V2.candidats]])
            for nom, liste in (("E5 de base", d), ("RRF sans reclasseur", f), ("R1, RRF et bge-m3", r)):
                for k in (5, 10):
                    succes.setdefault(nom, {}).setdefault(k, []).append(bool(set(liste[:k]) & p))
        return {nom: {"k5": float(np.mean(s[5])), "k10": float(np.mean(s[10])), "k10_moins_k5": a5.ecart(s[10], s[5], groupes)}
                for nom, s in succes.items()}

    corpus = [q for q in lire_jeu_v2() if q["type"] == "dans_corpus"]
    pv2 = PertinenceV2(table.texte.tolist())
    v1 = [q for q in mesure.lire_jeu("test") if q["type"] == "dans_corpus"]
    ip = IndexPertinence(table.texte.tolist())
    res = {"objet": "effet de k seul, descriptif", "sha256_cache_reclasseur": sha256(CACHE_RECLASSEUR),
           "jeu_v2": jeu([q["question"] for q in corpus], [pv2.pertinents(q["extrait"]) for q in corpus],
                         [q["url"] for q in corpus]),
           "jeu_v1_test": jeu([q["question"] for q in v1], [set(ip.pertinents(q["extrait"])) for q in v1],
                              [q["fiche"] for q in v1])}
    chemin = SORTIES / f"effet_k_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    print(f"écrit {chemin.name}, SHA-256 {a5.ecrire_une_fois(chemin, res)}")
    for j in ("jeu_v2", "jeu_v1_test"):
        for nom, v in res[j].items():
            e = v["k10_moins_k5"]
            print(f"{j:12s} {nom:20s} k5 {v['k5']:.3f} k10 {v['k10']:.3f} écart {e['ecart']:+.3f} "
                  f"[{e['ic95_tango'][0]:+.3f} ; {e['ic95_tango'][1]:+.3f}] gagnées {e['ajuste_seul']} perdues {e['base_seule']}")
    return res


# ---------------------------------------------------------------------------------------------------------------
# Famille B de bout en bout (section 7), sur les 161 questions du jeu v2
# ---------------------------------------------------------------------------------------------------------------
# R2 n'étant pas maintenue (famille B, récupération), la chaîne de démonstration est R1 (10_resultats.md, section 6).
PHASES = {"adapte": ("qwen2.5-7b-instruct:lora-v2b-q4_k_m-local",
                     "18cb25f099f2ba1b21a3bc945da6be7ce4d128cb4e579325fc0f70dfccb37174"),
          "temoin": ("qwen2.5-7b-instruct:temoin-q4_k_m-local",
                     "8a077f3d3f56b636face1357eba557b21e2ba68bc72ee81e48b377272da72f27")}
EXECUTIONS = (("B2", "adapte"), ("R1", "adapte"), ("R1", "temoin"))
FAMILLE_B = SORTIES / "famille_b_20261117T131518Z.json"
SHA256_FAMILLE_B = "67c1b3ac2e7ead1b9c278e75e3646d314a43a37e0e05730f387626d13bccfba2"


def questions_bout_en_bout() -> list[dict]:
    """Champs attendus par mesure.executer_etat ; la fiche (regroupement de M4) est l'adresse de la fiche source."""
    return [{"id": q["id"], "type": q["type"], "fiche": q["url"], "question": q["question"], "extrait": q["extrait"]}
            for q in lire_jeu_v2()]


def preparer_r1(questions: list[dict], outils: dict) -> list[dict]:
    """Contexte de R1 pour chaque question, au format de mesure.preparer_questions, sans seuil (sous_le_seuil faux).
    Contrôle : pour les questions du corpus, le contexte est celui publié par la famille B."""
    import rag
    if sha256(FAMILLE_B) != SHA256_FAMILLE_B:
        raise ErreurMesure10("Résultats de la famille B différents de ceux publiés")
    publies = {d["id"]: d["R1"]["passages"] for d in json.loads(FAMILLE_B.read_text(encoding="utf-8"))["jeux"]["jeu_v2"]["detail"]}
    index, ctx, rs, lexical, e5 = outils["index"], outils["ctx"], outils["rs"], outils["lexical"], outils["base"]
    preparees = []
    for q in questions:
        scores = index.matrice @ rag.encoder_question(e5, q["question"])
        dense = rc.classement(scores)[:PROFONDEUR].tolist()
        lex = rc.classement(lexical.score_matrix([q["question"]])[0], positifs=True)[:PROFONDEUR].tolist()
        notes = rs.noter(q["question"], rc.fusion_rrf([dense, lex])[:CONFIG_V2.candidats])
        indices = ctx.contexte(CONFIG_V2, q["question"], dense, lex, notes)["indices"]
        resultats = [{"rang": r, "indice": i, "score": float(scores[i]), "passage": index.passages[i]}
                     for r, i in enumerate(indices, 1)]
        if q["id"] in publies and [x["passage"]["passage_id"] for x in resultats] != publies[q["id"]]:
            raise ErreurMesure10(f"Contexte de R1 différent de celui publié par la famille B : {q['id']}")
        preparees.append({**q, "resultats": resultats, "score_max": float(scores.max()), "sous_le_seuil": False,
                          "proche_du_seuil": False,
                          "contexte": rc.construire_contexte_v2(q["question"], indices, index.passages)})
    return preparees


def bout_en_bout(etat: str, phase: str) -> Path:
    """Une exécution par état et par modèle (section 7) : refusée si son fichier existe déjà."""
    import generation
    import mesure
    import rag
    if (etat, phase) not in EXECUTIONS:
        raise ErreurMesure10(f"Exécution hors protocole : {etat}, {phase}")
    if list(SORTIES.glob(f"bout_en_bout_{etat}_{phase}_*.json")):
        raise ErreurMesure10(f"{etat}, {phase} : déjà exécuté, une seule exécution par état")
    modele, digest = PHASES[phase]
    infos = generation.verifier_ollama(modele, digest)
    if infos["version"] != mesure.VERSION_OLLAMA:
        raise ErreurMesure10(f"Ollama {infos['version']}, attendu {mesure.VERSION_OLLAMA}")
    questions = questions_bout_en_bout()
    index = rag.charger_index()
    e5 = rag.charger_encodeur()
    if etat == "B2":
        seuil = mesure.charger_seuil()
        preparees = mesure.preparer_questions(questions, index, lambda t: rag.encoder_question(e5, t), seuil)
    else:
        table, _ = a5.table_et_index_site()
        rs = ScoresReclasseur(rc.textes_lexicaux(table))
        try:
            preparees = preparer_r1(questions, {"index": index, "ctx": Contextes(index, table), "rs": rs,
                                                "lexical": bm25(table), "base": e5})
        finally:
            rs.ecrire()
    debut = dt.datetime.now(dt.timezone.utc)
    lignes = mesure.executer_etat(etat, preparees, generation.generer_reponse, modele, digest)
    res = {"protocole": "10, section 7, famille B de bout en bout", "etat": etat, "phase": phase, "modele": modele,
           "digest": digest, "version_ollama": infos["version"], "sha256_jeu_v2": SHA256_JEU_V2,
           "sha256_protocole": sha256(RACINE / "docs/etudes/evaluation/10_protocole_jeu_v2.md"),
           "debut": debut.isoformat(timespec="seconds"),
           "fin": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "contextes_tokens_max": max(l["entree"]["nb_tokens"] for l in lignes if l["entree"]) if any(l["entree"] for l in lignes) else None,
           "lignes": lignes}
    chemin = SORTIES / f"bout_en_bout_{etat}_{phase}_{debut.strftime('%Y%m%dT%H%M%SZ')}.json"
    print(f"écrit {chemin.name}, SHA-256 {a5.ecrire_une_fois(chemin, res)}")
    return chemin


def garde_m1(lignes_a: list[dict], lignes_b: list[dict]) -> dict:
    """Protocole 08 repris par le protocole 10 : M1 (abstention correcte hors corpus) de A ne doit pas baisser de plus
    d'une question par rapport à B, sur les questions hors corpus sans erreur technique dans les deux états."""
    a = {l["id"]: l for l in lignes_a if l["type"] == "hors_corpus"}
    b = {l["id"]: l for l in lignes_b if l["type"] == "hors_corpus"}
    if set(a) != set(b):
        raise ErreurMesure10("Questions hors corpus différentes entre les deux états")
    commune = [i for i in sorted(a) if "erreur_technique" not in (a[i]["classe"], b[i]["classe"])]
    sa = sum(a[i]["classe"] == "abstention" for i in commune)
    sb = sum(b[i]["classe"] == "abstention" for i in commune)
    return {"effectif_commun": len(commune), "abstentions_a": sa, "abstentions_b": sb, "baisse": sb - sa,
            "respectee": sb - sa <= 1}


def analyser_bout_en_bout() -> dict:
    import mesure
    fichiers = {}
    for etat, phase in EXECUTIONS:
        trouves = sorted(SORTIES.glob(f"bout_en_bout_{etat}_{phase}_*.json"))
        if len(trouves) != 1:
            raise ErreurMesure10(f"{etat}, {phase} : {len(trouves)} exécutions, une seule attendue")
        fichiers[(etat, phase)] = trouves[0]
    donnees = {k: json.loads(v.read_text(encoding="utf-8")) for k, v in fichiers.items()}
    table, _ = a5.table_et_index_site()
    pv2 = PertinenceV2(table.texte.tolist())
    ids = table.passage_id.tolist()
    pertinents = {q["id"]: {ids[i] for i in pv2.pertinents(q["extrait"])}
                  for q in questions_bout_en_bout() if q["type"] == "dans_corpus"}
    etiquete = {k: [{**l, "etat": "comparaison"} for l in d["lignes"]] for k, d in donnees.items()}
    res = {"protocole": "10, section 7, famille B de bout en bout",
           "sources": {f"{e}_{p}": {"fichier": f.name, "sha256": sha256(f)} for (e, p), f in fichiers.items()},
           "etats": {f"{e}_{p}": mesure.metriques(donnees[(e, p)]["lignes"], pertinents) for (e, p) in fichiers},
           "comparaisons": {}}
    for nom, a, b in (("R1_adapte_moins_B2_adapte", ("R1", "adapte"), ("B2", "adapte")),
                      ("R1_temoin_moins_R1_adapte", ("R1", "temoin"), ("R1", "adapte"))):
        c = mesure.comparer(etiquete[a], etiquete[b], pertinents)
        c["garde_m1"] = garde_m1(donnees[a]["lignes"], donnees[b]["lignes"])
        res["comparaisons"][nom] = c
    p_holm = holm({k: c["M4"]["mcnemar_p_exacte"] for k, c in res["comparaisons"].items()})
    for k, c in res["comparaisons"].items():
        c["M4"]["p_holm"] = p_holm[k]
    principale = res["comparaisons"]["R1_adapte_moins_B2_adapte"]
    res["decision"] = {"critere": "M4, R1 contre B2 avec le modèle adapté ; M1 ne baisse pas de plus d'une question",
                       "ecart_m4": principale["M4"]["ecart"], "intervalle_m4": principale["M4"]["intervalle"],
                       "m4_ameliore_demontre": principale["M4"]["intervalle"][0] > 0,
                       "garde_m1_respectee": principale["garde_m1"]["respectee"]}
    chemin = SORTIES / f"bout_en_bout_analyse_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    print(f"écrit {chemin.name}, SHA-256 {a5.ecrire_une_fois(chemin, res)}")
    return res


def afficher_b(res: dict) -> None:
    print(json.dumps({"decision": res["decision"], "controle_07": res["jeux"]["cdtn"]["controle_reproduction_07"],
                      "lot_reclasseur": res["jeux"]["cdtn"]["controle_lot_reclasseur"]}, ensure_ascii=False, indent=1))
    for nom in ("jeu_v2", "jeu_v1_test"):
        j = res["jeux"][nom]
        print(nom, j["questions"], "questions,", j["groupes"], "fiches ;",
              " ; ".join(f"{k} {v['rappel_contexte']:.3f} ({v['tokens_moyen']:.0f} tokens)" for k, v in j["systemes"].items()))
        for k, e in j["comparaisons"].items():
            print(f"  {k:10s} {e['ecart']:+.3f} [{e['ic95_tango'][0]:+.3f} ; {e['ic95_tango'][1]:+.3f}] "
                  f"{e['ajuste_seul']} contre {e['base_seule']}, p = {e['p_mcnemar']:.3f}, Holm {e['p_holm']:.3f}")
    c = res["jeux"]["cdtn"]
    print("cdtn", c["requetes"], "requêtes,", c["formulations"], "formulations ;",
          " ; ".join(f"{k} {v['moyenne']:.3f} [{v['ic95'][0]:.3f} ; {v['ic95'][1]:.3f}]" for k, v in c["systemes"].items()))
    for k, e in {**c["ecarts"], **{f"{s} R2-R1": v["R2_moins_R1"] for s, v in c["sous_populations"].items()}}.items():
        print(f"  {k:40s} {e['moyenne']:+.3f} [{e['ic95'][0]:+.3f} ; {e['ic95'][1]:+.3f}] ({e['requetes']} requêtes)")


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("commande", choices=("famille_a", "famille_b", "effet_k", "bout_en_bout", "analyser_bout_en_bout"))
    p.add_argument("--etat", choices=("B2", "R1"))
    p.add_argument("--phase", choices=tuple(PHASES))
    a = p.parse_args(argv)
    if a.commande == "bout_en_bout":
        if not (a.etat and a.phase):
            p.error("bout_en_bout demande --etat et --phase")
        bout_en_bout(a.etat, a.phase)
        return 0
    if a.commande == "analyser_bout_en_bout":
        res = analyser_bout_en_bout()
        print(json.dumps({"decision": res["decision"], "etats": {k: {m: (v[m] or {}).get("proportion") for m in ("M1", "M2", "M3", "M4", "M5")}
                                                                 for k, v in res["etats"].items()}}, ensure_ascii=False, indent=1))
        return 0
    if a.commande == "famille_b":
        afficher_b(famille_b())
        return 0
    if a.commande == "effet_k":
        effet_k()
        return 0
    res = famille_a()
    print(json.dumps({k: res[k] for k in ("controle_reproduction_05", "decision")}, ensure_ascii=False, indent=1))
    for nom, j in res["jeux"].items():
        e = j["ecart_recall5_F_moins_D"]
        print(f"{nom:12s} n={j['questions']:4d} | R@5 D {j['D']['recall@5']:.3f} F {j['F']['recall@5']:.3f} | écart {e['ecart']:+.3f} "
              f"[{e['ic95_tango'][0]:+.3f} ; {e['ic95_tango'][1]:+.3f}] F seul {e['ajuste_seul']} D seul {e['base_seule']} p={e['p_mcnemar']:.3f} | "
              f"fiche/10 D {j['D']['fiche_parmi_les_10_affiches']:.3f} F {j['F']['fiche_parmi_les_10_affiches']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
