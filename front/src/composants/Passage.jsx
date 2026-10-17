// Un passage renvoyé par la recherche : sa fiche, sa place dans la fiche, l'extrait, la date et le lien vers la
// source. Le score n'est pas affiché : il ne s'interprète qu'en relatif, entre les passages d'une même recherche.

import { useState } from "react";

const LONGUEUR_APERCU = 320;

function dateLisible(iso) {
  if (!iso) return null;
  const date = new Date(`${iso}T00:00:00`);
  return Number.isNaN(date.getTime())
    ? null
    : date.toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
}

// fil d'Ariane dans la fiche : section, puis intertitres ; le chapô est l'introduction de la fiche
function cheminDansLaFiche(passage) {
  const section = passage.section_titre === "Chapô" ? "Introduction" : passage.section_titre;
  return [section, ...(passage.chemin ?? [])].filter(Boolean);
}

export default function Passage({ passage }) {
  const [deplie, setDeplie] = useState(false);
  const long = passage.texte.length > LONGUEUR_APERCU;
  const texte = deplie || !long ? passage.texte : passage.texte.slice(0, LONGUEUR_APERCU).trimEnd() + "…";
  const date = dateLisible(passage.date_maj);
  const chemin = cheminDansLaFiche(passage);

  return (
    <article className="rounded-2xl border border-filet bg-white p-4 shadow-sm sm:p-5">
      <header className="flex items-start gap-3">
        <span
          className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent-clair text-xs font-semibold text-accent"
          aria-label={`Résultat ${passage.rang}`}
        >
          {passage.rang}
        </span>
        <div className="min-w-0">
          <h3 className="font-semibold leading-snug text-encre">{passage.titre_fiche}</h3>
          {chemin.length > 0 && (
            <p className="mt-0.5 text-sm leading-snug text-gris">{chemin.join(" › ")}</p>
          )}
        </div>
      </header>

      <p className="mt-3 whitespace-pre-line text-[15px] leading-relaxed text-encre/90">{texte}</p>
      {long && (
        <button
          type="button"
          onClick={() => setDeplie((d) => !d)}
          aria-expanded={deplie}
          className="mt-1 text-sm font-medium text-accent underline-offset-2 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          {deplie ? "Réduire le passage" : "Lire tout le passage"}
        </button>
      )}

      <footer className="mt-4 flex flex-wrap items-center justify-between gap-x-4 gap-y-2 border-t border-filet pt-3 text-sm">
        <span className="text-gris">{date ? `Fiche mise à jour le ${date}` : "Date de mise à jour inconnue"}</span>
        <a
          href={passage.url_citation || passage.url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 font-medium text-accent underline-offset-2 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Voir la source sur travail-emploi.gouv.fr
          <svg viewBox="0 0 20 20" className="h-4 w-4" fill="currentColor" aria-hidden="true">
            <path d="M11 3a1 1 0 100 2h2.59l-6.3 6.3a1 1 0 101.42 1.4L15 6.42V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
            <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
          </svg>
          <span className="sr-only">(nouvel onglet)</span>
        </a>
      </footer>
    </article>
  );
}
