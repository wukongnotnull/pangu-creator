#!/usr/bin/env python3
"""
盘古造物 CLI

命令行工具，用于信息采集
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from search.pipeline import SearchPipeline, DEFAULT_DIMENSIONS
from search.agent_tools import AgentSearchTool
from search.multi_agent import MasterSearchPipeline
from search.collector import MaterialCollector
from crawl import DuckDuckGoSearch, ContentFetcher
from transcribe import YouTubeTranscriber, AudioTranscriber, is_youtube_url


def cmd_search(args):
    """搜索命令"""
    pipeline = SearchPipeline(
        prefer_agent=not args.no_agent,
        fallback_enabled=True,
        max_workers=args.workers,
    )

    queries = args.query if isinstance(args.query, list) else [args.query]

    print(f"🔍 搜索 {len(queries)} 个查询...")

    results = pipeline.search(queries, num_results=args.num)

    for i, (query, result_list) in enumerate(zip(queries, results)):
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print(f"结果: {len(result_list)} 条")
        print("=" * 60)

        for j, r in enumerate(result_list[:args.num]):
            print(f"\n[{j+1}] {r.title}")
            print(f"    URL: {r.url}")
            print(f"    摘要: {r.snippet[:100]}...")
            print(f"    来源: {r.source.value}")

    return 0


def cmd_fetch(args):
    """抓取命令"""
    pipeline = SearchPipeline(prefer_agent=not args.no_agent)

    urls = args.url if isinstance(args.url, list) else [args.url]

    print(f"📥 抓取 {len(urls)} 个 URL...")

    contents = pipeline.fetch(urls)

    for c in contents:
        print(f"\n{'='*60}")
        print(f"标题: {c.title}")
        print(f"URL: {c.url}")
        print(f"字数: {c.word_count}")
        print(f"语言: {c.language.value}")
        print("-" * 60)
        print(c.content[:500] + "..." if len(c.content) > 500 else c.content)

    return 0


def cmd_collect(args):
    """多维度采集命令"""
    pipeline = SearchPipeline(
        prefer_agent=not args.no_agent,
        max_workers=args.workers,
    )

    target = args.target

    # 构建维度查询
    dimensions = {}
    if args.dimensions:
        for dim in args.dimensions:
            if ":" in dim:
                name, query = dim.split(":", 1)
                dimensions[name] = query
            else:
                dimensions[dim] = f"{target} {dim}"
    else:
        # 使用默认维度
        for name, query_template in DEFAULT_DIMENSIONS.items():
            dimensions[name] = query_template.format(target=target)

    print(f"🎯 开始采集: {target}")
    print(f"📊 维度数: {len(dimensions)}")
    print(f"   维度: {', '.join(dimensions.keys())}")

    # 执行采集
    output_dir = Path(args.output) if args.output else None
    result = pipeline.collect(target, dimensions, output_dir)

    # 输出结果
    print(f"\n✅ 采集完成")
    print(f"   总搜索结果: {result.total_results}")
    print(f"   总内容数: {result.total_contents}")

    if output_dir:
        print(f"   结果目录: {output_dir}")

    # 保存汇总
    if output_dir:
        summary_file = output_dir / "collection_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"   汇总文件: {summary_file}")

    return 0


def cmd_transcribe(args):
    """转录命令"""
    url = args.url
    output_dir = args.output or "./transcripts"

    print(f"🎬 开始转录: {url}")

    if is_youtube_url(url):
        print("📺 检测到 YouTube 视频")

        # 字幕优先
        yt = YouTubeTranscriber(output_dir=output_dir)
        result = yt.get_subtitle(url)

        if result.subtitles:
            print(f"✅ 获取到 {len(result.subtitles)} 个字幕")
            for sub in result.subtitles:
                print(f"   语言: {sub['lang']}, 类型: {sub['type']}")
                print(f"   内容预览: {sub['content'][:100]}...")

            if result.file_path:
                print(f"\n📁 字幕文件: {result.file_path}")

            return 0

        print("⚠️ 无字幕可用，尝试音频转录...")

    # Whisper 转录
    transcriber = AudioTranscriber(
        model=args.model or "base",
        output_dir=output_dir,
    )

    if is_youtube_url(url):
        text = transcriber.transcribe_youtube(url)
    else:
        text = transcriber.transcribe(url)

    print(f"\n✅ 转录完成")
    print(f"   字数: {len(text)}")
    print(f"\n内容预览:")
    print("-" * 60)
    print(text[:500] + "..." if len(text) > 500 else text)

    return 0


def cmd_info(args):
    """信息命令 - 显示 Agent 工具状态"""
    tool = AgentSearchTool(prefer_agent=True, fallback_enabled=True)

    print("🔧 Agent 工具状态:")
    print(f"   Agent 工具可用: {tool.is_agent_available()}")

    if tool.is_agent_available():
        print(f"   主搜索源: Agent WebSearch")
    else:
        print(f"   主搜索源: 降级到爬虫")

    # 测试爬虫
    print("\n🧪 测试爬虫...")
    try:
        crawler = DuckDuckGoSearch()
        results = crawler.search("测试", 3)
        print(f"   爬虫状态: 正常 ({len(results)} 条结果)")
    except Exception as e:
        print(f"   爬虫状态: 异常 ({e})")

    return 0


def cmd_team(args):
    """多Agent协作命令（主从模式）"""
    max_agents = args.agents or 3

    print(f"🤖 启动多Agent协作（最多 {max_agents} 个Agent）")
    print("   模式: 主从模式")
    print("   - Master: 负责网络搜索")
    print("   - Analysts: 负责分析已有素材")
    print("")

    # 创建搜索工具
    search_tool = None
    if not args.no_agent:
        search_tool = AgentSearchTool(prefer_agent=True, fallback_enabled=True)

    # 创建多Agent流水线
    pipeline = MasterSearchPipeline(
        max_agents=max_agents,
        search_tool=search_tool,
    )

    target = args.target

    # 构建维度（默认3个，与Agent数量匹配）
    dimensions = {}
    if args.dimensions:
        for dim in args.dimensions:
            if ":" in dim:
                name, query = dim.split(":", 1)
                dimensions[name] = query
            else:
                dimensions[name] = f"{target} {dim}"
    else:
        # 默认核心3维度
        dimensions = {
            "核心观点": f"{target} 核心思想 观点 理念",
            "代表作品": f"{target} 作品 成果 产品",
            "他人评价": f"{target} 评价 评论 反馈",
        }

    print(f"🎯 采集目标: {target}")
    print(f"📊 分析维度: {len(dimensions)} 个")
    for name in dimensions:
        print(f"   - {name}")

    # 执行协作采集
    result = pipeline.collect(
        target=target,
        dimensions=dimensions,
        num_results=args.num,
    )

    # 输出结果
    print(f"\n{'='*60}")
    print(f"✅ 多Agent协作完成")
    print(f"{'='*60}")
    print(f"   Agent数量: {result.agent_count} (1 Master + {result.agent_count - 1} Analysts)")
    print(f"   搜索次数: {result.total_searches}")
    print(f"   抓取页面: {result.total_fetches}")
    print(f"   收集结果: {len(result.all_results)} 条")
    print(f"   获取内容: {len(result.all_contents)} 条")

    # 显示 Master 报告
    if result.master_output:
        print(f"\n{'='*60}")
        print("📋 Master 素材收集报告 (预览)")
        print("=" * 60)
        lines = result.master_output.split("\n")
        for line in lines[:30]:
            print(line)
        if len(lines) > 30:
            print(f"... (共 {len(lines)} 行)")

    # 显示 Analyst 报告摘要
    if result.analyst_outputs:
        print(f"\n{'='*60}")
        print("📊 Analyst 分析结论")
        print("=" * 60)
        for i, output in enumerate(result.analyst_outputs, 1):
            lines = output.split("\n")
            print(f"\n### Analyst {i}")
            for line in lines[:15]:
                print(line)
            if len(lines) > 15:
                print(f"... (共 {len(lines)} 行)")

    # 保存结果
    output_dir = Path(args.output) if args.output else None
    if output_dir:
        pipeline.save_results(result, output_dir)
        print(f"\n💾 结果已保存到: {output_dir}")

    return 0


def cmd_collect_local(args):
    """本地素材采集命令"""
    collector = MaterialCollector(transcript_enabled=not args.no_transcribe)

    paths = args.paths if isinstance(args.paths, list) else [args.paths]

    print(f"📂 开始采集 {len(paths)} 个素材...")
    print("")

    result = collector.collect(paths)

    # 输出结果
    print(f"{'='*60}")
    print(f"✅ 采集完成")
    print(f"{'='*60}")
    print(f"   总文件数: {result.total_files}")
    print(f"   成功: {result.successful}")
    print(f"   失败: {result.failed}")
    print(f"   总字数: {result.total_words:,}")
    print("")

    # 显示每个素材的详情
    for i, mat in enumerate(result.materials, 1):
        status = "✅" if mat.success else "❌"
        print(f"{status} [{mat.material_type.value}] {Path(mat.path).name}")
        if mat.success:
            print(f"   标题: {mat.title or 'N/A'}")
            print(f"   字数: {mat.word_count:,}")
            print(f"   语言: {mat.language.value}")
            if args.verbose and mat.content:
                preview = mat.content[:200].replace("\n", " ")
                print(f"   预览: {preview}...")
        else:
            print(f"   错误: {mat.error}")
        print("")

    # 保存结果
    output_dir = Path(args.output) if args.output else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存汇总
        with open(output_dir / "collection_result.json", "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)

        # 保存每个素材的文本内容
        for i, mat in enumerate(result.materials):
            if mat.success and mat.content:
                ext = Path(mat.path).suffix
                output_path = output_dir / f"content_{i+1}{ext}"
                if ext in [".txt", ".md"]:
                    output_path.write_text(mat.content, encoding="utf-8")
                else:
                    # 统一保存为 txt
                    txt_path = output_dir / f"content_{i+1}.txt"
                    txt_path.write_text(mat.content, encoding="utf-8")

        print(f"💾 结果已保存到: {output_dir}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="盘古造物信息采集工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # search 命令
    search_parser = subparsers.add_parser(
        "search",
        help="搜索查询",
    )
    search_parser.add_argument("query", nargs="+", help="搜索查询")
    search_parser.add_argument(
        "-n", "--num",
        type=int,
        default=10,
        help="每查询结果数 (默认: 10)"
    )
    search_parser.add_argument(
        "--no-agent",
        action="store_true",
        help="跳过 Agent 工具，直接使用爬虫"
    )
    search_parser.add_argument(
        "-w", "--workers",
        type=int,
        default=5,
        help="并发数 (默认: 5)"
    )
    search_parser.set_defaults(func=cmd_search)

    # fetch 命令
    fetch_parser = subparsers.add_parser(
        "fetch",
        help="抓取 URL 内容",
    )
    fetch_parser.add_argument("url", nargs="+", help="URL 列表")
    fetch_parser.add_argument(
        "--no-agent",
        action="store_true",
        help="跳过 Agent 工具"
    )
    fetch_parser.set_defaults(func=cmd_fetch)

    # collect 命令
    collect_parser = subparsers.add_parser(
        "collect",
        help="多维度采集",
    )
    collect_parser.add_argument("target", help="采集对象 (如: 芒格)")
    collect_parser.add_argument(
        "-d", "--dimensions",
        nargs="+",
        help="指定维度，格式: dimension_name:query_template"
    )
    collect_parser.add_argument(
        "-o", "--output",
        help="输出目录"
    )
    collect_parser.add_argument(
        "--no-agent",
        action="store_true",
        help="跳过 Agent 工具"
    )
    collect_parser.add_argument(
        "-w", "--workers",
        type=int,
        default=5,
        help="并发数 (默认: 5)"
    )
    collect_parser.set_defaults(func=cmd_collect)

    # transcribe 命令
    transcribe_parser = subparsers.add_parser(
        "transcribe",
        help="音视频转录",
    )
    transcribe_parser.add_argument("url", help="YouTube URL 或本地音频路径")
    transcribe_parser.add_argument(
        "-o", "--output",
        help="输出目录"
    )
    transcribe_parser.add_argument(
        "-m", "--model",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper 模型"
    )
    transcribe_parser.set_defaults(func=cmd_transcribe)

    # info 命令
    info_parser = subparsers.add_parser(
        "info",
        help="显示状态信息"
    )
    info_parser.set_defaults(func=cmd_info)

    # team 命令（多Agent协作）
    team_parser = subparsers.add_parser(
        "team",
        help="多Agent协作采集（主从模式）"
    )
    team_parser.add_argument("target", help="采集目标 (如: 埃隆·马斯克)")
    team_parser.add_argument(
        "-d", "--dimensions",
        nargs="+",
        help="分析维度，格式: dimension_name:query_template"
    )
    team_parser.add_argument(
        "-o", "--output",
        help="输出目录"
    )
    team_parser.add_argument(
        "-n", "--num",
        type=int,
        default=10,
        help="每个维度搜索结果数 (默认: 10)"
    )
    team_parser.add_argument(
        "-a", "--agents",
        type=int,
        default=3,
        help="最大Agent数量 (默认: 3，最多3个)"
    )
    team_parser.add_argument(
        "--no-agent",
        action="store_true",
        help="跳过 Agent 工具，直接使用爬虫"
    )
    team_parser.set_defaults(func=cmd_team)

    # collect-local 命令（本地素材采集）
    local_parser = subparsers.add_parser(
        "collect-local",
        help="采集本地素材（PDF/Word/TXT/MD/Excel/字幕/音视频）"
    )
    local_parser.add_argument(
        "paths",
        nargs="+",
        help="文件路径或URL列表"
    )
    local_parser.add_argument(
        "-o", "--output",
        help="输出目录"
    )
    local_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细内容"
    )
    local_parser.add_argument(
        "--no-transcribe",
        action="store_true",
        help="跳过音视频转录"
    )
    local_parser.set_defaults(func=cmd_collect_local)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
