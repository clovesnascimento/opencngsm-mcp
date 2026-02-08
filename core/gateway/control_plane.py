"""
OpenCngsm MCP v3.0 - Control Plane
Central coordination for sessions, presence, config, cron, and webhooks
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

from core.orchestrator.orchestrator import CognitiveOrchestrator

logger = logging.getLogger(__name__)


class ControlPlane:
    """
    Control Plane - Unified interface for all gateway operations
    Inspired by OpenClaw's control plane architecture
    """
    
    def __init__(self, gateway):
        self.gateway = gateway
        self.orchestrator = CognitiveOrchestrator()
        
        # Component registries (to be implemented)
        self.sessions = {}  # Will be SessionManager
        self.presence = {}  # Presence tracking
        self.config = {}    # Config management
        self.cron = {}      # Scheduled tasks
        self.webhooks = {}  # Webhook registry
        
        logger.info("Control Plane initialized")
    
    async def handle_user_message(self, client_id: str, payload: dict) -> dict:
        """
        Handle user message and route to appropriate session
        
        Args:
            client_id: WebSocket client ID
            payload: Message payload with 'session_id', 'content', 'metadata'
        
        Returns:
            Response dict with 'content', 'plan', 'metadata'
        """
        try:
            session_id = payload.get("session_id", "main")
            content = payload.get("content", "")
            user_id = payload.get("user_id", client_id)
            metadata = payload.get("metadata", {})
            
            logger.info(f"Processing message for session {session_id}: {content[:50]}...")
            
            # TODO: Route to session manager
            # For now, use orchestrator directly
            result = await self.orchestrator.process_message(content, user_id)
            
            return {
                "session_id": session_id,
                "content": result.get("response", ""),
                "plan": result.get("plan"),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                }
            }
        
        except Exception as e:
            logger.error(f"Error handling user message: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def handle_command(self, client_id: str, payload: dict) -> dict:
        """
        Handle system command
        
        Commands:
            - session.create
            - session.destroy
            - session.list
            - presence.update
            - config.get
            - config.set
            - cron.add
            - cron.list
            - webhook.register
        """
        command = payload.get("command")
        args = payload.get("args", {})
        
        logger.info(f"Executing command: {command}")
        
        try:
            if command == "session.list":
                return await self.list_sessions()
            
            elif command == "session.create":
                return await self.create_session(args)
            
            elif command == "session.destroy":
                return await self.destroy_session(args.get("session_id"))
            
            elif command == "presence.update":
                return await self.update_presence(client_id, args)
            
            elif command == "config.get":
                return await self.get_config(args.get("key"))
            
            elif command == "config.set":
                return await self.set_config(args.get("key"), args.get("value"))
            
            elif command == "status":
                return await self.get_system_status()
            
            else:
                return {
                    "error": f"Unknown command: {command}",
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def list_sessions(self) -> dict:
        """List all active sessions"""
        # TODO: Implement with SessionManager
        return {
            "sessions": [
                {
                    "id": "main",
                    "type": "main",
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
            ],
            "count": 1
        }
    
    async def create_session(self, args: dict) -> dict:
        """Create a new session"""
        # TODO: Implement with SessionManager
        session_id = args.get("session_id", f"session-{datetime.now().timestamp()}")
        session_type = args.get("type", "group")
        
        logger.info(f"Creating session: {session_id} (type: {session_type})")
        
        return {
            "session_id": session_id,
            "type": session_type,
            "status": "created",
            "timestamp": datetime.now().isoformat()
        }
    
    async def destroy_session(self, session_id: str) -> dict:
        """Destroy a session"""
        # TODO: Implement with SessionManager
        logger.info(f"Destroying session: {session_id}")
        
        return {
            "session_id": session_id,
            "status": "destroyed",
            "timestamp": datetime.now().isoformat()
        }
    
    async def update_presence(self, client_id: str, args: dict) -> dict:
        """Update client presence"""
        status = args.get("status", "online")
        self.presence[client_id] = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        
        return {
            "client_id": client_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_config(self, key: Optional[str] = None) -> dict:
        """Get configuration"""
        if key:
            return {
                "key": key,
                "value": self.config.get(key),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "config": self.config,
                "timestamp": datetime.now().isoformat()
            }
    
    async def set_config(self, key: str, value: Any) -> dict:
        """Set configuration"""
        self.config[key] = value
        
        return {
            "key": key,
            "value": value,
            "status": "updated",
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        return {
            "status": "online",
            "version": "3.0.0",
            "gateway": {
                "protocol": "websocket",
                "connections": len(self.gateway.manager.get_connected_clients()),
                "clients": self.gateway.manager.get_connected_clients()
            },
            "sessions": {
                "active": len(self.sessions),
                "total": len(self.sessions)
            },
            "skills": self.orchestrator.get_available_skills(),
            "presence": len(self.presence),
            "timestamp": datetime.now().isoformat()
        }
    
    async def schedule_task(self, cron_expr: str, task: dict) -> dict:
        """Schedule a cron task"""
        # TODO: Implement with CronScheduler
        task_id = f"task-{datetime.now().timestamp()}"
        
        self.cron[task_id] = {
            "cron": cron_expr,
            "task": task,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Scheduled task {task_id}: {cron_expr}")
        
        return {
            "task_id": task_id,
            "cron": cron_expr,
            "status": "scheduled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def register_webhook(self, url: str, events: list) -> dict:
        """Register a webhook"""
        # TODO: Implement webhook system
        webhook_id = f"webhook-{datetime.now().timestamp()}"
        
        self.webhooks[webhook_id] = {
            "url": url,
            "events": events,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Registered webhook {webhook_id}: {url}")
        
        return {
            "webhook_id": webhook_id,
            "url": url,
            "events": events,
            "status": "registered",
            "timestamp": datetime.now().isoformat()
        }
