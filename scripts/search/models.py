"""
search 模块 - 数据模型定义

从 types 导入共享类型，保持向后兼容
"""

from shared import SearchSource, ContentLanguage, SearchResult, ContentResult

# 向后兼容：重新导出
__all__ = [
    "SearchSource",
    "ContentLanguage",
    "SearchResult",
    "ContentResult",
    "DimensionResult",
    "CollectionResult",
]

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class DimensionResult:
    """单个维度的采集结果"""
    dimension: str                # 维度名称
    query: str                    # 搜索查询
    results: List[SearchResult] = field(default_factory=list)
    contents: List[ContentResult] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None
    used_source: SearchSource = SearchSource.UNKNOWN
    retrieved_at: datetime = field(default_factory=datetime.now)

    @property
    def has_content(self) -> bool:
        return len(self.contents) > 0

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "query": self.query,
            "result_count": len(self.results),
            "content_count": len(self.contents),
            "success": self.success,
            "error": self.error,
            "used_source": self.used_source.value,
            "retrieved_at": self.retrieved_at.isoformat(),
        }


@dataclass
class CollectionResult:
    """多维度采集结果"""
    target: str                   # 采集对象
    dimensions: List[DimensionResult] = field(default_factory=list)
    total_results: int = 0
    total_contents: int = 0
    completed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "dimension_count": len(self.dimensions),
            "total_results": self.total_results,
            "total_contents": self.total_contents,
            "completed_at": self.completed_at.isoformat(),
            "dimensions": [d.to_dict() for d in self.dimensions],
        }
