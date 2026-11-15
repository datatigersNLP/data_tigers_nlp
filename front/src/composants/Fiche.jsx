// Une fiche du ministère et ses passages retenus par la recherche (A2, #164) : les passages renvoyés sont regroupés
// par fiche (moteur.js, regrouperParFiche), dans l'ordre du meilleur passage de chaque fiche, puis dans l'ordre des
// scores à l'intérieur de la fiche. La date de mise à jour est celle de la fiche : vérifié le 15/11/2026 sur
// front/public/index_ajuste/passages_m2.json, aucune des 261 fiches n'a deux dates.

import Passage from "./Passage.jsx";

function dateCourte(iso) {
  if (!iso) return null;
  const date = new Date(`${iso}T00:00:00`);
  return Number.isNaN(date.getTime()) ? null : date.toLocaleDateString("fr-FR");
}

export default function Fiche({ fiche }) {
  const date = dateCourte(fiche.passages[0]?.date_maj);
  const n = fiche.passages.length;
  return (
    <article className="flex flex-col gap-3 rounded-[14px] border border-filet bg-white px-4 py-3.5">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5">
        <h3 className="text-[15px] font-bold leading-snug">
          {/* le rang visible est décoratif : il est lu dans la phrase réservée aux lecteurs d'écran */}
          <span className="text-accent" aria-hidden="true">
            {fiche.rang}.{" "}
          </span>
          <span className="sr-only">Fiche {fiche.rang} : </span>
          {fiche.titre_fiche}
        </h3>
        <span className="text-xs text-gris">
          {n} {n > 1 ? "passages" : "passage"}
          {date && (
            <>
              {" · "}
              <span aria-hidden="true">maj {date}</span>
              <span className="sr-only">fiche mise à jour le {date}</span>
            </>
          )}
        </span>
      </div>
      <ol className="flex flex-col gap-3">
        {fiche.passages.map((p) => (
          <li key={p.passage_id}>
            <Passage passage={p} />
          </li>
        ))}
      </ol>
    </article>
  );
}
