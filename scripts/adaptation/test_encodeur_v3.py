"""Tests de l'encodeur v3-C (#167, amendement A3), sans modèle ni sous-agent : données et journaux synthétiques.

    python scripts/adaptation/test_encodeur_v3.py
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import tempfile
import time
import unittest
from pathlib import Path

ICI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("encodeur_v3", ICI / "12_encodeur_v3.py")
v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v3)

SONNET, OPUS = v3.MODELE_GENERATEUR, v3.MODELE_RELECTEUR


def horodatage(decalage_ms: int = 0) -> str:
    t = dt.datetime.now(dt.timezone.utc) + dt.timedelta(milliseconds=decalage_ms)
    return t.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def lignes(invite: str, texte: str, modele: str, fichier: Path, agent: str = "a1", debut: str | None = None,
           outils: list[dict] | None = None, modele_requete: str | None = None, remise: bool = True,
           memoire: str = "index", effort: str = "high") -> list[dict]:
    """Journal au format de Claude Code : invite, pièces jointes, requêtes, lecture du fichier, remise du rapport."""
    debut = debut or horodatage(5)
    lecture = {"type": "tool_use", "name": "Read", "input": {"file_path": str(fichier)}}
    rapport = {"type": "tool_use", "name": "SubagentHandback", "input": {"message": texte}}
    blocs = (outils if outils is not None else [lecture]) + ([rapport] if remise else [])
    L = [{"type": "user", "agentId": agent, "timestamp": debut, "message": {"content": invite}},
         {"type": "attachment", "agentId": agent, "attachment": {"type": "instructions", "files": [
             {"path": "MEMORY.md", "type": "AutoMem", "content": memoire}]}},
         {"type": "api-request", "agentId": agent, "shapeHash": "forme",
          "params": {"model": modele_requete or modele, "max_tokens": 64000, "output_config": {"effort": effort}}}]
    for b in blocs:
        L.append({"type": "assistant", "agentId": agent, "message": {"model": modele, "content": [b]}})
    return L


def ecrire_journal(dossier: Path, agent: str, L: list[dict]) -> Path:
    chemin = dossier / "projet" / "session" / "subagents" / f"agent-{agent}.jsonl"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in L), encoding="utf-8")
    return chemin


class Bac(unittest.TestCase):
    """Chaque test travaille dans un dossier temporaire : chemins du module redirigés, dépôt réputé propre."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = Path(self._tmp.name)
        self.t = t
        self._anciens = {k: getattr(v3, k) for k in ("V3", "REGISTRE", "LOTS", "SORTIES_LOTS", "JOURNAUX", "REMIS",
                                                     "REMIS_JUGES", "PROJETS_CLAUDE", "TRAIN", "VALIDATION", "MANIFESTE",
                                                     "RELECTURE", "VERDICTS", "BILAN", "exiger_depot_propre")}
        v3.V3 = t / "v3"
        v3.REGISTRE = t / "v3/registre.jsonl"
        v3.LOTS = t / "v3/lots"
        v3.SORTIES_LOTS = t / "v3/sorties"
        v3.JOURNAUX = t / "v3/journaux"
        v3.REMIS = t / "g3"
        v3.REMIS_JUGES = t / "r3"
        v3.PROJETS_CLAUDE = t / "projets"
        v3.TRAIN = t / "v3/train.jsonl"
        v3.VALIDATION = t / "v3/validation.jsonl"
        v3.MANIFESTE = t / "v3/manifeste.json"
        v3.RELECTURE = t / "v3/relecture_30.json"
        v3.VERDICTS = {1: t / "v3/juge1.json", 2: t / "v3/juge2.json"}
        v3.BILAN = t / "v3/bilan.json"
        v3.exiger_depot_propre = lambda: {"commit": "essai", "sha256_a3": "a", "sha256_script": "s"}
        v3.V3.mkdir()

    def tearDown(self):
        for k, v in self._anciens.items():
            setattr(v3, k, v)
        self._tmp.cleanup()

    def preparer_lots(self, lots: list[list[str]]):
        v3.LOTS.mkdir(parents=True)
        v3.REMIS.mkdir(parents=True)
        man = {"lots": []}
        for k, ids in enumerate(lots):
            contenu = [{"passage_id": i, "titre_fiche": "T", "texte": "texte"} for i in ids]
            sha = v3.ecrire_une_fois(v3.LOTS / v3.nom_lot(k), contenu)
            v3.ecrire_une_fois(v3.REMIS / v3.nom_lot(k), contenu)
            man["lots"].append({"lot": k, "passages": ids, "sha256": sha})
        v3.inscrire("lots", sha256_manifeste_lots=v3.ecrire_une_fois(v3.LOTS / "manifeste_lots.json", man))

    def journal_lot(self, k: int, ids: list[str], agent: str, **options) -> Path:
        texte = json.dumps([{"passage_id": i, "question": f"Question {i} ?"} for i in ids])
        return ecrire_journal(v3.PROJETS_CLAUDE, agent, lignes(v3.invite_lot(k), texte, SONNET, v3.REMIS / v3.nom_lot(k),
                                                               agent=agent, **options))


class TestLots(unittest.TestCase):
    def setUp(self):
        # 2 720 passages sur 194 fiches, dont une de 60 passages, comme la sélection de la v2-T
        tailles = [60] + [14] * 190 + [2720 - 60 - 14 * 190 - 2, 1, 1]
        self.passages = [{"passage_id": f"f{f}p{i}", "fiche": f"f{f}", "partition": "entrainement"}
                         for f, n in enumerate(tailles) for i in range(n)]

    def test_tourniquet_sans_deux_passages_d_une_fiche(self):
        lots = v3.former_lots(self.passages)
        v3.controler_lots(lots, self.passages)
        self.assertEqual(len(lots), 64)
        self.assertEqual(sorted({len(l) for l in lots}), [42, 43])
        self.assertEqual(lots, v3.former_lots(self.passages))            # même graine, mêmes lots

    def test_fiche_trop_grande_refusee(self):
        with self.assertRaises(v3.ErreurV3):
            v3.former_lots(self.passages, nb=59)

    def test_controle_des_lots(self):
        lots = v3.former_lots(self.passages)
        lots[0].append(lots[1][0])
        with self.assertRaises(v3.ErreurV3):
            v3.controler_lots(lots, self.passages)

    def test_controle_du_lot(self):
        ok = [{"passage_id": "a", "question": "Q ?"}, {"passage_id": "b", "question": "R ?"}]
        self.assertEqual(v3.controler_lot(["a", "b"], ok), ok)
        for faux in ([ok[1], ok[0]], ok[:1], ok + [{"passage_id": "c", "question": "S ?"}],
                     [{"passage_id": "a", "question": 3}, ok[1]], [{"passage_id": "a", "question": "Q ?", "x": 1}, ok[1]]):
            with self.assertRaises(v3.ErreurV3):
                v3.controler_lot(["a", "b"], faux)

    def test_tableau_json_et_bloc_de_code(self):
        self.assertEqual(v3.tableau_json('[{"a": 1}]'), [{"a": 1}])
        self.assertEqual(v3.tableau_json('```json\n[{"a": 1}]\n```'), [{"a": 1}])
        for faux in ('Voici : [{"a": 1}]', '{"a": 1}'):                   # aucun texte autour du tableau
            with self.assertRaises(v3.ErreurV3):
                v3.tableau_json(faux)


class TestJournal(Bac):
    def test_journal_conforme(self):
        f = self.t / "lot.json"
        j = ecrire_journal(self.t, "x", lignes("INVITE", "[]", SONNET, f, agent="x"))
        r = v3.controler_journal(j, "INVITE", SONNET, f)
        self.assertEqual((r["agent_id"], r["modele"], r["lectures"], r["rapport"]), ("x", SONNET, 1, "[]"))
        self.assertEqual(r["pieces_jointes"], ["instructions"])

    def test_journaux_refuses(self):
        f = self.t / "lot.json"
        autres = {
            "invite": dict(invite="AUTRE"),
            "modele": dict(modele=OPUS),
            "requete d'un autre modele": dict(modele_requete="claude-fable-5-2"),
            "bash": dict(outils=[{"type": "tool_use", "name": "Read", "input": {"file_path": str(f)}},
                                 {"type": "tool_use", "name": "Bash", "input": {"command": "cat x"}}]),
            "agent": dict(outils=[{"type": "tool_use", "name": "Agent", "input": {}}]),
            "autre fichier": dict(outils=[{"type": "tool_use", "name": "Read", "input": {"file_path": "/autre.json"}}]),
            "outil serveur": dict(outils=[{"type": "server_tool_use", "name": "Read", "input": {"file_path": str(f)}}]),
            "sans lecture": dict(outils=[]),
        }
        for nom, o in autres.items():
            with self.subTest(nom):
                invite = o.pop("invite", "INVITE")
                modele = o.pop("modele", SONNET)
                j = ecrire_journal(self.t, "x", lignes(invite, "[]", modele, f, agent="x", **o))
                with self.assertRaises(v3.ErreurV3):
                    v3.controler_journal(j, "INVITE", SONNET, f)

    def test_deux_remises_ou_remise_avant_la_fin(self):
        f = self.t / "lot.json"
        remise = {"type": "tool_use", "name": "SubagentHandback", "input": {"message": "[]"}}
        lecture = {"type": "tool_use", "name": "Read", "input": {"file_path": str(f)}}
        j = ecrire_journal(self.t, "x", lignes("I", "[]", SONNET, f, agent="x", outils=[lecture, remise]))
        with self.assertRaises(v3.ErreurV3):
            v3.controler_journal(j, "I", SONNET, f)

    def test_deux_agents_refuses(self):
        f = self.t / "lot.json"
        L = lignes("I", "[]", SONNET, f, agent="x")
        L[-1]["agentId"] = "y"
        with self.assertRaises(v3.ErreurV3):
            v3.controler_journal(ecrire_journal(self.t, "x", L), "I", SONNET, f)


class TestRegistre(Bac):
    def test_chainage_et_falsification(self):
        v3.inscrire("a", x=1)
        v3.inscrire("b", x=2)
        self.assertEqual([e["evenement"] for e in v3.lire_registre()], ["a", "b"])
        texte = v3.REGISTRE.read_text(encoding="utf-8").replace('"x": 1', '"x": 3')
        v3.REGISTRE.write_text(texte, encoding="utf-8")
        with self.assertRaises(v3.ErreurV3):
            v3.lire_registre()

    def test_ligne_retiree(self):
        for i in range(3):
            v3.inscrire("e", i=i)
        L = v3.REGISTRE.read_text(encoding="utf-8").splitlines()
        v3.REGISTRE.write_text("\n".join([L[0], L[2]]) + "\n", encoding="utf-8")
        with self.assertRaises(v3.ErreurV3):
            v3.lire_registre()


class TestCycleDesLots(Bac):
    def test_lot_conforme_puis_refus_de_tout_nouvel_appel(self):
        self.preparer_lots([["a", "b"]])
        invite = v3.lancer("lot", 0)
        self.assertEqual(invite, v3.invite_lot(0))
        with self.assertRaises(v3.ErreurV3):
            v3.lancer("lot", 0)                                              # un lancement attend son résultat
        s = v3.ingerer(0, self.journal_lot(0, ["a", "b"], "g1"))
        self.assertEqual([r["question"] for r in s["reponses"]], ["Question a ?", "Question b ?"])
        self.assertTrue((v3.JOURNAUX / "lot_00_t1.jsonl").exists())
        with self.assertRaises(v3.ErreurV3):
            v3.lancer("lot", 0)                                              # déjà conforme

    def test_une_relance_puis_arret(self):
        self.preparer_lots([["a", "b"], ["c"]])
        bash = [{"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]
        v3.lancer("lot", 1)
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(1, self.journal_lot(1, ["c"], "g2", outils=bash))
        r = [e for e in v3.lire_registre() if e["evenement"] == "resultat"]
        self.assertEqual((r[0]["conforme"], r[0]["agent_id"], r[0]["tentative"]), (False, "g2", 1))
        self.assertIn("Bash", r[0]["motif"])
        v3.lancer("lot", 1)                                                  # une relance admise
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(1, self.journal_lot(1, ["c", "d"], "g3"))             # réponse non conforme
        self.assertTrue(any(e["evenement"] == "arret" for e in v3.lire_registre()))
        with self.assertRaises(v3.ErreurV3):
            v3.lancer("lot", 0)                                              # tout est arrêté

    def test_ingestion_sans_lancement_ou_journal_anterieur(self):
        self.preparer_lots([["a"]])
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(0, self.journal_lot(0, ["a"], "g4"))                  # aucun lancement inscrit
        v3.lancer("lot", 0)
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(0, self.journal_lot(0, ["a"], "g5", debut="2026-11-20T10:00:00.000Z"))

    def test_journal_hors_du_dossier_de_claude_refuse(self):
        self.preparer_lots([["a"]])
        v3.lancer("lot", 0)
        faux = self.t / "ailleurs" / "agent-z.jsonl"
        faux.parent.mkdir()
        faux.write_text("{}", encoding="utf-8")
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(0, faux)

    def test_exhaustivite(self):
        self.preparer_lots([["a"]])
        v3.lancer("lot", 0)
        v3.ingerer(0, self.journal_lot(0, ["a"], "g6"))
        v3.exiger_exhaustivite(v3.lire_registre(), "lot")
        self.journal_lot(0, ["a"], "cache")                                  # un appel jamais inscrit
        with self.assertRaises(v3.ErreurV3):
            v3.exiger_exhaustivite(v3.lire_registre(), "lot")
        self.assertTrue(any(e["evenement"] == "arret" for e in v3.lire_registre()))

    def test_lancement_sans_journal(self):
        self.preparer_lots([["a"], ["b"]])
        v3.lancer("lot", 0)
        v3.ingerer(0, self.journal_lot(0, ["a"], "g7"))
        v3.lancer("lot", 1)                                                  # inscrit, jamais lancé
        with self.assertRaises(v3.ErreurV3):
            v3.exiger_exhaustivite(v3.lire_registre(), "lot")

    def test_journal_d_un_autre_lot_refuse_sans_inscription(self):
        # scénario de l'audit : écarter le lot 1 en faisant passer son journal pour celui du lot 0
        self.preparer_lots([["a"], ["b"]])
        v3.lancer("lot", 0)
        v3.lancer("lot", 1)
        j1 = self.journal_lot(1, ["b"], "g8")
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(0, j1)
        self.assertFalse(any(e["evenement"] == "resultat" for e in v3.lire_registre()))
        v3.ingerer(1, j1)
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(0, j1)                                                # agent déjà inscrit
        self.assertEqual(sum(e["evenement"] == "resultat" for e in v3.lire_registre()), 1)

    def test_invite_non_reconnaissable_refusee_sans_inscription(self):
        self.preparer_lots([["a"]])
        v3.lancer("lot", 0)
        f = v3.REMIS / v3.nom_lot(0)
        j = ecrire_journal(v3.PROJETS_CLAUDE, "z1", lignes("Autre invite\n\nFichier : " + str(f), "[]", SONNET, f, agent="z1"))
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(0, j)
        self.assertFalse(any(e["evenement"] == "resultat" for e in v3.lire_registre()))

    def test_agent_en_cours_et_agent_arrete(self):
        self.preparer_lots([["a"]])
        v3.lancer("lot", 0)
        j = self.journal_lot(0, ["a"], "g9", remise=False)
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(0, j)                                                 # en cours : rien n'est inscrit
        self.assertFalse(any(e["evenement"] == "resultat" for e in v3.lire_registre()))
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(0, self.journal_lot(0, ["a"], "g10"), echec=True)    # --echec sur un rapport : refusé
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(0, j, echec=True)                                     # arrêté : inscrit non conforme
        r = [e for e in v3.lire_registre() if e["evenement"] == "resultat"]
        self.assertEqual((len(r), r[0]["conforme"]), (1, False))

    def test_conditions_d_appel_identiques(self):
        self.preparer_lots([["a"], ["b"], ["c"]])
        v3.lancer("lot", 0)
        v3.ingerer(0, self.journal_lot(0, ["a"], "h1"))
        v3.lancer("lot", 1)
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(1, self.journal_lot(1, ["b"], "h2", effort="low"))
        v3.lancer("lot", 2)
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer(2, self.journal_lot(2, ["c"], "h3", memoire="index modifié"))
        motifs = [e["motif"] for e in v3.lire_registre() if e["evenement"] == "resultat" and not e["conforme"]]
        self.assertIn("Paramètres", motifs[0])
        self.assertIn("mémoire", motifs[1])

    def test_verrou_exclusif_entre_processus(self):
        # le cas réel : deux commandes lancées en même temps sont deux processus
        import subprocess
        import sys
        code = ("import importlib.util, sys; from pathlib import Path; "
                f"s = importlib.util.spec_from_file_location('v', {str(ICI / '12_encodeur_v3.py')!r}); "
                "v = importlib.util.module_from_spec(s); s.loader.exec_module(v); "
                f"v.V3 = Path({str(v3.V3)!r})\n"
                "try:\n    with v.verrou(): print('obtenu')\nexcept v.ErreurV3: print('refuse')")
        autre = lambda: subprocess.run([sys.executable, "-c", code], capture_output=True, text=True).stdout.strip()
        with v3.verrou():
            self.assertEqual(autre(), "refuse")
        self.assertEqual(autre(), "obtenu")


class TestJuges(Bac):
    def preparer_relecture(self):
        paires = [{"question": f"Q{i} ?", "passage": f"passage: {i}", "query": f"query: Q{i} ?"} for i in range(40)]
        sha = v3.gen.ecrire_jsonl_une_fois(v3.TRAIN, paires)
        v3.inscrire("assemblage", sha256_manifeste=v3.ecrire_une_fois(v3.MANIFESTE, {"entrainement": {"sha256": sha}}))
        return v3.relecture()

    def journal_juge(self, agent: str, fausses: set[int], indices: list[int]) -> Path:
        texte = json.dumps([{"indice": i, "verdict": "fausse" if i in fausses else "juste", "motif": ""} for i in indices])
        return ecrire_journal(v3.PROJETS_CLAUDE, agent, lignes(v3.invite_juge(), texte, OPUS,
                                                               v3.REMIS_JUGES / v3.FICHIER_JUGES, agent=agent))

    def test_bilan_verdict_le_plus_severe(self):
        idx = self.preparer_relecture()["indices"]
        v3.lancer("juge", 1)
        v3.lancer("juge", 2)
        j1 = self.journal_juge("o1", {idx[0], idx[1]}, idx)
        j2 = self.journal_juge("o2", {idx[1], idx[2]}, idx)
        time.sleep(0.02)
        v3.ingerer_verdicts(1, j1)
        v3.ingerer_verdicts(2, j2)
        b = v3.bilan(ecrire=True)
        self.assertEqual((b["fausses_juge_1"], b["fausses_juge_2"], b["fausses"]), (2, 2, 3))
        self.assertTrue(b["utilisable"])                                    # 3 sur 30 : à la limite, utilisable
        self.assertEqual(b["indices_fausses"], idx[:3])
        self.assertEqual(json.loads(v3.BILAN.read_text(encoding="utf-8"))["fausses"], 3)

    def test_quatre_fausses_arretent_tout(self):
        idx = self.preparer_relecture()["indices"]
        v3.lancer("juge", 1)
        v3.lancer("juge", 2)
        j1 = self.journal_juge("o1", {idx[0], idx[1]}, idx)
        j2 = self.journal_juge("o2", {idx[2], idx[3]}, idx)
        time.sleep(0.02)
        v3.ingerer_verdicts(1, j1)
        v3.ingerer_verdicts(2, j2)
        self.assertFalse(v3.bilan(ecrire=True)["utilisable"])
        self.assertTrue(any(e["evenement"] == "arret" for e in v3.lire_registre()))

    def test_les_deux_juges_lances_avant_toute_ingestion(self):
        idx = self.preparer_relecture()["indices"]
        v3.lancer("juge", 1)
        j1 = self.journal_juge("o1", set(), idx)
        time.sleep(0.02)
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer_verdicts(1, j1)

    def test_un_meme_agent_ne_juge_pas_deux_fois(self):
        idx = self.preparer_relecture()["indices"]
        v3.lancer("juge", 1)
        v3.lancer("juge", 2)
        j = self.journal_juge("o1", set(), idx)
        time.sleep(0.02)
        v3.ingerer_verdicts(1, j)
        with self.assertRaises(v3.ErreurV3):
            v3.ingerer_verdicts(2, j)                                        # refusé sans inscription
        with self.assertRaises(v3.ErreurV3):
            v3.bilan()                                                       # le juge 2 n'a aucun résultat

    def test_juge_lance_apres_l_ingestion_de_l_autre(self):
        idx = self.preparer_relecture()["indices"]
        v3.lancer("juge", 1)
        v3.lancer("juge", 2)
        j1 = self.journal_juge("o1", set(), idx)
        time.sleep(0.02)
        v3.ingerer_verdicts(1, j1)
        time.sleep(0.02)
        j2 = self.journal_juge("o2", set(), idx)                          # commencé après la première ingestion
        time.sleep(0.02)
        v3.ingerer_verdicts(2, j2)
        with self.assertRaises(v3.ErreurV3):
            v3.bilan()


class TestFiltres(unittest.TestCase):
    def test_filtre_du_jeu_v2_et_du_cdtn(self):
        n = v3.gen.normalize_tokens
        jeu_v2 = [n("Mon employeur peut-il refuser mes congés payés pendant l'été ?")]
        cdtn = [n("préavis démission durée")]
        r = v3.filtrer_v3("Mon employeur peut-il refuser mes congés payés pendant l'été ?", [], jeu_v2, cdtn)
        self.assertEqual(r[:2], (None, "jaccard_jeu_v2"))
        r = v3.filtrer_v3("Quelle est la durée du préavis en cas de démission ?", [], jeu_v2, cdtn)
        self.assertEqual(r[:2], (None, "jaccard_cdtn"))
        r = v3.filtrer_v3("Combien de jours de repos compensateur après des heures supplémentaires ?", [], jeu_v2, cdtn)
        self.assertEqual(r[1], "gardee")
        self.assertLessEqual(max(r[3], r[4]), v3.gen.JACCARD_MAX)

    def test_filtres_de_la_v2_d_abord(self):
        r = v3.filtrer_v3("Selon le texte, combien de jours de congés ai-je par an ?", [], [], [])
        self.assertEqual(r, (None, "meta_formulation", None, None, None))


class TestBilanEtRecette(unittest.TestCase):
    def test_kappa(self):
        self.assertAlmostEqual(v3.kappa([True, False, True, False], [True, False, True, False]), 1.0)
        self.assertIsNone(v3.kappa([False] * 4, [False] * 4))

    def test_recette_inchangee(self):
        self.assertEqual(v3.aj.RECETTE, {"num_train_epochs": 2, "per_device_train_batch_size": 16, "learning_rate": 2e-5,
                                         "warmup_ratio": 0.1, "weight_decay": 0.01, "seed": 42})
        self.assertEqual((v3.aj.MODELE_BASE, v3.aj.REVISION_BASE),
                         ("intfloat/multilingual-e5-small", "614241f622f53c4eeff9890bdc4f31cfecc418b3"))

    def test_seuils_inchanges(self):
        self.assertEqual((v3.gen.JACCARD_MAX, v3.gen.PAIRES_MIN, v3.gen.N_RELECTURE, v3.gen.FAUX_MAX), (0.40, 1500, 30, 3))

    def test_consigne_de_la_49_mot_pour_mot(self):
        self.assertTrue(v3.CONSIGNE_G3.endswith(v3.gen.GABARIT))
        self.assertIn("{titre}", v3.CONSIGNE_G3)
        self.assertTrue(v3.invite_lot(3).endswith("\n\nFichier : " + str(v3.REMIS / "lot_03.json")))

    def test_consignes_identiques_a_l_amendement(self):
        texte = v3.AMENDEMENT_A3.read_text(encoding="utf-8")
        for consigne in (v3.CONSIGNE_G3, v3.CONSIGNE_R3):
            bloc = "\n".join("> " + l if l else ">" for l in consigne.split("\n"))
            self.assertTrue(bloc in texte, "consigne absente de A3")
        for valeur in (v3.SHA256_SELECTION, v3.SHA256_JEU_V2, *v3.EMPREINTES_SCRIPTS.values(),
                       *(s for _, s in v3.CDTN.values()), v3.MODELE_GENERATEUR, v3.MODELE_RELECTEUR):
            self.assertTrue(valeur in texte, f"{valeur} absent de A3")


if __name__ == "__main__":
    unittest.main()
