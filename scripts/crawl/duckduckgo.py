"""
DuckDuckGo 搜索实现

无需 API key，直接抓取搜索结果页
"""

import re
import time
from typing import List
from datetime import datetime
from dataclasses import field

import requests
from bs4 import BeautifulSoup

from crawl.base import BaseSearchEngine
from shared import SearchSource, SearchResult


class DuckDuckGoSearch(BaseSearchEngine):
    """
    DuckDuckGo 搜索

    优点：无需 API key，直接搜索
    缺点：反爬较严，需要控制频率
    """

    BASE_URL = "https://duckduckgo.com/html/"
    TIMEOUT = 10

    def __init__(self, delay: float = 2.0, user_agent: str = None):
        """
        Args:
            delay: 请求间隔（秒），建议 2 秒以上
            user_agent: 自定义 User-Agent
        """
        super().__init__(delay)
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        执行 DuckDuckGo 搜索

        Args:
            query: 搜索查询
            num_results: 结果数量

        Returns:
            搜索结果列表
        """
        query = self._validate_query(query)
        num_results = self._validate_num_results(num_results)

        self._wait_before_request()

        try:
            # 搜索
            params = {"q": query, "kl": "wt-wt"}
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()

            # 解析结果
            results = self._parse_results(response.text, num_results)

            # 如果结果不够，尝试翻页
            if len(results) < num_results:
                more_results = self._fetch_more_pages(query, num_results - len(results))
                results.extend(more_results)

            return results[:num_results]

        except requests.RequestException as e:
            raise RuntimeError(f"DuckDuckGo 搜索失败: {e}")

    def _parse_results(self, html: str, limit: int) -> List[SearchResult]:
        """解析搜索结果页面"""
        soup = BeautifulSoup(html, "lxml")
        results = []

        # DuckDuckGo HTML 结果结构
        for result in soup.select(".result")[:limit]:
            try:
                # 标题和链接
                link_elem = result.select_one(".result__a")
                if not link_elem:
                    continue

                title = link_elem.get_text(strip=True)
                url = link_elem.get("href", "")

                # 摘要
                snippet_elem = result.select_one(".result__snippet")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                # 清理 URL
                url = self._clean_url(url)

                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        source=SearchSource.DUCKDUCKGO,
                    )
                )
            except Exception:
                continue

        return results

    def _fetch_more_pages(self, query: str, needed: int) -> List[SearchResult]:
        """翻页获取更多结果"""
        all_results = []
        offset = 10  # DuckDuckGo 每页约10个结果

        while needed > 0 and offset < 50:  # 最多获取50个
            self._wait_before_request()

            try:
                params = {"q": query, "kl": "wt-wt", "s": offset}
                response = self.session.get(
                    self.BASE_URL,
                    params=params,
                    timeout=self.TIMEOUT,
                )
                response.raise_for_status()

                page_results = self._parse_results(response.text, needed)
                all_results.extend(page_results)

                needed -= len(page_results)
                offset += 10

            except requests.RequestException:
                break

        return all_results

    def _clean_url(self, url: str) -> str:
        """清理 DuckDuckGo 的重定向 URL"""
        # DuckDuckGo 使用uddg=参数做重定向
        if "uddg=" in url:
            match = re.search(r"uddg=([^&]+)", url)
            if match:
                import urllib.parse
                url = urllib.parse.unquote(match.group(1))
        return url


class DuckDuckGoLiteSearch(DuckDuckGoSearch):
    """
    DuckDuckGo Lite 版本

    更轻量，但结果可能更少
    """

    BASE_URL = "https://lite.duckduckgo.com/lite/"
    TIMEOUT = 10

    def _parse_results(self, html: str, limit: int) -> List[SearchResult]:
        """解析 Lite 版结果"""
        soup = BeautifulSoup(html, "lxml")
        results = []

        for result in soup.select(".result")[:limit]:
            try:
                link_elem = result.select_one("a")
                if not link_elem:
                    continue

                title = link_elem.get_text(strip=True)
                url = link_elem.get("href", "")

                # 摘要在下一个兄弟元素
                snippet_elem = result.find_next_sibling("a", class_="result-snippet")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                if url and url.startswith("http"):
                    results.append(
                        SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source=SearchSource.DUCKDUCKGO,
                        )
                    )
            except Exception:
                continue

        return results
