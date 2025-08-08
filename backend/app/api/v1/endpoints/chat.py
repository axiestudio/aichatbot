from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging
import uuid
from datetime import datetime

from app.models.database import ChatMessage, ChatSession
from app.services.unified_chat_service import unified_chat_service
from app.services.rag_service import RAGService

# Create basic request/response models
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    config_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    timestamp: datetime
from app.core.dependencies import get_current_user, get_chat_service, get_rag_service
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    chat_service = Depends(get_chat_service),
    rag_service = Depends(get_rag_service),
    current_user: Optional[str] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to the chatbot and get a response with RAG support"""
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")

        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Create or get session
        if not request.session_id:
            session = await chat_service.create_session(
                user_id=current_user,
                config_id=request.config_id,
                ip_address="127.0.0.1",  # Would get from request in real implementation
                user_agent="api-client"
            )
            session_id = session.id

        # Send message with unified service
        response_message = await chat_service.send_message(
            session_id=session_id,
            message=request.message,
            user_id=current_user,
            db=db
        )

        logger.info(f"Generated response for session {session_id}")

        return ChatResponse(
            response=response_message.content,
            session_id=session_id,
            message_id=response_message.id,
            sources=[],  # Would be populated by RAG service
            metadata={
                "response_time": response_message.metadata.get("response_time", 0),
                "tokens_used": 0,  # Would be tracked by AI service
                "timestamp": response_message.timestamp.isoformat()
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
