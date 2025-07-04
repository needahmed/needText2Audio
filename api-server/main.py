from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import tempfile
import uuid
from pathlib import Path

from models import TTSRequest, VoicesResponse, TTSResponse, ErrorResponse
from tts_service import tts_service

# Create FastAPI app
app = FastAPI(
    title="Kokoro TTS API",
    description="Text-to-Speech API using Kokoro models",
    version="1.0.0"
)

# Get the frontend URL from an environment variable for production.
# This makes the app more flexible and secure.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Define allowed origins for CORS
# This includes local dev environments and your deployed Vercel frontend.
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    FRONTEND_URL,
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directory for generated audio files
AUDIO_DIR = Path("generated_audio")
AUDIO_DIR.mkdir(exist_ok=True)

# Mount static files for serving audio
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

@app.on_event("startup")
async def startup_event():
    """Initialize TTS service on startup"""
    print("Starting Kokoro TTS API server...")
    try:
        print("Initializing TTS service...")
        tts_service.initialize()
        print("TTS service initialization started")
    except Exception as e:
        print(f"Warning: TTS service initialization failed: {e}")
        print("Server will start anyway, TTS will use fallback mode")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Kokoro TTS API is running!",
        "status": "healthy",
        "tts_initialized": tts_service.initialized,
        "cuda_available": tts_service.cuda_available
    }

@app.get("/api/voices", response_model=VoicesResponse)
async def get_voices():
    """Get list of available voices"""
    try:
        voices = tts_service.get_voices()
        return VoicesResponse(voices=voices)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voices: {str(e)}")

@app.post("/api/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """Convert text to speech"""
    try:
        # Generate speech
        audio_path, tokens = tts_service.generate_speech(
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            use_gpu=request.use_gpu
        )
        
        # Move file to static directory with unique name
        audio_filename = f"{uuid.uuid4()}.wav"
        static_audio_path = AUDIO_DIR / audio_filename
        
        # Copy the temporary file to static directory
        import shutil
        shutil.move(audio_path, static_audio_path)
        
        # Return URL for the audio file
        audio_url = f"/audio/{audio_filename}"
        
        return TTSResponse(
            message="Speech generated successfully",
            audio_url=audio_url,
            tokens=tokens
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    tts_status = tts_service.get_status()
    return {
        "status": "ok",
        "tts": tts_status,
        "message": "API server is running"
    }

@app.get("/api/status")
async def get_status():
    """Get detailed service status"""
    return tts_service.get_status()

@app.delete("/api/audio/{filename}")
async def delete_audio(filename: str):
    """Delete an audio file"""
    try:
        audio_path = AUDIO_DIR / filename
        if audio_path.exists():
            audio_path.unlink()
            return {"message": "Audio file deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete audio file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 