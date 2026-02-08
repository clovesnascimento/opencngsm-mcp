# 🔧 OpenClaw MCP - Troubleshooting Guide

## ✅ Problema Resolvido: Instalação de Dependências

### Problema Original

Ao tentar instalar as dependências com `pip install -r requirements.txt`, você encontrou:

```
ERROR: Cargo, the Rust package manager, is not installed
```

E depois:

```
ModuleNotFoundError: No module named 'jwt'
```

### ✅ Solução Aplicada

Atualizei o `requirements.txt` para usar versões que **NÃO REQUEREM RUST**:

#### Mudanças Principais:

1. **Pydantic**: `2.5.3` → `1.10.12`
   - Pydantic v2 requer Rust para compilar
   - Pydantic v1 é puro Python

2. **FastAPI**: `0.109.0` → `0.88.0`
   - FastAPI 0.88.0 é totalmente compatível com Pydantic v1
   - Versões mais novas requerem Pydantic v2

3. **Uvicorn**: `0.27.0` → `0.20.0`
   - Compatível com FastAPI 0.88.0

4. **httpx**: `0.26.0` → `~0.25.2`
   - Compatível com python-telegram-bot 20.7

5. **PyJWT**: Adicionado `2.8.0`
   - Fornece o módulo `jwt` necessário

6. **Removidos extras**: `[cryptography]`, `[bcrypt]`, `[standard]`
   - Evita dependências que podem requerer compilação

### 📦 Requirements.txt Final (Windows Compatible)

```txt
# Core
fastapi==0.88.0
uvicorn==0.20.0
pydantic==1.10.12
python-multipart==0.0.6

# Auth & Security
PyJWT==2.8.0
python-jose==3.3.0
passlib==1.7.4
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.25
aiosqlite==0.19.0

# Telegram
python-telegram-bot==20.7

# HTTP
httpx~=0.25.2
requests==2.31.0

# Utils
pyyaml==6.0.1
click==8.1.7
rich==13.7.0

# Web Dashboard
jinja2==3.1.3
```

### ✅ Resultado

```bash
pip install -r requirements.txt
# ✅ Todas as dependências instaladas com sucesso!

python core/gateway/gateway.py
# ✅ Gateway rodando em http://127.0.0.1:18789
```

---

## 🚀 Comandos de Instalação (Testados e Funcionando)

```bash
# 1. Atualizar pip
pip install --upgrade pip

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Iniciar Gateway
python core/gateway/gateway.py
```

---

## 🐛 Outros Problemas Comuns

### Problema: "pydantic-settings requires pydantic>=2.7.0"

**Sintoma:**
```
ERROR: pydantic-settings 2.12.0 requires pydantic>=2.7.0, 
but you have pydantic 1.10.12 which is incompatible.
```

**Solução:**
- Este é apenas um **WARNING**, não um erro
- O OpenClaw MCP **NÃO USA** pydantic-settings
- O sistema funciona perfeitamente com este aviso
- Se quiser remover o aviso: `pip uninstall pydantic-settings`

### Problema: "ModuleNotFoundError: No module named 'X'"

**Solução:**
```bash
# Reinstalar todas as dependências
pip install -r requirements.txt --force-reinstall
```

### Problema: "Port 18789 already in use"

**Solução Windows:**
```powershell
# Encontrar processo usando a porta
netstat -ano | findstr :18789

# Matar processo (substitua PID)
taskkill /PID <PID> /F
```

**Solução Linux/Mac:**
```bash
# Encontrar e matar processo
lsof -ti:18789 | xargs kill -9
```

### Problema: Gateway não inicia

**Verificações:**

1. **Python version:**
   ```bash
   python --version
   # Deve ser 3.10+
   ```

2. **Dependências instaladas:**
   ```bash
   pip list | grep -E "fastapi|uvicorn|pydantic|PyJWT"
   ```

3. **Arquivo existe:**
   ```bash
   ls core/gateway/gateway.py
   ```

4. **Permissões:**
   ```bash
   # Windows: não aplicável
   # Linux/Mac:
   chmod +x core/gateway/gateway.py
   ```

---

## 📝 Logs e Debug

### Ver logs do Gateway

O Gateway imprime logs no console:

```
🦞 OpenClaw MCP Gateway
========================================
Starting server on http://127.0.0.1:18789
Docs available at http://127.0.0.1:18789/docs
========================================
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:18789
```

### Testar se está funcionando

```bash
# Status
curl http://127.0.0.1:18789/api/v1/status

# Deve retornar:
# {"status":"online","message":"OpenClaw MCP Gateway is running"}
```

---

## 🎯 Próximos Passos

Agora que o Gateway está funcionando:

### 1. Configurar API Keys (Opcional)

```bash
cp .env.example .env
# Editar .env com suas chaves
```

### 2. Testar API

```bash
# Gerar token
curl -X POST http://127.0.0.1:18789/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "secret": "openclaw-demo-secret"}'

# Enviar mensagem
curl -X POST http://127.0.0.1:18789/api/v1/message \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Crie um arquivo teste.txt", "user_id": "test"}'
```

### 3. Explorar Swagger UI

Acesse: http://127.0.0.1:18789/docs

- Interface interativa
- Teste todos os endpoints
- Veja schemas de request/response

### 4. Configurar Telegram Bot (Opcional)

```bash
# 1. Obter token do @BotFather
# 2. Adicionar ao .env:
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_ALLOWED_USERS=seu_user_id

# 3. Executar bot
python interfaces/telegram/bot.py
```

---

## 📊 Verificação de Saúde do Sistema

### Checklist

- [x] Python 3.10+ instalado
- [x] Todas as dependências instaladas
- [x] Gateway inicia sem erros
- [x] Porta 18789 acessível
- [x] Endpoint /status responde
- [x] Swagger docs acessível

### Comandos de Verificação

```bash
# 1. Versão Python
python --version

# 2. Dependências
pip list | grep -E "fastapi|pydantic|PyJWT"

# 3. Gateway
python core/gateway/gateway.py &
sleep 2
curl http://127.0.0.1:18789/api/v1/status
```

---

## 💡 Dicas

### Performance

- Gateway usa async/await (alta performance)
- SQLite para storage (sem configuração)
- Rate limiting: 60 req/min (configurável)

### Segurança

- JWT tokens expiram em 24h
- Secrets em .env (não versionado)
- Gateway em loopback (127.0.0.1)
- Permissões granulares em config/permissions.yaml

### Desenvolvimento

- Hot reload: `uvicorn core.gateway.gateway:app --reload`
- Logs detalhados: Edite `LOG_LEVEL=DEBUG` no .env
- Swagger UI para testes: http://127.0.0.1:18789/docs

---

## 🆘 Suporte

### Documentação

- `README.md` - Visão geral
- `COMO_USAR.md` - Guia de uso
- `SISTEMA_COMPLETO.md` - Documentação completa
- `walkthrough.md` - Implementação detalhada

### Recursos

- Swagger UI: http://127.0.0.1:18789/docs
- Logs: Console output
- Config: `config/default.yaml`

---

## ✅ Status Final

**Sistema OpenClaw MCP**: 🟢 **FUNCIONANDO**

- ✅ Instalação sem Rust
- ✅ Todas as dependências compatíveis
- ✅ Gateway rodando
- ✅ API acessível
- ✅ Documentação completa

**Versão**: 1.0.0  
**Data**: 2026-02-05  
**Testado em**: Windows (Git Bash)
