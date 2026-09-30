// Page de préfiguration du volet A (ticket #29) : elle valide la mise en ligne à l'URL définitive.
// La recherche sémantique sera branchée ensuite, sur l'index produit par le notebook 02.

const EXEMPLES = [
  "Combien de jours de congés payés par an ?",
  "Quelle est la durée d'une période d'essai en CDI ?",
  "Mon employeur peut-il refuser une rupture conventionnelle ?",
];

const ETAPES = [
  {
    titre: "Votre question reste chez vous",
    texte: "Le modèle de langage s'exécute dans votre navigateur. Aucune question n'est envoyée à un serveur.",
  },
  {
    titre: "Une recherche par le sens",
    texte: "La question est comparée aux passages des fiches pratiques, même si elle n'emploie pas les mêmes mots.",
  },
  {
    titre: "Des réponses sourcées",
    texte: "Chaque résultat indique la fiche et la section d'origine, avec un lien vers le passage exact.",
  },
];

function Logo() {
  return (
    <svg viewBox="0 0 32 32" className="h-8 w-8 shrink-0" aria-hidden="true">
      <rect width="32" height="32" rx="7" className="fill-accent" />
      <circle cx="14" cy="14" r="6.5" fill="none" stroke="#fff" strokeWidth="2.6" />
      <path d="M19 19l6 6" stroke="#fff" strokeWidth="2.6" strokeLinecap="round" />
    </svg>
  );
}

function EnTete() {
  return (
    <header className="border-b border-filet bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <div className="flex items-center gap-3">
          <Logo />
          <div className="leading-tight">
            <p className="text-[15px] font-semibold text-encre">Recherche droit du travail</p>
            <p className="text-xs text-gris">Équipe Data Tigers · M2 Data &amp; IA</p>
          </div>
        </div>
        <span className="shrink-0 rounded-full border border-accent2/30 bg-accent2/5 px-3 py-1 text-xs font-medium text-accent2">
          <span className="hidden sm:inline">Projet étudiant, non officiel</span>
          <span className="sm:hidden">Non officiel</span>
        </span>
      </div>
    </header>
  );
}

function BulleAssistant({ children }) {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent-clair text-accent">
        <svg viewBox="0 0 20 20" className="h-4 w-4" fill="currentColor" aria-hidden="true">
          <path d="M9 3a6 6 0 104.47 10l3.27 3.27a1 1 0 001.42-1.42L14.9 11.6A6 6 0 009 3zm-4 6a4 4 0 118 0 4 4 0 01-8 0z" />
        </svg>
      </div>
      <div className="max-w-prose rounded-2xl rounded-tl-sm border border-filet bg-white px-4 py-3 text-[15px] leading-relaxed shadow-sm">
        {children}
      </div>
    </div>
  );
}

function Conversation() {
  return (
    <section
      aria-label="Recherche"
      className="flex min-h-[26rem] flex-col overflow-hidden rounded-3xl border border-filet bg-fond/60 shadow-[0_1px_3px_rgba(22,24,29,0.06),0_12px_32px_-12px_rgba(22,24,29,0.12)]"
    >
      <div className="flex-1 space-y-5 p-4 sm:p-6">
        <BulleAssistant>
          <p>
            Bonjour. Posez une question sur le droit du travail : je vous montrerai les passages des fiches pratiques
            du ministère qui y répondent, avec le lien vers chaque source.
          </p>
        </BulleAssistant>

        <div className="pl-11">
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gris">Exemples de questions</p>
          <ul className="flex flex-wrap gap-2">
            {EXEMPLES.map((q) => (
              <li key={q}>
                <button
                  type="button"
                  disabled
                  className="cursor-not-allowed rounded-full border border-filet bg-white px-3 py-1.5 text-left text-sm text-encre/70"
                >
                  {q}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="border-t border-filet bg-white p-3 sm:p-4">
        <div
          role="status"
          className="mb-3 flex items-center gap-2 rounded-xl bg-accent-clair px-3 py-2 text-sm text-accent"
        >
          <span className="relative flex h-2 w-2" aria-hidden="true">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-accent" />
          </span>
          La recherche est en cours d'intégration et sera disponible prochainement.
        </div>
        <form className="flex items-end gap-2" onSubmit={(e) => e.preventDefault()}>
          <label htmlFor="question" className="sr-only">
            Votre question
          </label>
          <textarea
            id="question"
            rows={1}
            disabled
            placeholder="Posez votre question…"
            className="min-h-11 flex-1 resize-none rounded-xl border border-filet bg-fond px-4 py-2.5 text-[15px] placeholder:text-gris disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled
            aria-label="Rechercher"
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent text-white opacity-40 disabled:cursor-not-allowed"
          >
            <svg viewBox="0 0 20 20" className="h-5 w-5" fill="currentColor" aria-hidden="true">
              <path d="M3.4 16.6l14.2-6.1a.55.55 0 000-1L3.4 3.4a.55.55 0 00-.77.62L4.1 9.2l7.4.8-7.4.8-1.47 5.18a.55.55 0 00.77.62z" />
            </svg>
          </button>
        </form>
      </div>
    </section>
  );
}

function CommentCaMarche() {
  return (
    <section aria-labelledby="fonctionnement" className="mt-14">
      <h2 id="fonctionnement" className="text-sm font-semibold uppercase tracking-wide text-accent2">
        Comment ça marche
      </h2>
      <ol className="mt-4 grid gap-4 sm:grid-cols-3">
        {ETAPES.map((e, i) => (
          <li key={e.titre} className="rounded-2xl border border-filet bg-white p-5">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-accent text-sm font-semibold text-white">
              {i + 1}
            </span>
            <h3 className="mt-3 font-semibold text-encre">{e.titre}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-gris">{e.texte}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}

function PiedDePage() {
  return (
    <footer className="mt-16 border-t border-filet bg-white">
      <div className="mx-auto max-w-5xl space-y-2 px-4 py-6 text-xs leading-relaxed text-gris sm:px-6">
        <p>
          Source : fiches pratiques du site{" "}
          <a
            href="https://travail-emploi.gouv.fr"
            className="font-medium text-accent underline-offset-2 hover:underline"
            target="_blank"
            rel="noreferrer"
          >
            travail-emploi.gouv.fr
          </a>
          , via le jeu de données public AgentPublic/travail-emploi.
        </p>
        <p>
          Ce site est un projet étudiant (NLP 2, M2 Data &amp; IA, FGES). Il n'est pas un service officiel et ne
          remplace pas un conseil juridique.
        </p>
        <p className="font-mono text-[11px] text-gris/80">
          version {__VERSION__} · construite le {__DATE_CONSTRUCTION__}
        </p>
      </div>
    </footer>
  );
}

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <EnTete />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 pt-10 sm:px-6 sm:pt-14">
        <div className="mb-8 max-w-2xl">
          <h1 className="text-3xl font-semibold tracking-tight text-encre sm:text-4xl">
            Trouvez la bonne fiche, au bon passage.
          </h1>
          <p className="mt-3 text-base leading-relaxed text-gris sm:text-lg">
            Une recherche sémantique dans les fiches pratiques du droit du travail, exécutée entièrement dans votre
            navigateur.
          </p>
        </div>
        <Conversation />
        <CommentCaMarche />
      </main>
      <PiedDePage />
    </div>
  );
}
