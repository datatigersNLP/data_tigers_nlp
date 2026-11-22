// Tests du moteur de recherche (#48), sans dépendance : node --test front/src/recherche/moteur.test.js
// Les tests sur les vrais fichiers lisent data/indexation/ (export du notebook 02, non versionné) ; sans eux, ils
// sont sautés.

import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
import { ABSTENTION, ABSTENTION_AJUSTE, borneZoneGrise, chargerIndex, chargerModele, classer, creerMoteur, horsPerimetre,
  referenceAbstention, regrouperParFiche, seuilAbstention, servirOrtDepuisLeSite, sha256, zoneGrise } from "./moteur.js";

// racine du dépôt, ou du clone qui contient data/ (variable facultative RACINE_DONNEES)
const RACINE = process.env.RACINE_DONNEES ?? fileURLToPath(new URL("../../../", import.meta.url));
const SITE = RACINE + "data/indexation/site/";
const REFERENCE = RACINE + "data/indexation/controle/resultats_navigateur.json";
const DONNEES = existsSync(SITE + "index_m2.json") && existsSync(REFERENCE);
const sansDonnees = DONNEES ? false : "export du notebook 02 absent de data/indexation/";

// fetch de remplacement : lit les fichiers du dossier, en remplaçant éventuellement certains contenus
function lecteur(dossier, remplacements = {}) {
  return async (url) => {
    const nom = url.slice(url.lastIndexOf("/") + 1);
    const octets = remplacements[nom] ?? readFileSync(dossier + nom);
    const tampon = octets.buffer.slice(octets.byteOffset, octets.byteOffset + octets.byteLength);
    return { ok: true, status: 200, json: async () => JSON.parse(new TextDecoder().decode(tampon)),
      arrayBuffer: async () => tampon };
  };
}

test("classer : produit scalaire, ex aequo dans l'ordre de l'index", () => {
  // lignes (1,0), (0,1), (0,6 ; 0,8), (1,0) ; q = (1,0) : scores 1, 0, 0,6, 1
  const matrice = new Float32Array([1, 0, 0, 1, 0.6, 0.8, 1, 0]);
  const r = classer(matrice, 4, 2, new Float32Array([1, 0]), 3);
  assert.deepEqual(r.map((x) => x.indice), [0, 3, 2]);
  assert.deepEqual(r.map((x) => x.score), [1, 1, Math.fround(0.6)]);
  assert.throws(() => classer(matrice, 4, 2, new Float32Array([1, 0, 0])), /dimensions/);
});

test("sha256 : empreinte connue", async () => {
  // SHA-256 de « abc » (FIPS 180-2, exemple B.1)
  assert.equal(await sha256(new TextEncoder().encode("abc")),
    "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
});

test("chargerIndex : l'export du notebook 02 est accepté", { skip: sansDonnees }, async () => {
  const index = await chargerIndex("site/", { lire: lecteur(SITE) });
  assert.equal(index.N, 4240);
  assert.equal(index.D, 384);
  assert.equal(index.passages.length, 4240);
  assert.equal(index.matrice.length, 4240 * 384);
});

test("chargerIndex : un index incohérent est refusé", { skip: sansDonnees }, async () => {
  const matrice = readFileSync(SITE + "index_m2.f32");
  const altere = Buffer.from(matrice);
  altere[1000] ^= 1;
  await assert.rejects(chargerIndex("site/", { lire: lecteur(SITE, { "index_m2.f32": altere }) }), /empreinte de la matrice/);
  const tronque = matrice.subarray(0, matrice.length - 4);
  await assert.rejects(chargerIndex("site/", { lire: lecteur(SITE, { "index_m2.f32": tronque }) }), /octets/);
  const passages = Buffer.from(readFileSync(SITE + "passages_m2.json"));
  passages[passages.length - 3] ^= 1;
  await assert.rejects(chargerIndex("site/", { lire: lecteur(SITE, { "passages_m2.json": passages }) }), /passages/);
  const entete = JSON.parse(readFileSync(SITE + "index_m2.json", "utf-8"));
  entete.format = "autre";
  await assert.rejects(chargerIndex("site/", { lire: lecteur(SITE, { "index_m2.json": Buffer.from(JSON.stringify(entete)) }) }),
    /format/);
});

test("parité : mêmes 5 premiers passages et mêmes scores que la page de contrôle, sur les 24 requêtes",
  { skip: sansDonnees }, async () => {
    const index = await chargerIndex("site/", { lire: lecteur(SITE) });
    const reference = JSON.parse(readFileSync(REFERENCE, "utf-8"));
    assert.equal(reference.resultats.length, 24);
    for (const r of reference.resultats) {
      const top = classer(index.matrice, index.N, index.D, new Float32Array(r.vecteur), 5);
      assert.deepEqual(top.map((x) => index.passages[x.indice].passage_id), r.top5, r.question);
      assert.deepEqual(top.map((x) => x.score), r.scores5.map(Math.fround), r.question);
    }
  });

test("creerMoteur : préfixe et options de l'en-tête transmis au modèle, résultats complets",
  { skip: sansDonnees }, async () => {
    const reference = JSON.parse(readFileSync(REFERENCE, "utf-8")).resultats[0];
    const appels = [];
    const pipeline = async (tache, depot, options) => {
      appels.push({ tache, depot, options });
      return async (texte, opts) => { appels.push({ texte, opts }); return { data: new Float32Array(reference.vecteur) }; };
    };
    const moteur = await creerMoteur(pipeline, "site/", { lire: lecteur(SITE) });
    const resultats = await moteur.rechercher(reference.question, 5);
    const entete = JSON.parse(readFileSync(SITE + "index_m2.json", "utf-8"));
    assert.equal(appels[0].tache, "feature-extraction");
    assert.equal(appels[0].depot, entete.modele.depot);
    assert.equal(appels[0].options.revision, entete.modele.revision);
    assert.equal(appels[0].options.dtype, entete.modele.dtype);
    assert.equal(appels[1].texte, entete.requete.prefixe + reference.question);
    assert.deepEqual(appels[1].opts, { pooling: entete.requete.pooling, normalize: entete.requete.normalize });
    assert.deepEqual(resultats.map((x) => x.passage_id), reference.top5);
    assert.deepEqual(resultats.map((x) => x.rang), [1, 2, 3, 4, 5]);
    for (const champ of ["titre_fiche", "section_titre", "url_citation", "texte"]) assert.ok(champ in resultats[0], champ);
    assert.equal(moteur.seuilAbstention, ABSTENTION.seuil);
  });

// en-tête et fichiers versionnés du site, ceux que sert GitHub Pages : lus dans ce dépôt, quelle que soit RACINE_DONNEES
const PUBLIC = fileURLToPath(new URL("../../public/", import.meta.url));
const enteteSite = () => JSON.parse(readFileSync(PUBLIC + "index/index_m2.json", "utf-8"));

test("seuilAbstention : le seuil suit l'empreinte du fichier du modèle et celle de l'index, et elles seules", () => {
  const entete = enteteSite();
  assert.equal(seuilAbstention(entete), ABSTENTION.seuil);   // modèle élagué servi par le site
  const variante = (modif) => { const e = structuredClone(entete); modif(e); return seuilAbstention(e); };
  // le q8 de Xenova, d'où vient le modèle élagué : mêmes vecteurs, même seuil
  assert.equal(variante((e) => { e.modele = { ...e.modele.origine, dtype: "q8" }; }), ABSTENTION.seuil);
  // un autre fichier, une autre précision ou un autre index : aucun seuil
  assert.equal(variante((e) => { e.modele.sha256 = "0".repeat(64); }), null);
  assert.equal(variante((e) => { e.modele.dtype = "fp32"; }), null);
  assert.equal(variante((e) => { e.index.sha256 = "0".repeat(64); }), null);
  // le nom du dossier ne compte pas : seul le contenu du fichier fait foi
  assert.equal(variante((e) => { e.modele.depot = "autre-nom"; }), ABSTENTION.seuil);
  assert.equal(seuilAbstention(undefined), null);
});

test("chargerModele : un modèle servi par le site est lu sur le site, sans jamais interroger le Hub", async () => {
  const appels = [];
  const pipeline = async (tache, depot, options) => { appels.push({ tache, depot, options }); return "extracteur"; };
  const entete = enteteSite();
  const env = { allowLocalModels: false, allowRemoteModels: true };
  assert.equal(await chargerModele(pipeline, entete, { env, dossierModeles: "/base/modele/" }), "extracteur");
  // le site est l'hôte distant : Transformers.js lit la taille des fichiers par une requête Range, sans les télécharger
  assert.deepEqual(env, { allowLocalModels: false, allowRemoteModels: true, remoteHost: "/base/modele/",
    remotePathTemplate: "{model}/" });
  assert.equal(appels[0].depot, entete.modele.depot);
  assert.equal(appels[0].options.dtype, "q8");
  assert.ok(!("revision" in appels[0].options));
  await assert.rejects(chargerModele(pipeline, entete, {}), /env et dossierModeles/);
  // en-tête qui désigne le Hub : accès local coupé, révision transmise
  const hub = { modele: { ...entete.modele.origine, dtype: "q8" } };
  await chargerModele(pipeline, hub, { env });
  assert.equal(env.allowLocalModels, false);
  assert.equal(env.allowRemoteModels, true);
  assert.equal(env.remoteHost, "https://huggingface.co/");
  assert.equal(env.remotePathTemplate, "{model}/resolve/{revision}/");
  assert.equal(appels[1].options.revision, entete.modele.origine.revision);
});

// les deux index versionnés : celui de l'encodeur de base (lu par la chaîne du volet B, empreinte dans son verrou) et
// celui de l'encodeur ajusté, servi par le site depuis #164
const enteteAjuste = () => JSON.parse(readFileSync(PUBLIC + "index_ajuste/index_m2.json", "utf-8"));

for (const [nom, lire] of [["de base", enteteSite], ["ajusté", enteteAjuste]])
  test(`site : le modèle élagué ${nom} de l'en-tête est versionné, conforme à son manifeste, avec sa licence`, () =>
    verifierModeleSite(lire()));

function verifierModeleSite(entete) {
  assert.equal(entete.modele.emplacement, "site");
  const dossier = PUBLIC + "modele/" + entete.modele.depot + "/";
  assert.ok(entete.modele.depot.endsWith("-" + entete.modele.sha256.slice(0, 8)), "empreinte dans le nom du dossier");
  const empreinte = (chemin) => createHash("sha256").update(readFileSync(chemin)).digest("hex");
  assert.equal(empreinte(dossier + entete.modele.fichier), entete.modele.sha256);
  const manifeste = JSON.parse(readFileSync(dossier + "manifeste.json", "utf-8"));
  for (const [nom, f] of Object.entries(manifeste.fichiers)) assert.equal(empreinte(dossier + nom), f.sha256, nom);
  assert.equal(manifeste.source.sha256_onnx, entete.modele.origine.sha256);
  // l'ajusté n'a pas de révision du Hub : ni son manifeste ni son en-tête n'en donnent
  assert.equal(manifeste.source.revision ?? null, entete.modele.origine.revision);
  const licence = readFileSync(dossier + "LICENSE", "utf-8");
  assert.ok(licence.includes("The MIT License") && licence.includes("Copyright (c) Microsoft Corporation"));
}

test("site : l'index versionné est accepté tel quel", async () => {
  const index = await chargerIndex("index/", { lire: lecteur(PUBLIC + "index/") });
  assert.equal(index.N, 4240);
  assert.equal(index.entete.index.sha256, ABSTENTION.indexSha256);
});

test("horsPerimetre : strictement sous le seuil, comme le notebook 03", () => {
  const s = ABSTENTION.seuil;
  const de = (score) => [{ score: Math.fround(score) }, { score: Math.fround(score - 0.01) }];
  assert.equal(horsPerimetre(de(0.80), s), true);
  assert.equal(horsPerimetre(de(0.90), s), false);
  assert.equal(horsPerimetre([{ score: s }], s), false); // égalité : la question est conservée
  assert.equal(horsPerimetre([{ score: s - 1e-9 }], s), true);
  assert.equal(horsPerimetre(de(0.10), null), false); // pas de seuil applicable : jamais d'abstention
  assert.equal(horsPerimetre([], s), false);
});

// variantes du CDTN encodées dans le navigateur pour calculer le seuil (scripts/evaluation/cdtn_seuil.py)
const CDTN = RACINE + "data/evaluation/cdtn/vecteurs_cdtn.json";
test("abstention : le classement du site redonne le seuil et ses 24 rejets sur les 479 variantes du CDTN",
  { skip: DONNEES && existsSync(CDTN) ? false : "vecteurs du CDTN ou export du notebook 02 absents" }, async () => {
    const index = await chargerIndex("site/", { lire: lecteur(SITE) });
    const cdtn = JSON.parse(readFileSync(CDTN, "utf-8"));
    // encodées avec le q8 de Xenova, d'où vient le modèle élagué du site
    const origine = enteteSite().modele.origine;
    assert.equal(cdtn.depot, origine.depot);
    assert.equal(cdtn.revision, origine.revision);
    assert.equal(cdtn.dtype, ABSTENTION.dtype);
    assert.equal(cdtn.vecteurs.length, 479);
    const meilleurs = cdtn.vecteurs.map((v) => classer(index.matrice, index.N, index.D, new Float32Array(v), 1));
    // 5e centile par interpolation linéaire, comme numpy.percentile : position 0,05 × (n - 1)
    const tries = meilleurs.map((r) => r[0].score).sort((a, b) => a - b);
    const pos = 0.05 * (tries.length - 1), bas = Math.floor(pos);
    const centile = tries[bas] + (pos - bas) * (tries[bas + 1] - tries[bas]);
    assert.ok(Math.abs(centile - ABSTENTION.seuil) < 1e-6, `centile ${centile}`);
    assert.equal(meilleurs.filter((r) => horsPerimetre(r, ABSTENTION.seuil)).length, 24);
  });

// chemins par défaut de Transformers.js 4.3.0 (src/backends/onnx.js), pour la version d'ONNX Runtime Web qu'il épingle
const CDN = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.31.0-dev.20260914-8d85527a0/dist/";
const FICHIERS_SITE = {
  "ort-wasm-simd-threaded.mjs": "/data_tigers_nlp/assets/ort-wasm-simd-threaded-a.mjs",
  "ort-wasm-simd-threaded.wasm": "/data_tigers_nlp/assets/ort-wasm-simd-threaded-b.wasm",
  "ort-wasm-simd-threaded.asyncify.mjs": "/data_tigers_nlp/assets/ort-wasm-simd-threaded.asyncify-c.mjs",
  "ort-wasm-simd-threaded.asyncify.wasm": "/data_tigers_nlp/assets/ort-wasm-simd-threaded.asyncify-d.wasm",
};
const envAvec = (wasmPaths) => ({ backends: { onnx: { wasm: { wasmPaths } } } });

test("servirOrtDepuisLeSite : la variante choisie par Transformers.js est gardée, seul l'hôte change", () => {
  const asyncify = envAvec({ mjs: CDN + "ort-wasm-simd-threaded.asyncify.mjs", wasm: CDN + "ort-wasm-simd-threaded.asyncify.wasm" });
  assert.equal(servirOrtDepuisLeSite(asyncify, FICHIERS_SITE), true);
  assert.deepEqual(asyncify.backends.onnx.wasm.wasmPaths, {
    mjs: FICHIERS_SITE["ort-wasm-simd-threaded.asyncify.mjs"], wasm: FICHIERS_SITE["ort-wasm-simd-threaded.asyncify.wasm"] });
  // Safari avant la version 26, sans WebGPU : variante classique
  const classique = envAvec({ mjs: CDN + "ort-wasm-simd-threaded.mjs", wasm: CDN + "ort-wasm-simd-threaded.wasm" });
  assert.equal(servirOrtDepuisLeSite(classique, FICHIERS_SITE), true);
  assert.deepEqual(classique.backends.onnx.wasm.wasmPaths, {
    mjs: FICHIERS_SITE["ort-wasm-simd-threaded.mjs"], wasm: FICHIERS_SITE["ort-wasm-simd-threaded.wasm"] });
});

test("servirOrtDepuisLeSite : des chemins inattendus ne sont pas modifiés", () => {
  const inconnu = envAvec({ mjs: CDN + "ort-wasm-simd-threaded.jsep.mjs", wasm: CDN + "ort-wasm-simd-threaded.jsep.wasm" });
  assert.equal(servirOrtDepuisLeSite(inconnu, FICHIERS_SITE), false);
  assert.equal(inconnu.backends.onnx.wasm.wasmPaths.mjs, CDN + "ort-wasm-simd-threaded.jsep.mjs");
  const prefixe = envAvec(CDN);
  assert.equal(servirOrtDepuisLeSite(prefixe, FICHIERS_SITE), false);
  assert.equal(prefixe.backends.onnx.wasm.wasmPaths, CDN);
  assert.equal(servirOrtDepuisLeSite({}, FICHIERS_SITE), false);
});

// la version installée doit être celle qu'épingle Transformers.js : sinon le site servirait un autre moteur que celui
// pour lequel la bibliothèque a été écrite. Le site l'importe directement (useMoteur.js) et la déclare donc dans
// package.json, à la même version : une mise à jour de Transformers.js sans elle installerait deux versions
const MODULES = fileURLToPath(new URL("../../node_modules/", import.meta.url));
const sansModules = existsSync(MODULES + "onnxruntime-web/package.json") ? false : "dépendances npm non installées";
test("site : la version d'ONNX Runtime Web servie est celle qu'épingle Transformers.js", { skip: sansModules }, () => {
  const ort = JSON.parse(readFileSync(MODULES + "onnxruntime-web/package.json", "utf8"));
  const tjs = JSON.parse(readFileSync(MODULES + "@huggingface/transformers/package.json", "utf8"));
  assert.equal(ort.version, tjs.dependencies["onnxruntime-web"]);
  const site = JSON.parse(readFileSync(new URL("../../package.json", import.meta.url), "utf8"));
  assert.equal(site.dependencies["onnxruntime-web"], tjs.dependencies["onnxruntime-web"]);
  assert.ok(CDN.includes("@" + ort.version + "/"));
  for (const nom of Object.keys(FICHIERS_SITE)) assert.ok(existsSync(MODULES + "onnxruntime-web/dist/" + nom), nom);
});

// --- encodeur ajusté servi depuis #164 : seuil recalculé, zone grise (A3), regroupement par fiche (A2) ---

test("site : le moteur charge l'index de l'encodeur ajusté, auquel s'appliquent un seuil et une zone grise", () => {
  // sans seuil applicable, le site n'écarterait plus aucune question, sans erreur visible : d'où ce contrôle
  const source = readFileSync(new URL("./useMoteur.js", import.meta.url), "utf8");
  assert.match(source, /const DOSSIER_INDEX = import\.meta\.env\.BASE_URL \+ "index_ajuste\/";/);
  const entete = enteteAjuste();
  assert.equal(referenceAbstention(entete), ABSTENTION_AJUSTE);
  assert.equal(seuilAbstention(entete), ABSTENTION_AJUSTE.seuil);
  assert.equal(borneZoneGrise(entete), ABSTENTION_AJUSTE.zoneGrise);
  assert.ok(ABSTENTION_AJUSTE.seuil < ABSTENTION_AJUSTE.zoneGrise);
  // l'index de base garde son seuil, sans zone grise
  assert.equal(referenceAbstention(enteteSite()), ABSTENTION);
  assert.equal(borneZoneGrise(enteteSite()), null);
  const variante = (modif) => { const e = structuredClone(entete); modif(e); return referenceAbstention(e); };
  // le q8 ajusté non élagué : mêmes vecteurs, 822 sur 822 dans le navigateur, même référence
  assert.equal(variante((e) => { e.modele = { ...e.modele, sha256: e.modele.origine.sha256 }; }), ABSTENTION_AJUSTE);
  // croisements interdits : modèle ajusté avec l'index de base, modèle de base avec l'index ajusté
  assert.equal(variante((e) => { e.index.sha256 = ABSTENTION.indexSha256; }), null);
  assert.equal(variante((e) => { e.modele.sha256 = ABSTENTION.modeles[1]; }), null);
  assert.equal(variante((e) => { e.modele.dtype = "fp32"; }), null);
});

test("site : l'index ajusté versionné est accepté tel quel, avec les mêmes passages que l'index de base", async () => {
  const index = await chargerIndex("index_ajuste/", { lire: lecteur(PUBLIC + "index_ajuste/") });
  assert.equal(index.N, 4240);
  assert.equal(index.D, 384);
  assert.equal(index.entete.index.sha256, ABSTENTION_AJUSTE.indexSha256);
  // les passages sont une copie octet pour octet : seuls les vecteurs changent
  assert.ok(readFileSync(PUBLIC + "index_ajuste/passages_m2.json").equals(readFileSync(PUBLIC + "index/passages_m2.json")));
  assert.notEqual(index.entete.index.sha256, enteteSite().index.sha256);
});

test("zoneGrise : au-dessus du seuil et strictement sous la borne, jamais sans borne", () => {
  const { seuil: s, zoneGrise: b } = ABSTENTION_AJUSTE;
  const premier = (score) => [{ score }, { score: score - 0.01 }];
  assert.equal(zoneGrise(premier(b - 1e-6), s, b), true);
  assert.equal(zoneGrise(premier(s), s, b), true);           // égalité au seuil : conservée, donc en zone grise
  assert.equal(zoneGrise(premier(b), s, b), false);          // égalité à la borne : hors de la zone grise
  assert.equal(zoneGrise(premier(s - 1e-6), s, b), false);   // sous le seuil : hors périmètre, pas zone grise
  assert.equal(zoneGrise(premier(0.99), s, b), false);
  assert.equal(zoneGrise(premier(0.1), s, null), false);     // encodeur de base : pas de zone grise
  assert.equal(zoneGrise([], s, b), false);
  // sans seuil mais avec une borne (cas que ABSTENTIONS ne produit pas) : seule la borne compte
  assert.equal(zoneGrise(premier(b - 0.01), null, b), true);
});

test("regrouperParFiche : une fiche par adresse, dans l'ordre du meilleur passage, sans perte ni réordonnancement", () => {
  const p = (id, url, score) => ({ passage_id: id, url, titre_fiche: "T " + url, score, rang: 0 });
  const resultats = [p("a1", "u/a", 0.9), p("b1", "u/b", 0.85), p("a2", "u/a/", 0.8), p("c1", "u/c", 0.7), p("b2", "u/b", 0.6)]
    .map((x, i) => ({ ...x, rang: i + 1 }));
  const fiches = regrouperParFiche(resultats);
  assert.deepEqual(fiches.map((f) => f.rang), [1, 2, 3]);
  assert.deepEqual(fiches.map((f) => f.url), ["u/a", "u/b", "u/c"]);
  assert.deepEqual(fiches.map((f) => f.passages.map((x) => x.passage_id)), [["a1", "a2"], ["b1", "b2"], ["c1"]]);
  // la barre oblique finale ne sépare pas deux fiches ; chaque passage garde son rang d'origine
  assert.deepEqual(fiches[0].passages.map((x) => x.rang), [1, 3]);
  assert.equal(fiches.flatMap((f) => f.passages).length, resultats.length);
  assert.deepEqual(regrouperParFiche([]), []);
});

test("regrouperParFiche : sur le corpus, une adresse vaut une fiche et un titre", () => {
  const passages = JSON.parse(readFileSync(PUBLIC + "index_ajuste/passages_m2.json", "utf-8"));
  const fiches = regrouperParFiche(passages);
  assert.equal(fiches.length, 261);
  assert.equal(new Set(fiches.map((f) => f.titre_fiche)).size, 261);
  for (const f of fiches) {
    assert.ok(f.passages.every((x) => x.titre_fiche === f.titre_fiche), f.url);
    // une seule date par fiche : Fiche.jsx l'affiche une fois, sous le titre
    assert.equal(new Set(f.passages.map((x) => x.date_maj)).size, 1, f.url);
  }
});

// variantes du CDTN encodées dans le navigateur par l'encodeur ajusté (scripts/evaluation/encoder_navigateur.py)
const CDTN_AJUSTE = RACINE + "data/adaptation/navigateur/vecteurs/vecteurs_cdtn_ajuste.json";
const FICHIERS_SEUIL_AJUSTE = ["seuil_cdtn_ajuste.json", "zone_grise_ajuste.json"].map((n) => RACINE + "data/evaluation/notebook03/" + n);
test("abstention ajustée : le classement du site redonne le seuil, la borne, 24 rejets et 96 questions en zone grise",
  { skip: existsSync(CDTN_AJUSTE) && FICHIERS_SEUIL_AJUSTE.every(existsSync) ? false : "vecteurs ou seuils de l'ajusté absents" },
  async () => {
    const index = await chargerIndex("index_ajuste/", { lire: lecteur(PUBLIC + "index_ajuste/") });
    const cdtn = JSON.parse(readFileSync(CDTN_AJUSTE, "utf-8"));
    assert.equal(cdtn.sha256_q8, enteteAjuste().modele.origine.sha256);
    assert.equal(cdtn.dtype, ABSTENTION_AJUSTE.dtype);
    assert.equal(cdtn.vecteurs.length, 479);
    const [seuil, zone] = FICHIERS_SEUIL_AJUSTE.map((f) => JSON.parse(readFileSync(f, "utf-8")));
    assert.equal(seuil.empreinte_questions, cdtn.empreinte_questions);
    assert.equal(zone.empreinte_questions, cdtn.empreinte_questions);
    assert.equal(seuil.seuil, ABSTENTION_AJUSTE.seuil);
    assert.equal(zone.seuil, ABSTENTION_AJUSTE.seuil);
    assert.equal(zone.borne_haute, ABSTENTION_AJUSTE.zoneGrise);
    const meilleurs = cdtn.vecteurs.map((v) => classer(index.matrice, index.N, index.D, new Float32Array(v), 1));
    // centiles par interpolation linéaire, comme numpy.percentile : position c × (n - 1)
    const tries = meilleurs.map((r) => r[0].score).sort((a, b) => a - b);
    const centile = (c) => { const pos = c * (tries.length - 1), bas = Math.floor(pos);
      return tries[bas] + (pos - bas) * (tries[bas + 1] - tries[bas]); };
    assert.ok(Math.abs(centile(0.05) - ABSTENTION_AJUSTE.seuil) < 1e-6, `5e centile ${centile(0.05)}`);
    assert.ok(Math.abs(centile(0.25) - ABSTENTION_AJUSTE.zoneGrise) < 1e-6, `25e centile ${centile(0.25)}`);
    const { seuil: s, zoneGrise: b } = ABSTENTION_AJUSTE;
    assert.equal(meilleurs.filter((r) => horsPerimetre(r, s)).length, 24);
    assert.equal(meilleurs.filter((r) => zoneGrise(r, s, b)).length, 96);
  });
