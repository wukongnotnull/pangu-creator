"""
文本清洗工具
"""

import re
from typing import List, Tuple


class TextCleaner:
    """
    文本清洗工具

    功能：
    - HTML 标签移除
    - 噪声移除
    - 格式规范化
    """

    # 常见的广告和噪声选择器
    NOISE_SELECTORS = [
        ".ad",
        ".ads",
        ".advertisement",
        ".social-share",
        ".comments",
        ".related-posts",
        ".sidebar",
        ".newsletter",
        ".popup",
        "[class*='ad-']",
        "[id*='ad-']",
    ]

    @classmethod
    def clean_html(cls, html: str) -> str:
        """清理 HTML 文本，保留段落结构"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # 移除噪声
        for selector in cls.NOISE_SELECTORS:
            for elem in soup.select(selector):
                elem.decompose()

        # 保留换行
        text = soup.get_text(separator="\n")

        # 清理
        text = cls.clean_text(text)

        return text

    @classmethod
    def clean_text(cls, text: str) -> str:
        """清理纯文本"""
        # 移除多余空白
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 移除首尾空白
        text = text.strip()

        return text

    @classmethod
    def remove_html_tags(cls, html: str) -> str:
        """移除所有 HTML 标签"""
        text = re.sub(r"<[^>]+>", "", html)
        text = cls.clean_text(text)
        return text

    @classmethod
    def extract_paragraphs(cls, text: str) -> List[str]:
        """提取段落"""
        paragraphs = text.split("\n")
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs

    @classmethod
    def clean_urls(cls, text: str) -> str:
        """清理 URL"""
        # 移除 URL 中的跟踪参数
        patterns = [
            (r"\?utm_[^ ]+", ""),      # UTM 参数
            (r"&ref=[^ ]+", ""),        # ref 参数
            (r"#.[^ ]+$", ""),          # 片段标识
        ]

        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)

        # 清理空查询
        text = re.sub(r"\?&", "?", text)
        text = re.sub(r"\?$", "", text)

        return text

    @classmethod
    def normalize_chinese_spacing(cls, text: str) -> str:
        """
        规范化中文间距

        在中文和英文/数字之间添加空格
        """
        # 中英文之间
        text = re.sub(r"([\u4e00-\u9fff])([a-zA-Z0-9])", r"\1 \2", text)
        text = re.sub(r"([a-zA-Z0-9])([\u4e00-\u9fff])", r"\1 \2", text)

        return text

    @classmethod
    def split_sentences(cls, text: str) -> List[str]:
        """
        智能分句

        按照中文句号、英文句号、感叹号等分割
        """
        # 按句子分割
        sentences = re.split(r"[。.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    @classmethod
    def extract_key_sentences(
        cls,
        text: str,
        max_sentences: int = 5,
    ) -> List[Tuple[str, int]]:
        """
        提取关键句子

        基于位置和长度打分

        Returns:
            List of (sentence, score) tuples
        """
        sentences = cls.split_sentences(text)

        scored = []
        for i, sentence in enumerate(sentences):
            # 长度分数（太短太长都扣分）
            length = len(sentence)
            length_score = 1.0 if 10 < length < 100 else 0.5

            # 位置分数（开头和结尾更重要）
            position_score = 1.0
            if i == 0:
                position_score = 1.2
            elif i == len(sentences) - 1:
                position_score = 0.9

            # 综合分数
            score = length_score * position_score

            scored.append((sentence, score))

        # 按分数排序
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored[:max_sentences]


class MarkdownCleaner(TextCleaner):
    """
    Markdown 专用清洗器
    """

    @classmethod
    def clean_markdown(cls, md: str) -> str:
        """清理 Markdown"""
        # 移除图片
        md = re.sub(r"!\[.*?\]\(.*?\)", "", md)

        # 移除链接但保留文本
        md = re.sub(r"\[([^\]]+)\]\(.*?\)", r"\1", md)

        # 移除标题标记但保留文字
        md = re.sub(r"^#{1,6}\s+", "", md, flags=re.MULTILINE)

        # 移除引用标记
        md = re.sub(r"^>\s+", "", md, flags=re.MULTILINE)

        # 移除代码块标记
        md = re.sub(r"```.*?```", "", md, flags=re.DOTALL)

        # 移除行内代码标记
        md = re.sub(r"`([^`]+)`", r"\1", md)

        # 移除加粗/斜体标记
        md = re.sub(r"\*+([^\*]+)\*+", r"\1", md)
        md = re.sub(r"_+([^_]+)_+", r"\1", md)

        # 清理
        md = cls.clean_text(md)

        return md
