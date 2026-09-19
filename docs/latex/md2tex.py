#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convertisseur Markdown -> LaTeX dédié au support de réunion NLP 2."""
import re, sys, unicodedata

# ---------------------------------------------------------------- symboles
SYM = {
 '✅': r'\okmark',      # ✅
 '❌': r'\komark',      # ❌
 '⚠': r'\warnmark',    # ⚠
 '☐': r'\checkbox',    # ☐
 '✂': r'\cutmark',     # ✂
 '★': r'\starmark',    # ★
 '\U0001F6A7': r'\wipmark', # 🚧
}
UNI = {
 '…':r'\dots{}', '·':r'\textperiodcentered{}',
 '→':r'$\rightarrow$', '≥':r'$\geq$', '≈':r'$\approx$',
 '≠':r'$\neq$', '×':r'$\times$', '§':r'\S{}',
 'ᵉ':r'\textsuperscript{e}', '²':r'\textsuperscript{2}',
 '°':r'\textdegree{}', ' ':'~', ' ':'\\,',
}
ESC = [('\\', r'\textbackslash{}'), ('&', r'\&'), ('%', r'\%'), ('$', r'\$'),
       ('#', r'\#'), ('_', r'\_'), ('{', r'\{'), ('}', r'\}'),
       ('~', r'\textasciitilde{}'), ('^', r'\textasciicircum{}')]

def esc(s):
    s = s.replace('️', '')                    # sélecteur de variante
    for a, b in ESC: s = s.replace(a, b)
    for a, b in SYM.items(): s = s.replace(a, b + '{}')
    for a, b in UNI.items(): s = s.replace(a, b)
    return s

def esc_code(s):
    """Échappe et rend coupable une chaîne en chasse fixe (chemins, paquets)."""
    s = esc(s)
    for ch in ('/', '_', '.', '-', ':', '@'):
        tok = ch if ch != '_' else '\\_'
        s = s.replace(tok, tok + r'\allowbreak{}')
    return s.replace(r'\allowbreak{}' * 2, r'\allowbreak{}')

def strip_md(s):
    """texte nu, pour mesurer la largeur d'une cellule"""
    s = s.replace('️','')
    s = re.sub(r'\*\*|\*|`', '', s)
    return s

# ---------------------------------------------------------------- inline
GUILL = re.compile('\u00AB\\s*(.+?)\\s*\u00BB')

def inline(s):
    """Markdown en ligne -> LaTeX. Réserve partagée : les imbrications
    (gras contenant du code, etc.) se résolvent par récursion sur `render`."""
    stash = {}
    def put(kind, content):
        key = '\x01%d\x01' % len(stash)
        stash[key] = (kind, content)
        return key
    s = s.replace('\uFE0F', '')
    s = re.sub(r'`([^`]+)`',        lambda m: put('C', m.group(1)), s)
    s = re.sub(r'\*\*(.+?)\*\*',   lambda m: put('B', m.group(1)), s)
    s = re.sub(r'(?<![\w*])\*([^*\n]+?)\*(?![\w*])', lambda m: put('I', m.group(1)), s)

    def render(txt):
        txt = esc(txt)
        txt = GUILL.sub(lambda m: '\\og ' + m.group(1) + '\\fg{}', txt)
        def back(m):
            kind, content = stash[m.group(0)]
            if kind == 'C': return '\\code{' + esc_code(content) + '}'
            if kind == 'B': return '\\textbf{' + render(content) + '}'
            return '\\textit{' + render(content) + '}'
        return re.sub(r'\x01\d+\x01', back, txt)
    return render(s)

# ---------------------------------------------------------------- tableaux
TW_PT      = 478.006          # \textwidth mesuré
TABCOLSEP  = 4.0              # fixé par l'environnement tabletype
# largeur par caractère (Inter gras), mesurée par \settowidth
PERCHAR = {'small': 0.00940, 'footnotesize': 0.00846, 'scriptsize': 0.00752}
SPLIT = re.compile(r'[/_.\-:@]')

def longest_unit(s, credit=True):
    """Plus longue suite insécable. `credit` applique la remise de césure ;
    on l'interdit pour les en-têtes, dont les mots gras débordaient."""
    best = 1
    for tok in re.split(r'\s+', strip_md(s)):
        for part in SPLIT.split(tok):
            n = len(part)
            if n > 8 and re.fullmatch(r'[A-Za-zÀ-ÿœŒ]+', part):
                n = max(7, round(n * 0.60)) if credit else min(n, 13)
            best = max(best, n)
    return best

def allocate(weights, mins, avail):
    """Répartition proportionnelle sous contrainte de largeur minimale."""
    n = len(weights); frac = [0.0]*n; fixed = [False]*n
    for _ in range(n + 1):
        rest = avail - sum(frac[i] for i in range(n) if fixed[i])
        wsum = sum(weights[i] for i in range(n) if not fixed[i]) or 1.0
        newly = False
        for i in range(n):
            if fixed[i]: continue
            if weights[i]/wsum*rest < mins[i]:
                fixed[i] = True; frac[i] = mins[i]; newly = True
        if not newly:
            for i in range(n):
                if not fixed[i]: frac[i] = weights[i]/wsum*rest
            break
    return frac

TBL = {'k': 0, 'chunks': [], 'measured': None}

CODE = re.compile(r'`([^`]+)`')

def chunks_of(cell, credit):
    """Fragments insécables d'une cellule -> [(texte, chasse_fixe)].
    Le code ne se coupe pas : pas de remise de césure, et mesure en mono."""
    out = []
    mono_src = CODE.findall(cell)
    reste = CODE.sub(' ', cell)
    for src, mono in [(reste, False)] + [(m, True) for m in mono_src]:
        for tok in re.split(r'\s+', strip_md(src)):
            # les points de coupe (/, _, ., -) ne sont insérés que dans le code :
            # en texte courant, « 18/09 » est insécable et doit être mesuré entier.
            for part in (SPLIT.split(tok) if mono else [tok]):
                if not part: continue
                # On mesure le mot entier (plafonné) : une remise de césure
                # rendait la colonne trop étroite et forçait des coupures laides.
                if len(part) > 14 and re.fullmatch(r'[A-Za-zÀ-ÿœŒ]+', part):
                    part = part[:14]
                out.append((part, mono))
    return out or [('x', False)]

def table(rows):
    k = TBL['k']; TBL['k'] += 1
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    header, body = cells[0], cells[2:]
    n = len(header)
    body = [r + ['']*(n-len(r)) if len(r) < n else r[:n] for r in body]
    cols = [[header[j]] + [r[j] for r in body] for j in range(n)]

    weights = []
    for col in cols:
        lens = [len(strip_md(x)) for x in col]
        weights.append(max(0.6*max(lens) + 0.4*(sum(lens)/len(lens)), 3))

    longest_row = max(len(strip_md('|'.join(r))) for r in cells)
    size = 'scriptsize' if (longest_row > 260 or n >= 6) else \
           ('footnotesize' if (longest_row > 150 or n == 5) else 'small')
    gutter = (n - 1) * 2 * TABCOLSEP
    span   = TW_PT - gutter

    if TBL['measured'] is None:                     # passe 1 : on collecte à mesurer
        for j in range(n):
            TBL['chunks'].append((k, j, size,
                                  chunks_of(header[j], False),          # en-tête, gras
                                  [c for cell in cols[j][1:] for c in chunks_of(cell, True)]))
        mins = [0.028]*n
    else:                                           # passe 2 : largeurs mesurées en pt
        mins = [max(0.028, (TBL['measured'].get((k, j), 0.0) + 1.0) / span) for j in range(n)]
        if sum(mins) > 0.97:
            f = 0.97/sum(mins); mins = [m*f for m in mins]
    frac = allocate(weights, mins, 1.0)
    frac[frac.index(max(frac))] += 1.0 - sum(frac)

    spec = ''.join('L{%.5f\\tw}' % f for f in frac)
    out = ['%% TABLE %d' % k, r'\begin{tabletype}', '\\' + size, r'\settw{%.1f}' % gutter,
           r'\setlength{\LTpre}{0pt}\setlength{\LTpost}{0pt}',
           r'\begin{longtable}{@{}' + spec + r'@{}}', r'\toprule']
    hdr = ' & '.join(r'\thead{' + inline(c) + '}' for c in header) + r' \\'
    out += [hdr, r'\midrule', r'\endfirsthead', r'\toprule', hdr, r'\midrule', r'\endhead',
            r'\bottomrule', r'\endfoot', r'\bottomrule', r'\endlastfoot']
    for r_ in body:
        out.append(' & '.join(inline(c) for c in r_) + r' \\')
    out += [r'\end{longtable}', r'\end{tabletype}']
    return out

# ---------------------------------------------------------------- corps
def convert(md):
    L = md.split('\n'); out = []; i = 0
    while i < len(L):
        ln = L[i]
        # bloc de code
        if ln.strip().startswith('```'):
            j = i+1; buf = []
            while j < len(L) and not L[j].strip().startswith('```'):
                buf.append(L[j]); j += 1
            out += [r'\begin{codebox}', r'\begin{Verbatim}[fontsize=\small,xleftmargin=0pt]'] + buf + \
                   [r'\end{Verbatim}', r'\end{codebox}']
            i = j+1; continue
        # titres
        m = re.match(r'^(#{1,4})\s+(.*)$', ln)
        if m:
            lvl, txt = len(m.group(1)), m.group(2).strip()
            txt = re.sub(r'^\d+(\.\d+)*\.?\s*[—-]?\s*', '', txt)
            cmd = {1: 'section', 2: 'section', 3: 'subsection', 4: 'subsubsection*'}[lvl]
            # une annexe n'est pas numérotée, mais figure au sommaire
            annexe = (cmd == 'section' and re.match(r'^Annexe\b', txt))
            rendu = inline(txt)
            if any(c in rendu for c in ('$', '\\S{}', 'mark{}', '\\code')):
                plain = strip_md(txt)
                for a, b in (('\u00A7', 'S'), ('\u2260', ' different de '), ('\u2014', '-'),
                             ('\u2013', '-'), ('\u2192', '->'), ('\u2265', '>='),
                             ('\u00AB', '"'), ('\u00BB', '"'), ('\uFE0F', '')):
                    plain = plain.replace(a, b)
                plain = re.sub(r'\s+', ' ', plain).strip()
                rendu = r'\texorpdfstring{%s}{%s}' % (rendu, plain)
            if annexe:
                out += ['', r'\section*{%s}' % rendu,
                        r'\addcontentsline{toc}{section}{%s}' % rendu]
            else:
                out += ['', r'\%s{%s}' % (cmd, rendu)]
            i += 1; continue
        # filet horizontal
        if re.match(r'^-{3,}\s*$', ln):
            out.append(r'\rulebreak'); i += 1; continue
        # tableau
        if ln.strip().startswith('|'):
            j = i
            while j < len(L) and L[j].strip().startswith('|'): j += 1
            out += table(L[i:j]); i = j; continue
        # citation
        if ln.startswith('>'):
            j = i; buf = []
            while j < len(L) and L[j].startswith('>'):
                buf.append(L[j][1:].lstrip()); j += 1
            paras = '\n'.join(buf).split('\n\n')
            out.append(r'\begin{callout}')
            for p in paras:
                p = ' '.join(x for x in p.split('\n') if x.strip())
                if p.strip(): out += [inline(p), r'\par\smallskip']
            if out[-1] == r'\par\smallskip': out.pop()
            out.append(r'\end{callout}'); i = j; continue
        # listes
        m = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', ln)
        if m:
            ordered = bool(re.match(r'\d+\.', m.group(2)))
            env = 'enumerate' if ordered else 'itemize'
            j = i; items = []
            while j < len(L):
                mm = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', L[j])
                if mm:
                    items.append(mm.group(3)); j += 1
                elif L[j].startswith('   ') and L[j].strip() and items:
                    items[-1] += ' ' + L[j].strip(); j += 1
                else: break
            out.append(r'\begin{%s}' % env)
            for it in items: out.append(r'\item ' + inline(it))
            out.append(r'\end{%s}' % env); i = j; continue
        # paragraphe
        if ln.strip():
            j = i; buf = []
            while j < len(L) and L[j].strip() and not L[j].strip().startswith(('|','>','```','#')) \
                  and not re.match(r'^(\s*)([-*]|\d+\.)\s+', L[j]) and not re.match(r'^-{3,}\s*$', L[j]):
                buf.append(L[j].strip()); j += 1
            out += ['', inline(' '.join(buf))]; i = j; continue
        i += 1
    return '\n'.join(out)

if __name__ == '__main__':
    print(convert(open(sys.argv[1], encoding='utf-8').read()))
