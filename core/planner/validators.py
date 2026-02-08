"""
Validators - Validação de planos e tarefas
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class PlanValidator:
    """Valida planos de execução"""
    
    def validate(self, plan: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Valida um plano
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        # Validar estrutura
        if "tasks" not in plan:
            errors.append("Plan must have 'tasks' field")
        
        # Validar tarefas
        for task in plan.get("tasks", []):
            task_errors = self._validate_task(task)
            errors.extend(task_errors)
        
        return len(errors) == 0, errors
    
    def _validate_task(self, task: Dict[str, Any]) -> List[str]:
        """Valida uma tarefa individual"""
        errors = []
        
        if "skill" not in task:
            errors.append(f"Task {task.get('task_id')} missing 'skill' field")
        
        if "params" not in task:
            errors.append(f"Task {task.get('task_id')} missing 'params' field")
        
        return errors
