// Un passage renvoyé par la recherche : sa fiche, sa place dans la fiche, l'extrait, la date et le lien vers la
// source, avec son score de similarité, exigé par le sujet pour A3 (#53). Le score est un cosinus : il ne s'interprète
// qu'en relatif, entre les passages d'une même recherche, d'où « similarité 0,89 » et jamais un pourcentage.

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
  // trois décimales : à deux, les cinq premiers passages affichent souvent le même score (0,89 partout)
  const similarite = passage.score.toLocaleString("fr-FR", { minimumFractionDigits: 3, maximumFractionDigits: 3 });

  return (
    <article className="rounded-2xl border border-filet bg-white p-4 shadow-sm sm:p-5">
      <header className="flex items-start gap-3">
        {/* un aria-label sur un span sans rôle est ignoré : le rang est lu dans le titre, la pastille est décorative */}
        <span
          className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent-clair text-xs font-semibold text-accent"
          aria-hidden="true"
        >
          {passage.rang}
        </span>
        <div className="min-w-0">
          <h3 className="font-semibold leading-snug text-encre">
            <span className="sr-only">Résultat {passage.rang} : </span>
            {passage.titre_fiche}
          </h3>
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
        <span className="text-gris">
          <span className="font-medium text-encre">similarité {similarite}</span>
          {" · "}
          {date ? `fiche mise à jour le ${date}` : "date de mise à jour inconnue"}
        </span>
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
          {/* cinq liens au même libellé : la fiche visée est précisée aux lecteurs d'écran */}
          <span className="sr-only"> : fiche « {passage.titre_fiche} » (nouvel onglet)</span>
        </a>
      </footer>
    </article>
  );
}
