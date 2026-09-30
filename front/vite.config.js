import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// GitHub Pages sert le site sous https://datatigersnlp.github.io/data_tigers_nlp/ :
// sans ce chemin de base, les fichiers JS et CSS sont cherchés à la racine du domaine
// et la page reste blanche une fois déployée (risque signalé dans le ticket #7).
const BASE = "/data_tigers_nlp/";

export default defineConfig({
  base: BASE,
  plugins: [react(), tailwindcss()],
  define: {
    // version affichée en pied de page : preuve que la page servie est bien la dernière construite
    __VERSION__: JSON.stringify((process.env.GITHUB_SHA ?? "local").slice(0, 7)),
    __DATE_CONSTRUCTION__: JSON.stringify(new Date().toISOString().slice(0, 10)),
  },
});
