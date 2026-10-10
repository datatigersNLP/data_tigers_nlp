"""
Audit par simulation des méthodes statistiques du notebook 03, avant la mesure.

N'utilise que la structure du lot de test (nombre de questions du corpus par fiche annotée), jamais un résultat de
système. Reproduit la règle de décision du notebook : intervalle d'Agresti et Min sous 10 paires discordantes,
Wald robuste aux fiches sinon ; critère du J2 satisfait si la borne basse dépasse moins la marge.

Mesure, pour la règle figée et pour le score de Tango corrigé de l'effet de plan (noninferiority_tango) :
1. la puissance du test de non-infériorité quand l'écart réel est nul (protocole, section 6) ;
2. son risque d'erreur quand l'écart réel vaut exactement moins la marge (doit rester près de 2,5 %) ;
3. la couverture de l'intervalle de l'écart, et celle de l'intervalle d'une proportion (Wilson à effectif corrigé).

Deux scénarios de dépendance : questions indépendantes, et questions d'une même fiche qui partagent leur issue
avec une probabilité RHO (corrélation intra-fiche).

Usage : python scripts/evaluation/audit_statistique.py [tirages]
"""

import collections
import csv
import json
import pathlib
import sys

import numpy as np

RACINE = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "scripts" / "evaluation"))
from metrics import noninferiority_tango, paired_success_test, proportion_ci  # noqa: E402

MARGE, DISCORDANCES_MIN, GRAINE, RHO = 0.15, 10, 20261010, 0.5
SORTIE = RACINE / "data" / "evaluation" / "notebook03" / "audit_statistique.json"


def structure_fiches():
    """Taille de chaque fiche du lot de test (questions du corpus), d'après les seules URL annotées."""
    with open(RACINE / "evaluation" / "questions" / "questions_annotees.csv", encoding="utf-8", newline="") as f:
        lignes = [r for r in csv.DictReader(f) if r["lot"] == "test" and r["type"] == "dans_corpus"]
    return sorted(collections.Counter(r["url"] for r in lignes).values(), reverse=True)


def groupes(tailles):
    return np.repeat(np.arange(len(tailles)), tailles)


def tirer_paires(rng, tailles, p10, p01, p11, rho):
    """Succès de A et de B question par question. Chaque question tire l'une des quatre cases (10, 01, 11, 00) ;
    avec la probabilité rho, une question reprend la case de la première question de sa fiche."""
    probas = np.array([p10, p01, p11, 1 - p10 - p01 - p11])
    n = int(np.sum(tailles))
    cases = rng.choice(4, size=n, p=probas)
    if rho > 0:
        debut = np.repeat(np.cumsum([0] + list(tailles[:-1])), tailles)
        copie = rng.random(n) < rho
        cases = np.where(copie, cases[debut], cases)
    a = (cases == 0) | (cases == 2)
    b = (cases == 1) | (cases == 2)
    return a, b


def intervalle_retenu(t):
    if t["discordant"] < DISCORDANCES_MIN:
        return t["ci_difference_agresti_min"], "Agresti et Min"
    return t["ci_difference"], "Wald robuste"


def simuler(rng, tailles, g, delta, discordance, p11, rho, tirages):
    p10, p01 = (discordance + delta) / 2, (discordance - delta) / 2
    satisfait = couvert = agresti = satisfait_t = couvert_t = 0
    for _ in range(tirages):
        a, b = tirer_paires(rng, tailles, p10, p01, p11, rho)
        t = paired_success_test(a, b, groups=g)
        (bas, haut), methode = intervalle_retenu(t)
        satisfait += bas > -MARGE
        couvert += bas <= delta <= haut
        agresti += methode == "Agresti et Min"
        s = noninferiority_tango(a, b, MARGE, groups=g)
        satisfait_t += s["noninferior"]
        couvert_t += s["ci_score"][0] <= delta <= s["ci_score"][1]
    return {"delta": delta, "discordance": discordance, "rho": rho,
            "regle_figee": {"p_critere_satisfait": satisfait / tirages, "couverture_ic95": couvert / tirages,
                            "part_agresti_min": agresti / tirages},
            "tango_effet_de_plan": {"p_critere_satisfait": satisfait_t / tirages,
                                    "couverture_ic95": couvert_t / tirages}}


def taille_obuchowski(rng, tailles, g, discordance, rho, tirages):
    """Rejet à tort, au seuil de 5 %, du test d'Obuchowski groupé (familles F1 à F3) quand l'écart réel est nul."""
    rejets = 0
    for _ in range(tirages):
        a, b = tirer_paires(rng, tailles, discordance / 2, discordance / 2, 0.80 - discordance / 2, rho)
        rejets += paired_success_test(a, b, groups=g)["p_value_groups"] < 0.05
    return {"discordance": discordance, "rho": rho, "rejet_a_tort": rejets / tirages}


def couverture_proportion(rng, tailles, g, p, rho, tirages):
    n, couvert = int(np.sum(tailles)), 0
    for _ in range(tirages):
        s = rng.random(n) < p
        if rho > 0:
            debut = np.repeat(np.cumsum([0] + list(tailles[:-1])), tailles)
            s = np.where(rng.random(n) < rho, s[debut], s)
        bas, haut = proportion_ci(s, groups=g, method="wilson")
        couvert += bas <= p <= haut
    return {"p": p, "rho": rho, "couverture_ic95": couvert / tirages}


def main(tirages):
    tailles = structure_fiches()
    g = groupes(tailles)
    rng = np.random.default_rng(GRAINE)
    resultat = {"questions": int(np.sum(tailles)), "fiches": len(tailles),
                "tailles_fiches": dict(collections.Counter(tailles)), "tirages": tirages, "graine": GRAINE,
                "marge": MARGE, "erreur_monte_carlo_max": 0.5 / np.sqrt(tirages)}
    # p11 : réussites communes ; fixé pour que chaque système réussisse environ 80 % (ordre de grandeur de PIAF)
    scenarios = []
    for rho in (0.0, RHO):
        for disc in (0.14, 0.20, 0.25):
            scenarios.append(simuler(rng, tailles, g, 0.0, disc, 0.80 - disc / 2, rho, tirages))
        for disc in (0.20, 0.25, 0.30):
            scenarios.append(simuler(rng, tailles, g, -MARGE, disc, 0.80 - disc / 2, rho, tirages))
    resultat["test_apparie"] = scenarios
    resultat["obuchowski"] = [taille_obuchowski(rng, tailles, g, d, rho, tirages)
                              for rho in (0.0, RHO) for d in (0.05, 0.14, 0.25)]
    resultat["proportion"] = [couverture_proportion(rng, tailles, g, p, rho, tirages)
                              for rho in (0.0, RHO) for p in (0.6, 0.8, 0.9)]
    SORTIE.write_text(json.dumps(resultat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(resultat, ensure_ascii=False, indent=1))


def sanity_check():
    """Contrôles calculés à la main."""
    rng = np.random.default_rng(0)
    tailles = [3, 2, 1]
    # rho = 1 : toutes les questions d'une fiche ont la même case que la première
    a, b = tirer_paires(rng, tailles, 0.3, 0.3, 0.2, 1.0)
    assert a[0] == a[1] == a[2] and b[0] == b[1] == b[2] and a[3] == a[4] and b[3] == b[4]
    # probabilités des cases retrouvées sur un grand tirage indépendant
    a, b = tirer_paires(np.random.default_rng(1), [1] * 200000, 0.10, 0.05, 0.70, 0.0)
    assert abs(np.mean(a & ~b) - 0.10) < 0.005 and abs(np.mean(~a & b) - 0.05) < 0.005
    assert abs(np.mean(a & b) - 0.70) < 0.005
    assert list(groupes([2, 1])) == [0, 0, 1]
    return True


if __name__ == "__main__":
    assert sanity_check()
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 10000)
