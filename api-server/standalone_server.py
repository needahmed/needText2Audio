#!/usr/bin/env python3
"""
Standalone TTS API server for testing without Kokoro dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import tempfile
import uuid
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import List, Optional
import uvicorn

# Pydantic models (simplified)
try:
    from pydantic import BaseModel
except ImportError:
    print("Please install pydantic: pip install pydantic")
    exit(1)

class TTSRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    speed: float = 1.0
    use_gpu: bool = True

class Voice(BaseModel):
    id: str
    name: str
    language: str
    gender: str
    description: Optional[str] = None

class VoicesResponse(BaseModel):
    voices: List[Voice]

class TTSResponse(BaseModel):
    message: str
    audio_url: Optional[str] = None
    tokens: Optional[str] = None

# Create FastAPI app
app = FastAPI(
    title="Kokoro TTS API (Standalone)",
    description="Text-to-Speech API with mock functionality for testing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directory for generated audio files
AUDIO_DIR = Path("generated_audio")
AUDIO_DIR.mkdir(exist_ok=True)

# Mount static files for serving audio
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# Mock voice data
MOCK_VOICES = [
    {"id": "af_heart", "name": "Heart", "language": "American English", "gender": "Female", "description": "🇺🇸 🚺 Heart ❤️"},
    {"id": "af_bella", "name": "Bella", "language": "American English", "gender": "Female", "description": "🇺🇸 🚺 Bella 🔥"},
    {"id": "af_nicole", "name": "Nicole", "language": "American English", "gender": "Female", "description": "🇺🇸 🚺 Nicole 🎧"},
    {"id": "am_michael", "name": "Michael", "language": "American English", "gender": "Male", "description": "🇺🇸 🚹 Michael"},
    {"id": "am_eric", "name": "Eric", "language": "American English", "gender": "Male", "description": "🇺🇸 🚹 Eric"},
    {"id": "bf_emma", "name": "Emma", "language": "British English", "gender": "Female", "description": "🇬🇧 🚺 Emma"},
    {"id": "bm_george", "name": "George", "language": "British English", "gender": "Male", "description": "🇬🇧 🚹 George"},
]

def generate_mock_audio(text: str, voice: str, speed: float) -> str:
    """Generate mock audio file"""
    # Generate audio based on text length and parameters
    duration = min(len(text) * 0.05 * (2.0 / speed), 15.0)  # Max 15 seconds
    sample_rate = 24000
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Different frequencies for different voices
    voice_frequencies = {
        "af_heart": 440,    # A4
        "af_bella": 493.88, # B4
        "af_nicole": 523.25, # C5
        "am_michael": 329.63, # E4
        "am_eric": 293.66,   # D4
        "bf_emma": 466.16,   # A#4
        "bm_george": 261.63, # C4
    }
    
    frequency = voice_frequencies.get(voice, 440)
    
    # Generate a more interesting waveform
    audio = 0.3 * (
        np.sin(2 * np.pi * frequency * t) +
        0.3 * np.sin(2 * np.pi * frequency * 1.5 * t) +
        0.1 * np.sin(2 * np.pi * frequency * 2 * t)
    )
    
    # Add some envelope to make it less harsh
    envelope = np.exp(-t * 0.5)
    audio = audio * envelope
    
    # Create unique filename
    audio_filename = f"{uuid.uuid4()}.wav"
    audio_path = AUDIO_DIR / audio_filename
    
    # Save audio file
    sf.write(str(audio_path), audio, sample_rate)
    
    return f"/audio/{audio_filename}"

@app.get("/")
async def root():
    return {"message": "Kokoro TTS API (Standalone) is running!"}

@app.get("/api/voices", response_model=VoicesResponse)
async def get_voices():
    return VoicesResponse(voices=MOCK_VOICES)

@app.post("/api/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
        
        # Generate mock audio
        audio_url = generate_mock_audio(request.text, request.voice, request.speed)
        
        # Generate mock tokens
        mock_tokens = f"Mock phonetic tokens for voice {request.voice}: " + " ".join([
            f"/{word}/" for word in request.text.split()[:10]
        ])
        
        return TTSResponse(
            message="Mock speech generated successfully",
            audio_url=audio_url,
            tokens=mock_tokens
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Kokoro TTS API (Standalone)",
        "initialized": True,
        "cuda_available": False,
        "note": "Running in mock mode for testing"
    }

if __name__ == "__main__":
    print("Starting Standalone Kokoro TTS API server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation will be available at: http://localhost:8000/docs")
    print("\nNote: This is a mock implementation for testing the web interface.")
    print("It generates simple audio tones instead of real speech synthesis.")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info") 