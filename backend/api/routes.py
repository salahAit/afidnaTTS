"""AfidnaTTS Backend - API Routes"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from backend.tasks.manager import task_manager
from backend.tts.generation import orchestrator

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    lang: str = "ar"
    voice_id: Optional[str] = None
    ref_audio: Optional[str] = ""
    ref_text: Optional[str] = ""

@router.post("/generate")
async def generate(request: TTSRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    task_id = task_manager.create_task({
        "lang": request.lang,
        "voice_id": request.voice_id
    })
    
    orchestrator.start_generation(
        task_id, 
        request.text, 
        request.lang, 
        request.voice_id, 
        request.ref_audio, 
        request.ref_text
    )
    
    return {"task_id": task_id}

@router.get("/status/{task_id}")
async def status(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/status/{task_id}/timestamps")
async def get_timestamps(task_id: str):
    import os
    from fastapi.responses import FileResponse
    from backend.core.config import TIMESTAMPS_DIR
    
    ts_path = os.path.join(str(TIMESTAMPS_DIR), f"{task_id}.json")
    if os.path.exists(ts_path):
        return FileResponse(ts_path)
    raise HTTPException(status_code=404, detail="Timestamps not found")

