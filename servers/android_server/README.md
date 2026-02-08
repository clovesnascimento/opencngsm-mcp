# Android ADB MCP Server

MCP Server for controlling Android devices via ADB and uiautomator2.

## ✨ Features

### **Phase 1 Tools (14 tools)**

#### **Device Management**
- ✅ `android_list_devices` - List connected devices
- ✅ `android_device_info` - Get device information

#### **App Control**
- ✅ `android_start_app` - Start application
- ✅ `android_stop_app` - Stop application
- ✅ `android_list_apps` - List installed apps

#### **Input Simulation**
- ✅ `android_tap` - Tap at coordinates
- ✅ `android_swipe` - Swipe gesture
- ✅ `android_input_text` - Type text
- ✅ `android_press_key` - Press key (back/home/recent/power/volume)

#### **UI Automation (uiautomator2)**
- ✅ `android_find_element` - Find UI element
- ✅ `android_click_element` - Click UI element
- ✅ `android_get_text` - Get element text

#### **Screen Capture**
- ✅ `android_screenshot` - Take screenshot
- ✅ `android_get_ui_hierarchy` - Get UI XML

#### **System Info**
- ✅ `android_get_battery` - Battery status

---

## 📋 Prerequisites

### **Hardware**
- Android device (Android 7.0+)
- USB cable
- Computer with ADB

### **Software**
- Python 3.11+
- ADB (Android SDK Platform-Tools)
- USB drivers (Windows only)

---

## 🚀 Installation

### **1. Install ADB**

**Windows:**
```bash
# Download Android SDK Platform-Tools
# https://developer.android.com/tools/releases/platform-tools

# Extract and add to PATH
```

**Linux:**
```bash
sudo apt install android-tools-adb
```

**macOS:**
```bash
brew install android-platform-tools
```

### **2. Enable USB Debugging on Android**

1. Go to **Settings** > **About phone**
2. Tap **Build number** 7 times
3. Go back to **Settings** > **Developer options**
4. Enable **USB debugging**
5. Connect device via USB
6. Authorize computer when prompted

### **3. Verify ADB Connection**

```bash
adb devices
```

Should show:
```
List of devices attached
ABC123456789    device
```

### **4. Install Python Dependencies**

```bash
cd servers/android_server
pip install -r requirements.txt

# Initialize uiautomator2 on device
python -m uiautomator2 init
```

---

## 🔧 Configuration

Add to your MCP config file:

```json
{
  "mcpServers": {
    "android-adb": {
      "command": "python",
      "args": ["servers/android_server/android_server.py"]
    }
  }
}
```

---

## 📖 Usage Examples

### **Device Management**

```python
# List connected devices
await mcp.call_tool("android_list_devices", {})
# Returns: {"count": 1, "devices": ["ABC123456789"]}

# Get device info
await mcp.call_tool("android_device_info", {})
# Returns: {"model": "Pixel 7", "brand": "Google", "version": "14", ...}
```

### **App Control**

```python
# Start WhatsApp
await mcp.call_tool("android_start_app", {
    "package_name": "com.whatsapp"
})

# Stop WhatsApp
await mcp.call_tool("android_stop_app", {
    "package_name": "com.whatsapp"
})

# List installed apps
await mcp.call_tool("android_list_apps", {
    "system": False  # User apps only
})
```

### **Input Simulation**

```python
# Tap at coordinates
await mcp.call_tool("android_tap", {"x": 500, "y": 1000})

# Swipe (scroll down)
await mcp.call_tool("android_swipe", {
    "x1": 500, "y1": 1500,
    "x2": 500, "y2": 500,
    "duration": 0.5
})

# Type text
await mcp.call_tool("android_input_text", {
    "text": "Hello World!"
})

# Press back button
await mcp.call_tool("android_press_key", {"key": "back"})
```

### **UI Automation**

```python
# Find element by text
await mcp.call_tool("android_find_element", {
    "text": "Send",
    "timeout": 10
})

# Click element by text
await mcp.call_tool("android_click_element", {
    "text": "New chat"
})

# Click element by resource ID
await mcp.call_tool("android_click_element", {
    "resource_id": "com.whatsapp:id/send"
})

# Get text from element
await mcp.call_tool("android_get_text", {
    "resource_id": "com.whatsapp:id/conversation_contact_name"
})
```

### **Screen Capture**

```python
# Take screenshot
await mcp.call_tool("android_screenshot", {
    "output_path": "screenshot.png"
})

# Get UI hierarchy (for debugging)
await mcp.call_tool("android_get_ui_hierarchy", {})
```

### **System Info**

```python
# Get battery status
await mcp.call_tool("android_get_battery", {})
# Returns: {"level": 85, "status": "Charging", "temperature": 32.5}
```

---

## 📱 Common Package Names

| App | Package Name |
|-----|--------------|
| WhatsApp | `com.whatsapp` |
| Instagram | `com.instagram.android` |
| Chrome | `com.android.chrome` |
| YouTube | `com.google.android.youtube` |
| Gmail | `com.google.android.gm` |
| Spotify | `com.spotify.music` |
| Telegram | `org.telegram.messenger` |

---

## 🎯 Examples

See `examples/` directory:
- `whatsapp_automation.py` - Send WhatsApp message
- `instagram_automation.py` - Post to Instagram
- `device_monitor.py` - Monitor device status

---

## 🔍 Debugging

### **Find Element Selectors**

```python
# Get UI hierarchy
hierarchy = await mcp.call_tool("android_get_ui_hierarchy", {})

# Save to file and inspect
with open("ui_hierarchy.xml", "w") as f:
    f.write(hierarchy["xml"])
```

### **Enable Pointer Location**

On device:
1. **Developer options** > **Pointer location**
2. Tap screen to see coordinates

### **Check ADB Connection**

```bash
adb devices
adb shell dumpsys window | grep mCurrentFocus
```

---

## ⚠️ Limitations

| Feature | Status | Workaround |
|---------|--------|------------|
| Direct phone calls | ❌ Limited | Use `open_dialer` (Phase 2) |
| Direct SMS sending | ❌ Limited | Use `open_sms` (Phase 2) |
| Lock screen interaction | ❌ Not supported | Ensure device is unlocked |
| WiFi connection | 🔄 Phase 2 | USB only for now |

---

## 🔐 Security

- **USB Debugging** is a powerful feature - disable when not in use
- Only authorize trusted computers
- Be cautious with automation scripts
- Review permissions before running

---

## 🐛 Troubleshooting

**Device not detected:**
```bash
# Check USB connection
adb devices

# Restart ADB server
adb kill-server
adb start-server
```

**uiautomator2 not working:**
```bash
# Reinitialize
python -m uiautomator2 init

# Check ATX agent
adb shell pm list packages | grep atx
```

**Element not found:**
- Use `android_get_ui_hierarchy` to inspect
- Try different selectors (text, resource_id, class_name)
- Increase timeout
- Ensure app is fully loaded

---

## 📚 Resources

- [ADB Documentation](https://developer.android.com/tools/adb)
- [uiautomator2 Documentation](https://github.com/openatx/uiautomator2)
- [Android Developer Options](https://developer.android.com/studio/debug/dev-options)

---

**Version:** OpenCngsm v3.3  
**Phase:** 1 (14 tools)  
**Status:** ✅ Production Ready
