"""
GUI widgets module.
"""

from clevergit.ui.widgets.graph_view import CommitGraphView
from clevergit.ui.widgets.blame_view import BlameView
from clevergit.ui.widgets.command_palette import CommandPalette
from clevergit.ui.widgets.github_panel import GitHubPanel
from clevergit.ui.widgets.gitlab_panel import GitLabPanel

__all__ = ['CommitGraphView', 'BlameView', 'CommandPalette', 'GitHubPanel', 'GitLabPanel']
