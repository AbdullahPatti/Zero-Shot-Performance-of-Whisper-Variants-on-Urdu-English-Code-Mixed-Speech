from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas


def get_record_count(db: Session) -> int:
    return db.query(func.count(models.ResultRecord.id)).scalar() or 0


def get_unique_speakers(db: Session) -> int:
    return db.query(func.count(func.distinct(models.ResultRecord.speaker))).scalar() or 0


def get_average_wer(db: Session) -> float:
    result = db.query(func.avg(models.ResultRecord.wer)).filter(models.ResultRecord.wer != None).scalar()
    return float(result or 0.0)


def get_model_summary(db: Session) -> List[dict]:
    rows = (
        db.query(
            models.ResultRecord.model_name,
            models.ResultRecord.language,
            func.count(models.ResultRecord.id).label("count"),
            func.avg(models.ResultRecord.wer).label("avg_wer"),
            func.min(models.ResultRecord.wer).label("min_wer"),
            func.max(models.ResultRecord.wer).label("max_wer"),
        )
        .group_by(models.ResultRecord.model_name, models.ResultRecord.language)
        .all()
    )
    return [
        {
            "model_name": row.model_name,
            "language": row.language,
            "total_records": int(row.count or 0),
            "average_wer": round(float(row.avg_wer or 0.0), 4),
            "min_wer": round(float(row.min_wer or 0.0), 4),
            "max_wer": round(float(row.max_wer or 0.0), 4),
        }
        for row in rows
    ]


def get_language_distribution(db: Session) -> List[dict]:
    rows = (
        db.query(models.ResultRecord.language, func.count(models.ResultRecord.id).label("count"))
        .group_by(models.ResultRecord.language)
        .order_by(func.count(models.ResultRecord.id).desc())
        .all()
    )
    return [
        {
            "language": row.language,
            "count": int(row.count or 0),
        }
        for row in rows
    ]


def get_top_records(db: Session, limit: int = 12, model_name: Optional[str] = None, language: Optional[str] = None) -> List[models.ResultRecord]:
    query = db.query(models.ResultRecord)
    if model_name:
        query = query.filter(models.ResultRecord.model_name == model_name)
    if language:
        query = query.filter(models.ResultRecord.language == language)
    return query.order_by(models.ResultRecord.wer.asc()).limit(limit).all()


def get_participants(db: Session) -> List[dict]:
    rows = (
        db.query(
            models.Participant.display_name,
            models.Participant.age_bracket,
            models.Participant.age,
        )
        .order_by(models.Participant.age_bracket, models.Participant.display_name)
        .all()
    )
    return [
        {
            "display_name": row.display_name,
            "age_bracket": row.age_bracket,
            "recordings": int(row.age or 0),
        }
        for row in rows
    ]


def get_record_by_filename_model(db: Session, filename: str, model_name: str) -> Optional[models.ResultRecord]:
    return (
        db.query(models.ResultRecord)
        .filter(models.ResultRecord.filename == filename, models.ResultRecord.model_name == model_name)
        .first()
    )


def create_result_record(db: Session, record: schemas.ResultRecordCreate) -> models.ResultRecord:
    db_record = models.ResultRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_participant_by_speaker(db: Session, speaker: str) -> Optional[models.Participant]:
    return db.query(models.Participant).filter(models.Participant.speaker == speaker).first()


def create_participant(db: Session, participant: models.Participant) -> models.Participant:
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant
