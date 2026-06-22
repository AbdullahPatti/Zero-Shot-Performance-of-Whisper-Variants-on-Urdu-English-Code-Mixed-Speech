import os
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
import crud
import data_loader

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Voice Results Explorer")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/recordings", StaticFiles(directory=os.path.join(BASE_DIR, "Recordings")), name="recordings")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        data_loader.load_database(db)
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request, db: Session = Depends(get_db)):
    total_records = crud.get_record_count(db)
    unique_speakers = crud.get_unique_speakers(db)
    average_wer = crud.get_average_wer(db)
    summaries = crud.get_model_summary(db)
    language_distribution = crud.get_language_distribution(db)
    best_model = "N/A"
    if summaries:
        best_model = min(summaries, key=lambda s: s["average_wer"])["model_name"]

    top_records = crud.get_top_records(db, limit=12)
    participants = crud.get_participants(db)
    image_descriptions = {
        "WER_Comparison_Final.png": "WER Comparison across all Whisper models — final bar chart comparing tiny, base, and small models",
        "SPER_Comparison_Final.png": "SPER (Sentence-level Performance Error Rate) comparison across models",
        "WER_Line_base_english.png": "WER trend line for Whisper Base model on English segments",
        "WER_Line_base_guess.png": "WER trend line for Whisper Base model on auto-detected language",
        "WER_Line_base_urdu.png": "WER trend line for Whisper Base model on Urdu segments",
        "WER_Line_small_english.png": "WER trend line for Whisper Small model on English segments",
        "WER_Line_small_urdu.png": "WER trend line for Whisper Small model on Urdu segments",
        "WER_Line_tiny_urdu.png": "WER trend line for Whisper Tiny model on Urdu segments",
        "1.png": "Waveform and spectrogram analysis — sample recording 1",
        "2.png": "Waveform and spectrogram analysis — sample recording 2",
        "3.png": "Waveform and spectrogram analysis — sample recording 3",
        "4.png": "Waveform and spectrogram analysis — sample recording 4",
        "5.png": "Waveform and spectrogram analysis — sample recording 5",
        "6.png": "Waveform and spectrogram analysis — sample recording 6",
        "7.png": "Waveform and spectrogram analysis — sample recording 7",
        "8.png": "Waveform and spectrogram analysis — sample recording 8",
        "image.png": "Dataset overview and distribution visualization",
    }
    image_files = [f for f in os.listdir(os.path.join(BASE_DIR, "Images")) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
    images_with_desc = [{"filename": f, "description": image_descriptions.get(f, f)} for f in image_files]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "total_records": total_records,
            "unique_speakers": unique_speakers,
            "average_wer": round(average_wer, 4),
            "best_model": best_model,
            "summaries": summaries,
            "language_distribution": language_distribution,
            "top_records": top_records,
            "participants": participants,
            "images": images_with_desc,
        },
    )


@app.get("/records/{model_name}/{language}", response_class=HTMLResponse)
def records_by_model(request: Request, model_name: str, language: str, db: Session = Depends(get_db)):
    records = crud.get_top_records(db, limit=40, model_name=model_name, language=language)
    if not records:
        raise HTTPException(status_code=404, detail="Records not found")
    return templates.TemplateResponse(
        "model_records.html",
        {
            "request": request,
            "records": records,
            "model_name": model_name,
            "language": language,
        },
    )


@app.get("/api/overview")
def api_overview(db: Session = Depends(get_db)):
    total_records = crud.get_record_count(db)
    unique_speakers = crud.get_unique_speakers(db)
    average_wer = crud.get_average_wer(db)
    summaries = crud.get_model_summary(db)
    best_model = "N/A"
    if summaries:
        best_model = min(summaries, key=lambda s: s["average_wer"])["model_name"]
    return {
        "total_records": total_records,
        "unique_speakers": unique_speakers,
        "average_wer": round(average_wer, 4),
        "best_model": best_model,
        "summaries": summaries,
    }


@app.get("/api/records")
def api_records(model_name: str | None = None, language: str | None = None, db: Session = Depends(get_db)):
    records = crud.get_top_records(db, limit=100, model_name=model_name, language=language)
    return [
        {
            "id": record.id,
            "filename": record.filename,
            "speaker": record.speaker,
            "category": record.category,
            "reference": record.reference,
            "hypothesis": record.hypothesis,
            "wer": record.wer,
            "language": record.language,
            "model_name": record.model_name,
            "source_file": record.source_file,
        }
        for record in records
    ]


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return RedirectResponse(url="/static/favicon.ico")
