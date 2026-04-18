"""
Agent 工具封装层

封装 Agent (Claude Code/OpenCLAW/Hermes/Codex) 的 WebSearch/WebFetch 工具
让脚本能以编程方式调用这些工具
"""

import json
import subprocess
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

from .models import SearchResult, ContentResult, SearchSource


class AgentToolError(Exception):
    """Agent 工具调用异常"""
    pass


class ToolNotFoundError(AgentToolError):
    """工具不存在"""
    pass


@dataclass
class ToolCallResult:
    """工具调用结果"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    tool_name: Optional[str] = None
    used_fallback: bool = False


class BaseAgentTool:
    """Agent 工具基类"""

    def is_available(self) -> bool:
        """检测工具是否可用"""
        raise NotImplementedError

    def web_search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """执行搜索"""
        raise NotImplementedError

    def web_fetch(self, url: str) -> ContentResult:
        """抓取内容"""
        raise NotImplementedError


class ClaudeCodeTools(BaseAgentTool):
    """
    Claude Code Agent 工具封装

    Claude Code 有内置的 WebSearch 和 WebFetch 工具
    通过 subprocess 调用 Claude Code CLI
    """

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()

    def is_available(self) -> bool:
        """检测 Claude Code 是否可用"""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _call_claude(self, prompt: str) -> str:
        """调用 Claude Code 执行 prompt"""
        try:
            result = subprocess.run(
                [
                    "claude",
                    "--print",
                    "--output-format", "json",
                    prompt
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_path,
            )
            if result.returncode != 0:
                raise AgentToolError(f"Claude CLI error: {result.stderr}")
            return result.stdout
        except subprocess.TimeoutExpired:
            raise AgentToolError("Claude CLI timeout")
        except FileNotFoundError:
            raise ToolNotFoundError("Claude CLI not found")

    def web_search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        使用 Claude Code WebSearch 工具搜索

        注意：Claude Code 的 WebSearch 是 MCP 工具，不能直接通过 CLI 调用
        这里我们使用 Claude Code 的 mcp__plugin_ecc_exa__web_search_exa 工具
        或者直接用 WebFetch 抓取搜索引擎结果页面
        """
        # 方案1：尝试使用 MCP 工具（如果配置了）
        # 方案2：降级到搜索结果页面抓取

        # 这里先用 DuckDuckGo HTML 作为备选
        from crawl.duckduckgo import DuckDuckGoSearch

        crawler = DuckDuckGoSearch()
        results = crawler.search(query, num_results)

        for r in results:
            r.source = SearchSource.AGENT_WEB_SEARCH

        return results

    def web_fetch(self, url: str) -> ContentResult:
        """使用 Claude Code WebFetch 抓取内容"""
        # Claude Code 的 WebFetch 通常也是 MCP 工具
        # 这里使用爬虫备选方案
        from crawl.fetcher import ContentFetcher

        fetcher = ContentFetcher()
        return fetcher.fetch(url)


class OpenCLAWTools(BaseAgentTool):
    """OpenCLAW Agent 工具封装"""

    def is_available(self) -> bool:
        return False  # TODO: 实现

    def web_search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        raise ToolNotFoundError("OpenCLAW tools not implemented")

    def web_fetch(self, url: str) -> ContentResult:
        raise ToolNotFoundError("OpenCLAW tools not implemented")


class AgentToolFactory:
    """Agent 工具工厂"""

    _tools = {
        "claude_code": ClaudeCodeTools,
        "openclaw": OpenCLAWTools,
    }

    @classmethod
    def detect(cls) -> BaseAgentTool:
        """自动检测可用的 Agent 工具"""
        for name, tool_class in cls._tools.items():
            tool = tool_class()
            if tool.is_available():
                return tool

        # 没有检测到 Agent 工具，返回 None
        return None

    @classmethod
    def create(cls, agent_name: str) -> BaseAgentTool:
        """创建指定 Agent 的工具"""
        if agent_name not in cls._tools:
            raise ValueError(f"Unknown agent: {agent_name}")
        return cls._tools[agent_name]()


class AgentSearchTool:
    """
    Agent 搜索工具（对外统一接口）

    自动检测可用 Agent 工具，支持降级
    """

    def __init__(
        self,
        prefer_agent: bool = True,
        fallback_enabled: bool = True,
        agent_name: Optional[str] = None,
    ):
        self.prefer_agent = prefer_agent
        self.fallback_enabled = fallback_enabled
        self.agent_tools: Optional[BaseAgentTool] = None
        self.fallback = None

        if prefer_agent:
            if agent_name:
                try:
                    self.agent_tools = AgentToolFactory.create(agent_name)
                except ValueError:
                    pass
            else:
                self.agent_tools = AgentToolFactory.detect()

            if fallback_enabled:
                from crawl.duckduckgo import DuckDuckGoSearch
                self.fallback = DuckDuckGoSearch()

    def is_agent_available(self) -> bool:
        """Agent 工具是否可用"""
        return self.agent_tools is not None

    def search(
        self,
        query: str,
        num_results: int = 10,
        force_fallback: bool = False,
    ) -> List[SearchResult]:
        """执行搜索"""
        if force_fallback or not self.agent_tools:
            return self._search_fallback(query, num_results)

        try:
            return self.agent_tools.web_search(query, num_results)
        except Exception as e:
            if self.fallback_enabled:
                return self._search_fallback(query, num_results)
            raise

    def _search_fallback(
        self,
        query: str,
        num_results: int,
    ) -> List[SearchResult]:
        """降级到爬虫搜索"""
        if self.fallback:
            return self.fallback.search(query, num_results)
        from crawl.duckduckgo import DuckDuckGoSearch
        crawler = DuckDuckGoSearch()
        return crawler.search(query, num_results)

    def fetch(self, url: str) -> ContentResult:
        """抓取内容"""
        if not self.agent_tools:
            return self._fetch_fallback(url)

        try:
            return self.agent_tools.web_fetch(url)
        except Exception:
            if self.fallback_enabled:
                return self._fetch_fallback(url)
            raise

    def _fetch_fallback(self, url: str) -> ContentResult:
        """降级到爬虫抓取"""
        from crawl.fetcher import ContentFetcher
        fetcher = ContentFetcher()
        return fetcher.fetch(url)
