"""
OpenCngsm v3.0 - Voice Skill
Voice assistant capabilities using Voxtral (STT) and Kokoro (TTS)
"""
import os
import asyncio
import base64
from typing import Optional, AsyncIterator, Callable
from pathlib import Path
import logging

# Voxtral (Mistral AI)
from mistralai import Mistral
from mistralai.extra.realtime import UnknownRealtimeEvent
from mistralai.models import (
    AudioFormat,
    RealtimeTranscriptionError,
    RealtimeTranscriptionSessionCreated,
    TranscriptionStreamDone,
    TranscriptionStreamTextDelta
)

# Kokoro TTS
import torch
import torchaudio
from transformers import AutoTokenizer, AutoModel

logger = logging.getLogger(__name__)


class VoiceSkill:
    """
    Voice Assistant Skill - Alexa-like capabilities
    
    Features:
    - Speech-to-Text (Voxtral via Mistral AI)
    - Text-to-Speech (Kokoro local model)
    - Realtime transcription
    - Multi-language support
    - Voice profiles
    
    Setup:
    1. Get Mistral API key: https://console.mistral.ai/
    2. Kokoro model auto-downloads from Hugging Face
    """
    
    def __init__(
        self,
        mistral_api_key: Optional[str] = None,
        kokoro_model: str = 'hexgrad/Kokoro-82M',
        device: str = 'auto'
    ):
        """
        Initialize Voice Skill
        
        Args:
            mistral_api_key: Mistral AI API key for Voxtral
            kokoro_model: Kokoro model name from Hugging Face
            device: 'cuda', 'cpu', or 'auto'
        """
        # Mistral client for Voxtral
        self.mistral_api_key = mistral_api_key or os.getenv('MISTRAL_API_KEY')
        if not self.mistral_api_key:
            logger.warning("⚠️ MISTRAL_API_KEY not set - STT will not work")
        
        self.mistral_client = Mistral(api_key=self.mistral_api_key) if self.mistral_api_key else None
        
        # Kokoro TTS
        self.kokoro_model_name = kokoro_model
        self.device = self._get_device(device)
        self.kokoro_model = None
        self.kokoro_tokenizer = None
        
        # Audio settings
        self.sample_rate = 16000  # 16kHz for Voxtral
        self.audio_format = AudioFormat(encoding="pcm_s16le", sample_rate=self.sample_rate)
        
        logger.info(f"🎤 Voice Skill initialized (device: {self.device})")
    
    def _get_device(self, device: str) -> str:
        """Determine device (CUDA/CPU)"""
        if device == 'auto':
            return 'cuda' if torch.cuda.is_available() else 'cpu'
        return device
    
    async def load_kokoro(self):
        """Load Kokoro TTS model"""
        if self.kokoro_model is not None:
            return
        
        try:
            logger.info(f"📥 Loading Kokoro model: {self.kokoro_model_name}")
            
            self.kokoro_tokenizer = AutoTokenizer.from_pretrained(self.kokoro_model_name)
            self.kokoro_model = AutoModel.from_pretrained(self.kokoro_model_name).to(self.device)
            self.kokoro_model.eval()
            
            logger.info(f"✅ Kokoro loaded on {self.device}")
        
        except Exception as e:
            logger.error(f"❌ Failed to load Kokoro: {e}")
            raise
    
    # ==================== Speech-to-Text (Voxtral) ====================
    
    async def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
        diarize: bool = False
    ) -> str:
        """
        Transcribe audio file using Voxtral
        
        Args:
            audio_path: Path to audio file (mp3, wav, etc.)
            language: Language code (e.g., 'en', 'pt') or None for auto-detect
            diarize: Enable speaker diarization
        
        Returns:
            Transcribed text
        
        Example:
            text = await voice.transcribe_audio('recording.mp3', language='pt')
            print(f"Transcription: {text}")
        """
        if not self.mistral_client:
            raise RuntimeError("Mistral API key not configured")
        
        try:
            with open(audio_path, "rb") as f:
                response = self.mistral_client.audio.transcriptions.complete(
                    model="voxtral-mini-latest",
                    file={
                        "content": f,
                        "file_name": Path(audio_path).name,
                    },
                    language=language,
                    diarize=diarize
                )
            
            text = response.text
            logger.info(f"✅ Transcribed: {text[:50]}...")
            return text
        
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            return ""
    
    async def transcribe_audio_base64(
        self,
        audio_base64: str,
        language: Optional[str] = None
    ) -> str:
        """
        Transcribe audio from base64 string
        
        Args:
            audio_base64: Base64-encoded audio
            language: Language code or None
        
        Returns:
            Transcribed text
        """
        if not self.mistral_client:
            raise RuntimeError("Mistral API key not configured")
        
        try:
            response = self.mistral_client.audio.transcriptions.complete(
                model="voxtral-mini-latest",
                file_url=f"data:audio/mp3;base64,{audio_base64}",
                language=language
            )
            
            return response.text
        
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            return ""
    
    async def transcribe_realtime(
        self,
        audio_stream: AsyncIterator[bytes],
        on_text_callback: Optional[Callable[[str], None]] = None
    ) -> AsyncIterator[str]:
        """
        Realtime transcription from audio stream
        
        Args:
            audio_stream: Async iterator yielding audio chunks (PCM 16kHz)
            on_text_callback: Optional callback for each text delta
        
        Yields:
            Transcribed text deltas
        
        Example:
            async for text in voice.transcribe_realtime(audio_stream):
                print(text, end='', flush=True)
        """
        if not self.mistral_client:
            raise RuntimeError("Mistral API key not configured")
        
        try:
            async for event in self.mistral_client.audio.realtime.transcribe_stream(
                audio_stream=audio_stream,
                model="voxtral-mini-transcribe-realtime-2602",
                audio_format=self.audio_format,
            ):
                if isinstance(event, RealtimeTranscriptionSessionCreated):
                    logger.info("🎙️ Realtime session created")
                
                elif isinstance(event, TranscriptionStreamTextDelta):
                    text = event.text
                    if on_text_callback:
                        on_text_callback(text)
                    yield text
                
                elif isinstance(event, TranscriptionStreamDone):
                    logger.info("✅ Transcription done")
                
                elif isinstance(event, RealtimeTranscriptionError):
                    logger.error(f"❌ Realtime error: {event}")
                
                elif isinstance(event, UnknownRealtimeEvent):
                    logger.warning(f"⚠️ Unknown event: {event}")
        
        except Exception as e:
            logger.error(f"❌ Realtime transcription failed: {e}")
    
    # ==================== Text-to-Speech (Kokoro) ====================
    
    async def synthesize_speech(
        self,
        text: str,
        voice: str = 'af',  # Default voice
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Synthesize speech from text using Kokoro
        
        Args:
            text: Text to synthesize
            voice: Voice ID (e.g., 'af', 'am', 'bf', etc.)
            speed: Speech speed (0.5-2.0)
            output_path: Optional path to save audio file
        
        Returns:
            Audio bytes (WAV format)
        
        Example:
            audio = await voice.synthesize_speech("Hello, how can I help you?")
            # Save to file
            with open('response.wav', 'wb') as f:
                f.write(audio)
        """
        await self.load_kokoro()
        
        try:
            # Tokenize text
            inputs = self.kokoro_tokenizer(text, return_tensors="pt").to(self.device)
            
            # Generate speech
            with torch.no_grad():
                audio_tensor = self.kokoro_model.generate(
                    **inputs,
                    voice=voice,
                    speed=speed
                )
            
            # Convert to bytes (WAV format)
            audio_bytes = self._tensor_to_wav(audio_tensor)
            
            # Save to file if requested
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(audio_bytes)
                logger.info(f"💾 Audio saved to {output_path}")
            
            logger.info(f"🔊 Synthesized: {text[:50]}...")
            return audio_bytes
        
        except Exception as e:
            logger.error(f"❌ Speech synthesis failed: {e}")
            return b''
    
    async def speak(
        self,
        text: str,
        voice: str = 'af',
        play: bool = True
    ) -> bytes:
        """
        Synthesize and optionally play speech
        
        Args:
            text: Text to speak
            voice: Voice ID
            play: If True, play audio immediately
        
        Returns:
            Audio bytes
        """
        audio_bytes = await self.synthesize_speech(text, voice=voice)
        
        if play and audio_bytes:
            await self._play_audio(audio_bytes)
        
        return audio_bytes
    
    def _tensor_to_wav(self, audio_tensor: torch.Tensor) -> bytes:
        """Convert audio tensor to WAV bytes"""
        import io
        
        # Ensure tensor is on CPU
        audio_tensor = audio_tensor.cpu()
        
        # Save to BytesIO
        buffer = io.BytesIO()
        torchaudio.save(buffer, audio_tensor, self.sample_rate, format='wav')
        buffer.seek(0)
        
        return buffer.read()
    
    async def _play_audio(self, audio_bytes: bytes):
        """Play audio bytes (requires sounddevice)"""
        try:
            import sounddevice as sd
            import soundfile as sf
            import io
            
            # Load audio
            audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
            
            # Play
            sd.play(audio_data, sample_rate)
            sd.wait()
        
        except ImportError:
            logger.warning("⚠️ sounddevice not installed - cannot play audio")
        except Exception as e:
            logger.error(f"❌ Audio playback failed: {e}")
    
    # ==================== Voice Assistant ====================
    
    async def listen_and_respond(
        self,
        on_response: Callable[[str, str], None],
        language: str = 'pt',
        voice: str = 'af'
    ):
        """
        Voice assistant loop: listen → process → respond
        
        Args:
            on_response: Callback(user_text, assistant_text)
            language: Language for transcription
            voice: Voice for TTS
        
        Example:
            async def handle_response(user_text, assistant_text):
                print(f"User: {user_text}")
                print(f"Assistant: {assistant_text}")
            
            await voice.listen_and_respond(handle_response)
        """
        logger.info("🎤 Voice assistant started - Press Ctrl+C to stop")
        
        try:
            while True:
                # 1. Listen (record audio)
                logger.info("👂 Listening...")
                audio_path = await self._record_audio()
                
                # 2. Transcribe
                user_text = await self.transcribe_audio(audio_path, language=language)
                if not user_text:
                    continue
                
                logger.info(f"User: {user_text}")
                
                # 3. Process (placeholder - integrate with OpenCngsm core)
                assistant_text = await self._process_query(user_text)
                logger.info(f"Assistant: {assistant_text}")
                
                # 4. Speak
                await self.speak(assistant_text, voice=voice, play=True)
                
                # 5. Callback
                if on_response:
                    on_response(user_text, assistant_text)
        
        except KeyboardInterrupt:
            logger.info("🛑 Voice assistant stopped")
    
    async def _record_audio(self, duration: int = 5) -> str:
        """Record audio from microphone (placeholder)"""
        # TODO: Implement actual recording
        # For now, return a dummy path
        return "temp_recording.wav"
    
    async def _process_query(self, text: str) -> str:
        """Process user query (placeholder)"""
        # TODO: Integrate with OpenCngsm core
        return f"You said: {text}"


# Skill metadata
SKILL_NAME = "voice"
SKILL_CLASS = VoiceSkill
SKILL_DESCRIPTION = "Voice assistant with Voxtral (STT) and Kokoro (TTS) - Alexa-like capabilities"


# Auto-register
from . import register_skill
register_skill(SKILL_NAME, SKILL_CLASS, SKILL_DESCRIPTION)
