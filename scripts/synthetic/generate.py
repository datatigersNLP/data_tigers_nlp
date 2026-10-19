"""Préparer ou générer un candidat Agent0 Light traçable (#93/#94)."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

if __package__:
    from . import corpus, prompts
else:
    import corpus
    import prompts


DOSSIER_RUNS = corpus.RACINE / "data" / "synthetic"


class ErreurPreparation(ValueError):
    """Sélection incompatible, source modifiée ou groupe non pris en charge."""


def _objet_unique(paires: list[tuple]) -> dict:
    resultat = {}
    for cle, valeur in paires:
        if cle in resultat:
            raise ErreurPreparation(f"Clé JSON dupliquée : {cle}")
        resultat[cle] = valeur
    return resultat


def _constante_interdite(valeur: str):
    raise ErreurPreparation(f"Constante JSON interdite : {valeur}")


def charger_selection(chemin: Path, source: corpus.CorpusM2) -> tuple[dict, str]:
    """Vérifie chaque passage du manifeste contre les métadonnées du corpus contrôlé."""
    octets = chemin.read_bytes()
    selection = json.loads(octets.decode("utf-8"), object_pairs_hook=_objet_unique,
                           parse_constant=_constante_interdite)
    if (not isinstance(selection, dict) or selection.get("format") != "agent0-sources-v1"
            or selection.get("algorithme") != corpus.ALGORITHME
            or selection.get("mode") not in ("fiches", "paires", "ids")
            or selection.get("ollama_appele") is not False
            or selection.get("matrice_lue") is not False
            or not isinstance(selection.get("code"), dict)):
        raise ErreurPreparation("Manifeste de sources #92 attendu")
    graine = selection.get("graine")
    if ((selection["mode"] == "ids" and graine is not None)
            or (selection["mode"] != "ids" and type(graine) is not int)):
        raise ErreurPreparation("Graine incompatible avec le mode de sélection")
    attendu = {"sha256_entete": source.sha256_entete, "sha256_passages": source.sha256_passages,
               "nb_passages": len(source.passages),
               "nb_fiches": len({p["url"] for p in source.passages})}
    meta = selection.get("corpus")
    if (meta != attendu or type(meta.get("nb_passages")) is not int
            or type(meta.get("nb_fiches")) is not int):
        raise ErreurPreparation("La sélection ne correspond pas au corpus contrôlé")
    groupes = selection.get("groupes")
    if not isinstance(groupes, list) or not groupes:
        raise ErreurPreparation("La sélection doit contenir des groupes non vides")
    par_id = {p["passage_id"]: p for p in source.passages}
    vus = set()
    for groupe in groupes:
        if not isinstance(groupe, list) or not groupe:
            raise ErreurPreparation("Groupe de sources vide ou invalide")
        for passage in groupe:
            identifiant = passage.get("passage_id") if isinstance(passage, dict) else None
            if not isinstance(identifiant, str) or identifiant not in par_id:
                raise ErreurPreparation("Identifiant de source inconnu")
            if identifiant in vus or passage != par_id[identifiant]:
                raise ErreurPreparation("Passage dupliqué ou différent du corpus contrôlé")
            vus.add(identifiant)
    return selection, hashlib.sha256(octets).hexdigest()


def preparer(selection: dict, empreinte: str, groupe: int, categorie: str,
             difficulte: str = "easy") -> dict:
    """Prépare un seul exercice ; ni inférence ni contrôle du budget de tokens ici."""
    if type(groupe) is not int or not 1 <= groupe <= len(selection["groupes"]):
        raise ErreurPreparation("Numéro de groupe hors sélection (numérotation à partir de 1)")
    passages = selection["groupes"][groupe - 1]
    if categorie == "multi_passage":
        if len(passages) != 2:
            raise ErreurPreparation("Multi-passage exige un groupe de deux passages")
        prompt = prompts.preparer_prompt_multiple(passages, difficulte)
        sources = {"sources": passages}
        version = "agent0-preparation-v2"
    elif categorie == "adversarial":
        if len(passages) != 1:
            raise ErreurPreparation("Adversarial exige un groupe d'un seul passage")
        prompt = prompts.preparer_prompt_adversarial(passages[0], difficulte)
        sources = {"source": passages[0]}
        version = "agent0-preparation-v1"
    else:
        if len(passages) != 1:
            raise ErreurPreparation("Simple et reformulation exigent un groupe d'un seul passage")
        prompt = prompts.preparer_prompt(passages[0], categorie, difficulte)
        sources = {"source": passages[0]}
        version = "agent0-preparation-v1"
    octets_prompt = json.dumps(prompt, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return {"format": version, "statut": "prompt_prepare",
            "type": categorie, "difficulty_target": difficulte,
            "selection": {**{c: selection[c] for c in ("format", "algorithme", "mode", "graine", "code")},
                          "sha256_fichier": empreinte, "groupe": groupe},
            "corpus": selection["corpus"], **sources,
            "prompt": prompt, "sha256_prompt": hashlib.sha256(octets_prompt).hexdigest(),
            "ollama_appele": False, "matrice_lue": False, "budget_tokens_verifie": False}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare-only", action="store_true", help="aperçu hors ligne")
    modes.add_argument("--prepare-qwen", action="store_true",
                       help="vérifier modèle, gabarit et budget, sans génération")
    modes.add_argument("--generate", action="store_true", help="un appel, un candidat ou un rejet tracé")
    parser.add_argument("--run-id", help="nouveau lot, requis avec --generate")
    parser.add_argument("--allow-tokenizer-download", action="store_true",
                        help="autoriser le téléchargement du seul tokeniseur figé")
    parser.add_argument("--sources", type=Path, required=True, help="manifeste produit par corpus.py")
    parser.add_argument("--group", type=int, default=1, help="groupe de la sélection, à partir de 1")
    parser.add_argument("--type", choices=prompts.CATEGORIES, required=True)
    parser.add_argument("--difficulty", choices=prompts.DIFFICULTES, default="easy")
    parser.add_argument("--index-dir", type=Path, default=corpus.DOSSIER_INDEX)
    parser.add_argument("--output", type=Path, help="nouveau fichier UTF-8, sans écrasement")
    args = parser.parse_args(argv)
    if args.allow_tokenizer_download and not (args.prepare_qwen or args.generate):
        parser.error("--allow-tokenizer-download exige --prepare-qwen ou --generate")
    if args.generate and (not args.run_id or args.output):
        parser.error("--generate exige --run-id et n'utilise pas --output")
    if not args.generate and args.run_id is not None:
        parser.error("--run-id s'utilise seulement avec --generate")
    try:
        if args.output and args.output.exists():
            raise ErreurPreparation("Le fichier de sortie existe déjà ; choisir un autre nom")
        source = corpus.charger_corpus(args.index_dir)
        selection, empreinte = charger_selection(args.sources, source)
        preparation = preparer(selection, empreinte, args.group, args.type, args.difficulty)
        preparation["code"] = corpus.provenance_code()
        preparation["code"]["sha256_fichiers"] = {
            nom: hashlib.sha256(Path(__file__).with_name(nom).read_bytes()).hexdigest()
            for nom in ("generate.py", "prompts.py", "schema.py")}
        if args.generate:
            if __package__:
                from . import run
            else:
                import run
            resultat = run.executer(preparation, args.run_id, DOSSIER_RUNS, args.allow_tokenizer_download)
            print(json.dumps(resultat, ensure_ascii=False, indent=2))
            return 0 if resultat["statut"] == "candidat_prepare" else 1
        if args.prepare_qwen:
            if __package__:
                from . import client_qwen
            else:
                import client_qwen
            preparation["qwen"] = client_qwen.preparer_requete(
                preparation["prompt"], args.allow_tokenizer_download)
            preparation.update({"statut": "requete_preparee", "ollama_appele": True,
                                "budget_tokens_verifie": True, "generation_appelee": False})
            preparation["code"]["sha256_fichiers"]["client_qwen.py"] = hashlib.sha256(
                Path(client_qwen.__file__).read_bytes()).hexdigest()
        if args.output:
            corpus.enregistrer_manifeste(preparation, args.output)
            resultat = {c: preparation[c] for c in ("statut", "type", "difficulty_target", "code",
                        "sha256_prompt", "ollama_appele", "matrice_lue", "budget_tokens_verifie")}
            if args.type == "multi_passage":
                resultat["source_ids"] = [p["passage_id"] for p in preparation["sources"]]
            else:
                resultat["passage_id"] = preparation["source"]["passage_id"]
            resultat.update({"version_prompt": preparation["prompt"]["version"],
                             "output": str(args.output.resolve())})
            if args.prepare_qwen:
                resultat.update({"generation_appelee": False, "ollama": {
                    c: preparation["qwen"]["ollama"][c] for c in ("version", "modele", "digest")},
                    "budget": {c: v for c, v in preparation["qwen"]["entree"].items()
                               if c != "texte"}, "versions": preparation["qwen"]["versions"]})
        else:
            resultat = preparation
    except (ValueError, OSError, UnicodeDecodeError) as exc:
        print(f"Préparation refusée : {exc}", file=sys.stderr)
        return 1
    print(json.dumps(resultat, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
