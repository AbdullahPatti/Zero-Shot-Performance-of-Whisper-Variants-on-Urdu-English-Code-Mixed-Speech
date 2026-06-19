import os
import pandas as pd
import torch
from tqdm import tqdm
from transformers import pipeline


AUDIO_DIR = "Processed_Recordings"
REF_CSV = "References/references.csv"
RESULTS_DIR = "Results"

MODELS = {
    "tiny": "openai/whisper-tiny",
    "base": "openai/whisper-base",
    "small": "openai/whisper-small",
}

MODES = {
    "urdu": {"language": "urdu", "task": "transcribe"},
    "english": {"language": "english", "task": "transcribe"},
    "guess": {"task": "transcribe"},
}


def transcribe(model_name, mode_name, audio_dir=AUDIO_DIR, ref_csv=REF_CSV, output_dir=RESULTS_DIR):
    os.makedirs(output_dir, exist_ok=True)
    ref = pd.read_csv(ref_csv)

    model_id = MODELS[model_name]
    generate_kwargs = MODES[mode_name]

    print(f"Loading Whisper {model_name.capitalize()} ({mode_name} mode)...")
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model_id,
        generate_kwargs=generate_kwargs,
        device=0 if torch.cuda.is_available() else -1,
    )

    results = []
    for _, row in tqdm(ref.iterrows(), total=len(ref)):
        path = os.path.join(audio_dir, row["filename"])
        try:
            hyp = pipe(path)["text"].strip()
        except Exception as e:
            hyp = ""
            print(f"Error on {row['filename']}: {e}")
        results.append({
            "filename": row["filename"],
            "speaker": row["speaker"],
            "category": row["category"],
            "reference": row["reference"],
            "hypothesis": hyp,
        })

    df = pd.DataFrame(results)

    if mode_name == "urdu":
        output_file = f"Results_{model_name.capitalize()}.csv"
    elif mode_name == "english":
        output_file = f"Results_{model_name.capitalize()}_English.csv"
    else:
        output_file = f"Results_{model_name.capitalize()}_Guess.csv"

    output_path = os.path.join(output_dir, output_file)
    df.to_csv(output_path, index=False)
    print(f"Done. {len(df)} files transcribed. Saved to {output_path}")
    return df


def run_all():
    for model_name in MODELS:
        for mode_name in MODES:
            transcribe(model_name, mode_name)


if __name__ == "__main__":
    run_all()
