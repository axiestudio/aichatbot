from typing import List, Optional, Dict, Any
import logging
import uuid
from datetime import datetime, timedelta

from app.models.chat import ChatSession, ChatMessage, ChatConfig

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat sessions and messages"""
    
    def __init__(self):
        # In-memory storage for demo purposes
        # In production, this would use a proper database
        self.sessions: Dict[str, ChatSession] = {}
        self.configs: Dict[str, ChatConfig] = {}
        self._initialize_default_config()
    
    def _initialize_default_config(self):
        """Initialize default chat configuration"""
        default_config = ChatConfig(
            id="default",
            name="Default Chat",
            primary_color="#3b82f6",
            secondary_color="#e5e7eb",
            font_family="Inter",
            font_size=14,
            border_radius=12,
            position="bottom-right",
            welcome_message="Hello! How can I help you today?",
            placeholder="Type your message...",
            height=500,
            width=350,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.configs["default"] = default_config
    
    async def get_or_create_session(
        self, 
        session_id: str, 
        config_id: Optional[str] = None
    ) -> ChatSession:
        """Get existing session or create a new one"""
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Create new session
        session = ChatSession(
            id=session_id,
            messages=[],
            config_id=config_id or "default",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created new chat session: {session_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        return self.sessions.get(session_id)
    
    async def add_message_to_session(
        self, 
        session_id: str, 
        message: ChatMessage
    ) -> bool:
        """Add a message to a chat session"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return False
        
        session = self.sessions[session_id]
        session.messages.append(message)
        session.updated_at = datetime.utcnow()
        
        logger.info(f"Added message to session {session_id}: {message.role}")
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    async def list_sessions(
        self, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ChatSession]:
        """List chat sessions with pagination"""
        sessions = list(self.sessions.values())
        # Sort by updated_at descending
        sessions.sort(key=lambda x: x.updated_at, reverse=True)
        return sessions[offset:offset + limit]
    
    async def get_session_count(self) -> int:
        """Get total number of sessions"""
        return len(self.sessions)
    
    async def get_message_count(self) -> int:
        """Get total number of messages across all sessions"""
        total = 0
        for session in self.sessions.values():
            total += len(session.messages)
        return total
    
    async def get_recent_messages(
        self, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent messages across all sessions"""
        all_messages = []
        
        for session in self.sessions.values():
            for message in session.messages:
                all_messages.append({
                    "session_id": session.id,
                    "message": message,
                    "timestamp": message.timestamp
                })
        
        # Sort by timestamp descending
        all_messages.sort(key=lambda x: x["timestamp"] or datetime.min, reverse=True)
        return all_messages[:limit]
    
    async def get_chat_config(self, config_id: str) -> Optional[ChatConfig]:
        """Get chat configuration by ID"""
        return self.configs.get(config_id)
    
    async def create_chat_config(self, config: ChatConfig) -> ChatConfig:
        """Create a new chat configuration"""
        config.created_at = datetime.utcnow()
        config.updated_at = datetime.utcnow()
        self.configs[config.id] = config
        logger.info(f"Created chat config: {config.id}")
        return config
    
    async def update_chat_config(
        self, 
        config_id: str, 
        config: ChatConfig
    ) -> Optional[ChatConfig]:
        """Update an existing chat configuration"""
        if config_id not in self.configs:
            return None
        
        config.id = config_id
        config.updated_at = datetime.utcnow()
        self.configs[config_id] = config
        logger.info(f"Updated chat config: {config_id}")
        return config
    
    async def delete_chat_config(self, config_id: str) -> bool:
        """Delete a chat configuration"""
        if config_id in self.configs and config_id != "default":
            del self.configs[config_id]
            logger.info(f"Deleted chat config: {config_id}")
            return True
        return False
    
    async def list_chat_configs(self) -> List[ChatConfig]:
        """List all chat configurations"""
        return list(self.configs.values())
    
    async def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up sessions older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.updated_at < cutoff_date
        ]
        
        for session_id in old_sessions:
            del self.sessions[session_id]
        
        logger.info(f"Cleaned up {len(old_sessions)} old sessions")
        return len(old_sessions)
