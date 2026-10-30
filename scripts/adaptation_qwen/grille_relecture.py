"""Relecture humaine d'un échantillon des données d'adaptation (#107, étape 28) : grille à remplir, puis bilan.

    python scripts/adaptation_qwen/grille_relecture.py grille <lot>     # écrit grille_relecture.csv à partir de a_relire.jsonl
    python scripts/adaptation_qwen/grille_relecture.py bilan <lot>      # lit la grille remplie et applique la règle

La grille s'ouvre dans un tableur (UTF-8 avec BOM, séparateur « ; »). Les relecteurs remplissent, pour chaque exemple :
- question_naturelle : oui ou non (une vraie question d'utilisateur, autonome) ;
- reponse_juste : oui, partiel ou non (exemples cités ; juste au regard des passages cités) ;
- fidele_aux_passages : oui ou non (exemples cités ; chaque affirmation est dans le passage qu'elle cite) ;
- abstention_justifiee : oui ou non (abstentions ; aucun des cinq passages ne permet de répondre) ;
- commentaire : libre.

Règle écrite avant la relecture : un exemple est « faux » si reponse_juste vaut non, si fidele_aux_passages vaut non,
ou si abstention_justifiee vaut non. Le lot est utilisable si 10 % au plus des exemples relus sont faux ; sinon, le
filtre en cause est corrigé et le lot régénéré. Le taux est rapporté avec son intervalle de Wilson à 95 %, qui reste
large sur une quarantaine d'exemples : la règle est un garde-fou, pas une mesure de qualité du jeu entier.
"""

import csv
import io
import json
import math
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
DOSSIER = RACINE / "data" / "volet_b" / "donnees_adaptation"
COLONNES_VERDICT = ("question_naturelle", "reponse_juste", "fidele_aux_passages", "abstention_justifiee", "commentaire")
VALEURS = {"question_naturelle": {"oui", "non"}, "reponse_juste": {"oui", "partiel", "non", ""},
           "fidele_aux_passages": {"oui", "non", ""}, "abstention_justifiee": {"oui", "non", ""}}
PART_FAUX_MAX = 0.10


def passages_a_relire(exemple: dict) -> str:
    """Exemple cité : les passages qu'il cite ; abstention : les cinq, pour juger qu'aucun ne permet de répondre."""
    contexte = exemple["messages"][1]["content"]
    reponse = exemple["messages"][2]["content"]
    textes = {}
    for b in contexte.split("\n\n[P")[1:]:
        ref, _, reste = b.partition("]")
        fiche = reste.split("Fiche : ", 1)[-1].split("\n", 1)[0]
        textes[f"[P{ref}]"] = f"({fiche}) " + reste.split("Texte original :\n", 1)[-1].strip()
    retenues = [r for r in textes if r in reponse] if exemple["type"] == "citee" else list(textes)
    return "\n\n".join(f"{r} {textes[r]}" for r in retenues)


def grille(exemples: list[dict]) -> str:
    sortie = io.StringIO()
    w = csv.writer(sortie, delimiter=";", lineterminator="\n")
    w.writerow(("id", "variante", "question", "reponse_attendue", "passages") + COLONNES_VERDICT)
    for e in exemples:
        w.writerow((e["id"], e["variante"], e["question"], e["messages"][2]["content"], passages_a_relire(e))
                   + ("",) * len(COLONNES_VERDICT))
    return sortie.getvalue()


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - demi), min(1.0, centre + demi))


def bilan(lignes: list[dict]) -> dict:
    erreurs = []
    for l in lignes:
        for c, ok in VALEURS.items():
            if l.get(c, "").strip().lower() not in ok:
                erreurs.append(f"{l['id']} : {c} = {l.get(c)!r}")
        cite = l["variante"] == "citee"
        if cite and not l["reponse_juste"].strip() or not cite and not l["abstention_justifiee"].strip():
            erreurs.append(f"{l['id']} : verdict manquant")
    if erreurs:
        raise ValueError("Grille incomplète ou mal remplie : " + " ; ".join(erreurs[:5]))
    faux = [l["id"] for l in lignes if "non" in (l["reponse_juste"].strip().lower(),
                                                 l["fidele_aux_passages"].strip().lower(),
                                                 l["abstention_justifiee"].strip().lower())]
    bas, haut = wilson(len(faux), len(lignes))
    return {"relus": len(lignes), "faux": len(faux), "ids_faux": faux, "part_faux": len(faux) / len(lignes),
            "ic95_wilson": [round(bas, 3), round(haut, 3)],
            "questions_non_naturelles": sum(l["question_naturelle"].strip().lower() == "non" for l in lignes),
            "utilisable": len(faux) / len(lignes) <= PART_FAUX_MAX}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2 or argv[0] not in ("grille", "bilan"):
        print(__doc__)
        return 2
    lot = DOSSIER / argv[1]
    if argv[0] == "grille":
        exemples = [json.loads(l) for l in (lot / "a_relire.jsonl").read_text(encoding="utf-8").splitlines() if l]
        with open(lot / "grille_relecture.csv", "x", encoding="utf-8-sig", newline="") as f:
            f.write(grille(exemples))
        print(f"{len(exemples)} exemples dans {lot / 'grille_relecture.csv'}")
        return 0
    with open(lot / "grille_relecture.csv", encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    resultat = bilan(lignes)
    print(json.dumps(resultat, ensure_ascii=False, indent=1))
    return 0 if resultat["utilisable"] else 1


if __name__ == "__main__":
    sys.exit(main())
