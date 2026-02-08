# ESP32 Telegram Bot - Deployment Guide

Complete guide for deploying Telegram bots to ESP32 using OpenCngsm.

## Prerequisites

### Hardware
- ESP32 development board (ESP32, ESP32-S3, ESP32-C3)
- USB cable
- WiFi network

### Software
- Python 3.11+
- esptool (`pip install esptool`)
- mpremote (`pip install mpremote`)
- MicroPython firmware for ESP32

## Step 1: Flash MicroPython Firmware

### Download Firmware

Visit [micropython.org/download](https://micropython.org/download/esp32/) and download the latest firmware for your board.

### Flash Firmware

```bash
# Erase flash
esptool.py --port COM3 erase_flash

# Flash MicroPython
esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 esp32-20240222-v1.22.2.bin
```

**Note:** Replace `COM3` with your serial port (Linux: `/dev/ttyUSB0`, Mac: `/dev/tty.usbserial-*`)

## Step 2: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the bot token (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## Step 3: Register Device with OpenCngsm

### Using MCP Tool

```python
# Register your ESP32 device
await mcp.call_tool("esp32_register_device", {
    "device_id": "my-esp32",
    "bot_token": "YOUR_BOT_TOKEN_FROM_BOTFATHER",
    "wifi_ssid": "YOUR_WIFI_SSID",
    "wifi_password": "YOUR_WIFI_PASSWORD"
})
```

### Using CLI (if available)

```bash
opencngsm esp32 register \
  --device-id "my-esp32" \
  --bot-token "YOUR_BOT_TOKEN" \
  --wifi-ssid "YOUR_WIFI" \
  --wifi-password "YOUR_PASSWORD"
```

## Step 4: Generate Bot Code

```python
# Generate echo bot code
result = await mcp.call_tool("esp32_generate_bot_code", {
    "device_id": "my-esp32",
    "callback_type": "echo"  # or "forward", "custom"
})

# Save to file
with open("my_bot.py", "w") as f:
    f.write(result["code"])
```

## Step 5: Deploy to ESP32

### Copy telegram.py Library

```bash
# Navigate to server directory
cd servers/esp32_server/micropython

# Copy library to ESP32
mpremote cp telegram.py :
```

### Copy Your Bot Code

```bash
# Copy generated bot code
mpremote cp my_bot.py :
```

### Run Bot

```bash
# Run bot on ESP32
mpremote run my_bot.py
```

**For persistent operation**, save as `main.py`:

```bash
# Rename to main.py for auto-start
mpremote cp my_bot.py :main.py

# Soft reset to start
mpremote reset
```

## Step 6: Test Your Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start` or any message
4. Bot should respond!

## Monitoring and Debugging

### Serial Monitor

```bash
# Monitor serial output
mpremote
```

### Check WiFi Connection

```python
import network
sta = network.WLAN(network.STA_IF)
print(sta.isconnected())
print(sta.ifconfig())
```

### Check Memory

```python
import gc
print(f"Free memory: {gc.mem_free()} bytes")
```

## Troubleshooting

### Bot Not Connecting to WiFi

**Problem:** `Timedout connecting to WiFi network`

**Solutions:**
- Verify WiFi SSID and password
- Check WiFi signal strength
- Ensure 2.4GHz network (ESP32 doesn't support 5GHz)
- Try increasing timeout in `connect_wifi()`

### Bot Not Receiving Messages

**Problem:** Bot doesn't respond to messages

**Solutions:**
- Verify bot token is correct
- Check internet connectivity
- For group chats, give bot admin privileges
- Monitor serial output for errors

### Memory Errors

**Problem:** `MemoryError` or crashes

**Solutions:**
- Reduce buffer size in `telegram.py`
- Use message gluing (`glue=True`)
- Call `gc.collect()` periodically
- Simplify callback function

### SSL Errors

**Problem:** SSL handshake failures

**Solutions:**
- Update MicroPython firmware
- Check system time (if available)
- Verify internet connection

## Advanced Configuration

### Custom Callback

```python
def custom_callback(bot, msg_type, chat_name, sender_name, chat_id, text, entry):
    # Your custom logic here
    if text == "status":
        import machine
        freq = machine.freq() // 1000000
        bot.send(chat_id, f"CPU: {freq} MHz")
    else:
        bot.send(chat_id, "Unknown command")
```

### Enable Debug Mode

```python
bot = TelegramBot(Token, mycallback)
bot.debug = True  # Enable debug output
```

### Adjust Watchdog Timeout

```python
bot = TelegramBot(Token, mycallback)
bot.watchdog_timeout_ms = 120000  # 2 minutes
```

## File Structure on ESP32

After deployment, your ESP32 should have:

```
/
├── boot.py              # MicroPython boot script
├── main.py              # Your bot (auto-runs on boot)
└── telegram.py          # Telegram library
```

## Performance Tips

1. **Use message gluing** for multiple messages to same chat
2. **Call `gc.collect()`** periodically to free memory
3. **Keep callbacks simple** to avoid blocking
4. **Monitor memory usage** with `gc.mem_free()`
5. **Use watchdog** to auto-recover from hangs

## Security Best Practices

1. **Never commit bot tokens** to git
2. **Use environment variables** for sensitive data
3. **Validate all inputs** in callbacks
4. **Limit bot to specific users** if needed
5. **Monitor for unusual activity**

## Next Steps

- Add sensor reading to bot
- Implement actuator control
- Create custom commands
- Integrate with OpenCngsm agent
- Build smart home automation

## Resources

- [MicroPython Documentation](https://docs.micropython.org/)
- [ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [OpenCngsm Documentation](../../README.md)

---

**Generated:** 2026-02-08  
**Version:** OpenCngsm v3.3  
**ESP32 MCP Server**
