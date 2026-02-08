"""
Instagram Automation Example
Demonstrates posting to Instagram using Android MCP Server
"""
import asyncio

async def post_to_instagram(image_path: str, caption: str):
    """
    Automate posting an image to Instagram
    
    Args:
        image_path: Path to image file on device
        caption: Post caption
    """
    
    print(f"📸 Starting Instagram automation...")
    print(f"Image: {image_path}")
    print(f"Caption: {caption}\n")
    
    # Step 1: Start Instagram
    print("1️⃣ Starting Instagram...")
    # await mcp.call_tool("android_start_app", {"package_name": "com.instagram.android"})
    await asyncio.sleep(3)
    
    # Step 2: Click on "+" button to create new post
    print("2️⃣ Opening new post...")
    # await mcp.call_tool("android_click_element", {"description": "New post"})
    await asyncio.sleep(1)
    
    # Step 3: Select "Post"
    print("3️⃣ Selecting Post option...")
    # await mcp.call_tool("android_click_element", {"text": "Post"})
    await asyncio.sleep(1)
    
    # Step 4: Select image from gallery
    print("4️⃣ Selecting image...")
    # Tap on first image (coordinates may vary)
    # await mcp.call_tool("android_tap", {"x": 200, "y": 400})
    await asyncio.sleep(1)
    
    # Step 5: Click "Next"
    print("5️⃣ Proceeding to next step...")
    # await mcp.call_tool("android_click_element", {"text": "Next"})
    await asyncio.sleep(1)
    
    # Step 6: Click "Next" again (filters screen)
    print("6️⃣ Skipping filters...")
    # await mcp.call_tool("android_click_element", {"text": "Next"})
    await asyncio.sleep(1)
    
    # Step 7: Add caption
    print(f"7️⃣ Adding caption...")
    # await mcp.call_tool("android_click_element", {"text": "Write a caption..."})
    # await mcp.call_tool("android_input_text", {"text": caption})
    await asyncio.sleep(1)
    
    # Step 8: Share post
    print("8️⃣ Sharing post...")
    # await mcp.call_tool("android_click_element", {"text": "Share"})
    
    print("\n✅ Post shared successfully!")

# Example usage
if __name__ == "__main__":
    asyncio.run(post_to_instagram(
        image_path="/sdcard/Pictures/photo.jpg",
        caption="Automated post from OpenCngsm! 🤖 #automation"
    ))
