"""
Read File Skill - Lê arquivos do sistema
"""

from typing import Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

class ReadFileSkill:
    """Skill para ler arquivos"""
    
    metadata = {
        "name": "read_file",
        "category": "system",
        "description": "Lê conteúdo de arquivos",
        "permissions_required": ["file_read"],
        "parameters": {
            "path": {"type": "string", "required": True}
        }
    }
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """Valida parâmetros"""
        if not params.get("path"):
            raise ValueError("path é obrigatório")
        if not os.path.exists(params["path"]):
            raise FileNotFoundError(f"Arquivo não encontrado: {params['path']}")
        return True
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a skill"""
        try:
            self.validate(params)
            
            path = params["path"]
            
            with open(path, 'r', encoding="utf-8") as f:
                content = f.read()
            
            logger.info(f"[ReadFileSkill] File read: {path}")
            
            return {
                "status": "success",
                "content": content,
                "path": path,
                "size": os.path.getsize(path)
            }
            
        except Exception as e:
            logger.error(f"[ReadFileSkill] Error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "error_type": type(e).__name__
            }
