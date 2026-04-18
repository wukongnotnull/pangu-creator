"""
网页内容抓取器
"""

import re
from typing import Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from dataclasses import dataclass, field

from shared import ContentLanguage, ContentResult


class ContentFetcher:
    """
    网页内容抓取器

    功能：
    - 抓取网页正文
    - 自动语言检测
    - 字数统计
    """

    TIMEOUT = 30
    MAX_CONTENT_LENGTH = 500_000  # 最大内容长度

    def __init__(self, user_agent: str = None):
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def fetch(self, url: str) -> ContentResult:
        """
        抓取 URL 内容

        Args:
            url: 目标 URL

        Returns:
            ContentResult: 抓取结果
        """
        try:
            response = self.session.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()

            # 检测编码
            encoding = self._detect_encoding(response)
            html = response.content.decode(encoding, errors="replace")

            # 解析内容
            soup = BeautifulSoup(html, "lxml")

            # 移除脚本和样式
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            # 提取标题
            title = self._extract_title(soup)

            # 提取正文
            content = self._extract_content(soup)

            # 清理内容
            content = self._clean_content(content)

            # 检测语言
            language = self._detect_language(content)

            # 统计字数
            word_count = len(content)

            return ContentResult(
                url=url,
                title=title,
                content=content[:self.MAX_CONTENT_LENGTH],
                word_count=word_count,
                language=language,
            )

        except requests.RequestException as e:
            raise RuntimeError(f"抓取失败 [{url}]: {e}")
        except Exception as e:
            raise RuntimeError(f"解析失败 [{url}]: {e}")

    def _detect_encoding(self, response: requests.Response) -> str:
        """检测响应编码"""
        # 优先使用响应头中的编码
        if response.encoding and response.encoding != "ISO-8859-1":
            return response.encoding

        # 尝试从 HTML 中检测
        html = response.text
        match = re.search(r'charset=["\']?([^"\'\s]+)', html, re.I)
        if match:
            return match.group(1)

        # 默认
        return "utf-8"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取标题"""
        # 优先 og:title
        og_title = soup.select_one('meta[property="og:title"]')
        if og_title:
            return og_title.get("content", "")

        # 标准 title
        title_elem = soup.find("title")
        if title_elem:
            return title_elem.get_text(strip=True)

        # h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return ""

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取正文内容"""
        # 尝试常见的内容容器
        selectors = [
            "article",
            "[role='main']",
            ".post-content",
            ".article-content",
            ".entry-content",
            ".content",
            "main",
            "#content",
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and len(elem.get_text(strip=True)) > 100:
                return elem.get_text(separator="\n", strip=True)

        # 如果没找到容器，尝试 body
        body = soup.find("body")
        if body:
            return body.get_text(separator="\n", strip=True)

        # 降级到整个 soup
        return soup.get_text(separator="\n", strip=True)

    def _clean_content(self, content: str) -> str:
        """清理内容"""
        # 移除多余空行
        content = re.sub(r"\n{3,}", "\n\n", content)

        # 移除首尾空白
        content = content.strip()

        return content

    def _detect_language(self, content: str) -> ContentLanguage:
        """简单语言检测"""
        if not content:
            return ContentLanguage.UNKNOWN

        # 简单检测：计算中文字符比例
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", content))
        total_chars = len(re.sub(r"\s", "", content))

        if total_chars == 0:
            return ContentLanguage.UNKNOWN

        chinese_ratio = chinese_chars / total_chars

        if chinese_ratio > 0.3:
            return ContentLanguage.ZH
        elif chinese_ratio > 0.1:
            return ContentLanguage.MIXED
        else:
            return ContentLanguage.EN


class SmartFetcher(ContentFetcher):
    """
    智能抓取器

    增强版：
    - 支持登录后的内容
    - 支持 JavaScript 渲染页面（需要额外处理）
    """

    def __init__(self, cookies: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.cookies = cookies or {}

    def fetch(self, url: str) -> ContentResult:
        """重写 fetch 支持 cookies"""
        try:
            response = self.session.get(
                url,
                timeout=self.TIMEOUT,
                cookies=self.cookies,
            )
            response.raise_for_status()

            encoding = self._detect_encoding(response)
            html = response.content.decode(encoding, errors="replace")

            soup = BeautifulSoup(html, "lxml")

            # 移除不需要的标签
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            # 如果有反爬检测，尝试绕过
            if self._is_blocked(soup):
                raise RuntimeError("可能被反爬检测拦截")

            title = self._extract_title(soup)
            content = self._extract_content(soup)
            content = self._clean_content(content)
            language = self._detect_language(content)

            return ContentResult(
                url=url,
                title=title,
                content=content[:self.MAX_CONTENT_LENGTH],
                word_count=len(content),
                language=language,
            )

        except Exception as e:
            raise RuntimeError(f"SmartFetch 失败 [{url}]: {e}")

    def _is_blocked(self, soup: BeautifulSoup) -> bool:
        """检测是否被反爬"""
        # 检测常见的反爬提示
        blocked_texts = [
            "访问频率过高",
            "请输入验证码",
            "Access denied",
            "blocked",
        ]

        page_text = soup.get_text()

        for text in blocked_texts:
            if text in page_text:
                return True

        return False
