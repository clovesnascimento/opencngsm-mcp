"""
OpenCngsm v3.0 - Storage Skill
Native Python implementation using shelve and Redis
"""
import shelve
import json
import pickle
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class StorageSkill:
    """
    Persistent key-value storage with TTL support
    
    Features:
    - Key-value storage using shelve (stdlib)
    - TTL (Time To Live) support
    - JSON serialization
    - Export/import functionality
    - Namespace support
    
    Backend: Python shelve (file-based, no external dependencies)
    For production: Consider Redis for better performance
    """
    
    def __init__(
        self,
        db_path: str = 'data/storage.db',
        namespace: str = 'default'
    ):
        """
        Initialize Storage skill
        
        Args:
            db_path: Path to shelve database file
            namespace: Namespace for keys (allows multiple isolated stores)
        """
        self.db_path = db_path
        self.namespace = namespace
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _make_key(self, key: str) -> str:
        """Create namespaced key"""
        return f"{self.namespace}:{key}"
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value with optional TTL
        
        Args:
            key: Storage key
            value: Value to store (any JSON-serializable object)
            ttl: Time to live in seconds (None = no expiration)
        
        Returns:
            True if successful
        
        Example:
            storage = StorageSkill()
            await storage.set('user:123', {'name': 'João', 'age': 25})
            await storage.set('token', 'abc123', ttl=3600)  # Expires in 1 hour
        """
        try:
            with shelve.open(self.db_path) as db:
                data = {
                    'value': value,
                    'timestamp': datetime.now().isoformat(),
                    'ttl': ttl
                }
                db[self._make_key(key)] = data
            
            logger.info(f"✅ Stored {key} (TTL: {ttl}s)" if ttl else f"✅ Stored {key}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to store {key}: {e}")
            return False
    
    async def get(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get value, checking TTL
        
        Args:
            key: Storage key
            default: Default value if key not found or expired
        
        Returns:
            Stored value or default
        
        Example:
            user = await storage.get('user:123')
            token = await storage.get('token', default='')
        """
        try:
            with shelve.open(self.db_path) as db:
                namespaced_key = self._make_key(key)
                
                if namespaced_key not in db:
                    return default
                
                data = db[namespaced_key]
                
                # Check TTL
                if data.get('ttl'):
                    stored_time = datetime.fromisoformat(data['timestamp'])
                    expiry_time = stored_time + timedelta(seconds=data['ttl'])
                    
                    if datetime.now() > expiry_time:
                        # Expired - delete and return default
                        del db[namespaced_key]
                        logger.info(f"🕐 Key {key} expired")
                        return default
                
                return data['value']
        
        except Exception as e:
            logger.error(f"❌ Failed to get {key}: {e}")
            return default
    
    async def delete(self, key: str) -> bool:
        """
        Delete key
        
        Args:
            key: Storage key
        
        Returns:
            True if successful
        """
        try:
            with shelve.open(self.db_path) as db:
                namespaced_key = self._make_key(key)
                if namespaced_key in db:
                    del db[namespaced_key]
                    logger.info(f"✅ Deleted {key}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to delete {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists and is not expired
        
        Args:
            key: Storage key
        
        Returns:
            True if key exists and valid
        """
        value = await self.get(key, default=None)
        return value is not None
    
    async def keys(self, pattern: str = '*') -> List[str]:
        """
        List all keys in namespace
        
        Args:
            pattern: Key pattern (basic wildcard support)
        
        Returns:
            List of keys (without namespace prefix)
        """
        try:
            with shelve.open(self.db_path) as db:
                prefix = f"{self.namespace}:"
                all_keys = [
                    k.replace(prefix, '')
                    for k in db.keys()
                    if k.startswith(prefix)
                ]
                
                # Simple pattern matching
                if pattern != '*':
                    pattern = pattern.replace('*', '')
                    all_keys = [k for k in all_keys if pattern in k]
                
                return all_keys
        
        except Exception as e:
            logger.error(f"❌ Failed to list keys: {e}")
            return []
    
    async def clear(self) -> bool:
        """
        Clear all keys in current namespace
        
        Returns:
            True if successful
        """
        try:
            keys = await self.keys()
            for key in keys:
                await self.delete(key)
            
            logger.info(f"✅ Cleared {len(keys)} keys from namespace {self.namespace}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to clear: {e}")
            return False
    
    async def export(self) -> Dict[str, Any]:
        """
        Export all data in namespace
        
        Returns:
            Dictionary of all key-value pairs
        """
        try:
            data = {}
            keys = await self.keys()
            
            for key in keys:
                value = await self.get(key)
                if value is not None:
                    data[key] = value
            
            logger.info(f"✅ Exported {len(data)} keys")
            return data
        
        except Exception as e:
            logger.error(f"❌ Failed to export: {e}")
            return {}
    
    async def import_data(
        self,
        data: Dict[str, Any],
        overwrite: bool = False
    ) -> int:
        """
        Import data into storage
        
        Args:
            data: Dictionary of key-value pairs
            overwrite: If True, overwrite existing keys
        
        Returns:
            Number of keys imported
        """
        try:
            count = 0
            
            for key, value in data.items():
                if overwrite or not await self.exists(key):
                    await self.set(key, value)
                    count += 1
            
            logger.info(f"✅ Imported {count} keys")
            return count
        
        except Exception as e:
            logger.error(f"❌ Failed to import: {e}")
            return 0
    
    async def increment(
        self,
        key: str,
        amount: int = 1
    ) -> Optional[int]:
        """
        Increment numeric value
        
        Args:
            key: Storage key
            amount: Amount to increment
        
        Returns:
            New value or None if key doesn't exist or isn't numeric
        """
        try:
            current = await self.get(key, default=0)
            
            if not isinstance(current, (int, float)):
                logger.error(f"Key {key} is not numeric")
                return None
            
            new_value = current + amount
            await self.set(key, new_value)
            
            return new_value
        
        except Exception as e:
            logger.error(f"❌ Failed to increment {key}: {e}")
            return None


# Skill metadata
SKILL_NAME = "storage"
SKILL_CLASS = StorageSkill
SKILL_DESCRIPTION = "Persistent key-value storage with TTL support using Python shelve"


# Auto-register
from . import register_skill
register_skill(SKILL_NAME, SKILL_CLASS, SKILL_DESCRIPTION)
