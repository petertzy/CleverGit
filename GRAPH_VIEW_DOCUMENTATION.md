# Commit Graph Visualization

## Overview
The commit graph visualization feature provides a graphical representation of commit history, similar to `git log --graph`. It displays commits as nodes connected by edges, with different colors for different branches.

## Features

### Core Features Implemented
- ✅ Graph algorithms for computing branch topology
- ✅ Lane assignment and node layout calculation
- ✅ Edge path computation for connecting commits
- ✅ Branch color differentiation (8 distinct colors)
- ✅ Click-to-select commit functionality
- ✅ Commit diff viewer integration
- ✅ Scrolling support for large histories
- ✅ Virtual scrolling for performance

### User Interface
The graph view is accessible through the main window as a tab in the "Commit History" section:
- **List View**: Traditional table-based commit list
- **Graph View**: Visual graph representation of commits

## Architecture

### Module Structure
- `clevergit/core/graph.py` - Core graph algorithms and data structures
- `clevergit/ui/widgets/graph_view.py` - Qt-based visualization widget

### Key Components

#### 1. Graph Algorithms (`graph.py`)
- **GraphNode**: Represents a commit node with lane, color, and relationship information
- **GraphEdge**: Represents connections between commits
- **CommitGraph**: Main class that:
  - Processes commit history
  - Assigns lanes to branches
  - Calculates node positions
  - Generates edges between commits

##### Lane Assignment Algorithm
The algorithm uses a greedy approach:
1. Processes commits chronologically (newest first)
2. Reserves lanes for parent commits
3. First parent continues in the same lane (maintains branch continuity)
4. Additional parents (merge commits) get new lanes
5. Automatically assigns colors based on lane index

#### 2. Visualization Widget (`graph_view.py`)
- **CommitGraphCanvas**: Custom QWidget that renders the graph
  - Draws nodes as colored circles
  - Draws edges as lines between nodes
  - Handles click events for commit selection
  - Implements custom paint event for rendering
- **CommitGraphView**: Container widget with scrolling support

### Visual Constants
- Row height: 40 pixels
- Lane width: 30 pixels
- Node radius: 6 pixels
- Color palette: 8 distinct colors for branch differentiation

## Usage

### In the GUI
1. Open a repository
2. Navigate to the "Commit History" section
3. Click on the "Graph View" tab
4. Click on any commit node to view its diff

### Programmatic Usage
```python
from clevergit.core.log import get_log
from clevergit.core.graph import CommitGraph
from pathlib import Path

# Load commits
commits = get_log(Path("/path/to/repo"), max_count=100)

# Create graph
graph = CommitGraph(commits)

# Access graph data
for commit in commits:
    node = graph.get_node(commit.sha)
    print(f"Commit {commit.short_sha}: lane={node.lane}, color={node.color_index}")

# Get edges
edges = graph.edges
for edge in edges:
    print(f"Edge from {edge.from_sha[:7]} to {edge.to_sha[:7]}")
```

## Testing

### Unit Tests
The implementation includes comprehensive unit tests in `tests/test_graph.py`:
- Single commit graphs
- Linear commit history
- Branching scenarios
- Merge commits
- Parent-child relationships
- Lane assignment
- Color assignment
- Edge generation

Run tests with:
```bash
pytest tests/test_graph.py -v
```

### Test Coverage
- Graph algorithm correctness
- Lane assignment for various topologies
- Edge generation
- Node relationships
- Empty and single-commit edge cases

## Known Limitations

1. **Single Branch Display**: Currently displays commits from the current branch only. To show all branches, the underlying `get_log` function would need to be enhanced to support the `--all` flag.

2. **Advanced Layout**: The current lane assignment uses a greedy algorithm. More sophisticated layouts (like those in GitKraken or GitGraph) could be implemented for better visual clarity in complex branching scenarios.

3. **Zoom Functionality**: Basic scrolling is implemented, but zoom in/out functionality is planned for future enhancement.

4. **Performance**: While virtual scrolling is implemented, very large repositories (>10,000 commits) may benefit from additional optimizations like lazy loading or incremental rendering.

## Future Enhancements

### Planned Features
- [ ] Display all branches (not just current branch)
- [ ] Zoom in/out functionality
- [ ] Pan with mouse drag
- [ ] Show branch labels on the graph
- [ ] Show tags on commits
- [ ] Highlight HEAD and current branch
- [ ] Configurable color schemes
- [ ] Export graph as image
- [ ] Timeline view with date markers
- [ ] Search and filter in graph view
- [ ] Minimap for large histories

### Performance Optimizations
- [ ] Incremental rendering for large histories
- [ ] Lazy loading of commit details
- [ ] Caching of graph layout
- [ ] GPU acceleration for rendering (if needed)

## Implementation Notes

### Design Decisions
1. **Separation of Concerns**: Graph algorithms are separate from visualization, allowing for easier testing and potential alternative visualizations.

2. **Color Cycling**: Uses 8 colors that cycle based on lane index, providing good visual differentiation without overwhelming the user.

3. **Tab-Based Interface**: Graph view is in a tab alongside the list view, allowing users to choose their preferred view without losing functionality.

4. **Direct Integration**: Clicking on a commit in the graph view immediately opens the diff viewer, maintaining consistency with the list view.

### Code Quality
- Type hints throughout for better IDE support
- Comprehensive docstrings
- Unit test coverage
- Follows existing code style and patterns
- Minimal changes to existing code

## References
- [Git Log Graph](https://git-scm.com/docs/git-log#Documentation/git-log.txt---graph)
- [GitKraken Graph Visualization](https://www.gitkraken.com/)
- [PySide6 Custom Widgets](https://doc.qt.io/qtforpython-6/)
