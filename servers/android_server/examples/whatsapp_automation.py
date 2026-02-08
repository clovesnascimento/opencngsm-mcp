"""
WhatsApp Automation Example
Demonstrates sending a message via WhatsApp using Android MCP Server
"""
import asyncio
import json

# Simulated MCP client calls (replace with actual MCP client)
async def send_whatsapp_message(contact_name: str, message: str):
    """
    Automate sending a WhatsApp message
    
    Args:
        contact_name: Contact name to search for
        message: Message to send
    """
    
    print(f"📱 Starting WhatsApp automation...")
    print(f"Contact: {contact_name}")
    print(f"Message: {message}\n")
    
    # Step 1: Start WhatsApp
    print("1️⃣ Starting WhatsApp...")
    # await mcp.call_tool("android_start_app", {"package_name": "com.whatsapp"})
    await asyncio.sleep(2)  # Wait for app to load
    
    # Step 2: Click on "New chat" button
    print("2️⃣ Opening new chat...")
    # await mcp.call_tool("android_click_element", {"text": "New chat"})
    await asyncio.sleep(1)
    
    # Step 3: Search for contact
    print(f"3️⃣ Searching for contact: {contact_name}...")
    # await mcp.call_tool("android_click_element", {"resource_id": "com.whatsapp:id/search"})
    # await mcp.call_tool("android_input_text", {"text": contact_name})
    await asyncio.sleep(1)
    
    # Step 4: Click on contact
    print("4️⃣ Selecting contact...")
    # await mcp.call_tool("android_click_element", {"text": contact_name})
    await asyncio.sleep(1)
    
    # Step 5: Type message
    print(f"5️⃣ Typing message...")
    # await mcp.call_tool("android_click_element", {"resource_id": "com.whatsapp:id/entry"})
    # await mcp.call_tool("android_input_text", {"text": message})
    await asyncio.sleep(0.5)
    
    # Step 6: Send message
    print("6️⃣ Sending message...")
    # await mcp.call_tool("android_click_element", {"resource_id": "com.whatsapp:id/send"})
    
    print("\n✅ Message sent successfully!")

# Example usage
if __name__ == "__main__":
    asyncio.run(send_whatsapp_message(
        contact_name="Friend",
        message="Hello from OpenCngsm! 🤖"
    ))
