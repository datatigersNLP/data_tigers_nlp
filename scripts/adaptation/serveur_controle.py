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
        if self.path == "/api/sauvegarder_fidelite":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode("utf-8"))
            out_name = "fidelite_navigateur_ajuste.json" if data.get("modele_ajuste") else "fidelite_navigateur.json"
            out_path = PROJECT_ROOT / "data" / "indexation" / "controle" / out_name
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[Serveur] Résultats enregistrés dans {out_path} ({len(body)} octets)")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_error(404, "Endpoint inconnu")


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
