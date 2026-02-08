"""
Storage - Armazenamento persistente
"""

import json
import sqlite3
from typing import Dict, Any, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Storage:
    """Gerencia armazenamento em SQLite"""
    
    def __init__(self, db_path: str = "storage/database/openclaw.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Inicializa banco de dados"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de interações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Tabela de memórias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                context TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("[Storage] Database initialized")
    
    def store_interaction(self, user_id: str, message: str, response: str, metadata: Dict = None):
        """Armazena uma interação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interactions (user_id, message, response, timestamp, metadata)
            VALUES (?, ?, ?, datetime('now'), ?)
        """, (user_id, message, response, json.dumps(metadata or {})))
        
        conn.commit()
        conn.close()
        logger.info(f"[Storage] Interaction stored for user: {user_id}")
    
    def get_interactions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Recupera interações de um usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT message, response, timestamp, metadata
            FROM interactions
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "message": row[0],
                "response": row[1],
                "timestamp": row[2],
                "metadata": json.loads(row[3])
            }
            for row in rows
        ]
