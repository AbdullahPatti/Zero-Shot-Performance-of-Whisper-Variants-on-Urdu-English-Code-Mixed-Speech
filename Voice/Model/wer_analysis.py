import os
import pandas as pd
from jiwer import wer


RESULTS_DIR = "Results"

MODELS = ["tiny", "base", "small"]
MODES = ["urdu", "english", "guess"]


def get_results_filepath(model, mode, results_dir=RESULTS_DIR):
    if mode == "urdu":
        return os.path.join(results_dir, f"Results_{model.capitalize()}.csv")
    elif mode == "english":
        return os.path.join(results_dir, f"Results_{model.capitalize()}_English.csv")
    else:
        return os.path.join(results_dir, f"Results_{model.capitalize()}_Guess.csv")


def compute_wer_for_all(results_dir=RESULTS_DIR):
    all_results_summary = []

    for model in MODELS:
        for mode in MODES:
            file_path = get_results_filepath(model, mode, results_dir)
            try:
                df = pd.read_csv(file_path)
                df["wer"] = df.apply(
                    lambda r: wer(
                        str(r["reference"]).lower().strip(),
                        str(r["hypothesis"]).lower().strip(),
                    ),
                    axis=1,
                )

                output_path = os.path.join(results_dir, f"wer_{model}_{mode}.csv")
                df.to_csv(output_path, index=False)

                mean_wer = df["wer"].mean()
                print(f"{model.capitalize()} {mode}: mean WER = {mean_wer:.4f}")
                all_results_summary.append({
                    "Model": model.capitalize(),
                    "Mode": mode.capitalize(),
                    "Mean WER": mean_wer,
                })

            except FileNotFoundError:
                print(f"File not found: {file_path}. Skipping.")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    if all_results_summary:
        summary_df = pd.DataFrame(all_results_summary)
        pivot = summary_df.pivot(index="Model", columns="Mode", values="Mean WER")
        print("\nSummary of Mean WERs:")
        print(pivot)
        return summary_df
    return None


def compute_wer_statistics(results_dir=RESULTS_DIR):
    import numpy as np

    stats_list = []

    for model in MODELS:
        for mode in MODES:
            file_path = os.path.join(results_dir, f"wer_{model}_{mode}.csv")
            try:
                df = pd.read_csv(file_path)
                if "wer" not in df.columns:
                    continue

                wer_vals = pd.to_numeric(df["wer"], errors="coerce").dropna()
                if len(wer_vals) == 0:
                    continue

                stats_list.append({
                    "Model": model.capitalize(),
                    "Mode": mode.capitalize(),
                    "Mean": round(wer_vals.mean(), 4),
                    "Std Dev": round(wer_vals.std(), 4),
                    "Variance": round(wer_vals.var(), 4),
                    "CV (%)": round((wer_vals.std() / wer_vals.mean() * 100), 2) if wer_vals.mean() != 0 else np.nan,
                    "Min": round(wer_vals.min(), 4),
                    "Q1": round(wer_vals.quantile(0.25), 4),
                    "Median": round(wer_vals.median(), 4),
                    "Q3": round(wer_vals.quantile(0.75), 4),
                    "IQR": round(wer_vals.quantile(0.75) - wer_vals.quantile(0.25), 4),
                    "Max": round(wer_vals.max(), 4),
                    "Count": len(wer_vals),
                })
                print(f"{model.capitalize()} {mode}: mean WER = {wer_vals.mean():.4f}")

            except FileNotFoundError:
                print(f"File not found: {file_path}. Skipping.")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    if stats_list:
        stats_df = pd.DataFrame(stats_list)
        print("\n=== WER STATISTICAL SUMMARY ===")
        print(stats_df.to_string(index=False))

        stats_df.to_csv(os.path.join(results_dir, "ASR_Statistics_Summary.csv"), index=False)
        return stats_df
    return None


if __name__ == "__main__":
    print("=== Computing WER ===")
    compute_wer_for_all()
    print("\n=== Detailed Statistics ===")
    compute_wer_statistics()
