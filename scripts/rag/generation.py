"""Qwen local, budget et citations de la baseline #51. Aucun appel à l'import."""

import hashlib
import json
import re
import urllib.request


API_OLLAMA = "http://127.0.0.1:11434"
MODELE_QWEN = "qwen2.5-7b-instruct:q4_k_m-local"
DIGEST_QWEN_31 = "6ec54444a8511aae6c2116b172eb3685d1416c523bfee0252ca33c7e55c481e4"
TOKENISEUR_QWEN = "Qwen/Qwen2.5-7B-Instruct"
REVISION_TOKENISEUR = "a09a35458c702b33eeacc393d103063234e8bc28"
NUM_CTX = 8192
NUM_PREDICT = 512
MARGE_TOKENS = 64
OPTIONS = {"temperature": 0.0, "seed": 20261018, "num_predict": NUM_PREDICT,
           "num_ctx": NUM_CTX, "stop": ["<|im_end|>", "<|endoftext|>", "<|im_start|>"]}


class ErreurGeneration(ValueError):
    """Échec technique de préparation ou d'appel, jamais une abstention."""


def _api(route: str, donnees=None, timeout=5) -> dict:
    octets = None if donnees is None else json.dumps(donnees, ensure_ascii=False).encode("utf-8")
    requete = urllib.request.Request(API_OLLAMA + route, data=octets,
                                    headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(requete, timeout=timeout) as reponse:
            resultat = json.loads(reponse.read().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ErreurGeneration(f"Ollama {route} : {exc}") from exc
    if not isinstance(resultat, dict) or resultat.get("error"):
        raise ErreurGeneration(f"Ollama {route} : réponse JSON invalide ou erreur du serveur")
    return resultat


def verifier_ollama() -> dict:
    version = _api("/api/version").get("version")
    catalogue = _api("/api/tags").get("models", [])
    if not isinstance(catalogue, list):
        raise ErreurGeneration("Catalogue Ollama invalide")
    entrees = [m for m in catalogue if isinstance(m, dict) and m.get("name") == MODELE_QWEN]
    if len(entrees) != 1:
        raise ErreurGeneration(f"Modèle local absent ou ambigu : {MODELE_QWEN}")
    entree = entrees[0]
    digest = entree.get("digest")
    if not isinstance(digest, str):
        raise ErreurGeneration("Digest du modèle absent du catalogue Ollama")
    digest = digest.removeprefix("sha256:")
    if digest != DIGEST_QWEN_31:
        raise ErreurGeneration(
            f"Digest différent de #31 : {digest}. Vérifier le modèle avant de changer la référence."
        )
    infos = _api("/api/show", {"model": MODELE_QWEN})
    details = infos.get("details", {})
    if (not isinstance(details, dict) or details.get("format") != "gguf"
            or details.get("family") != "qwen2" or details.get("quantization_level") != "Q4_K_M"):
        raise ErreurGeneration("Modèle attendu : GGUF qwen2, Q4_K_M")
    template = infos.get("template")
    if not isinstance(version, str) or not isinstance(template, str) or not template.strip():
        raise ErreurGeneration("Version Ollama ou gabarit du modèle absent")
    return {"version": version, "modele": MODELE_QWEN, "digest": digest,
            "details": details, "template": template, "parameters": infos.get("parameters")}


def charger_tokeniseur_qwen():
    """Charge seulement le tokeniseur officiel figé, pas les poids génératifs."""
    try:
        from transformers import AutoTokenizer
        return AutoTokenizer.from_pretrained(TOKENISEUR_QWEN, revision=REVISION_TOKENISEUR,
                                            trust_remote_code=False)
    except Exception as exc:
        raise ErreurGeneration(f"Tokeniseur Qwen indisponible : {exc}") from exc


def preparer_entree(contexte: dict, template: str, tokeniseur) -> dict:
    """Rend le gabarit local, puis compte exactement le texte envoyé en raw.

    Le compte HF est contrôlé après l'appel contre prompt_eval_count d'Ollama :
    sa correspondance avec le tokeniseur GGUF n'est pas supposée acquise.
    """
    messages = [{"role": "system", "content": contexte["system"]},
                {"role": "user", "content": contexte["prompt"]}]
    try:
        texte = tokeniseur.apply_chat_template(messages, chat_template=template,
                                               tokenize=False, add_generation_prompt=True)
        attendu = ("<|im_start|>system\n" + contexte["system"] + "<|im_end|>\n"
                   + "<|im_start|>user\n" + contexte["prompt"] + "<|im_end|>\n"
                   + "<|im_start|>assistant\n")
        if texte != attendu:
            raise ErreurGeneration("Gabarit local différent du format Qwen system/user attendu")
        ids = tokeniseur(texte, add_special_tokens=False, truncation=False)["input_ids"]
    except ErreurGeneration:
        raise
    except Exception as exc:
        raise ErreurGeneration(f"Gabarit ou tokenisation Qwen impossible : {exc}") from exc
    nb_tokens = len(ids)
    if nb_tokens + NUM_PREDICT + MARGE_TOKENS > NUM_CTX:
        raise ErreurGeneration(
            f"Budget dépassé : {nb_tokens} + {NUM_PREDICT} + {MARGE_TOKENS} > {NUM_CTX}. "
            "Aucun passage n'est tronqué et aucun appel de génération n'est envoyé."
        )
    return {"texte": texte, "nb_tokens": nb_tokens,
            "sha256_texte": hashlib.sha256(texte.encode("utf-8")).hexdigest(),
            "sha256_template": hashlib.sha256(template.encode("utf-8")).hexdigest(),
            "tokeniseur": TOKENISEUR_QWEN, "revision_tokeniseur": REVISION_TOKENISEUR,
            "num_ctx": NUM_CTX, "num_predict": NUM_PREDICT, "marge_tokens": MARGE_TOKENS}


def valider_citations(texte: str, sources: list[dict], abstention: str) -> dict:
    """Contrôle structurel strict ; aucune vérification de justification sémantique."""
    reponse = texte.strip()
    base = {"justification_semantique_verifiee": False,
            "couverture_des_affirmations_verifiee": False}
    if reponse == abstention:
        return {**base, "statut": "abstention_modele", "citations": [],
                "citations_invalides": [], "motifs": []}
    autorisees = {s["reference"] for s in sources}
    # Tout groupe entre crochets est soumis au format contrôlé ; une ouverture
    # non fermée est également capturée. [P1][P2] est accepté, [P1, P2] refusé.
    groupes = re.findall(r"\[[^\]\n]*(?:\]|(?=\n|$))", reponse)
    valides = list(dict.fromkeys(g for g in groupes if g in autorisees))
    invalides = list(dict.fromkeys(g for g in groupes if g not in autorisees))
    motifs = []
    if not reponse:
        motifs.append("reponse_vide")
    if not valides:
        motifs.append("aucune_citation_valide")
    if invalides:
        motifs.append("reference_absente_ou_mal_formee")
    if abstention in reponse:
        motifs.append("abstention_melangee_a_une_autre_sortie")
    return {**base, "statut": "sortie_invalide" if motifs else "reponse_citee",
            "citations": valides, "citations_invalides": invalides, "motifs": motifs}


def generer_reponse(contexte: dict, abstention: str) -> dict:
    infos = verifier_ollama()
    tokeniseur = charger_tokeniseur_qwen()
    entree = preparer_entree(contexte, infos["template"], tokeniseur)
    # Le gabarit a déjà été rendu et compté. raw évite tout second habillage.
    requete = {"model": MODELE_QWEN, "prompt": entree["texte"], "raw": True,
               "stream": False, "keep_alive": "30m", "options": dict(OPTIONS)}
    resultat = _api("/api/generate", requete, timeout=300)
    texte = resultat.get("response")
    if not isinstance(texte, str):
        raise ErreurGeneration("Ollama n'a pas renvoyé de texte de réponse")
    validation = valider_citations(texte, contexte["sources"], abstention)
    erreurs = []
    if resultat.get("done") is not True or resultat.get("done_reason") != "stop":
        erreurs.append("generation_incomplete")
    if (type(resultat.get("prompt_eval_count")) is not int
            or resultat["prompt_eval_count"] != entree["nb_tokens"]):
        erreurs.append("comptage_tokens_ollama_different_du_compte_hf")
    if type(resultat.get("eval_count")) is not int or not 0 < resultat["eval_count"] <= NUM_PREDICT:
        erreurs.append("nombre_tokens_sortie_invalide")
    champs = ("done", "done_reason", "prompt_eval_count", "eval_count", "total_duration",
              "load_duration", "prompt_eval_duration", "eval_duration")
    return {
        "statut": "erreur_technique" if erreurs else validation["statut"],
        "erreurs_techniques": erreurs, "reponse_brute": texte, "validation_citations": validation,
        "ollama": {k: v for k, v in infos.items() if k != "template"},
        "entree": entree, "parametres": {**OPTIONS, "raw": True, "stream": False, "keep_alive": "30m"},
        "mesures_ollama": {k: resultat.get(k) for k in champs},
    }
