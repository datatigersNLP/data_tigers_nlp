"""
Règle de pertinence du notebook 03 (protocole, section 3, décision D4).

Un passage est pertinent pour une question annotée par un extrait si son texte normalisé et l'extrait normalisé
partagent un fragment contigu qui couvre :
1. au moins la moitié de l'extrait (arrondie à l'entier supérieur) ;
2. ou au moins la moitié du passage, avec un minimum de 80 caractères.

La seconde condition ne joue que pour les extraits longs, comme une réponse en liste : un passage plus court que
la moitié de l'extrait ne pourrait jamais satisfaire la première, ce qui avantagerait par construction les
découpages à grands passages. Pour un extrait de 160 caractères normalisés ou moins, elle ne change rien : un
fragment commun d'au moins 80 caractères couvre déjà la moitié de l'extrait.

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

LONGUEUR_MINIMALE = 80   # caractères de l'extrait normalisé, et du fragment commun de la seconde condition
PART_MINIMALE = 0.5      # part de l'extrait, ou du passage, que le fragment commun doit couvrir
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
    """Première condition : la moitié de l'extrait, arrondie à l'entier supérieur."""
    return math.ceil(part * len(extrait_normalise))


def longueur_requise_passage(passage_normalise: str, part: float = PART_MINIMALE) -> int:
    """Seconde condition : la moitié du passage, arrondie à l'entier supérieur, et au moins LONGUEUR_MINIMALE."""
    return max(LONGUEUR_MINIMALE, math.ceil(part * len(passage_normalise)))


def contient_fragment(extrait: str, passage: str, longueur: int) -> bool:
    """Vrai si passage contient un fragment contigu de extrait d'au moins longueur caractères (textes normalisés).

    Un fragment commun de longueur au moins L existe si et seulement si l'une des fenêtres de L caractères de
    l'extrait figure dans le passage.
    """
    if longueur <= 0 or longueur > len(extrait):
        return False
    return any(extrait[i:i + longueur] in passage for i in range(len(extrait) - longueur + 1))


def est_pertinent(extrait: str, passage: str, part: float = PART_MINIMALE) -> bool:
    """Règle D4 pour un extrait et un passage déjà normalisés de la même façon."""
    return (contient_fragment(extrait, passage, longueur_requise(extrait, part))
            or contient_fragment(extrait, passage, longueur_requise_passage(passage, part)))


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

    Présélection exacte. Les deux conditions exigent un fragment commun d'au moins L = min(L1, 80) caractères,
    avec L1 la longueur requise par la première ; la seconde en exige au moins 80. Avec k = TAILLE_ANCRE (si
    L >= k), toute fenêtre de L caractères de l'extrait contient l'un des fragments d'ancrage de k caractères pris
    aux positions 0, s, 2s, ... avec s = L - k + 1 (jusqu'à la position n - k). En effet, une fenêtre qui commence
    en i contient l'ancre commençant au premier multiple de s supérieur ou égal à i, qui vaut au plus
    i + s - 1 = i + L - k, donc finit avant i + L ; et cette position ne dépasse pas (n - L) + (L - k) = n - k. Un
    passage pertinent contient donc au moins une ancre, et seuls ces passages sont vérifiés.
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
            plus_court = min(longueur_requise(e, part), LONGUEUR_MINIMALE)
            normalises = self._variantes[retirer][0]
            resultat.update(i for i in self._candidats(retirer, e, plus_court)
                            if est_pertinent(e, normalises[i], part))
        return sorted(resultat)

    def pertinents_exhaustif(self, extrait: str, part: float = PART_MINIMALE) -> List[int]:
        """Même règle sans présélection, passage par passage ; réservé aux contrôles."""
        resultat = set()
        for retirer in (False, True):
            e = normaliser(extrait, retirer)
            resultat.update(i for i, p in enumerate(self._variantes[retirer][0]) if est_pertinent(e, p, part))
        return sorted(resultat)


def _bloc(lettre: str, n: int) -> str:
    """Texte normalisé de n caractères, fait de jetons « lettre + 3 chiffres » numérotés : deux blocs de lettres
    différentes n'ont aucun fragment commun de plus de 3 caractères, ce qui rend les longueurs communes exactes."""
    jetons = "".join(f"{lettre}{i:03d}" for i in range(n // 4 + 1))
    return jetons[:n]


def sanity_check() -> bool:
    """Contrôles calculés à la main."""
    # 1. Normalisation
    assert normaliser("L’article L. 1221-19 : « le CDI ».", False) == "larticlel122119lecdi"
    assert normaliser("Trois cas : 1. le premier ; 2. le second", True) == "troiscaslepremierlesecond"
    assert normaliser("Trois cas : 1. le premier ; 2. le second", False) == "troiscas1lepremier2lesecond"
    assert normaliser("Vérifié en 2024. Le salarié", True) == "vérifiéenlesalarié"   # l'année disparaît

    # 2. Longueurs requises : la moitié, arrondie à l'entier supérieur ; au moins 80 pour la seconde condition
    assert longueur_requise("a" * 83) == 42 and longueur_requise("a" * 84) == 42
    assert longueur_requise_passage("a" * 100) == 80 and longueur_requise_passage("a" * 201) == 101

    # 3. Fragment commun : seuil exact
    assert contient_fragment("abcdefghij", "xxabcdeyy", 5) and not contient_fragment("abcdefghij", "xxabcdyy", 5)
    assert plus_long_fragment_commun("abcdefghij", "xxabcdeyy") == 5
    assert plus_long_fragment_commun(_bloc("a", 120), _bloc("b", 120)) <= 3

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

    # 6. Seconde condition, sur une réponse en liste de 600 caractères (première condition : 300 en commun)
    a, b, c = _bloc("a", 200), _bloc("b", 200), _bloc("c", 200)
    liste = IndexPertinence([
        "x" + a,                    # 0 : passage de 201, 200 en commun ; 200 >= max(80, 101) : pertinent
        b + _bloc("y", 200),        # 1 : passage de 400, 200 en commun ; 200 >= 200 : pertinent, à la limite
        b + _bloc("y", 201),        # 2 : passage de 401, 200 en commun ; 200 < 201 : non pertinent
        c[:79],                     # 3 : passage de 79 entièrement dans l'extrait ; 79 < 80 : non pertinent
        a + b[:100],                # 4 : passage de 300, 300 en commun : pertinent par la première condition
        _bloc("z", 300),            # 5 : sans rapport
    ])
    assert liste.pertinents(a + b + c) == [0, 1, 4]
    assert [est_pertinent(a + b + c, normaliser(p, False)) for p in ("x" + a, c[:79])] == [True, False]
    # un extrait de 160 caractères ou moins : la seconde condition n'ajoute rien (fragment de 80 = la moitié)
    court = _bloc("d", 160)
    petit = IndexPertinence([court[:80], court[:79] + _bloc("w", 1)])
    assert petit.pertinents(court) == [0]

    # 7. Présélection exacte : même résultat que la recherche exhaustive
    for extrait, idx in (("Toutefois " + corps, index), (extrait_annee, index), (moitie_a + moitie_b, coupe),
                         (a + b + c, liste), (court, petit), (b + c, liste)):
        assert idx.pertinents(extrait) == idx.pertinents_exhaustif(extrait)

    # 8. Extrait trop court
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
