// Site du volet A : recherche sémantique dans les fiches pratiques, exécutée dans le navigateur (#29, #48). Depuis
// #53, l'application occupe tout l'écran, comme la maquette B validée par l'équipe : voir composants/Conversation.jsx.

import Conversation from "./composants/Conversation.jsx";
import { useMoteur } from "./recherche/useMoteur.js";

export default function App() {
  const moteur = useMoteur();
  return <Conversation moteur={moteur} />;
}
