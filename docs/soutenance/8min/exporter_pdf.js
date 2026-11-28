// Exporte le support de 8 minutes en PDF de secours : une page par appui, comme à l'écran (flèche droite = page suivante),
// puis le sommaire des annexes et les 17 annexes, une page chacune. Chromium sans interface, mouvement réduit (les
// animations sont remplacées par leur état final), page de 1920 x 1080 pixels, texte vectoriel sélectionnable.
//
// Usage : PLAYWRIGHT_CORE=<chemin de playwright-core> node docs/soutenance/8min/exporter_pdf.js <presentation_8min.html> <sortie.pdf>
// Prérequis : playwright-core 1.60.0 avec son Chromium, et pdfunite (poppler). Seul le fichier local est chargé : toute
// autre requête est refusée. Les pages intermédiaires vont dans un dossier temporaire, supprimé à la fin.
"use strict";
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");
const { chromium } = require(process.env.PLAYWRIGHT_CORE || "playwright-core");

const [, , entree, sortie] = process.argv;
if (!entree || !sortie) { console.error("usage : node exporter_pdf.js <presentation_8min.html> <sortie.pdf>"); process.exit(2); }
const url = "file://" + path.resolve(entree);

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "support-pdf-"));
  const navigateur = await chromium.launch({ headless: true });
  const contexte = await navigateur.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1, serviceWorkers: "block", reducedMotion: "reduce" });
  const refus = [];
  await contexte.route("**/*", (r) => {
    const u = r.request().url();
    if (u.startsWith("file:") || u.startsWith("data:") || u.startsWith("blob:")) return r.continue();
    refus.push(u); return r.abort();
  });
  const page = await contexte.newPage();
  await page.emulateMedia({ media: "screen", reducedMotion: "reduce" });
  await page.goto(url);
  const etapes = await page.evaluate(() => [...document.querySelectorAll(".diapo")].map((d) => ({
    nom: d.getAttribute("aria-label"), etapes: Number(d.getAttribute("data-etapes") || 0), annexe: d.classList.contains("annexe") })));
  const pages = [];
  for (let k = 1; k <= etapes.length; k++) {
    const d = etapes[k - 1];
    for (let e = 0; e <= (d.annexe ? 0 : d.etapes); e++) {
      await page.goto(`${url}#${k}.${e}`); await page.reload();
      await page.evaluate(() => document.fonts.ready); await page.waitForTimeout(300);
      const actif = await page.evaluate(() => document.querySelector(".diapo.active")?.getAttribute("aria-label"));
      if (actif !== d.nom) throw new Error(`diapositive ${k} : attendu « ${d.nom} », affiché « ${actif} »`);
      const f = path.join(tmp, `p${String(pages.length).padStart(3, "0")}.pdf`);
      await page.pdf({ path: f, width: "1920px", height: "1080px", printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 }, pageRanges: "1" });
      pages.push({ f, k, e, nom: d.nom });
    }
  }
  await navigateur.close();
  if (refus.length) throw new Error("requêtes refusées : " + refus.join(", "));
  execFileSync("pdfunite", [...pages.map((p) => p.f), path.resolve(sortie)]);
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log(`${pages.length} pages (${etapes.length} diapositives, dont ${etapes.filter((x) => x.annexe).length} d'annexes) -> ${sortie}`);
})().catch((e) => { console.error(e); process.exit(1); });
