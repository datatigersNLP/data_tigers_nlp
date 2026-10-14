// Chargement du moteur de recherche dans le site (#48) : index vérifié, puis modèle téléchargé une fois et mis en
// cache par le navigateur. Le hook expose la phase (chargement, prêt, erreur), la progression du téléchargement et
// la fonction de recherche.

import { useCallback, useEffect, useRef, useState } from "react";
import { creerMoteur, horsPerimetre } from "./moteur.js";

// dossiers de l'index et du modèle dans le site : sous le chemin de base de GitHub Pages en ligne, à la racine en local
const DOSSIER_INDEX = import.meta.env.BASE_URL + "index/";
const DOSSIER_MODELES = import.meta.env.BASE_URL + "modele/";

// message lisible par un visiteur, selon l'origine de l'erreur ; le détail technique reste affichable
export function messageErreur(erreur) {
  const texte = String(erreur?.message ?? erreur);
  if (!globalThis.crypto?.subtle)
    return "Cette page doit être ouverte en HTTPS (ou sur localhost) : le navigateur refuse sinon de vérifier l'index.";
  if (/empreinte|format d'index|octets|passages, attendu|index_m2/.test(texte))
    return "L'index de recherche est indisponible ou incohérent. Réessayez plus tard.";
  if (/fetch|network|réseau|Failed|NetworkError|load/i.test(texte))
    return "Le modèle n'a pas pu être téléchargé. Vérifiez votre connexion internet, puis réessayez.";
  return "La recherche n'a pas pu démarrer. Réessayez, ou rechargez la page.";
}

export function useMoteur() {
  const [etat, setEtat] = useState({ phase: "chargement", progression: null, erreur: null });
  const [essai, setEssai] = useState(0);
  const moteur = useRef(null);

  useEffect(() => {
    let abandonne = false;
    // progression affichée : celle du modèle ONNX q8 (65,7 Mio, élagué sans perte) dès qu'il est en cours, sinon celle
    // du vocabulaire du tokeniseur (4,1 Mio). Les deux se téléchargent en parallèle : un cumul afficherait un total faux
    const fichiers = new Map();
    setEtat({ phase: "chargement", progression: null, erreur: null });

    (async () => {
      try {
        // import différé : Transformers.js n'est chargé qu'une fois la page affichée
        const { pipeline, env } = await import("@huggingface/transformers");
        // l'en-tête de l'index dit d'où vient le modèle : du site (dossier DOSSIER_MODELES) ou du Hub ; moteur.js
        // règle env en conséquence
        const instance = await creerMoteur(pipeline, DOSSIER_INDEX, {
          env,
          dossierModeles: DOSSIER_MODELES,
          suivre: (p) => {
            if (abandonne || p.status !== "progress" || !p.file || !p.total) return;
            if (p.total < 2 ** 20) return; // fichiers de configuration : quelques Kio, sans intérêt pour le visiteur
            fichiers.set(p.file, { charge: p.loaded, total: p.total });
            const modele = [...fichiers.keys()].find((f) => f.endsWith(".onnx"));
            const [fichier, suivi] = modele ? [modele, fichiers.get(modele)] : [...fichiers.entries()][0];
            const quoi = fichier.endsWith(".onnx") ? "du modèle de recherche" : "du vocabulaire du modèle";
            setEtat((e) => ({ ...e, progression: { quoi, ...suivi } }));
          },
        });
        if (abandonne) return;
        moteur.current = instance;
        setEtat({ phase: "pret", progression: null, erreur: null });
      } catch (erreur) {
        if (!abandonne) setEtat({ phase: "erreur", progression: null, erreur });
      }
    })();

    return () => { abandonne = true; };
  }, [essai]);

  // horsPerimetre : le meilleur passage reste sous le seuil d'abstention du modèle servi (moteur.js, ABSTENTION)
  const rechercher = useCallback(async (question, k = 5) => {
    const debut = performance.now();
    const resultats = await moteur.current.rechercher(question, k);
    return { resultats, duree: performance.now() - debut,
      horsPerimetre: horsPerimetre(resultats, moteur.current.seuilAbstention) };
  }, []);

  const reessayer = useCallback(() => setEssai((n) => n + 1), []);

  return { ...etat, nbPassages: moteur.current?.nbPassages, rechercher, reessayer };
}
