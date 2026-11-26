"""Contrôle des débordements des supports de soutenance (#114), dans les deux formats.

Marp tronque ou superpose sans prévenir ce qui dépasse d'une diapositive, et le rendu d'impression de Chrome ne coupe
pas toujours les lignes comme son rendu d'écran : seul le PDF fait foi pour les fichiers Marp. Le script :

- rend pitch.md et presentation.md en PDF, lit la position de chaque mot (pdftotext -bbox, de poppler) et signale tout
  mot du corps qui descend sous la zone utile ou dépasse à droite ; les mots du pied de page et le numéro sont reconnus
  par leur texte, relu dans les directives footer du fichier Marp ;
- mesure soutenance.html dans Chrome, son propre moteur de rendu, élément par élément.

    MARP=<chemin de marp> CHROME_PATH=<chemin de Chrome> python3 -I docs/soutenance/outils/controler_debordements.py

Code de sortie 1 au moindre dépassement. Les fichiers intermédiaires vont dans un dossier temporaire, supprimé à la fin.
Variable SOUTENANCE_RACINE : contrôler un autre dossier (contrôle négatif sur une copie volontairement fautive).
"""

import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

RACINE = Path(os.environ.get("SOUTENANCE_RACINE", Path(__file__).resolve().parent.parent))
TOLERANCE_PT = 1.0   # arrondis du rendu PDF, en points
TOLERANCE_PX = 0.5   # arrondis du rendu HTML, en pixels


def pieds_marp(chemin: Path) -> tuple[list[str], int, int]:
    """Pied de chaque diapositive (directive footer, persistante), et marges basse et droite du style (en px)."""
    texte = chemin.read_text(encoding="utf-8")
    fin = texte.index("\n---\n", 4)
    entete, corps = texte[4:fin], texte[fin + 5:]
    pied = re.search(r'^footer:\s*"(.*)"\s*$', entete, re.M).group(1)
    marges = re.search(r"padding:\s*(\d+)px\s+(\d+)px\s+(\d+)px", entete)
    pieds = []
    for bloc in re.split(r"\n---\n", corps):
        for m in re.finditer(r"<!--\s*footer:\s*\"(.*?)\"\s*-->", bloc):
            pied = m.group(1)
        pieds.append(pied)
    return pieds, int(marges.group(3)), int(marges.group(2))


def controler_pdf(pdf: Path, md: Path) -> list[str]:
    pieds, marge_bas, marge_droite = pieds_marp(md)
    bbox = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    pages = re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', bbox, re.S)
    assert len(pages) == len(pieds), f"{md.name} : {len(pages)} pages pour {len(pieds)} diapositives"
    defauts = []
    for n, ((w, h, contenu), pied) in enumerate(zip(pages, pieds), start=1):
        W, H = float(w), float(h)
        bas, droite = (720 - marge_bas) / 720 * H, (1280 - marge_droite) / 1280 * W
        mots = [(float(a), float(b), float(c), float(d), html.unescape(t)) for a, b, c, d, t in
                re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', contenu)]
        attendus = Counter(pied.split() + [str(n)])            # pied de page et numéro : leur place est sous la zone utile
        sous = Counter(m[4] for m in mots if m[3] > bas + TOLERANCE_PT)
        intrus = sous - attendus
        trop_a_droite = [m[4] for m in mots if m[3] <= bas + TOLERANCE_PT and m[2] > droite + TOLERANCE_PT]
        if intrus or trop_a_droite:
            defauts.append(f"diapositive {n} : sous la zone utile {sorted(intrus.elements())[:8]}, à droite {trop_a_droite[:8]}")
    return defauts


MESURE_HTML = r"""<script>
window.addEventListener('load', function () {
  var sorties = [], diapos = [].slice.call(document.querySelectorAll('.diapo'));
  diapos.forEach(function (d, k) {
    var r = d.getBoundingClientRect(), s = r.width / 1280, st = getComputedStyle(d);
    var basMax = 720 - parseFloat(st.paddingBottom), droiteMax = 1280 - parseFloat(st.paddingRight), bas = 0, droite = 0, fautif = '';
    d.querySelectorAll('*').forEach(function (e) {
      if (e.closest('.entete,.pied,.num')) return;
      var sv = e.parentElement && e.parentElement.closest('svg');   // l'intérieur des figures ne compte pas
      if (sv && d.contains(sv)) return;
      var q = e.getBoundingClientRect(); if (!q.width && !q.height) return;
      var b = (q.bottom - r.top) / s, dr = (q.right - r.left) / s;
      if (b > bas) { bas = b; fautif = e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className ? '.' + e.className : ''); }
      if (dr > droite) droite = dr;
    });
    if (bas > basMax + TOL || droite > droiteMax + TOL) sorties.push('diapositive ' + (k + 1) + ' : bas ' + bas.toFixed(1) + ' pour ' + basMax + ', droite ' + droite.toFixed(1) + ' pour ' + droiteMax + ' (' + fautif + ')');
  });
  var p = document.createElement('pre'); p.id = 'resultat'; p.setAttribute('data-n', diapos.length); p.textContent = sorties.join('\n'); document.body.appendChild(p);
});
</script>"""


def controler_html(page: Path, chrome: str) -> tuple[int, list[str]]:
    page.write_text(page.read_text(encoding="utf-8").replace("</body>", MESURE_HTML.replace("TOL", str(TOLERANCE_PX)) + "</body>"), encoding="utf-8")
    sortie = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--window-size=1400,900", "--virtual-time-budget=4000",
                             "--dump-dom", page.as_uri()], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120).stdout
    m = re.search(r'<pre id="resultat" data-n="(\d+)">(.*?)</pre>', sortie, re.S)
    if not m:
        raise RuntimeError(f"aucune mesure obtenue pour {page.name}")
    return int(m.group(1)), [l for l in html.unescape(m.group(2)).splitlines() if l]


def main() -> int:
    marp, chrome = os.environ.get("MARP", "marp"), os.environ.get("CHROME_PATH")
    if not chrome or not shutil.which("pdftotext"):
        print("CHROME_PATH non défini ou pdftotext (poppler) absent", file=sys.stderr)
        return 2
    dossier = Path(tempfile.mkdtemp(prefix="controle_soutenance_"))
    echecs = 0
    try:
        for nom in ("pitch.md", "presentation.md"):
            pdf = dossier / (Path(nom).stem + ".pdf")
            subprocess.run([marp, "--html", "--allow-local-files", "--pdf", str(RACINE / nom), "-o", str(pdf)], stdin=subprocess.DEVNULL,
                           capture_output=True, check=True, timeout=180, env={**os.environ, "CHROME_PATH": chrome})
            defauts = controler_pdf(pdf, RACINE / nom)
            echecs += len(defauts)
            print(f"PDF de {nom} : {len(pieds_marp(RACINE / nom)[0])} diapositives, {len(defauts)} débordement(s)")
            for d in defauts:
                print("  " + d)
        copie = dossier / "soutenance.html"
        shutil.copy(RACINE / "soutenance.html", copie)
        n, defauts = controler_html(copie, chrome)
        echecs += len(defauts)
        print(f"soutenance.html : {n} diapositives, {len(defauts)} débordement(s)")
        for d in defauts:
            print("  " + d)
    finally:
        shutil.rmtree(dossier, ignore_errors=True)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
