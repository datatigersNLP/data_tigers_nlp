"""Modèle et budget Qwen de #93 ; aucun appel de génération dans cet incrément.

Garde-fous adaptés des helpers publics de scripts/rag/generation.py, PR #85,
commit df91b85981607c722f191f0205fc3072f0a62b8c. Aucun import du RAG en review.
"""

import copy
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import urllib.request


API_OLLAMA = "http://127.0.0.1:11434"
MODELE_QWEN = "qwen2.5-7b-instruct:q4_k_m-local"
DIGEST_QWEN = "6ec54444a8511aae6c2116b172eb3685d1416c523bfee0252ca33c7e55c481e4"
TOKENISEUR_QWEN = "Qwen/Qwen2.5-7B-Instruct"
REVISION_TOKENISEUR = "a09a35458c702b33eeacc393d103063234e8bc28"
NUM_CTX = 8192
NUM_PREDICT = 512
MARGE_TOKENS = 64
OPTIONS = {"temperature": 0.0, "seed": 20261018, "num_ctx": NUM_CTX,
           "num_predict": NUM_PREDICT,
           "stop": ["<|im_end|>", "<|endoftext|>", "<|im_start|>"]}


class ErreurQwen(ValueError):
    """Échec technique, jamais un jugement sur la qualité d'une question."""


def _api(route: str, donnees=None) -> dict:
    if route not in ("/api/version", "/api/tags", "/api/show"):
        raise ErreurQwen("Seules les métadonnées Ollama sont accessibles à cet incrément")
    octets = None if donnees is None else json.dumps(donnees, ensure_ascii=False).encode("utf-8")
    requete = urllib.request.Request(API_OLLAMA + route, data=octets,
                                    headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(requete, timeout=5) as reponse:
            resultat = json.loads(reponse.read().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ErreurQwen(f"Ollama {route} : {exc}") from exc
    if not isinstance(resultat, dict) or resultat.get("error"):
        raise ErreurQwen(f"Ollama {route} : objet JSON attendu, sans erreur du serveur")
    return resultat


def verifier_ollama() -> dict:
    version_ollama = _api("/api/version").get("version")
    catalogue = _api("/api/tags").get("models")
    if not isinstance(catalogue, list):
        raise ErreurQwen("Catalogue Ollama invalide")
    entrees = [m for m in catalogue if isinstance(m, dict) and m.get("name") == MODELE_QWEN]
    if len(entrees) != 1:
        raise ErreurQwen(f"Modèle absent ou ambigu : {MODELE_QWEN}")
    digest = entrees[0].get("digest")
    if not isinstance(digest, str) or digest.removeprefix("sha256:") != DIGEST_QWEN:
        raise ErreurQwen("Digest Qwen différent de la référence de #31/#85")
    infos = _api("/api/show", {"model": MODELE_QWEN})
    details, template = infos.get("details"), infos.get("template")
    if (not isinstance(details, dict) or details.get("format") != "gguf"
            or details.get("family") != "qwen2" or details.get("quantization_level") != "Q4_K_M"):
        raise ErreurQwen("Modèle attendu : GGUF qwen2 Q4_K_M")
    if (not isinstance(version_ollama, str) or not version_ollama.strip()
            or not isinstance(template, str) or not template.strip()):
        raise ErreurQwen("Version Ollama ou gabarit du modèle absent")
    return {"version": version_ollama, "modele": MODELE_QWEN, "digest": DIGEST_QWEN,
            "details": details, "template": template, "parameters": infos.get("parameters")}


def charger_tokeniseur_qwen(autoriser_telechargement: bool = False):
    """Utilise le cache local par défaut ; ne charge jamais les poids Qwen."""
    try:
        from transformers import AutoTokenizer
        return AutoTokenizer.from_pretrained(TOKENISEUR_QWEN, revision=REVISION_TOKENISEUR,
                                            trust_remote_code=False,
                                            local_files_only=not autoriser_telechargement)
    except Exception as exc:
        raise ErreurQwen(
            "Tokeniseur Qwen indisponible : installer les dépendances Agent0 et vérifier le cache. "
            "--allow-tokenizer-download autorise son téléchargement à la révision figée. "
            f"Détail : {exc}"
        ) from exc


def preparer_entree(messages: list[dict], template: str, tokeniseur) -> dict:
    """Compte le texte réellement préparé en raw, sans ajouter une seconde fois les balises."""
    if not isinstance(template, str) or not template.strip():
        raise ErreurQwen("Gabarit local non vide requis")
    if (not isinstance(messages, list) or len(messages) != 2
            or any(not isinstance(m, dict) or set(m) != {"role", "content"}
                   or not isinstance(m["content"], str) or not m["content"].strip() for m in messages)
            or [m["role"] for m in messages] != ["system", "user"]):
        raise ErreurQwen("Deux messages non vides system/user sont requis")
    try:
        texte = tokeniseur.apply_chat_template(messages, chat_template=template,
                                               tokenize=False, add_generation_prompt=True)
        attendu = ("<|im_start|>system\n" + messages[0]["content"] + "<|im_end|>\n"
                   + "<|im_start|>user\n" + messages[1]["content"] + "<|im_end|>\n"
                   + "<|im_start|>assistant\n")
        if texte != attendu:
            raise ErreurQwen("Gabarit local différent du format Qwen system/user attendu")
        ids = tokeniseur(texte, add_special_tokens=False, truncation=False)["input_ids"]
        if not isinstance(ids, list) or not ids or any(type(i) is not int for i in ids):
            raise ErreurQwen("Liste de tokens invalide")
    except ErreurQwen:
        raise
    except Exception as exc:
        raise ErreurQwen(f"Rendu du gabarit ou tokenisation impossible : {exc}") from exc
    nombre = len(ids)
    if nombre + NUM_PREDICT + MARGE_TOKENS > NUM_CTX:
        raise ErreurQwen(f"Budget dépassé : {nombre} + {NUM_PREDICT} + {MARGE_TOKENS} > {NUM_CTX}. "
                         "Aucun texte n'est tronqué et aucune génération n'est envoyée.")
    return {"texte": texte, "nb_tokens_hf": nombre,
            "sha256_texte": hashlib.sha256(texte.encode("utf-8")).hexdigest(),
            "sha256_template": hashlib.sha256(template.encode("utf-8")).hexdigest(),
            "tokeniseur": TOKENISEUR_QWEN, "revision_tokeniseur": REVISION_TOKENISEUR,
            "num_ctx": NUM_CTX, "num_predict": NUM_PREDICT, "marge_tokens": MARGE_TOKENS,
            "tokens_disponibles_entree": NUM_CTX - NUM_PREDICT - MARGE_TOKENS,
            "comptage_ollama_compare": False}


def preparer_requete(prompt: dict, autoriser_telechargement: bool = False) -> dict:
    """Construit une requête inspectable ; ne l'envoie jamais à /api/generate."""
    infos = verifier_ollama()
    tokeniseur = charger_tokeniseur_qwen(autoriser_telechargement)
    entree = preparer_entree(prompt["messages"], infos["template"], tokeniseur)
    if not isinstance(prompt.get("response_schema"), dict):
        raise ErreurQwen("Schéma JSON de sortie requis")
    versions = {}
    for paquet in ("transformers", "tokenizers", "jinja2"):
        try:
            versions[paquet] = version(paquet)
        except PackageNotFoundError:
            versions[paquet] = "absent"
    return {"ollama": infos, "entree": entree, "versions": versions,
            "requete": {"model": MODELE_QWEN, "prompt": entree["texte"],
                        "raw": True, "stream": False, "keep_alive": "30m",
                        "format": copy.deepcopy(prompt["response_schema"]),
                        "options": copy.deepcopy(OPTIONS)},
            "generation_appelee": False}
