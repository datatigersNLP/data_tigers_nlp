"""Récupération de la chaîne de démonstration du volet B (#172), sans dépendance au dossier data/ ni à la #166.

Chaînes mesurées par le protocole 10 (famille B) : partie lexicale par BM25 V3 ; fusion RRF (k = 60) des 100 premiers
rangs de la partie dense et de BM25 ; reclassement des 20 premiers candidats par bge-reranker-v2-m3 sur l'en-tête et le
texte ; 10 passages dans le budget de tokens du prompt (consigne v1, `rag.CONSIGNE_RAG`). Deux parties denses :
- `dense="base"`, état R1, retenu par la règle de maintien du protocole 10 : l'E5 de base fp32 et l'index de référence ;
- `dense="ajuste"`, état R2 : l'encodeur ajusté v1 du volet A (#49, #164), requête encodée par le q8 élagué que sert le
  site (`front/public/modele/`, onnxruntime), passages par l'index fp32 du site (`front/public/index_ajuste/`).

L'en-tête des passages (titre de la fiche, section, intertitres), entrée de BM25 V3 et du reclasseur, est reconstruit
depuis les métadonnées versionnées de l'index par la règle du notebook 01 (`entete`) : un test vérifie l'égalité avec le
parquet M2 pour les 4 240 passages quand il est présent. Les fichiers verrouillés de la mesure (#131) sont réutilisés
sans modification : `rag.py`, `generation.py`, `recuperation.py`, `lexical_baselines.py`.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Callable, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recuperation as rc  # noqa: E402  (ajoute scripts/rag et scripts/evaluation au chemin)
import rag  # noqa: E402

RACINE = rc.RACINE
MODELE_Q8 = RACINE / "front" / "public" / "modele" / "multilingual-e5-small-ajuste-q8-elague-13ed78c9"
SHA256_Q8 = "13ed78c9bf0c4e4ba2d36d0f715568edfb341a44051225f0b0a0e0214bf991d4"            # manifeste.json du modèle
SHA256_TOKENISEUR_Q8 = "b4f51d4228181f14ef705d2afec4d2fda41096e67ba0df359cb83ee20ebdc2c6"  # tokeniseur élagué
DOSSIER_INDEX_AJUSTE = RACINE / "front" / "public" / "index_ajuste"
CONFIGURATION = rc.Configuration(k=10, source="rrf", reclasseur="bge-m3", candidats=20)
PROFONDEUR = 100
DENSES = ("base", "ajuste")   # la première est celle par défaut (R1, protocole 10)


def sha256_octets(octets: bytes) -> str:
    return hashlib.sha256(octets).hexdigest()


def mots_vides_locaux() -> set[str]:
    """Lire la liste préparée sans utiliser le téléchargement automatique de lexical_baselines."""
    from lexical_baselines import MOTS_VIDES_CACHE, MOTS_VIDES_SHA256, TERMES_NEGATION_RESTRICTION
    try:
        octets = MOTS_VIDES_CACHE.read_bytes()
    except FileNotFoundError as exc:
        raise rc.ErreurRecuperationV2("Liste Snowball absente du cache ; préparer le cache avec connexion "
                                    "avant la démonstration (voir demo_b/README.md).") from exc
    if sha256_octets(octets) != MOTS_VIDES_SHA256:
        raise rc.ErreurRecuperationV2("Empreinte de la liste Snowball incorrecte ; réparer le cache "
                                    "avant la démonstration (voir demo_b/README.md).")
    mots = {ligne.split("|")[0].strip() for ligne in octets.decode("utf-8").splitlines()} - {""}
    return mots - TERMES_NEGATION_RESTRICTION


def entete(passage: dict) -> str:
    """Règle du notebook 01 (`entete`) : « fiche > section > intertitres », sans le chapô ni une section qui répète le
    titre de la fiche. Le chapô est la seule section dont le titre est « Chapô » (vérifié sur les 4 240 passages)."""
    parties = [passage["titre_fiche"]]
    if passage["section_titre"] not in ("Chapô", passage["titre_fiche"]):
        parties.append(passage["section_titre"])
    return " > ".join([*parties, *passage["chemin"]])


def textes_lexicaux(passages: Sequence[dict]) -> list[str]:
    """Entrée de BM25 V3 et du reclasseur, comme `recuperation.textes_lexicaux` : en-tête, saut de ligne, texte."""
    return [entete(p) + "\n" + p["texte"] for p in passages]


class IndexAjuste:
    """Matrice fp32 de l'encodeur ajusté servie par le site ; `rag.charger_index` la refuse à dessein (il n'admet que
    l'index de référence). Refusée si son empreinte diffère de son en-tête, si sa forme ou ses normes sont inattendues,
    ou si ses passages ne sont pas, octet pour octet, ceux de l'index de référence."""

    def __init__(self, index_base: rag.IndexCommun, dossier: Path = DOSSIER_INDEX_AJUSTE,
                 dossier_base: Path = rag.DOSSIER_INDEX):
        dossier, dossier_base = Path(dossier), Path(dossier_base)
        self.entete = json.loads((dossier / "index_m2.json").read_text(encoding="utf-8"))
        bloc = self.entete["index"]
        octets = (dossier / bloc["fichier"]).read_bytes()
        if sha256_octets(octets) != bloc["sha256"]:
            raise rc.ErreurRecuperationV2("Index ajusté : empreinte différente de son en-tête")
        passages = (dossier / "passages_m2.json").read_bytes()
        if passages != (dossier_base / "passages_m2.json").read_bytes():
            raise rc.ErreurRecuperationV2("Index ajusté : passages différents de ceux de l'index de référence")
        n, d = bloc["nb_vecteurs"], bloc["dimension"]
        if len(octets) != 4 * n * d or n != len(index_base.passages) or d != index_base.matrice.shape[1]:
            raise rc.ErreurRecuperationV2("Index ajusté : forme incompatible avec l'index de référence")
        self.matrice = np.frombuffer(octets, dtype="<f4").reshape(n, d)
        if not np.isfinite(self.matrice).all() or np.abs(np.linalg.norm(self.matrice, axis=1) - 1).max() >= 1e-4:
            raise rc.ErreurRecuperationV2("Index ajusté : vecteurs non finis ou non normalisés")
        self.sha256 = bloc["sha256"]


class EncodeurQ8:
    """Requête encodée par le q8 élagué de l'encodeur ajusté que sert le site, avec onnxruntime sur processeur :
    préfixe `query: `, moyenne des états de sortie pondérée par le masque, normalisation L2. Une question à la fois : la
    quantification dynamique calcule son échelle sur tout le lot, remplissage compris. Même calcul que l'instrument de
    mesure du protocole 10 (`scripts/evaluation/mesures_10.py`)."""

    def __init__(self, dossier: Path = MODELE_Q8, sha256_attendu: str = SHA256_Q8,
                 sha256_tokeniseur: str = SHA256_TOKENISEUR_Q8):
        import onnxruntime as ort
        from tokenizers import Tokenizer
        dossier = Path(dossier)
        onnx = (dossier / "onnx" / "model_quantized.onnx").read_bytes()
        tokeniseur = (dossier / "tokenizer.json").read_bytes()
        if sha256_octets(onnx) != sha256_attendu or sha256_octets(tokeniseur) != sha256_tokeniseur:
            raise rag.ErreurRecuperation("q8 de l'encodeur ajusté : empreinte du modèle ou du tokeniseur inattendue")
        self.tok = Tokenizer.from_str(tokeniseur.decode("utf-8"))
        self.session = ort.InferenceSession(onnx, providers=["CPUExecutionProvider"])
        self.entrees = {i.name for i in self.session.get_inputs()}
        self.sha256 = sha256_attendu

    def encoder(self, question: str) -> np.ndarray:
        if not isinstance(question, str) or not question.strip():
            raise rag.ErreurRecuperation("Question vide")
        e = self.tok.encode("query: " + question)
        if len(e.ids) > rag.BUDGET_E5:
            raise rag.ErreurRecuperation(f"Question de {len(e.ids)} tokens, limite {rag.BUDGET_E5} ; "
                                         "aucune troncature appliquée")
        donnees = {"input_ids": np.array([e.ids], dtype=np.int64),
                   "attention_mask": np.array([e.attention_mask], dtype=np.int64),
                   "token_type_ids": np.zeros((1, len(e.ids)), dtype=np.int64)}
        etats = self.session.run(None, {k: v for k, v in donnees.items() if k in self.entrees})[0][0]
        masque = np.array(e.attention_mask, dtype=np.float32)[:, None]
        v = (etats * masque).sum(axis=0) / masque.sum()
        v = (v / np.linalg.norm(v)).astype(np.float32)
        rag._verifier_vecteur(v)
        return v


class RecuperationDemo:
    """Les outils chargés une fois ; `recuperer` rend le contexte d'une question et les scores à afficher.

    Les composants sont injectables pour les tests : encoder(question) -> vecteur, matrice dense, reclasseur
    (méthode scores(question, textes)), mesurer(question, indices) -> nombre de tokens du prompt.
    """

    def __init__(self, passages: Sequence[dict], encoder: Callable[[str], np.ndarray], matrice: np.ndarray,
                 reclasseur, mesurer: Callable[[str, list[int]], int], description: dict,
                 mots_vides: set[str] | None = None):
        from lexical_baselines import BM25Retriever
        self.passages, self.encoder, self.matrice = passages, encoder, matrice
        self.reclasseur, self.mesurer, self.description = reclasseur, mesurer, description
        self.textes = textes_lexicaux(passages)
        self.bm25 = BM25Retriever(stopwords_variant=None, stemming="french")
        self.bm25.tokenizer.stopwords = mots_vides if mots_vides is not None else mots_vides_locaux()
        self.bm25.fit(self.textes, doc_ids=[p["passage_id"] for p in passages])

    @classmethod
    def charger(cls, dense: str = "base", index_base: rag.IndexCommun | None = None) -> "RecuperationDemo":
        if dense not in DENSES:
            raise rc.ErreurRecuperationV2(f"Partie dense inconnue : {dense}")
        mots_vides = mots_vides_locaux()
        index_base = index_base or rag.charger_index()
        if dense == "ajuste":
            index_aj, q8 = IndexAjuste(index_base), EncodeurQ8()
            encoder, matrice = q8.encoder, index_aj.matrice
            description = {"dense": "E5 ajusté v1 (#49, #164), requête q8 élaguée servie par le site, onnxruntime",
                           "sha256_q8": q8.sha256, "sha256_index_dense": index_aj.sha256}
        else:
            e5 = rag.charger_encodeur()
            encoder, matrice = (lambda q: rag.encoder_question(e5, q)), index_base.matrice
            description = {"dense": f"E5 de base fp32 ({rag.MODELE_E5}, {rag.REVISION_E5[:8]})",
                           "sha256_index_dense": index_base.entete["index"]["sha256"]}
        tok = rc.generation.charger_tokeniseur_qwen()
        passages = index_base.passages

        def mesurer(question, indices):
            return rc.compter_tokens(tok, rc.construire_contexte_v2(question, indices, passages))

        reclasseur = rc.Reclasseur(CONFIGURATION.reclasseur)
        description.update({"etat": "R2" if dense == "ajuste" else "R1", "configuration": CONFIGURATION.nom,
                            "reclasseur": f"{reclasseur.nom} ({reclasseur.revision[:8]})",
                            "lexical": "BM25 V3 (mots vides Snowball sans négations, racinisation française)",
                            "seuil_S": None})
        return cls(passages, encoder, matrice, reclasseur, mesurer, description, mots_vides=mots_vides)

    def recuperer(self, question: str) -> dict:
        vecteur = self.encoder(question)
        scores_denses = self.matrice @ vecteur
        liste_dense = rc.classement(scores_denses)[:PROFONDEUR].tolist()
        liste_bm25 = rc.classement(self.bm25.score_matrix([question])[0], positifs=True)[:PROFONDEUR].tolist()
        candidats = rc.fusion_rrf([liste_dense, liste_bm25])[:CONFIGURATION.candidats]
        scores_rc = np.asarray(self.reclasseur.scores(question, [self.textes[i] for i in candidats]), dtype=np.float64)
        ordre = rc.classement_final(CONFIGURATION, liste_dense, liste_bm25, dict(zip(candidats, scores_rc.tolist())),
                                    profondeur=PROFONDEUR)
        groupes = rc.groupes_du_contexte(ordre[:CONFIGURATION.k], [None] * len(self.passages), False)
        indices, retires = rc.dans_le_budget(groupes, lambda ind: self.mesurer(question, ind))
        return {"contexte": [int(i) for i in indices], "scores_denses": scores_denses,
                "score_dense_max": float(scores_denses[liste_dense[0]]),
                "candidats": [int(i) for i in candidats], "scores_reclasseur": scores_rc.tolist(),
                "groupes_retires": retires, "tokens": self.mesurer(question, indices)}
