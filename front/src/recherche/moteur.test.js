// Tests du moteur de recherche (#48), sans dépendance : node --test front/src/recherche/moteur.test.js
// Les tests sur les vrais fichiers lisent data/indexation/ (export du notebook 02, non versionné) ; sans eux, ils
// sont sautés.

import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
import { ABSTENTION, chargerIndex, chargerModele, classer, creerMoteur, horsPerimetre, seuilAbstention, sha256 } from "./moteur.js";

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
  // un autre fichier (l'encodeur ajusté, par exemple), une autre précision ou un autre index : aucun seuil
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

test("site : le modèle élagué de l'en-tête est versionné, conforme à son manifeste, avec sa licence", () => {
  const entete = enteteSite();
  assert.equal(entete.modele.emplacement, "site");
  const dossier = PUBLIC + "modele/" + entete.modele.depot + "/";
  assert.ok(entete.modele.depot.endsWith("-" + entete.modele.sha256.slice(0, 8)), "empreinte dans le nom du dossier");
  const empreinte = (chemin) => createHash("sha256").update(readFileSync(chemin)).digest("hex");
  assert.equal(empreinte(dossier + entete.modele.fichier), entete.modele.sha256);
  const manifeste = JSON.parse(readFileSync(dossier + "manifeste.json", "utf-8"));
  for (const [nom, f] of Object.entries(manifeste.fichiers)) assert.equal(empreinte(dossier + nom), f.sha256, nom);
  assert.equal(manifeste.source.sha256_onnx, entete.modele.origine.sha256);
  assert.equal(manifeste.source.revision, entete.modele.origine.revision);
  const licence = readFileSync(dossier + "LICENSE", "utf-8");
  assert.ok(licence.includes("The MIT License") && licence.includes("Copyright (c) Microsoft Corporation"));
});

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
