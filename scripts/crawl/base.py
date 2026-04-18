"""
爬虫基类
"""

from abc import ABC, abstractmethod
from typing import List
import time

from shared import SearchSource, SearchResult


class BaseSearchEngine(ABC):
    """搜索引擎抽象基类"""

    def __init__(self, delay: float = 1.0):
        """
        Args:
            delay: 请求间隔（秒），避免被限流
        """
        self.delay = delay
        self._last_request_time = 0.0

    def _wait_before_request(self):
        """请求前等待"""
        if self.delay > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
        self._last_request_time = time.time()

    @abstractmethod
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        执行搜索

        Args:
            query: 搜索查询
            num_results: 结果数量

        Returns:
            搜索结果列表
        """
        raise NotImplementedError

    def _validate_query(self, query: str) -> str:
        """验证和清理查询"""
        query = query.strip()
        if not query:
            raise ValueError("查询不能为空")
        return query

    def _validate_num_results(self, num_results: int) -> int:
        """验证结果数量"""
        if num_results < 1:
            return 10
        if num_results > 100:
            return 100
        return num_results
