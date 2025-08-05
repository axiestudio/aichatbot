from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging
import uuid
from datetime import datetime

from app.models.chat import ChatRequest, ChatResponse, ChatMessage, ChatSession
from app.services.enhanced_chat_service import EnhancedChatService
from app.services.enhanced_rag_service import EnhancedRAGService
from app.services.chat_monitoring_service import ChatMonitoringService
from app.core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Send a message to the chatbot and get a response with enhanced RAG"""
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")

        # Initialize enhanced services
        chat_service = EnhancedChatService()

        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Create or get enhanced session
        if not request.session_id:
            session = await chat_service.create_session_enhanced(
                user_id=current_user,
                config_id=request.config_id,
                ip_address="127.0.0.1",  # Would get from request in real implementation
                user_agent="api-client"
            )
            session_id = session.id

        # Send message with enhanced processing
        response_data = await chat_service.send_message_enhanced(
            session_id=session_id,
            message=request.message,
            config_id=request.config_id,
            context_strategy="comprehensive" if request.use_rag else "none"
        )

        logger.info(f"Generated enhanced response for session {session_id}")

        return ChatResponse(
            response=response_data["response"],
            session_id=session_id,
            message_id=response_data["message_id"],
            sources=response_data.get("context_metadata", {}).get("sources", []),
            metadata={
                "response_time": response_data["response_time"],
                "tokens_used": response_data["tokens_used"],
                "context_metadata": response_data.get("context_metadata", {})
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get a chat session by ID"""
    try:
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Delete a chat session"""
    try:
        success = await chat_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete session")


@router.get("/sessions", response_model=List[ChatSession])
async def list_chat_sessions(
    limit: int = 50,
    offset: int = 0,
    chat_service: ChatService = Depends(get_chat_service)
):
    """List chat sessions with pagination"""
    try:
        sessions = await chat_service.list_sessions(limit=limit, offset=offset)
        return sessions
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")
