"""
OpenCngsm v3.0 - WhatsApp Skill
Python wrapper for Baileys (WhatsApp Web API)
"""
import aiohttp
import asyncio
import subprocess
import os
import json
from typing import Callable, Optional
from pathlib import Path

import logging

logger = logging.getLogger(__name__)


class WhatsAppSkill:
    """
    WhatsApp integration using Baileys library
    
    Features:
    - Send/receive messages
    - Media support (photos, videos, voice)
    - Typing indicators
    - QR code pairing
    - Multi-device support
    """
    
    def __init__(self, baileys_port: int = 3000):
        """
        Initialize WhatsApp skill
        
        Args:
            baileys_port: Port for Baileys Node.js server
        """
        self.baileys_port = baileys_port
        self.baileys_url = f'http://localhost:{baileys_port}'
        self.baileys_process = None
        self.message_handler = None
    
    async def start(self):
        """Start Baileys Node.js server"""
        baileys_dir = Path(__file__).parent / 'baileys'
        
        if not (baileys_dir / 'index.js').exists():
            raise FileNotFoundError(
                f"Baileys server not found at {baileys_dir}/index.js\n"
                "Run: cd skills/whatsapp/baileys && npm install"
            )
        
        logger.info("🚀 Starting Baileys server...")
        
        self.baileys_process = subprocess.Popen(
            ['node', 'index.js'],
            cwd=str(baileys_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        await asyncio.sleep(3)
        
        # Check if server is running
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.baileys_url}/status') as resp:
                    if resp.status == 200:
                        logger.info("✅ Baileys server started")
                    else:
                        raise Exception("Baileys server failed to start")
        except Exception as e:
            logger.error(f"❌ Baileys server error: {e}")
            raise
    
    async def get_qr_code(self) -> Optional[str]:
        """
        Get QR code for pairing
        
        Returns:
            QR code string or None if already paired
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.baileys_url}/qr') as resp:
                data = await resp.json()
                return data.get('qr')
    
    async def send_message(self, to: str, message: str):
        """
        Send WhatsApp message
        
        Args:
            to: Phone number in JID format (e.g., '5511999999999@s.whatsapp.net')
            message: Text message
        
        Example:
            await whatsapp.send_message(
                to='5511999999999@s.whatsapp.net',
                message='Hello from OpenCngsm!'
            )
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.baileys_url}/send',
                json={'to': to, 'message': message}
            ) as resp:
                result = await resp.json()
                
                if result.get('success'):
                    logger.info(f"✅ Message sent to {to}")
                else:
                    logger.error(f"❌ Failed to send message: {result.get('error')}")
                
                return result
    
    async def send_typing(self, to: str):
        """Send typing indicator"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.baileys_url}/typing',
                json={'to': to}
            ) as resp:
                return await resp.json()
    
    async def send_image(self, to: str, image_path: str, caption: str = None):
        """
        Send image
        
        Args:
            to: Phone number in JID format
            image_path: Path to image file
            caption: Optional caption
        """
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('to', to)
            data.add_field('image', image_data, filename=os.path.basename(image_path))
            if caption:
                data.add_field('caption', caption)
            
            async with session.post(f'{self.baileys_url}/send-image', data=data) as resp:
                result = await resp.json()
                logger.info(f"✅ Image sent to {to}")
                return result
    
    async def send_video(self, to: str, video_path: str, caption: str = None):
        """Send video"""
        with open(video_path, 'rb') as f:
            video_data = f.read()
        
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('to', to)
            data.add_field('video', video_data, filename=os.path.basename(video_path))
            if caption:
                data.add_field('caption', caption)
            
            async with session.post(f'{self.baileys_url}/send-video', data=data) as resp:
                result = await resp.json()
                logger.info(f"✅ Video sent to {to}")
                return result
    
    async def send_voice(self, to: str, audio_path: str):
        """Send voice message"""
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('to', to)
            data.add_field('audio', audio_data, filename=os.path.basename(audio_path))
            
            async with session.post(f'{self.baileys_url}/send-voice', data=data) as resp:
                result = await resp.json()
                logger.info(f"✅ Voice message sent to {to}")
                return result
    
    def on_message(self, handler: Callable):
        """
        Set message handler callback
        
        Args:
            handler: Async function to handle incoming messages
        
        Example:
            async def handle_message(message):
                from_number = message['key']['remoteJid']
                text = message['message']['conversation']
                await whatsapp.send_message(from_number, f"You said: {text}")
            
            whatsapp.on_message(handle_message)
        """
        self.message_handler = handler
    
    async def stop(self):
        """Stop Baileys server"""
        if self.baileys_process:
            logger.info("🛑 Stopping Baileys server...")
            self.baileys_process.terminate()
            self.baileys_process.wait()
            logger.info("✅ Baileys server stopped")
    
    @staticmethod
    def format_phone_number(phone: str) -> str:
        """
        Format phone number to WhatsApp JID
        
        Args:
            phone: Phone number (e.g., '+5511999999999' or '5511999999999')
        
        Returns:
            JID format (e.g., '5511999999999@s.whatsapp.net')
        """
        # Remove + and spaces
        phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        return f'{phone}@s.whatsapp.net'


# Example usage
if __name__ == "__main__":
    async def main():
        whatsapp = WhatsAppSkill()
        
        # Start server
        await whatsapp.start()
        
        # Get QR code (first time)
        qr = await whatsapp.get_qr_code()
        if qr:
            print("Scan this QR code with WhatsApp:")
            print(qr)
            await asyncio.sleep(30)  # Wait for pairing
        
        # Send message
        await whatsapp.send_message(
            to=WhatsAppSkill.format_phone_number('+5511999999999'),
            message='Hello from OpenCngsm!'
        )
        
        # Stop server
        await whatsapp.stop()
    
    asyncio.run(main())
