from typing import Dict, Any

def format_commit_message(message: str) -> str:
    """Format a commit message by taking only the first line."""
    lines = message.split('\n')
    return lines[0] if lines else ''

def format_github_event(event_type: str, payload: dict) -> str:
    """Format GitHub webhook event into a Discord message."""
    parts = [f"**{event_type}**"]

    if event_type == "push":
        repo = payload.get('repository', {}).get('full_name', 'unknown')
        ref = payload.get('ref', '')
        branch = ref.replace('refs/heads/', '') if ref else 'unknown'
        commits = payload.get('commits', [])
        
        parts.append(f"Repository: {repo}")
        parts.append(f"Branch: {branch}")
        
        if commits:
            parts.append("Commits:")
            for commit in commits:
                message = format_commit_message(commit.get('message', ''))
                parts.append(f"• {message}")
    
    elif event_type == "pull_request":
        action = payload.get('action', 'unknown')
        pr = payload.get('pull_request', {})
        title = pr.get('title', 'unknown')
        url = pr.get('html_url', '#')
        
        parts.append(f"Action: {action}")
        parts.append(f"Title: {title}")
        parts.append(f"URL: {url}")
    
    return '\n'.join(parts)

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