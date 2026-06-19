import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


RESULTS_DIR = "Results"
OUTPUT_DIR = "Images"

MODELS = ["tiny", "base", "small"]
MODES = ["urdu", "english", "guess"]


def load_summary_data(results_dir=RESULTS_DIR):
    data = []
    for model in MODELS:
        for mode in MODES:
            try:
                wer_df = pd.read_csv(os.path.join(results_dir, f"wer_{model}_{mode}.csv"))
                sper_df = pd.read_csv(os.path.join(results_dir, f"sper_{model}_{mode}.csv"))
                data.append({
                    "Model": model.capitalize(),
                    "Mode": mode.capitalize(),
                    "WER": wer_df["wer"].mean(),
                    "SPER": sper_df["sper"].mean(),
                })
            except Exception:
                pass
    return pd.DataFrame(data)


def plot_wer_sper_bars(df, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (16, 7)
    plt.rcParams["font.size"] = 12

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    sns.barplot(data=df, x="Model", y="WER", hue="Mode", ax=axes[0], palette="Blues")
    axes[0].set_title("Word Error Rate (WER) by Model and Mode", fontsize=14, fontweight="bold")
    axes[0].set_ylabel("Mean WER (Lower is Better)")
    axes[0].legend(title="Mode")

    sns.barplot(data=df, x="Model", y="SPER", hue="Mode", ax=axes[1], palette="Oranges")
    axes[1].set_title("Switch Point Error Rate (SPER) by Model and Mode", fontsize=14, fontweight="bold")
    axes[1].set_ylabel("Mean SPER (Lower is Better)")
    axes[1].legend(title="Mode")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "WER_SPER_Bar_Comparison.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: WER_SPER_Bar_Comparison.png")


def plot_wer_comparison_final(df, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (10, 7)
    plt.rcParams["font.size"] = 14

    plt.figure()
    sns.barplot(data=df, x="Model", y="WER", hue="Mode", palette="Blues_d", edgecolor="black", linewidth=1.2)
    plt.title("Word Error Rate (WER) by Model and Mode\n(Lower is Better)", fontweight="bold", pad=20)
    plt.ylabel("Mean WER")
    plt.xlabel("Whisper Model Size")
    plt.legend(title="Prompting Mode")
    plt.savefig(os.path.join(output_dir, "WER_Comparison_Final.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: WER_Comparison_Final.png")


def plot_sper_comparison_final(df, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (10, 7)
    plt.rcParams["font.size"] = 14

    plt.figure()
    sns.barplot(data=df, x="Model", y="SPER", hue="Mode", palette="Oranges_d", edgecolor="black", linewidth=1.2)
    plt.title("Switch Point Error Rate (SPER) by Model and Mode\n(Lower is Better)", fontweight="bold", pad=20)
    plt.ylabel("Mean SPER")
    plt.xlabel("Whisper Model Size")
    plt.legend(title="Prompting Mode")
    plt.savefig(os.path.join(output_dir, "SPER_Comparison_Final.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: SPER_Comparison_Final.png")


def plot_stacked_grouped(df, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(14, 8))
    x = np.arange(len(MODELS))
    width = 0.25

    for i, mode in enumerate(MODES):
        subset = df[df["Mode"] == mode.capitalize()]
        plt.bar(x + i * width, subset["WER"], width, label=f"{mode.capitalize()} - WER", alpha=0.9)
        plt.bar(x + i * width, subset["SPER"], width, bottom=subset["WER"].values,
                label=f"{mode.capitalize()} - SPER", alpha=0.7)

    plt.xlabel("Whisper Model")
    plt.ylabel("Error Rate")
    plt.title("WER and SPER Comparison Across Models and Prompting Modes", fontsize=16, fontweight="bold")
    plt.xticks(x + width, [m.capitalize() for m in MODELS])
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(axis="y", alpha=0.3)
    plt.savefig(os.path.join(output_dir, "WER_SPER_Stacked_Grouped.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: WER_SPER_Stacked_Grouped.png")


def plot_performance_trend(df, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(10, 6))
    for mode in MODES:
        subset = df[df["Mode"] == mode.capitalize()]
        plt.plot(subset["Model"], subset["WER"], marker="o", linewidth=2.5, label=f"{mode.capitalize()} WER")
        plt.plot(subset["Model"], subset["SPER"], marker="s", linestyle="--", label=f"{mode.capitalize()} SPER")

    plt.title("Performance Trend: Smaller to Larger Whisper Models", fontsize=14, fontweight="bold")
    plt.xlabel("Model Size")
    plt.ylabel("Error Rate")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, "Performance_Trend.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: Performance_Trend.png")


def plot_wer_by_category(results_dir=RESULTS_DIR, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["font.size"] = 12

    for model in MODELS:
        for mode in MODES:
            filename = os.path.join(results_dir, f"wer_{model}_{mode}.csv")
            try:
                df = pd.read_csv(filename)
                if "category" not in df.columns:
                    continue

                grouped = df.groupby("category")["wer"].mean().reset_index()

                plt.figure()
                plt.plot(grouped["category"], grouped["wer"], marker="o", linewidth=2.5, markersize=8, color="#1f77b4")
                plt.title(f"WER Trend - {model.capitalize()} Model ({mode.capitalize()} Mode)", fontweight="bold", pad=15)
                plt.xlabel("Category (A=Mild, B=Moderate, C=Heavy)")
                plt.ylabel("Mean WER (Lower is Better)")
                plt.grid(True, alpha=0.3)

                overall_mean = df["wer"].mean()
                plt.axhline(y=overall_mean, color="red", linestyle="--", alpha=0.7,
                            label=f"Overall Mean: {overall_mean:.4f}")
                plt.legend()

                save_name = f"WER_Line_{model}_{mode}.png"
                plt.savefig(os.path.join(output_dir, save_name), dpi=300, bbox_inches="tight")
                plt.close()
                print(f"Saved: {save_name}")

            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"Error processing {filename}: {e}")


def plot_wer_trend_all_modes(df, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(10, 6))
    for mode in df["Mode"].unique():
        subset = df[df["Mode"] == mode]
        plt.plot(subset["Model"], subset["WER"], marker="o", label=f"{mode} WER")

    plt.title("WER Trend Across Whisper Models and Prompting Modes", fontweight="bold", pad=15)
    plt.xlabel("Whisper Model Size")
    plt.ylabel("Mean WER (Lower is Better)")
    plt.legend(title="Prompting Mode")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "WER_Trend_All_Modes.png"), dpi=300)
    plt.close()
    print("Saved: WER_Trend_All_Modes.png")


def plot_sper_trend_all_modes(df, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(10, 6))
    for mode in df["Mode"].unique():
        subset = df[df["Mode"] == mode]
        plt.plot(subset["Model"], subset["SPER"], marker="o", label=f"{mode} SPER")

    plt.title("SPER Trend Across Whisper Models and Prompting Modes", fontweight="bold", pad=15)
    plt.xlabel("Whisper Model Size")
    plt.ylabel("Mean SPER (Lower is Better)")
    plt.legend(title="Prompting Mode")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "SPER_Trend_All_Modes.png"), dpi=300)
    plt.close()
    print("Saved: SPER_Trend_All_Modes.png")


def plot_combined_trend(df, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    sns.set_style("whitegrid")

    plt.figure(figsize=(12, 7))
    for mode in df["Mode"].unique():
        subset = df[df["Mode"] == mode]
        plt.plot(subset["Model"], subset["SPER"], marker="o", linestyle="-", label=f"{mode} SPER")
        plt.plot(subset["Model"], subset["WER"], marker="x", linestyle="--", label=f"{mode} WER")

    plt.title("Combined SPER and WER Trends Across Whisper Models and Prompting Modes", fontweight="bold", pad=15)
    plt.xlabel("Whisper Model Size")
    plt.ylabel("Error Rate (Lower is Better)")
    plt.legend(title="Metric and Prompting Mode", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "Combined_SPER_WER_Trend.png"), dpi=300)
    plt.close()
    print("Saved: Combined_SPER_WER_Trend.png")


def generate_all_plots(results_dir=RESULTS_DIR, output_dir=OUTPUT_DIR):
    df = load_summary_data(results_dir)
    if df.empty:
        print("No data found. Run WER and SPER analysis first.")
        return

    print(f"\nData loaded: {len(df)} entries\n")
    plot_wer_sper_bars(df, output_dir)
    plot_wer_comparison_final(df, output_dir)
    plot_sper_comparison_final(df, output_dir)
    plot_stacked_grouped(df, output_dir)
    plot_performance_trend(df, output_dir)
    plot_wer_by_category(results_dir, output_dir)
    plot_wer_trend_all_modes(df, output_dir)
    plot_sper_trend_all_modes(df, output_dir)
    plot_combined_trend(df, output_dir)
    print("\nAll plots generated.")


if __name__ == "__main__":
    generate_all_plots()
