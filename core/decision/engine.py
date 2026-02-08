"""
Decision Engine - Motor de decisão do MCP
Decide QUAL skill usar e QUANDO executar
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Decision:
    """Representa uma decisão de execução"""
    def __init__(self, task: Dict, skill: str, provider: Optional[str] = None, approved: bool = True):
        self.task = task
        self.skill = skill
        self.provider = provider
        self.approved = approved
        self.timestamp = datetime.now().isoformat()

class DecisionEngine:
    """Motor de decisão principal"""
    
    def __init__(self):
        self.skill_registry = self._load_skill_registry()
        self.provider_selector = ProviderSelector()
    
    def _load_skill_registry(self) -> Dict[str, Dict]:
        """Carrega registro de skills disponíveis"""
        return {
            "create_file": {
                "module": "skills.system.create_file",
                "class": "CreateFileSkill",
                "permissions": ["file_write"]
            },
            "read_file": {
                "module": "skills.system.read_file",
                "class": "ReadFileSkill",
                "permissions": ["file_read"]
            },
            "edit_file": {
                "module": "skills.system.edit_file",
                "class": "EditFileSkill",
                "permissions": ["file_write"]
            },
            "execute_command": {
                "module": "skills.system.execute_command",
                "class": "ExecuteCommandSkill",
                "permissions": ["bash_execute"]
            },
            "generate_text": {
                "module": "skills.ia.generate_text",
                "class": "GenerateTextSkill",
                "permissions": ["ia_api"]
            }
        }
    
    async def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa um plano completo
        
        Args:
            plan: Plano de execução
        
        Returns:
            Resultados da execução
        """
        logger.info(f"[Decision Engine] Executing plan: {plan['plan_id']}")
        
        results = []
        
        for task in plan["tasks"]:
            logger.info(f"[Decision Engine] Processing task: {task['task_id']}")
            
            # Selecionar skill
            skill_name = task["skill"]
            skill_info = self.skill_registry.get(skill_name)
            
            if not skill_info:
                logger.error(f"[Decision Engine] Skill not found: {skill_name}")
                results.append({
                    "task_id": task["task_id"],
                    "status": "error",
                    "message": f"Skill '{skill_name}' not found"
                })
                continue
            
            # Verificar permissões (mock)
            if not self._check_permissions(skill_info["permissions"]):
                logger.warning(f"[Decision Engine] Permission denied for skill: {skill_name}")
                results.append({
                    "task_id": task["task_id"],
                    "status": "error",
                    "message": "Permission denied"
                })
                continue
            
            # Selecionar provider (se necessário)
            provider = None
            if "ia_api" in skill_info["permissions"]:
                provider = self.provider_selector.select(task)
                logger.info(f"[Decision Engine] Selected provider: {provider}")
            
            # Executar skill (mock)
            result = await self._execute_skill(skill_name, task["params"], provider)
            results.append(result)
        
        return {
            "plan_id": plan["plan_id"],
            "status": "completed",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_permissions(self, required_permissions: List[str]) -> bool:
        """Verifica permissões (mock)"""
        # Em produção, verificar contra config/permissions.yaml
        return True
    
    async def _execute_skill(self, skill_name: str, params: Dict, provider: Optional[str]) -> Dict:
        """Executa uma skill (mock)"""
        logger.info(f"[Decision Engine] Executing skill: {skill_name}")
        
        # Mock de execução
        return {
            "skill": skill_name,
            "status": "success",
            "message": f"Skill '{skill_name}' executed successfully",
            "params": params,
            "provider": provider
        }

class ProviderSelector:
    """Seleciona o melhor provider de IA para a tarefa"""
    
    def select(self, task: Dict) -> str:
        """Seleciona provider baseado na tarefa"""
        # Lógica de seleção
        if task.get("requires_reasoning"):
            return "deepseek-r1"
        elif task.get("requires_speed"):
            return "claude-haiku"
        elif task.get("requires_quality"):
            return "gpt-4o"
        else:
            return "openrouter"
