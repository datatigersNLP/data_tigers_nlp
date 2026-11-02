// Mise en forme de la réponse de Qwen (#111) : lignes, listes à puces et références [Pk]. Fonctions sans React, pour
// être testées avec node --test. Une référence n'est rendue cliquable que si elle est une citation valide de la
// réponse (valider_citations de la #85) et qu'elle désigne un passage renvoyé : sinon, elle reste du texte.

const REFERENCE = /(\[P\d+\])/;

// découpe une ligne en morceaux de texte et en références cliquables
export function morceaux(ligne, valides) {
  const resultat = [];
  for (const m of ligne.split(REFERENCE)) {
    if (m === "") continue;
    if (valides.has(m)) resultat.push({ reference: m });
    // une référence non cliquable reste dans la phrase : le texte voisin forme un seul morceau
    else if (resultat.at(-1)?.texte !== undefined) resultat.at(-1).texte += m;
    else resultat.push({ texte: m });
  }
  return resultat;
}

// blocs de la réponse : paragraphes, et listes pour les lignes qui commencent par « - », « * » ou « • »
export function blocs(reponse, valides) {
  const resultat = [];
  for (const brute of (reponse ?? "").split("\n")) {
    const ligne = brute.trim();
    if (!ligne) continue;
    const puce = ligne.match(/^[-*•]\s+(.*)$/);
    if (puce) {
      const dernier = resultat.at(-1);
      const element = morceaux(puce[1], valides);
      if (dernier?.type === "liste") dernier.elements.push(element);
      else resultat.push({ type: "liste", elements: [element] });
    } else {
      resultat.push({ type: "paragraphe", morceaux: morceaux(ligne, valides) });
    }
  }
  return resultat;
}

// références cliquables d'une réponse : citées, valides, et présentes parmi les sources
export function referencesValides(reponse) {
  const presentes = new Set(reponse.sources.map((s) => s.reference));
  return new Set(reponse.citations.filter((c) => presentes.has(c)));
}

// « P1 » pour l'affichage et les lecteurs d'écran
export const numero = (reference) => reference.slice(1, -1);
