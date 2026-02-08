"""
OpenCngsm v3.0 - Telegram + Voice Integration Example
Demonstrates voice message transcription in Telegram
"""
import asyncio
import os
from skills.telegram_skill import TelegramSkill
from skills.voice_skill import VoiceSkill


async def main():
    """Telegram bot with voice message support"""
    
    # Initialize Voice Skill
    voice = VoiceSkill(
        mistral_api_key=os.getenv('MISTRAL_API_KEY')
    )
    
    # Initialize Telegram Skill with Voice support
    telegram = TelegramSkill(
        bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        chat_id=os.getenv('TELEGRAM_CHAT_ID'),
        voice_skill=voice  # Enable voice transcription
    )
    
    # Optional: Enable voice responses
    telegram.enable_voice_responses(enabled=False)  # Respond with text by default
    
    # Text message handler
    async def handle_text_message(text: str, update):
        print(f"📝 Text: {text}")
        
        # Process message (integrate with OpenCngsm core here)
        response = f"You said: {text}"
        
        # Send response
        await telegram.send_message(response)
    
    # Voice message handler
    async def handle_voice_message(transcription: str, update):
        print(f"🎤 Voice transcription: {transcription}")
        
        # Process transcription (same as text)
        response = f"You said (via voice): {transcription}"
        
        # Send response (text or voice based on config)
        if telegram._voice_response_enabled:
            # Respond with voice
            audio_bytes = await voice.synthesize_speech(response)
            
            # Save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(audio_bytes)
                temp_path = f.name
            
            await telegram.send_voice(temp_path)
            
            # Cleanup
            import os
            os.unlink(temp_path)
        else:
            # Respond with text
            await telegram.send_message(response)
    
    # Start bot
    print("🤖 Starting Telegram bot with voice support...")
    print("📝 Send text messages or 🎤 voice messages")
    print("Press Ctrl+C to stop\n")
    
    try:
        await telegram.start_bot(
            on_message_callback=handle_text_message,
            on_voice_callback=handle_voice_message
        )
        
        # Keep running
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping bot...")
        await telegram.stop_bot()


if __name__ == '__main__':
    asyncio.run(main())
