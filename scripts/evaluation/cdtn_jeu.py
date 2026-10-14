"""
Jeu complémentaire du CDTN (#56) pour l'analyse secondaire du notebook 03 (protocole, section 8.3 ;
docs/etudes/evaluation/04_cdtn.md).

Règle d'appariement, figée avant la mesure du notebook 03 :
1. fiche : l'identifiant de la référence (`/fiche-ministere-travail/<identifiant>`) est exactement celui d'une de nos
   261 fiches ; aucun rapprochement approximatif ;
2. section : l'ancre de la référence, ramenée à ses lettres et chiffres sans accents ni résidu « nbsp », est égale
   au titre d'une section de la fiche ramené de même ; à défaut, si elle compte au moins 30 caractères, elle est le
   début du titre d'une seule section de la fiche (le CDTN tronque les titres longs) ;
3. passages pertinents : les passages M2 qui couvrent au moins une section appariée de la requête.

Formulations retenues pour chaque requête appariée : son titre (tirets remplacés par des espaces) et ses variantes
rédigées en question (contenant « ? », règle du 4 octobre). Le jugement porte sur la requête : ses formulations
héritent toutes des mêmes passages pertinents.

Les données du CDTN n'ont pas de licence : seuls des identifiants et des verdicts sont versionnés.

Usage, depuis la racine du dépôt :
    python scripts/evaluation/cdtn_jeu.py construire   # jeu local, identifiants versionnés, fiches de relecture
    python scripts/evaluation/cdtn_jeu.py importer     # verdicts des fiches de relecture vers evaluation/cdtn/
"""

import collections
import csv
import hashlib
import json
import pathlib
import re
import sys
import unicodedata

import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "scripts" / "evaluation"))
from cdtn_seuil import FICHIER_SOURCE, SOURCE, est_question, identifiant_fiche, sha256_fichier  # noqa: E402

LONGUEUR_PREFIXE = 30
RELECTEURS = ["JIBZZOU", "msignate", "vanecktiyo"]
DOSSIER_LOCAL = RACINE / "data" / "evaluation" / "cdtn"
DOSSIER_VERSIONNE = RACINE / "evaluation" / "cdtn"
JEU_LOCAL = DOSSIER_LOCAL / "jeu_cdtn.json"
IDENTIFIANTS = DOSSIER_VERSIONNE / "identifiants.csv"
JUGEMENTS = DOSSIER_VERSIONNE / "jugements.csv"
VERDICTS = {"oui", "partiel", "non"}


def cle(texte):
    """Lettres et chiffres seuls, en minuscules, sans accents ni résidu « nbsp » (ancres et titres de section)."""
    t = unicodedata.normalize("NFKD", texte.replace("’", "'"))
    t = "".join(ch for ch in t if not unicodedata.combining(ch)).lower()
    t = re.sub(r"(^|[^a-z0-9])nbsp([^a-z0-9]|$)", " ", t)
    return re.sub(r"[^a-z0-9]", "", t)


def apparier_section(ancre, sections):
    """Indices des sections de la fiche que désigne l'ancre, et le mode ; sections : liste (indice, titre)."""
    a = cle(ancre)
    exactes = [i for i, t in sections if cle(t) == a]
    if exactes:
        return exactes, "exacte"
    debut = [i for i, t in sections if len(a) >= LONGUEUR_PREFIXE and cle(t).startswith(a)]
    if len(debut) == 1:
        return debut, "début de titre"
    return [], "absente"


def charger_passages():
    manifeste = json.loads((RACINE / "data/decoupage/passages/manifeste.json").read_text(encoding="utf-8"))
    tables, titres = {}, {}
    for m in ("m0", "m2", "m2_256"):
        info = manifeste["methodes"][m]
        chemin = RACINE / info["fichier"]
        if sha256_fichier(chemin) != info["sha256_fichier"]:
            raise ValueError(f"Empreinte de {chemin} différente du manifeste.")
        tables[m] = pd.read_parquet(chemin)
        for u, i, t in zip(tables[m].url, tables[m].section_idx, tables[m].section_titre):
            if int(i) >= 0:
                cle_section = (u.rstrip("/").rsplit("/", 1)[1], int(i))
                if titres.get(cle_section, t) != t:
                    raise ValueError(f"Titres différents pour la section {cle_section}.")
                titres[cle_section] = t
    m2 = tables["m2"].copy()
    m2["fiche"] = m2.url.str.rstrip("/").str.rsplit("/", n=1).str[1]
    return m2, titres


def construire_jeu(requetes, m2, titres):
    sections_de = collections.defaultdict(list)
    for (f, i), t in sorted(titres.items()):
        sections_de[f].append((i, t))
    fiches = set(m2.fiche)
    jeu, bilan = [], collections.Counter()
    for k, req in enumerate(requetes):
        appariees = {}
        for r in req["refs"]:
            f = identifiant_fiche(r["url"])
            if f not in fiches:
                continue
            if "#" not in r["url"]:
                bilan["sans ancre"] += 1
                continue
            indices, mode = apparier_section(r["url"].split("#", 1)[1], sections_de[f])
            bilan[mode] += 1
            for i in indices:
                appariees[(f, i)] = mode
        if not appariees:
            continue
        pertinents = [pid for pid, f, sc in zip(m2.passage_id, m2.fiche, m2.sections_couvertes)
                      if any((f, int(s)) in appariees for s in sc)]
        formulations = [{"id": f"R{k:03d}-T", "type": "titre", "texte": req["title"].replace("-", " ")}]
        formulations += [{"id": f"R{k:03d}-V{j:02d}", "type": "question", "texte": v}
                         for j, v in enumerate(req["variants"]) if est_question(v)]
        jeu.append({"id": f"R{k:03d}", "titre": req["title"], "formulations": formulations,
                    "sections": [{"fiche": f, "indice": i, "titre": titres[(f, i)], "mode": mode}
                                 for (f, i), mode in sorted(appariees.items())],
                    "passages_pertinents": pertinents})
    return jeu, bilan


def empreinte_jeu(jeu):
    """Empreinte des seuls identifiants (formulations et passages pertinents), indépendante des textes."""
    lignes = [f"{fo['id']}\t{' '.join(r['passages_pertinents'])}" for r in jeu for fo in r["formulations"]]
    return hashlib.sha256("\n".join(lignes).encode("utf-8")).hexdigest()


def construire():
    if sha256_fichier(FICHIER_SOURCE) != SOURCE["sha256"]:
        raise ValueError("Empreinte de la source du CDTN différente de celle figée dans #56.")
    requetes = json.loads(FICHIER_SOURCE.read_text(encoding="utf-8"))
    m2, titres = charger_passages()
    jeu, bilan = construire_jeu(requetes, m2, titres)
    DOSSIER_LOCAL.mkdir(parents=True, exist_ok=True)
    DOSSIER_VERSIONNE.mkdir(parents=True, exist_ok=True)
    JEU_LOCAL.write_text(json.dumps({"source": SOURCE, "empreinte_identifiants": empreinte_jeu(jeu), "requetes": jeu},
                                    ensure_ascii=False, indent=1), encoding="utf-8")
    # identifiants versionnés : aucun texte du CDTN
    with open(IDENTIFIANTS, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["id_formulation", "id_requete", "type", "passages_pertinents"])
        for r in jeu:
            for fo in r["formulations"]:
                w.writerow([fo["id"], r["id"], fo["type"], " ".join(r["passages_pertinents"])])
    # fiches de relecture locales : textes du CDTN, jamais versionnées ; répartition par requête, à tour de rôle
    url_de = dict(zip(m2.fiche, m2.url))
    lien = {(f, int(s)): u for f, sc, u in zip(m2.fiche, m2.sections_couvertes, m2.url_citation) for s in sc}
    for n, relecteur in enumerate(RELECTEURS):
        with open(DOSSIER_LOCAL / f"relecture_{relecteur}.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["id_requete", "id_formulation", "formulation", "sections_de_notre_corpus", "liens",
                        "verdict_requete", "formulation_a_ecarter", "remarque"])
            for r in jeu[n::len(RELECTEURS)]:
                sections = " | ".join(f"{s['titre']} ({s['fiche']})" for s in r["sections"])
                liens = " ".join(lien.get((s["fiche"], s["indice"]), url_de[s["fiche"]]) for s in r["sections"])
                for j, fo in enumerate(r["formulations"]):
                    w.writerow([r["id"], fo["id"], fo["texte"], sections if j == 0 else "", liens if j == 0 else "",
                                "", "", ""])
    n_form = sum(len(r["formulations"]) for r in jeu)
    print(f"{len(jeu)} requêtes, {n_form} formulations ; appariement des références : {dict(bilan)}")
    print(f"empreinte des identifiants : {empreinte_jeu(jeu)}")
    for n, relecteur in enumerate(RELECTEURS):
        part = jeu[n::len(RELECTEURS)]
        print(f"  {relecteur} : {len(part)} requêtes, {sum(len(r['formulations']) for r in part)} formulations")


def importer():
    """Verdicts des fiches de relecture vers evaluation/cdtn/jugements.csv : identifiants et verdicts seulement."""
    lignes = []
    for relecteur in RELECTEURS:
        chemin = DOSSIER_LOCAL / f"relecture_{relecteur}.csv"
        with open(chemin, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["verdict_requete"]:
                    if r["verdict_requete"] not in VERDICTS:
                        raise ValueError(f"{chemin.name}, {r['id_requete']} : verdict « {r['verdict_requete']} » "
                                         f"hors de {sorted(VERDICTS)}.")
                    lignes.append([r["id_requete"], "", relecteur, r["verdict_requete"]])
                if r["formulation_a_ecarter"].strip().lower() == "oui":
                    lignes.append([r["id_requete"], r["id_formulation"], relecteur, "écartée"])
    with open(JUGEMENTS, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["id_requete", "id_formulation", "relecteur", "verdict"])
        w.writerows(lignes)
    print(f"{len(lignes)} jugements écrits dans {JUGEMENTS.relative_to(RACINE)}")


def sanity_check():
    """Contrôles calculés à la main."""
    assert cle("Quelle est la durée du contrat ?") == "quelleestladureeducontrat"
    assert cle("Quelles-sont-les-caracteristiques-de-la-sanction-disciplinaire-nbsp") == cle(
        "Quelles sont les caractéristiques de la sanction disciplinaire ?")
    sections = [(0, "Chapô"), (1, "Que se passe-t-il à l'issue des périodes de suspension du contrat de travail ?"),
                (2, "Comment contester une sanction ?")]
    assert apparier_section("Comment-contester-une-sanction", sections) == ([2], "exacte")
    assert apparier_section("Que-se-passe-t-il-a-l-issue-des-periodes-de-suspension-du-contrat-de-nbsp",
                            sections) == ([1], "début de titre")
    assert apparier_section("Comment-contester", sections) == ([], "absente")   # moins de 30 caractères
    doubles = [(3, "Comment calculer le montant de l'indemnité légale ?"),
               (4, "Comment calculer le montant de l'indemnité conventionnelle ?")]
    assert apparier_section("Comment-calculer-le-montant-de-l-indemnite", doubles) == ([], "absente")   # ambiguë
    requetes = [{"title": "a-b", "variants": ["x ?", "y"], "refs": [{"url": "/fiche-ministere-travail/f1#Titre-un"}]},
                {"title": "c", "variants": ["z ?"], "refs": [{"url": "/fiche-ministere-travail/f1"}]}]
    m2 = pd.DataFrame({"passage_id": ["p0", "p1", "p2"], "fiche": ["f1", "f1", "f1"],
                       "sections_couvertes": [[0], [1], [1, 2]]})
    jeu, bilan = construire_jeu(requetes, m2, {("f1", 0): "Chapô", ("f1", 1): "Titre un", ("f1", 2): "Titre deux"})
    assert [r["id"] for r in jeu] == ["R000"] and jeu[0]["passages_pertinents"] == ["p1", "p2"]
    assert [fo["id"] for fo in jeu[0]["formulations"]] == ["R000-T", "R000-V00"]
    assert jeu[0]["formulations"][0]["texte"] == "a b" and bilan == {"exacte": 1, "sans ancre": 1}
    return True


if __name__ == "__main__":
    assert sanity_check()
    {"construire": construire, "importer": importer}[sys.argv[1]]()
