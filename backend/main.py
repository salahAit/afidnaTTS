"""AfidnaTTS Backend - Main Entry Point"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from backend.api.routes import router as api_router
from backend.core.config import HOST, PORT, CORS_ORIGINS, AUDIO_DIR

app = FastAPI(title="AfidnaTTS Professional Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
