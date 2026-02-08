"""
OpenCngsm v3.3 - Approval Gateway
Gateway de aprovação entre Reader e Executor

RESPONSABILIDADES:
- Validar planos de ação
- Determinar se requer aprovação do usuário
- Solicitar aprovação quando necessário
- Logar decisões de aprovação
"""
import logging
from typing import Optional
from datetime import datetime

from core.agents.models import ActionPlan, ActionType, RiskLevel
from core.security.audit_logger import get_audit_logger
from pathlib import Path

logger = logging.getLogger(__name__)


class ApprovalGateway:
    """
    Gateway de aprovação entre Reader e Executor
    
    Features:
    - Valida planos de ação
    - Determina necessidade de aprovação
    - Solicita aprovação do usuário
    - Loga decisões
    
    Example:
        gateway = ApprovalGateway()
        
        if gateway.requires_approval(plan):
            approved = await gateway.request_approval(plan)
        else:
            approved = True
    """
    
    # Ações que sempre requerem aprovação
    REQUIRE_APPROVAL = [
        ActionType.SEND_MESSAGE,
        ActionType.SEND_EMAIL,
        ActionType.MODIFY_FILE,
        ActionType.DELETE_FILE,
        ActionType.EXEC_COMMAND,
        ActionType.ACCESS_CREDENTIALS,
        ActionType.MODIFY_CREDENTIALS,
    ]
    
    # Ações que podem ser auto-aprovadas
    AUTO_APPROVE = [
        ActionType.READ_FILE,
        ActionType.SEARCH,
        ActionType.LIST_FILES,
    ]
    
    def __init__(self, log_dir: Optional[Path] = None, auto_approve_low_risk: bool = True):
        """
        Initialize Approval Gateway
        
        Args:
            log_dir: Diretório de logs (opcional)
            auto_approve_low_risk: Se True, auto-aprova ações de baixo risco
        """
        self.auto_approve_low_risk = auto_approve_low_risk
        self.audit = get_audit_logger(log_dir) if log_dir else None
        self.approval_history = []
        
        logger.info(f"✅ Approval Gateway inicializado (auto_approve_low_risk={auto_approve_low_risk})")
    
    def requires_approval(self, plan: ActionPlan) -> bool:
        """
        Verifica se plano requer aprovação do usuário
        
        Args:
            plan: Plano de ação
        
        Returns:
            True se requer aprovação
        """
        # Verificar se alguma ação requer aprovação
        for action in plan.actions:
            # Ações críticas sempre requerem aprovação
            if action.risk_level == RiskLevel.CRITICAL:
                return True
            
            # Ações de alto risco requerem aprovação
            if action.risk_level == RiskLevel.HIGH:
                return True
            
            # Ações de médio risco requerem aprovação
            if action.risk_level == RiskLevel.MEDIUM:
                return True
            
            # Ações específicas que requerem aprovação
            if action.type in self.REQUIRE_APPROVAL:
                return True
        
        # Se auto-aprovação de baixo risco está desabilitada, sempre requer aprovação
        if not self.auto_approve_low_risk:
            return True
        
        # Caso contrário, não requer aprovação
        return False
    
    async def request_approval(
        self,
        plan: ActionPlan,
        user_id: Optional[str] = None,
        interactive: bool = True
    ) -> bool:
        """
        Solicita aprovação do usuário para o plano
        
        Args:
            plan: Plano de ação
            user_id: ID do usuário
            interactive: Se True, solicita aprovação interativa
        
        Returns:
            True se aprovado, False se rejeitado
        """
        logger.info(f"🔐 Solicitando aprovação para plano: {plan.id}")
        
        # Exibir resumo do plano
        self._display_plan_summary(plan)
        
        # Solicitar aprovação
        if interactive:
            approved = self._request_interactive_approval()
        else:
            # Modo não-interativo: rejeitar por padrão
            approved = False
            logger.warning("⚠️ Modo não-interativo: plano rejeitado por padrão")
        
        # Registrar decisão
        self._log_approval_decision(plan, approved, user_id)
        
        # Marcar plano como aprovado se necessário
        if approved:
            plan.approve()
        
        return approved
    
    def _display_plan_summary(self, plan: ActionPlan):
        """Exibe resumo do plano"""
        print("\n" + "=" * 60)
        print("🔐 APROVAÇÃO NECESSÁRIA")
        print("=" * 60)
        
        print(f"\n📋 Plano: {plan.description}")
        print(f"   ID: {plan.id}")
        print(f"   Criado em: {plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Resumo de riscos
        risk_summary = plan.get_risk_summary()
        print(f"\n📊 Resumo de Riscos:")
        print(f"   🟢 Baixo: {risk_summary['low']}")
        print(f"   🟡 Médio: {risk_summary['medium']}")
        print(f"   🟠 Alto: {risk_summary['high']}")
        print(f"   🔴 Crítico: {risk_summary['critical']}")
        
        # Listar ações
        print(f"\n📝 Ações ({len(plan.actions)}):")
        for i, action in enumerate(plan.actions, 1):
            risk_icon = {
                RiskLevel.LOW: "🟢",
                RiskLevel.MEDIUM: "🟡",
                RiskLevel.HIGH: "🟠",
                RiskLevel.CRITICAL: "🔴"
            }.get(action.risk_level, "⚪")
            
            print(f"   {i}. {risk_icon} {action.type.value}")
            print(f"      {action.description}")
            
            # Exibir argumentos (mascarar dados sensíveis)
            if action.args:
                safe_args = self._mask_sensitive_args(action.args)
                print(f"      Args: {safe_args}")
        
        print("\n" + "=" * 60)
    
    def _mask_sensitive_args(self, args: dict) -> dict:
        """Mascara argumentos sensíveis"""
        sensitive_keys = ['password', 'token', 'api_key', 'secret']
        
        masked = {}
        for key, value in args.items():
            if any(s in key.lower() for s in sensitive_keys):
                masked[key] = "••••••••"
            else:
                # Limitar tamanho de valores longos
                if isinstance(value, str) and len(value) > 50:
                    masked[key] = value[:50] + "..."
                else:
                    masked[key] = value
        
        return masked
    
    def _request_interactive_approval(self) -> bool:
        """Solicita aprovação interativa do usuário"""
        while True:
            response = input("\n❓ Aprovar este plano? (s/n): ").strip().lower()
            
            if response in ['s', 'sim', 'y', 'yes']:
                print("✅ Plano APROVADO")
                return True
            elif response in ['n', 'não', 'nao', 'no']:
                print("❌ Plano REJEITADO")
                return False
            else:
                print("⚠️ Resposta inválida. Use 's' para sim ou 'n' para não.")
    
    def _log_approval_decision(
        self,
        plan: ActionPlan,
        approved: bool,
        user_id: Optional[str] = None
    ):
        """Loga decisão de aprovação"""
        # Registrar no histórico
        decision = {
            'plan_id': plan.id,
            'approved': approved,
            'timestamp': datetime.now(),
            'user_id': user_id,
            'actions_count': len(plan.actions),
            'risk_summary': plan.get_risk_summary()
        }
        
        self.approval_history.append(decision)
        
        # Logar no audit logger
        if self.audit:
            self.audit.log_event(
                event_type='approval_decision',
                details={
                    'plan_id': plan.id,
                    'approved': approved,
                    'actions_count': len(plan.actions),
                    'risk_summary': plan.get_risk_summary()
                },
                severity='INFO' if approved else 'WARNING',
                user_id=user_id
            )
        
        # Logar
        if approved:
            logger.info(f"✅ Plano aprovado: {plan.id}")
        else:
            logger.warning(f"❌ Plano rejeitado: {plan.id}")
    
    def get_approval_stats(self) -> dict:
        """Retorna estatísticas de aprovações"""
        total = len(self.approval_history)
        approved = sum(1 for d in self.approval_history if d['approved'])
        rejected = total - approved
        
        return {
            'total': total,
            'approved': approved,
            'rejected': rejected,
            'approval_rate': (approved / total * 100) if total > 0 else 0
        }


# Example usage
if __name__ == "__main__":
    from core.agents.models import Action, ActionPlan, ActionType, RiskLevel
    
    # Criar gateway
    gateway = ApprovalGateway(auto_approve_low_risk=True)
    
    print("=" * 60)
    print("🔐 Approval Gateway - Teste")
    print("=" * 60)
    
    # Teste 1: Plano de baixo risco (auto-aprovado)
    print("\n✅ Teste 1: Plano de baixo risco")
    low_risk_plan = ActionPlan(
        id="test-1",
        description="Ler arquivos",
        actions=[
            Action(
                type=ActionType.READ_FILE,
                description="Ler arquivo",
                args={'path': 'test.txt'},
                risk_level=RiskLevel.LOW
            )
        ]
    )
    
    requires = gateway.requires_approval(low_risk_plan)
    print(f"   Requer aprovação: {requires}")
    
    # Teste 2: Plano de médio risco (requer aprovação)
    print("\n🟡 Teste 2: Plano de médio risco")
    medium_risk_plan = ActionPlan(
        id="test-2",
        description="Enviar mensagem",
        actions=[
            Action(
                type=ActionType.SEND_MESSAGE,
                description="Enviar mensagem via Telegram",
                args={'text': 'Hello World!'},
                service='telegram',
                risk_level=RiskLevel.MEDIUM
            )
        ]
    )
    
    requires = gateway.requires_approval(medium_risk_plan)
    print(f"   Requer aprovação: {requires}")
    
    # Estatísticas
    print(f"\n📊 Estatísticas:")
    stats = gateway.get_approval_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Teste completo!")
