// Tests du client de la couche locale (couche.js) sur un vrai serveur HTTP local, sans modèle : node --test, depuis
// demo_b/. Le délai est raccourci ; seul le comportement du client est vérifié, pas la chaîne.

import { test } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { ErreurAppel, poserQuestion, VERSION_CONTRAT } from "./couche.js";

const REPONSE = JSON.stringify({ version_contrat: VERSION_CONTRAT, statut: "reponse_citee" });

// lance un serveur, exécute le corps du test, puis ferme les connexions restées ouvertes
async function avecServeur(traiter, corps) {
  const stats = { appels: 0 };
  const serveur = createServer((req, res) => {
    stats.appels += 1;
    traiter(res);
  });
  await new Promise((pret) => serveur.listen(0, "127.0.0.1", pret));
  try {
    await corps(`http://127.0.0.1:${serveur.address().port}`, stats);
  } finally {
    serveur.closeAllConnections();
    await new Promise((fin) => serveur.close(fin));
  }
}

test("en-têtes immédiats et corps bloqué : erreur de délai, sans relance automatique", async () => {
  await avecServeur(
    (res) => {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.flushHeaders();
      res.write('{"version_contrat":'); // le JSON n'est jamais terminé
    },
    async (base, stats) => {
      await assert.rejects(poserQuestion("Q ?", { base, delaiMs: 100 }), (e) => {
        assert.ok(e instanceof ErreurAppel);
        assert.equal(e.type, "delai");
        return true;
      });
      assert.equal(stats.appels, 1);
    },
  );
});

test("corps complet avant le délai : la réponse est rendue", async () => {
  await avecServeur(
    (res) => {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(REPONSE);
    },
    async (base) => {
      const r = await poserQuestion("Q ?", { base, delaiMs: 2000 });
      assert.equal(r.statut, "reponse_citee");
    },
  );
});

test("aucune réponse du tout : erreur de délai", async () => {
  await avecServeur(
    () => {},
    async (base) => {
      await assert.rejects(poserQuestion("Q ?", { base, delaiMs: 100 }), (e) => e.type === "delai");
    },
  );
});

test("409 : question déjà en cours, sans relance automatique", async () => {
  await avecServeur(
    (res) => {
      res.writeHead(409, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ version_contrat: VERSION_CONTRAT, erreur: { type: "occupe", message: "occupé" } }));
    },
    async (base, stats) => {
      await assert.rejects(poserQuestion("Q ?", { base, delaiMs: 2000 }), (e) => e.type === "occupe" && e.http === 409);
      assert.equal(stats.appels, 1);
    },
  );
});

test("corps illisible avec un code 200 : réponse inattendue, pas une erreur de délai", async () => {
  await avecServeur(
    (res) => {
      res.writeHead(200);
      res.end("pas du JSON");
    },
    async (base) => {
      await assert.rejects(poserQuestion("Q ?", { base, delaiMs: 2000 }), (e) => e.type === "http");
    },
  );
});
