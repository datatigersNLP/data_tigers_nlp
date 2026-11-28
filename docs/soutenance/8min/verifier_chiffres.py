"""Vérifie chaque chiffre du support de 8 minutes contre sa source, et que le support ne contient aucun tiret long.

    python docs/soutenance/8min/verifier_chiffres.py [--donnees <dossier data/ d'une copie du dépôt>]

Les chiffres recalculables le sont à partir des fichiers de résultats (protocoles 07 et 10, dans data/, non versionné) ;
les autres sont lus dans les documents versionnés qui les publient (texte exact recherché). Sortie : une ligne par
chiffre, et un code de retour non nul si l'un d'eux manque ou diffère.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[2]


def pc(x: float) -> str:
    return f"{100 * x:.1f}".replace(".", ",")


def doc(chemin: str, ref: str = "origin/dev") -> str:
    """Document versionné, lu sur dev (ou une autre référence) sans changer de branche."""
    return subprocess.run(["git", "-C", str(RACINE), "show", f"{ref}:{chemin}"], capture_output=True, text=True,
                          check=True).stdout


def doc_premier(chemin: str, refs: tuple[str, ...]) -> str:
    """Premier document trouvé parmi plusieurs références (branche d'une PR ouverte, puis dev après sa fusion)."""
    for ref in refs:
        try:
            return doc(chemin, ref)
        except subprocess.CalledProcessError:
            continue
    return ""


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--donnees", type=Path, default=Path.home() / "NLP2_local/depot_v2/data")
    a = p.parse_args(argv)
    gabarit = (ICI / "deck.html").read_text(encoding="utf-8")
    texte = re.sub(r"<[^>]+>", " ", gabarit).replace("&nbsp;", " ").replace(" ", " ")
    texte = re.sub(r"\s+", " ", texte)
    donnees = json.loads((ICI / "donnees.json").read_text(encoding="utf-8"))
    D = a.donnees
    b = json.loads((D / "evaluation/protocole_10/famille_b_20261117T131518Z.json").read_text(encoding="utf-8"))["jeux"]
    k = json.loads((D / "evaluation/protocole_10/effet_k_20261117T131939Z.json").read_text(encoding="utf-8"))
    g = json.loads((D / "evaluation/recuperation/resultats_grille.json").read_text(encoding="utf-8"))["configurations"]
    conf = json.loads((D / "evaluation/recuperation/confirmation/resultats.json").read_text(encoding="utf-8"))["principal"]
    bb = json.loads((D / "evaluation/protocole_10/bout_en_bout_analyse_20261121T134041Z.json").read_text(encoding="utf-8"))
    ea3 = json.loads((D / "evaluation/protocole_10/famille_e_a3_20261121T162956Z.json").read_text(encoding="utf-8"))["candidats"]
    e3, ea3v2t = ea3["v3_C"], ea3["v2_T"]
    r10 = doc_premier("docs/etudes/evaluation/10_resultats.md", ("origin/docs/171-protocole-10", "origin/dev"))
    r05 = doc("docs/etudes/evaluation/05_resultats_ajustement.md")
    rapport = doc("docs/rapport/RAPPORT_FINAL.md")
    j3 = doc("docs/jalons/J3_diapositives_mahe.md")
    q = lambda c: g[c]["questions"]
    controles = [
        # (chiffre tel qu'écrit dans le support, valeur de la source formatée, source)
        ("4 240 passages", "4 240 passages" if "4 240 passages" in rapport else None, "rapport, section 1"),
        ("261 fiches", "261 fiches" if "261 fiches" in rapport else None, "rapport, section 1"),
        ("65,7 Mio", "65,7 Mio" if "65,7 Mio" in r05 else None, "05_resultats, section 3"),
        ("112,8", "112,8" if "112,8" in rapport else None, "rapport, 2.3"),
        ("21 ms", "21 ms" if "21 ms" in rapport else None, "rapport, 2.2"),
        ("43,8 %", "43,8 %" if "| 43,8 % |" in r05 else None, "05_resultats, Recall@5 base"),
        ("63,0 %", "63,0 %" if "| 63,0 % |" in r05 else None, "05_resultats, Recall@5 ajusté"),
        ("+19,2 points", "+19,2 points" if "+19,2 points" in r05 else None, "05_resultats, écart"),
        ("+9,7 à +30,4", "+9,7 à +30,4" if "+9,7 à +30,4" in r05 else None, "05_resultats, IC"),
        ("93,2 %", "93,2 %" if "93,2 %" in r05 else None, "05_resultats, section 4"),
        ("185,5 s", "185,5 s" if "2 époques, 185,5 s" in rapport else None, "rapport, annexe (ajustement)"),
        ("109 paires", "109 paires" if "109 paires" in rapport else None, "rapport, 2.1"),
        ("45,2 %", pc(conf["rappel_contexte_r0"]) + " %", "confirmation du 9/11, R0"),
        ("72,6 %", pc(conf["rappel_contexte_v2"]) + " %", "confirmation du 9/11, V2"),
        ("57,0 %", pc(b["jeu_v2"]["systemes"]["R0"]["rappel_contexte"]) + " %", "famille B, jeu v2, R0"),
        ("86,0 %", pc(b["jeu_v2"]["systemes"]["R1"]["rappel_contexte"]) + " %", "famille B, jeu v2, R1"),
        ("+28,9 points", f"+{pc(b['jeu_v2']['comparaisons']['R1_moins_R0']['ecart'])} points", "famille B, jeu v2, R1 moins R0"),
        ("70,9 %", pc(q("e5+k5")["rappel_contexte"]["moyenne"]) + " %", "grille 07, e5+k5"),
        ("85,1 %", pc(q("rrf+k10+bge-m3@20")["rappel_contexte"]["moyenne"]) + " %", "grille 07, retenue"),
        ("+14,2 points", f"+{pc(q('rrf+k10+bge-m3@20')['ecart_rappel_vs_reference']['moyenne'])} points", "grille 07, écart"),
        ("66,1 %", pc(k["jeu_v2"]["E5 de base"]["k10"]) + " %", "effet de k, E5, k10"),
        ("66,9 %", pc(k["jeu_v2"]["RRF sans reclasseur"]["k5"]) + " %", "effet de k, fusion, k5"),
        ("76,9 %", pc(k["jeu_v2"]["RRF sans reclasseur"]["k10"]) + " %", "effet de k, fusion, k10"),
        ("81,0 %", pc(k["jeu_v2"]["R1, RRF et bge-m3"]["k5"]) + " %", "effet de k, R1, k5"),
        ("3 953 tokens", f"{round(q('rrf+k10+bge-m3@20')['tokens']['moyenne']):,} tokens".replace(",", " "), "grille 07, tokens k10"),
        ("2 179", f"{round(q('rrf+k5+bge-m3@20')['tokens']['moyenne']):,}".replace(",", " "), "grille 07, tokens k5"),
        ("23,4 %", pc(q("rrf+k10+bge-m3@20")["precision_contexte"]["moyenne"]) + " %", "grille 07, précision k10"),
        ("31,4 %", pc(q("rrf+k5+bge-m3@20")["precision_contexte"]["moyenne"]) + " %", "grille 07, précision k5"),
        ("6 889 tokens", f"{q('e5+k15')['tokens_max']:,} tokens".replace(",", " "), "grille 07, e5+k15, maximum"),
        ("+11,1 points", "+11,1 points" if "+11,1" in j3 else None, "J3, diapositive 8"),
        ("4,36 Gio", "4,36 Gio" if "4,36 Gio" in rapport else None, "rapport, 2.1"),
        ("81,6 %", "81,6 %" if "81,6 %" in rapport else None, "rapport, 2.3"),
        ("218 exemples", "218 exemples" if "218 exemples" in j3 else None, "J3, diapositive 7"),
        ("52,9 %", pc(bb["etats"]["R1_adapte"]["M4"]["proportion"]) + " %", "bout en bout, R1 adapté, M4"),
        ("+16,9 points", f"+{pc(bb['comparaisons']['R1_adapte_moins_B2_adapte']['M4']['ecart'])} points", "bout en bout, M4, R1 moins B2"),
        ("11,8 s", f"{bb['etats']['R1_adapte']['descriptif']['duree_totale_mediane_ns'] / 1e9:.1f}".replace(".", ",") + " s", "bout en bout, R1 adapté, durée médiane"),
        ("2 289 et 2 420", "2 289 et 2 420" if "2 289 paires d'entraînement" in r10 and "2 420 paires d'entraînement" in r10 else None, "10_resultats, sections 7 et 7 bis"),
        ("12,4 points", f"{pc(e3['jeu_v2']['ecart_recall5']['ecart'])} points", "famille E, A3, v3-C, jeu v2"),
        ("recule de 5,5 points", f"recule de {pc(-e3['jeu_v1_test']['ecart_recall5']['ecart'])} points", "famille E, A3, v3-C, lot de test"),
        # annexes (26/11) : mesure de bout en bout (A3) et encodeurs synthétiques (A5)
        # (28/11 : les diapositives 10 à 12 sont supprimées ; les contrôles qui ne portaient que sur elles le sont aussi : 84,3 %, 13,9 puis 25,0 %, 8 faux sur 30, 121 + 40)
        *[(f"{e['M' + m]['succes']} sur {e['M' + m]['effectif']}", f"{e['M' + m]['succes']} sur {e['M' + m]['effectif']}"
           if "M" + m in e else None, f"bout en bout, {nom}, M{m}")
          for nom, e in bb["etats"].items() for m in "1234"],
        ("10,1 %", pc(bb["etats"]["R1_temoin"]["M4"]["proportion"]) + " %", "bout en bout, R1 témoin, M4"),
        # ligne entière de l'annexe A3 : les deux états de R1 ont la même médiane arrondie, un contrôle de présence serait ambigu
        ("Durée par question, médiane 4,9 s 11,8 s 11,8 s",
         "Durée par question, médiane " + " ".join(f"{bb['etats'][k]['descriptif']['duree_totale_mediane_ns'] / 1e9:.1f}".replace(".", ",") + " s"
                                                  for k in ("B2_adapte", "R1_adapte", "R1_temoin")), "bout en bout, durées médianes"),
        ("62,8 %", pc(ea3v2t["jeu_v2"]["v2_T"]["recall@5"]) + " %", "famille E, v2-T, jeu v2"),
        ("69,4 %", pc(e3["jeu_v2"]["v3_C"]["recall@5"]) + " %", "famille E, v3-C, jeu v2"),
        ("70,0 %", pc(e3["cdtn"]["v3_C"]["recall@5"]) + " %", "famille E, v3-C, CDTN"),
        ("57,5 %", pc(e3["jeu_v1_test"]["v3_C"]["recall@5"]) + " %", "famille E, v3-C, lot de test"),
    ]
    ecarts = 0
    for ecrit, source, nom in controles:
        # les barres de la diapositive 8 sont écrites dans le script, en nombres décimaux (66.1)
        present = ecrit in texte or (ecrit.endswith(" %") and re.search(r"[\[ ,]" + re.escape(ecrit[:-2].replace(",", ".")) + r"[\],]", gabarit) is not None)
        conforme = source is not None and source == ecrit
        if not (present and conforme):
            ecarts += 1
        print(f"{'OK ' if present and conforme else 'NON'} {ecrit:22s} source : {source!s:22s} ({nom})")
    # données des schémas
    h = donnees["hybride"]
    if (h["rangs"]["dense_base"], h["rangs"]["bm25"], h["rangs"]["fusion"], h["rangs"]["reclasseur"]) != (59, 2, 6, 1):
        ecarts += 1; print("NON rangs de l'exemple hybride")
    tirets = [c for c in gabarit if c in "–—"]
    if tirets:
        ecarts += 1; print(f"NON {len(tirets)} tiret(s) long(s) dans le gabarit")
    print(f"{len(controles)} chiffres contrôlés, {ecarts} écart(s)")
    return 1 if ecarts else 0


if __name__ == "__main__":
    sys.exit(main())
