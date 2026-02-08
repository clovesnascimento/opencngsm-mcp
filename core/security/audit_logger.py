"""
OpenCngsm v3.2 - Audit Logger
Logging seguro de eventos sem expor credenciais
"""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Logger de auditoria que NÃO expõe credenciais
    
    Features:
    - Mascaramento automático de dados sensíveis
    - Logging estruturado (JSON)
    - Rotação de logs
    - Níveis de severidade
    - Timestamps precisos
    - Contexto de usuário/sessão
    
    Example:
        audit = AuditLogger(log_dir)
        
        audit.log_event('user_login', {
            'user_id': '123',
            'ip': '192.168.1.1',
            'api_key': 'sk-secret'  # Será mascarado
        })
    """
    
    # Chaves sensíveis que devem ser mascaradas
    SENSITIVE_KEYS = [
        'api_key', 'apikey', 'api-key',
        'token', 'auth_token', 'access_token',
        'password', 'passwd', 'pwd',
        'secret', 'secret_key',
        'bot_token',
        'private_key',
        'credential', 'credentials',
    ]
    
    # Padrões de dados sensíveis (regex)
    SENSITIVE_PATTERNS = [
        r'sk-[a-zA-Z0-9]{48}',  # OpenAI keys
        r'sk-ant-[a-zA-Z0-9-]{95}',  # Anthropic keys
        r'[0-9]{8,10}:[a-zA-Z0-9_-]{35}',  # Telegram bot tokens
        r'AIza[a-zA-Z0-9_-]{35}',  # Google API keys
    ]
    
    def __init__(
        self,
        log_dir: Path,
        log_file: str = 'audit.log',
        max_file_size: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5
    ):
        """
        Initialize audit logger
        
        Args:
            log_dir: Diretório de logs
            log_file: Nome do arquivo de log
            max_file_size: Tamanho máximo do arquivo (bytes)
            backup_count: Número de backups a manter
        """
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / log_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Criar diretório se não existir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar logger
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        # Handler de arquivo com rotação
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(
            self.log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        
        # Formato JSON
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        
        logger.info(f"✅ Audit logger inicializado: {self.log_file}")
    
    def log_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str = 'INFO',
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """
        Loga evento de segurança
        
        Args:
            event_type: Tipo de evento (ex: 'user_login', 'api_call')
            details: Detalhes do evento
            severity: Nível de severidade (INFO, WARNING, ERROR, CRITICAL)
            user_id: ID do usuário
            session_id: ID da sessão
        """
        # Mascarar dados sensíveis
        safe_details = self._mask_sensitive(details)
        
        # Criar entrada de log
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': safe_details,
        }
        
        # Adicionar contexto opcional
        if user_id:
            entry['user_id'] = user_id
        if session_id:
            entry['session_id'] = session_id
        
        # Logar como JSON
        log_line = json.dumps(entry, ensure_ascii=False)
        
        # Escolher nível de log
        if severity == 'CRITICAL':
            self.logger.critical(log_line)
        elif severity == 'ERROR':
            self.logger.error(log_line)
        elif severity == 'WARNING':
            self.logger.warning(log_line)
        else:
            self.logger.info(log_line)
    
    def _mask_sensitive(self, data: Any) -> Any:
        """
        Mascara dados sensíveis recursivamente
        
        Args:
            data: Dados a serem mascarados
        
        Returns:
            Dados mascarados
        """
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                # Verificar se chave é sensível
                if any(s in key.lower() for s in self.SENSITIVE_KEYS):
                    masked[key] = self._mask_string(str(value))
                else:
                    # Recursão para valores aninhados
                    masked[key] = self._mask_sensitive(value)
            return masked
        
        elif isinstance(data, list):
            return [self._mask_sensitive(item) for item in data]
        
        elif isinstance(data, str):
            # Verificar padrões sensíveis
            return self._mask_patterns(data)
        
        else:
            return data
    
    def _mask_string(self, s: str) -> str:
        """
        Mascara string (mostra apenas 4 primeiros e 4 últimos)
        
        Args:
            s: String a ser mascarada
        
        Returns:
            String mascarada
        """
        if len(s) < 8:
            return '••••••••'
        
        return f"{s[:4]}{'•' * (len(s) - 8)}{s[-4:]}"
    
    def _mask_patterns(self, text: str) -> str:
        """
        Mascara padrões sensíveis em texto
        
        Args:
            text: Texto a ser mascarado
        
        Returns:
            Texto mascarado
        """
        masked = text
        
        for pattern in self.SENSITIVE_PATTERNS:
            masked = re.sub(pattern, '[REDACTED]', masked)
        
        return masked
    
    def log_security_event(
        self,
        event_type: str,
        threat_level: str,
        details: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """
        Loga evento de segurança específico
        
        Args:
            event_type: Tipo de evento (ex: 'prompt_injection', 'rate_limit')
            threat_level: Nível de ameaça (LOW, MEDIUM, HIGH, CRITICAL)
            details: Detalhes do evento
            user_id: ID do usuário
        """
        # Mapear threat_level para severity
        severity_map = {
            'LOW': 'INFO',
            'MEDIUM': 'WARNING',
            'HIGH': 'ERROR',
            'CRITICAL': 'CRITICAL'
        }
        
        severity = severity_map.get(threat_level, 'WARNING')
        
        # Adicionar threat_level aos detalhes
        enhanced_details = {
            'threat_level': threat_level,
            **details
        }
        
        self.log_event(
            event_type=f"security.{event_type}",
            details=enhanced_details,
            severity=severity,
            user_id=user_id
        )
    
    def log_api_call(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        user_id: Optional[str] = None,
        duration_ms: Optional[float] = None
    ):
        """
        Loga chamada de API
        
        Args:
            endpoint: Endpoint chamado
            method: Método HTTP
            status_code: Código de status
            user_id: ID do usuário
            duration_ms: Duração em milissegundos
        """
        details = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
        }
        
        if duration_ms is not None:
            details['duration_ms'] = duration_ms
        
        # Determinar severity baseado no status code
        if status_code >= 500:
            severity = 'ERROR'
        elif status_code >= 400:
            severity = 'WARNING'
        else:
            severity = 'INFO'
        
        self.log_event(
            event_type='api_call',
            details=details,
            severity=severity,
            user_id=user_id
        )
    
    def get_recent_events(
        self,
        count: int = 100,
        event_type: Optional[str] = None
    ) -> list:
        """
        Retorna eventos recentes
        
        Args:
            count: Número de eventos
            event_type: Filtrar por tipo de evento
        
        Returns:
            Lista de eventos
        """
        events = []
        
        if not self.log_file.exists():
            return events
        
        # Ler arquivo de log
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Processar linhas (mais recentes primeiro)
        for line in reversed(lines[-count:]):
            try:
                event = json.loads(line.strip())
                
                # Filtrar por tipo se especificado
                if event_type and event.get('event_type') != event_type:
                    continue
                
                events.append(event)
            except json.JSONDecodeError:
                continue
        
        return events


# Singleton global
_global_audit_logger = None


def get_audit_logger(log_dir: Path) -> AuditLogger:
    """
    Retorna instância global do audit logger
    
    Args:
        log_dir: Diretório de logs
    
    Returns:
        AuditLogger instance
    """
    global _global_audit_logger
    if _global_audit_logger is None:
        _global_audit_logger = AuditLogger(log_dir)
    return _global_audit_logger


# Example usage
if __name__ == "__main__":
    # Criar logger
    log_dir = Path.home() / '.opencngsm' / 'logs'
    audit = AuditLogger(log_dir)
    
    print("=" * 60)
    print("📝 Audit Logger - Teste")
    print("=" * 60)
    
    # Teste 1: Log normal
    print("\n✅ Teste 1: Log normal")
    audit.log_event('user_login', {
        'user_id': '123',
        'ip': '192.168.1.1'
    })
    print("   Evento logado!")
    
    # Teste 2: Log com credenciais (serão mascaradas)
    print("\n✅ Teste 2: Log com credenciais (mascaradas)")
    audit.log_event('api_call', {
        'endpoint': '/telegram/send',
        'api_key': 'sk-proj-xxxxxxxxxxxxxxxxxxxxx',
        'bot_token': '123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'
    })
    print("   Credenciais mascaradas!")
    
    # Teste 3: Log de segurança
    print("\n✅ Teste 3: Log de segurança")
    audit.log_security_event(
        event_type='prompt_injection',
        threat_level='HIGH',
        details={
            'pattern': 'ignore instructions',
            'blocked': True
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
        print(f"   - {event['event_type']} ({event['severity']})")
    
    print(f"\n📁 Log file: {audit.log_file}")
    print("\n✅ Teste completo!")
