# ESP32 Telegram Bot - MicroPython Library

Simple, non-blocking Telegram bot library for MicroPython on ESP32.

## Features

- ✅ Non-blocking async operation
- ✅ SSL/TLS support
- ✅ UTF-16 surrogate pair handling
- ✅ Memory efficient (4KB buffer)
- ✅ WiFi connection management
- ✅ Message batching ("gluing")
- ✅ Watchdog for connection monitoring

## Installation

1. Copy `telegram.py` to your ESP32:
   ```bash
   mp cp telegram.py :
   ```

2. Create your bot code (see examples below)

## Quick Start

```python
import uasyncio as asyncio
from telegram import TelegramBot

# Configuration
Token = "YOUR_BOT_TOKEN_FROM_BOTFATHER"
WifiNetwork = "YOUR_WIFI_SSID"
WifiPassword = "YOUR_WIFI_PASSWORD"

# Callback function
def mycallback(bot, msg_type, chat_name, sender_name, chat_id, text, entry):
    print(f"Received: {text} from {sender_name}")
    bot.send(chat_id, "Echo: " + text)

# Initialize and run bot
bot = TelegramBot(Token, mycallback)
bot.connect_wifi(WifiNetwork, WifiPassword)
asyncio.create_task(bot.run())
loop = asyncio.get_event_loop()
loop.run_forever()
```

## API Reference

### TelegramBot Class

#### Constructor
```python
TelegramBot(token, callback)
```
- `token`: Bot token from @BotFather
- `callback`: Function to handle incoming messages

#### Methods

**`connect_wifi(ssid, password, timeout=30)`**
- Connect to WiFi network
- Blocks until connected or timeout

**`send(chat_id, text, glue=False)`**
- Send message to chat
- `glue=True`: Batch messages to same chat (up to 2KB)

**`stop()`**
- Stop the bot task

**`run()`**
- Main bot loop (async, run with `asyncio.create_task()`)

### Callback Function

```python
def callback(bot, msg_type, chat_name, sender_name, chat_id, text, entry):
    pass
```

**Parameters:**
- `bot`: TelegramBot instance
- `msg_type`: "private", "group", "supergroup", or "channel"
- `chat_name`: Group/channel name (None for private)
- `sender_name`: Telegram username
- `chat_id`: Chat ID (use for replies)
- `text`: Message text (UTF-8)
- `entry`: Raw JSON from Telegram API

## Examples

### Echo Bot
```python
def echo_callback(bot, msg_type, chat_name, sender_name, chat_id, text, entry):
    bot.send(chat_id, "Echo: " + text)
```

### Command Handler
```python
def command_callback(bot, msg_type, chat_name, sender_name, chat_id, text, entry):
    if text.startswith("/start"):
        bot.send(chat_id, "Welcome! I'm your ESP32 bot.")
    elif text.startswith("/status"):
        bot.send(chat_id, "ESP32 is running!")
    else:
        bot.send(chat_id, "Unknown command")
```

### Group Admin Bot
```python
def admin_callback(bot, msg_type, chat_name, sender_name, chat_id, text, entry):
    if msg_type == "group":
        bot.send(chat_id, f"Message in {chat_name}: {text}")
```

## Integration with OpenCngsm

Use the ESP32 MCP Server to manage bots:

```bash
# Register device
esp32_register_device \
  --device_id "my-esp32" \
  --bot_token "YOUR_TOKEN" \
  --wifi_ssid "YOUR_SSID" \
  --wifi_password "YOUR_PASSWORD"

# Generate bot code
esp32_generate_bot_code \
  --device_id "my-esp32" \
  --callback_type "echo"
```

## Troubleshooting

**Bot not receiving messages in groups:**
- Make sure bot has admin privileges in the group

**Connection timeout:**
- Check WiFi credentials
- Verify bot token
- Ensure ESP32 has internet access

**Memory errors:**
- Reduce buffer size in telegram.py
- Use message gluing to reduce API calls

## License

BSD 2-Clause License

## Credits

Based on the MicroPython Telegram bot library by Salvatore Sanfilippo
