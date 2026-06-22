# Voice Results Explorer

## 📘 Project Overview
This repository supports a research-driven dashboard and evaluation pipeline for compact OpenAI Whisper models on Urdu-English code-mixed speech.

The core contribution is a reproducible analysis of Tiny, Base, and Small Whisper variants in a zero-shot setting using a purpose-built corpus of **327 usable Urdu-English recordings** from **11 bilingual speakers**.

The project combines:
- a FastAPI dashboard with HTML rendering and audio preview support
- SQLAlchemy database loading from existing `Results/*.csv` and `Results/*.xlsx` files
- research metrics for **WER** and **SPER** extracted from `Voice.pdf`
- speaker metadata, language mix insights, and model summaries

## 🎯 Purpose of the Project
This work evaluates how compact Whisper models perform on multilingual Urdu-English speech without any fine-tuning.

It investigates:
- how code-mixing intensity affects transcription accuracy
- whether errors cluster at language switch boundaries
- the practical trade-off between model size and inference language configuration
- real-world applicability on a low-resource Urdu-English corpus

## 🔬 Key Findings from `Voice.pdf`
- Total usable recordings: **327**
- Speakers: **11 Urdu-English bilingual participants**
- Dataset is stratified into three mixing tiers:
  - Tier A: Mild mixing
  - Tier B: Moderate mixing
  - Tier C: Heavy mixing
- Best zero-shot configuration: **Whisper Small (244M) + English-forced inference**
  - Best mean WER: **0.8990**
  - Best consistency: **CV = 10.72%**
- Language boundary failures are systematic:
  - **SPER remains >0.93** across all evaluated conditions
- Tiny variant is not recommended for this task due to very high error and instability

## 📊 Research Metrics
The project tracks:
- **WER** (Word Error Rate)
- **SPER** (Switch Point Error Rate) for language transition boundaries
- model size comparisons:
  - Tiny: 39M parameters
  - Base: 74M parameters
  - Small: 244M parameters
- inference settings:
  - Urdu-forced
  - English-forced
  - Automatic detection

## 🧩 What is included
- `Voice.pdf` — research paper describing the study, dataset, and results
- `Voice/main.py` — FastAPI dashboard and API server
- `Voice/crud.py`, `Voice/models.py`, `Voice/database.py` — ORM and database logic
- `Voice/data_loader.py` — loads CSV/XLSX results into the database
- `Voice/templates/index.html` — dashboard UI template
- `Voice/static/style.css` — dashboard styling
- `Voice/Recordings/` — actual audio recordings for preview
- `Voice/Results/` — existing CSV and Excel results used by the dashboard

## ⚙️ Setup Criteria
Recommended environment:
- Python **3.10+** (the workspace has Python 3.13 available)
- `pip install -r Voice/requirements.txt`
- Optional: PostgreSQL for production via `DATABASE_URL`

Supported OS:
- Windows, macOS, Linux

## 🚀 Install and Run
From the repo root:

```bash
cd Voice
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## 🗂 Recommended Configuration
For prototype evaluation and visualization, use the built-in SQLite fallback.

For production or larger-scale use:

```bash
set DATABASE_URL=postgresql://user:password@localhost:5432/voice_db
python -m uvicorn main:app --reload
```

## 🧪 What the Dashboard Shows
- summary statistics for loaded records
- best-performing records by WER
- participant roster and metadata
- model/language summaries from the research
- audio preview for actual recordings
- gallery of available analysis images

## 📝 Notes
- The app does not retrain models; it uses existing CSV/XLSX result files.
- Recordings are served from `Voice/Recordings/` via the dashboard.
- The dataset is intentionally small and research-oriented, with controlled acoustic conditions.

## 📌 Future Directions
Potential extensions include:
- fine-tuning Whisper models on code-mixed Urdu-English speech
- adding boundary-aware language segmentation
- expanding the corpus to rural and regional dialects
- including noisy and telephony-style audio conditions

## 📚 Reference
This README is based on the research paper in `Voice.pdf`, which documents the first systematic zero-shot evaluation of compact Whisper variants on Urdu-English code-mixed speech.

