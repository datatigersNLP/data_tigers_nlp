"""Relecture humaine d'un échantillon des données d'adaptation (#107, étape 28) : grille à remplir, puis bilan.

    python scripts/adaptation_qwen/grille_relecture.py grille <lot>     # écrit grille_relecture.csv (tirage stratifié)
    python scripts/adaptation_qwen/grille_relecture.py bilan <lot>      # contrôle la grille remplie, applique la règle
    python scripts/adaptation_qwen/grille_relecture.py accord <lot> <A.csv> <B.csv>   # deux relectures séparées

Lot v2 (décision du 04/11, #107) : deux relecteurs remplissent chacun une copie de la grille, sans préremplissage ;
accord compare leurs verdicts (désaccords, kappa de Cohen sur « faux »). Les désaccords sont tranchés ensemble, et la
grille commune ainsi obtenue devient grille_relecture.csv, la seule que lisent bilan et l'entraînement.

La grille s'ouvre dans un tableur (UTF-8 avec BOM, séparateur « ; »). Les relecteurs remplissent, pour chaque exemple :
- question_naturelle : oui ou non (une vraie question d'utilisateur, autonome) ;
- reponse_juste : oui, partiel ou non (exemples cités ; juste au regard des passages cités) ;
- fidele_aux_passages : oui ou non (exemples cités ; chaque affirmation est dans le passage qu'elle cite) ;
- abstention_justifiee : oui ou non (abstentions ; aucun des cinq passages ne permet de répondre) ;
- commentaire : libre.

L'échantillon est stratifié (donnees_adaptation.tirage_relecture), tiré dans train.jsonl et valid.jsonl du lot ; le
tirage est déterministe, et a_relire.jsonl n'en est pas la référence (celui du lot du 30/10 précède ce tirage). Avant le
bilan, la grille remplie doit reprendre exactement les lignes du tirage, dans le même ordre, sans doublon, avec les mêmes
colonnes fixes ; seules les fins de ligne écrites par un tableur sont tolérées.

Règles écrites avant la relecture :
- un exemple est « faux » si reponse_juste vaut non, si fidele_aux_passages vaut non, ou si abstention_justifiee vaut
  non. Le lot est utilisable si 10 % au plus des exemples relus sont faux ; sinon, le filtre en cause est corrigé et le
  lot régénéré. Le taux est rapporté avec son intervalle de Wilson à 95 %, large sur 30 exemples : c'est un garde-fou,
  pas une mesure de la qualité du jeu entier ;
- variante « passage retiré » : Qwen s'abstient à tort sur 23 % des contextes qui contiennent le bon passage (lot du
  30/10), et cette variante garde les exemples où il s'abstient. Si plus de 2 de ses abstentions relues sont
  injustifiées, elle est retirée du lot, réassemblé avec les seules abstentions hors corpus.
"""

import csv
import io
import json
import math
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
DOSSIER = RACINE / "data" / "volet_b" / "donnees_adaptation"
COLONNES_FIXES = ("id", "variante", "question", "reponse_attendue", "passages")
COLONNES_VERDICT = ("question_naturelle", "reponse_juste", "fidele_aux_passages", "abstention_justifiee", "commentaire")
VALEURS = {"question_naturelle": {"oui", "non"}, "reponse_juste": {"oui", "partiel", "non", ""},
           "fidele_aux_passages": {"oui", "non", ""}, "abstention_justifiee": {"oui", "non", ""}}
PART_FAUX_MAX = 0.10
RETIRE_INJUSTIFIEES_MAX = 2


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


def echantillon(exemples: list[dict]) -> list[dict]:
    """Exemples tirés pour la relecture, dans l'ordre du lot (train puis valid)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from donnees_adaptation import tirage_relecture
    ids = set(tirage_relecture(exemples))
    return [e for e in exemples if e["id"] in ids]


def verifier_grille(lignes: list[dict], exemples: list[dict]) -> None:
    """La grille remplie reprend exactement le tirage du lot : mêmes lignes, même ordre, mêmes colonnes fixes."""
    attendues = list(csv.DictReader(io.StringIO(grille(echantillon(exemples))), delimiter=";"))
    ids = [l.get("id") for l in lignes]
    if len(ids) != len(set(ids)):
        raise ValueError("Grille non conforme : identifiants en double")
    if ids != [a["id"] for a in attendues]:
        manquants = sorted({a["id"] for a in attendues} - set(ids))
        raise ValueError(f"Grille non conforme au tirage du lot : {len(ids)} lignes pour {len(attendues)} attendues, "
                         f"manquantes {manquants[:5]}, étrangères {sorted(set(ids) - {a['id'] for a in attendues})[:5]}")
    norm = lambda t: (t or "").replace("\r\n", "\n")
    for a, l in zip(attendues, lignes):
        for c in COLONNES_FIXES:
            if norm(l.get(c)) != norm(a[c]):
                raise ValueError(f"Grille non conforme : colonne {c} modifiée pour {a['id']}")


def lire_exemples(lot: Path) -> list[dict]:
    return [json.loads(l) for n in ("train.jsonl", "valid.jsonl")
            for l in (lot / n).read_text(encoding="utf-8").splitlines() if l]


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
        if cite and not (l["reponse_juste"].strip() and l["fidele_aux_passages"].strip()) \
                or not cite and not l["abstention_justifiee"].strip():
            erreurs.append(f"{l['id']} : verdict manquant")
    if erreurs:
        raise ValueError("Grille incomplète ou mal remplie : " + " ; ".join(erreurs[:5]))
    faux = [l["id"] for l in lignes if "non" in (l["reponse_juste"].strip().lower(),
                                                 l["fidele_aux_passages"].strip().lower(),
                                                 l["abstention_justifiee"].strip().lower())]
    bas, haut = wilson(len(faux), len(lignes))
    retire = [l for l in lignes if l["variante"] == "passage_retire"]
    injustifiees = sum(l["abstention_justifiee"].strip().lower() == "non" for l in retire)
    return {"relus": len(lignes), "faux": len(faux), "ids_faux": faux, "part_faux": len(faux) / len(lignes),
            "ic95_wilson": [round(bas, 3), round(haut, 3)],
            "questions_non_naturelles": sum(l["question_naturelle"].strip().lower() == "non" for l in lignes),
            "par_variante": {v: {"relus": sum(l["variante"] == v for l in lignes),
                                 "faux": sum(l["variante"] == v and l["id"] in faux for l in lignes)}
                             for v in ("citee", "passage_retire", "hors_corpus")},
            "utilisable": len(faux) / len(lignes) <= PART_FAUX_MAX,
            "garder_passage_retire": injustifiees <= RETIRE_INJUSTIFIEES_MAX}


def accord(a: list[dict], b: list[dict]) -> dict:
    """Deux relectures séparées de la même grille : désaccords et kappa de Cohen sur le verdict « faux »."""
    ids = [l["id"] for l in a]
    if ids != [l["id"] for l in b]:
        raise ValueError("Les deux grilles ne portent pas sur les mêmes exemples, dans le même ordre")
    fa, fb = set(bilan(a)["ids_faux"]), set(bilan(b)["ids_faux"])
    n = len(ids)
    po = sum((i in fa) == (i in fb) for i in ids) / n
    pe = (len(fa) / n) * (len(fb) / n) + (1 - len(fa) / n) * (1 - len(fb) / n)
    colonnes = [c for c in COLONNES_VERDICT if c != "commentaire"]
    ecarts = {la["id"]: [c for c in colonnes if la[c].strip().lower() != lb[c].strip().lower()] for la, lb in zip(a, b)}
    return {"relus": n, "faux_a": len(fa), "faux_b": len(fb), "accord_observe": round(po, 3),
            "kappa": round((po - pe) / (1 - pe), 3) if pe < 1 else None,     # indéfini si un seul verdict partout
            "desaccords_sur_faux": sorted(fa ^ fb), "desaccords_par_colonne": {i: c for i, c in ecarts.items() if c}}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not (len(argv) == 2 and argv[0] in ("grille", "bilan") or len(argv) == 4 and argv[0] == "accord"):
        print(__doc__)
        return 2
    lot = DOSSIER / argv[1]
    exemples = lire_exemples(lot)
    if argv[0] == "accord":
        grilles = []
        for nom in argv[2:]:
            with open(lot / Path(nom).name, encoding="utf-8-sig", newline="") as f:
                grilles.append(list(csv.DictReader(f, delimiter=";")))
            verifier_grille(grilles[-1], exemples)
        print(json.dumps(accord(*grilles), ensure_ascii=False, indent=1))
        return 0
    if argv[0] == "grille":
        choisis = echantillon(exemples)
        with open(lot / "grille_relecture.csv", "x", encoding="utf-8-sig", newline="") as f:
            f.write(grille(choisis))
        print(f"{len(choisis)} exemples dans {lot / 'grille_relecture.csv'} : "
              + ", ".join(f"{v} {sum(e['variante'] == v for e in choisis)}" for v in ("citee", "passage_retire", "hors_corpus")))
        return 0
    with open(lot / "grille_relecture.csv", encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    verifier_grille(lignes, exemples)
    resultat = bilan(lignes)
    print(json.dumps(resultat, ensure_ascii=False, indent=1))
    return 0 if resultat["utilisable"] else 1


if __name__ == "__main__":
    sys.exit(main())
