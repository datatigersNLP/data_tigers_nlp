// Confidentialité et mentions (#176, remarque de l'enseignant), version du volet B : tout s'exécute sur cet ordinateur.
// Vérifié le 21/11/2026 : aucune ressource extérieure ni stockage dans l'interface ; la couche locale
// (scripts/rag/serveur_demo.py) et Ollama, tels que lancés pour la démonstration, ne journalisent ni question ni
// réponse. Même fenêtre modale native que le volet A (front/src/composants/Confidentialite.jsx).

import { useEffect, useRef } from "react";

// éléments activables et visibles de la fenêtre, dans l'ordre du document (même règle que le panneau, Barre.jsx)
const ACTIVABLES = 'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])';

// la tabulation boucle dans la fenêtre : sans cela, Chrome laisse le focus partir vers son interface après le dernier
// lien, et Safari, avec ses réglages par défaut, ne passe pas par les boutons
function boucler(ev, boite) {
  if (ev.key !== "Tab" || !boite) return;
  const liste = [...boite.querySelectorAll(ACTIVABLES)].filter((el) => el.getClientRects().length > 0);
  if (liste.length === 0) return;
  ev.preventDefault();
  const i = liste.indexOf(document.activeElement);
  const n = liste.length;
  liste[i === -1 ? (ev.shiftKey ? n - 1 : 0) : (i + (ev.shiftKey ? n - 1 : 1)) % n].focus();
}

const lien =
  "font-medium text-accent-texte underline underline-offset-2 hover:text-encre focus-visible:outline-2 focus-visible:outline-accent";

function Externe({ href, children }) {
  return (
    <a href={href} target="_blank" rel="noreferrer" className={lien}>
      {children}
      <span className="sr-only"> (nouvel onglet)</span>
    </a>
  );
}

function Rubrique({ titre, children }) {
  return (
    <section className="flex flex-col gap-1.5">
      <h3 className="text-[15px] font-semibold text-encre">{titre}</h3>
      <div className="flex flex-col gap-1.5 text-sm leading-relaxed text-texte2">{children}</div>
    </section>
  );
}

export default function Confidentialite({ ouvert, fermer }) {
  const boite = useRef(null);

  // l'état React commande la fenêtre ; sa fermeture native (Échap, bouton) le remet à jour par l'événement close
  useEffect(() => {
    const d = boite.current;
    if (!d) return;
    if (ouvert && !d.open) d.showModal();
    if (!ouvert && d.open) d.close();
  }, [ouvert]);

  useEffect(() => {
    const d = boite.current;
    d.addEventListener("close", fermer);
    return () => d.removeEventListener("close", fermer);
  }, [fermer]);

  return (
    <dialog
      ref={boite}
      aria-labelledby="titre-confidentialite"
      // un clic sur le fond assombri, hors du contenu, ferme la fenêtre
      onClick={(ev) => ev.target === boite.current && boite.current.close()}
      onKeyDown={(ev) => boucler(ev, boite.current)}
      className="m-auto max-h-[min(86dvh,780px)] w-[min(640px,calc(100vw-24px))] overflow-hidden rounded-[18px] border border-filet bg-fond p-0 text-encre shadow-[0_24px_60px_-20px_rgba(28,27,26,0.45)] backdrop:bg-encre/45"
    >
      <div className="flex max-h-[min(86dvh,780px)] flex-col">
        <div className="flex items-center gap-3 border-b border-filet px-5 py-3.5">
          <h2 id="titre-confidentialite" className="flex-1 text-base font-bold">
            Confidentialité et mentions
          </h2>
          <button
            type="button"
            onClick={() => boite.current.close()}
            aria-label="Fermer"
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[10px] text-encre hover:bg-actif focus-visible:outline-2 focus-visible:outline-accent"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>

        <div className="flex flex-col gap-5 overflow-y-auto px-5 py-5">
          <Rubrique titre="Tout reste sur cet ordinateur">
            <p>
              L'interface, la recherche dans les fiches et le modèle qui rédige la réponse s'exécutent sur cette machine.
              Votre question est transmise au modèle local par Ollama, à l'adresse 127.0.0.1 : elle ne part jamais sur
              Internet, ni vers l'équipe ni vers un service en ligne.
            </p>
          </Rubrique>

          <Rubrique titre="Aucune question enregistrée">
            <p>
              Dans la configuration de la démonstration, la couche locale et Ollama ne journalisent, pour chaque appel,
              que la route, la durée et l'adresse locale : jamais le texte de la question ni celui de la réponse. Vos
              chats restent en mémoire et disparaissent quand vous fermez ou rechargez la page.
            </p>
          </Rubrique>

          <Rubrique titre="Ni cookie, ni compte, ni mesure d'audience">
            <p>
              L'interface ne dépose aucun cookie, n'utilise aucun outil de statistiques, n'écrit rien dans le stockage
              local du navigateur et ne charge aucune ressource extérieure.
            </p>
          </Rubrique>

          <Rubrique titre="Une réponse rédigée par un modèle">
            <p>
              Les réponses sont rédigées par un modèle de langage, Qwen2.5-7B-Instruct, adapté par l'équipe à citer ses
              sources. Elles peuvent contenir des erreurs ou des omissions : vérifiez toujours dans les passages cités.
            </p>
          </Rubrique>

          <Rubrique titre="Un conseil">
            <p>
              Pour chercher, l'assistant n'a besoin d'aucune information personnelle. Évitez d'écrire votre nom, celui de
              votre employeur ou des détails sur votre santé : décrivez votre situation en termes généraux.
            </p>
          </Rubrique>

          <Rubrique titre="Vos droits">
            <p>
              L'équipe ne collecte et ne conserve aucune donnée personnelle sur les personnes qui utilisent
              l'assistant : elle n'a rien à vous communiquer ni à effacer. Vous pouvez aussi adresser une réclamation à
              la <Externe href="https://www.cnil.fr">CNIL</Externe>.
            </p>
          </Rubrique>

          <Rubrique titre="Mentions">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-1.5 sm:grid-cols-[150px_1fr]">
              <dt className="font-semibold text-encre">Éditeur</dt>
              <dd>
                L'équipe Data Tigers, projet pédagogique du Master 2 Data &amp; IA de la FGES (Université Catholique de
                Lille), module NLP 2, 2026‑2027.
              </dd>
              <dt className="font-semibold text-encre">Contact</dt>
              <dd>
                par un ticket sur le{" "}
                <Externe href="https://github.com/datatigersNLP/data_tigers_nlp/issues">dépôt GitHub du projet</Externe>
              </dd>
              <dt className="font-semibold text-encre">Modèle</dt>
              <dd>Qwen2.5-7B-Instruct, de l'équipe Qwen, sous licence Apache 2.0, adapté par l'équipe.</dd>
              <dt className="font-semibold text-encre">Contenus</dt>
              <dd>
                Extraits des fiches pratiques du ministère du Travail, instantané SocialGouv du 11 septembre 2026,
                Licence Ouverte Etalab 2.0. Assistant non officiel : il ne remplace pas un conseil juridique. Le logo et
                l'interface sont des créations de l'équipe.
              </dd>
              <dt className="font-semibold text-encre">Vérifié le</dt>
              <dd>21 novembre 2026</dd>
            </dl>
          </Rubrique>
        </div>
      </div>
    </dialog>
  );
}
