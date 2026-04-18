"""
Test logging configuration and usage.

RED PHASE: Write tests that verify:
1. Logger is properly configured with name
2. Logging level can be controlled
3. Log format is consistent
"""

import logging
import pytest
from unittest.mock import patch, MagicMock


class TestLoggingConfiguration:
    """Test that logging is properly configured in modules."""

    def test_collector_has_logger_configured(self):
        """Collector module should have a logger instance, not print statements."""
        from scripts.search import collector

        # Verify collector module has a logger attribute
        assert hasattr(collector, 'logger'), "collector module should have a logger"
        assert isinstance(collector.logger, logging.Logger), "logger should be a Logger instance"
        assert collector.logger.name == "scripts.search.collector"

    def test_multi_agent_has_logger_configured(self):
        """MultiAgent module should have a logger instance, not print statements."""
        from scripts.search import multi_agent

        # Verify multi_agent module has a logger attribute
        assert hasattr(multi_agent, 'logger'), "multi_agent module should have a logger"
        assert isinstance(multi_agent.logger, logging.Logger), "logger should be a Logger instance"
        assert multi_agent.logger.name == "scripts.search.multi_agent"

    def test_collector_logger_level_controllable(self):
        """Collector logger level should be settable via module-level function."""
        from scripts.search import collector

        # Should be able to set log level
        original_level = collector.logger.level

        # Set to DEBUG and verify
        collector.set_log_level(logging.DEBUG)
        assert collector.logger.level == logging.DEBUG

        # Set back to original
        collector.set_log_level(original_level)

    def test_multi_agent_logger_level_controllable(self):
        """MultiAgent logger level should be settable via module-level function."""
        from scripts.search import multi_agent

        original_level = multi_agent.logger.level

        multi_agent.set_log_level(logging.INFO)
        assert multi_agent.logger.level == logging.INFO

        multi_agent.set_log_level(original_level)

    def test_log_format_includes_module_info(self):
        """Log format should include module name and level."""
        from scripts.search import collector

        # Verify the logger has handlers with proper formatting
        assert collector.logger.handlers, "logger should have at least one handler"

        formatter = collector.logger.handlers[0].formatter
        if formatter:
            format_string = formatter._fmt
            # Should include at least level and message
            assert '%(levelname)s' in format_string or 'level' in format_string.lower()
            assert '%(message)s' in format_string or 'msg' in format_string.lower()


class TestNoPrintStatements:
    """Verify that print statements have been replaced with logging."""

    def test_collector_no_print_statements(self):
        """Collector module should not contain print function calls."""
        import ast
        from pathlib import Path

        collector_path = Path(__file__).parent.parent / "search" / "collector.py"
        source = collector_path.read_text()
        tree = ast.parse(source)

        print_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    print_calls.append(node.lineno)

        assert len(print_calls) == 0, f"Found {len(print_calls)} print statements at lines: {print_calls}"

    def test_multi_agent_no_print_statements(self):
        """MultiAgent module should not contain print function calls."""
        import ast
        from pathlib import Path

        multi_agent_path = Path(__file__).parent.parent / "search" / "multi_agent.py"
        source = multi_agent_path.read_text()
        tree = ast.parse(source)

        print_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    print_calls.append(node.lineno)

        assert len(print_calls) == 0, f"Found {len(print_calls)} print statements at lines: {print_calls}"
