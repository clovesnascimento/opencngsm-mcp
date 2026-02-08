"""
Context Builder - Constrói contexto para execução
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ContextBuilder:
    """Constrói contexto completo para execução de tarefas"""
    
    def build_context(self, user_id: str, message: str, history: List[Dict] = None) -> Dict[str, Any]:
        """Constrói contexto completo"""
        return {
            "user_id": user_id,
            "current_message": message,
            "conversation_history": history or [],
            "user_preferences": self._get_user_preferences(user_id),
            "system_state": self._get_system_state()
        }
    
    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Recupera preferências do usuário"""
        return {
            "language": "pt-BR",
            "timezone": "America/Sao_Paulo"
        }
    
    def _get_system_state(self) -> Dict[str, Any]:
        """Recupera estado atual do sistema"""
        return {
            "available_skills": ["create_file", "read_file", "edit_file"],
            "active_tasks": 0
        }
