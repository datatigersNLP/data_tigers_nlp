// Maquette (étape 2 de #111) : même interface que couche.js, sans couche locale ni Ollama. Les réponses viennent des
// traces de la #85 converties au format du contrat (outils/convertir_traces.mjs, dans public/maquette/, versionnées
// avec l'accord de Jibril) ;
// deux cas sans trace réelle, sortie invalide et erreur de préparation, sont simulés à la main et marqués comme tels
// (contrat, section 8).

import { ErreurAppel, VERSION_CONTRAT } from "./couche.js";

const TRACES = ["Q036", "Q003"];
const ATTENTE_MS = 1200; // pour voir l'état d'attente ; les durées réelles sont celles de la trace, affichées à part

export const SIMULEE_INVALIDE = "Exemple simulé : réponse aux références mal formées";
export const SIMULEE_ERREUR = "Exemple simulé : chaîne indisponible pendant la génération";

let chargement = null;

async function chargerTraces() {
  const base = import.meta.env.BASE_URL + "maquette/";
  const reponses = await Promise.all(
    TRACES.map(async (id) => {
      const r = await fetch(`${base}${id}.json`, { cache: "no-store" });
      if (!r.ok) throw new Error(id);
      return r.json();
    }),
  );
  return reponses;
}

const traces = () => (chargement ??= chargerTraces().catch((e) => {
  chargement = null;
  throw e;
}));

// clé de comparaison : la question d'exemple doit être retrouvée même avec des espaces ou une casse différents
const cle = (texte) => texte.normalize("NFC").trim().toLowerCase().replace(/\s+/g, " ");

function simulees(citee) {
  return [
    {
      ...citee,
      question: SIMULEE_INVALIDE,
      statut: "sortie_invalide",
      reponse: "L'employeur doit adapter l'organisation du travail et fournir de l'eau potable fraîche [P1, P5].",
      citations: [],
      citations_invalides: ["[P1, P5]"],
      sources: citee.sources.map((s) => ({ ...s, citee: false })),
      mesures: { duree_totale_s: null, ollama: null },
      trace: { simulee: true },
    },
    {
      version_contrat: VERSION_CONTRAT,
      question: SIMULEE_ERREUR,
      statut: "erreur_preparation",
      reponse: null,
      citations: [],
      citations_invalides: [],
      verifications: { justification_semantique_verifiee: false, couverture_des_affirmations_verifiee: false },
      sources: [],
      modele: null,
      mesures: { duree_totale_s: null, ollama: null },
      erreur: { type: "ErreurGeneration", message: "Ollama /api/tags : connexion refusée (exemple simulé)" },
      trace: { simulee: true },
    },
  ];
}

export async function lireEtat() {
  try {
    await traces();
  } catch {
    throw new ErreurAppel(
      "maquette",
      "Traces de la maquette absentes : lancez « npm run convertir -- <dossier des traces> » (voir demo_b/README.md).",
    );
  }
  return {
    version_contrat: VERSION_CONTRAT,
    pret: true,
    maquette: true,
    occupe: false,
    message: null,
  };
}

export async function questionsExemples() {
  const [citee, abstention] = await traces();
  return [
    { question: citee.question, libelle: "Réponse citée (trace Q036)" },
    { question: abstention.question, libelle: "Abstention (trace Q003)" },
    { question: SIMULEE_INVALIDE, libelle: "Réponse non conforme (simulée)" },
    { question: SIMULEE_ERREUR, libelle: "Chaîne indisponible (simulée)" },
  ];
}

export async function poserQuestion(question) {
  const reponses = await traces();
  const toutes = [...reponses, ...simulees(reponses[0])];
  await new Promise((fin) => setTimeout(fin, ATTENTE_MS));
  const trouvee = toutes.find((r) => cle(r.question) === cle(question));
  if (!trouvee)
    throw new ErreurAppel("maquette", "Maquette : seules les questions d'exemple ont une réponse enregistrée. Choisissez-en une dans le panneau.");
  return structuredClone(trouvee);
}
