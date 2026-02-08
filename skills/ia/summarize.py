"""
Summarize Skill - Resume textos
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SummarizeSkill:
    """Skill para resumir textos"""
    
    metadata = {
        "name": "summarize",
        "category": "ia",
        "description": "Resume textos longos",
        "permissions_required": ["ia_api"],
        "parameters": {
            "text": {"type": "string", "required": True},
            "max_length": {"type": "integer", "default": 200}
        }
    }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a skill"""
        try:
            text = params["text"]
            max_length = params.get("max_length", 200)
            
            # Mock - resumo simples
            summary = text[:max_length] + "..." if len(text) > max_length else text
            
            logger.info(f"[SummarizeSkill] Text summarized")
            
            return {
                "status": "success",
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary)
            }
            
        except Exception as e:
            logger.error(f"[SummarizeSkill] Error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
