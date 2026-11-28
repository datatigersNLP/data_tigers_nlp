"""Écrit le script oral de la soutenance (script_oral.md) à partir du support : le texte à dire de chaque diapositive, de
chaque démonstration et de la clôture est celui des notes de deck.html, mot pour mot ; le script ne peut donc pas diverger
du support.

    python3 docs/soutenance/8min/script_oral.py          # écrit docs/soutenance/8min/script_oral.md

Format du 28 novembre 2026 : 8 minutes au plus, démonstrations comprises. Neuf diapositives d'architecture, puis les
démonstrations en direct du volet A (annexe A1) et du volet B (annexe A2), puis une clôture de quelques secondes.

Répartition des orateurs, retenue par Mahé le 28 novembre 2026 : Remy ouvre (diapositives 1 à 4) et conclut, Mahé dit les
diapositives 5 à 7, Jibril les diapositives 8 et 9, Vaneck fait la démonstration du volet A, Maïmouna celle du volet B. Une
seule personne tient le clavier (Mahé). Le texte de la répartition écrit dans le script est tiré de ces constantes.
"""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from pathlib import Path

ICI = Path(__file__).resolve().parent
ORATEURS = {1: "Remy", 2: "Remy", 3: "Remy", 4: "Remy", 5: "Mahé", 6: "Mahé", 7: "Mahé", 8: "Jibril", 9: "Jibril"}
ORATEUR_DEMO = {"1": "Vaneck", "2": "Maïmouna"}
ORATEUR_CLOTURE = "Remy"
CLAVIER = "Mahé"
LIMITE = 480            # secondes : la présentation dure 8 minutes au plus, démonstrations comprises


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


def abrege(x: str, n: int = 110) -> str:
    """Texte coupé à une limite de mot, jamais au milieu d'un mot."""
    return x if len(x) <= n else x[:n].rsplit(" ", 1)[0].rstrip(" ,;:") + " …"


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


def demonstrations(deck: str) -> list[dict]:
    """Démonstrations en direct (annexes portant data-demo) : questions du tableau, texte à dire, clôture éventuelle."""
    sortie = []
    for m in re.finditer(r'<section class="diapo annexe" data-duree="0" data-demo="(\d+)"([^>]*)data-annexe="(\d+)" aria-label="([^"]+)">(.*?)</section>',
                         deck, re.S):
        duree, attributs, numero, nom, corps = int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5)
        cloture = re.search(r'data-cloture="(\d+)"', attributs)
        aside = re.search(r'<aside class="texte-a-dire"[^>]*>(.*?)</aside>', corps, re.S).group(1)
        lignes = []
        for tr in re.findall(r"<tr>(.*?)</tr>", re.search(r"<tbody>(.*?)</tbody>", corps, re.S).group(1), re.S):
            lignes.append([texte(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)])
        sortie.append({"annexe": numero, "nom": re.sub(r"^Annexe \d+\. ", "", nom), "duree": duree,
                       "cloture_duree": int(cloture.group(1)) if cloture else 0,
                       "dire": [texte(p) for p in re.findall(r"<p>(.*?)</p>", aside, re.S)],
                       "cloture": [texte(p) for p in re.findall(r'<p class="cloture">(.*?)</p>', aside, re.S)],
                       "a_savoir": [texte(li) for li in re.findall(r"<li>(.*?)</li>", aside, re.S)], "lignes": lignes})
    return sortie


def plages(orateurs: dict[int, str]) -> list[str]:
    """Diapositives consécutives d'un même orateur, en une phrase : « Remy les diapositives 1 à 4 »."""
    sortie, debut = [], 1
    for k in range(1, len(orateurs) + 1):
        if k == len(orateurs) or orateurs[k + 1] != orateurs[k]:
            if debut == k:
                texte_plage = f"la diapositive {k}"
            else:
                texte_plage = f"les diapositives {debut} {'et' if k - debut == 1 else 'à'} {k}"
            sortie.append(f"{orateurs[k]} {texte_plage}")
            debut = k + 1
    return sortie


def mmss(s: int) -> str:
    return f"{s // 60}:{s % 60:02d}"


def nb_mots(paragraphes: list[str]) -> int:
    return len(" ".join(paragraphes).split())


def main() -> None:
    deck = (ICI / "deck.html").read_text(encoding="utf-8")
    ds, demos = diapositives(deck), demonstrations(deck)
    assert len(ds) == len(ORATEURS), f"{len(ds)} diapositives pour {len(ORATEURS)} orateurs : mettre à jour ORATEURS"
    assert [d["annexe"] for d in demos] == list(ORATEUR_DEMO), "démonstrations attendues : annexes 1 et 2"
    t_pres = sum(d["duree"] for d in ds)
    t_demos = sum(d["duree"] for d in demos)
    t_cloture = sum(d["cloture_duree"] for d in demos)
    total = t_pres + t_demos + t_cloture
    mots_pres = sum(nb_mots(d["dire"]) for d in ds)
    assert total <= LIMITE, f"{mmss(total)} dépasse les {mmss(LIMITE)} autorisées"
    l = ["# Script oral de la soutenance (8 minutes, démonstrations comprises)", "",
         "**Source** le texte à dire est celui des notes de `deck.html`, mot pour mot ; ce fichier est généré par `script_oral.py` : "
         "ne pas le modifier à la main, modifier le support puis relancer le script.", "",
         f"**Durée prévue** {mmss(total)} sur {mmss(LIMITE)} au plus, marge de {LIMITE - total} s : présentation de {len(ds)} diapositives {mmss(t_pres)} "
         f"({mots_pres} mots, {mots_pres / t_pres * 60:.0f} mots par minute), démonstration du volet A {mmss(demos[0]['duree'])}, "
         f"démonstration du volet B {mmss(demos[1]['duree'])}, clôture {mmss(t_cloture)}.", "",
         "**Orateurs** répartition retenue par Mahé le 28 novembre : " + ", ".join(plages(ORATEURS))
         + f", {ORATEUR_DEMO['1']} la démonstration du volet A, {ORATEUR_DEMO['2']} la démonstration du volet B, {ORATEUR_CLOTURE} la clôture ; "
         f"{CLAVIER} tient le clavier pendant toute la soutenance.", "",
         "---", "",
         "## Avant de commencer", "",
         "- Ouvrir `Soutenance_Data_Tigers_8min.html` (hors ligne), touche F pour le plein écran.",
         "- Les notes (touche N) s'affichent sur la page projetée : ne les ouvrir qu'en répétition, ou avec un second écran qui ne recopie pas le premier.",
         "- Ouvrir à l'avance, dans un autre onglet, le site du volet A, et y poser une première question : la première visite télécharge le modèle.",
         "- Lancer l'assistant du volet B sur le Mac cinq minutes avant (`lancer_demo_volet_b.zsh`), ouvrir les deux onglets, le modèle adapté sur le port 8765 et le témoin T sur le port 8766, "
         "et poser une question d'échauffement dans chacun, en finissant par le modèle adapté.",
         "- Avoir les deux vidéos de secours prêtes (volet A, 70 s ; volet B, 64 s), sans les lancer.",
         "- Avancer d'un appui (flèche droite ou espace) à chaque nouvel élément évoqué : l'ordre des apparitions est indiqué sous chaque diapositive.",
         "- À éviter en direct : la question de la diapositive 2 (le modèle adapté s'abstient alors que le bon passage est en tête), la période d'essai d'un cadre (réponse en fragment), "
         "les 48 heures (dérogation attribuée à l'inspecteur du travail, alors que le passage dit la DREETS).", "",
         "## Déroulé", "",
         "| Partie | Début | Durée | Orateur |", "|---|---:|---:|---|"]
    t = 0
    for k, d in enumerate(ds, 1):
        l.append(f"| Diapositive {k}. {d['titre']} | {mmss(t)} | {d['duree']} s | {ORATEURS[k]} |")
        t += d["duree"]
    for d in demos:
        volet = d["nom"].split("Démonstration du ")[1].split(",")[0]
        l.append(f"| Démonstration du {volet}, en direct | {mmss(t)} | {d['duree']} s | {ORATEUR_DEMO[d['annexe']]} |")
        t += d["duree"]
    l += [f"| Clôture | {mmss(t)} | {t_cloture} s | {ORATEUR_CLOTURE} |", f"| Fin | {mmss(t + t_cloture)} | | |", ""]
    t = 0
    for k, d in enumerate(ds, 1):
        l += [f"### Diapositive {k} : {d['titre']}", "",
              f"**{ORATEURS[k]}**, de {mmss(t)} à {mmss(t + d['duree'])} ({d['duree']} s, {nb_mots(d['dire'])} mots).", ""]
        if d["etapes"]:
            l += ["Apparitions, dans l'ordre des appuis :", ""]
            l += [f"- Appui {e} : {' ; puis '.join(xs)}" for e, xs in d["etapes"]]
            l.append("")
        l += [f"> {p}" if i == 0 else f">\n> {p}" for i, p in enumerate(d["dire"])]
        l.append("")
        if d["a_savoir"]:
            l += ["À savoir si on vous interrompt :", ""] + [f"- {x}" for x in d["a_savoir"]] + [""]
        t += d["duree"]
    for d in demos:
        l += [f"### {d['nom']}", "",
              f"**{ORATEUR_DEMO[d['annexe']]}**, de {mmss(t)} à {mmss(t + d['duree'])} ({d['duree']} s, {nb_mots(d['dire'])} mots ; {CLAVIER} tape les questions). "
              f"Annexe A{d['annexe']} du support.", "",
              "Questions, dans l'ordre :", ""]
        for i, c in enumerate(d["lignes"], 1):
            l.append(f"- {i}. {c[0]} ({' ; '.join(c[1:])})" + ("" if i <= 3 else " : en réserve, pour les questions du jury"))
        l.append("")
        l += [f"> {p}" if i == 0 else f">\n> {p}" for i, p in enumerate(d["dire"])]
        l.append("")
        if d["a_savoir"]:
            l += ["À savoir si on vous interrompt :", ""] + [f"- {x}" for x in d["a_savoir"]] + [""]
        t += d["duree"]
        if d["cloture"]:
            l += ["### Clôture", "",
                  f"**{ORATEUR_CLOTURE}**, de {mmss(t)} à {mmss(t + d['cloture_duree'])} ({d['cloture_duree']} s, {nb_mots(d['cloture'])} mots).", ""]
            l += [f"> {p}" for p in d["cloture"]] + [""]
            t += d["cloture_duree"]
    l += ["## Si quelque chose ne se passe pas comme prévu", "",
          "- **Le site du volet A ne répond pas, ou pas d'Internet** : lire la vidéo de secours du volet A (70 s), filmée sur le site en ligne, en le disant.",
          "- **L'assistant du volet B ne démarre pas, ou la génération est lente** : lire la vidéo de secours du volet B (64 s). Si la génération est seulement lente, passer la troisième question : "
          "l'abstention hors corpus est déjà montrée par le volet A.",
          "- **Une réponse en direct est mauvaise** : dire que les questions ont été choisies après essai, que c'est une illustration et non une mesure, puis passer à la vidéo.",
          "- **Le support ne s'ouvre pas** : le même fichier sur le second ordinateur ou sur la clé, sinon le PDF de secours, une page par appui.", "",
          "## Pendant les questions", "",
          "- **Autres questions** : sommaire des annexes (touche A) ; réponses préparées dans `questions_reponses.md`.",
          "- **Reprendre une démonstration** : annexes A1 et A2 (touche A, puis le numéro).", "",
          "## Chronométrage", "",
          "- Faire au moins deux répétitions complètes, chronomètre lancé (touche R pour le remettre à zéro), démonstrations comprises, sur le Mac de la soutenance.",
          f"- Repères : la diapositive 7 ({ds[6]['titre']}) commence à {mmss(sum(d['duree'] for d in ds[:6]))} ; la présentation finit à {mmss(t_pres)} ; "
          f"la démonstration du volet B commence à {mmss(t_pres + demos[0]['duree'])} ; la clôture à {mmss(t_pres + t_demos)}.",
          "- En cas de retard, raccourcir les diapositives 8 (10 passages) et 3 (préparation commune), puis passer la troisième question de la démonstration du volet B.", ""]
    (ICI / "script_oral.md").write_text("\n".join(l), encoding="utf-8")
    print(f"script_oral.md : {len(ds)} diapositives {mmss(t_pres)} + démonstrations {mmss(t_demos)} + clôture {mmss(t_cloture)} = {mmss(total)}, "
          f"{mots_pres} mots de présentation")


if __name__ == "__main__":
    main()
