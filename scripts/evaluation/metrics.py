"""
Module de calcul et de validation des métriques de recherche d'information (IR).

Conçu pour le projet NLP 2 (Équipe Data Tigers).
Réutilisable pour la validation PIAF (Issue #45) et l'évaluation sur corpus (Notebook 03 / Issue #46).

Conventions, celles du support sur l'encodeur (docs/etudes/indexation/01_encodeur_e5_small) et du rapport J2 :
- une question a un ou plusieurs passages pertinents. Une question sans passage pertinent (hors corpus) ne s'évalue
  pas ici : elle relève de l'abstention, mesurée à part, et la passer lève une erreur ;
- Recall@k vaut 1 si au moins un passage pertinent figure parmi les k premiers résultats, 0 sinon, en moyenne sur
  les questions. C'est la « top-k accuracy » de DPR (Karpukhin et al., 2020). BEIR appelle Recall@k la part des
  passages pertinents retrouvés : les deux définitions coïncident tant qu'une question n'a qu'un passage pertinent ;
- le rang d'une question est celui de son premier passage pertinent. MRR est la moyenne de 1 / rang, avec 0 quand
  aucun passage pertinent ne figure dans la liste : sur des listes de L résultats, c'est le MRR@L ;
- à score égal, les passages se départagent par leur ordre dans l'index (rank_by_score), pour tous les systèmes.

Métriques implémentées :
- Recall@k (k = 1, 3, 5, 10, ...)
- Reciprocal Rank (RR) & Mean Reciprocal Rank (MRR)
- Intervalle de confiance d'une proportion : Wilson, ou erreur type robuste aux groupes de questions
- Matrice de contingence et test exact de McNemar pour comparaisons appariées, différence appariée et son
  intervalle, test d'Obuchowski quand les questions sont groupées
"""

import math
from typing import List, Dict, Set, Union, Any, Tuple, Optional, Sequence

import numpy as np
from scipy import stats

# collections lues comme plusieurs identifiants pertinents ; tout autre objet est un identifiant
COLLECTIONS = (set, frozenset, list, tuple, np.ndarray)


def _relevant_set(relevant_doc_ids: Any) -> Set[Any]:
    """Ensemble des identifiants pertinents d'une question ; lève ValueError s'il est vide."""
    if isinstance(relevant_doc_ids, np.ndarray):
        target_set = set(relevant_doc_ids.tolist())
    elif isinstance(relevant_doc_ids, COLLECTIONS):
        target_set = set(relevant_doc_ids)
    else:
        target_set = {relevant_doc_ids}
    if not target_set:
        raise ValueError("Question sans passage pertinent : une question hors corpus s'évalue à part (abstention), "
                         "pas dans Recall@k ni MRR.")
    return target_set


def rank_by_score(scores: Sequence[float], depth: Optional[int] = None) -> np.ndarray:
    """
    Indices des passages par score décroissant ; à score égal, par ordre croissant d'indice (tri stable).

    Une règle commune à tous les systèmes comparés : np.argsort(scores)[::-1] range les ex aequo dans l'ordre
    décroissant des indices, et chaque bibliothèque a sa propre règle. Les ex aequo sont fréquents avec BM25.
    """
    order = np.argsort(-np.asarray(scores, dtype=np.float64), kind="stable")
    return order if depth is None else order[:depth]


def first_relevant_rank(
    ranked_doc_ids: Sequence[Any],
    relevant_doc_ids: Union[Set[Any], List[Any], Any]
) -> float:
    """Rang (à partir de 1) du premier document pertinent de la liste, math.inf s'il n'y figure pas."""
    target_set = _relevant_set(relevant_doc_ids)
    for rank, doc_id in enumerate(ranked_doc_ids, start=1):
        if doc_id in target_set:
            return float(rank)
    return math.inf


def recall_at_k(
    ranked_doc_ids: Sequence[Any],
    relevant_doc_ids: Union[Set[Any], List[Any], Any],
    k: int
) -> float:
    """
    Calcule le Recall@k pour une requête unique.

    Vaut 1.0 si au moins un document pertinent figure dans les k premiers résultats, 0.0 sinon (convention de
    l'en-tête du module). relevant_doc_ids est un identifiant, ou une collection d'identifiants (set, frozenset,
    list, tuple, tableau numpy).
    """
    if k <= 0:
        raise ValueError(f"k doit être strictement positif, reçu: {k}")
    return float(first_relevant_rank(ranked_doc_ids, relevant_doc_ids) <= k)


def reciprocal_rank(
    ranked_doc_ids: Sequence[Any],
    relevant_doc_ids: Union[Set[Any], List[Any], Any]
) -> float:
    """
    Calcule le Reciprocal Rank (RR) pour une requête unique.

    Retourne 1 / rang (1-indexé) du premier document pertinent retrouvé.
    Retourne 0.0 si aucun document pertinent n'apparaît dans la liste fournie.
    """
    return 1.0 / first_relevant_rank(ranked_doc_ids, relevant_doc_ids)


def evaluate_retrieval(
    predictions: List[Sequence[Any]],
    ground_truth: List[Union[Set[Any], List[Any], Any]],
    k_values: Tuple[int, ...] = (1, 3, 5, 10)
) -> Dict[str, float]:
    """
    Évalue un ensemble de requêtes et calcule les moyennes globales :
    - Recall@k pour chaque k spécifié
    - MRR (Mean Reciprocal Rank), sur les listes fournies : avec des listes de L résultats, c'est le MRR@L,
      et L est rendu sous la clé "profondeur" (longueur de la plus courte liste)

    Chaque liste doit compter au moins max(k_values) résultats : une liste plus courte fausserait Recall@k sans
    erreur visible.
    """
    if len(predictions) != len(ground_truth):
        raise ValueError(
            f"Taille divergente : {len(predictions)} prédictions vs {len(ground_truth)} vérités terrain."
        )
    n_queries = len(predictions)
    if n_queries == 0:
        raise ValueError("Aucune requête à évaluer.")
    if min(k_values) <= 0:
        raise ValueError(f"k doit être strictement positif, reçu: {k_values}")
    depth = min(len(preds) for preds in predictions)
    if depth < max(k_values):
        raise ValueError(f"Une liste ne compte que {depth} résultats, moins que k = {max(k_values)}.")

    ranks = np.array([first_relevant_rank(preds, gt) for preds, gt in zip(predictions, ground_truth)])
    results: Dict[str, float] = {"n_queries": n_queries, "profondeur": depth}

    # Calcul des Recall@k
    for k in k_values:
        results[f"recall@{k}"] = float(np.mean(ranks <= k))

    # Calcul du MRR (1 / inf = 0 pour les questions dont aucun pertinent n'est dans la liste)
    results["mrr"] = float(np.mean(1.0 / ranks))

    return results


def _clustered_se(residuals: np.ndarray, groups: Sequence[Any]) -> Tuple[float, int]:
    """
    Erreur type d'une moyenne de n valeurs, robuste à la corrélation à l'intérieur des groupes.

    residuals : écarts x_i - moyenne. Estimateur « sandwich » : racine de G / (G - 1) fois la somme, sur les G
    groupes, du carré de la somme des écarts du groupe, divisée par n. Avec un groupe par question, c'est
    l'erreur type usuelle (écart type d'échantillon divisé par racine de n).
    """
    _, inverse = np.unique(np.asarray(groups), return_inverse=True)
    sums = np.bincount(inverse.ravel(), weights=residuals)
    n_groups = len(sums)
    if n_groups < 2:
        raise ValueError("Il faut au moins deux groupes.")
    return math.sqrt(n_groups / (n_groups - 1) * np.sum(sums ** 2)) / len(residuals), n_groups


def _wilson(p: float, n: float, z: float) -> Tuple[float, float]:
    """Intervalle de Wilson d'une proportion p observée sur un effectif n, éventuellement non entier."""
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    demi = z / (1 + z * z / n) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return float(max(0.0, centre - demi)), float(min(1.0, centre + demi))


def proportion_ci(
    successes: Sequence[Union[bool, float]],
    groups: Optional[Sequence[Any]] = None,
    level: float = 0.95,
    method: str = "wald"
) -> Tuple[float, float]:
    """
    Intervalle de confiance d'une proportion de succès (par exemple Recall@5 : un succès par question).

    Sans groupes : intervalle de Wilson, qui suppose les questions indépendantes. Avec groups (une étiquette par
    question : fiche, article, contexte), des questions d'un même groupe se ressemblent, et l'intervalle de Wilson
    serait trop étroit :
    - method="wald" : intervalle de Wald à erreur type robuste aux groupes (celui de la validation sur PIAF) ;
      il peut sortir de [0, 1] quand la proportion est proche d'une borne ou l'effectif petit ;
    - method="wilson" : intervalle de Wilson calculé sur l'effectif corrigé de l'effet de plan,
      n / (variance robuste aux groupes / variance sans groupes), la variance sans groupes valant p(1 - p) / (n - 1).
      Il reste dans [0, 1], et se réduit exactement au Wilson classique quand chaque groupe compte une question.
      Quand p vaut 0 ou 1, l'effet de plan n'est pas défini : on prend le Wilson classique.
    """
    s = np.asarray(successes, dtype=float)
    n, p = len(s), float(s.mean())
    z = stats.norm.ppf(0.5 + level / 2)
    if groups is None or (method == "wilson" and p in (0.0, 1.0)):
        ci = stats.binomtest(int(s.sum()), n).proportion_ci(confidence_level=level, method="wilson")
        return float(ci.low), float(ci.high)
    se, _ = _clustered_se(s - p, groups)
    if method == "wald":
        return float(p - z * se), float(p + z * se)
    if method == "wilson":
        effet_de_plan = se ** 2 / (p * (1 - p) / (n - 1))
        return _wilson(p, n / effet_de_plan, z)
    raise ValueError(f"Méthode inconnue : {method}")


def compute_mcnemar_test(
    preds_a: List[Sequence[Any]],
    preds_b: List[Sequence[Any]],
    ground_truth: List[Union[Set[Any], List[Any], Any]],
    k: int = 5,
    groups: Optional[Sequence[Any]] = None,
    level: float = 0.95
) -> Dict[str, Any]:
    """
    Réalise le test statistique apparié de McNemar sur le Recall@k (succès binaire : top-k contient un pertinent).

    Compare deux systèmes (par ex. E5 Dense vs BM25) sur les mêmes requêtes. Retourne :
    - la table de contingence, la statistique du chi2 avec correction de continuité d'Edwards (1948) et la
      p-valeur du test binomial exact bilatéral ; tous deux supposent les questions indépendantes ;
    - la différence des Recall@k (A - B) et son intervalle de confiance de Wald apparié, à erreur type robuste aux
      groupes si groups est fourni. Il sert au test de non-infériorité : A n'est pas inférieur à B avec la marge
      delta si la borne basse dépasse -delta. Peu fiable quand les paires discordantes se comptent sur les doigts ;
    - si groups est fourni (une étiquette par question), la statistique d'Obuchowski (Statistics in Medicine,
      1998), McNemar pour données groupées : (K - 1) / K fois (somme des D_g) au carré sur la somme des D_g au
      carré, où D_g = (A seul) - (B seul) dans le groupe g, comparée à un chi2 à 1 degré de liberté. Elle pondère
      les questions également, comme Recall@k. C'est alors elle qui décide de significant_5pct.
    """
    if not (len(preds_a) == len(preds_b) == len(ground_truth)):
        raise ValueError("Les longueurs de preds_a, preds_b et ground_truth doivent être identiques.")
    if groups is not None and len(groups) != len(ground_truth):
        raise ValueError("Il faut une étiquette de groupe par question.")

    # 1 si succès à Recall@k, 0 sinon
    success_a = [recall_at_k(p, gt, k) == 1.0 for p, gt in zip(preds_a, ground_truth)]
    success_b = [recall_at_k(p, gt, k) == 1.0 for p, gt in zip(preds_b, ground_truth)]
    return {"k": k, **paired_success_test(success_a, success_b, groups=groups, level=level)}


def _agresti_min(n_10: int, n_01: int, n_total: int, z: float) -> Tuple[float, float]:
    """
    Intervalle d'Agresti et Min (Statistics in Medicine, 2005) pour l'écart de deux proportions appariées : une
    demi-observation est ajoutée à chacune des quatre cases, puis l'intervalle de Wald est calculé sur ces effectifs.
    Il ne dégénère pas quand les paires discordantes sont rares ou absentes, contrairement au Wald ; il suppose les
    questions indépendantes.
    """
    m = n_total + 2
    p10, p01 = (n_10 + 0.5) / m, (n_01 + 0.5) / m
    d = p10 - p01
    se = math.sqrt(max(0.0, (p10 + p01) - d * d) / m)
    return float(d - z * se), float(d + z * se)


def paired_success_test(
    success_a: Sequence[bool],
    success_b: Sequence[bool],
    groups: Optional[Sequence[Any]] = None,
    level: float = 0.95
) -> Dict[str, Any]:
    """
    Cœur du test apparié de compute_mcnemar_test, à partir des succès question par question de deux systèmes.

    Sert quand les deux systèmes n'ont pas la même vérité terrain, par exemple deux découpages dont les passages
    pertinents diffèrent : chaque succès est alors calculé avec la vérité terrain de son propre système. Mêmes
    sorties que compute_mcnemar_test, sans la clé "k".
    """
    if len(success_a) != len(success_b):
        raise ValueError("Les deux vecteurs de succès doivent avoir la même longueur.")
    if groups is not None and len(groups) != len(success_a):
        raise ValueError("Il faut une étiquette de groupe par question.")
    success_a = np.asarray(success_a, dtype=bool)
    success_b = np.asarray(success_b, dtype=bool)

    n_00 = int(np.sum(~success_a & ~success_b))  # Échec A, Échec B
    n_01 = int(np.sum(~success_a & success_b))   # Échec A, Succès B
    n_10 = int(np.sum(success_a & ~success_b))   # Succès A, Échec B
    n_11 = int(np.sum(success_a & success_b))    # Succès A, Succès B
    n_total = len(success_a)

    discordant = n_01 + n_10
    if discordant == 0:
        p_value = 1.0
        statistic = 0.0
    else:
        # Test binomial exact bilatéral (adapté pour petits et grands échantillons)
        res = stats.binomtest(min(n_01, n_10), n=discordant, p=0.5, alternative="two-sided")
        p_value = float(res.pvalue)
        # Chi2 avec correction de continuité de Edwards
        statistic = float(((abs(n_10 - n_01) - 1.0) ** 2) / discordant)

    # Différence appariée et son intervalle ; sans groupes, chaque question forme son propre groupe
    diff = success_a.astype(float) - success_b.astype(float)
    difference = (n_10 - n_01) / n_total
    se, n_groups = _clustered_se(diff - difference, np.arange(n_total) if groups is None else groups)
    z = stats.norm.ppf(0.5 + level / 2)

    result = {
        "n_total": n_total,
        "contingency_table": {
            "n_00": n_00,  # Deux échecs
            "n_10_A_only": n_10,  # A seul réussit
            "n_01_B_only": n_01,  # B seul réussit
            "n_11": n_11,  # Deux réussites
        },
        "discordant": discordant,
        "chi2_statistic": statistic,
        "p_value": p_value,
        "difference": difference,
        "ci_difference": (float(difference - z * se), float(difference + z * se)),
        "ci_difference_agresti_min": _agresti_min(n_10, n_01, n_total, z),
    }
    decision_p = p_value
    if groups is not None:
        _, inverse = np.unique(np.asarray(groups), return_inverse=True)
        d_g = np.bincount(inverse.ravel(), weights=diff)
        denominator = float(np.sum(d_g ** 2))
        chi2_groups = (n_groups - 1) / n_groups * float(d_g.sum()) ** 2 / denominator if denominator > 0 else 0.0
        decision_p = float(stats.chi2.sf(chi2_groups, df=1)) if denominator > 0 else 1.0
        result.update({"n_groups": n_groups, "chi2_obuchowski": chi2_groups, "p_value_groups": decision_p})
    result["significant_5pct"] = bool(decision_p < 0.05)
    return result


def holm(p_values: Sequence[float]) -> List[float]:
    """
    Valeurs p ajustées par la méthode de Holm (1979), dans l'ordre des entrées.

    Triées par ordre croissant, la i-ième (à partir de 0) est multipliée par m - i, puis on impose la monotonie par
    un maximum cumulé, et l'on plafonne à 1. Une hypothèse est rejetée au seuil alpha si sa valeur ajustée est
    inférieure à alpha ; le risque de rejeter à tort au moins une hypothèse de la famille reste alors sous alpha.
    """
    m = len(p_values)
    order = sorted(range(m), key=lambda i: p_values[i])
    adjusted, running = [0.0] * m, 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p_values[i]))
        adjusted[i] = running
    return adjusted


def random_expectations(
    n_relevant: int,
    n_docs: int,
    k_values: Tuple[int, ...] = (1, 3, 5, 10),
    depth: int = 10
) -> Dict[str, float]:
    """
    Espérance exacte de Recall@k et du MRR@depth pour un classement tiré uniformément au hasard, quand une question
    a n_relevant passages pertinents parmi n_docs (loi hypergéométrique).

    Avec q_j la probabilité qu'aucun pertinent ne figure dans les j - 1 premiers rangs,
    q_j = produit pour t de 0 à j - 2 de (N - r - t) / (N - t), le premier pertinent est au rang j avec la
    probabilité q_j * r / (N - j + 1). Recall@k vaut 1 - q_(k+1), et MRR@depth la somme, pour j de 1 à depth, de
    q_j * r / (N - j + 1) / j.
    """
    if not 1 <= n_relevant <= n_docs:
        raise ValueError("Il faut au moins un passage pertinent, et pas plus que de passages.")
    r, n = n_relevant, n_docs
    no_hit = [1.0]   # no_hit[j - 1] = q_j
    for t in range(max(max(k_values), depth) + 1):
        no_hit.append(no_hit[-1] * max(0.0, (n - r - t) / (n - t)) if n - t > 0 else 0.0)
    out = {f"recall@{k}": 1.0 - no_hit[k] for k in k_values}
    out["mrr"] = sum(no_hit[j - 1] * r / (n - j + 1) / j for j in range(1, depth + 1) if n - j + 1 > 0)
    return out


def sanity_check_manual_examples() -> bool:
    """
    Contrôle unitaire strict avec calculs manuels pré-vérifiés.
    Garantit l'absence d'effet d'indexation (off-by-one, inversion, etc.).
    """
    # Exemple 1 : Le document cible "doc_C" est au rang 1
    ranked_1 = ["doc_C", "doc_A", "doc_B", "doc_D"]
    assert recall_at_k(ranked_1, "doc_C", k=1) == 1.0
    assert recall_at_k(ranked_1, "doc_C", k=3) == 1.0
    assert reciprocal_rank(ranked_1, "doc_C") == 1.0

    # Exemple 2 : Le document cible "doc_B" est au rang 3
    ranked_2 = ["doc_X", "doc_Y", "doc_B", "doc_Z"]
    assert recall_at_k(ranked_2, "doc_B", k=1) == 0.0
    assert recall_at_k(ranked_2, "doc_B", k=2) == 0.0
    assert recall_at_k(ranked_2, "doc_B", k=3) == 1.0
    assert recall_at_k(ranked_2, "doc_B", k=5) == 1.0
    assert np.isclose(reciprocal_rank(ranked_2, "doc_B"), 1.0 / 3.0)

    # Exemple 3 : Le document cible "doc_W" n'est pas présent
    ranked_3 = ["doc_1", "doc_2", "doc_3"]
    assert recall_at_k(ranked_3, "doc_W", k=3) == 0.0
    assert reciprocal_rank(ranked_3, "doc_W") == 0.0

    # Évaluation globale sur ces 3 exemples :
    # Req 1 : R@1=1.0, R@3=1.0, RR=1.0
    # Req 2 : R@1=0.0, R@3=1.0, RR=1/3 (~0.333333)
    # Req 3 : R@1=0.0, R@3=0.0, RR=0.0
    # Moyennes attendues :
    # Recall@1 = (1 + 0 + 0) / 3 = 1/3
    # Recall@3 = (1 + 1 + 0) / 3 = 2/3
    # MRR = (1 + 1/3 + 0) / 3 = (4/3) / 3 = 4/9 (~0.444444)
    preds = [ranked_1, ranked_2, ranked_3]
    gt = ["doc_C", "doc_B", "doc_W"]
    res = evaluate_retrieval(preds, gt, k_values=(1, 3))

    assert np.isclose(res["recall@1"], 1.0 / 3.0)
    assert np.isclose(res["recall@3"], 2.0 / 3.0)
    assert np.isclose(res["mrr"], 4.0 / 9.0)
    assert res["profondeur"] == 3

    # Exemple 4 : deux passages pertinents (texte identique), aux rangs 2 et 7 ; un seul suffit
    ranked_4 = ["x", "p1", "y", "z", "w", "v", "p2"]
    assert recall_at_k(ranked_4, {"p1", "p2"}, k=1) == 0.0
    assert recall_at_k(ranked_4, {"p1", "p2"}, k=5) == 1.0
    assert reciprocal_rank(ranked_4, ["p2", "p1"]) == 0.5

    # Exemple 5 : un frozenset ou un tableau numpy est une collection, pas un identifiant
    assert recall_at_k(ranked_4, frozenset({"p1"}), k=2) == 1.0
    assert recall_at_k(ranked_4, np.array(["p1"]), k=2) == 1.0

    # Exemple 6 : entrées qui fausseraient une moyenne sans erreur visible
    invalid_calls = [
        lambda: recall_at_k(ranked_4, set(), k=5),                       # question hors corpus
        lambda: evaluate_retrieval([ranked_3], ["doc_W"], k_values=(5,)),  # 3 résultats pour k = 5
        lambda: evaluate_retrieval([], []),
    ]
    for call in invalid_calls:
        try:
            call()
        except ValueError:
            continue
        raise AssertionError("Une entrée invalide doit lever ValueError.")

    # Exemple 7 : ex aequo départagés par l'ordre de l'index
    assert rank_by_score([0.5, 0.9, 0.5, 0.9]).tolist() == [1, 3, 0, 2]

    # Exemple 8 : intervalle de Wilson, valeur publiée (Newcombe, Statistics in Medicine 1998 : 81 sur 263)
    low, high = proportion_ci([1] * 81 + [0] * 182)
    assert (round(low, 4), round(high, 4)) == (0.2553, 0.3662)

    # Test McNemar sur données synthétiques :
    # A réussit 1 et 2, échoue 3. B réussit 1, échoue 2 et 3.
    # Discordance sur Req 2 (A seul réussit) -> n_10 = 1, n_01 = 0
    mcn = compute_mcnemar_test(preds, [ranked_1, ranked_3, ranked_3], gt, k=3)
    assert mcn["contingency_table"]["n_10_A_only"] == 1
    assert mcn["contingency_table"]["n_01_B_only"] == 0
    # différence 1/3 ; écarts (0, 1, 0) - 1/3, somme des carrés 2/3, erreur type racine(3/2 * 2/3) / 3 = 1/3
    assert np.isclose(mcn["difference"], 1.0 / 3.0)
    assert np.allclose(mcn["ci_difference"], (1.0 / 3.0 - 1.959964 / 3.0, 1.0 / 3.0 + 1.959964 / 3.0))

    # Exemple 9 : six questions en trois groupes de deux, succès A = 1 1 1 0 1 0, B = 0 0 1 1 0 0
    # Sans groupes : A seul 3, B seul 1, différence 2/6. Par groupe, D = (2, -1, 1).
    # Obuchowski : (3 - 1) / 3 * 2² / (4 + 1 + 1) = 4/9.
    # Erreur type robuste : D - 2 * (1/3) = (4/3, -5/3, 1/3), carrés 42/9, fois 3/2 = 7, racine(7) / 6.
    hit, miss = ["ok", "a", "b"], ["a", "b", "c"]
    preds_a = [hit if s else miss for s in (1, 1, 1, 0, 1, 0)]
    preds_b = [hit if s else miss for s in (0, 0, 1, 1, 0, 0)]
    mcn = compute_mcnemar_test(preds_a, preds_b, ["ok"] * 6, k=1, groups=["g1", "g1", "g2", "g2", "g3", "g3"])
    assert (mcn["contingency_table"]["n_10_A_only"], mcn["contingency_table"]["n_01_B_only"]) == (3, 1)
    assert np.isclose(mcn["chi2_obuchowski"], 4.0 / 9.0)
    se = math.sqrt(7.0) / 6.0
    assert np.allclose(mcn["ci_difference"], (1.0 / 3.0 - 1.959964 * se, 1.0 / 3.0 + 1.959964 * se))

    # Exemple 10 : le test sur vecteurs de succès redonne exactement compute_mcnemar_test
    direct = paired_success_test([1, 1, 1, 0, 1, 0], [0, 0, 1, 1, 0, 0], groups=["g1", "g1", "g2", "g2", "g3", "g3"])
    assert {"k": 1, **direct} == mcn

    # Exemple 11 : Holm sur (0,01 ; 0,04 ; 0,03) : triées 0,01 x 3, 0,03 x 2, 0,04 x 1, puis maximum cumulé
    assert np.allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])

    # Exemple 12 : tirage aléatoire, 4 passages
    one = random_expectations(1, 4, k_values=(1, 2))      # un pertinent : k / N, et MRR = (1 + 1/2 + 1/3 + 1/4) / 4
    assert np.allclose([one["recall@1"], one["recall@2"], one["mrr"]], [0.25, 0.5, 25 / 48])
    two = random_expectations(2, 4, k_values=(1, 2))      # deux pertinents : 1/2, 1 - C(2,2)/C(4,2) = 5/6, MRR = 13/18
    assert np.allclose([two["recall@1"], two["recall@2"], two["mrr"]], [0.5, 5 / 6, 13 / 18])
    assert np.isclose(random_expectations(1, 761)["recall@5"], 5 / 761)   # valeur de PIAF

    # Exemple 13 : Wilson à effectif corrigé ; un groupe par question redonne le Wilson classique
    succes = [1] * 81 + [0] * 182
    assert np.allclose(proportion_ci(succes, groups=list(range(263)), method="wilson"), proportion_ci(succes))
    # six questions en trois groupes, succès 1 1 0 0 1 0 : p = 1/2, variance robuste 3/2 * 2 / 36 = 1/12,
    # variance sans groupes 0,25 / 5 = 1/20, effet de plan 5/3, effectif 3,6 ; Wilson(1/2 ; 3,6) = [0,1408 ; 0,8592]
    bas, haut = proportion_ci([1, 1, 0, 0, 1, 0], groups=["g1", "g1", "g2", "g2", "g3", "g3"], method="wilson")
    assert (round(bas, 4), round(haut, 4)) == (0.1408, 0.8592)
    assert proportion_ci([1, 1, 1], groups=["a", "b", "c"], method="wilson") == proportion_ci([1, 1, 1])

    # Exemple 14 : Agresti et Min ; A seul 1, B seul 0, sur 5 questions : effectifs 7, (1,5 - 0,5) / 7 = 1/7,
    # variance (2/7 - 1/49) / 7, intervalle [-0,2387 ; 0,5244] ; sans aucune discordance, il ne dégénère pas
    t = paired_success_test([1, 0, 1, 0, 0], [0, 0, 1, 0, 0])
    assert tuple(round(x, 4) for x in t["ci_difference_agresti_min"]) == (-0.2387, 0.5244)
    assert t["ci_difference"] != t["ci_difference_agresti_min"]
    nul = paired_success_test([1, 0, 1, 0, 0], [1, 0, 1, 0, 0])
    assert nul["ci_difference"] == (0.0, 0.0) and nul["ci_difference_agresti_min"][0] < 0 < nul["ci_difference_agresti_min"][1]

    return True


if __name__ == "__main__":
    if sanity_check_manual_examples():
        print("Sanity checks unitaires validés avec succès (100% conformes aux calculs manuels).")
