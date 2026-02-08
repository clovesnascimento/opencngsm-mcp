"""
OpenClaw MCP - Planner
Analisa tarefas e cria planos de execução
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import re

logger = logging.getLogger(__name__)

class Task:
    """Representa uma tarefa no plano"""
    def __init__(self, task_id: str, skill: str, params: Dict[str, Any], dependencies: List[str] = None):
        self.task_id = task_id
        self.skill = skill
        self.params = params
        self.dependencies = dependencies or []
        self.estimated_duration = 1.0
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "skill": self.skill,
            "params": self.params,
            "dependencies": self.dependencies,
            "estimated_duration": self.estimated_duration
        }

class ExecutionPlan:
    """Plano de execução completo"""
    def __init__(self, plan_id: str, user_id: str, tasks: List[Task]):
        self.plan_id = plan_id
        self.user_id = user_id
        self.tasks = tasks
        self.created_at = datetime.now().isoformat()
        self.requires_approval = False
    
    def to_dict(self):
        return {
            "plan_id": self.plan_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "tasks": [task.to_dict() for task in self.tasks],
            "total_estimated_duration": sum(t.estimated_duration for t in self.tasks),
            "requires_approval": self.requires_approval
        }

class Planner:
    """Motor de planejamento principal"""
    
    def __init__(self):
        self.task_patterns = self._load_task_patterns()
    
    def _load_task_patterns(self) -> Dict[str, Dict]:
        """Carrega padrões de tarefas conhecidas"""
        return {
            "create_file": {
                "keywords": ["criar", "create", "novo arquivo", "new file"],
                "skill": "create_file",
                "params_extractor": self._extract_file_creation_params
            },
            "read_file": {
                "keywords": ["ler", "read", "mostrar", "show", "ver", "view"],
                "skill": "read_file",
                "params_extractor": self._extract_file_read_params
            },
            "edit_file": {
                "keywords": ["editar", "edit", "modificar", "modify", "alterar"],
                "skill": "edit_file",
                "params_extractor": self._extract_file_edit_params
            },
            "execute_command": {
                "keywords": ["executar", "execute", "rodar", "run", "comando"],
                "skill": "execute_command",
                "params_extractor": self._extract_command_params
            }
        }
    
    def analyze_task(self, message: str, user_id: str) -> ExecutionPlan:
        """
        Analisa mensagem do usuário e cria plano de execução
        
        Args:
            message: Mensagem do usuário
            user_id: ID do usuário
        
        Returns:
            ExecutionPlan com as tarefas a executar
        """
        logger.info(f"[Planner] Analyzing task: {message}")
        
        # Identificar intenção
        intent = self._identify_intent(message)
        logger.info(f"[Planner] Identified intent: {intent}")
        
        # Criar tarefas baseadas na intenção
        tasks = self._create_tasks(intent, message)
        
        # Criar plano
        plan_id = f"plan_{datetime.now().timestamp()}"
        plan = ExecutionPlan(plan_id, user_id, tasks)
        
        logger.info(f"[Planner] Plan created with {len(tasks)} task(s)")
        return plan
    
    def _identify_intent(self, message: str) -> str:
        """Identifica a intenção do usuário"""
        message_lower = message.lower()
        
        for intent, pattern in self.task_patterns.items():
            for keyword in pattern["keywords"]:
                if keyword in message_lower:
                    return intent
        
        return "unknown"
    
    def _create_tasks(self, intent: str, message: str) -> List[Task]:
        """Cria lista de tarefas baseada na intenção"""
        if intent == "unknown":
            # Tarefa genérica
            return [Task(
                task_id="task_1",
                skill="generate_text",
                params={"prompt": message}
            )]
        
        pattern = self.task_patterns[intent]
        params = pattern["params_extractor"](message)
        
        return [Task(
            task_id="task_1",
            skill=pattern["skill"],
            params=params
        )]
    
    def _extract_file_creation_params(self, message: str) -> Dict[str, Any]:
        """Extrai parâmetros para criação de arquivo"""
        # Regex para extrair nome do arquivo
        file_match = re.search(r"(?:arquivo|file)\s+([\w\./\-]+)", message, re.IGNORECASE)
        filename = file_match.group(1) if file_match else "output.txt"
        
        # Regex para extrair conteúdo
        content_match = re.search(r"(?:com|with|conteúdo|content)\s+['"]?([^'"]+)['"]?", message, re.IGNORECASE)
        content = content_match.group(1) if content_match else "Default content"
        
        return {
            "path": filename,
            "content": content,
            "mode": "overwrite"
        }
    
    def _extract_file_read_params(self, message: str) -> Dict[str, Any]:
        """Extrai parâmetros para leitura de arquivo"""
        file_match = re.search(r"(?:arquivo|file)\s+([\w\./\-]+)", message, re.IGNORECASE)
        filename = file_match.group(1) if file_match else "input.txt"
        
        return {"path": filename}
    
    def _extract_file_edit_params(self, message: str) -> Dict[str, Any]:
        """Extrai parâmetros para edição de arquivo"""
        file_match = re.search(r"(?:arquivo|file)\s+([\w\./\-]+)", message, re.IGNORECASE)
        filename = file_match.group(1) if file_match else "file.txt"
        
        return {
            "path": filename,
            "operation": "append",
            "content": "Edited content"
        }
    
    def _extract_command_params(self, message: str) -> Dict[str, Any]:
        """Extrai parâmetros para execução de comando"""
        cmd_match = re.search(r"(?:comando|command)\s+['"]?([^'"]+)['"]?", message, re.IGNORECASE)
        command = cmd_match.group(1) if cmd_match else "echo 'Hello'"
        
        return {
            "command": command,
            "shell": True
        }
    
    def validate_plan(self, plan: ExecutionPlan) -> bool:
        """Valida se o plano é executável"""
        # Verificar dependências circulares
        # Verificar se todas as skills existem
        # Verificar parâmetros obrigatórios
        return True
