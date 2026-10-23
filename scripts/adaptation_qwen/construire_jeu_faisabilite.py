"""Jeu factice de faisabilité pour #107 : format exact du contexte de la #85, 5 passages réels tirés au hasard.
Ce ne sont PAS des données d'entraînement : la réponse est une phrase fixe ; seul le coût mémoire et temps est mesuré."""
import json, random, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])  # scripts/rag de la PR #85 (construire_contexte), à fusionner avant usage
import rag
passages = json.load(open(sys.argv[2], encoding="utf-8"))
sortie = Path(sys.argv[3]); sortie.mkdir(parents=True, exist_ok=True)
tirage = random.Random(20261023)
def exemple():
    choisis = tirage.sample(passages, 5)
    resultats = [{"rang": r, "indice": 0, "score": 0.0, "passage": p} for r, p in enumerate(choisis, 1)]
    question = f"Que prévoit la fiche « {choisis[0]['titre_fiche']} » sur ce point : {choisis[0]['section_titre']} ?"
    ctx = rag.construire_contexte(question, resultats)
    return {"messages": [{"role": "system", "content": ctx["system"]}, {"role": "user", "content": ctx["prompt"]},
                         {"role": "assistant", "content": "Selon la fiche fournie, les conditions applicables sont décrites dans le premier passage [P1]."}]}
for nom, n in (("train", 24), ("valid", 4)):
    with open(sortie / f"{nom}.jsonl", "w", encoding="utf-8") as f:
        for _ in range(n): f.write(json.dumps(exemple(), ensure_ascii=False) + "\n")
print("jeu écrit dans", sortie)
