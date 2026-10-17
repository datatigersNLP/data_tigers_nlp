// Panneau latéral de la maquette B (#53) : nouveau chat, chats de la session, exemples, confidentialité. Colonne fixe
// sur ordinateur ; sur téléphone, menu ouvert par-dessus la conversation, fermé par Échap ou par un toucher à côté.

import { useEffect, useRef } from "react";

export function Logo({ className = "h-[30px] w-[30px]" }) {
  return (
    <svg viewBox="0 0 32 32" className={`${className} shrink-0`} aria-hidden="true">
      <rect width="32" height="32" rx="9" className="fill-accent" />
      <path d="M10 11h12M10 16h12M10 21h7" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  );
}

const titreRubrique = "mb-2 px-1.5 text-xs font-semibold uppercase tracking-wide text-gris";
const elementListe =
  "w-full rounded-[9px] px-2.5 py-[9px] text-left text-sm focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-accent";

export default function Barre({ ouvert, fermer, chats, actuel, choisir, nouveauChat, exemples, utiliserExemple, occupe }) {
  const premier = useRef(null);
  // chats de la session qui ont au moins une question, le plus récent en haut ; titre : leur première question
  const session = chats.filter((c) => c.echanges.length > 0).reverse();

  // à l'ouverture du menu sur téléphone, le focus y entre : un visiteur au clavier n'a pas à le chercher
  useEffect(() => {
    if (ouvert) premier.current?.focus();
  }, [ouvert]);

  return (
    <>
      {ouvert && <div className="fixed inset-0 z-30 bg-encre/40 md:hidden" onClick={fermer} aria-hidden="true" />}
      <aside
        id="menu-lateral"
        aria-label="Menu"
        onKeyDown={(ev) => ev.key === "Escape" && ouvert && fermer()}
        className={`${ouvert ? "flex" : "hidden"} fixed inset-y-0 left-0 z-40 w-[280px] max-w-[85vw] flex-col gap-5 overflow-y-auto border-r border-filet bg-panneau p-4 md:static md:z-auto md:flex md:w-[280px] md:max-w-none md:shrink-0`}
      >
        <div className="flex items-center gap-2.5 px-1 pt-1">
          <Logo />
          <span className="flex-1 text-[15px] font-bold">Code du travail, en clair</span>
          <button
            type="button"
            onClick={fermer}
            aria-label="Fermer le menu"
            className="flex h-11 w-11 items-center justify-center rounded-[10px] text-encre focus-visible:outline-2 focus-visible:outline-accent md:hidden"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>

        <button
          ref={premier}
          type="button"
          onClick={nouveauChat}
          className="flex min-h-11 items-center justify-center gap-2 rounded-xl border border-bordure bg-white text-sm font-semibold text-encre hover:border-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" aria-hidden="true">
            <path d="M12 5v14M5 12h14" />
          </svg>
          Nouveau chat
        </button>

        {session.length > 0 && (
          <nav aria-labelledby="titre-session">
            <h2 id="titre-session" className={titreRubrique}>
              Cette session
            </h2>
            <ul className="flex flex-col gap-0.5">
              {session.map((c) => (
                <li key={c.id}>
                  <button
                    type="button"
                    onClick={() => choisir(c.id)}
                    aria-current={c.id === actuel ? "true" : undefined}
                    className={`${elementListe} line-clamp-2 ${c.id === actuel ? "bg-actif font-medium text-encre" : "text-texte2 hover:bg-actif/60"}`}
                  >
                    {c.echanges[0].question}
                  </button>
                </li>
              ))}
            </ul>
          </nav>
        )}

        <div>
          <h2 className={titreRubrique}>Exemples</h2>
          <ul className="flex flex-col gap-0.5">
            {exemples.map((q) => (
              <li key={q}>
                <button
                  type="button"
                  disabled={occupe}
                  onClick={() => utiliserExemple(q)}
                  className={`${elementListe} text-texte2 hover:bg-actif/60 disabled:cursor-not-allowed disabled:text-[#6b665f] disabled:hover:bg-transparent`}
                >
                  {q}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-auto space-y-3">
          <p className="flex gap-2.5 rounded-xl bg-accent-clair p-3 text-[13px] leading-normal text-accent-texte">
            <svg viewBox="0 0 24 24" className="mt-px h-[18px] w-[18px] shrink-0" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="5" y="11" width="14" height="10" rx="2" />
              <path d="M8 11V8a4 4 0 018 0v3" />
            </svg>
            {/* revue de #42 : un encodeur ne génère rien ; il analyse la question, dans le navigateur */}
            Vos questions restent dans votre navigateur : le modèle qui les analyse s'y exécute, aucune n'est envoyée à
            un serveur.
          </p>
          <p className="px-1 font-mono text-[11px] text-gris">
            version {__VERSION__} · construite le {__DATE_CONSTRUCTION__}
          </p>
        </div>
      </aside>
    </>
  );
}
