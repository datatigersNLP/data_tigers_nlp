// Réponse de l'assistant à une question (#111), selon les cinq statuts du contrat de la #121 (section 6) :
// - reponse_citee : texte rédigé, chaque [Pk] valide est un bouton qui amène la carte de son passage ;
// - abstention_modele : encadré distinct, comme l'abstention du volet A, passages consultables sur demande ;
// - sortie_invalide : avertissement, réponse brute repliée, passages consultables ;
// - erreur_technique et erreur_preparation : message, détail technique et bouton « Réessayer ».
// Un échec de l'appel lui-même (réseau, délai, 409) est affiché de la même façon que les erreurs.

import { useEffect, useState } from "react";
import Passage from "./Passage.jsx";
import { blocs, numero, referencesValides } from "../citations.js";

const secondes = (ns) => (ns / 1e9).toLocaleString("fr-FR", { maximumFractionDigits: 1 });

export const idCarte = (echangeId, reference) => `passage-${echangeId}-${numero(reference)}`;

function IconeAssistant() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M4 5h16v11H9l-5 4z" />
      <path d="M8 9h8M8 12h5" />
    </svg>
  );
}

export function BulleAssistant({ children }) {
  return (
    <div className="flex items-start gap-3">
      <span className="mt-0.5 hidden h-8 w-8 shrink-0 items-center justify-center rounded-[10px] bg-accent-clair text-accent sm:flex" aria-hidden="true">
        <IconeAssistant />
      </span>
      <div className="flex min-w-0 flex-1 flex-col gap-3">{children}</div>
    </div>
  );
}

// attente longue (jusqu'à plusieurs dizaines de secondes, contrat §7) : le temps écoulé est affiché, sans être
// annoncé à chaque seconde aux lecteurs d'écran
function Attente({ texte, debut }) {
  const [ecoule, setEcoule] = useState(0);
  useEffect(() => {
    if (!debut) return;
    const minuterie = setInterval(() => setEcoule(Math.floor((performance.now() - debut) / 1000)), 1000);
    return () => clearInterval(minuterie);
  }, [debut]);
  return (
    <BulleAssistant>
      <p className="flex items-center gap-2.5 py-1.5 text-[15px] text-gris">
        <span className="h-2 w-2 rounded-full bg-accent motion-safe:animate-pulse" aria-hidden="true" />
        {texte}
        {debut && ecoule >= 3 && <span aria-hidden="true" className="tabular-nums"> · {ecoule} s</span>}
      </p>
      {debut && ecoule >= 10 && (
        <p className="text-[13px] text-gris">
          Le modèle s'exécute sur cet ordinateur : la première réponse peut prendre près d'une minute, le temps de le
          charger.
        </p>
      )}
    </BulleAssistant>
  );
}

function BoutonCitation({ reference, source, montrer }) {
  return (
    <button
      type="button"
      onClick={() => montrer(reference)}
      className="mx-0.5 inline-flex items-center rounded-md bg-accent-clair px-1.5 align-baseline text-[13px] font-semibold text-accent-texte hover:bg-accent hover:text-white focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-accent"
    >
      {numero(reference)}
      <span className="sr-only"> : voir le passage « {source.titre_fiche} »</span>
    </button>
  );
}

function Morceaux({ liste, sources, montrer }) {
  return liste.map((m, i) =>
    m.reference ? (
      <BoutonCitation key={i} reference={m.reference} source={sources.get(m.reference)} montrer={montrer} />
    ) : (
      <span key={i}>{m.texte}</span>
    ),
  );
}

function TexteCite({ reponse, montrer }) {
  const valides = referencesValides(reponse);
  const sources = new Map(reponse.sources.map((s) => [s.reference, s]));
  return (
    <div className="flex flex-col gap-2.5 rounded-[16px] rounded-tl-md border border-filet bg-white px-4 py-3.5 text-[15px] leading-relaxed">
      {blocs(reponse.reponse, valides).map((b, i) =>
        b.type === "liste" ? (
          <ul key={i} className="flex list-disc flex-col gap-1 pl-5">
            {b.elements.map((e, j) => (
              <li key={j}>
                <Morceaux liste={e} sources={sources} montrer={montrer} />
              </li>
            ))}
          </ul>
        ) : (
          <p key={i}>
            <Morceaux liste={b.morceaux} sources={sources} montrer={montrer} />
          </p>
        ),
      )}
    </div>
  );
}

function ListePassages({ echange, sources }) {
  return (
    <ol className="flex flex-col gap-3">
      {sources.map((s) => (
        <li key={s.passage_id}>
          <Passage passage={s} id={idCarte(echange.id, s.reference)} surligne={echange.surligne === s.reference} />
        </li>
      ))}
    </ol>
  );
}

function BoutonBascule({ ouvert, basculer, texteOuvrir, texteFermer }) {
  return (
    <button
      type="button"
      onClick={basculer}
      aria-expanded={ouvert}
      className="self-start text-sm font-semibold text-accent underline underline-offset-[3px] hover:text-accent-fonce focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
    >
      {ouvert ? texteFermer : texteOuvrir}
    </button>
  );
}

function Erreur({ titre, message, detail, reessayer }) {
  return (
    <div role="alert" className="rounded-[14px] border border-red-200 bg-red-50 px-4 py-3 text-[15px] text-red-800">
      <p className="font-semibold">{titre}</p>
      {message && <p className="mt-1 text-sm">{message}</p>}
      <div className="mt-2 flex flex-wrap items-center gap-3 text-sm">
        {reessayer && (
          <button
            type="button"
            onClick={reessayer}
            className="rounded-lg bg-red-700 px-3 py-1.5 font-medium text-white hover:bg-red-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-700"
          >
            Réessayer
          </button>
        )}
        {detail && (
          <details className="text-xs">
            <summary className="cursor-pointer">Détail technique</summary>
            <code className="mt-1 block whitespace-pre-wrap break-all">{detail}</code>
          </details>
        )}
      </div>
    </div>
  );
}

// d'où vient la réponse : une trace rejouée par la maquette n'est jamais présentée comme une nouvelle exécution
function Provenance({ reponse }) {
  const o = reponse.mesures?.ollama;
  let texte;
  if (reponse.trace?.simulee) texte = "Cas simulé à la main pour la maquette : aucun modèle n'a été exécuté.";
  else if (reponse.trace) {
    texte = `Réponse enregistrée lors d'un essai de la chaîne (${reponse.trace.id_question}, Ollama ${reponse.trace.ollama}), rejouée par la maquette : ce n'est pas une nouvelle exécution.`;
    if (o) texte += ` Lors de cet essai, Ollama a mis ${secondes(o.total_duration)} s, dont ${secondes(o.load_duration)} s de chargement du modèle.`;
  } else if (reponse.modele) {
    const duree = reponse.mesures?.duree_totale_s;
    texte = `Rédigée sur cet ordinateur par ${reponse.modele.nom}${duree != null ? ` en ${duree.toLocaleString("fr-FR", { maximumFractionDigits: 1 })} s` : ""}.`;
  }
  return texte ? <p className="text-[13px] leading-normal text-gris">{texte}</p> : null;
}

export default function Reponse({ echange, basculer, montrer, reessayer }) {
  if (echange.statut === "attente") return <Attente texte="Votre question est gardée : elle partira dès que l'assistant sera prêt." />;
  if (echange.statut === "envoi") return <Attente texte="Recherche des passages, puis rédaction de la réponse…" debut={echange.debut} />;
  if (echange.statut === "echec") {
    const e = echange.erreurAppel;
    return (
      <BulleAssistant>
        <Erreur
          titre={e.type === "maquette" ? "Pas de réponse enregistrée pour cette question." : "La question n'a pas pu aboutir."}
          message={e.message}
          reessayer={e.type === "maquette" ? null : () => reessayer(echange.id)}
        />
      </BulleAssistant>
    );
  }

  const r = echange.reponse;
  const voir = (reference) => montrer(echange.id, reference);
  const citees = r.sources.filter((s) => s.citee);
  const autres = r.sources.filter((s) => !s.citee);

  if (r.statut === "erreur_technique" || r.statut === "erreur_preparation") {
    return (
      <BulleAssistant>
        <Erreur
          titre={r.statut === "erreur_preparation" ? "L'assistant n'a pas pu préparer la réponse." : "La réponse a été interrompue ou est incohérente."}
          message="Réessayez. Si le problème continue, vérifiez que la chaîne locale (Ollama et le modèle) est lancée."
          detail={[r.erreur && `${r.erreur.type} : ${r.erreur.message}`, r.reponse && `Réponse reçue :\n${r.reponse}`].filter(Boolean).join("\n\n")}
          reessayer={() => reessayer(echange.id)}
        />
        <Provenance reponse={r} />
      </BulleAssistant>
    );
  }

  if (r.statut === "abstention_modele") {
    return (
      <BulleAssistant>
        <div className="rounded-[14px] border border-alerte-bord bg-alerte-fond px-4 py-3.5">
          <p className="text-[15px] font-semibold leading-normal">
            Je ne peux pas répondre à cette question à partir des fiches consultées.
          </p>
          <p className="mt-1 text-sm leading-relaxed text-texte">
            Les passages trouvés ne contiennent pas l'information. La question sort peut-être du périmètre des fiches
            pratiques du droit du travail : reformulez-la en décrivant votre situation, ou consultez les passages.
          </p>
          <div className="mt-2">
            <BoutonBascule
              ouvert={echange.afficher}
              basculer={() => basculer(echange.id)}
              texteOuvrir={`Afficher les ${r.sources.length} passages consultés`}
              texteFermer="Masquer les passages"
            />
          </div>
        </div>
        {echange.afficher && <ListePassages echange={echange} sources={r.sources} />}
        <Provenance reponse={r} />
      </BulleAssistant>
    );
  }

  if (r.statut === "sortie_invalide") {
    return (
      <BulleAssistant>
        <div className="rounded-[14px] border border-alerte-bord bg-alerte-fond px-4 py-3.5">
          <p className="text-[15px] font-semibold leading-normal">Réponse non conforme : elle n'est pas affichée comme fiable.</p>
          <p className="mt-1 text-sm leading-relaxed text-texte">
            Ses références aux passages sont absentes ou mal formées
            {r.citations_invalides.length > 0 && <> ({r.citations_invalides.join(", ")})</>}. Reformulez la question,
            ou consultez directement les passages.
          </p>
          <details className="mt-2 text-sm">
            <summary className="cursor-pointer font-semibold text-accent">Voir la réponse brute</summary>
            <p className="mt-1 whitespace-pre-line text-texte">{r.reponse}</p>
          </details>
          <div className="mt-2">
            <BoutonBascule
              ouvert={echange.afficher}
              basculer={() => basculer(echange.id)}
              texteOuvrir={`Afficher les ${r.sources.length} passages consultés`}
              texteFermer="Masquer les passages"
            />
          </div>
        </div>
        {echange.afficher && <ListePassages echange={echange} sources={r.sources} />}
        <Provenance reponse={r} />
      </BulleAssistant>
    );
  }

  // reponse_citee
  return (
    <BulleAssistant>
      <TexteCite reponse={r} montrer={voir} />
      {citees.length > 0 && (
        <>
          <h3 className="text-xs font-semibold uppercase tracking-wide text-gris">
            {citees.length > 1 ? `Les ${citees.length} passages cités` : "Le passage cité"}
          </h3>
          <ListePassages echange={echange} sources={citees} />
        </>
      )}
      {autres.length > 0 && (
        <BoutonBascule
          ouvert={echange.afficher}
          basculer={() => basculer(echange.id)}
          texteOuvrir={`Voir ${autres.length > 1 ? `les ${autres.length} autres passages consultés` : "l'autre passage consulté"}`}
          texteFermer="Masquer les autres passages"
        />
      )}
      {echange.afficher && <ListePassages echange={echange} sources={autres} />}
      <p className="text-[13px] leading-normal text-gris">
        Les références renvoient aux passages fournis à l'assistant ; elles ne garantissent pas que chaque phrase soit
        justifiée par son passage. Vérifiez dans la fiche. Cette réponse n'est pas un conseil juridique.
      </p>
      <Provenance reponse={r} />
    </BulleAssistant>
  );
}
