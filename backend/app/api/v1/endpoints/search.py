"""
Advanced Search API Endpoints
Enterprise-grade search functionality with analytics
"""

import logging
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from app.services.advanced_search_service import (
    advanced_search_service,
    SearchType,
    SortOrder,
    SearchFilter,
    SearchResponse
)
from app.services.unified_monitoring_service import unified_monitoring
from app.core.dependencies import get_current_user
from app.core.tracing import trace_async_function

router = APIRouter()
logger = logging.getLogger(__name__)


class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=2, max_length=500)
    search_type: SearchType = SearchType.ALL
    sort_order: SortOrder = SortOrder.RELEVANCE
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    
    # Filters
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    message_type: Optional[str] = None
    has_attachments: Optional[bool] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None


@router.post("/", response_model=SearchResponse)
@trace_async_function("search.execute_search")
async def search(
    request: SearchRequest,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Execute advanced search with filtering and pagination"""
    
    try:
        # Create search filter
        search_filter = SearchFilter(
            date_from=request.date_from,
            date_to=request.date_to,
            user_id=request.user_id,
            session_id=request.session_id,
            message_type=request.message_type,
            has_attachments=request.has_attachments,
            min_length=request.min_length,
            max_length=request.max_length
        )
        
        # Execute search
        results = await advanced_search_service.search(
            query=request.query,
            search_type=request.search_type,
            filters=search_filter,
            sort_order=request.sort_order,
            page=request.page,
            page_size=request.page_size,
            user_id=current_user
        )
        
        # Track search metrics
        unified_monitoring.track_business_metric(
            "search_requests",
            1,
            {
                "search_type": request.search_type.value,
                "result_count": results.total_count,
                "search_time_ms": results.search_time_ms,
                "user_id": current_user or "anonymous"
            }
        )
        
        logger.info(f"Search executed: '{request.query}' -> {results.total_count} results in {results.search_time_ms}ms")
        
        return results
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/quick")
@trace_async_function("search.quick_search")
async def quick_search(
    q: str = Query(..., min_length=2, max_length=200, description="Search query"),
    type: SearchType = Query(SearchType.ALL, description="Search type"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Quick search with minimal parameters"""
    
    try:
        # Execute quick search
        results = await advanced_search_service.search(
            query=q,
            search_type=type,
            page=1,
            page_size=limit,
            user_id=current_user
        )
        
        # Return simplified response
        return {
            "query": q,
            "results": [
                {
                    "id": result.id,
                    "type": result.type,
                    "title": result.title,
                    "snippet": result.snippet,
                    "score": result.score,
                    "timestamp": result.timestamp
                }
                for result in results.results
            ],
            "total_count": results.total_count,
            "search_time_ms": results.search_time_ms
        }
        
    except Exception as e:
        logger.error(f"Quick search error: {e}")
        raise HTTPException(status_code=500, detail="Quick search failed")


@router.get("/suggestions")
@trace_async_function("search.get_suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Partial query"),
    limit: int = Query(5, ge=1, le=20, description="Maximum suggestions"),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get search suggestions based on partial query"""
    
    try:
        suggestions = await advanced_search_service.get_search_suggestions(
            partial_query=q,
            limit=limit,
            user_id=current_user
        )
        
        return {
            "query": q,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Search suggestions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get suggestions")


@router.get("/analytics")
@trace_async_function("search.get_analytics")
async def get_search_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get search analytics and trends"""
    
    try:
        # Check if user has access to analytics
        if not _can_access_analytics(current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        analytics = advanced_search_service.get_search_analytics(days)
        
        return {
            "period_days": days,
            "analytics": analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get search analytics")


@router.get("/trending")
@trace_async_function("search.get_trending")
async def get_trending_searches(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(10, ge=1, le=50, description="Maximum trending queries"),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get trending search queries"""
    
    try:
        trending = await advanced_search_service.get_trending_searches(
            hours=hours,
            limit=limit
        )
        
        return {
            "period_hours": hours,
            "trending_searches": trending,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Trending searches error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trending searches")


@router.get("/popular")
@trace_async_function("search.get_popular")
async def get_popular_searches(
    days: int = Query(7, ge=1, le=90, description="Days to analyze"),
    limit: int = Query(20, ge=1, le=100, description="Maximum popular queries"),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get most popular search queries"""
    
    try:
        popular = await advanced_search_service.get_popular_searches(
            days=days,
            limit=limit
        )
        
        return {
            "period_days": days,
            "popular_searches": popular,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Popular searches error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get popular searches")


@router.post("/feedback")
@trace_async_function("search.submit_feedback")
async def submit_search_feedback(
    query: str = Query(..., description="Original search query"),
    result_id: str = Query(..., description="Result ID that was clicked/selected"),
    feedback_type: str = Query(..., description="Type of feedback: click, helpful, not_helpful"),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Submit feedback on search results for improvement"""
    
    try:
        await advanced_search_service.record_search_feedback(
            query=query,
            result_id=result_id,
            feedback_type=feedback_type,
            user_id=current_user
        )
        
        # Track feedback metrics
        unified_monitoring.track_business_metric(
            "search_feedback",
            1,
            {
                "feedback_type": feedback_type,
                "user_id": current_user or "anonymous"
            }
        )
        
        return {"message": "Feedback recorded successfully"}
        
    except Exception as e:
        logger.error(f"Search feedback error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record feedback")


@router.get("/export")
@trace_async_function("search.export_results")
async def export_search_results(
    query: str = Query(..., description="Search query to export"),
    format: str = Query("json", description="Export format: json, csv"),
    max_results: int = Query(1000, ge=1, le=10000, description="Maximum results to export"),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Export search results for analysis"""
    
    try:
        if not _can_export_data(current_user):
            raise HTTPException(status_code=403, detail="Export access denied")
        
        # Execute search with high limit
        results = await advanced_search_service.search(
            query=query,
            page=1,
            page_size=max_results,
            user_id=current_user
        )
        
        if format.lower() == "csv":
            # Convert to CSV format
            csv_data = await _convert_results_to_csv(results.results)
            return {
                "format": "csv",
                "data": csv_data,
                "total_results": len(results.results)
            }
        else:
            # Return JSON format
            return {
                "format": "json",
                "query": query,
                "results": results.results,
                "total_results": results.total_count,
                "exported_at": datetime.utcnow().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search export error: {e}")
        raise HTTPException(status_code=500, detail="Failed to export search results")


def _can_access_analytics(user_id: Optional[str]) -> bool:
    """Check if user can access search analytics"""
    # In a real implementation, this would check user permissions
    return user_id is not None


def _can_export_data(user_id: Optional[str]) -> bool:
    """Check if user can export search data"""
    # In a real implementation, this would check user permissions
    return user_id and (user_id.endswith("_admin") or user_id.endswith("_analyst"))


async def _convert_results_to_csv(results: List) -> str:
    """Convert search results to CSV format"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["ID", "Type", "Title", "Content", "Score", "Timestamp"])
    
    # Write data
    for result in results:
        writer.writerow([
            result.id,
            result.type,
            result.title,
            result.content[:200] + "..." if len(result.content) > 200 else result.content,
            result.score,
            result.timestamp.isoformat()
        ])
    
    return output.getvalue()
