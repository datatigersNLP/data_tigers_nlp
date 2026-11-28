"""Tests de 09_generer_paires_v2.py (#167), sans modèle : python scripts/adaptation/test_generer_paires_v2.py

Les tests sur les vraies données (exclusions, sélection) sont sautés si data/ est absent.
"""

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ICI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("generer_v2", ICI / "09_generer_paires_v2.py")
g = importlib.util.module_from_spec(_spec)
sys.modules["generer_v2"] = g
_spec.loader.exec_module(g)

JEU = [{"question": "Mon employeur peut-il refuser mes congés payés en été ?"}]
JETONS = [g.normalize_tokens(q["question"]) for q in JEU]


class Consigne(unittest.TestCase):
    def test_consigne_identique_a_celle_de_la_49(self):
        source = (ICI / "03_generer_paires_locales.py").read_text(encoding="utf-8")
        m = re.search(r'prompt = f"""(.*?)"""', source, re.S)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1).replace("{texte_passage}", "{texte_passage}"), g.GABARIT)

    def test_options_de_la_49(self):
        source = (ICI / "03_generer_paires_locales.py").read_text(encoding="utf-8")
        for cle, valeur in g.OPTIONS.items():
            self.assertRegex(source, rf'"{cle}":\s*{valeur}\b')

    def test_constantes_du_jeu_identiques_a_mesure(self):
        source = (ICI.parent / "rag/mesure.py").read_text(encoding="utf-8")
        self.assertIn(g.SHA256_JEU, source)
        rag = (ICI.parent / "rag/rag.py").read_text(encoding="utf-8")
        self.assertIn(g.JEU_COMMIT, rag)
        self.assertIn(g.FICHIER_JEU, rag)


class Filtres(unittest.TestCase):
    def test_question_simple_gardee(self):
        q, motif, j = g.filtrer("Quel est le délai de prévenance pour une rupture conventionnelle ?", JETONS)
        self.assertEqual((q, motif), ("Quel est le délai de prévenance pour une rupture conventionnelle ?", "gardee"))

    def test_guillemets_et_premiere_ligne(self):
        q, motif, _ = g.filtrer('"Combien de jours de congé pour un mariage ?"\nRéponse : quatre jours.', JETONS)
        self.assertEqual(q, "Combien de jours de congé pour un mariage ?")

    def test_coupe_apres_le_premier_point_d_interrogation(self):
        q, _, _ = g.filtrer("Combien de jours de congé pour un mariage ? Et pour un pacs.", JETONS)
        self.assertEqual(q, "Combien de jours de congé pour un mariage ?")

    def test_sans_point_d_interrogation(self):
        self.assertEqual(g.filtrer("Le délai de prévenance est de quinze jours.", JETONS)[1], "sans_point_d_interrogation")

    def test_longueurs_limites(self):
        court = "a" * 23 + " ?"           # 25 caractères : gardée
        self.assertEqual(g.filtrer(court, JETONS)[1], "gardee")
        self.assertEqual(g.filtrer("a" * 22 + " ?", JETONS)[1], "longueur")
        long_ = "b" * 218 + " ?"          # 220 caractères : gardée
        self.assertEqual(g.filtrer(long_, JETONS)[1], "gardee")
        self.assertEqual(g.filtrer("b" * 219 + " ?", JETONS)[1], "longueur")

    def test_meta_formulation(self):
        self.assertEqual(g.filtrer("Selon le texte, quel est le délai de préavis ?", JETONS)[1], "meta_formulation")

    def test_jaccard_strictement_au_dessus_de_0_40(self):
        self.assertEqual(g.filtrer("Mon employeur peut-il refuser mes congés payés en été ?", JETONS)[1], "jaccard")
        # 2 mots communs sur 5 distincts : 0,40 exactement, gardée
        jetons = [g.normalize_tokens("alpha beta gamma")]
        q, motif, j = g.filtrer("alpha beta delta epsilon bientôt ?", jetons)
        self.assertAlmostEqual(j, 2 / 6)
        jetons = [g.normalize_tokens("alpha beta gamma delta")]
        q, motif, j = g.filtrer("alpha beta gamma epsilon zeta aaaa ?", jetons)
        self.assertAlmostEqual(j, 3 / 7)
        self.assertEqual(motif, "jaccard")
        jetons = [g.normalize_tokens("alpha beta")]
        q, motif, j = g.filtrer("alpha beta gamma delta eeee ?", jetons)
        self.assertAlmostEqual(j, 0.40)
        self.assertEqual(motif, "gardee")

    def test_renvoi_a_la_source_sans_toucher_aux_termes_du_droit(self):
        rejetees = ["Quels sont les facteurs de risques mentionnés dans la fiche ?",
                    "Quelle situation est considérée comme du harcèlement selon la fiche ?",
                    "Quels documents sont cités dans ce texte en matière de prévention ?",
                    "Quelles aides sont prévues d’après l’extrait pour les apprentis ?",
                    "Quelles obligations sont décrites dans cette fiche pour l'employeur ?"]
        gardees = ["Que doit contenir la fiche de paie remise chaque mois ?",
                   "Que doit-on indiquer dans la fiche de poste d'un salarié ?",
                   "L'employeur peut-il exiger l'extrait de casier judiciaire d'un candidat ?",
                   "Qu'est-ce qui doit figurer dans le document unique d'évaluation des risques ?",
                   "Quand la fiche d'aptitude est-elle remise par le médecin du travail ?"]
        for q in rejetees:
            self.assertEqual(g.filtrer(q, JETONS)[1], "renvoi_a_la_source", q)
        for q in gardees:
            self.assertEqual(g.filtrer(q, JETONS)[1], "gardee", q)

    def test_doublons_a_la_casse_et_aux_espaces_pres(self):
        self.assertEqual(g.cle_doublon("Quel  délai ?"), g.cle_doublon("quel délai ?"))
        self.assertNotEqual(g.cle_doublon("Quel délai ?"), g.cle_doublon("Quels délais ?"))

    def test_url_de_fiche(self):
        self.assertEqual(g.url_fiche("https://travail-emploi.gouv.fr/le-cdd/#section"), "https://travail-emploi.gouv.fr/le-cdd")


class Selection(unittest.TestCase):
    def table(self):
        import pandas as pd
        lignes = []
        for f in range(30):
            for k in range(3):
                lignes.append({"passage_id": f"p{f:02d}-{k}", "url": f"https://x/f{f:02d}#s{k}",
                               "n_tokens": 39 if k == 2 else 100})
        return pd.DataFrame(lignes)

    def test_exclusion_seuil_partition_et_determinisme(self):
        t = self.table()
        exclues = {"https://x/f00", "https://x/f01"}
        old = g.PASSAGES_EXCLUS
        g.PASSAGES_EXCLUS = 6
        try:
            s1 = g.selectionner(t, exclues)
            s2 = g.selectionner(t.sample(frac=1, random_state=3), exclues)
        finally:
            g.PASSAGES_EXCLUS = old
        self.assertEqual(s1, s2)                                    # indépendant de l'ordre de la table
        self.assertEqual(len(s1["passages"]), 28 * 2)               # passages de 39 tokens retirés
        self.assertEqual(s1["fiches"], 28)
        self.assertEqual(len(s1["fiches_validation"]), 3)           # round(2,8)
        self.assertEqual([p["rang"] for p in s1["passages"]], list(range(56)))
        self.assertTrue(all(p["graine"] == g.GRAINE + p["rang"] for p in s1["passages"]))
        val = set(s1["fiches_validation"])
        self.assertTrue(all((p["partition"] == "validation") == (p["fiche"] in val) for p in s1["passages"]))

    def test_nombre_de_passages_exclus_controle(self):
        with self.assertRaises(g.ErreurPaires):
            g.selectionner(self.table(), {"https://x/f00"})


class Reprise(unittest.TestCase):
    def test_reprise_dans_l_ordre_et_assemblage(self):
        import pandas as pd
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            sel = {"sha256_passages": g.SHA256_PASSAGES, "sha256_jeu": g.SHA256_JEU,
                   "passages": [{"rang": r, "passage_id": f"p{r}", "fiche": f"https://x/f{r % 4}",
                                 "graine": g.GRAINE + r, "partition": "validation" if r % 4 == 0 else "entrainement"}
                                for r in range(8)]}
            table = pd.DataFrame([{"passage_id": f"p{r}", "titre_fiche": f"T{r}", "texte": f"texte {r}",
                                   "url": f"https://x/f{r % 4}", "entree_encodeur": f"passage: texte {r}"}
                                  for r in range(8)])
            appels = []

            def appeler(prompt, graine):
                appels.append(graine)
                r = graine - g.GRAINE
                brut = "Pas de question." if r == 3 else ("Quelle est la règle commune ?" if r in (5, 6)
                                                            else f"Quelle est la règle numéro {r} du texte ?")
                return {"brut": brut, "done_reason": "stop", "eval_count": 9}

            olla = {"version": g.VERSION_OLLAMA, "modele": g.MODELE, "digest": g.DIGEST}
            anciens = (g.lire_selection, g.charger_passages, g.lire_jeu, g.SORTIES, g.SELECTION, g.TRAIN,
                       g.VALIDATION, g.MANIFESTE, g.PAIRES_MIN, g.RACINE)
            g.lire_selection = lambda: sel
            g.charger_passages = lambda: table
            g.lire_jeu = lambda: JEU
            g.RACINE = d
            g.SORTIES, g.SELECTION = d, d / "selection.json"
            g.SELECTION.write_text("{}")
            g.TRAIN, g.VALIDATION, g.MANIFESTE = d / "t.jsonl", d / "v.jsonl", d / "m.json"
            g.PAIRES_MIN = 1
            try:
                partiel = d / "partiel.jsonl"
                # première exécution interrompue après 3 passages : on simule en écrivant 3 lignes
                g.generer(appeler=appeler, verifier=lambda: olla, chemin_partiel=partiel)
                lignes = partiel.read_text().splitlines()
                partiel.write_text("\n".join(lignes[:3]) + "\n")
                appels.clear()
                g.generer(appeler=appeler, verifier=lambda: olla, chemin_partiel=partiel)
                self.assertEqual(appels, [g.GRAINE + r for r in range(3, 8)])   # reprise au rang 3
                m = g.assembler(chemin_partiel=partiel)
                self.assertEqual(m["motifs"], {"gardee": 6, "sans_point_d_interrogation": 1, "doublon": 1})
                self.assertEqual(m["paires"], {"entrainement": 4, "validation": 2})
                t = [json.loads(l) for l in g.TRAIN.read_text().splitlines()]
                self.assertEqual([p["passage_id"] for p in t], ["p1", "p2", "p5", "p7"])   # p6 doublon de p5
                self.assertTrue(all(p["query"] == "query: " + p["question"] for p in t))
                with self.assertRaises(FileExistsError):
                    g.assembler(chemin_partiel=partiel)
                # un fichier partiel désordonné est refusé
                lignes = partiel.read_text().splitlines()
                partiel.write_text("\n".join([lignes[1], lignes[0]]) + "\n")
                with self.assertRaises(g.ErreurPaires):
                    g.generer(appeler=appeler, verifier=lambda: olla, chemin_partiel=partiel)
            finally:
                (g.lire_selection, g.charger_passages, g.lire_jeu, g.SORTIES, g.SELECTION, g.TRAIN,
                 g.VALIDATION, g.MANIFESTE, g.PAIRES_MIN, g.RACINE) = anciens


@unittest.skipUnless(g.PASSAGES.is_file(), "data/ absent")
class DonneesReelles(unittest.TestCase):
    def test_exclusions_de_la_49_et_selection(self):
        jeu = g.lire_jeu()
        self.assertEqual(len(jeu), 105)
        ex = g.fiches_exclues(jeu)
        self.assertIn(g.URL_RETIREE_DU_JEU, ex)
        s = g.selectionner(g.charger_passages(), ex)
        self.assertEqual((len(s["passages"]), s["fiches"], len(s["fiches_validation"])), (2720, 194, 19))
        self.assertEqual(s["effectifs"], {"entrainement": 2442, "validation": 278})
        self.assertFalse({p["fiche"] for p in s["passages"]} & ex)


if __name__ == "__main__":
    unittest.main(verbosity=1)
