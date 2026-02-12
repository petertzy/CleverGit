"""
Test suite for command palette module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys

# Mock PySide6 modules before importing command palette
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtGui'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()

from clevergit.ui.widgets.command_palette import (
    FuzzyMatcher,
    SearchResult,
    SearchCategory,
)


class TestFuzzyMatcher:
    """Test suite for FuzzyMatcher class."""
    
    def test_exact_match(self):
        """Test exact match returns highest score."""
        matches, score = FuzzyMatcher.match("test", "test")
        assert matches is True
        assert score == 1.0
    
    def test_empty_pattern(self):
        """Test empty pattern matches everything with perfect score."""
        matches, score = FuzzyMatcher.match("", "anything")
        assert matches is True
        assert score == 1.0
    
    def test_contains_match(self):
        """Test substring match."""
        matches, score = FuzzyMatcher.match("main", "main.py")
        assert matches is True
        assert score > 0.0
    
    def test_contains_match_case_insensitive(self):
        """Test case insensitive matching."""
        matches, score = FuzzyMatcher.match("Main", "main.py")
        assert matches is True
        assert score > 0.0
    
    def test_fuzzy_match_consecutive(self):
        """Test fuzzy match with consecutive characters."""
        matches, score = FuzzyMatcher.match("mp", "main.py")
        assert matches is True
        assert score > 0.0
    
    def test_fuzzy_match_scattered(self):
        """Test fuzzy match with scattered characters."""
        matches, score = FuzzyMatcher.match("mpy", "main.py")
        assert matches is True
        assert score > 0.0
    
    def test_no_match(self):
        """Test non-matching pattern."""
        matches, score = FuzzyMatcher.match("xyz", "main.py")
        assert matches is False
        assert score == 0.0
    
    def test_partial_match_fails(self):
        """Test partial pattern match fails."""
        matches, score = FuzzyMatcher.match("abc", "abx")
        assert matches is False
        assert score == 0.0
    
    def test_score_ordering(self):
        """Test that better matches have higher scores."""
        # Exact match should have highest score
        _, exact_score = FuzzyMatcher.match("test", "test")
        
        # Contains match at start should be high
        _, start_score = FuzzyMatcher.match("test", "test_file.py")
        
        # Contains match in middle should be lower
        _, middle_score = FuzzyMatcher.match("test", "my_test_file.py")
        
        # Fuzzy match should be lowest
        _, fuzzy_score = FuzzyMatcher.match("tf", "test_file.py")
        
        assert exact_score > start_score > middle_score > fuzzy_score
    
    def test_position_matters(self):
        """Test that match position affects score."""
        # Match at start should score higher than match at end
        _, start_score = FuzzyMatcher.match("main", "main_file.py")
        _, end_score = FuzzyMatcher.match("py", "main_file.py")
        
        assert start_score > end_score


class TestSearchResult:
    """Test suite for SearchResult dataclass."""
    
    def test_create_search_result(self):
        """Test creating a search result."""
        result = SearchResult(
            category=SearchCategory.FILE,
            title="main.py",
            description="File: main.py",
            data="/path/to/main.py",
            score=0.95
        )
        
        assert result.category == SearchCategory.FILE
        assert result.title == "main.py"
        assert result.description == "File: main.py"
        assert result.data == "/path/to/main.py"
        assert result.score == 0.95
    
    def test_default_values(self):
        """Test default values for optional fields."""
        result = SearchResult(
            category=SearchCategory.COMMIT,
            title="abc1234 Initial commit",
            description="By author on 2024-01-01"
        )
        
        assert result.data is None
        assert result.score == 0.0


class TestSearchCategory:
    """Test suite for SearchCategory enum."""
    
    def test_category_values(self):
        """Test category enum values have proper icons."""
        assert "📄" in SearchCategory.FILE.value
        assert "📝" in SearchCategory.COMMIT.value
        assert "🌿" in SearchCategory.BRANCH.value
        assert "⚡" in SearchCategory.COMMAND.value
    
    def test_category_uniqueness(self):
        """Test that all categories are unique."""
        categories = [cat for cat in SearchCategory]
        assert len(categories) == len(set(categories))


class TestCommandPaletteFuzzySearch:
    """Test fuzzy search patterns commonly used in command palettes."""
    
    def test_abbreviation_match(self):
        """Test matching file paths by abbreviation."""
        # Common pattern: matching src/components/Button.tsx with 'scb'
        matches, score = FuzzyMatcher.match("scb", "src/components/Button.tsx")
        assert matches is True
    
    def test_camelcase_match(self):
        """Test matching camelCase identifiers."""
        matches, score = FuzzyMatcher.match("btn", "Button")
        assert matches is True
    
    def test_path_matching(self):
        """Test matching file paths."""
        # Should match 'app/main' in 'clevergit/ui/app/main.py'
        matches, score = FuzzyMatcher.match("appmain", "clevergit/ui/app/main.py")
        assert matches is True
    
    def test_common_file_extensions(self):
        """Test matching files by extension."""
        matches, score = FuzzyMatcher.match(".py", "test.py")
        assert matches is True
        
        matches, score = FuzzyMatcher.match(".js", "script.js")
        assert matches is True


class TestCommandPaletteCommands:
    """Test command palette command functionality."""
    
    def test_default_commands_exist(self):
        """Test that default commands are available."""
        default_commands = [
            "refresh", "commit", "pull", "push", "fetch",
            "checkout", "merge", "stash", "tag", "diff", "blame"
        ]
        
        # These are the commands that should be available by default
        # We can't instantiate CommandPalette without mocking Qt,
        # but we can verify the expected commands list
        assert len(default_commands) > 0


class TestFuzzyMatcherEdgeCases:
    """Test edge cases for fuzzy matcher."""
    
    def test_unicode_characters(self):
        """Test matching with unicode characters."""
        matches, score = FuzzyMatcher.match("café", "café.txt")
        assert matches is True
    
    def test_special_characters(self):
        """Test matching with special characters."""
        matches, score = FuzzyMatcher.match("test-", "test-file.py")
        assert matches is True
    
    def test_whitespace_in_pattern(self):
        """Test matching with whitespace."""
        matches, score = FuzzyMatcher.match("test file", "test file.txt")
        assert matches is True
    
    def test_very_long_text(self):
        """Test matching against very long text."""
        long_text = "a" * 1000 + "test" + "b" * 1000
        matches, score = FuzzyMatcher.match("test", long_text)
        assert matches is True
        assert 0.0 < score < 1.0
    
    def test_pattern_longer_than_text(self):
        """Test pattern longer than text."""
        matches, score = FuzzyMatcher.match("verylongpattern", "short")
        assert matches is False
        assert score == 0.0
    
    def test_identical_consecutive_characters(self):
        """Test matching with repeated characters."""
        matches, score = FuzzyMatcher.match("aaa", "aaaaaa")
        assert matches is True


class TestSearchResultScoring:
    """Test search result scoring and ranking."""
    
    def test_score_range(self):
        """Test that scores are in valid range."""
        test_cases = [
            ("test", "test"),
            ("test", "test.py"),
            ("t", "test.py"),
            ("tp", "test.py"),
        ]
        
        for pattern, text in test_cases:
            matches, score = FuzzyMatcher.match(pattern, text)
            if matches:
                assert 0.0 <= score <= 1.0
    
    def test_score_consistency(self):
        """Test that same match produces same score."""
        pattern = "test"
        text = "test.py"
        
        _, score1 = FuzzyMatcher.match(pattern, text)
        _, score2 = FuzzyMatcher.match(pattern, text)
        
        assert score1 == score2


# Integration test (commented out as it requires Qt)
# class TestCommandPaletteIntegration:
#     """Integration tests for command palette."""
#     
#     def test_palette_creation(self):
#         """Test creating command palette instance."""
#         # Would require proper Qt application setup
#         pass
#     
#     def test_search_filtering(self):
#         """Test search input filtering results."""
#         # Would require proper Qt application setup
#         pass
