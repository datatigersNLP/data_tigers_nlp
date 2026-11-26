"""Tests du jeu v2 (#171, protocole 10) : contrôles mécaniques et règles de sélection, sur des données construites."""
import csv
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jeu_v2 as j  # noqa: E402

PASSAGE = ("Le salarié a droit à un congé de deux jours et demi ouvrables par mois de travail effectif chez le même "
           "employeur, dans la limite de trente jours ouvrables par an.")
EXTRAIT = "Le salarié a droit à un congé de deux jours et demi ouvrables par mois de travail effectif chez le même employeur"


class TestControleMecanique(unittest.TestCase):
    def test_question_valide(self):
        self.assertEqual(j.controle_mecanique("Combien de jours de repos je gagne chaque mois ?", EXTRAIT, PASSAGE, []), [])

    def test_motifs(self):
        cas = {
            "Selon le texte, combien de jours de repos ?": "renvoi_au_texte",
            "Trop court ?": "longueur",
            "Combien de jours de repos je gagne chaque mois": "point_interrogation",
            "Combien ? de jours de repos je gagne chaque mois ?": "point_interrogation",
        }
        for question, motif in cas.items():
            self.assertIn(motif, j.controle_mecanique(question, EXTRAIT, PASSAGE, []), question)

    def test_fiche_de_paie_toleree(self):
        self.assertEqual(j.controle_mecanique("Dois-je recevoir ma fiche de paie chaque mois ?", EXTRAIT, PASSAGE, []), [])

    def test_extrait_absent_et_proche_du_jeu_v1(self):
        q = "Combien de jours de repos je gagne chaque mois ?"
        self.assertIn("extrait_non_verbatim", j.controle_mecanique(q, "Une phrase absente.", PASSAGE, []))
        self.assertIn("proche_jeu_v1", j.controle_mecanique(q, EXTRAIT, PASSAGE, [q]))


def construire(d: Path, verdict_j, hors_corpus_non: int = 45, decaler: bool = False):
    """Deux fiches, trois candidats chacune ; verdict_j(passage_id) donne le verdict du juge."""
    travail, sortie = d / "travail", d / "sortie"
    for sous in ("lots", "sorties", "juge"):
        (travail / sous).mkdir(parents=True)
    candidats, controles = [], []
    for f in ("https://travail-emploi.gouv.fr/a", "https://travail-emploi.gouv.fr/b"):
        for rang in (1, 2, 3):
            pid = f"{f[-1]}-{rang}"
            candidats.append({"rang": rang, "passage_id": pid, "url": f, "titre_fiche": f[-1], "entete": "", "texte": PASSAGE,
                              "n_tokens": 50})
            controles.append({"passage_id": pid, "question": f"Question {pid} sur mes jours de repos ?", "extrait": EXTRAIT,
                              "rang": rang, "url": f, "motifs_mecaniques": ["proche_jeu_v1"] if pid == "a-1" else []})
    j.ecrire(travail / "candidats.json", candidats)
    j.ecrire(travail / "controles_mecaniques.json", controles)
    acceptables = [c for c in controles if not c["motifs_mecaniques"]]
    feuilles = [acceptables[:3], acceptables[3:]]
    for k, feuille in enumerate(feuilles, start=1):
        j.ecrire(travail / "juge" / f"feuille_j_{k}.json", [{"passage_id": c["passage_id"]} for c in feuille])
        v = [{"passage_id": c["passage_id"], **verdict_j(c["passage_id"])} for c in feuille]
        if decaler and k == 1:
            v.reverse()
        j.ecrire(travail / "sorties" / f"verdicts_j_{k}.json", v)
    hc = [f"Question hors corpus numéro {i} sur la retraite ?" for i in range(60)]
    j.ecrire(travail / "sorties" / "hors_corpus_generateur.json", hc)
    v = [{"question": q, "un_passage_repond": "non" if i < hors_corpus_non else "oui", "passage_id": ""} for i, q in enumerate(hc)]
    j.ecrire(travail / "sorties" / "verdicts_v_1.json", v[:30])
    j.ecrire(travail / "sorties" / "verdicts_v_2.json", v[30:])
    return travail, sortie


def oui(_):
    return {"comprehensible_seule": "oui", "repond": "oui", "extrait_repond": "oui", "motif": ""}


class TestAssembler(unittest.TestCase):
    def assembler(self, d, verdict_j, **k):
        travail, sortie = construire(d, verdict_j, **k)
        with unittest.mock.patch.object(j, "TRAVAIL", travail), unittest.mock.patch.object(j, "SORTIE", sortie):
            res = j.assembler()
            lignes = list(csv.DictReader((sortie / "questions_v2.csv").open(encoding="utf-8")))
        return res, lignes

    def test_deux_premiers_acceptes_par_fiche_dans_l_ordre_des_rangs(self):
        refus = lambda pid: {**oui(pid), "repond": "non"} if pid == "b-1" else oui(pid)
        with tempfile.TemporaryDirectory() as d:
            res, lignes = self.assembler(Path(d), refus)
        corpus = [l["passage_id"] for l in lignes if l["type"] == "dans_corpus"]
        self.assertEqual(corpus, ["a-2", "a-3", "b-2", "b-3"])   # a-1 rejeté mécaniquement, b-1 par le juge
        self.assertEqual(res["dans_corpus"], 4)

    def test_partiel_accepte_mais_pas_extrait_insuffisant(self):
        v = lambda pid: {**oui(pid), "repond": "partiel"} if pid == "a-2" else (
            {**oui(pid), "extrait_repond": "non"} if pid == "a-3" else oui(pid))
        with tempfile.TemporaryDirectory() as d:
            _, lignes = self.assembler(Path(d), v)
        self.assertEqual([l["passage_id"] for l in lignes if l["url"].endswith("/a")], ["a-2"])

    def test_hors_corpus_premieres_retenues_dans_l_ordre(self):
        with tempfile.TemporaryDirectory() as d:
            res, lignes = self.assembler(Path(d), oui)
        hors = [l["question"] for l in lignes if l["type"] == "hors_corpus"]
        self.assertEqual(len(hors), 40)
        # trois candidats acceptés pour la fiche b : seuls les deux premiers rangs sont retenus
        self.assertEqual([l["passage_id"] for l in lignes if l["type"] == "dans_corpus"], ["a-2", "a-3", "b-1", "b-2"])
        self.assertEqual(hors[0], "Question hors corpus numéro 0 sur la retraite ?")
        self.assertEqual([l["id"] for l in lignes][:2], ["V001", "V002"])

    def test_moins_de_trente_hors_corpus_refuse(self):
        with tempfile.TemporaryDirectory() as d, self.assertRaises(j.ErreurJeuV2):
            self.assembler(Path(d), oui, hors_corpus_non=29)

    def test_verdicts_desalignes_refuses(self):
        with tempfile.TemporaryDirectory() as d, self.assertRaises(j.ErreurJeuV2):
            self.assembler(Path(d), oui, decaler=True)


if __name__ == "__main__":
    unittest.main()
