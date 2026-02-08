# 🌍 Universal Path Management - OpenCngsm

## 📖 Overview

Sistema de gerenciamento de configuração universal que funciona em **qualquer diretório** e **qualquer plataforma** (Windows, Linux, macOS).

---

## 🎯 Problema Resolvido

### **Antes (Hardcoded):**
```python
config_path = '~/.opencngsm/config.json'  # ❌ Não funciona em Windows
skills_dir = 'C:/Users/user/Desktop/XXX/skills'  # ❌ Path específico
```

### **Depois (Universal):**
```python
from core.config_manager import config

config_path = config.config_file  # ✅ Auto-detectado
skills_dir = config.get_skills_dir()  # ✅ Universal
```

---

## 🚀 Como Funciona

### **1. Auto-detecção do Diretório de Instalação**

```python
# Método 1: Variável de ambiente
export OPENCNGSM_HOME=/opt/opencngsm

# Método 2: Diretório atual (se contém skills/ e core/)
cd /home/user/opencngsm
python main.py  # ✅ Detecta automaticamente

# Método 3: Localização do script
python /opt/opencngsm/main.py  # ✅ Detecta /opt/opencngsm

# Método 4: Executável compilado
./opencngsm  # ✅ Detecta diretório do executável
```

### **2. Diretórios de Configuração (Cross-Platform)**

| Plataforma | Config Dir |
|------------|------------|
| **Windows** | `%APPDATA%\OpenCngsm` |
| **macOS** | `~/Library/Application Support/OpenCngsm` |
| **Linux** | `~/.config/opencngsm` |

**Exemplo:**
```python
from core.config_manager import get_config_dir

config_dir = get_config_dir()
# Windows: C:\Users\user\AppData\Roaming\OpenCngsm
# macOS: /Users/user/Library/Application Support/OpenCngsm
# Linux: /home/user/.config/opencngsm
```

### **3. Estrutura de Diretórios**

```
# Instalação (pode estar em qualquer lugar)
/opt/opencngsm/  (ou C:\Program Files\OpenCngsm\)
├── core/
├── skills/
├── api/
└── main.py

# Configuração do usuário (específica por plataforma)
~/.config/opencngsm/  (Linux)
├── config.json
├── data/
└── logs/
    └── opencngsm.log
```

---

## 📋 Uso

### **Básico**

```python
from core.config_manager import config

# Obter valores
port = config.get('gateway.port')  # 18789
token = config.get('gateway.auth.token')

# Definir valores
config.set('gateway.port', 8080)

# Obter paths
skills_dir = config.get_skills_dir()
data_dir = config.get_data_dir()
logs_dir = config.get_logs_dir()
```

### **Funções de Conveniência**

```python
from core.config_manager import (
    get_config_dir,
    get_install_dir,
    get_skills_dir,
    get_data_dir,
    get_logs_dir
)

# Diretórios
config_dir = get_config_dir()  # ~/.config/opencngsm
install_dir = get_install_dir()  # /opt/opencngsm
skills_dir = get_skills_dir()  # /opt/opencngsm/skills
```

### **Em Skills**

```python
from core.config_manager import config

class MySkill:
    def __init__(self):
        # Usar config universal
        self.config_path = config.config_file
        self.data_dir = config.get_data_dir()
    
    def save_data(self, data):
        # Salvar em diretório de dados do usuário
        file_path = self.data_dir / 'myskill_data.json'
        with open(file_path, 'w') as f:
            json.dump(data, f)
```

---

## 🔧 Configuração Padrão

```json
{
  "version": "3.1",
  "install_dir": "/opt/opencngsm",
  "config_dir": "/home/user/.config/opencngsm",
  "platform": "Linux",
  
  "gateway": {
    "bind": "loopback",
    "port": 18789,
    "auth": {
      "mode": "token",
      "token": "auto-generated-48-char-token"
    }
  },
  
  "skills": {
    "directory": "/opt/opencngsm/skills",
    "auto_load": true,
    "sandbox": {
      "enabled": false,
      "default_cpu_limit": 1.0,
      "default_memory_limit": "512m"
    }
  },
  
  "logging": {
    "level": "INFO",
    "file": "/home/user/.config/opencngsm/logs/opencngsm.log"
  }
}
```

---

## 🌍 Distribuição em Massa

### **Cenário 1: Instalação em Diferentes Diretórios**

```bash
# Usuário 1
cd /home/alice/projects/opencngsm
python main.py  # ✅ Funciona

# Usuário 2
cd C:\Users\Bob\Desktop\opencngsm
python main.py  # ✅ Funciona

# Usuário 3
cd /opt/opencngsm
python main.py  # ✅ Funciona
```

### **Cenário 2: Múltiplos Usuários no Mesmo Sistema**

```bash
# Usuário Alice
python /opt/opencngsm/main.py
# Config: /home/alice/.config/opencngsm/

# Usuário Bob
python /opt/opencngsm/main.py
# Config: /home/bob/.config/opencngsm/

# ✅ Cada usuário tem sua própria configuração
```

### **Cenário 3: Variável de Ambiente**

```bash
# Definir diretório de instalação
export OPENCNGSM_HOME=/custom/path/opencngsm

python -m opencngsm
# ✅ Usa /custom/path/opencngsm
```

---

## 🔄 Integração com Conversor

O conversor de skills agora usa paths universais:

```python
from core.converters.clawdbot_converter import ClawdbotSkillConverter

# Sem especificar output_dir (usa auto-detectado)
converter = ClawdbotSkillConverter()
output = converter.convert_skill(skill_path)
# ✅ Salva em <install_dir>/skills/

# Com output_dir customizado
converter = ClawdbotSkillConverter(output_dir='/custom/skills')
output = converter.convert_skill(skill_path)
# ✅ Salva em /custom/skills/
```

**Skills convertidas usam ConfigManager:**

```python
# Skill gerada automaticamente
from core.config_manager import config

class ConvertedSkill:
    def __init__(self):
        # ✅ Path universal
        self.config_path = config.config_file
```

---

## 📊 Benefícios

| Benefício | Descrição |
|-----------|-----------|
| **Portabilidade** | Funciona em qualquer diretório |
| **Cross-platform** | Windows, Linux, macOS |
| **Multi-usuário** | Cada usuário tem sua config |
| **Distribuição** | Sem hardcoded paths |
| **Flexibilidade** | Variável de ambiente opcional |

---

## 🧪 Teste

```bash
# Testar auto-detecção
python -c "
from core.config_manager import config
print(f'Platform: {config.platform}')
print(f'Install Dir: {config.install_dir}')
print(f'Config Dir: {config.config_dir}')
print(f'Skills Dir: {config.get_skills_dir()}')
"

# Output (exemplo Linux):
# Platform: Linux
# Install Dir: /home/user/opencngsm
# Config Dir: /home/user/.config/opencngsm
# Skills Dir: /home/user/opencngsm/skills
```

---

## 🎯 Resumo

**OpenCngsm agora é 100% portável!**

✅ **Auto-detecção** de diretório de instalação  
✅ **Cross-platform** (Windows, Linux, macOS)  
✅ **Multi-usuário** (configs separadas)  
✅ **Sem hardcoded paths**  
✅ **Distribuição em massa** sem erros  

**Funciona em qualquer lugar, para qualquer usuário!** 🌍✨
