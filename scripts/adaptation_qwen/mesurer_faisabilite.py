"""Lance mlx_lm.lora dans ce processus et relève la durée totale et la mémoire de pointe du GPU (mx.get_peak_memory)."""
import sys, time, json
import mlx.core as mx
from mlx_lm import lora
couches, iters, dossier = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = ["mlx_lm.lora", "--model", "data/volet_b/qwen25-7b-instruct-4bit-mlx", "--train",
            "--data", "data/volet_b/essai_faisabilite", "--fine-tune-type", "lora", "--num-layers", couches,
            "--batch-size", "1", "--iters", iters, "--max-seq-length", "3072", "--grad-checkpoint", "--mask-prompt",
            "--learning-rate", "1e-5", "--steps-per-report", "100", "--steps-per-eval", "1000", "--val-batches", "1",
            "--seed", "20261023", "--adapter-path", dossier]
t0 = time.perf_counter(); lora.main(); duree = time.perf_counter() - t0
print("MESURE " + json.dumps({"couches": int(couches), "iters": int(iters), "duree_s": round(duree, 1),
                              "pic_memoire_gio": round(mx.get_peak_memory() / 2**30, 2)}))
