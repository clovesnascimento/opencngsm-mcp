"""
OpenCngsm MCP v3.0 - Allowlist Management
Manages approved users for DM access
"""
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AllowlistManager:
    """
    Manages allowlist for approved DM users
    Inspired by OpenClaw's allowlist system
    """
    
    def __init__(self, db_path: str = "data/allowlist.db"):
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
            
            # Allowlist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS allowlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_by TEXT,
                    metadata TEXT,
                    UNIQUE(channel, user_id)
                )
            """)
            
            # Index
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_allowlist_channel_user
                ON allowlist(channel, user_id)
            """)
            
            conn.commit()
            logger.info(f"✅ Allowlist database initialized: {self.db_path}")
    
    def add_user(
        self,
        channel: str,
        user_id: str,
        approved_by: str = "owner",
        metadata: Optional[str] = None
    ) -> bool:
        """
        Add user to allowlist
        
        Args:
            channel: Channel name (telegram, whatsapp, etc)
            user_id: User identifier
            approved_by: Who approved the user
            metadata: Additional metadata (JSON string)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO allowlist (channel, user_id, approved_by, metadata)
                    VALUES (?, ?, ?, ?)
                """, (channel, user_id, approved_by, metadata))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"✅ User added to allowlist: {channel}:{user_id}")
                    return True
                else:
                    logger.info(f"ℹ️  User already in allowlist: {channel}:{user_id}")
                    return True
        
        except Exception as e:
            logger.error(f"❌ Failed to add user to allowlist: {e}")
            return False
    
    def remove_user(self, channel: str, user_id: str) -> bool:
        """Remove user from allowlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM allowlist
                    WHERE channel = ? AND user_id = ?
                """, (channel, user_id))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"🗑️  User removed from allowlist: {channel}:{user_id}")
                    return True
                else:
                    logger.warning(f"⚠️  User not found in allowlist: {channel}:{user_id}")
                    return False
        
        except Exception as e:
            logger.error(f"❌ Failed to remove user from allowlist: {e}")
            return False
    
    def is_allowed(self, channel: str, user_id: str) -> bool:
        """Check if user is in allowlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM allowlist
                    WHERE channel = ? AND user_id = ?
                """, (channel, user_id))
                
                count = cursor.fetchone()[0]
                return count > 0
        
        except Exception as e:
            logger.error(f"❌ Failed to check allowlist: {e}")
            return False
    
    def list_users(self, channel: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all allowed users"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if channel:
                    cursor.execute("""
                        SELECT * FROM allowlist
                        WHERE channel = ?
                        ORDER BY approved_at DESC
                    """, (channel,))
                else:
                    cursor.execute("""
                        SELECT * FROM allowlist
                        ORDER BY approved_at DESC
                    """)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"❌ Failed to list allowlist: {e}")
            return []
    
    def get_user_count(self, channel: Optional[str] = None) -> int:
        """Get count of allowed users"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if channel:
                    cursor.execute("""
                        SELECT COUNT(*) FROM allowlist WHERE channel = ?
                    """, (channel,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM allowlist")
                
                return cursor.fetchone()[0]
        
        except Exception as e:
            logger.error(f"❌ Failed to get user count: {e}")
            return 0


# Singleton instance
allowlist_manager = AllowlistManager()
