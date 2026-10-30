"""Mesure du volet B selon le protocole 06 (#52, #107) : états, classement, métriques et analyse appariée.

Le lot de test n'est lu qu'en mode mesure, et seulement si le verrou écrit au gel du protocole existe et si toutes
ses empreintes concordent : protocole, scripts, module de métriques, règle de pertinence, jeu figé, index et seuil S.
En mode calibration, seul le lot de calibration (5 questions du corpus, 3 hors corpus) est lu : c'est le mode de
mise au point et de relecture. Aucune décision de conception ne s'appuie sur le lot de test.

Sous-commandes, depuis la racine du dépôt, avec l'environnement de scripts/rag/requirements.txt :
    python scripts/rag/mesure.py executer --mode calibration --phase avant
    python scripts/rag/mesure.py analyser --mode calibration --phase avant
    python scripts/rag/mesure.py comparer --mode calibration --a apres --b avant
    python scripts/rag/mesure.py comparer --mode mesure --a apres --b temoin --reference temoin   # analyse principale
    python scripts/rag/mesure.py echantillon --a avant --b apres     # mode mesure : réponses à juger à l'aveugle
    python scripts/rag/mesure.py verrouiller                         # au gel : écrit le verrou à versionner

Phases : avant (modèle de #31), apres (modèle adapté de #107), temoin (témoin T, protocole section 3). Les phases
apres et temoin exigent --modele et --digest. Chaque exécution écrit dans data/evaluation/volet_b/<mode>/<phase>/,
qui n'est pas versionné, et refuse d'écraser une sortie : une seule exécution par état et par phase. La seule reprise
admise est celle d'un état invalide, dont plus de 5 % des questions ont fini en erreur technique (section 4).
L'analyse ne remplace jamais une analyse antérieure : --nouvelle-analyse en écrit une autre à côté. Toute génération
doit venir de la version d'Ollama épinglée par le protocole (section 8). L'analyse principale (section 6) n'est
désignée que pour B2, en mode mesure, « apres » contre la référence --reference (avant, ou temoin si T diffère du
modèle de #31) ; toute autre comparaison est descriptive, à 95 %, sans conclusion d'amélioration.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys

import numpy as np

if __package__:
    from .generation import DIGEST_QWEN_31, MODELE_QWEN, ErreurGeneration, generer_reponse, valider_citations
    from .rag import (ABSTENTION, CONSIGNE_RAG, FICHIER_QUESTIONS, JEU_COMMIT, charger_encodeur, charger_index,
                      construire_contexte, encoder_question, recuperer_passages)
else:
    from generation import DIGEST_QWEN_31, MODELE_QWEN, ErreurGeneration, generer_reponse, valider_citations
    from rag import (ABSTENTION, CONSIGNE_RAG, FICHIER_QUESTIONS, JEU_COMMIT, charger_encodeur, charger_index,
                     construire_contexte, encoder_question, recuperer_passages)

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "scripts" / "evaluation"))
from metrics import noninferiority_tango, paired_success_test, proportion_ci  # noqa: E402
from pertinence import IndexPertinence  # noqa: E402

PROTOCOLE = RACINE / "docs" / "etudes" / "evaluation" / "06_protocole_volet_b.md"
VERROU = Path(__file__).with_name("verrou_mesure.json")
SORTIES = RACINE / "data" / "evaluation" / "volet_b"
FICHIER_SEUIL = SORTIES / "seuil_b2.json"
SHA256_SEUIL = "7ba7230e5e8cda87fa1eb8dda2adc01d73c6702d542c27a4e3dc620464939936"   # protocole, section 7
SHA256_JEU = "807498144fec46722ffab045a87c191b6282a86300799976869d4d6c1755fb35"     # protocole, section 2
EFFECTIFS = {"calibration": (5, 3), "test": (73, 24)}   # questions du corpus, hors corpus
ETATS = ("B0", "B1", "B2", "R+", "R-")
FICHIERS_ETATS = {"B0": "B0", "B1": "B1", "B2": "B2", "R+": "Rplus", "R-": "Rmoins"}
PHASES = ("avant", "apres", "temoin")
CLASSES = ("abstention", "reponse_citee", "sortie_invalide", "erreur_technique", "reponse")
ECART_SIGNALE = 1e-5          # section 7 : question signalée si son score est à moins de 1e-5 de S
PART_ERREURS_MAX = 0.05       # section 4 : au-delà, l'état est invalide et refait en entier
NIVEAU = 0.95                 # section 6 : intervalles à 95 %
NIVEAU_PRINCIPAL = 0.975      # section 6 : analyse principale, Bonferroni pour deux comparaisons
GRAINE_JUGES, N_JUGES = 20261018, 20
VERSION_OLLAMA = "0.40.11"    # section 8 : version épinglée du Legion pour toutes les mesures
# Section 3 : B0 reprend mot pour mot la phrase de brièveté de la consigne de la #85, que B1 conserve, pour que B0 et
# B1 ne diffèrent que par les passages (calibration du 29 octobre : B0 coupé à 512 tokens sans elle).
BRIEVETE = [l for l in CONSIGNE_RAG.split("\n") if l.startswith("Réponds brièvement")]
if len(BRIEVETE) != 1:
    raise RuntimeError("La consigne de la #85 n'a plus exactement une phrase de brièveté")
CONSIGNE_B0 = ("Tu réponds en français à la question de l'utilisateur.\n" + BRIEVETE[0] + "\n"
               "Si tu ne connais pas la réponse avec certitude, réponds uniquement :\n" + ABSTENTION)
ENTETE_B0 = "Question utilisateur (texte exact) :\n"
REPONSE_R_PLUS = "La réponse se trouve dans le premier passage récupéré [P1]."


class ErreurMesure(ValueError):
    """Condition du protocole non satisfaite : la mesure ne doit pas se poursuivre."""


def sha256_octets(octets: bytes) -> str:
    return hashlib.sha256(octets).hexdigest()


def sha256_fichier(chemin: Path) -> str:
    return sha256_octets(Path(chemin).read_bytes())


def sha256_texte(chemin: Path) -> str:
    """Empreinte d'un fichier texte versionné, fins de ligne normalisées (CRLF en LF) : Git pour Windows convertit
    souvent les fins de ligne à l'extraction (core.autocrlf), et le verrou doit valoir sur le Mac comme sur le Legion.
    Le résultat est l'empreinte du contenu tel que Git le stocke."""
    return sha256_octets(Path(chemin).read_bytes().replace(b"\r\n", b"\n"))


def consigne_b1() -> str:
    """Consigne de la #85 privée de ses deux dernières lignes, celles qui demandent l'abstention (section 3)."""
    lignes = CONSIGNE_RAG.split("\n")
    if lignes[-1] != ABSTENTION or not lignes[-2].startswith("Si les passages ne permettent pas"):
        raise ErreurMesure("La consigne de la #85 a changé : les deux lignes d'abstention ne sont plus en fin")
    return "\n".join(lignes[:-2])


def fiche(url: str) -> str:
    if not isinstance(url, str) or not url.startswith("https://travail-emploi.gouv.fr/"):
        raise ErreurMesure(f"URL de fiche inattendue : {url!r}")
    return url.split("#", 1)[0].rstrip("/").rsplit("/", 1)[1]


def lire_jeu(lot: str, racine: Path = RACINE) -> list[dict]:
    """Questions d'un lot, lues au commit du tag jeu-questions-v1 après contrôle de l'empreinte du CSV."""
    if lot not in EFFECTIFS:
        raise ErreurMesure(f"Lot inconnu : {lot}")
    try:
        octets = subprocess.run(["git", "-C", str(racine), "show", f"{JEU_COMMIT}:{FICHIER_QUESTIONS}"],
                                check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ErreurMesure("Jeu figé indisponible ; lancer git fetch origin --tags") from exc
    if sha256_octets(octets) != SHA256_JEU:
        raise ErreurMesure("Empreinte du jeu différente de celle du protocole")
    questions = []
    for ligne in csv.DictReader(io.StringIO(octets.decode("utf-8"), newline="")):
        if ligne["lot"] != lot:
            continue
        corpus = ligne["type"] == "dans_corpus"
        questions.append({"id": ligne["id"], "type": ligne["type"], "question": ligne["question"],
                          "fiche": fiche(ligne["url"]) if corpus else None,
                          "extrait": ligne["extrait"] if corpus else None})
    attendus = EFFECTIFS[lot]
    obtenus = (sum(q["type"] == "dans_corpus" for q in questions), sum(q["type"] == "hors_corpus" for q in questions))
    if obtenus != attendus:
        raise ErreurMesure(f"Lot {lot} : {obtenus} questions (corpus, hors corpus), {attendus} attendues")
    return questions


def charger_seuil(chemin: Path | None = None) -> float:
    """Valeur complète de S, sans arrondi, lue après contrôle de l'empreinte du fichier (section 7)."""
    octets = Path(chemin or FICHIER_SEUIL).read_bytes()
    if sha256_octets(octets) != SHA256_SEUIL:
        raise ErreurMesure("Empreinte du fichier du seuil S différente de celle du protocole")
    seuil = json.loads(octets)["seuil"]
    if not isinstance(seuil, float) or not math.isfinite(seuil):
        raise ErreurMesure("Seuil S absent ou non fini")
    return seuil


# Verrou du protocole gelé

def empreintes_actuelles(index_entete: dict) -> dict:
    dossier = Path(__file__).parent
    evaluation = RACINE / "scripts" / "evaluation"
    if not PROTOCOLE.exists():
        raise ErreurMesure("Protocole 06 absent de cette copie : il n'est pas encore fusionné")
    return {"protocole": sha256_texte(PROTOCOLE), "mesure": sha256_texte(dossier / "mesure.py"),
            "rag": sha256_texte(dossier / "rag.py"), "generation": sha256_texte(dossier / "generation.py"),
            "metrics": sha256_texte(evaluation / "metrics.py"),
            "pertinence": sha256_texte(evaluation / "pertinence.py"),
            "jeu": SHA256_JEU, "seuil": SHA256_SEUIL,
            "index": index_entete["index"]["sha256"], "passages": index_entete["metadonnees"]["sha256"]}


def verifier_verrou(index_entete: dict, chemin: Path | None = None) -> dict:
    chemin = Path(chemin or VERROU)
    if not chemin.exists():
        raise ErreurMesure("Verrou absent : le protocole n'est pas gelé, le lot de test reste fermé")
    attendu = json.loads(chemin.read_text(encoding="utf-8"))["empreintes"]
    actuel = empreintes_actuelles(index_entete)
    ecarts = sorted(k for k in set(attendu) | set(actuel) if attendu.get(k) != actuel.get(k))
    if ecarts:
        raise ErreurMesure(f"Empreintes différentes du verrou : {', '.join(ecarts)}")
    return actuel


def verrouiller(index_entete: dict, chemin: Path | None = None) -> dict:
    chemin = Path(chemin or VERROU)
    if chemin.exists():
        raise ErreurMesure("Verrou déjà écrit : il ne se réécrit pas")
    contenu = {"ecrit_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "empreintes": empreintes_actuelles(index_entete)}
    chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return contenu


# Exécution d'un état

def classer(statut: str, etat: str) -> str:
    """Classe de la section 4 à partir du statut de generer_reponse ou de valider_citations."""
    if statut == "erreur_technique":
        return "erreur_technique"
    if statut == "abstention_modele":
        return "abstention"
    if etat == "B0":
        return "reponse"      # sans passage, aucune citation n'est possible : toute autre sortie est une réponse
    if statut in ("reponse_citee", "sortie_invalide"):
        return statut
    raise ErreurMesure(f"Statut inconnu : {statut}")


def preparer_questions(questions: list[dict], index, encoder, seuil: float) -> list[dict]:
    """Récupération unique par question, partagée par B1, B2 et R+ ; signalement des scores proches de S."""
    preparees = []
    for q in questions:
        resultats = recuperer_passages(index, encoder(q["question"]), top_k=5)
        score_max = resultats[0]["score"]
        preparees.append({**q, "resultats": resultats, "score_max": score_max,
                          "sous_le_seuil": score_max < seuil,
                          "proche_du_seuil": abs(score_max - seuil) < ECART_SIGNALE,
                          "contexte": construire_contexte(q["question"], resultats)})
    return preparees


def executer_etat(etat: str, preparees: list[dict], generer, modele: str, digest: str,
                  version_ollama: str = VERSION_OLLAMA) -> list[dict]:
    lignes = []
    for q in preparees:
        contexte, gen, appel = q["contexte"], None, True
        if etat == "B0":
            contexte = {"system": CONSIGNE_B0, "prompt": ENTETE_B0 + q["question"], "sources": []}
        elif etat == "B1":
            contexte = {**contexte, "system": consigne_b1()}
        if etat == "B2" and q["sous_le_seuil"]:
            statut, appel, motifs = "abstention_modele", False, ["sous_le_seuil"]
            validation = {"citations": []}
        elif etat == "R+":
            validation = valider_citations(REPONSE_R_PLUS, contexte["sources"], ABSTENTION)
            statut, appel, motifs = validation["statut"], False, validation["motifs"]
        elif etat == "R-":
            statut, appel, motifs, validation = "abstention_modele", False, [], {"citations": []}
        else:
            try:
                gen = generer(contexte, ABSTENTION, modele, digest)
                statut, validation = gen["statut"], gen["validation_citations"]
                motifs = gen["erreurs_techniques"] + validation.get("motifs", [])
            except ErreurGeneration as exc:
                statut, validation, motifs = "erreur_technique", {"citations": []}, [f"exception : {exc}"]
            if gen and gen["ollama"].get("version") != version_ollama:
                raise ErreurMesure(f"Ollama {gen['ollama'].get('version')} au lieu de la version épinglée "
                                   f"{version_ollama} (section 8) : mesure interrompue, rien n'est écrit pour {etat}")
        refs = {s["reference"]: s["passage_id"] for s in contexte["sources"]}
        citations = validation.get("citations", []) if statut != "erreur_technique" else []
        lignes.append({
            "id": q["id"], "type": q["type"], "fiche": q["fiche"], "etat": etat, "classe": classer(statut, etat),
            "appel_modele": appel, "score_max": q["score_max"], "proche_du_seuil": q["proche_du_seuil"],
            "passages": [r["passage"]["passage_id"] for r in q["resultats"]],
            "citations": citations, "passages_cites": [refs[c] for c in citations if c in refs],
            "motifs": motifs,
            "reponse": (REPONSE_R_PLUS if etat == "R+" else ABSTENTION if not appel else gen["reponse_brute"]
                        if gen else None),
            "sha256_system": sha256_octets(contexte["system"].encode("utf-8")) if etat not in ("R+", "R-") else None,
            "mesures_ollama": gen["mesures_ollama"] if gen else None,
            "entree": {k: gen["entree"][k] for k in ("nb_tokens", "sha256_texte")} if gen else None,
            "ollama": gen["ollama"] if gen else None,
        })
    return lignes


def chemin_etat(mode: str, phase: str, etat: str, racine: Path | None = None) -> Path:
    return Path(racine or SORTIES) / mode / phase / f"{FICHIERS_ETATS[etat]}.jsonl"


def part_erreurs(lignes: list[dict]) -> float:
    return sum(l["classe"] == "erreur_technique" for l in lignes) / len(lignes)


def ecrire_etat(chemin: Path, lignes: list[dict], reprendre: bool = False) -> None:
    """Une seule exécution par état et par phase ; reprise admise seulement pour un état invalide (section 4)."""
    chemin = Path(chemin)
    if chemin.exists():
        precedent = [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not reprendre:
            raise ErreurMesure(f"{chemin.name} existe déjà : une seule exécution par état et par phase")
        if part_erreurs(precedent) <= PART_ERREURS_MAX:
            raise ErreurMesure("Reprise refusée : l'état précédent n'est pas invalide (5 % d'erreurs ou moins)")
        n = 1
        while chemin.with_name(f"{chemin.stem}.invalide-{n}.jsonl").exists():
            n += 1
        chemin.rename(chemin.with_name(f"{chemin.stem}.invalide-{n}.jsonl"))
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("".join(json.dumps(l, ensure_ascii=False, allow_nan=False) + "\n" for l in lignes),
                      encoding="utf-8")


def lire_etat(chemin: Path) -> list[dict]:
    return [json.loads(l) for l in Path(chemin).read_text(encoding="utf-8").splitlines() if l.strip()]


# Métriques (section 5)

def couverture(reponse: str) -> float:
    """Part des phrases d'une réponse citée qui portent au moins une référence [Pk] (indicateur descriptif)."""
    phrases = [p for p in re.split(r"(?<=[.!?])\s+|\n+", reponse.strip()) if p.strip()]
    return sum(bool(re.search(r"\[P\d+\]", p)) for p in phrases) / len(phrases) if phrases else 0.0


def succes(ligne: dict, metrique: str, pertinents: dict) -> bool:
    c = ligne["classe"]
    if metrique in ("M1", "M2"):
        return c == "abstention"
    if metrique == "M3":
        return c == "reponse_citee"
    if metrique == "M4":
        return c == "reponse_citee" and bool(set(ligne["passages_cites"]) & pertinents[ligne["id"]])
    if metrique == "M5":
        return c in ("reponse_citee", "sortie_invalide", "reponse")
    raise ErreurMesure(f"Métrique inconnue : {metrique}")


POPULATIONS = {"M1": "hors_corpus", "M2": "dans_corpus", "M3": "dans_corpus", "M4": "dans_corpus", "M5": "hors_corpus"}


def passages_pertinents(questions: list[dict], passages: list[dict]) -> dict:
    """Passages pertinents de chaque question du corpus selon la règle D4 du notebook 03."""
    index = IndexPertinence([p["texte"] for p in passages])
    ids = [p["passage_id"] for p in passages]
    return {q["id"]: {ids[i] for i in index.pertinents(q["extrait"])} for q in questions if q["type"] == "dans_corpus"}


def intervalle(succes_: list[bool], groupes: list | None) -> list[float] | None:
    if not succes_:
        return None
    if groupes is not None and len(set(groupes)) < 2:
        groupes = None
    bas, haut = proportion_ci(succes_, groups=groupes, level=NIVEAU, method="wilson")
    return [bas, haut]


def metriques(lignes: list[dict], pertinents: dict) -> dict:
    """M1 à M5 sur les questions sans erreur technique, avec leurs intervalles à 95 %, et les indicateurs."""
    etat = lignes[0]["etat"]
    sortie = {"etat": etat, "questions": len(lignes),
              "erreurs_techniques": sum(l["classe"] == "erreur_technique" for l in lignes),
              "part_erreurs": part_erreurs(lignes)}
    sortie["etat_invalide"] = sortie["part_erreurs"] > PART_ERREURS_MAX
    for m, population in POPULATIONS.items():
        if etat == "B0" and m in ("M3", "M4"):
            sortie[m] = None      # sans passage, aucune citation n'est possible (section 4)
            continue
        valides = [l for l in lignes if l["type"] == population and l["classe"] != "erreur_technique"]
        s = [succes(l, m, pertinents) for l in valides]
        groupes = [l["fiche"] for l in valides] if population == "dans_corpus" else None
        sortie[m] = {"succes": sum(s), "effectif": len(s), "proportion": (sum(s) / len(s)) if s else None,
                     "ic95": intervalle(s, groupes)}
    valides = [l for l in lignes if l["classe"] != "erreur_technique"]
    citees = [l for l in valides if l["classe"] == "reponse_citee"]
    sortie["descriptif"] = {
        "part_sorties_invalides": (sum(l["classe"] == "sortie_invalide" for l in valides) / len(valides))
        if valides else None,
        "couverture_mediane": float(np.median([couverture(l["reponse"]) for l in citees])) if citees else None,
        "questions_proches_du_seuil": sorted(l["id"] for l in lignes if l["proche_du_seuil"]),
        "tokens_entree_medians": _mediane("prompt_eval_count", lignes),
        "tokens_sortie_medians": _mediane("eval_count", lignes),
        "duree_totale_mediane_ns": _mediane("total_duration", lignes),
    }
    return sortie


def _mediane(champ: str, lignes: list[dict]):
    valeurs = [l["mesures_ollama"][champ] for l in lignes
               if l["mesures_ollama"] and isinstance(l["mesures_ollama"].get(champ), (int, float))]
    return float(np.median(valeurs)) if valeurs else None


# Comparaisons appariées (section 6)

def est_principale(mode: str, etat: str, a: str, b: str, reference: str | None) -> bool:
    """Section 6 : l'analyse principale est B2, en mode mesure, « apres » contre la référence désignée (avant, ou
    temoin si T diffère du modèle de #31). Toute autre comparaison est descriptive."""
    return mode == "mesure" and etat == "B2" and a == "apres" and reference in ("avant", "temoin") and b == reference


def versions_ollama(lignes: list[dict]) -> list[str]:
    return sorted({l["ollama"]["version"] for l in lignes if l.get("ollama") and l["ollama"].get("version")})


def comparer(lignes_a: list[dict], lignes_b: list[dict], pertinents: dict, principale: bool = False) -> dict:
    """Écarts A moins B sur la population commune : questions sans erreur technique dans les deux états, par
    identifiant, jamais par position. Dans l'analyse principale, M1 et M4 sont à 97,5 % avec la règle de conclusion ;
    tout le reste, et toute comparaison qui n'est pas l'analyse principale, est descriptif à 95 %."""
    if lignes_a[0]["etat"] != lignes_b[0]["etat"]:
        raise ErreurMesure("Comparaison de deux états différents")
    a = {l["id"]: l for l in lignes_a}
    b = {l["id"]: l for l in lignes_b}
    if set(a) != set(b):
        raise ErreurMesure("Les deux phases ne portent pas sur les mêmes questions")
    va, vb = versions_ollama(lignes_a), versions_ollama(lignes_b)
    if len(va) > 1 or len(vb) > 1 or (va and vb and va != vb):
        raise ErreurMesure(f"Versions d'Ollama différentes ({va}, {vb}) : la comparaison est invalide (section 8)")
    resultat = {"etat": lignes_a[0]["etat"], "analyse": "principale (section 6)" if principale else "descriptive",
                "versions_ollama": sorted(set(va) | set(vb))}
    for m, population in POPULATIONS.items():
        if resultat["etat"] == "B0" and m in ("M3", "M4"):
            continue
        ids = sorted(i for i in a if a[i]["type"] == population)
        exclus = sorted(i for i in ids if "erreur_technique" in (a[i]["classe"], b[i]["classe"]))
        commune = [i for i in ids if i not in exclus]
        principal = principale and m in ("M1", "M4")
        niveau = NIVEAU_PRINCIPAL if principal else NIVEAU
        entree = {"population": population, "effectif_commun": len(commune), "exclus": exclus,
                  "analyse_principale": principal, "niveau": niveau}
        if commune:
            sa = [succes(a[i], m, pertinents) for i in commune]
            sb = [succes(b[i], m, pertinents) for i in commune]
            groupes = [a[i]["fiche"] for i in commune] if population == "dans_corpus" else None
            if groupes is not None and len(set(groupes)) < 2:
                groupes = None
            mcnemar = paired_success_test(sa, sb)
            tango = noninferiority_tango(sa, sb, margin=0.0, groups=groupes if m != "M1" else None, level=niveau)
            entree.update({"proportion_a": sum(sa) / len(sa), "proportion_b": sum(sb) / len(sb),
                           "ecart": tango["difference"], "intervalle": list(tango["ci_score"]),
                           "effet_de_plan": tango["design_effect"],
                           "mcnemar_p_exacte": mcnemar["p_value"],
                           "table": mcnemar["contingency_table"]})
            if principal:
                entree["amelioration_demontree"] = bool(tango["ci_score"][0] > 0)
        resultat[m] = entree
    return resultat


def analyser(mode: str, phase: str, pertinents: dict, nouvelle: bool = False) -> dict:
    """Métriques des états présents, avec l'empreinte de chaque fichier analysé. Une analyse écrite n'est jamais
    remplacée : sans --nouvelle-analyse, l'existence de metriques.json arrête tout ; avec, metriques-<n>.json."""
    dossier = chemin_etat(mode, phase, "B0").parent
    cible = dossier / "metriques.json"
    if cible.exists():
        if not nouvelle:
            raise ErreurMesure(f"{cible.name} existe déjà : --nouvelle-analyse pour en écrire une autre à côté")
        n = 2
        while (dossier / f"metriques-{n}.json").exists():
            n += 1
        cible = dossier / f"metriques-{n}.json"
    sources, etats = {}, {}
    for etat in ETATS:
        chemin = chemin_etat(mode, phase, etat)
        if chemin.exists():
            sources[etat] = {"fichier": chemin.name, "sha256": sha256_fichier(chemin)}
            etats[etat] = metriques(lire_etat(chemin), pertinents)
    if not etats:
        raise ErreurMesure(f"Aucun état exécuté pour la phase {phase} en mode {mode}")
    resultat = {"mode": mode, "phase": phase, "ecrit_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "fichier": cible.name, "sources": sources, "etats": etats}
    texte = json.dumps(resultat, ensure_ascii=False, indent=1, allow_nan=False) + "\n"
    with open(cible, "x", encoding="utf-8") as f:       # « x » : jamais d'écrasement, même en cas de course
        f.write(texte)
    return resultat


# Échantillon pour le jugement à l'aveugle (section 5)

def echantillon(lignes_a: list[dict], lignes_b: list[dict], phases: tuple[str, str], questions: dict,
               passages: dict) -> tuple[list[dict], dict]:
    """20 réponses citées tirées au hasard dans chaque phase (graine 20261018), mélangées et anonymisées ;
    la clé qui rend la phase de chaque réponse est rendue à part, pour rester inaccessible aux juges."""
    rng = np.random.default_rng(GRAINE_JUGES)
    tirees = []
    for phase, lignes in zip(phases, (lignes_a, lignes_b)):
        citees = sorted((l for l in lignes if l["classe"] == "reponse_citee"), key=lambda l: l["id"])
        choix = rng.choice(len(citees), size=min(N_JUGES, len(citees)), replace=False) if citees else []
        tirees += [(phase, citees[int(i)]) for i in sorted(choix)]
    ordre = rng.permutation(len(tirees))
    fiches, cle = [], {}
    for rang, i in enumerate(ordre, 1):
        phase, l = tirees[int(i)]
        code = f"J{rang:02d}"
        fiches.append({"code": code, "question": questions[l["id"]], "reponse": l["reponse"],
                       "passages_cites": [{"passage_id": pid, "texte": passages[pid]} for pid in l["passages_cites"]]})
        cle[code] = {"phase": phase, "id_question": l["id"]}
    return fiches, cle


# Ligne de commande

def _outils_reels():
    index = charger_index()
    modele_e5 = charger_encodeur()
    return index, (lambda texte: encoder_question(modele_e5, texte)), generer_reponse


def _lot(mode: str, index_entete: dict) -> str:
    if mode == "mesure":
        verifier_verrou(index_entete)
        return "test"
    return "calibration"


def main(argv=None, outils=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sous = parser.add_subparsers(dest="commande", required=True)
    ex = sous.add_parser("executer")
    ex.add_argument("--mode", choices=("calibration", "mesure"), required=True)
    ex.add_argument("--phase", choices=PHASES, required=True)
    ex.add_argument("--etats", default=",".join(ETATS))
    ex.add_argument("--modele", default=MODELE_QWEN)
    ex.add_argument("--digest", default=DIGEST_QWEN_31)
    ex.add_argument("--reprendre-etat-invalide", action="store_true")
    an = sous.add_parser("analyser")
    an.add_argument("--mode", choices=("calibration", "mesure"), required=True)
    an.add_argument("--phase", choices=PHASES, required=True)
    an.add_argument("--nouvelle-analyse", action="store_true",
                    help="écrire metriques-<n>.json à côté des analyses antérieures, qui restent intactes")
    co = sous.add_parser("comparer")
    co.add_argument("--mode", choices=("calibration", "mesure"), required=True)
    co.add_argument("--a", choices=PHASES, required=True)
    co.add_argument("--b", choices=PHASES, required=True)
    co.add_argument("--etat", choices=ETATS, default="B2")
    co.add_argument("--reference", choices=("avant", "temoin"),
                    help="référence de l'analyse principale (section 6) : avant, ou temoin si T diffère de #31")
    ec = sous.add_parser("echantillon")
    ec.add_argument("--a", choices=PHASES, default="avant")
    ec.add_argument("--b", choices=PHASES, default="apres")
    sous.add_parser("verrouiller")
    args = parser.parse_args(argv)
    try:
        if args.commande == "comparer":
            if args.a == args.b:
                raise ErreurMesure("Comparaison d'une phase avec elle-même")
            if args.mode == "mesure" and args.etat == "B2" and args.a == "apres" and args.reference is None:
                raise ErreurMesure("Désigner la référence de l'analyse principale : --reference avant ou temoin "
                                   "(section 3 : temoin si T diffère du modèle de #31)")
        if args.commande == "verrouiller":
            print(json.dumps(verrouiller(charger_index().entete), ensure_ascii=False, indent=1))
            return 0
        if args.commande == "executer":
            etats = [e for e in args.etats.split(",") if e]
            if not set(etats) <= set(ETATS):
                raise ErreurMesure(f"États inconnus : {sorted(set(etats) - set(ETATS))}")
            if args.phase != "avant" and (args.modele == MODELE_QWEN or args.digest == DIGEST_QWEN_31):
                raise ErreurMesure("Les phases apres et temoin exigent --modele et --digest de leur propre modèle")
            if args.phase == "avant" and (args.modele != MODELE_QWEN or args.digest != DIGEST_QWEN_31):
                raise ErreurMesure("La phase avant mesure le modèle de #31, et lui seul")
            index, encoder, generer = outils() if outils else _outils_reels()
            lot = _lot(args.mode, index.entete)
            seuil = charger_seuil()
            for etat in etats:
                chemin = chemin_etat(args.mode, args.phase, etat)
                if chemin.exists() and not args.reprendre_etat_invalide:
                    raise ErreurMesure(f"{etat} déjà exécuté pour la phase {args.phase}")
                if chemin.exists() and part_erreurs(lire_etat(chemin)) <= PART_ERREURS_MAX:
                    raise ErreurMesure(f"Reprise de {etat} refusée : l'état précédent n'est pas invalide")
            preparees = preparer_questions(lire_jeu(lot), index, encoder, seuil)
            for etat in etats:
                lignes = executer_etat(etat, preparees, generer, args.modele, args.digest)
                ecrire_etat(chemin_etat(args.mode, args.phase, etat), lignes, args.reprendre_etat_invalide)
                print(f"{etat} : {len(lignes)} questions, part d'erreurs techniques {part_erreurs(lignes):.1%}")
            meta = {"mode": args.mode, "phase": args.phase, "lot": lot, "etats": etats, "modele": args.modele,
                    "digest": args.digest, "version_ollama": VERSION_OLLAMA, "seuil": seuil,
                    "ecrit_le": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "numpy": np.__version__}
            chemin_meta = chemin_etat(args.mode, args.phase, etats[0]).with_name(
                f"execution-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}.json")
            chemin_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            return 0
        index = (outils()[0] if outils else charger_index())
        if args.commande == "echantillon":
            verifier_verrou(index.entete)
            questions = lire_jeu("test")
        else:
            questions = lire_jeu(_lot(args.mode, index.entete))
        pertinents = passages_pertinents(questions, index.passages)
        if args.commande == "analyser":
            print(json.dumps(analyser(args.mode, args.phase, pertinents, args.nouvelle_analyse), ensure_ascii=False,
                             indent=1, allow_nan=False))
            return 0
        if args.commande == "comparer":
            resultat = comparer(lire_etat(chemin_etat(args.mode, args.a, args.etat)),
                                lire_etat(chemin_etat(args.mode, args.b, args.etat)), pertinents,
                                est_principale(args.mode, args.etat, args.a, args.b, args.reference))
            print(json.dumps(resultat, ensure_ascii=False, indent=1, allow_nan=False))
            return 0
        fiches_juges, cle = echantillon(lire_etat(chemin_etat("mesure", args.a, "B2")),
                                        lire_etat(chemin_etat("mesure", args.b, "B2")), (args.a, args.b),
                                        {q["id"]: q["question"] for q in questions},
                                        {p["passage_id"]: p["texte"] for p in index.passages})
        dossier = Path(SORTIES) / "mesure" / "jugement"
        dossier.mkdir(parents=True, exist_ok=True)
        for nom, contenu in (("a_juger.json", fiches_juges), ("cle_a_garder_secrete.json", cle)):
            if (dossier / nom).exists():
                raise ErreurMesure(f"{nom} existe déjà")
            (dossier / nom).write_text(json.dumps(contenu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{len(fiches_juges)} réponses à juger écrites dans {dossier}")
        return 0
    except ErreurMesure as exc:
        print(f"Mesure refusée : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
