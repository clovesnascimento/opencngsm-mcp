"""
Edit File Skill - Edita arquivos existentes
"""

from typing import Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

class EditFileSkill:
    """Skill para editar arquivos"""
    
    metadata = {
        "name": "edit_file",
        "category": "system",
        "description": "Edita arquivos existentes",
        "permissions_required": ["file_write"],
        "parameters": {
            "path": {"type": "string", "required": True},
            "operation": {"type": "string", "required": True},
            "content": {"type": "string", "required": True}
        }
    }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a skill"""
        try:
            path = params["path"]
            operation = params["operation"]
            content = params["content"]
            
            if operation == "append":
                with open(path, 'a', encoding="utf-8") as f:
                    f.write(content)
            elif operation == "replace":
                with open(path, 'w', encoding="utf-8") as f:
                    f.write(content)
            
            logger.info(f"[EditFileSkill] File edited: {path}")
            
            return {
                "status": "success",
                "message": f"Arquivo editado: {path}",
                "path": path
            }
            
        except Exception as e:
            logger.error(f"[EditFileSkill] Error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
