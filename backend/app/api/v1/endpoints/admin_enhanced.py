from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from app.services.enhanced_chat_service import EnhancedChatService
from app.services.chat_monitoring_service import ChatMonitoringService
from app.services.enhanced_rag_service import EnhancedRAGService
from app.services.document_service import DocumentService
from app.core.dependencies import get_current_user
from app.core.database import DatabaseUtils
from app.api.admin import api_config, rag_config, supabase

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/analytics")
async def get_comprehensive_analytics(
    time_range: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get comprehensive system analytics"""
    try:
        # Initialize services
        chat_service = EnhancedChatService()
        monitoring_service = ChatMonitoringService()
        rag_service = EnhancedRAGService()
        document_service = DocumentService()
        
        # Get analytics from all services
        chat_analytics = await chat_service.get_global_analytics()
        monitoring_analytics = await monitoring_service.get_analytics()
        rag_analytics = await rag_service.get_rag_analytics()
        document_analytics = await document_service.get_analytics()
        
        # Get database stats
        db_stats = await DatabaseUtils.get_database_stats()
        
        # Calculate time-based metrics
        now = datetime.utcnow()
        if time_range == "1h":
            start_time = now - timedelta(hours=1)
        elif time_range == "24h":
            start_time = now - timedelta(days=1)
        elif time_range == "7d":
            start_time = now - timedelta(days=7)
        else:  # 30d
            start_time = now - timedelta(days=30)
        
        # Combine all analytics
        comprehensive_analytics = {
            "chat_metrics": {
                "total_sessions": chat_analytics.get("chat_metrics", {}).get("total_sessions", 0),
                "active_sessions": chat_analytics.get("chat_metrics", {}).get("active_sessions", 0),
                "total_messages": chat_analytics.get("chat_metrics", {}).get("total_messages", 0),
                "total_tokens": chat_analytics.get("chat_metrics", {}).get("total_tokens", 0),
                "average_response_time": monitoring_analytics.get("average_response_time", 0),
                "sessions_by_hour": monitoring_analytics.get("sessions_by_hour", {}),
                "popular_topics": monitoring_analytics.get("popular_topics", []),
                "error_rate": monitoring_analytics.get("error_rate", 0)
            },
            "document_metrics": {
                "total_documents": document_analytics.total_documents,
                "processed_documents": document_analytics.documents_by_status.get("processed", 0),
                "total_chunks": document_analytics.total_chunks,
                "storage_usage": document_analytics.storage_usage.get("disk_usage", 0),
                "documents_by_type": document_analytics.documents_by_type,
                "documents_by_status": document_analytics.documents_by_status
            },
            "security_metrics": {
                "blocked_ips": 0,  # Would come from security service
                "recent_events": 0,  # Would come from security service
                "failed_attempts": 0,  # Would come from security service
                "threat_types": {}  # Would come from security service
            },
            "system_metrics": {
                "uptime": 86400,  # Mock data - would come from system monitoring
                "memory_usage": 65.5,  # Mock data
                "cpu_usage": 23.2,  # Mock data
                "disk_usage": 45.8,  # Mock data
                "response_time": monitoring_analytics.get("average_response_time", 0) * 1000  # Convert to ms
            },
            "database_metrics": db_stats,
            "rag_metrics": rag_analytics,
            "time_range": time_range,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return comprehensive_analytics
        
    except Exception as e:
        logger.error(f"Error getting comprehensive analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")


@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    activity_type: Optional[str] = Query(None),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get recent system activity"""
    try:
        monitoring_service = ChatMonitoringService()
        
        # Get recent messages as activity
        recent_messages = await monitoring_service.get_recent_messages(limit)
        
        # Convert to activity format
        activities = []
        for msg in recent_messages:
            activities.append({
                "id": msg.message_id,
                "type": "chat",
                "message": f"User message processed in session {msg.session_id[:8]}...",
                "timestamp": msg.timestamp.isoformat(),
                "severity": "low" if not msg.error else "high"
            })
        
        # Add mock activities for demo
        activities.extend([
            {
                "id": "doc_001",
                "type": "document",
                "message": "Document uploaded and processed successfully",
                "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "severity": "low"
            },
            {
                "id": "sec_001",
                "type": "security",
                "message": "Rate limit exceeded for IP 192.168.1.100",
                "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                "severity": "medium"
            },
            {
                "id": "sys_001",
                "type": "system",
                "message": "Database backup completed successfully",
                "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "severity": "low"
            }
        ])
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        if activity_type:
            activities = [a for a in activities if a["type"] == activity_type]
        
        return activities[:limit]
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Activity retrieval failed: {str(e)}")


@router.get("/sessions")
async def get_active_sessions(
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get active chat sessions"""
    try:
        monitoring_service = ChatMonitoringService()
        active_sessions = await monitoring_service.get_active_sessions()
        
        return [
            {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "ip_address": session.ip_address,
                "started_at": session.started_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "message_count": session.message_count,
                "config_id": session.config_id
            }
            for session in active_sessions
        ]
        
    except Exception as e:
        logger.error(f"Error getting active sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Session retrieval failed: {str(e)}")


@router.post("/sessions/{session_id}/intervene")
async def admin_intervene_session(
    session_id: str,
    message: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Admin intervention in chat session"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        chat_service = EnhancedChatService()
        success = await chat_service.admin_intervene(
            session_id=session_id,
            admin_message=message,
            admin_id=current_user
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or intervention failed")
        
        return {"message": "Intervention successful", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin intervention: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Intervention failed: {str(e)}")


@router.get("/conversations/search")
async def search_conversations(
    query: str = Query(..., min_length=1),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Search through conversation history"""
    try:
        chat_service = EnhancedChatService()
        
        # Parse dates if provided
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        results = await chat_service.search_conversations(
            query=query,
            start_date=start_dt,
            end_date=end_dt,
            session_id=session_id,
            limit=limit
        )
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "search_time": 0.1  # Mock search time
        }
        
    except Exception as e:
        logger.error(f"Error searching conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/messages/{session_id}/{message_id}/flag")
async def flag_message(
    session_id: str,
    message_id: str,
    admin_notes: Optional[str] = None,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Flag a message for review"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        chat_service = EnhancedChatService()
        success = await chat_service.flag_message(
            session_id=session_id,
            message_id=message_id,
            admin_notes=admin_notes
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return {"message": "Message flagged successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error flagging message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Flag operation failed: {str(e)}")


@router.get("/system/health")
async def get_system_health():
    """Get system health status"""
    try:
        from app.core.database import db_manager
        
        # Check database connection
        db_connected = await db_manager.check_connection()
        
        # Get database info
        db_info = await db_manager.get_database_info()
        
        # Mock other health checks
        health_status = {
            "status": "healthy" if db_connected else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": {
                    "status": "healthy" if db_connected else "unhealthy",
                    "details": db_info
                },
                "redis": {
                    "status": "healthy",  # Mock
                    "details": {"connected": True}
                },
                "ai_services": {
                    "status": "healthy",  # Mock
                    "details": {"openai": True, "anthropic": True}
                },
                "storage": {
                    "status": "healthy",  # Mock
                    "details": {"type": "local", "available": True}
                }
            },
            "metrics": {
                "uptime": 86400,  # Mock
                "memory_usage": 65.5,  # Mock
                "cpu_usage": 23.2,  # Mock
                "disk_usage": 45.8  # Mock
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.post("/system/optimize")
async def optimize_system(
    background_tasks: BackgroundTasks,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Optimize system performance"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Add optimization tasks to background
        background_tasks.add_task(run_system_optimization)
        
        return {
            "message": "System optimization started",
            "estimated_duration": "5-10 minutes",
            "started_by": current_user,
            "started_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting system optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


async def run_system_optimization():
    """Background task for system optimization"""
    try:
        logger.info("Starting system optimization...")
        
        # Optimize RAG system
        rag_service = EnhancedRAGService()
        rag_results = await rag_service.optimize_rag_performance()
        
        # Clean up old sessions
        monitoring_service = ChatMonitoringService()
        await monitoring_service._cleanup_old_sessions()
        
        # Database maintenance (mock)
        # In production, this would run VACUUM, ANALYZE, etc.
        
        logger.info("System optimization completed successfully")
        
    except Exception as e:
        logger.error(f"System optimization failed: {str(e)}")


@router.get("/database/info")
async def get_database_info(
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get database information"""
    try:
        from app.core.database import db_manager
        
        db_info = await db_manager.get_database_info()
        db_stats = await DatabaseUtils.get_database_stats()
        
        return {
            "connection_info": db_info,
            "statistics": db_stats,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting database info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database info retrieval failed: {str(e)}")


@router.get("/export/analytics")
async def export_analytics(
    format: str = Query("json", regex="^(json|csv)$"),
    time_range: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Export analytics data"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get comprehensive analytics
        analytics = await get_comprehensive_analytics(time_range, current_user)
        
        if format == "json":
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content=analytics,
                headers={
                    "Content-Disposition": f"attachment; filename=analytics_{time_range}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                }
            )
        else:  # CSV format
            # Convert to CSV (simplified)
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers and data
            writer.writerow(["Metric", "Value", "Category"])
            
            # Flatten analytics data for CSV
            for category, metrics in analytics.items():
                if isinstance(metrics, dict):
                    for metric, value in metrics.items():
                        writer.writerow([metric, value, category])
            
            from fastapi.responses import StreamingResponse
            output.seek(0)
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=analytics_{time_range}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        
    except Exception as e:
        logger.error(f"Error exporting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# Include configuration sub-routers
router.include_router(api_config.router, prefix="", tags=["admin-api-config"])
router.include_router(rag_config.router, prefix="", tags=["admin-rag-config"])
router.include_router(supabase.router, prefix="", tags=["admin-supabase"])
