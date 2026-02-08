---
name: voice
description: Voice assistant capabilities with speech-to-text (Voxtral) and text-to-speech (Kokoro). Transcribe audio files, realtime transcription, synthesize speech, and voice assistant loop. Use when user mentions voice, audio, transcription, or speech.
license: MIT
metadata:
  author: opencngsm
  version: "3.0"
  requires: mistralai[realtime]==1.2.0, torch==2.1.0, transformers==4.36.0
compatibility: Requires MISTRAL_API_KEY for speech-to-text. TTS works offline.
---

# Voice Skill

## When to use this skill

Use this skill when the user wants to:
- Transcribe audio files to text
- Convert text to speech
- Realtime voice transcription
- Voice assistant capabilities (listen → process → respond)
- Handle voice messages from Telegram/WhatsApp
- Multi-language voice support

## Setup

1. **Get Mistral API key (for STT):**
   - Visit: https://console.mistral.ai/
   - Create account and get API key
   - Set environment variable:
   ```bash
   export MISTRAL_API_KEY="your_mistral_api_key"
   ```

2. **Install dependencies:**
   ```bash
   pip install mistralai[realtime]==1.2.0 torch==2.1.0 transformers==4.36.0 sounddevice==0.4.6
   ```

3. **Kokoro TTS** (auto-downloads on first use):
   - Model: `hexgrad/Kokoro-82M`
   - No API key needed (runs locally)

## How to use

### Transcribe audio file

```python
from skills.voice.voice_skill import VoiceSkill

voice = VoiceSkill()

# Transcribe audio
text = await voice.transcribe_audio(
    'recording.mp3',
    language='pt',  # Portuguese
    diarize=True    # Identify speakers
)

print(f"Transcription: {text}")
```

### Synthesize speech

```python
# Text to speech
audio_bytes = await voice.synthesize_speech(
    text="Olá! Como posso ajudar?",
    voice='af',  # Female voice
    speed=1.0,
    output_path='response.wav'
)

# Speak (synthesize + play)
await voice.speak("Hello! This is OpenCngsm.", play=True)
```

### Realtime transcription

```python
# Realtime transcription from audio stream
async for text_delta in voice.transcribe_realtime(audio_stream):
    print(text_delta, end='', flush=True)
```

### Voice assistant loop

```python
async def handle_response(user_text, assistant_text):
    print(f"User: {user_text}")
    print(f"Assistant: {assistant_text}")

await voice.listen_and_respond(
    on_response=handle_response,
    language='pt',
    voice='af'
)
```

## Features

### Speech-to-Text (Voxtral)
- ✅ Transcribe audio files (mp3, wav, ogg, etc.)
- ✅ Realtime transcription
- ✅ Multi-language support (20+ languages)
- ✅ Speaker diarization
- ✅ Timestamps (word/segment level)
- ✅ High accuracy (<5% WER)

### Text-to-Speech (Kokoro)
- ✅ Natural voice synthesis
- ✅ Multi-voice (af, am, bf, bm, etc.)
- ✅ Multi-language (EN, PT, ES, FR, JP, CN, KR)
- ✅ Speed control (0.5-2.0x)
- ✅ Runs locally (no API needed)
- ✅ Apache-licensed

### Voice Assistant
- ✅ Listen → Process → Respond loop
- ✅ Configurable language and voice
- ✅ Integration with OpenCngsm core
- ✅ Optional audio playback

## Supported Languages

**STT (Voxtral):** Portuguese, English, Spanish, French, German, Italian, Dutch, Polish, Russian, Chinese, Japanese, Korean, Arabic, Hindi, and more.

**TTS (Kokoro):** English, Portuguese, Spanish, French, Japanese, Chinese, Korean.

## Voice IDs

- `af` - American Female
- `am` - American Male
- `bf` - British Female
- `bm` - British Male

## Performance

| Operation | Latency |
|-----------|---------|
| Transcription (Voxtral) | ~200-500ms |
| Synthesis (Kokoro) | ~200-300ms |
| Realtime transcription | Real-time |

## Implementation

See [voice_skill.py](voice_skill.py) for the complete implementation.

## Examples

See [examples/voice_usage.py](../../examples/voice_usage.py) for comprehensive examples.

## Troubleshooting

### "Mistral API key not configured"
- Set MISTRAL_API_KEY environment variable
- Verify key at https://console.mistral.ai/

### "Transcription failed"
- Check audio file format (mp3, wav, ogg supported)
- Verify audio is not too short (<1 second)
- Check internet connection (Voxtral is cloud-based)

### "Kokoro model loading failed"
- Ensure torch and transformers are installed
- Check disk space (model is ~300MB)
- Verify internet connection for first download

### "Audio playback failed"
- Install sounddevice: `pip install sounddevice`
- Check audio output device

## References

- [Mistral AI Voxtral](https://docs.mistral.ai/capabilities/voice/)
- [Kokoro TTS](https://huggingface.co/hexgrad/Kokoro-82M)
