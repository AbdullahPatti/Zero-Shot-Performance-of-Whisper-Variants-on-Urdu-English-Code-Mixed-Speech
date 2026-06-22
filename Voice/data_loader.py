import os
from typing import Dict
from sqlalchemy.orm import Session
import pandas as pd
import crud
import schemas
import participant_data
import models

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(ROOT_DIR, "Results")

WER_FILES: Dict[str, tuple[str, str]] = {
    "wer_base_english.csv": ("Base", "English"),
    "wer_base_urdu.csv": ("Base", "Urdu"),
    "wer_base_guess.csv": ("Base", "Guess"),
    "wer_small_english.csv": ("Small", "English"),
    "wer_small_urdu.csv": ("Small", "Urdu"),
    "wer_small_guess.csv": ("Small", "Guess"),
    "wer_tiny_urdu.csv": ("Tiny", "Urdu"),
}

EXCEL_FILES: Dict[str, tuple[str, str]] = {
    "Results_Base.xlsx": ("Base", "English"),
    "Results_Small.xlsx": ("Small", "English"),
    "Results_Tiny.xlsx": ("Tiny", "English"),
}


def normalize_string(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def load_csv_file(db: Session, path: str, model_name: str, language: str) -> None:
    try:
        df = pd.read_csv(path, encoding="utf-8", dtype=str)
    except Exception:
        df = pd.read_csv(path, encoding="latin-1", dtype=str)

    if df.empty:
        return

    for _, row in df.iterrows():
        filename = normalize_string(row.get("filename") or row.get("file") or "")
        if not filename:
            continue

        if crud.get_record_by_filename_model(db, filename, model_name):
            continue

        record = schemas.ResultRecordCreate(
            filename=filename,
            speaker=normalize_string(row.get("speaker") or "Unknown"),
            category=normalize_string(row.get("category") or ""),
            reference=normalize_string(row.get("reference") or ""),
            hypothesis=normalize_string(row.get("hypothesis") or ""),
            wer=float(row.get("wer")) if row.get("wer") and str(row.get("wer")).strip() != "" else None,
            language=language,
            model_name=model_name,
            source_file=os.path.basename(path),
        )
        try:
            crud.create_result_record(db, record)
        except Exception:
            db.rollback()


def load_excel_file(db: Session, path: str, model_name: str, language: str) -> None:
    try:
        df = pd.read_excel(path, dtype=str)
    except Exception:
        return

    if df.empty:
        return

    for _, row in df.iterrows():
        filename = normalize_string(row.get("filename") or row.get("file") or "")
        if not filename:
            continue

        if crud.get_record_by_filename_model(db, filename, model_name):
            continue

        record = schemas.ResultRecordCreate(
            filename=filename,
            speaker=normalize_string(row.get("speaker") or "Unknown"),
            category=normalize_string(row.get("category") or ""),
            reference=normalize_string(row.get("reference") or ""),
            hypothesis=normalize_string(row.get("hypothesis") or ""),
            wer=float(row.get("wer")) if row.get("wer") and str(row.get("wer")).strip() != "" else None,
            language=language,
            model_name=model_name,
            source_file=os.path.basename(path),
        )
        try:
            crud.create_result_record(db, record)
        except Exception:
            db.rollback()


def load_participants(db: Session) -> None:
    for participant in participant_data.participants:
        existing = crud.get_participant_by_speaker(db, participant["speaker"])
        if existing:
            continue
        new_participant = models.Participant(
            speaker=participant["speaker"],
            display_name=participant["display_name"],
            age_bracket=participant["age_bracket"],
            age=participant["age"],
            bio=f"{participant['display_name']} is a {participant['age_bracket'].lower()} participant with {participant['age']} years."
        )
        crud.create_participant(db, new_participant)


def load_database(db: Session) -> None:
    if crud.get_record_count(db) > 0:
        load_participants(db)
        return

    load_participants(db)

    for filename, info in WER_FILES.items():
        path = os.path.join(RESULTS_DIR, filename)
        if os.path.exists(path):
            load_csv_file(db, path, info[0], info[1])

    for filename, info in EXCEL_FILES.items():
        path = os.path.join(RESULTS_DIR, filename)
        if os.path.exists(path):
            load_excel_file(db, path, info[0], info[1])
