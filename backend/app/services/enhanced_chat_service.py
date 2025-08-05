from typing import List, Optional, Dict, Any
import logging
import uuid
import time
from datetime import datetime, timedelta

from app.models.chat import ChatSession, ChatMessage, ChatConfig
from app.services.chat_service import ChatService
from app.services.enhanced_rag_service import EnhancedRAGService
from app.services.chat_monitoring_service import ChatMonitoringService
from app.core.config import settings

logger = logging.getLogger(__name__)


class EnhancedChatService(ChatService):
    """Enhanced chat service with RAG integration and monitoring"""
    
    def __init__(self):
        super().__init__()
        self.rag_service = EnhancedRAGService()
        self.monitoring_service = ChatMonitoringService()
        
    async def create_session_enhanced(
        self,
        user_id: Optional[str] = None,
        config_id: Optional[str] = None,
        ip_address: str = "unknown",
        user_agent: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """Create enhanced chat session with monitoring"""
        session_id = str(uuid.uuid4())
        
        # Start monitoring session
        monitoring_session = await self.monitoring_service.start_session(
            session_id=session_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            config_id=config_id,
            metadata=metadata
        )
        
        # Create chat session
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            config_id=config_id or "default",
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            is_active=True,
            metadata=metadata
        )
        
        self.sessions[session_id] = session
        
        logger.info(f"Enhanced chat session created: {session_id}")
        return session
    
    async def send_message_enhanced(
        self,
        session_id: str,
        message: str,
        config_id: Optional[str] = None,
        context_strategy: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Send message with enhanced RAG and monitoring"""
        start_time = time.time()
        
        try:
            # Get session
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
            
            # Update session activity
            session.last_activity = datetime.utcnow()
            
            # Get enhanced context from RAG
            context, context_metadata = await self.rag_service.generate_enhanced_context(
                query=message,
                config_id=config_id or session.config_id,
                context_strategy=context_strategy
            )
            
            # Generate AI response (simplified for demo)
            ai_response = await self._generate_ai_response_enhanced(
                message=message,
                context=context,
                config_id=config_id or session.config_id
            )
            
            # Calculate response time and tokens
            response_time = time.time() - start_time
            tokens_used = self._estimate_tokens(message + ai_response)
            
            # Create message record
            chat_message = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                user_message=message,
                ai_response=ai_response,
                timestamp=datetime.utcnow(),
                config_id=config_id or session.config_id,
                metadata={
                    "context_strategy": context_strategy,
                    "context_metadata": context_metadata,
                    "response_time": response_time,
                    "tokens_used": tokens_used
                }
            )
            
            # Store message
            if session_id not in self.messages:
                self.messages[session_id] = []
            self.messages[session_id].append(chat_message)
            
            # Log to monitoring service
            await self.monitoring_service.log_message(
                session_id=session_id,
                user_message=message,
                ai_response=ai_response,
                response_time=response_time,
                tokens_used=tokens_used,
                config_used=config_id or session.config_id,
                rag_context=[source["name"] for source in context_metadata.get("sources", [])]
            )
            
            logger.info(f"Enhanced message processed for session {session_id} in {response_time:.2f}s")
            
            return {
                "message_id": chat_message.id,
                "response": ai_response,
                "context_metadata": context_metadata,
                "response_time": response_time,
                "tokens_used": tokens_used,
                "timestamp": chat_message.timestamp.isoformat()
            }
            
        except Exception as e:
            # Log error to monitoring
            await self.monitoring_service.log_message(
                session_id=session_id,
                user_message=message,
                ai_response="",
                response_time=time.time() - start_time,
                tokens_used=0,
                config_used=config_id or "default",
                error=str(e)
            )
            
            logger.error(f"Error processing message for session {session_id}: {str(e)}")
            raise
    
    async def _generate_ai_response_enhanced(
        self,
        message: str,
        context: str,
        config_id: str
    ) -> str:
        """Generate AI response with enhanced context"""
        try:
            # Get chat configuration
            config = self.configs.get(config_id, self.configs["default"])
            
            # Build enhanced prompt
            system_prompt = f"""You are a helpful AI assistant. Use the provided context to answer user questions accurately and helpfully.

Context Information:
{context}

Guidelines:
- Always be helpful and professional
- Use the context provided to give accurate answers
- If the context doesn't contain relevant information, politely say so
- Keep responses concise but informative
- Maintain a friendly and professional tone"""

            # For demo purposes, return a simple response
            # In production, this would call OpenAI/Anthropic API
            if context and context.strip():
                response = f"Based on the available information, {message.lower()}. I found relevant context that helps me provide you with accurate information. How can I assist you further?"
            else:
                response = f"I understand you're asking about {message.lower()}. While I don't have specific context for this query, I'm here to help. Could you provide more details or ask about something specific?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "I apologize, but I encountered an error while processing your request. Please try again."
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    async def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a specific session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return {"error": "Session not found"}
            
            messages = self.messages.get(session_id, [])
            
            # Calculate session metrics
            total_messages = len(messages)
            total_tokens = sum(msg.metadata.get("tokens_used", 0) for msg in messages)
            avg_response_time = sum(msg.metadata.get("response_time", 0) for msg in messages) / total_messages if total_messages > 0 else 0
            
            # Get session duration
            if messages:
                duration = (messages[-1].timestamp - session.created_at).total_seconds()
            else:
                duration = (datetime.utcnow() - session.created_at).total_seconds()
            
            return {
                "session_id": session_id,
                "total_messages": total_messages,
                "total_tokens": total_tokens,
                "average_response_time": avg_response_time,
                "session_duration": duration,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "is_active": session.is_active
            }
            
        except Exception as e:
            logger.error(f"Error getting session analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_global_analytics(self) -> Dict[str, Any]:
        """Get global chat analytics"""
        try:
            # Get monitoring analytics
            monitoring_analytics = await self.monitoring_service.get_analytics()
            
            # Get RAG analytics
            rag_analytics = await self.rag_service.get_rag_analytics()
            
            # Calculate additional metrics
            total_sessions = len(self.sessions)
            active_sessions = len([s for s in self.sessions.values() if s.is_active])
            
            all_messages = []
            for messages in self.messages.values():
                all_messages.extend(messages)
            
            total_messages = len(all_messages)
            total_tokens = sum(msg.metadata.get("tokens_used", 0) for msg in all_messages)
            
            return {
                "chat_metrics": {
                    "total_sessions": total_sessions,
                    "active_sessions": active_sessions,
                    "total_messages": total_messages,
                    "total_tokens": total_tokens
                },
                "monitoring_analytics": monitoring_analytics,
                "rag_analytics": rag_analytics,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting global analytics: {str(e)}")
            return {"error": str(e)}
    
    async def admin_intervene(
        self,
        session_id: str,
        admin_message: str,
        admin_id: str
    ) -> bool:
        """Admin intervention in chat session"""
        try:
            # Use monitoring service for intervention
            success = await self.monitoring_service.intervene_session(
                session_id=session_id,
                admin_message=admin_message,
                admin_id=admin_id
            )
            
            if success:
                # Also add to chat messages
                intervention_message = ChatMessage(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_message="[ADMIN INTERVENTION]",
                    ai_response=admin_message,
                    timestamp=datetime.utcnow(),
                    config_id="admin_intervention",
                    metadata={
                        "admin_id": admin_id,
                        "intervention": True
                    }
                )
                
                if session_id not in self.messages:
                    self.messages[session_id] = []
                self.messages[session_id].append(intervention_message)
                
                logger.info(f"Admin intervention successful in session {session_id} by {admin_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in admin intervention: {str(e)}")
            return False
    
    async def end_session_enhanced(self, session_id: str) -> bool:
        """End session with monitoring"""
        try:
            # End in monitoring service
            await self.monitoring_service.end_session(session_id)
            
            # End in chat service
            session = self.sessions.get(session_id)
            if session:
                session.is_active = False
                session.last_activity = datetime.utcnow()
                logger.info(f"Enhanced chat session ended: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {str(e)}")
            return False
    
    async def search_conversations(
        self,
        query: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search through conversation history"""
        try:
            # Use monitoring service for search
            results = await self.monitoring_service.search_conversations(
                query=query,
                start_date=start_date,
                end_date=end_date,
                session_id=session_id,
                limit=limit
            )
            
            # Convert to dict format
            return [
                {
                    "message_id": result.message_id,
                    "session_id": result.session_id,
                    "user_message": result.user_message,
                    "ai_response": result.ai_response,
                    "timestamp": result.timestamp.isoformat(),
                    "flagged": result.flagged,
                    "admin_notes": result.admin_notes
                }
                for result in results
            ]
            
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
            return await self.monitoring_service.flag_message(
                session_id=session_id,
                message_id=message_id,
                admin_notes=admin_notes
            )
        except Exception as e:
            logger.error(f"Error flagging message: {str(e)}")
            return False
