# ESP32 MCP Server

MCP Server for controlling ESP32 devices running MicroPython Telegram bots.

## Features

- ✅ Device registration and management
- ✅ Bot code generation
- ✅ Multiple device support
- ✅ Persistent device storage
- ✅ Integration with OpenCngsm

## Installation

1. Install dependencies:
   ```bash
   pip install mcp
   ```

2. Configure MCP server in your `mcp_config.json`:
   ```json
   {
     "mcpServers": {
       "esp32-telegram": {
         "command": "python",
         "args": ["servers/esp32_server/esp32_server.py"]
       }
     }
   }
   ```

## MCP Tools

### `esp32_register_device`

Register a new ESP32 device.

**Parameters:**
- `device_id` (string): Unique device identifier
- `bot_token` (string): Telegram bot token from @BotFather
- `wifi_ssid` (string): WiFi network SSID
- `wifi_password` (string): WiFi password
- `endpoint` (string, optional): HTTP endpoint (default: http://{device_id}.local)

**Example:**
```json
{
  "device_id": "living-room-esp32",
  "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
  "wifi_ssid": "MyWiFi",
  "wifi_password": "mypassword"
}
```

### `esp32_list_devices`

List all registered ESP32 devices.

**Returns:**
```json
{
  "status": "success",
  "count": 2,
  "devices": [
    {
      "device_id": "living-room-esp32",
      "bot_token": "123456:ABC...",
      "wifi_ssid": "MyWiFi",
      "endpoint": "http://living-room-esp32.local",
      "status": "unknown",
      "last_seen": null
    }
  ]
}
```

### `esp32_get_device`

Get information about a specific device.

**Parameters:**
- `device_id` (string): Device identifier

### `esp32_remove_device`

Remove a device from registry.

**Parameters:**
- `device_id` (string): Device identifier

### `esp32_generate_bot_code`

Generate MicroPython code for ESP32 bot.

**Parameters:**
- `device_id` (string): Device identifier
- `callback_type` (string): "echo", "forward", or "custom"

**Returns:**
- Generated MicroPython code
- Deployment instructions

## Usage Example

### 1. Register Device

```python
# Using MCP tool
result = await mcp.call_tool("esp32_register_device", {
    "device_id": "my-esp32",
    "bot_token": "YOUR_BOT_TOKEN",
    "wifi_ssid": "YOUR_WIFI",
    "wifi_password": "YOUR_PASSWORD"
})
```

### 2. Generate Bot Code

```python
# Generate echo bot code
result = await mcp.call_tool("esp32_generate_bot_code", {
    "device_id": "my-esp32",
    "callback_type": "echo"
})

# Save code to file
with open("my_bot.py", "w") as f:
    f.write(result["code"])
```

### 3. Deploy to ESP32

```bash
# Copy telegram.py library
mp cp servers/esp32_server/micropython/telegram.py :

# Copy your bot code
mp cp my_bot.py :

# Run bot
mp run my_bot.py
```

## Directory Structure

```
servers/esp32_server/
├── esp32_server.py          # Main MCP server
├── mcp_config.json          # MCP configuration
├── micropython/
│   ├── telegram.py          # Telegram bot library
│   └── README.md            # Library documentation
├── examples/
│   ├── echo_bot.py          # Echo bot example
│   └── command_bot.py       # Command handler example
└── README.md                # This file
```

## Configuration

Device configuration is stored in:
```
~/.config/opencngsm/esp32/devices.json
```

## Troubleshooting

**MCP server not starting:**
- Check Python path
- Verify mcp library is installed
- Check logs in console

**Device not registering:**
- Verify bot token is valid
- Check WiFi credentials
- Ensure device_id is unique

**Bot not working on ESP32:**
- Verify telegram.py is copied to device
- Check WiFi connection
- Monitor serial output for errors

## Examples

See `examples/` directory for:
- `echo_bot.py` - Simple echo bot
- `command_bot.py` - Bot with /start, /status, /help commands

## License

BSD 2-Clause License
