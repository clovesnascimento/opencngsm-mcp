"""
Device Monitoring Example
Demonstrates monitoring Android device status
"""
import asyncio
import json

async def monitor_device():
    """Monitor device battery, network, and apps"""
    
    print("📊 Android Device Monitor\n")
    print("=" * 50)
    
    # Get device info
    print("\n🔍 Device Information:")
    # device_info = await mcp.call_tool("android_device_info", {})
    # print(json.dumps(device_info, indent=2))
    print("  Model: Pixel 7")
    print("  Brand: Google")
    print("  Android: 14")
    print("  Display: 1080x2400")
    
    # Get battery status
    print("\n🔋 Battery Status:")
    # battery = await mcp.call_tool("android_get_battery", {})
    # print(json.dumps(battery, indent=2))
    print("  Level: 85%")
    print("  Status: Charging")
    print("  Temperature: 32.5°C")
    
    # List installed apps
    print("\n📱 Installed Apps (user):")
    # apps = await mcp.call_tool("android_list_apps", {"system": False})
    # for app in apps["packages"][:10]:
    #     print(f"  - {app}")
    print("  - com.whatsapp")
    print("  - com.instagram.android")
    print("  - com.spotify.music")
    print("  - com.google.android.youtube")
    print("  - ... (and more)")
    
    # Take screenshot
    print("\n📸 Taking screenshot...")
    # await mcp.call_tool("android_screenshot", {"output_path": "device_screen.png"})
    print("  ✅ Saved to: device_screen.png")
    
    print("\n" + "=" * 50)
    print("✅ Monitoring complete!")

# Example usage
if __name__ == "__main__":
    asyncio.run(monitor_device())
