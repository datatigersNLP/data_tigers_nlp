// Confidentialité et mentions légales (#176, remarque de l'enseignant). Chaque affirmation a été vérifiée le 21/11/2026
// sur le site en ligne (requêtes réseau, cookies, stockages du navigateur, après une question) et dans la documentation
// de GitHub Pages ; voir le ticket. Fenêtre modale native : <dialog> gère le piège du focus et la touche Échap.

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
            Confidentialité et mentions légales
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
          <Rubrique titre="Vos questions restent sur votre appareil">
            <p>
              Le modèle qui analyse votre question s'exécute dans votre navigateur. Ni vos questions ni les résultats ne
              sont envoyés à l'équipe ou à un serveur : une fois le site chargé, une recherche ne fait aucune requête.
              Vos chats restent en mémoire et disparaissent quand vous fermez ou rechargez la page.
            </p>
          </Rubrique>

          <Rubrique titre="Ni cookie, ni compte, ni mesure d'audience">
            <p>
              Le site ne dépose aucun cookie, n'utilise aucun outil de statistiques et n'écrit rien dans le stockage
              local de votre navigateur. Il ne contacte aucun autre site : la police de caractères, le modèle et son
              moteur d'exécution sont servis par le site lui-même.
            </p>
          </Rubrique>

          <Rubrique titre="Ce que garde votre navigateur">
            <p>
              Pour ne pas retélécharger le modèle à chaque visite, votre navigateur garde ses fichiers dans son cache
              (environ 100 Mo, sous le nom « transformers-cache »). Ce sont des fichiers techniques, identiques pour
              tous les visiteurs, qui ne contiennent aucune information sur vous. Vous pouvez les effacer à tout moment
              en supprimant les données de ce site dans les réglages de votre navigateur.
            </p>
          </Rubrique>

          <Rubrique titre="Hébergement par GitHub Pages">
            <p>
              Le site est hébergé par GitHub Pages, un service de GitHub, Inc. Comme pour tout site GitHub Pages, GitHub
              enregistre l'adresse IP des visiteurs à des fins de sécurité. Ce traitement relève de GitHub, et non de
              l'équipe, qui ne reçoit pas ces journaux.
            </p>
            <p>
              Pour ces données : délégué à la protection des données de GitHub, dpo@github.com, et{" "}
              <Externe href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">
                déclaration de confidentialité de GitHub
              </Externe>
              .
            </p>
          </Rubrique>

          <Rubrique titre="Un conseil">
            <p>
              Pour chercher, le site n'a besoin d'aucune information personnelle. Évitez d'écrire votre nom, celui de
              votre employeur ou des détails sur votre santé : décrivez votre situation en termes généraux.
            </p>
          </Rubrique>

          <Rubrique titre="Liens vers les fiches">
            <p>
              Les liens « Voir dans la fiche » ouvrent le site du ministère du Travail, travail-emploi.gouv.fr, qui
              applique sa propre politique de confidentialité.
            </p>
          </Rubrique>

          <Rubrique titre="Vos droits">
            <p>
              L'équipe ne collecte et ne conserve aucune donnée personnelle sur les visiteurs : elle n'a rien à vous
              communiquer ni à effacer. Pour les données traitées par GitHub, adressez-vous à GitHub. Vous pouvez aussi
              adresser une réclamation à la <Externe href="https://www.cnil.fr">CNIL</Externe>.
            </p>
          </Rubrique>

          <Rubrique titre="Mentions légales">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-1.5 sm:grid-cols-[150px_1fr]">
              <dt className="font-semibold text-encre">Éditeur</dt>
              <dd>
                L'équipe Data Tigers, projet pédagogique du Master 2 Data &amp; IA de la FGES (Université Catholique de
                Lille), module NLP 2, 2026‑2027.
              </dd>
              <dt className="font-semibold text-encre">Directeur de la publication</dt>
              <dd>Mahé BEGNIS</dd>
              <dt className="font-semibold text-encre">Contact</dt>
              <dd>
                par un ticket sur le{" "}
                <Externe href="https://github.com/datatigersNLP/data_tigers_nlp/issues">dépôt GitHub du projet</Externe>
              </dd>
              <dt className="font-semibold text-encre">Hébergeur</dt>
              <dd>GitHub, Inc., 88 Colin P. Kelly Jr. St., San Francisco, CA 94107, États-Unis</dd>
              <dt className="font-semibold text-encre">Contenus</dt>
              <dd>
                Extraits des fiches pratiques du ministère du Travail, instantané SocialGouv du 11 septembre 2026,
                Licence Ouverte Etalab 2.0. Site non officiel : il ne remplace pas un conseil juridique. Le logo et le
                site sont des créations de l'équipe.
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
