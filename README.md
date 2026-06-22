# Voice Results Explorer

This project now includes a FastAPI backend with a PostgreSQL-ready SQLAlchemy database and a beautiful Urdu/Latin HTML frontend.

## Run the app

1. Install dependencies:

```bash
cd Voice
python -m pip install -r requirements.txt
```

2. Start the app:

```bash
cd Voice
python -m uvicorn main:app --reload
```

3. Open `http://127.0.0.1:8000` in your browser.

## PostgreSQL support

Set the `DATABASE_URL` environment variable before starting the app, for example:

```bash
set DATABASE_URL=postgresql://user:password@localhost:5432/voice_db
python -m uvicorn main:app --reload
```

If `DATABASE_URL` is not set, the app uses a local SQLite database file `voice_app.db`.

## What the app shows

- summary statistics for all loaded result records
- model/language summaries with WER statistics
- a gallery of existing result images
- top records sorted by lowest WER

## Notes

- The app reads existing `Results/*.csv` and `Results/*.xlsx` files into the database at startup.
- No audio input or model training is required to use this dashboard.

