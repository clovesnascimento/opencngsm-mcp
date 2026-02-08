"""
OpenCngsm MCP v3.0 - WebSocket Gateway
Inspired by OpenClaw architecture (171k ⭐)
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Set, Optional, Any
import asyncio
import json
import uuid
from datetime import datetime
import logging

from .control_plane import ControlPlane

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket, metadata: Optional[Dict] = None):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_metadata[client_id] = metadata or {}
        logger.info(f"Client connected: {client_id}")
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.client_metadata:
            del self.client_metadata[client_id]
        logger.info(f"Client disconnected: {client_id}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict, exclude: Optional[Set[str]] = None):
        """Broadcast message to all connected clients"""
        exclude = exclude or set()
        disconnected = []
        
        for client_id, websocket in self.active_connections.items():
            if client_id not in exclude:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    def get_connected_clients(self) -> list:
        """Get list of connected client IDs"""
        return list(self.active_connections.keys())


class WebSocketGateway:
    """WebSocket Gateway - Main control plane for OpenCngsm v3.0"""
    
    def __init__(self):
        self.app = FastAPI(
            title="OpenCngsm MCP Gateway v3.0",
            version="3.0.0",
            description="WebSocket-based Gateway inspired by OpenClaw"
        )
        
        # CORS Configuration
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Components
        self.manager = ConnectionManager()
        self.control_plane = ControlPlane(self)
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """Main WebSocket endpoint"""
            client_id = str(uuid.uuid4())
            await self.manager.connect(client_id, websocket)
            
            # Send welcome message
            await self.manager.send_personal_message({
                "type": "system",
                "payload": {
                    "event": "connected",
                    "client_id": client_id,
                    "timestamp": datetime.now().isoformat()
                }
            }, client_id)
            
            # Start heartbeat
            heartbeat_task = asyncio.create_task(
                self._heartbeat_loop(client_id, websocket)
            )
            
            try:
                while True:
                    # Receive message
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Handle message
                    await self._handle_message(client_id, message)
                    
            except WebSocketDisconnect:
                logger.info(f"Client {client_id} disconnected")
            except Exception as e:
                logger.error(f"Error in WebSocket connection: {e}")
            finally:
                heartbeat_task.cancel()
                self.manager.disconnect(client_id)
                await self._broadcast_event("client.disconnected", {"client_id": client_id})
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "version": "3.0.0",
                "timestamp": datetime.now().isoformat(),
                "connections": len(self.manager.get_connected_clients())
            }
        
        @self.app.get("/status")
        async def get_status():
            """System status endpoint (legacy compatibility)"""
            return await self.control_plane.get_system_status()
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "name": "OpenCngsm MCP Gateway v3.0",
                "version": "3.0.0",
                "protocol": "websocket",
                "status": "running",
                "connections": len(self.manager.get_connected_clients())
            }
    
    async def _handle_message(self, client_id: str, message: dict):
        """Handle incoming WebSocket message"""
        msg_type = message.get("type")
        msg_id = message.get("id", str(uuid.uuid4()))
        payload = message.get("payload", {})
        
        logger.info(f"Received {msg_type} from {client_id}")
        
        try:
            if msg_type == "ping":
                # Respond to ping
                await self.manager.send_personal_message({
                    "type": "pong",
                    "id": msg_id,
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            elif msg_type == "message":
                # User message to agent
                response = await self.control_plane.handle_user_message(
                    client_id, payload
                )
                await self.manager.send_personal_message({
                    "type": "response",
                    "id": msg_id,
                    "payload": response,
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            elif msg_type == "command":
                # System command
                response = await self.control_plane.handle_command(
                    client_id, payload
                )
                await self.manager.send_personal_message({
                    "type": "command_response",
                    "id": msg_id,
                    "payload": response,
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            elif msg_type == "subscribe":
                # Subscribe to events
                events = payload.get("events", [])
                # TODO: Implement event subscription
                await self.manager.send_personal_message({
                    "type": "subscribed",
                    "id": msg_id,
                    "payload": {"events": events},
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                await self.manager.send_personal_message({
                    "type": "error",
                    "id": msg_id,
                    "payload": {"error": f"Unknown message type: {msg_type}"},
                    "timestamp": datetime.now().isoformat()
                }, client_id)
        
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.manager.send_personal_message({
                "type": "error",
                "id": msg_id,
                "payload": {"error": str(e)},
                "timestamp": datetime.now().isoformat()
            }, client_id)
    
    async def _heartbeat_loop(self, client_id: str, websocket: WebSocket):
        """Send periodic heartbeat to keep connection alive"""
        try:
            while client_id in self.manager.active_connections:
                await asyncio.sleep(30)  # Every 30 seconds
                await self.manager.send_personal_message({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                }, client_id)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Heartbeat error for {client_id}: {e}")
    
    async def _broadcast_event(self, event: str, data: dict):
        """Broadcast event to all connected clients"""
        await self.manager.broadcast({
            "type": "event",
            "id": str(uuid.uuid4()),
            "payload": {
                "event": event,
                "data": data
            },
            "timestamp": datetime.now().isoformat()
        })
    
    def run(self, host: str = "127.0.0.1", port: int = 18789):
        """Run the WebSocket Gateway"""
        import uvicorn
        
        print("=" * 60)
        print("🚀 OpenCngsm MCP Gateway v3.0")
        print("=" * 60)
        print(f"📡 WebSocket: ws://{host}:{port}/ws")
        print(f"🌐 HTTP: http://{host}:{port}")
        print(f"❤️  Health: http://{host}:{port}/health")
        print("=" * 60)
        
        uvicorn.run(self.app, host=host, port=port)


# Singleton instance
gateway = WebSocketGateway()


if __name__ == "__main__":
    gateway.run()
