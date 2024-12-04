import pytest
from src.utils.formatting import format_github_event

def test_format_push_event():
    """Test formatting of push events."""
    payload = {
        "repository": {"full_name": "test/repo"},
        "ref": "refs/heads/main",
        "commits": [
            {"message": "First commit\nMore details"},
            {"message": "Second commit"}
        ]
    }
    
    result = format_github_event("push", payload)
    
    assert "test/repo" in result
    assert "main" in result
    assert "First commit" in result
    assert "Second commit" in result
    assert "More details" not in result  # Should only include first line

def test_format_pull_request_event():
    """Test formatting of pull request events."""
    payload = {
        "action": "opened",
        "pull_request": {
            "title": "Test PR",
            "html_url": "https://github.com/test/pr/1"
        }
    }
    
    result = format_github_event("pull_request", payload)
    
    assert "opened" in result
    assert "Test PR" in result
    assert "https://github.com/test/pr/1" in result

def test_format_unknown_event():
    """Test formatting of unknown event types."""
    result = format_github_event("unknown", {})
    assert "unknown" in result