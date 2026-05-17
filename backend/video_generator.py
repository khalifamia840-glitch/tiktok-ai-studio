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
import os
from typing import Any

from services.script_service import generate_script
from audio_service import generate_audio
from services.media_service import fetch_media
from subtitle_service import generate_subtitles
from services.video_service import assemble_video


from jobs_db import update_job

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
    fast_mode: bool = False,
    visual_style: str = "cinematic",
    upscaler: str = "pil",
    job_id: str = None,
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
    if not job_id:
        job_id = str(uuid.uuid4())

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

    # --- Etapa 2 y 3: Generar audio y obtener media EN PARALELO ---
    if job_id: update_job(job_id, status="running", progress=30, message="🎙️ Voces IA y 🎬 Engine 5D: Analizando Shot, Entorno y Luz...")
    import asyncio
    narration: str = script.get("narration", topic)
    keywords: list[str] = script.get("keywords", [topic])
    
    async def get_audio_safe():
        try:
            return await generate_audio(
                script=narration,
                job_id=job_id,
                language=language,
                engine=voice,
            )
        except Exception as exc:
            return exc

    async def get_media_safe():
        try:
            return await fetch_media(
                keywords=keywords,
                duration=duration,
                job_id=job_id,
                fast_mode=fast_mode,
                visual_style=visual_style,
                segments=script.get("segments", []),
                topic=topic,
                upscaler=upscaler,
            )
        except Exception as exc:
            return exc

    results = await asyncio.gather(get_audio_safe(), get_media_safe())
    audio_res = results[0]
    media_res = results[1]

    if isinstance(audio_res, Exception):
        return {
            "success": False,
            "job_id": job_id,
            "output_path": None,
            "script": script,
            "error_stage": "audio",
            "error_message": str(audio_res),
        }
    else:
        audio_path = audio_res

    if isinstance(media_res, Exception):
        return {
            "success": False,
            "job_id": job_id,
            "output_path": None,
            "script": script,
            "error_stage": "media",
            "error_message": str(media_res),
        }
    else:
        media_paths = media_res

    # --- Etapa 4: Generar subtitulos (opcional) ---
    if job_id: update_job(job_id, status="running", progress=60, message="✍️ Generando narrativa visual y subtítulos dinámicos...")
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

    # --- VALIDACIÓN ESTRICTA PRE-ENSAMBLADO: No permitir fallos visuales ---
    valid_paths = []
    from image_processor import validate_image
    
    for i, p in enumerate(media_paths):
        if not p or not os.path.exists(p):
            return {
                "success": False,
                "job_id": job_id,
                "error_stage": "media_validation",
                "error_message": f"CRITICAL: Scene {i} is missing its image asset ({p}). Stopping render."
            }
        
        if "placeholder" in p.lower():
             return {
                "success": False,
                "job_id": job_id,
                "error_stage": "media_validation",
                "error_message": f"CRITICAL: Placeholder detected for scene {i}. Strict mode active: no placeholders allowed."
            }
            
        if not validate_image(p):
             return {
                "success": False,
                "job_id": job_id,
                "error_stage": "media_validation",
                "error_message": f"CRITICAL: Image for scene {i} ({p}) failed content validation (corrupted, black or too small)."
            }
        valid_paths.append(p)


    # --- Etapa 5: Ensamblar video ---
    if job_id: update_job(job_id, status="running", progress=75, message="🎬 Masterizado: Renderizando física de movimiento y color grading...")
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
            fast_mode=fast_mode,
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