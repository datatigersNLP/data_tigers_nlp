"""Contrôles automatiques des candidats #93 ; aucune validation sémantique."""

import hashlib
from pathlib import Path
import unicodedata

if __package__:
    from .schema import CasSynthetique, creer_candidat, lire_proposition
else:
    from schema import CasSynthetique, creer_candidat, lire_proposition


def normaliser_question(question: str) -> str:
    texte = unicodedata.normalize("NFKC", question).casefold()
    texte = "".join(" " if unicodedata.category(c).startswith("P") else c for c in texte)
    return " ".join(texte.split())


def charger_questions_vues(dossier: Path, exclure: Path | None = None) -> tuple[set[str], list[dict]]:
    """Déduplique dans ce dossier de runs, sans lire les questions humaines."""
    questions, fichiers = set(), []
    for chemin in sorted(dossier.glob("*/candidates.jsonl")):
        if chemin.parent == exclure:
            continue
        octets = chemin.read_bytes()
        for ligne in octets.decode("utf-8").splitlines():
            if ligne.strip():
                candidat = CasSynthetique.model_validate_json(ligne)
                questions.add(normaliser_question(candidat.question))
        fichiers.append({"fichier": chemin.relative_to(dossier).as_posix(),
                         "sha256": hashlib.sha256(octets).hexdigest()})
    return questions, fichiers


def valider_proposition(texte: str, preparation: dict, run_id: str,
                       questions_vues: set[str]) -> CasSynthetique:
    proposition = lire_proposition(texte)
    if (proposition.type != preparation["type"]
            or proposition.difficulty_target != preparation["difficulty_target"]):
        raise ValueError("Catégorie ou difficulté différente de la demande")
    source = preparation["source"]
    for preuve in proposition.evidence:
        if preuve.passage_id != source["passage_id"]:
            raise ValueError("Preuve provenant d'une source non fournie")
        if preuve.excerpt not in source["texte"]:
            raise ValueError("Extrait non retrouvé mot pour mot dans le passage fourni")
    normalisee = normaliser_question(proposition.question)
    if not normalisee or normalisee in questions_vues:
        raise ValueError("Question vide après normalisation ou doublon normalisé")
    candidat = creer_candidat(proposition, run_id, 1, [source["passage_id"]])
    contenu = candidat.model_dump()
    contenu["validation"]["automatic"] = "passed"
    return CasSynthetique.model_validate(contenu)
