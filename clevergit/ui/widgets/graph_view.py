"""
Commit graph visualization widget.

This module provides a graphical widget for displaying commit history
as a node-edge graph similar to git log --graph.
"""

from typing import List, Optional, Dict
from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout
from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPaintEvent, QMouseEvent, QWheelEvent

from clevergit.models.commit_info import CommitInfo
from clevergit.core.graph import CommitGraph, GraphNode
from clevergit.ui.themes import get_theme_manager


class CommitGraphCanvas(QWidget):
    """
    Canvas widget for rendering the commit graph.

    Handles the actual drawing of nodes, edges, and commit information.
    """

    commit_clicked = Signal(str)  # Emits commit SHA when clicked

    # Visual constants
    ROW_HEIGHT = 40
    LANE_WIDTH = 30
    NODE_RADIUS = 6
    TEXT_PADDING = 10

    def __init__(self) -> None:
        super().__init__()
        self.graph: Optional[CommitGraph] = None
        self.commits: List[CommitInfo] = []
        self.zoom_level = 1.0
        self._selected_sha: Optional[str] = None

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

        # Set minimum size
        self.setMinimumWidth(600)

        # Get theme colors
        self._update_colors()

    def _update_colors(self) -> None:
        """Update colors from current theme."""
        theme_manager = get_theme_manager()
        theme = theme_manager.get_current_theme()

        if theme and theme.graph_colors:
            # Convert hex colors to QColor
            self.COLORS = [QColor(color) for color in theme.graph_colors]
        else:
            # Default fallback colors
            self.COLORS = [
                QColor(255, 87, 51),  # Red-orange
                QColor(76, 175, 80),  # Green
                QColor(33, 150, 243),  # Blue
                QColor(255, 193, 7),  # Yellow
                QColor(156, 39, 176),  # Purple
                QColor(0, 188, 212),  # Cyan
                QColor(255, 152, 0),  # Orange
                QColor(233, 30, 99),  # Pink
            ]

    def set_commits(self, commits: List[CommitInfo]) -> None:
        """
        Set the commits to display.

        Args:
            commits: List of commits in chronological order (newest first)
        """
        self.commits = commits
        if commits:
            self.graph = CommitGraph(commits)
            # Calculate required height
            height = len(commits) * self.ROW_HEIGHT
            self.setMinimumHeight(height)
            self.setFixedHeight(height)
        else:
            self.graph = None
            self.setMinimumHeight(100)

        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint the commit graph.

        Args:
            event: The paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.graph or not self.commits:
            painter.drawText(self.rect(), Qt.AlignCenter, "No commits to display")
            return

        # Calculate graph width
        max_lane = self.graph.get_max_lane()
        graph_width = (max_lane + 1) * self.LANE_WIDTH + self.TEXT_PADDING

        # Draw edges first (so they appear behind nodes)
        self._draw_edges(painter)

        # Draw nodes and commit information
        self._draw_nodes(painter, graph_width)

    def _draw_edges(self, painter: QPainter) -> None:
        """
        Draw edges connecting commits.

        Args:
            painter: The QPainter to draw with
        """
        for i, commit in enumerate(self.commits):
            node = self.graph.get_node(commit.sha)
            if not node:
                continue

            edges = self.graph.get_edges_for_row(i)

            for edge in edges:
                # Calculate positions
                from_x = edge.from_lane * self.LANE_WIDTH + self.LANE_WIDTH // 2
                from_y = i * self.ROW_HEIGHT + self.ROW_HEIGHT // 2

                # Find target row
                to_row = next((j for j, c in enumerate(self.commits) if c.sha == edge.to_sha), None)

                if to_row is not None:
                    to_x = edge.to_lane * self.LANE_WIDTH + self.LANE_WIDTH // 2
                    to_y = to_row * self.ROW_HEIGHT + self.ROW_HEIGHT // 2

                    # Draw the edge
                    color = self.COLORS[edge.color_index % len(self.COLORS)]
                    pen = QPen(color, 2)
                    painter.setPen(pen)

                    # Draw straight line (future: could use curves for lane changes)
                    painter.drawLine(from_x, from_y, to_x, to_y)

    def _draw_nodes(self, painter: QPainter, graph_width: int) -> None:
        """
        Draw commit nodes and text.

        Args:
            painter: The QPainter to draw with
            graph_width: Width of the graph area
        """
        for i, commit in enumerate(self.commits):
            node = self.graph.get_node(commit.sha)
            if not node:
                continue

            y = i * self.ROW_HEIGHT + self.ROW_HEIGHT // 2
            x = node.lane * self.LANE_WIDTH + self.LANE_WIDTH // 2

            # Draw node circle
            color = self.COLORS[node.color_index % len(self.COLORS)]

            # Highlight selected commit
            if self._selected_sha == commit.sha:
                painter.setPen(QPen(Qt.black, 3))
            else:
                painter.setPen(QPen(color.darker(120), 2))

            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPoint(x, y), self.NODE_RADIUS, self.NODE_RADIUS)

            # Draw commit info text
            text_x = graph_width
            text_rect = QRect(
                text_x, i * self.ROW_HEIGHT, self.width() - text_x - 10, self.ROW_HEIGHT
            )

            # Format: [short_sha] message - author
            commit_text = f"{commit.short_sha}  {commit.subject}"
            if len(commit_text) > 80:
                commit_text = commit_text[:77] + "..."

            painter.setPen(QPen(Qt.black))
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, commit_text)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse click events.

        Args:
            event: The mouse event
        """
        if event.button() == Qt.LeftButton and self.graph:
            # Find which commit was clicked
            row = event.pos().y() // self.ROW_HEIGHT
            if 0 <= row < len(self.commits):
                commit = self.commits[row]
                self._selected_sha = commit.sha
                self.commit_clicked.emit(commit.sha)
                self.update()

    def get_selected_commit(self) -> Optional[CommitInfo]:
        """
        Get the currently selected commit.

        Returns:
            The selected commit or None
        """
        if self._selected_sha:
            for commit in self.commits:
                if commit.sha == self._selected_sha:
                    return commit
        return None


class CommitGraphView(QWidget):
    """
    Scrollable commit graph view widget.

    Provides a complete graph visualization with scrolling, zooming,
    and commit selection capabilities.
    """

    commit_selected = Signal(str)  # Emits commit SHA when selected

    def __init__(self) -> None:
        super().__init__()

        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create canvas
        self.canvas = CommitGraphCanvas()
        self.canvas.commit_clicked.connect(self._on_commit_clicked)

        self.scroll_area.setWidget(self.canvas)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

    def update_commits(self, commits: List[CommitInfo]) -> None:
        """
        Update the displayed commits.

        Args:
            commits: List of commits to display
        """
        self.canvas.set_commits(commits)

    def _on_commit_clicked(self, sha: str) -> None:
        """
        Handle commit click event.

        Args:
            sha: The commit SHA that was clicked
        """
        self.commit_selected.emit(sha)

    def get_selected_commit(self) -> Optional[CommitInfo]:
        """
        Get the currently selected commit.

        Returns:
            The selected commit or None
        """
        return self.canvas.get_selected_commit()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Handle mouse wheel for zooming (future enhancement).

        Args:
            event: The wheel event
        """
        # For now, just pass to scroll area
        # Future: implement zoom functionality
        super().wheelEvent(event)
