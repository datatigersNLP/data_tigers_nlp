// Appels à la couche locale (scripts/rag/serveur_demo.py), selon le contrat de la #121 : GET /api/etat et
// POST /api/question, sur la même origine que l'interface. Le code HTTP est lu avant le corps (contrat, section 6).

export const VERSION_CONTRAT = "b1-demo-v1";
// délai de l'interface : 300 s de génération au plus (generation.py), plus une marge pour la récupération (contrat, §7)
const DELAI_MS = 330_000;

// échec d'un appel, distinct d'une réponse de la chaîne : réseau, délai dépassé, 400, 409 ou réponse inattendue
export class ErreurAppel extends Error {
  constructor(type, message, http = null) {
    super(message);
    this.type = type;
    this.http = http;
  }
}

async function lireJson(reponse) {
  try {
    return await reponse.json();
  } catch {
    return null;
  }
}

export async function lireEtat() {
  let reponse;
  try {
    reponse = await fetch("/api/etat", { cache: "no-store" });
  } catch {
    throw new ErreurAppel("reseau", "La couche locale ne répond pas. Vérifiez qu'elle est lancée sur cet ordinateur.");
  }
  const corps = await lireJson(reponse);
  if (!reponse.ok || corps?.version_contrat !== VERSION_CONTRAT)
    throw new ErreurAppel("http", `État de la chaîne illisible (HTTP ${reponse.status}).`, reponse.status);
  return corps;
}

export async function poserQuestion(question) {
  const arret = new AbortController();
  const minuterie = setTimeout(() => arret.abort(), DELAI_MS);
  let reponse;
  try {
    reponse = await fetch("/api/question", {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({ question }),
      signal: arret.signal,
    });
  } catch {
    // contrat, §6 : sans réponse, rien ne prouve qu'Ollama n'a pas commencé le calcul ; aucune relance automatique
    throw arret.signal.aborted
      ? new ErreurAppel("delai", "Aucune réponse au bout de 5 min 30. Le calcul a peut-être continué sur cet ordinateur : attendez un peu avant de réessayer.")
      : new ErreurAppel("reseau", "La couche locale ne répond pas. Vérifiez qu'elle est lancée sur cet ordinateur.");
  } finally {
    clearTimeout(minuterie);
  }
  const corps = await lireJson(reponse);
  if (reponse.status === 200 && corps?.version_contrat === VERSION_CONTRAT) return corps;
  if (reponse.status === 409)
    throw new ErreurAppel("occupe", "Une autre question est déjà en cours sur cet ordinateur. Réessayez quand elle sera terminée.", 409);
  if (reponse.status === 400)
    throw new ErreurAppel("requete", corps?.erreur?.message ?? "La question n'a pas été acceptée.", 400);
  throw new ErreurAppel("http", `Réponse inattendue de la couche locale (HTTP ${reponse.status}).`, reponse.status);
}
