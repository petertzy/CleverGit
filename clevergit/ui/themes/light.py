"""Light theme implementation."""

from .base import Theme


class LightTheme(Theme):
    """Light color theme."""

    def __init__(self):
        super().__init__(
            name="light",
            # Background colors
            background="#ffffff",
            background_secondary="#f6f8fa",
            background_hover="#e1e4e8",
            # Text colors
            text="#24292e",
            text_secondary="#586069",
            text_disabled="#959da5",
            # Button colors
            button_primary="#0366d6",
            button_success="#28a745",
            button_warning="#ff9800",
            button_danger="#d73a49",
            button_info="#0366d6",
            # Diff colors
            diff_added="#e6ffed",
            diff_removed="#ffeef0",
            diff_modified="#fff8c5",
            diff_context="#ffffff",
            # Graph colors (matching existing colors)
            graph_colors=[
                "#e74c3c",  # red
                "#3498db",  # blue
                "#2ecc71",  # green
                "#f39c12",  # orange
                "#9b59b6",  # purple
                "#1abc9c",  # turquoise
                "#e67e22",  # carrot
                "#95a5a6",  # gray
            ],
            # Border and separator colors
            border="#d1d5da",
            separator="#e1e4e8",
            # Status colors
            status_success="#28a745",
            status_warning="#ff9800",
            status_error="#d73a49",
            status_info="#0366d6",
            # Selection colors
            selection_background="#0366d6",
            selection_text="#ffffff",
        )
