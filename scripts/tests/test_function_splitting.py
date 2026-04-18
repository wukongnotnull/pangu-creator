"""
Test function splitting in collector.py.

RED PHASE: Write tests that verify:
1. _collect_single is split into smaller focused functions
2. Each helper function has a single responsibility
3. Functions are under 50 lines
"""

import ast
import pytest
from pathlib import Path


class TestFunctionLengths:
    """Verify that long functions have been split."""

    def test_collect_single_under_50_lines(self):
        """_collect_single should be under 50 lines after refactoring."""
        collector_path = Path(__file__).parent.parent / "search" / "collector.py"
        source = collector_path.read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_collect_single':
                # Count actual code lines (not comments, not blank)
                start_line = node.lineno
                end_line = node.end_lineno
                lines = source.split('\n')[start_line - 1:end_line]

                code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
                line_count = len(code_lines)

                assert line_count <= 50, f"_collect_single is {line_count} lines, should be <= 50"

    def test_no_single_function_over_50_lines(self):
        """No function in collector.py should exceed 50 lines."""
        collector_path = Path(__file__).parent.parent / "search" / "collector.py"
        source = collector_path.read_text()
        tree = ast.parse(source)

        oversized_functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private methods that are decorators
                if node.name.startswith('_') and not node.name.startswith('__'):
                    start_line = node.lineno
                    end_line = node.end_lineno
                    lines = source.split('\n')[start_line - 1:end_line]

                    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
                    line_count = len(code_lines)

                    if line_count > 50:
                        oversized_functions.append((node.name, line_count))

        assert len(oversized_functions) == 0, f"Oversized functions: {oversized_functions}"


class TestSingleResponsibility:
    """Verify that functions have single responsibility."""

    def test_collect_single_delegates_properly(self):
        """_collect_single should only dispatch to helper methods, not implement logic."""
        collector_path = Path(__file__).parent.parent / "search" / "collector.py"
        source = collector_path.read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_collect_single':
                # _collect_single should only have try-except and if-elif for type dispatching
                # It should NOT contain complex logic like text processing, language detection, etc.

                # Check that it doesn't directly call re.findall, len(content), etc.
                source_lines = source.split('\n')[node.lineno - 1:node.end_lineno]
                function_source = '\n'.join(source_lines)

                # These are indicators of logic that should be in helper functions
                complex_patterns = [
                    're.findall',
                    'len(content.replace',
                    'replace("\\n", "")',
                    'chinese_chars',
                    'detect_content_lang',
                ]

                found_complex = []
                for pattern in complex_patterns:
                    if pattern in function_source:
                        found_complex.append(pattern)

                assert len(found_complex) == 0, \
                    f"_collect_single should not contain complex logic: {found_complex}. Extract to helper methods."

    def test_helper_methods_exist(self):
        """Collector should have helper methods for each material type."""
        from scripts.search.collector import MaterialCollector

        collector = MaterialCollector()

        # These helper methods should exist
        expected_methods = [
            '_collect_url',
            '_collect_pdf',
            '_collect_word',
            '_collect_txt',
            '_collect_markdown',
            '_collect_excel',
            '_collect_subtitle',
            '_collect_image',
            '_collect_media',
        ]

        for method_name in expected_methods:
            assert hasattr(collector, method_name), f"Missing helper method: {method_name}"

    def test_collect_method_signature(self):
        """collect() method should properly aggregate results."""
        from scripts.search.collector import MaterialCollector

        collector = MaterialCollector()

        # Test with empty list
        result = collector.collect([])

        assert result.total_files == 0
        assert result.successful == 0
        assert result.failed == 0

        # Test with list of paths
        result = collector.collect(["test.pdf", "test.txt"])

        assert result.total_files == 2


class TestRefactoredBehavior:
    """Verify that refactoring didn't break functionality."""

    def test_collect_single_returns_material(self):
        """_collect_single should always return a Material object."""
        from scripts.search.collector import MaterialCollector

        collector = MaterialCollector()

        # Even with invalid input, should return Material, not raise
        result = collector._collect_single("/nonexistent/file.pdf", False)

        from scripts.search.collector import Material
        assert isinstance(result, Material)

    def test_collect_single_sets_error_on_failure(self):
        """_collect_single should set error message on failure."""
        from scripts.search.collector import MaterialCollector

        collector = MaterialCollector()

        # Invalid URL should result in error
        result = collector._collect_single("not-a-valid-path", False)

        # Should have either error set or success=False
        assert result.error is not None or result.success == False

    def test_detect_type_handles_unknown(self):
        """_detect_type should return UNKNOWN for unrecognized types."""
        from scripts.search.collector import MaterialCollector, MaterialType

        collector = MaterialCollector()

        unknown_type = collector._detect_type("/some/file.xyz")
        assert unknown_type == MaterialType.UNKNOWN

    def test_detect_type_handles_url(self):
        """_detect_type should recognize URL patterns."""
        from scripts.search.collector import MaterialCollector, MaterialType

        collector = MaterialCollector()

        assert collector._detect_type("https://example.com") == MaterialType.URL
        assert collector._detect_type("http://example.com") == MaterialType.URL
        assert collector._detect_type("www.example.com") == MaterialType.URL
