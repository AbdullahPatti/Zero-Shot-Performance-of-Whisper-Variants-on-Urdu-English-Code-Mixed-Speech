from pydantic import BaseModel
from typing import Optional, List

class ResultRecordBase(BaseModel):
    filename: str
    speaker: str
    category: Optional[str] = None
    reference: str
    hypothesis: str
    wer: Optional[float] = None
    language: str
    model_name: str
    source_file: Optional[str] = None

class ResultRecordCreate(ResultRecordBase):
    pass

class ResultRecordRead(ResultRecordBase):
    id: int

    class Config:
        orm_mode = True

class ModelSummary(BaseModel):
    model_name: str
    language: str
    total_records: int
    average_wer: float
    min_wer: float
    max_wer: float

class ParticipantSummary(BaseModel):
    display_name: str
    age_bracket: str
    age: int
    recordings: int
    bio: Optional[str] = None

class OverviewResponse(BaseModel):
    total_records: int
    unique_speakers: int
    average_wer: float
    best_model: str
    summaries: List[ModelSummary]
