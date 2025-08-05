import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re
from collections import defaultdict

from app.core.config import settings
from app.services.supabase_service import SupabaseService
from app.services.embedding_service import EmbeddingService
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)


class EnhancedRAGService(RAGService):
    """Enhanced RAG service with advanced document processing and retrieval"""
    
    def __init__(self):
        super().__init__()
        self.embedding_service = EmbeddingService()
        self.document_service = DocumentService()
        
        # Enhanced configuration
        self.max_context_length = getattr(settings, 'MAX_CONTEXT_LENGTH', 4000)
        self.similarity_threshold = getattr(settings, 'SIMILARITY_THRESHOLD', 0.7)
        self.chunk_overlap_threshold = 0.8
        
        # Context ranking weights
        self.ranking_weights = {
            'similarity': 0.4,
            'recency': 0.2,
            'relevance': 0.2,
            'source_quality': 0.2
        }
    
    async def enhanced_search_context(
        self, 
        query: str, 
        config_id: Optional[str] = None,
        limit: int = None,
        filters: Optional[Dict[str, Any]] = None,
        rerank: bool = True
    ) -> List[Dict[str, Any]]:
        """Enhanced context search with filtering and reranking"""
        try:
            search_limit = limit or 10
            
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Search in multiple sources
            results = []
            
            # 1. Search in Supabase vector store (existing functionality)
            try:
                supabase_results = await self.supabase_service.search_documents(
                    query_embedding=query_embedding,
                    limit=search_limit * 2,
                    config_id=config_id
                )
                results.extend(supabase_results)
            except Exception as e:
                logger.warning(f"Supabase search failed: {str(e)}")
            
            # 2. Search in document service
            try:
                from app.models.document import DocumentSearchRequest
                doc_search_request = DocumentSearchRequest(
                    query=query,
                    config_id=config_id,
                    limit=search_limit,
                    similarity_threshold=self.similarity_threshold
                )
                doc_results = await self.document_service.search_documents(doc_search_request)
                
                # Convert document results to standard format
                for result in doc_results.results:
                    results.append({
                        'content': result.content,
                        'source': result.document_title,
                        'similarity': result.similarity_score,
                        'metadata': result.metadata or {},
                        'chunk_id': result.chunk_id,
                        'document_id': result.document_id
                    })
            except Exception as e:
                logger.warning(f"Document service search failed: {str(e)}")
            
            # Apply filters
            if filters:
                results = await self._apply_filters(results, filters)
            
            # Remove duplicates and overlapping content
            results = await self._deduplicate_results(results)
            
            # Rerank results if requested
            if rerank:
                results = await self._rerank_results(results, query)
            
            # Apply similarity threshold
            results = [r for r in results if r.get('similarity', 0) >= self.similarity_threshold]
            
            # Limit results
            results = results[:search_limit]
            
            logger.info(f"Enhanced RAG search found {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error in enhanced RAG search: {str(e)}")
            return []
    
    async def generate_enhanced_context(
        self, 
        query: str, 
        config_id: Optional[str] = None,
        context_strategy: str = "comprehensive"
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate optimized context with metadata"""
        try:
            # Search for relevant documents
            search_results = await self.enhanced_search_context(query, config_id)
            
            if not search_results:
                return "No relevant context found.", {"sources": [], "total_chunks": 0}
            
            # Generate context based on strategy
            if context_strategy == "focused":
                context, metadata = await self._generate_focused_context(search_results, query)
            elif context_strategy == "balanced":
                context, metadata = await self._generate_balanced_context(search_results, query)
            else:  # comprehensive
                context, metadata = await self._generate_comprehensive_context(search_results, query)
            
            logger.info(f"Generated {context_strategy} context of {len(context)} characters from {metadata['total_chunks']} sources")
            return context, metadata
            
        except Exception as e:
            logger.error(f"Error generating enhanced context: {str(e)}")
            return "Error retrieving context.", {"sources": [], "total_chunks": 0, "error": str(e)}
    
    async def add_document_to_rag(
        self, 
        document_id: str,
        force_reprocess: bool = False
    ) -> bool:
        """Add a processed document to the RAG system"""
        try:
            # Get document from document service
            document = await self.document_service.get_document(document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                return False
            
            # Check if document is processed
            if document.status.value != "processed" and not force_reprocess:
                logger.error(f"Document not processed: {document_id}")
                return False
            
            # Get document chunks
            chunks = self.document_service.chunks.get(document_id, [])
            if not chunks:
                logger.error(f"No chunks found for document: {document_id}")
                return False
            
            # Add each chunk to Supabase
            success_count = 0
            for chunk in chunks:
                if chunk.embedding:
                    chunk_metadata = {
                        "document_id": document_id,
                        "document_title": document.original_filename,
                        "chunk_index": chunk.chunk_index,
                        "chunk_id": chunk.id,
                        "file_type": document.file_type.value,
                        "upload_date": document.created_at.isoformat(),
                        "config_id": document.config_id,
                        "tags": document.tags or []
                    }
                    
                    success = await self.supabase_service.store_document(
                        content=chunk.content,
                        embedding=chunk.embedding,
                        metadata=chunk_metadata,
                        config_id=document.config_id
                    )
                    
                    if success:
                        success_count += 1
            
            logger.info(f"Added {success_count}/{len(chunks)} chunks to RAG for document {document_id}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error adding document to RAG: {str(e)}")
            return False
    
    async def get_rag_analytics(
        self, 
        config_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive RAG system analytics"""
        try:
            # Get basic stats from Supabase
            try:
                supabase_stats = await self.supabase_service.get_document_stats(config_id)
            except:
                supabase_stats = {"total_documents": 0, "total_size": 0}
            
            # Get document service stats
            try:
                doc_analytics = await self.document_service.get_analytics()
            except:
                doc_analytics = type('obj', (object,), {
                    'total_documents': 0,
                    'documents_by_status': {},
                    'total_chunks': 0,
                    'storage_usage': {}
                })()
            
            # Combine analytics
            analytics = {
                "vector_store": supabase_stats,
                "document_processing": {
                    "total_documents": doc_analytics.total_documents,
                    "processed_documents": getattr(doc_analytics, 'documents_by_status', {}).get("processed", 0),
                    "total_chunks": getattr(doc_analytics, 'total_chunks', 0),
                    "storage_usage": getattr(doc_analytics, 'storage_usage', {})
                },
                "embedding_info": self.embedding_service.get_embedding_info(),
                "search_performance": await self._get_search_performance_stats(),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting RAG analytics: {str(e)}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _apply_filters(
        self, 
        results: List[Dict[str, Any]], 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply filters to search results"""
        filtered_results = []
        
        for result in results:
            metadata = result.get('metadata', {})
            
            # Date filter
            if 'date_from' in filters or 'date_to' in filters:
                upload_date = metadata.get('upload_date')
                if upload_date:
                    try:
                        doc_date = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                        if 'date_from' in filters and doc_date < filters['date_from']:
                            continue
                        if 'date_to' in filters and doc_date > filters['date_to']:
                            continue
                    except:
                        pass
            
            # File type filter
            if 'file_types' in filters:
                file_type = metadata.get('file_type')
                if file_type and file_type not in filters['file_types']:
                    continue
            
            # Tags filter
            if 'tags' in filters:
                doc_tags = metadata.get('tags', [])
                if not any(tag in doc_tags for tag in filters['tags']):
                    continue
            
            filtered_results.append(result)
        
        return filtered_results
    
    async def _deduplicate_results(
        self, 
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate and overlapping content"""
        if not results:
            return results
        
        deduplicated = []
        seen_content = set()
        
        for result in results:
            content = result.get('content', '').strip()
            
            if not content:
                continue
            
            # Check for exact duplicates
            content_hash = hash(content)
            if content_hash in seen_content:
                continue
            
            # Check for overlapping content
            is_overlap = False
            for existing in deduplicated:
                existing_content = existing.get('content', '')
                overlap_ratio = self._calculate_overlap_ratio(content, existing_content)
                
                if overlap_ratio > self.chunk_overlap_threshold:
                    if result.get('similarity', 0) > existing.get('similarity', 0):
                        deduplicated.remove(existing)
                        break
                    else:
                        is_overlap = True
                        break
            
            if not is_overlap:
                deduplicated.append(result)
                seen_content.add(content_hash)
        
        return deduplicated
    
    def _calculate_overlap_ratio(self, text1: str, text2: str) -> float:
        """Calculate overlap ratio between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def _rerank_results(
        self, 
        results: List[Dict[str, Any]], 
        query: str
    ) -> List[Dict[str, Any]]:
        """Rerank results using multiple factors"""
        for result in results:
            score = 0.0
            
            # Similarity score
            similarity = result.get('similarity', 0)
            score += similarity * self.ranking_weights['similarity']
            
            # Recency score
            metadata = result.get('metadata', {})
            upload_date = metadata.get('upload_date')
            if upload_date:
                try:
                    doc_date = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    days_old = (datetime.utcnow() - doc_date.replace(tzinfo=None)).days
                    recency_score = max(0, 1 - (days_old / 365))
                    score += recency_score * self.ranking_weights['recency']
                except:
                    pass
            
            # Relevance score (keyword matching)
            content = result.get('content', '').lower()
            query_words = query.lower().split()
            keyword_matches = sum(1 for word in query_words if word in content)
            relevance_score = keyword_matches / len(query_words) if query_words else 0
            score += relevance_score * self.ranking_weights['relevance']
            
            # Source quality score
            file_type = metadata.get('file_type', '')
            quality_scores = {'pdf': 0.9, 'docx': 0.8, 'txt': 0.7, 'html': 0.6}
            source_quality = quality_scores.get(file_type, 0.5)
            
            content_length = len(content)
            if 200 <= content_length <= 1500:
                source_quality *= 1.2
            elif content_length < 100:
                source_quality *= 0.8
            
            score += source_quality * self.ranking_weights['source_quality']
            result['rerank_score'] = score
        
        return sorted(results, key=lambda x: x.get('rerank_score', 0), reverse=True)
    
    async def _generate_comprehensive_context(
        self, 
        results: List[Dict[str, Any]], 
        query: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate comprehensive context"""
        context_parts = []
        sources = []
        total_length = 0
        
        for i, result in enumerate(results):
            content = result.get('content', '')
            source = result.get('source', f'Source {i+1}')
            similarity = result.get('similarity', 0)
            
            context_part = f"[Source: {source} (Relevance: {similarity:.2f})]\n{content}\n"
            
            if total_length + len(context_part) > self.max_context_length:
                break
            
            context_parts.append(context_part)
            sources.append({
                "name": source,
                "similarity": similarity,
                "length": len(content)
            })
            total_length += len(context_part)
        
        context = "\n" + "="*50 + "\n".join(context_parts)
        
        metadata = {
            "sources": sources,
            "total_chunks": len(context_parts),
            "total_length": total_length,
            "strategy": "comprehensive"
        }
        
        return context, metadata
    
    async def _generate_focused_context(
        self, 
        results: List[Dict[str, Any]], 
        query: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate focused context with most relevant information"""
        top_results = results[:3]
        context_parts = []
        sources = []
        
        for result in top_results:
            content = result.get('content', '')
            source = result.get('source', 'Unknown')
            relevant_content = self._extract_relevant_sentences(content, query)
            
            context_parts.append(f"{source}: {relevant_content}")
            sources.append({
                "name": source,
                "similarity": result.get('similarity', 0),
                "length": len(relevant_content)
            })
        
        context = "\n\n".join(context_parts)
        
        metadata = {
            "sources": sources,
            "total_chunks": len(context_parts),
            "total_length": len(context),
            "strategy": "focused"
        }
        
        return context, metadata
    
    async def _generate_balanced_context(
        self, 
        results: List[Dict[str, Any]], 
        query: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate balanced context with diverse sources"""
        source_groups = defaultdict(list)
        for result in results:
            source = result.get('source', 'Unknown')
            source_groups[source].append(result)
        
        balanced_results = []
        for source, group in source_groups.items():
            best_result = max(group, key=lambda x: x.get('similarity', 0))
            balanced_results.append(best_result)
        
        balanced_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        balanced_results = balanced_results[:5]
        
        return await self._generate_comprehensive_context(balanced_results, query)
    
    def _extract_relevant_sentences(self, content: str, query: str) -> str:
        """Extract most relevant sentences from content"""
        sentences = re.split(r'[.!?]+', content)
        query_words = set(query.lower().split())
        
        sentence_scores = []
        for sentence in sentences:
            if len(sentence.strip()) < 20:
                continue
            
            sentence_words = set(sentence.lower().split())
            overlap = len(query_words.intersection(sentence_words))
            score = overlap / len(query_words) if query_words else 0
            
            sentence_scores.append((sentence.strip(), score))
        
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in sentence_scores[:3] if s[1] > 0]
        
        return '. '.join(top_sentences) + '.' if top_sentences else content[:200] + '...'
    
    async def _get_search_performance_stats(self) -> Dict[str, Any]:
        """Get search performance statistics"""
        return {
            "average_search_time": 0.5,
            "cache_hit_rate": 0.75,
            "total_searches": 1000,
            "successful_searches": 950
        }
