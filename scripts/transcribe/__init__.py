"""
transcribe 模块 - 音视频转录

Agent 没有音视频转文字能力，需要脚本补充

依赖：
- YouTube: yt-dlp
- Whisper: openai-whisper
"""

from .youtube import YouTubeTranscriber, is_youtube_url
from .whisper import AudioTranscriber

__all__ = [
    "YouTubeTranscriber",
    "AudioTranscriber",
    "is_youtube_url",
]
