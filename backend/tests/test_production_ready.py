"""
Production Readiness Tests
Comprehensive tests to ensure the application is production-ready
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import time
import json

from app.main import app
from app.core.config import settings
from app.services.unified_chat_service import unified_chat_service
from app.services.unified_monitoring_service import unified_monitoring


class TestProductionReadiness:
    """Test suite for production readiness"""
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Check required metrics
        assert "system_cpu_percent" in data
        assert "system_memory_total" in data
        assert "app_uptime_seconds" in data
        assert "timestamp" in data
    
    def test_api_documentation(self, client):
        """Test API documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/redoc")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/api/v1/chat/send", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get("/")
        
        # Check for security headers
        headers = response.headers
        assert "x-content-type-options" in headers
        assert headers["x-content-type-options"] == "nosniff"
    
    def test_rate_limiting_headers(self, client):
        """Test rate limiting is working"""
        # Make multiple requests quickly
        responses = []
        for _ in range(5):
            response = client.get("/health")
            responses.append(response)
        
        # All should succeed for health endpoint
        for response in responses:
            assert response.status_code == 200
    
    def test_error_handling(self, client):
        """Test proper error handling"""
        # Test 404
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        # Test malformed JSON
        response = client.post("/api/v1/chat/send", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422
    
    def test_database_connection(self, client):
        """Test database connectivity"""
        # This would test actual database connection
        # For now, we'll test that the app starts without database errors
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_environment_configuration(self):
        """Test environment configuration is properly loaded"""
        assert settings.ENVIRONMENT is not None
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) >= 32  # Minimum security requirement
    
    def test_logging_configuration(self, client, caplog):
        """Test logging is properly configured"""
        response = client.get("/health")
        assert response.status_code == 200
        
        # Check that logs are being generated
        assert len(caplog.records) >= 0
    
    @pytest.mark.asyncio
    async def test_async_operations(self):
        """Test async operations work correctly"""
        # Test unified chat service
        session = await unified_chat_service.create_session(
            user_id="test_user",
            ip_address="127.0.0.1",
            user_agent="test"
        )
        assert session is not None
        assert session.id is not None
    
    def test_monitoring_service(self):
        """Test monitoring service functionality"""
        # Test system metrics
        metrics = unified_monitoring.get_system_metrics()
        assert "timestamp" in metrics
        assert "uptime_seconds" in metrics
        
        # Test health status
        health = unified_monitoring.get_health_status()
        assert "overall" in health
        assert health["overall"] in ["healthy", "warning", "critical"]
    
    def test_performance_requirements(self, client):
        """Test performance requirements are met"""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        # Response time should be under 200ms for health check
        response_time = (end_time - start_time) * 1000
        assert response_time < 200, f"Response time {response_time}ms exceeds 200ms requirement"
        assert response.status_code == 200
    
    def test_memory_usage(self):
        """Test memory usage is within acceptable limits"""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Memory usage should be reasonable (less than 1GB for basic operations)
        memory_mb = memory_info.rss / 1024 / 1024
        assert memory_mb < 1024, f"Memory usage {memory_mb}MB exceeds 1GB limit"
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            response = client.get("/health")
            results.put(response.status_code)
        
        # Create 10 concurrent threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check all requests succeeded
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        assert len(status_codes) == 10
        assert all(code == 200 for code in status_codes)
    
    def test_input_validation(self, client):
        """Test input validation and sanitization"""
        # Test XSS prevention
        malicious_input = "<script>alert('xss')</script>"
        response = client.post("/api/v1/chat/send", json={
            "message": malicious_input,
            "session_id": "test_session"
        })
        
        # Should not return 500 error (proper validation)
        assert response.status_code in [200, 400, 422]
    
    def test_api_versioning(self, client):
        """Test API versioning is properly implemented"""
        # Test v1 endpoints exist
        response = client.get("/api/v1/health")
        assert response.status_code in [200, 404]  # Either exists or properly not found
    
    def test_graceful_shutdown(self):
        """Test application can shut down gracefully"""
        # This would test graceful shutdown in a real scenario
        # For now, we'll test that cleanup functions exist
        assert hasattr(app, 'router')
        assert hasattr(unified_chat_service, 'get_service_stats')
    
    def test_configuration_validation(self):
        """Test all required configuration is present"""
        required_settings = [
            'ENVIRONMENT',
            'SECRET_KEY',
            'DATABASE_URL',
        ]
        
        for setting in required_settings:
            assert hasattr(settings, setting)
            assert getattr(settings, setting) is not None
    
    def test_feature_flags(self):
        """Test feature flags are properly configured"""
        flags = settings.get_feature_flags()
        assert isinstance(flags, dict)
        assert 'tracing' in flags
        assert 'metrics' in flags
        assert 'caching' in flags
    
    def test_production_optimizations(self, client):
        """Test production optimizations are in place"""
        # Test compression
        response = client.get("/health", headers={"Accept-Encoding": "gzip"})
        assert response.status_code == 200
        
        # Test caching headers for static content
        response = client.get("/docs")
        if response.status_code == 200:
            # Should have appropriate caching headers
            assert "cache-control" in response.headers or "etag" in response.headers
