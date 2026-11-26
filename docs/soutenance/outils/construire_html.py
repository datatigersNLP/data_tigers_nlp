"""Version HTML animée des supports de soutenance (#114), construite depuis les fichiers Marp.

Source unique : pitch.md puis presentation.md. Textes, définitions et notes d'orateur sont repris tels quels ; les
figures SVG sont insérées dans la page pour être animées. La page ne charge aucune ressource externe : elle fonctionne
hors ligne, n'envoie l'adresse IP d'aucun spectateur à un tiers, et utilise la même pile de polices que le rendu Marp,
donc les mêmes retours à la ligne que les PDF contrôlés.

    <python avec markdown-it-py> docs/soutenance/outils/construire_html.py [--corps-seul SORTIE]

Écrit docs/soutenance/soutenance.html (document complet). Avec --corps-seul, écrit en plus la même page sans
<html>/<head>/<body>, forme attendue pour une publication en artefact.
"""

import html
import json
import re
import sys
from pathlib import Path

from markdown_it import MarkdownIt

RACINE = Path(__file__).resolve().parent.parent
SOURCES = [("pitch.md", "pitch"), ("presentation.md", "presentation")]
MD = MarkdownIt("commonmark", {"html": True, "typographer": False}).enable("table")
DIRECTIVE = re.compile(r"^\s*(_?)(class|paginate|footer|header)\s*:\s*(.*?)\s*$", re.S)
IMAGE = re.compile(r'<p><img src="figures/([\w.-]+\.svg)" alt="w:(\d+)" /></p>')
ENTETES_NOTES = ("Durée visée", "À dire", "Questions probables", "Volet A", "Volet B", "Questions de secours si besoin")


def lire_figure(nom):
    svg = (RACINE / "figures" / nom).read_text(encoding="utf-8")
    return svg[svg.index("<svg"):]


def duree_secondes(notes):
    """« 45 s » donne 45 ; « 1 min 15 s » et « 3 min 50 » donnent 75 et 230."""
    m = re.search(r"Durée visée\s*:\s*(\d+)\s*(min|s)\b(?:\s*(\d+))?", notes)
    if not m:
        return None
    a, unite, b = int(m.group(1)), m.group(2), m.group(3)
    return a * 60 + int(b or 0) if unite == "min" else a


def decouper(chemin):
    texte = chemin.read_text(encoding="utf-8")
    assert texte.startswith("---\n"), chemin
    fin = texte.index("\n---\n", 4)
    entete, corps = texte[4:fin], texte[fin + 5:]
    pied = re.search(r'^footer:\s*"(.*)"\s*$', entete, re.M).group(1)
    return pied, re.split(r"\n---\n", corps)


def diapositives():
    toutes = []
    for fichier, source in SOURCES:
        pied, blocs = decouper(RACINE / fichier)
        for numero, bloc in enumerate(blocs, start=1):
            classes, notes, pagine = [], [], True
            for c in re.findall(r"<!--(.*?)-->", bloc, re.S):
                d = DIRECTIVE.match(c)
                if not d:
                    notes.append(c.strip())
                    continue
                locale, cle, valeur = d.group(1), d.group(2), d.group(3).strip().strip('"')
                if cle == "class":
                    classes.append(valeur)
                elif cle == "footer" and not locale:
                    pied = valeur
                elif cle == "paginate" and locale:
                    pagine = valeur != "false"
            md = re.sub(r"<!--.*?-->", "", bloc, flags=re.S).strip()
            corps = IMAGE.sub(lambda m: f'<figure class="fig" style="--w:{int(m.group(2))}px">{lire_figure(m.group(1))}</figure>',
                              MD.render(md))
            assert "<img" not in corps, f"image non convertie dans {fichier}, diapositive {numero}"
            titre = re.search(r"<h1>(.*?)</h1>", corps, re.S)
            texte_notes = "\n".join(notes)
            toutes.append({"source": source, "numero": numero if pagine else None, "pied": pied,
                           "partie": "Pitch" if source == "pitch" else pied.split(" · ")[0],
                           "classes": classes, "corps": corps, "notes": texte_notes,
                           "duree": duree_secondes(texte_notes),
                           "titre": re.sub(r"<[^>]+>", "", titre.group(1)).strip() if titre else "Diapositive"})
    return toutes


def notes_html(notes):
    if not notes:
        return '<p class="vide">Pas de notes pour cette diapositive.</p>'
    sortie = []
    for ligne in notes.splitlines():
        ligne = ligne.strip()
        if not ligne:
            continue
        e = html.escape(ligne, quote=False)
        if ligne.startswith("- "):
            sortie.append(f"<li>{e[2:]}</li>")
            continue
        for t in ENTETES_NOTES:
            if re.match(re.escape(t) + r"\s*:", e):
                e = re.sub(r"^" + re.escape(t) + r"\s*:", f"<b>{t} :</b>", e)
                break
        sortie.append(f"<p>{e}</p>")
    return re.sub(r"((?:<li>.*?</li>)+)", r"<ul>\1</ul>", "".join(sortie))


CSS = r"""
/* Diapositives 1280 x 720 mises à l'échelle de l'écran, barre de commande en bas ; fond blanc imposé, un seul thème. */
:root{
  --papier:#ffffff; --encre:#111827; --bleu:#1f3b73; --vert:#2e6a4f; --gris:#5b6472; --texte-def:#374151;
  --filet:#d7dbe0; --teinte:#f3f5f8; --scene:#e6e9ee; --ombre:rgba(17,24,39,.16);
  --ambre:#b45309; --ambre-fond:#fff7ed; --ambre-texte:#7c2d12;
  --police:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif; --mono:"IBM Plex Mono",Menlo,Consolas,monospace;
  --barre-h:52px; color-scheme:light;
}
html,body{height:100%}
body{margin:0;background:var(--scene);color:var(--encre);font-family:var(--police);overflow:hidden;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0;box-sizing:border-box}
.scene{position:fixed;top:env(safe-area-inset-top,0px);bottom:calc(var(--barre-h) + env(safe-area-inset-bottom,0px));
  left:max(16px,env(safe-area-inset-left,0px));right:max(16px,env(safe-area-inset-right,0px));overflow:hidden}
/* centré par position absolue puis réduit autour de son centre : une grille élargirait sa colonne à 1280 px sur un écran étroit */
.cadre{width:1280px;height:720px;position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);transform-origin:center center;
  background:var(--papier);box-shadow:0 10px 36px var(--ombre)}

/* une diapositive, mêmes mesures que le style Marp de presentation.md */
.diapo{position:absolute;inset:0;background:var(--papier);color:var(--encre);padding:62px 70px 50px;box-sizing:border-box;display:flex;flex-direction:column;
  font-size:24px;line-height:1.38;visibility:hidden;opacity:0}
.diapo.active{visibility:visible;opacity:1}
/* fondu entre diapositives seulement après la première navigation : au chargement, rien n'est en cours de fondu */
.cadre.navigue .diapo{transition:opacity .4s ease,visibility 0s linear .4s}
.cadre.navigue .diapo.active{transition:opacity .4s ease}
.diapo .entete,.diapo .pied,.diapo .num{position:absolute;font-size:15px;color:var(--gris)}
.diapo .entete{top:26px;left:34px}.diapo .pied{bottom:22px;left:34px}.diapo .num{bottom:22px;right:34px;font-variant-numeric:tabular-nums}
.diapo h1{color:var(--bleu);font-size:34px;line-height:1.2;margin:0 0 16px;font-weight:700;text-wrap:balance}
.diapo h3{margin:0 0 8px;font-size:24px;color:var(--bleu)}
.diapo strong{color:var(--bleu)}
.diapo ul,.diapo ol{margin:0;padding-left:1.1em}
.diapo li{margin:0 0 7px}
.diapo p{margin:0 0 10px}
.diapo code{font-family:var(--mono);font-size:.9em;background:var(--teinte);padding:0 4px;border-radius:3px}
.diapo table{border-collapse:collapse;font-size:18.5px;margin:2px 0 8px;width:100%}
.diapo th{background:var(--teinte);color:var(--bleu);text-align:left}
.diapo th,.diapo td{border:1px solid var(--filet);padding:4px 9px;vertical-align:top}
.def{margin-top:auto;border-top:2px solid var(--bleu);padding-top:7px;font-size:16.5px;line-height:1.33;color:var(--texte-def)}
.def b{color:var(--bleu)}
.colonnes{display:grid;grid-template-columns:1fr 1fr;gap:30px}.colonnes>*{min-width:0}
.petit{font-size:20px}.tres-petit{font-size:17px;line-height:1.32}
.bloc{border:1px solid var(--filet);border-top:4px solid var(--bleu);padding:12px 16px;font-size:22px}
.bloc.b{border-top-color:var(--vert)}.bloc.b h3{color:var(--vert)}
.question{border-left:4px solid var(--bleu);padding:6px 14px;background:var(--teinte);font-size:24px;margin:6px 0 16px}
.a-completer{border:2px dashed var(--ambre);background:var(--ambre-fond);color:var(--ambre-texte);padding:5px 12px;font-size:19px}
.glossaire{columns:2;column-gap:34px;font-size:16.5px;line-height:1.3}.glossaire p{margin:0 0 5px;break-inside:avoid}.glossaire b{color:var(--bleu)}
.diapo.titre{justify-content:center}.diapo.titre h1{font-size:46px}
.etape{font-size:22px}
.fig{margin:4px auto 10px;width:var(--w);max-width:100%}.fig svg{display:block;width:100%;height:auto}

/* écarts du style Marp de pitch.md */
.diapo.pitch{font-size:25px;line-height:1.4;padding:64px 70px 52px}
.diapo.pitch h1{font-size:37px;margin-bottom:22px}
.diapo.pitch li{margin-bottom:10px}
.diapo.pitch .def{font-size:17px;line-height:1.35;padding-top:8px}
.diapo.pitch .colonnes{gap:34px}
.diapo.pitch.titre h1{font-size:54px;margin-bottom:10px}
.sous-titre{font-size:29px;color:var(--bleu);margin-bottom:34px}.equipe{font-size:21px;color:var(--texte-def)}

/* Apparitions, seulement quand on arrive sur une diapositive par la navigation (classe .entree) :
   au chargement, la diapositive affichée est complète, sans rien à attendre. */
@keyframes monte{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes apparait{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}
@keyframes trace{from{stroke-dashoffset:1400}to{stroke-dashoffset:0}}
@keyframes pousse{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.diapo.entree .anim{animation:monte .5s cubic-bezier(.2,.7,.2,1) both;animation-delay:calc(var(--d,0) * 90ms + 100ms)}
.diapo.entree .fig .b{animation:monte .45s ease both;animation-delay:calc(var(--i,0) * 110ms + 300ms)}
.diapo .fig .point{transform-box:fill-box;transform-origin:center}
.diapo.entree .fig .point{animation:apparait .4s ease both;animation-delay:calc(var(--i,0) * 110ms + 300ms)}
.diapo.entree .fig .f,.diapo.entree .fig .lien{stroke-dasharray:1400;animation:trace .7s ease both;animation-delay:calc(var(--i,0) * 110ms + 320ms)}
.diapo .fig .barre{transform-box:fill-box;transform-origin:left center}
.diapo.entree .fig .barre{animation:pousse .9s cubic-bezier(.2,.7,.2,1) both;animation-delay:calc(var(--i,0) * 160ms + 350ms)}
@media (prefers-reduced-motion:reduce){
  .cadre.navigue .diapo,.cadre.navigue .diapo.active{transition:none}
  .diapo.entree .anim,.diapo.entree .fig .b,.diapo.entree .fig .point,.diapo.entree .fig .f,.diapo.entree .fig .lien,.diapo.entree .fig .barre{animation:none}
  .diapo.entree .fig .f,.diapo.entree .fig .lien{stroke-dasharray:none}
}

/* barre de commande */
.barre-cmd{position:fixed;left:0;right:0;bottom:0;height:var(--barre-h);display:flex;align-items:center;gap:10px;box-sizing:content-box;
  padding:0 max(16px,env(safe-area-inset-right,0px)) env(safe-area-inset-bottom,0px) max(16px,env(safe-area-inset-left,0px));
  background:var(--papier);border-top:1px solid var(--filet);font-size:14px;color:var(--gris);z-index:5}
.barre-cmd button{font:inherit;color:var(--encre);background:var(--teinte);border:1px solid var(--filet);border-radius:6px;padding:6px 10px;cursor:pointer;white-space:nowrap}
.barre-cmd button:hover{border-color:var(--bleu)}
.barre-cmd button:focus-visible,.sommaire a:focus-visible{outline:2px solid var(--bleu);outline-offset:2px}
.barre-cmd .partie{font-weight:600;color:var(--bleu);min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.barre-cmd .compteur{font-variant-numeric:tabular-nums;white-space:nowrap}
.barre-cmd .espace{flex:1}
.progression{position:fixed;left:0;bottom:calc(var(--barre-h) + env(safe-area-inset-bottom,0px));height:3px;background:var(--bleu);width:0;transition:width .3s ease;z-index:5}
.panneau{position:fixed;left:max(16px,env(safe-area-inset-left,0px));right:max(16px,env(safe-area-inset-right,0px));
  bottom:calc(var(--barre-h) + 12px + env(safe-area-inset-bottom,0px));max-height:48vh;overflow:auto;background:var(--papier);color:var(--encre);
  border:1px solid var(--filet);border-radius:8px;box-shadow:0 10px 30px var(--ombre);padding:14px 18px;font-size:15px;line-height:1.45;z-index:6}
.panneau h2{font-size:15px;margin:0 0 6px;color:var(--bleu)}
.panneau ul{margin:4px 0 8px;padding-left:1.2em}.panneau p{margin:0 0 6px}.panneau .vide{color:var(--gris)}
.sommaire{columns:2;column-gap:28px}
.sommaire h3{font-size:12px;letter-spacing:.07em;text-transform:uppercase;color:var(--gris);margin:8px 0 4px;break-after:avoid}
.sommaire a{display:block;color:var(--encre);text-decoration:none;padding:2px 0;break-inside:avoid}
.sommaire a:hover,.sommaire a[aria-current]{color:var(--bleu);font-weight:600}
.court{display:none}
@media (max-width:700px){.barre-cmd .facultatif,.barre-cmd .partie{display:none}.long{display:none}.court{display:inline}.sommaire{columns:1}}
"""

JS = r"""
(function(){
  var diapos=[].slice.call(document.querySelectorAll('.diapo')), cadre=document.querySelector('.cadre'), scene=document.querySelector('.scene');
  var DONNEES=JSON.parse(document.getElementById('donnees').textContent);
  var prog=document.querySelector('.progression'), partie=document.querySelector('.partie'), compteur=document.querySelector('.compteur');
  var pNotes=document.getElementById('notes'), pSommaire=document.getElementById('sommaire'), liens=[].slice.call(pSommaire.querySelectorAll('a'));
  var i=0;
  function echelle(){var s=scene.getBoundingClientRect();var k=Math.max(0.1,Math.min(s.width/1280,s.height/720));cadre.style.transform='translate(-50%,-50%) scale('+k+')';}
  function preparer(d){
    var n=0;function pose(e){e.classList.add('anim');e.style.setProperty('--d',n++);}
    [].slice.call(d.children).forEach(function(c){
      if(c.matches('.entete,.pied,.num,.fig'))return;
      if(c.matches('ul,ol')){[].forEach.call(c.querySelectorAll(':scope>li'),pose);return;}
      if(c.matches('table')){[].forEach.call(c.querySelectorAll('tr'),pose);return;}
      var t=c.querySelector(':scope>table');if(t){[].forEach.call(t.querySelectorAll('tr'),pose);return;}
      if(c.matches('.colonnes')){[].forEach.call(c.children,pose);return;}
      pose(c);
    });
  }
  diapos.forEach(preparer);
  function format(s){if(s==null)return'';var m=Math.floor(s/60),r=s%60;return m?(m+' min'+(r?' '+r+' s':'')):r+' s';}
  function afficher(n,anime,depuisHash){
    var avant=i;i=Math.max(0,Math.min(diapos.length-1,n));
    diapos.forEach(function(d,k){var a=k===i;d.classList.toggle('active',a);d.setAttribute('aria-hidden',a?'false':'true');if(!a)d.classList.remove('entree');});
    if(anime&&i!==avant){cadre.classList.add('navigue');var d=diapos[i];d.classList.remove('entree');void d.offsetWidth;d.classList.add('entree');}
    var info=DONNEES[i];
    prog.style.width=((i+1)/diapos.length*100)+'%';
    partie.textContent=info.partie;
    compteur.textContent=(i+1)+' / '+diapos.length;
    var cumul=0,total=0;DONNEES.forEach(function(x,k){if(x.partie===info.partie&&x.duree){total+=x.duree;if(k<=i)cumul+=x.duree;}});
    document.getElementById('notes-corps').innerHTML=info.notes_html;
    document.getElementById('notes-duree').textContent=info.duree?('Durée visée '+format(info.duree)+' · cumul '+format(cumul)+' sur '+format(total)+' ('+info.partie+')'):(info.partie+' · diapositive '+(i+1));
    liens.forEach(function(a,k){if(k===i)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});
    if(!depuisHash){try{history.replaceState(null,'','#d'+(i+1));}catch(e){}}
  }
  function lireHash(){var m=/^#d(\d+)$/.exec(location.hash);return m?parseInt(m[1],10)-1:0;}
  function bascule(p){var ouvrir=p.hidden;pNotes.hidden=true;pSommaire.hidden=true;p.hidden=!ouvrir;}
  function plein(){try{if(document.fullscreenElement){document.exitFullscreen();}else if(document.documentElement.requestFullscreen){document.documentElement.requestFullscreen().catch(function(){});}}catch(e){}}
  document.getElementById('prec').addEventListener('click',function(){afficher(i-1,true);});
  document.getElementById('suiv').addEventListener('click',function(){afficher(i+1,true);});
  document.getElementById('b-notes').addEventListener('click',function(){bascule(pNotes);});
  document.getElementById('b-sommaire').addEventListener('click',function(){bascule(pSommaire);});
  document.getElementById('b-plein').addEventListener('click',plein);
  liens.forEach(function(a,k){a.addEventListener('click',function(e){e.preventDefault();afficher(k,true);pSommaire.hidden=true;});});
  document.addEventListener('keydown',function(e){
    if(e.altKey||e.ctrlKey||e.metaKey)return;
    var k=e.key, surCommande=e.target.closest&&e.target.closest('button,a');
    if(surCommande&&(k===' '||k==='Enter'))return;
    if(k==='ArrowRight'||k==='PageDown'||k===' '||k==='Enter'){e.preventDefault();afficher(i+1,true);}
    else if(k==='ArrowLeft'||k==='PageUp'||k==='Backspace'){e.preventDefault();afficher(i-1,true);}
    else if(k==='Home'){e.preventDefault();afficher(0,true);}else if(k==='End'){e.preventDefault();afficher(diapos.length-1,true);}
    else if(k==='n'||k==='N'){bascule(pNotes);}else if(k==='m'||k==='M'){bascule(pSommaire);}
    else if(k==='f'||k==='F'){plein();}
    else if(k==='Escape'){pNotes.hidden=true;pSommaire.hidden=true;}
  });
  var x0=null;
  scene.addEventListener('touchstart',function(e){x0=e.touches[0].clientX;},{passive:true});
  scene.addEventListener('touchend',function(e){if(x0==null)return;var dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40)afficher(i+(dx<0?1:-1),true);x0=null;});
  window.addEventListener('resize',echelle);
  window.addEventListener('hashchange',function(){afficher(lireHash(),true,true);});
  echelle();afficher(lireHash(),false,true);
})();
"""


def construire():
    d = diapositives()
    sections = []
    for k, x in enumerate(d):
        classes = " ".join(["diapo", x["source"]] + x["classes"])
        num = f'<div class="num">{x["numero"]}</div>' if x["numero"] else ""
        sections.append(f'<section class="{classes}" id="diapo-{k + 1}" aria-label="{html.escape(x["partie"])}, {html.escape(x["titre"])}" aria-hidden="true">'
                        f'<div class="entete">Data Tigers · NLP 2 · soutenance du 30 novembre 2026</div>\n{x["corps"]}'
                        f'<div class="pied">{html.escape(x["pied"])}</div>{num}</section>')
    donnees = [{"partie": x["partie"], "duree": x["duree"], "notes_html": notes_html(x["notes"])} for x in d]
    sommaire, partie = [], None
    for k, x in enumerate(d):
        if x["partie"] != partie:
            partie = x["partie"]
            sommaire.append(f"<h3>{html.escape(partie)}</h3>")
        sommaire.append(f'<a href="#d{k + 1}">{k + 1}. {html.escape(x["titre"])}</a>')
    corps = f"""<title>Soutenance Data Tigers</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="Supports de soutenance de l'équipe Data Tigers, NLP 2 : pitch, démonstration, présentation et annexes.">
<style>{CSS}</style>
<main class="scene"><div class="cadre">
{chr(10).join(sections)}
</div></main>
<div class="progression" aria-hidden="true"></div>
<div class="panneau" id="notes" hidden><h2 id="notes-duree"></h2><div id="notes-corps"></div></div>
<nav class="panneau" id="sommaire" hidden aria-label="Sommaire"><div class="sommaire">{"".join(sommaire)}</div></nav>
<div class="barre-cmd" role="toolbar" aria-label="Commandes de la présentation">
<button id="prec" type="button" aria-label="Diapositive précédente"><span class="long">Précédente</span><span class="court">←</span></button>
<button id="suiv" type="button" aria-label="Diapositive suivante"><span class="long">Suivante</span><span class="court">→</span></button>
<span class="partie"></span><span class="compteur"></span><span class="espace"></span>
<button id="b-sommaire" type="button">Sommaire<span class="facultatif"> (M)</span></button>
<button id="b-notes" type="button">Notes<span class="facultatif"> (N)</span></button>
<button id="b-plein" type="button" class="facultatif">Plein écran (F)</button>
</div>
<script type="application/json" id="donnees">{json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/")}</script>
<script>{JS}</script>
"""
    complet = ('<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
               '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n'
               + corps + "</body>\n</html>\n")
    return d, corps, complet


if __name__ == "__main__":
    d, corps, complet = construire()
    for interdit, nom in ((chr(0x2014), "tiret cadratin"), (chr(0x2013), "tiret demi-cadratin")):
        assert interdit not in complet, nom
    assert not re.search("[" + chr(0x1F300) + "-" + chr(0x1FAFF) + chr(0x2600) + "-" + chr(0x27BF) + "]", complet), "émoji"
    (RACINE / "soutenance.html").write_text(complet, encoding="utf-8")
    if "--corps-seul" in sys.argv:
        Path(sys.argv[sys.argv.index("--corps-seul") + 1]).write_text(corps, encoding="utf-8")
    parties = {}
    for x in d:
        if x["duree"]:
            parties[x["partie"]] = parties.get(x["partie"], 0) + x["duree"]
    print(len(d), "diapositives ; durées visées par partie (s) :", parties, "; total", sum(parties.values()), "s")
