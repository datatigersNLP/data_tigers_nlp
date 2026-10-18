"""Préparer une consigne Agent0 Light (#93), sans Ollama ni tokeniseur."""

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
    if len(passages) != 1:
        raise ErreurPreparation("Simple et reformulation exigent un groupe d'un seul passage")
    prompt = prompts.preparer_prompt(passages[0], categorie, difficulte)
    octets_prompt = json.dumps(prompt, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return {"format": "agent0-preparation-v1", "statut": "prompt_prepare",
            "type": categorie, "difficulty_target": difficulte,
            "selection": {**{c: selection[c] for c in ("format", "algorithme", "mode", "graine", "code")},
                          "sha256_fichier": empreinte, "groupe": groupe},
            "corpus": selection["corpus"], "source": passages[0],
            "prompt": prompt, "sha256_prompt": hashlib.sha256(octets_prompt).hexdigest(),
            "ollama_appele": False, "matrice_lue": False, "budget_tokens_verifie": False}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true", required=True,
                        help="seul mode disponible : aucune génération")
    parser.add_argument("--sources", type=Path, required=True, help="manifeste produit par corpus.py")
    parser.add_argument("--group", type=int, default=1, help="groupe de la sélection, à partir de 1")
    parser.add_argument("--type", choices=prompts.CATEGORIES, required=True)
    parser.add_argument("--difficulty", choices=prompts.DIFFICULTES, default="easy")
    parser.add_argument("--index-dir", type=Path, default=corpus.DOSSIER_INDEX)
    parser.add_argument("--output", type=Path, help="nouveau fichier UTF-8, sans écrasement")
    args = parser.parse_args(argv)
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
        if args.output:
            corpus.enregistrer_manifeste(preparation, args.output)
            resultat = {c: preparation[c] for c in ("statut", "type", "difficulty_target", "code",
                        "sha256_prompt", "ollama_appele", "matrice_lue", "budget_tokens_verifie")}
            resultat.update({"passage_id": preparation["source"]["passage_id"],
                             "version_prompt": preparation["prompt"]["version"],
                             "output": str(args.output.resolve())})
        else:
            resultat = preparation
    except (ValueError, OSError, UnicodeDecodeError) as exc:
        print(f"Préparation refusée : {exc}", file=sys.stderr)
        return 1
    print(json.dumps(resultat, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
