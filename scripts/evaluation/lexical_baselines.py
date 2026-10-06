"""
Module de références lexicales pour la recherche d'information (TF-IDF et BM25).

Conçu pour l'Issue #47 et réutilisable dans le Notebook 03 (Issue #46).
Supporte les passages M2 du corpus travail-emploi SocialGouv.

Variantes supportées :
1. Sans mots vides (stopwords=None)
2. Mots vides Snowball standard (stopwords='snowball')
3. Mots vides Snowball sans les négations (stopwords='snowball_no_negation')
4. Avec et sans racinisation française (stemming='french' ou None)
5. Coupure par fréquence de termes (min_df, max_df)
"""

import re
import json
import unicodedata
from pathlib import Path
from typing import List, Dict, Set, Union, Optional, Tuple, Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from rank_bm25 import BM25Okapi

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem.snowball import FrenchStemmer
    _NLTK_AVAILABLE = True
except ImportError:
    _NLTK_AVAILABLE = False


# Mots à forte valeur juridique et restrictive à préserver impérativement en droit du travail
TERMES_NEGATION_RESTRICTION = {
    "ne", "pas", "point", "non", "ni", "aucun", "aucune", "aucuns", "aucunes",
    "nul", "nulle", "jamais", "rien", "sans", "personne", "guère", "guere",
    "sauf", "hors", "interdit", "interdite", "interdits", "interdictions"
}


def get_french_stopwords(variant: Optional[str] = "snowball") -> Optional[Set[str]]:
    """
    Retourne la liste des mots vides français selon la variante demandée.
    - None : aucune suppression
    - 'snowball' : liste standard NLTK Snowball (157 mots)
    - 'snowball_no_negation' : liste Snowball expurgée des négations et termes restrictifs
    """
    if not variant:
        return None

    if variant in ("snowball", "snowball_no_negation"):
        if not _NLTK_AVAILABLE:
            raise ImportError("nltk est requis pour charger les stopwords Snowball.")
        try:
            base_sw = set(stopwords.words("french"))
        except LookupError:
            nltk.download("stopwords", quiet=True)
            base_sw = set(stopwords.words("french"))

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
            if not _NLTK_AVAILABLE:
                raise ImportError("nltk est requis pour utiliser le FrenchStemmer.")
            self.stemmer = FrenchStemmer()
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
        
        # Filtrage stopwords
        if self.stopwords:
            tokens = [t for t in tokens if t not in self.stopwords]

        # Racinisation
        if self.stemmer:
            tokens = [self.stemmer.stem(t) for t in tokens]

        return tokens


class BM25Retriever:
    """
    Index et moteur de recherche BM25 basé sur rank_bm25.
    Supporte toutes les variantes de tokenisation et l'évaluation de taille d'export.
    """
    def __init__(
        self,
        stopwords_variant: Optional[str] = None,
        stemming: Optional[str] = None,
        lowercase: bool = True,
        k1: float = 1.5,
        b: float = 0.75
    ):
        self.tokenizer = LexicalTokenizer(
            stopwords_variant=stopwords_variant,
            stemming=stemming,
            lowercase=lowercase
        )
        self.k1 = k1
        self.b = b
        self.doc_ids: List[Any] = []
        self.corpus_size = 0
        self.bm25: Optional[BM25Okapi] = None
        self.tokenized_corpus: List[List[str]] = []

    def fit(self, documents: List[str], doc_ids: Optional[List[Any]] = None) -> "BM25Retriever":
        self.corpus_size = len(documents)
        if doc_ids is not None:
            if len(doc_ids) != self.corpus_size:
                raise ValueError("La taille de doc_ids doit correspondre à documents.")
            self.doc_ids = list(doc_ids)
        else:
            self.doc_ids = list(range(self.corpus_size))

        self.tokenized_corpus = [self.tokenizer(doc) for doc in documents]
        self.bm25 = BM25Okapi(self.tokenized_corpus, k1=self.k1, b=self.b)
        return self

    def search(self, query: str, k: int = 5) -> List[Tuple[Any, float]]:
        if not self.bm25:
            raise RuntimeError("Le modèle BM25 doit être entraîné via fit() avant d'interroger.")
        
        tok_query = self.tokenizer(query)
        if not tok_query:
            return [(self.doc_ids[i], 0.0) for i in range(min(k, self.corpus_size))]

        scores = self.bm25.get_scores(tok_query)
        top_k_idx = np.argsort(scores)[::-1][:k]
        return [(self.doc_ids[i], float(scores[i])) for i in top_k_idx]

    def batch_search(self, queries: List[str], k: int = 5) -> List[List[Any]]:
        """Interroge un ensemble de requêtes et renvoie la liste des identifiants classés."""
        results = []
        for q in queries:
            ranked = self.search(q, k=k)
            results.append([doc_id for doc_id, _ in ranked])
        return results

    def estimate_index_size_bytes(self) -> Dict[str, Any]:
        """
        Estime l'empreinte mémoire d'un export JSON ou binaire de cet index pour le navigateur :
        vocabulaire, fréquences documentaires, et listes inversées compactées.
        """
        if not self.bm25:
            raise RuntimeError("Modèle non fitté.")
        
        vocab = set()
        total_postings = 0
        doc_lens = [len(doc) for doc in self.tokenized_corpus]
        
        for doc in self.tokenized_corpus:
            unique_terms = set(doc)
            vocab.update(unique_terms)
            total_postings += len(unique_terms)

        vocab_size = len(vocab)
        # Estimation taille JSON brut :
        # - vocabulaire (terme -> id, idf) : ~25 octets / mot
        # - listes d'inversion (doc_id, tf) : ~8 octets par posting
        # - longueurs de documents : 4 octets * nb_docs
        estimated_raw_bytes = (vocab_size * 25) + (total_postings * 8) + (self.corpus_size * 4)
        estimated_gzip_bytes = int(estimated_raw_bytes * 0.32)

        return {
            "n_docs": self.corpus_size,
            "vocab_size": vocab_size,
            "total_postings": total_postings,
            "estimated_json_raw_bytes": estimated_raw_bytes,
            "estimated_json_raw_mb": estimated_raw_bytes / (1024 * 1024),
            "estimated_gzip_mb": estimated_gzip_bytes / (1024 * 1024)
        }


class TfidfRetriever:
    """
    Index et moteur de recherche TF-IDF basé sur scikit-learn.
    Prend en charge les mêmes tokeniseurs et variantes.
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
        self.vectorizer = TfidfVectorizer(
            tokenizer=self.tokenizer,
            token_pattern=None,
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

    def search(self, query: str, k: int = 5) -> List[Tuple[Any, float]]:
        if self.tfidf_matrix is None:
            raise RuntimeError("Le modèle TF-IDF doit être entraîné via fit() avant d'interroger.")

        q_vec = self.vectorizer.transform([query])
        # Produit scalaire (matrices sparse) = similarité cosinus car norm='l2'
        scores = (self.tfidf_matrix * q_vec.T).toarray().ravel()
        top_k_idx = np.argsort(scores)[::-1][:k]
        return [(self.doc_ids[i], float(scores[i])) for i in top_k_idx]

    def batch_search(self, queries: List[str], k: int = 5) -> List[List[Any]]:
        results = []
        for q in queries:
            ranked = self.search(q, k=k)
            results.append([doc_id for doc_id, _ in ranked])
        return results
