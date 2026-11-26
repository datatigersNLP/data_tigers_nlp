"""Contributions par membre, mesurées dans le dépôt : tickets, commits et lignes.

Les heures déclarées du classeur de suivi sont des estimations rétrospectives (voir le rapport, section 3.3) : elles ne
servent pas à comparer les membres. Ce script ne compte que ce que GitHub et Git enregistrent.

Usage :
    git fetch origin --prune --tags
    git fetch origin '+refs/pull/*/head:refs/statpr/*'      # têtes de PR : commits des branches supprimées
    python3 -I scripts/suivi/contributions.py --depot . --reference origin/dev --csv contributions.csv --md contributions.md
    git for-each-ref --format='%(refname)' refs/statpr | xargs -n1 git update-ref -d     # nettoyage

Trois mesures, chacune avec sa définition :
  * tickets : assignés (GitHub), créés, et « touchés » (un commit ou une PR du membre cite le ticket, dans son sujet, son
    titre ou le nom de sa branche) ;
  * commits : commits uniques hors fusions, sur toutes les branches du dépôt GitHub et les têtes de PR ;
  * lignes : « ajoutées » = cumul de `git log --numstat` ; « conservées » = lignes non vides encore présentes dans la
    référence d'après `git blame -w -M -C`. Les lignes sont rangées par catégorie : code, documentation, notebooks
    (JSON brut, hors totaux), données et fichiers de verrouillage (hors totaux), autres.

Une adresse inconnue arrête le script : aucun commit ne tombe dans une catégorie fourre-tout. Les adresses qui ne sont
pas des adresses GitHub « noreply » se déclarent dans un fichier d'alias JSON, non versionné : {"partie locale": "login"}.
"""
import argparse
import collections
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

LOGINS = {"mahebegnis": "Mahé", "jibzzou": "Jibril", "remynou": "Remy", "vanecktiyo": "Vaneck", "msignate": "Maïmouna"}
MEMBRES = ["Mahé", "Jibril", "Remy", "Vaneck", "Maïmouna"]
NOREPLY = re.compile(r"^(?:\d+\+)?([^@]+)@users\.noreply\.github\.com$", re.I)
EXT_CODE = {"py", "js", "jsx", "mjs", "cjs", "ts", "tsx", "css", "html", "sh", "zsh", "ps1", "yml", "yaml", "toml", "cfg", "ini"}
EXT_DOC = {"md", "tex", "txt", "rst", "bib"}
EXT_DONNEES = {"json", "jsonl", "csv", "tsv", "svg", "xml", "xlsx", "lock"}
VERROU = re.compile(r"(?:^|[-_.])lock(?:[-_.]|$)")
CATEGORIES = ["code", "documentation", "notebooks", "donnees", "autres"]
TOTAUX = ["code", "documentation"]  # les carnets (JSON brut) et les données ne se comparent pas en lignes


def membre(adresse, alias=None):
    """Membre d'après l'adresse de l'auteur du commit ; ValueError si elle n'est pas reconnue."""
    m = NOREPLY.match(adresse.strip().lower())
    cle = m.group(1) if m else adresse.strip().lower().split("@")[0]
    cle = (alias or {}).get(cle, cle)
    if cle in LOGINS:
        return LOGINS[cle]
    raise ValueError("identité non reconnue : ajouter la partie locale de l'adresse au fichier d'alias")


def categorie(chemin):
    """Catégorie d'un fichier d'après son chemin ; pour un renommage, d'après le chemin d'arrivée."""
    if "=>" in chemin:
        chemin = re.sub(r"\{[^{}]*=> ([^{}]*)\}", r"\1", chemin).split(" => ")[-1]
    bas = chemin.lower().replace("//", "/")
    nom = bas.rsplit("/", 1)[-1]
    ext = nom.rsplit(".", 1)[-1] if "." in nom else ""
    if VERROU.search(nom) or re.match(r"requirements.*\.txt$", nom) or ext in EXT_DONNEES:
        return "donnees"
    if ext == "ipynb":
        return "notebooks"
    if ext == "html" and bas.startswith("docs/"):
        return "documentation"  # diapositives et pages de soutenance
    if ext in EXT_CODE or nom in {"dockerfile", "makefile"}:
        return "code"
    if ext in EXT_DOC:
        return "documentation"
    return "autres"


def numeros_de_tickets(texte, tickets, branche=""):
    """Tickets cités par un sujet de commit ou un titre de PR (« type(NN): … » et « #NN »), et par le nom d'une branche
    (« feat/163-chaine-v2 »). Un numéro qui n'est pas un ticket (le numéro d'une PR, par exemple) n'est pas retenu.
    Une plage écrite « #91 à #95 » ne donne que ses deux bornes : la mesure peut sous-compter, jamais sur-compter."""
    candidats = [int(x) for x in re.findall(r"#(\d+)", texte)]
    m = re.match(r"^\w+\((\d+)(?:[,/ ]|\))", texte)
    if m:
        candidats.append(int(m.group(1)))
    m = re.match(r"^[\w.-]+/(\d+)-", branche)
    if m:
        candidats.append(int(m.group(1)))
    return {n for n in candidats if n in tickets}


def compter_blame(sortie, alias=None):
    """Lignes non vides par membre dans une sortie `git blame --line-porcelain`."""
    comptes, adresse = collections.Counter(), None
    for ligne in sortie.split("\n"):
        if ligne.startswith("author-mail "):
            adresse = ligne[len("author-mail "):].strip("<>")
        elif ligne.startswith("\t") and ligne.strip():
            comptes[membre(adresse, alias)] += 1
    return comptes


def git(depot, *args):
    return subprocess.run(["git", "-C", str(depot), *args], capture_output=True, text=True, check=True).stdout


def commits(depot, alias, tickets):
    """Commits uniques hors fusions de tous les refs d'origine, des tags et des têtes de PR, avec leurs lignes ajoutées."""
    refs = ["--remotes=origin", "--tags", "--glob=refs/statpr/*"]
    stats = {m: collections.Counter() for m in MEMBRES}
    touches = {m: set() for m in MEMBRES}
    for ligne in git(depot, "log", *refs, "--merges", "--format=%aE").splitlines():
        stats[membre(ligne, alias)]["fusions"] += 1
    courant, vus = None, set()
    flux = git(depot, "log", *refs, "--no-merges", "-M", "--numstat", "--format=@@\x1f%H\x1f%aE\x1f%s")
    for ligne in flux.splitlines():
        if ligne.startswith("@@\x1f"):
            _, sha, adresse, sujet = ligne.split("\x1f", 3)
            try:
                courant = membre(adresse, alias)
            except ValueError as e:
                raise ValueError(f"{e} (commit {sha[:7]})") from None
            assert sha not in vus, "commit compté deux fois"
            vus.add(sha)
            stats[courant]["commits"] += 1
            cites = numeros_de_tickets(sujet, tickets)
            touches[courant] |= cites
            if not cites:
                stats[courant]["sans_ticket"] += 1
            continue
        if not ligne.strip():
            continue
        ajout, suppr, chemin = ligne.split("\t", 2)
        if ajout == "-":
            stats[courant]["binaires"] += 1
            continue
        c = categorie(chemin)
        stats[courant][f"ajouts_{c}"] += int(ajout)
        stats[courant][f"suppr_{c}"] += int(suppr)
    return stats, touches, vus


def commits_de_la_reference(depot, reference, alias):
    comptes = collections.Counter()
    for adresse in git(depot, "log", reference, "--no-merges", "--format=%aE").splitlines():
        comptes[membre(adresse, alias)] += 1
    return comptes


def lignes_conservees(depot, reference, alias):
    """Lignes non vides encore présentes dans la référence, par membre et par catégorie (code et documentation).
    Deux fichiers au contenu identique ne comptent qu'une fois (le premier chemin dans l'ordre alphabétique)."""
    comptes = {c: collections.Counter() for c in TOTAUX}
    vus = set()
    for ligne in sorted(git(depot, "ls-tree", "-r", reference).splitlines(), key=lambda l: l.split("\t", 1)[1]):
        meta, chemin = ligne.split("\t", 1)
        mode, type_, blob = meta.split()
        c = categorie(chemin)
        if type_ != "blob" or c not in TOTAUX or blob in vus:
            continue
        vus.add(blob)
        sortie = git(depot, "blame", "--line-porcelain", "-w", "-M", "-C", reference, "--", chemin)
        comptes[c].update(compter_blame(sortie, alias))
    return comptes


def github(depot, depot_distant=None):
    """Tickets et pull requests par l'API de GitHub (CLI gh)."""
    def gh(*args):
        r = subprocess.run(["gh", *args] + (["--repo", depot_distant] if depot_distant else []), capture_output=True, text=True,
                           check=True, cwd=str(depot))
        return json.loads(r.stdout)
    tickets = gh("issue", "list", "--state", "all", "--limit", "500", "--json", "number,state,stateReason,assignees,author")
    prs = gh("pr", "list", "--state", "all", "--limit", "500", "--json", "number,state,author,reviews,title,headRefName")
    return tickets, prs


def mesures_github(tickets, prs):
    """Tickets assignés, fermés, créés ; PR ouvertes, fusionnées ; relectures données sur la PR d'un autre."""
    t = {m: collections.Counter() for m in MEMBRES}
    touches = {m: set() for m in MEMBRES}
    numeros = {x["number"] for x in tickets}
    for x in tickets:
        auteur = LOGINS.get(((x.get("author") or {}).get("login") or "").lower())
        if auteur:
            t[auteur]["tickets_crees"] += 1
        for a in x["assignees"]:
            m = LOGINS.get(a["login"].lower())
            if not m:
                continue
            t[m]["tickets_assignes"] += 1
            if x["state"] == "CLOSED":
                t[m]["tickets_termines" if x.get("stateReason") == "COMPLETED" else "tickets_abandonnes"] += 1
    for p in prs:
        login_auteur = ((p.get("author") or {}).get("login") or "").lower()
        auteur = LOGINS.get(login_auteur)
        if auteur:
            t[auteur]["pr_ouvertes"] += 1
            if p["state"] == "MERGED":
                t[auteur]["pr_fusionnees"] += 1
            touches[auteur] |= numeros_de_tickets(p.get("title", ""), numeros, p.get("headRefName", ""))
        for r in p["reviews"]:
            login = ((r.get("author") or {}).get("login") or "").lower()
            if LOGINS.get(login) and login != login_auteur:
                t[LOGINS[login]]["relectures"] += 1  # les commentaires d'un auteur sur sa propre PR ne comptent pas
    return t, touches


def tableau(donnees, colonnes):
    lignes = []
    total = {c: sum(donnees[m][c] for m in MEMBRES) for c in colonnes}
    for m in MEMBRES:
        cellules = []
        for c in colonnes:
            part = 100 * donnees[m][c] / total[c] if total[c] else 0
            cellules.append(f"{donnees[m][c]:,} ({part:.0f} %)".replace(",", " "))
        lignes.append((m, cellules))
    lignes.append(("Total", [f"{total[c]:,}".replace(",", " ") for c in colonnes]))
    return lignes


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--depot", required=True)
    p.add_argument("--reference", default="origin/dev")
    p.add_argument("--alias", help="fichier JSON d'alias d'adresses (non versionné)")
    p.add_argument("--distant", help="dépôt GitHub OWNER/NOM pour gh (défaut : celui du dossier)")
    p.add_argument("--csv", required=True)
    p.add_argument("--md", required=True)
    a = p.parse_args()
    alias = json.loads(Path(a.alias).read_text(encoding="utf-8")) if a.alias else {}
    tickets, prs = github(a.depot, a.distant)
    gh_mesures, touches_pr = mesures_github(tickets, prs)
    stats, touches, vus = commits(a.depot, alias, {t["number"] for t in tickets})
    sur_reference = commits_de_la_reference(a.depot, a.reference, alias)
    conservees = lignes_conservees(a.depot, a.reference, alias)
    ligne = {}
    for m in MEMBRES:
        s, g = stats[m], gh_mesures[m]
        ligne[m] = collections.Counter({
            "tickets_assignes": g["tickets_assignes"], "tickets_termines": g["tickets_termines"], "tickets_crees": g["tickets_crees"],
            "tickets_touches": len(touches[m] | touches_pr[m]), "pr_ouvertes": g["pr_ouvertes"], "pr_fusionnees": g["pr_fusionnees"],
            "relectures": g["relectures"], "commits": s["commits"], "commits_reference": sur_reference[m], "fusions": s["fusions"],
            "ajouts_code": s["ajouts_code"], "suppr_code": s["suppr_code"], "conservees_code": conservees["code"][m],
            "ajouts_documentation": s["ajouts_documentation"], "suppr_documentation": s["suppr_documentation"],
            "conservees_documentation": conservees["documentation"][m],
            "ajouts_notebooks": s["ajouts_notebooks"], "ajouts_donnees": s["ajouts_donnees"], "ajouts_autres": s["ajouts_autres"],
            "binaires": s["binaires"]})
    colonnes = list(ligne["Mahé"].keys())
    with open(a.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["membre"] + colonnes)
        for m in MEMBRES:
            w.writerow([m] + [ligne[m][c] for c in colonnes])
        w.writerow(["total"] + [sum(ligne[m][c] for m in MEMBRES) for c in colonnes])
    blocs = [
        ("Tickets et pull requests", ["tickets_assignes", "tickets_termines", "tickets_touches", "tickets_crees", "pr_fusionnees", "relectures"],
         ["Tickets assignés", "dont terminés", "Tickets touchés (commit ou PR)", "Tickets créés", "PR fusionnées", "Relectures des PR des autres"]),
        ("Commits et lignes de code", ["commits", "commits_reference", "ajouts_code", "conservees_code"],
         ["Commits poussés", f"dont dans {a.reference}", "Lignes de code ajoutées", "Lignes de code conservées"]),
        ("Documentation", ["ajouts_documentation", "conservees_documentation"], ["Lignes de documentation ajoutées", "Lignes de documentation conservées"]),
        ("Hors totaux (volume brut, non comparable)", ["ajouts_notebooks", "ajouts_donnees"],
         ["Lignes ajoutées dans les carnets (JSON brut)", "Lignes ajoutées dans les données et verrous"]),
    ]
    sortie = [f"Référence : {a.reference} ({git(a.depot, 'rev-parse', '--short', a.reference).strip()}) ; commits uniques hors fusions : {len(vus)}.", ""]
    for titre, cols, noms in blocs:
        sortie += [f"**{titre}**", "", "| Membre | " + " | ".join(noms) + " |", "|---|" + "---:|" * len(noms)]
        for nom, cellules in tableau(ligne, cols):
            sortie.append(f"| {nom} | " + " | ".join(cellules) + " |")
        sortie.append("")
    Path(a.md).write_text("\n".join(sortie), encoding="utf-8")
    print("\n".join(sortie))


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        sys.exit(f"Erreur : {e}")
