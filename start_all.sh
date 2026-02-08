#!/bin/bash
# OpenClaw MCP - Iniciar Todos os Serviços (Linux/Mac)

echo ""
echo "========================================"
echo "  🦞 OpenClaw MCP - Iniciando Sistema"
echo "========================================"
echo ""

# Verificar se está no diretório correto
if [ ! -f "core/gateway/gateway.py" ]; then
    echo "❌ ERRO: Execute este script dentro do diretório openclaw-system"
    exit 1
fi

# Função para matar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Parando todos os serviços..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "[1/3] 🚀 Iniciando Gateway MCP..."
python core/gateway/gateway.py &
GATEWAY_PID=$!
sleep 3

echo "[2/3] 🌐 Iniciando Web Dashboard..."
python interfaces/web/dashboard/app.py &
WEB_PID=$!
sleep 2

echo "[3/3] 🤖 Iniciando Telegram Bot..."
python interfaces/telegram/bot.py &
BOT_PID=$!

echo ""
echo "========================================"
echo "  ✅ Todos os serviços foram iniciados!"
echo "========================================"
echo ""
echo "  Gateway:       http://127.0.0.1:18789"
echo "  Web Dashboard: http://127.0.0.1:8080"
echo "  Telegram Bot:  Rodando"
echo ""
echo "  Swagger Docs:  http://127.0.0.1:18789/docs"
echo ""
echo "Pressione Ctrl+C para parar todos os serviços"
echo ""

# Aguardar
wait
