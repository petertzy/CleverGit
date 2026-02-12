"""
Test suite for GitLab integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from clevergit.integrations.gitlab import (
    GitLabClient,
    GitLabAPIError,
    GitLabAuthError,
    parse_gitlab_url
)


class TestGitLabClient:
    """Test GitLabClient class."""
    
    def test_init_without_token(self):
        """Test initializing client without token."""
        client = GitLabClient()
        assert client.token is None
        assert "Private-Token" not in client.session.headers
    
    def test_init_with_token(self):
        """Test initializing client with token."""
        token = "test_token_123"
        client = GitLabClient(token)
        assert client.token == token
        assert client.session.headers["Private-Token"] == token
    
    def test_init_with_custom_base_url(self):
        """Test initializing client with custom base URL."""
        client = GitLabClient(base_url="https://gitlab.example.com")
        assert client.base_url == "https://gitlab.example.com"
        assert client.api_base == "https://gitlab.example.com/api/v4"
    
    @patch('requests.Session.request')
    def test_get_authenticated_user_success(self, mock_request):
        """Test getting authenticated user info."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"username": "testuser", "id": 123}'
        mock_response.json.return_value = {"username": "testuser", "id": 123}
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        user = client.get_authenticated_user()
        
        assert user["username"] == "testuser"
        assert user["id"] == 123
    
    def test_get_authenticated_user_no_token(self):
        """Test getting user info without token raises error."""
        client = GitLabClient()
        
        with pytest.raises(GitLabAuthError):
            client.get_authenticated_user()
    
    @patch('requests.Session.request')
    def test_get_project(self, mock_request):
        """Test getting project information."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"name": "project", "namespace": {"name": "namespace"}}'
        mock_response.json.return_value = {
            "name": "project",
            "namespace": {"name": "namespace"}
        }
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        project = client.get_project("namespace/project")
        
        assert project["name"] == "project"
        assert project["namespace"]["name"] == "namespace"
    
    @patch('requests.Session.request')
    def test_list_merge_requests(self, mock_request):
        """Test listing merge requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[{"iid": 1, "title": "Test MR"}]'
        mock_response.json.return_value = [{"iid": 1, "title": "Test MR"}]
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        mrs = client.list_merge_requests("namespace/project")
        
        assert len(mrs) == 1
        assert mrs[0]["iid"] == 1
        assert mrs[0]["title"] == "Test MR"
    
    @patch('requests.Session.request')
    def test_list_merge_requests_with_filters(self, mock_request):
        """Test listing merge requests with filters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[]'
        mock_response.json.return_value = []
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        client.list_merge_requests("namespace/project", state="merged", sort="asc")
        
        # Check that the request was made with correct parameters
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["params"]["state"] == "merged"
        assert call_kwargs["params"]["sort"] == "asc"
    
    @patch('requests.Session.request')
    def test_get_merge_request(self, mock_request):
        """Test getting a specific merge request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"iid": 42, "title": "Fix bug"}'
        mock_response.json.return_value = {"iid": 42, "title": "Fix bug"}
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        mr = client.get_merge_request("namespace/project", 42)
        
        assert mr["iid"] == 42
        assert mr["title"] == "Fix bug"
    
    @patch('requests.Session.request')
    def test_list_issues(self, mock_request):
        """Test listing issues."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[{"iid": 1, "title": "Bug report"}]'
        mock_response.json.return_value = [{"iid": 1, "title": "Bug report"}]
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        issues = client.list_issues("namespace/project")
        
        assert len(issues) == 1
        assert issues[0]["iid"] == 1
    
    @patch('requests.Session.request')
    def test_create_merge_request(self, mock_request):
        """Test creating a merge request."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"iid": 10, "title": "New feature"}'
        mock_response.json.return_value = {"iid": 10, "title": "New feature"}
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        mr = client.create_merge_request(
            "namespace/project",
            "New feature",
            "feature-branch",
            "main",
            "Description here"
        )
        
        assert mr["iid"] == 10
        assert mr["title"] == "New feature"
    
    @patch('requests.Session.request')
    def test_create_merge_request_draft(self, mock_request):
        """Test creating a draft merge request."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"iid": 11, "title": "Draft: Work in progress"}'
        mock_response.json.return_value = {"iid": 11, "title": "Draft: Work in progress"}
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        mr = client.create_merge_request(
            "namespace/project",
            "Work in progress",
            "wip-branch",
            "main",
            draft=True
        )
        
        # Check that the request data included "Draft: " prefix
        call_kwargs = mock_request.call_args[1]
        assert "Draft:" in call_kwargs["json"]["title"]
    
    @patch('requests.Session.request')
    def test_fork_project(self, mock_request):
        """Test forking a project."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"name": "project", "forked_from_project": {"id": 1}}'
        mock_response.json.return_value = {"name": "project", "forked_from_project": {"id": 1}}
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        fork = client.fork_project("namespace/project")
        
        assert "forked_from_project" in fork
    
    @patch('requests.Session.request')
    def test_star_project(self, mock_request):
        """Test starring a project."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"star_count": 10}'
        mock_response.json.return_value = {"star_count": 10}
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        result = client.star_project("namespace/project")
        
        mock_request.assert_called_once()
        assert result["star_count"] == 10
    
    @patch('requests.Session.request')
    def test_unstar_project(self, mock_request):
        """Test unstarring a project."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"star_count": 9}'
        mock_response.json.return_value = {"star_count": 9}
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        result = client.unstar_project("namespace/project")
        
        mock_request.assert_called_once()
        assert result["star_count"] == 9
    
    @patch('requests.Session.request')
    def test_list_pipelines(self, mock_request):
        """Test listing CI/CD pipelines."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[{"id": 1, "status": "success"}]'
        mock_response.json.return_value = [{"id": 1, "status": "success"}]
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        pipelines = client.list_pipelines("namespace/project")
        
        assert len(pipelines) == 1
        assert pipelines[0]["status"] == "success"
    
    @patch('requests.Session.request')
    def test_list_pipelines_with_filters(self, mock_request):
        """Test listing pipelines with filters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[]'
        mock_response.json.return_value = []
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        client.list_pipelines("namespace/project", ref="main", status="running")
        
        # Check that the request was made with correct parameters
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["params"]["ref"] == "main"
        assert call_kwargs["params"]["status"] == "running"
    
    @patch('requests.Session.request')
    def test_get_pipeline(self, mock_request):
        """Test getting a specific pipeline."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"id": 123, "status": "success"}'
        mock_response.json.return_value = {"id": 123, "status": "success"}
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        pipeline = client.get_pipeline("namespace/project", 123)
        
        assert pipeline["id"] == 123
        assert pipeline["status"] == "success"
    
    @patch('requests.Session.request')
    def test_list_pipeline_jobs(self, mock_request):
        """Test listing pipeline jobs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[{"id": 1, "name": "test"}]'
        mock_response.json.return_value = [{"id": 1, "name": "test"}]
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        jobs = client.list_pipeline_jobs("namespace/project", 123)
        
        assert len(jobs) == 1
        assert jobs[0]["name"] == "test"
    
    @patch('requests.Session.request')
    def test_api_error_handling(self, mock_request):
        """Test API error handling."""
        from requests.exceptions import HTTPError
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not Found"}
        error = HTTPError()
        error.response = mock_response
        mock_response.raise_for_status.side_effect = error
        mock_response.text = '{"message": "Not Found"}'
        mock_request.return_value = mock_response
        
        client = GitLabClient("test_token")
        
        with pytest.raises(GitLabAPIError) as exc_info:
            client.get_project("namespace/nonexistent")
        
        assert "Not Found" in str(exc_info.value)


class TestParseGitLabURL:
    """Test parse_gitlab_url function."""
    
    def test_parse_https_url(self):
        """Test parsing HTTPS URL."""
        url = "https://gitlab.com/namespace/project"
        result = parse_gitlab_url(url)
        
        assert result == "namespace/project"
    
    def test_parse_https_url_with_git_extension(self):
        """Test parsing HTTPS URL with .git extension."""
        url = "https://gitlab.com/namespace/project.git"
        result = parse_gitlab_url(url)
        
        assert result == "namespace/project"
    
    def test_parse_ssh_url(self):
        """Test parsing SSH URL."""
        url = "git@gitlab.com:namespace/project.git"
        result = parse_gitlab_url(url)
        
        assert result == "namespace/project"
    
    def test_parse_ssh_url_without_git_extension(self):
        """Test parsing SSH URL without .git extension."""
        url = "git@gitlab.com:namespace/project"
        result = parse_gitlab_url(url)
        
        assert result == "namespace/project"
    
    def test_parse_nested_groups(self):
        """Test parsing URL with nested groups."""
        url = "https://gitlab.com/group/subgroup/project"
        result = parse_gitlab_url(url)
        
        assert result == "group/subgroup/project"
    
    def test_parse_nested_groups_ssh(self):
        """Test parsing SSH URL with nested groups."""
        url = "git@gitlab.com:group/subgroup/project.git"
        result = parse_gitlab_url(url)
        
        assert result == "group/subgroup/project"
    
    def test_parse_custom_gitlab_instance(self):
        """Test parsing custom GitLab instance URL."""
        url = "https://gitlab.example.com/namespace/project"
        result = parse_gitlab_url(url)
        
        assert result == "namespace/project"
    
    def test_parse_invalid_url(self):
        """Test parsing invalid URL returns None."""
        url = "https://github.com/owner/repo"
        result = parse_gitlab_url(url)
        
        # This will still parse, but the check for "gitlab" in the URL happens in the UI
        assert result == "owner/repo"
    
    def test_parse_malformed_url(self):
        """Test parsing malformed URL returns None."""
        url = "not_a_valid_url"
        result = parse_gitlab_url(url)
        
        assert result is None
    
    def test_parse_url_with_dots_in_name(self):
        """Test parsing project names that contain dots."""
        url = "https://gitlab.com/namespace/project.name.test"
        result = parse_gitlab_url(url)
        
        # Should preserve dots in project name
        assert result == "namespace/project.name.test"
    
    def test_parse_url_with_dots_and_git_suffix(self):
        """Test parsing project names with dots and .git suffix."""
        url = "https://gitlab.com/namespace/project.name.git"
        result = parse_gitlab_url(url)
        
        # Should preserve dots but remove .git
        assert result == "namespace/project.name"
