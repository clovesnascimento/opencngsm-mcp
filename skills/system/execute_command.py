"""
Execute Command Skill - Executa comandos shell
"""

from typing import Dict, Any
import subprocess
import logging

logger = logging.getLogger(__name__)

class ExecuteCommandSkill:
    """Skill para executar comandos"""
    
    metadata = {
        "name": "execute_command",
        "category": "system",
        "description": "Executa comandos shell",
        "permissions_required": ["bash_execute"],
        "parameters": {
            "command": {"type": "string", "required": True},
            "shell": {"type": "boolean", "default": True}
        }
    }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a skill"""
        try:
            command = params["command"]
            shell = params.get("shell", True)
            
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            logger.info(f"[ExecuteCommandSkill] Command executed: {command}")
            
            return {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except Exception as e:
            logger.error(f"[ExecuteCommandSkill] Error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
