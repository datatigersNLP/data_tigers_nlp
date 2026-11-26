"""Tests de la mesure des contributions : identités, catégories, tickets, lignes conservées, sur un dépôt Git jetable."""

import collections
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import contributions as c


class TestIdentites(unittest.TestCase):
    def test_adresse_noreply_avec_et_sans_numero(self):
        self.assertEqual(c.membre("137395602+mahebegnis@users.noreply.github.com"), "Mahé")
        self.assertEqual(c.membre("jibzzou@users.noreply.github.com"), "Jibril")

    def test_alias_pour_une_autre_adresse(self):
        self.assertEqual(c.membre("x.y@example.org", {"x.y": "remynou"}), "Remy")

    def test_adresse_inconnue_arrete_la_mesure(self):
        with self.assertRaises(ValueError):
            c.membre("inconnu@example.org")

    def test_le_message_d_erreur_ne_recopie_pas_l_adresse(self):
        with self.assertRaises(ValueError) as e:
            c.membre("personne.privee@example.org")
        self.assertNotIn("personne.privee", str(e.exception))


class TestCategories(unittest.TestCase):
    def test_categories(self):
        attendu = {
            "scripts/rag/rag.py": "code", "front/src/App.jsx": "code", "demo_b/index.html": "code",
            "docs/rapport/RAPPORT_FINAL.md": "documentation", "docs/soutenance/8min/deck.html": "documentation",
            "docs/latex/build.py": "code", "scripts/evaluation/03_evaluation.ipynb": "notebooks",
            "front/package-lock.json": "donnees", "scripts/indexation/requirements-lock.txt": "donnees",
            "scripts/rag/requirements.txt": "donnees", "evaluation/cdtn/identifiants.csv": "donnees",
            "docs/etudes/x.json": "donnees", "docs/soutenance/8min/polices/OFL-DM-Sans.txt": "documentation",
            "LICENSE": "autres",
        }
        for chemin, cat in attendu.items():
            self.assertEqual(c.categorie(chemin), cat, chemin)

    def test_un_fichier_dont_le_nom_contient_block_n_est_pas_un_verrou(self):
        self.assertEqual(c.categorie("scripts/block.py"), "code")

    def test_renommage_classe_d_apres_le_chemin_d_arrivee(self):
        self.assertEqual(c.categorie("docs/{ancien.md => nouveau.json}"), "donnees")
        self.assertEqual(c.categorie("scripts/a.py => docs/b.md"), "documentation")


class TestTickets(unittest.TestCase):
    def test_numeros_de_tickets(self):
        tickets = {49, 52, 112}
        self.assertEqual(c.numeros_de_tickets("feat(49): ajustement", tickets), {49})
        self.assertEqual(c.numeros_de_tickets("fix(112): reprise (#52, PR #134)", tickets), {112, 52})
        self.assertEqual(c.numeros_de_tickets("docs: corrections (#134)", tickets), set())  # 134 est une PR, pas un ticket
        self.assertEqual(c.numeros_de_tickets("docs: corrections (#49)", tickets), {49})
        self.assertEqual(c.numeros_de_tickets("chore: sans numéro", tickets), set())

    def test_numero_dans_le_nom_de_branche(self):
        self.assertEqual(c.numeros_de_tickets("Mise à jour", {163}, "feat/163-chaine-v2"), {163})
        self.assertEqual(c.numeros_de_tickets("Mise à jour", {163}, "docs/suivi-charges-20261126"), set())


class TestBlame(unittest.TestCase):
    def test_compter_blame_ignore_les_lignes_vides(self):
        sortie = ("a" * 40 + " 1 1 1\nauthor Z\nauthor-mail <1+mahebegnis@users.noreply.github.com>\nfilename f\n\tx = 1\n"
                  + "b" * 40 + " 2 2 1\nauthor Z\nauthor-mail <1+mahebegnis@users.noreply.github.com>\nfilename f\n\t\n"
                  + "c" * 40 + " 3 3 1\nauthor Z\nauthor-mail <2+jibzzou@users.noreply.github.com>\nfilename f\n\ty = 2\n")
        self.assertEqual(c.compter_blame(sortie), collections.Counter({"Mahé": 1, "Jibril": 1}))


class TestDepotJetable(unittest.TestCase):
    """Un dépôt de deux auteurs, une fusion, un fichier copié à l'identique et un carnet."""

    def commit(self, depot, login, message, fichiers):
        for chemin, contenu in fichiers.items():
            f = Path(depot, chemin)
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(contenu, encoding="utf-8")
        env = {**os.environ, "GIT_AUTHOR_NAME": login, "GIT_AUTHOR_EMAIL": f"1+{login}@users.noreply.github.com",
               "GIT_COMMITTER_NAME": login, "GIT_COMMITTER_EMAIL": f"1+{login}@users.noreply.github.com"}
        subprocess.run(["git", "-C", depot, "add", "-A"], check=True, env=env)
        subprocess.run(["git", "-C", depot, "commit", "-q", "-m", message], check=True, env=env)

    def test_chaine_complete(self):
        with tempfile.TemporaryDirectory() as depot:
            subprocess.run(["git", "-C", depot, "init", "-q", "-b", "dev"], check=True)
            self.commit(depot, "mahebegnis", "feat(7): premier", {"scripts/a.py": "x = 1\n\ny = 2\n", "docs/n.md": "un\ndeux\n"})
            self.commit(depot, "jibzzou", "feat(8): second (#9)",
                        {"scripts/b.py": "x = 1\n\ny = 2\n", "nb.ipynb": '{\n "a": 1\n}\n', "data.json": '{"k": 1}\n'})
            self.commit(depot, "mahebegnis", "docs: sans numéro", {"scripts/a.py": "x = 1\n\ny = 2\nz = 3\n"})
            subprocess.run(["git", "-C", depot, "update-ref", "refs/remotes/origin/dev", "HEAD"], check=True)  # ce qui est sur GitHub
            self.commit(depot, "mahebegnis", "wip: pas encore poussé", {"scripts/local.py": "l = 1\n"})  # local seulement
            stats, touches, vus = c.commits(depot, {}, {7, 8})
            self.assertEqual(len(vus), 3, "un commit qui n'est pas sur GitHub ne compte pas")
            self.assertEqual(stats["Mahé"]["commits"], 2)
            self.assertEqual(stats["Jibril"]["commits"], 1)
            self.assertEqual(stats["Mahé"]["ajouts_code"], 3 + 1)  # trois lignes, puis une ligne ajoutée
            self.assertEqual(stats["Mahé"]["ajouts_documentation"], 2)
            self.assertEqual(stats["Jibril"]["ajouts_notebooks"], 3)
            self.assertEqual(stats["Jibril"]["ajouts_donnees"], 1)
            self.assertEqual(touches["Mahé"], {7})
            self.assertEqual(stats["Mahé"]["sans_ticket"], 1)
            cons = c.lignes_conservees(depot, "origin/dev", {})
            # a.py garde 3 lignes non vides, toutes à Mahé. b.py a le contenu qu'avait a.py avant sa modification : ce n'est
            # pas un doublon exact du fichier actuel, ses 2 lignes non vides sont comptées à Jibril.
            self.assertEqual(cons["code"]["Mahé"], 3)
            self.assertEqual(cons["code"]["Jibril"], 2)
            self.assertEqual(cons["documentation"]["Mahé"], 2)
            self.assertEqual(c.commits_de_la_reference(depot, "origin/dev", {})["Mahé"], 2)

    def test_deux_fichiers_identiques_ne_comptent_qu_une_fois(self):
        with tempfile.TemporaryDirectory() as depot:
            subprocess.run(["git", "-C", depot, "init", "-q", "-b", "dev"], check=True)
            self.commit(depot, "mahebegnis", "feat(1): a", {"scripts/a.py": "x = 1\ny = 2\n"})
            self.commit(depot, "jibzzou", "feat(2): copie", {"scripts/b.py": "x = 1\ny = 2\n"})
            cons = c.lignes_conservees(depot, "dev", {})
            self.assertEqual(cons["code"]["Mahé"], 2)
            self.assertEqual(cons["code"]["Jibril"], 0)


class TestGithub(unittest.TestCase):
    def test_mesures_github(self):
        tickets = [{"number": 1, "state": "CLOSED", "stateReason": "COMPLETED", "author": {"login": "mahebegnis"},
                    "assignees": [{"login": "mahebegnis"}, {"login": "JIBZZOU"}]},
                   {"number": 2, "state": "CLOSED", "stateReason": "NOT_PLANNED", "author": {"login": "jibzzou"}, "assignees": [{"login": "Remynou"}]},
                   {"number": 3, "state": "OPEN", "author": None, "assignees": []}]
        prs = [{"number": 10, "state": "MERGED", "author": {"login": "mahebegnis"},
                "reviews": [{"author": {"login": "mahebegnis"}}, {"author": {"login": "JIBZZOU"}}, {"author": {"login": "copilot-bot"}}, {"author": None}]},
               {"number": 11, "state": "CLOSED", "author": {"login": "jibzzou"}, "reviews": [{"author": {"login": "mahebegnis"}}]}]
        for x in prs:
            x["title"], x["headRefName"] = "feat(1): essai", "feat/2-essai"
        t, touches = c.mesures_github(tickets, prs)
        self.assertEqual(touches["Mahé"], {1, 2})
        self.assertEqual(t["Mahé"]["tickets_assignes"], 1)
        self.assertEqual(t["Mahé"]["tickets_termines"], 1)
        self.assertEqual(t["Remy"]["tickets_abandonnes"], 1)
        self.assertEqual(t["Jibril"]["tickets_crees"], 1)
        self.assertEqual(t["Mahé"]["pr_fusionnees"], 1)
        self.assertEqual(t["Jibril"]["pr_ouvertes"], 1)
        self.assertEqual(t["Jibril"]["pr_fusionnees"], 0)
        self.assertEqual(t["Mahé"]["relectures"], 1)  # son propre commentaire sur la PR 10 ne compte pas
        self.assertEqual(t["Jibril"]["relectures"], 1)


if __name__ == "__main__":
    unittest.main()
