// Application de recherche, maquette B validée par l'équipe (#53) : panneau latéral (nouveau chat, chats de la session,
// exemples), fil de la conversation qui défile seul, champ de saisie fixé en bas. Comportement repris de #48 et #53 :
// une question posée pendant le chargement est gardée puis envoyée dès que le moteur est prêt ; une question hors du
// périmètre (seuil d'abstention, #76) est signalée, ses passages restant consultables ; chaque passage porte son score.

import { useEffect, useRef, useState } from "react";
import Barre from "./Barre.jsx";
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
// premier chargement : modèle élagué servi par le site (65,7 Mio, #78), taille demandée par le compte rendu du Weekly,
// et vocabulaire du tokeniseur (4,1 Mio). Mesuré le 14/10/2026 sur le site en ligne, profil vierge : prêt en 23 à 30 s
// (le serveur compresse le modèle : 45,9 Mio transférés). Avant la #78 : 113 Mio depuis le Hub, 52 à 56 s
const POIDS_MODELE = "65,7 Mio";

// tailles en Mio (2^20 octets), l'unité de l'équipe ; une décimale, pour que la progression reste lisible
const mio = (octets) =>
  (octets / 2 ** 20).toLocaleString("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
// identifiants des chats et des échanges : uniques dans la session
let compteur = 0;
const nouvelId = () => ++compteur;

function IconeRecherche() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" aria-hidden="true">
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5" />
    </svg>
  );
}

function BulleAssistant({ children }) {
  return (
    <div className="flex items-start gap-3">
      <span className="mt-0.5 hidden h-8 w-8 shrink-0 items-center justify-center rounded-[10px] bg-accent-clair text-accent sm:flex" aria-hidden="true">
        <IconeRecherche />
      </span>
      <div className="flex min-w-0 flex-1 flex-col gap-3">{children}</div>
    </div>
  );
}

function BulleQuestion({ texte }) {
  return (
    <div className="flex justify-end">
      <p className="max-w-[85%] whitespace-pre-line rounded-[18px] rounded-br-md bg-accent px-4 py-3 text-[15px] leading-normal text-white sm:max-w-[80%]">
        {texte}
      </p>
    </div>
  );
}

function Attente({ texte }) {
  return (
    <BulleAssistant>
      <p className="flex items-center gap-2.5 py-1.5 text-[15px] text-gris">
        <span className="h-2 w-2 rounded-full bg-accent motion-safe:animate-pulse" aria-hidden="true" />
        {texte}
      </p>
    </BulleAssistant>
  );
}

function Reponse({ echange, basculer }) {
  if (echange.statut === "attente") return <Attente texte="Votre question est gardée : elle partira dès que la recherche sera prête." />;
  if (echange.statut === "recherche") return <Attente texte="Recherche des passages les plus proches…" />;
  if (echange.statut === "erreur") {
    return (
      <BulleAssistant>
        <p className="rounded-[14px] border border-red-200 bg-red-50 px-4 py-3 text-[15px] text-red-800">
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
        <p className="text-[15px] leading-relaxed">
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
        <div className="rounded-[14px] border border-alerte-bord bg-alerte-fond px-4 py-3.5">
          <p className="text-[15px] font-semibold leading-normal">
            Votre question semble sortir du périmètre des fiches pratiques du droit du travail.
          </p>
          <p className="mt-1 text-sm leading-relaxed text-texte">
            Aucun passage n'en est assez proche. Reformulez-la en décrivant votre situation de travail, ou consultez
            quand même les passages les plus proches.
          </p>
          <button
            type="button"
            onClick={() => basculer(echange.id)}
            aria-expanded={echange.afficher}
            className="mt-2 text-sm font-semibold text-accent underline underline-offset-[3px] hover:text-accent-fonce focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            {echange.afficher ? "Masquer les passages" : "Afficher quand même les passages les plus proches"}
          </button>
        </div>
      ) : (
        <p className="text-[15px] leading-relaxed">
          J'ai trouvé <strong>{echange.resultats.length} passages</strong> des fiches pratiques qui parlent de votre
          question. Les voici, du plus proche au moins proche.
        </p>
      )}
      {visibles && (
        <>
          <ol className="flex flex-col gap-3">
            {echange.resultats.map((p) => (
              <li key={p.passage_id}>
                <Passage passage={p} />
              </li>
            ))}
          </ol>
          <p className="text-[13px] leading-normal text-gris">
            Trouvés en {Math.round(echange.duree)} ms. Plus la similarité est proche de 1, plus le passage ressemble à
            votre question, mais elle ne compare que les passages entre eux. Si votre question porte sur un sujet que les
            fiches ne traitent pas (impôts, aides sociales…), ces passages peuvent ne pas y répondre. Ces extraits ne sont
            pas un conseil juridique.
          </p>
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
  if (moteur.phase === "pret") return null;
  if (moteur.phase === "erreur") {
    return (
      <div role="alert" className="mb-2.5 rounded-[14px] border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm text-red-800">
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
  const restant = estimerRestant(p, debut);
  // pas de role="status" ici : le texte change à chaque paquet reçu et serait relu sans fin par un lecteur d'écran ;
  // les changements de phase sont annoncés par la zone dédiée de la conversation
  return (
    <div className="mb-2.5 rounded-[14px] bg-accent-clair px-3.5 py-2.5 text-sm text-accent-texte">
      <p>
        {pourcent === null
          ? `Préparation de la recherche : premier téléchargement du modèle (${POIDS_MODELE}), comptez une trentaine de secondes.`
          : `Téléchargement ${p.quoi} : ${mio(p.charge)} Mio sur ${mio(p.total)} Mio${restant ? ` · ${restant}` : ""}`}
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
      <p className="mt-1.5 text-xs">Une seule fois : le modèle reste ensuite en mémoire dans votre navigateur.</p>
    </div>
  );
}

// texte de la zone d'annonce : l'état du dernier échange du chat affiché, sinon la disponibilité de la recherche ;
// vide au premier affichage, pour ne rien annoncer avant que le visiteur ait pu lire la page
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
  // chats de la session : gardés en mémoire jusqu'au rechargement de la page, jamais enregistrés ni envoyés
  const [chats, setChats] = useState(() => [{ id: nouvelId(), echanges: [] }]);
  const [actuel, setActuel] = useState(() => chats[0].id);
  const [question, setQuestion] = useState("");
  const [menuOuvert, setMenuOuvert] = useState(false);
  const dernier = useRef(null);
  const zoneFil = useRef(null);
  const saisie = useRef(null);
  const boutonMenu = useRef(null);

  const pret = moteur.phase === "pret";
  const echanges = chats.find((c) => c.id === actuel).echanges;
  // une seule question à la fois, tous chats confondus : en cours de recherche, ou gardée pendant le chargement
  const occupe = chats.some((c) => c.echanges.some((e) => e.statut === "recherche" || e.statut === "attente"));
  // titre du chat : sa première question, comme dans la liste du panneau
  const titre = echanges[0]?.question ?? "Nouveau chat";

  // à chaque nouvelle question, et à chaque changement de chat, le dernier échange est amené en haut de la zone qui
  // défile : la question, puis le premier résultat. Pas de scrollIntoView : il ferait aussi défiler le cadre de
  // l'application, pourtant en overflow-hidden, et la page remonterait en laissant un vide sous le champ de saisie
  // Le dernier échange occupe au moins la hauteur de la zone, comme dans les applications de chat : sans cette
  // réserve, une question suivie d'une réponse courte ne pourrait pas remonter en haut, faute de contenu en dessous
  useEffect(() => {
    const zone = zoneFil.current;
    const el = dernier.current;
    if (echanges.length === 0 || !zone || !el) return;
    zone.querySelectorAll("[data-echange]").forEach((e) => (e.style.minHeight = ""));
    el.style.minHeight = `${zone.clientHeight - 48}px`;
    const doux = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    zone.scrollTo({ top: el.offsetTop - 16, behavior: doux ? "smooth" : "auto" });
  }, [actuel, echanges.length]);

  const majEchange = (id, changer) =>
    setChats((liste) =>
      liste.map((c) => ({ ...c, echanges: c.echanges.map((e) => (e.id === id ? { ...e, ...changer(e) } : e)) })),
    );

  async function lancer(id, q) {
    try {
      const { resultats, duree, horsPerimetre } = await moteur.rechercher(q, NB_RESULTATS);
      majEchange(id, () => ({ statut: "resultats", resultats, duree, horsPerimetre, afficher: false }));
    } catch {
      majEchange(id, () => ({ statut: "erreur" }));
    }
  }

  // avant la fin du chargement, la question n'est plus ignorée : elle est gardée, puis envoyée par l'effet ci-dessous
  function envoyer(texte) {
    const q = texte.trim();
    if (!q || occupe) return;
    const id = nouvelId();
    setQuestion("");
    setChats((liste) =>
      liste.map((c) =>
        c.id === actuel ? { ...c, echanges: [...c.echanges, { id, question: q, statut: pret ? "recherche" : "attente" }] } : c,
      ),
    );
    if (pret) lancer(id, q);
  }

  // dès que le moteur est prêt, la question gardée part ; après une erreur de chargement, elle attend « Réessayer »
  useEffect(() => {
    if (!pret) return;
    const enAttente = chats.flatMap((c) => c.echanges).find((e) => e.statut === "attente");
    if (!enAttente) return;
    majEchange(enAttente.id, () => ({ statut: "recherche" }));
    lancer(enAttente.id, enAttente.question);
  }, [pret, chats]);

  const basculer = (id) => majEchange(id, (e) => ({ afficher: !e.afficher }));

  function fermerMenu() {
    setMenuOuvert(false);
    boutonMenu.current?.focus();
  }

  // un chat vide sert de nouveau chat : on n'en crée pas un second, on y place seulement le curseur
  function nouveauChat() {
    if (echanges.length > 0) {
      const id = nouvelId();
      setChats((liste) => [...liste, { id, echanges: [] }]);
      setActuel(id);
    }
    setMenuOuvert(false);
    setQuestion("");
    requestAnimationFrame(() => saisie.current?.focus());
  }

  function choisirChat(id) {
    setActuel(id);
    setMenuOuvert(false);
  }

  function utiliserExemple(q) {
    setMenuOuvert(false);
    // le menu se ferme sur téléphone : le focus irait sinon se perdre sur la page
    saisie.current?.focus();
    envoyer(q);
  }

  return (
    <div className="flex h-dvh overflow-hidden bg-fond text-encre">
      <Barre
        ouvert={menuOuvert}
        fermer={fermerMenu}
        chats={chats}
        actuel={actuel}
        choisir={choisirChat}
        nouveauChat={nouveauChat}
        exemples={EXEMPLES}
        utiliserExemple={utiliserExemple}
        occupe={occupe}
      />

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-2 border-b border-filet px-3 py-2 sm:px-7 sm:py-3.5">
          <button
            ref={boutonMenu}
            type="button"
            onClick={() => setMenuOuvert(true)}
            aria-label="Ouvrir le menu"
            aria-expanded={menuOuvert}
            aria-controls="menu-lateral"
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[10px] text-encre focus-visible:outline-2 focus-visible:outline-accent md:hidden"
          >
            <svg viewBox="0 0 24 24" className="h-[22px] w-[22px]" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
              <path d="M4 7h16M4 12h16M4 17h10" />
            </svg>
          </button>
          <h1 className="min-w-0 flex-1 truncate text-[15px] font-semibold">{titre}</h1>
          <span className="hidden shrink-0 text-[13px] text-gris lg:inline">
            Fiches du ministère · instantané du 11 sept. 2026
          </span>
          <button
            type="button"
            onClick={nouveauChat}
            aria-label="Nouveau chat"
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[10px] text-encre focus-visible:outline-2 focus-visible:outline-accent md:hidden"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
              <path d="M12 5v14M5 12h14" />
            </svg>
          </button>
        </header>

        {/* annonce courte pour les lecteurs d'écran ; un aria-live sur toute la conversation ferait relire les cinq
            passages en entier à chaque réponse */}
        <p className="sr-only" role="status">
          {annonce(echanges, pret)}
        </p>

        {/* relative : la zone est le repère des offsetTop utilisés pour le défilement */}
        <section ref={zoneFil} aria-label="Conversation" className="relative min-h-0 flex-1 overflow-y-auto px-3 pb-2 pt-6 sm:px-7 sm:pt-7">
          <div className="mx-auto flex max-w-[760px] flex-col gap-[22px]">
            {echanges.length === 0 && (
              <BulleAssistant>
                <p className="rounded-[16px] rounded-tl-md border border-filet bg-white px-3.5 py-3 text-[15px] leading-normal">
                  Bonjour ! Posez une question sur votre travail : je vous montre les passages des fiches du ministère
                  qui y répondent, avec le lien vers chaque source.
                </p>
                {!pret && moteur.phase !== "erreur" && (
                  <p className="text-[13px] text-gris">
                    Vous pouvez déjà poser votre question : elle partira dès que la recherche sera prête.
                  </p>
                )}
                {/* sur téléphone, les exemples du panneau sont cachés dans le menu : ils sont repris ici */}
                <ul className="flex flex-wrap gap-2 md:hidden">
                  {EXEMPLES.map((q) => (
                    <li key={q}>
                      <button
                        type="button"
                        disabled={occupe}
                        onClick={() => utiliserExemple(q)}
                        className="min-h-11 rounded-full border border-bordure bg-white px-3.5 py-2 text-left text-sm text-texte2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed"
                      >
                        {q}
                      </button>
                    </li>
                  ))}
                </ul>
              </BulleAssistant>
            )}

            {echanges.map((e, i) => (
              <div key={e.id} data-echange ref={i === echanges.length - 1 ? dernier : undefined} className="flex flex-col gap-[22px]">
                <BulleQuestion texte={e.question} />
                <Reponse echange={e} basculer={basculer} />
              </div>
            ))}
          </div>
        </section>

        <div className="bg-gradient-to-b from-fond/0 to-fond to-30% px-3 pb-3 pt-2 sm:px-7 sm:pb-[18px] sm:pt-3">
          <div className="mx-auto max-w-[760px]">
            <BandeauEtat moteur={moteur} />
            <form
              className="flex items-end gap-2 rounded-[18px] border border-bordure bg-white py-2 pl-4 pr-2 shadow-[0_8px_24px_-12px_rgba(28,27,26,0.25)] focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/25"
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
                placeholder={echanges.length > 0 ? "Posez une autre question…" : "Posez votre question…"}
                className="min-h-11 flex-1 resize-none bg-transparent py-2.5 text-base outline-none placeholder:text-gris sm:text-[15px]"
              />
              <button
                type="submit"
                disabled={occupe || !question.trim()}
                aria-label="Rechercher"
                className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent text-white hover:bg-accent-fonce focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:bg-[#c8d6cf] disabled:text-accent-texte"
              >
                <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 19V5M5 12l7-7 7 7" />
                </svg>
              </button>
            </form>
            {/* revue de #42 : le texte indexé vient de l'instantané SocialGouv (front/public/index/SOURCES.md), et sa
                date compte, une règle ayant pu changer depuis ; mentions exigées par #53, toujours visibles */}
            <p className="mt-2 text-center text-xs leading-normal text-gris">
              Extraits des fiches de{" "}
              <a
                href="https://travail-emploi.gouv.fr"
                target="_blank"
                rel="noreferrer"
                className="underline underline-offset-2 hover:text-encre focus-visible:outline-2 focus-visible:outline-accent"
              >
                travail-emploi.gouv.fr
                <span className="sr-only"> (nouvel onglet)</span>
              </a>
              , instantané SocialGouv du 11 sept. 2026, Licence Ouverte Etalab 2.0. Projet étudiant, non officiel : ne
              remplace pas un conseil juridique.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
