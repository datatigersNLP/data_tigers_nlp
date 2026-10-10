"""
Contrôle du jeu de questions annotées (#44) et accord entre annotateurs (protocole du notebook 03, section 2.1).

Ne lit que les annotations et les passages découpés : aucun système n'est interrogé, aucun classement n'est
calculé. Il peut donc être exécuté avant la mesure, sur le lot de test compris.

Usage, depuis la racine du dépôt :
    python scripts/evaluation/controle_jeu.py [--questions CSV] [--secondaires CSV] [--avant-arbitrage CSV]
                                              [--sortie JSON]

L'accord se calcule sur l'annotation principale telle qu'elle était au moment de la seconde annotation : une
question arbitrée ensuite d'après l'annotation secondaire gonflerait l'accord. Le fichier d'avant l'arbitrage
s'obtient par exemple avec
    git show 187a9f8:evaluation/questions/questions_annotees.csv > avant_arbitrage.csv
"""

import argparse
import collections
import csv
import hashlib
import json
import math
import pathlib
import random
import sys

import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "scripts" / "evaluation"))
from pertinence import LONGUEUR_MINIMALE, IndexPertinence, normaliser  # noqa: E402

COLONNES = ["id", "lot", "type", "theme", "question", "url", "extrait", "redacteur", "double_annotation", "remarque"]
COLONNES_SEC = ["id_question", "annotateur", "url", "extrait", "accord_url", "accord_extrait", "remarque"]
DECOUPAGES = ["m0", "m1", "m2", "m2_256", "m3"]
DECOUPAGE_SERVI = "m2"
MIN_TEST_DANS_CORPUS = 68   # rapport J2
GRAINE, TIRAGES = 20261006, 10_000
Z95 = 1.959963984540054


def lire_csv(chemin):
    """Lignes d'un CSV UTF-8 sans BOM ni retour chariot, et empreinte SHA-256 du fichier."""
    octets = pathlib.Path(chemin).read_bytes()
    if octets.startswith(b"\xef\xbb\xbf") or b"\r" in octets:
        raise ValueError(f"{chemin} : BOM ou retour chariot présent.")
    return list(csv.DictReader(octets.decode("utf-8").splitlines(keepends=True))), hashlib.sha256(octets).hexdigest()


def kappa_cohen(paires, modalites):
    """Accord observé, accord attendu par hasard et kappa de Cohen (None si l'accord attendu vaut 1)."""
    n = len(paires)
    po = sum(a == b for a, b in paires) / n
    pe = sum((sum(a == m for a, _ in paires) / n) * (sum(b == m for _, b in paires) / n) for m in modalites)
    return po, pe, (None if pe == 1 else (po - pe) / (1 - pe))


def wilson(succes, n, z=Z95):
    p = succes / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - demi), min(1.0, centre + demi)


def sanity_check():
    """Contrôles calculés à la main."""
    # table a=10 (o,o), b=2 (o,n), c=3 (n,o), d=5 (n,n) ; po = 15/20 ; pe = 0,6 x 0,65 + 0,4 x 0,35 = 0,53
    paires = [("o", "o")] * 10 + [("o", "n")] * 2 + [("n", "o")] * 3 + [("n", "n")] * 5
    po, pe, k = kappa_cohen(paires, ["o", "n"])
    assert abs(po - 0.75) < 1e-12 and abs(pe - 0.53) < 1e-12 and abs(k - 0.22 / 0.47) < 1e-12
    assert kappa_cohen([("o", "o")] * 4, ["o", "n"])[2] is None
    # Wilson(3, 6) : centre 0,5 ; demi-largeur 1,96 x racine(0,25/6 + 3,8415/144) / 1,64025 = 0,3124
    lo, hi = wilson(3, 6)
    assert abs(lo - 0.1876) < 1e-4 and abs(hi - 0.8124) < 1e-4
    return True


def kappa_reechantillonne(paires, modalites):
    """Intervalle indicatif à 95 % du kappa, par rééchantillonnage des paires (percentiles) ; les tirages où le
    kappa n'est pas défini (une seule modalité) sont écartés et comptés."""
    alea, valeurs, degeneres = random.Random(GRAINE), [], 0
    for _ in range(TIRAGES):
        k = kappa_cohen([paires[alea.randrange(len(paires))] for _ in paires], modalites)[2]
        if k is None:
            degeneres += 1
        else:
            valeurs.append(k)
    valeurs.sort()
    return [valeurs[math.floor(0.025 * (len(valeurs) - 1))], valeurs[math.ceil(0.975 * (len(valeurs) - 1))]], degeneres


def charger_passages():
    manifeste = json.loads((RACINE / "data/decoupage/passages/manifeste.json").read_text(encoding="utf-8"))
    passages = {}
    for m in DECOUPAGES:
        info = manifeste["methodes"][m]
        chemin = RACINE / info["fichier"]
        if hashlib.sha256(chemin.read_bytes()).hexdigest() != info["sha256_fichier"]:
            raise ValueError(f"Empreinte de {chemin} différente du manifeste.")
        passages[m] = pd.read_parquet(chemin)
    return passages


def controler(questions, secondaires, avant):
    alertes, rapport = [], collections.OrderedDict()
    passages = charger_passages()
    urls_corpus = set(passages[DECOUPAGE_SERVI]["url"])
    rapport["corpus"] = {m: len(p) for m, p in passages.items()} | {"fiches": len(urls_corpus)}

    # 1. Structure
    if list(questions[0]) != COLONNES or list(secondaires[0]) != COLONNES_SEC:
        raise ValueError("Colonnes inattendues.")
    ids = [r["id"] for r in questions]
    if ids != [f"Q{i:03d}" for i in range(1, len(ids) + 1)]:
        raise ValueError("Identifiants non consécutifs ou non uniques.")
    par_id = {r["id"]: r for r in questions}
    for r in questions:
        if r["lot"] not in ("calibration", "test") or r["type"] not in ("dans_corpus", "hors_corpus"):
            alertes.append(f"{r['id']} : lot ou type non autorisé")
        if r["double_annotation"] not in ("oui", "non") or not r["question"].strip() or not r["redacteur"]:
            alertes.append(f"{r['id']} : double_annotation, question ou rédacteur invalide")
        if r["type"] == "hors_corpus" and (r["url"] or r["extrait"]):
            alertes.append(f"{r['id']} : hors corpus avec une URL ou un extrait")
        if r["type"] == "dans_corpus":
            if r["url"] not in urls_corpus:
                alertes.append(f"{r['id']} : URL absente du corpus")
            if len(normaliser(r["extrait"], False)) < LONGUEUR_MINIMALE:
                alertes.append(f"{r['id']} : extrait normalisé de moins de {LONGUEUR_MINIMALE} caractères")
        if "à relire" in r["remarque"].lower():
            alertes.append(f"{r['id']} : annotation encore marquée « à relire »")
    comptes = collections.Counter(f"{r['lot']}/{r['type']}" for r in questions)
    rapport["repartition"] = dict(sorted(comptes.items()))
    rapport["part_hors_corpus"] = round(sum(r["type"] == "hors_corpus" for r in questions) / len(questions), 4)
    if comptes["test/dans_corpus"] < MIN_TEST_DANS_CORPUS:
        alertes.append(f"moins de {MIN_TEST_DANS_CORPUS} questions du corpus dans le lot de test")
    urls = collections.Counter(r["url"] for r in questions if r["type"] == "dans_corpus")
    rapport["fiches_annotees"] = {"distinctes": len(urls), "au_plus_par_fiche": max(urls.values())}

    # 2. Règle D4 dans chaque découpage
    index = {m: IndexPertinence(p["texte"].tolist()) for m, p in passages.items()}
    url_de = {m: p["url"].tolist() for m, p in passages.items()}
    couverture = {}
    for m in DECOUPAGES:
        c = collections.Counter()
        for r in questions:
            if r["type"] == "dans_corpus":
                n = len(index[m].pertinents(r["extrait"]))
                c["0" if n == 0 else "1" if n == 1 else "2 ou plus"] += 1
                if n == 0:
                    alertes.append(f"{r['id']} : aucun passage pertinent en {m}")
        couverture[m] = dict(c)
    rapport["passages_pertinents_par_question"] = couverture

    # 3. Seconde annotation : complétude et indépendance des personnes
    ids_oui = sorted(r["id"] for r in questions if r["double_annotation"] == "oui")
    ids_sec = sorted(r["id_question"] for r in secondaires)
    if ids_oui != ids_sec:
        alertes.append("questions doublement annotées différentes de celles marquées « oui »")
    for r in secondaires:
        if r["annotateur"] == par_id[r["id_question"]]["redacteur"]:
            alertes.append(f"{r['id_question']} : annotation secondaire faite par le rédacteur")
        if bool(r["url"]) != bool(r["extrait"]):
            alertes.append(f"{r['id_question']} (secondaire) : URL et extrait pas tous deux remplis ou vides")
        if r["url"] and r["url"] not in urls_corpus:
            alertes.append(f"{r['id_question']} (secondaire) : URL absente du corpus")
    rapport["secondaires"] = {"nombre": len(secondaires),
                              "par_annotateur": dict(collections.Counter(r["annotateur"] for r in secondaires))}

    # 4. Accord, sur l'annotation principale au moment de la seconde annotation
    base = {r["id"]: r for r in avant}
    modalites = ["dans_corpus", "hors_corpus"]
    paires, lignes = [], []
    for r in secondaires:
        p = base[r["id_question"]]
        type_s = "dans_corpus" if r["url"] else "hors_corpus"
        paires.append((p["type"], type_s))
        ligne = {"id": p["id"], "type_principal": p["type"], "type_secondaire": type_s,
                 "accord_url_equipe": r["accord_url"], "accord_extrait_equipe": r["accord_extrait"]}
        if p["type"] == type_s == "dans_corpus":
            rp = set(index[DECOUPAGE_SERVI].pertinents(p["extrait"]))
            rs = set(index[DECOUPAGE_SERVI].pertinents(r["extrait"]))
            fp, fs = {url_de[DECOUPAGE_SERVI][i] for i in rp}, {url_de[DECOUPAGE_SERVI][i] for i in rs}
            ligne |= {"meme_url": p["url"] == r["url"], "passages_principale": len(rp), "passages_secondaire": len(rs),
                      "passages_communs": len(rp & rs), "memes_passages": rp == rs, "memes_fiches": fp == fs}
        attendu = "oui" if (type_s == p["type"] == "hors_corpus" or ligne.get("meme_url")) else "non"
        if r["accord_url"] != attendu:
            alertes.append(f"{p['id']} : accord_url renseigné {r['accord_url']}, recalculé {attendu}")
        lignes.append(ligne)
    po, pe, k = kappa_cohen(paires, modalites)
    n_acc = sum(a == b for a, b in paires)
    ic, degeneres = kappa_reechantillonne(paires, modalites)
    deux_dans = [l for l in lignes if "meme_url" in l]
    rapport["accord"] = {
        "type": {"table": {f"{a}/{b}": n for (a, b), n in sorted(collections.Counter(paires).items())},
                 "accord": f"{n_acc}/{len(paires)}", "wilson_95": [round(x, 3) for x in wilson(n_acc, len(paires))],
                 "accord_attendu": round(pe, 4), "kappa": None if k is None else round(k, 4),
                 "kappa_95_indicatif": [round(x, 3) for x in ic], "tirages_ecartes": degeneres},
        "paires_dans_le_corpus": len(deux_dans),
        "meme_url": sum(l["meme_url"] for l in deux_dans),
        f"memes_passages_{DECOUPAGE_SERVI}": sum(l["memes_passages"] for l in deux_dans),
        f"au_moins_un_passage_commun_{DECOUPAGE_SERVI}": sum(l["passages_communs"] > 0 for l in deux_dans),
        f"memes_fiches_pertinentes_{DECOUPAGE_SERVI}": sum(l["memes_fiches"] for l in deux_dans),
        "lignes": lignes,
    }
    rapport["alertes"] = alertes
    return rapport


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    dossier = RACINE / "evaluation" / "questions"
    parser.add_argument("--questions", default=dossier / "questions_annotees.csv")
    parser.add_argument("--secondaires", default=dossier / "annotations_secondaires.csv")
    parser.add_argument("--avant-arbitrage", default=None, help="annotation principale au moment de la seconde")
    parser.add_argument("--sortie", default=None, help="fichier JSON du rapport")
    args = parser.parse_args()
    assert sanity_check()
    questions, sha_q = lire_csv(args.questions)
    secondaires, sha_s = lire_csv(args.secondaires)
    avant, sha_a = lire_csv(args.avant_arbitrage) if args.avant_arbitrage else (questions, sha_q)
    rapport = {"empreintes": {"questions": sha_q, "secondaires": sha_s, "avant_arbitrage": sha_a}} | controler(
        questions, secondaires, avant)
    texte = json.dumps(rapport, ensure_ascii=False, indent=1)
    if args.sortie:
        pathlib.Path(args.sortie).write_text(texte + "\n", encoding="utf-8")
    print(texte)


if __name__ == "__main__":
    main()
