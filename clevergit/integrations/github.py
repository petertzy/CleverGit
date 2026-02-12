"""
GitHub API integration module.

Provides functionality for interacting with GitHub's REST API.
"""

import json
import base64
from typing import Optional, List, Dict, Any
from pathlib import Path
from urllib.parse import urlencode
import requests


class GitHubAuthError(Exception):
    """Exception raised when authentication fails."""
    pass


class GitHubAPIError(Exception):
    """Exception raised when API call fails."""
    pass


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    API_BASE = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token or OAuth token
        """
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make a request to GitHub API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body data
            
        Returns:
            Parsed JSON response
            
        Raises:
            GitHubAPIError: If request fails
        """
        url = f"{self.API_BASE}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json() if response.text else None
        except requests.exceptions.HTTPError as e:
            error_msg = f"GitHub API error: {e}"
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = f"GitHub API error: {error_data.get('message', str(e))}"
                except json.JSONDecodeError:
                    pass
            raise GitHubAPIError(error_msg) from e
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error: {e}") from e
    
    def get_authenticated_user(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user.
        
        Returns:
            User information dictionary
            
        Raises:
            GitHubAuthError: If not authenticated
            GitHubAPIError: If request fails
        """
        if not self.token:
            raise GitHubAuthError("No authentication token provided")
        
        try:
            return self._request("GET", "/user")
        except GitHubAPIError:
            raise GitHubAuthError("Invalid or expired token")
    
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get information about a repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            
        Returns:
            Repository information dictionary
        """
        return self._request("GET", f"/repos/{owner}/{repo}")
    
    def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        List pull requests for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open, closed, all)
            sort: Sort by (created, updated, popularity, long-running)
            direction: Sort direction (asc, desc)
            
        Returns:
            List of pull request dictionaries
        """
        params = {
            "state": state,
            "sort": sort,
            "direction": direction
        }
        return self._request("GET", f"/repos/{owner}/{repo}/pulls", params=params)
    
    def get_pull_request(
        self,
        owner: str,
        repo: str,
        number: int
    ) -> Dict[str, Any]:
        """
        Get details of a specific pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            number: PR number
            
        Returns:
            Pull request details dictionary
        """
        return self._request("GET", f"/repos/{owner}/{repo}/pulls/{number}")
    
    def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        labels: Optional[List[str]] = None,
        sort: str = "created",
        direction: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        List issues for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            labels: Filter by labels
            sort: Sort by (created, updated, comments)
            direction: Sort direction (asc, desc)
            
        Returns:
            List of issue dictionaries
        """
        params: Dict[str, Any] = {
            "state": state,
            "sort": sort,
            "direction": direction
        }
        if labels:
            params["labels"] = ",".join(labels)
        
        return self._request("GET", f"/repos/{owner}/{repo}/issues", params=params)
    
    def get_issue(
        self,
        owner: str,
        repo: str,
        number: int
    ) -> Dict[str, Any]:
        """
        Get details of a specific issue.
        
        Args:
            owner: Repository owner
            repo: Repository name
            number: Issue number
            
        Returns:
            Issue details dictionary
        """
        return self._request("GET", f"/repos/{owner}/{repo}/issues/{number}")
    
    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: Optional[str] = None,
        draft: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: PR title
            head: Branch containing changes
            base: Branch to merge into
            body: PR description
            draft: Whether to create as draft PR
            
        Returns:
            Created pull request dictionary
        """
        data: Dict[str, Any] = {
            "title": title,
            "head": head,
            "base": base,
            "draft": draft
        }
        if body:
            data["body"] = body
        
        return self._request("POST", f"/repos/{owner}/{repo}/pulls", data=data)
    
    def fork_repository(
        self,
        owner: str,
        repo: str,
        organization: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fork a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            organization: Optional organization to fork to
            
        Returns:
            Forked repository dictionary
        """
        data = {}
        if organization:
            data["organization"] = organization
        
        return self._request("POST", f"/repos/{owner}/{repo}/forks", data=data if data else None)
    
    def star_repository(self, owner: str, repo: str) -> None:
        """
        Star a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
        """
        self._request("PUT", f"/user/starred/{owner}/{repo}")
    
    def unstar_repository(self, owner: str, repo: str) -> None:
        """
        Unstar a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
        """
        self._request("DELETE", f"/user/starred/{owner}/{repo}")
    
    def is_repository_starred(self, owner: str, repo: str) -> bool:
        """
        Check if a repository is starred by the authenticated user.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            True if starred, False otherwise
        """
        try:
            self._request("GET", f"/user/starred/{owner}/{repo}")
            return True
        except GitHubAPIError:
            return False
    
    def list_workflows(
        self,
        owner: str,
        repo: str
    ) -> List[Dict[str, Any]]:
        """
        List GitHub Actions workflows for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of workflow dictionaries
        """
        result = self._request("GET", f"/repos/{owner}/{repo}/actions/workflows")
        return result.get("workflows", [])
    
    def list_workflow_runs(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[int] = None,
        branch: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List workflow runs for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            workflow_id: Optional workflow ID to filter by
            branch: Optional branch name to filter by
            status: Optional status to filter by (queued, in_progress, completed)
            
        Returns:
            List of workflow run dictionaries
        """
        if workflow_id:
            endpoint = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            endpoint = f"/repos/{owner}/{repo}/actions/runs"
        
        params = {}
        if branch:
            params["branch"] = branch
        if status:
            params["status"] = status
        
        result = self._request("GET", endpoint, params=params if params else None)
        return result.get("workflow_runs", [])
    
    def get_workflow_run(
        self,
        owner: str,
        repo: str,
        run_id: int
    ) -> Dict[str, Any]:
        """
        Get details of a specific workflow run.
        
        Args:
            owner: Repository owner
            repo: Repository name
            run_id: Workflow run ID
            
        Returns:
            Workflow run details dictionary
        """
        return self._request("GET", f"/repos/{owner}/{repo}/actions/runs/{run_id}")


def parse_github_url(url: str) -> Optional[tuple[str, str]]:
    """
    Parse a GitHub repository URL to extract owner and repo name.
    
    Args:
        url: GitHub repository URL (HTTPS or SSH)
        
    Returns:
        Tuple of (owner, repo) or None if invalid
        
    Examples:
        >>> parse_github_url("https://github.com/owner/repo")
        ('owner', 'repo')
        >>> parse_github_url("git@github.com:owner/repo.git")
        ('owner', 'repo')
    """
    import re
    
    # HTTPS URL pattern - allow dots in repo name
    https_pattern = r'https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?$'
    # SSH URL pattern - allow dots in repo name
    ssh_pattern = r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$'
    
    for pattern in [https_pattern, ssh_pattern]:
        match = re.match(pattern, url)
        if match:
            owner, repo = match.groups()
            return (owner, repo)
    
    return None
