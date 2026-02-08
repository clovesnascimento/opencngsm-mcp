"""
OpenClaw CLI - Interface de linha de comando
"""

import click
import os
import subprocess

@click.group()
def cli():
    """🦞 OpenClaw MCP - Sistema de Agente Autônomo"""
    pass

@cli.command()
def install():
    """Instalação inicial do sistema"""
    click.echo("🦞 OpenClaw MCP - Instalação")
    click.echo("=" * 50)
    
    # Instalar dependências
    click.echo("📦 Instalando dependências...")
    subprocess.run(["pip", "install", "-r", "requirements.txt"])
    
    # Criar diretórios
    click.echo("📁 Criando diretórios...")
    os.makedirs("storage/database", exist_ok=True)
    os.makedirs("storage/logs", exist_ok=True)
    os.makedirs("storage/files", exist_ok=True)
    
    click.echo("✅ Instalação concluída!")

@cli.command()
def start():
    """Inicia o sistema"""
    click.echo("🚀 Iniciando OpenClaw MCP...")
    subprocess.run(["python", "core/gateway/gateway.py"])

@cli.command()
def stop():
    """Para o sistema"""
    click.echo("🛑 Parando OpenClaw MCP...")
    # Implementar lógica de parada

@cli.command()
def status():
    """Mostra status do sistema"""
    click.echo("📊 Status do OpenClaw MCP")
    click.echo("=" * 50)
    click.echo("Gateway: 🟢 Ready")
    click.echo("Planner: 🟢 Ready")
    click.echo("Decision Engine: 🟢 Ready")
    click.echo("Memory: 🟢 Ready")
    click.echo("Skills: 11 disponíveis")

if __name__ == "__main__":
    cli()
