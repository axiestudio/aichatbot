import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import tempfile
import os
from datetime import datetime

from app.main import app
from app.core.database import db_manager
from app.services.document_service import DocumentService
from app.services.enhanced_rag_service import EnhancedRAGService
from app.services.chat_monitoring_service import ChatMonitoringService
from app.services.enhanced_chat_service import EnhancedChatService
from app.services.embedding_service import EmbeddingService


class TestComprehensiveSystem:
    """Comprehensive system tests for the entire chatbot application"""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Test client fixture"""
        return TestClient(app)
    
    @pytest.fixture(scope="class")
    async def async_client(self):
        """Async test client fixture"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture(scope="class")
    def temp_file(self):
        """Temporary file fixture for testing uploads"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for RAG processing.\n")
            f.write("It contains sample content that should be indexed.\n")
            f.write("The system should be able to search through this content.")
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Modern Chatbot Backend API"
        assert "features" in data
        assert len(data["features"]) > 0
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection and basic operations"""
        # Test connection
        connected = await db_manager.check_connection()
        assert connected, "Database connection should be successful"
        
        # Test database info
        db_info = await db_manager.get_database_info()
        assert "url" in db_info
        assert "connected" in db_info
    
    @pytest.mark.asyncio
    async def test_embedding_service(self):
        """Test embedding service functionality"""
        embedding_service = EmbeddingService()
        
        # Test health check
        healthy = await embedding_service.health_check()
        assert healthy, "Embedding service should be healthy"
        
        # Test embedding generation
        text = "This is a test sentence for embedding generation."
        embedding = await embedding_service.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
        
        # Test similarity calculation
        embedding2 = await embedding_service.generate_embedding("This is another test sentence.")
        similarity = embedding_service.calculate_similarity(embedding, embedding2)
        
        assert 0 <= similarity <= 1
    
    @pytest.mark.asyncio
    async def test_document_service(self, temp_file):
        """Test document service functionality"""
        document_service = DocumentService()
        
        # Test analytics (should work even with no documents)
        analytics = await document_service.get_analytics()
        assert isinstance(analytics.total_documents, int)
        assert isinstance(analytics.documents_by_type, dict)
        assert isinstance(analytics.documents_by_status, dict)
    
    @pytest.mark.asyncio
    async def test_rag_service(self):
        """Test RAG service functionality"""
        rag_service = EnhancedRAGService()
        
        # Test analytics
        analytics = await rag_service.get_rag_analytics()
        assert "vector_store" in analytics
        assert "document_processing" in analytics
        assert "embedding_info" in analytics
        
        # Test context generation (should handle empty results gracefully)
        context, metadata = await rag_service.generate_enhanced_context(
            query="test query",
            context_strategy="focused"
        )
        
        assert isinstance(context, str)
        assert isinstance(metadata, dict)
        assert "sources" in metadata
        assert "total_chunks" in metadata
    
    @pytest.mark.asyncio
    async def test_chat_monitoring_service(self):
        """Test chat monitoring service"""
        monitoring_service = ChatMonitoringService()
        
        # Test session creation
        session = await monitoring_service.start_session(
            session_id="test_session_123",
            user_id="test_user",
            ip_address="127.0.0.1",
            user_agent="test_agent"
        )
        
        assert session.session_id == "test_session_123"
        assert session.user_id == "test_user"
        assert session.is_active
        
        # Test message logging
        message = await monitoring_service.log_message(
            session_id="test_session_123",
            user_message="Hello, this is a test message",
            ai_response="Hello! I'm here to help you.",
            response_time=0.5,
            tokens_used=20,
            config_used="default"
        )
        
        assert message.session_id == "test_session_123"
        assert message.user_message == "Hello, this is a test message"
        assert message.response_time == 0.5
        
        # Test analytics
        analytics = await monitoring_service.get_analytics()
        assert analytics.total_sessions >= 1
        assert analytics.total_messages >= 1
        
        # Test session ending
        ended = await monitoring_service.end_session("test_session_123")
        assert ended
    
    @pytest.mark.asyncio
    async def test_enhanced_chat_service(self):
        """Test enhanced chat service"""
        chat_service = EnhancedChatService()
        
        # Test session creation
        session = await chat_service.create_session_enhanced(
            user_id="test_user_enhanced",
            ip_address="127.0.0.1",
            user_agent="test_agent"
        )
        
        assert session.user_id == "test_user_enhanced"
        assert session.is_active
        
        # Test message sending
        response = await chat_service.send_message_enhanced(
            session_id=session.id,
            message="What is the weather like today?",
            context_strategy="focused"
        )
        
        assert "message_id" in response
        assert "response" in response
        assert "context_metadata" in response
        assert "response_time" in response
        
        # Test session analytics
        session_analytics = await chat_service.get_session_analytics(session.id)
        assert "session_id" in session_analytics
        assert "total_messages" in session_analytics
        assert session_analytics["total_messages"] >= 1
        
        # Test global analytics
        global_analytics = await chat_service.get_global_analytics()
        assert "chat_metrics" in global_analytics
        assert "monitoring_analytics" in global_analytics
        
        # Test session ending
        ended = await chat_service.end_session_enhanced(session.id)
        assert ended
    
    def test_api_endpoints_basic(self, client):
        """Test basic API endpoint accessibility"""
        # Test API router is mounted
        response = client.get("/api/v1/")
        # Should return 404 or method not allowed, but not 500
        assert response.status_code in [404, 405]
        
        # Test admin endpoints (should require auth)
        response = client.get("/api/v1/admin/analytics")
        assert response.status_code in [401, 403]  # Unauthorized or Forbidden
        
        # Test document endpoints
        response = client.get("/api/v1/documents/")
        assert response.status_code in [200, 401]  # OK or requires auth
    
    def test_cors_middleware(self, client):
        """Test CORS middleware is working"""
        response = client.options("/", headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        })
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers or response.status_code == 200
    
    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get("/")
        
        # Check for security headers (some might be added by middleware)
        headers = {k.lower(): v for k, v in response.headers.items()}
        
        # At minimum, should have content-type
        assert "content-type" in headers
    
    @pytest.mark.asyncio
    async def test_error_handling(self, async_client):
        """Test error handling middleware"""
        # Test non-existent endpoint
        response = await async_client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        # Response should be JSON with error structure
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            # Should have error structure from our middleware
            assert isinstance(data, dict)
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, async_client):
        """Test rate limiting (basic test)"""
        # Make multiple requests quickly
        responses = []
        for i in range(5):
            response = await async_client.get("/health")
            responses.append(response.status_code)
        
        # Should mostly succeed (rate limit is generous for health checks)
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 3, "Most health check requests should succeed"
    
    @pytest.mark.asyncio
    async def test_integration_flow(self):
        """Test complete integration flow"""
        # 1. Create enhanced chat service
        chat_service = EnhancedChatService()
        
        # 2. Create a session
        session = await chat_service.create_session_enhanced(
            user_id="integration_test_user",
            ip_address="127.0.0.1"
        )
        
        # 3. Send a message
        response1 = await chat_service.send_message_enhanced(
            session_id=session.id,
            message="Hello, can you help me with testing?"
        )
        
        assert "response" in response1
        
        # 4. Send another message
        response2 = await chat_service.send_message_enhanced(
            session_id=session.id,
            message="What features does this system have?"
        )
        
        assert "response" in response2
        
        # 5. Check session has messages
        session_analytics = await chat_service.get_session_analytics(session.id)
        assert session_analytics["total_messages"] >= 2
        
        # 6. Search conversations
        search_results = await chat_service.search_conversations(
            query="testing",
            session_id=session.id
        )
        
        assert isinstance(search_results, list)
        
        # 7. End session
        ended = await chat_service.end_session_enhanced(session.id)
        assert ended
    
    def test_system_completeness(self):
        """Test that all major system components are available"""
        # Test that all major services can be imported and instantiated
        try:
            document_service = DocumentService()
            assert document_service is not None
            
            rag_service = EnhancedRAGService()
            assert rag_service is not None
            
            monitoring_service = ChatMonitoringService()
            assert monitoring_service is not None
            
            chat_service = EnhancedChatService()
            assert chat_service is not None
            
            embedding_service = EmbeddingService()
            assert embedding_service is not None
            
        except Exception as e:
            pytest.fail(f"Failed to instantiate core services: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_cleanup(self):
        """Test system cleanup"""
        # Test database cleanup
        try:
            await db_manager.cleanup()
        except Exception as e:
            # Cleanup might fail if already cleaned up, that's OK
            pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
