"""
Memory Manager - Gerenciador de memória do sistema
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MemoryManager:
    """Gerencia memória de curto e longo prazo"""
    
    def __init__(self, storage_path: str = "storage/memory"):
        self.storage_path = storage_path
        self.short_term = {}  # Memória de sessão
        self.long_term_path = f"{storage_path}/MEMORY.md"
    
    def store(self, key: str, value: Any, context: str = "short_term"):
        """
        Armazena informação
        
        Args:
            key: Chave de identificação
            value: Valor a armazenar
            context: "short_term" ou "long_term"
        """
        if context == "short_term":
            self.short_term[key] = {
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            logger.info(f"[Memory] Stored in short-term: {key}")
        else:
            self._store_long_term(key, value)
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """
        Busca semântica na memória
        
        Args:
            query: Consulta
            k: Número de resultados
        
        Returns:
            Lista de memórias relevantes
        """
        # Mock - busca simples em short_term
        results = []
        for key, data in self.short_term.items():
            if query.lower() in str(data["value"]).lower():
                results.append({
                    "key": key,
                    "value": data["value"],
                    "timestamp": data["timestamp"],
                    "relevance": 0.9
                })
        
        return results[:k]
    
    def _store_long_term(self, key: str, value: Any):
        """Armazena em memória de longo prazo"""
        # Append to MEMORY.md
        try:
            with open(self.long_term_path, "a", encoding="utf-8") as f:
                f.write(f"\n## {key}\n")
                f.write(f"{value}\n")
                f.write(f"*Stored at: {datetime.now().isoformat()}*\n")
            logger.info(f"[Memory] Stored in long-term: {key}")
        except Exception as e:
            logger.error(f"[Memory] Error storing long-term: {e}")
    
    def update_long_term(self, insights: List[str]):
        """Atualiza MEMORY.md com insights importantes"""
        try:
            with open(self.long_term_path, "a", encoding="utf-8") as f:
                f.write(f"\n## Insights - {datetime.now().date()}\n")
                for insight in insights:
                    f.write(f"- {insight}\n")
            logger.info(f"[Memory] Updated long-term with {len(insights)} insights")
        except Exception as e:
            logger.error(f"[Memory] Error updating long-term: {e}")
