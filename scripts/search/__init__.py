"""
search 模块 - Agent 工具封装 + 备选爬虫

主方案：Agent 工具封装（agent_tools.py）
备选方案：爬虫实现（fallback.py, ../crawl/）
"""

from .pipeline import SearchPipeline
from .agent_tools import AgentSearchTool
from .fallback import FallbackTrigger, CrawlerFallback
from .models import SearchResult, ContentResult

__all__ = [
    "SearchPipeline",
    "AgentSearchTool",
    "FallbackTrigger",
    "CrawlerFallback",
]
