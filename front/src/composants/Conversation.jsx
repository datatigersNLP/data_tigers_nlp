// Conversation de recherche (#48) : la question du visiteur, puis les passages les plus proches, avec l'état du
// chargement du modèle, la recherche en cours et les erreurs.

import { useEffect, useRef, useState } from "react";
import Passage from "./Passage.jsx";
import { messageErreur } from "../recherche/useMoteur.js";

const EXEMPLES = [
  "Combien de jours de congés payés par an ?",
  "Quelle est la durée d'une période d'essai en CDI ?",
  "Mon employeur peut-il refuser une rupture conventionnelle ?",
];
const NB_RESULTATS = 5;

const mo = (octets) => (octets / 2 ** 20).toLocaleString("fr-FR", { maximumFractionDigits: 0 });

function Avatar() {
  return (
    <div className="mt-0.5 hidden h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent-clair text-accent sm:flex">
      <svg viewBox="0 0 20 20" className="h-4 w-4" fill="currentColor" aria-hidden="true">
        <path d="M9 3a6 6 0 104.47 10l3.27 3.27a1 1 0 001.42-1.42L14.9 11.6A6 6 0 009 3zm-4 6a4 4 0 118 0 4 4 0 01-8 0z" />
      </svg>
    </div>
  );
}

function BulleAssistant({ children }) {
  return (
    <div className="flex items-start gap-3">
      <Avatar />
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}

function BulleQuestion({ texte }) {
  return (
    <div className="flex justify-end">
      <p className="max-w-[85%] whitespace-pre-line rounded-2xl rounded-tr-sm bg-accent px-4 py-2.5 text-[15px] leading-relaxed text-white">
        {texte}
      </p>
    </div>
  );
}

function Reponse({ echange }) {
  if (echange.statut === "recherche") {
    return (
      <BulleAssistant>
        <p className="flex items-center gap-2 py-2 text-[15px] text-gris" role="status">
          <span className="h-2 w-2 rounded-full bg-accent motion-safe:animate-pulse" aria-hidden="true" />
          Recherche des passages les plus proches…
        </p>
      </BulleAssistant>
    );
  }
  if (echange.statut === "erreur") {
    return (
      <BulleAssistant>
        <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-[15px] text-red-800">
          La recherche a échoué. Reformulez la question ou réessayez.
        </p>
      </BulleAssistant>
    );
  }
  return (
    <BulleAssistant>
      <p className="text-[15px] leading-relaxed text-encre">
        Voici les {echange.resultats.length} passages des fiches pratiques les plus proches de votre question.
      </p>
      <p className="mt-0.5 text-xs text-gris">
        Classés par proximité de sens, trouvés en {Math.round(echange.duree)} ms. Ils ne constituent pas un conseil
        juridique.
      </p>
      <ol className="mt-3 space-y-3">
        {echange.resultats.map((p) => (
          <li key={p.passage_id}>
            <Passage passage={p} />
          </li>
        ))}
      </ol>
    </BulleAssistant>
  );
}

function BandeauEtat({ moteur }) {
  if (moteur.phase === "pret") return null;
  if (moteur.phase === "erreur") {
    return (
      <div role="alert" className="mb-3 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-800">
        <p>{messageErreur(moteur.erreur)}</p>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={moteur.reessayer}
            className="rounded-lg bg-red-700 px-3 py-1.5 font-medium text-white hover:bg-red-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-700"
          >
            Réessayer
          </button>
          <details className="text-xs text-red-700/80">
            <summary className="cursor-pointer">Détail technique</summary>
            <code className="mt-1 block break-all">{String(moteur.erreur?.message ?? moteur.erreur)}</code>
          </details>
        </div>
      </div>
    );
  }
  const p = moteur.progression;
  const pourcent = p && p.total ? Math.min(100, Math.round((100 * p.charge) / p.total)) : null;
  return (
    <div role="status" className="mb-3 rounded-xl bg-accent-clair px-3 py-2.5 text-sm text-accent">
      <p>
        {pourcent === null
          ? "Préparation de la recherche…"
          : `Téléchargement ${p.quoi} : ${mo(p.charge)} Mo sur ${mo(p.total)} Mo`}
      </p>
      <div
        className="mt-2 h-1.5 overflow-hidden rounded-full bg-white"
        role="progressbar"
        aria-label="Téléchargement du modèle"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={pourcent ?? undefined}
      >
        <div
          className={`h-full rounded-full bg-accent ${pourcent === null ? "w-1/3 motion-safe:animate-pulse" : ""}`}
          style={pourcent === null ? undefined : { width: `${pourcent}%` }}
        />
      </div>
      <p className="mt-1.5 text-xs text-accent/80">
        Une seule fois : le modèle reste ensuite en mémoire dans votre navigateur.
      </p>
    </div>
  );
}

export default function Conversation({ moteur }) {
  const [question, setQuestion] = useState("");
  const [echanges, setEchanges] = useState([]);
  const fin = useRef(null);
  const pret = moteur.phase === "pret";
  const occupe = echanges.some((e) => e.statut === "recherche");

  useEffect(() => {
    if (echanges.length === 0) return;
    const doux = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    fin.current?.scrollIntoView({ behavior: doux ? "smooth" : "auto", block: "nearest" });
  }, [echanges]);

  async function envoyer(texte) {
    const q = texte.trim();
    if (!q || !pret || occupe) return;
    const id = Date.now();
    setQuestion("");
    setEchanges((liste) => [...liste, { id, question: q, statut: "recherche" }]);
    try {
      const { resultats, duree } = await moteur.rechercher(q, NB_RESULTATS);
      setEchanges((liste) => liste.map((e) => (e.id === id ? { ...e, statut: "resultats", resultats, duree } : e)));
    } catch {
      setEchanges((liste) => liste.map((e) => (e.id === id ? { ...e, statut: "erreur" } : e)));
    }
  }

  return (
    <section
      aria-label="Recherche"
      className="flex min-h-[26rem] flex-col overflow-hidden rounded-3xl border border-filet bg-fond/60 shadow-[0_1px_3px_rgba(22,24,29,0.06),0_12px_32px_-12px_rgba(22,24,29,0.12)]"
    >
      <div className="flex-1 space-y-5 p-4 sm:p-6" aria-live="polite">
        <BulleAssistant>
          <p className="max-w-prose rounded-2xl rounded-tl-sm border border-filet bg-white px-4 py-3 text-[15px] leading-relaxed shadow-sm">
            Bonjour. Posez une question sur le droit du travail : je vous montrerai les passages des fiches pratiques
            du ministère qui y répondent, avec le lien vers chaque source.
          </p>
        </BulleAssistant>

        {echanges.length === 0 && (
          <div className="sm:pl-11">
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gris">Exemples de questions</p>
            <ul className="flex flex-wrap gap-2">
              {EXEMPLES.map((q) => (
                <li key={q}>
                  <button
                    type="button"
                    disabled={!pret}
                    onClick={() => envoyer(q)}
                    className="rounded-full border border-filet bg-white px-3 py-1.5 text-left text-sm text-encre hover:border-accent hover:text-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:border-filet disabled:hover:text-encre"
                  >
                    {q}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {echanges.map((e) => (
          <div key={e.id} className="space-y-4">
            <BulleQuestion texte={e.question} />
            <Reponse echange={e} />
          </div>
        ))}
        <div ref={fin} />
      </div>

      <div className="border-t border-filet bg-white p-3 sm:p-4">
        <BandeauEtat moteur={moteur} />
        <form
          className="flex items-end gap-2"
          onSubmit={(ev) => {
            ev.preventDefault();
            envoyer(question);
          }}
        >
          <label htmlFor="question" className="sr-only">
            Votre question
          </label>
          <textarea
            id="question"
            rows={1}
            value={question}
            onChange={(ev) => setQuestion(ev.target.value)}
            onKeyDown={(ev) => {
              // Entrée envoie, Maj + Entrée passe à la ligne
              if (ev.key === "Enter" && !ev.shiftKey) {
                ev.preventDefault();
                envoyer(question);
              }
            }}
            placeholder={pret ? "Posez votre question…" : "Posez votre question (la recherche se prépare)…"}
            className="min-h-11 flex-1 resize-none rounded-xl border border-filet bg-fond px-4 py-2.5 text-[15px] placeholder:text-gris focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20"
          />
          <button
            type="submit"
            disabled={!pret || occupe || !question.trim()}
            aria-label="Rechercher"
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent text-white hover:bg-accent/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-40"
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
