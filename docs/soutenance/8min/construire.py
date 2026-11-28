"""Construit le support de soutenance de 8 minutes en un seul fichier HTML, sans aucune ressource externe.

    python docs/soutenance/8min/construire.py           # écrit docs/soutenance/presentation_8min.html

Le gabarit deck.html reçoit trois éléments, embarqués pour fonctionner hors ligne le jour de la soutenance :
- la police DM Sans (variable, latin), sous licence SIL OFL 1.1 (polices/OFL-DM-Sans.txt), version 5.3.0 de
  @fontsource-variable/dm-sans, la même que le site du volet A ;
- le logo de l'équipe (#176), copie de docs/charte/logo/logo-tigre.svg ;
- donnees.json : les données réelles des schémas, calculées le 21/11/2026 (voir README.md).
"""
from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
SORTIE = ICI.parent / "presentation_8min.html"
EMPREINTES = {
    "polices/dm-sans-latin-wght-normal.woff2": "9fea608a947e67020c33cad9a6fe3d60c54119dfb8cff87768a8117a15ed7543",
    "logo-tigre.svg": "89c1d70f6a28265c968b5d88c4347c5ea7221376eca1c96a490b6d59049b019f",   # = docs/charte/logo (PR #177)
}


def sha256(chemin: Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def main() -> int:
    for nom, attendue in EMPREINTES.items():
        if attendue is not None and sha256(ICI / nom) != attendue:
            raise SystemExit(f"{nom} : empreinte inattendue, fichier modifié")
    gabarit = (ICI / "deck.html").read_text(encoding="utf-8")
    police = base64.b64encode((ICI / "polices/dm-sans-latin-wght-normal.woff2").read_bytes()).decode("ascii")
    logo = "data:image/svg+xml;base64," + base64.b64encode((ICI / "logo-tigre.svg").read_bytes()).decode("ascii")
    donnees = json.loads((ICI / "donnees.json").read_text(encoding="utf-8"))
    texte_donnees = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    for marque in ("@@POLICE@@", "@@LOGO_URI@@", "/*@@DONNEES@@*/null"):
        if marque not in gabarit:
            raise SystemExit(f"Marque absente du gabarit : {marque}")
    html = (gabarit.replace("@@POLICE@@", police).replace("@@LOGO_URI@@", logo)
            .replace("/*@@DONNEES@@*/null", texte_donnees))
    if "@@" in html:
        raise SystemExit("Une marque n'a pas été remplacée")
    SORTIE.write_text(html, encoding="utf-8")
    print(f"{SORTIE.name} : {len(html.encode()):,} octets, SHA-256 {hashlib.sha256(html.encode()).hexdigest()[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
