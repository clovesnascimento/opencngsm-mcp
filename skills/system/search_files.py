"""
Search Files Skill - Busca arquivos no sistema
"""

from typing import Dict, Any, List
import os
import glob
import logging

logger = logging.getLogger(__name__)

class SearchFilesSkill:
    """Skill para buscar arquivos"""
    
    metadata = {
        "name": "search_files",
        "category": "system",
        "description": "Busca arquivos por padrão",
        "permissions_required": ["file_read"],
        "parameters": {
            "pattern": {"type": "string", "required": True},
            "directory": {"type": "string", "default": "."}
        }
    }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a skill"""
        try:
            pattern = params["pattern"]
            directory = params.get("directory", ".")
            
            search_pattern = os.path.join(directory, pattern)
            files = glob.glob(search_pattern, recursive=True)
            
            logger.info(f"[SearchFilesSkill] Found {len(files)} files")
            
            return {
                "status": "success",
                "files": files,
                "count": len(files)
            }
            
        except Exception as e:
            logger.error(f"[SearchFilesSkill] Error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
