"""
Graph algorithms for commit history visualization.

This module provides algorithms to compute branch topology, calculate
commit node layout, and generate connecting edges for graphical display.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from clevergit.models.commit_info import CommitInfo


@dataclass
class GraphNode:
    """
    Represents a node in the commit graph.
    
    Attributes:
        commit: The commit information
        lane: The horizontal lane/column where this node is drawn
        color_index: Index for color assignment
        parents: List of parent node SHAs
        children: List of child node SHAs
    """
    commit: CommitInfo
    lane: int = 0
    color_index: int = 0
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)


@dataclass
class GraphEdge:
    """
    Represents an edge connecting two nodes in the commit graph.
    
    Attributes:
        from_sha: Source commit SHA
        to_sha: Target commit SHA
        from_lane: Source lane
        to_lane: Target lane
        color_index: Color index for this edge
    """
    from_sha: str
    from_lane: int
    to_sha: str
    to_lane: int
    color_index: int


class CommitGraph:
    """
    Computes and manages the commit graph layout.
    
    This class implements algorithms for:
    - Topological ordering of commits
    - Lane assignment for branches
    - Color assignment for branch differentiation
    - Edge path calculation
    """
    
    def __init__(self, commits: List[CommitInfo]):
        """
        Initialize the commit graph.
        
        Args:
            commits: List of commits in chronological order (newest first)
        """
        self.commits = commits
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        
        self._build_graph()
    
    def _build_graph(self) -> None:
        """Build the graph structure from commits."""
        # Create nodes
        for commit in self.commits:
            node = GraphNode(
                commit=commit,
                parents=commit.parents.copy(),
                children=[]
            )
            self.nodes[commit.sha] = node
        
        # Build parent-child relationships
        for sha, node in self.nodes.items():
            for parent_sha in node.parents:
                if parent_sha in self.nodes:
                    self.nodes[parent_sha].children.append(sha)
        
        # Assign lanes and colors
        self._assign_lanes()
    
    def _assign_lanes(self) -> None:
        """
        Assign lanes (horizontal positions) to commits.
        
        Uses an improved algorithm that:
        1. Processes commits in chronological order (newest first)
        2. Tracks which lanes are "reserved" for parent commits
        3. Tries to keep linear history in the same lane
        4. Creates edges between parent-child nodes
        """
        # Track which parent SHA should continue in which lane
        lane_reservations: Dict[str, int] = {}
        
        for i, commit in enumerate(self.commits):
            node = self.nodes[commit.sha]
            
            # Check if this commit was reserved a lane by a child
            if commit.sha in lane_reservations:
                assigned_lane = lane_reservations[commit.sha]
                del lane_reservations[commit.sha]
            else:
                # Find first available lane
                assigned_lane = self._find_free_lane(lane_reservations)
            
            node.lane = assigned_lane
            node.color_index = assigned_lane % 8
            
            # Reserve lanes for parents
            for j, parent_sha in enumerate(node.parents):
                if parent_sha in self.nodes:
                    if j == 0:
                        # First parent continues in the same lane
                        lane_reservations[parent_sha] = assigned_lane
                    else:
                        # Additional parents get new lanes
                        parent_lane = self._find_free_lane(lane_reservations)
                        lane_reservations[parent_sha] = parent_lane
                    
                    # Create edge
                    target_lane = lane_reservations[parent_sha]
                    edge = GraphEdge(
                        from_sha=commit.sha,
                        from_lane=assigned_lane,
                        to_sha=parent_sha,
                        to_lane=target_lane,
                        color_index=node.color_index
                    )
                    self.edges.append(edge)
    
    def _find_free_lane(self, reservations: Dict[str, int]) -> int:
        """
        Find the first available lane that's not reserved.
        
        Args:
            reservations: Dictionary of SHA -> lane reservations
            
        Returns:
            The first free lane index
        """
        reserved_lanes = set(reservations.values())
        lane = 0
        while lane in reserved_lanes:
            lane += 1
        return lane
    
    def get_node(self, sha: str) -> Optional[GraphNode]:
        """
        Get a graph node by commit SHA.
        
        Args:
            sha: The commit SHA
            
        Returns:
            The graph node or None if not found
        """
        return self.nodes.get(sha)
    
    def get_edges_for_row(self, row_index: int) -> List[GraphEdge]:
        """
        Get edges that should be drawn at a specific row.
        
        Args:
            row_index: The row index (0 = first commit)
            
        Returns:
            List of edges to draw
        """
        if row_index >= len(self.commits):
            return []
        
        commit_sha = self.commits[row_index].sha
        
        # Return edges that start from this commit
        return [edge for edge in self.edges if edge.from_sha == commit_sha]
    
    def get_max_lane(self) -> int:
        """
        Get the maximum lane index used in the graph.
        
        Returns:
            The maximum lane index
        """
        if not self.nodes:
            return 0
        return max(node.lane for node in self.nodes.values())
