"""
音频转录 - Whisper 实现

使用 OpenAI Whisper 进行音频转录
"""

import subprocess
from pathlib import Path
from typing import Optional


class AudioTranscriber:
    """
    音频转录器

    使用 Whisper 进行本地音频转录
    """

    def __init__(
        self,
        model: str = "base",
        language: str = None,
        output_dir: str = "./transcripts",
    ):
        """
        Args:
            model: Whisper 模型大小 (tiny, base, small, medium, large)
            language: 指定语言（可选）
            output_dir: 输出目录
        """
        self.model = model
        self.language = language
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def transcribe(
        self,
        audio_path: str,
        output_format: str = "txt",
    ) -> str:
        """
        转录音频

        Args:
            audio_path: 音频文件路径
            output_format: 输出格式 (txt, json, srt, vtt)

        Returns:
            转录文本或文件路径
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")

        # 构建命令
        cmd = [
            "whisper",
            str(audio_path),
            "--model", self.model,
            "--output_format", output_format,
            "--output_dir", str(self.output_dir),
        ]

        if self.language:
            cmd.extend(["--language", self.language])

        # 执行
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 分钟超时
            )

            if result.returncode != 0:
                raise RuntimeError(f"Whisper 转录失败: {result.stderr}")

            # 输出文件路径
            output_file = self.output_dir / f"{audio_path.stem}.{output_format}"

            if output_format == "txt":
                return output_file.read_text(encoding="utf-8")
            else:
                return str(output_file)

        except FileNotFoundError:
            raise RuntimeError(
                "Whisper 未安装。请运行: pip install openai-whisper"
            )

    def transcribe_youtube(self, youtube_url: str) -> str:
        """
        直接从 YouTube 转录

        Args:
            youtube_url: YouTube URL

        Returns:
            转录文本
        """
        # 先下载音频
        from .youtube import YouTubeTranscriber, is_youtube_url

        if not is_youtube_url(youtube_url):
            raise ValueError("不是有效的 YouTube URL")

        # 获取字幕（更快）
        yt = YouTubeTranscriber(output_dir=str(self.output_dir))
        result = yt.get_subtitle(youtube_url)

        if result.file_path:
            return Path(result.file_path).read_text(encoding="utf-8")

        # 如果没有字幕，需要下载音频后转录
        print("无可用字幕，正在下载音频...")

        audio_path = self._download_audio(youtube_url)

        return self.transcribe(str(audio_path))

    def _download_audio(self, url: str) -> Path:
        """下载 YouTube 音频"""
        from .youtube import is_youtube_url

        if not is_youtube_url(url):
            raise ValueError("不是有效的 YouTube URL")

        output_file = self.output_dir / "audio.mp3"

        cmd = [
            "yt-dlp",
            "-x",  # 提取音频
            "--audio-format", "mp3",
            "-o", str(output_file),
            "--no-warnings",
            url,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                raise RuntimeError(f"音频下载失败: {result.stderr}")

            # yt-dlp 输出的文件名可能不同
            # 查找最新创建的 mp3 文件
            mp3_files = list(self.output_dir.glob("*.mp3"))
            if mp3_files:
                return max(mp3_files, key=lambda p: p.stat().st_mtime)

            return output_file

        except FileNotFoundError:
            raise RuntimeError(
                "yt-dlp 未安装。请运行: pip install yt-dlp"
            )


def check_whisper() -> bool:
    """检查 Whisper 是否可用"""
    try:
        result = subprocess.run(
            ["whisper", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False
