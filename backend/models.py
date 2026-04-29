"""
Data models for TikTok Video Generator pipeline.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class GenerationRequest:
    """Represents a video generation request."""
    topic: str
    duration: int = 30


@dataclass
class GenerationResult:
    """Represents the result of a video generation pipeline run."""
    success: bool
    job_id: str
    output_path: str | None = None    # Set on success; None on failure
    error_stage: str | None = None    # Name of the failed stage, or None
    error_message: str | None = None  # Human-readable failure reason, or None


@dataclass
class SubtitleEntry:
    """A single timed subtitle entry.

    Invariant: 0 <= start < end
    """
    text: str
    start: float  # Start time in seconds (relative to video start)
    end: float    # End time in seconds (relative to video start)


@dataclass
class ImageProviderConfig:
    """Configuration for image providers, read from environment variables."""
    provider: str          # "dalle" | "pexels" | "pixabay"
    openai_api_key: str
    pexels_api_key: str
    pixabay_api_key: str


@dataclass
class VideoSpec:
    """Constants that define the output video format."""
    width: int = 540
    height: int = 960
    fps: int = 24
    video_codec: str = "libx264"
    audio_codec: str = "aac"