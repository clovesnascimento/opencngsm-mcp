#!/bin/bash
# OpenClaw MCP - Run Telegram Bot

echo "🦞 Starting OpenClaw Telegram Bot..."

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Verificar se token está configurado
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN não configurado!"
    echo "Configure a variável de ambiente ou edite .env"
    exit 1
fi

# Rodar bot
python interfaces/telegram/bot.py
