// Tests de la mise en forme des réponses (citations.js) : node --test, depuis demo_b/.

import { test } from "node:test";
import assert from "node:assert/strict";
import { blocs, morceaux, numero, referencesValides } from "./citations.js";

const valides = new Set(["[P1]", "[P5]"]);

test("une référence valide devient cliquable, les autres restent du texte", () => {
  assert.deepEqual(morceaux("Mesures [P1][P5] et [P3].", valides), [
    { texte: "Mesures " },
    { reference: "[P1]" },
    { reference: "[P5]" },
    { texte: " et [P3]." },
  ]);
});

test("une référence mal formée n'est jamais cliquable", () => {
  assert.deepEqual(morceaux("Eau fraîche [P1, P5].", valides), [{ texte: "Eau fraîche [P1, P5]." }]);
});

test("les lignes à puces consécutives forment une seule liste", () => {
  const b = blocs("Les obligations [P1] :\n\n- première ;\n- seconde [P5].\nFin.", valides);
  assert.equal(b.length, 3);
  assert.equal(b[0].type, "paragraphe");
  assert.equal(b[1].type, "liste");
  assert.equal(b[1].elements.length, 2);
  assert.deepEqual(b[1].elements[1].at(-2), { reference: "[P5]" });
  assert.equal(b[2].type, "paragraphe");
});

test("une réponse absente donne zéro bloc", () => {
  assert.deepEqual(blocs(null, valides), []);
});

test("seules les citations présentes parmi les sources sont valides", () => {
  const reponse = { citations: ["[P1]", "[P9]"], sources: [{ reference: "[P1]" }, { reference: "[P2]" }] };
  assert.deepEqual([...referencesValides(reponse)], ["[P1]"]);
});

test("numéro affiché d'une référence", () => {
  assert.equal(numero("[P3]"), "P3");
});
