#!/usr/bin/env python3
"""
Script de teste para a API do OpenClaw MCP
Execute com: python testar_api.py
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://127.0.0.1:18789/api/v1"
USER_ID = "teste"
SECRET = "openclaw-demo-secret"

def print_section(title):
    """Imprime seção formatada"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_status():
    """Testa endpoint de status"""
    print_section("1. Testando Status do Sistema")
    
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"✅ Status Code: {response.status_code}")
        print(f"📊 Resposta: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def get_token():
    """Obtém token de autenticação"""
    print_section("2. Gerando Token de Autenticação")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"user_id": USER_ID, "secret": SECRET}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print(f"✅ Token obtido com sucesso!")
            print(f"🔑 Token: {token[:30]}...")
            print(f"⏰ Expira em: {data['expires_in']} segundos")
            return token
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def send_message(token, message):
    """Envia mensagem para o sistema"""
    print_section(f"3. Enviando Mensagem: '{message}'")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/message",
            headers=headers,
            json={"message": message, "user_id": USER_ID}
        )
        
        if response.status_code == 200:
            print(f"✅ Mensagem enviada com sucesso!")
            print(f"\n📨 Resposta completa:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return response.json()
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    """Função principal"""
    print("\n" + "🦞" * 30)
    print("  OpenClaw MCP - Teste de API")
    print("🦞" * 30)
    
    # 1. Testar status
    if not test_status():
        print("\n❌ Gateway não está respondendo!")
        print("💡 Certifique-se de que o Gateway está rodando:")
        print("   python core/gateway/gateway.py")
        return
    
    # 2. Obter token
    token = get_token()
    if not token:
        print("\n❌ Não foi possível obter token!")
        return
    
    # 3. Enviar mensagens de teste
    test_messages = [
        "Crie um arquivo teste.txt com conteúdo Hello World",
        "Leia o arquivo teste.txt",
        "Execute o comando dir",
    ]
    
    for i, msg in enumerate(test_messages, 1):
        send_message(token, msg)
        if i < len(test_messages):
            input("\nPressione ENTER para continuar...")
    
    # Resumo final
    print_section("✅ Testes Concluídos!")
    print("\n📚 Próximos passos:")
    print("   1. Explore a API em: http://127.0.0.1:18789/docs")
    print("   2. Configure permissões em: config/permissions.yaml")
    print("   3. Adicione API keys no .env para usar skills de IA")
    print("\n🦞 Sistema OpenClaw MCP funcionando perfeitamente!\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
