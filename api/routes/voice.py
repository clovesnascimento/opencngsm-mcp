"""
OpenCngsm v3.0 - Voice API Routes
FastAPI endpoints for voice transcription
"""
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/voice", tags=["voice"])

# Voice skill instance (lazy loaded)
_voice_skill = None


def get_voice_skill():
    """Get or create Voice Skill instance"""
    global _voice_skill
    
    if _voice_skill is None:
        try:
            from skills.voice_skill import VoiceSkill
            _voice_skill = VoiceSkill()
            logger.info("✅ Voice Skill initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Voice Skill: {e}")
            raise HTTPException(
                status_code=500,
                detail="Voice service not available. Check MISTRAL_API_KEY."
            )
    
    return _voice_skill


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    language: Optional[str] = Form('pt', description="Language code (pt, en, es, etc.)"),
    diarize: bool = Form(False, description="Enable speaker diarization")
):
    """
    Transcribe audio file to text
    
    Args:
        audio: Audio file (webm, mp3, wav, ogg, etc.)
        language: Language code (pt, en, es, fr, etc.)
        diarize: Enable speaker diarization
    
    Returns:
        {
            "transcription": "transcribed text",
            "language": "pt",
            "confidence": 0.98
        }
    
    Example:
        curl -X POST http://localhost:8000/api/voice/transcribe \
          -F "audio=@recording.webm" \
          -F "language=pt"
    """
    try:
        # Get Voice Skill
        voice = get_voice_skill()
        
        # Read audio bytes
        audio_bytes = await audio.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Save to temp file
        suffix = os.path.splitext(audio.filename)[1] or '.webm'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        logger.info(f"🎤 Transcribing audio: {audio.filename} ({len(audio_bytes)} bytes)")
        
        # Transcribe
        transcription = await voice.transcribe_audio(
            temp_path,
            language=language if language != 'auto' else None,
            diarize=diarize
        )
        
        # Cleanup temp file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        if not transcription:
            raise HTTPException(
                status_code=500,
                detail="Transcription failed. Audio may be too short or unclear."
            )
        
        logger.info(f"✅ Transcription: {transcription[:50]}...")
        
        return JSONResponse({
            "transcription": transcription,
            "language": language,
            "confidence": 0.95  # Voxtral doesn't provide confidence, using placeholder
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Transcription error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/synthesize")
async def synthesize_speech(
    text: str = Form(..., description="Text to synthesize"),
    voice: str = Form('af', description="Voice ID (af, am, bf, bm, etc.)"),
    speed: float = Form(1.0, description="Speech speed (0.5-2.0)")
):
    """
    Synthesize speech from text (Text-to-Speech)
    
    Args:
        text: Text to synthesize
        voice: Voice ID (af=female, am=male, etc.)
        speed: Speech speed
    
    Returns:
        Audio file (WAV format)
    
    Example:
        curl -X POST http://localhost:8000/api/voice/synthesize \
          -F "text=Hello, how are you?" \
          -F "voice=af" \
          --output response.wav
    """
    try:
        # Get Voice Skill
        voice_skill = get_voice_skill()
        
        logger.info(f"🔊 Synthesizing: {text[:50]}...")
        
        # Synthesize
        audio_bytes = await voice_skill.synthesize_speech(
            text,
            voice=voice,
            speed=speed
        )
        
        if not audio_bytes:
            raise HTTPException(
                status_code=500,
                detail="Speech synthesis failed"
            )
        
        logger.info(f"✅ Synthesized {len(audio_bytes)} bytes")
        
        # Return audio file
        from fastapi.responses import Response
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Synthesis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Speech synthesis failed: {str(e)}"
        )


@router.get("/status")
async def voice_status():
    """
    Check voice service status
    
    Returns:
        {
            "status": "ok",
            "stt_available": true,
            "tts_available": true
        }
    """
    try:
        voice = get_voice_skill()
        
        return {
            "status": "ok",
            "stt_available": voice.mistral_client is not None,
            "tts_available": True,  # Kokoro is always available
            "models": {
                "stt": "voxtral-mini-latest",
                "tts": voice.kokoro_model_name
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "stt_available": False,
            "tts_available": False
        }
