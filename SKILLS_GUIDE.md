# 🎯 OpenCngsm v3.0 - Skills Guide

## 📦 Available Skills

OpenCngsm v3.0 includes **6 native Python skills** that replace the need for JavaScript MCPs:

1. **Telegram** - Send/receive messages via Telegram bot
2. **Email** - Send/receive emails via SMTP/IMAP
3. **PIX** - Generate Brazilian payment QR codes
4. **WebScraping** - Extract content from web pages
5. **GoogleDrive** - Upload/download files to Google Drive
6. **Storage** - Persistent key-value storage with TTL

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from skills.telegram_skill import TelegramSkill
from skills.pix_skill import PIXSkill
from skills.storage_skill import StorageSkill

# Telegram
telegram = TelegramSkill(bot_token='YOUR_TOKEN', chat_id='YOUR_CHAT_ID')
await telegram.send_message('Hello! 🚀')

# PIX
pix = PIXSkill(nome='Minha Loja', cidade='Fortaleza')
qr_buffer = pix.generate_qr_code(
    chave='seuemail@gmail.com',
    valor=49.90,
    output_path='qrcode.png'
)

# Storage
storage = StorageSkill()
await storage.set('user:123', {'name': 'João', 'age': 25})
user = await storage.get('user:123')
```

---

## 📚 Skills Documentation

### 1. Telegram Skill

**Setup:**
1. Create bot via [@BotFather](https://t.me/BotFather)
2. Get bot token
3. Get your chat ID from [@userinfobot](https://t.me/userinfobot)

**Features:**
- Send messages (Markdown/HTML)
- Receive messages with callback
- Send photos
- Typing action
- Bot polling

**Example:**
```python
from skills.telegram_skill import TelegramSkill

telegram = TelegramSkill(
    bot_token='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
    chat_id='123456789'
)

# Send message
await telegram.send_message('Hello from OpenCngsm! 🤖')

# Send photo
await telegram.send_photo('screenshot.png', caption='Check this out!')

# Receive messages
async def handle_message(text, update):
    print(f"Received: {text}")
    await telegram.send_message(f"You said: {text}")

await telegram.start_bot(handle_message)
```

---

### 2. Email Skill

**Setup (Gmail):**
1. Enable 2FA in Google Account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use app password instead of regular password

**Features:**
- Send emails (plain text/HTML)
- Attachments support
- Template emails
- Receive unread emails via IMAP
- CC/BCC support

**Example:**
```python
from skills.email_skill import EmailSkill

email = EmailSkill(
    email_address='your@gmail.com',
    password='your_app_password'
)

# Send HTML email
await email.send_email(
    to='client@example.com',
    subject='Order Confirmed',
    body='<h1>Thank you!</h1><p>Your order has been confirmed.</p>',
    html=True
)

# Send with attachment
await email.send_email(
    to='client@example.com',
    subject='Invoice',
    body='Please find attached invoice.',
    attachments=['invoice.pdf']
)

# Get unread emails
unread = await email.get_unread_emails(limit=10)
for msg in unread:
    print(f"{msg['from']}: {msg['subject']}")
```

---

### 3. PIX Skill

**Features:**
- Generate static PIX QR codes
- BR Code payload generation
- CRC16 validation
- Support for all PIX key types

**Example:**
```python
from skills.pix_skill import PIXSkill

pix = PIXSkill(nome='Minha Loja', cidade='Fortaleza')

# Generate QR code
qr_buffer = pix.generate_qr_code(
    chave='seuemail@gmail.com',  # or CPF, CNPJ, phone, random key
    valor=49.90,
    descricao='Pagamento pedido #1234',
    output_path='qrcode.png'
)

# Generate only payload (for copy-paste)
payload = pix.generate_static_payload(
    chave='seuemail@gmail.com',
    valor=49.90
)
print(f"PIX Copia e Cola: {payload}")
```

---

### 4. Web Scraping Skill

**Features:**
- Extract text, HTML, metadata
- Parse tables
- Extract links and images
- Open Graph and Twitter Cards support
- Retry logic

**Example:**
```python
from skills.webscraping_skill import WebScrapingSkill

scraper = WebScrapingSkill(timeout=15)

# Full scrape
data = await scraper.scrape('https://example.com')
print(data['metadata']['title'])
print(data['text'][:200])

# Get only text
text = await scraper.get_text('https://example.com')

# Get tables
tables = await scraper.get_tables('https://example.com')
for table in tables:
    print(f"Table with {table['row_count']} rows")
    print(table['headers'])
```

---

### 5. Google Drive Skill

**Setup:**
1. Go to https://console.cloud.google.com/
2. Create project and enable Google Drive API
3. Create OAuth 2.0 credentials
4. Download `credentials.json`

**Features:**
- Upload/download files
- Create folders
- List files
- Share files
- Delete files

**Example:**
```python
from skills.googledrive_skill import GoogleDriveSkill

drive = GoogleDriveSkill(
    credentials_path='credentials.json',
    token_path='token.json'
)

# Authenticate (opens browser first time)
await drive.authenticate()

# Upload file
file = await drive.upload_file('document.pdf')
print(f"Uploaded: {file['webViewLink']}")

# Create folder and upload
folder = await drive.create_folder('Backups')
await drive.upload_file('backup.zip', folder_id=folder['id'])

# Share file
link = await drive.share_file(file['id'], role='reader')
print(f"Share link: {link}")

# List files
files = await drive.list_files(page_size=20)
for f in files:
    print(f"- {f['name']}")
```

---

### 6. Storage Skill

**Features:**
- Key-value storage using Python shelve
- TTL (Time To Live) support
- Namespaces for isolation
- Export/import functionality
- Increment counters

**Example:**
```python
from skills.storage_skill import StorageSkill

storage = StorageSkill(
    db_path='data/storage.db',
    namespace='myapp'
)

# Store data
await storage.set('user:123', {'name': 'João', 'age': 25})

# Store with TTL (expires in 1 hour)
await storage.set('session:abc', 'active', ttl=3600)

# Get data
user = await storage.get('user:123')
print(user)  # {'name': 'João', 'age': 25}

# Check existence
if await storage.exists('session:abc'):
    print("Session is active")

# Increment counter
await storage.set('page_views', 0)
await storage.increment('page_views')
count = await storage.get('page_views')  # 1

# List keys
keys = await storage.keys()
print(keys)  # ['user:123', 'session:abc', 'page_views']

# Export/Import
data = await storage.export()
await storage.import_data(data, overwrite=True)
```

---

## 🔧 Advanced Usage

### Skill Registry

All skills auto-register on import:

```python
from skills import list_skills, get_skill

# List all available skills
skills = list_skills()
for name, description in skills.items():
    print(f"{name}: {description}")

# Get skill class dynamically
TelegramSkill = get_skill('telegram')
telegram = TelegramSkill(bot_token='...', chat_id='...')
```

### Error Handling

All skills use Python logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Skills will log errors and info
telegram = TelegramSkill(...)
await telegram.send_message('Test')  # Logs: ✅ Message sent to 123456789
```

---

## 📖 Full Examples

See `examples/skills_usage.py` for complete working examples of all skills.

```bash
# Run examples
python examples/skills_usage.py
```

---

## 🚀 Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure credentials**: Set up API keys/tokens for skills you want to use
3. **Run examples**: `python examples/skills_usage.py`
4. **Integrate with OpenCngsm**: Use skills in your session handlers

---

**Skills are 100% Python native - no Node.js required!** 🐍
