// Site du volet A : recherche sémantique dans les fiches pratiques, exécutée dans le navigateur (#29, #48).

import Conversation from "./composants/Conversation.jsx";
import { useMoteur } from "./recherche/useMoteur.js";

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
  const moteur = useMoteur();
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
        <Conversation moteur={moteur} />
        <CommentCaMarche />
      </main>
      <PiedDePage />
    </div>
  );
}
