import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def format_commit_message(commit: dict) -> str:
    """Format a commit message for Discord."""
    author = commit.get("author", {}).get("name", "Unknown")
    message = commit.get("message", "No message provided")
    url = commit.get("url", "")
    return f"• {author}: {message}\n  {url}"


def format_pull_request_message(payload: dict) -> str:
    """Format a pull request message for Discord."""
    action = payload.get("action", "unknown")
    pr = payload.get("pull_request", {})
    title = pr.get("title", "No title")
    number = pr.get("number", "0")
    url = pr.get("html_url", "")
    user = pr.get("user", {}).get("login", "Unknown")

    return (
        f"Pull Request #{number} {action} by {user}\n" f"Title: {title}\n" f"URL: {url}"
    )


def format_issue_message(payload: dict) -> str:
    """Format an issue message for Discord."""
    action = payload.get("action", "unknown")
    issue = payload.get("issue", {})
    title = issue.get("title", "No title")
    number = issue.get("number", "0")
    url = issue.get("html_url", "")
    user = issue.get("user", {}).get("login", "Unknown")

    return f"Issue #{number} {action} by {user}\n" f"Title: {title}\n" f"URL: {url}"


def format_github_event(event_type: str, payload: Dict[str, Any]) -> str:
    """Format GitHub event for Discord message."""
    if event_type == "pull_request":
        return format_pull_request_message(payload)
    elif event_type == "issues":
        return format_issue_message(payload)
    else:
        logger.warning(f"Unsupported event type: {event_type}")
        return f"Received {event_type} event"


def format_pr_event(payload: Dict[Any, Any]) -> str:
    """Format pull request event message."""
    action = payload.get("action", "unknown")
    pr = payload.get("pull_request", {})

    return (
        f"🔍 Pull Request {action}: {pr.get('title')}\n"
        f"Repository: {payload.get('repository', {}).get('full_name')}\n"
        f"Author: {pr.get('user', {}).get('login')}\n"
        f"URL: {pr.get('html_url')}"
    )
