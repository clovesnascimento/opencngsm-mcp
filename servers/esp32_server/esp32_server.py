"""
ESP32 MCP Server - Telegram Bot Integration
Enables OpenCngsm to control ESP32 devices running MicroPython Telegram bots
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("esp32_server")

class ESP32Device:
    """Represents an ESP32 device with Telegram bot"""
    
    def __init__(self, device_id: str, bot_token: str, wifi_ssid: str, wifi_password: str, endpoint: Optional[str] = None):
        self.device_id = device_id
        self.bot_token = bot_token
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.endpoint = endpoint or f"http://{device_id}.local"
        self.status = "unknown"
        self.last_seen = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert device to dictionary"""
        return {
            "device_id": self.device_id,
            "bot_token": self.bot_token[:10] + "..." if self.bot_token else None,
            "wifi_ssid": self.wifi_ssid,
            "endpoint": self.endpoint,
            "status": self.status,
            "last_seen": self.last_seen
        }

class DeviceManager:
    """Manages ESP32 devices"""
    
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.devices: Dict[str, ESP32Device] = {}
        self.load_devices()
    
    def load_devices(self):
        """Load devices from config file"""
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text())
                for device_data in data.get("devices", []):
                    device = ESP32Device(**device_data)
                    self.devices[device.device_id] = device
                logger.info(f"Loaded {len(self.devices)} devices")
            except Exception as e:
                logger.error(f"Error loading devices: {e}")
    
    def save_devices(self):
        """Save devices to config file"""
        try:
            data = {
                "devices": [
                    {
                        "device_id": d.device_id,
                        "bot_token": d.bot_token,
                        "wifi_ssid": d.wifi_ssid,
                        "wifi_password": d.wifi_password,
                        "endpoint": d.endpoint
                    }
                    for d in self.devices.values()
                ]
            }
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(json.dumps(data, indent=2))
            logger.info(f"Saved {len(self.devices)} devices")
        except Exception as e:
            logger.error(f"Error saving devices: {e}")
    
    def register(self, device: ESP32Device):
        """Register a new device"""
        self.devices[device.device_id] = device
        self.save_devices()
    
    def get(self, device_id: str) -> Optional[ESP32Device]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def list_all(self) -> List[ESP32Device]:
        """List all devices"""
        return list(self.devices.values())
    
    def remove(self, device_id: str) -> bool:
        """Remove a device"""
        if device_id in self.devices:
            del self.devices[device_id]
            self.save_devices()
            return True
        return False

class ESP32Server:
    """MCP Server for ESP32 Telegram bot integration"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.device_manager = DeviceManager(self.config_dir / "devices.json")
        self.server = Server("esp32-telegram-server")
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available ESP32 tools"""
            return [
                Tool(
                    name="esp32_register_device",
                    description="Register a new ESP32 device with Telegram bot",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Unique identifier for the device (e.g., 'living-room-esp32')"
                            },
                            "bot_token": {
                                "type": "string",
                                "description": "Telegram bot token from @BotFather"
                            },
                            "wifi_ssid": {
                                "type": "string",
                                "description": "WiFi network SSID"
                            },
                            "wifi_password": {
                                "type": "string",
                                "description": "WiFi network password"
                            },
                            "endpoint": {
                                "type": "string",
                                "description": "Optional HTTP endpoint (default: http://{device_id}.local)"
                            }
                        },
                        "required": ["device_id", "bot_token", "wifi_ssid", "wifi_password"]
                    }
                ),
                Tool(
                    name="esp32_list_devices",
                    description="List all registered ESP32 devices",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="esp32_get_device",
                    description="Get information about a specific ESP32 device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Device identifier"
                            }
                        },
                        "required": ["device_id"]
                    }
                ),
                Tool(
                    name="esp32_remove_device",
                    description="Remove an ESP32 device from registry",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Device identifier"
                            }
                        },
                        "required": ["device_id"]
                    }
                ),
                Tool(
                    name="esp32_generate_bot_code",
                    description="Generate MicroPython code for ESP32 Telegram bot",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Device identifier"
                            },
                            "callback_type": {
                                "type": "string",
                                "description": "Type of callback: 'echo', 'forward', 'custom'",
                                "enum": ["echo", "forward", "custom"]
                            }
                        },
                        "required": ["device_id", "callback_type"]
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[TextContent]:
            """Handle tool calls"""
            
            if name == "esp32_register_device":
                return await self._register_device(arguments)
            elif name == "esp32_list_devices":
                return await self._list_devices()
            elif name == "esp32_get_device":
                return await self._get_device(arguments)
            elif name == "esp32_remove_device":
                return await self._remove_device(arguments)
            elif name == "esp32_generate_bot_code":
                return await self._generate_bot_code(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    async def _register_device(self, args: dict) -> List[TextContent]:
        """Register a new ESP32 device"""
        try:
            device = ESP32Device(
                device_id=args["device_id"],
                bot_token=args["bot_token"],
                wifi_ssid=args["wifi_ssid"],
                wifi_password=args["wifi_password"],
                endpoint=args.get("endpoint")
            )
            
            self.device_manager.register(device)
            
            result = {
                "status": "success",
                "message": f"Device '{device.device_id}' registered successfully",
                "device": device.to_dict()
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except Exception as e:
            logger.error(f"Error registering device: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _list_devices(self) -> List[TextContent]:
        """List all registered devices"""
        devices = self.device_manager.list_all()
        
        result = {
            "status": "success",
            "count": len(devices),
            "devices": [d.to_dict() for d in devices]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _get_device(self, args: dict) -> List[TextContent]:
        """Get device information"""
        device = self.device_manager.get(args["device_id"])
        
        if not device:
            return [TextContent(type="text", text=f"Error: Device '{args['device_id']}' not found")]
        
        result = {
            "status": "success",
            "device": device.to_dict()
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _remove_device(self, args: dict) -> List[TextContent]:
        """Remove a device"""
        success = self.device_manager.remove(args["device_id"])
        
        if success:
            result = {
                "status": "success",
                "message": f"Device '{args['device_id']}' removed"
            }
        else:
            result = {
                "status": "error",
                "message": f"Device '{args['device_id']}' not found"
            }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _generate_bot_code(self, args: dict) -> List[TextContent]:
        """Generate MicroPython bot code"""
        device = self.device_manager.get(args["device_id"])
        
        if not device:
            return [TextContent(type="text", text=f"Error: Device '{args['device_id']}' not found")]
        
        callback_type = args.get("callback_type", "echo")
        
        # Generate code based on callback type
        if callback_type == "echo":
            callback_code = """def mycallback(bot,msg_type,chat_name,sender_name,chat_id,text,entry):
    print(msg_type,chat_name,sender_name,chat_id,text)
    bot.send(chat_id,"Echo: "+text)"""
        elif callback_type == "forward":
            callback_code = """def mycallback(bot,msg_type,chat_name,sender_name,chat_id,text,entry):
    print(msg_type,chat_name,sender_name,chat_id,text)
    # Forward to OpenCngsm via HTTP
    # TODO: Implement HTTP forwarding"""
        else:
            callback_code = """def mycallback(bot,msg_type,chat_name,sender_name,chat_id,text,entry):
    # Custom callback - implement your logic here
    print(msg_type,chat_name,sender_name,chat_id,text)"""
        
        code = f"""# ESP32 Telegram Bot - Generated for {device.device_id}
# Copy telegram.py to your ESP32 first: mp cp telegram.py :

### Configuration
Token = "{device.bot_token}"
WifiNetwork = "{device.wifi_ssid}"
WifiPassword = "{device.wifi_password}"
###

import uasyncio as asyncio
from telegram import TelegramBot

{callback_code}

bot = TelegramBot(Token, mycallback)
bot.connect_wifi(WifiNetwork, WifiPassword)
asyncio.create_task(bot.run())
loop = asyncio.get_event_loop()
loop.run_forever()
"""
        
        result = {
            "status": "success",
            "device_id": device.device_id,
            "callback_type": callback_type,
            "code": code,
            "instructions": [
                "1. Copy telegram.py to ESP32: mp cp telegram.py :",
                f"2. Save this code as {device.device_id}_bot.py",
                f"3. Run on ESP32: mp run {device.device_id}_bot.py"
            ]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("ESP32 MCP Server starting...")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main entry point"""
    import sys
    from pathlib import Path
    
    # Default config directory
    config_dir = Path.home() / ".config" / "opencngsm" / "esp32"
    
    server = ESP32Server(config_dir)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
