import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_router_inclusion():
    """Test that the Discord router is properly included."""
    routes = [route.path for route in app.routes]
    assert "/discord-interaction" in routes
    assert "/health" in routes
