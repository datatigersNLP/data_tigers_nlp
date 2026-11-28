// Tests du convertisseur (convertir_traces.mjs) sur une trace artificielle, puis contrôle des deux réponses
// versionnées de la maquette contre le contrat de la #121 : node --test, depuis demo_b/.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { convertirTrace, VERSION_CONTRAT } from "./convertir_traces.mjs";

const CLES_CONTRAT = ["version_contrat", "question", "statut", "reponse", "citations", "citations_invalides",
  "verifications", "sources", "modele", "mesures", "erreur"];

function trace({ statut = "reponse_citee", citations = ["[P2]"], ordreContexte = [1, 2, 3, 4, 5] } = {}) {
  const passage = (i) => ({ passage_id: `m2-x-${i}`, titre_fiche: `Fiche ${i}`, section_titre: "S", chemin: [],
    url: "u", url_citation: "uc", date_maj: "2025-01-01", texte: `texte ${i}`, articles: [] });
  return {
    question: { id: "Q999", question: "Question ?" },
    resultats: [1, 2, 3, 4, 5].map((i) => ({ rang: i, indice: i, score: 1 - i / 100, passage: passage(i) })),
    contexte: { sources: ordreContexte.map((i, k) => ({ reference: `[P${k + 1}]`, passage_id: `m2-x-${i}` })) },
    generation: {
      statut, erreurs_techniques: statut === "erreur_technique" ? ["generation_incomplete"] : [],
      reponse_brute: "Réponse [P2].", validation_citations: { citations, citations_invalides: [] },
      ollama: { version: "0.40.5", modele: "m", digest: "d" },
      mesures_ollama: { total_duration: 1, load_duration: 0, prompt_eval_duration: 0, eval_duration: 1,
        prompt_eval_count: 10, eval_count: 2, done: true },
    },
  };
}

test("toutes les clés du contrat sont présentes, sans prompt ni gabarit", () => {
  const r = convertirTrace(trace(), "t.json");
  for (const c of CLES_CONTRAT) assert.ok(c in r, c);
  assert.equal(r.version_contrat, VERSION_CONTRAT);
  assert.equal(r.erreur, null);
  assert.equal(r.mesures.duree_totale_s, null);
  assert.ok(!("done" in r.mesures.ollama));
  assert.ok(!JSON.stringify(r).includes("contexte"));
});

test("la référence vient du contexte par identifiant de passage, et citee suit les citations", () => {
  const r = convertirTrace(trace({ ordreContexte: [2, 1, 3, 4, 5] }));
  assert.equal(r.sources[0].passage_id, "m2-x-1");
  assert.equal(r.sources[0].reference, "[P2]");
  assert.equal(r.sources[0].citee, true);
  assert.equal(r.sources[1].citee, false);
});

test("une erreur technique porte ses motifs dans erreur", () => {
  const r = convertirTrace(trace({ statut: "erreur_technique" }));
  assert.deepEqual(r.erreur, { type: "erreur_technique", message: "generation_incomplete" });
});

test("une trace sans cinq résultats est refusée", () => {
  const t = trace();
  t.resultats.pop();
  assert.throws(() => convertirTrace(t), /cinq résultats/);
});

for (const id of ["Q036", "Q003"]) {
  test(`réponse versionnée ${id} conforme au contrat`, () => {
    const r = JSON.parse(readFileSync(new URL(`../public/maquette/${id}.json`, import.meta.url), "utf-8"));
    for (const c of CLES_CONTRAT) assert.ok(c in r, c);
    assert.equal(r.sources.length, 5);
    assert.deepEqual(r.sources.map((s) => s.reference).sort(), ["[P1]", "[P2]", "[P3]", "[P4]", "[P5]"]);
    for (const s of r.sources) assert.equal(s.citee, r.citations.includes(s.reference));
    assert.equal(r.trace.id_question, id);
  });
}
