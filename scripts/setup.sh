#!/bin/bash
# OpenClaw MCP - Setup Script

echo "🦞 OpenClaw MCP - Setup"
echo "======================================"

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "🔌 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Criar diretórios
echo "📁 Criando diretórios..."
mkdir -p storage/database
mkdir -p storage/logs
mkdir -p storage/files
mkdir -p storage/memory

# Copiar arquivo de configuração
echo "⚙️ Configurando..."
cp .env.example .env
cp config/secrets.yaml.example config/secrets.yaml

echo ""
echo "✅ Setup concluído!"
echo ""
echo "Próximos passos:"
echo "1. Edite .env com suas configurações"
echo "2. Edite config/secrets.yaml com suas API keys"
echo "3. Execute: python core/gateway/gateway.py"
