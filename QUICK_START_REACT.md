# 🚀 OpenCngsm MCP v2.0 - Quick Start Guide (React Frontend)

## ✅ Sistema Instalado com Sucesso!

Você agora tem um sistema completo com:
- ✅ Backend FastAPI (Gateway + Orchestrator)
- ✅ Frontend React moderno com Tailwind CSS
- ✅ Autenticação JWT
- ✅ 11 Skills modulares
- ✅ Interface de Chat interativa

---

## 📋 Passo a Passo para Iniciar

### 1️⃣ Iniciar o Backend (Terminal 1)

```bash
cd opencngsm-mcp
pip install -r requirements.txt
python core/gateway/gateway.py
```

**Aguarde a mensagem:**
```
🚀 Starting OpenCngsm MCP Gateway...
📡 Backend: http://127.0.0.1:18789
🌐 Frontend: http://localhost:5173
```

### 2️⃣ Iniciar o Frontend (Terminal 2 - NOVO)

```bash
cd opencngsm-mcp/frontend
npm install
npm run dev
```

**Aguarde a mensagem:**
```
  VITE v5.0.11  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3️⃣ Acessar a Interface

Abra seu navegador em: **http://localhost:5173**

### 4️⃣ Fazer Login

Use as credenciais padrão:
- **User ID:** `admin`
- **Secret:** `opencngsm_secret_2024`

---

## 🎨 Recursos da Interface React

### Dashboard Principal
- ✅ Header com status online
- ✅ 4 Cards de estatísticas (Gateway, Skills, Mensagens, Status)
- ✅ Chat interativo em tempo real
- ✅ Design responsivo (mobile/desktop)

### Chat Component
- ✅ Input de mensagem com validação
- ✅ Lista de mensagens (user/bot)
- ✅ Loading states com animação
- ✅ Auto-scroll para última mensagem
- ✅ Exibição de planos de execução
- ✅ Error handling visual

### Tecnologias Usadas
- **React 18.2** - Framework UI
- **Vite 5.0** - Build tool
- **Tailwind CSS 3.4** - Styling
- **Axios 1.6** - HTTP client
- **Heroicons 2.1** - Ícones

---

## 🔧 Comandos Úteis

### Backend
```bash
# Iniciar gateway
python core/gateway/gateway.py

# Testar API
python testar_api.py

# CLI Interface
python interfaces/cli/cli.py
```

### Frontend
```bash
# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

---

## 📡 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/login` | Autenticar usuário |
| GET | `/api/status` | Status do sistema |
| POST | `/api/message` | Enviar mensagem |
| GET | `/api/skills` | Listar skills |

---

## 🎯 Testando o Sistema

### 1. Teste de Login
1. Acesse http://localhost:5173
2. Digite: `admin` / `opencngsm_secret_2024`
3. Clique em "Login"

### 2. Teste de Chat
1. Digite uma mensagem: "Olá, como você funciona?"
2. Pressione "Send"
3. Veja a resposta com plano de execução

### 3. Teste de Status
1. Observe os cards de estatísticas
2. Verifique se "Gateway" está "active"
3. Confirme que há 11 skills disponíveis

---

## 🏗️ Estrutura do Projeto

```
opencngsm-mcp/
├── core/
│   ├── gateway/
│   │   └── gateway.py          # FastAPI server
│   ├── orchestrator/
│   │   └── orchestrator.py     # Cognitive orchestration
│   ├── memory/
│   │   └── memory_system.py    # Memory management
│   ├── skills/
│   │   └── skills.py           # 11 modular skills
│   └── auth/
│       └── jwt_auth.py         # JWT authentication
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx      # Header component
│   │   │   ├── StatusCard.jsx  # Status cards
│   │   │   └── Chat.jsx        # Chat interface
│   │   ├── services/
│   │   │   └── api.js          # API client
│   │   ├── App.jsx             # Main app
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Tailwind CSS
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── interfaces/
│   ├── telegram/
│   │   └── bot.py              # Telegram bot
│   └── cli/
│       └── cli.py              # CLI interface
└── config/
    └── config.json             # Configuration
```

---

## 🔐 Segurança

### Alterar Credenciais Padrão

**Backend (core/gateway/gateway.py):**
```python
if request.secret == "SUA_NOVA_SENHA_AQUI":
```

**Backend (core/auth/jwt_auth.py):**
```python
self.secret_key = "SUA_CHAVE_JWT_AQUI"
```

---

## 🚀 Build para Produção

### 1. Build do Frontend
```bash
cd frontend
npm run build
```

Arquivos gerados em: `frontend/dist/`

### 2. Servir Arquivos Estáticos
Configure o FastAPI para servir os arquivos do build:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

---

## 🐛 Troubleshooting

### Backend não inicia
- ✅ Verifique se a porta 18789 está livre
- ✅ Instale as dependências: `pip install -r requirements.txt`

### Frontend não conecta
- ✅ Verifique se o backend está rodando
- ✅ Confirme o proxy no `vite.config.js`
- ✅ Verifique CORS no `gateway.py`

### Erro de autenticação
- ✅ Limpe o localStorage: `localStorage.clear()`
- ✅ Verifique as credenciais
- ✅ Reinicie o backend

---

## 📚 Próximos Passos

1. **Personalizar Interface**
   - Edite `frontend/src/components/`
   - Modifique cores em `tailwind.config.js`

2. **Adicionar Skills**
   - Crie novas skills em `core/skills/`
   - Registre no orchestrator

3. **Integrar Telegram**
   - Configure token em `config/config.json`
   - Execute `python interfaces/telegram/bot.py`

4. **Deploy**
   - Build do frontend: `npm run build`
   - Configure servidor (Nginx, Apache, etc.)
   - Use gunicorn/uvicorn para backend

---

## 🎉 Pronto!

Seu sistema OpenCngsm MCP v2.0 está funcionando!

- **Backend:** http://127.0.0.1:18789
- **Frontend:** http://localhost:5173
- **Docs API:** http://127.0.0.1:18789/docs

**Divirta-se! 🚀**
