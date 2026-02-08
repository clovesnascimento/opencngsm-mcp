# 📖 Como Usar o OpenClaw MCP

## 1️⃣ Instalação

### Passo 1: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 2: Configurar Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar .env com suas credenciais
nano .env
```

Preencha:
- `OPENROUTER_API_KEY` (obrigatório para IA)
- `TELEGRAM_BOT_TOKEN` (opcional, para bot Telegram)

### Passo 3: Criar Diretórios

```bash
mkdir -p storage/database storage/logs storage/files storage/memory
```

## 2️⃣ Executar o Sistema

### Opção A: Gateway MCP (API)

```bash
python core/gateway/gateway.py
```

Acesse: `http://127.0.0.1:18789`

### Opção B: Bot Telegram

```bash
python interfaces/telegram/bot.py
```

### Opção C: Web Dashboard

```bash
python interfaces/web/dashboard/app.py
```

Acesse: `http://127.0.0.1:8080`

## 3️⃣ Usar via API

### Gerar Token

```bash
curl -X POST http://127.0.0.1:18789/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "seu-id",
    "secret": "openclaw-demo-secret"
  }'
```

Resposta:
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Enviar Mensagem

```bash
curl -X POST http://127.0.0.1:18789/api/v1/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "message": "Crie um arquivo teste.txt com conteúdo Hello World",
    "user_id": "seu-id"
  }'
```

## 4️⃣ Usar via Telegram

1. Configure `TELEGRAM_BOT_TOKEN` no `.env`
2. Adicione seu User ID em `TELEGRAM_ALLOWED_USERS`
3. Execute: `python interfaces/telegram/bot.py`
4. Envie `/start` para o bot
5. Envie comandos naturais

Exemplos:
- "Crie um arquivo hello.txt com Hello World"
- "Leia o arquivo hello.txt"
- "Execute o comando ls -la"

## 5️⃣ Skills Disponíveis

### Sistema
- `create_file`: Criar arquivos
- `read_file`: Ler arquivos
- `edit_file`: Editar arquivos
- `execute_command`: Executar comandos
- `search_files`: Buscar arquivos
- `delete_file`: Deletar arquivos

### IA
- `generate_text`: Gerar texto
- `analyze_code`: Analisar código
- `summarize`: Resumir textos

### API
- `web_search`: Buscar na web
- `weather_api`: Consultar clima

## 6️⃣ Configuração Avançada

### Permissões

Edite `config/permissions.yaml`:

```yaml
user_permissions:
  "seu-user-id":
    file_read: allow
    file_write: allow
    bash_execute: ask
```

### Providers de IA

Edite `config/secrets.yaml`:

```yaml
openrouter:
  api_key: "sk-or-v1-..."

openai:
  api_key: "sk-..."
```

## 7️⃣ Troubleshooting

### Gateway não inicia

```bash
# Verificar se porta 18789 está livre
lsof -i :18789

# Matar processo se necessário
kill -9 <PID>
```

### Bot Telegram não responde

```bash
# Verificar token
echo $TELEGRAM_BOT_TOKEN

# Verificar logs
tail -f storage/logs/openclaw.log
```

### Erro de permissão

```bash
# Verificar permissões em config/permissions.yaml
# Adicionar seu user_id com permissões adequadas
```

## 8️⃣ Próximos Passos

1. Explore a API em `http://127.0.0.1:18789/docs`
2. Crie suas próprias skills em `skills/custom/`
3. Configure permissões personalizadas
4. Integre com seus workflows

---

**Precisa de ajuda?** Consulte a documentação completa ou abra uma issue.
