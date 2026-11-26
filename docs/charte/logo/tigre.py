"""Logo de l'équipe Data Tigers (#176) : un tigre en pixel art, en robe d'avocat, qui lit un livre ouvert et répond.

Source unique du dessin : la grille de 32 x 32 pixels ci-dessous, une lettre par couleur (PALETTE). Le script écrit le
SVG, à pixels nets, et un PNG agrandi sans lissage, pour les supports. Création originale de l'équipe.

    python docs/charte/logo/tigre.py              # écrit logo-tigre.svg et logo-tigre-512.png à côté de ce fichier
    python docs/charte/logo/tigre.py --verifier   # vérifie que les fichiers versionnés correspondent à la grille

Le SVG est recopié tel quel dans front/public/favicon.svg, front/src/assets/logo-tigre.svg,
demo_b/public/favicon.svg et demo_b/src/assets/logo-tigre.svg ; --verifier contrôle aussi ces copies.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[2]
COPIES = ("front/public/favicon.svg", "front/src/assets/logo-tigre.svg",
          "demo_b/public/favicon.svg", "demo_b/src/assets/logo-tigre.svg")

PALETTE = {
    "K": "#2A1F1A",  # contour, rayures
    "O": "#F39A33",  # pelage
    "o": "#D8762A",  # pelage ombré
    "Y": "#FFC46B",  # pelage éclairé
    "W": "#FFF8EC",  # blanc : museau, rabat
    "w": "#E6D8C0",  # blanc ombré
    "P": "#F4A3A8",  # intérieur des oreilles, langue
    "N": "#5B3A33",  # truffe
    "E": "#1E1916",  # pupilles, bouche
    "R": "#2B2F38",  # robe d'avocat
    "r": "#454B57",  # robe éclairée
    "G": "#17604A",  # couverture du livre : le vert des deux interfaces
    "g": "#2A8564",  # couverture éclairée
    "C": "#FFF4D8",  # page
    "c": "#EBD9B0",  # page ombrée, près de la reliure
    "L": "#A08A63",  # lignes de texte
}

GRILLE = [
    "................................",  #  0
    "....KKK..................KKK....",  #  1 oreilles
    "...KYOOK................KOOYK...",  #  2
    "...KOPPOK..............KOPPOK...",  #  3
    "...KOPPOKKKKKKKKKKKKKKKKOPPOK...",  #  4
    "..KYYOOOOOOOKOOKKOOKOOOOOOOYYK..",  #  5 rayures du front
    "..KYOOOOOOOOKOOKKOOKOOOOOOOOYK..",  #  6
    "..KKKOOOOOOOOOOKKOOOOOOOOOOKKK..",  #  7 rayures des tempes
    "..KOKKOOOOOOOOOOOOOOOOOOOOKKOK..",  #  8
    "..KOOOOOOKKOOOOOOOOOOKKOOOOOOK..",  #  9 paupières en arc
    "..KWWOOOKEEKOOOOOOOOKEEKOOOWWK..",  # 10 regard baissé : il lit
    "..KWWWOOOOOOOWWNNWWOOOOOOOWWWK..",  # 11 truffe
    "..KWWWWOOOOWWWKEEKWWWOOOOWWWWK..",  # 12 bouche entrouverte : il répond
    "..KoWWWWOOOWWWKPPKWWWOOOWWWWoK..",  # 13
    "...KooOOWWWWWWWKKWWWWWWWOOooK...",  # 14
    "....KoooOOWWWWWWWWWWWWOOoooK....",  # 15
    ".....KKKKKKKKKKKKKKKKKKKKKK.....",  # 16 menton
    "....KrrRRRRRKWWWWWWKRRRRRrrK....",  # 17 col de la robe
    "...KrrRRRRRRRWWKKWWRRRRRRRrrK...",  # 18 rabat d'avocat : deux bandes blanches
    "...KrRRRRRRRRWWKKWWRRRRRRRRrK...",  # 19
    "...KRRRRRRRRRwwRRwwRRRRRRRRRK...",  # 20
    "...KRKKKKKKKKKKKKKKKKKKKKKKRK...",  # 21 livre ouvert, tenu par les pattes
    "...KRKCCCCCCCCCKKCCCCCCCCCKRK...",  # 22
    "..KOOKCLLLLLLLcKKcLLLLLLLCKOOK..",  # 23
    "..KOOKCCCCCCCCCKKCCCCCCCCCKOOK..",  # 24
    "..KYOKCLLLLLLCcKKcCLLLLLCCKOYK..",  # 25 lignes de longueurs différentes : seule rangée asymétrique
    "..KOOKCCCCCCCCCKKCCCCCCCCCKOOK..",  # 26
    "...KKGCLLLLLLccKKccLLLLLLCGKK...",  # 27
    "...KRgGGGGGGGGGKKGGGGGGGGGgRK...",  # 28 couverture verte
    "...KRRKKKKKKKKKKKKKKKKKKKKRRK...",  # 29
    "...KrRRRRRRRRRRRRRRRRRRRRRRrK...",  # 30
    "...KKKKKKKKKKKKKKKKKKKKKKKKKK...",  # 31
]
RANGEES_ASYMETRIQUES = {25}


def controler(grille=GRILLE) -> None:
    if len(grille) != 32 or any(len(r) != 32 for r in grille):
        raise ValueError("La grille doit compter 32 rangées de 32 pixels")
    inconnues = set("".join(grille)) - set(PALETTE) - {"."}
    if inconnues:
        raise ValueError(f"Lettres hors palette : {sorted(inconnues)}")
    asymetriques = {y for y, r in enumerate(grille) if r != r[::-1]}
    if asymetriques != RANGEES_ASYMETRIQUES:
        raise ValueError(f"Rangées asymétriques inattendues : {sorted(asymetriques)}")


def svg(grille=GRILLE) -> str:
    """Un chemin par couleur, fait des suites horizontales de pixels ; crispEdges garde les pixels nets à toute taille."""
    chemins: dict[str, list[str]] = {}
    for y, rangee in enumerate(grille):
        x = 0
        while x < 32:
            n = 1
            while x + n < 32 and rangee[x + n] == rangee[x]:
                n += 1
            if rangee[x] != ".":
                chemins.setdefault(rangee[x], []).append(f"M{x} {y}h{n}v1h-{n}z")
            x += n
    corps = "".join(f'<path fill="{PALETTE[c]}" d="{"".join(d)}"/>' for c, d in sorted(chemins.items()))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" shape-rendering="crispEdges">'
            "<title>Data Tigers</title>" + corps + "</svg>\n")


def png(chemin: Path, echelle: int = 16, grille=GRILLE) -> None:
    from PIL import Image
    image = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    for y, rangee in enumerate(grille):
        for x, c in enumerate(rangee):
            if c != ".":
                image.putpixel((x, y), tuple(int(PALETTE[c][i:i + 2], 16) for i in (1, 3, 5)) + (255,))
    image.resize((32 * echelle, 32 * echelle), Image.NEAREST).save(chemin, optimize=True)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--verifier", action="store_true", help="contrôler le SVG versionné et ses copies, sans rien écrire")
    a = p.parse_args(argv)
    controler()
    attendu = svg()
    if a.verifier:
        ecarts = [c for c in ("docs/charte/logo/logo-tigre.svg", *COPIES)
                  if not (RACINE / c).is_file() or (RACINE / c).read_text(encoding="utf-8") != attendu]
        print("conforme" if not ecarts else f"différent de la grille : {ecarts}")
        return 1 if ecarts else 0
    (ICI / "logo-tigre.svg").write_text(attendu, encoding="utf-8")
    png(ICI / "logo-tigre-512.png")
    print(f"logo-tigre.svg ({len(attendu.encode())} octets) et logo-tigre-512.png écrits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
