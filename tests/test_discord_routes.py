import pytest
from fastapi.testclient import TestClient
from nacl.signing import SigningKey
import json
from src.routes.discord import router, get_verify_key
from fastapi import FastAPI

# Create a test app and add the router
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Create a signing key pair for testing
signing_key = SigningKey.generate()
verify_key = signing_key.verify_key

def create_signed_headers(body: str, timestamp: str = "1234567890"):
    """Create signed headers for Discord interaction testing."""
    signature = signing_key.sign(f"{timestamp}{body}".encode()).signature.hex()
    return {
        "X-Signature-Ed25519": signature,
        "X-Signature-Timestamp": timestamp
    }

@pytest.fixture
def ping_payload():
    return json.dumps({"type": 1})

@pytest.fixture
def command_payload():
    return json.dumps({
        "type": 2,
        "data": {
            "name": "test_command"
        }
    })

def test_ping_interaction(ping_payload, monkeypatch):
    """Test handling of Discord ping interaction."""
    # Mock the verify key
    monkeypatch.setattr("src.routes.discord.get_verify_key", lambda: verify_key)
    
    headers = create_signed_headers(ping_payload)
    response = client.post(
        "/discord-interaction",
        headers=headers,
        content=ping_payload
    )
    
    assert response.status_code == 200
    assert response.json() == {"type": 1}

def test_invalid_signature(ping_payload, monkeypatch):
    """Test handling of invalid signatures."""
    # Mock the verify key
    monkeypatch.setattr("src.routes.discord.get_verify_key", lambda: verify_key)
    
    headers = {
        "X-Signature-Ed25519": "invalid",
        "X-Signature-Timestamp": "1234567890"
    }
    response = client.post(
        "/discord-interaction",
        headers=headers,
        content=ping_payload
    )
    
    assert response.status_code == 401

def test_missing_headers(ping_payload):
    """Test handling of missing headers."""
    response = client.post(
        "/discord-interaction",
        content=ping_payload
    )
    
    assert response.status_code == 401

def test_command_interaction(command_payload, monkeypatch):
    """Test handling of Discord command interaction."""
    # Mock the verify key
    monkeypatch.setattr("src.routes.discord.get_verify_key", lambda: verify_key)
    
    headers = create_signed_headers(command_payload)
    response = client.post(
        "/discord-interaction",
        headers=headers,
        content=command_payload
    )
    
    assert response.status_code == 200 