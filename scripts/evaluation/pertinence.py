"""
Règle de pertinence du notebook 03 (protocole, section 3, décision D4).

Un passage est pertinent pour une question annotée par un extrait si son texte normalisé contient un fragment
contigu de l'extrait normalisé long d'au moins la moitié de l'extrait (arrondie à l'entier supérieur).

Normalisation : minuscules, apostrophe typographique remplacée par l'apostrophe droite, puis seuls les lettres,
y compris accentuées, et les chiffres sont conservés. La comparaison est faite deux fois, avec et sans retrait des
marques de liste numérotées (un nombre suivi d'un point et d'une espace) : la copie depuis le site les perd parfois,
alors que les passages les gardent, mais les retirer partout effacerait aussi une année en fin de phrase. Un
passage est pertinent si l'une des deux comparaisons le déclare tel. Les tirets de liste, qui ne sont ni lettres ni
chiffres, disparaissent dans les deux cas.
"""

import bisect
import math
import re
from typing import List, Sequence

LONGUEUR_MINIMALE = 80   # caractères de l'extrait normalisé
PART_MINIMALE = 0.5      # part de l'extrait que le fragment commun doit couvrir
TAILLE_ANCRE = 20        # caractères des fragments d'ancrage qui présélectionnent les passages

_MARQUE_NUMEROTEE = re.compile(r"(^|\s)\d+\.(?=\s)")
_HORS_ALPHANUMERIQUE = re.compile(r"[^0-9a-zà-ÿœæ]")


def normaliser(texte: str, retirer_marques: bool) -> str:
    """Texte réduit à ses lettres et chiffres, en minuscules ; marques de liste numérotées retirées si demandé."""
    t = texte.replace("’", "'").lower()
    if retirer_marques:
        t = _MARQUE_NUMEROTEE.sub(" ", t)
    return _HORS_ALPHANUMERIQUE.sub("", t)


def longueur_requise(extrait_normalise: str, part: float = PART_MINIMALE) -> int:
    """Longueur minimale du fragment commun : la moitié de l'extrait, arrondie à l'entier supérieur."""
    return math.ceil(part * len(extrait_normalise))


def contient_fragment(extrait: str, passage: str, longueur: int) -> bool:
    """Vrai si passage contient un fragment contigu de extrait d'au moins longueur caractères (textes normalisés).

    Un fragment commun de longueur au moins L existe si et seulement si l'une des fenêtres de L caractères de
    l'extrait figure dans le passage.
    """
    if longueur <= 0 or longueur > len(extrait):
        return False
    return any(extrait[i:i + longueur] in passage for i in range(len(extrait) - longueur + 1))


def plus_long_fragment_commun(a: str, b: str) -> int:
    """Longueur du plus long fragment contigu commun, par programmation dynamique ; réservé aux contrôles."""
    meilleur, precedent = 0, [0] * (len(b) + 1)
    for ca in a:
        courant = [0] * (len(b) + 1)
        for j, cb in enumerate(b, start=1):
            if ca == cb:
                courant[j] = precedent[j - 1] + 1
                meilleur = max(meilleur, courant[j])
        precedent = courant
    return meilleur


class IndexPertinence:
    """
    Recherche des passages pertinents d'un découpage, pour un extrait donné.

    Présélection exacte : avec L la longueur requise et k = TAILLE_ANCRE (si L >= k), toute fenêtre de L
    caractères de l'extrait contient l'un des fragments d'ancrage de k caractères pris aux positions 0, s, 2s, ...
    avec s = L - k + 1 (jusqu'à la position n - k). En effet, une fenêtre qui commence en i contient l'ancre
    commençant au premier multiple de s supérieur ou égal à i, qui vaut au plus i + s - 1 = i + L - k, donc
    finit avant i + L ; et cette position ne dépasse pas (n - L) + (L - k) = n - k. Un passage pertinent contient
    donc au moins une ancre, et seuls ces passages sont vérifiés fenêtre par fenêtre.
    """

    def __init__(self, textes: Sequence[str]):
        self.n_passages = len(textes)
        self._variantes = {}
        for retirer in (False, True):
            normalises = [normaliser(t, retirer) for t in textes]
            # séparateur hors alphabet normalisé : une ancre ne peut pas chevaucher deux passages
            debuts, position = [], 0
            for t in normalises:
                debuts.append(position)
                position += len(t) + 1
            self._variantes[retirer] = (normalises, "|".join(normalises), debuts)

    def _candidats(self, retirer: bool, extrait: str, longueur: int) -> List[int]:
        normalises, concatene, debuts = self._variantes[retirer]
        if longueur < TAILLE_ANCRE:
            return list(range(self.n_passages))
        pas = longueur - TAILLE_ANCRE + 1
        trouves = set()
        for a in range(0, len(extrait) - TAILLE_ANCRE + 1, pas):
            ancre = extrait[a:a + TAILLE_ANCRE]
            k = concatene.find(ancre)
            while k != -1:
                trouves.add(bisect.bisect_right(debuts, k) - 1)
                k = concatene.find(ancre, k + 1)
        return sorted(trouves)

    def pertinents(self, extrait: str, part: float = PART_MINIMALE) -> List[int]:
        """Indices, croissants, des passages pertinents pour l'extrait ; ValueError si l'extrait est trop court."""
        # la longueur minimale porte sur l'extrait tel qu'annoté, sans retrait des marques de liste
        longueur_annotee = len(normaliser(extrait, False))
        if longueur_annotee < LONGUEUR_MINIMALE:
            raise ValueError(f"Extrait normalisé de {longueur_annotee} caractères, moins que {LONGUEUR_MINIMALE}.")
        resultat = set()
        for retirer in (False, True):
            e = normaliser(extrait, retirer)
            longueur = longueur_requise(e, part)
            normalises = self._variantes[retirer][0]
            resultat.update(i for i in self._candidats(retirer, e, longueur)
                            if contient_fragment(e, normalises[i], longueur))
        return sorted(resultat)

    def pertinents_exhaustif(self, extrait: str, part: float = PART_MINIMALE) -> List[int]:
        """Même règle sans présélection, passage par passage ; réservé aux contrôles."""
        resultat = set()
        for retirer in (False, True):
            e = normaliser(extrait, retirer)
            longueur = longueur_requise(e, part)
            resultat.update(i for i, p in enumerate(self._variantes[retirer][0]) if contient_fragment(e, p, longueur))
        return sorted(resultat)


def sanity_check() -> bool:
    """Contrôles calculés à la main."""
    # 1. Normalisation
    assert normaliser("L’article L. 1221-19 : « le CDI ».", False) == "larticlel122119lecdi"
    assert normaliser("Trois cas : 1. le premier ; 2. le second", True) == "troiscaslepremierlesecond"
    assert normaliser("Trois cas : 1. le premier ; 2. le second", False) == "troiscas1lepremier2lesecond"
    assert normaliser("Vérifié en 2024. Le salarié", True) == "vérifiéenlesalarié"   # l'année disparaît

    # 2. Longueur requise : la moitié, arrondie à l'entier supérieur
    assert longueur_requise("a" * 83) == 42 and longueur_requise("a" * 84) == 42

    # 3. Fragment commun : seuil exact
    assert contient_fragment("abcdefghij", "xxabcdeyy", 5) and not contient_fragment("abcdefghij", "xxabcdyy", 5)
    assert plus_long_fragment_commun("abcdefghij", "xxabcdeyy") == 5

    # 4. Règle sur de vrais cas de forme : tirets de liste, marques numérotées, année en fin d'extrait
    corps = "le salarié peut être dispensé de préavis à sa demande et après acceptation de l'employeur, un écrit est conseillé "
    passages = [
        "Toutefois " + corps.replace("préavis à", "préavis : - À") + "dans ce cas l'indemnité n'est pas due.",
        "Les cas prévus : 1. " + corps + "fin du passage.",
        "Le décret publié en 2024. " + corps,
        "Aucun rapport avec la question posée, sur la durée du travail et les heures supplémentaires du salarié.",
    ]
    index = IndexPertinence(passages)
    assert index.pertinents("Toutefois " + corps.replace("préavis à", "préavis :À")) == [0, 1, 2]
    extrait_annee = "Le décret publié en 2024." + " " + corps[:80]
    assert 2 in index.pertinents(extrait_annee)
    # 5. Extrait de 100 caractères coupé entre deux passages : il en faut 50 d'un seul tenant (longueurs exactes)
    moitie_a, moitie_b = "abcdefghij" * 5, "klmnopqrst" * 5
    coupe = IndexPertinence(["zz " + moitie_a, moitie_b + " zz", "zz " + moitie_a[:49], "sans rapport " * 10])
    assert coupe.pertinents(moitie_a + moitie_b) == [0, 1]   # 50 caractères : oui ; 49 : non
    # 6. Présélection exacte : même résultat que la recherche exhaustive
    for extrait in ("Toutefois " + corps, extrait_annee, moitie_a + moitie_b):
        for idx in (index, coupe):
            assert idx.pertinents(extrait) == idx.pertinents_exhaustif(extrait)
    # 7. Extrait trop court
    try:
        index.pertinents("trop court")
    except ValueError:
        pass
    else:
        raise AssertionError("Un extrait trop court doit lever ValueError.")
    return True


if __name__ == "__main__":
    if sanity_check():
        print("Contrôles de la règle de pertinence validés (calculs à la main, présélection exacte).")
