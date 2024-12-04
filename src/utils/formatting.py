from typing import Dict, Any

def format_github_event(event_type: str, payload: Dict[Any, Any]) -> str:
    """Format GitHub webhook event into Discord message."""
    message = f"**{event_type}**\n"

    if event_type == "push":
        repo = payload.get("repository", {}).get("full_name", "unknown")
        ref = payload.get("ref", "").replace("refs/heads/", "")
        commits = payload.get("commits", [])
        
        message += f"Repository: {repo}\n"
        message += f"Branch: {ref}\n"
        message += f"Commits:\n"
        
        for commit in commits:
            commit_message = commit.get("message", "").split("\n")[0]
            message += f"• {commit_message}\n"
    
    elif event_type == "pull_request":
        action = payload.get("action", "unknown")
        pr = payload.get("pull_request", {})
        title = pr.get("title", "unknown")
        url = pr.get("html_url", "#")
        
        message += f"Action: {action}\n"
        message += f"Title: {title}\n"
        message += f"URL: {url}\n"
    
    return message

def format_push_event(payload: Dict[Any, Any]) -> str:
    """Format push event message."""
    repo = payload.get("repository", {}).get("full_name", "unknown")
    branch = payload.get("ref", "").replace("refs/heads/", "")
    commits = payload.get("commits", [])
    
    message = f"🔨 New push to {repo} on branch `{branch}`\n"
    for commit in commits[:5]:  # Show max 5 commits
        message += f"• {commit.get('message', '').split('\n')[0]} "
        message += f"(`{commit.get('id', '')[:7]}`)\n"
    
    if len(commits) > 5:
        message += f"... and {len(commits) - 5} more commits"
    
    return message

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