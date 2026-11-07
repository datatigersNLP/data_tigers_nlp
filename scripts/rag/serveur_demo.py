"""Couche locale de la démonstration du volet B (#111), selon le contrat de la #121.

Elle relie l'interface de demo_b/ à la chaîne de la #85, sans en changer la logique : elle appelle les fonctions de
rag.py et generation.py dans le même ordre que main(), avec une question tapée au lieu d'une question de calibration.

    python scripts/rag/serveur_demo.py          # puis ouvrir http://127.0.0.1:8765/

Routes : GET / (interface construite), GET /api/etat, POST /api/question. Tout reste sur 127.0.0.1 : E5 et le
tokeniseur Qwen sont lus dans le cache Hugging Face, préparé avant la démonstration.
"""

from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback
from urllib.parse import urlsplit

# Contrat, section 2 : aucun accès réseau. À poser avant tout chargement : rag et generation importent Hugging Face
# à la demande.
os.environ["HF_HUB_OFFLINE"] = "1"

if __package__:
    from .generation import (API_OLLAMA, DIGEST_QWEN_31, MODELE_QWEN, ErreurGeneration, _api,
                             charger_tokeniseur_qwen, generer_reponse, verifier_ollama)
    from .rag import (ABSTENTION, DOSSIER_INDEX, RACINE, ErreurIndex, ErreurRecuperation, charger_encodeur,
                      charger_index, construire_contexte, encoder_question, recuperer_passages)
else:
    from generation import (API_OLLAMA, DIGEST_QWEN_31, MODELE_QWEN, ErreurGeneration, _api,
                            charger_tokeniseur_qwen, generer_reponse, verifier_ollama)
    from rag import (ABSTENTION, DOSSIER_INDEX, RACINE, ErreurIndex, ErreurRecuperation, charger_encodeur,
                     charger_index, construire_contexte, encoder_question, recuperer_passages)


VERSION_CONTRAT = "b1-demo-v1"
VERSION_OLLAMA = "0.40.13"  # contrat, section 4 : même version épinglée que mesure.py (un test vérifie l'égalité)
PORT = 8765  # celui vers lequel Vite relaie /api en développement (demo_b/vite.config.js)
DOSSIER_INTERFACE = RACINE / "demo_b" / "dist"
TAILLE_MAX_CORPS = 64 * 1024  # une question ; la limite de fond reste celle d'E5 (512 tokens)
CHAMPS_MESURES = ("total_duration", "load_duration", "prompt_eval_duration", "eval_duration",
                  "prompt_eval_count", "eval_count")  # contrat, section 5


def mettre_en_forme(question: str, resultats, contexte, generation, erreur, duree_s: float) -> dict:
    """Construit la réponse de la section 5 : toutes les clés sont présentes, quels que soient le statut et l'échec."""
    validation = generation["validation_citations"] if generation else {}
    citations = validation.get("citations", [])
    sources = []
    if resultats and contexte:
        for resultat, source in zip(resultats, contexte["sources"]):
            passage = resultat["passage"]
            sources.append({
                "reference": source["reference"], "citee": source["reference"] in citations,
                "rang": resultat["rang"], "score": resultat["score"],
                **{k: passage[k] for k in ("passage_id", "titre_fiche", "section_titre", "chemin", "url",
                                           "url_citation", "date_maj", "texte")},
            })
    statut = "erreur_preparation"
    if generation:
        statut = generation["statut"]
        if statut == "erreur_technique":
            erreur = {"type": "erreur_technique", "message": ", ".join(generation["erreurs_techniques"])}
    mesures = generation["mesures_ollama"] if generation else None
    return {
        "version_contrat": VERSION_CONTRAT,
        "question": question,
        "statut": statut,
        "reponse": generation["reponse_brute"] if generation else None,
        "citations": citations,
        "citations_invalides": validation.get("citations_invalides", []),
        "verifications": {k: validation.get(k, False) for k in ("justification_semantique_verifiee",
                                                                "couverture_des_affirmations_verifiee")},
        "sources": sources,
        "modele": ({"nom": generation["ollama"]["modele"], "digest": generation["ollama"]["digest"]}
                   if generation else None),
        "mesures": {"duree_totale_s": round(duree_s, 3),
                    "ollama": {k: mesures.get(k) for k in CHAMPS_MESURES} if mesures else None},
        "erreur": erreur,
    }


class Chaine:
    """Index, encodeur et modèle configuré. Le navigateur ne choisit jamais le modèle (contrat, section 10)."""

    def __init__(self, index, encodeur, tokeniseur_disponible: bool, causes: list[str], modele: str = MODELE_QWEN,
                 digest: str = DIGEST_QWEN_31, version_ollama: str = VERSION_OLLAMA):
        self.index, self.encodeur, self.tokeniseur_disponible = index, encodeur, tokeniseur_disponible
        self.causes = causes  # ce qui a manqué au démarrage ; relancer la couche une fois le manque corrigé
        self.modele, self.digest, self.version_ollama = modele, digest, version_ollama
        self.verrou = threading.Lock()  # une question à la fois, même avec deux onglets (contrat, section 6)

    @classmethod
    def charger(cls, dossier_index: Path = DOSSIER_INDEX, **config) -> "Chaine":
        """Charge une seule fois index et E5. Un échec n'arrête pas la couche : /api/etat en donne la cause."""
        index, encodeur, tokeniseur, causes = None, None, False, []
        try:
            index = charger_index(dossier_index)
        except ErreurIndex as exc:
            causes.append(f"Index refusé : {exc}")
        try:
            encodeur = charger_encodeur()
        except ErreurRecuperation as exc:
            causes.append(f"Encodeur E5 indisponible : {exc}")
        try:
            charger_tokeniseur_qwen()
            tokeniseur = True
        except ErreurGeneration:
            causes.append("Tokeniseur Qwen absent du cache local : le préparer avant la démonstration (demo_b/README.md).")
        return cls(index, encodeur, tokeniseur, causes, **config)

    def _controler_version(self, version) -> None:
        if version != self.version_ollama:
            raise ErreurGeneration(f"Version d'Ollama {version}, attendue {self.version_ollama} : "
                                   "vérifier la configuration avant la démonstration.")

    def etat(self) -> dict:
        """Section 4 : contrôle le modèle servi sans aucun appel de génération."""
        causes = list(self.causes)
        ollama = {"joignable": False, "verifie": False, "version": None, "modele": self.modele, "digest": None}
        try:
            ollama["version"] = _api("/api/version").get("version")
            ollama["joignable"] = True
        except ErreurGeneration:
            causes.append(f"Ollama ne répond pas sur {API_OLLAMA} : le lancer, puis réessayer.")
        if ollama["joignable"]:
            try:
                infos = verifier_ollama(self.modele, self.digest)
                self._controler_version(infos["version"])
                ollama.update(verifie=True, digest=infos["digest"])
            except ErreurGeneration as exc:
                causes.append(str(exc))
        index = self.index
        return {
            "version_contrat": VERSION_CONTRAT,
            "pret": bool(index and self.encodeur and self.tokeniseur_disponible and ollama["verifie"]),
            "index": {"verifie": index is not None,
                      "nb_passages": len(index.passages) if index else None,
                      "sha256_index": index.entete["index"]["sha256"] if index else None},
            "encodeur_charge": self.encodeur is not None,
            "tokeniseur_disponible": self.tokeniseur_disponible,
            "ollama": ollama,
            "occupe": self.verrou.locked(),
            "message": " ; ".join(causes) or None,
        }

    def repondre(self, question: str) -> dict:
        """Section 5 : même ordre que main() ; la question reste mot pour mot, seul encoder_question ajoute le préfixe."""
        debut = time.monotonic()
        resultats, contexte, generation, erreur = None, None, None, None
        try:
            if self.index is None or self.encodeur is None:
                raise ErreurRecuperation("Index ou encodeur non chargé : voir l'état de la chaîne.")
            resultats = recuperer_passages(self.index, encoder_question(self.encodeur, question))
            contexte = construire_contexte(question, resultats)
            self._controler_version(_api("/api/version").get("version"))
            generation = generer_reponse(contexte, ABSTENTION, self.modele, self.digest)
        except (ErreurRecuperation, ErreurGeneration) as exc:
            erreur = {"type": type(exc).__name__, "message": str(exc)}
        return mettre_en_forme(question, resultats, contexte, generation, erreur, time.monotonic() - debut)


class Gestionnaire(SimpleHTTPRequestHandler):
    # le registre de Windows peut donner text/plain aux .js, que le navigateur refuse alors d'exécuter
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".js": "text/javascript", ".css": "text/css",
                      ".svg": "image/svg+xml", ".woff2": "font/woff2", ".json": "application/json"}

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server, directory=str(server.dossier_interface))

    def _json(self, code: int, corps: dict) -> None:
        octets = json.dumps(corps, ensure_ascii=False).encode("utf-8")
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(octets)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(octets)
        except ConnectionError:
            pass  # l'interface a abandonné l'appel (délai dépassé) : il n'y a plus personne à qui répondre

    def _refus(self, code: int, type_erreur: str, message: str) -> None:
        self._json(code, {"version_contrat": VERSION_CONTRAT, "erreur": {"type": type_erreur, "message": message}})

    def list_directory(self, path):
        self.send_error(404)
        return None

    def do_GET(self):
        chemin = urlsplit(self.path).path
        if chemin == "/api/etat":
            self._json(200, self.server.chaine.etat())
        elif chemin.startswith("/api/"):
            self._refus(404, "route_inconnue", "Route inconnue.")
        else:
            super().do_GET()

    def _lire_question(self) -> str | None:
        """La question telle qu'envoyée, ou None si le corps n'est pas un JSON avec une question non vide.

        Exiger application/json écarte aussi les envois d'une autre page : ce type impose au navigateur une
        vérification préalable que la couche n'accepte pas.
        """
        if self.headers.get_content_type() != "application/json":
            return None
        try:
            taille = int(self.headers.get("Content-Length", ""))
            if not 0 < taille <= TAILLE_MAX_CORPS:
                return None
            corps = json.loads(self.rfile.read(taille).decode("utf-8"))
        except (ValueError, OSError):
            return None
        question = corps.get("question") if isinstance(corps, dict) else None
        return question if isinstance(question, str) and question.strip() else None

    def do_POST(self):
        if urlsplit(self.path).path != "/api/question":
            self._refus(404, "route_inconnue", "Route inconnue.")
            return
        question = self._lire_question()
        if question is None:
            self._refus(400, "requete_invalide", "La requête doit être un JSON avec une question non vide.")
            return
        chaine = self.server.chaine
        if not chaine.verrou.acquire(blocking=False):
            self._refus(409, "occupe", "Une question est déjà en cours.")
            return
        try:
            self._json(200, chaine.repondre(question))
        except Exception:  # défaut inattendu : tracé ici, sans bloquer les questions suivantes
            traceback.print_exc()
            self._refus(500, "erreur_interne", "Erreur inattendue de la couche locale, voir son terminal.")
        finally:
            chaine.verrou.release()


class Serveur(ThreadingHTTPServer):
    # sous Windows, cette option laisserait deux couches écouter le même port sans aucune erreur
    allow_reuse_address = False

    def __init__(self, chaine: Chaine, port: int = PORT, dossier_interface: Path = DOSSIER_INTERFACE):
        self.chaine, self.dossier_interface = chaine, Path(dossier_interface)
        super().__init__(("127.0.0.1", port), Gestionnaire)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--index-dir", type=Path, default=DOSSIER_INDEX)
    parser.add_argument("--interface", type=Path, default=DOSSIER_INTERFACE, help="interface construite de demo_b/")
    parser.add_argument("--modele", help="modèle Ollama à servir, avec --digest (par défaut celui de la #31)")
    parser.add_argument("--digest", help="empreinte attendue de ce modèle")
    parser.add_argument("--version-ollama", default=VERSION_OLLAMA)
    args = parser.parse_args(argv)
    if bool(args.modele) != bool(args.digest):
        parser.error("--modele et --digest se donnent ensemble")
    if not (args.interface / "index.html").is_file():
        print(f"Interface absente de {args.interface} : lancer npm run build dans demo_b/.", file=sys.stderr)
    print("Chargement de l'index, d'E5 et du tokeniseur Qwen, depuis le cache local.", file=sys.stderr)
    chaine = Chaine.charger(args.index_dir, modele=args.modele or MODELE_QWEN, digest=args.digest or DIGEST_QWEN_31,
                            version_ollama=args.version_ollama)
    for cause in chaine.causes:
        print(cause, file=sys.stderr)
    try:
        serveur = Serveur(chaine, args.port, args.interface)
    except OSError as exc:
        print(f"Port {args.port} indisponible : {exc}", file=sys.stderr)
        return 1
    print(f"Couche locale prête : http://127.0.0.1:{args.port}/ (Ctrl+C pour arrêter)", file=sys.stderr)
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        serveur.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
