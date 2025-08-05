"""
Advanced Search Service
Enterprise-grade search functionality with analytics and filtering
"""

import re
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from app.services.unified_chat_service import unified_chat_service
from app.services.unified_monitoring_service import unified_monitoring
from app.core.tracing import trace_async_function

logger = logging.getLogger(__name__)


class SearchType(Enum):
    MESSAGES = "messages"
    SESSIONS = "sessions"
    USERS = "users"
    DOCUMENTS = "documents"
    ALL = "all"


class SortOrder(Enum):
    RELEVANCE = "relevance"
    DATE_ASC = "date_asc"
    DATE_DESC = "date_desc"
    ALPHABETICAL = "alphabetical"


@dataclass
class SearchFilter:
    """Search filter configuration"""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    message_type: Optional[str] = None  # user, assistant, system
    has_attachments: Optional[bool] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None


@dataclass
class SearchResult:
    """Individual search result"""
    id: str
    type: str
    title: str
    content: str
    snippet: str
    score: float
    timestamp: datetime
    metadata: Dict[str, Any]
    highlights: List[str]


@dataclass
class SearchResponse:
    """Search response with results and metadata"""
    query: str
    results: List[SearchResult]
    total_count: int
    page: int
    page_size: int
    search_time_ms: float
    filters_applied: Dict[str, Any]
    suggestions: List[str]
    facets: Dict[str, Dict[str, int]]


class AdvancedSearchService:
    """Advanced search service with full-text search and analytics"""
    
    def __init__(self):
        self.search_analytics = {}
        self.popular_queries = {}
        self.search_suggestions = set()
        
    @trace_async_function("search.execute_search")
    async def search(
        self,
        query: str,
        search_type: SearchType = SearchType.ALL,
        filters: Optional[SearchFilter] = None,
        sort_order: SortOrder = SortOrder.RELEVANCE,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[str] = None
    ) -> SearchResponse:
        """Execute advanced search with filtering and pagination"""
        
        start_time = datetime.utcnow()
        
        try:
            # Validate inputs
            if not query or len(query.strip()) < 2:
                raise ValueError("Query must be at least 2 characters long")
            
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 20
            
            # Clean and prepare query
            cleaned_query = self._clean_query(query)
            search_terms = self._extract_search_terms(cleaned_query)
            
            # Track search analytics
            self._track_search(query, search_type, user_id)
            
            # Execute search based on type
            all_results = []
            
            if search_type in [SearchType.MESSAGES, SearchType.ALL]:
                message_results = await self._search_messages(search_terms, filters, user_id)
                all_results.extend(message_results)
            
            if search_type in [SearchType.SESSIONS, SearchType.ALL]:
                session_results = await self._search_sessions(search_terms, filters, user_id)
                all_results.extend(session_results)
            
            if search_type in [SearchType.DOCUMENTS, SearchType.ALL]:
                document_results = await self._search_documents(search_terms, filters, user_id)
                all_results.extend(document_results)
            
            # Score and rank results
            scored_results = self._score_results(all_results, search_terms)
            
            # Sort results
            sorted_results = self._sort_results(scored_results, sort_order)
            
            # Apply pagination
            total_count = len(sorted_results)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_results = sorted_results[start_idx:end_idx]
            
            # Generate suggestions and facets
            suggestions = self._generate_suggestions(query, all_results)
            facets = self._generate_facets(all_results)
            
            # Calculate search time
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Track performance metrics
            unified_monitoring.track_business_metric(
                "search_queries",
                1,
                {
                    "search_type": search_type.value,
                    "result_count": total_count,
                    "search_time_ms": search_time,
                    "user_id": user_id or "anonymous"
                }
            )
            
            return SearchResponse(
                query=query,
                results=paginated_results,
                total_count=total_count,
                page=page,
                page_size=page_size,
                search_time_ms=search_time,
                filters_applied=self._serialize_filters(filters),
                suggestions=suggestions,
                facets=facets
            )
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    async def _search_messages(
        self,
        search_terms: List[str],
        filters: Optional[SearchFilter],
        user_id: Optional[str]
    ) -> List[SearchResult]:
        """Search chat messages"""
        
        results = []
        
        try:
            # Get active sessions (in a real implementation, this would query the database)
            sessions = await unified_chat_service.get_active_sessions(user_id)
            
            for session in sessions:
                for message in session.messages:
                    # Apply filters
                    if not self._message_matches_filters(message, filters):
                        continue
                    
                    # Check if message matches search terms
                    relevance_score = self._calculate_message_relevance(message.content, search_terms)
                    
                    if relevance_score > 0:
                        # Generate snippet with highlights
                        snippet = self._generate_snippet(message.content, search_terms)
                        highlights = self._generate_highlights(message.content, search_terms)
                        
                        result = SearchResult(
                            id=message.id,
                            type="message",
                            title=f"Message from {message.role}",
                            content=message.content,
                            snippet=snippet,
                            score=relevance_score,
                            timestamp=message.timestamp,
                            metadata={
                                "session_id": session.id,
                                "role": message.role,
                                "user_id": session.user_id,
                                "message_type": message.metadata.get("type", "chat")
                            },
                            highlights=highlights
                        )
                        results.append(result)
            
        except Exception as e:
            logger.error(f"Message search error: {e}")
        
        return results
    
    async def _search_sessions(
        self,
        search_terms: List[str],
        filters: Optional[SearchFilter],
        user_id: Optional[str]
    ) -> List[SearchResult]:
        """Search chat sessions"""
        
        results = []
        
        try:
            sessions = await unified_chat_service.get_active_sessions(user_id)
            
            for session in sessions:
                # Create searchable content from session
                session_content = f"Session {session.id} "
                session_content += " ".join([msg.content for msg in session.messages[:5]])  # First 5 messages
                
                relevance_score = self._calculate_message_relevance(session_content, search_terms)
                
                if relevance_score > 0:
                    snippet = self._generate_snippet(session_content, search_terms, max_length=200)
                    
                    result = SearchResult(
                        id=session.id,
                        type="session",
                        title=f"Chat Session - {session.created_at.strftime('%Y-%m-%d %H:%M')}",
                        content=session_content,
                        snippet=snippet,
                        score=relevance_score,
                        timestamp=session.created_at,
                        metadata={
                            "user_id": session.user_id,
                            "message_count": len(session.messages),
                            "is_active": session.is_active
                        },
                        highlights=self._generate_highlights(session_content, search_terms)
                    )
                    results.append(result)
            
        except Exception as e:
            logger.error(f"Session search error: {e}")
        
        return results
    
    async def _search_documents(
        self,
        search_terms: List[str],
        filters: Optional[SearchFilter],
        user_id: Optional[str]
    ) -> List[SearchResult]:
        """Search uploaded documents"""
        
        results = []
        
        # In a real implementation, this would search through uploaded documents
        # using a proper search engine like Elasticsearch or similar
        
        return results
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize search query"""
        # Remove special characters, normalize whitespace
        cleaned = re.sub(r'[^\w\s\-\.]', ' ', query)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned.lower()
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract individual search terms from query"""
        # Split on whitespace and filter out short terms
        terms = [term.strip() for term in query.split() if len(term.strip()) >= 2]
        return list(set(terms))  # Remove duplicates
    
    def _calculate_message_relevance(self, content: str, search_terms: List[str]) -> float:
        """Calculate relevance score for content against search terms"""
        if not content or not search_terms:
            return 0.0
        
        content_lower = content.lower()
        score = 0.0
        
        for term in search_terms:
            term_lower = term.lower()
            
            # Exact match bonus
            if term_lower in content_lower:
                score += 1.0
                
                # Word boundary match bonus
                if re.search(r'\b' + re.escape(term_lower) + r'\b', content_lower):
                    score += 0.5
                
                # Count occurrences
                occurrences = content_lower.count(term_lower)
                score += min(occurrences * 0.1, 0.5)  # Cap bonus at 0.5
        
        # Normalize by content length (favor shorter, more relevant content)
        if len(content) > 0:
            score = score / (len(content) / 100)  # Normalize per 100 characters
        
        return min(score, 10.0)  # Cap maximum score
    
    def _generate_snippet(self, content: str, search_terms: List[str], max_length: int = 150) -> str:
        """Generate snippet with search term context"""
        if not content:
            return ""
        
        # Find best snippet location
        best_pos = 0
        best_score = 0
        
        for term in search_terms:
            pos = content.lower().find(term.lower())
            if pos != -1:
                # Score based on term importance and position
                score = len(term) / (pos + 1)
                if score > best_score:
                    best_score = score
                    best_pos = max(0, pos - 50)
        
        # Extract snippet
        snippet = content[best_pos:best_pos + max_length]
        
        # Clean up snippet boundaries
        if best_pos > 0:
            snippet = "..." + snippet
        if len(content) > best_pos + max_length:
            snippet = snippet + "..."
        
        return snippet.strip()
    
    def _generate_highlights(self, content: str, search_terms: List[str]) -> List[str]:
        """Generate highlighted terms in content"""
        highlights = []
        content_lower = content.lower()
        
        for term in search_terms:
            term_lower = term.lower()
            if term_lower in content_lower:
                # Find actual case-preserved matches
                pattern = re.compile(re.escape(term_lower), re.IGNORECASE)
                matches = pattern.findall(content)
                highlights.extend(matches[:3])  # Limit to 3 matches per term
        
        return list(set(highlights))  # Remove duplicates
    
    def _message_matches_filters(self, message, filters: Optional[SearchFilter]) -> bool:
        """Check if message matches search filters"""
        if not filters:
            return True
        
        # Date filters
        if filters.date_from and message.timestamp < filters.date_from:
            return False
        if filters.date_to and message.timestamp > filters.date_to:
            return False
        
        # Message type filter
        if filters.message_type and message.role != filters.message_type:
            return False
        
        # Length filters
        if filters.min_length and len(message.content) < filters.min_length:
            return False
        if filters.max_length and len(message.content) > filters.max_length:
            return False
        
        # Attachment filter
        if filters.has_attachments is not None:
            has_attachments = bool(getattr(message, 'attachments', None))
            if has_attachments != filters.has_attachments:
                return False
        
        return True
    
    def _score_results(self, results: List[SearchResult], search_terms: List[str]) -> List[SearchResult]:
        """Apply additional scoring to results"""
        for result in results:
            # Boost recent results
            days_old = (datetime.utcnow() - result.timestamp).days
            recency_boost = max(0, 1 - (days_old / 30))  # Boost decreases over 30 days
            result.score += recency_boost * 0.2
            
            # Boost results with more highlights
            highlight_boost = len(result.highlights) * 0.1
            result.score += highlight_boost
        
        return results
    
    def _sort_results(self, results: List[SearchResult], sort_order: SortOrder) -> List[SearchResult]:
        """Sort results according to specified order"""
        if sort_order == SortOrder.RELEVANCE:
            return sorted(results, key=lambda r: r.score, reverse=True)
        elif sort_order == SortOrder.DATE_DESC:
            return sorted(results, key=lambda r: r.timestamp, reverse=True)
        elif sort_order == SortOrder.DATE_ASC:
            return sorted(results, key=lambda r: r.timestamp)
        elif sort_order == SortOrder.ALPHABETICAL:
            return sorted(results, key=lambda r: r.title.lower())
        else:
            return results
    
    def _generate_suggestions(self, query: str, results: List[SearchResult]) -> List[str]:
        """Generate search suggestions based on results"""
        suggestions = []
        
        # Add popular related queries
        if query in self.popular_queries:
            related = self.popular_queries[query].get("related", [])
            suggestions.extend(related[:3])
        
        # Add suggestions based on result content
        if results:
            # Extract common terms from top results
            top_results = results[:5]
            common_terms = set()
            
            for result in top_results:
                words = result.content.lower().split()
                common_terms.update([w for w in words if len(w) > 3])
            
            # Filter and add relevant terms
            relevant_terms = [term for term in common_terms if term not in query.lower()]
            suggestions.extend(relevant_terms[:2])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _generate_facets(self, results: List[SearchResult]) -> Dict[str, Dict[str, int]]:
        """Generate search facets for filtering"""
        facets = {
            "type": {},
            "date_range": {},
            "user": {}
        }
        
        for result in results:
            # Type facet
            result_type = result.type
            facets["type"][result_type] = facets["type"].get(result_type, 0) + 1
            
            # Date range facet
            days_old = (datetime.utcnow() - result.timestamp).days
            if days_old <= 1:
                date_range = "today"
            elif days_old <= 7:
                date_range = "this_week"
            elif days_old <= 30:
                date_range = "this_month"
            else:
                date_range = "older"
            
            facets["date_range"][date_range] = facets["date_range"].get(date_range, 0) + 1
            
            # User facet
            user_id = result.metadata.get("user_id", "unknown")
            facets["user"][user_id] = facets["user"].get(user_id, 0) + 1
        
        return facets
    
    def _serialize_filters(self, filters: Optional[SearchFilter]) -> Dict[str, Any]:
        """Serialize filters for response"""
        if not filters:
            return {}
        
        return {
            "date_from": filters.date_from.isoformat() if filters.date_from else None,
            "date_to": filters.date_to.isoformat() if filters.date_to else None,
            "user_id": filters.user_id,
            "session_id": filters.session_id,
            "message_type": filters.message_type,
            "has_attachments": filters.has_attachments,
            "min_length": filters.min_length,
            "max_length": filters.max_length
        }
    
    def _track_search(self, query: str, search_type: SearchType, user_id: Optional[str]):
        """Track search analytics"""
        # Update search analytics
        if query not in self.search_analytics:
            self.search_analytics[query] = {
                "count": 0,
                "first_searched": datetime.utcnow(),
                "last_searched": datetime.utcnow(),
                "users": set()
            }
        
        self.search_analytics[query]["count"] += 1
        self.search_analytics[query]["last_searched"] = datetime.utcnow()
        if user_id:
            self.search_analytics[query]["users"].add(user_id)
    
    def get_search_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get search analytics for the specified period"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        recent_searches = {
            query: data for query, data in self.search_analytics.items()
            if data["last_searched"] > cutoff_date
        }

        # Sort by popularity
        popular_queries = sorted(
            recent_searches.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:10]

        return {
            "total_searches": sum(data["count"] for data in recent_searches.values()),
            "unique_queries": len(recent_searches),
            "popular_queries": [
                {
                    "query": query,
                    "count": data["count"],
                    "unique_users": len(data["users"])
                }
                for query, data in popular_queries
            ],
            "period_days": days
        }

    async def get_search_suggestions(self, partial_query: str, limit: int = 5, user_id: Optional[str] = None) -> List[str]:
        """Get search suggestions based on partial query"""
        suggestions = []

        # Get suggestions from search history
        for query in self.search_analytics.keys():
            if partial_query.lower() in query.lower() and query != partial_query:
                suggestions.append(query)

        # Sort by popularity and limit
        suggestions = sorted(suggestions, key=lambda q: self.search_analytics[q]["count"], reverse=True)
        return suggestions[:limit]

    async def get_trending_searches(self, hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending search queries"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        trending = []
        for query, data in self.search_analytics.items():
            if data["last_searched"] > cutoff_time:
                trending.append({
                    "query": query,
                    "count": data["count"],
                    "trend_score": data["count"] / max(1, (datetime.utcnow() - data["last_searched"]).total_seconds() / 3600)
                })

        # Sort by trend score
        trending = sorted(trending, key=lambda x: x["trend_score"], reverse=True)
        return trending[:limit]

    async def get_popular_searches(self, days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most popular search queries"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        popular = []
        for query, data in self.search_analytics.items():
            if data["last_searched"] > cutoff_date:
                popular.append({
                    "query": query,
                    "count": data["count"],
                    "unique_users": len(data["users"]),
                    "avg_daily_searches": data["count"] / days
                })

        # Sort by count
        popular = sorted(popular, key=lambda x: x["count"], reverse=True)
        return popular[:limit]

    async def record_search_feedback(self, query: str, result_id: str, feedback_type: str, user_id: Optional[str] = None):
        """Record feedback on search results"""
        if query not in self.search_analytics:
            return

        if "feedback" not in self.search_analytics[query]:
            self.search_analytics[query]["feedback"] = []

        self.search_analytics[query]["feedback"].append({
            "result_id": result_id,
            "feedback_type": feedback_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow()
        })


# Global search service instance
advanced_search_service = AdvancedSearchService()
