"""
OpenCngsm v3.2 - Security Integration Example (Phase 2)
Demonstra Rate Limiting, Input Validation e Audit Logging
"""
import asyncio
from pathlib import Path

# Importar módulos de segurança (Phase 2)
from core.security.rate_limiter import RateLimiter, get_limiter
from core.security.input_validator import InputValidator, get_validator
from core.security.audit_logger import AuditLogger, get_audit_logger


def example_1_rate_limiting():
    """
    Exemplo 1: Rate Limiting
    """
    print("=" * 60)
    print("🚦 Exemplo 1: Rate Limiting")
    print("=" * 60)
    
    # Criar limiter (5 req/min)
    limiter = RateLimiter(max_requests=5, window_minutes=1)
    
    user_id = "user_123"
    
    # Fazer 7 requisições
    print(f"\n📊 Fazendo 7 requisições (limite: 5):")
    for i in range(1, 8):
        allowed = limiter.check_limit(user_id)
        remaining = limiter.get_remaining(user_id)
        
        if allowed:
            print(f"   ✅ Request {i}: ALLOWED (remaining: {remaining})")
        else:
            print(f"   ❌ Request {i}: BLOCKED (remaining: {remaining})")
    
    # Estatísticas
    print(f"\n📊 Estatísticas:")
    stats = limiter.get_stats()
    print(f"   Total checks: {stats['total_checks']}")
    print(f"   Blocked: {stats['blocked_count']}")
    print(f"   Blocked %: {stats['blocked_percentage']:.1f}%")
    
    print()


def example_2_input_validation():
    """
    Exemplo 2: Input Validation
    """
    print("=" * 60)
    print("🔍 Exemplo 2: Input Validation")
    print("=" * 60)
    
    validator = InputValidator(strict_mode=True)
    
    # Teste 1: Sanitizar HTML/JavaScript
    print("\n✅ Teste 1: Sanitizar HTML/JavaScript")
    dirty = "<script>alert('XSS')</script>Hello <b>World</b>"
    clean = validator.sanitize_text(dirty)
    print(f"   Input:  {dirty}")
    print(f"   Output: {clean}")
    
    # Teste 2: Validar URLs
    print("\n✅ Teste 2: Validar URLs")
    urls = [
        "https://google.com",
        "http://localhost:8000",  # Bloqueado em strict mode
        "ftp://example.com",      # Scheme inválido
    ]
    for url in urls:
        is_valid, error = validator.validate_url(url)
        if is_valid:
            print(f"   ✅ {url}")
        else:
            print(f"   ❌ {url} - {error}")
    
    # Teste 3: Validar API keys
    print("\n✅ Teste 3: Validar API keys")
    keys = [
        ("123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11", "telegram"),
        ("sk-invalid-key", "openai"),
        ("AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI", "google"),
    ]
    for key, provider in keys:
        is_valid, error = validator.validate_api_key(key, provider)
        if is_valid:
            print(f"   ✅ {provider}: VALID")
        else:
            print(f"   ❌ {provider}: {error}")
    
    # Teste 4: Validar e-mails
    print("\n✅ Teste 4: Validar e-mails")
    emails = [
        "user@example.com",
        "invalid-email",
        "test@domain.co.uk"
    ]
    for email in emails:
        is_valid = validator.validate_email(email)
        print(f"   {'✅' if is_valid else '❌'} {email}")
    
    # Teste 5: Sanitizar filenames
    print("\n✅ Teste 5: Sanitizar filenames")
    filenames = [
        "normal_file.txt",
        "../../../etc/passwd",
        "file with spaces.pdf",
        "<script>alert()</script>.txt"
    ]
    for filename in filenames:
        safe = validator.sanitize_filename(filename)
        print(f"   {filename} → {safe}")
    
    print()


def example_3_audit_logging():
    """
    Exemplo 3: Audit Logging
    """
    print("=" * 60)
    print("📝 Exemplo 3: Audit Logging")
    print("=" * 60)
    
    # Criar logger
    log_dir = Path.home() / '.opencngsm' / 'logs'
    audit = AuditLogger(log_dir)
    
    # Teste 1: Log normal
    print("\n✅ Teste 1: Log de evento normal")
    audit.log_event('user_login', {
        'user_id': '123',
        'ip': '192.168.1.1',
        'timestamp': '2024-01-01T12:00:00'
    })
    print("   Evento logado!")
    
    # Teste 2: Log com credenciais (serão mascaradas)
    print("\n✅ Teste 2: Log com credenciais (AUTO-MASCARADAS)")
    audit.log_event('api_call', {
        'endpoint': '/telegram/send',
        'api_key': 'sk-proj-xxxxxxxxxxxxxxxxxxxxx',
        'bot_token': '123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
        'message': 'Hello World'
    })
    print("   ✅ Credenciais mascaradas automaticamente!")
    print("   ✅ Mensagem preservada!")
    
    # Teste 3: Log de segurança
    print("\n✅ Teste 3: Log de evento de segurança")
    audit.log_security_event(
        event_type='prompt_injection',
        threat_level='HIGH',
        details={
            'pattern': 'ignore instructions',
            'blocked': True,
            'user_message': 'Ignore previous instructions and...'
        },
        user_id='user_456'
    )
    print("   Evento de segurança logado!")
    
    # Teste 4: Log de API call
    print("\n✅ Teste 4: Log de API call")
    audit.log_api_call(
        endpoint='/api/chat',
        method='POST',
        status_code=200,
        user_id='user_789',
        duration_ms=123.45
    )
    print("   API call logada!")
    
    # Teste 5: Ler eventos recentes
    print("\n✅ Teste 5: Eventos recentes")
    events = audit.get_recent_events(count=5)
    print(f"   Total de eventos: {len(events)}")
    for event in events:
        severity_icon = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }.get(event['severity'], 'ℹ️')
        print(f"   {severity_icon} {event['event_type']} ({event['severity']})")
    
    print(f"\n📁 Log file: {audit.log_file}")
    print()


def example_4_integrated_security():
    """
    Exemplo 4: Segurança integrada (Rate Limit + Validation + Audit)
    """
    print("=" * 60)
    print("🛡️ Exemplo 4: Segurança Integrada (Phase 2)")
    print("=" * 60)
    
    # Inicializar componentes
    limiter = get_limiter(max_requests=10, window_minutes=1)
    validator = get_validator(strict_mode=True)
    log_dir = Path.home() / '.opencngsm' / 'logs'
    audit = get_audit_logger(log_dir)
    
    # Simular requisição de usuário
    user_id = "user_123"
    user_input = "<script>alert('XSS')</script>Send message to https://google.com"
    
    print(f"\n📥 Requisição do usuário:")
    print(f"   User ID: {user_id}")
    print(f"   Input: {user_input}")
    
    # 1. Rate Limiting
    print(f"\n1️⃣ Verificar rate limit...")
    if not limiter.check_limit(user_id):
        print(f"   ❌ BLOQUEADO: Rate limit excedido")
        
        # Logar bloqueio
        audit.log_security_event(
            event_type='rate_limit_exceeded',
            threat_level='MEDIUM',
            details={'user_id': user_id},
            user_id=user_id
        )
        return
    print(f"   ✅ Rate limit OK")
    
    # 2. Input Validation
    print(f"\n2️⃣ Validar e sanitizar input...")
    clean_input = validator.sanitize_text(user_input)
    print(f"   Input original: {user_input}")
    print(f"   Input sanitizado: {clean_input}")
    
    # Extrair URL
    import re
    urls = re.findall(r'https?://[^\s]+', clean_input)
    if urls:
        print(f"\n   URLs encontradas: {urls}")
        for url in urls:
            is_valid, error = validator.validate_url(url)
            if is_valid:
                print(f"   ✅ URL válida: {url}")
            else:
                print(f"   ❌ URL inválida: {url} - {error}")
                
                # Logar URL inválida
                audit.log_security_event(
                    event_type='invalid_url',
                    threat_level='LOW',
                    details={'url': url, 'error': error},
                    user_id=user_id
                )
    
    # 3. Audit Logging
    print(f"\n3️⃣ Logar evento...")
    audit.log_event(
        event_type='message_processed',
        details={
            'original_input': user_input,
            'sanitized_input': clean_input,
            'urls_found': len(urls)
        },
        user_id=user_id
    )
    print(f"   ✅ Evento logado!")
    
    print(f"\n✅ Requisição processada com segurança!")
    print()


async def main():
    """
    Executar todos os exemplos
    """
    print("\n" + "=" * 60)
    print("🔐 OpenCngsm v3.2 - Exemplos de Segurança (Phase 2)")
    print("=" * 60)
    print()
    
    # Exemplo 1: Rate Limiting
    example_1_rate_limiting()
    
    # Exemplo 2: Input Validation
    example_2_input_validation()
    
    # Exemplo 3: Audit Logging
    example_3_audit_logging()
    
    # Exemplo 4: Segurança Integrada
    example_4_integrated_security()
    
    print("=" * 60)
    print("✅ Todos os exemplos executados!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(main())
