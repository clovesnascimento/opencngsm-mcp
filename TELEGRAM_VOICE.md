# 🎤 Telegram Voice Integration

## 📖 Visão Geral

Integração automática de **voice messages do Telegram** com transcrição via Voxtral.

---

## ✨ Recursos

- ✅ **Auto-transcrição** de voice messages
- ✅ **Processamento normal** (transcription → OpenCngsm)
- ✅ **Resposta configurável** (texto ou voz)
- ✅ **Typing action** durante transcrição
- ✅ **Suporte multi-idioma**

---

## 🚀 Como Usar

### 1. Configurar Bot

```python
from skills.telegram_skill import TelegramSkill
from skills.voice_skill import VoiceSkill

# Initialize Voice Skill
voice = VoiceSkill(mistral_api_key='your_key')

# Initialize Telegram with Voice support
telegram = TelegramSkill(
    bot_token='your_bot_token',
    chat_id='your_chat_id',
    voice_skill=voice  # Enable voice transcription
)
```

---

### 2. Handlers

```python
# Text message handler
async def handle_text(text: str, update):
    response = process_message(text)
    await telegram.send_message(response)

# Voice message handler
async def handle_voice(transcription: str, update):
    response = process_message(transcription)
    await telegram.send_message(response)

# Start bot
await telegram.start_bot(
    on_message_callback=handle_text,
    on_voice_callback=handle_voice
)
```

---

### 3. Resposta em Voz (Opcional)

```python
# Enable voice responses
telegram.enable_voice_responses(True)

async def handle_voice(transcription: str, update):
    response = process_message(transcription)
    
    # Synthesize voice response
    audio = await voice.synthesize_speech(response)
    
    # Send voice message
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(audio)
        await telegram.send_voice(f.name)
```

---

## 🔄 Fluxo

```
1. User sends voice message in Telegram
2. Bot receives voice message
3. Download voice file (.ogg)
4. Voice Skill → Voxtral → Transcription
5. Process transcription (same as text)
6. Generate response
7. Send response (text or voice)
```

---

## 📋 Exemplo Completo

Ver `examples/telegram_voice_bot.py`:

```bash
# Setup
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export MISTRAL_API_KEY="your_mistral_key"

# Run
python examples/telegram_voice_bot.py
```

**Uso:**
1. Envie mensagem de texto → Resposta em texto
2. Envie voice message → Auto-transcrição → Resposta em texto
3. (Opcional) Habilite voice responses → Resposta em voz

---

## ⚙️ Configuração

### Resposta em Texto (Padrão)

```python
telegram.enable_voice_responses(False)
```

**Fluxo:**
```
Voice message → Transcription → Text response
```

---

### Resposta em Voz

```python
telegram.enable_voice_responses(True)
```

**Fluxo:**
```
Voice message → Transcription → Voice response
```

---

## 🎯 Casos de Uso

### 1. **Assistente Mãos-Livres**
- Usuário dirigindo
- Envia comandos de voz
- Recebe respostas em voz

### 2. **Acessibilidade**
- Usuários com dificuldade de digitação
- Interface 100% por voz

### 3. **Multilíngue**
- Detecção automática de idioma
- Transcrição precisa

---

## 📊 Performance

| Métrica | Valor |
|---------|-------|
| **Download** | ~500ms |
| **Transcrição** | ~200-500ms |
| **Processamento** | ~500-1000ms |
| **Total** | ~1-2s |

---

## 🔐 Privacidade

- **Voice files** são temporários (deletados após transcrição)
- **Transcrições** armazenadas como mensagens normais
- **Mesma política** de privacidade do sistema

---

## 🛠️ Troubleshooting

### "Voice skill not configured"
```python
# Certifique-se de passar voice_skill ao criar TelegramSkill
telegram = TelegramSkill(..., voice_skill=voice)
```

### "Transcription failed"
- Verificar `MISTRAL_API_KEY`
- Verificar créditos da API
- Testar com arquivo de áudio menor

### "Voice message not detected"
- Verificar se é voice message (não áudio comum)
- Telegram envia voice messages como .ogg

---

**Telegram + Voice = Input de voz automático! 🎤**
