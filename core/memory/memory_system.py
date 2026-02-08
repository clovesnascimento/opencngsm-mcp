"""
Memory System - Context Management
"""
from typing import Dict, Any, List
from datetime import datetime
import json

class MemorySystem:
    def __init__(self):
        self.short_term = {}
        self.long_term = {}
        
    def store(self, key: str, value: Any, memory_type: str = "short"):
        """Store information in memory"""
        timestamp = datetime.now().isoformat()
        
        if memory_type == "short":
            self.short_term[key] = {"value": value, "timestamp": timestamp}
        else:
            self.long_term[key] = {"value": value, "timestamp": timestamp}
    
    def retrieve(self, key: str, memory_type: str = "short") -> Any:
        """Retrieve information from memory"""
        memory = self.short_term if memory_type == "short" else self.long_term
        return memory.get(key, {}).get("value")
    
    def clear_short_term(self):
        """Clear short-term memory"""
        self.short_term = {}
