"""
YouTube 字幕获取

支持：
- 人工字幕
- 自动字幕
- 字幕下载
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum


class SubtitleType(Enum):
    """字幕类型"""
    MANUAL = "manual"
    AUTO = "auto"
    UNKNOWN = "unknown"


@dataclass
class SubtitleResult:
    """字幕结果"""
    video_id: str
    title: str
    subtitles: List[dict]  # [{lang, type, content}]
    downloaded_at: str
    file_path: Optional[str] = None


class YouTubeTranscriber:
    """
    YouTube 字幕获取

    使用 yt-dlp 获取字幕
    """

    def __init__(self, output_dir: str = "./subtitles"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_subtitle(
        self,
        youtube_url: str,
        languages: List[str] = None,
    ) -> SubtitleResult:
        """
        获取 YouTube 字幕

        Args:
            youtube_url: YouTube URL
            languages: 语言优先级，默认 ["zh-CN", "zh", "en"]

        Returns:
            SubtitleResult: 字幕结果
        """
        languages = languages or ["zh-CN", "zh", "en"]

        # 提取视频信息
        info = self._get_video_info(youtube_url)

        video_id = info.get("id", "")
        title = info.get("title", "")

        # 获取字幕
        subtitles = self._get_subtitles(youtube_url, languages)

        result = SubtitleResult(
            video_id=video_id,
            title=title,
            subtitles=subtitles,
            downloaded_at=self._now(),
        )

        # 如果有字幕，下载到文件
        if subtitles:
            result.file_path = self._save_subtitle(result)

        return result

    def _get_video_info(self, url: str) -> dict:
        """获取视频信息"""
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-download",
            "--no-warnings",
            url,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass

        return {}

    def _get_subtitles(self, url: str, languages: List[str]) -> List[dict]:
        """获取字幕列表"""
        subtitles = []

        # 下载字幕
        cmd = [
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs", ",".join(languages),
            "--skip-download",
            "--no-warnings",
            "-o", "%(id)s.%(ext)s",
            url,
        ]

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except Exception:
            return []

        # 解析下载的字幕文件
        video_id = self._extract_video_id(url)
        if not video_id:
            return []

        # 查找字幕文件
        for ext in ["vtt", "srt", "ass"]:
            sub_file = Path(f"{video_id}.{ext}")
            if sub_file.exists():
                subtitles.append({
                    "lang": self._detect_lang(sub_file),
                    "type": self._detect_type(sub_file),
                    "file": str(sub_file),
                    "content": self._read_subtitle(sub_file),
                })
                break

        return subtitles

    def _detect_lang(self, file: Path) -> str:
        """检测字幕语言"""
        name = file.stem.lower()
        if "zh" in name or "cn" in name:
            return "zh-CN"
        elif "en" in name:
            return "en"
        return "unknown"

    def _detect_type(self, file: Path) -> str:
        """检测字幕类型"""
        name = file.stem.lower()
        if "auto" in name:
            return SubtitleType.AUTO.value
        return SubtitleType.MANUAL.value

    def _read_subtitle(self, file: Path) -> str:
        """读取字幕内容"""
        try:
            content = file.read_text(encoding="utf-8")
            # 转换为纯文本
            return self._subtitle_to_text(content)
        except Exception:
            return ""

    def _subtitle_to_text(self, content: str) -> str:
        """字幕转换为纯文本"""
        lines = content.split("\n")
        text_lines = []

        for line in lines:
            # 跳过时间轴
            if "-->" in line:
                continue
            # 跳过标签
            line = re.sub(r"<[^>]+>", "", line)
            line = line.strip()
            if line and not line.isdigit():
                text_lines.append(line)

        return " ".join(text_lines)

    def _save_subtitle(self, result: SubtitleResult) -> str:
        """保存字幕到文件"""
        filename = f"{result.video_id}_subtitles.txt"
        filepath = self.output_dir / filename

        # 合并所有字幕
        all_content = []
        for sub in result.subtitles:
            all_content.append(f"[{sub['lang']}] {sub['content']}")

        filepath.write_text("\n\n".join(all_content), encoding="utf-8")

        return str(filepath)

    def _extract_video_id(self, url: str) -> Optional[str]:
        """提取视频 ID"""
        patterns = [
            r"v=([a-zA-Z0-9_-]{11})",
            r"youtu\.be/([a-zA-Z0-9_-]{11})",
            r"embed/([a-zA-Z0-9_-]{11})",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def _now(self) -> str:
        """当前时间"""
        from datetime import datetime
        return datetime.now().isoformat()


def is_youtube_url(url: str) -> bool:
    """检测是否是 YouTube URL"""
    return "youtube.com" in url or "youtu.be" in url
