"""
Bing 搜索实现

需要 API key 或直接抓取（有限制）
"""

import re
from typing import List

import requests
from bs4 import BeautifulSoup

from crawl.base import BaseSearchEngine
from shared import SearchSource, SearchResult


class BingSearch(BaseSearchEngine):
    """
    Bing 搜索

    方式1: 使用 Bing API（需要 key）
    方式2: 直接抓取（反爬较严）
    """

    BASE_URL = "https://www.bing.com/search"
    TIMEOUT = 10

    def __init__(
        self,
        api_key: str = None,
        delay: float = 2.0,
        user_agent: str = None,
    ):
        """
        Args:
            api_key: Bing API key（可选，有 key 更稳定）
            delay: 请求间隔
            user_agent: 自定义 User-Agent
        """
        super().__init__(delay)
        self.api_key = api_key
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        执行 Bing 搜索

        Args:
            query: 搜索查询
            num_results: 结果数量

        Returns:
            搜索结果列表
        """
        query = self._validate_query(query)
        num_results = self._validate_num_results(num_results)

        if self.api_key:
            return self._search_api(query, num_results)
        else:
            return self._search_html(query, num_results)

    def _search_api(self, query: str, num_results: int) -> List[SearchResult]:
        """使用 Bing API 搜索"""
        # TODO: 实现 Bing API 调用
        # API: https://api.bing.microsoft.com/v7.0/search
        raise NotImplementedError("Bing API 尚未实现，请使用 html 搜索模式")

    def _search_html(self, query: str, num_results: int) -> List[SearchResult]:
        """直接抓取 Bing 搜索结果"""
        self._wait_before_request()

        try:
            params = {
                "q": query,
                "count": num_results,
                "setLang": "zh-CN",
            }
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()

            return self._parse_results(response.text, num_results)

        except requests.RequestException as e:
            raise RuntimeError(f"Bing 搜索失败: {e}")

    def _parse_results(self, html: str, limit: int) -> List[SearchResult]:
        """解析 Bing 搜索结果"""
        soup = BeautifulSoup(html, "lxml")
        results = []

        # Bing 结果结构
        for item in soup.select(".b_algo")[:limit]:
            try:
                # 标题和链接
                link_elem = item.select_one("h2 a")
                if not link_elem:
                    continue

                title = link_elem.get_text(strip=True)
                url = link_elem.get("href", "")

                # 摘要
                snippet_elem = item.select_one(".b_paracte p")
                if not snippet_elem:
                    snippet_elem = item.select_one(".b_caption p")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                if url and url.startswith("http"):
                    results.append(
                        SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source=SearchSource.BING,
                        )
                    )
            except Exception:
                continue

        return results
