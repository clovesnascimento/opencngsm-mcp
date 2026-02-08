# 🔄 Clawdbot Skill Converter

## 📖 Overview

Automatic converter for Clawdbot skills to OpenCngsm format. Detects Clawdbot skills, converts paths/config, and generates Python wrappers for bash/curl commands.

---

## 🎯 Features

- ✅ **Auto-detection** - Identifies Clawdbot skills by metadata
- ✅ **Path conversion** - `~/.clawdbot` → `~/.opencngsm`
- ✅ **Metadata update** - `clawdbot` → `opencngsm`
- ✅ **Python generation** - Converts bash/curl to Python
- ✅ **Batch import** - Convert multiple skills at once
- ✅ **CLI interface** - Easy command-line usage

---

## 🚀 Quick Start

### **1. Import Single Skill**

```bash
python -m core.converters.skill_importer import-skill C:/Users/cngsm/Desktop/XXX/AG/hack
```

**Output:**
```
🔄 Converting Clawdbot skill: hack
📝 Converted SKILL.md
🐍 Generated Python wrapper: hack_skill.py
✅ Skill imported successfully!
📁 Location: skills/hack
```

### **2. Import All Skills from Directory**

```bash
python -m core.converters.skill_importer import-batch C:/Users/cngsm/Desktop/XXX/AG
```

**Output:**
```
🔄 Converting Clawdbot skill: hack
✅ Converted skill saved to: skills/hack
🔄 Converting Clawdbot skill: telegram-bot-1.0.0
✅ Converted skill saved to: skills/telegram-bot-1.0.0

✅ Batch import complete!
📊 Converted 2 skills:
  - hack
  - telegram-bot-1.0.0
```

### **3. Check if Skill is Clawdbot**

```bash
python -m core.converters.skill_importer check C:/Users/cngsm/Desktop/XXX/AG/hack
```

**Output:**
```
✅ Clawdbot skill detected: hack

📋 Metadata:
  Name: dont-hack-me
  Description: Security self-check for Clawdbot/Moltbot...
  Emoji: 🔒
  Dependencies:
    Binaries: jq, curl, openssl
```

---

## 📋 What Gets Converted

### **1. SKILL.md**

**Before (Clawdbot):**
```yaml
---
name: dont-hack-me
metadata:
  clawdbot:
    emoji: "🔒"
---

# Security Check

Read `~/.clawdbot/clawdbot.json`...
Run `clawdbot gateway restart`...
```

**After (OpenCngsm):**
```yaml
---
name: dont-hack-me
metadata:
  opencngsm:
    emoji: "🔒"
---

# Security Check

Read `~/.opencngsm/config.json`...
Run `opencngsm gateway restart`...
```

### **2. Path Mappings**

| Clawdbot | OpenCngsm |
|----------|-----------|
| `~/.clawdbot/clawdbot.json` | `~/.opencngsm/config.json` |
| `~/.clawdbot/` | `~/.opencngsm/` |
| `clawdbot.json` | `config.json` |
| `clawdbot gateway` | `opencngsm gateway` |
| `Clawdbot` | `OpenCngsm` |

### **3. Python Wrapper Generation**

**Original (bash/curl):**
```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe" | jq
```

**Generated (Python):**
```python
class TelegramBotSkill:
    async def api_call_1(self, **kwargs) -> Dict:
        """API call (auto-generated)"""
        url = "https://api.telegram.org/bot{token}/getMe"
        
        for key, value in kwargs.items():
            url = url.replace(f'{{{key}}}', str(value))
        
        response = requests.get(url)
        response.raise_for_status()
        
        return response.json()
```

---

## 🛠️ Programmatic Usage

### **Python API**

```python
from pathlib import Path
from core.converters.clawdbot_converter import ClawdbotSkillConverter

# Initialize converter
converter = ClawdbotSkillConverter(output_dir='skills')

# Check if Clawdbot skill
skill_path = Path('C:/Users/cngsm/Desktop/XXX/AG/hack')
if converter.is_clawdbot_skill(skill_path):
    print("✅ Clawdbot skill detected")
    
    # Convert
    output_path = converter.convert_skill(skill_path, auto_python=True)
    print(f"📁 Converted to: {output_path}")

# Batch convert
skills_dir = Path('C:/Users/cngsm/Desktop/XXX/AG')
converted = converter.batch_convert(skills_dir)
print(f"✅ Converted {len(converted)} skills")
```

---

## 📊 Conversion Process

```
┌─────────────────────────────────────┐
│   Clawdbot Skill (Input)            │
│   - SKILL.md (clawdbot metadata)    │
│   - bash/curl commands              │
│   - ~/.clawdbot paths               │
└──────────────┬──────────────────────┘
               ↓
┌──────────────────────────────────────┐
│   ClawdbotSkillConverter             │
│   1. Detect Clawdbot metadata        │
│   2. Convert frontmatter             │
│   3. Replace paths                   │
│   4. Generate Python wrapper         │
│   5. Copy additional files           │
└──────────────┬───────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   OpenCngsm Skill (Output)          │
│   - SKILL.md (opencngsm metadata)   │
│   - skill_name_skill.py (Python)    │
│   - ~/.opencngsm paths              │
└─────────────────────────────────────┘
```

---

## 🎯 CLI Commands

### **import-skill**
Import single Clawdbot skill

```bash
python -m core.converters.skill_importer import-skill <skill_path> [--output skills] [--no-python]
```

**Options:**
- `--output, -o`: Output directory (default: `skills`)
- `--no-python`: Skip Python wrapper generation

### **import-batch**
Import all Clawdbot skills from directory

```bash
python -m core.converters.skill_importer import-batch <skills_dir> [--output skills]
```

### **check**
Check if skill is Clawdbot format

```bash
python -m core.converters.skill_importer check <skill_path>
```

---

## 🔧 Advanced Configuration

### **Custom Path Mappings**

```python
from core.converters.clawdbot_converter import ClawdbotSkillConverter

converter = ClawdbotSkillConverter()

# Add custom mappings
converter.PATH_MAPPINGS['custom_old_path'] = 'custom_new_path'

# Convert
output = converter.convert_skill(skill_path)
```

### **Custom Python Template**

Override `_generate_wrapper_code()` method to customize Python generation.

---

## 📝 Examples

### **Example 1: Import Security Audit Skill**

```bash
# Check if Clawdbot skill
python -m core.converters.skill_importer check C:/Users/cngsm/Desktop/XXX/AG/hack

# Import
python -m core.converters.skill_importer import-skill C:/Users/cngsm/Desktop/XXX/AG/hack

# Result: skills/hack/
#   - SKILL.md (converted)
#   - hack_skill.py (generated)
#   - _meta.json (copied)
```

### **Example 2: Batch Import AG Skills**

```bash
python -m core.converters.skill_importer import-batch C:/Users/cngsm/Desktop/XXX/AG

# Result: skills/
#   - hack/
#   - telegram-bot-1.0.0/
```

### **Example 3: Programmatic Conversion**

```python
from pathlib import Path
from core.converters.clawdbot_converter import ClawdbotSkillConverter

converter = ClawdbotSkillConverter()

# Convert with custom output
output = converter.convert_skill(
    Path('C:/Users/cngsm/Desktop/XXX/AG/hack'),
    auto_python=True
)

print(f"Converted to: {output}")

# Read converted SKILL.md
skill_md = output / 'SKILL.md'
print(skill_md.read_text())
```

---

## 🐛 Troubleshooting

### **"Not a Clawdbot skill"**
- Check if `SKILL.md` exists
- Verify YAML frontmatter has `metadata.clawdbot`

### **"Python wrapper not generated"**
- Skill may not have bash/curl commands
- Use `--no-python` flag if not needed

### **"Import failed"**
- Check file permissions
- Verify output directory exists
- Check logs for detailed error

---

## 🎉 Success!

After conversion, you'll have:
- ✅ OpenCngsm-compatible SKILL.md
- ✅ Python wrapper (if applicable)
- ✅ All original files preserved
- ✅ Ready to integrate with OpenCngsm

**Next steps:**
1. Review converted skill
2. Test functionality
3. Add to OpenCngsm registry
4. Deploy!

---

## 📚 References

- [Agent Skills Specification](../Skills.txt)
- [OpenCngsm Skills Guide](../SKILLS_GUIDE.md)
- [Clawdbot Documentation](https://github.com/openclaw/openclaw)
