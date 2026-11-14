"""Figures des supports de soutenance (#114), en SVG autonomes.

Les couleurs sont écrites dans les attributs, pour que Marp les affiche telles quelles. Chaque élément animable porte
une classe (« b » pour une boîte, « f » pour une flèche, « barre », « lien », « point ») et un rang d'apparition
--i, que la version HTML utilise ; Marp les ignore. Les identifiants des marqueurs sont préfixés par le nom de la
figure, car la version HTML place toutes les figures dans la même page.

Chiffres repris des sources vérifiées : étude 01 du découpage (#35), notebook 03, protocole 06 et résultats du 11/11
publiés sur le #52. Exécution : python3 docs/soutenance/outils/figures.py (aucune dépendance).
"""

from pathlib import Path

ICI = Path(__file__).resolve().parent
SORTIE = ICI.parent / "figures"

ENCRE, BLEU, GRIS, FILET, FOND = "#111827", "#1f3b73", "#5b6472", "#cfd5dc", "#f3f5f8"
A, A_FOND, B, B_FOND = "#2c5d8a", "#e7eef6", "#2e6a4f", "#e6f0ea"
POLICE = "IBM Plex Sans, Helvetica Neue, Arial, sans-serif"
MONO = "IBM Plex Mono, Menlo, monospace"
NB = " "


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def largeur_texte(t, taille):
    return len(t) * taille * 0.56


class Figure:
    def __init__(self, nom, largeur, hauteur, titre):
        self.nom, self.l, self.h, self.titre, self.corps = nom, largeur, hauteur, titre, []

    def ajoute(self, s):
        self.corps.append(s)

    def marqueurs(self):
        m = []
        for cle, couleur in (("n", GRIS), ("a", A), ("b", B), ("u", BLEU)):
            m.append(f'<marker id="{self.nom}-{cle}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" '
                     f'markerHeight="7" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{couleur}"/></marker>')
        return "<defs>" + "".join(m) + "</defs>"

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.l} {self.h}" role="img" '
                f'aria-label="{esc(self.titre)}" font-family="{POLICE}">\n<title>{esc(self.titre)}</title>\n'
                + self.marqueurs() + "\n" + "\n".join(self.corps) + "\n</svg>\n")

    def ecrire(self):
        SORTIE.mkdir(parents=True, exist_ok=True)
        (SORTIE / f"{self.nom}.svg").write_text(self.svg(), encoding="utf-8")


def boite(fig, x, y, w, h, lignes, sous=None, genre="n", i=0, taille=17, gras=True):
    trait, fond = {"n": (FILET, FOND), "a": (A, A_FOND), "b": (B, B_FOND), "u": (BLEU, "#e8edf6")}[genre]
    lignes = [lignes] if isinstance(lignes, str) else lignes
    sous = [sous] if isinstance(sous, str) else (sous or [])
    n = len(lignes) + len(sous)
    pas = taille * 1.25
    y0 = y + h / 2 - (n - 1) * pas / 2 + taille * 0.35
    t = [f'<g class="b" style="--i:{i}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fond}" '
         f'stroke="{trait}" stroke-width="1.4"/>']
    for k, l in enumerate(lignes):
        t.append(f'<text x="{x + w / 2}" y="{y0 + k * pas:.1f}" text-anchor="middle" font-size="{taille}" '
                 f'font-weight="{600 if gras else 400}" fill="{ENCRE}">{esc(l)}</text>')
    for k, l in enumerate(sous):
        t.append(f'<text x="{x + w / 2}" y="{y0 + (len(lignes) + k) * pas:.1f}" text-anchor="middle" '
                 f'font-size="{taille - 2}" font-family="{MONO}" fill="{GRIS}">{esc(l)}</text>')
    t.append("</g>")
    fig.ajoute("".join(t))
    largeur_min = max([largeur_texte(l, taille) for l in lignes] + [largeur_texte(l, taille - 2) * 1.08 for l in sous])
    assert largeur_min <= w - 10, f"{fig.nom} : texte trop large ({largeur_min:.0f} > {w - 10}) : {lignes} {sous}"


def fleche(fig, d, genre="n", i=0):
    couleur = {"n": GRIS, "a": A, "b": B, "u": BLEU}[genre]
    fig.ajoute(f'<path class="f" style="--i:{i}" d="{d}" fill="none" stroke="{couleur}" stroke-width="2" '
               f'marker-end="url(#{fig.nom}-{genre})"/>')


def etiquette(fig, x, y, texte, couleur=GRIS, taille=14, ancre="start", poids=600, i=0, classe="b"):
    fig.ajoute(f'<text class="{classe}" style="--i:{i}" x="{x}" y="{y}" text-anchor="{ancre}" font-size="{taille}" '
               f'font-weight="{poids}" fill="{couleur}" letter-spacing="0.4">{esc(texte)}</text>')


def rangee(fig, y, h, x0, x1, items, genre, i0=0, gap=34):
    """Boîtes réparties sur [x0, x1] avec des flèches entre elles ; largeur proportionnelle au texte."""
    besoins = []
    for it in items:
        lignes = it[0] if isinstance(it[0], list) else [it[0]]
        sous = it[1] if len(it) > 1 else None
        sous_l = [sous] if isinstance(sous, str) else (sous or [])
        besoins.append(max([largeur_texte(l, 17) for l in lignes] + [largeur_texte(l, 15) * 1.08 for l in sous_l]) + 24)
    libre = (x1 - x0) - gap * (len(items) - 1)
    total = sum(besoins)
    assert total <= libre, f"{fig.nom} : rangée trop large ({total:.0f} > {libre:.0f})"
    extra = (libre - total) / len(items)
    x, pos = x0, []
    for k, (it, bes) in enumerate(zip(items, besoins)):
        w = bes + extra
        g = it[2] if len(it) > 2 else genre
        boite(fig, round(x, 1), y, round(w, 1), h, it[0], it[1] if len(it) > 1 else None, g, i0 + 2 * k)
        pos.append((x, w))
        if k:
            px, pw = pos[k - 1]
            fleche(fig, f"M{px + pw + 2:.1f},{y + h / 2} H{x - 4:.1f}", "n" if g == "n" else g, i0 + 2 * k - 1)
        x += w + gap
    return pos


# 1. Frise du projet : étapes dans l'ordre, espacées régulièrement (une séquence, pas une échelle de temps)
def frise():
    evts = [("21/09", ["J2 : cas A3", "et B1 choisis"]), ("27/09", ["corpus découpé,", "1re inférence"]),
            ("30/09", ["site du volet A", "en ligne"]), ("13/10", ["mesure officielle", "du volet A"]),
            ("27/10", ["chaîne RAG", "du volet B"]), ("04/11", ["protocole 06", "gelé"]),
            ("09/11", ["mesure avant", "(PC Legion)"]), ("11/11", ["adaptation,", "mesure après"]),
            ("16/11", ["J3, revue", "d'avancement"]), ("30/11", ["soutenance"])]
    f = Figure("frise", 1200, 220, "Frise du projet, du J2 à la soutenance")
    y = 110
    f.ajoute(f'<line class="f" style="--i:0" x1="90" y1="{y}" x2="1110" y2="{y}" stroke="{FILET}" stroke-width="3"/>')
    pas = 1020 / (len(evts) - 1)
    for k, (date, lignes) in enumerate(evts):
        x = 90 + k * pas
        fort = date in ("09/11", "11/11")
        couleur = BLEU if fort else GRIS
        f.ajoute(f'<circle class="point" style="--i:{k + 1}" cx="{x:.1f}" cy="{y}" r="{8 if fort else 6}" '
                 f'fill="{couleur if fort else "#ffffff"}" stroke="{couleur}" stroke-width="2.5"/>')
        haut = k % 2 == 0
        yd = y - 62 if haut else y + 40
        etiquette(f, round(x, 1), yd, date, BLEU if fort else ENCRE, 17, "middle", 700, k + 1)
        for j, l in enumerate(lignes):
            etiquette(f, round(x, 1), yd + 20 + 18 * j, l, GRIS, 15, "middle", 400, k + 1)
            assert largeur_texte(l, 15) < 2 * pas - 20
    f.ecrire()


# 2. Découpage : part du texte rattaché à une autre section que celle citée (étude 01, #35), à l'échelle
def decoupage():
    donnees = [("M0", "découpage de l'éditeur", 23.4), ("M1", "fenêtre glissante, 20 % de chevauchement", 17.9),
               ("M3", "coupure sémantique", 14.2), ("M2", "découpage structurel, retenu", 0.0)]
    f = Figure("decoupage", 1100, 300, "Part du texte rattaché à une autre section que celle citée, par méthode")
    x0, x1, vmax = 460, 1020, 25.0
    ech = (x1 - x0) / vmax
    for t in range(0, 26, 5):
        x = x0 + t * ech
        f.ajoute(f'<line x1="{x:.1f}" y1="20" x2="{x:.1f}" y2="236" stroke="{FILET}" stroke-width="1"/>'
                 f'<text x="{x:.1f}" y="258" text-anchor="middle" font-size="14" font-family="{MONO}" fill="{GRIS}">{t}{NB}%</text>')
    for k, (code, lib, v) in enumerate(donnees):
        y = 34 + k * 52
        retenu = code == "M2"
        couleur = BLEU if retenu else "#9aa3ad"
        f.ajoute(f'<text class="b" style="--i:{k}" x="20" y="{y + 20}" font-size="18" font-weight="700" fill="{BLEU if retenu else ENCRE}">{code}</text>'
                 f'<text class="b" style="--i:{k}" x="64" y="{y + 20}" font-size="16" fill="{ENCRE if retenu else GRIS}">{esc(lib)}</text>')
        w = v * ech
        if v > 0:
            f.ajoute(f'<rect class="barre" style="--i:{k}" x="{x0}" y="{y + 4}" width="{w:.1f}" height="24" rx="3" fill="{couleur}"/>')
        else:
            f.ajoute(f'<rect class="barre" style="--i:{k}" x="{x0}" y="{y + 4}" width="3" height="24" fill="{couleur}"/>')
        f.ajoute(f'<text class="b" style="--i:{k}" x="{x0 + w + 10:.1f}" y="{y + 22}" font-size="17" font-weight="700" '
                 f'font-family="{MONO}" fill="{BLEU if retenu else ENCRE}">{str(v).replace(".", ",")}{NB}%</text>')
    f.ajoute(f'<text x="{x0}" y="290" font-size="14" fill="{GRIS}">part du texte des passages rattachée à une autre section que celle citée</text>')
    f.ecrire()


# 3. Chaîne du volet A
def chaine_a():
    f = Figure("chaine_a", 1200, 250, "Chaîne du volet A : index calculé une fois, question encodée dans le navigateur")
    etiquette(f, 20, 22, "UNE FOIS, À LA CONSTRUCTION DU SITE", GRIS, 14)
    haut = rangee(f, 32, 62, 20, 760, [(["4 240 passages"], "découpage M2"), (["E5-small"], "« passage: »"),
                                        (["Index"], f"4{NB}240 × 384 nombres")], "n", 0)
    etiquette(f, 20, 132, "À CHAQUE QUESTION, DANS LE NAVIGATEUR", A, 14, i=6)
    bas = rangee(f, 142, 74, 20, 1180, [(["Question"], "« query: »"), (["E5 q8 élagué"], [f"65,7{NB}Mio,", f"18,3{NB}ms"]),
                                          (["Vecteur"], "384 nombres"), (["Produit scalaire"], f"4{NB}240 scores"),
                                          (["5 passages + liens"], ["sous 0,8560 :", "hors périmètre"])], "a", 7)
    xi, wi = haut[2]
    xp, wp = bas[3]
    fleche(f, f"M{xi + wi / 2:.1f},94 V112 H{xp + wp / 2:.1f} V138", "a", 16)
    f.ecrire()


# 4. Chaîne du volet B
def chaine_b():
    f = Figure("chaine_b", 1200, 250, "Chaîne du volet B : récupération, seuil, contexte numéroté, Qwen, contrôle")
    etiquette(f, 20, 22, "À CHAQUE QUESTION, SUR LA MACHINE LOCALE", B, 14)
    pos = rangee(f, 32, 84, 20, 1180, [(["Question"],), (["E5 fp32"], "5 passages"),
                                         (["Score max", "≥ S ?"], "S = 0,8565"), (["Contexte"], ["consigne +", "[P1] à [P5]"]),
                                         (["Qwen2.5-7B"], ["Q4_K_M,", "Ollama"]), (["Contrôle"], "des citations")], "b", 0)
    x, w = pos[2]
    fleche(f, f"M{x + w / 2:.1f},116 V160", "b", 12)
    boite(f, round(x + w / 2 - 170, 1), 164, 340, 58, ["non : abstention"], "sans appeler le modèle", "n", 13, 16)
    xr, wr = pos[5]
    fleche(f, f"M{xr + wr / 2:.1f},116 V160", "b", 14)
    boite(f, round(min(xr + wr / 2 - 150, 1180 - 300), 1), 164, 300, 58, ["réponse citée"], "ou abstention", "b", 15, 16)
    f.ecrire()


# 5. Données d'adaptation (lot v2b, #107, #115)
def donnees():
    f = Figure("donnees", 1200, 250, "Construction des données d'adaptation, façon RAFT")
    etiquette(f, 20, 22, "POUR CHAQUE EXEMPLE", B, 14)
    rangee(f, 32, 92, 20, 1180, [(["Passage cible"], ["hors des 61", "fiches du test"]), (["Question"], ["écrite", "par Qwen"]),
                                   (["5 passages"], ["récupérés", "par E5"]), (["Réponse"], ["recopiée,", "avec [Pk]"]),
                                   (["Filtres"], ["cible citée,", "recopie exacte"]), (["Relecture"], ["humaine,", "30 exemples"])], "b", 0)
    boite(f, 20, 160, 1160, 62, [f"Lot v2b : 218 exemples, 164 réponses citées et 54 abstentions hors corpus (24,8{NB}%)"],
          f"198 pour l'entraînement, 20 pour la validation ; 3 faux sur 30 à la relecture", "u", 12, 18)
    f.ecrire()


# 6. Entraînement, fusion, export et témoin T (#125, #140)
def export():
    f = Figure("export", 1200, 330, "Entraînement LoRA, fusion dans les poids bf16, export vers Ollama, témoin T")
    etiquette(f, 20, 22, "ENTRAÎNEMENT, MLX SUR LE MAC", B, 14)
    h1 = rangee(f, 32, 66, 20, 760, [(["Base 4 bits"], "gelée"), (["LoRA, rang 8"], "396 itérations"),
                                       (["Adaptateur"], f"11,5{NB}M paramètres")], "b", 0)
    etiquette(f, 20, 132, "EXPORT DU MODÈLE ADAPTÉ", B, 14, i=6)
    h2 = rangee(f, 142, 66, 20, 1180, [(["Poids bf16"], "officiels"), (["Fusion"], "W + 20·(A·B)ᵀ"),
                                         (["GGUF f16"], "339 tenseurs vérifiés"), (["Q4_K_M"], f"4,9 bits/poids"),
                                         (["Ollama"], "modèle adapté")], "b", 7)
    xa, wa = h1[2]
    xf, wf = h2[1]
    fleche(f, f"M{xa + wa / 2:.1f},98 V116 H{xf + wf / 2:.1f} V138", "b", 16)
    etiquette(f, 20, 242, "TÉMOIN T : MÊME CHAÎNE, SANS ADAPTATEUR", GRIS, 14, i=17)
    rangee(f, 252, 62, 20, 1180, [(["Poids bf16"], "officiels"), (["GGUF f16"],), (["Q4_K_M"],), (["Ollama"], "témoin T")], "n", 18)
    f.ecrire()


# 7. Résultats, B2 : témoin T contre modèle adapté (#52, 11/11), à l'échelle
def resultats():
    lignes = [("M4", "citation pertinente", 13.9, 25.0), ("M3", "citation valide", 25.0, 44.4),
              ("M2", "abstention à tort (plus bas = mieux)", 70.8, 55.6), ("M1", "abstention correcte, hors corpus", 83.3, 83.3)]
    f = Figure("resultats", 1200, 340, "État B2 : taux du témoin T et du modèle adapté sur M4, M3, M2 et M1")
    x0, x1 = 470, 1150
    ech = (x1 - x0) / 100
    for t in (0, 25, 50, 75, 100):
        x = x0 + t * ech
        f.ajoute(f'<line x1="{x:.1f}" y1="44" x2="{x:.1f}" y2="290" stroke="{FILET}" stroke-width="1"/>'
                 f'<text x="{x:.1f}" y="314" text-anchor="middle" font-size="15" font-family="{MONO}" fill="{GRIS}">{t}{NB}%</text>')
    f.ajoute(f'<circle cx="{x0}" cy="16" r="7" fill="#ffffff" stroke="{GRIS}" stroke-width="2.5"/>'
             f'<text x="{x0 + 14}" y="21" font-size="15" fill="{GRIS}">témoin T</text>'
             f'<circle cx="{x0 + 120}" cy="16" r="7" fill="{B}"/><text x="{x0 + 134}" y="21" font-size="15" fill="{B}">modèle adapté</text>')
    for k, (code, lib, t, a) in enumerate(lignes):
        y = 72 + k * 60
        f.ajoute(f'<text x="20" y="{y + 6}" font-size="18" font-weight="700" fill="{ENCRE}">{code}</text>'
                 f'<text x="66" y="{y + 6}" font-size="16" fill="{GRIS}">{esc(lib)}</text>')
        xt, xa = x0 + t * ech, x0 + a * ech
        f.ajoute(f'<line class="lien" style="--i:{k}" x1="{xt:.1f}" y1="{y}" x2="{xa:.1f}" y2="{y}" stroke="{GRIS}" stroke-width="3"/>')
        f.ajoute(f'<circle class="point" style="--i:{k}" cx="{xt:.1f}" cy="{y}" r="8" fill="#ffffff" stroke="{GRIS}" stroke-width="2.5"/>'
                 f'<circle class="point" style="--i:{k}" cx="{xa:.1f}" cy="{y}" r="8" fill="{B}"/>')
        v = lambda z: f"{z:.1f}".replace(".", ",") + f"{NB}%"
        if t == a:
            f.ajoute(f'<text class="b" style="--i:{k}" x="{xa - 16:.1f}" y="{y + 6}" text-anchor="end" font-size="16" font-family="{MONO}" fill="{B}">{v(a)} des deux côtés</text>')
        elif a > t:
            f.ajoute(f'<text class="b" style="--i:{k}" x="{xt - 18:.1f}" y="{y + 6}" text-anchor="end" font-size="16" font-family="{MONO}" fill="{GRIS}">{v(t)}</text>'
                     f'<text class="b" style="--i:{k}" x="{xa + 18:.1f}" y="{y + 6}" font-size="16" font-weight="700" font-family="{MONO}" fill="{B}">{v(a)}</text>')
        else:
            f.ajoute(f'<text class="b" style="--i:{k}" x="{xa - 18:.1f}" y="{y + 6}" text-anchor="end" font-size="16" font-weight="700" font-family="{MONO}" fill="{B}">{v(a)}</text>'
                     f'<text class="b" style="--i:{k}" x="{xt + 18:.1f}" y="{y + 6}" font-size="16" font-family="{MONO}" fill="{GRIS}">{v(t)}</text>')
    f.ecrire()


# 8. Trois mécanismes : bi-encodeur, cross-encodeur, LoRA
def mecanismes():
    f = Figure("mecanismes", 1200, 300, "Bi-encodeur, cross-encodeur et adaptation LoRA")
    etiquette(f, 20, 22, "BI-ENCODEUR (E5)", A, 14)
    boite(f, 20, 40, 120, 46, "question", None, "n", 0, 16)
    boite(f, 20, 130, 120, 46, "passage", None, "n", 0, 16)
    boite(f, 168, 40, 120, 46, "encodeur", None, "a", 1, 16)
    boite(f, 168, 130, 120, 46, "encodeur", None, "a", 1, 16)
    boite(f, 316, 40, 56, 46, "q", None, "n", 2, 16)
    boite(f, 316, 130, 56, 46, "p", None, "n", 2, 16)
    boite(f, 388, 85, 46, 46, "·", None, "u", 3, 20)
    for d in ("M140,63 H164", "M140,153 H164", "M288,63 H312", "M288,153 H312", "M372,63 H380 V98 H384", "M372,153 H380 V118 H384"):
        fleche(f, d, "a", 2)
    for j, l in enumerate(["p est calculé une fois (index) ;", "score = cosinus(q, p)"]):
        etiquette(f, 20, 220 + 22 * j, l, GRIS, 15, poids=400, i=4)

    etiquette(f, 470, 22, "CROSS-ENCODEUR (BGE)", B, 14)
    boite(f, 470, 85, 190, 46, "question + passage", None, "n", 5, 16)
    boite(f, 690, 72, 150, 72, "transformeur", "24 couches", "b", 6, 16)
    boite(f, 870, 85, 80, 46, "score", None, "n", 7, 16)
    fleche(f, "M660,108 H686", "b", 6)
    fleche(f, "M840,108 H866", "b", 7)
    for j, l in enumerate(["les deux textes sont lus ensemble :", "plus précis, un calcul par paire"]):
        etiquette(f, 470, 220 + 22 * j, l, GRIS, 15, poids=400, i=8)

    etiquette(f, 990, 22, "LORA (QWEN)", B, 14)
    boite(f, 990, 40, 120, 56, "W gelée", "4 bits", "n", 9, 16)
    boite(f, 990, 120, 56, 46, "A", None, "b", 10, 16)
    boite(f, 1054, 120, 56, 46, "B", None, "b", 10, 16)
    boite(f, 1140, 85, 46, 46, "+", None, "u", 11, 20)
    fleche(f, "M1110,68 H1126 V98 H1136", "b", 11)
    fleche(f, "M1110,143 H1126 V118 H1136", "b", 11)
    for j, l in enumerate(["rang 8, facteur 20 ;", "seuls A et B s'entraînent"]):
        etiquette(f, 990, 220 + 22 * j, l, GRIS, 15, poids=400, i=12)
    f.ecrire()


if __name__ == "__main__":
    for fonction in (frise, decoupage, chaine_a, chaine_b, donnees, export, resultats, mecanismes):
        fonction()
    print(sorted(p.name for p in SORTIE.glob("*.svg")))
