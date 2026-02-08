"""
OpenCngsm MCP v3.0 - Session Manager
Manages session lifecycle and routing
"""
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

from .session_store import session_store
from core.sandbox.session_sandbox import SessionSandbox, SandboxMode

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages session lifecycle, routing, and isolation
    Inspired by OpenClaw's multi-agent routing
    """
    
    def __init__(self, workspace_root: str = "~/.opencngsm/sessions"):
        self.workspace_root = Path(workspace_root).expanduser()
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        
        self.sessions: Dict[str, SessionSandbox] = {}
        self.store = session_store
        
        logger.info(f"📂 Session Manager initialized (workspace: {self.workspace_root})")
    
    def create_session(
        self,
        session_id: str,
        session_type: str = "group",
        channel: Optional[str] = None,
        channel_id: Optional[str] = None,
        sandbox_mode: str = "non-main",
        metadata: Optional[Dict] = None
    ) -> Optional[SessionSandbox]:
        """
        Create a new session
        
        Args:
            session_id: Unique session identifier
            session_type: Type (main, group, channel, dm)
            channel: Channel name (telegram, whatsapp, etc)
            channel_id: Channel-specific ID
            sandbox_mode: Sandbox mode (host, docker, non-main)
            metadata: Additional metadata
        
        Returns:
            SessionSandbox instance or None
        """
        if session_id in self.sessions:
            logger.warning(f"Session already exists: {session_id}")
            return self.sessions[session_id]
        
        try:
            # Create session workspace
            workspace_path = self.workspace_root / session_id
            workspace_path.mkdir(parents=True, exist_ok=True)
            
            # Create MEMORY.md
            memory_file = workspace_path / "MEMORY.md"
            if not memory_file.exists():
                memory_file.write_text(f"# Session Memory: {session_id}\n\n")
            
            # Create workspace subdirectory
            (workspace_path / "workspace").mkdir(exist_ok=True)
            
            # Determine sandbox mode
            mode = SandboxMode(sandbox_mode) if sandbox_mode in ["host", "docker", "non-main"] else SandboxMode.NON_MAIN
            
            # Create sandbox
            sandbox = SessionSandbox(
                session_id=session_id,
                session_type=session_type,
                workspace_path=str(workspace_path / "workspace"),
                sandbox_mode=mode
            )
            
            # Start sandbox
            if not sandbox.start():
                logger.error(f"Failed to start sandbox for {session_id}")
                return None
            
            # Store in database
            self.store.create_session(
                session_id=session_id,
                session_type=session_type,
                channel=channel,
                channel_id=channel_id,
                sandbox_mode="docker" if sandbox.use_docker else "host",
                metadata=metadata
            )
            
            # Register session
            self.sessions[session_id] = sandbox
            
            logger.info(f"✅ Session created: {session_id} (type: {session_type})")
            
            return sandbox
        
        except Exception as e:
            logger.error(f"❌ Failed to create session: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[SessionSandbox]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def destroy_session(self, session_id: str) -> bool:
        """Destroy a session"""
        if session_id not in self.sessions:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        try:
            # Stop and destroy sandbox
            sandbox = self.sessions[session_id]
            sandbox.destroy()
            
            # Update database
            self.store.update_session(session_id, status="destroyed")
            
            # Remove from active sessions
            del self.sessions[session_id]
            
            logger.info(f"🗑️  Session destroyed: {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to destroy session: {e}")
            return False
    
    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List sessions"""
        return self.store.list_sessions(status=status)
    
    def get_or_create_session(
        self,
        session_id: str,
        session_type: str = "group",
        **kwargs
    ) -> Optional[SessionSandbox]:
        """Get existing session or create new one"""
        session = self.get_session(session_id)
        if session:
            return session
        
        return self.create_session(session_id, session_type, **kwargs)
    
    def route_message(
        self,
        session_id: str,
        content: str,
        user_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Route message to appropriate session
        
        Args:
            session_id: Target session ID
            content: Message content
            user_id: User identifier
            metadata: Additional metadata
        
        Returns:
            Response dict
        """
        # Get or create session
        session = self.get_or_create_session(session_id)
        
        if not session:
            return {
                "error": f"Failed to get/create session: {session_id}",
                "session_id": session_id
            }
        
        # Store user message
        self.store.add_message(
            session_id=session_id,
            role="user",
            content=content,
            metadata=metadata
        )
        
        # TODO: Process message with orchestrator
        # For now, return echo
        response_content = f"Echo from {session_id}: {content}"
        
        # Store assistant response
        self.store.add_message(
            session_id=session_id,
            role="assistant",
            content=response_content
        )
        
        return {
            "session_id": session_id,
            "content": response_content,
            "sandbox_info": session.get_info()
        }
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive session information"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        db_session = self.store.get_session(session_id)
        
        return {
            "session_id": session_id,
            "sandbox": session.get_info(),
            "database": db_session,
            "message_count": len(self.store.get_messages(session_id))
        }
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """Cleanup inactive sessions older than max_age_hours"""
        # TODO: Implement cleanup logic
        logger.info("🧹 Cleanup not yet implemented")
        pass


# Singleton instance
session_manager = SessionManager()
