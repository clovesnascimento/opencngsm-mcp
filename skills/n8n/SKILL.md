---
name: n8n
description: >-
  N8N workflow automation integration. Trigger N8N workflows from OpenCngsm,
  receive webhooks from N8N, execute workflows, and manage automation pipelines.
  Bidirectional communication between OpenCngsm and N8N.
homepage: https://n8n.io
metadata:
  opencngsm:
    emoji: "🔄"
    requires:
      env:
        - N8N_API_URL
        - N8N_API_KEY
---

# N8N Integration Skill

Integrate OpenCngsm with N8N workflow automation platform.

## 🎯 Features

- ✅ **Trigger N8N workflows** from OpenCngsm
- ✅ **Receive webhooks** from N8N
- ✅ **Execute workflows** with parameters
- ✅ **Monitor workflow status**
- ✅ **Bidirectional communication**
- ✅ **Workflow management** (list, activate, deactivate)

## 📋 Setup

### **1. N8N Installation**

**Option A: Docker (Recommended)**
```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Option B: npm**
```bash
npm install -g n8n
n8n start
```

### **2. Get API Key**

1. Open N8N: `http://localhost:5678`
2. Go to **Settings** → **API**
3. Create new API key
4. Copy the key

### **3. Configure OpenCngsm**

```bash
# Set environment variables
export N8N_API_URL="http://localhost:5678/api/v1"
export N8N_API_KEY="your-api-key-here"
```

Or add to `~/.opencngsm/config.json`:
```json
{
  "skills": {
    "n8n": {
      "api_url": "http://localhost:5678/api/v1",
      "api_key": "your-api-key-here",
      "webhook_url": "http://localhost:18789/webhooks/n8n"
    }
  }
}
```

## 🚀 Usage

### **1. Trigger N8N Workflow**

```python
from skills.n8n.n8n_skill import N8NSkill

n8n = N8NSkill()

# Execute workflow by ID
result = await n8n.execute_workflow(
    workflow_id='123',
    data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'action': 'send_welcome_email'
    }
)

print(f"Execution ID: {result['id']}")
print(f"Status: {result['status']}")
```

### **2. Trigger by Webhook**

```python
# Trigger workflow via webhook
result = await n8n.trigger_webhook(
    webhook_path='opencngsm-trigger',
    data={
        'message': 'Hello from OpenCngsm!',
        'timestamp': datetime.now().isoformat()
    }
)
```

### **3. List Workflows**

```python
# Get all workflows
workflows = await n8n.list_workflows()

for workflow in workflows:
    print(f"{workflow['id']}: {workflow['name']} - {'Active' if workflow['active'] else 'Inactive'}")
```

### **4. Monitor Execution**

```python
# Get execution status
execution = await n8n.get_execution(execution_id='456')

print(f"Status: {execution['status']}")
print(f"Started: {execution['startedAt']}")
print(f"Finished: {execution['finishedAt']}")
print(f"Data: {execution['data']}")
```

### **5. Activate/Deactivate Workflow**

```python
# Activate workflow
await n8n.activate_workflow(workflow_id='123')

# Deactivate workflow
await n8n.deactivate_workflow(workflow_id='123')
```

## 🔗 N8N → OpenCngsm (Webhooks)

### **Setup Webhook in N8N:**

1. Create new workflow in N8N
2. Add **Webhook** node
3. Set webhook URL: `http://localhost:18789/webhooks/n8n`
4. Set HTTP Method: `POST`
5. Add your workflow logic
6. Activate workflow

### **Receive in OpenCngsm:**

```python
# OpenCngsm automatically receives N8N webhooks
# Access via webhook handler

from core.webhooks import webhook_handler

@webhook_handler.register('/n8n')
async def handle_n8n_webhook(payload):
    """Handle incoming N8N webhook"""
    print(f"Received from N8N: {payload}")
    
    # Process data
    if payload.get('event') == 'workflow_completed':
        await telegram.send_message(f"N8N workflow completed: {payload['workflow_name']}")
    
    return {'status': 'success'}
```

## 📊 Use Cases

### **1. Email Automation**

**N8N Workflow:**
- Trigger: OpenCngsm webhook
- Action: Send email via Gmail
- Response: Send confirmation to Telegram

**OpenCngsm:**
```python
# Trigger email workflow
await n8n.execute_workflow(
    workflow_id='email-automation',
    data={
        'to': 'client@example.com',
        'subject': 'Monthly Report',
        'body': 'Please find attached...',
        'attachments': ['report.pdf']
    }
)
```

### **2. Data Processing Pipeline**

**N8N Workflow:**
- Trigger: Webhook from OpenCngsm
- Steps:
  1. Fetch data from API
  2. Transform data
  3. Store in database
  4. Send notification

**OpenCngsm:**
```python
# Trigger data pipeline
await n8n.trigger_webhook(
    webhook_path='data-pipeline',
    data={
        'source': 'api.example.com',
        'filters': {'date': '2024-01-01'},
        'notify': True
    }
)
```

### **3. Multi-Channel Notifications**

**N8N Workflow:**
- Trigger: OpenCngsm
- Actions:
  - Send Slack message
  - Send Discord message
  - Send email
  - Update Google Sheets

**OpenCngsm:**
```python
# Broadcast notification
await n8n.execute_workflow(
    workflow_id='broadcast-notification',
    data={
        'message': 'System maintenance scheduled',
        'channels': ['slack', 'discord', 'email'],
        'priority': 'high'
    }
)
```

### **4. Scheduled Tasks via N8N**

**N8N Workflow:**
- Trigger: Cron (daily at 9 AM)
- Actions:
  1. Generate report
  2. Send to OpenCngsm webhook
  3. OpenCngsm sends via Telegram

**N8N Setup:**
1. Add **Cron** node: `0 9 * * *`
2. Add **HTTP Request** to OpenCngsm webhook
3. Activate workflow

**OpenCngsm receives:**
```python
@webhook_handler.register('/daily-report')
async def handle_daily_report(payload):
    report = payload['report']
    await telegram.send_message(f"📊 Daily Report:\n{report}")
```

## 🔐 Security

### **API Key Protection**
- Store API key in environment variables
- Never commit to version control
- Use `.env` file or config manager

### **Webhook Signature Verification**
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    """Verify N8N webhook signature"""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)
```

### **IP Whitelisting**
```json
{
  "webhooks": {
    "n8n": {
      "allowed_ips": ["127.0.0.1", "192.168.1.0/24"]
    }
  }
}
```

## 🌐 N8N Cloud

For N8N Cloud (cloud.n8n.io):

```bash
export N8N_API_URL="https://your-instance.app.n8n.cloud/api/v1"
export N8N_API_KEY="your-cloud-api-key"
```

**Webhook URL:** Use public URL (ngrok, cloudflare tunnel, etc.)

## 📚 Examples

### **Example 1: Send Telegram Message via N8N**

```python
# OpenCngsm triggers N8N workflow
await n8n.execute_workflow(
    workflow_id='telegram-sender',
    data={
        'chat_id': '123456789',
        'message': 'Hello from N8N!'
    }
)
```

### **Example 2: Process Form Submission**

```python
# N8N receives form submission
# N8N sends webhook to OpenCngsm
# OpenCngsm processes and responds

@webhook_handler.register('/form-submission')
async def handle_form(payload):
    name = payload['name']
    email = payload['email']
    
    # Save to database
    await storage.save(f'forms/{email}.json', payload)
    
    # Send confirmation email via N8N
    await n8n.execute_workflow(
        workflow_id='send-confirmation',
        data={'email': email, 'name': name}
    )
    
    return {'status': 'processed'}
```

### **Example 3: Monitor Website**

**N8N Workflow:**
- Cron: Every 5 minutes
- HTTP Request: Check website
- Condition: If down
- Webhook: Alert OpenCngsm

**OpenCngsm:**
```python
@webhook_handler.register('/website-alert')
async def handle_alert(payload):
    website = payload['website']
    status = payload['status']
    
    await telegram.send_message(
        f"🚨 ALERT: {website} is {status}!"
    )
```

## 🔄 Bidirectional Flow

```
OpenCngsm ──────► N8N
    │              │
    │              ├─► External APIs
    │              ├─► Databases
    │              ├─► Email/SMS
    │              └─► Other services
    │
    ◄──────────────┘
  (Webhooks)
```

## 🎯 Benefits

| Benefit | Description |
|---------|-------------|
| **No-Code Automation** | Use N8N's visual editor |
| **400+ Integrations** | Connect to any service |
| **Complex Workflows** | Multi-step automation |
| **Scheduled Tasks** | Cron-based execution |
| **Error Handling** | Built-in retry logic |
| **Self-Hosted** | Full control over data |

## 🐛 Troubleshooting

### **Connection Error**
```
Error: Cannot connect to N8N API
```
**Solution:** Check `N8N_API_URL` and ensure N8N is running

### **Authentication Failed**
```
Error: 401 Unauthorized
```
**Solution:** Verify `N8N_API_KEY` is correct

### **Webhook Not Received**
**Solution:** 
- Check webhook URL is accessible
- Verify firewall settings
- Test with curl:
  ```bash
  curl -X POST http://localhost:18789/webhooks/n8n \
    -H "Content-Type: application/json" \
    -d '{"test": "data"}'
  ```

## 📖 References

- [N8N Documentation](https://docs.n8n.io)
- [N8N API Reference](https://docs.n8n.io/api/)
- [N8N Workflows](https://n8n.io/workflows)
- [N8N Community](https://community.n8n.io)

---

**OpenCngsm + N8N = Automation Superpowers! 🚀**
