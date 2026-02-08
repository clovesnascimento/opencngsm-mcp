# 🎤 Voice Input Feature - OpenCngsm v3.0

## 📖 Visão Geral

O **Voice Input** é um **recurso adicional** do OpenCngsm v3.0 que permite aos usuários **enviar comandos via voz** em vez de texto.

> **Importante**: Voice é uma **opção adicional**, não substitui o sistema existente. Usuários podem escolher entre texto ou voz.

---

## ✨ Recursos

### 🎙️ Entrada de Voz (Speech-to-Text)
- **Transcrição de áudio** usando Voxtral (Mistral AI)
- **Suporte multi-idioma** (PT, EN, ES, FR, etc.)
- **Realtime transcription** para conversas ao vivo
- **Diarização** (identificar quem está falando)

### 🔊 Saída de Voz (Text-to-Speech) - Opcional
- **Síntese de voz** usando Kokoro
- **Vozes naturais** (masculina, feminina)
- **Multi-idioma** (EN, PT, ES, FR, JP, CN, KR)
- **Resposta em áudio** (opcional, configurável)

---

## 🚀 Como Usar

### 1. **Interface Web - Botão de Voz**

```jsx
// Frontend React
<VoiceButton 
  onTranscript={(text) => sendMessage(text)}
  enableAudioResponse={true}
/>
```

**Fluxo:**
1. Clique no botão 🎤
2. Fale seu comando
3. Solte o botão
4. Comando é processado normalmente

---

### 2. **Telegram - Voice Messages**

**Fluxo:**
1. Envie uma mensagem de voz no Telegram
2. Bot transcreve automaticamente
3. Processa como mensagem de texto
4. Responde em texto (ou voz, se configurado)

**Exemplo:**
```
👤 User: [voice message: "Qual é o clima hoje?"]
🤖 Bot: "O clima em Fortaleza está 28°C e ensolarado."
```

---

### 3. **API - Endpoint de Voz**

```bash
# Enviar áudio via API
curl -X POST http://localhost:8000/api/voice/transcribe \
  -H "Authorization: Bearer TOKEN" \
  -F "audio=@recording.mp3" \
  -F "language=pt"

# Response
{
  "transcription": "Qual é o clima hoje?",
  "confidence": 0.98
}
```

---

### 4. **Python SDK**

```python
from skills.voice_skill import VoiceSkill

voice = VoiceSkill()

# Transcrever áudio
text = await voice.transcribe_audio('comando.mp3', language='pt')
print(f"Comando: {text}")

# Processar normalmente
response = await process_command(text)

# Opcional: Responder em voz
await voice.speak(response)
```

---

## 📋 Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Dependências adicionadas:**
- `mistralai[realtime]` - Voxtral STT
- `torch`, `transformers` - Kokoro TTS
- `pyaudio`, `sounddevice` - Audio I/O

---

### 2. Configurar API Key

```bash
# Obter em: https://console.mistral.ai/
export MISTRAL_API_KEY="your_mistral_api_key"
```

---

### 3. Habilitar Voice no Config

```json
// config.json
{
  "voice": {
    "enabled": true,
    "stt_provider": "voxtral",
    "tts_provider": "kokoro",
    "default_language": "pt",
    "audio_response": false,  // Responder em voz por padrão?
    "realtime": false         // Transcrição em tempo real?
  }
}
```

---

## 🎯 Casos de Uso

### ✅ Quando Usar Voz

1. **Mãos ocupadas** - Usuário dirigindo, cozinhando, etc.
2. **Mais rápido** - Falar é mais rápido que digitar
3. **Acessibilidade** - Usuários com dificuldade de digitação
4. **Preferência pessoal** - Alguns preferem falar

### 📝 Quando Usar Texto

1. **Ambiente silencioso** - Biblioteca, reunião, etc.
2. **Privacidade** - Não quer que outros ouçam
3. **Precisão** - Comandos complexos ou técnicos
4. **Histórico** - Mais fácil revisar texto

---

## 🔧 Integração com Canais

### Telegram

```python
# telegram_skill.py
async def handle_voice_message(update):
    # Download voice message
    voice_file = await update.message.voice.get_file()
    audio_bytes = await voice_file.download_as_bytearray()
    
    # Transcribe
    text = await voice_skill.transcribe_audio(audio_bytes)
    
    # Process normally
    response = await process_message(text)
    
    # Respond (text or voice)
    if user_prefers_voice:
        audio = await voice_skill.synthesize_speech(response)
        await bot.send_voice(chat_id, audio)
    else:
        await bot.send_message(chat_id, response)
```

---

### Web Interface

```jsx
// VoiceButton.jsx
function VoiceButton() {
  const [recording, setRecording] = useState(false);
  
  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    // ... record audio
  };
  
  const stopRecording = async () => {
    // ... stop recording
    const audioBlob = recorder.getBlob();
    
    // Send to backend
    const formData = new FormData();
    formData.append('audio', audioBlob);
    
    const response = await fetch('/api/voice/transcribe', {
      method: 'POST',
      body: formData
    });
    
    const { transcription } = await response.json();
    onTranscript(transcription);
  };
  
  return (
    <button 
      onMouseDown={startRecording}
      onMouseUp={stopRecording}
    >
      {recording ? '🔴 Recording...' : '🎤 Hold to Talk'}
    </button>
  );
}
```

---

## 📊 Performance

### Latência Esperada

| Etapa | Tempo |
|-------|-------|
| Gravação | 1-5s (usuário falando) |
| Upload | 100-500ms |
| Transcrição (Voxtral) | 200-500ms |
| Processamento | 500-1000ms |
| TTS (opcional) | 200-300ms |
| **Total** | **~2-3s** |

### Qualidade

- **WER (Word Error Rate)**: <5% (Voxtral)
- **Precisão**: >95% (português)
- **Suporte**: 20+ idiomas

---

## 🔐 Privacidade

### Dados de Áudio

- **Não armazenados** por padrão
- **Processados em tempo real** e descartados
- **Opcional**: Salvar para análise (com consentimento)

### Transcrições

- **Armazenadas** como mensagens de texto normais
- **Mesma política** de privacidade do sistema

---

## 🚧 Limitações

1. **Requer internet** - Voxtral é API cloud (Mistral AI)
2. **Custo** - Transcrição tem custo por minuto
3. **Idiomas** - Melhor performance em EN/PT/ES/FR
4. **Ruído** - Ambientes barulhentos afetam qualidade

---

## 🛠️ Troubleshooting

### "Microfone não funciona"
- Verificar permissões do navegador
- Testar em `chrome://settings/content/microphone`

### "Transcrição incorreta"
- Falar mais devagar e claramente
- Reduzir ruído de fundo
- Usar fone com microfone

### "API key inválida"
- Verificar `MISTRAL_API_KEY`
- Renovar key em https://console.mistral.ai/

---

## 📚 Exemplos

Ver `examples/voice_usage.py` para exemplos completos:

```bash
python examples/voice_usage.py
```

---

## 🎯 Roadmap

### v3.1 (Atual)
- ✅ Voice Skill básico
- ✅ Transcrição de arquivos
- ✅ Integração Telegram
- ✅ Web interface

### v3.2 (Futuro)
- [ ] Realtime transcription (streaming)
- [ ] Wake word detection
- [ ] Voice profiles personalizados
- [ ] Phone call integration

---

**Voice é um recurso adicional que complementa o OpenCngsm! 🎤**
