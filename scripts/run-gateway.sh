#!/bin/bash
# OpenClaw MCP - Run Gateway

echo "🦞 Starting OpenClaw MCP Gateway..."

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Rodar gateway
python core/gateway/gateway.py
