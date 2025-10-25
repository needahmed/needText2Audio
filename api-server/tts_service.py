import os
import tempfile
import numpy as np
from typing import Tuple, Optional
import soundfile as sf
import threading
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.models = {}
        self.pipelines = {}
        self.initialized = False
        self.initialization_in_progress = False
        self.initialization_error = None
        self.voices_loaded = set()
        
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
        
        # Start background initialization (non-blocking)
        self._start_background_init()
        
    def _start_background_init(self):
        """Start initialization in background thread"""
        def init_worker():
            try:
                self.initialization_in_progress = True
                logger.info("Starting TTS service initialization in background...")
                
                # Try to import torch first
                try:
                    import torch
                    self.cuda_available = torch.cuda.is_available()
                    logger.info(f"Torch available. CUDA: {self.cuda_available}")
                except Exception as e:
                    logger.error(f"Failed to import torch: {e}")
                    self.cuda_available = False
                
                # Try to import kokoro
                try:
                    from kokoro import KModel, KPipeline
                    logger.info("Successfully imported Kokoro modules")
                    
                    # Initialize CPU model only for now
                    logger.info("Loading CPU model...")
                    self.models[False] = KModel().to('cpu').eval()
                    logger.info("CPU model loaded successfully")
                    
                    # Initialize pipelines
                    logger.info("Loading pipelines...")
                    self.pipelines = {
                        'a': KPipeline(lang_code='a', model=False),
                        'b': KPipeline(lang_code='b', model=False)
                    }
                    
                    # Add custom pronunciations
                    self.pipelines['a'].g2p.lexicon.golds['kokoro'] = 'kˈOkəɹO'
                    self.pipelines['b'].g2p.lexicon.golds['kokoro'] = 'kˈQkəɹQ'
                    
                    logger.info("Pipelines loaded successfully")
                    
                    self.initialized = True
                    logger.info("TTS Service fully initialized!")
                    
                except Exception as e:
                    logger.error(f"Failed to initialize Kokoro: {e}")
                    self.initialization_error = str(e)
                    
            except Exception as e:
                logger.error(f"TTS initialization failed: {e}")
                self.initialization_error = str(e)
            finally:
                self.initialization_in_progress = False
        
        # Start the worker thread
        thread = threading.Thread(target=init_worker, daemon=True)
        thread.start()
    
    def get_status(self):
        """Get initialization status"""
        if self.initialized:
            return {"status": "ready", "message": "TTS service is ready"}
        elif self.initialization_in_progress:
            return {"status": "initializing", "message": "TTS service is starting up..."}
        elif self.initialization_error:
            return {"status": "error", "message": f"TTS service failed: {self.initialization_error}"}
        else:
            return {"status": "waiting", "message": "TTS service is waiting to start"}
    
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
    
    def generate_speech(self, text: str, voice: str = "af_heart", speed: float = 1.0, use_gpu: bool = True) -> Tuple[str, str]:
        """Generate speech from text.
        Note: `use_gpu` is currently accepted for API compatibility but is not
        used; the service generates audio on CPU for stability and fallback.
        """
        # Check if service is ready
        if not self.initialized:
            if self.initialization_in_progress:
                # Wait a bit for initialization
                logger.info("Waiting for TTS initialization...")
                for _ in range(10):  # Wait up to 10 seconds
                    if self.initialized:
                        break
                    time.sleep(1)
            
            if not self.initialized:
                logger.warning("TTS service not ready, returning mock audio")
                return self._generate_mock_audio(text), f"Mock audio for: {text[:50]}..."
        
        # Validate voice
        if voice not in [v for v in self.CHOICES.values()]:
            voice = "af_heart"  # Default fallback
        
        # Limit text length
        text = text.strip()[:5000]  # Reduced limit for stability
        
        try:
            return self._do_generation(text, voice, speed)
        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            return self._generate_mock_audio(text), f"Generation failed: {str(e)}"
    
    def _do_generation(self, text: str, voice: str, speed: float) -> Tuple[str, str]:
        """Actually generate the speech"""
        pipeline = self.pipelines[voice[0]]
        
        # Load voice if needed
        if voice not in self.voices_loaded:
            logger.info(f"Loading voice: {voice}")
            pipeline.load_voice(voice)
            self.voices_loaded.add(voice)
        
        pack = pipeline.load_voice(voice)
        
        for _, ps, _ in pipeline(text, voice, speed):
            ref_s = pack[len(ps)-1]
            
            # Use CPU model for now (more stable)
            audio = self.models[False](ps, ref_s, speed)
            
            # Convert to numpy and save as temporary file
            audio_np = audio.numpy()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                # Save audio file
                sf.write(tmp_file.name, audio_np, 24000)
                
                # Create tokens summary
                num_tokens = len(ps)
                tokens_info = f"Generated {num_tokens} tokens for text: {text[:100]}..."
                
                return tmp_file.name, tokens_info
        
        # Fallback if no audio generated
        return self._generate_mock_audio(text), f"No audio generated for: {text[:50]}..."
    
    def _generate_mock_audio(self, text: str) -> str:
        """Generate a mock audio file for testing"""
        try:
            # Generate 1 second of sine wave as mock audio
            sample_rate = 24000
            duration = min(len(text) * 0.05, 10)  # Max 10 seconds
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                sf.write(tmp_file.name, audio, sample_rate)
                return tmp_file.name
        except Exception as e:
            logger.error(f"Failed to generate mock audio: {e}")
            # Return a dummy path if even mock generation fails
            return "/tmp/mock_audio.wav"

# Create global instance
tts_service = TTSService() 