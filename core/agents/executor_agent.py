"""
OpenCngsm v3.3 - Executor Agent
Agente de execução com permissões elevadas (alto privilégio)

RESPONSABILIDADES:
- Executar planos aprovados
- Acessar credenciais
- Executar skills

RESTRIÇÕES:
- NÃO processa inputs diretos do usuário
- Apenas executa planos pré-aprovados
"""
import logging
from pathlib import Path
from typing import Optional
import asyncio

from core.security.credential_manager import CredentialManager
from core.sandbox.docker_runner import DockerRunner
from core.agents.models import Action, ActionPlan, ExecutionResult, ActionType

logger = logging.getLogger(__name__)


class ExecutorAgent:
    """
    Agente de execução com permissões elevadas
    
    Features:
    - Executa planos aprovados
    - Acessa credenciais criptografadas
    - Executa skills em sandbox
    - NÃO processa inputs diretos
    
    Example:
        executor = ExecutorAgent(config_dir)
        result = await executor.execute_plan(plan, approved=True)
    """
    
    def __init__(self, config_dir: Path, workspace_path: Path):
        """
        Initialize Executor Agent
        
        Args:
            config_dir: Diretório de configuração
            workspace_path: Caminho do workspace
        """
        self.config_dir = Path(config_dir)
        self.workspace_path = Path(workspace_path)
        self.cred_manager = CredentialManager(config_dir)
        self.sandbox = DockerRunner()
        self.credentials_unlocked = False
        
        logger.info(f"✅ Executor Agent inicializado")
    
    async def execute_plan(
        self,
        plan: ActionPlan,
        approved: bool = False,
        password: Optional[str] = None
    ) -> ExecutionResult:
        """
        Executa plano de ação aprovado
        
        Args:
            plan: Plano de ação
            approved: Se True, plano foi aprovado pelo usuário
            password: Senha para desbloquear credenciais
        
        Returns:
            ExecutionResult com resultados
        
        Raises:
            SecurityException: Se plano não foi aprovado
        """
        logger.info(f"⚙️ Executor Agent executando plano: {plan.id}")
        
        # Verificar aprovação
        if plan.requires_approval and not approved:
            raise SecurityException("Plan requires user approval")
        
        results = []
        success = True
        error = None
        
        try:
            # Desbloquear credenciais se necessário
            if password and self._plan_needs_credentials(plan):
                self.cred_manager.unlock(password)
                self.credentials_unlocked = True
                logger.info("🔓 Credenciais desbloqueadas")
            
            # Executar cada ação
            for i, action in enumerate(plan.actions):
                logger.info(f"   Executando ação {i+1}/{len(plan.actions)}: {action.type.value}")
                
                try:
                    result = await self._execute_action(action)
                    results.append({
                        'action': action.type.value,
                        'success': True,
                        'result': result
                    })
                except Exception as e:
                    logger.error(f"   ❌ Erro na ação {i+1}: {e}")
                    results.append({
                        'action': action.type.value,
                        'success': False,
                        'error': str(e)
                    })
                    success = False
                    error = f"Action {i+1} failed: {e}"
                    break
        
        finally:
            # Bloquear credenciais
            if self.credentials_unlocked:
                self.cred_manager.lock()
                self.credentials_unlocked = False
                logger.info("🔒 Credenciais bloqueadas")
        
        # Criar resultado
        execution_result = ExecutionResult(
            plan_id=plan.id,
            success=success,
            results=results,
            error=error
        )
        
        if success:
            logger.info(f"✅ Plano executado com sucesso: {len(results)} ações")
        else:
            logger.error(f"❌ Plano falhou: {error}")
        
        return execution_result
    
    def _plan_needs_credentials(self, plan: ActionPlan) -> bool:
        """Verifica se plano precisa de credenciais"""
        credential_actions = [
            ActionType.SEND_MESSAGE,
            ActionType.SEND_EMAIL,
            ActionType.RUN_SKILL,
            ActionType.ACCESS_CREDENTIALS
        ]
        
        return any(action.type in credential_actions for action in plan.actions)
    
    async def _execute_action(self, action: Action) -> dict:
        """
        Executa ação individual
        
        Args:
            action: Ação a executar
        
        Returns:
            Resultado da ação
        """
        if action.type == ActionType.SEND_MESSAGE:
            return await self._send_message(action)
        
        elif action.type == ActionType.WRITE_FILE:
            return self._write_file(action)
        
        elif action.type == ActionType.READ_FILE:
            return self._read_file(action)
        
        elif action.type == ActionType.LIST_FILES:
            return self._list_files(action)
        
        elif action.type == ActionType.RUN_SKILL:
            return await self._run_skill(action)
        
        else:
            raise NotImplementedError(f"Action type not implemented: {action.type.value}")
    
    async def _send_message(self, action: Action) -> dict:
        """Envia mensagem via skill"""
        service = action.service or 'telegram'
        
        # Recuperar credenciais
        if not self.credentials_unlocked:
            raise SecurityException("Credentials not unlocked")
        
        creds = self.cred_manager.get_credential(service)
        if not creds:
            raise ValueError(f"Credentials not found for service: {service}")
        
        # Executar skill em sandbox
        result = await self.sandbox.run_skill(
            skill_name=service,
            action='send_message',
            args=action.args,
            network_mode='bridge',  # Necessário para enviar mensagem
            workspace_access='none'
        )
        
        return result
    
    def _write_file(self, action: Action) -> dict:
        """Escreve arquivo no workspace"""
        file_path = action.args.get('path')
        content = action.args.get('content')
        
        if not file_path or content is None:
            raise ValueError("Missing 'path' or 'content' in args")
        
        # Validar path
        full_path = (self.workspace_path / file_path).resolve()
        
        if not str(full_path).startswith(str(self.workspace_path.resolve())):
            raise SecurityException("Path traversal attempt detected")
        
        # Escrever arquivo
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        
        logger.info(f"✍️ Arquivo escrito: {file_path}")
        
        return {'path': file_path, 'size': len(content)}
    
    def _read_file(self, action: Action) -> dict:
        """Lê arquivo do workspace"""
        file_path = action.args.get('path')
        
        if not file_path:
            raise ValueError("Missing 'path' in args")
        
        # Validar path
        full_path = (self.workspace_path / file_path).resolve()
        
        if not str(full_path).startswith(str(self.workspace_path.resolve())):
            raise SecurityException("Path traversal attempt detected")
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Ler arquivo
        content = full_path.read_text()
        
        logger.info(f"📖 Arquivo lido: {file_path}")
        
        return {'path': file_path, 'content': content}
    
    def _list_files(self, action: Action) -> dict:
        """Lista arquivos do workspace"""
        directory = action.args.get('path', '.')
        
        # Validar path
        full_path = (self.workspace_path / directory).resolve()
        
        if not str(full_path).startswith(str(self.workspace_path.resolve())):
            raise SecurityException("Path traversal attempt detected")
        
        if not full_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Listar arquivos
        files = [f.name for f in full_path.iterdir()]
        
        logger.info(f"📂 Arquivos listados: {len(files)} itens")
        
        return {'path': directory, 'files': files}
    
    async def _run_skill(self, action: Action) -> dict:
        """Executa skill em sandbox"""
        skill_name = action.args.get('skill_name')
        skill_action = action.args.get('action')
        skill_args = action.args.get('args', {})
        
        if not skill_name or not skill_action:
            raise ValueError("Missing 'skill_name' or 'action' in args")
        
        # Executar skill
        result = await self.sandbox.run_skill(
            skill_name=skill_name,
            action=skill_action,
            args=skill_args,
            network_mode='bridge',
            workspace_access='ro'
        )
        
        return result


class SecurityException(Exception):
    """Exceção de segurança"""
    pass


# Example usage
if __name__ == "__main__":
    async def main():
        # Criar diretórios de teste
        config_dir = Path("/tmp/opencngsm_config")
        workspace = Path("/tmp/opencngsm_workspace")
        config_dir.mkdir(exist_ok=True)
        workspace.mkdir(exist_ok=True)
        
        # Criar Executor Agent
        executor = ExecutorAgent(config_dir, workspace)
        
        print("=" * 60)
        print("⚙️ Executor Agent - Teste")
        print("=" * 60)
        
        # Criar plano de teste
        from core.agents.models import Action, ActionPlan, ActionType
        
        plan = ActionPlan(
            id="test-plan-1",
            description="Teste de execução",
            actions=[
                Action(
                    type=ActionType.WRITE_FILE,
                    description="Escrever arquivo de teste",
                    args={'path': 'test.txt', 'content': 'Hello World!'}
                ),
                Action(
                    type=ActionType.READ_FILE,
                    description="Ler arquivo de teste",
                    args={'path': 'test.txt'}
                ),
                Action(
                    type=ActionType.LIST_FILES,
                    description="Listar arquivos",
                    args={'path': '.'}
                )
            ]
        )
        
        # Executar plano
        print(f"\n⚙️ Executando plano: {plan.description}")
        result = await executor.execute_plan(plan, approved=True)
        
        print(f"\n📊 Resultado:")
        print(f"   Sucesso: {result.success}")
        print(f"   Ações executadas: {len(result.results)}")
        
        for i, action_result in enumerate(result.results):
            status = "✅" if action_result['success'] else "❌"
            print(f"   {status} Ação {i+1}: {action_result['action']}")
        
        print("\n✅ Teste completo!")
    
    asyncio.run(main())
