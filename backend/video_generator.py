import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

# -*- coding: utf-8 -*-
"""
VideoGenerator - Orquestador principal del pipeline TikTok Video Generator.

Coordina las etapas en orden:
  1. generate_script  (services/script_service.py)
  2. generate_audio   (audio_service.py)
  3. fetch_media      (services/media_service.py)
  4. generate_subtitles (subtitle_service.py)  [opcional]
  5. assemble_video   (services/video_service.py)

Retorna un dict con success=True/False y los campos correspondientes.
"""
import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import uuid
from typing import Any

from services.script_service import generate_script
from audio_service import generate_audio
from services.media_service import fetch_media
from subtitle_service import generate_subtitles
from services.video_service import assemble_video


async def generate_video(
    topic: str,
    duration: int = 30,
    language: str = "es",
    voice: str = "gtts",
    niche: str = "general",
    style: str = "entretenido",
    audience: str = "general",
    add_subtitles: bool = True,
    is_premium: bool = False,
) -> dict[str, Any]:
    """
    Orquesta el pipeline completo de generacion de video TikTok.

    Args:
        topic:         Tema del video.
        duration:      Duracion objetivo en segundos (por defecto 30).
        language:      Codigo de idioma, p.ej. "es" o "en".
        voice:         Motor TTS: "gtts" o "edge".
        niche:         Nicho del contenido (p.ej. "fitness", "tecnologia").
        style:         Estilo narrativo (p.ej. "entretenido", "educativo").
        audience:      Audiencia objetivo (p.ej. "jovenes", "general").
        add_subtitles: Si True, genera y superpone subtitulos en el video.
        is_premium:    Si True, omite marca de agua. Si False, anade marca de agua.

    Returns:
        Dict con los campos:
          - success (bool)
          - job_id (str)
          - output_path (str | None)
          - script (dict | None)
          - error_stage (str | None)
          - error_message (str | None)
    """
    job_id: str = str(uuid.uuid4())

    # --- Etapa 1: Generar script ---
    try:
        script = await generate_script(
            topic=topic,
            style=style,
            audience=audience,
            duration=duration,
            language=language,
            niche=niche,
        )
    except Exception as exc:
        return {
            "success": False,
            "job_id": job_id,
            "output_path": None,
            "script": None,
            "error_stage": "script",
            "error_message": str(exc),
        }

    # --- Etapa 2: Generar audio ---
    narration: str = script.get("narration", topic)
    try:
        audio_path: str = await generate_audio(
            script=narration,
            job_id=job_id,
            language=language,
            engine=voice,
        )
    except Exception as exc:
        return {
            "success": False,
            "job_id": job_id,
            "output_path": None,
            "script": script,
            "error_stage": "audio",
            "error_message": str(exc),
        }

    # --- Etapa 3: Obtener media ---
    keywords: list[str] = script.get("keywords", [topic])
    try:
        media_paths: list[str] = await fetch_media(
            keywords=keywords,
            duration=duration,
            job_id=job_id,
        )
    except Exception as exc:
        return {
            "success": False,
            "job_id": job_id,
            "output_path": None,
            "script": script,
            "error_stage": "media",
            "error_message": str(exc),
        }

    # --- Etapa 4: Generar subtitulos (opcional) ---
    subtitles: list = []
    if add_subtitles:
        # Intentar obtener duracion del audio para sincronizar subtitulos
        try:
            from moviepy.editor import AudioFileClip
            audio_clip = AudioFileClip(audio_path)
            audio_duration: float = audio_clip.duration
            audio_clip.close()
        except Exception:
            audio_duration = float(duration)

        # Los subtitulos ya vienen del script si el script_service los genera
        if script.get("subtitles"):
            subtitles = script["subtitles"]
        else:
            try:
                subtitles = generate_subtitles(
                    script=narration,
                    audio_duration=audio_duration,
                )
            except Exception as exc:
                return {
                    "success": False,
                    "job_id": job_id,
                    "output_path": None,
                    "script": script,
                    "error_stage": "subtitles",
                    "error_message": str(exc),
                }

    # --- Etapa 5: Ensamblar video ---
    title: str = script.get("title", topic)
    segment_durations: list = script.get("segment_durations", [])
    try:
        video_path: str = await assemble_video(
            job_id=job_id,
            audio_path=audio_path,
            media_paths=media_paths,
            subtitles=subtitles,
            title=title,
            segment_durations=segment_durations if segment_durations else None,
            is_premium=is_premium,
        )
    except Exception as exc:
        return {
            "success": False,
            "job_id": job_id,
            "output_path": None,
            "script": script,
            "error_stage": "assembly",
            "error_message": str(exc),
        }

    # --- Exito ---
    return {
        "success": True,
        "job_id": job_id,
        "output_path": video_path,
        "script": {
            "title": script.get("title", topic),
            "narration": narration,
            "keywords": keywords,
            "hook": script.get("hook", ""),
            "cta": script.get("cta", ""),
            "mood": script.get("mood", ""),
            "niche": script.get("niche", niche),
        },
        "error_stage": None,
        "error_message": None,
    }