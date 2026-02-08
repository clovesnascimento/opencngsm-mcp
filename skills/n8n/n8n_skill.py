"""
OpenCngsm v3.1 - N8N Integration Skill
Workflow automation integration with N8N
"""
import os
import json
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Import config manager for universal paths
try:
    from core.config_manager import config
except ImportError:
    config = None

logger = logging.getLogger(__name__)


class N8NSkill:
    """
    N8N workflow automation integration
    
    Features:
    - Execute N8N workflows
    - Trigger webhooks
    - Monitor executions
    - Manage workflows (list, activate, deactivate)
    - Bidirectional communication
    
    Example:
        n8n = N8NSkill()
        
        # Execute workflow
        result = await n8n.execute_workflow(
            workflow_id='123',
            data={'name': 'John', 'email': 'john@example.com'}
        )
        
        # Trigger webhook
        await n8n.trigger_webhook(
            webhook_path='my-webhook',
            data={'message': 'Hello!'}
        )
    """
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize N8N skill
        
        Args:
            api_url: N8N API URL (default: from env or config)
            api_key: N8N API key (default: from env or config)
        """
        # Get from environment or config
        self.api_url = api_url or os.getenv('N8N_API_URL')
        self.api_key = api_key or os.getenv('N8N_API_KEY')
        
        # Try to get from config
        if not self.api_url and config:
            self.api_url = config.get('skills.n8n.api_url')
        if not self.api_key and config:
            self.api_key = config.get('skills.n8n.api_key')
        
        if not self.api_url:
            raise ValueError("N8N_API_URL not set. Set environment variable or config.")
        if not self.api_key:
            raise ValueError("N8N_API_KEY not set. Set environment variable or config.")
        
        # Remove trailing slash
        self.api_url = self.api_url.rstrip('/')
        
        # Headers
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to N8N API"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=self.headers,
                json=data,
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def execute_workflow(
        self,
        workflow_id: str,
        data: Dict[str, Any]
    ) -> Dict:
        """
        Execute N8N workflow
        
        Args:
            workflow_id: N8N workflow ID
            data: Data to pass to workflow
        
        Returns:
            Execution result
        
        Example:
            result = await n8n.execute_workflow(
                workflow_id='123',
                data={'name': 'John', 'action': 'send_email'}
            )
        """
        logger.info(f"Executing N8N workflow: {workflow_id}")
        
        result = await self._request(
            'POST',
            f'/workflows/{workflow_id}/execute',
            data={'data': data}
        )
        
        logger.info(f"Workflow executed: {result.get('id')}")
        return result
    
    async def trigger_webhook(
        self,
        webhook_path: str,
        data: Dict[str, Any],
        method: str = 'POST'
    ) -> Dict:
        """
        Trigger N8N webhook
        
        Args:
            webhook_path: Webhook path (e.g., 'my-webhook')
            data: Data to send
            method: HTTP method (default: POST)
        
        Returns:
            Webhook response
        
        Example:
            result = await n8n.trigger_webhook(
                webhook_path='opencngsm-trigger',
                data={'message': 'Hello from OpenCngsm!'}
            )
        """
        # N8N webhooks are at /webhook/{path}
        webhook_url = f"{self.api_url.replace('/api/v1', '')}/webhook/{webhook_path}"
        
        logger.info(f"Triggering N8N webhook: {webhook_path}")
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                webhook_url,
                json=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def list_workflows(
        self,
        active: Optional[bool] = None
    ) -> List[Dict]:
        """
        List N8N workflows
        
        Args:
            active: Filter by active status (None = all)
        
        Returns:
            List of workflows
        
        Example:
            workflows = await n8n.list_workflows(active=True)
            for workflow in workflows:
                print(f"{workflow['id']}: {workflow['name']}")
        """
        params = {}
        if active is not None:
            params['active'] = 'true' if active else 'false'
        
        result = await self._request('GET', '/workflows', params=params)
        return result.get('data', [])
    
    async def get_workflow(self, workflow_id: str) -> Dict:
        """
        Get workflow details
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            Workflow details
        """
        return await self._request('GET', f'/workflows/{workflow_id}')
    
    async def activate_workflow(self, workflow_id: str) -> Dict:
        """
        Activate workflow
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            Updated workflow
        """
        logger.info(f"Activating workflow: {workflow_id}")
        
        return await self._request(
            'PATCH',
            f'/workflows/{workflow_id}',
            data={'active': True}
        )
    
    async def deactivate_workflow(self, workflow_id: str) -> Dict:
        """
        Deactivate workflow
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            Updated workflow
        """
        logger.info(f"Deactivating workflow: {workflow_id}")
        
        return await self._request(
            'PATCH',
            f'/workflows/{workflow_id}',
            data={'active': False}
        )
    
    async def get_execution(self, execution_id: str) -> Dict:
        """
        Get execution details
        
        Args:
            execution_id: Execution ID
        
        Returns:
            Execution details
        
        Example:
            execution = await n8n.get_execution('456')
            print(f"Status: {execution['status']}")
            print(f"Data: {execution['data']}")
        """
        return await self._request('GET', f'/executions/{execution_id}')
    
    async def list_executions(
        self,
        workflow_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        List workflow executions
        
        Args:
            workflow_id: Filter by workflow ID (None = all)
            limit: Max results
        
        Returns:
            List of executions
        """
        params = {'limit': limit}
        if workflow_id:
            params['workflowId'] = workflow_id
        
        result = await self._request('GET', '/executions', params=params)
        return result.get('data', [])
    
    async def delete_execution(self, execution_id: str):
        """
        Delete execution
        
        Args:
            execution_id: Execution ID
        """
        await self._request('DELETE', f'/executions/{execution_id}')
        logger.info(f"Deleted execution: {execution_id}")
    
    async def get_credentials(self) -> List[Dict]:
        """
        List N8N credentials
        
        Returns:
            List of credentials
        """
        result = await self._request('GET', '/credentials')
        return result.get('data', [])
    
    async def test_connection(self) -> bool:
        """
        Test N8N API connection
        
        Returns:
            True if connection successful
        
        Example:
            if await n8n.test_connection():
                print("✅ N8N connected!")
        """
        try:
            await self.list_workflows()
            logger.info("✅ N8N connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ N8N connection failed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize
        n8n = N8NSkill()
        
        # Test connection
        if await n8n.test_connection():
            print("✅ Connected to N8N!")
            
            # List workflows
            workflows = await n8n.list_workflows()
            print(f"\n📋 Workflows ({len(workflows)}):")
            for workflow in workflows:
                status = "✅ Active" if workflow['active'] else "⏸️ Inactive"
                print(f"  {workflow['id']}: {workflow['name']} - {status}")
            
            # List recent executions
            executions = await n8n.list_executions(limit=5)
            print(f"\n🔄 Recent Executions ({len(executions)}):")
            for execution in executions:
                print(f"  {execution['id']}: {execution['status']} - {execution['startedAt']}")
    
    asyncio.run(main())
