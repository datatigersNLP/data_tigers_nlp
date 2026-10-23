"""Contrat des cas synthétiques (#91), sans lecture du corpus ni appel réseau."""

import json
from typing import Annotated, Literal, Self

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator


def _non_vide(texte: str) -> str:
    if not texte.strip():
        raise ValueError("Un texte composé seulement d'espaces est interdit")
    return texte  # Le texte reçu reste intact, y compris sa typographie.


Texte = Annotated[str, Field(min_length=1), AfterValidator(_non_vide)]
Categorie = Literal["simple", "reformulation", "multi_passage", "adversarial", "hors_corpus"]
Difficulte = Literal["easy", "medium", "hard"]
IdentifiantLot = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")]


class ModeleStrict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class Preuve(ModeleStrict):
    passage_id: Texte
    excerpt: Texte


class Proposition(ModeleStrict):
    """Seul contenu autorisé dans la réponse du futur générateur Qwen."""

    question: Texte
    type: Categorie
    difficulty_target: Difficulte
    answerable_proposed: bool
    evidence: list[Preuve]
    generation_reason: Texte
    adversarial_premise: Texte | None = None
    correction_proposed: Texte | None = None
    out_of_corpus_reason: Texte | None = None

    @model_validator(mode="after")
    def verifier_coherence(self) -> Self:
        preuves = [(p.passage_id, p.excerpt) for p in self.evidence]
        if len(preuves) != len(set(preuves)):
            raise ValueError("Preuve dupliquée")
        sources = {p.passage_id for p in self.evidence}
        if self.type in {"simple", "reformulation", "multi_passage"} and not self.answerable_proposed:
            raise ValueError("Cette catégorie doit proposer une question répondable")
        if self.type == "hors_corpus" and self.answerable_proposed:
            raise ValueError("Un candidat hors corpus doit proposer une abstention")
        if self.answerable_proposed:
            if not sources or self.out_of_corpus_reason is not None:
                raise ValueError("Une réponse possible exige des preuves, sans motif hors corpus")
        elif self.evidence or self.out_of_corpus_reason is None:
            raise ValueError("Une absence de réponse exige un motif et aucune preuve positive")
        if self.type in {"simple", "reformulation"} and len(sources) != 1:
            raise ValueError("Cette catégorie utilise un seul passage")
        if self.type == "multi_passage" and len(sources) < 2:
            raise ValueError("Un cas multi-passage exige deux identifiants distincts")
        if self.type == "adversarial":
            if self.adversarial_premise is None:
                raise ValueError("Un piège exige une prémisse à vérifier")
            if self.answerable_proposed and self.correction_proposed is None:
                raise ValueError("Un piège répondable exige une correction proposée")
            if not self.answerable_proposed and self.correction_proposed is not None:
                raise ValueError("Un piège non répondable ne fournit pas de correction étayée")
        elif self.adversarial_premise is not None or self.correction_proposed is not None:
            raise ValueError("Prémisse et correction sont réservées aux pièges")
        return self


class ValidationCas(ModeleStrict):
    """Trace déclarative d'une validation, pas une preuve d'identité du relecteur."""

    automatic: Literal["pending", "passed", "failed"] = "pending"
    human: Literal["pending", "accepted", "rejected"] = "pending"
    answerable_confirmed: bool | None = None
    reviewer: Texte | None = None
    review_note: Texte | None = None
    expected_points: list[Texte] = Field(default_factory=list)

    @model_validator(mode="after")
    def verifier_relecture(self) -> Self:
        if self.human == "pending":
            if (self.answerable_confirmed is not None or self.reviewer is not None
                    or self.review_note is not None or self.expected_points):
                raise ValueError("Une relecture en attente ne porte aucun verdict humain")
        else:
            if self.reviewer is None or self.review_note is None:
                raise ValueError("Une relecture exige un nom et une justification")
            if self.human == "accepted":
                if self.automatic != "passed" or self.answerable_confirmed is None:
                    raise ValueError("Une acceptation exige les contrôles et un verdict explicite")
                if self.answerable_confirmed != bool(self.expected_points):
                    raise ValueError("Les points attendus sont requis seulement pour une réponse possible")
        return self


class CasSynthetique(Proposition):
    """Enveloppe attribuée par le programme, liée au manifeste par run_id."""

    schema_version: Literal["synthetic-v1"] = "synthetic-v1"
    set: Literal["synthetic_challenge"] = "synthetic_challenge"
    id: Texte
    run_id: IdentifiantLot
    generation_source_ids: list[Texte]
    validation: ValidationCas = Field(default_factory=ValidationCas)

    @model_validator(mode="after")
    def verifier_enveloppe(self) -> Self:
        prefixe = f"SYN_{self.run_id}_"
        suffixe = self.id.removeprefix(prefixe)
        if (not self.id.startswith(prefixe) or len(suffixe) < 4
                or not suffixe.isascii() or not suffixe.isdecimal() or int(suffixe) < 1):
            raise ValueError("Identifiant attendu : SYN_<run_id>_<numéro positif sur au moins 4 chiffres>")
        sources = self.generation_source_ids
        if len(sources) != len(set(sources)):
            raise ValueError("Source de génération dupliquée")
        if not {p.passage_id for p in self.evidence}.issubset(sources):
            raise ValueError("Une preuve doit appartenir aux sources fournies au générateur")
        if (self.validation.human == "accepted"
                and self.validation.answerable_confirmed != self.answerable_proposed):
            raise ValueError("Une proposition mal classée doit être rejetée, pas confirmée")
        return self


def _objet_sans_doublon(paires: list[tuple]) -> dict:
    resultat = {}
    for cle, valeur in paires:
        if cle in resultat:
            raise ValueError(f"Clé JSON dupliquée : {cle}")
        resultat[cle] = valeur
    return resultat


def _constante_interdite(valeur: str):
    raise ValueError(f"Constante non conforme au JSON : {valeur}")


def lire_proposition(texte_json: str) -> Proposition:
    """Refuse le JSON ambigu ou entouré de Markdown, sans réparer la sortie."""
    donnees = json.loads(texte_json, object_pairs_hook=_objet_sans_doublon,
                         parse_constant=_constante_interdite)
    return Proposition.model_validate(donnees)


def creer_candidat(proposition: Proposition, run_id: str, numero: int,
                   source_ids: list[str]) -> CasSynthetique:
    """Attribue l'identité ; aucun verdict humain ou contrôle de corpus n'est ajouté."""
    if type(numero) is not int or numero < 1:
        raise ValueError("Le numéro doit être un entier strictement positif")
    contenu = Proposition.model_validate(proposition.model_dump()).model_dump()
    return CasSynthetique(**contenu, id=f"SYN_{run_id}_{numero:04d}", run_id=run_id,
                         generation_source_ids=source_ids)


def schema_generation() -> dict:
    """Schéma structurel pour Ollama ; les règles croisées restent vérifiées en Python."""
    return Proposition.model_json_schema()
