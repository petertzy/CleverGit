"""
GitLab API integration module.

Provides functionality for interacting with GitLab's REST API.
"""

import json
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode
import requests


class GitLabAuthError(Exception):
    """Exception raised when authentication fails."""
    pass


class GitLabAPIError(Exception):
    """Exception raised when API call fails."""
    pass


class GitLabClient:
    """Client for interacting with GitLab API."""
    
    def __init__(self, token: Optional[str] = None, base_url: str = "https://gitlab.com"):
        """
        Initialize GitLab client.
        
        Args:
            token: GitLab personal access token
            base_url: GitLab instance URL (default: https://gitlab.com)
        """
        self.token = token
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v4"
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                "Private-Token": token,
                "Content-Type": "application/json"
            })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make a request to GitLab API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body data
            
        Returns:
            Parsed JSON response
            
        Raises:
            GitLabAPIError: If request fails
        """
        url = f"{self.api_base}{endpoint}"
        
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
            error_msg = f"GitLab API error: {e}"
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    if isinstance(error_data, dict):
                        error_msg = f"GitLab API error: {error_data.get('message', str(e))}"
                    elif isinstance(error_data, list) and error_data:
                        error_msg = f"GitLab API error: {error_data[0]}"
                except json.JSONDecodeError:
                    pass
            raise GitLabAPIError(error_msg) from e
        except requests.exceptions.RequestException as e:
            raise GitLabAPIError(f"Network error: {e}") from e
    
    def get_authenticated_user(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user.
        
        Returns:
            User information dictionary
            
        Raises:
            GitLabAuthError: If not authenticated
            GitLabAPIError: If request fails
        """
        if not self.token:
            raise GitLabAuthError("No authentication token provided")
        
        try:
            return self._request("GET", "/user")
        except GitLabAPIError:
            raise GitLabAuthError("Invalid or expired token")
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get information about a project.
        
        Args:
            project_id: Project ID or URL-encoded path (e.g., "namespace/project")
            
        Returns:
            Project information dictionary
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        return self._request("GET", f"/projects/{encoded_id}")
    
    def list_merge_requests(
        self,
        project_id: str,
        state: str = "opened",
        order_by: str = "created_at",
        sort: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        List merge requests for a project.
        
        Args:
            project_id: Project ID or URL-encoded path
            state: MR state (opened, closed, locked, merged, all)
            order_by: Order by (created_at, updated_at, title)
            sort: Sort direction (asc, desc)
            
        Returns:
            List of merge request dictionaries
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        params = {
            "state": state,
            "order_by": order_by,
            "sort": sort
        }
        return self._request("GET", f"/projects/{encoded_id}/merge_requests", params=params)
    
    def get_merge_request(
        self,
        project_id: str,
        mr_iid: int
    ) -> Dict[str, Any]:
        """
        Get details of a specific merge request.
        
        Args:
            project_id: Project ID or URL-encoded path
            mr_iid: MR internal ID (IID)
            
        Returns:
            Merge request details dictionary
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        return self._request("GET", f"/projects/{encoded_id}/merge_requests/{mr_iid}")
    
    def list_issues(
        self,
        project_id: str,
        state: str = "opened",
        labels: Optional[List[str]] = None,
        order_by: str = "created_at",
        sort: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        List issues for a project.
        
        Args:
            project_id: Project ID or URL-encoded path
            state: Issue state (opened, closed, all)
            labels: Filter by labels
            order_by: Order by (created_at, updated_at, priority, etc.)
            sort: Sort direction (asc, desc)
            
        Returns:
            List of issue dictionaries
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        params: Dict[str, Any] = {
            "state": state,
            "order_by": order_by,
            "sort": sort
        }
        if labels:
            params["labels"] = ",".join(labels)
        
        return self._request("GET", f"/projects/{encoded_id}/issues", params=params)
    
    def get_issue(
        self,
        project_id: str,
        issue_iid: int
    ) -> Dict[str, Any]:
        """
        Get details of a specific issue.
        
        Args:
            project_id: Project ID or URL-encoded path
            issue_iid: Issue internal ID (IID)
            
        Returns:
            Issue details dictionary
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        return self._request("GET", f"/projects/{encoded_id}/issues/{issue_iid}")
    
    def create_merge_request(
        self,
        project_id: str,
        title: str,
        source_branch: str,
        target_branch: str,
        description: Optional[str] = None,
        draft: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new merge request.
        
        Args:
            project_id: Project ID or URL-encoded path
            title: MR title (prefixed with "Draft: " if draft=True)
            source_branch: Source branch containing changes
            target_branch: Target branch to merge into
            description: MR description
            draft: Whether to create as draft MR
            
        Returns:
            Created merge request dictionary
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        
        # Add Draft: prefix to title if draft
        mr_title = f"Draft: {title}" if draft else title
        
        data: Dict[str, Any] = {
            "title": mr_title,
            "source_branch": source_branch,
            "target_branch": target_branch
        }
        if description:
            data["description"] = description
        
        return self._request("POST", f"/projects/{encoded_id}/merge_requests", data=data)
    
    def fork_project(
        self,
        project_id: str,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fork a project.
        
        Args:
            project_id: Project ID or URL-encoded path
            namespace: Optional namespace to fork to
            
        Returns:
            Forked project dictionary
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        data = {}
        if namespace:
            data["namespace"] = namespace
        
        return self._request("POST", f"/projects/{encoded_id}/fork", data=data if data else None)
    
    def star_project(self, project_id: str) -> Dict[str, Any]:
        """
        Star a project.
        
        Args:
            project_id: Project ID or URL-encoded path
            
        Returns:
            Project information
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        return self._request("POST", f"/projects/{encoded_id}/star")
    
    def unstar_project(self, project_id: str) -> Dict[str, Any]:
        """
        Unstar a project.
        
        Args:
            project_id: Project ID or URL-encoded path
            
        Returns:
            Project information
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        return self._request("POST", f"/projects/{encoded_id}/unstar")
    
    def is_project_starred(self, project_id: str) -> bool:
        """
        Check if a project is starred by the authenticated user.
        
        Args:
            project_id: Project ID or URL-encoded path
            
        Returns:
            True if starred, False otherwise
        """
        try:
            from urllib.parse import quote
            encoded_id = quote(project_id, safe='')
            project = self._request("GET", f"/projects/{encoded_id}")
            # GitLab includes star_count in project details
            # We need to check if current user has starred it
            starred_projects = self._request("GET", "/users/starred_projects")
            return any(p["id"] == project["id"] for p in starred_projects)
        except GitLabAPIError:
            return False
    
    def list_pipelines(
        self,
        project_id: str,
        ref: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List CI/CD pipelines for a project.
        
        Args:
            project_id: Project ID or URL-encoded path
            ref: Optional branch/tag name to filter by
            status: Optional status to filter by (running, pending, success, failed, canceled, skipped)
            
        Returns:
            List of pipeline dictionaries
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        params = {}
        if ref:
            params["ref"] = ref
        if status:
            params["status"] = status
        
        return self._request("GET", f"/projects/{encoded_id}/pipelines", params=params if params else None)
    
    def get_pipeline(
        self,
        project_id: str,
        pipeline_id: int
    ) -> Dict[str, Any]:
        """
        Get details of a specific pipeline.
        
        Args:
            project_id: Project ID or URL-encoded path
            pipeline_id: Pipeline ID
            
        Returns:
            Pipeline details dictionary
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        return self._request("GET", f"/projects/{encoded_id}/pipelines/{pipeline_id}")
    
    def list_pipeline_jobs(
        self,
        project_id: str,
        pipeline_id: int
    ) -> List[Dict[str, Any]]:
        """
        List jobs for a specific pipeline.
        
        Args:
            project_id: Project ID or URL-encoded path
            pipeline_id: Pipeline ID
            
        Returns:
            List of job dictionaries
        """
        from urllib.parse import quote
        encoded_id = quote(project_id, safe='')
        return self._request("GET", f"/projects/{encoded_id}/pipelines/{pipeline_id}/jobs")


def parse_gitlab_url(url: str) -> Optional[str]:
    """
    Parse a GitLab repository URL to extract namespace and project name.
    
    Args:
        url: GitLab repository URL (HTTPS or SSH)
        
    Returns:
        Project path string (e.g., "namespace/project" or "group/subgroup/project") or None if invalid
        
    Examples:
        >>> parse_gitlab_url("https://gitlab.com/namespace/project")
        'namespace/project'
        >>> parse_gitlab_url("git@gitlab.com:namespace/project.git")
        'namespace/project'
        >>> parse_gitlab_url("https://gitlab.com/group/subgroup/project")
        'group/subgroup/project'
    """
    import re
    
    # HTTPS URL pattern - support nested groups
    https_pattern = r'https?://[^/]+/(.+?)(?:\.git)?$'
    # SSH URL pattern - support nested groups
    ssh_pattern = r'git@[^:]+:(.+?)(?:\.git)?$'
    
    for pattern in [https_pattern, ssh_pattern]:
        match = re.match(pattern, url)
        if match:
            project_path = match.group(1)
            return project_path
    
    return None
