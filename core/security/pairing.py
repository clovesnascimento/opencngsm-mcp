"""
OpenCngsm MCP v3.0 - DM Pairing Policy
Security layer for unknown DM senders
"""
import sqlite3
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PairingManager:
    """
    Manages DM pairing codes and approval flow
    Inspired by OpenClaw's dmPolicy="pairing"
    """
    
    def __init__(self, db_path: str = "data/pairing.db"):
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
            
            # Pairing codes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pairing_codes (
                    code TEXT PRIMARY KEY,
                    channel TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            # Index
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_pairing_codes_expires
                ON pairing_codes(expires_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_pairing_codes_status
                ON pairing_codes(status)
            """)
            
            conn.commit()
            logger.info(f"✅ Pairing database initialized: {self.db_path}")
    
    def generate_code(
        self,
        channel: str,
        user_id: str,
        expiry_hours: int = 24
    ) -> str:
        """
        Generate a 6-digit pairing code
        
        Args:
            channel: Channel name (telegram, whatsapp, etc)
            user_id: User identifier
            expiry_hours: Hours until code expires
        
        Returns:
            6-digit pairing code
        """
        # Generate 6-digit code
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # Calculate expiry
        expires_at = datetime.now() + timedelta(hours=expiry_hours)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO pairing_codes (code, channel, user_id, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (code, channel, user_id, expires_at))
                conn.commit()
                
                logger.info(f"🔑 Pairing code generated: {code} for {channel}:{user_id}")
                return code
        
        except Exception as e:
            logger.error(f"❌ Failed to generate pairing code: {e}")
            return ""
    
    def validate_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Validate a pairing code
        
        Args:
            code: 6-digit pairing code
        
        Returns:
            Pairing info dict or None if invalid
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM pairing_codes
                    WHERE code = ? AND status = 'pending'
                """, (code,))
                
                row = cursor.fetchone()
                
                if not row:
                    logger.warning(f"⚠️  Invalid or already used code: {code}")
                    return None
                
                pairing = dict(row)
                
                # Check expiry
                expires_at = datetime.fromisoformat(pairing['expires_at'])
                if datetime.now() > expires_at:
                    logger.warning(f"⚠️  Expired code: {code}")
                    
                    # Mark as expired
                    cursor.execute("""
                        UPDATE pairing_codes SET status = 'expired'
                        WHERE code = ?
                    """, (code,))
                    conn.commit()
                    
                    return None
                
                return pairing
        
        except Exception as e:
            logger.error(f"❌ Failed to validate code: {e}")
            return None
    
    def approve_code(self, code: str, approved_by: str = "owner") -> bool:
        """
        Approve a pairing code
        
        Args:
            code: 6-digit pairing code
            approved_by: Who approved the code
        
        Returns:
            True if successful, False otherwise
        """
        # Validate code first
        pairing = self.validate_code(code)
        if not pairing:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Mark code as approved
                cursor.execute("""
                    UPDATE pairing_codes SET status = 'approved'
                    WHERE code = ?
                """, (code,))
                
                conn.commit()
                
                logger.info(f"✅ Pairing code approved: {code}")
                return True
        
        except Exception as e:
            logger.error(f"❌ Failed to approve code: {e}")
            return False
    
    def get_pending_codes(self) -> list:
        """Get all pending pairing codes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM pairing_codes
                    WHERE status = 'pending' AND expires_at > datetime('now')
                    ORDER BY created_at DESC
                """)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"❌ Failed to get pending codes: {e}")
            return []
    
    def cleanup_expired_codes(self):
        """Remove expired pairing codes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM pairing_codes
                    WHERE expires_at < datetime('now')
                """)
                
                deleted = cursor.rowcount
                conn.commit()
                
                if deleted > 0:
                    logger.info(f"🧹 Cleaned up {deleted} expired pairing codes")
        
        except Exception as e:
            logger.error(f"❌ Failed to cleanup codes: {e}")


# Singleton instance
pairing_manager = PairingManager()
