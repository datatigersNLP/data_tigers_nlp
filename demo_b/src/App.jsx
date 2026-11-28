// Interface de la démonstration du volet B (#111) : assistant local sourcé, au parcours et à la charte du site du
// volet A (#53). Les réponses viennent de la couche locale (contrat de la #121), ou des traces enregistrées en mode
// maquette : voir composants/Conversation.jsx et api/useChaine.js.

import Conversation from "./composants/Conversation.jsx";
import { useChaine } from "./api/useChaine.js";

export default function App() {
  const chaine = useChaine();
  return <Conversation chaine={chaine} />;
}
