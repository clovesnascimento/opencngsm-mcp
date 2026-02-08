"""
OpenCngsm v3.0 - Docker Sandbox
Container-based skill execution for security and isolation
"""
import docker
from docker.types import Mount
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DockerRunner:
    """
    Docker container management for skill execution
    
    Features:
    - Container isolation per skill
    - Resource limits (CPU, memory)
    - Network isolation
    - Filesystem mounts (read-only/read-write)
    - Automatic cleanup
    """
    
    def __init__(self):
        """Initialize Docker client"""
        try:
            self.client = docker.from_env()
            self.client.ping()
            logger.info("✅ Docker client initialized")
        except Exception as e:
            logger.error(f"❌ Docker not available: {e}")
            raise Exception(
                "Docker is not running. Please start Docker Desktop or Docker daemon.\n"
                "Install: https://www.docker.com/products/docker-desktop"
            )
        
        self.containers = {}
        self.images = {}
    
    async def run_skill(
        self,
        skill_name: str,
        action: str,
        args: Dict[str, Any],
        cpu_limit: float = 1.0,
        memory_limit: str = '512m',
        mounts: List[str] = None,
        network_mode: str = 'bridge',
        env_vars: Dict[str, str] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Run skill in isolated Docker container
        
        Args:
            skill_name: Name of skill to run
            action: Action/method to execute
            args: Arguments for the action
            cpu_limit: CPU limit (1.0 = 1 core)
            memory_limit: Memory limit (e.g., '512m', '1g')
            mounts: List of volume mounts (format: 'host_path:container_path:mode')
            network_mode: Network mode ('bridge', 'none', 'host')
            env_vars: Environment variables
            timeout: Execution timeout in seconds
        
        Returns:
            {
                'status': exit_code,
                'output': stdout,
                'error': stderr,
                'duration': execution_time
            }
        
        Example:
            result = await runner.run_skill(
                skill_name='telegram',
                action='send_message',
                args={'text': 'Hello', 'chat_id': '123'},
                cpu_limit=0.5,
                memory_limit='256m',
                mounts=['/data/telegram:/app/data:ro']
            )
        """
        import time
        start_time = time.time()
        
        # Build image if not exists
        image_name = f'opencngsm-skill-{skill_name}'
        self._ensure_image(skill_name, image_name)
        
        # Prepare mounts
        volumes = {}
        if mounts:
            for mount in mounts:
                parts = mount.split(':')
                if len(parts) == 3:
                    host_path, container_path, mode = parts
                    volumes[host_path] = {
                        'bind': container_path,
                        'mode': mode
                    }
        
        # Prepare environment
        environment = env_vars or {}
        environment['SKILL_ACTION'] = action
        environment['SKILL_ARGS'] = json.dumps(args)
        
        logger.info(f"🐳 Running skill '{skill_name}' in container...")
        
        try:
            # Run container
            container = self.client.containers.run(
                image_name,
                command=f'python -m skills.{skill_name}',
                environment=environment,
                cpu_quota=int(cpu_limit * 100000),
                mem_limit=memory_limit,
                network_mode=network_mode,
                volumes=volumes,
                detach=True,
                remove=False  # Keep for logs
            )
            
            # Wait for completion
            result = container.wait(timeout=timeout)
            logs = container.logs().decode('utf-8')
            
            # Get exit code
            exit_code = result['StatusCode']
            
            # Separate stdout/stderr
            output = logs
            error = result.get('Error', '')
            
            # Cleanup
            container.remove()
            
            duration = time.time() - start_time
            
            logger.info(f"✅ Skill executed in {duration:.2f}s (exit code: {exit_code})")
            
            return {
                'status': exit_code,
                'output': output,
                'error': error,
                'duration': duration
            }
        
        except docker.errors.ContainerError as e:
            logger.error(f"❌ Container error: {e}")
            return {
                'status': -1,
                'output': '',
                'error': str(e),
                'duration': time.time() - start_time
            }
        except Exception as e:
            logger.error(f"❌ Execution error: {e}")
            return {
                'status': -1,
                'output': '',
                'error': str(e),
                'duration': time.time() - start_time
            }
    
    def _ensure_image(self, skill_name: str, image_name: str):
        """Build Docker image for skill if not exists"""
        try:
            self.client.images.get(image_name)
            logger.info(f"📦 Using existing image: {image_name}")
        except docker.errors.ImageNotFound:
            logger.info(f"🔨 Building image: {image_name}")
            
            skill_path = Path(f'skills/{skill_name}')
            
            if not skill_path.exists():
                raise FileNotFoundError(f"Skill not found: {skill_path}")
            
            # Create Dockerfile if not exists
            dockerfile_path = skill_path / 'Dockerfile'
            if not dockerfile_path.exists():
                self._create_default_dockerfile(skill_path)
            
            # Build image
            image, build_logs = self.client.images.build(
                path=str(skill_path),
                tag=image_name,
                rm=True
            )
            
            logger.info(f"✅ Image built: {image_name}")
            self.images[skill_name] = image
    
    def _create_default_dockerfile(self, skill_path: Path):
        """Create default Dockerfile for skill"""
        dockerfile_content = """FROM python:3.11-slim

# Non-root user
RUN useradd -m -u 1000 skilluser

# Install dependencies
WORKDIR /app
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy skill code
COPY . .

# Switch to non-root
USER skilluser

# Default command
CMD ["python", "-m", "skills"]
"""
        
        dockerfile_path = skill_path / 'Dockerfile'
        dockerfile_path.write_text(dockerfile_content)
        logger.info(f"📝 Created default Dockerfile: {dockerfile_path}")
    
    def list_images(self) -> List[str]:
        """List all OpenCngsm skill images"""
        images = self.client.images.list(filters={'reference': 'opencngsm-skill-*'})
        return [img.tags[0] for img in images if img.tags]
    
    def remove_image(self, skill_name: str):
        """Remove skill image"""
        image_name = f'opencngsm-skill-{skill_name}'
        try:
            self.client.images.remove(image_name, force=True)
            logger.info(f"🗑️ Removed image: {image_name}")
        except docker.errors.ImageNotFound:
            logger.warning(f"⚠️ Image not found: {image_name}")
    
    def cleanup_all(self):
        """Remove all skill images"""
        for image_name in self.list_images():
            self.client.images.remove(image_name, force=True)
        logger.info("🧹 Cleaned up all skill images")


class SkillSandbox:
    """
    High-level skill execution with sandboxing
    """
    
    def __init__(self, enable_sandbox: bool = True):
        """
        Initialize skill sandbox
        
        Args:
            enable_sandbox: If True, run skills in Docker containers
        """
        self.enable_sandbox = enable_sandbox
        self.runner = DockerRunner() if enable_sandbox else None
    
    async def execute_skill(
        self,
        skill_name: str,
        action: str,
        args: Dict[str, Any],
        sandbox_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute skill with optional sandboxing
        
        Args:
            skill_name: Skill to execute
            action: Action to perform
            args: Action arguments
            sandbox_config: Sandbox configuration (cpu_limit, memory_limit, etc.)
        
        Returns:
            Execution result
        """
        if self.enable_sandbox:
            config = sandbox_config or {}
            return await self.runner.run_skill(
                skill_name=skill_name,
                action=action,
                args=args,
                **config
            )
        else:
            # Direct execution (no sandbox)
            return await self._execute_direct(skill_name, action, args)
    
    async def _execute_direct(
        self,
        skill_name: str,
        action: str,
        args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute skill directly without sandbox"""
        import importlib
        import time
        
        start_time = time.time()
        
        try:
            # Import skill module
            module = importlib.import_module(f'skills.{skill_name}.{skill_name}_skill')
            
            # Get skill class (assume SkillName + 'Skill')
            class_name = ''.join(word.capitalize() for word in skill_name.split('_')) + 'Skill'
            skill_class = getattr(module, class_name)
            
            # Instantiate and execute
            skill = skill_class()
            method = getattr(skill, action)
            result = await method(**args)
            
            return {
                'status': 0,
                'output': str(result),
                'error': '',
                'duration': time.time() - start_time
            }
        except Exception as e:
            logger.error(f"❌ Direct execution error: {e}")
            return {
                'status': -1,
                'output': '',
                'error': str(e),
                'duration': time.time() - start_time
            }


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # With sandbox
        sandbox = SkillSandbox(enable_sandbox=True)
        
        result = await sandbox.execute_skill(
            skill_name='telegram',
            action='send_message',
            args={'text': 'Hello from sandbox!', 'chat_id': '123'},
            sandbox_config={
                'cpu_limit': 0.5,
                'memory_limit': '256m',
                'network_mode': 'bridge'
            }
        )
        
        print(f"Status: {result['status']}")
        print(f"Output: {result['output']}")
        print(f"Duration: {result['duration']:.2f}s")
    
    asyncio.run(main())
