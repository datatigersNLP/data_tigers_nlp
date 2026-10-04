"""
Module de calcul et de validation des métriques de recherche d'information (IR).

Conçu pour le projet NLP 2 (Équipe Data Tigers).
Réutilisable pour la validation PIAF (Issue #45) et l'évaluation sur corpus (Notebook 03 / Issue #46).

Métriques implémentées :
- Recall@k (k = 1, 3, 5, 10, ...)
- Reciprocal Rank (RR) & Mean Reciprocal Rank (MRR)
- Matrice de contingence et test exact de McNemar pour comparaisons appariées
"""

from typing import List, Dict, Set, Union, Any, Tuple
import numpy as np
from scipy import stats


def recall_at_k(
    ranked_doc_ids: List[Any],
    relevant_doc_ids: Union[Set[Any], List[Any], Any],
    k: int
) -> float:
    """
    Calcule le Recall@k pour une requête unique.
    
    Si relevant_doc_ids est un identifiant unique ou une collection :
    - Retourne la proportion de documents pertinents retrouvés dans les k premiers résultats.
    - Si un seul document pertinent est attendu : vaut 1.0 si le document est dans le top-k, sinon 0.0.
    """
    if k <= 0:
        raise ValueError(f"k doit être strictement positif, reçu: {k}")
    
    if not isinstance(relevant_doc_ids, (set, list, tuple)):
        target_set = {relevant_doc_ids}
    else:
        target_set = set(relevant_doc_ids)
        
    if not target_set:
        return 0.0

    top_k = set(ranked_doc_ids[:k])
    hits = len(top_k.intersection(target_set))
    return float(hits / len(target_set))


def reciprocal_rank(
    ranked_doc_ids: List[Any],
    relevant_doc_ids: Union[Set[Any], List[Any], Any]
) -> float:
    """
    Calcule le Reciprocal Rank (RR) pour une requête unique.
    
    Retourne 1 / rang (1-indexé) du premier document pertinent retrouvé.
    Retourne 0.0 si aucun document pertinent n'apparaît dans la liste fournie.
    """
    if not isinstance(relevant_doc_ids, (set, list, tuple)):
        target_set = {relevant_doc_ids}
    else:
        target_set = set(relevant_doc_ids)

    if not target_set:
        return 0.0

    for rank, doc_id in enumerate(ranked_doc_ids, start=1):
        if doc_id in target_set:
            return 1.0 / rank
    return 0.0


def evaluate_retrieval(
    predictions: List[List[Any]],
    ground_truth: List[Union[Set[Any], List[Any], Any]],
    k_values: Tuple[int, ...] = (1, 3, 5, 10)
) -> Dict[str, float]:
    """
    Évalue un ensemble de requêtes et calcule les moyennes globales :
    - Recall@k pour chaque k spécifié
    - MRR (Mean Reciprocal Rank)
    """
    if len(predictions) != len(ground_truth):
        raise ValueError(
            f"Taille divergente : {len(predictions)} prédictions vs {len(ground_truth)} vérités terrain."
        )
    n_queries = len(predictions)
    if n_queries == 0:
        return {"n_queries": 0}

    results: Dict[str, float] = {"n_queries": float(n_queries)}
    
    # Calcul des Recall@k
    for k in k_values:
        recalls = [
            recall_at_k(preds, gt, k)
            for preds, gt in zip(predictions, ground_truth)
        ]
        results[f"recall@{k}"] = float(np.mean(recalls))

    # Calcul du MRR
    rrs = [
        reciprocal_rank(preds, gt)
        for preds, gt in zip(predictions, ground_truth)
    ]
    results["mrr"] = float(np.mean(rrs))
    
    return results


def compute_mcnemar_test(
    preds_a: List[List[Any]],
    preds_b: List[List[Any]],
    ground_truth: List[Union[Set[Any], List[Any], Any]],
    k: int = 5
) -> Dict[str, Any]:
    """
    Réalise le test statistique apparié de McNemar sur le Recall@k (succès binaire : top-k contient la cible).
    
    Compare deux systèmes (par ex. E5 Dense vs BM25) sur les mêmes requêtes.
    Retourne la table de contingence et la p-valeur exacte binomiale ou du chi2.
    """
    if not (len(preds_a) == len(preds_b) == len(ground_truth)):
        raise ValueError("Les longueurs de preds_a, preds_b et ground_truth doivent être identiques.")

    # 1 si succès à Recall@k, 0 sinon
    success_a = [recall_at_k(p, gt, k) >= 1.0 for p, gt in zip(preds_a, ground_truth)]
    success_b = [recall_at_k(p, gt, k) >= 1.0 for p, gt in zip(preds_b, ground_truth)]

    n_00 = 0  # Échec A, Échec B
    n_01 = 0  # Échec A, Succès B
    n_10 = 0  # Succès A, Échec B
    n_11 = 0  # Succès A, Succès B

    for sa, sb in zip(success_a, success_b):
        if not sa and not sb:
            n_00 += 1
        elif not sa and sb:
            n_01 += 1
        elif sa and not sb:
            n_10 += 1
        else:
            n_11 += 1

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

    return {
        "k": k,
        "n_total": len(ground_truth),
        "contingency_table": {
            "n_00": n_00,  # Deux échecs
            "n_10_A_only": n_10,  # A seul réussit
            "n_01_B_only": n_01,  # B seul réussit
            "n_11": n_11,  # Deux réussites
        },
        "discordant": discordant,
        "chi2_statistic": statistic,
        "p_value": p_value,
        "significant_5pct": bool(p_value < 0.05)
    }


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
    # Req 1 : R@1=1.0, R@3=1.0, R@5=1.0, RR=1.0
    # Req 2 : R@1=0.0, R@3=1.0, R@5=1.0, RR=1/3 (~0.333333)
    # Req 3 : R@1=0.0, R@3=0.0, R@5=0.0, RR=0.0
    # Moyennes attendues :
    # Recall@1 = (1 + 0 + 0) / 3 = 1/3
    # Recall@3 = (1 + 1 + 0) / 3 = 2/3
    # Recall@5 = (1 + 1 + 0) / 3 = 2/3
    # MRR = (1 + 1/3 + 0) / 3 = (4/3) / 3 = 4/9 (~0.444444)
    preds = [ranked_1, ranked_2, ranked_3]
    gt = ["doc_C", "doc_B", "doc_W"]
    res = evaluate_retrieval(preds, gt, k_values=(1, 3, 5))

    assert np.isclose(res["recall@1"], 1.0 / 3.0)
    assert np.isclose(res["recall@3"], 2.0 / 3.0)
    assert np.isclose(res["recall@5"], 2.0 / 3.0)
    assert np.isclose(res["mrr"], 4.0 / 9.0)

    # Test McNemar sur données synthétiques :
    # A réussit 1 et 2, échoue 3. B réussit 1, échoue 2 et 3.
    # Discordance sur Req 2 (A seul réussit) -> n_10 = 1, n_01 = 0
    mcn = compute_mcnemar_test(preds, [ranked_1, ranked_3, ranked_3], gt, k=3)
    assert mcn["contingency_table"]["n_10_A_only"] == 1
    assert mcn["contingency_table"]["n_01_B_only"] == 0

    return True


if __name__ == "__main__":
    if sanity_check_manual_examples():
        print("Sanity checks unitaires validés avec succès (100% conformes aux calculs manuels).")
