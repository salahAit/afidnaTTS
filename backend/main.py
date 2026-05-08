"""AfidnaTTS Backend - Main Entry Point"""
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import asyncio
from backend.api.routes import router as api_router
from backend.core.config import HOST, PORT, CORS_ORIGINS, AUDIO_DIR
from backend.tasks.manager import task_manager

app = FastAPI(title="AfidnaTTS Professional Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket for real-time task tracking
@app.websocket("/ws/tasks/{task_id}")
async def task_status_ws(websocket: WebSocket, task_id: str):
    await websocket.accept()
    try:
        last_update = ""
        while True:
            task = task_manager.get_task(task_id)
            if not task:
                await websocket.send_json({"error": "Task not found"})
                break
            
            # Only send if something changed to save bandwidth
            current_update = f"{task['status']}-{task['progress']}-{task['progress_text']}"
            if current_update != last_update:
                await websocket.send_json(task)
                last_update = current_update
            
            if task["status"] in ["completed", "failed"]:
                # Send one final update before closing
                await websocket.send_json(task)
                break
            
            await asyncio.sleep(0.3) 
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WS Error: {e}")

# Routes
app.include_router(api_router, prefix="/api/v1")


# Static Audio Serving
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(str(AUDIO_DIR), filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}, 404

@app.get("/")
async def root():
    return {"message": "AfidnaTTS Backend is running", "version": "2.0.0"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
