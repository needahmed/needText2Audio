import os
import sys
import torch
import tempfile
import numpy as np
from typing import Tuple, Optional
import soundfile as sf
import threading
import time

# Add parent directory to path to import kokoro
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TTSService:
    def __init__(self):
        self.models = {}
        self.pipelines = {}
        self.initialized = False
        self.initialization_in_progress = False
        self.initialization_error = None
        self.cuda_available = torch.cuda.is_available()
        
        # Voice choices from original app.py
        self.CHOICES = {
            '🇺🇸 🚺 Heart ❤️': 'af_heart',
            '🇺🇸 🚺 Bella 🔥': 'af_bella',
            '🇺🇸 🚺 Nicole 🎧': 'af_nicole',
            '🇺🇸 🚺 Aoede': 'af_aoede',
            '🇺🇸 🚺 Kore': 'af_kore',
            '🇺🇸 🚺 Sarah': 'af_sarah',
            '🇺🇸 🚺 Nova': 'af_nova',
            '🇺🇸 🚺 Sky': 'af_sky',
            '🇺🇸 🚺 Alloy': 'af_alloy',
            '🇺🇸 🚺 Jessica': 'af_jessica',
            '🇺🇸 🚺 River': 'af_river',
            '🇺🇸 🚹 Michael': 'am_michael',
            '🇺🇸 🚹 Fenrir': 'am_fenrir',
            '🇺🇸 🚹 Puck': 'am_puck',
            '🇺🇸 🚹 Echo': 'am_echo',
            '🇺🇸 🚹 Eric': 'am_eric',
            '🇺🇸 🚹 Liam': 'am_liam',
            '🇺🇸 🚹 Onyx': 'am_onyx',
            '🇺🇸 🚹 Santa': 'am_santa',
            '🇺🇸 🚹 Adam': 'am_adam',
            '🇬🇧 🚺 Emma': 'bf_emma',
            '🇬🇧 🚺 Isabella': 'bf_isabella',
            '🇬🇧 🚺 Alice': 'bf_alice',
            '🇬🇧 🚺 Lily': 'bf_lily',
            '🇬🇧 🚹 George': 'bm_george',
            '🇬🇧 🚹 Fable': 'bm_fable',
            '🇬🇧 🚹 Lewis': 'bm_lewis',
            '🇬🇧 🚹 Daniel': 'bm_daniel',
        }
        
    def initialize(self):
        """Initialize models and pipelines with better error handling"""
        if self.initialized or self.initialization_in_progress:
            return
            
        self.initialization_in_progress = True
        
        def _async_initialize():
            try:
                print("Starting TTS service initialization...")
                
                # Try to import and initialize the minimum required components
                from kokoro import KModel, KPipeline
                
                # Initialize models (start with CPU only to be safe)
                print("Loading CPU model...")
                self.models[False] = KModel().to('cpu').eval()
                
                # Only load GPU model if we have sufficient resources
                if self.cuda_available:
                    try:
                        print("Loading GPU model...")
                        self.models[True] = KModel().to('cuda').eval()
                        print("GPU model loaded successfully")
                    except Exception as gpu_error:
                        print(f"GPU model loading failed: {gpu_error}, continuing with CPU only")
                        self.cuda_available = False
                
                # Initialize pipelines for languages a and b
                print("Loading pipelines...")
                self.pipelines = {
                    lang_code: KPipeline(lang_code=lang_code, model=False) 
                    for lang_code in 'ab'
                }
                
                # Add custom pronunciations
                self.pipelines['a'].g2p.lexicon.golds['kokoro'] = 'kˈOkəɹO'
                self.pipelines['b'].g2p.lexicon.golds['kokoro'] = 'kˈQkəɹQ'
                
                # Don't preload voices during startup - do it on demand
                print("TTS Service initialized successfully (voices will load on demand)")
                self.initialized = True
                self.initialization_error = None
                
            except Exception as e:
                error_msg = f"Error initializing TTS service: {e}"
                print(error_msg)
                self.initialization_error = str(e)
                self.initialized = False
            finally:
                self.initialization_in_progress = False
        
        # Run initialization in background thread to not block startup
        thread = threading.Thread(target=_async_initialize, daemon=True)
        thread.start()
        
        # Give it a few seconds to initialize, but don't block indefinitely
        thread.join(timeout=30)  # Wait maximum 30 seconds
        
        if self.initialization_in_progress:
            print("TTS initialization taking longer than expected, will continue in background...")
    
    def get_voices(self):
        """Get list of available voices"""
        voices = []
        for display_name, voice_id in self.CHOICES.items():
            # Parse display name to extract info
            parts = display_name.split()
            country = parts[0] if parts else "🇺🇸"
            gender = "Female" if "🚺" in display_name else "Male"
            name = display_name.split()[-1] if parts else voice_id
            
            # Determine language
            language = "British English" if voice_id.startswith('b') else "American English"
            
            voices.append({
                "id": voice_id,
                "name": name,
                "language": language,
                "gender": gender,
                "description": display_name
            })
        
        return voices
    
    def generate_speech(self, text: str, voice: str = "af_heart", speed: float = 1.0, use_gpu: bool = None) -> Tuple[str, str]:
        """Generate speech from text"""
        # Wait for initialization to complete if it's in progress
        max_wait = 60  # Maximum 60 seconds
        waited = 0
        while self.initialization_in_progress and waited < max_wait:
            time.sleep(1)
            waited += 1
        
        if not self.initialized:
            if self.initialization_error:
                print(f"TTS service failed to initialize: {self.initialization_error}")
            else:
                print("TTS service not initialized, using mock audio")
            return self._generate_mock_audio(text), f"Service unavailable - Mock tokens for: {text[:50]}..."
        
        # Validate voice
        if voice not in [v for v in self.CHOICES.values()]:
            voice = "af_heart"  # Default fallback
        
        # Limit text length
        text = text.strip()[:25000]
        
        # Determine GPU usage
        if use_gpu is None:
            use_gpu = self.cuda_available
        use_gpu = use_gpu and self.cuda_available
        
        try:
            pipeline = self.pipelines[voice[0]]
            
            # Load voice if not already loaded
            if voice not in getattr(pipeline, '_loaded_voices', set()):
                print(f"Loading voice: {voice}")
                pipeline.load_voice(voice)
                if not hasattr(pipeline, '_loaded_voices'):
                    pipeline._loaded_voices = set()
                pipeline._loaded_voices.add(voice)
            
            pack = pipeline.load_voice(voice)
            
            for _, ps, _ in pipeline(text, voice, speed):
                ref_s = pack[len(ps)-1]
                
                try:
                    if use_gpu:
                        audio = self.models[True](ps, ref_s, speed)
                    else:
                        audio = self.models[False](ps, ref_s, speed)
                except Exception as e:
                    if use_gpu:
                        print(f"GPU generation failed: {e}, falling back to CPU")
                        audio = self.models[False](ps, ref_s, speed)
                    else:
                        raise e
                
                # Convert to numpy and save as temporary file
                audio_np = audio.numpy()
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    sf.write(tmp_file.name, audio_np, 24000)
                    return tmp_file.name, ps
                    
        except Exception as e:
            print(f"Error generating speech: {str(e)}")
            # Fallback to mock audio
            return self._generate_mock_audio(text), f"Error tokens: {str(e)[:100]}"
        
        raise Exception("No audio generated")
    
    def _generate_mock_audio(self, text: str) -> str:
        """Generate a mock audio file for testing when TTS is not available"""
        # Generate 3 seconds of sine wave as placeholder
        duration = min(len(text) * 0.1, 10.0)  # Dynamic duration based on text length
        sample_rate = 24000
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440  # A4 note
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            sf.write(tmp_file.name, audio, sample_rate)
            return tmp_file.name

# Global instance
tts_service = TTSService() 