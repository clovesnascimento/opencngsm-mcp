# 🎤 Voice Button - React Component

## 📖 Visão Geral

Componente React **VoiceButton** para entrada de voz com:
- ✅ Push-to-talk (segurar para gravar)
- ✅ Visualização de áudio em tempo real
- ✅ Transcrição automática via API
- ✅ UI moderna e responsiva

---

## 🚀 Instalação

```bash
# Já incluído no frontend
cd frontend
npm install
```

---

## 💡 Uso Básico

```jsx
import VoiceButton from './components/VoiceButton';

function App() {
  const handleTranscript = (text) => {
    console.log('User said:', text);
    // Process transcription
  };

  return (
    <VoiceButton
      onTranscript={handleTranscript}
      apiUrl="/api/voice/transcribe"
      language="pt"
    />
  );
}
```

---

## 📋 Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onTranscript` | `(text: string) => void` | - | Callback com transcrição |
| `onError` | `(error: Error) => void` | - | Callback de erro |
| `apiUrl` | `string` | `/api/voice/transcribe` | Endpoint da API |
| `language` | `string` | `'pt'` | Idioma (pt, en, es, etc.) |
| `className` | `string` | `''` | CSS class adicional |

---

## 🎨 Recursos

### 1. **Push-to-Talk**
- Segurar botão para gravar
- Soltar para parar e transcrever
- Funciona com mouse e touch

### 2. **Visualização de Áudio**
- Nível de áudio em tempo real
- Animação de pulso durante gravação
- Indicador visual de status

### 3. **Estados**
- 🎤 **Idle**: "Hold to talk"
- 🔴 **Recording**: "Recording..."
- ⏳ **Processing**: "Transcribing..."
- ⚠️ **Error**: Mensagem de erro

### 4. **Responsivo**
- Mobile-friendly
- Touch events
- Tamanhos adaptativos

---

## 🔧 Backend API

O componente espera um endpoint `/api/voice/transcribe`:

```python
# FastAPI example
from fastapi import FastAPI, File, UploadFile, Form

app = FastAPI()

@app.post("/api/voice/transcribe")
async def transcribe_voice(
    audio: UploadFile = File(...),
    language: str = Form('pt')
):
    # Save audio
    audio_bytes = await audio.read()
    
    # Transcribe with Voice Skill
    from skills.voice_skill import VoiceSkill
    voice = VoiceSkill()
    
    # Save to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
        f.write(audio_bytes)
        temp_path = f.name
    
    # Transcribe
    transcription = await voice.transcribe_audio(temp_path, language=language)
    
    # Cleanup
    os.unlink(temp_path)
    
    return {
        "transcription": transcription,
        "language": language
    }
```

---

## 🎯 Exemplo Completo

Ver `frontend/src/App.jsx` para exemplo completo com:
- Chat interface
- Mensagens de texto e voz
- Integração com VoiceButton
- UI moderna

```bash
# Rodar frontend
cd frontend
npm start
```

---

## 🔐 Permissões

### Microfone

O navegador pedirá permissão para acessar o microfone:

**Chrome/Edge:**
```
Settings → Privacy → Microphone → Allow
```

**Firefox:**
```
Preferences → Privacy → Permissions → Microphone
```

**Safari:**
```
Preferences → Websites → Microphone → Allow
```

---

## 🎨 Customização

### CSS

Edite `VoiceButton.css` para customizar:

```css
.voice-button {
  /* Cor do botão */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  /* Tamanho */
  width: 64px;
  height: 64px;
}

.voice-button.recording {
  /* Cor durante gravação */
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
```

---

## 📊 Performance

| Métrica | Valor |
|---------|-------|
| **Gravação** | Tempo real |
| **Upload** | ~500ms (depende da conexão) |
| **Transcrição** | ~200-500ms (Voxtral API) |
| **Total** | ~1-2s |

---

## 🛠️ Troubleshooting

### "Microphone access denied"
- Verificar permissões do navegador
- Usar HTTPS (HTTP não permite microfone)
- Testar em `chrome://settings/content/microphone`

### "Failed to transcribe"
- Verificar se backend está rodando
- Verificar endpoint `/api/voice/transcribe`
- Verificar `MISTRAL_API_KEY` no backend

### "No audio detected"
- Testar microfone em outras apps
- Verificar volume do microfone
- Tentar outro navegador

---

## 🌐 Browser Support

| Browser | Support |
|---------|---------|
| Chrome | ✅ Full |
| Firefox | ✅ Full |
| Safari | ✅ Full (iOS 14.3+) |
| Edge | ✅ Full |

---

**VoiceButton pronto para uso! 🎤✨**
