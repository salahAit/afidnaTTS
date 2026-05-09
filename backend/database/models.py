from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(String, nullable=False)
    language = Column(String, default="ar")
    voice_id = Column(String, nullable=True)
    status = Column(String, default="pending") # pending, processing, completed, failed
    progress = Column(Integer, default=0)
    progress_text = Column(String, default="Waiting...")
    output_path = Column(String, nullable=True)
    timestamps_path = Column(String, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json = Column(JSON, nullable=True)

class Voice(Base):
    __tablename__ = "voices"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    language = Column(String, nullable=False)
    gender = Column(String, nullable=True)
    engine = Column(String, nullable=False) # f5tts, kokoro
    sample_path = Column(String, nullable=True)
    is_active = Column(Integer, default=1)

class Cache(Base):
    __tablename__ = "cache"
    
    hash = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"))
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
