import os
import pandas as pd


RESULTS_DIR = "Results"
ANN_CSV = "References/annotations.csv"

MODELS = ["tiny", "base", "small"]
MODES = ["urdu", "english", "guess"]


def get_switch_positions(tags):
    positions = set()
    tag_list = str(tags).strip().split()
    for i in range(1, len(tag_list)):
        if tag_list[i] != tag_list[i - 1]:
            positions.add(i - 1)
            positions.add(i)
    return positions


def compute_sper(ref, hyp, tags):
    sw_pos = get_switch_positions(tags)
    if not sw_pos:
        return 0.0

    try:
        ref_words = str(ref).lower().strip().split()
        hyp_words = str(hyp).lower().strip().split()

        errors = 0
        total_sw = len(sw_pos)

        for pos in sw_pos:
            if pos < len(ref_words) and pos < len(hyp_words):
                if ref_words[pos] != hyp_words[pos]:
                    errors += 1
            elif pos < len(ref_words) or pos < len(hyp_words):
                errors += 1

        return round(errors / total_sw, 4) if total_sw > 0 else 0.0
    except Exception:
        return 0.0


def compute_sper_for_all(results_dir=RESULTS_DIR, ann_csv=ANN_CSV):
    ann = pd.read_csv(ann_csv)
    all_results = []

    for model in MODELS:
        for mode in MODES:
            wer_file = os.path.join(results_dir, f"wer_{model}_{mode}.csv")
            try:
                df = pd.read_csv(wer_file)
                sper_vals = []

                for _, row in df.iterrows():
                    filename = str(row["filename"])
                    clean = filename.replace(".wav", "")
                    sid = clean.split("_")[-1]

                    ann_row = ann[ann["sentence_id"].astype(str) == sid]

                    if ann_row.empty:
                        sper_vals.append(0.0)
                    else:
                        tags = ann_row["lang_tags"].values[0]
                        sper = compute_sper(row["reference"], row["hypothesis"], tags)
                        sper_vals.append(sper)

                df["sper"] = sper_vals
                output_path = os.path.join(results_dir, f"sper_{model}_{mode}.csv")
                df.to_csv(output_path, index=False)

                mean_sper = pd.Series(sper_vals).mean()
                print(f"{model.capitalize()} {mode}: mean SPER = {mean_sper:.4f}")
                all_results.append({
                    "Model": model.capitalize(),
                    "Mode": mode.capitalize(),
                    "Mean SPER": mean_sper,
                })

            except FileNotFoundError:
                print(f"File not found: {wer_file}. Skipping.")
            except Exception as e:
                print(f"Error with {model} {mode}: {e}")

    if all_results:
        summary_df = pd.DataFrame(all_results)
        print("\nSPER Summary:")
        print(summary_df.pivot(index="Model", columns="Mode", values="Mean SPER"))
        return summary_df
    return None


def combined_summary(results_dir=RESULTS_DIR):
    summary = []

    for model in MODELS:
        for mode in MODES:
            try:
                wer_df = pd.read_csv(os.path.join(results_dir, f"wer_{model}_{mode}.csv"))
                sper_df = pd.read_csv(os.path.join(results_dir, f"sper_{model}_{mode}.csv"))

                summary.append({
                    "Model": model.capitalize(),
                    "Mode": mode.capitalize(),
                    "Mean WER": round(wer_df["wer"].mean(), 4),
                    "Mean SPER": round(sper_df["sper"].mean(), 4),
                })
            except Exception:
                pass

    if summary:
        summary_df = pd.DataFrame(summary)
        print("=== FINAL RESULTS SUMMARY ===")
        pivot = summary_df.pivot(index="Model", columns="Mode", values=["Mean WER", "Mean SPER"])
        print(pivot)
        return summary_df
    return None


if __name__ == "__main__":
    print("=== Computing SPER ===")
    compute_sper_for_all()
    print("\n")
    combined_summary()
