# 🎙️ AfidnaTTS - Unified Voice Platform

AfidnaTTS is a professional, production-grade Arabic Text-to-Speech platform built with SvelteKit and F5-TTS. This project features a unified architecture where the inference engine, virtual environments, and model logic are self-contained within the project structure.

## 🚀 Key Features

- **Unified Engine**: F5-TTS is integrated directly into the backend, eliminating external dependencies.
- **Standalone Virtual Envs**: The system uses isolated environments for both the API and the TTS engine.
- **Smart Normalization**: Built-in Arabic text normalization and chunking for high-quality audio generation.
- **Real-time Tracking**: WebSocket-based progress tracking for audio generation tasks.

## 🛠️ Tech Stack

- **Frontend**: SvelteKit 5, Bun, TailwindCSS 4, Bits-UI.
- **Backend**: FastAPI (Python 3.12), Uvicorn.
- **TTS Engine**: F5-TTS (Flow Matching) with a custom inference wrapper.

## 🏃 Getting Started

### Prerequisites

- [Bun](https://bun.sh) (JavaScript Runtime)
- Python 3.12+
- NVIDIA GPU (Recommended for F5-TTS inference)

### Installation

1. **Install Frontend Dependencies**:
   ```bash
   bun install
   ```

2. **Setup Backend Environment**:
   ```bash
   # Create and activate root venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt  # If available, or install fastapi uvicorn etc.
   ```

3. **Models**:
   Ensure you have a compatible F5-TTS model in `backend/storage/arabic_model/`.

### Running the Project

You need to run two processes simultaneously:

#### 1. Backend Server
```bash
source .venv/bin/activate
python -m backend.main
```

#### 2. Frontend Development Server
```bash
bun run dev
```

The application will be available at `http://localhost:5173`.

## 📁 Project Structure

```text
afidnaTTS/
├── backend/            # Python FastAPI backend
│   ├── core/           # Configuration and core logic
│   ├── api/            # API Routes
│   ├── tts/            # TTS Engines
│   │   └── f5/         # Unified F5-TTS Engine (Self-contained)
│   └── storage/        # Audio, Models, and Cache
├── src/                # SvelteKit Frontend
├── static/             # Static assets
└── package.json        # Frontend dependencies
```

## 📜 License

Private Property of Afidna. All rights reserved.
