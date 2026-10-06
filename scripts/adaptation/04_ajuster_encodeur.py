"""
scripts/adaptation/04_ajuster_encodeur.py
Ajustement fin (fine-tuning contrastif) de multilingual-e5-small sur le corpus SocialGouv.
Utilise MultipleNegativesRankingLoss (négatifs in-batch) et préserve les préfixes "query: " et "passage: ".
"""

import json
import os
import sys
import time
from pathlib import Path
import torch
from sentence_transformers import (
    SentenceTransformer,
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments,
    losses,
)
from datasets import Dataset

# Standard d'import du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    print("[1/5] Chargement des paires d'entraînement synthétiques...")
    train_file = "data/adaptation/train_paires.jsonl"
    paires = []
    with open(train_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                paires.append(json.loads(line.strip()))

    print(f"       Nombre de paires d'entraînement chargées : {len(paires)}")

    # Préparation du dataset HuggingFace / SentenceTransformers
    # Les paires doivent comporter query et passage préfixés
    dataset_dict = {
        "anchor": [p["query"] for p in paires],       # "query: ..."
        "positive": [p["passage"] for p in paires],   # "passage: ..."
    }
    train_dataset = Dataset.from_dict(dataset_dict)

    print("[2/5] Chargement du modèle de base intfloat/multilingual-e5-small...")
    model_id = "intfloat/multilingual-e5-small"
    model = SentenceTransformer(model_id)

    print("[3/5] Configuration de la fonction de perte contrastive (MultipleNegativesRankingLoss)...")
    # MultipleNegativesRankingLoss utilise les passages des autres requêtes du batch comme négatifs
    loss = losses.MultipleNegativesRankingLoss(model)

    output_dir = "models/multilingual-e5-small-finetuned"
    os.makedirs(output_dir, exist_ok=True)

    # Hyperparamètres d'entraînement scientifiquement justifiés :
    # - batch_size = 16 (fournit 15 négatifs in-batch par exemple)
    # - lr = 2e-5 (fine-tuning conservateur prévenant l'oubli catastrophique)
    # - epochs = 2 (évite le surapprentissage sur les formulations synthétiques)
    # - warmup_ratio = 0.1
    epochs = 2
    batch_size = 16
    learning_rate = 2e-5

    print(f"[4/5] Lancement de l'ajustement (epochs={epochs}, batch_size={batch_size}, lr={learning_rate})...")
    training_args = SentenceTransformerTrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        warmup_ratio=0.1,
        weight_decay=0.01,
        logging_steps=2,
        save_strategy="no",
        seed=42,
        report_to="none",
    )

    trainer = SentenceTransformerTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        loss=loss,
    )

    t0 = time.time()
    train_result = trainer.train()
    training_time = time.time() - t0
    print(f"       Entraînement terminé en {training_time:.2f}s.")

    print(f"[5/5] Sauvegarde du modèle ajusté dans {output_dir}...")
    model.save_pretrained(output_dir)

    # Sauvegarde du rapport d'entraînement
    history = trainer.state.log_history
    rapport = {
        "modele_source": model_id,
        "n_paires_entrainement": len(paires),
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "temps_entrainement_sec": round(training_time, 2),
        "train_loss_finale": train_result.training_loss,
        "log_history": history,
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open("data/adaptation/rapport_entrainement.json", "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)

    print("Rapport d'entraînement sauvegardé dans data/adaptation/rapport_entrainement.json.")


if __name__ == "__main__":
    main()
