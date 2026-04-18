"""
盘古造物配置

集中管理配置项
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class SearchConfig:
    """搜索配置"""
    # 并发数
    max_workers: int = 5

    # 超时（秒）
    timeout: int = 30

    # 请求延迟（秒）
    delay: float = 2.0

    # 结果数
    default_num_results: int = 10

    # 优先使用 Agent 工具
    prefer_agent: bool = True

    # 启用降级
    fallback_enabled: bool = True


@dataclass
class CrawlConfig:
    """爬虫配置"""
    # User-Agent
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # 超时
    timeout: int = 30

    # 最大内容长度
    max_content_length: int = 500_000

    # 请求延迟
    delay: float = 2.0


@dataclass
class TranscribeConfig:
    """转录配置"""
    # Whisper 模型
    model: str = "base"

    # 语言（None = 自动检测）
    language: Optional[str] = None

    # 输出目录
    output_dir: str = "./transcripts"


@dataclass
class StorageConfig:
    """存储配置"""
    # 采集结果目录
    collection_dir: Path = PROJECT_ROOT / "collections"

    # 字幕目录
    subtitle_dir: Path = PROJECT_ROOT / "subtitles"

    # 转录目录
    transcript_dir: Path = PROJECT_ROOT / "transcripts"


# 全局配置实例
search_config = SearchConfig()
crawl_config = CrawlConfig()
transcribe_config = TranscribeConfig()
storage_config = StorageConfig()


def get_default_dimensions() -> dict:
    """获取默认采集维度"""
    return {
        "writings": "{target} 著作 书单 论文",
        "conversations": "{target} 访谈 播客 演讲",
        "expression": "{target} Twitter 社交媒体 观点",
        "critics": "{target} 批评 争议 负面评价",
        "decisions": "{target} 决策 投资 关键选择",
        "timeline": "{target} 生平 时间线 里程碑",
    }


def get_chinese_dimensions() -> dict:
    """获取中文优先的采集维度"""
    return {
        "writings": "{target} 著作 书籍 论文",
        "conversations": "{target} 访谈 演讲 B站 播客",
        "expression": "{target} 微博 微信 社交媒体",
        "critics": "{target} 批评 争议 负面评价",
        "decisions": "{target} 决策 投资 选择",
        "timeline": "{target} 生平 经历 时间线",
    }
