"""
Test suite for GitHub integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from clevergit.integrations.github import (
    GitHubClient,
    GitHubAPIError,
    GitHubAuthError,
    parse_github_url
)


class TestGitHubClient:
    """Test GitHubClient class."""
    
    def test_init_without_token(self):
        """Test initializing client without token."""
        client = GitHubClient()
        assert client.token is None
        assert "Authorization" not in client.session.headers
    
    def test_init_with_token(self):
        """Test initializing client with token."""
        token = "test_token_123"
        client = GitHubClient(token)
        assert client.token == token
        assert client.session.headers["Authorization"] == f"token {token}"
    
    @patch('requests.Session.request')
    def test_get_authenticated_user_success(self, mock_request):
        """Test getting authenticated user info."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"login": "testuser", "id": 123}'
        mock_response.json.return_value = {"login": "testuser", "id": 123}
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        user = client.get_authenticated_user()
        
        assert user["login"] == "testuser"
        assert user["id"] == 123
    
    def test_get_authenticated_user_no_token(self):
        """Test getting user info without token raises error."""
        client = GitHubClient()
        
        with pytest.raises(GitHubAuthError):
            client.get_authenticated_user()
    
    @patch('requests.Session.request')
    def test_get_repository(self, mock_request):
        """Test getting repository information."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"name": "repo", "owner": {"login": "owner"}}'
        mock_response.json.return_value = {
            "name": "repo",
            "owner": {"login": "owner"}
        }
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        repo = client.get_repository("owner", "repo")
        
        assert repo["name"] == "repo"
        assert repo["owner"]["login"] == "owner"
    
    @patch('requests.Session.request')
    def test_list_pull_requests(self, mock_request):
        """Test listing pull requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[{"number": 1, "title": "Test PR"}]'
        mock_response.json.return_value = [{"number": 1, "title": "Test PR"}]
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        prs = client.list_pull_requests("owner", "repo")
        
        assert len(prs) == 1
        assert prs[0]["number"] == 1
        assert prs[0]["title"] == "Test PR"
    
    @patch('requests.Session.request')
    def test_list_pull_requests_with_filters(self, mock_request):
        """Test listing pull requests with filters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[]'
        mock_response.json.return_value = []
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        client.list_pull_requests("owner", "repo", state="closed", sort="updated")
        
        # Check that the request was made with correct parameters
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["params"]["state"] == "closed"
        assert call_kwargs["params"]["sort"] == "updated"
    
    @patch('requests.Session.request')
    def test_get_pull_request(self, mock_request):
        """Test getting a specific pull request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"number": 42, "title": "Fix bug"}'
        mock_response.json.return_value = {"number": 42, "title": "Fix bug"}
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        pr = client.get_pull_request("owner", "repo", 42)
        
        assert pr["number"] == 42
        assert pr["title"] == "Fix bug"
    
    @patch('requests.Session.request')
    def test_list_issues(self, mock_request):
        """Test listing issues."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[{"number": 1, "title": "Bug report"}]'
        mock_response.json.return_value = [{"number": 1, "title": "Bug report"}]
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        issues = client.list_issues("owner", "repo")
        
        assert len(issues) == 1
        assert issues[0]["number"] == 1
    
    @patch('requests.Session.request')
    def test_create_pull_request(self, mock_request):
        """Test creating a pull request."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"number": 10, "title": "New feature"}'
        mock_response.json.return_value = {"number": 10, "title": "New feature"}
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        pr = client.create_pull_request(
            "owner",
            "repo",
            "New feature",
            "feature-branch",
            "main",
            "Description here"
        )
        
        assert pr["number"] == 10
        assert pr["title"] == "New feature"
    
    @patch('requests.Session.request')
    def test_fork_repository(self, mock_request):
        """Test forking a repository."""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.text = '{"name": "repo", "fork": true}'
        mock_response.json.return_value = {"name": "repo", "fork": True}
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        fork = client.fork_repository("owner", "repo")
        
        assert fork["fork"] is True
    
    @patch('requests.Session.request')
    def test_star_repository(self, mock_request):
        """Test starring a repository."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ''
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        client.star_repository("owner", "repo")
        
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_unstar_repository(self, mock_request):
        """Test unstarring a repository."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ''
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        client.unstar_repository("owner", "repo")
        
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_is_repository_starred_true(self, mock_request):
        """Test checking if repository is starred (true)."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ''
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        is_starred = client.is_repository_starred("owner", "repo")
        
        assert is_starred is True
    
    @patch('requests.Session.request')
    def test_is_repository_starred_false(self, mock_request):
        """Test checking if repository is starred (false)."""
        from requests.exceptions import HTTPError
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError()
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        is_starred = client.is_repository_starred("owner", "repo")
        
        assert is_starred is False
    
    @patch('requests.Session.request')
    def test_list_workflows(self, mock_request):
        """Test listing GitHub Actions workflows."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"workflows": [{"id": 1, "name": "CI"}]}'
        mock_response.json.return_value = {"workflows": [{"id": 1, "name": "CI"}]}
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        workflows = client.list_workflows("owner", "repo")
        
        assert len(workflows) == 1
        assert workflows[0]["name"] == "CI"
    
    @patch('requests.Session.request')
    def test_list_workflow_runs(self, mock_request):
        """Test listing workflow runs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"workflow_runs": [{"id": 1, "status": "completed"}]}'
        mock_response.json.return_value = {
            "workflow_runs": [{"id": 1, "status": "completed"}]
        }
        mock_request.return_value = mock_response
        
        client = GitHubClient("test_token")
        runs = client.list_workflow_runs("owner", "repo")
        
        assert len(runs) == 1
        assert runs[0]["status"] == "completed"
    
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
        
        client = GitHubClient("test_token")
        
        with pytest.raises(GitHubAPIError) as exc_info:
            client.get_repository("owner", "nonexistent")
        
        assert "Not Found" in str(exc_info.value)


class TestParseGitHubURL:
    """Test parse_github_url function."""
    
    def test_parse_https_url(self):
        """Test parsing HTTPS URL."""
        url = "https://github.com/owner/repo"
        result = parse_github_url(url)
        
        assert result == ("owner", "repo")
    
    def test_parse_https_url_with_git_extension(self):
        """Test parsing HTTPS URL with .git extension."""
        url = "https://github.com/owner/repo.git"
        result = parse_github_url(url)
        
        assert result == ("owner", "repo")
    
    def test_parse_ssh_url(self):
        """Test parsing SSH URL."""
        url = "git@github.com:owner/repo.git"
        result = parse_github_url(url)
        
        assert result == ("owner", "repo")
    
    def test_parse_ssh_url_without_git_extension(self):
        """Test parsing SSH URL without .git extension."""
        url = "git@github.com:owner/repo"
        result = parse_github_url(url)
        
        assert result == ("owner", "repo")
    
    def test_parse_invalid_url(self):
        """Test parsing invalid URL returns None."""
        url = "https://gitlab.com/owner/repo"
        result = parse_github_url(url)
        
        assert result is None
    
    def test_parse_malformed_url(self):
        """Test parsing malformed URL returns None."""
        url = "not_a_valid_url"
        result = parse_github_url(url)
        
        assert result is None
    
    def test_parse_url_with_git_suffix_edge_case(self):
        """Test that only the .git suffix is removed, not other occurrences."""
        url = "https://github.com/owner/repo.git"
        result = parse_github_url(url)
        
        # Should remove .git suffix
        assert result == ("owner", "repo")
    
    def test_parse_url_with_dots_in_name(self):
        """Test parsing repository names that contain dots."""
        url = "https://github.com/owner/repo.name.test"
        result = parse_github_url(url)
        
        # Should preserve dots in repository name
        assert result == ("owner", "repo.name.test")
    
    def test_parse_url_with_dots_and_git_suffix(self):
        """Test parsing repository names with dots and .git suffix."""
        url = "https://github.com/owner/repo.name.git"
        result = parse_github_url(url)
        
        # Should preserve dots but remove .git
        assert result == ("owner", "repo.name")
