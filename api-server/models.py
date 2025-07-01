from pydantic import BaseModel, Field
from typing import List, Optional

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech", max_length=25000)
    voice: str = Field(default="af_heart", description="Voice model to use")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    use_gpu: bool = Field(default=True, description="Whether to use GPU acceleration")

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

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None 