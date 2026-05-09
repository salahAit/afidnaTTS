from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend.database.models import Base
import os

DB_URL = "sqlite:///./afidna_tts.db"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
