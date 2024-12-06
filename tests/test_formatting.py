import pytest
from src.utils.formatting import (
    format_commit_message,
    format_pull_request_message,
    format_issue_message,
    format_github_event,
    format_pr_event,
)

def test_format_commit_message():
    """Test commit message formatting"""
    # Test with complete data
    commit = {
        "author": {"name": "Test User"},
        "message": "Test commit",
        "url": "https://github.com/test/commit"
    }
    expected = "• Test User: Test commit\n  https://github.com/test/commit"
    assert format_commit_message(commit) == expected

    # Test with missing data
    empty_commit = {}
    expected_empty = "• Unknown: No message provided\n  "
    assert format_commit_message(empty_commit) == expected_empty

def test_format_pull_request_message():
    """Test pull request message formatting"""
    # Test with complete data
    payload = {
        "action": "opened",
        "pull_request": {
            "title": "Test PR",
            "number": 123,
            "html_url": "https://github.com/test/pr",
            "user": {"login": "testuser"}
        }
    }
    expected = (
        "Pull Request #123 opened by testuser\n"
        "Title: Test PR\n"
        "URL: https://github.com/test/pr"
    )
    assert format_pull_request_message(payload) == expected

    # Test with missing data
    empty_payload = {}
    expected_empty = "Pull Request #0 unknown by Unknown\nTitle: No title\nURL: "
    assert format_pull_request_message(empty_payload) == expected_empty

def test_format_issue_message():
    """Test issue message formatting"""
    # Test with complete data
    payload = {
        "action": "created",
        "issue": {
            "title": "Test Issue",
            "number": 456,
            "html_url": "https://github.com/test/issue",
            "user": {"login": "testuser"}
        }
    }
    expected = (
        "Issue #456 created by testuser\n"
        "Title: Test Issue\n"
        "URL: https://github.com/test/issue"
    )
    assert format_issue_message(payload) == expected

    # Test with missing data
    empty_payload = {}
    expected_empty = "Issue #0 unknown by Unknown\nTitle: No title\nURL: "
    assert format_issue_message(empty_payload) == expected_empty

def test_format_github_event():
    """Test GitHub event formatting"""
    # Test pull request event
    pr_payload = {
        "action": "opened",
        "pull_request": {
            "title": "Test PR",
            "number": 123,
            "html_url": "https://github.com/test/pr",
            "user": {"login": "testuser"}
        }
    }
    assert format_github_event("pull_request", pr_payload) == format_pull_request_message(pr_payload)

    # Test issue event
    issue_payload = {
        "action": "created",
        "issue": {
            "title": "Test Issue",
            "number": 456,
            "html_url": "https://github.com/test/issue",
            "user": {"login": "testuser"}
        }
    }
    assert format_github_event("issues", issue_payload) == format_issue_message(issue_payload)

    # Test unsupported event
    assert format_github_event("unsupported", {}) == "Received unsupported event"

def test_format_pr_event():
    """Test pull request event formatting"""
    # Test with complete data
    payload = {
        "action": "opened",
        "pull_request": {
            "title": "Test PR",
            "user": {"login": "testuser"},
            "html_url": "https://github.com/test/pr"
        },
        "repository": {"full_name": "test/repo"}
    }
    expected = (
        "🔍 Pull Request opened: Test PR\n"
        "Repository: test/repo\n"
        "Author: testuser\n"
        "URL: https://github.com/test/pr"
    )
    assert format_pr_event(payload) == expected

    # Test with missing data
    empty_payload = {}
    expected_empty = (
        "🔍 Pull Request unknown: None\n"
        "Repository: None\n"
        "Author: None\n"
        "URL: None"
    )
    assert format_pr_event(empty_payload) == expected_empty
