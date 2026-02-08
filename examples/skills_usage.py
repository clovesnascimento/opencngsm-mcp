"""
OpenCngsm v3.0 - Skills Usage Examples
Demonstrates how to use all 6 native Python skills
"""
import asyncio
import os
from skills.telegram_skill import TelegramSkill
from skills.email_skill import EmailSkill
from skills.pix_skill import PIXSkill
from skills.webscraping_skill import WebScrapingSkill
from skills.googledrive_skill import GoogleDriveSkill
from skills.storage_skill import StorageSkill


async def telegram_example():
    """Example: Send and receive Telegram messages"""
    print("\n=== Telegram Skill Example ===")
    
    telegram = TelegramSkill(
        bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        chat_id=os.getenv('TELEGRAM_CHAT_ID')
    )
    
    # Send message
    await telegram.send_message('Hello from OpenCngsm v3.0! 🚀')
    
    # Send typing action
    await telegram.send_typing_action()
    
    # Get bot info
    bot_info = await telegram.get_bot_info()
    print(f"Bot: @{bot_info.get('username')}")
    
    # Start bot to receive messages
    async def handle_message(text: str, update):
        print(f"Received: {text}")
        await telegram.send_message(f"You said: {text}")
    
    # await telegram.start_bot(handle_message)
    # Keep running to receive messages...


async def email_example():
    """Example: Send and receive emails"""
    print("\n=== Email Skill Example ===")
    
    email = EmailSkill(
        email_address='your@gmail.com',
        password='your_app_password'  # Use Gmail App Password
    )
    
    # Send simple email
    await email.send_email(
        to='recipient@example.com',
        subject='Test from OpenCngsm',
        body='This is a test email from OpenCngsm v3.0!'
    )
    
    # Send HTML email
    await email.send_email(
        to='recipient@example.com',
        subject='Welcome!',
        body='<h1>Welcome to OpenCngsm!</h1><p>Enjoy your experience.</p>',
        html=True
    )
    
    # Send template email
    await email.send_template_email(
        to='user@example.com',
        template='welcome',
        variables={'name': 'João', 'email': 'user@example.com'}
    )
    
    # Get unread emails
    unread = await email.get_unread_emails(limit=5)
    for msg in unread:
        print(f"From: {msg['from']}")
        print(f"Subject: {msg['subject']}")


async def pix_example():
    """Example: Generate PIX QR codes"""
    print("\n=== PIX Skill Example ===")
    
    pix = PIXSkill(
        nome='Minha Loja',
        cidade='Fortaleza'
    )
    
    # Generate payload
    payload = pix.generate_static_payload(
        chave='seuemail@gmail.com',
        valor=49.90,
        descricao='Pagamento pedido #1234'
    )
    print(f"PIX Payload: {payload[:50]}...")
    
    # Generate QR code image
    qr_buffer = pix.generate_qr_code(
        chave='seuemail@gmail.com',
        valor=49.90,
        descricao='Pagamento pedido #1234',
        output_path='pix_qrcode.png'
    )
    print("QR code saved to pix_qrcode.png")
    
    # Validate payload
    is_valid = pix.validate_payload(payload)
    print(f"Payload valid: {is_valid}")


async def webscraping_example():
    """Example: Scrape web pages"""
    print("\n=== Web Scraping Skill Example ===")
    
    scraper = WebScrapingSkill(timeout=15)
    
    # Scrape full page
    data = await scraper.scrape('https://example.com')
    if data:
        print(f"Title: {data['metadata']['title']}")
        print(f"Text preview: {data['text'][:200]}...")
        print(f"Tables found: {len(data.get('tables', []))}")
    
    # Get only text
    text = await scraper.get_text('https://example.com')
    if text:
        print(f"Clean text: {text[:100]}...")
    
    # Get only metadata
    metadata = await scraper.get_metadata('https://example.com')
    if metadata:
        print(f"Description: {metadata.get('description')}")
        print(f"OG Image: {metadata.get('og', {}).get('image')}")


async def googledrive_example():
    """Example: Google Drive operations"""
    print("\n=== Google Drive Skill Example ===")
    
    drive = GoogleDriveSkill(
        credentials_path='credentials.json',
        token_path='token.json'
    )
    
    # Authenticate
    await drive.authenticate()
    
    # List files
    files = await drive.list_files(page_size=10)
    for file in files:
        print(f"- {file['name']} ({file.get('size', 'N/A')} bytes)")
    
    # Create folder
    folder = await drive.create_folder('OpenCngsm Backups')
    if folder:
        print(f"Created folder: {folder['name']}")
        
        # Upload file to folder
        uploaded = await drive.upload_file(
            file_path='example.txt',
            folder_id=folder['id']
        )
        if uploaded:
            print(f"Uploaded: {uploaded['webViewLink']}")
            
            # Share file
            link = await drive.share_file(
                file_id=uploaded['id'],
                role='reader'
            )
            print(f"Share link: {link}")


async def storage_example():
    """Example: Persistent storage"""
    print("\n=== Storage Skill Example ===")
    
    storage = StorageSkill(
        db_path='data/storage.db',
        namespace='opencngsm'
    )
    
    # Store simple value
    await storage.set('user:123', {'name': 'João', 'age': 25})
    
    # Store with TTL (expires in 1 hour)
    await storage.set('session:abc', 'active', ttl=3600)
    
    # Get values
    user = await storage.get('user:123')
    print(f"User: {user}")
    
    session = await storage.get('session:abc')
    print(f"Session: {session}")
    
    # Check existence
    exists = await storage.exists('user:123')
    print(f"User exists: {exists}")
    
    # List all keys
    keys = await storage.keys()
    print(f"All keys: {keys}")
    
    # Increment counter
    await storage.set('page_views', 0)
    new_count = await storage.increment('page_views')
    print(f"Page views: {new_count}")
    
    # Export data
    data = await storage.export()
    print(f"Exported {len(data)} keys")
    
    # Import data
    imported = await storage.import_data({
        'config:theme': 'dark',
        'config:language': 'pt-BR'
    })
    print(f"Imported {imported} keys")


async def main():
    """Run all examples"""
    print("🚀 OpenCngsm v3.0 - Skills Examples\n")
    
    # Uncomment the examples you want to run
    
    # await telegram_example()
    # await email_example()
    await pix_example()
    await webscraping_example()
    # await googledrive_example()
    await storage_example()
    
    print("\n✅ Examples completed!")


if __name__ == '__main__':
    asyncio.run(main())
