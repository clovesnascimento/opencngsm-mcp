---
name: whatsapp
description: WhatsApp integration using Baileys library with QR code pairing, send/receive messages, media support (photos, videos, voice), typing indicators, and read receipts. Use when user mentions WhatsApp or wants to send WhatsApp messages.
license: MIT
metadata:
  author: opencngsm
  version: "3.0"
  requires: Node.js 18+, @whiskeysockets/baileys==6.5.0, aiohttp==3.9.1
compatibility: Requires Node.js for Baileys server
---

# WhatsApp Skill

## When to use this skill

Use this skill when the user wants to:
- Send WhatsApp messages
- Receive WhatsApp messages
- Send photos/videos
- Send voice messages
- Handle WhatsApp bot interactions
- QR code pairing

## Setup

1. **Install Node.js** (18+):
   - Download from: https://nodejs.org/

2. **Install Baileys dependencies:**
   ```bash
   cd skills/whatsapp/baileys
   npm install
   ```

3. **Install Python dependencies:**
   ```bash
   pip install aiohttp==3.9.1
   ```

4. **First run (QR pairing):**
   - Start Baileys server: `node skills/whatsapp/baileys/index.js`
   - Scan QR code with WhatsApp mobile app
   - Session saved to `auth_info/`

## How to use

### Start WhatsApp

```python
from skills.whatsapp.whatsapp_skill import WhatsAppSkill

whatsapp = WhatsAppSkill()

# Start Baileys server
await whatsapp.start()

# Get QR code for pairing (first time)
qr = await whatsapp.get_qr_code()
if qr:
    print("Scan this QR code with WhatsApp:")
    print(qr)
```

### Send message

```python
# Send text message
await whatsapp.send_message(
    to='5511999999999@s.whatsapp.net',  # Phone number
    message='Hello from OpenCngsm!'
)

# Send with typing indicator
await whatsapp.send_typing(to='5511999999999@s.whatsapp.net')
await asyncio.sleep(2)
await whatsapp.send_message(to='5511999999999@s.whatsapp.net', message='Processing...')
```

### Send media

```python
# Send photo
await whatsapp.send_image(
    to='5511999999999@s.whatsapp.net',
    image_path='photo.jpg',
    caption='Check this out!'
)

# Send video
await whatsapp.send_video(
    to='5511999999999@s.whatsapp.net',
    video_path='video.mp4',
    caption='Video message'
)

# Send voice message
await whatsapp.send_voice(
    to='5511999999999@s.whatsapp.net',
    audio_path='voice.ogg'
)
```

### Receive messages

```python
# Set message handler
async def handle_message(message):
    from_number = message['key']['remoteJid']
    text = message['message']['conversation']
    
    print(f"From: {from_number}")
    print(f"Message: {text}")
    
    # Reply
    await whatsapp.send_message(from_number, f"You said: {text}")

whatsapp.on_message(handle_message)
```

## Features

- ✅ Send text messages
- ✅ Receive messages
- ✅ Send photos
- ✅ Send videos
- ✅ Send voice messages
- ✅ Typing indicator
- ✅ Read receipts
- ✅ QR code pairing
- ✅ Multi-device support
- ✅ Session persistence
- ✅ Auto-reconnection

## Phone Number Format

WhatsApp uses JID format:
- **Individual**: `5511999999999@s.whatsapp.net`
- **Group**: `123456789-1234567890@g.us`

Example:
```python
# Brazil mobile: +55 11 99999-9999
jid = '5511999999999@s.whatsapp.net'
```

## Implementation

See [whatsapp_skill.py](whatsapp_skill.py) for Python wrapper and [baileys/index.js](baileys/index.js) for Node.js server.

## Examples

See [examples/whatsapp_bot.py](../../examples/whatsapp_bot.py) for a complete bot example.

## Troubleshooting

### "Baileys server not responding"
- Check if Node.js is installed: `node --version`
- Start server manually: `node skills/whatsapp/baileys/index.js`
- Check port 3000 is not in use

### "QR code not appearing"
- Delete `auth_info/` folder
- Restart Baileys server
- QR code expires after 60 seconds

### "Connection lost"
- WhatsApp may disconnect after inactivity
- Auto-reconnection is enabled
- Check internet connection

### "Message not sent"
- Verify phone number format (JID)
- Check if number is registered on WhatsApp
- Ensure session is active

## Security

- ⚠️ Never commit `auth_info/` folder
- ✅ Add to `.gitignore`
- ✅ Session data is encrypted by Baileys
- ✅ End-to-end encryption (native WhatsApp)

## Architecture

```
Python (OpenCngsm)
    ↓ HTTP/WebSocket
Baileys Server (Node.js)
    ↓ WhatsApp Protocol
WhatsApp Servers
```

## References

- [Baileys GitHub](https://github.com/WhiskeySockets/Baileys)
- [WhatsApp Web Protocol](https://github.com/sigalor/whatsapp-web-reveng)
