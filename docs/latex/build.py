#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, sys, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md2tex import convert, inline, esc, TBL

if len(sys.argv) < 2:
    sys.exit("usage : python3 build.py <document.md>")
DOC = os.path.abspath(sys.argv[1])
SRC = DOC
OUT = os.path.splitext(DOC)[0] + ".tex"

# Bandeau de titre par document : (titre, sous-titre, surtitre)
BANDEAU = {
 "03_SUPPORT_REUNION_J2": ("Réunion de cadrage",
     "Projet NLP~2 \\textbullet{} M2 Data \\& IA \\textbullet{} FGES \\textemdash{} Université Catholique de Lille",
     "Jalon J2 \\textemdash{} 10 points"),
 "06_JOURNAL_USAGE_IA": ("Journal d'usage de l'IA",
     "Équipe Data Tigers \\textbullet{} NLP~2 \\textbullet{} M2 Data \\& IA \\textbullet{} FGES",
     "Ouvert le 18 septembre 2026, tenu jusqu'à la soutenance"),
 "05_RAPPORT_J2": ("Rapport de jalon J2",
     "Équipe Data Tigers \\textbullet{} NLP~2 \\textbullet{} M2 Data \\& IA \\textbullet{} FGES",
     "Année universitaire 2026-2027"),
}
SCR = os.path.dirname(os.path.abspath(__file__))
PRE = os.path.join(SCR, "preambule.tex")


def mesurer(chunks):
    """Mesure par XeLaTeX la largeur du plus large fragment insécable de chaque
    colonne, en-tête en gras et corps en romain, à la taille effective du tableau."""
    L = [r'\documentclass[11pt,a4paper]{article}', r'\usepackage{fontspec}',
         r'\usepackage[french]{babel}',
         r'\newfontfamily\tabfont{Inter-Regular.otf}[BoldFont=Inter-Bold.otf,'
         r'ItalicFont=Inter-Italic.otf,BoldItalicFont=Inter-BoldItalic.otf,Scale=0.94]',
         r'\setmonofont{FiraMono-Regular.otf}[BoldFont=FiraMono-Bold.otf,Scale=0.84]',
         r'\usepackage{pifont}\usepackage{fontawesome5}\usepackage{xcolor}',
         r'\newcommand{\okmark}{\ding{51}}\newcommand{\komark}{\ding{55}}',
         r'\newcommand{\warnmark}{\faExclamationTriangle}',
         r'\newcommand{\checkbox}{\ding{113}}\newcommand{\cutmark}{\ding{34}}',
         r'\newcommand{\starmark}{\ding{72}}\newcommand{\wipmark}{\faTools}',
         r'\newcommand{\code}[1]{{\ttfamily #1}}',
         r'\newlength{\W}\newlength{\M}', r'\begin{document}']
    for k, j, size, hdr, bod in chunks:
        L.append(r'\setlength{\M}{0pt}')
        for (txt, mono), gras in [(x, True) for x in hdr] + [(x, False) for x in bod]:
            # tout est mesuré en gras : borne supérieure sûre, car une cellule
            # du corps peut elle aussi être en gras (**...** dans le markdown).
            fonte = r'\ttfamily\bfseries' if mono else r'\tabfont\bfseries'
            body = fonte + '\\' + size + ' ' + esc(txt)
            L.append(r'\settowidth{\W}{%s}\ifdim\W>\M\setlength{\M}{\W}\fi' % body)
        L.append(r'\typeout{MW|%d|%d|\the\M}' % (k, j))
    L.append(r'\end{document}')
    probe = os.path.join(SCR, 'probe.tex')
    open(probe, 'w', encoding='utf-8').write('\n'.join(L))
    subprocess.run(['xelatex', '-interaction=nonstopmode', 'probe.tex'],
                   cwd=SCR, capture_output=True)
    out = {}
    for line in open(os.path.join(SCR, 'probe.log'), encoding='utf-8', errors='replace'):
        m = re.match(r'MW\|(\d+)\|(\d+)\|([\d.]+)pt', line.strip())
        if m: out[(int(m.group(1)), int(m.group(2)))] = float(m.group(3))
    return out

md = open(SRC, encoding='utf-8').read()
head, body = md.split('\n---\n', 1)
hl = head.split('\n')

titre_brut = hl[0].lstrip('# ').strip()
meta, quote, libres = [], [], []
for l in hl[1:]:
    s = l.strip()
    if not s: continue
    m = re.match(r'^\*\*([^*]+?)\*\*\s+(\S.*)$', s)
    if s.startswith('>'):
        quote.append(s[1:].lstrip())
    elif m and not s.endswith('.') or (m and len(m.group(1)) < 24 and not m.group(1).endswith('.')):
        meta.append((m.group(1), m.group(2)))
    else:
        libres.append(s)

ENTETE = {
 "03_SUPPORT_REUNION_J2": r"Réunion de cadrage \textbullet{} Projet NLP 2",
 "05_RAPPORT_J2":         r"Rapport de jalon J2 \textbullet{} Équipe Data Tigers",
 "06_JOURNAL_USAGE_IA":   r"Journal d'usage de l'IA \textbullet{} Équipe Data Tigers",
}

T = []
T.append(r'\renewcommand{\entetecourant}{%s}'
         % ENTETE.get(os.path.splitext(os.path.basename(DOC))[0], r"Projet NLP 2"))
T.append(r'\begin{document}')
T.append(r'\thispagestyle{empty}')
T.append(r'\begingroup\sffamily')
T.append(r'{\color{accent}\rule{\textwidth}{2.6pt}}\par\vspace{13pt}')
_t, _st, _sur = BANDEAU.get(os.path.splitext(os.path.basename(DOC))[0],
                            (titre_brut, "", ""))
T.append(r'{\fontsize{27}{31}\selectfont\bfseries\color{encre} ' + _t + r'}\par\vspace{7pt}')
if _st: T.append(r'{\fontsize{13.5}{17}\selectfont\color{gris} ' + _st + r'}\par\vspace{5pt}')
if _sur: T.append(r'{\fontsize{11}{14}\selectfont\color{accent2}\bfseries ' + _sur + r'}\par\vspace{12pt}')
T.append(r'{\color{filet}\rule{\textwidth}{0.6pt}}\par\vspace{14pt}')
T.append(r'\endgroup')
# bloc méta
T.append(r'\begingroup\setlength{\parskip}{0pt}')
_lab = max((k for k, _ in meta), key=len, default="x")
T.append(r'\settowidth{\metalab}{\tabfont\bfseries ' + inline(_lab) + '}')
T.append(r'\begin{tabular}{@{}>{\tabfont\bfseries\color{accent}}l@{\hspace{16pt}}'
         r'p{\dimexpr\textwidth-\metalab-18pt\relax}@{}}')
for k, v in meta:
    T.append(inline(k) + ' & ' + inline(v) + r' \\[3.5pt]')
T.append(r'\end{tabular}\par\vspace{16pt}\endgroup')
for _p in libres:
    T.append(r'\begingroup\small\color{gris}' + inline(_p) + r'\par\endgroup\vspace{6pt}')
# encadré d'ouverture
if quote:
    T.append(r'\begin{callout}')
    T.append(inline(' '.join(quote)))
    T.append(r'\end{callout}')
T.append(r'\vspace{10pt}{\color{filet}\rule{\textwidth}{0.4pt}}\par\vspace{16pt}')
T.append(r'\begingroup\setlength{\parskip}{0pt}\tableofcontents\endgroup')
T.append(r'\clearpage')
# passe 1 : collecte des fragments ; passe 2 : génération avec largeurs mesurées
TBL['k'] = 0; TBL['chunks'] = []; TBL['measured'] = None
convert(body)
mes = mesurer(TBL['chunks'])
print(f"   {len(mes)} colonnes mesurées par XeLaTeX")
TBL['k'] = 0; TBL['measured'] = mes
T.append(convert(body))
T.append(r'\end{document}')

tex = open(PRE, encoding='utf-8').read() + '\n' + '\n'.join(T) + '\n'
open(OUT, 'w', encoding='utf-8').write(tex)
print(f"✅ {OUT}\n   {len(tex)} caractères, {tex.count(chr(10))} lignes")
