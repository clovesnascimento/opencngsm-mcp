"""
Delete File Skill - Remove arquivos
"""

from typing import Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

class DeleteFileSkill:
    """Skill para deletar arquivos"""
    
    metadata = {
        "name": "delete_file",
        "category": "system",
        "description": "Remove arquivos do sistema",
        "permissions_required": ["file_delete"],
        "parameters": {
            "path": {"type": "string", "required": True}
        }
    }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a skill"""
        try:
            path = params["path"]
            
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"[DeleteFileSkill] File deleted: {path}")
                return {
                    "status": "success",
                    "message": f"Arquivo removido: {path}"
                }
            else:
                return {
                    "status": "error",
                    "message": "Arquivo não encontrado"
                }
            
        except Exception as e:
            logger.error(f"[DeleteFileSkill] Error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
