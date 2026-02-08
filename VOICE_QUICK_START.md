# 🚀 OpenCngsm v3.0 - Voice Feature Quick Start

## 📦 O que foi implementado

### ✅ Backend (Python)
- **Voice Skill** - Voxtral STT + Kokoro TTS
- **Telegram Integration** - Auto-transcrição de voice messages
- **FastAPI Routes** - `/api/voice/transcribe` e `/api/voice/synthesize`

### ✅ Frontend (React)
- **VoiceButton** - Componente push-to-talk
- **Audio Visualization** - Nível de áudio em tempo real
- **Chat UI** - Interface moderna com suporte a voz

---

## 🚀 Como Rodar

### 1. Backend

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar API key
export MISTRAL_API_KEY="your_mistral_api_key"

# Rodar servidor
python api/main.py
```

**Servidor rodando em:** http://localhost:8000

---

### 2. Frontend

```bash
# Entrar no diretório
cd frontend

# Instalar dependências (primeira vez)
npm install

# Rodar dev server
npm start
```

**Frontend rodando em:** http://localhost:3000

---

## 🎯 Testar

### Web Interface

1. Abra http://localhost:3000
2. Clique e **segure** o botão 🎤
3. Fale seu comando
4. Solte o botão
5. Veja a transcrição aparecer!

---

### Telegram Bot

```bash
# Configurar
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export MISTRAL_API_KEY="your_key"

# Rodar bot
python examples/telegram_voice_bot.py
```

**Uso:**
- Envie mensagem de texto → Resposta em texto
- Envie voice message → Auto-transcrição → Resposta

---

### API Direta

```bash
# Transcrever áudio
curl -X POST http://localhost:8000/api/voice/transcribe \
  -F "audio=@recording.mp3" \
  -F "language=pt"

# Sintetizar voz
curl -X POST http://localhost:8000/api/voice/synthesize \
  -F "text=Olá, como posso ajudar?" \
  -F "voice=af" \
  --output response.wav
```

---

## 📁 Estrutura de Arquivos

```
opencngsm-mcp/
├── skills/
│   ├── voice_skill.py          # Voice Skill (STT + TTS)
│   └── telegram_skill.py       # Telegram com voice support
├── api/
│   ├── main.py                 # FastAPI app
│   └── routes/
│       └── voice.py            # Voice endpoints
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── VoiceButton.jsx # Componente de voz
│       │   └── VoiceButton.css # Estilos
│       ├── App.jsx             # App principal
│       └── App.css             # Estilos do app
├── examples/
│   ├── telegram_voice_bot.py  # Bot Telegram
│   └── voice_usage.py          # Exemplos de uso
└── docs/
    ├── VOICE_FEATURE.md        # Documentação geral
    ├── VOICE_BUTTON.md         # Documentação do componente
    └── TELEGRAM_VOICE.md       # Integração Telegram
```

---

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Obrigatório para STT
export MISTRAL_API_KEY="your_mistral_api_key"

# Opcional para Telegram
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

**Obter Mistral API Key:**
https://console.mistral.ai/

---

## 📚 Documentação

- **VOICE_FEATURE.md** - Visão geral do recurso de voz
- **VOICE_BUTTON.md** - Componente React VoiceButton
- **TELEGRAM_VOICE.md** - Integração com Telegram
- **SKILLS_GUIDE.md** - Guia de todos os skills

---

## 🎯 Casos de Uso

### 1. **Web Chat com Voz**
- Usuário digita OU fala
- Resposta em texto
- Interface moderna

### 2. **Telegram Voice Bot**
- Voice messages → Auto-transcrição
- Processamento normal
- Resposta em texto ou voz

### 3. **API de Voz**
- Apps mobile podem enviar áudio
- Recebem transcrição
- Integração fácil

---

## 🛠️ Troubleshooting

### Backend não inicia
```bash
# Verificar dependências
pip install -r requirements.txt

# Verificar API key
echo $MISTRAL_API_KEY
```

### Frontend não conecta
```bash
# Verificar se backend está rodando
curl http://localhost:8000/health

# Verificar CORS no backend
```

### Microfone não funciona
- Usar HTTPS (ou localhost)
- Permitir acesso ao microfone no navegador
- Testar em chrome://settings/content/microphone

---

## 📊 Performance

| Componente | Latência |
|------------|----------|
| Gravação | Tempo real |
| Upload | ~500ms |
| Transcrição (Voxtral) | ~200-500ms |
| Processamento | ~500ms |
| **Total** | **~1-2s** |

---

## 🎉 Pronto!

**OpenCngsm v3.0 agora tem capacidade de voz completa!** 🎤✨

- ✅ Voice Skill implementado
- ✅ Telegram integrado
- ✅ Frontend React com VoiceButton
- ✅ API endpoints prontos
- ✅ Documentação completa

**Comece a testar agora!** 🚀
