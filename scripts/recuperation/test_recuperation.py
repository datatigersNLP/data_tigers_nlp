"""Tests de la récupération v2 (#138), sans modèle et sans question d'évaluation."""

from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recuperation as rc  # noqa: E402
import generation  # noqa: E402
import rag  # noqa: E402

# Empreintes du verrou de la PR #131 (scripts/rag/verrou_mesure.json, écrit le 04/11 à 18:16 UTC).
VERROU_131 = {
    "protocole": "f41366f35c9057c6734489cbfe93fe3d98f17aa9d5eb3d8b507282f7db1b2301",
    "mesure": "d6a4df6a7c1d812abed4f677ca081f4bf40f7c6a10377352e08d127c96215e38",
    "rag": "302dce21a9ce81a67f804016078e7fc2ed2868aaf920693c1b74e19719c7ca9e",
    "generation": "37614842bc9ebbfd3b5f15c6f2d40e4027a11ae9e8b856bbea016db51718b9c7",
    "metrics": "1c9c28f2e0933016b32c1293c50ea1eb2d521bc91f05e69c2a2d4b26cb4f2de4",
    "pertinence": "5acd3aa98b6f035bfddfc724ed187c7dad4842950423a044d5ce2451669151fb",
    "jeu": "807498144fec46722ffab045a87c191b6282a86300799976869d4d6c1755fb35",
    "seuil": "7ba7230e5e8cda87fa1eb8dda2adc01d73c6702d542c27a4e3dc620464939936",
    "index": "2ec45586ab9aaa578f11e271d0ff077c87c105c5de50dcd839e5e9258475b886",
    "passages": "aee5bbdbe401de7506162429912cb5bd54a79132642481a8e7068f12ee99a36d",
}


def passages_factices(n):
    # Documents artificiels : aucun exemple d'évaluation n'est créé.
    return [dict(passage_id=f"fixture-{i}", titre_fiche="Fiche technique", section_titre=f"Section {i % 2}",
                 chemin=[] if i % 2 else ["Intertitre"], url="https://exemple.invalid/fiche",
                 url_citation="https://exemple.invalid/fiche#s", date_maj="2026-01-01", texte=f"Texte {i}.",
                 articles=[]) for i in range(n)]


class FusionTests(unittest.TestCase):
    def test_exemple_calcule_a_la_main(self):
        # 20 : 1/61 + 1/62 ; 10 : 1/61 ; 40 : 1/62 ; 30 : 1/63
        self.assertEqual(rc.fusion_rrf([[10, 20, 30], [20, 40]]), [20, 10, 40, 30])

    def test_rangs_comptes_a_partir_de_un(self):
        # k = 1 : 2 vaut 1/3 + 1/3 = 2/3, 1 et 3 valent 1/2. Avec des rangs comptés à partir de 0, tout vaudrait 1.
        self.assertEqual(rc.fusion_rrf([[1, 2], [3, 2]], k=1), [2, 1, 3])

    def test_ex_aequo_exact(self):
        # 1 et 2 valent tous deux 1/61 + 1/62 : départage par le meilleur rang (1 et 1), puis par l'indice
        self.assertEqual(rc.fusion_rrf([[2, 1], [1, 2]]), [1, 2])

    def test_ex_aequo_departage_par_meilleur_rang(self):
        # x = 1000, 2e dans A seulement : 1/62. y = 5, 64e dans A et dans B : 1/124 + 1/124 = 1/62.
        # Égalité exacte ; x passe devant grâce à son meilleur rang (2 contre 64), bien que son indice soit plus grand.
        a = [100, 1000] + list(range(101, 162)) + [5]
        b = list(range(200, 263)) + [5]
        self.assertEqual((a.index(1000) + 1, a.index(5) + 1, b.index(5) + 1), (2, 64, 64))
        ordre = rc.fusion_rrf([a, b])
        self.assertLess(ordre.index(1000), ordre.index(5))

    def test_doublon_refuse(self):
        with self.assertRaises(rc.ErreurRecuperationV2):
            rc.fusion_rrf([[1, 1]])


class ClassementTests(unittest.TestCase):
    def test_tri_stable_et_positifs(self):
        s = np.array([0.5, 0.0, 0.5, 2.0, -1.0])
        self.assertEqual(rc.classement(s).tolist(), [3, 0, 2, 1, 4])
        self.assertEqual(rc.classement(s, positifs=True).tolist(), [3, 0, 2])

    def test_reclasser(self):
        self.assertEqual(rc.reclasser([7, 8, 9], [0.1, 0.9, 0.9]), [8, 9, 7])
        with self.assertRaises(rc.ErreurRecuperationV2):
            rc.reclasser([7, 8], [0.1])


class VoisinsTests(unittest.TestCase):
    cles = [("f", 0), ("f", 0), ("f", 0), ("f", 1), ("g", 1)]

    def test_voisins_dans_la_section(self):
        self.assertEqual(rc.avec_voisins([1], self.cles), [0, 1, 2])
        self.assertEqual(rc.avec_voisins([3], self.cles), [3])      # sections et fiches différentes autour
        self.assertEqual(rc.avec_voisins([2, 0], self.cles), [1, 2, 0])

    def test_groupes_et_budget(self):
        groupes = rc.groupes_du_contexte([2, 0, 3], self.cles, voisins=True)
        self.assertEqual(groupes, [[1, 2], [0], [3]])
        self.assertEqual(rc.groupes_du_contexte([2, 0], self.cles, voisins=False), [[2], [0]])
        mesurer = lambda indices: 3000 * len(indices)           # 3 passages = 9 000 > 7 616
        self.assertEqual(rc.dans_le_budget([[1], [2], [3]], mesurer), ([1, 2], 1))
        self.assertEqual(rc.dans_le_budget([[1, 2, 3]], mesurer), ([1, 2, 3], 0))   # un groupe est toujours gardé
        juste = lambda indices: rc.PLAFOND_PROMPT if len(indices) <= 2 else rc.PLAFOND_PROMPT + 1
        self.assertEqual(rc.dans_le_budget([[1], [2], [3]], juste), ([1, 2], 1))      # le plafond est inclus

    def test_plafond(self):
        self.assertEqual(rc.PLAFOND_PROMPT, 8192 - 512 - 64)


class ContexteTests(unittest.TestCase):
    def test_identique_a_rag_pour_cinq_passages(self):
        p = passages_factices(7)
        indices = [4, 0, 6, 2, 1]
        resultats = [{"rang": r, "indice": i, "score": 0.0, "passage": p[i]} for r, i in enumerate(indices, 1)]
        attendu = rag.construire_contexte("Question factice ?", resultats)
        obtenu = rc.construire_contexte_v2("Question factice ?", indices, p)
        for cle in ("version_prompt", "system", "prompt", "sources"):
            self.assertEqual(obtenu[cle], attendu[cle], cle)

    def test_texte_brut_accepte_par_generation(self):
        contexte = rc.construire_contexte_v2("Question factice ?", [0, 1], passages_factices(2))
        tok = Mock()
        tok.apply_chat_template.return_value = rc.texte_brut(contexte)
        tok.return_value = {"input_ids": list(range(10))}
        entree = generation.preparer_entree(contexte, "gabarit factice", tok)   # refuse tout autre texte
        self.assertEqual(entree["texte"], rc.texte_brut(contexte))

    def test_doublon_refuse(self):
        with self.assertRaises(rc.ErreurRecuperationV2):
            rc.construire_contexte_v2("Q ?", [0, 0], passages_factices(2))


class ConfigurationTests(unittest.TestCase):
    def test_refus(self):
        for kwargs in ({"k": 0}, {"k": 5, "source": "bm25"}, {"k": 5, "candidats": 20},
                       {"k": 10, "reclasseur": "bge-m3", "candidats": 5}, {"k": 5, "reclasseur": "inconnu", "candidats": 20}):
            with self.assertRaises(rc.ErreurRecuperationV2, msg=str(kwargs)):
                rc.Configuration(**kwargs)

    def test_classement_final(self):
        e5, bm25 = [3, 1, 2, 0], [2, 3]
        self.assertEqual(rc.classement_final(rc.Configuration(k=2), e5, bm25), [3, 1, 2, 0])
        self.assertEqual(rc.classement_final(rc.Configuration(k=2, source="rrf"), e5, bm25)[:2], [3, 2])
        c = rc.Configuration(k=2, reclasseur="bge-m3", candidats=3)
        self.assertEqual(rc.classement_final(c, e5, bm25, {3: 0.1, 1: 0.5, 2: 0.9}), [2, 1, 3])
        with self.assertRaises(rc.ErreurRecuperationV2):
            rc.classement_final(c, e5, bm25, {3: 0.1})


class VerrouTests(unittest.TestCase):
    def test_chaine_verrouillee_inchangee(self):
        """Les dix empreintes du verrou de la #131 sont celles des fichiers de cette branche."""
        import mesure
        try:
            index = rag.charger_index()
        except rag.ErreurIndex as exc:
            self.skipTest(f"index commun indisponible : {exc}")
        self.assertEqual(mesure.empreintes_actuelles(index.entete), VERROU_131)


if __name__ == "__main__":
    unittest.main()
