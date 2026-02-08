"""
Android ADB MCP Server
Enables OpenCngsm to control Android devices via ADB and uiautomator2
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from mcp.server import Server
from mcp.types import Tool, TextContent
import uiautomator2 as u2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("android_server")

class AndroidDevice:
    """Represents an Android device"""
    
    def __init__(self, serial: str):
        self.serial = serial
        self.device = None
        self._connect()
    
    def _connect(self):
        """Connect to device via uiautomator2"""
        try:
            self.device = u2.connect(self.serial)
            logger.info(f"Connected to device: {self.serial}")
        except Exception as e:
            logger.error(f"Failed to connect to {self.serial}: {e}")
            raise
    
    def get_info(self) -> Dict[str, Any]:
        """Get device information"""
        try:
            info = self.device.info
            return {
                "serial": self.serial,
                "model": info.get("productName", "Unknown"),
                "brand": info.get("brand", "Unknown"),
                "version": info.get("version", "Unknown"),
                "sdk": info.get("sdkInt", 0),
                "display": {
                    "width": info.get("displayWidth", 0),
                    "height": info.get("displayHeight", 0)
                }
            }
        except Exception as e:
            return {"error": str(e), "serial": self.serial}

class DeviceManager:
    """Manages Android devices"""
    
    def __init__(self):
        self.devices: Dict[str, AndroidDevice] = {}
    
    def list_devices(self) -> List[str]:
        """List connected devices"""
        try:
            import subprocess
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            devices = []
            for line in result.stdout.split('\n')[1:]:
                if '\tdevice' in line:
                    serial = line.split('\t')[0]
                    devices.append(serial)
            
            return devices
        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            return []
    
    def get_device(self, serial: Optional[str] = None) -> Optional[AndroidDevice]:
        """Get device by serial or first available"""
        if serial:
            if serial not in self.devices:
                self.devices[serial] = AndroidDevice(serial)
            return self.devices[serial]
        
        # Get first available device
        available = self.list_devices()
        if not available:
            return None
        
        serial = available[0]
        if serial not in self.devices:
            self.devices[serial] = AndroidDevice(serial)
        
        return self.devices[serial]

class AndroidServer:
    """MCP Server for Android device control"""
    
    def __init__(self):
        self.device_manager = DeviceManager()
        self.server = Server("android-adb-server")
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available Android tools"""
            return [
                # Device Management
                Tool(
                    name="android_list_devices",
                    description="List all connected Android devices",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="android_device_info",
                    description="Get device information (model, brand, version, display)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "serial": {
                                "type": "string",
                                "description": "Device serial number (optional, uses first device if not specified)"
                            }
                        }
                    }
                ),
                
                # App Control
                Tool(
                    name="android_start_app",
                    description="Start an application by package name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "package_name": {
                                "type": "string",
                                "description": "Package name (e.g., 'com.whatsapp')"
                            },
                            "serial": {
                                "type": "string",
                                "description": "Device serial (optional)"
                            }
                        },
                        "required": ["package_name"]
                    }
                ),
                Tool(
                    name="android_stop_app",
                    description="Stop/force close an application",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "package_name": {
                                "type": "string",
                                "description": "Package name to stop"
                            },
                            "serial": {
                                "type": "string",
                                "description": "Device serial (optional)"
                            }
                        },
                        "required": ["package_name"]
                    }
                ),
                Tool(
                    name="android_list_apps",
                    description="List installed applications",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "serial": {
                                "type": "string",
                                "description": "Device serial (optional)"
                            },
                            "system": {
                                "type": "boolean",
                                "description": "Include system apps (default: false)"
                            }
                        }
                    }
                ),
                
                # Input Simulation
                Tool(
                    name="android_tap",
                    description="Simulate screen tap at coordinates",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "x": {
                                "type": "number",
                                "description": "X coordinate"
                            },
                            "y": {
                                "type": "number",
                                "description": "Y coordinate"
                            },
                            "serial": {
                                "type": "string",
                                "description": "Device serial (optional)"
                            }
                        },
                        "required": ["x", "y"]
                    }
                ),
                Tool(
                    name="android_swipe",
                    description="Simulate swipe gesture",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "x1": {"type": "number", "description": "Start X"},
                            "y1": {"type": "number", "description": "Start Y"},
                            "x2": {"type": "number", "description": "End X"},
                            "y2": {"type": "number", "description": "End Y"},
                            "duration": {
                                "type": "number",
                                "description": "Duration in seconds (default: 0.5)"
                            },
                            "serial": {"type": "string", "description": "Device serial (optional)"}
                        },
                        "required": ["x1", "y1", "x2", "y2"]
                    }
                ),
                Tool(
                    name="android_input_text",
                    description="Type text into focused field",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to type"
                            },
                            "serial": {
                                "type": "string",
                                "description": "Device serial (optional)"
                            }
                        },
                        "required": ["text"]
                    }
                ),
                Tool(
                    name="android_press_key",
                    description="Press a key (back, home, recent, etc.)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "Key name: 'back', 'home', 'recent', 'power', 'volume_up', 'volume_down'",
                                "enum": ["back", "home", "recent", "power", "volume_up", "volume_down"]
                            },
                            "serial": {
                                "type": "string",
                                "description": "Device serial (optional)"
                            }
                        },
                        "required": ["key"]
                    }
                ),
                
                # UI Automation
                Tool(
                    name="android_find_element",
                    description="Find UI element by text, resource ID, or class name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Element text"},
                            "resource_id": {"type": "string", "description": "Resource ID"},
                            "class_name": {"type": "string", "description": "Class name"},
                            "description": {"type": "string", "description": "Content description"},
                            "timeout": {"type": "number", "description": "Timeout in seconds (default: 10)"},
                            "serial": {"type": "string", "description": "Device serial (optional)"}
                        }
                    }
                ),
                Tool(
                    name="android_click_element",
                    description="Click UI element by text, resource ID, or class name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Element text"},
                            "resource_id": {"type": "string", "description": "Resource ID"},
                            "class_name": {"type": "string", "description": "Class name"},
                            "timeout": {"type": "number", "description": "Timeout in seconds (default: 10)"},
                            "serial": {"type": "string", "description": "Device serial (optional)"}
                        }
                    }
                ),
                Tool(
                    name="android_get_text",
                    description="Get text from UI element",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Element text"},
                            "resource_id": {"type": "string", "description": "Resource ID"},
                            "class_name": {"type": "string", "description": "Class name"},
                            "serial": {"type": "string", "description": "Device serial (optional)"}
                        }
                    }
                ),
                
                # Screen Capture
                Tool(
                    name="android_screenshot",
                    description="Take screenshot and save to file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "output_path": {
                                "type": "string",
                                "description": "Output file path (e.g., 'screenshot.png')"
                            },
                            "serial": {
                                "type": "string",
                                "description": "Device serial (optional)"
                            }
                        },
                        "required": ["output_path"]
                    }
                ),
                Tool(
                    name="android_get_ui_hierarchy",
                    description="Get UI hierarchy XML for current screen",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "serial": {
                                "type": "string",
                                "description": "Device serial (optional)"
                            }
                        }
                    }
                ),
                
                # System Info
                Tool(
                    name="android_get_battery",
                    description="Get battery status and level",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "serial": {
                                "type": "string",
                                "description": "Device serial (optional)"
                            }
                        }
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[TextContent]:
            """Handle tool calls"""
            
            try:
                if name == "android_list_devices":
                    return await self._list_devices()
                elif name == "android_device_info":
                    return await self._device_info(arguments)
                elif name == "android_start_app":
                    return await self._start_app(arguments)
                elif name == "android_stop_app":
                    return await self._stop_app(arguments)
                elif name == "android_list_apps":
                    return await self._list_apps(arguments)
                elif name == "android_tap":
                    return await self._tap(arguments)
                elif name == "android_swipe":
                    return await self._swipe(arguments)
                elif name == "android_input_text":
                    return await self._input_text(arguments)
                elif name == "android_press_key":
                    return await self._press_key(arguments)
                elif name == "android_find_element":
                    return await self._find_element(arguments)
                elif name == "android_click_element":
                    return await self._click_element(arguments)
                elif name == "android_get_text":
                    return await self._get_text(arguments)
                elif name == "android_screenshot":
                    return await self._screenshot(arguments)
                elif name == "android_get_ui_hierarchy":
                    return await self._get_ui_hierarchy(arguments)
                elif name == "android_get_battery":
                    return await self._get_battery(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
            except Exception as e:
                logger.error(f"Error in {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    # Tool implementations
    async def _list_devices(self) -> List[TextContent]:
        """List connected devices"""
        devices = self.device_manager.list_devices()
        result = {
            "status": "success",
            "count": len(devices),
            "devices": devices
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _device_info(self, args: dict) -> List[TextContent]:
        """Get device information"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        info = device.get_info()
        return [TextContent(type="text", text=json.dumps(info, indent=2))]
    
    async def _start_app(self, args: dict) -> List[TextContent]:
        """Start application"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        device.device.app_start(args["package_name"])
        result = {"status": "success", "package": args["package_name"]}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _stop_app(self, args: dict) -> List[TextContent]:
        """Stop application"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        device.device.app_stop(args["package_name"])
        result = {"status": "success", "package": args["package_name"]}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _list_apps(self, args: dict) -> List[TextContent]:
        """List installed apps"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        import subprocess
        cmd = ["adb", "-s", device.serial, "shell", "pm", "list", "packages"]
        if not args.get("system", False):
            cmd.append("-3")  # Third-party apps only
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        packages = [line.replace("package:", "").strip() 
                   for line in result.stdout.split('\n') if line.startswith("package:")]
        
        return [TextContent(type="text", text=json.dumps({
            "status": "success",
            "count": len(packages),
            "packages": packages
        }, indent=2))]
    
    async def _tap(self, args: dict) -> List[TextContent]:
        """Simulate tap"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        device.device.click(args["x"], args["y"])
        result = {"status": "success", "x": args["x"], "y": args["y"]}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _swipe(self, args: dict) -> List[TextContent]:
        """Simulate swipe"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        duration = args.get("duration", 0.5)
        device.device.swipe(args["x1"], args["y1"], args["x2"], args["y2"], duration)
        result = {"status": "success"}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _input_text(self, args: dict) -> List[TextContent]:
        """Input text"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        device.device.send_keys(args["text"])
        result = {"status": "success", "text": args["text"]}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _press_key(self, args: dict) -> List[TextContent]:
        """Press key"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        key_map = {
            "back": "back",
            "home": "home",
            "recent": "recent",
            "power": "power",
            "volume_up": "volume_up",
            "volume_down": "volume_down"
        }
        
        device.device.press(key_map[args["key"]])
        result = {"status": "success", "key": args["key"]}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _find_element(self, args: dict) -> List[TextContent]:
        """Find UI element"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        timeout = args.get("timeout", 10)
        selector = device.device
        
        if args.get("text"):
            selector = selector(text=args["text"])
        elif args.get("resource_id"):
            selector = selector(resourceId=args["resource_id"])
        elif args.get("class_name"):
            selector = selector(className=args["class_name"])
        elif args.get("description"):
            selector = selector(description=args["description"])
        else:
            return [TextContent(type="text", text="Error: No selector provided")]
        
        if selector.wait(timeout=timeout):
            info = selector.info
            bounds = info.get('bounds', {})
            result = {
                "found": True,
                "bounds": bounds,
                "text": info.get('text', ''),
                "resource_id": info.get('resourceName', ''),
                "class_name": info.get('className', '')
            }
        else:
            result = {"found": False}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _click_element(self, args: dict) -> List[TextContent]:
        """Click UI element"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        timeout = args.get("timeout", 10)
        selector = device.device
        
        if args.get("text"):
            selector = selector(text=args["text"])
        elif args.get("resource_id"):
            selector = selector(resourceId=args["resource_id"])
        elif args.get("class_name"):
            selector = selector(className=args["class_name"])
        else:
            return [TextContent(type="text", text="Error: No selector provided")]
        
        if selector.wait(timeout=timeout):
            selector.click()
            result = {"status": "success", "clicked": True}
        else:
            result = {"status": "error", "message": "Element not found"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _get_text(self, args: dict) -> List[TextContent]:
        """Get element text"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        selector = device.device
        
        if args.get("text"):
            selector = selector(text=args["text"])
        elif args.get("resource_id"):
            selector = selector(resourceId=args["resource_id"])
        elif args.get("class_name"):
            selector = selector(className=args["class_name"])
        else:
            return [TextContent(type="text", text="Error: No selector provided")]
        
        if selector.exists:
            text = selector.info.get('text', '')
            result = {"status": "success", "text": text}
        else:
            result = {"status": "error", "message": "Element not found"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _screenshot(self, args: dict) -> List[TextContent]:
        """Take screenshot"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        device.device.screenshot(args["output_path"])
        result = {"status": "success", "path": args["output_path"]}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _get_ui_hierarchy(self, args: dict) -> List[TextContent]:
        """Get UI hierarchy"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        xml = device.device.dump_hierarchy()
        result = {"status": "success", "xml": xml}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _get_battery(self, args: dict) -> List[TextContent]:
        """Get battery info"""
        device = self.device_manager.get_device(args.get("serial"))
        if not device:
            return [TextContent(type="text", text="Error: No device connected")]
        
        import subprocess
        result = subprocess.run(
            ["adb", "-s", device.serial, "shell", "dumpsys", "battery"],
            capture_output=True,
            text=True
        )
        
        battery_info = {}
        for line in result.stdout.split('\n'):
            if 'level:' in line:
                battery_info['level'] = int(line.split(':')[1].strip())
            elif 'status:' in line:
                battery_info['status'] = line.split(':')[1].strip()
            elif 'temperature:' in line:
                battery_info['temperature'] = int(line.split(':')[1].strip()) / 10
        
        return [TextContent(type="text", text=json.dumps({
            "status": "success",
            "battery": battery_info
        }, indent=2))]
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Android ADB MCP Server starting...")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main entry point"""
    server = AndroidServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
