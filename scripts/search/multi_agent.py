"""
多Agent搜索编排器

主从模式：
- Master Agent：负责网络搜索和素材收集
- Slave Agents：只分析已有素材，不重复搜索
- 最多3个Agent
"""

import json
import logging
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

from .models import SearchResult, ContentResult, SearchSource

# Module-level logger
logger = logging.getLogger("scripts.search.multi_agent")

def set_log_level(level: int) -> None:
    """Set the logging level for this module."""
    logger.setLevel(level)


def _setup_logging() -> None:
    """Configure module logging with default format."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

_setup_logging()


class AgentRole(Enum):
    """Agent角色"""
    MASTER = "master"      # 主Agent：负责搜索
    ANALYST = "analyst"   # 从Agent：负责分析


@dataclass
class AgentTask:
    """Agent任务"""
    role: AgentRole
    name: str                    # Agent名称，如"分析师A"
    instruction: str             # 给Agent的指令
    input_data: Any = None       # 输入数据（Master的搜索结果）
    output: Optional[str] = None  # Agent输出
    success: bool = True
    error: Optional[str] = None


@dataclass
class MultiAgentResult:
    """多Agent协作结果"""
    target: str
    master_output: str = ""                    # Master的搜索摘要
    analyst_outputs: List[str] = field(default_factory=list)  # 各分析师输出
    all_results: List[SearchResult] = field(default_factory=list)  # 所有搜索结果
    all_contents: List[ContentResult] = field(default_factory=list)  # 所有抓取内容
    total_searches: int = 0
    total_fetches: int = 0
    agent_count: int = 0
    completed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "master_output": self.master_output,
            "analyst_outputs": self.analyst_outputs,
            "result_count": len(self.all_results),
            "content_count": len(self.all_contents),
            "total_searches": self.total_searches,
            "total_fetches": self.total_fetches,
            "agent_count": self.agent_count,
            "completed_at": self.completed_at.isoformat(),
        }


class MasterSearchPipeline:
    """
    主从模式搜索流水线

    工作流程：
    1. Master Agent 执行网络搜索（只做一次）
    2. Slave Agents 分析已有的搜索结果（不重复搜索）
    3. 汇总各Agent的分析结论

    最多3个Agent：
    - 1 Master（搜索）
    - 2 Analysts（分析）
    """

    def __init__(
        self,
        max_agents: int = 3,
        search_tool = None,
    ):
        """
        Args:
            max_agents: 最大Agent数量（默认3，含Master）
            search_tool: 搜索工具实例
        """
        # 确保最多3个Agent
        self.max_agents = min(max(max_agents, 1), 3)
        self.search_tool = search_tool
        self._setup_agents()

    def _setup_agents(self):
        """初始化Agent列表"""
        self.agents: List[AgentTask] = []

        # Agent 1: Master（必须）
        self.agents.append(AgentTask(
            role=AgentRole.MASTER,
            name="素材收集师",
            instruction="你负责从网络搜索并收集与目标相关的素材。",
        ))

        # Agent 2-3: Analysts（按需添加，最多2个）
        analyst_count = self.max_agents - 1
        for i in range(analyst_count):
            self.agents.append(AgentTask(
                role=AgentRole.ANALYST,
                name=f"分析师_{chr(65+i)}",  # 分析师_A, 分析师_B
                instruction="你负责从已收集的素材中分析提炼观点。",
            ))

    def collect(
        self,
        target: str,
        dimensions: Optional[Dict[str, str]] = None,
        num_results: int = 10,
    ) -> MultiAgentResult:
        """
        执行多Agent协作采集

        Args:
            target: 采集目标
            dimensions: 维度配置（可选，默认3个核心维度）
            num_results: 每个维度的搜索结果数

        Returns:
            多Agent协作结果
        """
        result = MultiAgentResult(target=target)
        result.agent_count = len(self.agents)

        # 默认3个核心维度（不超过Agent数量）
        if dimensions is None:
            dimensions = self._get_default_dimensions()

        # 确保维度数量不超过分析师数量
        dim_list = list(dimensions.items())
        if len(dim_list) > (self.max_agents - 1):
            dim_list = dim_list[:self.max_agents - 1]

        # ========== Step 1: Master 执行搜索（只做一次）==========
        master = self.agents[0]
        logger.info(f"[{master.name}] 开始搜索 {target}...")

        try:
            # 合并所有维度的查询，统一搜索
            all_queries = [query.format(target=target) for _, query in dim_list]
            all_results: List[SearchResult] = []

            for query in all_queries:
                if self.search_tool:
                    results = self.search_tool.search(query, num_results)
                else:
                    # 使用默认搜索
                    from .agent_tools import AgentSearchTool
                    tool = AgentSearchTool()
                    results = tool.search(query, num_results)
                all_results.extend(results)

            # 去重
            seen_urls = set()
            unique_results = []
            for r in all_results:
                if r.url not in seen_urls:
                    seen_urls.add(r.url)
                    unique_results.append(r)

            result.all_results = unique_results
            result.total_searches = len(all_queries)

            # 抓取内容
            urls = [r.url for r in unique_results[:20]]  # 限制抓取数量
            contents = self._fetch_contents(urls)
            result.all_contents = contents
            result.total_fetches = len(urls)

            # Master 生成摘要
            result.master_output = self._generate_master_summary(
                target, unique_results, contents
            )

            logger.info(f"[{master.name}] 搜索完成，获取 {len(unique_results)} 条结果")

        except (RuntimeError, ConnectionError, TimeoutError) as e:
            master.success = False
            master.error = str(e)
            logger.error(f"[{master.name}] 搜索失败: {e}")
        except Exception as e:
            master.success = False
            master.error = str(e)
            logger.exception(f"[{master.name}] 搜索失败 (未知错误): {e}")

        # ========== Step 2: Analysts 并行分析（不重复搜索）==========
        analysts = [a for a in self.agents if a.role == AgentRole.ANALYST]

        for i, analyst in enumerate(analysts):
            if i < len(dim_list):
                dim_name, query_template = dim_list[i]
                logger.info(f"[{analyst.name}] 开始分析维度: {dim_name}")

                try:
                    # 筛选相关结果
                    related = self._filter_related_results(
                        result.all_contents, dim_name
                    )

                    # 分析
                    output = self._analyze_dimension(
                        target, dim_name, related, analyst.name
                    )
                    analyst.output = output
                    result.analyst_outputs.append(output)

                    logger.info(f"[{analyst.name}] 分析完成")

                except (ValueError, RuntimeError) as e:
                    analyst.success = False
                    analyst.error = str(e)
                    result.analyst_outputs.append(f"[{analyst.name}] 分析失败: {e}")
                except Exception as e:
                    analyst.success = False
                    analyst.error = str(e)
                    logger.exception(f"[{analyst.name}] 分析失败 (未知错误): {e}")
                    result.analyst_outputs.append(f"[{analyst.name}] 分析失败: {e}")

        return result

    def _get_default_dimensions(self) -> Dict[str, str]:
        """获取默认维度（核心3维度）"""
        return {
            "核心观点": "{target} 核心思想 观点 理念",
            "代表作品": "{target} 作品 成果 产品",
            "他人评价": "{target} 评价 评论 反馈",
        }

    def _fetch_contents(self, urls: List[str]) -> List[ContentResult]:
        """抓取URL内容"""
        if not urls:
            return []

        contents: List[ContentResult] = []

        # 优先用 search_tool.fetch
        if self.search_tool:
            for url in urls:
                try:
                    content = self.search_tool.fetch(url)
                    contents.append(content)
                except (ConnectionError, TimeoutError, RuntimeError) as e:
                    logger.warning(f"Failed to fetch {url}: {e}")
                except Exception as e:
                    logger.exception(f"Unexpected error fetching {url}: {e}")

        # 如果没有内容，尝试直接用爬虫
        if not contents:
            try:
                from crawl.fetcher import ContentFetcher
                fetcher = ContentFetcher()
                for url in urls:
                    try:
                        content = fetcher.fetch(url)
                        contents.append(content)
                    except (ConnectionError, TimeoutError, RuntimeError) as e:
                        logger.warning(f"Failed to fetch {url}: {e}")
                    except Exception as e:
                        logger.exception(f"Unexpected error fetching {url}: {e}")
            except ImportError as e:
                logger.warning(f"Failed to import ContentFetcher: {e}")
            except Exception as e:
                logger.exception(f"Unexpected error in ContentFetcher: {e}")

        return contents

    def _filter_related_results(
        self,
        contents: List[ContentResult],
        dimension: str,
    ) -> List[ContentResult]:
        """根据维度筛选相关内容"""
        # 简单关键词匹配
        keywords = dimension.split()
        related = []

        for content in contents:
            # 检查标题或内容是否包含关键词
            text = (content.title + content.content).lower()
            if any(kw.lower() in text for kw in keywords):
                related.append(content)

        # 如果过滤后太少，返回全部
        return related if related else contents[:5]

    def _generate_master_summary(
        self,
        target: str,
        results: List[SearchResult],
        contents: List[ContentResult],
    ) -> str:
        """Master生成搜索摘要"""
        lines = [
            f"# {target} 网络素材收集报告",
            "",
            f"共收集 {len(results)} 条搜索结果，{len(contents)} 条内容",
            "",
            "## 搜索结果概览",
        ]

        for i, r in enumerate(results[:5], 1):
            lines.append(f"{i}. [{r.title}]({r.url})")
            lines.append(f"   {r.snippet[:100]}...")

        lines.append("")
        lines.append("## 内容摘要")

        for c in contents[:3]:
            lines.append(f"### {c.title}")
            lines.append(c.content[:300] + "..." if len(c.content) > 300 else c.content)
            lines.append("")

        return "\n".join(lines)

    def _analyze_dimension(
        self,
        target: str,
        dimension: str,
        contents: List[ContentResult],
        analyst_name: str,
    ) -> str:
        """分析师分析指定维度"""
        lines = [
            f"# {analyst_name} - {dimension} 分析",
            "",
            f"目标: {target}",
            f"维度: {dimension}",
            f"依据: {len(contents)} 条相关素材",
            "",
            "## 分析结论",
        ]

        # 简单分析：按内容提取关键词和观点
        all_text = "\n".join([c.content for c in contents])
        sentences = all_text.split("。")[:10]  # 取前10句

        for i, sentence in enumerate(sentences, 1):
            if len(sentence) > 20:  # 过滤短句
                lines.append(f"{i}. {sentence}。")

        lines.append("")
        lines.append("## 关键发现")

        # 简单提取：标题+首句作为关键发现
        for c in contents[:3]:
            if c.title:
                lines.append(f"- **{c.title}**: {c.content[:100]}...")

        return "\n".join(lines)

    def save_results(
        self,
        result: MultiAgentResult,
        output_dir: Path,
    ) -> None:
        """保存结果到文件"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存完整结果
        with open(output_dir / "multi_agent_result.json", "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)

        # 保存 Master 报告
        if result.master_output:
            with open(output_dir / "00_master_report.md", "w", encoding="utf-8") as f:
                f.write(result.master_output)

        # 保存各 Analyst 报告
        for i, output in enumerate(result.analyst_outputs, 1):
            with open(output_dir / f"0{i}_analyst_report.md", "w", encoding="utf-8") as f:
                f.write(output)
