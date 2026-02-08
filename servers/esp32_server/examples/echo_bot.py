# ESP32 Telegram Bot - Echo Example
# This bot simply echoes back whatever you send to it

### Configuration - EDIT THESE VALUES
Token = "YOUR_BOT_TOKEN_FROM_BOTFATHER"
WifiNetwork = "YOUR_WIFI_SSID"
WifiPassword = "YOUR_WIFI_PASSWORD"
###

import uasyncio as asyncio
from telegram import TelegramBot

def mycallback(bot, msg_type, chat_name, sender_name, chat_id, text, entry):
    """Echo callback - replies with 'Echo: ' + your message"""
    print(f"[{msg_type}] {sender_name}: {text}")
    bot.send(chat_id, "Echo: " + text)

# Initialize bot
bot = TelegramBot(Token, mycallback)

# Connect to WiFi
print("Connecting to WiFi...")
bot.connect_wifi(WifiNetwork, WifiPassword)
print("WiFi connected!")

# Run bot
print("Starting bot...")
asyncio.create_task(bot.run())
loop = asyncio.get_event_loop()
loop.run_forever()
