import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Interface de la démonstration du volet B (#111). Elle est servie par la couche locale (scripts/rag/serveur_demo.py,
// contrat de la #121) sur 127.0.0.1, à la racine : pas de chemin de base, contrairement au site du volet A.
// En développement, les appels /api sont relayés vers cette couche ; en mode maquette, ils ne partent pas : les
// réponses viennent des traces enregistrées (src/api/maquette.js).
const COUCHE_LOCALE = "http://127.0.0.1:8765";

export default defineConfig({
  base: "/",
  plugins: [react(), tailwindcss()],
  server: {
    host: "127.0.0.1",
    proxy: { "/api": COUCHE_LOCALE },
  },
  define: {
    __VERSION__: JSON.stringify((process.env.GITHUB_SHA ?? "local").slice(0, 7)),
    __DATE_CONSTRUCTION__: JSON.stringify(new Date().toISOString().slice(0, 10)),
  },
});
