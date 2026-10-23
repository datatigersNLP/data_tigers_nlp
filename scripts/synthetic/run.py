"""Un run = un appel et ses traces, dans un nouveau dossier (#93)."""

from contextlib import ExitStack
import hashlib
import json
from pathlib import Path

from pydantic import TypeAdapter

if __package__:
    from . import client_qwen, corpus, validation
    from .schema import IdentifiantLot
else:
    import client_qwen
    import corpus
    import validation
    from schema import IdentifiantLot


def _ligne(fichier, objet: dict) -> None:
    fichier.write(json.dumps(objet, ensure_ascii=False) + "\n")
    fichier.flush()


def executer(preparation: dict, run_id: str, racine: Path,
             autoriser_telechargement: bool = False) -> dict:
    """Réserve le dossier avant toute API ; conserve aussi les erreurs techniques."""
    TypeAdapter(IdentifiantLot).validate_python(run_id, strict=True)
    racine.mkdir(parents=True, exist_ok=True)
    dossier = racine / run_id
    dossier.mkdir()  # exist_ok=False : protège aussi un run partiel ou en cours.
    empreintes = {nom: hashlib.sha256(Path(__file__).with_name(nom).read_bytes()).hexdigest()
                  for nom in ("run.py", "validation.py", "client_qwen.py")}
    manifeste = {"format": "agent0-run-v1", "run_id": run_id,
                 "preparation": preparation, "sha256_fichiers_execution": empreintes,
                 "autoriser_telechargement_tokeniseur": autoriser_telechargement}
    corpus.enregistrer_manifeste(manifeste, dossier / "manifest.json")
    resume = {"run_id": run_id, "dossier": str(dossier.resolve()),
              "statut": "erreur_technique", "nb_candidats": 0, "nb_rejets": 0,
              "generation_tentee": False, "generation_reponse_recue": False}
    with ExitStack() as pile:
        fichiers = {nom: pile.enter_context((dossier / nom).open("x", encoding="utf-8", newline="\n"))
                    for nom in ("traces.jsonl", "candidates.jsonl", "rejected.jsonl")}
        phase = "deduplication"
        try:
            vues, antecedents = validation.charger_questions_vues(racine, exclure=dossier)
            _ligne(fichiers["traces.jsonl"], {"phase": phase, "fichiers": antecedents})
            phase = "preparation_qwen"
            qwen = client_qwen.preparer_requete(preparation["prompt"], autoriser_telechargement)
            _ligne(fichiers["traces.jsonl"], {"phase": phase, "qwen": qwen})
            phase = "generation"
            resume["generation_tentee"] = True
            _ligne(fichiers["traces.jsonl"], {"phase": phase, "evenement": "debut_appel"})
            resultat = client_qwen.generer(qwen)
            resume["generation_reponse_recue"] = True
            _ligne(fichiers["traces.jsonl"], {"phase": phase, "resultat": resultat})
            resume["mesures"] = {c: resultat["reponse_ollama"].get(c)
                                 for c in ("done", "done_reason", "prompt_eval_count", "eval_count")}
            resume["mesures"]["nb_tokens_hf"] = qwen["entree"]["nb_tokens_hf"]
            resume["comptage_ollama_compare"] = resultat["comptage_ollama_compare"]
            if resultat["erreurs_techniques"]:
                raise client_qwen.ErreurQwen(" ; ".join(resultat["erreurs_techniques"]))
            phase = "validation_automatique"
            candidat = validation.valider_proposition(resultat["reponse_brute"], preparation, run_id, vues)
            _ligne(fichiers["candidates.jsonl"], candidat.model_dump())
            resume.update({"statut": "candidat_prepare", "nb_candidats": 1,
                           "id": candidat.id, "question_proposee": candidat.question,
                           "relecture_humaine": candidat.validation.human})
        except (ValueError, OSError, UnicodeDecodeError) as exc:
            statut = "rejet_automatique" if phase == "validation_automatique" else "erreur_technique"
            rejet = {"run_id": run_id, "phase": phase, "statut": statut, "motif": str(exc),
                     "diagnostic": getattr(exc, "diagnostic", {})}
            _ligne(fichiers["traces.jsonl"], {"evenement": "erreur", **rejet})
            _ligne(fichiers["rejected.jsonl"], rejet)
            resume.update({"statut": statut, "nb_rejets": 1, "motif": str(exc)})
    corpus.enregistrer_manifeste(resume, dossier / "summary.json")
    return resume
