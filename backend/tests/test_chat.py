import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Modern Chatbot Backend API" in response.json()["message"]

def test_chat_message():
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "Hello", "conversation_id": "test"}
    )
    assert response.status_code == 200
    assert "response" in response.json()

def test_chat_message_empty():
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "", "conversation_id": "test"}
    )
    assert response.status_code == 422

def test_chat_history():
    response = client.get("/api/v1/chat/history/test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
