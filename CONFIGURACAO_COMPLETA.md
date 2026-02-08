# 🎨 Configuração Completa - Interface Web + Telegram Bot

## 🌐 INTERFACE WEB (Já Implementada!)

### Como Usar:

```bash
# Terminal 1: Gateway (obrigatório)
cd openclaw-system
python core/gateway/gateway.py

# Terminal 2: Web Dashboard
python interfaces/web/dashboard/app.py
```

Acesse: **http://127.0.0.1:8080**

**Recursos da Interface Web:**
- ✅ Chat interativo com o agente
- ✅ Estatísticas do sistema em tempo real
- ✅ Histórico de mensagens
- ✅ Design moderno com gradientes
- ✅ Animações suaves

---

## 💻 CLI (Já Implementado!)

### Comandos Disponíveis:

```bash
cd openclaw-system

# Ver ajuda
python -m cli.main --help

# Instalar sistema
python -m cli.main install

# Iniciar sistema
python -m cli.main start

# Ver status
python -m cli.main status

# Parar sistema
python -m cli.main stop
```

---

## 🤖 CONFIGURAR TELEGRAM BOT

### Passo 1: Criar Bot no Telegram

1. Abra o Telegram
2. Procure por **@BotFather**
3. Envie `/newbot`
4. Escolha um nome: `Meu OpenClaw Bot`
5. Escolha um username: `meu_openclaw_bot` (deve terminar com `_bot`)
6. **Copie o token** que o BotFather te enviar (formato: `1234567890:ABC-DEF...`)

### Passo 2: Obter Seu User ID

1. Procure por **@userinfobot** no Telegram
2. Envie `/start`
3. **Copie seu User ID** (ex: `123456789`)

### Passo 3: Configurar .env

```bash
cd openclaw-system

# Criar arquivo .env (se não existir)
cp .env.example .env

# Editar .env
nano .env  # ou notepad .env no Windows
```

**Adicione estas linhas:**

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:ABC-DEF1gh4Ij5Kl-mNoPQRsTUVwxyZ
TELEGRAM_ALLOWED_USERS=123456789

# Se tiver mais usuários permitidos, separe por vírgula:
# TELEGRAM_ALLOWED_USERS=123456789,987654321
```

### Passo 4: Configurar API Keys (Para IA)

No mesmo arquivo `.env`, adicione suas API keys:

```bash
# OpenRouter (Recomendado - acesso a vários modelos)
OPENROUTER_API_KEY=sk-or-v1-sua-chave-aqui

# OU OpenAI
OPENAI_API_KEY=sk-sua-chave-aqui

# OU Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui

# OU DeepSeek
DEEPSEEK_API_KEY=sk-sua-chave-aqui
```

**Como obter API keys:**

- **OpenRouter**: https://openrouter.ai/keys (Recomendado - $5 grátis)
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys
- **DeepSeek**: https://platform.deepseek.com/api_keys

### Passo 5: Iniciar Telegram Bot

```bash
# Terminal 1: Gateway (obrigatório)
python core/gateway/gateway.py

# Terminal 2: Telegram Bot
python interfaces/telegram/bot.py
```

Você verá:
```
🦞 OpenClaw Telegram Bot
========================================
Bot iniciado com sucesso!
Aguardando mensagens...
========================================
```

### Passo 6: Usar no Telegram

1. Procure seu bot no Telegram (pelo username que você criou)
2. Envie `/start`
3. Envie `/help` para ver comandos
4. Envie mensagens naturais:
   - "Crie um arquivo notas.txt com minhas tarefas"
   - "Leia o arquivo notas.txt"
   - "Execute o comando dir"
   - "Gere um resumo sobre inteligência artificial"

---

## 📝 Exemplo Completo de .env

```bash
# ============================================
# OpenClaw MCP - Configuração
# ============================================

# Sistema
OPENCLAW_SECRET=openclaw-demo-secret
JWT_SECRET_KEY=mude-isso-em-producao-use-senha-forte
ENVIRONMENT=development

# Gateway
GATEWAY_HOST=127.0.0.1
GATEWAY_PORT=18789

# ============================================
# TELEGRAM BOT
# ============================================
TELEGRAM_BOT_TOKEN=1234567890:ABC-DEF1gh4Ij5Kl-mNoPQRsTUVwxyZ
TELEGRAM_ALLOWED_USERS=123456789

# ============================================
# API KEYS (Escolha pelo menos uma)
# ============================================

# OpenRouter (Recomendado - múltiplos modelos)
OPENROUTER_API_KEY=sk-or-v1-sua-chave-aqui

# OpenAI
# OPENAI_API_KEY=sk-sua-chave-aqui

# Anthropic Claude
# ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui

# DeepSeek
# DEEPSEEK_API_KEY=sk-sua-chave-aqui

# ============================================
# Logging
# ============================================
LOG_LEVEL=INFO
```

---

## 🎯 Fluxo Completo de Uso

### Opção 1: Web Dashboard

```bash
# Terminal 1
python core/gateway/gateway.py

# Terminal 2
python interfaces/web/dashboard/app.py

# Navegador
http://127.0.0.1:8080
```

### Opção 2: Telegram Bot

```bash
# Terminal 1
python core/gateway/gateway.py

# Terminal 2
python interfaces/telegram/bot.py

# Telegram
Envie mensagens para seu bot
```

### Opção 3: API Direta

```bash
# Terminal 1
python core/gateway/gateway.py

# Navegador
http://127.0.0.1:18789/docs

# Ou use cURL/Python
python testar_api.py
```

---

## 🔐 Configurar Permissões

Edite `config/permissions.yaml`:

```yaml
# Permissões padrão
default_permissions:
  file_read: allow
  file_write: ask      # Pede confirmação
  file_delete: deny    # Bloqueia
  bash_execute: ask
  ia_api: allow
  external_api: ask

# Permissões por usuário (Telegram User ID)
user_permissions:
  "123456789":  # Seu User ID do Telegram
    file_read: allow
    file_write: allow
    file_delete: ask
    bash_execute: allow
    ia_api: allow
    external_api: allow
```

---

## 🚀 Iniciar Tudo de Uma Vez

Crie um script `start_all.sh` (Linux/Mac) ou `start_all.bat` (Windows):

**Windows (start_all.bat):**
```batch
@echo off
start "Gateway" cmd /k "python core/gateway/gateway.py"
timeout /t 2
start "Web Dashboard" cmd /k "python interfaces/web/dashboard/app.py"
start "Telegram Bot" cmd /k "python interfaces/telegram/bot.py"
echo.
echo ✅ Todos os serviços iniciados!
echo.
echo Gateway: http://127.0.0.1:18789
echo Web Dashboard: http://127.0.0.1:8080
echo Telegram Bot: Rodando
```

**Linux/Mac (start_all.sh):**
```bash
#!/bin/bash

# Gateway
python core/gateway/gateway.py &
sleep 2

# Web Dashboard
python interfaces/web/dashboard/app.py &

# Telegram Bot
python interfaces/telegram/bot.py &

echo "✅ Todos os serviços iniciados!"
echo "Gateway: http://127.0.0.1:18789"
echo "Web Dashboard: http://127.0.0.1:8080"
echo "Telegram Bot: Rodando"
```

Execute:
```bash
# Windows
start_all.bat

# Linux/Mac
chmod +x start_all.sh
./start_all.sh
```

---

## 📊 Verificar se Está Funcionando

```bash
# 1. Gateway
curl http://127.0.0.1:18789/api/v1/status

# 2. Web Dashboard
curl http://127.0.0.1:8080

# 3. Telegram Bot
# Envie /start para o bot no Telegram
```

---

## 🎨 Screenshots do que você terá:

### Web Dashboard:
- Chat interface moderna
- Gradientes azul/roxo
- Animações suaves
- Estatísticas em tempo real

### Telegram Bot:
- Comandos: /start, /help, /status
- Mensagens naturais
- Respostas formatadas
- Emojis e markdown

### CLI:
- Comandos simples
- Output colorido (com rich)
- Fácil automação

---

## ✅ Checklist Final

- [ ] Criar bot no @BotFather
- [ ] Obter User ID no @userinfobot
- [ ] Criar arquivo .env
- [ ] Adicionar TELEGRAM_BOT_TOKEN
- [ ] Adicionar TELEGRAM_ALLOWED_USERS
- [ ] Adicionar API key (OpenRouter/OpenAI/etc)
- [ ] Iniciar Gateway
- [ ] Iniciar Telegram Bot
- [ ] Testar enviando /start
- [ ] Enviar mensagem de teste

---

**Pronto!** Agora você tem:
- ✅ Interface Web moderna
- ✅ Bot Telegram funcional
- ✅ CLI para automação
- ✅ API REST completa

Qualquer dúvida, é só perguntar! 🦞
