"""Couche locale de la démonstration du volet B avec la chaîne v2 (#172), même contrat que serveur_demo.py (#121).

Seule la récupération change (scripts/recuperation/recuperation_demo.py) : partie dense par l'E5 de base, BM25 V3,
fusion RRF, reclasseur bge-reranker-v2-m3 sur 20 candidats, 10 passages dans le budget de tokens ; consigne v1 ; pas de
seuil S, le modèle seul s'abstient. C'est l'état R1 du protocole 10 (famille B), gardé par sa règle de maintien
(docs/etudes/evaluation/10_resultats.md, section 5). `--dense ajuste` sert l'état R2 (encodeur ajusté v1 du volet A,
requête q8 servie par le site), mesuré à 84,3 % de rappel du contexte contre 86,0 % pour R1 sur le jeu v2. L'ordre des
passages suit le reclasseur ; le score affiché reste la similarité cosinus de la partie dense.

    python scripts/rag/serveur_demo_v2.py --modele <nom Ollama> --digest <empreinte>   # puis http://127.0.0.1:8765/

Routes et garanties de serveur_demo.py, inchangées : 127.0.0.1 seulement, Hugging Face hors ligne (bge-m3, tokeniseur
Qwen et, avec la partie dense par défaut, E5 lus dans le cache local), une question à la fois, état sans génération.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import time

os.environ["HF_HUB_OFFLINE"] = "1"   # contrat, section 2 : aucun accès réseau, posé avant tout chargement
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "recuperation"))

import generation  # noqa: E402  (verrouillé, inchangé)
import rag  # noqa: E402  (verrouillé, inchangé)
import recuperation as rc  # noqa: E402
import recuperation_demo as rd  # noqa: E402
import serveur_demo as sd  # noqa: E402


class ChaineV2(sd.Chaine):
    """La chaîne de serveur_demo.py, dont l'encodeur est remplacé par la récupération v2 (même verrou, même état)."""

    def __init__(self, index, recuperation, tokeniseur_disponible: bool, causes: list[str], **config):
        super().__init__(index, recuperation, tokeniseur_disponible, causes, **config)
        self.recuperation = recuperation

    @classmethod
    def charger_v2(cls, dense: str = "base", **config) -> "ChaineV2":
        """Charge une seule fois index et outils. Un échec n'arrête pas la couche : /api/etat en donne la cause."""
        index, recuperation, causes = None, None, []
        try:
            index = rag.charger_index()
        except rag.ErreurIndex as exc:
            causes.append(f"Index refusé : {exc}")
        if index is not None:
            try:
                recuperation = rd.RecuperationDemo.charger(dense, index)
            except (rag.ErreurRecuperation, rc.ErreurRecuperationV2, generation.ErreurGeneration, OSError,
                    ImportError) as exc:
                causes.append(f"Récupération v2 indisponible (dépendances ou cache local, voir demo_b/README.md) : {exc}")
        return cls(index, recuperation, recuperation is not None, causes, **config)

    def etat(self) -> dict:
        etat = super().etat()
        etat["chaine"] = self.recuperation.description if self.recuperation is not None else None
        return etat

    def repondre(self, question: str) -> dict:
        """Même ordre que serveur_demo.Chaine.repondre : récupération, contexte, contrôle de version, génération."""
        debut = time.monotonic()
        resultats, contexte, reponse, erreur = None, None, None, None
        try:
            if self.index is None or self.recuperation is None:
                raise rag.ErreurRecuperation("Index ou récupération non chargés : voir l'état de la chaîne.")
            recup = self.recuperation.recuperer(question)
            passages = self.index.passages
            contexte = rc.construire_contexte_v2(question, recup["contexte"], passages)
            resultats = [{"passage": passages[i], "rang": rang, "score": float(recup["scores_denses"][i])}
                         for rang, i in enumerate(recup["contexte"], 1)]
            self._controler_version(sd._api("/api/version").get("version"))
            reponse = sd.generer_reponse(contexte, rag.ABSTENTION, self.modele, self.digest)
        except (rag.ErreurRecuperation, generation.ErreurGeneration, rc.ErreurRecuperationV2) as exc:
            erreur = {"type": type(exc).__name__, "message": str(exc)}
        return sd.mettre_en_forme(question, resultats, contexte, reponse, erreur, time.monotonic() - debut)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=sd.PORT)
    parser.add_argument("--interface", type=Path, default=sd.DOSSIER_INTERFACE, help="interface construite de demo_b/")
    parser.add_argument("--modele", help="modèle Ollama à servir, avec --digest (par défaut celui de la #31)")
    parser.add_argument("--digest", help="empreinte attendue de ce modèle")
    parser.add_argument("--version-ollama", default=sd.VERSION_OLLAMA)
    parser.add_argument("--dense", choices=rd.DENSES, default="base",
                        help="partie dense : base (état R1, par défaut, retenu par le protocole 10) ou ajuste (état R2)")
    args = parser.parse_args(argv)
    if bool(args.modele) != bool(args.digest):
        parser.error("--modele et --digest se donnent ensemble")
    if not (args.interface / "index.html").is_file():
        print(f"Interface absente de {args.interface} : lancer npm run build dans demo_b/.", file=sys.stderr)
    print("Chargement : index, encodeur, BM25, reclasseur bge-m3 et tokeniseur Qwen (cache local).", file=sys.stderr)
    chaine = ChaineV2.charger_v2(args.dense, modele=args.modele or sd.MODELE_QWEN,
                                 digest=args.digest or sd.DIGEST_QWEN_31, version_ollama=args.version_ollama)
    for cause in chaine.causes:
        print(cause, file=sys.stderr)
    try:
        serveur = sd.Serveur(chaine, args.port, args.interface)
    except OSError as exc:
        print(f"Port {args.port} indisponible : {exc}", file=sys.stderr)
        return 1
    etat = chaine.recuperation.description["etat"] if chaine.recuperation else "non chargée"
    print(f"Couche locale prête : http://127.0.0.1:{args.port}/ (chaîne v2, état {etat} ; Ctrl+C pour arrêter)",
          file=sys.stderr)
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        serveur.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
