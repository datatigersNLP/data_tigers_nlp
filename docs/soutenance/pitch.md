---
marp: true
lang: fr
title: "Data Tigers, pitch de soutenance"
size: 16:9
paginate: true
header: "Data Tigers · NLP 2 · soutenance du 30 novembre 2026"
footer: "Pitch · 4 minutes"
style: |
  section {
    background: #ffffff; color: #111827;
    font-family: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
    font-size: 25px; line-height: 1.4;
    padding: 64px 70px 52px;
    display: flex; flex-direction: column; justify-content: flex-start;
  }
  header, footer { color: #5b6472; font-size: 15px; }
  section::after { color: #5b6472; font-size: 15px; }
  h1 { color: #1f3b73; font-size: 37px; line-height: 1.2; margin: 0 0 22px; font-weight: 700; }
  strong { color: #1f3b73; }
  ul, ol { margin: 0; padding-left: 1.1em; }
  li { margin: 0 0 10px; }
  .def { margin-top: auto; border-top: 2px solid #1f3b73; padding-top: 8px; font-size: 17px; line-height: 1.35; color: #374151; }
  .def b { color: #1f3b73; }
  .colonnes { display: grid; grid-template-columns: 1fr 1fr; gap: 34px; }
  .bloc { border: 1px solid #d7dbe0; border-top: 4px solid #1f3b73; padding: 12px 16px; font-size: 22px; }
  .bloc.b { border-top-color: #2e6a4f; }
  .bloc h3 { margin: 0 0 8px; font-size: 24px; color: #1f3b73; }
  .bloc.b h3 { color: #2e6a4f; }
  .question { border-left: 4px solid #1f3b73; padding: 6px 14px; background: #f3f5f8; font-size: 24px; margin: 6px 0 16px; }
  section.titre { justify-content: center; }
  section.titre h1 { font-size: 54px; margin-bottom: 10px; }
  .sous-titre { font-size: 29px; color: #1f3b73; margin-bottom: 34px; }
  .equipe { font-size: 21px; color: #374151; }
---

<!-- _class: titre -->
<!-- _paginate: false -->

# Data Tigers

<div class="sous-titre">Trouver la règle, citer sa source : deux outils sur les fiches du droit du travail</div>

<div class="equipe">Mahé BEGNIS · Remy RAYANE · Jibril BENSALEM · Vaneck DAGAR · Maïmouna SIGNATE<br>Master 2 Data &amp; IA, FGES, Université Catholique de Lille · module NLP 2</div>

<!--
Durée visée : 10 s
À dire : Bonjour, nous sommes les Data Tigers. En quatre minutes : le problème, pour qui, et ce que nous livrons.
-->

---

# Les règles du travail sont publiques, mais difficiles à trouver

- Le ministère du Travail publie **261 fiches pratiques**, en licence ouverte : contrat, congés, rupture, santé, représentants du personnel.
- Une question réelle :

<div class="question">« Est-ce légal de travailler 10 heures dans la même journée ? »</div>

- La réponse existe, mais au milieu d'une fiche de plusieurs pages, **avec ses conditions et ses exceptions**.
- Un assistant conversationnel généraliste répond toujours, avec assurance, même quand il ne sait pas : il peut **inventer une règle**.

<div class="def"><b>Fiche pratique</b> : page du site du ministère qui explique une règle du Code du travail en langage courant. Notre corpus en est un instantané du 11/09/2026.</div>

<!--
Durée visée : 45 s
À dire : Le droit du travail est public. Le ministère publie 261 fiches pratiques, sous licence ouverte, sur le contrat, les congés, la rupture ou les représentants du personnel. Prenons une vraie question : est-ce légal de travailler dix heures dans la même journée ? La réponse existe, mais elle se trouve au milieu d'une longue fiche, avec des conditions et des exceptions qu'il ne faut pas perdre. Et si l'on interroge un assistant conversationnel généraliste, il répond toujours, avec assurance, même quand il ne sait pas. Il peut inventer une règle, ce qui est grave en droit.
Questions probables :
- Pourquoi ces fiches ? Elles sont publiques, structurées, à jour, et sous Licence Ouverte Etalab 2.0 ; elles couvrent les questions les plus courantes.
- La réponse à la question des 10 heures ? 10 heures de travail effectif par jour au plus, sauf dans les cas prévus par le Code du travail, par exemple un accord collectif.
-->

---

# Pour qui, et avec quelles exigences

- **Les publics des fiches** : salariés, employeurs, représentants du personnel.
- **Leur besoin** : une réponse rapide, la règle exacte avec ses conditions, et la source pour la vérifier.
- **Deux exigences fortes**
  - la **confidentialité** : une question sur son travail est personnelle ;
  - la **fiabilité** : mieux vaut « je ne peux pas répondre » qu'une règle inventée.

<div class="def"><b>Abstention</b> : le système répond qu'il ne peut pas répondre, au lieu d'inventer. C'est une réponse correcte quand l'information n'est pas dans les fiches.</div>

<!--
Durée visée : 40 s
À dire : Nos utilisateurs sont les publics de ces fiches : des salariés, des employeurs, des représentants du personnel. Leur besoin est simple : une réponse rapide, la règle exacte avec ses conditions, et la source pour pouvoir vérifier. Deux exigences en découlent. La confidentialité, d'abord : une question sur son travail est personnelle et ne devrait pas partir chez un tiers. La fiabilité, ensuite : quand l'information n'est pas dans les fiches, il vaut mieux dire « je ne peux pas répondre » que d'inventer. C'est ce qu'on appelle l'abstention, et c'est le cœur de notre travail.
Questions probables :
- Avez-vous interrogé des utilisateurs ? Non, nous n'avons pas mené d'enquête : nous partons du public auquel le ministère destine ces fiches, et des questions réelles de notre jeu d'évaluation.
-->

---

# Deux réponses complémentaires au même besoin

<div class="colonnes">
<div class="bloc">

### Volet A : chercher

- On pose sa question sur un **site web**.
- Le site affiche les **5 passages les plus proches**, avec leur section et un lien vers la fiche.
- Tout se calcule **dans le navigateur** : la question ne quitte pas l'ordinateur. Gratuit, sans serveur.

</div>
<div class="bloc b">

### Volet B : répondre en citant

- Un **modèle de langage installé sur la machine** lit les passages trouvés.
- Il rédige une réponse courte et **cite chaque source** : [P1], [P2]…
- Si les passages ne suffisent pas, il **s'abstient**.

</div>
</div>

<div class="def"><b>Passage</b> : extrait d'une section de fiche, 259 tokens en moyenne (un token est un morceau de mot). <b>Modèle de langage</b> : programme qui génère du texte token par token ; ici Qwen2.5-7B-Instruct, 7,6 milliards de paramètres.</div>

<!--
Durée visée : 75 s
À dire : Nous livrons deux outils complémentaires, construits sur le même corpus. Le volet A sert à chercher : on pose sa question sur un site web, et le site affiche les cinq passages des fiches les plus proches du sens de la question, avec leur section et un lien vers la fiche complète. Tout le calcul se fait dans le navigateur : la question ne quitte pas l'ordinateur, il n'y a aucun serveur, et c'est gratuit. Le volet B sert à répondre : un modèle de langage installé sur la machine lit les passages trouvés, rédige une réponse courte, et cite chaque passage qu'il utilise, comme P1 ou P2. Si les passages ne permettent pas de répondre, il s'abstient. Le premier outil ne génère rien, il montre les textes ; le second génère, mais il doit justifier chaque phrase.
Questions probables :
- Pourquoi deux volets ? C'est le sujet : un modèle léger et maîtrisé dans le navigateur, et un modèle plus puissant en local. Nous avons choisi deux cas qui partagent le même corpus et la même recherche.
- Le volet B envoie-t-il des données ? Non : Qwen tourne sous Ollama sur la machine, sans aucune API distante.
-->

---

# Ce qui est démontré, mesures à l'appui

- **Volet A** : aussi bon que la recherche classique par mots-clés (BM25) pour trouver le bon passage : **43,8 %** contre 42,5 %, non-infériorité démontrée. Un modèle de **65,7 Mio** chargé dans le navigateur, une recherche en **21 ms** (médiane).
- **Volet B** : après adaptation du modèle, les réponses qui citent un passage pertinent passent de **13,9 % à 25,0 %** : amélioration démontrée, sans perte observée hors du corpus. Leur exactitude, jugée à l'aveugle, ne progresse pas.
- **Méthode** : chaque mesure suit un protocole **écrit et figé avant** d'être exécutée.

<div class="def"><b>Non-infériorité</b> : on démontre que le site n'est pas moins bon que BM25 de 15 points ou plus ; cela ne dit pas qu'il est meilleur. <b>Démontrée</b> : l'intervalle de confiance de l'écart reste entièrement au-dessus de 0.</div>

<!--
Durée visée : 55 s
À dire : Qu'avons-nous démontré ? Pour le volet A, la recherche par le sens est aussi bonne que la recherche classique par mots-clés, BM25 : le bon passage est dans les cinq premiers résultats pour 43,8 % des questions, contre 42,5 %. Nous démontrons la non-infériorité, pas la supériorité. Le modèle, chargé dans le navigateur, pèse 65,7 mébioctets, et une recherche prend une vingtaine de millisecondes. Pour le volet B, après adaptation du modèle, les réponses qui citent un passage pertinent passent de 13,9 à 25 % : l'amélioration est démontrée, sans perte observée sur les questions hors du corpus. En revanche, un jugement humain à l'aveugle ne trouve pas de réponses plus exactes. Et chaque mesure suit un protocole écrit avant de mesurer. Place à la démonstration.
Questions probables :
- 25 %, c'est peu ? Oui. Le système reste prudent : sur les questions couvertes, il s'abstient encore à tort dans 55,6 % des cas. C'est notre principale limite, et notre feuille de route (récupération v2) la traite.
- L'exactitude ? Deux membres l'ont jugée à l'aveugle : réponses mieux appuyées sur leurs passages, mais pas plus exactes, souvent incomplètes.
- Mio ? Mébioctet, 2 puissance 20 octets, environ 1,05 mégaoctet.
-->
