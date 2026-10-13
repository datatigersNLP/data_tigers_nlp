"""
scripts/adaptation/serveur_controle.py
Serveur HTTP local permettant de servir les fichiers du dépôt et d'enregistrer
automatiquement les résultats de fidélité issus du navigateur.
"""

import http.server
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ControleHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api/sauvegarder_fidelite":
            self.send_error(404, "Endpoint inconnu")
            return

        # 1. Contrôle du Content-Type
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("application/json"):
            self.send_error(415, "Content-Type non supporté (application/json requis)")
            return

        # 2. Contrôle de l'Origin (protection contre les requêtes inter-origines non autorisées)
        origin = self.headers.get("Origin")
        if origin:
            allowed_prefixes = ("http://127.0.0.1:", "http://localhost:")
            if not any(origin.startswith(prefix) for prefix in allowed_prefixes):
                self.send_error(403, f"Origine non autorisée : {origin}")
                return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode("utf-8"))
        except Exception as e:
            self.send_error(400, f"Format JSON invalide : {e}")
            return

        # 3. Destination : ne JAMAIS écraser fidelite_navigateur.json (référence figée du notebook 02)
        if data.get("modele_ajuste"):
            out_name = "fidelite_navigateur_ajuste.json"
        elif data.get("modele_temoin") or data.get("depot") == "multilingual-e5-small-base":
            out_name = "fidelite_navigateur_temoin.json"
        else:
            out_name = "fidelite_navigateur_capture.json"

        out_path = PROJECT_ROOT / "data" / "indexation" / "controle" / out_name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[Serveur] Résultats enregistrés dans {out_path} ({len(body)} octets)")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')


def main():
    port = 8765
    server = http.server.HTTPServer(("127.0.0.1", port), ControleHandler)
    print(f"Serveur démarré sur http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")


if __name__ == "__main__":
    main()
