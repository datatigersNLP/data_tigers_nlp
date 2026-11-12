// Conversion des traces de la chaîne RAG (sorties de scripts/rag/rag.py --generate, #85) au format de réponse de
// POST /api/question (contrat de la #121, section 5), pour alimenter la maquette sans Ollama (étape 2 de #111).
// Seule la structure change : question, réponse, références, textes et mesures restent ceux de la trace, et ne sont
// jamais présentés comme une nouvelle exécution (contrat, section 5). Le prompt, le gabarit et les réglages ne sont
// pas repris.
//
//   node outils/convertir_traces.mjs <dossier des traces> [dossier de sortie]
//
// Les traces brutes restent hors Git (data/rag/ sur le Legion) ; leur conversion, dans public/maquette/, est versionnée
// avec l'accord de Jibril (02/11/2026), pour que la maquette se lance depuis le dépôt.

import { readFileSync, readdirSync, writeFileSync, mkdirSync } from "node:fs";
import { join, basename, dirname } from "node:path";
import { fileURLToPath } from "node:url";

export const VERSION_CONTRAT = "b1-demo-v1";
const STATUTS = new Set(["reponse_citee", "abstention_modele", "sortie_invalide", "erreur_technique"]);
const CHAMPS_OLLAMA = ["total_duration", "load_duration", "prompt_eval_duration", "eval_duration",
  "prompt_eval_count", "eval_count"];
const CHAMPS_PASSAGE = ["passage_id", "titre_fiche", "section_titre", "chemin", "url", "url_citation", "date_maj", "texte"];

export function convertirTrace(trace, fichier = null) {
  const g = trace.generation;
  if (!g || !STATUTS.has(g.statut)) throw new Error(`${fichier ?? "trace"} : génération absente ou statut inconnu`);
  if (!Array.isArray(trace.resultats) || trace.resultats.length !== 5) throw new Error(`${fichier ?? "trace"} : cinq résultats attendus`);
  const v = g.validation_citations ?? {};
  const citations = v.citations ?? [];
  // la référence [Pk] vient de construire_contexte ; elle est retrouvée par l'identifiant du passage, pas par position
  const references = new Map((trace.contexte?.sources ?? []).map((s) => [s.passage_id, s.reference]));
  const sources = trace.resultats.map((r) => {
    const reference = references.get(r.passage.passage_id);
    if (!reference) throw new Error(`${fichier ?? "trace"} : passage ${r.passage.passage_id} absent du contexte`);
    return {
      reference,
      citee: citations.includes(reference),
      rang: r.rang,
      score: r.score,
      ...Object.fromEntries(CHAMPS_PASSAGE.map((c) => [c, r.passage[c]])),
    };
  });
  const erreurs = g.erreurs_techniques ?? [];
  return {
    version_contrat: VERSION_CONTRAT,
    question: trace.question.question,
    statut: g.statut,
    reponse: typeof g.reponse_brute === "string" ? g.reponse_brute : null,
    citations,
    citations_invalides: v.citations_invalides ?? [],
    verifications: {
      justification_semantique_verifiee: false,
      couverture_des_affirmations_verifiee: false,
    },
    sources,
    modele: g.ollama ? { nom: g.ollama.modele, digest: g.ollama.digest } : null,
    mesures: {
      // durée de la chaîne entière : la trace ne la contient pas, aucune valeur n'est reconstituée
      duree_totale_s: null,
      ollama: g.mesures_ollama ? Object.fromEntries(CHAMPS_OLLAMA.map((c) => [c, g.mesures_ollama[c]])) : null,
    },
    erreur: g.statut === "erreur_technique"
      ? { type: "erreur_technique", message: erreurs.join(", ") || "génération incomplète" }
      : null,
    // hors contrat, propre à la maquette : d'où vient cette réponse, pour ne jamais la présenter comme une exécution
    trace: {
      fichier,
      id_question: trace.question.id,
      ollama: g.ollama?.version ?? null,
    },
  };
}

function principal(args) {
  const [entree, sortie = join(dirname(fileURLToPath(import.meta.url)), "..", "public", "maquette")] = args;
  if (!entree) {
    console.error("Usage : node outils/convertir_traces.mjs <dossier des traces> [dossier de sortie]");
    return 2;
  }
  const fichiers = readdirSync(entree).filter((f) => f.endsWith(".json"));
  if (fichiers.length === 0) {
    console.error(`Aucune trace JSON dans ${entree}`);
    return 1;
  }
  mkdirSync(sortie, { recursive: true });
  for (const f of fichiers) {
    const reponse = convertirTrace(JSON.parse(readFileSync(join(entree, f), "utf-8")), basename(f));
    const cible = join(sortie, `${reponse.trace.id_question}.json`);
    writeFileSync(cible, JSON.stringify(reponse, null, 2) + "\n", "utf-8");
    console.log(`${f} → ${cible} (${reponse.statut}, ${reponse.citations.length} citation(s))`);
  }
  return 0;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) process.exitCode = principal(process.argv.slice(2));
