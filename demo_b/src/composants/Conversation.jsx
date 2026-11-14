// Conversation de la démonstration du volet B (#111), reprise du site du volet A (maquette B, #53) : panneau latéral,
// fil qui défile seul, champ de saisie fixé en bas, une question à la fois, question gardée pendant la vérification
// de la chaîne. Ce qui change : la réponse est rédigée par Qwen et cite ses passages (composants/Reponse.jsx), l'attente
// peut durer plusieurs dizaines de secondes, et un clic sur une référence [Pk] amène la carte de son passage.

import { useEffect, useRef, useState } from "react";
import Barre from "./Barre.jsx";
import Reponse, { BulleAssistant, idCarte } from "./Reponse.jsx";
import { numero } from "../citations.js";

// périmètre du corpus, le même qu'au volet A : index commun (front/public/index/), lu par la chaîne de la #85
const PERIMETRE = { fiches: "261", passages: "4 240", instantane: "11 sept. 2026" };
const DUREE_SURLIGNAGE_MS = 2500;

// identifiants des chats et des échanges : uniques dans la session
let compteur = 0;
const nouvelId = () => ++compteur;

function BulleQuestion({ texte }) {
  return (
    <div className="flex justify-end">
      <p className="max-w-[85%] whitespace-pre-line rounded-[18px] rounded-br-md bg-accent px-4 py-3 text-[15px] leading-normal text-white sm:max-w-[80%]">
        {texte}
      </p>
    </div>
  );
}

function BandeauEtat({ chaine }) {
  if (chaine.phase === "indisponible") {
    return (
      <div role="alert" className="mb-2.5 rounded-[14px] border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm text-red-800">
        <p>L'assistant n'est pas disponible : {chaine.erreur}</p>
        <button
          type="button"
          onClick={chaine.reessayer}
          className="mt-2 rounded-lg bg-red-700 px-3 py-1.5 font-medium text-white hover:bg-red-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-700"
        >
          Réessayer
        </button>
      </div>
    );
  }
  if (chaine.phase === "verification") {
    return (
      <p className="mb-2.5 rounded-[14px] bg-accent-clair px-3.5 py-2.5 text-sm text-accent-texte">
        Vérification de l'assistant local : index, modèle de recherche et modèle de rédaction…
      </p>
    );
  }
  if (chaine.maquette) {
    return (
      <p className="mb-2.5 rounded-[14px] bg-accent-clair px-3.5 py-2.5 text-sm text-accent-texte">
        <strong>Maquette :</strong> aucun modèle n'est appelé. Les réponses rejouent deux essais enregistrés de la
        chaîne et deux cas simulés : choisissez une question d'exemple.
      </p>
    );
  }
  return null;
}

// texte de la zone d'annonce : l'état du dernier échange du chat affiché, sinon la disponibilité de l'assistant
function annonce(echanges, pret) {
  const e = echanges.at(-1);
  if (!e) return pret ? "L'assistant est prêt." : "";
  if (e.statut === "attente") return "Question gardée : elle partira dès que l'assistant sera prêt.";
  if (e.statut === "envoi") return "Recherche des passages et rédaction de la réponse en cours.";
  if (e.statut === "echec") return `La question n'a pas pu aboutir. ${e.erreurAppel.message}`;
  const r = e.reponse;
  if (r.statut === "reponse_citee") {
    const citees = r.sources.filter((s) => s.citee).map((s) => numero(s.reference));
    return `Réponse rédigée${citees.length ? `, citant ${citees.length > 1 ? "les passages" : "le passage"} ${citees.join(", ")}` : ""}.`;
  }
  if (r.statut === "abstention_modele") return "L'assistant ne peut pas répondre à partir des fiches consultées.";
  if (r.statut === "sortie_invalide") return "Réponse non conforme : ses références sont mal formées.";
  return "L'assistant n'a pas pu produire de réponse. Vous pouvez réessayer.";
}

export default function Conversation({ chaine }) {
  // chats de la session : gardés en mémoire jusqu'au rechargement de la page, jamais enregistrés
  const [chats, setChats] = useState(() => [{ id: nouvelId(), echanges: [] }]);
  const [actuel, setActuel] = useState(() => chats[0].id);
  const [question, setQuestion] = useState("");
  const [menuOuvert, setMenuOuvert] = useState(false);
  const dernier = useRef(null);
  const zoneFil = useRef(null);
  const saisie = useRef(null);
  const boutonMenu = useRef(null);

  const pret = chaine.phase === "pret";
  const echanges = chats.find((c) => c.id === actuel).echanges;
  // une seule question à la fois, tous chats confondus (contrat de la #121, §2 : Ollama traite les appels un par un)
  const occupe = chats.some((c) => c.echanges.some((e) => e.statut === "envoi" || e.statut === "attente"));
  const titre = echanges[0]?.question ?? "Nouveau chat";

  // même défilement qu'au volet A : le dernier échange est amené en haut de la zone, qui seule défile
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
    majEchange(id, () => ({ statut: "envoi", debut: performance.now(), reponse: null, erreurAppel: null }));
    try {
      const reponse = await chaine.poser(q);
      majEchange(id, () => ({ statut: "recue", reponse, afficher: false, surligne: null }));
    } catch (e) {
      majEchange(id, () => ({ statut: "echec", erreurAppel: { type: e.type ?? "inconnue", message: e.message } }));
    }
  }

  function envoyer(texte) {
    const q = texte.trim();
    if (!q || occupe) return;
    const id = nouvelId();
    setQuestion("");
    setChats((liste) =>
      liste.map((c) =>
        c.id === actuel ? { ...c, echanges: [...c.echanges, { id, question: q, statut: "attente" }] } : c,
      ),
    );
    if (pret) lancer(id, q);
  }

  // dès que la chaîne est prête, la question gardée part ; si elle est indisponible, elle attend « Réessayer »
  useEffect(() => {
    if (!pret) return;
    const enAttente = chats.flatMap((c) => c.echanges).find((e) => e.statut === "attente");
    if (enAttente) lancer(enAttente.id, enAttente.question);
  }, [pret, chats]);

  // contrat, §6 : aucune relance automatique ; c'est le visiteur qui relance la même question
  function reessayer(id) {
    if (occupe) return;
    const e = chats.flatMap((c) => c.echanges).find((x) => x.id === id);
    if (e) lancer(id, e.question);
  }

  const basculer = (id) => majEchange(id, (e) => ({ afficher: !e.afficher }));

  // clic sur [Pk] : la carte du passage est amenée en haut de la zone qui défile, reçoit le focus et reste surlignée
  // un instant ; si elle fait partie des passages non cités repliés, ils sont d'abord dépliés
  function montrer(echangeId, reference) {
    majEchange(echangeId, (e) => ({
      surligne: reference,
      afficher: e.afficher || !e.reponse.sources.find((s) => s.reference === reference)?.citee,
    }));
    requestAnimationFrame(() => {
      const carte = document.getElementById(idCarte(echangeId, reference));
      const zone = zoneFil.current;
      if (!carte || !zone) return;
      const doux = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      zone.scrollTo({ top: carte.getBoundingClientRect().top - zone.getBoundingClientRect().top + zone.scrollTop - 16, behavior: doux ? "smooth" : "auto" });
      carte.focus({ preventScroll: true });
    });
    setTimeout(() => majEchange(echangeId, (e) => (e.surligne === reference ? { surligne: null } : {})), DUREE_SURLIGNAGE_MS);
  }

  function fermerMenu() {
    setMenuOuvert(false);
    requestAnimationFrame(() => boutonMenu.current?.focus());
  }

  // le menu n'est une surcouche que sur téléphone : en largeur d'ordinateur (md, 48rem), il se ferme
  useEffect(() => {
    if (!menuOuvert) return;
    const ordinateur = window.matchMedia("(min-width: 48rem)");
    if (ordinateur.matches) {
      setMenuOuvert(false);
      return;
    }
    const changer = (ev) => ev.matches && setMenuOuvert(false);
    ordinateur.addEventListener("change", changer);
    return () => ordinateur.removeEventListener("change", changer);
  }, [menuOuvert]);

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
    requestAnimationFrame(() => saisie.current?.focus());
  }

  function utiliserExemple(q) {
    setMenuOuvert(false);
    requestAnimationFrame(() => saisie.current?.focus());
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
        exemples={chaine.exemples}
        utiliserExemple={utiliserExemple}
        occupe={occupe}
      />

      <main inert={menuOuvert || undefined} className="flex min-w-0 flex-1 flex-col">
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
            Fiches du ministère · instantané du 11 sept. 2026 · modèle local
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

        <p className="sr-only" role="status">
          {annonce(echanges, pret)}
        </p>

        <section ref={zoneFil} aria-label="Conversation" className="relative min-h-0 flex-1 overflow-y-auto px-3 pb-2 pt-6 sm:px-7 sm:pt-7">
          <div className="mx-auto flex max-w-[760px] flex-col gap-[22px]">
            {echanges.length === 0 && (
              <BulleAssistant>
                <p className="rounded-[16px] rounded-tl-md border border-filet bg-white px-3.5 py-3 text-[15px] leading-normal">
                  Bonjour ! Posez une question sur votre travail : je rédige une réponse à partir des fiches du ministère,
                  en citant les passages utilisés. Si les fiches ne permettent pas de répondre, je vous le dis.
                </p>
                <p className="text-[13px] leading-normal text-gris">
                  Je cherche dans les {PERIMETRE.fiches} fiches pratiques du ministère du Travail ({PERIMETRE.passages}{" "}
                  passages, instantané du {PERIMETRE.instantane}). Le Code du travail lui-même et les conventions
                  collectives ne sont pas interrogés.
                </p>
                {/* sur téléphone, les exemples du panneau sont cachés dans le menu : ils sont repris ici */}
                <ul className="flex flex-wrap gap-2 md:hidden">
                  {chaine.exemples.map(({ question: q, libelle }) => (
                    <li key={q}>
                      <button
                        type="button"
                        disabled={occupe}
                        onClick={() => utiliserExemple(q)}
                        className="min-h-11 rounded-full border border-bordure bg-white px-3.5 py-2 text-left text-sm text-texte2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed"
                      >
                        {libelle ? `${libelle} : ` : ""}
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
                <Reponse echange={e} basculer={basculer} montrer={montrer} reessayer={reessayer} />
              </div>
            ))}
          </div>
        </section>

        <div className="bg-gradient-to-b from-fond/0 to-fond to-30% px-3 pb-3 pt-2 sm:px-7 sm:pb-[18px] sm:pt-3">
          <div className="mx-auto max-w-[760px]">
            <BandeauEtat chaine={chaine} />
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
                aria-label="Envoyer la question"
                className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent text-white hover:bg-accent-fonce focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:bg-[#c8d6cf] disabled:text-accent-texte"
              >
                <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 19V5M5 12l7-7 7 7" />
                </svg>
              </button>
            </form>
            <p className="mt-2 text-center text-xs leading-normal text-gris">
              Réponses rédigées par un modèle exécuté sur cet ordinateur, à partir des fiches de travail-emploi.gouv.fr
              (instantané SocialGouv du 11 sept. 2026, Licence Ouverte Etalab 2.0). Projet étudiant, non officiel : ne
              remplace pas un conseil juridique.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
