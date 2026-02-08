# 🚀 Guia Rápido - Como Usar o OpenClaw MCP

## 1️⃣ Iniciar o Gateway

```bash
cd openclaw-system
python core/gateway/gateway.py
```

O servidor estará rodando em: **http://127.0.0.1:18789**

---

## 2️⃣ Testar a API (3 formas)

### Opção A: Swagger UI (Mais Fácil) 🌟

1. Abra no navegador: **http://127.0.0.1:18789/docs**
2. Você verá uma interface interativa com todos os endpoints
3. Clique em qualquer endpoint para testar

**Exemplo - Testar Status:**
- Clique em `GET /api/v1/status`
- Clique em "Try it out"
- Clique em "Execute"
- Veja a resposta!

### Opção B: cURL (Terminal)

```bash
# 1. Verificar status
curl http://127.0.0.1:18789/api/v1/status

# 2. Gerar token de autenticação
curl -X POST http://127.0.0.1:18789/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "meu-usuario", "secret": "openclaw-demo-secret"}'

# Copie o "access_token" da resposta

# 3. Enviar mensagem (substitua SEU_TOKEN pelo token copiado)
curl -X POST http://127.0.0.1:18789/api/v1/message \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Crie um arquivo teste.txt com conteúdo Hello World", "user_id": "meu-usuario"}'
```

### Opção C: Python Script

Crie um arquivo `testar_api.py`:

```python
import requests
import json

# URL base
BASE_URL = "http://127.0.0.1:18789/api/v1"

# 1. Gerar token
auth_response = requests.post(
    f"{BASE_URL}/auth/token",
    json={"user_id": "teste", "secret": "openclaw-demo-secret"}
)
token = auth_response.json()["access_token"]
print(f"✅ Token obtido: {token[:20]}...")

# 2. Enviar mensagem
headers = {"Authorization": f"Bearer {token}"}
message_response = requests.post(
    f"{BASE_URL}/message",
    headers=headers,
    json={
        "message": "Crie um arquivo hello.txt com Hello World",
        "user_id": "teste"
    }
)

print("\n📨 Resposta:")
print(json.dumps(message_response.json(), indent=2, ensure_ascii=False))
```

Execute:
```bash
python testar_api.py
```

---

## 3️⃣ Usar o Bot Telegram (Opcional)

### Configuração:

1. **Obter token do bot:**
   - Abra o Telegram
   - Procure por `@BotFather`
   - Envie `/newbot`
   - Siga as instruções
   - Copie o token

2. **Obter seu User ID:**
   - Procure por `@userinfobot` no Telegram
   - Envie `/start`
   - Copie seu User ID

3. **Configurar .env:**
   ```bash
   cp .env.example .env
   nano .env  # ou use seu editor favorito
   ```
   
   Adicione:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABC-DEF...
   TELEGRAM_ALLOWED_USERS=123456789
   ```

4. **Iniciar bot:**
   ```bash
   python interfaces/telegram/bot.py
   ```

5. **Usar no Telegram:**
   - Procure seu bot no Telegram
   - Envie `/start`
   - Envie comandos naturais:
     - "Crie um arquivo teste.txt"
     - "Leia o arquivo teste.txt"
     - "Execute o comando ls"

---

## 4️⃣ Usar o Web Dashboard (Opcional)

```bash
python interfaces/web/dashboard/app.py
```

Acesse: **http://127.0.0.1:8080**

Interface web com:
- Chat interativo
- Estatísticas do sistema
- Histórico de mensagens

---

## 5️⃣ Exemplos de Comandos

O sistema entende linguagem natural. Exemplos:

### Criar Arquivo
```
"Crie um arquivo notas.txt com o conteúdo: Lembrar de estudar Python"
```

### Ler Arquivo
```
"Leia o arquivo notas.txt"
```

### Editar Arquivo
```
"Adicione 'Estudar FastAPI também' ao arquivo notas.txt"
```

### Executar Comando
```
"Execute o comando dir" (Windows)
"Execute o comando ls -la" (Linux/Mac)
```

### Buscar Arquivos
```
"Busque todos os arquivos .txt no diretório atual"
```

### Gerar Texto com IA (requer API key)
```
"Gere um poema sobre programação"
```

---

## 6️⃣ Configurar API Keys (Opcional)

Para usar skills de IA (generate_text, analyze_code, summarize):

1. **Editar .env:**
   ```bash
   nano .env
   ```

2. **Adicionar chaves:**
   ```
   OPENROUTER_API_KEY=sk-or-v1-...
   # ou
   OPENAI_API_KEY=sk-...
   # ou
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **Reiniciar Gateway**

---

## 7️⃣ Estrutura de Resposta da API

Quando você envia uma mensagem, recebe:

```json
{
  "response_id": "resp_1234567890.123",
  "status": "success",
  "message": "Mensagem recebida: 'Crie um arquivo teste.txt'. Sistema em desenvolvimento.",
  "plan": {
    "plan_id": "plan_1234567890.123",
    "tasks": [
      {
        "task_id": "task_1",
        "skill": "create_file",
        "params": {
          "path": "teste.txt",
          "content": "conteúdo"
        }
      }
    ]
  },
  "timestamp": "2026-02-05T21:48:50-03:00"
}
```

---

## 8️⃣ Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Página inicial |
| `/api/v1/status` | GET | Status do sistema |
| `/api/v1/auth/token` | POST | Gerar token JWT |
| `/api/v1/message` | POST | Enviar mensagem |
| `/docs` | GET | Documentação Swagger |
| `/ws` | WebSocket | Conexão em tempo real |

---

## 9️⃣ Permissões

Edite `config/permissions.yaml` para controlar o que cada usuário pode fazer:

```yaml
user_permissions:
  "meu-usuario":
    file_read: allow      # Permitir ler arquivos
    file_write: ask       # Pedir confirmação para escrever
    file_delete: deny     # Negar deletar arquivos
    bash_execute: ask     # Pedir confirmação para comandos
    ia_api: allow         # Permitir usar IA
    external_api: allow   # Permitir APIs externas
```

Opções: `allow`, `deny`, `ask`

---

## 🔟 Troubleshooting Rápido

### Gateway não inicia
```bash
# Verificar se porta está livre
netstat -ano | findstr :18789

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Erro de autenticação
```bash
# Verificar secret no .env
# Secret padrão: "openclaw-demo-secret"
```

### Skills não funcionam
```bash
# Verificar permissões em config/permissions.yaml
# Verificar logs no console do Gateway
```

---

## 📚 Documentação Completa

- **COMO_USAR.md** - Guia detalhado
- **TROUBLESHOOTING.md** - Solução de problemas
- **README.md** - Visão geral
- **Swagger UI** - http://127.0.0.1:18789/docs

---

## 🎯 Fluxo Típico de Uso

```
1. Iniciar Gateway
   ↓
2. Gerar token (via API ou Swagger)
   ↓
3. Enviar mensagem com token
   ↓
4. Sistema analisa mensagem (Planner)
   ↓
5. Seleciona skill apropriada (Decision Engine)
   ↓
6. Executa ação (Skill)
   ↓
7. Retorna resultado
```

---

## ✨ Dicas

- **Use Swagger UI** para explorar a API interativamente
- **Veja os logs** no console do Gateway para debug
- **Configure permissões** antes de usar em produção
- **Teste com cURL** antes de integrar em aplicações
- **Use .env** para secrets, nunca hardcode

---

**Pronto para começar!** 🚀

Inicie o Gateway e acesse http://127.0.0.1:18789/docs para explorar!
