# 🐳 Docker Sandbox - OpenCngsm v3.0

## 📖 Overview

Docker Sandbox provides **container-based isolation** for skill execution, ensuring security and resource management.

---

## 🎯 Features

- ✅ **Container Isolation** - Each skill runs in isolated container
- ✅ **Resource Limits** - CPU and memory constraints
- ✅ **Network Isolation** - Control network access per skill
- ✅ **Filesystem Mounts** - Read-only/read-write volume mounts
- ✅ **Automatic Cleanup** - Containers removed after execution
- ✅ **Non-root Execution** - Skills run as non-root user

---

## 🚀 Quick Start

### 1. Install Docker

**Windows/macOS:**
- Download Docker Desktop: https://www.docker.com/products/docker-desktop

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 2. Verify Installation

```bash
docker --version
docker ps
```

### 3. Run Skill in Sandbox

```python
from core.sandbox.docker_runner import SkillSandbox

sandbox = SkillSandbox(enable_sandbox=True)

result = await sandbox.execute_skill(
    skill_name='telegram',
    action='send_message',
    args={'text': 'Hello!', 'chat_id': '123'},
    sandbox_config={
        'cpu_limit': 0.5,        # 50% of 1 CPU core
        'memory_limit': '256m',  # 256 MB RAM
        'network_mode': 'bridge' # Network access
    }
)

print(f"Status: {result['status']}")
print(f"Output: {result['output']}")
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         OpenCngsm Core                  │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │      SkillSandbox                  │ │
│  │  - Enable/disable sandboxing       │ │
│  │  - Execution wrapper               │ │
│  └──────────────┬─────────────────────┘ │
│                 ↓                        │
│  ┌────────────────────────────────────┐ │
│  │      DockerRunner                  │ │
│  │  - Container lifecycle             │ │
│  │  - Resource limits                 │ │
│  │  - Image management                │ │
│  └──────────────┬─────────────────────┘ │
└─────────────────┼──────────────────────┘
                  ↓
        ┌─────────────────────┐
        │   Docker Engine     │
        │                     │
        │  ┌───────────────┐  │
        │  │  Container 1  │  │ ← Telegram Skill
        │  └───────────────┘  │
        │  ┌───────────────┐  │
        │  │  Container 2  │  │ ← Voice Skill
        │  └───────────────┘  │
        └─────────────────────┘
```

---

## 📦 Configuration

### Resource Limits

```python
sandbox_config = {
    'cpu_limit': 1.0,        # 1.0 = 1 CPU core, 0.5 = 50% of 1 core
    'memory_limit': '512m',  # '256m', '512m', '1g', etc.
    'timeout': 300           # Execution timeout (seconds)
}
```

### Network Modes

- **`bridge`** (default) - Container has network access
- **`none`** - No network access (isolated)
- **`host`** - Use host network (not recommended)

### Filesystem Mounts

```python
mounts = [
    '/host/data:/app/data:ro',      # Read-only
    '/host/output:/app/output:rw',  # Read-write
]
```

---

## 🔐 Security

### Non-root User

All containers run as `skilluser` (UID 1000), not root.

### Resource Limits

Prevents resource exhaustion:
- CPU quota enforcement
- Memory limits with OOM killer
- Execution timeout

### Network Isolation

Skills can be run without network access:
```python
sandbox_config={'network_mode': 'none'}
```

### Filesystem Isolation

Only explicitly mounted directories are accessible.

---

## 🛠️ Usage Examples

### Example 1: Send Telegram Message (Sandboxed)

```python
from core.sandbox.docker_runner import SkillSandbox

sandbox = SkillSandbox(enable_sandbox=True)

result = await sandbox.execute_skill(
    skill_name='telegram',
    action='send_message',
    args={
        'text': 'Hello from sandbox!',
        'chat_id': '123456789'
    },
    sandbox_config={
        'cpu_limit': 0.5,
        'memory_limit': '256m',
        'network_mode': 'bridge',
        'env_vars': {
            'TELEGRAM_BOT_TOKEN': 'your_token'
        }
    }
)

if result['status'] == 0:
    print("✅ Message sent successfully")
else:
    print(f"❌ Error: {result['error']}")
```

### Example 2: Transcribe Audio (Isolated)

```python
result = await sandbox.execute_skill(
    skill_name='voice',
    action='transcribe_audio',
    args={'audio_path': '/app/data/audio.mp3'},
    sandbox_config={
        'cpu_limit': 1.0,
        'memory_limit': '1g',
        'mounts': [
            '/host/audio:/app/data:ro'  # Read-only audio files
        ],
        'env_vars': {
            'MISTRAL_API_KEY': 'your_key'
        }
    }
)

transcription = result['output']
```

### Example 3: Web Scraping (No Network After Download)

```python
# First, download page
result1 = await sandbox.execute_skill(
    skill_name='webscraping',
    action='download_page',
    args={'url': 'https://example.com'},
    sandbox_config={
        'network_mode': 'bridge',  # Network access
        'mounts': ['/host/cache:/app/cache:rw']
    }
)

# Then, parse offline (no network)
result2 = await sandbox.execute_skill(
    skill_name='webscraping',
    action='parse_html',
    args={'html_path': '/app/cache/page.html'},
    sandbox_config={
        'network_mode': 'none',  # No network
        'mounts': ['/host/cache:/app/cache:ro']
    }
)
```

---

## 🧪 Testing

### Test Docker Setup

```python
from core.sandbox.docker_runner import DockerRunner

runner = DockerRunner()
print("✅ Docker is working!")

# List images
images = runner.list_images()
print(f"Images: {images}")
```

### Test Skill Execution

```bash
python -c "
from core.sandbox.docker_runner import SkillSandbox
import asyncio

async def test():
    sandbox = SkillSandbox(enable_sandbox=True)
    result = await sandbox.execute_skill(
        skill_name='storage',
        action='list_files',
        args={'directory': '.'},
        sandbox_config={'cpu_limit': 0.5, 'memory_limit': '128m'}
    )
    print(result)

asyncio.run(test())
"
```

---

## 🐛 Troubleshooting

### "Docker not available"
- Install Docker Desktop (Windows/macOS)
- Start Docker daemon (Linux): `sudo systemctl start docker`
- Verify: `docker ps`

### "Image build failed"
- Check Dockerfile in skill directory
- Verify requirements.txt exists
- Check Docker disk space: `docker system df`

### "Container timeout"
- Increase timeout in sandbox_config
- Check skill execution time
- Verify network connectivity (if needed)

### "Permission denied"
- Ensure Docker daemon is running
- Add user to docker group (Linux): `sudo usermod -aG docker $USER`

---

## 📊 Performance

| Overhead | Time |
|----------|------|
| Container startup | ~1-2s |
| Image build (first time) | ~30-60s |
| Image build (cached) | ~5-10s |
| Execution overhead | ~100-200ms |

**Recommendation:** Pre-build images for production.

---

## 🔧 Advanced Configuration

### Custom Dockerfile

Create `skills/myskill/Dockerfile`:

```dockerfile
FROM python:3.11-slim

RUN useradd -m skilluser

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

USER skilluser

CMD ["python", "-m", "skills.myskill"]
```

### Pre-build Images

```bash
# Build all skill images
python -c "
from core.sandbox.docker_runner import DockerRunner
runner = DockerRunner()
for skill in ['telegram', 'voice', 'email']:
    runner._ensure_image(skill, f'opencngsm-skill-{skill}')
"
```

---

## 🎯 Best Practices

1. ✅ **Use resource limits** - Prevent resource exhaustion
2. ✅ **Minimize network access** - Use `network_mode='none'` when possible
3. ✅ **Read-only mounts** - Use `:ro` for input data
4. ✅ **Pre-build images** - Faster execution in production
5. ✅ **Monitor resources** - Check Docker stats: `docker stats`

---

## 📚 References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Python SDK](https://docker-py.readthedocs.io/)
- [Container Security Best Practices](https://docs.docker.com/engine/security/)
