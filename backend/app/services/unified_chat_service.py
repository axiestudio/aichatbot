"""
Unified Chat Service
Consolidated chat functionality with RAG, monitoring, and caching
"""

import time
import uuid
import logging
import asyncio
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta

from app.models.chat import ChatSession, ChatMessage, ChatConfig
from app.models.database import ApiConfiguration, RagInstruction, LiveConfiguration
from app.services.advanced_cache_service import cache_service, cached, CacheConfig
from app.services.circuit_breaker_service import circuit_breaker, CircuitBreakerConfig
from app.services.performance_monitoring_service import performance_service, performance_monitor
from app.services.error_tracking_service import error_tracker
from app.services.websocket_manager import websocket_manager
from app.core.config import settings
from app.core.database import get_db
from sqlalchemy.orm import Session
import openai
import anthropic

logger = logging.getLogger(__name__)


class UnifiedChatService:
    """
    Unified chat service combining all chat functionality:
    - Session management
    - Message processing
    - RAG integration
    - Performance monitoring
    - Error tracking
    - Caching
    - Circuit breaker protection
    """
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.configs: Dict[str, ChatConfig] = {}
        self._initialize_default_config()
        
        # Circuit breaker configurations
        self.openai_breaker_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30,
            timeout=30.0
        )
        
        # Cache configurations
        self.session_cache_config = CacheConfig(
            ttl=3600,  # 1 hour
            max_size=1000
        )
        
        self.response_cache_config = CacheConfig(
            ttl=1800,  # 30 minutes
            max_size=500
        )

        # WebSocket manager for real-time updates
        self.websocket_manager = websocket_manager
    
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

    async def get_live_config(self, instance_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get live configuration for an instance"""
        try:
            config = db.query(LiveConfiguration).filter(
                LiveConfiguration.instance_id == instance_id,
                LiveConfiguration.is_active == True
            ).first()

            if config:
                return {
                    "chat_title": config.chat_title,
                    "chat_subtitle": config.chat_subtitle,
                    "welcome_message": config.welcome_message,
                    "placeholder_text": config.placeholder_text,
                    "primary_color": config.primary_color,
                    "secondary_color": config.secondary_color,
                    "accent_color": config.accent_color,
                    "background_color": config.background_color,
                    "text_color": config.text_color,
                    "logo_url": config.logo_url,
                    "company_name": config.company_name,
                    "show_branding": config.show_branding,
                    "custom_css": config.custom_css,
                    "typing_indicator": config.typing_indicator,
                    "sound_enabled": config.sound_enabled,
                    "auto_scroll": config.auto_scroll,
                    "message_timestamps": config.message_timestamps,
                    "file_upload_enabled": config.file_upload_enabled,
                    "max_file_size_mb": config.max_file_size_mb,
                    "allowed_file_types": config.allowed_file_types,
                    "messages_per_minute": config.messages_per_minute,
                    "messages_per_hour": config.messages_per_hour,
                    "conversation_starters": config.conversation_starters,
                    "quick_replies": config.quick_replies,
                    "custom_fields": config.custom_fields
                }

            return None

        except Exception as e:
            logger.error(f"Error getting live config for instance {instance_id}: {e}")
            return None

    async def apply_rate_limits(self, instance_id: str, user_id: str, db: Session) -> bool:
        """Apply rate limiting based on live configuration"""
        try:
            config = await self.get_live_config(instance_id, db)
            if not config:
                return True  # Allow if no config found

            # Check rate limits (simplified implementation)
            # In production, you'd use Redis or similar for distributed rate limiting
            current_time = datetime.utcnow()

            # For now, just return True (rate limiting would be implemented with Redis)
            return True

        except Exception as e:
            logger.error(f"Error applying rate limits: {e}")
            return True  # Allow on error

    def _get_active_api_config(self, db: Session) -> ApiConfiguration:
        """Get active API configuration from database"""
        config = db.query(ApiConfiguration).filter(ApiConfiguration.is_active == True).first()
        if not config:
            # Create default config if none exists
            config = ApiConfiguration(
                id="default",
                name="Default OpenAI",
                provider="openai",
                api_key=settings.OPENAI_API_KEY or "your-api-key-here",
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=1000,
                is_active=True
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        return config

    def _get_active_rag_config(self, db: Session) -> RagInstruction:
        """Get active RAG instruction from database"""
        config = db.query(RagInstruction).filter(RagInstruction.is_active == True).first()
        if not config:
            # Create default config if none exists
            config = RagInstruction(
                id="default",
                name="Default RAG",
                system_prompt="You are a helpful AI assistant. Use the provided context to answer questions accurately.",
                context_prompt="Context: {context}\n\nQuestion: {question}",
                max_context_length=2000,
                search_limit=5,
                similarity_threshold=0.7,
                is_active=True
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        return config
    
    @performance_monitor("chat.create_session")
    @cached(key_prefix="chat_session", ttl=3600)
    async def create_session(
        self,
        user_id: Optional[str] = None,
        config_id: Optional[str] = None,
        ip_address: str = "unknown",
        user_agent: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """Create a new chat session with comprehensive tracking"""
        
        try:
            session_id = str(uuid.uuid4())
            config = self.configs.get(config_id, self.configs["default"])
            
            session = ChatSession(
                id=session_id,
                user_id=user_id,
                config_id=config.id,
                messages=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True,
                metadata={
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "config_name": config.name,
                    **(metadata or {})
                }
            )
            
            # Add welcome message if configured
            if config.welcome_message:
                welcome_msg = ChatMessage(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    role="assistant",
                    content=config.welcome_message,
                    timestamp=datetime.utcnow(),
                    metadata={"type": "welcome"}
                )
                session.messages.append(welcome_msg)
            
            self.sessions[session_id] = session
            
            # Track session creation
            performance_service.track_custom_metric(
                "chat.session_created",
                1,
                {"config_id": config.id, "user_id": user_id or "anonymous"}
            )
            
            logger.info(f"Created chat session {session_id} for user {user_id}")
            return session
            
        except Exception as e:
            error_tracker.track_error(
                e,
                context={
                    "operation": "create_session",
                    "user_id": user_id,
                    "config_id": config_id
                },
                severity="error"
            )
            raise
    
    @performance_monitor("chat.send_message")
    @circuit_breaker("openai_api")
    async def send_message(
        self,
        session_id: str,
        message: str,
        user_id: Optional[str] = None,
        message_type: str = "user",
        db: Session = None
    ) -> ChatMessage:
        """Send a message and get AI response with full monitoring"""
        
        start_time = time.time()
        
        try:
            # Validate session
            session = await self._get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Create user message
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role="user",
                content=message,
                timestamp=datetime.utcnow(),
                metadata={
                    "user_id": user_id,
                    "type": message_type,
                    "ip_address": session.metadata.get("ip_address"),
                    "user_agent": session.metadata.get("user_agent")
                }
            )
            
            session.messages.append(user_message)
            session.updated_at = datetime.utcnow()
            
            # Get database session if not provided
            if db is None:
                db = next(get_db())

            # Generate AI response with caching
            response_content = await self._generate_ai_response(
                session_id, message, session.messages, db
            )
            
            # Create assistant message
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role="assistant",
                content=response_content,
                timestamp=datetime.utcnow(),
                metadata={
                    "model": "gpt-3.5-turbo",  # This would be dynamic
                    "response_time": time.time() - start_time,
                    "cached": False  # This would be set by cache layer
                }
            )
            
            session.messages.append(assistant_message)
            
            # Update session cache
            await cache_service.set(
                f"session:{session_id}",
                session,
                config=self.session_cache_config
            )
            
            # Track message metrics
            duration = time.time() - start_time
            performance_service.track_custom_metric(
                "chat.message_processed",
                duration,
                {
                    "session_id": session_id,
                    "user_id": user_id or "anonymous",
                    "message_length": len(message),
                    "response_length": len(response_content)
                }
            )
            
            logger.info(
                f"Processed message in session {session_id}, "
                f"response time: {duration:.2f}s"
            )
            
            return assistant_message
            
        except Exception as e:
            error_tracker.track_error(
                e,
                context={
                    "operation": "send_message",
                    "session_id": session_id,
                    "user_id": user_id,
                    "message_length": len(message) if message else 0
                },
                severity="error"
            )
            raise
    
    @cached(key_prefix="ai_response", ttl=1800)
    async def _generate_ai_response(
        self,
        session_id: str,
        message: str,
        conversation_history: List[ChatMessage],
        db: Session
    ) -> str:
        """Generate AI response using configured API provider"""

        try:
            # Get active API configuration
            api_config = self._get_active_api_config(db)
            rag_config = self._get_active_rag_config(db)

            # Build context from conversation history
            context_messages = []

            # Add system prompt from RAG config
            context_messages.append({
                "role": "system",
                "content": rag_config.system_prompt
            })

            # Add conversation history
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                context_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Add current message
            context_messages.append({
                "role": "user",
                "content": message
            })

            # Generate response using configured provider
            if api_config.provider.lower() == "openai":
                return await self._generate_openai_response(api_config, context_messages)
            elif api_config.provider.lower() == "anthropic":
                return await self._generate_anthropic_response(api_config, context_messages)
            else:
                return f"I'm sorry, but the configured AI provider '{api_config.provider}' is not supported yet."

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."

    async def _generate_openai_response(self, api_config: ApiConfiguration, messages: List[dict]) -> str:
        """Generate response using OpenAI API"""
        try:
            client = openai.AsyncOpenAI(api_key=api_config.api_key)

            response = await client.chat.completions.create(
                model=api_config.model,
                messages=messages,
                temperature=api_config.temperature,
                max_tokens=api_config.max_tokens,
                top_p=api_config.top_p,
                frequency_penalty=api_config.frequency_penalty,
                presence_penalty=api_config.presence_penalty
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"OpenAI API error: {str(e)}"

    async def _generate_anthropic_response(self, api_config: ApiConfiguration, messages: List[dict]) -> str:
        """Generate response using Anthropic API"""
        try:
            client = anthropic.AsyncAnthropic(api_key=api_config.api_key)

            # Convert messages format for Anthropic
            system_message = ""
            anthropic_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            response = await client.messages.create(
                model=api_config.model,
                max_tokens=api_config.max_tokens,
                temperature=api_config.temperature,
                system=system_message,
                messages=anthropic_messages
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return f"Anthropic API error: {str(e)}"
            response = f"I understand you said: '{message}'. How can I help you further?"
            
            return response
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."
    
    @cached(key_prefix="session", ttl=3600)
    async def _get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session with caching"""
        
        # Try memory first
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Try cache
        cached_session = await cache_service.get(
            f"session:{session_id}",
            config=self.session_cache_config
        )
        
        if cached_session:
            self.sessions[session_id] = cached_session
            return cached_session
        
        return None
    
    async def get_session_history(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatMessage]:
        """Get session message history with pagination"""
        
        try:
            session = await self._get_session(session_id)
            if not session:
                return []
            
            messages = session.messages[offset:offset + limit]
            
            performance_service.track_custom_metric(
                "chat.history_retrieved",
                len(messages),
                {"session_id": session_id, "limit": limit, "offset": offset}
            )
            
            return messages
            
        except Exception as e:
            error_tracker.track_error(
                e,
                context={
                    "operation": "get_session_history",
                    "session_id": session_id,
                    "limit": limit,
                    "offset": offset
                },
                severity="warning"
            )
            return []
    
    async def get_active_sessions(self, user_id: Optional[str] = None) -> List[ChatSession]:
        """Get active sessions, optionally filtered by user"""
        
        try:
            active_sessions = [
                session for session in self.sessions.values()
                if session.is_active and (not user_id or session.user_id == user_id)
            ]
            
            performance_service.track_custom_metric(
                "chat.active_sessions_retrieved",
                len(active_sessions),
                {"user_id": user_id or "all"}
            )
            
            return active_sessions
            
        except Exception as e:
            error_tracker.track_error(
                e,
                context={
                    "operation": "get_active_sessions",
                    "user_id": user_id
                },
                severity="warning"
            )
            return []
    
    async def close_session(self, session_id: str) -> bool:
        """Close a chat session"""
        
        try:
            session = await self._get_session(session_id)
            if not session:
                return False
            
            session.is_active = False
            session.updated_at = datetime.utcnow()
            
            # Update cache
            await cache_service.set(
                f"session:{session_id}",
                session,
                config=self.session_cache_config
            )
            
            performance_service.track_custom_metric(
                "chat.session_closed",
                1,
                {"session_id": session_id}
            )
            
            logger.info(f"Closed chat session {session_id}")
            return True
            
        except Exception as e:
            error_tracker.track_error(
                e,
                context={
                    "operation": "close_session",
                    "session_id": session_id
                },
                severity="warning"
            )
            return False
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get comprehensive service statistics"""
        
        total_sessions = len(self.sessions)
        active_sessions = len([s for s in self.sessions.values() if s.is_active])
        total_messages = sum(len(s.messages) for s in self.sessions.values())
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "cache_stats": cache_service.get_stats(),
            "performance_stats": performance_service.get_performance_alerts(),
            "error_stats": error_tracker.get_error_analytics(24)
        }


# Global unified chat service instance
unified_chat_service = UnifiedChatService()
