// État de la chaîne locale du volet B (#111), comme useMoteur.js au volet A : vérification au démarrage
// (GET /api/etat), prête ou indisponible, et fonction pour poser une question. En mode maquette (npm run maquette),
// les mêmes fonctions rejouent les traces enregistrées, sans couche locale ni Ollama.

import { useCallback, useEffect, useState } from "react";
import * as couche from "./couche.js";
import * as maquette from "./maquette.js";

export const MAQUETTE = import.meta.env.MODE === "maquette";
const api = MAQUETTE ? maquette : couche;

// questions de calibration de la #85 (jeu-questions-v1), reprises mot pour mot ; le scénario de démonstration
// (étape 4 de #111) fixera les questions définitives
const EXEMPLES_CHAINE = [
  { question: "Quelles sont les obligations légales de l'empoyeur en période de forte chaleur ?", libelle: null },
  { question: "Un fonctionnaire peut-il avoir une autre activité à coté de son travail ?", libelle: null },
];

export function useChaine() {
  const [etat, setEtat] = useState({ phase: "verification", details: null, erreur: null });
  const [exemples, setExemples] = useState(MAQUETTE ? [] : EXEMPLES_CHAINE);
  const [essai, setEssai] = useState(0);

  useEffect(() => {
    let abandonne = false;
    setEtat({ phase: "verification", details: null, erreur: null });
    (async () => {
      try {
        const details = await api.lireEtat();
        if (MAQUETTE) {
          const liste = await maquette.questionsExemples();
          if (!abandonne) setExemples(liste);
        }
        if (abandonne) return;
        // pret à false : la couche répond, mais un élément manque (index, E5, tokeniseur, Ollama) ; message en français
        setEtat(details.pret
          ? { phase: "pret", details, erreur: null }
          : { phase: "indisponible", details, erreur: details.message ?? "La chaîne locale n'est pas prête." });
      } catch (e) {
        if (!abandonne) setEtat({ phase: "indisponible", details: null, erreur: e.message });
      }
    })();
    return () => { abandonne = true; };
  }, [essai]);

  const poser = useCallback((question) => api.poserQuestion(question), []);
  const reessayer = useCallback(() => setEssai((n) => n + 1), []);

  return { ...etat, maquette: MAQUETTE, exemples, poser, reessayer };
}
