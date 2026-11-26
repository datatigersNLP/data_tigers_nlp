"""Encodeur ajusté v3-C (#167, amendement A3) : la recette de la v2-T, avec des questions écrites par Claude Sonnet.

Ce qui change par rapport à la v2-T (amendement A2) est déclaré à la section 8 de A3 : le générateur et ses conditions
d'appel, des lots de passages, un filtre de proximité avec le jeu v2 et le CDTN, une relecture plus stricte et un
nombre de fils de calcul limité. Les fonctions de la v2-T sont réutilisées telles quelles (09, 10, 11 et 06, contrôlés
par empreinte à l'import) ; seuls les chemins, le générateur et la relecture changent.

Chaque appel à un sous-agent est inscrit au registre (data/adaptation/v3/registre.jsonl, en ajout seul, chaque ligne
chaînée à la précédente par son empreinte) avant d'être lancé. Son journal est copié puis contrôlé avant que la
réponse soit lue : invite exacte, modèle exact, aucun outil autre que la lecture du fichier remis et la remise du
rapport. Un lot ou un juge non conforme est inscrit comme tel ; il est relancé une fois au plus, et une seconde
non-conformité arrête tout.

    python scripts/adaptation/12_encodeur_v3.py lots                        # 64 lots, aucun avec deux passages d'une fiche
    python scripts/adaptation/12_encodeur_v3.py lancer --lot 7              # inscrit l'appel, affiche l'invite exacte
    python scripts/adaptation/12_encodeur_v3.py ingerer --lot 7 --journal <.../subagents/agent-....jsonl> [--echec]
    python scripts/adaptation/12_encodeur_v3.py assembler                   # filtres, doublons, paires, manifeste
    python scripts/adaptation/12_encodeur_v3.py relecture                   # tirage des 30 paires à relire
    python scripts/adaptation/12_encodeur_v3.py lancer --juge 1             # puis --juge 2, avant toute ingestion
    python scripts/adaptation/12_encodeur_v3.py verdicts --juge 1 --journal <.../subagents/agent-....jsonl>
    python scripts/adaptation/12_encodeur_v3.py bilan                       # verdict le plus sévère, au plus 3 sur 30
    HF_HUB_OFFLINE=1 nice -n 15 python scripts/adaptation/12_encodeur_v3.py entrainer | valider | exporter | index

Les commandes s'exécutent une à une (verrou exclusif) ; seuls les sous-agents tournent en parallèle. Chaque étape
exige un dépôt propre (scripts et protocoles commités) et consigne le commit et les empreintes de A3 et de ce script ; chaque sortie est écrite une seule fois ; chaque entrée est contrôlée par l'empreinte inscrite au
registre ou au manifeste qui l'a produite.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import importlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[1]


class ErreurV3(RuntimeError):
    """Précondition ou contrôle non rempli : rien n'est écrit, sinon la trace de l'échec au registre."""


def _sha256(octets: bytes) -> str:
    return hashlib.sha256(octets).hexdigest()


# Scripts réutilisés, inchangés depuis l'amendement A2 ; leurs empreintes complètes sont inscrites à A3, section 9.
EMPREINTES_SCRIPTS = {
    "scripts/adaptation/09_generer_paires_v2.py": "98aa305b232be4be270f2d54f8c36b5fdd7ec3d82b3da718a4787e919db44ca1",
    "scripts/adaptation/10_ajuster_encodeur_v2.py": "4c2274bf16cbc50fed0a9975066e93f099183eab41128755954ee435f77b91c7",
    "scripts/adaptation/11_exporter_v2.py": "369fb283881a551d9033095212a9f7e6ae97369655064fe5a5f5716616b0bef1",
    "scripts/adaptation/06_exporter_onnx.py": "3491d0495d286b5135f2b71917d07f9b65306d8db41fe8cf5624598b62adbd7f",
    "scripts/evaluation/ajustement_05.py": "925e800adf1107fdbd7233c94ff3502f3ae83abe1f5798d2cd8716d872f9fb36",
    "scripts/evaluation/ajustement_v2.py": "af1696ee98d681644382e78a3d6ba04986b54361884c0e152c62f1cc5e68ff90",
    "scripts/evaluation/metrics.py": "1c9c28f2e0933016b32c1293c50ea1eb2d521bc91f05e69c2a2d4b26cb4f2de4",
    "scripts/rag/rag.py": "302dce21a9ce81a67f804016078e7fc2ed2868aaf920693c1b74e19719c7ca9e",
}
for _chemin, _attendu in EMPREINTES_SCRIPTS.items():
    if _sha256((RACINE / _chemin).read_bytes()) != _attendu:
        raise ErreurV3(f"{_chemin} différent de celui inscrit à l'amendement A3")


def _module(nom: str, fichier: str):
    spec = importlib.util.spec_from_file_location(nom, ICI / fichier)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


gen = _module("generer_v2", "09_generer_paires_v2.py")      # filtres, doublons, écriture unique, jeu v1
aj = _module("ajuster_v2", "10_ajuster_encodeur_v2.py")      # recette, encodeur, métriques, garde-fou

AMENDEMENT_A3 = RACINE / "docs/etudes/evaluation/05_amendement_A3.md"
V3 = RACINE / "data/adaptation/v3"
REGISTRE = V3 / "registre.jsonl"
SELECTION = gen.SELECTION                                    # la sélection de la v2-T, réutilisée telle quelle
SHA256_SELECTION = "47bc23ceffa13e422713676df821d81bf70ae78bfad84254d590d6737adb952a"
LOTS = V3 / "lots"                                           # archive des lots et leur manifeste
SORTIES_LOTS = V3 / "sorties"
JOURNAUX = V3 / "journaux"                                   # copie de chaque journal de sous-agent, échecs compris
NB_LOTS = 64                                                 # au moins le plus grand nombre de passages d'une fiche (60)
GRAINE_LOTS = 1121
# Dossiers remis aux sous-agents, aux noms neutres et hors du dépôt : chacun ne contient que les fichiers à lire.
REMIS = Path.home() / "NLP2_local/g3"
REMIS_JUGES = Path.home() / "NLP2_local/r3"
FICHIER_JUGES = "paires.json"
# Journaux des sous-agents tenus par Claude Code, tous projets confondus (réglage cleanupPeriodDays : 365 jours)
PROJETS_CLAUDE = Path.home() / ".claude/projects"
TRAIN = V3 / "train_paires_v3.jsonl"
VALIDATION = V3 / "validation_v3.jsonl"
MANIFESTE = V3 / "manifeste_paires_v3.json"
RELECTURE = V3 / "relecture_30.json"
VERDICTS = {1: V3 / "relecture_opus_1.json", 2: V3 / "relecture_opus_2.json"}
BILAN = V3 / "bilan_relecture.json"
GRAINE_RELECTURE = 20261121
DOSSIER_V3 = V3 / "modele"
RAPPORT = V3 / "rapport_entrainement_v3.json"
GARDE_FOU = V3 / "garde_fou_v3.json"
DOSSIER_V2 = gen.SORTIES / "modele"
SHA256_POIDS_V2 = "508868b82a21b6fd769636db254d90173d680188eedcd60ee9e4b8826b322e6c"   # amendement A2, section 9
NAV = RACINE / "data/adaptation/navigateur"
NAV_V3 = NAV / "ajuste_v3"
INDEX_V2 = NAV / "index_ajuste_v2.f32"
SHA256_INDEX_V2 = "1bbdade6b7568f84650167d566b1eeba9f9ca180aef3481683d60bfaa57d06e3"
INDEX_V3 = NAV / "index_ajuste_v3.f32"
FILS = 4                    # fils de calcul du processeur, pour ménager la machine (décision de Mahé du 21/11)
TENTATIVES_MAX = 2          # un lancement, plus une seule relance après une non-conformité
VERSIONS = {"torch": "2.14.0", "transformers": "5.17.0", "sentence_transformers": "6.1.0", "datasets": "5.0.1",
            "accelerate": "1.15.0"}
VERSIONS_EXPORT = {"onnx": "1.23.2", "onnxruntime": "1.30.0"}

# Jeu v2 (protocole 10), lu à son étiquette, et CDTN : leurs questions servent au filtre de proximité de A3
ETIQUETTE_JEU_V2 = "jeu-questions-v2"
FICHIER_JEU_V2 = "evaluation/questions_v2/questions_v2.csv"
SHA256_JEU_V2 = "316d82816e924a8a474653240ce2372e0ec2a85e16870dfd6354f24db521f17f"
CDTN = {"formulations_mesure": (RACINE / "data/evaluation/cdtn/formulations_mesure.json",
                                "164cf7974aafc5b97104acb0628e1a1720d2529c5f002c0041422074a5ddc98c"),
        "questions_cdtn": (RACINE / "data/evaluation/cdtn/questions_cdtn.json",
                           "fea79fbe90b28f6a7cafc554656a660f0635b37f861c93415928cb3ed00f3f45")}

MODELE_GENERATEUR = "claude-sonnet-5-5"     # identifiant exact exigé dans le journal de chaque générateur
MODELE_RELECTEUR = "claude-opus-5-5"        # identifiant exact exigé pour chaque juge

# Consigne G3 (amendement A3, annexe) : l'enveloppe des lots autour de la consigne de la #49, mot pour mot.
CONSIGNE_G3 = ("Lis uniquement le fichier indiqué, et n'ouvre aucun autre fichier : c'est un tableau JSON de passages, "
               "chacun avec passage_id, titre_fiche et texte. Pour chaque passage, dans l'ordre du fichier, applique "
               "la consigne ci-dessous, en remplaçant {titre} par le titre_fiche et {texte_passage} par le texte du "
               "passage. Réponds uniquement par un tableau JSON, un objet par passage, dans l'ordre du fichier, de la "
               "forme {\"passage_id\": \"...\", \"question\": \"...\"}, sans aucun texte avant ni après.\n\n"
               "Consigne :\n\n" + gen.GABARIT)

# Consigne R3 (amendement A3, annexe) : la définition d'une paire fausse de l'amendement A2, section 2.
CONSIGNE_R3 = ("Lis uniquement le fichier indiqué, et n'ouvre aucun autre fichier : il contient 30 paires, chacune avec "
               "un indice, une question et le passage d'où elle a été tirée. Pour chaque paire, dis si elle est juste "
               "ou fausse. Une paire est fausse si la question ne se comprend pas sans le passage (renvoi au texte ou à "
               "la fiche, pronom ou démonstratif sans antécédent), ou si le passage n'y répond pas, même en partie. "
               "Sinon, elle est juste. Réponds uniquement par un tableau JSON, dans l'ordre du fichier, de la forme "
               "{\"indice\": 0, \"verdict\": \"juste\", \"motif\": \"\"}, avec verdict « juste » ou « fausse » et, "
               "pour une paire fausse, un motif d'une phrase ; sans aucun texte avant ni après.")

# Invite complète remise à un sous-agent : la consigne, puis le chemin absolu du fichier (A3, annexe).
SUFFIXE_INVITE = "\n\nFichier : {chemin}"


def invite_lot(k: int) -> str:
    return CONSIGNE_G3 + SUFFIXE_INVITE.format(chemin=REMIS / nom_lot(k))


def invite_juge() -> str:
    return CONSIGNE_R3 + SUFFIXE_INVITE.format(chemin=REMIS_JUGES / FICHIER_JUGES)


sha256_fichier = gen.sha256_fichier
ecrire_une_fois = gen.ecrire_une_fois


def maintenant() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def instant(texte: str) -> dt.datetime:
    return dt.datetime.fromisoformat(texte.replace("Z", "+00:00"))


# ---------------------------------------------------------------------------------------------------------------
# Dépôt, environnement, registre
# ---------------------------------------------------------------------------------------------------------------
def exiger_depot_propre() -> dict:
    """Commit courant et empreintes de A3 et de ce script ; refus si un script ou un protocole n'est pas commité."""
    git = aj.etat_git()
    if not git["propre"]:
        raise ErreurV3("scripts ou protocoles modifiés et non commités : l'amendement A3 doit être figé")
    return {"commit": git["commit"], "sha256_a3": sha256_fichier(AMENDEMENT_A3),
            "sha256_script": sha256_fichier(Path(__file__))}


def exiger_environnement(export: bool = False) -> dict:
    if os.environ.get("HF_HUB_OFFLINE") != "1":
        raise ErreurV3("HF_HUB_OFFLINE=1 exigé : aucun téléchargement n'est admis")
    attendues = {**VERSIONS, **(VERSIONS_EXPORT if export else {})}
    lues = {nom: importlib.import_module(nom).__version__ for nom in attendues}
    if lues != attendues:
        raise ErreurV3(f"Versions différentes de celles de A3, section 3 : {lues}")
    return lues


@contextlib.contextmanager
def verrou():
    """Les commandes du script s'exécutent une à une (A3, section 2) : verrou exclusif, refusé s'il est déjà pris."""
    V3.mkdir(parents=True, exist_ok=True)
    with open(V3 / "registre.verrou", "a") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ErreurV3("Une autre commande du script est en cours : les commandes s'exécutent une à une") from exc
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def lire_registre() -> list[dict]:
    """Événements du registre, après contrôle du chaînage : numéro de ligne et empreinte de la ligne précédente.
    Un registre incohérent arrête tout (A3, section 2) : plus aucune étape ne peut s'exécuter."""
    if not REGISTRE.exists():
        return []
    evenements, precedent = [], None
    for i, ligne in enumerate(REGISTRE.read_text(encoding="utf-8").splitlines()):
        e = json.loads(ligne)
        if e.get("n") != i or e.get("precedent") != precedent:
            raise ErreurV3(f"Registre modifié ou incohérent à la ligne {i}")
        evenements.append(e)
        precedent = _sha256(ligne.encode("utf-8"))
    return evenements


def inscrire(evenement: str, **champs) -> dict:
    evenements = lire_registre()
    precedent = _sha256(REGISTRE.read_text(encoding="utf-8").splitlines()[-1].encode("utf-8")) if evenements else None
    e = {"n": len(evenements), "precedent": precedent, "horodatage": maintenant(), "evenement": evenement, **champs}
    REGISTRE.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRE, "a", encoding="utf-8") as f:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return e


def exiger_pas_d_arret(evenements: list[dict]) -> None:
    arrets = [e for e in evenements if e["evenement"] == "arret"]
    if arrets:
        raise ErreurV3(f"Génération arrêtée (A3, section 2) : {arrets[0]['motif']} ; la v1 reste servie")


def appels(evenements: list[dict], etape: str, cle: int) -> tuple[list[dict], list[dict]]:
    """(lancements, résultats) inscrits pour un lot ou un juge."""
    champ = "lot" if etape == "lot" else "juge"
    lancements = [e for e in evenements if e["evenement"] == "lancement" and e["etape"] == etape and e[champ] == cle]
    resultats = [e for e in evenements if e["evenement"] == "resultat" and e["etape"] == etape and e[champ] == cle]
    return lancements, resultats


def evenement_unique(evenements: list[dict], nom: str) -> dict:
    trouves = [e for e in evenements if e["evenement"] == nom]
    if len(trouves) != 1:
        raise ErreurV3(f"Événement « {nom} » attendu une fois au registre, trouvé {len(trouves)} fois")
    return trouves[0]


# ---------------------------------------------------------------------------------------------------------------
# Journaux des sous-agents
# ---------------------------------------------------------------------------------------------------------------
def lignes_journal(chemin: Path) -> list[dict]:
    return [json.loads(l) for l in Path(chemin).read_text(encoding="utf-8").splitlines() if l.strip()]


def premier_message(L: list[dict]) -> str | None:
    """Invite reçue par le sous-agent : contenu du premier message utilisateur du journal."""
    for l in L:
        if l.get("type") == "user":
            contenu = l.get("message", {}).get("content")
            return contenu if isinstance(contenu, str) else None
    return None


def fichier_de_l_invite(invite: str | None) -> str | None:
    m = re.search(r"\n\nFichier : (.+)\Z", invite or "")
    return m.group(1) if m else None


def agent_du_journal(chemin: Path) -> str | None:
    try:
        ids = {l.get("agentId") for l in lignes_journal(chemin) if l.get("agentId")}
    except (OSError, json.JSONDecodeError):
        return None
    return ids.pop() if len(ids) == 1 else None


def source_journal(journal: Path) -> Path:
    """Chemin réel d'un journal de sous-agent tenu par Claude Code, jamais d'un fichier écrit à la main."""
    source = Path(journal).resolve()
    if source.parent.name != "subagents" or source.parent.parent.parent.parent != PROJETS_CLAUDE.resolve() \
            or not re.fullmatch(r"agent-[0-9a-z]+\.jsonl", source.name):
        raise ErreurV3(f"{journal} n'est pas un journal de sous-agent tenu par Claude Code")
    return source


def copier_journal(journal: Path, nom: str) -> tuple[Path, str]:
    """Copie, avant tout contrôle, du journal et de sa description (.meta.json), dans data/adaptation/v3/journaux."""
    source = source_journal(journal)
    JOURNAUX.mkdir(parents=True, exist_ok=True)
    copie = JOURNAUX / f"{nom}.jsonl"
    with open(source, "rb") as f, open(copie, "xb") as g:
        g.write(f.read())
    meta = source.with_suffix(".meta.json")
    if meta.exists():
        with open(meta, "rb") as f, open(JOURNAUX / f"{nom}.meta.json", "xb") as g:
            g.write(f.read())
    return copie, sha256_fichier(copie)


def controler_journal(chemin: Path, invite: str, modele: str, fichier: Path) -> dict:
    """Contrôles de A3, section 2 : un seul agent ; invite reçue identique à celle inscrite ; un seul modèle, exact, dans
    chaque réponse et chaque requête ; aucun appel d'outil autre que Read du fichier remis et une remise du rapport
    (SubagentHandback), en dernier. Rapporte aussi ce que le harnais a joint au contexte, les paramètres des requêtes et
    l'empreinte de leur forme (invite système et outils), tenue par Claude Code (A3, section 8)."""
    L = lignes_journal(chemin)
    agents = {l.get("agentId") for l in L if l.get("agentId")}
    if len(agents) != 1:
        raise ErreurV3(f"Journal de {len(agents)} agents")
    if not L or L[0].get("type") != "user" or L[0].get("message", {}).get("content") != invite:
        raise ErreurV3("Invite reçue différente de l'invite inscrite")
    reponses = [l for l in L if l.get("type") == "assistant"]
    requetes = [l for l in L if l.get("type") == "api-request"]
    modeles = {l.get("message", {}).get("model") for l in reponses} | {l.get("params", {}).get("model") for l in requetes}
    if not reponses or not requetes or modeles != {modele}:
        raise ErreurV3(f"Modèles du journal {sorted(map(str, modeles))}, et non {modele} seul")
    outils = [b for l in reponses for b in (l["message"].get("content") or [])
              if isinstance(b, dict) and b.get("type") in ("tool_use", "server_tool_use")]
    admis = lambda b: b.get("type") == "tool_use" and (b.get("name") == "SubagentHandback" or (
        b.get("name") == "Read" and b.get("input", {}).get("file_path") == str(fichier)))
    interdits = [b.get("name") for b in outils if not admis(b)]
    if interdits:
        raise ErreurV3(f"Outils non admis : {interdits}")
    remises = [b for b in outils if b.get("name") == "SubagentHandback"]
    if len(remises) != 1 or outils[-1] is not remises[0] or not isinstance(remises[0].get("input", {}).get("message"), str):
        raise ErreurV3("Une seule remise du rapport, en dernier, est attendue")
    lectures = sum(b.get("name") == "Read" for b in outils)
    if lectures < 1:
        raise ErreurV3("Le fichier remis n'a pas été lu")
    pieces = [l["attachment"] for l in L if l.get("type") == "attachment" and isinstance(l.get("attachment"), dict)]
    instructions = [{"chemin": f.get("path"), "type": f.get("type"), "sha256": _sha256(str(f.get("content")).encode("utf-8"))}
                    for p in pieces if p.get("type") == "instructions" for f in p.get("files", [])]
    contexte = [_sha256(json.dumps(p.get("context"), ensure_ascii=False, sort_keys=True).encode("utf-8"))
                for p in pieces if p.get("type") == "session_context"]
    parametres = sorted({json.dumps({k: v for k, v in l.get("params", {}).items() if k != "betas"}, sort_keys=True)
                         for l in requetes})
    return {"agent_id": agents.pop(), "debut": L[0].get("timestamp"), "modele": modele,
            "rapport": remises[0]["input"]["message"], "lectures": lectures, "requetes": len(requetes),
            "pieces_jointes": sorted({str(p.get("type")) for p in pieces}), "instructions": instructions,
            "contexte_session_sha256": contexte, "parametres": [json.loads(p) for p in parametres],
            "formes_de_requete": sorted({str(l.get("shapeHash")) for l in requetes})}


def journaux_par_consigne(consigne: str) -> dict[str, dict]:
    """Tous les journaux de sous-agents, de tous les projets de Claude Code, dont l'invite commence par la consigne :
    par identifiant d'agent, le chemin, le fichier désigné par l'invite et l'heure de début."""
    prefixe, trouves = consigne[:150], {}
    for f in sorted(PROJETS_CLAUDE.glob("*/*/subagents/agent-*.jsonl")):
        with open(f, encoding="utf-8") as h:
            for _, ligne in zip(range(20), h):
                try:
                    x = json.loads(ligne)
                except json.JSONDecodeError:
                    break
                if x.get("type") == "user":
                    contenu = x.get("message", {}).get("content")
                    if isinstance(contenu, str) and contenu.startswith(prefixe):
                        trouves[x.get("agentId")] = {"chemin": f, "fichier": fichier_de_l_invite(contenu),
                                                     "debut": x.get("timestamp")}
                    break
    return trouves


def exiger_exhaustivite(evenements: list[dict], etape: str) -> None:
    """Aucun appel hors du registre (A3, section 2) : chaque journal qui porte la consigne de l'étape a son résultat
    au registre, sous le lot que désigne son invite, et il y a autant de tels journaux que de lancements inscrits.
    Sinon tout s'arrête."""
    consigne = CONSIGNE_G3 if etape == "lot" else CONSIGNE_R3
    trouves = journaux_par_consigne(consigne)
    resultats = [e for e in evenements if e["evenement"] == "resultat" and e["etape"] == etape]
    lancements = [e for e in evenements if e["evenement"] == "lancement" and e["etape"] == etape]
    ecarts = sorted(set(trouves) - {e.get("agent_id") for e in resultats})
    for e in resultats:
        attendu = str(REMIS / nom_lot(e["lot"])) if etape == "lot" else str(REMIS_JUGES / FICHIER_JUGES)
        if e.get("agent_id") not in trouves or trouves[e["agent_id"]]["fichier"] != attendu:
            ecarts.append(f"{etape} {e.get('lot', e.get('juge'))} : {e.get('agent_id')}")
    if ecarts or len(trouves) != len(lancements):
        motif = f"étape « {etape} » : journaux hors registre ou mal attribués {ecarts}, {len(trouves)} journaux pour {len(lancements)} lancements"
        inscrire("arret", motif=motif)
        raise ErreurV3(motif)


def tableau_json(texte: str) -> list:
    """Le tableau JSON du rapport. Seule tolérance : un bloc de code Markdown autour du tableau (déclaré en A3)."""
    t = texte.strip()
    m = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", t, re.S)
    if m:
        t = m.group(1)
    try:
        donnees = json.loads(t)
    except json.JSONDecodeError as exc:
        raise ErreurV3(f"Rapport qui n'est pas un JSON : {exc}") from exc
    if not isinstance(donnees, list):
        raise ErreurV3("Le rapport n'est pas un tableau JSON")
    return donnees


# ---------------------------------------------------------------------------------------------------------------
# Lots
# ---------------------------------------------------------------------------------------------------------------
def lire_selection() -> dict:
    if sha256_fichier(SELECTION) != SHA256_SELECTION:
        raise ErreurV3("selection.json différente de celle de la v2-T")
    return json.loads(SELECTION.read_text(encoding="utf-8"))


def former_lots(passages: list[dict], nb: int = NB_LOTS, graine: int = GRAINE_LOTS) -> list[list[dict]]:
    """Fiches dans un ordre tiré au sort, passages d'une fiche à la suite, puis distribution en tourniquet : comme une
    fiche a au plus nb passages, aucun lot n'en reçoit deux. L'ordre dans chaque lot est ensuite tiré au sort."""
    rng = np.random.default_rng(graine)
    fiches = sorted({p["fiche"] for p in passages})
    par_fiche: dict[str, list] = {}
    for p in passages:
        par_fiche.setdefault(p["fiche"], []).append(p)
    if max(len(v) for v in par_fiche.values()) > nb:
        raise ErreurV3("Une fiche a plus de passages qu'il n'y a de lots")
    file = [p for i in rng.permutation(len(fiches)) for p in par_fiche[fiches[i]]]
    lots = [file[k::nb] for k in range(nb)]
    return [[lot[j] for j in rng.permutation(len(lot))] for lot in lots]


def controler_lots(lots: list[list[dict]], passages: list[dict]) -> None:
    ids = [p["passage_id"] for lot in lots for p in lot]
    if sorted(ids) != sorted(p["passage_id"] for p in passages) or len(set(ids)) != len(ids):
        raise ErreurV3("Les lots ne couvrent pas chaque passage exactement une fois")
    if any(len({p["fiche"] for p in lot}) != len(lot) for lot in lots):
        raise ErreurV3("Un lot contient deux passages d'une même fiche")


def nom_lot(k: int) -> str:
    return f"lot_{k:02d}.json"


def ecrire_lots() -> dict:
    depot = exiger_depot_propre()
    if lire_registre():
        raise ErreurV3("Le registre est déjà commencé : les lots ne sont pas réécrits")
    sel = lire_selection()
    table = gen.charger_passages().set_index("passage_id")
    if LOTS.exists() or REMIS.exists():
        raise ErreurV3(f"{LOTS} ou {REMIS} existe déjà : rien n'est écrasé")
    lots = former_lots(sel["passages"])
    controler_lots(lots, sel["passages"])
    LOTS.mkdir(parents=True)
    REMIS.mkdir(parents=True)
    manifeste = {"amendement": "A3 (#167)", "lots_nombre": NB_LOTS, "graine": GRAINE_LOTS,
                 "sha256_selection": SHA256_SELECTION, "depot": depot, "lots": []}
    for k, lot in enumerate(lots):
        contenu = [{"passage_id": p["passage_id"], "titre_fiche": table.loc[p["passage_id"]].titre_fiche,
                    "texte": table.loc[p["passage_id"]].texte} for p in lot]
        sha = ecrire_une_fois(LOTS / nom_lot(k), contenu)
        if ecrire_une_fois(REMIS / nom_lot(k), contenu) != sha:
            raise ErreurV3(f"Copie remise du lot {k} différente")
        manifeste["lots"].append({"lot": k, "fichier": nom_lot(k), "passages": [p["passage_id"] for p in lot],
                                  "entrainement": sum(p["partition"] == "entrainement" for p in lot), "sha256": sha})
    sha_manifeste = ecrire_une_fois(LOTS / "manifeste_lots.json", manifeste)
    inscrire("lots", depot=depot, sha256_manifeste_lots=sha_manifeste, lots=len(lots),
             tailles=sorted({len(l) for l in lots}), invite_g3_sha256=_sha256(CONSIGNE_G3.encode("utf-8")))
    print(f"{len(lots)} lots de {min(map(len, lots))} à {max(map(len, lots))} passages ; manifeste SHA-256 {sha_manifeste}")
    return manifeste


def lire_manifeste_lots(evenements: list[dict]) -> dict:
    chemin = LOTS / "manifeste_lots.json"
    if sha256_fichier(chemin) != evenement_unique(evenements, "lots")["sha256_manifeste_lots"]:
        raise ErreurV3("Manifeste des lots différent de celui inscrit au registre")
    return json.loads(chemin.read_text(encoding="utf-8"))


def lancer(etape: str, cle: int) -> str:
    """Inscrit le lancement d'un lot ou d'un juge, avant l'appel, et rend l'invite exacte à remettre au sous-agent."""
    depot = exiger_depot_propre()
    evenements = lire_registre()
    exiger_pas_d_arret(evenements)
    if etape == "lot":
        man = lire_manifeste_lots(evenements)
        if not 0 <= cle < len(man["lots"]):
            raise ErreurV3(f"Lot {cle} inconnu")
        invite = invite_lot(cle)
    else:
        evenement_unique(evenements, "relecture")
        if cle not in (1, 2):
            raise ErreurV3(f"Juge {cle} inconnu")
        invite = invite_juge()
    lancements, resultats = appels(evenements, etape, cle)
    if len(lancements) > len(resultats):
        raise ErreurV3(f"{etape} {cle} : un lancement attend encore son résultat")
    if any(r["conforme"] for r in resultats):
        raise ErreurV3(f"{etape} {cle} : déjà conforme, aucun nouvel appel")
    if len(lancements) >= TENTATIVES_MAX:
        raise ErreurV3(f"{etape} {cle} : plus aucune tentative")
    inscrire("lancement", etape=etape, **{"lot" if etape == "lot" else "juge": cle}, tentative=len(lancements) + 1,
             sha256_invite=_sha256(invite.encode("utf-8")), depot=depot)
    return invite


def ingerer_appel(etape: str, cle: int, journal: Path, invite: str, modele: str, fichier: Path, sha_fichier: str,
                  lire_reponse, echec: bool = False) -> tuple[dict, dict]:
    """Copie et contrôle du journal du dernier lancement, lecture de la réponse ; un échec est inscrit au registre, et
    une seconde non-conformité arrête tout. Sont refusés sans rien inscrire, comme erreurs de l'opérateur : un journal
    dont l'invite désigne un autre fichier que celui de ce lot ou de ce juge, un agent déjà inscrit, et un journal sans
    rapport final (agent encore en cours), sauf avec echec=True pour un agent arrêté sans rapport."""
    evenements = lire_registre()
    exiger_pas_d_arret(evenements)
    lancements, resultats = appels(evenements, etape, cle)
    if len(lancements) != len(resultats) + 1:
        raise ErreurV3(f"{etape} {cle} : aucun lancement en attente")
    L = lignes_journal(source_journal(journal))
    recue = premier_message(L)
    consigne = CONSIGNE_G3 if etape == "lot" else CONSIGNE_R3
    if recue is None or not recue.startswith(consigne[:150]) or fichier_de_l_invite(recue) != str(fichier):
        raise ErreurV3("Journal d'un autre lot ou d'une autre étape, ou invite non reconnaissable : rien n'est inscrit")
    agents = {l.get("agentId") for l in L if l.get("agentId")}
    if agents & {e.get("agent_id") for e in evenements if e["evenement"] == "resultat"}:
        raise ErreurV3("Agent déjà inscrit au registre : rien n'est inscrit")
    remis = any(isinstance(b, dict) and b.get("name") == "SubagentHandback" for l in L if l.get("type") == "assistant"
                for b in (l.get("message", {}).get("content") or []))
    if remis == echec:
        raise ErreurV3("Journal sans rapport final : agent en cours ? Rien n'est inscrit (--echec pour un agent arrêté)"
                       if not remis else "--echec refusé : le journal porte un rapport final")
    tentative = len(lancements)
    nom = f"{etape}_{cle:02d}_t{tentative}"
    copie, sha_journal = copier_journal(journal, nom)
    champs = {"etape": etape, "lot" if etape == "lot" else "juge": cle, "tentative": tentative,
              "journal": copie.name, "sha256_journal": sha_journal, "agent_id": agent_du_journal(copie)}
    try:
        j = controler_journal(copie, invite, modele, fichier)
        if instant(j["debut"]) <= instant(lancements[-1]["horodatage"]):
            raise ErreurV3("Journal commencé avant l'inscription de son lancement")
        if sha256_fichier(fichier) != sha_fichier:
            raise ErreurV3("Fichier remis différent de celui inscrit")
        # mêmes conditions d'appel pour tous les appels d'une étape, et index de la mémoire inchangé depuis le premier
        reference = next((e for e in evenements if e["evenement"] == "resultat" and e["etape"] == etape and e["conforme"]), None)
        if reference is not None and reference["parametres"] != j["parametres"]:
            raise ErreurV3(f"Paramètres d'appel différents de ceux du premier appel conforme : {j['parametres']}")
        premier = next((e for e in evenements if e["evenement"] == "resultat" and e["conforme"]), None)
        if premier is not None and premier["instructions"] != j["instructions"]:
            raise ErreurV3("Index de la mémoire modifié depuis le premier appel conforme")
        reponse = lire_reponse(tableau_json(j["rapport"]))
    except ErreurV3 as exc:
        inscrire("resultat", **champs, conforme=False, motif=str(exc))
        if tentative >= TENTATIVES_MAX:
            inscrire("arret", motif=f"{etape} {cle} non conforme deux fois")
        raise
    meta = {k: j[k] for k in ("debut", "modele", "lectures", "requetes", "pieces_jointes", "instructions",
                              "contexte_session_sha256", "parametres", "formes_de_requete")}
    return {**champs, **meta, "sha256_rapport": _sha256(j["rapport"].encode("utf-8"))}, reponse


def controler_lot(attendus: list[str], reponse: list) -> list[dict]:
    if [r.get("passage_id") if isinstance(r, dict) else None for r in reponse] != attendus:
        raise ErreurV3("Passages manquants, en trop ou dans un autre ordre que le lot")
    if any(set(r) != {"passage_id", "question"} or not isinstance(r["question"], str) for r in reponse):
        raise ErreurV3("Objet sans question texte, ou avec d'autres clés que passage_id et question")
    return reponse


def ingerer(k: int, journal: Path, echec: bool = False) -> dict:
    exiger_depot_propre()
    evenements = lire_registre()
    man = lire_manifeste_lots(evenements)
    entree = man["lots"][k]
    champs, reponse = ingerer_appel("lot", k, journal, invite_lot(k), MODELE_GENERATEUR, REMIS / nom_lot(k),
                                    entree["sha256"], lambda r: controler_lot(entree["passages"], r), echec)
    sortie = {"lot": k, **champs, "reponses": reponse}
    sha = ecrire_une_fois(SORTIES_LOTS / nom_lot(k), sortie)
    inscrire("resultat", **champs, conforme=True, sha256_sortie=sha)
    print(f"lot {k} : {len(reponse)} questions de {champs['modele']}, sortie SHA-256 {sha[:12]}")
    return sortie


# ---------------------------------------------------------------------------------------------------------------
# Filtres, doublons, paires
# ---------------------------------------------------------------------------------------------------------------
def lire_jeu_v2() -> list[dict]:
    import csv
    import io
    octets = subprocess.run(["git", "-C", str(RACINE), "show", f"{ETIQUETTE_JEU_V2}:{FICHIER_JEU_V2}"],
                            check=True, capture_output=True).stdout
    if _sha256(octets) != SHA256_JEU_V2:
        raise ErreurV3("Jeu v2 différent de celui étiqueté jeu-questions-v2")
    return list(csv.DictReader(io.StringIO(octets.decode("utf-8"))))


def lire_cdtn() -> list[str]:
    """Textes des formulations du CDTN mesurées (494) et des variantes du seuil (479), sans doublon."""
    textes = []
    for chemin, attendu in CDTN.values():
        if sha256_fichier(chemin) != attendu:
            raise ErreurV3(f"{chemin.name} différent de celui du protocole 10")
        textes += [q["texte"] for q in json.loads(chemin.read_text(encoding="utf-8"))["questions"]]
    return list(dict.fromkeys(textes))


def filtrer_v3(brut: str, jetons_jeu_v1: list[set], jetons_jeu_v2: list[set], jetons_cdtn: list[set]) \
        -> tuple[str | None, str, float | None, float | None, float | None]:
    """Filtres de la v2-T dans le même ordre (09_generer_paires_v2.filtrer), puis ceux de l'amendement A3 : rejet si
    l'indice de Jaccard avec une question du jeu v2, puis avec une formulation du CDTN, dépasse le même seuil (0,40)."""
    question, motif, jmax = gen.filtrer(brut, jetons_jeu_v1)
    if question is None:
        return None, motif, jmax, None, None
    jetons = gen.normalize_tokens(question)
    j2 = max((gen.jaccard_overlap(jetons, t) for t in jetons_jeu_v2), default=0.0)
    if j2 > gen.JACCARD_MAX:
        return None, "jaccard_jeu_v2", jmax, j2, None
    jc = max((gen.jaccard_overlap(jetons, t) for t in jetons_cdtn), default=0.0)
    if jc > gen.JACCARD_MAX:
        return None, "jaccard_cdtn", jmax, j2, jc
    return question, "gardee", jmax, j2, jc


def assembler() -> dict:
    depot = exiger_depot_propre()
    evenements = lire_registre()
    exiger_pas_d_arret(evenements)
    man = lire_manifeste_lots(evenements)
    conformes = {e["lot"]: e for e in evenements if e["evenement"] == "resultat" and e["etape"] == "lot" and e["conforme"]}
    if sorted(conformes) != list(range(len(man["lots"]))):
        raise ErreurV3(f"Lots sans résultat conforme : {sorted(set(range(len(man['lots']))) - set(conformes))}")
    exiger_exhaustivite(evenements, "lot")
    reponses = {}
    for k in range(len(man["lots"])):
        chemin = SORTIES_LOTS / nom_lot(k)
        if sha256_fichier(chemin) != conformes[k]["sha256_sortie"]:
            raise ErreurV3(f"Sortie du lot {k} différente de celle inscrite au registre")
        reponses.update({r["passage_id"]: r["question"] for r in json.loads(chemin.read_text(encoding="utf-8"))["reponses"]})
    sel = lire_selection()
    if sorted(reponses) != sorted(p["passage_id"] for p in sel["passages"]):
        raise ErreurV3("Questions manquantes ou en trop")
    table = gen.charger_passages().set_index("passage_id")
    jetons_v1 = [gen.normalize_tokens(q["question"]) for q in gen.lire_jeu()]
    jetons_v2 = [gen.normalize_tokens(q["question"]) for q in lire_jeu_v2()]
    jetons_cdtn = [gen.normalize_tokens(t) for t in lire_cdtn()]
    vues, sortie, motifs = set(), {"entrainement": [], "validation": []}, {}
    for p in sel["passages"]:                       # ordre de la sélection : la première occurrence d'un doublon gagne
        question, motif, jmax, j2, jc = filtrer_v3(reponses[p["passage_id"]], jetons_v1, jetons_v2, jetons_cdtn)
        if motif == "gardee":
            cle = gen.cle_doublon(question)
            if cle in vues:
                motif = "doublon"
            else:
                vues.add(cle)
                t = table.loc[p["passage_id"]]
                sortie[p["partition"]].append({
                    "passage_id": p["passage_id"], "url": t.url, "titre_fiche": t.titre_fiche, "question": question,
                    "query": f"query: {question}", "passage": t.entree_encodeur, "max_jaccard_jeu": round(jmax, 4),
                    "max_jaccard_jeu_v2": round(j2, 4), "max_jaccard_cdtn": round(jc, 4)})
        motifs[motif] = motifs.get(motif, 0) + 1
    if len(sortie["entrainement"]) < gen.PAIRES_MIN:
        inscrire("arret", motif=f"{len(sortie['entrainement'])} paires d'entraînement, moins que {gen.PAIRES_MIN}")
        raise ErreurV3(f"{len(sortie['entrainement'])} paires d'entraînement, moins que {gen.PAIRES_MIN}")
    manifeste = {
        "amendement": "A3 (#167)", "ecrit_le": maintenant(), "depot": depot,
        "selection": {"fichier": str(SELECTION.relative_to(RACINE)), "sha256": SHA256_SELECTION},
        "lots": {"manifeste": sha256_fichier(LOTS / "manifeste_lots.json"),
                 "sorties": {nom_lot(k): conformes[k]["sha256_sortie"] for k in sorted(conformes)},
                 "relances": sum(e["evenement"] == "lancement" and e["etape"] == "lot" and e["tentative"] > 1
                                 for e in evenements)},
        "generateur": {"modele": MODELE_GENERATEUR, "outil": "sous-agents general-purpose de Claude Code (outil Agent)",
                       "agents": {str(k): conformes[k]["agent_id"] for k in sorted(conformes)},
                       "consigne_sha256": _sha256(CONSIGNE_G3.encode("utf-8"))},
        "motifs": motifs, "paires": {k: len(v) for k, v in sortie.items()},
        "fiches": {k: len({p["url"] for p in v}) for k, v in sortie.items()},
        "sha256_registre": sha256_fichier(REGISTRE),
    }
    manifeste["entrainement"] = {"fichier": str(TRAIN.relative_to(RACINE)),
                                 "sha256": gen.ecrire_jsonl_une_fois(TRAIN, sortie["entrainement"])}
    manifeste["validation"] = {"fichier": str(VALIDATION.relative_to(RACINE)),
                               "sha256": gen.ecrire_jsonl_une_fois(VALIDATION, sortie["validation"])}
    sha = ecrire_une_fois(MANIFESTE, manifeste)
    inscrire("assemblage", depot=depot, sha256_manifeste=sha, paires=manifeste["paires"], motifs=motifs)
    print(json.dumps({k: v for k, v in manifeste.items() if k != "generateur"}, ensure_ascii=False, indent=1))
    return manifeste


# ---------------------------------------------------------------------------------------------------------------
# Relecture par deux juges Opus, à l'aveugle
# ---------------------------------------------------------------------------------------------------------------
def lire_manifeste(evenements: list[dict]) -> dict:
    if sha256_fichier(MANIFESTE) != evenement_unique(evenements, "assemblage")["sha256_manifeste"]:
        raise ErreurV3("Manifeste des paires différent de celui inscrit au registre")
    return json.loads(MANIFESTE.read_text(encoding="utf-8"))


def paires_entrainement(evenements: list[dict]) -> list[dict]:
    if sha256_fichier(TRAIN) != lire_manifeste(evenements)["entrainement"]["sha256"]:
        raise ErreurV3("Paires d'entraînement différentes du manifeste")
    return [json.loads(l) for l in TRAIN.read_text(encoding="utf-8").splitlines() if l.strip()]


def relecture() -> dict:
    depot = exiger_depot_propre()
    evenements = lire_registre()
    exiger_pas_d_arret(evenements)
    paires = paires_entrainement(evenements)
    if REMIS_JUGES.exists():
        raise ErreurV3(f"{REMIS_JUGES} existe déjà : le dossier des juges ne doit contenir que leur fichier")
    idx = sorted(np.random.default_rng(GRAINE_RELECTURE).choice(len(paires), size=gen.N_RELECTURE, replace=False).tolist())
    tirage = {"sha256_entrainement": sha256_fichier(TRAIN), "graine": GRAINE_RELECTURE, "indices": idx,
              "paires": [{"indice": i, "question": paires[i]["question"], "passage": paires[i]["passage"]} for i in idx]}
    sha = ecrire_une_fois(RELECTURE, tirage)
    REMIS_JUGES.mkdir(parents=True)
    sha_remis = ecrire_une_fois(REMIS_JUGES / FICHIER_JUGES, tirage["paires"])   # les paires seules, rien d'autre
    inscrire("relecture", depot=depot, sha256_tirage=sha, sha256_remis=sha_remis, indices=idx)
    print(f"{RELECTURE.name} SHA-256 {sha} ; fichier des juges {sha_remis[:12]}")
    return tirage


def controler_verdicts(indices: list[int], verdicts: list) -> list[dict]:
    if [v.get("indice") if isinstance(v, dict) else None for v in verdicts] != indices:
        raise ErreurV3("Les verdicts ne portent pas sur les paires tirées, dans l'ordre")
    if any(v.get("verdict") not in ("juste", "fausse") or not set(v) <= {"indice", "verdict", "motif"} for v in verdicts):
        raise ErreurV3("Verdict inconnu ou clé non prévue")
    return verdicts


def ingerer_verdicts(juge: int, journal: Path, echec: bool = False) -> dict:
    exiger_depot_propre()
    evenements = lire_registre()
    rel = evenement_unique(evenements, "relecture")
    for autre in (1, 2):
        if not appels(evenements, "juge", autre)[0]:
            raise ErreurV3("Les deux juges doivent être lancés avant toute ingestion")
    champs, verdicts = ingerer_appel("juge", juge, journal, invite_juge(), MODELE_RELECTEUR, REMIS_JUGES / FICHIER_JUGES,
                                     rel["sha256_remis"], lambda v: controler_verdicts(rel["indices"], v), echec)
    sortie = {"juge": juge, **champs, "verdicts": verdicts}
    sha = ecrire_une_fois(VERDICTS[juge], sortie)
    inscrire("resultat", **champs, conforme=True, sha256_sortie=sha)
    print(f"juge {juge} ({champs['modele']}) : verdicts écrits, SHA-256 {sha[:12]}")   # le décompte n'est lu qu'au bilan
    return sortie


def kappa(a: list[bool], b: list[bool]) -> float | None:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def bilan(ecrire: bool = False) -> dict:
    """Une paire est fausse si l'un des deux juges la juge fausse ; le lot est utilisable avec au plus 3 fausses sur 30.
    Exige deux juges distincts, un seul résultat conforme chacun, des premiers journaux commencés tous deux avant la
    première ingestion de verdicts, et des fichiers conformes au registre."""
    depot = exiger_depot_propre() if ecrire else None
    evenements = lire_registre()
    rel = evenement_unique(evenements, "relecture")
    conformes, premiers = {}, {}
    for j in (1, 2):
        lancements, resultats = appels(evenements, "juge", j)
        ok = [r for r in resultats if r["conforme"]]
        if len(ok) != 1:
            raise ErreurV3(f"Juge {j} : {len(ok)} résultat(s) conforme(s)")
        conformes[j], premiers[j] = ok[0], resultats[0]
    if conformes[1]["agent_id"] == conformes[2]["agent_id"] or conformes[1]["sha256_journal"] == conformes[2]["sha256_journal"]:
        raise ErreurV3("Les deux juges ne sont pas deux sous-agents distincts")
    premiere_ingestion = min(instant(e["horodatage"]) for e in evenements
                             if e["evenement"] == "resultat" and e["etape"] == "juge")
    debuts = [lignes_journal(JOURNAUX / premiers[j]["journal"])[0].get("timestamp") for j in (1, 2)]
    if any(d is None or instant(d) >= premiere_ingestion for d in debuts):
        raise ErreurV3("Un juge a été lancé après l'ingestion des verdicts de l'autre")
    exiger_exhaustivite(evenements, "juge")
    if sha256_fichier(RELECTURE) != rel["sha256_tirage"]:
        raise ErreurV3("Tirage différent de celui inscrit au registre")
    tirage = json.loads(RELECTURE.read_text(encoding="utf-8"))
    if tirage["sha256_entrainement"] != lire_manifeste(evenements)["entrainement"]["sha256"] or tirage["indices"] != rel["indices"]:
        raise ErreurV3("Tirage qui ne porte pas sur les paires d'entraînement du manifeste")
    v = {}
    for j in (1, 2):
        if sha256_fichier(VERDICTS[j]) != conformes[j]["sha256_sortie"]:
            raise ErreurV3(f"Verdicts du juge {j} différents de ceux inscrits au registre")
        v[j] = json.loads(VERDICTS[j].read_text(encoding="utf-8"))
        if [x["indice"] for x in v[j]["verdicts"]] != tirage["indices"]:
            raise ErreurV3(f"Verdicts du juge {j} sur d'autres paires que le tirage")
    f1 = [x["verdict"] == "fausse" for x in v[1]["verdicts"]]
    f2 = [x["verdict"] == "fausse" for x in v[2]["verdicts"]]
    severe = [x or y for x, y in zip(f1, f2)]
    res = {"fausses_juge_1": sum(f1), "fausses_juge_2": sum(f2), "fausses": sum(severe), "relues": len(severe),
           "accord": sum(x == y for x, y in zip(f1, f2)), "kappa": kappa(f1, f2),
           "utilisable": sum(severe) <= gen.FAUX_MAX, "relecteurs": [v[1]["modele"], v[2]["modele"]],
           "agents": [conformes[1]["agent_id"], conformes[2]["agent_id"]],
           "relances": {j: len(appels(evenements, "juge", j)[0]) - 1 for j in (1, 2)},
           "indices_fausses": [x["indice"] for x, s in zip(v[1]["verdicts"], severe) if s]}
    if ecrire:
        sha = ecrire_une_fois(BILAN, res)
        inscrire("bilan", depot=depot, sha256_bilan=sha, fausses=res["fausses"],
                 utilisable=res["utilisable"])
        if not res["utilisable"]:
            inscrire("arret", motif=f"relecture : {res['fausses']} paires fausses sur 30")
    return res


# ---------------------------------------------------------------------------------------------------------------
# Entraînement, garde-fou, export, index : la recette de la v2-T, avec les chemins de la v3
# ---------------------------------------------------------------------------------------------------------------
def limiter_fils() -> None:
    import torch
    torch.set_num_threads(FILS)
    torch.set_num_interop_threads(1)


def bilan_inscrit(evenements: list[dict]) -> dict:
    exiger_pas_d_arret(evenements)
    if sha256_fichier(BILAN) != evenement_unique(evenements, "bilan")["sha256_bilan"]:
        raise ErreurV3("Bilan de la relecture différent de celui inscrit au registre")
    rel = json.loads(BILAN.read_text(encoding="utf-8"))
    if json.loads(json.dumps(bilan())) != rel or not rel["utilisable"]:
        raise ErreurV3("Bilan de la relecture non reproduit ou lot refusé")
    return rel


def entrainer() -> dict:
    depot = exiger_depot_propre()
    versions = exiger_environnement()
    evenements = lire_registre()
    rel = bilan_inscrit(evenements)
    if DOSSIER_V3.exists():
        raise ErreurV3(f"{DOSSIER_V3} existe déjà : rien n'est écrasé")
    paires = paires_entrainement(evenements)
    if not all(p["query"].startswith("query: ") and p["passage"].startswith("passage: ") for p in paires):
        raise ErreurV3("Préfixes E5 absents")
    limiter_fils()
    import torch
    from datasets import Dataset
    from sentence_transformers import (SentenceTransformer, SentenceTransformerTrainer,
                                       SentenceTransformerTrainingArguments, losses)
    torch.manual_seed(aj.RECETTE["seed"])
    jeu = Dataset.from_dict({"anchor": [p["query"] for p in paires], "positive": [p["passage"] for p in paires]})
    modele = SentenceTransformer(aj.MODELE_BASE, revision=aj.REVISION_BASE, device="cpu")
    perte = losses.MultipleNegativesRankingLoss(modele)
    args = SentenceTransformerTrainingArguments(
        output_dir=str(V3 / "trainer_v3"), logging_steps=2, save_strategy="no", report_to="none", use_cpu=True,
        dataloader_num_workers=0, **aj.RECETTE)
    trainer = SentenceTransformerTrainer(model=modele, args=args, train_dataset=jeu, loss=perte)
    t0 = time.time()
    resultat = trainer.train()
    duree = time.time() - t0
    modele.save_pretrained(str(DOSSIER_V3))
    pas = trainer.state.global_step
    rapport = {
        "amendement": "A3 (#167)", "depot": depot, "relecture": rel, "n_paires": len(paires),
        "manifeste": lire_manifeste(evenements)["entrainement"],
        "modele_depart": {"depot": aj.MODELE_BASE, "revision": aj.REVISION_BASE}, "recette": aj.RECETTE,
        "fils": {"torch": torch.get_num_threads(), "interop": torch.get_num_interop_threads()},
        "optimiseur": args.optim, "planificateur": args.lr_scheduler_type, "max_grad_norm": args.max_grad_norm,
        "pas": pas, "pas_d_echauffement": args.get_warmup_steps(pas), "appareil": str(modele.device),
        "duree_s": round(duree, 1), "perte_finale": resultat.training_loss, "journal": trainer.state.log_history,
        "lots_avec_deux_passages_d_une_fiche": aj.lots_meme_fiche([p["url"] for p in paires],
                                                                  aj.RECETTE["per_device_train_batch_size"]),
        "versions": versions,
        "poids": {"fichier": str((DOSSIER_V3 / "model.safetensors").relative_to(RACINE)),
                  "sha256": sha256_fichier(DOSSIER_V3 / "model.safetensors")},
        "ecrit_le": maintenant(),
    }
    sha = ecrire_une_fois(RAPPORT, rapport)
    inscrire("entrainement", depot=depot, sha256_rapport=sha, sha256_poids=rapport["poids"]["sha256"], pas=pas,
             n_paires=len(paires))
    print(json.dumps({k: v for k, v in rapport.items() if k != "journal"}, ensure_ascii=False, indent=1))
    return rapport


def rapport_inscrit(evenements: list[dict]) -> dict:
    e = evenement_unique(evenements, "entrainement")
    if sha256_fichier(RAPPORT) != e["sha256_rapport"]:
        raise ErreurV3("Rapport d'entraînement différent de celui inscrit au registre")
    if sha256_fichier(DOSSIER_V3 / "model.safetensors") != e["sha256_poids"]:
        raise ErreurV3("Poids de la v3 différents de ceux de l'entraînement")
    return json.loads(RAPPORT.read_text(encoding="utf-8"))


def valider() -> dict:
    """Garde-fou (A3, section 4) : la v3-C doit dépasser strictement la v1 sur ses questions de validation."""
    depot = exiger_depot_propre()
    exiger_environnement()
    evenements = lire_registre()
    exiger_pas_d_arret(evenements)
    if GARDE_FOU.exists():
        raise ErreurV3("Garde-fou déjà calculé : rien n'est écrasé")
    rapport_inscrit(evenements)
    if sha256_fichier(aj.DOSSIER_V1 / "model.safetensors") != aj.SHA256_POIDS_V1:
        raise ErreurV3("Poids de la v1 différents de ceux du protocole 05")
    if sha256_fichier(DOSSIER_V2 / "model.safetensors") != SHA256_POIDS_V2:
        raise ErreurV3("Poids de la v2-T différents de ceux de l'amendement A2")
    if sha256_fichier(VALIDATION) != lire_manifeste(evenements)["validation"]["sha256"]:
        raise ErreurV3("Questions de validation différentes du manifeste")
    limiter_fils()
    val = [json.loads(l) for l in VALIDATION.read_text(encoding="utf-8").splitlines() if l.strip()]
    table = gen.charger_passages()
    site = json.loads(gen.PASSAGES_SITE.read_text(encoding="utf-8"))
    entree = dict(zip(table.passage_id, table.entree_encodeur))
    ids = [p["passage_id"] for p in site]
    passages = [entree[i] for i in ids]
    position = {i: k for k, i in enumerate(ids)}
    fiche_de = [gen.url_fiche(p["url"]) for p in site]
    cibles = [position[q["passage_id"]] for q in val]
    fiches_cibles = [gen.url_fiche(q["url"]) for q in val]
    questions = [q["question"] for q in val]
    res = {"amendement": "A3 (#167), section 4", "depot": depot, "questions": len(val),
           "fiches": len(set(fiches_cibles)), "systemes": {}}
    succes = {}
    for nom, (source, rev) in {"base": (aj.MODELE_BASE, aj.REVISION_BASE), "v1": (str(aj.DOSSIER_V1), None),
                               "v2_T": (str(DOSSIER_V2), None), "v3_C": (str(DOSSIER_V3), None)}.items():
        m = aj.metriques(aj.classements(aj.encodeur(source, rev), questions, passages), cibles, fiche_de, fiches_cibles)
        succes[nom] = m.pop("succes@5")
        res["systemes"][nom] = m
        print(nom, json.dumps(m), flush=True)
    sys.path.insert(0, str(RACINE / "scripts/evaluation"))
    from metrics import noninferiority_tango, paired_success_test
    for a, b in (("v3_C", "v1"), ("v3_C", "v2_T"), ("v3_C", "base"), ("v1", "base")):
        t = noninferiority_tango(succes[a], succes[b], margin=0.0, groups=fiches_cibles, level=0.95)
        p = paired_success_test(succes[a], succes[b], groups=fiches_cibles)
        res[f"{a} moins {b}"] = {"ecart": t["difference"], "ic95_tango": list(t["ci_score"]),
                                 "effet_de_plan": t["design_effect"], "a_seul": t["n_10_A_only"],
                                 "b_seul": t["n_01_B_only"], "p_mcnemar": p["p_value"]}
    r3, r1 = res["systemes"]["v3_C"]["recall@5"], res["systemes"]["v1"]["recall@5"]
    res["regle"] = "la mesure continue si le Recall@5 de la v3-C dépasse strictement celui de la v1"
    res["passe"] = bool(r3 > r1)
    sha = ecrire_une_fois(GARDE_FOU, res)
    inscrire("garde_fou", depot=depot, sha256_garde_fou=sha, passe=res["passe"], recall5_v3=r3, recall5_v1=r1)
    if not res["passe"]:
        inscrire("arret", motif="garde-fou non passé")
    print(json.dumps({k: v for k, v in res.items() if k != "systemes"}, ensure_ascii=False, indent=1))
    return res


def exporter() -> dict:
    """Export ONNX et q8 par la recette de 06, après le contrôle de l'environnement : l'export rejoué sur la v1 doit
    redonner, bit à bit, les fichiers livrés le 14 octobre (comme pour la v2-T)."""
    depot = exiger_depot_propre()
    exiger_environnement(export=True)
    evenements = lire_registre()
    exiger_pas_d_arret(evenements)
    g = evenement_unique(evenements, "garde_fou")
    if sha256_fichier(GARDE_FOU) != g["sha256_garde_fou"] or not g["passe"]:
        raise ErreurV3("Garde-fou absent, modifié ou non passé : la v3-C n'est pas exportée")
    rapport_inscrit(evenements)
    if NAV_V3.exists():
        raise ErreurV3(f"{NAV_V3} existe déjà")
    limiter_fils()
    ex = _module("exporter_v2", "11_exporter_v2.py")         # import différé : il exige onnx, absent ailleurs
    c = ex.exporter(ex.DOSSIER_V1, V3 / "export_v1_controle")
    controle = {"fp32": c["fp32"]["sha256"] == ex.LIVRES_V1["onnx/model.onnx"],
                "q8": c["q8"]["sha256"] == ex.LIVRES_V1["onnx/model_quantized.onnx"]}
    if not all(controle.values()):
        inscrire("arret", motif="export rejoué sur la v1 différent des fichiers livrés : environnement non validé")
        raise ErreurV3(f"Export de contrôle de la v1 non identique : {controle}")
    r = ex.exporter(DOSSIER_V3, V3 / "export")
    r["controle_v1"] = controle
    (NAV_V3 / "onnx").mkdir(parents=True)
    for f in ex.FICHIERS_XENOVA:        # mêmes fichiers que le dossier navigateur de la v1 (Xenova, révision 761b726d)
        shutil.copyfile(ex.NAV_V1 / f, NAV_V3 / f)
        if sha256_fichier(NAV_V3 / f) != sha256_fichier(ex.NAV_V1 / f):
            raise ErreurV3(f"Copie de {f} différente")
    shutil.copyfile(V3 / "export/onnx/model_quantized.onnx", NAV_V3 / "onnx/model_quantized.onnx")
    r["navigateur"] = {"dossier": str(NAV_V3.relative_to(RACINE)),
                       "fichiers": {str(p.relative_to(NAV_V3)): sha256_fichier(p)
                                    for p in sorted(NAV_V3.rglob("*")) if p.is_file()}}
    sha = ecrire_une_fois(V3 / "export_v3.json", r)
    inscrire("export", depot=depot, sha256_export=sha, sha256_q8=r["q8"]["sha256"], navigateur=r["navigateur"]["fichiers"])
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return r


def encoder_index(dossier: Path) -> np.ndarray:
    """Les 4 240 passages en fp32, comme ajustement_v2.construire_index (amendement A2) : modèle en fp32, mode
    évaluation, tokeniseur de l'encodeur de base, aucune troncature, normalisation."""
    sys.path.insert(0, str(RACINE / "scripts/evaluation"))
    sys.path.insert(0, str(RACINE / "scripts/rag"))
    import ajustement_05 as a05
    import rag
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer
    table, _ = a05.table_et_index_site()
    modele = SentenceTransformer(str(dossier), device="cpu")
    modele.float()
    modele.eval()
    base = AutoTokenizer.from_pretrained(rag.MODELE_E5, revision=rag.REVISION_E5)
    modele[0].processor = base
    if modele.tokenizer is not base:
        raise ErreurV3("Le tokeniseur de base n'a pas remplacé celui du modèle")
    modele.max_seq_length = rag.BUDGET_E5
    textes = table.entree_encodeur.tolist()
    if max(len(modele.tokenizer(t, truncation=False)["input_ids"]) for t in textes) > 512:
        raise ErreurV3("Passage de plus de 512 tokens : aucune troncature n'est admise")
    m = np.asarray(modele.encode(textes, batch_size=32, normalize_embeddings=True, convert_to_numpy=True,
                                 show_progress_bar=False), dtype=np.float32)
    if m.shape != (4240, 384) or not np.isfinite(m).all() or np.abs(np.linalg.norm(m, axis=1) - 1).max() >= a05.TOLERANCE_NORME:
        raise ErreurV3("Index de forme inattendue, non fini ou non normalisé")
    return m


def index() -> dict:
    """Contrôle d'abord que le même code, avec 4 fils, redonne l'index de la v2-T ; puis encode les passages par la v3-C."""
    depot = exiger_depot_propre()
    exiger_environnement()
    evenements = lire_registre()
    exiger_pas_d_arret(evenements)
    evenement_unique(evenements, "export")
    rapport_inscrit(evenements)
    if INDEX_V3.exists():
        raise ErreurV3(f"{INDEX_V3} existe déjà")
    if sha256_fichier(INDEX_V2) != SHA256_INDEX_V2 or sha256_fichier(DOSSIER_V2 / "model.safetensors") != SHA256_POIDS_V2:
        raise ErreurV3("Index ou poids de la v2-T différents de ceux de l'amendement A2")
    limiter_fils()
    m2 = encoder_index(DOSSIER_V2)
    v2 = np.fromfile(INDEX_V2, dtype="<f4").reshape(4240, 384)
    controle = {"identique_bit_a_bit": m2.astype("<f4").tobytes() == v2.tobytes(),
                "cosinus_min": float((m2 * v2).sum(axis=1).min()), "ecart_absolu_max": float(np.abs(m2 - v2).max())}
    if controle["cosinus_min"] < 1 - 1e-6:
        inscrire("arret", motif="le code de l'index ne redonne pas l'index de la v2-T")
        raise ErreurV3(f"Index de la v2-T non reproduit : {controle}")
    m = encoder_index(DOSSIER_V3)
    with open(INDEX_V3, "xb") as f:
        f.write(m.astype("<f4").tobytes())
    sys.path.insert(0, str(RACINE / "scripts/evaluation"))
    import ajustement_05 as a05
    v1 = a05.charger_index_ajuste()
    resultat = {"fichier": str(INDEX_V3.relative_to(RACINE)), "sha256": sha256_fichier(INDEX_V3),
                "forme": list(m.shape), "poids_v3": rapport_inscrit(evenements)["poids"]["sha256"],
                "controle_v2": controle,
                "cosinus_avec_v1": {"min": float((m * v1).sum(axis=1).min()), "median": float(np.median((m * v1).sum(axis=1)))},
                "tokeniseur": "intfloat/multilingual-e5-small (révision de rag.py)", "fils": FILS}
    sha = ecrire_une_fois(INDEX_V3.with_suffix(".json"), resultat)
    inscrire("index", depot=depot, sha256_index=resultat["sha256"], sha256_meta=sha, controle_v2=controle)
    print(json.dumps(resultat, ensure_ascii=False, indent=1))
    return resultat


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = p.add_subparsers(dest="commande", required=True)
    sp.add_parser("lots")
    pl = sp.add_parser("lancer")
    g = pl.add_mutually_exclusive_group(required=True)
    g.add_argument("--lot", type=int)
    g.add_argument("--juge", type=int, choices=(1, 2))
    pi = sp.add_parser("ingerer"); pi.add_argument("--lot", type=int, required=True); pi.add_argument("--journal", type=Path, required=True)
    pi.add_argument("--echec", action="store_true", help="agent arrêté sans rapport final : inscrit comme non conforme")
    sp.add_parser("assembler")
    sp.add_parser("relecture")
    pv = sp.add_parser("verdicts"); pv.add_argument("--juge", type=int, choices=(1, 2), required=True)
    pv.add_argument("--journal", type=Path, required=True)
    pv.add_argument("--echec", action="store_true", help="agent arrêté sans rapport final : inscrit comme non conforme")
    sp.add_parser("bilan")
    for c in ("entrainer", "valider", "exporter", "index"):
        sp.add_parser(c)
    a = p.parse_args(argv)
    with verrou():
        executer(a)
    return 0


def executer(a) -> None:
    if a.commande == "lots":
        ecrire_lots()
    elif a.commande == "lancer":
        print(lancer("lot", a.lot) if a.lot is not None else lancer("juge", a.juge))
    elif a.commande == "ingerer":
        ingerer(a.lot, a.journal, a.echec)
    elif a.commande == "assembler":
        assembler()
    elif a.commande == "relecture":
        relecture()
    elif a.commande == "verdicts":
        ingerer_verdicts(a.juge, a.journal, a.echec)
    elif a.commande == "bilan":
        print(json.dumps(bilan(ecrire=True), ensure_ascii=False, indent=1))
    else:
        {"entrainer": entrainer, "valider": valider, "exporter": exporter, "index": index}[a.commande]()


if __name__ == "__main__":
    sys.exit(main())
