import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_config():
    response = client.get("/api/v1/config/default")
    assert response.status_code == 200
    config = response.json()
    assert "id" in config
    assert "name" in config

def test_get_config_not_found():
    response = client.get("/api/v1/config/nonexistent")
    assert response.status_code == 404

def test_create_config():
    config_data = {
        "name": "Test Config",
        "primaryColor": "#ff0000",
        "secondaryColor": "#00ff00",
        "welcomeMessage": "Hello Test"
    }
    response = client.post("/api/v1/config/", json=config_data)
    assert response.status_code == 200
    created_config = response.json()
    assert created_config["name"] == config_data["name"]

def test_update_config():
    config_data = {
        "name": "Updated Config",
        "primaryColor": "#0000ff"
    }
    response = client.put("/api/v1/config/default", json=config_data)
    assert response.status_code == 200
    updated_config = response.json()
    assert updated_config["name"] == config_data["name"]
