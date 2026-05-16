"""
Ensamblaje de video con MoviePy + subtitulos via PIL (sin ImageMagick)
Formato TikTok: 540x960, 24fps, H.264/AAC
"""
import os
import logging
import asyncio
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips,
)

# Importar VideoSpec desde models.py para evitar constantes hardcodeadas
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import VideoSpec
from image_processor import normalize_batch, validate_image

_SPEC = VideoSpec()
W = _SPEC.width        # 540
H = _SPEC.height       # 960
FPS = _SPEC.fps        # 24

logger = logging.getLogger(__name__)


async def assemble_video(
    job_id: str,
    audio_path: str,
    media_paths: list,
    subtitles: list,
    title: str,
    segment_durations: list = None,
    is_premium: bool = False,
    fast_mode: bool = False,
) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _build, job_id, audio_path, media_paths, subtitles, title, segment_durations, is_premium, fast_mode
    )


def _get_font(size: int):
    """Intenta cargar una fuente TrueType; cae en la fuente por defecto de PIL."""
    for path in [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _make_subtitle_clip(text: str, start: float, end: float, total: float):
    """
    Genera un clip de subtitulo ELITE (Estilo Hormozi / Viral).
    - Texto en negrita, grande.
    - Contorno negro grueso (4px).
    - Resaltado aleatorio en Amarillo o Cian.
    """
    font = _get_font(48)  # Más grande para impacto
    max_text_width = W - 60

    # Lógica de resaltado (Hormozi Style)
    import random
    highlight_colors = [(255, 255, 0, 255), (0, 255, 255, 255)] # Amarillo y Cian
    
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        try:
            tmp = Image.new("RGBA", (1, 1))
            bbox = ImageDraw.Draw(tmp).textbbox((0, 0), test, font=font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = len(test) * 24
        if tw > max_text_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)

    line_h = 60
    pad = 20
    total_h = len(lines) * line_h + pad * 2

    # Canvas transparente para el subtítulo
    bg = Image.new("RGBA", (W, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bg)

    for i, line in enumerate(lines):
        y = pad + i * line_h
        # Elegir color (80% blanco, 20% resaltado)
        main_color = (255, 255, 255, 255)
        if random.random() > 0.8:
            main_color = random.choice(highlight_colors)

        # Stroke/Contorno grueso (Req Elite)
        stroke_w = 4
        for dx in range(-stroke_w, stroke_w + 1):
            for dy in range(-stroke_w, stroke_w + 1):
                if dx*dx + dy*dy <= stroke_w*stroke_w:
                    draw.text((W // 2 + dx, y + dy), line, font=font, fill=(0, 0, 0, 255), anchor="mt")
        
        # Texto principal
        draw.text((W // 2, y), line, font=font, fill=main_color, anchor="mt")

    arr = np.array(bg)
    clamped_end = min(end, total)
    clip = (
        ImageClip(arr, ismask=False)
        .set_start(start)
        .set_end(clamped_end)
        .set_position(("center", int(H * 0.70))) # Un poco más arriba para evitar el HUD de TikTok
    )
    return clip


def _build(
    job_id: str,
    audio_path: str,
    media_paths: list,
    subtitles: list,
    title: str,
    segment_durations: list = None,
    is_premium: bool = False,
    fast_mode: bool = False,
) -> str:
    """
    Ensambla el video final y limpia los archivos temporales.

    Raises:
        RuntimeError: Si no se puede cargar ninguna imagen.
    """
    audio = AudioFileClip(audio_path)
    total = audio.duration
    n = max(len(media_paths), 1)

    # Calcular duraciones por clip
    if segment_durations and len(segment_durations) == len(media_paths):
        scale = total / sum(segment_durations)
        durations = [d * scale for d in segment_durations]
    else:
        durations = [total / n] * n

    # ─── NORMALIZACIÓN OBLIGATORIA ───────────────────────────────────────
    # Convierte TODA imagen (WebP, PNG, RGBA, Progressive JPEG, etc.) a
    # JPEG baseline RGB válido antes de pasarla a MoviePy/FFmpeg.
    # Si alguna falla: usa un placeholder cinematográfico.
    # ─────────────────────────────────────────────────────────────────────
    logger.info("[Video] Normalizando %d imágenes para job %s...", len(media_paths), job_id)
    norm_dir = f"outputs/media/{job_id}/normalized"
    normalized = normalize_batch(media_paths, norm_dir, job_id)
    logger.info("[Video] %d/%d imágenes normalizadas OK", len(normalized), len(media_paths))

    # Ajustar durations al número real de imágenes normalizadas
    n_actual = len(normalized)
    if n_actual != n:
        durations = [total / n_actual] * n_actual

    # Crear clips de imagen desde las rutas normalizadas
    clips = []
    import math
    for i, (p, dur) in enumerate(zip(normalized, durations)):
        try:
            logger.info("[Video] Cargando clip %d: %s", i, p)
            clip = ImageClip(p).set_duration(max(0.1, dur))
            if not fast_mode:
                # Efecto Ken Burns (Zoom in / out)
                zoom_factor = 1.05
                if i % 2 == 0:
                    clip = clip.resize(lambda t: 1 + (zoom_factor - 1) * t / clip.duration)
                else:
                    clip = clip.resize(lambda t: zoom_factor - (zoom_factor - 1) * t / clip.duration)
                # Crossfade transition
                if i > 0:
                    clip = clip.crossfadein(0.5)
            clips.append(clip)
            logger.info("[Video] ✅ Clip %d cargado OK (%s)", i, p)
        except Exception as exc:
            logger.error("[Video] ❌ No se pudo crear clip %d para %s: %s", i, p, exc)

    # Fallback de emergencia: si NADA funcionó, clip negro
    if not clips:
        logger.error("[Video] ❌ EMERGENCIA: ningún clip cargó, usando pantalla negra para job %s", job_id)
        from image_processor import create_fallback_image
        emergency_path = f"outputs/media/{job_id}/emergency.jpg"
        os.makedirs(f"outputs/media/{job_id}", exist_ok=True)
        create_fallback_image(emergency_path, idx=0)
        clips = [ImageClip(emergency_path).set_duration(total)]




    video = (
        concatenate_videoclips(clips, method="compose" if not fast_mode else "chain")
        .set_duration(total)
    )

    # Añadir música de fondo si no es fast_mode
    if not fast_mode:
        from moviepy.editor import CompositeAudioClip
        bgm_path = "assets/bgm.mp3"
        if os.path.exists(bgm_path):
            try:
                bgm = AudioFileClip(bgm_path).volumex(0.15)
                # Loopear o cortar la música para que coincida con el total
                if bgm.duration < total:
                    from moviepy.audio.fx.all import audio_loop
                    bgm = audio_loop(bgm, duration=total)
                else:
                    bgm = bgm.subclip(0, total)
                
                final_audio = CompositeAudioClip([audio, bgm])
                video = video.set_audio(final_audio)
            except Exception as exc:
                logger.warning("[Video] Error añadiendo BGM: %s", exc)
                video = video.set_audio(audio)
        else:
            video = video.set_audio(audio)
    else:
        video = video.set_audio(audio)

    # Subtitulos con PIL (sin ImageMagick)
    layers = [video]
    for sub in subtitles:
        try:
            # Soportar tanto dict como SubtitleEntry dataclass
            if hasattr(sub, "text"):
                text, start, end = sub.text, sub.start, sub.end
            else:
                text, start, end = sub["text"], sub["start"], sub["end"]
            layers.append(_make_subtitle_clip(text, start, end, total))
        except Exception as exc:
            logger.warning("[Subtitulo] Error al crear clip: %s", exc)

    # --- Ethical AI Label & Watermark (PIL based) ---
    try:
        # Reutilizar lógica de subtítulos para la marca de agua y etiqueta ética
        ai_label = _make_subtitle_clip("🤖 AI Generated Content", 0, total, total)
        # Posicionar la etiqueta ética arriba a la derecha (pequeña)
        ai_label = ai_label.set_position(("right", "top")).set_opacity(0.5)
        layers.append(ai_label)

        if not is_premium:
            studio_label = _make_subtitle_clip("TikTok AI Studio", 0, total, total)
            studio_label = studio_label.set_position(("center", "bottom")).set_opacity(0.7)
            layers.append(studio_label)
            
    except Exception as exc:
        logger.warning("[Ethics/Watermark] Error al crear clips estáticos: %s", exc)

    final = CompositeVideoClip(layers, size=(W, H)) if len(layers) > 1 else video

    out_path = f"outputs/{job_id}.mp4"
    final.write_videofile(
        out_path,
        fps=FPS,
        codec=_SPEC.video_codec,
        audio_codec=_SPEC.audio_codec,
        temp_audiofile=f"outputs/tmp_{job_id}.m4a",
        remove_temp=True,
        logger=None,
        preset="ultrafast",
        threads=4,
    )

    # --- Tarea 5.2: Limpieza de archivos temporales ---
    # Eliminar directorio outputs/media/{job_id}/
    media_dir = f"outputs/media/{job_id}"
    try:
        shutil.rmtree(media_dir)
        logger.info("[Cleanup] Eliminado directorio %s", media_dir)
    except OSError as exc:
        logger.warning("[Cleanup] No se pudo eliminar %s: %s", media_dir, exc)

    # Eliminar todos los archivos temporales de audio
    audio_file = f"outputs/audio/{job_id}.mp3"
    try:
        if os.path.exists(audio_file):
            os.remove(audio_file)
            logger.info("[Cleanup] Eliminado %s", audio_file)
    except OSError as exc:
        logger.warning("[Cleanup] No se pudo eliminar %s: %s", audio_file, exc)

    return out_path