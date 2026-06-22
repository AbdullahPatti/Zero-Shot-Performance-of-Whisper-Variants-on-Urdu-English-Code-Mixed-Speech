from sqlalchemy import Column, Integer, Float, String, Text, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from database import Base

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    speaker = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(150), nullable=False)
    age_bracket = Column(String(50), nullable=False)
    age = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ResultRecord(Base):
    __tablename__ = "result_records"
    __table_args__ = (UniqueConstraint("filename", "model_name", name="uq_filename_model"),)

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(260), nullable=False, index=True)
    speaker = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=True, index=True)
    reference = Column(Text, nullable=False)
    hypothesis = Column(Text, nullable=False)
    wer = Column(Float, nullable=True, index=True)
    language = Column(String(32), nullable=False, index=True)
    model_name = Column(String(32), nullable=False, index=True)
    source_file = Column(String(260), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
