"""
OpenCngsm MCP v3.0 - Session Sandbox
Per-session isolation with Docker or host execution
"""
from typing import Optional, List, Dict, Any
from enum import Enum
import logging
from pathlib import Path

from .docker_runner import docker_runner

logger = logging.getLogger(__name__)


class SandboxMode(Enum):
    """Sandbox execution modes"""
    HOST = "host"           # Execute on host (main session)
    DOCKER = "docker"       # Execute in Docker container (groups/channels)
    NON_MAIN = "non-main"   # Docker for non-main sessions


class SessionSandbox:
    """
    Manages per-session sandbox isolation
    Inspired by OpenClaw's sandbox.mode configuration
    """
    
    def __init__(
        self,
        session_id: str,
        session_type: str,
        workspace_path: str,
        sandbox_mode: SandboxMode = SandboxMode.NON_MAIN,
        allowlist: Optional[List[str]] = None,
        denylist: Optional[List[str]] = None
    ):
        self.session_id = session_id
        self.session_type = session_type  # main, group, channel, dm
        self.workspace_path = workspace_path
        self.sandbox_mode = sandbox_mode
        self.container_id = None
        
        # Tool permissions
        self.allowlist = allowlist or [
            "bash", "process", "read", "write", "edit",
            "sessions_list", "sessions_history", "sessions_send"
        ]
        self.denylist = denylist or [
            "browser", "canvas", "nodes", "cron", "discord", "gateway"
        ]
        
        # Determine execution mode
        self.use_docker = self._should_use_docker()
        
        logger.info(
            f"🔒 Sandbox created for {session_id} "
            f"(type: {session_type}, mode: {'docker' if self.use_docker else 'host'})"
        )
    
    def _should_use_docker(self) -> bool:
        """Determine if Docker should be used for this session"""
        # Check if Docker is available
        if not docker_runner.is_available():
            logger.warning("Docker not available, using host mode")
            return False
        
        # Main session always runs on host
        if self.session_type == "main":
            return False
        
        # Non-main mode: use Docker for non-main sessions
        if self.sandbox_mode == SandboxMode.NON_MAIN:
            return self.session_type != "main"
        
        # Explicit Docker mode
        if self.sandbox_mode == SandboxMode.DOCKER:
            return True
        
        # Explicit host mode
        return False
    
    def start(self) -> bool:
        """Start the sandbox"""
        if not self.use_docker:
            logger.info(f"📂 Session {self.session_id} running on HOST")
            return True
        
        # Create and start Docker container
        self.container_id = docker_runner.create_container(
            session_id=self.session_id,
            workspace_path=self.workspace_path
        )
        
        if not self.container_id:
            logger.error(f"Failed to create container for {self.session_id}")
            return False
        
        success = docker_runner.start_container(self.session_id)
        
        if success:
            logger.info(f"🐳 Session {self.session_id} running in DOCKER")
        
        return success
    
    def stop(self) -> bool:
        """Stop the sandbox"""
        if not self.use_docker:
            return True
        
        return docker_runner.stop_container(self.session_id)
    
    def destroy(self) -> bool:
        """Destroy the sandbox"""
        if not self.use_docker:
            return True
        
        docker_runner.stop_container(self.session_id)
        return docker_runner.remove_container(self.session_id, force=True)
    
    def execute_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """
        Execute a tool with permission checking
        
        Args:
            tool_name: Name of the tool
            *args, **kwargs: Tool arguments
        
        Returns:
            Tool execution result
        
        Raises:
            PermissionError: If tool is not allowed
        """
        # Check permissions
        if not self.is_tool_allowed(tool_name):
            raise PermissionError(
                f"Tool '{tool_name}' is not allowed in this sandbox. "
                f"Allowlist: {self.allowlist}, Denylist: {self.denylist}"
            )
        
        # Execute tool
        if self.use_docker:
            return self._execute_tool_in_docker(tool_name, *args, **kwargs)
        else:
            return self._execute_tool_on_host(tool_name, *args, **kwargs)
    
    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check if tool is allowed"""
        # Check denylist first
        if tool_name in self.denylist:
            return False
        
        # Check allowlist
        if self.allowlist and tool_name not in self.allowlist:
            return False
        
        return True
    
    def _execute_tool_on_host(self, tool_name: str, *args, **kwargs) -> Any:
        """Execute tool on host"""
        # TODO: Implement tool execution on host
        logger.info(f"🖥️  Executing {tool_name} on HOST")
        return {"status": "executed_on_host", "tool": tool_name}
    
    def _execute_tool_in_docker(self, tool_name: str, *args, **kwargs) -> Any:
        """Execute tool in Docker container"""
        # TODO: Implement tool execution in Docker
        logger.info(f"🐳 Executing {tool_name} in DOCKER")
        
        # For bash/shell commands
        if tool_name == "bash":
            command = args[0] if args else kwargs.get("command", "")
            exit_code, output = docker_runner.execute_command(
                self.session_id,
                command
            )
            return {
                "exit_code": exit_code,
                "output": output
            }
        
        return {"status": "executed_in_docker", "tool": tool_name}
    
    def get_stats(self) -> Optional[Dict]:
        """Get sandbox resource stats"""
        if not self.use_docker:
            return None
        
        return docker_runner.get_container_stats(self.session_id)
    
    def get_info(self) -> Dict[str, Any]:
        """Get sandbox information"""
        return {
            "session_id": self.session_id,
            "session_type": self.session_type,
            "workspace": self.workspace_path,
            "mode": "docker" if self.use_docker else "host",
            "container_id": self.container_id,
            "allowlist": self.allowlist,
            "denylist": self.denylist
        }
