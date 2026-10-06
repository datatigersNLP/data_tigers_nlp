"""
Module de références lexicales pour la recherche d'information (TF-IDF et BM25).

Conçu pour l'Issue #47 et réutilisable dans le Notebook 03 (Issue #46).
Supporte les passages M2 du corpus travail-emploi SocialGouv.

Variantes supportées :
1. Sans mots vides (stopwords_variant=None)
2. Mots vides Snowball (stopwords_variant='snowball') : la liste du projet Snowball, figée sur le même commit
   et contrôlée par la même empreinte que dans le notebook 01 et la validation sur PIAF (#45)
3. Mots vides Snowball sans les négations ni les restrictions (stopwords_variant='snowball_no_negation')
4. Avec et sans racinisation française Snowball (stemming='french' ou None)
5. Coupure par fréquence documentaire (min_df, max_df), appliquée à TF-IDF comme à BM25

BM25 : formule de Lucene par défaut (idf toujours positif, k1 = 1,2, b = 0,75), ou formule de rank_bm25
(idf="atire" : idf négatifs remplacés par epsilon fois l'idf moyen), reproduite à 1e-9 près.
Les classements suivent la règle d'ex aequo de metrics.rank_by_score. Un passage de score nul, qui ne partage
aucun mot avec la requête, n'est jamais renvoyé par search() ni batch_search().
"""

import gzip
import hashlib
import json
import math
import re
import unicodedata
import urllib.request
from collections import Counter
from pathlib import Path
from typing import List, Dict, Set, Union, Optional, Tuple, Any, Sequence

import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
import snowballstemmer

try:  # import en paquet (scripts.evaluation) ou depuis le dossier du module
    from .metrics import rank_by_score
except ImportError:
    from metrics import rank_by_score


# liste française du projet Snowball, figée sur le même commit que le notebook 01
MOTS_VIDES_URL = ("https://raw.githubusercontent.com/snowballstem/snowball-website/"
                  "5a8cf2451d108217585d8e32d744f8b8fd20c711/algorithms/french/stop.txt")
MOTS_VIDES_SHA256 = "e235f5e633bf831c601ce6f1dc87d8608c038209a7aab64e69a9e70f52f83d4c"
MOTS_VIDES_CACHE = Path(__file__).resolve().parents[2] / "data" / "evaluation" / "mots_vides_snowball.txt"

# Mots à forte valeur juridique et restrictive à préserver impérativement en droit du travail.
# Seuls « ne », « pas » et « sans » figurent dans la liste Snowball : ce sont les seuls que la variante
# 'snowball_no_negation' conserve en plus. Les autres sont listés pour le cas où la liste changerait.
TERMES_NEGATION_RESTRICTION = {
    "ne", "pas", "point", "non", "ni", "aucun", "aucune", "aucuns", "aucunes",
    "nul", "nulle", "jamais", "rien", "sans", "personne", "guère", "guere",
    "sauf", "hors", "interdit", "interdite", "interdits", "interdictions"
}


def load_snowball_stopwords(path: Path = MOTS_VIDES_CACHE) -> Set[str]:
    """Liste Snowball, téléchargée une fois puis relue ; refusée si son empreinte SHA-256 diffère."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MOTS_VIDES_URL, path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != MOTS_VIDES_SHA256:
        raise RuntimeError(f"Empreinte inattendue pour {path} : fichier à supprimer puis à retélécharger.")
    # un mot en début de ligne, commentaire après une barre verticale
    return {ligne.split("|")[0].strip() for ligne in path.read_text(encoding="utf-8").splitlines()} - {""}


def get_french_stopwords(variant: Optional[str] = "snowball") -> Optional[Set[str]]:
    """
    Retourne la liste des mots vides français selon la variante demandée.
    - None : aucune suppression
    - 'snowball' : liste du projet Snowball (154 mots), figée
    - 'snowball_no_negation' : liste Snowball sans les négations et termes restrictifs
    """
    if not variant:
        return None
    if variant in ("snowball", "snowball_no_negation"):
        base_sw = load_snowball_stopwords()
        if variant == "snowball_no_negation":
            return base_sw - TERMES_NEGATION_RESTRICTION
        return base_sw
    raise ValueError(f"Variante de stopwords inconnue : {variant}")


class LexicalTokenizer:
    """
    Tokeniseur configurable pour les modèles lexicaux français.
    Gère la normalisation, la racinisation (stemming) et le filtrage des mots vides.
    """
    def __init__(
        self,
        stopwords_variant: Optional[str] = None,
        stemming: Optional[str] = None,
        lowercase: bool = True,
        strip_accents: bool = False
    ):
        self.lowercase = lowercase
        self.strip_accents = strip_accents
        self.stopwords = get_french_stopwords(stopwords_variant)
        self.stemmer = None
        if stemming == "french":
            self.stemmer = snowballstemmer.stemmer("french")
        elif stemming is not None:
            raise ValueError(f"Stemmer non supporté : {stemming}")

        # Motif de tokenisation par mots (incluant lettres accentuées et chiffres)
        self.pattern = re.compile(r"(?u)\b\w+\b")

    def __call__(self, text: str) -> List[str]:
        if self.lowercase:
            text = text.lower()
        if self.strip_accents:
            text = "".join(
                c for c in unicodedata.normalize("NFD", text)
                if unicodedata.category(c) != "Mn"
            )
        tokens = self.pattern.findall(text)
        # Filtrage stopwords, avant la racinisation : la liste porte sur les formes fléchies
        if self.stopwords:
            tokens = [t for t in tokens if t not in self.stopwords]
        if self.stemmer:
            tokens = self.stemmer.stemWords(tokens)
        return tokens


def _df_bounds(n_docs: int, min_df: Union[int, float], max_df: Union[int, float]) -> Tuple[float, float]:
    """Bornes de fréquence documentaire, avec la convention de scikit-learn : entier = nombre de passages,
    réel = proportion des passages."""
    low = min_df * n_docs if isinstance(min_df, float) else min_df
    high = max_df * n_docs if isinstance(max_df, float) else max_df
    return low, high


def _top_positive(scores: np.ndarray, k: int) -> np.ndarray:
    """Indices des k meilleurs scores strictement positifs, selon la règle d'ex aequo de rank_by_score."""
    order = rank_by_score(scores)
    return order[scores[order] > 0][:k]


class BM25Retriever:
    """
    Index et moteur de recherche BM25, calculé en matrices creuses.

    idf="lucene" (défaut) : log(1 + (N - n_t + 0,5) / (n_t + 0,5)), toujours positif, avec k1 = 1,2, b = 0,75.
    idf="atire" : log((N - n_t + 0,5) / (n_t + 0,5)), idf négatifs remplacés par epsilon fois l'idf moyen ;
    avec k1 = 1,5 et b = 0,75, ce sont les scores de rank_bm25.BM25Okapi.
    La longueur d'un passage est son nombre de mots après mots vides et racinisation, avant la coupure par
    fréquence. Un mot répété dans la requête compte autant de fois, comme dans rank_bm25.
    """
    def __init__(
        self,
        stopwords_variant: Optional[str] = None,
        stemming: Optional[str] = None,
        lowercase: bool = True,
        k1: float = 1.2,
        b: float = 0.75,
        idf: str = "lucene",
        epsilon: float = 0.25,
        min_df: Union[int, float] = 1,
        max_df: Union[int, float] = 1.0
    ):
        if idf not in ("lucene", "atire"):
            raise ValueError(f"Formule d'idf inconnue : {idf}")
        self.tokenizer = LexicalTokenizer(
            stopwords_variant=stopwords_variant,
            stemming=stemming,
            lowercase=lowercase
        )
        self.k1, self.b, self.idf_formula, self.epsilon = k1, b, idf, epsilon
        self.min_df, self.max_df = min_df, max_df
        self.doc_ids: List[Any] = []
        self.corpus_size = 0
        self.tokenized_corpus: List[List[str]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Optional[np.ndarray] = None
        self.doc_len: Optional[np.ndarray] = None
        self.tf: Optional[sparse.csr_matrix] = None       # passages x termes, fréquences brutes
        self.weights: Optional[sparse.csr_matrix] = None  # passages x termes, contributions BM25

    def fit(self, documents: List[str], doc_ids: Optional[List[Any]] = None) -> "BM25Retriever":
        self.corpus_size = len(documents)
        if doc_ids is not None:
            if len(doc_ids) != self.corpus_size:
                raise ValueError("La taille de doc_ids doit correspondre à documents.")
            self.doc_ids = list(doc_ids)
        else:
            self.doc_ids = list(range(self.corpus_size))

        self.tokenized_corpus = [self.tokenizer(doc) for doc in documents]
        counts = [Counter(doc) for doc in self.tokenized_corpus]
        df = Counter(t for c in counts for t in c)
        low, high = _df_bounds(self.corpus_size, self.min_df, self.max_df)
        kept = sorted(t for t, n in df.items() if low <= n <= high)
        self.vocabulary = {t: i for i, t in enumerate(kept)}

        rows, cols, vals = [], [], []
        for j, c in enumerate(counts):
            for t, f in c.items():
                if t in self.vocabulary:
                    rows.append(j)
                    cols.append(self.vocabulary[t])
                    vals.append(f)
        shape = (self.corpus_size, len(self.vocabulary))
        self.tf = sparse.csr_matrix((np.array(vals, dtype=np.float64), (rows, cols)), shape=shape)

        n_docs = self.corpus_size
        n_t = np.array([df[t] for t in kept], dtype=np.float64)
        if self.idf_formula == "lucene":
            self.idf = np.log(1 + (n_docs - n_t + 0.5) / (n_t + 0.5))
        else:
            raw = np.log(n_docs - n_t + 0.5) - np.log(n_t + 0.5)
            self.idf = np.where(raw < 0, self.epsilon * raw.mean(), raw)

        self.doc_len = np.array([len(doc) for doc in self.tokenized_corpus], dtype=np.float64)
        norm = self.k1 * (1 - self.b + self.b * self.doc_len / self.doc_len.mean())
        coo = self.tf.tocoo()
        contrib = self.idf[coo.col] * coo.data * (self.k1 + 1) / (coo.data + norm[coo.row])
        self.weights = sparse.csr_matrix((contrib, (coo.row, coo.col)), shape=shape)
        return self

    def _query_matrix(self, queries: Sequence[str]) -> sparse.csr_matrix:
        rows, cols, vals = [], [], []
        for i, q in enumerate(queries):
            for t, f in Counter(t for t in self.tokenizer(q) if t in self.vocabulary).items():
                rows.append(i)
                cols.append(self.vocabulary[t])
                vals.append(f)
        return sparse.csr_matrix((np.array(vals, dtype=np.float64), (rows, cols)),
                                 shape=(len(queries), len(self.vocabulary)))

    def score_matrix(self, queries: Sequence[str]) -> np.ndarray:
        """Scores de toutes les requêtes contre tous les passages (requêtes x passages), pour l'évaluation."""
        if self.weights is None:
            raise RuntimeError("Le modèle BM25 doit être entraîné via fit() avant d'interroger.")
        return (self._query_matrix(queries) @ self.weights.T).toarray()

    def search(self, query: str, k: int = 5) -> List[Tuple[Any, float]]:
        """Les k meilleurs passages de score strictement positif, avec leur score ; liste vide si aucun mot
        de la requête n'est dans le vocabulaire."""
        scores = self.score_matrix([query])[0]
        return [(self.doc_ids[i], float(scores[i])) for i in _top_positive(scores, k)]

    def batch_search(self, queries: List[str], k: int = 5) -> List[List[Any]]:
        """Interroge un ensemble de requêtes et renvoie la liste des identifiants classés."""
        matrix = self.score_matrix(queries)
        return [[self.doc_ids[i] for i in _top_positive(row, k)] for row in matrix]

    def export_size_bytes(self) -> Dict[str, Any]:
        """
        Mesure le poids d'un export JSON de l'index pour le navigateur : vocabulaire, idf (6 décimales),
        listes inversées (numéro de passage, fréquence) et longueurs des passages, puis sa version gzip.
        """
        if self.tf is None:
            raise RuntimeError("Modèle non fitté.")
        csc = self.tf.tocsc()
        postings = [np.column_stack([csc.indices[csc.indptr[j]:csc.indptr[j + 1]],
                                     csc.data[csc.indptr[j]:csc.indptr[j + 1]].astype(int)]).tolist()
                    for j in range(csc.shape[1])]
        export = {"k1": self.k1, "b": self.b, "vocabulaire": list(self.vocabulary),
                  "idf": [round(float(x), 6) for x in self.idf], "postings": postings,
                  "longueurs": self.doc_len.astype(int).tolist()}
        raw = json.dumps(export, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        compressed = gzip.compress(raw, compresslevel=9, mtime=0)
        return {
            "n_docs": self.corpus_size,
            "vocab_size": len(self.vocabulary),
            "total_postings": int(self.tf.nnz),
            "json_raw_bytes": len(raw),
            "json_gzip_bytes": len(compressed),
            "json_raw_mb": len(raw) / (1024 * 1024),
            "json_gzip_mb": len(compressed) / (1024 * 1024),
        }


class TfidfRetriever:
    """
    Index et moteur de recherche TF-IDF basé sur scikit-learn.
    Prend en charge les mêmes tokeniseurs et variantes. Score : cosinus (vecteurs normalisés L2).
    """
    def __init__(
        self,
        stopwords_variant: Optional[str] = None,
        stemming: Optional[str] = None,
        lowercase: bool = True,
        min_df: Union[int, float] = 1,
        max_df: Union[int, float] = 1.0,
        sublinear_tf: bool = True
    ):
        self.tokenizer = LexicalTokenizer(
            stopwords_variant=stopwords_variant,
            stemming=stemming,
            lowercase=lowercase
        )
        # le tokeniseur fait déjà la mise en minuscules : scikit-learn ne doit pas la refaire
        self.vectorizer = TfidfVectorizer(
            tokenizer=self.tokenizer,
            token_pattern=None,
            lowercase=False,
            min_df=min_df,
            max_df=max_df,
            sublinear_tf=sublinear_tf,
            norm="l2"
        )
        self.doc_ids: List[Any] = []
        self.tfidf_matrix = None
        self.corpus_size = 0

    def fit(self, documents: List[str], doc_ids: Optional[List[Any]] = None) -> "TfidfRetriever":
        self.corpus_size = len(documents)
        if doc_ids is not None:
            if len(doc_ids) != self.corpus_size:
                raise ValueError("La taille de doc_ids doit correspondre à documents.")
            self.doc_ids = list(doc_ids)
        else:
            self.doc_ids = list(range(self.corpus_size))
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)
        return self

    def score_matrix(self, queries: Sequence[str]) -> np.ndarray:
        """Cosinus de toutes les requêtes contre tous les passages (requêtes x passages)."""
        if self.tfidf_matrix is None:
            raise RuntimeError("Le modèle TF-IDF doit être entraîné via fit() avant d'interroger.")
        return (self.vectorizer.transform(list(queries)) @ self.tfidf_matrix.T).toarray()

    def search(self, query: str, k: int = 5) -> List[Tuple[Any, float]]:
        scores = self.score_matrix([query])[0]
        return [(self.doc_ids[i], float(scores[i])) for i in _top_positive(scores, k)]

    def batch_search(self, queries: List[str], k: int = 5) -> List[List[Any]]:
        matrix = self.score_matrix(queries)
        return [[self.doc_ids[i] for i in _top_positive(row, k)] for row in matrix]


def sanity_check() -> bool:
    """Contrôles calculés à la main sur un petit corpus, et recoupement avec rank_bm25."""
    docs = ["Le salarié ne peut pas être licencié sans motif.",
            "Le salarié peut démissionner du contrat.",
            "Le contrat de travail est écrit.",
            "Les licenciements économiques."]

    # 1. Mots vides : la variante sans négations garde « ne », « pas », « sans »
    std = LexicalTokenizer("snowball")("Il ne peut pas partir sans préavis")
    neg = LexicalTokenizer("snowball_no_negation")("Il ne peut pas partir sans préavis")
    assert std == ["peut", "partir", "préavis"], std
    assert neg == ["ne", "peut", "pas", "partir", "sans", "préavis"], neg
    assert len(load_snowball_stopwords()) == 154

    # 2. Racinisation : deux flexions d'un même mot ont la même racine
    stem = LexicalTokenizer(stemming="french")
    assert stem("licenciement")[0] == stem("licenciements")[0]

    # 3. Formule de Lucene sur une requête d'un mot : « écrit » n'est que dans le passage 2 (6 mots, sur des
    # longueurs 9, 6, 6 et 3 : moyenne 6). idf = ln(1 + (4 - 1 + 0,5) / (1 + 0,5)) = ln(10/3).
    bm = BM25Retriever(k1=1.2, b=0.75).fit(docs)
    assert bm.doc_len.tolist() == [9, 6, 6, 3]
    idf = math.log(10 / 3)
    expected = idf * 1 * 2.2 / (1 + 1.2 * (1 - 0.75 + 0.75 * 6 / 6))
    scores = bm.score_matrix(["écrit"])[0]
    assert np.isclose(scores[2], expected) and np.count_nonzero(scores) == 1

    # 4. Formule de rank_bm25 : mêmes scores que BM25Okapi, à 1e-9 près
    from rank_bm25 import BM25Okapi
    tok = LexicalTokenizer()
    okapi = BM25Okapi([tok(d) for d in docs])
    atire = BM25Retriever(k1=1.5, b=0.75, idf="atire").fit(docs)
    for q in ["le salarié peut", "contrat de travail", "le le salarié"]:
        assert np.allclose(atire.score_matrix([q])[0], okapi.get_scores(tok(q)), atol=1e-9), q

    # 5. Aucun mot connu : aucun résultat ; à score égal, l'ordre de l'index
    assert bm.search("xyzzy", k=3) == []
    assert bm.batch_search(["xyzzy", "écrit"], k=3) == [[], [2]]
    twins = BM25Retriever().fit(["alpha beta", "gamma", "alpha beta"])
    assert [d for d, _ in twins.search("alpha", k=3)] == [0, 2]

    # 6. Coupure par fréquence : min_df = 2 ne garde que les mots présents dans au moins deux passages
    cut = BM25Retriever(min_df=2).fit(docs)
    df = Counter(t for d in docs for t in set(tok(d)))
    assert set(cut.vocabulary) == {t for t, n in df.items() if n >= 2}

    # 7. TF-IDF : une requête identique à un passage le place en tête, avec un cosinus de 1
    tfidf = TfidfRetriever(sublinear_tf=False).fit(docs)
    top = tfidf.search(docs[2], k=1)
    assert top[0][0] == 2 and np.isclose(top[0][1], 1.0)
    assert tfidf.search("xyzzy") == []

    # 8. Poids d'export : la version gzip est plus petite que le JSON brut
    size = bm.export_size_bytes()
    assert 0 < size["json_gzip_bytes"] < size["json_raw_bytes"]
    return True


if __name__ == "__main__":
    if sanity_check():
        print("Contrôles des références lexicales validés (calculs à la main et recoupement avec rank_bm25).")
