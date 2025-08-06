"""
WebSocket Manager for Real-Time Configuration Updates
"""

import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store connections by instance_id
        self.connections: Dict[str, Set[WebSocket]] = {}
        # Store connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, instance_id: str, connection_type: str = "chat"):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to connections
        if instance_id not in self.connections:
            self.connections[instance_id] = set()
        
        self.connections[instance_id].add(websocket)
        
        # Store metadata
        self.connection_metadata[websocket] = {
            "instance_id": instance_id,
            "connection_type": connection_type,
            "connected_at": asyncio.get_event_loop().time()
        }
        
        logger.info(f"WebSocket connected: {connection_type} for instance {instance_id}")
        
        # Send initial connection confirmation
        await self.send_to_connection(websocket, {
            "type": "connection_established",
            "instance_id": instance_id,
            "connection_type": connection_type
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.connection_metadata:
            metadata = self.connection_metadata[websocket]
            instance_id = metadata["instance_id"]
            
            # Remove from connections
            if instance_id in self.connections:
                self.connections[instance_id].discard(websocket)
                
                # Clean up empty instance groups
                if not self.connections[instance_id]:
                    del self.connections[instance_id]
            
            # Remove metadata
            del self.connection_metadata[websocket]
            
            logger.info(f"WebSocket disconnected: {metadata['connection_type']} for instance {instance_id}")
    
    async def send_to_connection(self, websocket: WebSocket, message: dict):
        """Send message to a specific connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def broadcast_to_instance(self, instance_id: str, message: dict, connection_type: str = None):
        """Broadcast message to all connections for an instance"""
        if instance_id not in self.connections:
            return
        
        # Filter by connection type if specified
        target_connections = []
        for websocket in self.connections[instance_id]:
            if websocket in self.connection_metadata:
                metadata = self.connection_metadata[websocket]
                if connection_type is None or metadata["connection_type"] == connection_type:
                    target_connections.append(websocket)
        
        # Send to all target connections
        disconnected = []
        for websocket in target_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_config_update(self, instance_id: str, changes: dict):
        """Broadcast configuration changes to chat clients"""
        message = {
            "type": "config_update",
            "instance_id": instance_id,
            "changes": changes,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.broadcast_to_instance(instance_id, message, "chat")
        logger.info(f"Broadcasted config update to instance {instance_id}: {list(changes.keys())}")
    
    async def broadcast_admin_notification(self, instance_id: str, notification: dict):
        """Broadcast notifications to admin clients"""
        message = {
            "type": "admin_notification",
            "instance_id": instance_id,
            "notification": notification,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.broadcast_to_instance(instance_id, message, "admin")
    
    async def send_typing_indicator(self, instance_id: str, is_typing: bool, user_id: str = None):
        """Send typing indicator to chat clients"""
        message = {
            "type": "typing_indicator",
            "instance_id": instance_id,
            "is_typing": is_typing,
            "user_id": user_id,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.broadcast_to_instance(instance_id, message, "chat")
    
    def get_connection_stats(self) -> dict:
        """Get statistics about current connections"""
        total_connections = sum(len(connections) for connections in self.connections.values())
        
        instance_stats = {}
        for instance_id, connections in self.connections.items():
            connection_types = {}
            for websocket in connections:
                if websocket in self.connection_metadata:
                    conn_type = self.connection_metadata[websocket]["connection_type"]
                    connection_types[conn_type] = connection_types.get(conn_type, 0) + 1
            
            instance_stats[instance_id] = {
                "total": len(connections),
                "by_type": connection_types
            }
        
        return {
            "total_connections": total_connections,
            "total_instances": len(self.connections),
            "instance_stats": instance_stats
        }


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


# WebSocket endpoint
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

websocket_router = APIRouter()

@websocket_router.websocket("/ws/{instance_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    instance_id: str,
    connection_type: str = Query("chat", regex="^(chat|admin)$")
):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket, instance_id, connection_type)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, instance_id, message)
            except json.JSONDecodeError:
                await websocket_manager.send_to_connection(websocket, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


async def handle_websocket_message(websocket: WebSocket, instance_id: str, message: dict):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    if message_type == "ping":
        await websocket_manager.send_to_connection(websocket, {
            "type": "pong",
            "timestamp": asyncio.get_event_loop().time()
        })
    
    elif message_type == "typing_start":
        await websocket_manager.send_typing_indicator(
            instance_id, 
            True, 
            message.get("user_id")
        )
    
    elif message_type == "typing_stop":
        await websocket_manager.send_typing_indicator(
            instance_id, 
            False, 
            message.get("user_id")
        )
    
    else:
        await websocket_manager.send_to_connection(websocket, {
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })
