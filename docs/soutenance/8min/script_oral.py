"""Écrit le script oral de la soutenance (script_oral.md) à partir du support : le texte à dire de chaque diapositive est
celui des notes de deck.html, mot pour mot ; le script ne peut donc pas diverger du support.

    python3 docs/soutenance/8min/script_oral.py          # écrit docs/soutenance/8min/script_oral.md

La répartition des orateurs ci-dessous est une proposition, par domaine du classeur de suivi : à valider en équipe.
"""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from pathlib import Path

ICI = Path(__file__).resolve().parent
ORATEURS = {1: "Maïmouna", 2: "Maïmouna", 3: "Vaneck", 4: "Vaneck", 5: "Remy", 6: "Jibril", 7: "Jibril", 8: "Jibril",
            9: "Mahé", 10: "Mahé", 11: "Mahé", 12: "Mahé"}
MOTS_PAR_MINUTE = 130


def texte(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


class Etapes(HTMLParser):
    """Texte exact de chaque élément révélé par une étape (attribut data-e), imbrication comprise."""
    VIDES = {"br", "img", "input", "meta", "link", "hr", "path", "circle", "rect", "line", "polygon", "polyline", "use", "stop"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pile, self.ouverts, self.trouves = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag in self.VIDES:
            return
        e = dict(attrs).get("data-e")
        self.pile.append(tag)
        if e is not None:
            self.ouverts.append([len(self.pile), int(e), []])

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in self.VIDES or not self.pile:
            return
        if self.ouverts and self.ouverts[-1][0] == len(self.pile):
            _, e, morceaux = self.ouverts.pop()
            self.trouves.append((e, re.sub(r"\s+", " ", " ".join(morceaux)).strip()))
        self.pile.pop()

    def handle_data(self, data):
        for o in self.ouverts:
            o[2].append(data)


def diapositives(deck: str) -> list[dict]:
    sortie = []
    for m in re.finditer(r'<section class="diapo(?! annexe)[^"]*" data-duree="(\d+)"([^>]*)aria-label="([^"]+)">(.*?)</section>',
                         deck, re.S):
        duree, attributs, nom, corps = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        aside = re.search(r'<aside class="texte-a-dire"[^>]*>(.*?)</aside>', corps, re.S).group(1)
        dire = [texte(p) for p in re.findall(r"<p>(.*?)</p>", aside, re.S)]
        a_savoir = [texte(li) for li in re.findall(r"<li>(.*?)</li>", aside, re.S)]
        visible = re.sub(r'<aside class="texte-a-dire".*?</aside>', "", corps, flags=re.S)
        titre = re.search(r'<h[12][^>]*>(.*?)</h[12]>', visible, re.S)
        analyse = Etapes()
        analyse.feed(visible)
        etapes = [(e, abrege(x) if x else "élément du schéma") for e, x in analyse.trouves]
        nb = int(re.search(r'data-etapes="(\d+)"', attributs).group(1)) if "data-etapes" in attributs else 0
        par_etape = [(k, [x for e, x in sorted(set(etapes)) if e == k] or ["animation du schéma, sans nouvel élément"])
                     for k in range(1, nb + 1)]
        sortie.append({"nom": nom, "duree": duree, "titre": texte(titre.group(1)) if titre else nom, "dire": dire,
                       "a_savoir": a_savoir, "etapes": par_etape})
    return sortie


def abrege(x: str, n: int = 110) -> str:
    """Texte coupé à une limite de mot, jamais au milieu d'un mot."""
    return x if len(x) <= n else x[:n].rsplit(" ", 1)[0].rstrip(" ,;:") + " …"


def mmss(s: int) -> str:
    return f"{s // 60}:{s % 60:02d}"


def main() -> None:
    deck = (ICI / "deck.html").read_text(encoding="utf-8")
    ds = diapositives(deck)
    total = sum(d["duree"] for d in ds)
    mots = sum(len(" ".join(d["dire"]).split()) for d in ds)
    l = ["# Script oral de la soutenance (8 minutes)", "",
         f"**Source** le texte à dire est celui des notes de `deck.html`, mot pour mot ; ce fichier est généré par `script_oral.py` : "
         f"ne pas le modifier à la main, modifier le support puis relancer le script.", "",
         f"**Durée prévue** {mmss(total)} pour {len(ds)} diapositives ; {mots} mots, soit {mots / total * 60:.0f} mots par minute "
         f"(à {MOTS_PAR_MINUTE} mots par minute, {mmss(round(mots / MOTS_PAR_MINUTE * 60))}). Marge restante sur 8 minutes : "
         f"{480 - total} s, pour les changements d'orateur.", "",
         "**Orateurs** répartition proposée par domaine du classeur de suivi, à valider en équipe.", "",
         "---", "",
         "## Avant de commencer", "",
         "- Ouvrir `docs/soutenance/presentation_8min.html` (hors ligne), touche F pour le plein écran.",
         "- Les notes (touche N) s'affichent sur la page projetée : ne les ouvrir qu'en répétition, ou avec un second écran qui ne recopie pas le premier.",
         "- Ouvrir à l'avance, dans un autre onglet, le site du volet A, et y poser une première question : la première visite télécharge le modèle.",
         "- Avoir les deux vidéos de secours prêtes (volet A, 70 s ; volet B, 64 s), et, si une démonstration en direct est prévue, l'assistant lancé sur le Mac cinq minutes avant.",
         "- Avancer d'un appui (flèche droite ou espace) à chaque nouvel élément évoqué : l'ordre des apparitions est indiqué sous chaque diapositive.", "",
         "## Déroulé", "",
         "| Diapositive | Début | Durée | Orateur |", "|---|---:|---:|---|"]
    t = 0
    for k, d in enumerate(ds, 1):
        l.append(f"| {k}. {d['titre']} | {mmss(t)} | {d['duree']} s | {ORATEURS.get(k, 'à définir')} |")
        t += d["duree"]
    l += [f"| Fin | {mmss(t)} | | |", ""]
    t = 0
    for k, d in enumerate(ds, 1):
        n = len(" ".join(d["dire"]).split())
        l += [f"### Diapositive {k} : {d['titre']}", "",
              f"**{ORATEURS.get(k, 'à définir')}**, de {mmss(t)} à {mmss(t + d['duree'])} ({d['duree']} s, {n} mots).", ""]
        if d["etapes"]:
            l.append("Apparitions, dans l'ordre des appuis :")
            l.append("")
            l += [f"- Appui {e} : {' ; puis '.join(xs)}" for e, xs in d["etapes"]]
            l.append("")
        l += [f"> {p}" if i == 0 else f">\n> {p}" for i, p in enumerate(d["dire"])]
        l.append("")
        if d["a_savoir"]:
            l.append("À savoir si on vous interrompt :")
            l.append("")
            l += [f"- {x}" for x in d["a_savoir"]]
            l.append("")
        t += d["duree"]
    l += ["## Pendant les questions : la démonstration", "",
          "- **Volet A, en direct** : annexe A1 du support (touche A, puis A1). Taper les questions telles quelles ; la dernière montre la limite de la recherche par le sens seule. Sans Internet : lire la vidéo de secours du volet A (70 s).",
          "- **Volet B** : lire la vidéo de secours (64 s). En direct seulement si le jury le demande et si l'assistant est déjà lancé : annexe A2, questions et réponses attendues.",
          "- **Autres questions** : sommaire des annexes (touche A) ; réponses préparées dans `questions_reponses.md`.", "",
          "## Chronométrage", "",
          "- Faire au moins deux répétitions complètes, chronomètre lancé (touche R pour le remettre à zéro).",
          f"- Repères : la diapositive 7 ({ds[6]['titre']}) commence à {mmss(sum(d['duree'] for d in ds[:6]))} ; "
          f"le bilan (diapositive 11) à {mmss(sum(d['duree'] for d in ds[:10]))}.",
          "- En cas de retard, raccourcir la diapositive 9 (trois modèles) et la diapositive 8 (10 passages), pas le bilan.", ""]
    (ICI / "script_oral.md").write_text("\n".join(l), encoding="utf-8")
    print(f"script_oral.md : {len(ds)} diapositives, {mmss(total)}, {mots} mots")


if __name__ == "__main__":
    main()
