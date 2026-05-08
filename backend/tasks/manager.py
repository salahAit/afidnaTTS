"""AfidnaTTS Backend - Task Manager"""
import uuid
import threading
from typing import Dict, Any, Optional
from datetime import datetime
from backend.core.logging import get_logger

logger = get_logger("tasks")

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "id": task_id,
            "status": "pending",
            "progress": 0,
            "progress_text": "Waiting in queue...",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "output_path": None,
            "metadata": metadata or {}
        }
        logger.info(f"Task created: {task_id}")
        return task_id

    def update_task(self, task_id: str, status: str = None, progress: int = None, progress_text: str = None, output_path: str = None):
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        if status: task["status"] = status
        if progress is not None: task["progress"] = progress
        if progress_text: task["progress_text"] = progress_text
        if output_path: task["output_path"] = output_path
        
        task["updated_at"] = datetime.now().isoformat()
        
        if status in ["completed", "failed"]:
            logger.info(f"Task {task_id} finished with status: {status}")

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.tasks.get(task_id)

task_manager = TaskManager()
