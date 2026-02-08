"""
Create File Skill - Cria arquivos no sistema
"""

from typing import Dict, Any
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

class CreateFileSkill:
    """Skill para criar arquivos"""
    
    metadata = {
        "name": "create_file",
        "category": "system",
        "description": "Cria ou sobrescreve arquivos",
        "permissions_required": ["file_write"],
        "parameters": {
            "path": {"type": "string", "required": True},
            "content": {"type": "string", "required": True},
            "mode": {"type": "string", "default": "overwrite"}
        }
    }
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """Valida parâmetros"""
        if not params.get("path"):
            raise ValueError("path é obrigatório")
        if not params.get("content"):
            raise ValueError("content é obrigatório")
        return True
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a skill"""
        try:
            self.validate(params)
            
            path = params["path"]
            content = params["content"]
            mode = params.get("mode", "overwrite")
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
            
            # Escrever arquivo
            file_mode = "a" if mode == "append" else "w"
            with open(path, file_mode, encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"[CreateFileSkill] File created: {path}")
            
            return {
                "status": "success",
                "message": f"Arquivo criado: {path}",
                "path": path,
                "size": os.path.getsize(path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[CreateFileSkill] Error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "error_type": type(e).__name__
            }
