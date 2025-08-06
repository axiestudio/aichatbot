"""
Advanced Intelligence API Endpoints
Conversation intelligence, content moderation, and knowledge graph APIs
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
from datetime import datetime

from ....services.conversation_intelligence_service import conversation_intelligence_service
from ....services.content_moderation_service import content_moderation_service
from ....services.knowledge_graph_service import knowledge_graph_service
from ....services.realtime_collaboration_service import realtime_collaboration_service
from ....core.dependencies import get_current_admin_user

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


# Conversation Intelligence Endpoints
@router.post("/conversation/analyze")
async def analyze_conversation_message(
    data: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_admin_user)
):
    """Analyze a conversation message for sentiment, intent, and insights"""
    try:
        message = data.get("message", "")
        session_id = data.get("session_id", "")
        message_id = data.get("message_id", "")
        role = data.get("role", "user")
        
        if not message or not session_id:
            raise HTTPException(status_code=400, detail="Message and session_id are required")
        
        insight = await conversation_intelligence_service.analyze_message(
            message, session_id, message_id, role
        )
        
        if insight:
            return {
                "insight": {
                    "sentiment": insight.sentiment.value,
                    "intent": insight.intent.value,
                    "confidence": insight.confidence,
                    "emotions": insight.emotions,
                    "topics": insight.topics,
                    "urgency_score": insight.urgency_score,
                    "satisfaction_score": insight.satisfaction_score,
                    "complexity_score": insight.complexity_score
                },
                "timestamp": insight.timestamp.isoformat()
            }
        else:
            return {"message": "No insights generated"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/conversation/summary/{session_id}")
async def get_conversation_summary(
    session_id: str,
    current_user = Depends(get_current_admin_user)
):
    """Get conversation summary and insights"""
    try:
        summary = await conversation_intelligence_service.get_conversation_summary(session_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


# Content Moderation Endpoints
@router.post("/moderation/analyze")
async def moderate_content(
    data: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_admin_user)
):
    """Moderate content for safety and compliance"""
    try:
        content = data.get("content", "")
        user_id = data.get("user_id")
        context = data.get("context", {})
        
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        result = await content_moderation_service.moderate_content(content, user_id, context)
        
        return {
            "moderation_result": {
                "action": result.action.value,
                "toxicity_level": result.toxicity_level.value,
                "categories": [cat.value for cat in result.categories],
                "confidence": result.confidence,
                "reasoning": result.reasoning,
                "flagged_terms": result.flagged_terms,
                "ai_safety_score": result.ai_safety_score
            },
            "timestamp": result.timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Moderation failed: {str(e)}")


@router.get("/moderation/stats")
async def get_moderation_stats(
    timeframe_hours: int = Query(24, description="Timeframe in hours"),
    current_user = Depends(get_current_admin_user)
):
    """Get content moderation statistics"""
    try:
        stats = await content_moderation_service.get_moderation_stats(timeframe_hours)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/moderation/feedback")
async def report_false_positive(
    data: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_admin_user)
):
    """Report false positive for model improvement"""
    try:
        content_id = data.get("content_id", "")
        feedback = data.get("feedback", "")
        
        if not content_id or not feedback:
            raise HTTPException(status_code=400, detail="Content ID and feedback are required")
        
        await content_moderation_service.report_false_positive(content_id, feedback)
        return {"message": "Feedback recorded successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {str(e)}")


# Knowledge Graph Endpoints
@router.post("/knowledge/extract")
async def extract_knowledge(
    data: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_admin_user)
):
    """Extract knowledge from text"""
    try:
        text = data.get("text", "")
        source_id = data.get("source_id")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        result = await knowledge_graph_service.extract_knowledge_from_text(text, source_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge extraction failed: {str(e)}")


@router.get("/knowledge/query")
async def query_knowledge(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum results"),
    current_user = Depends(get_current_admin_user)
):
    """Query knowledge graph"""
    try:
        results = await knowledge_graph_service.query_knowledge(q, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge query failed: {str(e)}")


@router.get("/knowledge/entity/{entity_id}")
async def get_entity_details(
    entity_id: str,
    current_user = Depends(get_current_admin_user)
):
    """Get detailed information about an entity"""
    try:
        details = await knowledge_graph_service.get_entity_details(entity_id)
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entity details: {str(e)}")


@router.get("/knowledge/stats")
async def get_knowledge_stats(
    current_user = Depends(get_current_admin_user)
):
    """Get knowledge graph statistics"""
    try:
        stats = await knowledge_graph_service.get_knowledge_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge stats: {str(e)}")


# Real-Time Collaboration Endpoints
@router.post("/collaboration/join")
async def join_collaboration_session(
    data: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_admin_user)
):
    """Join a collaboration session"""
    try:
        user_id = data.get("user_id", "")
        session_id = data.get("session_id", "")
        user_data = data.get("user_data", {})
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="User ID and session ID are required")
        
        user = await realtime_collaboration_service.user_join_session(user_id, session_id, user_data)
        
        if user:
            return {
                "message": "Successfully joined collaboration session",
                "user": {
                    "user_id": user.user_id,
                    "name": user.name,
                    "presence": user.presence.value,
                    "permissions": user.permissions
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to join session")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join session: {str(e)}")


@router.post("/collaboration/leave")
async def leave_collaboration_session(
    data: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_admin_user)
):
    """Leave a collaboration session"""
    try:
        user_id = data.get("user_id", "")
        session_id = data.get("session_id", "")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="User ID and session ID are required")
        
        await realtime_collaboration_service.user_leave_session(user_id, session_id)
        return {"message": "Successfully left collaboration session"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to leave session: {str(e)}")


@router.get("/collaboration/session/{session_id}")
async def get_collaboration_session_state(
    session_id: str,
    current_user = Depends(get_current_admin_user)
):
    """Get collaboration session state"""
    try:
        state = await realtime_collaboration_service.get_session_state(session_id)
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session state: {str(e)}")


@router.post("/collaboration/typing")
async def update_typing_status(
    data: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_admin_user)
):
    """Update typing status"""
    try:
        user_id = data.get("user_id", "")
        session_id = data.get("session_id", "")
        is_typing = data.get("is_typing", False)
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="User ID and session ID are required")
        
        if is_typing:
            await realtime_collaboration_service.start_typing(user_id, session_id)
        else:
            await realtime_collaboration_service.stop_typing(user_id, session_id)
        
        return {"message": "Typing status updated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update typing status: {str(e)}")


# Combined Intelligence Endpoint
@router.post("/analyze-comprehensive")
async def comprehensive_analysis(
    data: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_admin_user)
):
    """Comprehensive analysis combining all intelligence services"""
    try:
        content = data.get("content", "")
        session_id = data.get("session_id", "")
        user_id = data.get("user_id")
        context = data.get("context", {})
        
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Run all analyses in parallel
        import asyncio
        
        tasks = []
        
        # Conversation intelligence
        if session_id:
            tasks.append(conversation_intelligence_service.analyze_message(
                content, session_id, f"msg_{datetime.utcnow().timestamp()}", "user"
            ))
        
        # Content moderation
        tasks.append(content_moderation_service.moderate_content(content, user_id, context))
        
        # Knowledge extraction
        tasks.append(knowledge_graph_service.extract_knowledge_from_text(content))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        response = {
            "content": content[:100] + "..." if len(content) > 100 else content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Process conversation intelligence result
        if len(results) > 0 and not isinstance(results[0], Exception) and results[0]:
            insight = results[0]
            response["conversation_intelligence"] = {
                "sentiment": insight.sentiment.value,
                "intent": insight.intent.value,
                "confidence": insight.confidence,
                "emotions": insight.emotions,
                "topics": insight.topics,
                "urgency_score": insight.urgency_score,
                "satisfaction_score": insight.satisfaction_score
            }
        
        # Process moderation result
        if len(results) > 1 and not isinstance(results[1], Exception):
            moderation = results[1]
            response["content_moderation"] = {
                "action": moderation.action.value,
                "toxicity_level": moderation.toxicity_level.value,
                "categories": [cat.value for cat in moderation.categories],
                "confidence": moderation.confidence,
                "ai_safety_score": moderation.ai_safety_score
            }
        
        # Process knowledge extraction result
        if len(results) > 2 and not isinstance(results[2], Exception):
            knowledge = results[2]
            response["knowledge_extraction"] = {
                "entities_found": len(knowledge.get("entities", [])),
                "relationships_found": len(knowledge.get("relationships", [])),
                "entities": knowledge.get("entities", [])[:5],  # Top 5 entities
                "relationships": knowledge.get("relationships", [])[:5]  # Top 5 relationships
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")
