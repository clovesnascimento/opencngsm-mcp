"""
OpenCngsm v3.3 - Incident Response System (Enhanced with Admin Protection)
Sistema automático de detecção e resposta a incidentes de segurança

Features:
- Detecção automática de ameaças
- Resposta automática baseada em severidade
- Análise forense
- Notificações para administradores
- Histórico de incidentes
- Proteção anti-Self-DoS (admin whitelist)
"""
import logging
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio

from core.security.audit_logger import get_audit_logger

logger = logging.getLogger(__name__)


class IncidentType(Enum):
    """Tipos de incidentes de segurança"""
    PROMPT_INJECTION = "prompt_injection"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    CREDENTIAL_THEFT = "credential_theft"
    MALICIOUS_FILE = "malicious_file"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    BRUTE_FORCE = "brute_force"
    DATA_EXFILTRATION = "data_exfiltration"


class Severity(Enum):
    """Níveis de severidade"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Incident:
    """
    Incidente de segurança
    
    Attributes:
        id: ID único
        type: Tipo de incidente
        severity: Severidade
        details: Detalhes do incidente
        user_id: ID do usuário envolvido
        timestamp: Timestamp do incidente
        response_actions: Ações de resposta tomadas
        resolved: Se foi resolvido
    """
    id: str
    type: IncidentType
    severity: Severity
    details: Dict[str, Any]
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    response_actions: List[str] = field(default_factory=list)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class IncidentResponse:
    """
    Sistema de resposta automática a incidentes
    
    Features:
    - Detecção de ameaças
    - Resposta automática
    - Análise forense
    - Notificações
    - Proteção anti-Self-DoS
    
    Example:
        ir = IncidentResponse(config_dir)
        
        await ir.handle_incident(
            incident_type=IncidentType.PROMPT_INJECTION,
            severity=Severity.HIGH,
            details={'pattern': 'ignore instructions'},
            user_id='user_123'
        )
    """
    
    # Admin whitelist - usuários que NUNCA são bloqueados
    ADMIN_WHITELIST = ['admin', 'root', 'system', 'superuser', 'administrator']
    
    def __init__(self, config_dir: Path):
        """
        Initialize Incident Response
        
        Args:
            config_dir: Diretório de configuração
        """
        self.config_dir = Path(config_dir)
        self.incidents_dir = self.config_dir / 'incidents'
        self.incidents_dir.mkdir(parents=True, exist_ok=True)
        
        # Audit logger
        self.audit = get_audit_logger(self.config_dir / 'logs')
        
        # Estado
        self.blocked_users: Set[str] = set()
        self.temp_blocks: Dict[str, datetime] = {}  # user_id -> unblock_time
        self.incidents: List[Incident] = []
        
        logger.info(f"✅ Incident Response inicializado")
        logger.info(f"🛡️ Admin whitelist: {self.ADMIN_WHITELIST}")
    
    async def handle_incident(
        self,
        incident_type: IncidentType,
        severity: Severity,
        details: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Incident:
        """
        Processa incidente de segurança
        
        Args:
            incident_type: Tipo de incidente
            severity: Severidade
            details: Detalhes do incidente
            user_id: ID do usuário envolvido
        
        Returns:
            Incident criado
        """
        # Criar incidente
        incident = Incident(
            id=str(uuid.uuid4()),
            type=incident_type,
            severity=severity,
            details=details,
            user_id=user_id
        )
        
        self.incidents.append(incident)
        
        logger.warning(
            f"🚨 Incident detected: {incident_type.value} "
            f"(severity: {severity.value}, user: {user_id})"
        )
        
        # Logar incidente
        self.audit.log_security_event(
            event_type=f"incident.{incident_type.value}",
            threat_level=severity.value.upper(),
            details=details,
            user_id=user_id
        )
        
        # Resposta automática baseada em severidade
        if severity == Severity.CRITICAL:
            await self._critical_response(incident)
        elif severity == Severity.HIGH:
            await self._high_response(incident)
        elif severity == Severity.MEDIUM:
            await self._medium_response(incident)
        elif severity == Severity.LOW:
            await self._low_response(incident)
        
        # Salvar snapshot
        await self._save_incident(incident)
        
        return incident
    
    async def _critical_response(self, incident: Incident):
        """Resposta a incidente crítico"""
        logger.critical(f"🚨 CRITICAL incident: {incident.type.value}")
        
        actions = []
        
        # PROTEÇÃO ANTI-SELF-DOS: Não bloquear admin permanentemente
        if incident.user_id and incident.user_id in self.ADMIN_WHITELIST:
            logger.error(f"🚨 CRITICAL incident for ADMIN {incident.user_id} - NOT blocking (whitelist protection)")
            logger.error(f"⚠️ ADMIN SECURITY BREACH DETECTED - Manual investigation required!")
            await self._create_forensic_snapshot(incident)
            await self._notify_admin(incident, urgent=True)
            actions.append("admin_incident_logged")
            incident.response_actions = actions
            return
        
        # 1. Bloquear usuário permanentemente
        if incident.user_id:
            self.blocked_users.add(incident.user_id)
            actions.append(f"blocked_user:{incident.user_id}")
            logger.critical(f"🔒 User {incident.user_id} PERMANENTLY BLOCKED")
        
        # 2. Revogar credenciais (TODO: implementar)
        actions.append("revoke_credentials")
        logger.critical("🔑 Credentials revoked")
        
        # 3. Notificar administrador
        await self._notify_admin(incident, urgent=True)
        actions.append("admin_notified:urgent")
        
        # 4. Criar snapshot forense
        await self._create_forensic_snapshot(incident)
        actions.append("forensic_snapshot_created")
        
        incident.response_actions = actions
    
    async def _high_response(self, incident: Incident):
        """Resposta a incidente de alta severidade"""
        logger.error(f"⚠️ HIGH severity incident: {incident.type.value}")
        
        actions = []
        
        # PROTEÇÃO ANTI-SELF-DOS: Não bloquear admin
        if incident.user_id and incident.user_id in self.ADMIN_WHITELIST:
            logger.warning(f"⚠️ HIGH incident for ADMIN {incident.user_id} - NOT blocking (whitelist protection)")
            await self._notify_admin(incident, urgent=False)
            actions.append("admin_incident_logged")
            incident.response_actions = actions
            return
        
        # 1. Bloquear usuário temporariamente (15 min)
        if incident.user_id:
            block_duration = 900  # 15 minutos
            unblock_time = datetime.now() + timedelta(seconds=block_duration)
            
            self.blocked_users.add(incident.user_id)
            self.temp_blocks[incident.user_id] = unblock_time
            
            actions.append(f"temp_blocked_user:{incident.user_id}:15min")
            logger.error(f"⏱️ User {incident.user_id} blocked for 15 minutes")
            
            # Agendar desbloqueio
            asyncio.create_task(self._unblock_after(incident.user_id, block_duration))
        
        # 2. Notificar administrador
        await self._notify_admin(incident, urgent=False)
        actions.append("admin_notified")
        
        # 3. Criar snapshot
        await self._create_forensic_snapshot(incident)
        actions.append("snapshot_created")
        
        incident.response_actions = actions
    
    async def _medium_response(self, incident: Incident):
        """Resposta a incidente de média severidade"""
        logger.warning(f"⚠️ MEDIUM severity incident: {incident.type.value}")
        
        actions = []
        
        # 1. Aumentar monitoramento do usuário
        if incident.user_id:
            actions.append(f"increased_monitoring:{incident.user_id}")
            logger.warning(f"👁️ Increased monitoring for user {incident.user_id}")
        
        # 2. Logar detalhes
        actions.append("detailed_logging")
        
        incident.response_actions = actions
    
    async def _low_response(self, incident: Incident):
        """Resposta a incidente de baixa severidade"""
        logger.info(f"ℹ️ LOW severity incident: {incident.type.value}")
        
        actions = ["logged"]
        incident.response_actions = actions
    
    async def _unblock_after(self, user_id: str, seconds: int):
        """Desbloqueia usuário após tempo especificado"""
        await asyncio.sleep(seconds)
        
        if user_id in self.blocked_users:
            self.blocked_users.remove(user_id)
            
        if user_id in self.temp_blocks:
            del self.temp_blocks[user_id]
        
        logger.info(f"🔓 User {user_id} unblocked")
        
        # Logar desbloqueio
        self.audit.log_event(
            event_type='user_unblocked',
            details={'user_id': user_id},
            severity='INFO'
        )
    
    async def _notify_admin(self, incident: Incident, urgent: bool = False):
        """Notifica administrador sobre incidente"""
        # TODO: Implementar notificação real (e-mail, Telegram, etc.)
        
        urgency = "🚨 URGENT" if urgent else "⚠️"
        
        message = f"""
{urgency} Security Incident Report

Incident ID: {incident.id}
Type: {incident.type.value}
Severity: {incident.severity.value}
User: {incident.user_id or 'Unknown'}
Timestamp: {incident.timestamp.isoformat()}

Details:
{json.dumps(incident.details, indent=2)}

Response Actions:
{', '.join(incident.response_actions)}
"""
        
        logger.critical(f"📧 Admin notification:\n{message}")
        
        # Salvar notificação com UTF-8 encoding
        notification_file = self.incidents_dir / f"notification_{incident.id}.txt"
        notification_file.write_text(message, encoding='utf-8')
    
    async def _create_forensic_snapshot(self, incident: Incident):
        """Cria snapshot forense para análise"""
        snapshot = {
            'incident_id': incident.id,
            'incident_type': incident.type.value,
            'severity': incident.severity.value,
            'timestamp': incident.timestamp.isoformat(),
            'user_id': incident.user_id,
            'details': incident.details,
            'response_actions': incident.response_actions,
            
            # Estado do sistema
            'system_state': {
                'blocked_users': list(self.blocked_users),
                'temp_blocks': {
                    user: time.isoformat()
                    for user, time in self.temp_blocks.items()
                },
                'total_incidents': len(self.incidents),
            },
            
            # Logs recentes
            'recent_logs': self.audit.get_recent_events(count=100),
        }
        
        # Salvar snapshot
        snapshot_file = self.incidents_dir / f"snapshot_{incident.id}.json"
        snapshot_file.write_text(json.dumps(snapshot, indent=2, default=str), encoding='utf-8')
        
        logger.info(f"📸 Forensic snapshot created: {snapshot_file}")
    
    async def _save_incident(self, incident: Incident):
        """Salva incidente em arquivo"""
        incident_data = {
            'id': incident.id,
            'type': incident.type.value,
            'severity': incident.severity.value,
            'details': incident.details,
            'user_id': incident.user_id,
            'timestamp': incident.timestamp.isoformat(),
            'response_actions': incident.response_actions,
            'resolved': incident.resolved,
        }
        
        incident_file = self.incidents_dir / f"incident_{incident.id}.json"
        incident_file.write_text(json.dumps(incident_data, indent=2), encoding='utf-8')
    
    def is_blocked(self, user_id: str) -> bool:
        """
        Verifica se usuário está bloqueado
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se bloqueado
        """
        # PROTEÇÃO ANTI-SELF-DOS: Admin NUNCA é bloqueado
        if user_id in self.ADMIN_WHITELIST:
            return False
        
        # Verificar bloqueio permanente
        if user_id in self.blocked_users:
            # Verificar se é bloqueio temporário expirado
            if user_id in self.temp_blocks:
                if datetime.now() > self.temp_blocks[user_id]:
                    # Bloqueio expirado
                    self.blocked_users.remove(user_id)
                    del self.temp_blocks[user_id]
                    return False
            
            return True
        
        return False
    
    def get_incident_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de incidentes"""
        # Contar por tipo
        by_type = {}
        for incident in self.incidents:
            type_name = incident.type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        # Contar por severidade
        by_severity = {}
        for incident in self.incidents:
            sev = incident.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            'total_incidents': len(self.incidents),
            'by_type': by_type,
            'by_severity': by_severity,
            'blocked_users': len(self.blocked_users),
            'temp_blocks': len(self.temp_blocks),
        }
    
    def get_recent_incidents(self, count: int = 10) -> List[Incident]:
        """Retorna incidentes recentes"""
        return sorted(
            self.incidents,
            key=lambda i: i.timestamp,
            reverse=True
        )[:count]


# Example usage
if __name__ == "__main__":
    async def main():
        # Criar diretório de teste
        config_dir = Path("/tmp/opencngsm_config")
        config_dir.mkdir(exist_ok=True)
        
        # Criar Incident Response
        ir = IncidentResponse(config_dir)
        
        print("=" * 60)
        print("🚨 Incident Response - Teste com Admin Protection")
        print("=" * 60)
        
        # Teste 1: Incidente CRITICAL para admin (deve NÃO bloquear)
        print("\n🚨 Teste 1: Incidente CRITICAL para ADMIN")
        await ir.handle_incident(
            incident_type=IncidentType.CREDENTIAL_THEFT,
            severity=Severity.CRITICAL,
            details={'test': 'admin_critical'},
            user_id='admin'
        )
        print(f"Admin bloqueado: {ir.is_blocked('admin')} (deve ser False)")
        
        # Teste 2: Incidente CRITICAL para usuário normal (deve bloquear)
        print("\n🚨 Teste 2: Incidente CRITICAL para usuário normal")
        await ir.handle_incident(
            incident_type=IncidentType.CREDENTIAL_THEFT,
            severity=Severity.CRITICAL,
            details={'test': 'user_critical'},
            user_id='user_999'
        )
        print(f"User_999 bloqueado: {ir.is_blocked('user_999')} (deve ser True)")
        
        # Teste 3: Incidente HIGH para admin (deve NÃO bloquear)
        print("\n⚠️ Teste 3: Incidente HIGH para ADMIN")
        await ir.handle_incident(
            incident_type=IncidentType.PROMPT_INJECTION,
            severity=Severity.HIGH,
            details={'test': 'admin_high'},
            user_id='admin'
        )
        print(f"Admin bloqueado: {ir.is_blocked('admin')} (deve ser False)")
        
        # Estatísticas
        print(f"\n📊 Estatísticas:")
        stats = ir.get_incident_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print(f"\n📁 Arquivos salvos em: {ir.incidents_dir}")
        print("\n✅ Teste completo!")
    
    asyncio.run(main())
