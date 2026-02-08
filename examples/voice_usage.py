"""
OpenCngsm v3.0 - Voice Skill Usage Examples
Demonstrates Voxtral (STT) and Kokoro (TTS) capabilities
"""
import asyncio
import os
from skills.voice_skill import VoiceSkill


async def example_transcribe_file():
    """Example: Transcribe audio file"""
    print("\n=== Transcribe Audio File ===")
    
    voice = VoiceSkill(
        mistral_api_key=os.getenv('MISTRAL_API_KEY')
    )
    
    # Transcribe audio file
    text = await voice.transcribe_audio(
        'recording.mp3',
        language='pt',  # Portuguese
        diarize=True    # Identify speakers
    )
    
    print(f"Transcription: {text}")


async def example_realtime_transcription():
    """Example: Realtime transcription from microphone"""
    print("\n=== Realtime Transcription ===")
    
    voice = VoiceSkill()
    
    # Simulate audio stream (in real app, use microphone)
    async def audio_stream():
        # This would come from microphone in real implementation
        # For now, just a placeholder
        yield b''  # PCM audio chunks
    
    # Transcribe in realtime
    print("Listening... (speak now)")
    async for text_delta in voice.transcribe_realtime(audio_stream()):
        print(text_delta, end='', flush=True)


async def example_text_to_speech():
    """Example: Synthesize speech"""
    print("\n=== Text-to-Speech ===")
    
    voice = VoiceSkill()
    
    # Synthesize speech
    audio_bytes = await voice.synthesize_speech(
        text="Olá! Bem-vindo ao OpenCngsm v3.0. Como posso ajudá-lo hoje?",
        voice='af',  # Female voice
        speed=1.0,
        output_path='response.wav'
    )
    
    print(f"Generated {len(audio_bytes)} bytes of audio")
    print("Saved to response.wav")


async def example_speak():
    """Example: Speak text (synthesize + play)"""
    print("\n=== Speak ===")
    
    voice = VoiceSkill()
    
    # Speak (auto-play)
    await voice.speak(
        "Hello! This is OpenCngsm speaking.",
        voice='am',  # Male voice
        play=True
    )


async def example_voice_assistant():
    """Example: Full voice assistant loop"""
    print("\n=== Voice Assistant ===")
    
    voice = VoiceSkill(
        mistral_api_key=os.getenv('MISTRAL_API_KEY')
    )
    
    # Define response handler
    async def handle_response(user_text: str, assistant_text: str):
        print(f"\n👤 User: {user_text}")
        print(f"🤖 Assistant: {assistant_text}\n")
        
        # Here you could save to database, send to Telegram, etc.
    
    # Start voice assistant
    # await voice.listen_and_respond(
    #     on_response=handle_response,
    #     language='pt',
    #     voice='af'
    # )


async def example_multi_language():
    """Example: Multi-language support"""
    print("\n=== Multi-Language ===")
    
    voice = VoiceSkill()
    
    languages = {
        'en': "Hello, how can I help you today?",
        'pt': "Olá, como posso ajudá-lo hoje?",
        'es': "Hola, ¿cómo puedo ayudarte hoy?",
        'fr': "Bonjour, comment puis-je vous aider aujourd'hui?",
    }
    
    for lang, text in languages.items():
        print(f"\n{lang.upper()}: {text}")
        audio = await voice.synthesize_speech(
            text,
            output_path=f'greeting_{lang}.wav'
        )
        print(f"✅ Saved to greeting_{lang}.wav")


async def example_voice_profiles():
    """Example: Different voice profiles"""
    print("\n=== Voice Profiles ===")
    
    voice = VoiceSkill()
    
    text = "This is a test of different voice profiles."
    
    voices = {
        'af': 'Female (American)',
        'am': 'Male (American)',
        'bf': 'Female (British)',
        'bm': 'Male (British)',
    }
    
    for voice_id, description in voices.items():
        print(f"\n{description} ({voice_id})")
        await voice.synthesize_speech(
            text,
            voice=voice_id,
            output_path=f'voice_{voice_id}.wav'
        )
        print(f"✅ Saved to voice_{voice_id}.wav")


async def main():
    """Run examples"""
    print("🎤 OpenCngsm v3.0 - Voice Skill Examples\n")
    
    # Uncomment the examples you want to run
    
    # await example_transcribe_file()
    # await example_realtime_transcription()
    await example_text_to_speech()
    # await example_speak()
    # await example_voice_assistant()
    # await example_multi_language()
    # await example_voice_profiles()
    
    print("\n✅ Examples completed!")


if __name__ == '__main__':
    asyncio.run(main())
