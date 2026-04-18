"""
搜索流水线

整合搜索、抓取、存储流程
"""

import json
from typing import List, Dict, Optional, Callable
from dataclasses import asdict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from .agent_tools import AgentSearchTool
from .fallback import FallbackTrigger
from .models import (
    SearchResult,
    ContentResult,
    DimensionResult,
    CollectionResult,
    SearchSource,
)


class SearchPipeline:
    """
    搜索 + 抓取组合流水线

    支持：
    - 单查询搜索
    - 多查询并行搜索
    - 搜索 + 抓取组合
    - 结果保存到文件
    """

    def __init__(
        self,
        prefer_agent: bool = True,
        fallback_enabled: bool = True,
        max_workers: int = 5,
        timeout: int = 30,
    ):
        self.search_tool = AgentSearchTool(
            prefer_agent=prefer_agent,
            fallback_enabled=fallback_enabled,
        )
        self.max_workers = max_workers
        self.timeout = timeout

    def search(
        self,
        queries: List[str],
        num_results: int = 10,
    ) -> List[List[SearchResult]]:
        """
        并行搜索多个查询

        Args:
            queries: 查询列表
            num_results: 每个查询的结果数

        Returns:
            每个查询的搜索结果列表
        """
        all_results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.search_tool.search, q, num_results): q
                for q in queries
            }

            for future in as_completed(futures):
                query = futures[future]
                try:
                    results = future.result()
                    all_results.append(results)
                except Exception as e:
                    print(f"搜索失败 [{query}]: {e}")
                    all_results.append([])

        return all_results

    def fetch(
        self,
        urls: List[str],
    ) -> List[ContentResult]:
        """
        批量抓取 URL 内容

        Args:
            urls: URL 列表

        Returns:
            抓取结果列表
        """
        contents = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.search_tool.fetch, url): url
                for url in urls
            }

            for future in as_completed(futures):
                url = futures[future]
                try:
                    content = future.result()
                    contents.append(content)
                except Exception as e:
                    print(f"抓取失败 [{url}]: {e}")
                    contents.append(None)

        return [c for c in contents if c is not None]

    def search_and_fetch(
        self,
        query: str,
        num_results: int = 10,
        fetch_content: bool = True,
    ) -> List[ContentResult]:
        """
        搜索 + 抓取组合

        Args:
            query: 搜索查询
            num_results: 结果数
            fetch_content: 是否抓取内容

        Returns:
            内容结果列表
        """
        # 搜索
        results = self.search_tool.search(query, num_results)

        if not fetch_content:
            return []

        # 提取 URL
        urls = [r.url for r in results if r.url]

        # 并行抓取
        return self.fetch(urls)

    def collect_dimension(
        self,
        dimension: str,
        query: str,
        num_results: int = 10,
    ) -> DimensionResult:
        """
        采集单个维度

        Args:
            dimension: 维度名称
            query: 搜索查询
            num_results: 结果数

        Returns:
            维度采集结果
        """
        result = DimensionResult(
            dimension=dimension,
            query=query,
        )

        try:
            # 搜索
            search_results = self.search_tool.search(query, num_results)
            result.results = search_results
            result.used_source = search_results[0].source if search_results else SearchSource.UNKNOWN

            # 抓取内容
            if search_results:
                urls = [r.url for r in search_results if r.url]
                contents = self.fetch(urls)
                result.contents = contents

        except Exception as e:
            result.success = False
            result.error = str(e)

        return result

    def collect(
        self,
        target: str,
        dimensions: Dict[str, str],
        output_dir: Optional[Path] = None,
    ) -> CollectionResult:
        """
        多维度并行采集

        Args:
            target: 采集对象（如"芒格"）
            dimensions: 维度配置 {维度名: 查询模板}
                示例:
                {
                    "writings": "芒格 著作 书单",
                    "conversations": "芒格 访谈 播客",
                    "expression": "芒格 Twitter 社交媒体",
                }
            output_dir: 输出目录

        Returns:
            采集结果
        """
        collection = CollectionResult(target=target)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self.collect_dimension,
                    dim_name,
                    query.format(target=target),
                    10,
                ): dim_name
                for dim_name, query in dimensions.items()
            }

            for future in as_completed(futures):
                dim_name = futures[future]
                try:
                    dim_result = future.result()
                    collection.dimensions.append(dim_result)
                    collection.total_results += len(dim_result.results)
                    collection.total_contents += len(dim_result.contents)
                except Exception as e:
                    print(f"维度采集失败 [{dim_name}]: {e}")

        # 保存到文件
        if output_dir:
            self._save_results(collection, output_dir)

        return collection

    def _save_results(
        self,
        collection: CollectionResult,
        output_dir: Path,
    ) -> None:
        """保存采集结果到文件"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for dim_result in collection.dimensions:
            filename = f"{dim_result.dimension}.json"
            filepath = output_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(dim_result.to_dict(), f, ensure_ascii=False, indent=2)


# 默认 6 维度采集配置
DEFAULT_DIMENSIONS = {
    "writings": "{target} 著作 书单 论文",
    "conversations": "{target} 访谈 播客 演讲",
    "expression": "{target} Twitter 社交媒体 观点",
    "critics": "{target} 批评 争议 负面评价",
    "decisions": "{target} 决策 投资 关键选择",
    "timeline": "{target} 生平 时间线 里程碑",
}
