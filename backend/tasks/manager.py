"""AfidnaTTS Backend - Task Manager"""
import uuid
import threading
from typing import Dict, Any, Optional
from datetime import datetime
from backend.core.logging import get_logger

logger = get_logger("tasks")

from backend.database.session import SessionLocal, init_db
from backend.database.models import Task
from sqlalchemy import update as sqlalchemy_update

logger = get_logger("tasks")

class TaskManager:
    def __init__(self):
        # Initialize DB on first access
        init_db()

    def create_task(self, metadata: Optional[Dict[str, Any]] = None, text: str = "", lang: str = "ar", voice_id: str = None) -> str:
        task_id = str(uuid.uuid4())
        db = SessionLocal()
        try:
            new_task = Task(
                id=task_id,
                text=text,
                language=lang,
                voice_id=voice_id,
                status="pending",
                progress=0,
                progress_text="Waiting in queue...",
                metadata_json=metadata or {}
            )
            db.add(new_task)
            db.commit()
            logger.info(f"Task created in DB: {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"Failed to create task in DB: {e}")
            return task_id
        finally:
            db.close()

    def update_task(self, task_id: str, status: str = None, progress: int = None, progress_text: str = None, output_path: str = None, error: str = None, timestamps_path: str = None):
        db = SessionLocal()
        try:
            update_data = {"updated_at": datetime.utcnow()}
            if status: update_data["status"] = status
            if progress is not None: update_data["progress"] = progress
            if progress_text: update_data["progress_text"] = progress_text
            if output_path: update_data["output_path"] = output_path
            if error: update_data["error"] = error
            if timestamps_path: update_data["timestamps_path"] = timestamps_path
            
            db.execute(
                sqlalchemy_update(Task).where(Task.id == task_id).values(**update_data)
            )
            db.commit()
            
            if status in ["completed", "failed"]:
                logger.info(f"Task {task_id} finished with status: {status}")
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
        finally:
            db.close()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None
            return {
                "id": task.id,
                "status": task.status,
                "progress": task.progress,
                "progress_text": task.progress_text,
                "output_path": task.output_path,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "error": task.error,
                "timestamps_path": task.timestamps_path
            }
        finally:
            db.close()

task_manager = TaskManager()
