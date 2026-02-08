"""
OpenCngsm v3.3 - Action Plan Models
Modelos de dados para planos de ação
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ActionType(Enum):
    """Tipos de ações permitidas"""
    # Ações de leitura (baixo risco)
    READ_FILE = "read_file"
    SEARCH = "search"
    LIST_FILES = "list_files"
    
    # Ações de escrita (médio risco)
    WRITE_FILE = "write_file"
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    
    # Ações de comunicação (médio risco)
    SEND_MESSAGE = "send_message"
    SEND_EMAIL = "send_email"
    
    # Ações de execução (alto risco)
    EXEC_COMMAND = "exec_command"
    RUN_SKILL = "run_skill"
    
    # Ações de credenciais (alto risco)
    ACCESS_CREDENTIALS = "access_credentials"
    MODIFY_CREDENTIALS = "modify_credentials"


class RiskLevel(Enum):
    """Níveis de risco de ações"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Action:
    """
    Ação individual a ser executada
    
    Attributes:
        type: Tipo da ação
        description: Descrição legível
        args: Argumentos da ação
        service: Serviço/skill a usar (opcional)
        risk_level: Nível de risco
    """
    type: ActionType
    description: str
    args: Dict[str, Any]
    service: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    
    def __post_init__(self):
        """Determina nível de risco baseado no tipo"""
        if self.risk_level == RiskLevel.LOW:
            # Auto-determinar risco
            if self.type in [ActionType.READ_FILE, ActionType.SEARCH, ActionType.LIST_FILES]:
                self.risk_level = RiskLevel.LOW
            elif self.type in [ActionType.WRITE_FILE, ActionType.SEND_MESSAGE]:
                self.risk_level = RiskLevel.MEDIUM
            elif self.type in [ActionType.EXEC_COMMAND, ActionType.ACCESS_CREDENTIALS]:
                self.risk_level = RiskLevel.HIGH
            elif self.type == ActionType.MODIFY_CREDENTIALS:
                self.risk_level = RiskLevel.CRITICAL


@dataclass
class ActionPlan:
    """
    Plano de ação completo
    
    Attributes:
        id: ID único do plano
        description: Descrição do objetivo
        actions: Lista de ações
        requires_approval: Se requer aprovação do usuário
        created_at: Timestamp de criação
        approved: Se foi aprovado
        approved_at: Timestamp de aprovação
    """
    id: str
    description: str
    actions: List[Action]
    requires_approval: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    approved: bool = False
    approved_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Determina se requer aprovação baseado nas ações"""
        if not self.requires_approval:
            # Requer aprovação se tiver ações de médio/alto risco
            for action in self.actions:
                if action.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    self.requires_approval = True
                    break
    
    def approve(self):
        """Marca plano como aprovado"""
        self.approved = True
        self.approved_at = datetime.now()
    
    def get_risk_summary(self) -> Dict[str, int]:
        """Retorna resumo de riscos"""
        summary = {
            'low': 0,
            'medium': 0,
            'high': 0,
            'critical': 0
        }
        
        for action in self.actions:
            summary[action.risk_level.value] += 1
        
        return summary


@dataclass
class ExecutionResult:
    """
    Resultado da execução de um plano
    
    Attributes:
        plan_id: ID do plano executado
        success: Se foi bem-sucedido
        results: Resultados de cada ação
        error: Mensagem de erro (se houver)
        executed_at: Timestamp de execução
    """
    plan_id: str
    success: bool
    results: List[Dict[str, Any]]
    error: Optional[str] = None
    executed_at: datetime = field(default_factory=datetime.now)
