"""
Tableaux du rapport du notebook 03, générés à partir du fichier de résultats, pour qu'aucun chiffre ne soit recopié
à la main.

Usage, depuis la racine du dépôt :
    python scripts/evaluation/rapport_tableaux.py data/evaluation/notebook03/resultats_mesure.json
"""

import json
import math
import sys


def vide(x):
    """Valeur absente : None ou NaN (l'aléatoire n'a ni intervalle ni niveau fiche)."""
    return x is None or (isinstance(x, float) and math.isnan(x))


def pct(x, d=1):
    """Proportion en pourcentage, virgule décimale ; case vide si la valeur manque."""
    if vide(x):
        return ""
    return f"{100 * x:.{d}f}".replace(".", ",") + " %"


def pts(x, d=1):
    """Écart en points de pourcentage, signé."""
    return f"{100 * x:+.{d}f}".replace(".", ",")


def nb(x, d=3):
    return f"{x:.{d}f}".replace(".", ",")


def p_val(p):
    return "< 0,001" if p < 0.001 else nb(p, 3)


def tableau(entetes, lignes):
    sortie = ["| " + " | ".join(entetes) + " |", "|" + "|".join("---" for _ in entetes) + "|"]
    sortie += ["| " + " | ".join(str(c) for c in l) + " |" for l in lignes]
    return "\n".join(sortie)


def rapport(r):
    blocs = [f"Mode : {r['mode']} ; lot analysé : {r['lot']} ; {r['questions_dans']} questions du corpus, "
             f"{r['questions_hors']} hors corpus."]
    p = r["principale"]
    # intervalle et méthode tels que le notebook les a retenus pour le verdict, sans refaire le choix ici
    ic, meth = p["intervalle_retenu"], p["methode_intervalle"]
    t = p["contingency_table"]
    blocs.append("### Analyse principale\n\n" + tableau(
        ["Écart de Recall@5 (E5 servi moins BM25 V3)", "IC 95 %", "Intervalle", "Paires discordantes",
         "p McNemar", "p groupé (Obuchowski)", "Marge", "Verdict"],
        [[pts(p["difference"]), f"[{pts(ic[0])} ; {pts(ic[1])}]", meth, p["discordant"], p_val(p["p_value"]),
          p_val(p["p_value_groups"]), f"{round(100 * p['marge'])} points", p["verdict"]]])
        + "\n\nTable de contingence : les deux réussissent " + str(t["n_11"]) + ", E5 seul " + str(t["n_10_A_only"])
        + ", BM25 seul " + str(t["n_01_B_only"]) + ", aucun " + str(t["n_00"]) + f" ; {p['n_groups']} fiches.")
    blocs.append("### Métriques par système\n\n" + tableau(
        ["Système", "R@1", "R@3", "R@5", "R@5, IC 95 %", "R@10", "MRR@10", "R@5 fiche"],
        [[m["système"], pct(m["R@1"]), pct(m["R@3"]), pct(m["R@5"]),
          "" if vide(m.get("R@5 IC bas")) else f"{pct(m['R@5 IC bas'])} à {pct(m['R@5 IC haut'])}",
          pct(m["R@10"]), nb(m["MRR@10"]), pct(m.get("R@5 fiche"))]
         for m in r["metriques"]]))
    blocs.append("### Analyses secondaires (Holm par famille)\n\n" + tableau(
        ["Famille", "Comparaison", "Écart", "IC 95 %", "Intervalle", "Discordantes", "p groupé", "p Holm",
         "Significatif"],
        [[s["famille"], s["comparaison"], pts(s["écart"]), f"[{pts(s['IC bas'])} ; {pts(s['IC haut'])}]",
          s["intervalle"], s["discordantes"], p_val(s["p groupé"]), p_val(s["p Holm"]),
          "oui" if s["significatif"] else "non"] for s in r["secondaires"]]))
    a = r.get("abstention")
    if a:
        h, d = a["hors_rejetees"], a["dans_conservees"]
        blocs.append("### Abstention\n\n" + tableau(
            ["AUC", "IC 95 %", "Seuil", "Origine", "Hors corpus rejetées", "Dans le corpus conservées"],
            [[nb(a["auc"]), f"[{nb(a['auc_ic'][0])} ; {nb(a['auc_ic'][1])}]", nb(a["seuil"], 4), a["origine_seuil"],
              f"{h[0]}/{h[1]} ({pct(h[0] / h[1]) if h[1] else '-'})",
              f"{d[0]}/{d[1]} ({pct(d[0] / d[1]) if d[1] else '-'})"]]))
    if r.get("sigles"):
        cles = list(r["sigles"][0])
        blocs.append("### Sigles\n\n" + tableau(cles, [[s[k] for k in cles] for s in r["sigles"]]))
    f = r.get("fidelite_q8")
    if f:
        blocs.append(f"Fidélité des vecteurs du navigateur au fp32 : cosinus minimal {nb(f['cosinus_min'], 4)}, "
                     f"médian {nb(f['cosinus_median'], 4)} (transformers.js {f['transformers_js']}).")
    return "\n\n".join(blocs)


if __name__ == "__main__":
    print(rapport(json.load(open(sys.argv[1], encoding="utf-8"))))
