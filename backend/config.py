"""
Configuracion central - AUTO TIKTOK AI
"""
import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

# -- IA / Script ----------------------------------------------------------
GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")

# -- Voz ------------------------------------------------------------------
ELEVENLABS_API_KEY  = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# -- Video Clips ----------------------------------------------------------
PEXELS_API_KEY  = os.getenv("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")

# -- Image provider -------------------------------------------------------
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "dalle")

# -- Servidor -------------------------------------------------------------
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
REDIS_URL = os.getenv("REDIS_URL", "")

# -- Video ----------------------------------------------------------------
VIDEO_W   = 1080
VIDEO_H   = 1920
VIDEO_FPS = 24

# -- Directorios ----------------------------------------------------------
OUTPUT_DIR = "outputs"
AUDIO_DIR  = "outputs/audio"
MEDIA_DIR  = "outputs/media"


def ensure_output_dirs() -> None:
    """Create required output directories if they do not exist."""
    for directory in (OUTPUT_DIR, MEDIA_DIR, AUDIO_DIR):
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)


# Create output directories at import time
ensure_output_dirs()


def get_script_engine() -> str:
    """Retorna el motor de IA disponible."""
    if OPENAI_API_KEY:
        return "openai"
    if GROQ_API_KEY:
        return "groq"
    raise ValueError(
        "Necesitas al menos una API key de IA.\n"
        "- Groq (GRATIS): https://console.groq.com\n"
        "- OpenAI: https://platform.openai.com"
    )


def get_tts_engine() -> str:
    """Retorna el motor TTS disponible."""
    if ELEVENLABS_API_KEY:
        return "elevenlabs"
    return "edge"  # Edge TTS siempre disponible, gratis


def validate() -> list:
    """Retorna lista de advertencias de configuracion."""
    warnings = []
    if not GROQ_API_KEY and not OPENAI_API_KEY:
        warnings.append("Sin API key de IA. Configura GROQ_API_KEY (gratis) en .env")
    if not PEXELS_API_KEY and not PIXABAY_API_KEY:
        warnings.append("Sin API key de video. Configura PEXELS_API_KEY (gratis) en .env")
    if not ELEVENLABS_API_KEY:
        warnings.append("Sin ElevenLabs: usando Edge TTS (gratis, buena calidad)")
    return warnings