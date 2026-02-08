"""
Router - Roteamento de tarefas
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class TaskRouter:
    """Roteia tarefas para os componentes apropriados"""
    
    def route(self, task: Dict[str, Any]) -> str:
        """Determina para onde rotear a tarefa"""
        skill = task.get("skill", "")
        
        if skill.startswith("system"):
            return "system_executor"
        elif skill.startswith("ia"):
            return "ia_executor"
        elif skill.startswith("api"):
            return "api_executor"
        else:
            return "default_executor"
