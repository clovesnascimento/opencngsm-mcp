# ESP32 Telegram Bot - Command Handler Example
# Responds to commands like /start, /status, /help

### Configuration - EDIT THESE VALUES
Token = "YOUR_BOT_TOKEN_FROM_BOTFATHER"
WifiNetwork = "YOUR_WIFI_SSID"
WifiPassword = "YOUR_WIFI_PASSWORD"
###

import uasyncio as asyncio
from telegram import TelegramBot
import machine
import gc

def command_callback(bot, msg_type, chat_name, sender_name, chat_id, text, entry):
    """Handle bot commands"""
    print(f"[{msg_type}] {sender_name}: {text}")
    
    # Command handling
    if text.startswith("/start"):
        bot.send(chat_id, "🤖 Welcome! I'm your ESP32 bot.\n\nAvailable commands:\n/status - System status\n/help - Show this message")
    
    elif text.startswith("/status"):
        # Get system info
        freq = machine.freq() // 1000000
        mem_free = gc.mem_free() // 1024
        mem_alloc = gc.mem_alloc() // 1024
        
        status_msg = f"📊 ESP32 Status:\n\n"
        status_msg += f"CPU: {freq} MHz\n"
        status_msg += f"Memory Free: {mem_free} KB\n"
        status_msg += f"Memory Used: {mem_alloc} KB"
        
        bot.send(chat_id, status_msg)
    
    elif text.startswith("/help"):
        help_msg = "🤖 ESP32 Bot Commands:\n\n"
        help_msg += "/start - Welcome message\n"
        help_msg += "/status - System status\n"
        help_msg += "/help - Show this message"
        
        bot.send(chat_id, help_msg)
    
    else:
        bot.send(chat_id, f"Unknown command: {text}\n\nUse /help for available commands")

# Initialize bot
bot = TelegramBot(Token, command_callback)

# Connect to WiFi
print("Connecting to WiFi...")
bot.connect_wifi(WifiNetwork, WifiPassword)
print("WiFi connected!")

# Run bot
print("Starting command bot...")
asyncio.create_task(bot.run())
loop = asyncio.get_event_loop()
loop.run_forever()
