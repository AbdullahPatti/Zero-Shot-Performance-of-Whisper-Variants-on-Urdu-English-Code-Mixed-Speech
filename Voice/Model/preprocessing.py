import os
import pandas as pd
import soundfile as sf


AUDIO_DIR = "Recordings"
PROCESSED_AUDIO_DIR = "Processed_Recordings"
REF_CSV = "References/references.csv"
ANN_CSV = "References/annotations.csv"


def verify_audio_files(audio_dir=AUDIO_DIR):
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith(".wav")]
    print(f"WAV files found: {len(audio_files)}")

    issues = []
    for fname in audio_files:
        path = os.path.join(audio_dir, fname)
        try:
            info = sf.info(path)
            if info.samplerate != 16000:
                issues.append(f"{fname}: {info.samplerate}Hz")
        except Exception:
            issues.append(f"{fname}: could not read")

    if issues:
        print(f"{len(issues)} files with issues:")
        for i in issues:
            print(i)
    else:
        print("All files are 16kHz. Ready to go.")

    return issues


def check_corrupted_file(filepath):
    try:
        data, sr = sf.read(filepath)
        print(f"Readable: {sr}Hz, {len(data)} samples")
        return True
    except Exception as e:
        print(f"Corrupted: {e}")
        return False


def remove_corrupted_from_references(filenames_to_remove, ref_csv=REF_CSV):
    ref = pd.read_csv(ref_csv)
    for fname in filenames_to_remove:
        ref = ref[ref["filename"] != fname]
    ref.to_csv(ref_csv, index=False)
    print(f"Remaining rows: {len(ref)}")
    return ref


def load_data_summary():
    ref = pd.read_csv(REF_CSV)
    ann = pd.read_csv(ANN_CSV)
    print(f"References rows: {len(ref)}")
    print(f"Annotations rows: {len(ann)}")
    print("\nReferences sample:")
    print(ref.head(3))
    print("\nAnnotations sample:")
    print(ann.head(3))
    return ref, ann


if __name__ == "__main__":
    load_data_summary()
    print("\n--- Verifying raw recordings ---")
    issues = verify_audio_files(AUDIO_DIR)

    if issues:
        corrupted = [i.split(":")[0] for i in issues if "could not read" in i]
        if corrupted:
            print(f"\nRemoving corrupted files from references: {corrupted}")
            remove_corrupted_from_references(corrupted)

    print("\n--- Verifying processed recordings ---")
    processed_files = [f for f in os.listdir(PROCESSED_AUDIO_DIR) if f.endswith(".wav")]
    print(f"Processed WAV files: {len(processed_files)}")
