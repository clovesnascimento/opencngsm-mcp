"""
OpenCngsm v3.0 - Telegram Skill
Native Python implementation using python-telegram-bot
"""
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from typing import Optional, Callable, Awaitable
import asyncio
import logging
import os
import tempfile

logger = logging.getLogger(__name__)


class TelegramSkill:
    """
    Telegram bot skill using python-telegram-bot
    
    Features:
    - Send messages with Markdown/HTML formatting
    - Receive messages with callback
    - Typing action
    - Bot polling with auto-reconnection
    """
    
    def __init__(self, bot_token: str, chat_id: str, voice_skill=None):
        """
        Initialize Telegram skill
        
        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Target chat ID
            voice_skill: Optional VoiceSkill instance for voice message support
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
        self.application: Optional[Application] = None
        self.message_callback: Optional[Callable] = None
        self.voice_callback: Optional[Callable] = None
        self.voice_skill = voice_skill
        self._running = False
        self._voice_response_enabled = False  # Respond with voice?
    
    async def send_message(
        self,
        text: str,
        parse_mode: str = 'Markdown',
        disable_notification: bool = False
    ) -> bool:
        """
        Send message to Telegram chat
        
        Args:
            text: Message text
            parse_mode: 'Markdown', 'HTML', or None
            disable_notification: Silent notification
        
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_notification=disable_notification
            )
            logger.info(f"✅ Message sent to {self.chat_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            return False
    
    async def send_typing_action(self) -> bool:
        """
        Send typing action (shows "typing..." in chat)
        
        Returns:
            True if successful
        """
        try:
            await self.bot.send_chat_action(
                chat_id=self.chat_id,
                action='typing'
            )
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send typing action: {e}")
            return False
    
    async def send_photo(
        self,
        photo_path: str,
        caption: str = None
    ) -> bool:
        """
        Send photo to chat
        
        Args:
            photo_path: Path to photo file
            caption: Optional caption
        
        Returns:
            True if successful
        """
        try:
            with open(photo_path, 'rb') as photo:
                await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=photo,
                    caption=caption
                )
            logger.info(f"✅ Photo sent to {self.chat_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send photo: {e}")
            return False
    
    async def send_voice(
        self,
        voice_path: str,
        caption: str = None
    ) -> bool:
        """
        Send voice message to chat
        
        Args:
            voice_path: Path to voice file (OGG, MP3, WAV)
            caption: Optional caption
        
        Returns:
            True if successful
        """
        try:
            with open(voice_path, 'rb') as voice:
                await self.bot.send_voice(
                    chat_id=self.chat_id,
                    voice=voice,
                    caption=caption
                )
            logger.info(f"🎤 Voice message sent to {self.chat_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send voice: {e}")
            return False
    
    def enable_voice_responses(self, enabled: bool = True):
        """
        Enable/disable voice responses
        
        Args:
            enabled: If True, respond with voice messages
        """
        self._voice_response_enabled = enabled
        logger.info(f"🔊 Voice responses: {'enabled' if enabled else 'disabled'}")
    
    async def start_bot(
        self,
        on_message_callback: Callable[[str, Update], Awaitable[None]],
        on_voice_callback: Optional[Callable[[str, Update], Awaitable[None]]] = None
    ):
        """
        Start bot polling to receive messages and voice messages
        
        Args:
            on_message_callback: Async function(message: str, update: Update)
                Called when a text message is received
            on_voice_callback: Optional async function(transcription: str, update: Update)
                Called when a voice message is received and transcribed
        
        Example:
            async def handle_message(text: str, update: Update):
                print(f"Received: {text}")
                await telegram.send_message(f"You said: {text}")
            
            async def handle_voice(transcription: str, update: Update):
                print(f"Voice transcription: {transcription}")
                await telegram.send_message(f"You said (voice): {transcription}")
            
            await telegram.start_bot(handle_message, handle_voice)
        """
        if self._running:
            logger.warning("Bot is already running")
            return
        
        self.message_callback = on_message_callback
        self.voice_callback = on_voice_callback
        
        # Create application
        self.application = Application.builder().token(self.bot_token).build()
        
        # Text message handler
        async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if update.message and str(update.message.chat_id) == str(self.chat_id):
                message_text = update.message.text
                if message_text and self.message_callback:
                    try:
                        await self.message_callback(message_text, update)
                    except Exception as e:
                        logger.error(f"Error in message callback: {e}")
        
        # Voice message handler
        async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if update.message and update.message.voice and str(update.message.chat_id) == str(self.chat_id):
                try:
                    logger.info("🎤 Received voice message")
                    
                    # Download voice file
                    voice_file = await update.message.voice.get_file()
                    
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
                        temp_path = temp_file.name
                        await voice_file.download_to_drive(temp_path)
                    
                    # Transcribe if voice skill available
                    if self.voice_skill:
                        await self.send_typing_action()
                        transcription = await self.voice_skill.transcribe_audio(temp_path)
                        
                        logger.info(f"📝 Transcription: {transcription}")
                        
                        # Call voice callback or message callback
                        if self.voice_callback:
                            await self.voice_callback(transcription, update)
                        elif self.message_callback:
                            await self.message_callback(transcription, update)
                    else:
                        logger.warning("⚠️ Voice skill not configured - cannot transcribe")
                    
                    # Cleanup temp file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                
                except Exception as e:
                    logger.error(f"❌ Error handling voice message: {e}")
        
        # Add handlers
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )
        self.application.add_handler(
            MessageHandler(filters.VOICE, handle_voice)
        )
        
        # Start polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        self._running = True
        logger.info(f"🤖 Telegram bot started for chat {self.chat_id}")
        if self.voice_skill:
            logger.info("🎤 Voice message support enabled")
    
    async def stop_bot(self):
        """Stop bot polling"""
        if not self._running:
            return
        
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            self._running = False
            logger.info("🛑 Telegram bot stopped")
    
    async def get_bot_info(self) -> dict:
        """
        Get bot information
        
        Returns:
            Dict with bot info (username, first_name, etc.)
        """
        try:
            bot_info = await self.bot.get_me()
            return {
                'id': bot_info.id,
                'username': bot_info.username,
                'first_name': bot_info.first_name,
                'is_bot': bot_info.is_bot
            }
        except Exception as e:
            logger.error(f"❌ Failed to get bot info: {e}")
            return {}
    
    def is_running(self) -> bool:
        """Check if bot is currently running"""
        return self._running


# Skill metadata for registration
SKILL_NAME = "telegram"
SKILL_CLASS = TelegramSkill
SKILL_DESCRIPTION = "Send and receive Telegram messages using python-telegram-bot"


# Auto-register skill
from . import register_skill
register_skill(SKILL_NAME, SKILL_CLASS, SKILL_DESCRIPTION)
