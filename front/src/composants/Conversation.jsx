// Conversation de recherche (#48) : la question du visiteur, puis les passages les plus proches, avec l'état du
// chargement du modèle, la recherche en cours et les erreurs. Depuis #53 : une question posée pendant le chargement est
// gardée et envoyée dès que le moteur est prêt, et une question hors du périmètre (seuil d'abstention, #76) est
// signalée, ses passages restant consultables.

import { useEffect, useRef, useState } from "react";
import Passage from "./Passage.jsx";
import { messageErreur } from "../recherche/useMoteur.js";

// revue de #42 : formulée avec « CDI », la question sur la période d'essai ne gardait la bonne fiche en tête qu'avec
// 0,0002 d'avance (notebook 02, section 11) ; sans le sigle, l'avance est de 0,022
const EXEMPLES = [
  "Combien de jours de congés payés par an ?",
  "Quelle est la durée maximale de la période d'essai ?",
  "Mon employeur peut-il refuser une rupture conventionnelle ?",
];
const NB_RESULTATS = 5;
// premier chargement : modèle q8 (113 Mio) et vocabulaire du tokeniseur (16 Mio) ; 52 à 56 s mesurés à la PR #71
const POIDS_PREMIER_CHARGEMENT = "130 Mo";

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

function Reponse({ echange, basculer }) {
  if (echange.statut === "attente") {
    return (
      <BulleAssistant>
        <p className="flex items-center gap-2 py-2 text-[15px] text-gris">
          <span className="h-2 w-2 rounded-full bg-accent motion-safe:animate-pulse" aria-hidden="true" />
          Votre question est gardée : elle partira dès que la recherche sera prête.
        </p>
      </BulleAssistant>
    );
  }
  if (echange.statut === "recherche") {
    return (
      <BulleAssistant>
        <p className="flex items-center gap-2 py-2 text-[15px] text-gris">
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
  // le moteur classe tous les passages et renvoie toujours les k premiers : cet état ne devrait pas se produire, mais
  // un écran vide serait pris pour une panne
  if (echange.resultats.length === 0) {
    return (
      <BulleAssistant>
        <p className="rounded-2xl border border-filet bg-white px-4 py-3 text-[15px] text-encre">
          Aucun passage trouvé pour cette question. Reformulez-la avec d'autres mots, par exemple en décrivant votre
          situation.
        </p>
      </BulleAssistant>
    );
  }
  // seuil d'abstention (#76) : il repère surtout les saisies sans rapport avec le droit du travail, pas les questions
  // juridiques absentes des fiches ; le message n'en promet pas plus, et les passages restent consultables
  const visibles = !echange.horsPerimetre || echange.afficher;
  return (
    <BulleAssistant>
      {echange.horsPerimetre ? (
        <div className="rounded-2xl border border-accent2/30 bg-accent2/5 px-4 py-3">
          <p className="text-[15px] font-medium leading-relaxed text-encre">
            Votre question semble sortir du périmètre des fiches pratiques du droit du travail.
          </p>
          <p className="mt-1 text-sm leading-relaxed text-encre">
            Aucun passage n'en est assez proche. Reformulez-la en décrivant votre situation de travail, ou consultez
            quand même les passages les plus proches.
          </p>
          <button
            type="button"
            onClick={() => basculer(echange.id)}
            aria-expanded={echange.afficher}
            className="mt-2 text-sm font-medium text-accent underline underline-offset-2 hover:no-underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            {echange.afficher ? "Masquer les passages" : "Afficher quand même les passages les plus proches"}
          </button>
        </div>
      ) : (
        <p className="text-[15px] leading-relaxed text-encre">
          Voici les {echange.resultats.length} passages des fiches pratiques les plus proches de votre question.
        </p>
      )}
      {visibles && (
        <>
          <p className={`${echange.horsPerimetre ? "mt-3" : "mt-0.5"} text-xs text-gris`}>
            Classés par similarité de sens, trouvés en {Math.round(echange.duree)} ms : plus elle est proche de 1, plus
            le passage ressemble à votre question, mais elle ne compare que les passages entre eux. Si votre question
            porte sur un sujet que les fiches ne traitent pas (impôts, aides sociales…), ces passages peuvent ne pas y
            répondre. Ils ne constituent pas un conseil juridique.
          </p>
          <ol className="mt-3 space-y-3">
            {echange.resultats.map((p) => (
              <li key={p.passage_id}>
                <Passage passage={p} />
              </li>
            ))}
          </ol>
        </>
      )}
    </BulleAssistant>
  );
}

// temps restant estimé au débit moyen depuis le début du fichier suivi ; rien tant que l'estimation est instable
function estimerRestant(p, debut) {
  if (!p?.total) return null;
  const maintenant = performance.now();
  if (!debut.current || debut.current.quoi !== p.quoi || p.charge < debut.current.charge) {
    debut.current = { quoi: p.quoi, charge: p.charge, t: maintenant };
    return null;
  }
  const ecoule = (maintenant - debut.current.t) / 1000;
  const debit = (p.charge - debut.current.charge) / ecoule;
  if (ecoule < 2 || debit <= 0) return null;
  const secondes = (p.total - p.charge) / debit;
  if (secondes < 5) return "quelques secondes restantes";
  return secondes < 90
    ? `environ ${Math.ceil(secondes / 5) * 5} s restantes`
    : `environ ${Math.round(secondes / 60)} min restantes`;
}

function BandeauEtat({ moteur }) {
  const debut = useRef(null);
  const tempsRestant = (p) => estimerRestant(p, debut);
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
          <details className="text-xs text-red-800">
            <summary className="cursor-pointer">Détail technique</summary>
            <code className="mt-1 block break-all">{String(moteur.erreur?.message ?? moteur.erreur)}</code>
          </details>
        </div>
      </div>
    );
  }
  const p = moteur.progression;
  const pourcent = p && p.total ? Math.min(100, Math.round((100 * p.charge) / p.total)) : null;
  const restant = tempsRestant(p);
  // pas de role="status" ici : le texte change à chaque paquet reçu et serait relu sans fin par un lecteur d'écran ;
  // les changements de phase sont annoncés par la zone dédiée de la conversation
  return (
    <div className="mb-3 rounded-xl bg-accent-clair px-3 py-2.5 text-sm text-accent">
      <p>
        {pourcent === null
          ? `Préparation de la recherche : premier téléchargement d'environ ${POIDS_PREMIER_CHARGEMENT}, comptez environ une minute.`
          : `Téléchargement ${p.quoi} : ${mo(p.charge)} Mo sur ${mo(p.total)} Mo${restant ? ` · ${restant}` : ""}`}
      </p>
      <div
        className="mt-2 h-1.5 overflow-hidden rounded-full bg-white"
        role="progressbar"
        aria-label="Téléchargement du modèle"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={pourcent ?? undefined}
        aria-valuetext={pourcent === null ? "Préparation" : `${pourcent} %`}
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

// texte de la zone d'annonce : l'état du dernier échange, sinon la disponibilité de la recherche ; vide au premier
// affichage, pour ne rien annoncer avant que le visiteur ait pu lire la page
function annonce(echanges, pret) {
  const e = echanges.at(-1);
  if (!e) return pret ? "La recherche est prête." : "";
  if (e.statut === "attente") return "Question gardée : elle partira dès que la recherche sera prête.";
  if (e.statut === "recherche") return "Recherche en cours.";
  if (e.statut === "erreur") return "La recherche a échoué. Reformulez la question ou réessayez.";
  if (e.resultats.length === 0) return "Aucun passage trouvé.";
  if (e.horsPerimetre && !e.afficher)
    return "Votre question semble sortir du périmètre des fiches pratiques. Les passages les plus proches restent consultables.";
  return `${e.resultats.length} passages trouvés. Premier résultat : ${e.resultats[0].titre_fiche}.`;
}

export default function Conversation({ moteur }) {
  const [question, setQuestion] = useState("");
  const [echanges, setEchanges] = useState([]);
  const dernier = useRef(null);
  const saisie = useRef(null);
  const pret = moteur.phase === "pret";
  // une seule question à la fois : en cours de recherche, ou gardée en attendant la fin du chargement
  const occupe = echanges.some((e) => e.statut === "recherche" || e.statut === "attente");

  // à chaque nouvelle question, l'échange est amené en haut de l'écran : la question, puis le premier résultat ; le
  // bas de la zone serait sinon masqué par le champ de saisie, fixé en bas de l'écran
  useEffect(() => {
    if (echanges.length === 0) return;
    const doux = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    dernier.current?.scrollIntoView({ behavior: doux ? "smooth" : "auto", block: "start" });
  }, [echanges.length]);

  const maj = (id, champs) => setEchanges((liste) => liste.map((e) => (e.id === id ? { ...e, ...champs } : e)));

  async function lancer(id, q) {
    try {
      const { resultats, duree, horsPerimetre } = await moteur.rechercher(q, NB_RESULTATS);
      maj(id, { statut: "resultats", resultats, duree, horsPerimetre, afficher: false });
    } catch {
      maj(id, { statut: "erreur" });
    }
  }

  // avant la fin du chargement, la question n'est plus ignorée : elle est gardée, puis envoyée par l'effet ci-dessous
  function envoyer(texte) {
    const q = texte.trim();
    if (!q || occupe) return;
    const id = Date.now();
    setQuestion("");
    setEchanges((liste) => [...liste, { id, question: q, statut: pret ? "recherche" : "attente" }]);
    if (pret) lancer(id, q);
  }

  // dès que le moteur est prêt, la question gardée part ; après une erreur de chargement, elle attend « Réessayer »
  useEffect(() => {
    if (!pret) return;
    const enAttente = echanges.find((e) => e.statut === "attente");
    if (!enAttente) return;
    maj(enAttente.id, { statut: "recherche" });
    lancer(enAttente.id, enAttente.question);
  }, [pret, echanges]);

  const basculer = (id) =>
    setEchanges((liste) => liste.map((e) => (e.id === id ? { ...e, afficher: !e.afficher } : e)));

  return (
    // overflow-clip et non overflow-hidden : hidden ferait de la section un conteneur de défilement, et le champ de
    // saisie ne pourrait plus rester fixé en bas de l'écran
    <section
      aria-labelledby="titre-recherche"
      className="flex min-h-[26rem] flex-col overflow-clip rounded-3xl border border-filet bg-fond/60 shadow-[0_1px_3px_rgba(22,24,29,0.06),0_12px_32px_-12px_rgba(22,24,29,0.12)]"
    >
      <h2 id="titre-recherche" className="sr-only">
        Recherche
      </h2>
      {/* annonce courte pour les lecteurs d'écran ; un aria-live sur toute la conversation ferait relire les cinq
          passages en entier à chaque réponse */}
      <p className="sr-only" role="status">
        {annonce(echanges, pret)}
      </p>
      <div className="flex-1 space-y-5 p-4 sm:p-6">
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
                    disabled={occupe}
                    onClick={() => {
                      // les exemples disparaissent avec la première question : le focus irait sinon se perdre sur
                      // la page, et un visiteur au clavier devrait repartir du haut
                      saisie.current?.focus();
                      envoyer(q);
                    }}
                    className="rounded-full border border-filet bg-white px-3 py-1.5 text-left text-sm text-encre hover:border-accent hover:text-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:border-filet disabled:hover:text-encre"
                  >
                    {q}
                  </button>
                </li>
              ))}
            </ul>
            {!pret && moteur.phase !== "erreur" && (
              <p className="mt-2 text-xs text-gris">
                Vous pouvez déjà poser votre question : elle partira dès que la recherche sera prête.
              </p>
            )}
          </div>
        )}

        {echanges.map((e, i) => (
          <div key={e.id} ref={i === echanges.length - 1 ? dernier : undefined} className="scroll-mt-4 space-y-4">
            <BulleQuestion texte={e.question} />
            <Reponse echange={e} basculer={basculer} />
          </div>
        ))}
      </div>

      {/* fixé en bas de l'écran seulement après la première question : avant, sur téléphone, il masquerait les exemples
          sous le bandeau de chargement */}
      <div className={`${echanges.length > 0 ? "sticky bottom-0 z-10" : ""} border-t border-filet bg-white p-3 sm:p-4`}>
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
            ref={saisie}
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
            placeholder="Posez votre question…"
            className="min-h-11 flex-1 resize-none rounded-xl border border-filet bg-fond px-4 py-2.5 text-[15px] placeholder:text-gris focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20"
          />
          <button
            type="submit"
            disabled={occupe || !question.trim()}
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
