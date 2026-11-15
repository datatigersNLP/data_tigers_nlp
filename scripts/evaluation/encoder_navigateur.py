"""Pilote de la page d'encodage dans le navigateur (protocole 05 et son amendement A1, #164).

Sert la racine du dépôt sur 127.0.0.1 seulement, ouvre `scripts/evaluation/encodage_navigateur.html` dans Chrome sans
interface, avec un profil temporaire vierge, et reçoit les vecteurs que la page renvoie (paramètre `envoi=1`). Le
fichier reçu est écrit dans `data/adaptation/navigateur/vecteurs/`, jamais écrasé. Aucun autre fichier n'est servi
que ceux dont la page a besoin, et aucun autre fichier n'est écrit.

    CHROME_PATH=... python scripts/evaluation/encoder_navigateur.py --modele base [--lot cdtn_mesure]
"""

from __future__ import annotations

import argparse
import functools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "adaptation" / "navigateur" / "vecteurs"
PAGE = "scripts/evaluation/encodage_navigateur.html"
# Seuls fichiers lisibles : la page, l'en-tête de l'index de mesure, les lots de questions et les modèles locaux.
AUTORISES = re.compile(r"^/(scripts/evaluation/encodage_navigateur\.html"
                       r"|data/indexation/site/index_m2\.json"
                       r"|data/evaluation/notebook03/questions_navigateur\.json"
                       r"|data/evaluation/cdtn/(questions_cdtn|formulations_mesure)\.json"
                       r"|data/adaptation/navigateur/(base|ajuste)/[A-Za-z0-9_./-]+)$")
NOM_SORTIE = re.compile(r"^vecteurs_(navigateur|cdtn|cdtn_mesure)(_(base|ajuste))?\.json$")


class Gestionnaire(SimpleHTTPRequestHandler):
    recu: dict = {}

    def log_message(self, *args):          # journal discret : seules les erreurs comptent
        pass

    def do_GET(self):
        chemin = urlparse(self.path).path
        if ".." in chemin or not AUTORISES.match(chemin):
            self.send_error(404)
            return
        super().do_GET()

    def do_HEAD(self):
        chemin = urlparse(self.path).path
        if ".." in chemin or not AUTORISES.match(chemin):
            self.send_error(404)
            return
        super().do_HEAD()

    def do_POST(self):
        url = urlparse(self.path)
        nom = parse_qs(url.query).get("nom", [""])[0]
        if url.path != "/resultats" or not NOM_SORTIE.match(nom):
            self.send_error(403)
            return
        corps = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        donnees = json.loads(corps.decode("utf-8"))
        SORTIE.mkdir(parents=True, exist_ok=True)
        with open(SORTIE / nom, "x", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False)
        Gestionnaire.recu = {"nom": nom, "erreur": donnees.get("erreur"), "n": len(donnees.get("vecteurs", []))}
        self.send_response(204)
        self.end_headers()


def encoder(modele: str | None, lot: str | None, delai: int = 900) -> dict:
    chrome = os.environ.get("CHROME_PATH")
    if not chrome or not Path(chrome).exists():
        raise SystemExit("CHROME_PATH absent")
    Gestionnaire.recu = {}
    serveur = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Gestionnaire, directory=str(RACINE)))
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    parametres = "&".join(p for p in (f"modele={modele}" if modele else "", f"lot={lot}" if lot else "", "envoi=1") if p)
    url = f"http://127.0.0.1:{serveur.server_address[1]}/{PAGE}?{parametres}"
    profil = tempfile.mkdtemp(prefix="chrome_encodage_")
    navigateur = subprocess.Popen([chrome, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                                   "--disable-extensions", f"--user-data-dir={profil}", url],
                                  stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    debut = time.time()
    try:
        while not Gestionnaire.recu and time.time() - debut < delai:
            time.sleep(1)
    finally:
        navigateur.terminate()
        try:
            navigateur.wait(timeout=20)
        except subprocess.TimeoutExpired:
            navigateur.kill()
        serveur.shutdown()
        shutil.rmtree(profil, ignore_errors=True)
    if not Gestionnaire.recu:
        raise SystemExit(f"aucun résultat reçu en {delai} s")
    resultat = {**Gestionnaire.recu, "duree_s": round(time.time() - debut, 1)}
    print(json.dumps(resultat, ensure_ascii=False))
    if resultat["erreur"]:
        raise SystemExit(1)
    return resultat


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--modele", choices=("base", "ajuste"))
    p.add_argument("--lot", choices=("cdtn", "cdtn_mesure"))
    a = p.parse_args(argv)
    encoder(a.modele, a.lot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
