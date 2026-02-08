---
name: telegram
description: Send and receive Telegram messages with bot polling, typing action, photo support, and voice message transcription. Use when user mentions Telegram, wants to send messages, or handle voice messages.
license: MIT
metadata:
  author: opencngsm
  version: "3.0"
  requires: python-telegram-bot==20.7
compatibility: Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables
---

# Telegram Skill

## When to use this skill

Use this skill when the user wants to:
- Send messages via Telegram bot
- Receive messages from Telegram
- Handle voice messages (with Voice Skill integration)
- Send photos or media
- Show typing indicators
- Run a Telegram bot with polling

## Setup

1. **Get bot token from @BotFather:**
   - Open Telegram and search for @BotFather
   - Send `/newbot` and follow instructions
   - Copy the bot token

2. **Get chat ID:**
   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Copy the chat ID from the response

3. **Set environment variables:**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   ```

## How to use

### Basic usage

```python
from skills.telegram.telegram_skill import TelegramSkill

# Initialize
telegram = TelegramSkill(
    bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
    chat_id=os.getenv('TELEGRAM_CHAT_ID')
)

# Send message
await telegram.send_message("Hello from OpenCngsm!")

# Send with typing action
await telegram.send_typing_action()
await telegram.send_message("Processing...")

# Send photo
await telegram.send_photo("image.jpg", caption="Check this out!")
```

### With voice support

```python
from skills.voice.voice_skill import VoiceSkill

# Initialize with voice skill
voice = VoiceSkill()
telegram = TelegramSkill(
    bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
    chat_id=os.getenv('TELEGRAM_CHAT_ID'),
    voice_skill=voice  # Enable voice transcription
)

# Handle messages
async def handle_text(text, update):
    response = process_message(text)
    await telegram.send_message(response)

async def handle_voice(transcription, update):
    response = process_message(transcription)
    await telegram.send_message(f"You said (voice): {response}")

# Start bot
await telegram.start_bot(
    on_message_callback=handle_text,
    on_voice_callback=handle_voice
)
```

## Features

- ✅ Send text messages (Markdown/HTML formatting)
- ✅ Receive messages with callback
- ✅ Typing action indicator
- ✅ Send photos with captions
- ✅ Send voice messages
- ✅ Bot polling with auto-reconnection
- ✅ Voice message transcription (with Voice Skill)
- ✅ Configurable voice responses

## Implementation

See [telegram_skill.py](telegram_skill.py) for the complete implementation.

## Examples

See [examples/telegram_voice_bot.py](../../examples/telegram_voice_bot.py) for a complete bot example with voice support.

## Troubleshooting

### "Bot token invalid"
- Verify token from @BotFather
- Check TELEGRAM_BOT_TOKEN env var

### "Chat ID not found"
- Send a message to your bot first
- Get chat ID from getUpdates endpoint

### "Voice transcription failed"
- Ensure Voice Skill is configured
- Check MISTRAL_API_KEY is set
- Verify voice_skill parameter is passed

## References

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot docs](https://python-telegram-bot.readthedocs.io/)
