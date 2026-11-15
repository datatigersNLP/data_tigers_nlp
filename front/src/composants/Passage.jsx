// Un passage renvoyé par la recherche, affiché dans sa fiche (Fiche.jsx, A2 de #164) au style de la maquette B (#53) :
// sa place dans la fiche, l'extrait et le lien vers la source, avec son score de similarité, exigé par le sujet pour
// A3. Le titre et la date de mise à jour sont ceux de la fiche, affichés une seule fois au-dessus de ses passages. Le
// score est un cosinus : il ne s'interprète qu'en relatif, entre les passages d'une même recherche, d'où « similarité
// 0,895 » et jamais un pourcentage.

import { useState } from "react";

const LONGUEUR_APERCU = 320;

// fil d'Ariane dans la fiche : section, puis intertitres ; le chapô est l'introduction de la fiche
function cheminDansLaFiche(passage) {
  const section = passage.section_titre === "Chapô" ? "Introduction" : passage.section_titre;
  return [section, ...(passage.chemin ?? [])].filter(Boolean);
}

export default function Passage({ passage }) {
  const [deplie, setDeplie] = useState(false);
  const long = passage.texte.length > LONGUEUR_APERCU;
  const texte = deplie || !long ? passage.texte : passage.texte.slice(0, LONGUEUR_APERCU).trimEnd() + "…";
  const chemin = cheminDansLaFiche(passage);
  // trois décimales : à deux, les premiers passages affichent souvent le même score (0,89 partout)
  const similarite = passage.score.toLocaleString("fr-FR", { minimumFractionDigits: 3, maximumFractionDigits: 3 });

  return (
    <div className="flex flex-col gap-1.5 border-t border-filet pt-3">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5">
        <h4 className="text-[13px] font-semibold leading-snug text-texte2">
          {chemin.length > 0 ? chemin.join(" › ") : "Passage de la fiche"}
        </h4>
        <span className="text-xs font-semibold text-encre">similarité {similarite}</span>
      </div>

      <p className="whitespace-pre-line text-[15px] leading-relaxed text-texte">{texte}</p>

      <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
        <a
          href={passage.url_citation || passage.url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 font-semibold text-accent underline underline-offset-[3px] hover:text-accent-fonce focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Voir dans la fiche
          <svg viewBox="0 0 20 20" className="h-3.5 w-3.5" fill="currentColor" aria-hidden="true">
            <path d="M11 3a1 1 0 100 2h2.59l-6.3 6.3a1 1 0 101.42 1.4L15 6.42V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
            <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
          </svg>
          {/* plusieurs liens au même libellé : la fiche visée est précisée aux lecteurs d'écran */}
          <span className="sr-only"> « {passage.titre_fiche} » sur travail-emploi.gouv.fr (nouvel onglet)</span>
        </a>
        {long && (
          <button
            type="button"
            onClick={() => setDeplie((d) => !d)}
            aria-expanded={deplie}
            className="text-texte2 underline-offset-[3px] hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            {deplie ? "Réduire le passage" : "Lire tout le passage"}
          </button>
        )}
      </div>
    </div>
  );
}
