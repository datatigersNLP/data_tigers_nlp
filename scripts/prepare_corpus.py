"""Préparation du corpus travail-emploi (ticket #27, domaine D1).

Télécharge l'instantané figé du 11/09/2026, vérifie son empreinte, applique les règles
de filtrage, compte les tokens de chaque passage et écrit le corpus filtré dans data/processed/.

Règles, toutes évaluées sur la colonne `text` (le contenu propre du passage) :
  R1  retirer les passages réduits au bouton « Échanger avec le bon conseiller… »
  R2  retirer les sections de liens : « Services en ligne », « À lire sur ce site »,
      « À lire sur service-public »
  R3  retirer les fragments de moins de SEUIL caractères
  R4  marquer dans `doublon_text` les passages dont le `text` est identique à celui d'un
      passage précédent (première occurrence non marquée) ; avec --sans-doublons, les retirer

Une ligne retirée l'est en entier : `text` et `chunk_text` partent ensemble.

Le nombre de tokens de `text` et de `chunk_text` est compté avec le tokeniseur de l'encodeur
retenu au jalon J2 (Xenova/multilingual-e5-small), tokens spéciaux compris, sans préfixe E5.

Dépendances : pandas, pyarrow, tokenizers.

Usage, depuis la racine du dépôt :
    python scripts/prepare_corpus.py                  # doublons marqués
    python scripts/prepare_corpus.py --sans-doublons  # doublons retirés
"""
import argparse
import hashlib
import json
import os
import urllib.request
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parent.parent

# source figée : commit Hugging Face du 25/09/2026, instantané du 11/09/2026
COMMIT = "98744a63d40d982ff8b5345ca635ad543a412163"
CHEMIN_HF = "data/travail-emploi-20260911/travail_emploi_part_0.parquet"
URL = f"https://huggingface.co/datasets/AgentPublic/travail-emploi/resolve/{COMMIT}/{CHEMIN_HF}"
SHA256 = "b76ab4c4408b737fadaade549dfa7734ec9b3343b7c19f0285cf3c6cd858ef4f"

BRUT = RACINE / "data/raw/travail-emploi-20260911/travail_emploi_part_0.parquet"
SORTIE = RACINE / "data/processed"

PHRASE_NAV = r"Échanger avec le bon conseiller pour votre entreprise sur Conseillers[- ]Entreprises? Service Public"
SECTIONS_LIENS = r"^(Services en ligne|À lire sur ce site|À lire sur service-public)"
SEUIL = 50

MOTIFS = {
    "R1": "bouton de navigation « Échanger avec le bon conseiller » seul",
    "R2": "section de liens vers d'autres pages",
    "R3": "fragment de moins de {seuil} caractères",
    "R4": "texte identique à celui d'un passage précédent",
}

# tokeniseur de l'encodeur retenu au jalon J2, figé sur un commit Hugging Face
TOKENISEUR = "Xenova/multilingual-e5-small"
REVISION_TOKENISEUR = "761b726dd34fb83930e26aab4e9ac3899aa1fa78"
LIMITE_TOKENS = 512            # au-delà, l'encodeur tronque l'entrée
PREFIXE_PASSAGE = "passage: "  # préfixe attendu par les modèles E5 pour les passages


def empreinte(fichier):
    h = hashlib.sha256()
    with open(fichier, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def telecharger():
    """Télécharge le fichier brut s'il est absent, puis vérifie son empreinte."""
    if not BRUT.exists():
        print(f"téléchargement de {URL}")
        BRUT.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL, BRUT)
    if empreinte(BRUT) != SHA256:
        raise SystemExit(f"empreinte SHA-256 inattendue pour {BRUT} : fichier corrompu ou autre version")
    print(f"fichier brut vérifié : {BRUT.relative_to(RACINE)}")


def lignes_retirees(df, regles, section, seuil):
    """Met en forme les passages retirés, avec la règle retenue et toutes les règles concernées."""
    retire = regles.any(axis=1)
    retires = df.loc[retire, ["chunk_id", "doc_id", "chunk_index", "title", "text"]].copy()
    # règle retenue pour un passage concerné par plusieurs : la première dans l'ordre des colonnes
    regle = regles[retire].idxmax(axis=1)
    retires.insert(0, "regle", regle)
    retires.insert(1, "motif", regle.map(lambda r: MOTIFS[r].format(seuil=seuil)))
    retires.insert(2, "toutes_regles", regles[retire].apply(lambda l: ", ".join(l.index[l]), axis=1))
    retires.insert(6, "section", section[retire])
    return retires


def filtrer(df, seuil, sans_doublons):
    """Renvoie (corpus filtré, passages retirés, règles prises isolément), sans modifier aucun texte."""
    texte = df["text"].str.strip()
    section = df["context"].apply(lambda x: x[0])

    regles = pd.DataFrame({
        "R1": texte.str.fullmatch(PHRASE_NAV),
        "R2": section.str.match(SECTIONS_LIENS),
        "R3": texte.str.len() < seuil,
    })
    garde = df[~regles.any(axis=1)].copy()
    garde["doublon_text"] = garde["text"].str.strip().duplicated(keep="first")
    # R4 ne porte que sur les passages conservés par R1, R2 et R3
    regles["R4"] = df.index.isin(garde.index[garde["doublon_text"]])

    appliquees = regles if sans_doublons else regles[["R1", "R2", "R3"]]
    retires = lignes_retirees(df, appliquees, section, seuil)
    if sans_doublons:
        garde = garde[~garde["doublon_text"]]
    return garde, retires, regles


def compter_tokens(garde):
    """Ajoute le nombre de tokens de text et de chunk_text, tokens spéciaux compris."""
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    from tokenizers import Tokenizer

    tokeniseur = Tokenizer.from_pretrained(TOKENISEUR, revision=REVISION_TOKENISEUR)
    for col in ("text", "chunk_text"):
        garde[f"tokens_{col}"] = [len(e.ids) for e in tokeniseur.encode_batch(garde[col].tolist())]
    return len(tokeniseur.encode(PREFIXE_PASSAGE, add_special_tokens=False).ids)


def mesurer(df):
    return {
        "passages": int(len(df)),
        "fiches": int(df["doc_id"].nunique()),
        "caracteres_text": int(df["text"].str.len().sum()),
    }


def decrit(valeur, description):
    """Associe une valeur à sa description : le format JSON n'admet pas de commentaires."""
    return {"valeur": valeur, "description": description}


def decrire_mesures(mesures, description):
    return {
        "description": description,
        "passages": decrit(mesures["passages"], "nombre de passages (lignes du corpus)"),
        "fiches": decrit(mesures["fiches"], "nombre de fiches distinctes (valeurs distinctes de doc_id)"),
        "caracteres_text": decrit(mesures["caracteres_text"],
                                  "total des caractères de la colonne text, additionnés sur tous les passages "
                                  "(espaces et ponctuation compris ; chunk_text n'est pas compté)"),
    }


def decrire_tokens(garde, n_prefixe):
    bloc = {"description": f"nombre de tokens compté avec le tokeniseur {TOKENISEUR} (révision "
                           f"{REVISION_TOKENISEUR[:7]}), tokens spéciaux compris ; l'encodeur tronque au-delà "
                           f"de {LIMITE_TOKENS} tokens"}
    for col in ("text", "chunk_text"):
        n = garde[f"tokens_{col}"]
        bloc[col] = {
            "maximum": decrit(int(n.max()), f"nombre de tokens du plus long {col}"),
            "mediane": decrit(float(n.median()), f"nombre médian de tokens de {col}"),
            "au_dela_limite": decrit(int((n > LIMITE_TOKENS).sum()),
                                     f"passages dont {col} dépasse {LIMITE_TOKENS} tokens"),
            "au_dela_limite_avec_prefixe": decrit(
                int((n + n_prefixe > LIMITE_TOKENS).sum()),
                f"passages dont {col} dépasse {LIMITE_TOKENS} tokens une fois ajouté le préfixe "
                f"« {PREFIXE_PASSAGE} » ({n_prefixe} tokens) attendu par les modèles E5"),
        }
    return bloc


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seuil", type=int, default=SEUIL,
                        help=f"longueur minimale de text en caractères pour R3 (défaut : {SEUIL})")
    parser.add_argument("--sans-doublons", action="store_true",
                        help="retirer les doublons de R4 au lieu de seulement les marquer")
    args = parser.parse_args()

    telecharger()
    df = pd.read_parquet(BRUT)
    garde, retires, regles = filtrer(df, args.seuil, args.sans_doublons)
    n_prefixe = compter_tokens(garde)

    SORTIE.mkdir(parents=True, exist_ok=True)
    fichier_filtre = SORTIE / "travail_emploi_filtre.parquet"
    garde.to_parquet(fichier_filtre, index=False, compression="zstd")   # même compression que la source
    # séparateur « ; » et BOM UTF-8 : le fichier s'ouvre directement en colonnes dans Excel en français
    retires.to_csv(SORTIE / "passages_retires.csv", index=False, sep=";", encoding="utf-8-sig")

    avant, apres = mesurer(df), mesurer(garde)
    isolement = {r: int(regles[r].sum()) for r in regles}
    par_regle = {r: int((retires["regle"] == r).sum()) for r in regles}
    doublons_marques = int(garde["doublon_text"].sum())

    stats = {
        "source": {
            "description": "fichier brut d'origine, figé sur un commit Hugging Face",
            "url": decrit(URL, "adresse de téléchargement de l'instantané du 11/09/2026"),
            "sha256": decrit(SHA256, "empreinte attendue du fichier brut ; vérifiée avant tout traitement"),
        },
        "seuil_R3": decrit(args.seuil, "longueur minimale de text, en caractères, en dessous de laquelle R3 retire le passage"),
        "doublons_retires": decrit(args.sans_doublons,
                                   "vrai si le script a été lancé avec --sans-doublons : R4 retire alors les doublons "
                                   "au lieu de seulement les marquer"),
        "avant": decrire_mesures(avant, "corpus brut, avant filtrage"),
        "regles_prises_isolement": {
            "description": "nombre de passages concernés par chaque règle prise seule ; un passage peut relever "
                           "de plusieurs règles, la somme dépasse donc le total retiré ; R4 ne porte que sur les "
                           "passages conservés par R1, R2 et R3",
            **{r: decrit(n, MOTIFS[r].format(seuil=args.seuil)) for r, n in isolement.items()},
        },
        "retires": {
            "description": "passages effectivement retirés, chacun compté une seule fois, "
                           "sous la première règle qui le concerne dans l'ordre R1, R2, R3, R4",
            "total": decrit(len(retires), "nombre total de passages retirés"),
            **{r: decrit(n, f"passages retirés au titre de {r}") for r, n in par_regle.items()},
        },
        "apres": decrire_mesures(apres, "corpus filtré tel qu'écrit dans travail_emploi_filtre.parquet"
                                        + (" ; doublons retirés par R4" if args.sans_doublons
                                           else " ; doublons marqués par R4 inclus")),
        "doublons_text_marques": decrit(doublons_marques,
                                        "passages du corpus filtré dont le text est identique à celui d'un passage "
                                        "précédent (colonne doublon_text = vrai) ; à écarter si l'encodage porte "
                                        "sur text ; vaut 0 avec --sans-doublons"),
        "apres_sans_doublons": decrire_mesures(mesurer(garde[~garde["doublon_text"]]),
                                               "corpus filtré sans les doublons de R4"),
        "tokens": decrire_tokens(garde, n_prefixe),
        "taille_fichier_filtre_octets": decrit(fichier_filtre.stat().st_size,
                                               "taille sur disque de travail_emploi_filtre.parquet, en octets ; "
                                               "surtout due à la colonne embeddings_bge-m3, conservée"),
    }
    (SORTIE / "stats_filtrage.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    t = stats["tokens"]
    print(f"règles prises isolément : {isolement}")
    print(f"passages retirés        : {len(retires)} {par_regle}")
    print(f"avant                   : {avant['passages']} passages, {avant['fiches']} fiches, {avant['caracteres_text']} caractères")
    print(f"après                   : {apres['passages']} passages, {apres['fiches']} fiches, {apres['caracteres_text']} caractères")
    print(f"doublons marqués (R4)   : {doublons_marques}")
    print(f"au-delà de {LIMITE_TOKENS} tokens    : text {t['text']['au_dela_limite']['valeur']}, "
          f"chunk_text {t['chunk_text']['au_dela_limite']['valeur']} "
          f"({t['chunk_text']['au_dela_limite_avec_prefixe']['valeur']} avec le préfixe E5)")
    print(f"sorties                 : {SORTIE.relative_to(RACINE)}/")


if __name__ == "__main__":
    main()
