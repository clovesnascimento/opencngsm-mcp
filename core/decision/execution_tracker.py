"""
Execution Tracker - Rastreamento de execução
"""

from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ExecutionTracker:
    """Rastreia execução de tarefas"""
    
    def __init__(self):
        self.executions = []
    
    def track_start(self, task_id: str, skill: str):
        """Registra início de execução"""
        execution = {
            "task_id": task_id,
            "skill": skill,
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }
        self.executions.append(execution)
        logger.info(f"[Tracker] Started: {task_id}")
    
    def track_complete(self, task_id: str, result: Dict[str, Any]):
        """Registra conclusão de execução"""
        for execution in self.executions:
            if execution["task_id"] == task_id:
                execution["completed_at"] = datetime.now().isoformat()
                execution["status"] = "completed"
                execution["result"] = result
                logger.info(f"[Tracker] Completed: {task_id}")
                break
    
    def get_status(self, task_id: str) -> Dict[str, Any]:
        """Obtém status de uma tarefa"""
        for execution in self.executions:
            if execution["task_id"] == task_id:
                return execution
        return {}
