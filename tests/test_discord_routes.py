import pytest
from fastapi.testclient import TestClient
from nacl.signing import SigningKey
import json
from src.routes.discord import router, get_verify_key
from fastapi import FastAPI
from config import config  # Import the config module

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
    # Use mock values for testing
    mock_guild_id = "123456789"
    mock_application_id = "1313573192371273788"  # Mock application ID
    
    return json.dumps({
        "type": 2,  # APPLICATION_COMMAND
        "id": "123456789",  # Test ID can be mock value
        "application_id": mock_application_id,  # Use mock application ID instead of config
        "channel_id": "987654321",  # Test ID can be mock value
        "guild_id": mock_guild_id,
        "data": {
            "id": "987654321",
            "name": "test_command",
            "type": 1
        },
        "member": {
            "user": {
                "id": "123456789",
                "username": "test_user",
                "discriminator": "1234"
            }
        },
        "token": "mock_token",
        "version": 1
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
    
    # Create a test payload with a specific command
    payload = json.loads(command_payload)
    payload["data"] = {"name": "githubsub", "options": [{"name": "repository", "value": "owner/repo"}]}
    command_payload = json.dumps(payload)
    
    headers = create_signed_headers(command_payload)
    response = client.post(
        "/discord-interaction",
        headers=headers,
        content=command_payload
    )
    
    assert response.status_code == 200
    response_data = response.json()
    
    # Check response based on command type
    command_name = payload["data"]["name"]
    if command_name == "githubsub":
        assert response_data == {"type": 5, "data": {"flags": 64}}  # Deferred response
    elif command_name == "ping":
        assert response_data["type"] == 4  # Immediate response
        assert "Pong!" in response_data["data"]["content"]
    elif command_name == "help":
        assert response_data["type"] == 4  # Immediate response
        assert "Available Commands" in response_data["data"]["content"]
    else:
        assert response_data == {
            "type": 4,
            "data": {"content": "Unknown command", "flags": 64}
        }