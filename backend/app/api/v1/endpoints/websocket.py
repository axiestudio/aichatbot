"""
WebSocket endpoints for real-time chat functionality
Production-ready WebSocket implementation with connection management
"""

import json
import logging
import asyncio
from typing import Dict, Set, Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.websockets import WebSocketState

from app.services.unified_chat_service import unified_chat_service
from app.services.unified_monitoring_service import unified_monitoring
from app.core.dependencies import get_current_user_ws
from app.core.tracing import trace_async_function

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        # Active connections by session_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # User to sessions mapping
        self.user_sessions: Dict[str, Set[str]] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, any]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str, user_id: Optional[str] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to active connections
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        
        # Track user sessions
        if user_id:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            'session_id': session_id,
            'user_id': user_id,
            'connected_at': datetime.utcnow(),
            'last_activity': datetime.utcnow()
        }
        
        logger.info(f"WebSocket connected: session={session_id}, user={user_id}")
        
        # Track connection metrics
        unified_monitoring.track_business_metric(
            'websocket_connections',
            len(self.get_all_connections()),
            {'action': 'connect', 'session_id': session_id}
        )
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket not in self.connection_metadata:
            return
            
        metadata = self.connection_metadata[websocket]
        session_id = metadata['session_id']
        user_id = metadata['user_id']
        
        # Remove from active connections
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        # Remove from user sessions
        if user_id and user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]
        
        # Remove metadata
        del self.connection_metadata[websocket]
        
        logger.info(f"WebSocket disconnected: session={session_id}, user={user_id}")
        
        # Track disconnection metrics
        unified_monitoring.track_business_metric(
            'websocket_connections',
            len(self.get_all_connections()),
            {'action': 'disconnect', 'session_id': session_id}
        )
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(message)
                self._update_activity(websocket)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def send_to_session(self, message: str, session_id: str):
        """Send a message to all connections in a session"""
        if session_id not in self.active_connections:
            return
            
        disconnected = []
        for websocket in self.active_connections[session_id].copy():
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(message)
                    self._update_activity(websocket)
                else:
                    disconnected.append(websocket)
            except Exception as e:
                logger.error(f"Error sending to session {session_id}: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.disconnect(ws)
    
    async def send_to_user(self, message: str, user_id: str):
        """Send a message to all sessions of a user"""
        if user_id not in self.user_sessions:
            return
            
        for session_id in self.user_sessions[user_id].copy():
            await self.send_to_session(message, session_id)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients"""
        for session_connections in self.active_connections.values():
            for websocket in session_connections.copy():
                await self.send_personal_message(message, websocket)
    
    def get_session_connections(self, session_id: str) -> Set[WebSocket]:
        """Get all connections for a session"""
        return self.active_connections.get(session_id, set())
    
    def get_user_sessions(self, user_id: str) -> Set[str]:
        """Get all sessions for a user"""
        return self.user_sessions.get(user_id, set())
    
    def get_all_connections(self) -> Set[WebSocket]:
        """Get all active connections"""
        all_connections = set()
        for connections in self.active_connections.values():
            all_connections.update(connections)
        return all_connections
    
    def _update_activity(self, websocket: WebSocket):
        """Update last activity timestamp"""
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]['last_activity'] = datetime.utcnow()
    
    def get_connection_stats(self) -> Dict[str, any]:
        """Get connection statistics"""
        return {
            'total_connections': len(self.get_all_connections()),
            'active_sessions': len(self.active_connections),
            'active_users': len(self.user_sessions),
            'connections_by_session': {
                session_id: len(connections) 
                for session_id, connections in self.active_connections.items()
            }
        }


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
@trace_async_function("websocket.chat_connection")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    user_id: Optional[str] = None
):
    """WebSocket endpoint for real-time chat"""
    
    await manager.connect(websocket, session_id, user_id)
    
    try:
        # Send connection confirmation
        await manager.send_personal_message(
            json.dumps({
                'type': 'connection_established',
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat()
            }),
            websocket
        )
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                await handle_websocket_message(websocket, session_id, message_data, user_id)
                
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }),
                    websocket
                )
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await manager.send_personal_message(
                    json.dumps({
                        'type': 'error',
                        'message': 'Internal server error'
                    }),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def handle_websocket_message(
    websocket: WebSocket,
    session_id: str,
    message_data: Dict[str, any],
    user_id: Optional[str] = None
):
    """Handle different types of WebSocket messages"""
    
    message_type = message_data.get('type')
    
    if message_type == 'chat_message':
        # Handle chat message
        message_content = message_data.get('message', '')
        
        if message_content.strip():
            # Send message through chat service
            response_message = await unified_chat_service.send_message(
                session_id=session_id,
                message=message_content,
                user_id=user_id
            )
            
            # Broadcast user message to all session connections
            await manager.send_to_session(
                json.dumps({
                    'type': 'user_message',
                    'message': message_content,
                    'message_id': str(response_message.id),
                    'timestamp': datetime.utcnow().isoformat(),
                    'user_id': user_id
                }),
                session_id
            )
            
            # Send AI response to all session connections
            await manager.send_to_session(
                json.dumps({
                    'type': 'ai_response',
                    'message': response_message.content,
                    'message_id': response_message.id,
                    'timestamp': response_message.timestamp.isoformat(),
                    'metadata': response_message.metadata
                }),
                session_id
            )
    
    elif message_type == 'typing_start':
        # Broadcast typing indicator
        await manager.send_to_session(
            json.dumps({
                'type': 'user_typing',
                'user_id': user_id,
                'is_typing': True,
                'timestamp': datetime.utcnow().isoformat()
            }),
            session_id
        )
    
    elif message_type == 'typing_stop':
        # Stop typing indicator
        await manager.send_to_session(
            json.dumps({
                'type': 'user_typing',
                'user_id': user_id,
                'is_typing': False,
                'timestamp': datetime.utcnow().isoformat()
            }),
            session_id
        )
    
    elif message_type == 'ping':
        # Respond to ping with pong
        await manager.send_personal_message(
            json.dumps({
                'type': 'pong',
                'timestamp': datetime.utcnow().isoformat()
            }),
            websocket
        )
    
    else:
        await manager.send_personal_message(
            json.dumps({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            }),
            websocket
        )


@router.get("/ws/stats")
async def get_websocket_stats(current_user: str = Depends(get_current_user)):
    """Get WebSocket connection statistics (admin only)"""
    return manager.get_connection_stats()


@router.post("/ws/broadcast")
async def broadcast_message(
    message: str,
    current_user: str = Depends(get_current_user)
):
    """Broadcast a message to all connected clients (admin only)"""
    await manager.broadcast(json.dumps({
        'type': 'broadcast',
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'from': 'admin'
    }))
    
    return {'message': 'Broadcast sent successfully'}
