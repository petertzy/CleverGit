"""Dark theme implementation."""

from .base import Theme


class DarkTheme(Theme):
    """Dark color theme."""

    def __init__(self):
        super().__init__(
            name="dark",
            # Background colors
            background="#1e1e1e",
            background_secondary="#252526",
            background_hover="#2a2d2e",
            # Text colors
            text="#d4d4d4",
            text_secondary="#a0a0a0",
            text_disabled="#6e6e6e",
            # Button colors
            button_primary="#0e639c",
            button_success="#107c10",
            button_warning="#ca5010",
            button_danger="#c42b1c",
            button_info="#0e639c",
            # Diff colors
            diff_added="#1a3d2e",
            diff_removed="#4b1818",
            diff_modified="#3d3721",
            diff_context="#1e1e1e",
            # Graph colors (adjusted for dark theme)
            graph_colors=[
                "#f48771",  # light red
                "#6cb6ff",  # light blue
                "#73c991",  # light green
                "#f9cb8f",  # light orange
                "#c68af1",  # light purple
                "#76d7c4",  # light turquoise
                "#f0a878",  # light carrot
                "#b8bcbe",  # light gray
            ],
            # Border and separator colors
            border="#3e3e42",
            separator="#454545",
            # Status colors
            status_success="#107c10",
            status_warning="#ca5010",
            status_error="#c42b1c",
            status_info="#0e639c",
            # Selection colors
            selection_background="#094771",
            selection_text="#ffffff",
        )
