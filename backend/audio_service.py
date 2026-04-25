# -*- coding: utf-8 -*-
"""
Audio Service - Sintesis de voz para el pipeline TikTok Video Generator.

Motores soportados:
  - edge       : edge-tts (Microsoft Edge TTS, sin costo)
  - gtts       : gTTS (Google Text-to-Speech, sin costo)
  - elevenlabs : ElevenLabs (voz ultra-realista, requiere ELEVENLABS_API_KEY)

Uso:
    from audio_service import generate_audio
    path = await generate_audio(script, job_id, language="es", engine="edge")
"""

import os
import asyncio
import requests

# Mapas de voces por idioma
_EDGE_VOICES: dict[str, str] = {
    "es": "es-ES-AlvaroNeural",
    "en": "en-US-GuyNeural",
}

_GTTS_LANGS: dict[str, str] = {
    "es": "es",
    "en": "en",
}

_ELEVENLABS_VOICES: dict[str, str] = {
    "es": "pNInz6obpgDQGcFmaJgB",
    "en": "21m00Tcm4TlvDq8ikWAM",
}


async def generate_audio(
    script: str,
    job_id: str,
    language: str = "es",
    engine: str = "gtts",
) -> str:
    """Sintetiza voz desde `script` y guarda el resultado en outputs/audio/{job_id}.mp3.

    Args:
        script:   Texto a sintetizar.
        job_id:   Identificador unico del trabajo.
        language: Codigo de idioma, p.ej. "es" o "en".
        engine:   Motor TTS: "edge", "gtts" o "elevenlabs".

    Returns:
        Ruta al archivo MP3 generado.
    """
    out_dir = os.path.join("outputs", "audio")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{job_id}.mp3")

    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")

    if engine == "elevenlabs" and elevenlabs_key:
        try:
            await _synthesize_elevenlabs(script, language, out_path, elevenlabs_key)
            return out_path
        except Exception as e:
            print(f"[AudioService][ElevenLabs] Error: {e}, usando fallback edge-tts")

    if engine in ("edge", "elevenlabs"):
        try:
            await _synthesize_edge(script, language, out_path)
            return out_path
        except Exception as e:
            print(f"[AudioService][edge-tts] Error: {e}, usando fallback gTTS")

    await _synthesize_gtts(script, language, out_path)
    return out_path


async def _synthesize_elevenlabs(script: str, language: str, out_path: str, api_key: str) -> None:
    """Sintetiza con ElevenLabs (voz ultra-realista)."""
    voice_id = _ELEVENLABS_VOICES.get(language, _ELEVENLABS_VOICES["es"])
    loop = asyncio.get_event_loop()

    def _blocking():
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
            json={
                "text": script,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            },
            timeout=30,
        )
        if r.status_code != 200:
            raise RuntimeError(f"ElevenLabs HTTP {r.status_code}: {r.text[:200]}")
        with open(out_path, "wb") as f:
            f.write(r.content)
        print(f"[AudioService][ElevenLabs] Guardado: {out_path}")

    await loop.run_in_executor(None, _blocking)


async def _synthesize_edge(script: str, language: str, out_path: str) -> None:
    """Sintetiza con edge-tts (Microsoft Edge TTS)."""
    import edge_tts  # type: ignore[import]
    voice = _EDGE_VOICES.get(language, _EDGE_VOICES["es"])
    communicate = edge_tts.Communicate(script, voice)
    await communicate.save(out_path)
    print(f"[AudioService][edge-tts] Guardado: {out_path} (voz={voice})")


async def _synthesize_gtts(script: str, language: str, out_path: str) -> None:
    """Sintetiza con gTTS (Google Text-to-Speech)."""
    from gtts import gTTS  # type: ignore[import]
    lang = _GTTS_LANGS.get(language, _GTTS_LANGS["es"])
    loop = asyncio.get_event_loop()

    def _blocking_save() -> None:
        tts = gTTS(text=script, lang=lang)
        tts.save(out_path)

    await loop.run_in_executor(None, _blocking_save)
    print(f"[AudioService][gTTS] Guardado: {out_path} (lang={lang})")
