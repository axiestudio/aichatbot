"""
Advanced Real-Time Collaboration Service
Multi-user collaboration, live editing, and real-time synchronization
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from .cache_service import cache_service
from .websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


class CollaborationEventType(Enum):
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"
    MESSAGE_DRAFT = "message_draft"
    CURSOR_MOVE = "cursor_move"
    SELECTION_CHANGE = "selection_change"
    DOCUMENT_EDIT = "document_edit"
    ANNOTATION_ADD = "annotation_add"
    ANNOTATION_REMOVE = "annotation_remove"
    SCREEN_SHARE = "screen_share"
    VOICE_CHAT = "voice_chat"


class UserPresence(Enum):
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass
class CollaborationUser:
    user_id: str
    name: str
    avatar_url: Optional[str]
    presence: UserPresence
    cursor_position: Optional[Dict[str, Any]]
    selection: Optional[Dict[str, Any]]
    last_activity: datetime
    permissions: List[str]
    metadata: Dict[str, Any]


@dataclass
class CollaborationEvent:
    event_id: str
    event_type: CollaborationEventType
    user_id: str
    session_id: str
    data: Dict[str, Any]
    timestamp: datetime
    expires_at: Optional[datetime] = None


class RealtimeCollaborationService:
    """Advanced real-time collaboration and synchronization service"""
    
    def __init__(self):
        self.active_sessions = defaultdict(dict)  # session_id -> user_data
        self.collaboration_events = deque(maxlen=10000)
        self.user_cursors = defaultdict(dict)  # session_id -> {user_id: cursor_data}
        self.typing_indicators = defaultdict(set)  # session_id -> set of user_ids
        self.document_locks = defaultdict(dict)  # document_id -> {user_id: lock_data}
        self.shared_documents = defaultdict(dict)  # session_id -> document_data
        self.voice_rooms = defaultdict(set)  # session_id -> set of user_ids
        self.screen_shares = defaultdict(dict)  # session_id -> {user_id: share_data}
        
        # Collaboration features
        self.features = {
            "real_time_editing": True,
            "cursor_tracking": True,
            "typing_indicators": True,
            "voice_chat": True,
            "screen_sharing": True,
            "document_locking": True,
            "annotations": True,
            "presence_awareness": True,
            "conflict_resolution": True
        }
    
    async def start_collaboration_service(self):
        """Start real-time collaboration service"""
        logger.info("🤝 Real-Time Collaboration Service started")
        asyncio.create_task(self._collaboration_monitoring_loop())
        asyncio.create_task(self._presence_update_loop())
        asyncio.create_task(self._cleanup_loop())
    
    async def user_join_session(self, user_id: str, session_id: str, user_data: Dict[str, Any]) -> CollaborationUser:
        """Handle user joining a collaboration session"""
        try:
            # Create collaboration user
            collab_user = CollaborationUser(
                user_id=user_id,
                name=user_data.get("name", f"User {user_id[:8]}"),
                avatar_url=user_data.get("avatar_url"),
                presence=UserPresence.ONLINE,
                cursor_position=None,
                selection=None,
                last_activity=datetime.utcnow(),
                permissions=user_data.get("permissions", ["read", "write"]),
                metadata=user_data.get("metadata", {})
            )
            
            # Add to active session
            self.active_sessions[session_id][user_id] = collab_user
            
            # Create join event
            event = CollaborationEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollaborationEventType.USER_JOINED,
                user_id=user_id,
                session_id=session_id,
                data={
                    "user": asdict(collab_user),
                    "session_users": len(self.active_sessions[session_id])
                },
                timestamp=datetime.utcnow()
            )
            
            # Store event
            self.collaboration_events.append(event)
            
            # Broadcast to session
            await self._broadcast_to_session(session_id, event, exclude_user=user_id)
            
            # Send current session state to new user
            await self._send_session_state(user_id, session_id)
            
            logger.info(f"User {user_id} joined collaboration session {session_id}")
            return collab_user
            
        except Exception as e:
            logger.error(f"Error handling user join: {e}")
            return None
    
    async def user_leave_session(self, user_id: str, session_id: str):
        """Handle user leaving a collaboration session"""
        try:
            if session_id in self.active_sessions and user_id in self.active_sessions[session_id]:
                # Remove user from session
                del self.active_sessions[session_id][user_id]
                
                # Clean up user data
                if user_id in self.user_cursors.get(session_id, {}):
                    del self.user_cursors[session_id][user_id]
                
                self.typing_indicators.get(session_id, set()).discard(user_id)
                self.voice_rooms.get(session_id, set()).discard(user_id)
                
                if user_id in self.screen_shares.get(session_id, {}):
                    del self.screen_shares[session_id][user_id]
                
                # Release document locks
                for doc_id, locks in self.document_locks.items():
                    if user_id in locks:
                        del locks[user_id]
                
                # Create leave event
                event = CollaborationEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=CollaborationEventType.USER_LEFT,
                    user_id=user_id,
                    session_id=session_id,
                    data={
                        "session_users": len(self.active_sessions[session_id])
                    },
                    timestamp=datetime.utcnow()
                )
                
                self.collaboration_events.append(event)
                await self._broadcast_to_session(session_id, event)
                
                logger.info(f"User {user_id} left collaboration session {session_id}")
                
        except Exception as e:
            logger.error(f"Error handling user leave: {e}")
    
    async def update_cursor_position(self, user_id: str, session_id: str, cursor_data: Dict[str, Any]):
        """Update user cursor position"""
        try:
            if session_id not in self.user_cursors:
                self.user_cursors[session_id] = {}
            
            self.user_cursors[session_id][user_id] = {
                "position": cursor_data.get("position", {}),
                "selection": cursor_data.get("selection", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Update user activity
            if session_id in self.active_sessions and user_id in self.active_sessions[session_id]:
                self.active_sessions[session_id][user_id].last_activity = datetime.utcnow()
                self.active_sessions[session_id][user_id].cursor_position = cursor_data.get("position")
                self.active_sessions[session_id][user_id].selection = cursor_data.get("selection")
            
            # Broadcast cursor update
            event = CollaborationEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollaborationEventType.CURSOR_MOVE,
                user_id=user_id,
                session_id=session_id,
                data=cursor_data,
                timestamp=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=30)  # Cursor events expire quickly
            )
            
            await self._broadcast_to_session(session_id, event, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error updating cursor position: {e}")
    
    async def start_typing(self, user_id: str, session_id: str):
        """Handle user starting to type"""
        try:
            self.typing_indicators[session_id].add(user_id)
            
            event = CollaborationEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollaborationEventType.TYPING_START,
                user_id=user_id,
                session_id=session_id,
                data={"typing_users": list(self.typing_indicators[session_id])},
                timestamp=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=10)
            )
            
            await self._broadcast_to_session(session_id, event, exclude_user=user_id)
            
            # Auto-stop typing after 5 seconds
            asyncio.create_task(self._auto_stop_typing(user_id, session_id))
            
        except Exception as e:
            logger.error(f"Error handling start typing: {e}")
    
    async def stop_typing(self, user_id: str, session_id: str):
        """Handle user stopping typing"""
        try:
            self.typing_indicators[session_id].discard(user_id)
            
            event = CollaborationEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollaborationEventType.TYPING_STOP,
                user_id=user_id,
                session_id=session_id,
                data={"typing_users": list(self.typing_indicators[session_id])},
                timestamp=datetime.utcnow()
            )
            
            await self._broadcast_to_session(session_id, event, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling stop typing: {e}")
    
    async def update_document(self, user_id: str, session_id: str, document_id: str, changes: Dict[str, Any]):
        """Handle real-time document updates"""
        try:
            # Check if user has write permissions
            if not await self._check_write_permission(user_id, session_id):
                return False
            
            # Apply operational transformation for conflict resolution
            transformed_changes = await self._apply_operational_transform(document_id, changes)
            
            # Update document
            if session_id not in self.shared_documents:
                self.shared_documents[session_id] = {}
            
            if document_id not in self.shared_documents[session_id]:
                self.shared_documents[session_id][document_id] = {
                    "content": "",
                    "version": 0,
                    "last_modified": datetime.utcnow().isoformat(),
                    "modified_by": user_id
                }
            
            doc = self.shared_documents[session_id][document_id]
            doc["content"] = transformed_changes.get("content", doc["content"])
            doc["version"] += 1
            doc["last_modified"] = datetime.utcnow().isoformat()
            doc["modified_by"] = user_id
            
            # Create document edit event
            event = CollaborationEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollaborationEventType.DOCUMENT_EDIT,
                user_id=user_id,
                session_id=session_id,
                data={
                    "document_id": document_id,
                    "changes": transformed_changes,
                    "version": doc["version"]
                },
                timestamp=datetime.utcnow()
            )
            
            await self._broadcast_to_session(session_id, event, exclude_user=user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    async def start_screen_share(self, user_id: str, session_id: str, share_data: Dict[str, Any]):
        """Start screen sharing"""
        try:
            self.screen_shares[session_id][user_id] = {
                "stream_id": share_data.get("stream_id"),
                "quality": share_data.get("quality", "medium"),
                "audio_enabled": share_data.get("audio_enabled", False),
                "started_at": datetime.utcnow().isoformat()
            }
            
            event = CollaborationEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollaborationEventType.SCREEN_SHARE,
                user_id=user_id,
                session_id=session_id,
                data={
                    "action": "start",
                    "share_data": self.screen_shares[session_id][user_id]
                },
                timestamp=datetime.utcnow()
            )
            
            await self._broadcast_to_session(session_id, event, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error starting screen share: {e}")
    
    async def join_voice_chat(self, user_id: str, session_id: str, voice_data: Dict[str, Any]):
        """Join voice chat"""
        try:
            self.voice_rooms[session_id].add(user_id)
            
            event = CollaborationEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollaborationEventType.VOICE_CHAT,
                user_id=user_id,
                session_id=session_id,
                data={
                    "action": "join",
                    "voice_users": list(self.voice_rooms[session_id]),
                    "voice_data": voice_data
                },
                timestamp=datetime.utcnow()
            )
            
            await self._broadcast_to_session(session_id, event, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error joining voice chat: {e}")
    
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get current collaboration session state"""
        try:
            session_users = self.active_sessions.get(session_id, {})
            
            return {
                "session_id": session_id,
                "users": {
                    user_id: asdict(user_data) 
                    for user_id, user_data in session_users.items()
                },
                "cursors": self.user_cursors.get(session_id, {}),
                "typing_users": list(self.typing_indicators.get(session_id, set())),
                "voice_users": list(self.voice_rooms.get(session_id, set())),
                "screen_shares": self.screen_shares.get(session_id, {}),
                "documents": self.shared_documents.get(session_id, {}),
                "total_users": len(session_users),
                "features": self.features,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting session state: {e}")
            return {"error": str(e)}
    
    async def _broadcast_to_session(self, session_id: str, event: CollaborationEvent, exclude_user: str = None):
        """Broadcast event to all users in session"""
        try:
            message = {
                "type": "collaboration_event",
                "event": asdict(event),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Get all users in session
            session_users = self.active_sessions.get(session_id, {})
            
            for user_id in session_users:
                if user_id != exclude_user:
                    await websocket_manager.send_to_user(user_id, message)
                    
        except Exception as e:
            logger.error(f"Error broadcasting to session: {e}")
    
    async def _send_session_state(self, user_id: str, session_id: str):
        """Send current session state to user"""
        try:
            state = await self.get_session_state(session_id)
            
            message = {
                "type": "session_state",
                "data": state,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket_manager.send_to_user(user_id, message)
            
        except Exception as e:
            logger.error(f"Error sending session state: {e}")
    
    async def _check_write_permission(self, user_id: str, session_id: str) -> bool:
        """Check if user has write permission"""
        try:
            session_users = self.active_sessions.get(session_id, {})
            user = session_users.get(user_id)
            
            if user and "write" in user.permissions:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking write permission: {e}")
            return False
    
    async def _apply_operational_transform(self, document_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Apply operational transformation for conflict resolution"""
        # Simplified operational transformation
        # In production, this would implement proper OT algorithms
        return changes
    
    async def _auto_stop_typing(self, user_id: str, session_id: str):
        """Auto-stop typing after timeout"""
        await asyncio.sleep(5)
        await self.stop_typing(user_id, session_id)
    
    async def _collaboration_monitoring_loop(self):
        """Main collaboration monitoring loop"""
        while True:
            try:
                # Monitor collaboration health
                await self._monitor_collaboration_health()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Collaboration monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _presence_update_loop(self):
        """Update user presence status"""
        while True:
            try:
                await self._update_user_presence()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Presence update error: {e}")
                await asyncio.sleep(120)
    
    async def _cleanup_loop(self):
        """Clean up expired events and inactive sessions"""
        while True:
            try:
                await self._cleanup_expired_data()
                await asyncio.sleep(300)  # Clean up every 5 minutes
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(600)
    
    async def _monitor_collaboration_health(self):
        """Monitor collaboration service health"""
        # Implementation would monitor service health
        pass
    
    async def _update_user_presence(self):
        """Update user presence based on activity"""
        try:
            now = datetime.utcnow()
            
            for session_id, users in self.active_sessions.items():
                for user_id, user in users.items():
                    # Check last activity
                    time_since_activity = (now - user.last_activity).total_seconds()
                    
                    if time_since_activity > 300:  # 5 minutes
                        user.presence = UserPresence.AWAY
                    elif time_since_activity > 1800:  # 30 minutes
                        user.presence = UserPresence.OFFLINE
                    else:
                        user.presence = UserPresence.ONLINE
                        
        except Exception as e:
            logger.error(f"Error updating user presence: {e}")
    
    async def _cleanup_expired_data(self):
        """Clean up expired events and data"""
        try:
            now = datetime.utcnow()
            
            # Clean up expired events
            self.collaboration_events = deque([
                event for event in self.collaboration_events
                if not event.expires_at or event.expires_at > now
            ], maxlen=10000)
            
            # Clean up inactive sessions
            inactive_sessions = []
            for session_id, users in self.active_sessions.items():
                if not users:  # Empty session
                    inactive_sessions.append(session_id)
                    
            for session_id in inactive_sessions:
                del self.active_sessions[session_id]
                self.user_cursors.pop(session_id, None)
                self.typing_indicators.pop(session_id, None)
                self.voice_rooms.pop(session_id, None)
                self.screen_shares.pop(session_id, None)
                self.shared_documents.pop(session_id, None)
                
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {e}")


# Global real-time collaboration service instance
realtime_collaboration_service = RealtimeCollaborationService()
