"""
盘古造物工具包

用于 meta skill 的信息采集

使用方式：

1. 命令行:
   uv run python scripts/run.py search "芒格 思维框架"
   uv run python scripts/run.py collect "芒格"

2. Python API:
   from scripts.search import SearchPipeline

   pipeline = SearchPipeline()
   results = pipeline.search_and_fetch("芒格 思维框架")
"""

from .search import SearchPipeline, AgentSearchTool
from .config import (
    search_config,
    crawl_config,
    transcribe_config,
    storage_config,
    get_default_dimensions,
)

__all__ = [
    "SearchPipeline",
    "AgentSearchTool",
    "search_config",
    "crawl_config",
    "transcribe_config",
    "storage_config",
    "get_default_dimensions",
]
