import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
from collections import defaultdict

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ChatSession:
    session_id: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    started_at: datetime
    last_activity: datetime
    message_count: int
    is_active: bool
    config_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatMessage:
    message_id: str
    session_id: str
    user_message: str
    ai_response: str
    timestamp: datetime
    response_time: float
    tokens_used: int
    config_used: str
    rag_context: Optional[List[str]] = None
    error: Optional[str] = None
    flagged: bool = False
    admin_notes: Optional[str] = None


@dataclass
class ChatAnalytics:
    total_sessions: int
    active_sessions: int
    total_messages: int
    average_response_time: float
    total_tokens_used: int
    sessions_by_hour: Dict[str, int]
    popular_topics: List[Dict[str, Any]]
    error_rate: float
    user_satisfaction: Optional[float] = None


class ChatMonitoringService:
    """Service for monitoring and managing chat sessions"""
    
    def __init__(self):
        # In-memory storage - replace with database in production
        self.sessions: Dict[str, ChatSession] = {}
        self.messages: Dict[str, List[ChatMessage]] = defaultdict(list)
        self.analytics_cache: Optional[ChatAnalytics] = None
        self.cache_expiry: Optional[datetime] = None
        
        # Real-time monitoring
        self.active_connections: Dict[str, Any] = {}
        self.message_queue: List[ChatMessage] = []
        
        # Configuration
        self.session_timeout = timedelta(minutes=30)
        self.max_sessions = 1000
        self.max_messages_per_session = 100
    
    async def start_session(
        self, 
        session_id: str, 
        user_id: Optional[str] = None,
        ip_address: str = "unknown",
        user_agent: str = "unknown",
        config_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """Start a new chat session"""
        try:
            # Clean up old sessions if needed
            await self._cleanup_old_sessions()
            
            # Create new session
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                started_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                message_count=0,
                is_active=True,
                config_id=config_id,
                metadata=metadata
            )
            
            self.sessions[session_id] = session
            self.messages[session_id] = []
            
            logger.info(f"Chat session started: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error starting session {session_id}: {str(e)}")
            raise
    
    async def log_message(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        response_time: float,
        tokens_used: int,
        config_used: str,
        rag_context: Optional[List[str]] = None,
        error: Optional[str] = None
    ) -> ChatMessage:
        """Log a chat message"""
        try:
            # Get or create session
            session = self.sessions.get(session_id)
            if not session:
                session = await self.start_session(session_id)
            
            # Create message
            message = ChatMessage(
                message_id=f"{session_id}_{len(self.messages[session_id])}",
                session_id=session_id,
                user_message=user_message,
                ai_response=ai_response,
                timestamp=datetime.utcnow(),
                response_time=response_time,
                tokens_used=tokens_used,
                config_used=config_used,
                rag_context=rag_context,
                error=error,
                flagged=False
            )
            
            # Store message
            self.messages[session_id].append(message)
            
            # Update session
            session.last_activity = datetime.utcnow()
            session.message_count += 1
            
            # Add to real-time queue
            self.message_queue.append(message)
            
            # Keep queue size manageable
            if len(self.message_queue) > 100:
                self.message_queue = self.message_queue[-50:]
            
            # Invalidate analytics cache
            self.analytics_cache = None
            
            logger.debug(f"Message logged for session {session_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error logging message for session {session_id}: {str(e)}")
            raise
    
    async def end_session(self, session_id: str) -> bool:
        """End a chat session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            session.is_active = False
            session.last_activity = datetime.utcnow()
            
            logger.info(f"Chat session ended: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {str(e)}")
            return False
    
    async def get_active_sessions(self) -> List[ChatSession]:
        """Get all active chat sessions"""
        try:
            await self._cleanup_old_sessions()
            return [session for session in self.sessions.values() if session.is_active]
        except Exception as e:
            logger.error(f"Error getting active sessions: {str(e)}")
            return []
    
    async def get_session_history(
        self, 
        session_id: str, 
        limit: int = 50
    ) -> List[ChatMessage]:
        """Get message history for a session"""
        try:
            messages = self.messages.get(session_id, [])
            return messages[-limit:] if limit > 0 else messages
        except Exception as e:
            logger.error(f"Error getting session history {session_id}: {str(e)}")
            return []
    
    async def search_conversations(
        self,
        query: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Search through conversation history"""
        try:
            results = []
            
            for sid, messages in self.messages.items():
                if session_id and sid != session_id:
                    continue
                
                for message in messages:
                    # Date filtering
                    if start_date and message.timestamp < start_date:
                        continue
                    if end_date and message.timestamp > end_date:
                        continue
                    
                    # Text search
                    if query.lower() in message.user_message.lower() or \
                       query.lower() in message.ai_response.lower():
                        results.append(message)
                        
                        if len(results) >= limit:
                            break
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            return []
    
    async def flag_message(
        self, 
        session_id: str, 
        message_id: str, 
        admin_notes: Optional[str] = None
    ) -> bool:
        """Flag a message for review"""
        try:
            messages = self.messages.get(session_id, [])
            for message in messages:
                if message.message_id == message_id:
                    message.flagged = True
                    message.admin_notes = admin_notes
                    logger.info(f"Message flagged: {message_id}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error flagging message {message_id}: {str(e)}")
            return False
    
    async def get_analytics(self, refresh: bool = False) -> ChatAnalytics:
        """Get chat analytics"""
        try:
            # Return cached analytics if available and not expired
            if not refresh and self.analytics_cache and self.cache_expiry:
                if datetime.utcnow() < self.cache_expiry:
                    return self.analytics_cache
            
            # Calculate analytics
            total_sessions = len(self.sessions)
            active_sessions = len([s for s in self.sessions.values() if s.is_active])
            
            all_messages = []
            for messages in self.messages.values():
                all_messages.extend(messages)
            
            total_messages = len(all_messages)
            
            # Calculate average response time
            response_times = [m.response_time for m in all_messages if m.response_time > 0]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Calculate total tokens
            total_tokens = sum(m.tokens_used for m in all_messages)
            
            # Sessions by hour (last 24 hours)
            now = datetime.utcnow()
            sessions_by_hour = {}
            for i in range(24):
                hour = (now - timedelta(hours=i)).strftime("%H:00")
                sessions_by_hour[hour] = 0
            
            for session in self.sessions.values():
                hour = session.started_at.strftime("%H:00")
                if hour in sessions_by_hour:
                    sessions_by_hour[hour] += 1
            
            # Error rate
            error_messages = [m for m in all_messages if m.error]
            error_rate = len(error_messages) / total_messages if total_messages > 0 else 0
            
            # Popular topics (simplified - based on common words)
            popular_topics = await self._extract_popular_topics(all_messages)
            
            analytics = ChatAnalytics(
                total_sessions=total_sessions,
                active_sessions=active_sessions,
                total_messages=total_messages,
                average_response_time=avg_response_time,
                total_tokens_used=total_tokens,
                sessions_by_hour=sessions_by_hour,
                popular_topics=popular_topics,
                error_rate=error_rate
            )
            
            # Cache analytics
            self.analytics_cache = analytics
            self.cache_expiry = datetime.utcnow() + timedelta(minutes=5)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error calculating analytics: {str(e)}")
            # Return empty analytics on error
            return ChatAnalytics(
                total_sessions=0,
                active_sessions=0,
                total_messages=0,
                average_response_time=0,
                total_tokens_used=0,
                sessions_by_hour={},
                popular_topics=[],
                error_rate=0
            )
    
    async def get_recent_messages(self, limit: int = 20) -> List[ChatMessage]:
        """Get recent messages across all sessions"""
        try:
            return self.message_queue[-limit:] if self.message_queue else []
        except Exception as e:
            logger.error(f"Error getting recent messages: {str(e)}")
            return []
    
    async def intervene_session(
        self, 
        session_id: str, 
        admin_message: str,
        admin_id: str
    ) -> bool:
        """Admin intervention in a chat session"""
        try:
            session = self.sessions.get(session_id)
            if not session or not session.is_active:
                return False
            
            # Log intervention
            intervention = ChatMessage(
                message_id=f"{session_id}_intervention_{datetime.utcnow().timestamp()}",
                session_id=session_id,
                user_message="[ADMIN INTERVENTION]",
                ai_response=admin_message,
                timestamp=datetime.utcnow(),
                response_time=0,
                tokens_used=0,
                config_used="admin_intervention",
                admin_notes=f"Intervention by admin {admin_id}"
            )
            
            self.messages[session_id].append(intervention)
            
            # Notify active connection if exists
            if session_id in self.active_connections:
                # In a real implementation, this would send a WebSocket message
                pass
            
            logger.info(f"Admin intervention in session {session_id} by {admin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error in admin intervention: {str(e)}")
            return False
    
    # Private helper methods
    
    async def _cleanup_old_sessions(self):
        """Clean up old inactive sessions"""
        try:
            cutoff_time = datetime.utcnow() - self.session_timeout
            sessions_to_remove = []
            
            for session_id, session in self.sessions.items():
                if session.last_activity < cutoff_time:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                if session_id in self.sessions:
                    self.sessions[session_id].is_active = False
                    
            # Keep only recent sessions in memory
            if len(self.sessions) > self.max_sessions:
                # Remove oldest inactive sessions
                inactive_sessions = [
                    (sid, s) for sid, s in self.sessions.items() 
                    if not s.is_active
                ]
                inactive_sessions.sort(key=lambda x: x[1].last_activity)
                
                to_remove = len(self.sessions) - self.max_sessions
                for i in range(min(to_remove, len(inactive_sessions))):
                    session_id = inactive_sessions[i][0]
                    del self.sessions[session_id]
                    if session_id in self.messages:
                        del self.messages[session_id]
                        
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {str(e)}")
    
    async def _extract_popular_topics(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """Extract popular topics from messages"""
        try:
            # Simple word frequency analysis
            word_count = defaultdict(int)
            
            for message in messages[-100:]:  # Last 100 messages
                words = message.user_message.lower().split()
                for word in words:
                    if len(word) > 3:  # Only count words longer than 3 characters
                        word_count[word] += 1
            
            # Get top 10 words
            popular_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return [
                {"topic": word, "count": count} 
                for word, count in popular_words
            ]
            
        except Exception as e:
            logger.error(f"Error extracting popular topics: {str(e)}")
            return []
