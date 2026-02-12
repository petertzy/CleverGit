"""
Test suite for commit graph algorithms.
"""

import pytest
from datetime import datetime
from clevergit.models.commit_info import CommitInfo
from clevergit.core.graph import CommitGraph, GraphNode, GraphEdge


def create_test_commit(sha: str, parents: list = None, message: str = "Test commit") -> CommitInfo:
    """Helper function to create a test commit."""
    if parents is None:
        parents = []
    return CommitInfo(
        sha=sha,
        short_sha=sha[:7],
        message=message,
        author="Test Author",
        author_email="test@example.com",
        date=datetime.now(),
        parents=parents
    )


def test_single_commit_graph():
    """Test graph with a single commit."""
    commits = [create_test_commit("abc123")]
    graph = CommitGraph(commits)
    
    assert len(graph.nodes) == 1
    assert "abc123" in graph.nodes
    
    node = graph.nodes["abc123"]
    assert node.lane == 0
    assert node.color_index == 0
    assert len(graph.edges) == 0


def test_linear_commit_history():
    """Test graph with linear commit history."""
    commits = [
        create_test_commit("commit3", parents=["commit2"]),
        create_test_commit("commit2", parents=["commit1"]),
        create_test_commit("commit1", parents=[]),
    ]
    graph = CommitGraph(commits)
    
    assert len(graph.nodes) == 3
    
    # All commits should be in the same lane
    assert graph.nodes["commit3"].lane == 0
    assert graph.nodes["commit2"].lane == 0
    assert graph.nodes["commit1"].lane == 0
    
    # Should have 2 edges
    assert len(graph.edges) == 2


def test_branching_history():
    """Test graph with branching history."""
    commits = [
        create_test_commit("main2", parents=["main1"]),
        create_test_commit("branch1", parents=["main1"]),
        create_test_commit("main1", parents=[]),
    ]
    graph = CommitGraph(commits)
    
    assert len(graph.nodes) == 3
    
    # main2 and branch1 should be in different lanes
    assert graph.nodes["main2"].lane != graph.nodes["branch1"].lane
    
    # Should have 2 edges (one from each branch to main1)
    assert len(graph.edges) == 2


def test_merge_commit():
    """Test graph with a merge commit."""
    commits = [
        create_test_commit("merge", parents=["main1", "branch1"]),
        create_test_commit("main1", parents=["base"]),
        create_test_commit("branch1", parents=["base"]),
        create_test_commit("base", parents=[]),
    ]
    graph = CommitGraph(commits)
    
    assert len(graph.nodes) == 4
    
    # Merge commit should have 2 parent edges
    merge_edges = [e for e in graph.edges if e.from_sha == "merge"]
    assert len(merge_edges) == 2


def test_get_node():
    """Test getting a node by SHA."""
    commits = [create_test_commit("abc123")]
    graph = CommitGraph(commits)
    
    node = graph.get_node("abc123")
    assert node is not None
    assert node.commit.sha == "abc123"
    
    # Non-existent node
    assert graph.get_node("nonexistent") is None


def test_get_edges_for_row():
    """Test getting edges for a specific row."""
    commits = [
        create_test_commit("commit2", parents=["commit1"]),
        create_test_commit("commit1", parents=[]),
    ]
    graph = CommitGraph(commits)
    
    # Row 0 should have edges from commit2 to commit1
    edges = graph.get_edges_for_row(0)
    assert len(edges) == 1
    assert edges[0].from_sha == "commit2"
    assert edges[0].to_sha == "commit1"
    
    # Row 1 should have no outgoing edges
    edges = graph.get_edges_for_row(1)
    assert len(edges) == 0


def test_get_max_lane():
    """Test getting the maximum lane index."""
    commits = [
        create_test_commit("commit1", parents=[]),
    ]
    graph = CommitGraph(commits)
    assert graph.get_max_lane() == 0
    
    # Test with branching
    commits = [
        create_test_commit("main2", parents=["main1"]),
        create_test_commit("branch1", parents=["main1"]),
        create_test_commit("main1", parents=[]),
    ]
    graph = CommitGraph(commits)
    assert graph.get_max_lane() >= 1  # At least 2 lanes


def test_parent_child_relationships():
    """Test parent-child relationships are built correctly."""
    commits = [
        create_test_commit("child", parents=["parent"]),
        create_test_commit("parent", parents=[]),
    ]
    graph = CommitGraph(commits)
    
    parent_node = graph.nodes["parent"]
    child_node = graph.nodes["child"]
    
    assert "parent" in child_node.parents
    assert "child" in parent_node.children


def test_color_assignment():
    """Test that colors are assigned consistently."""
    commits = [
        create_test_commit("commit1", parents=[]),
    ]
    graph = CommitGraph(commits)
    
    node = graph.nodes["commit1"]
    # Color should be assigned based on lane
    assert node.color_index == node.lane % 8


def test_empty_commit_list():
    """Test graph with no commits."""
    commits = []
    graph = CommitGraph(commits)
    
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0
    assert graph.get_max_lane() == 0


def test_complex_branching():
    """Test a more complex branching scenario."""
    # Create a realistic branching scenario:
    #   * feature2
    #   * feature1
    #   | * branch2
    #   | * branch1
    #   |/
    #   * main1
    #   * main0
    commits = [
        create_test_commit("feature2", parents=["feature1"]),
        create_test_commit("feature1", parents=["main1"]),
        create_test_commit("branch2", parents=["branch1"]),
        create_test_commit("branch1", parents=["main1"]),
        create_test_commit("main1", parents=["main0"]),
        create_test_commit("main0", parents=[]),
    ]
    graph = CommitGraph(commits)
    
    assert len(graph.nodes) == 6
    
    # Verify that different branches use different lanes
    feature_lane = graph.nodes["feature1"].lane
    branch_lane = graph.nodes["branch1"].lane
    assert feature_lane != branch_lane
    
    # Both branches should converge back to main1
    feature_edges = [e for e in graph.edges if e.from_sha == "feature1"]
    branch_edges = [e for e in graph.edges if e.from_sha == "branch1"]
    
    assert any(e.to_sha == "main1" for e in feature_edges)
    assert any(e.to_sha == "main1" for e in branch_edges)
