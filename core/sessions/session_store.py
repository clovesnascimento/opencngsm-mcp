"""
OpenCngsm MCP v3.0 - Session Store
SQLite-based persistence for sessions
"""
import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SessionStore:
    """
    SQLite-based session persistence
    Stores session metadata, messages, and state
    """
    
    def __init__(self, db_path: str = "data/sessions.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    channel TEXT,
                    channel_id TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    sandbox_mode TEXT DEFAULT 'host',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Session messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_messages_session_id
                ON session_messages(session_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_status
                ON sessions(status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_type
                ON sessions(type)
            """)
            
            conn.commit()
            logger.info(f"✅ Database initialized: {self.db_path}")
    
    def create_session(
        self,
        session_id: str,
        session_type: str,
        channel: Optional[str] = None,
        channel_id: Optional[str] = None,
        sandbox_mode: str = "host",
        metadata: Optional[Dict] = None
    ) -> bool:
        """Create a new session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (id, type, channel, channel_id, sandbox_mode, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    session_type,
                    channel,
                    channel_id,
                    sandbox_mode,
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
                logger.info(f"✅ Session created: {session_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
                row = cursor.fetchone()
                
                if row:
                    session = dict(row)
                    if session['metadata']:
                        session['metadata'] = json.loads(session['metadata'])
                    return session
                return None
        except Exception as e:
            logger.error(f"❌ Failed to get session: {e}")
            return None
    
    def update_session(
        self,
        session_id: str,
        status: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Update session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                updates = []
                params = []
                
                if status:
                    updates.append("status = ?")
                    params.append(status)
                
                if metadata:
                    updates.append("metadata = ?")
                    params.append(json.dumps(metadata))
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(session_id)
                
                query = f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()
                
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update session: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                cursor.execute("DELETE FROM session_messages WHERE session_id = ?", (session_id,))
                conn.commit()
                logger.info(f"🗑️  Session deleted: {session_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to delete session: {e}")
            return False
    
    def list_sessions(
        self,
        status: Optional[str] = None,
        session_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List sessions with optional filters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM sessions WHERE 1=1"
                params = []
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                if session_type:
                    query += " AND type = ?"
                    params.append(session_type)
                
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                sessions = []
                for row in rows:
                    session = dict(row)
                    if session['metadata']:
                        session['metadata'] = json.loads(session['metadata'])
                    sessions.append(session)
                
                return sessions
        except Exception as e:
            logger.error(f"❌ Failed to list sessions: {e}")
            return []
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Add message to session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO session_messages (session_id, role, content, metadata)
                    VALUES (?, ?, ?, ?)
                """, (
                    session_id,
                    role,
                    content,
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to add message: {e}")
            return False
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get messages for session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM session_messages WHERE session_id = ? ORDER BY timestamp DESC"
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query, (session_id,))
                rows = cursor.fetchall()
                
                messages = []
                for row in rows:
                    message = dict(row)
                    if message['metadata']:
                        message['metadata'] = json.loads(message['metadata'])
                    messages.append(message)
                
                return list(reversed(messages))  # Return in chronological order
        except Exception as e:
            logger.error(f"❌ Failed to get messages: {e}")
            return []
    
    def get_session_count(self, status: Optional[str] = None) -> int:
        """Get count of sessions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if status:
                    cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = ?", (status,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM sessions")
                
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"❌ Failed to get session count: {e}")
            return 0


# Singleton instance
session_store = SessionStore()
