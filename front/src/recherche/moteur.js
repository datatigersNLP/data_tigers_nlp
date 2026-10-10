// Moteur de recherche du volet A (#48), sans interface : il applique les règles de lecture de l'export du notebook 02
// (docs/etudes/indexation/02_indexation.md, section 6) et reprend le calcul de scripts/indexation/controle_navigateur.html.
//
// Transformers.js n'est pas importé ici : la fonction pipeline est passée en paramètre, pour que le site choisisse
// sa façon de l'importer (paquet npm ou CDN), et pour tester le reste sans le modèle.

export const FORMAT_INDEX = "index-e5-v1";

// empreinte SHA-256 d'un ArrayBuffer, en hexadécimal, comme celles de l'en-tête
export async function sha256(tampon) {
  const condensat = await globalThis.crypto.subtle.digest("SHA-256", tampon);
  return Array.from(new Uint8Array(condensat), (octet) => octet.toString(16).padStart(2, "0")).join("");
}

// Lit l'en-tête, puis la matrice et les passages, et refuse un index incohérent : c'est la garantie qu'un vecteur
// n'est jamais associé au mauvais passage. base : URL du dossier qui contient les trois fichiers, terminée par « / ».
export async function chargerIndex(base, { lire = globalThis.fetch } = {}) {
  const reponse = async (nom) => {
    const r = await lire(base + nom);
    if (!r.ok) throw new Error(`${nom} : réponse ${r.status}`);
    return r;
  };
  const entete = await (await reponse("index_m2.json")).json();
  if (entete.format !== FORMAT_INDEX) throw new Error(`format d'index ${entete.format}, attendu ${FORMAT_INDEX}`);
  const [octets, octetsMeta] = await Promise.all([
    reponse(entete.index.fichier).then((r) => r.arrayBuffer()),
    reponse(entete.metadonnees.fichier).then((r) => r.arrayBuffer()),
  ]);
  const N = entete.index.nb_vecteurs, D = entete.index.dimension;
  if (octets.byteLength !== N * D * 4) throw new Error(`matrice de ${octets.byteLength} octets, attendu ${N * D * 4}`);
  if ((await sha256(octets)) !== entete.index.sha256) throw new Error("empreinte de la matrice différente de l'en-tête");
  if ((await sha256(octetsMeta)) !== entete.metadonnees.sha256)
    throw new Error("empreinte des passages différente de l'en-tête");
  const passages = JSON.parse(new TextDecoder().decode(octetsMeta));
  if (passages.length !== N || passages.length !== entete.metadonnees.nb_passages)
    throw new Error(`${passages.length} passages, attendu ${N}`);
  return { entete, matrice: new Float32Array(octets), passages, N, D };
}

// Charge le modèle à la révision et avec la précision de l'en-tête. Le dtype doit être explicite : par défaut,
// Transformers.js charge q8 en WASM mais fp32 ailleurs. suivre reçoit la progression du téléchargement.
export async function chargerModele(pipeline, entete, { suivre } = {}) {
  return pipeline("feature-extraction", entete.modele.depot, {
    revision: entete.modele.revision, dtype: entete.modele.dtype, device: "wasm", progress_callback: suivre,
  });
}

// Vecteur de la question, avec le préfixe et les options de l'en-tête : sans pooling ni normalisation,
// Transformers.js renverrait un vecteur par token.
export async function encoder(extracteur, entete, question) {
  const sortie = await extracteur(entete.requete.prefixe + question,
    { pooling: entete.requete.pooling, normalize: entete.requete.normalize });
  return sortie.data;
}

// Produit scalaire de q avec chacune des N lignes de la matrice (le cosinus, les vecteurs étant normalisés), puis
// les k meilleurs. Le tri de JavaScript est stable : à score égal, l'ordre de l'index, comme rank_by_score en Python.
export function classer(matrice, N, D, q, k = 5) {
  if (q.length !== D) throw new Error(`vecteur de ${q.length} dimensions, attendu ${D}`);
  const scores = new Float32Array(N);
  for (let n = 0; n < N; n++) {
    let s = 0;
    const o = n * D;
    for (let i = 0; i < D; i++) s += matrice[o + i] * q[i];
    scores[n] = s;
  }
  return Array.from(scores.keys()).sort((a, b) => scores[b] - scores[a]).slice(0, k)
    .map((n) => ({ indice: n, score: scores[n] }));
}

// Moteur complet : index vérifié, modèle chargé, puis rechercher(question, k) renvoie les k meilleurs passages.
export async function creerMoteur(pipeline, base, options = {}) {
  const index = await chargerIndex(base, options);
  const extracteur = await chargerModele(pipeline, index.entete, options);
  return {
    entete: index.entete,
    nbPassages: index.N,
    async rechercher(question, k = 5) {
      const q = await encoder(extracteur, index.entete, question);
      return classer(index.matrice, index.N, index.D, q, k)
        .map(({ indice, score }, rang) => ({ rang: rang + 1, score, ...index.passages[indice] }));
    },
  };
}
