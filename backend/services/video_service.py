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
) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _build, job_id, audio_path, media_paths, subtitles, title, segment_durations, is_premium
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
    Genera un clip de subtitulo usando PIL (sin ImageMagick).

    - Fondo semitransparente negro con alpha 160.
    - Texto blanco (255, 255, 255) con sombra negra de 2 px.
    - Posicion vertical al 75 % desde arriba.
    - Wrapping con padding de 40 px (max ancho de linea = W - 40).
    - end se clampea a total.
    """
    font = _get_font(32)
    max_text_width = W - 40  # Req 6.2: frame width minus 40 px padding

    # Dividir texto en lineas respetando el ancho maximo
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
            tw = len(test) * 16
        if tw > max_text_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)

    line_h = 40
    pad = 10
    total_h = len(lines) * line_h + pad * 2

    # Fondo semitransparente: alpha 160 (Req 6.3)
    bg = Image.new("RGBA", (W, total_h), (0, 0, 0, 160))
    draw = ImageDraw.Draw(bg)

    for i, line in enumerate(lines):
        y = pad + i * line_h
        # Sombra negra desplazada 2 px (Req 6.4)
        draw.text((W // 2 + 2, y + 2), line, font=font, fill=(0, 0, 0, 255), anchor="mt")
        # Texto blanco (Req 6.4)
        draw.text((W // 2, y), line, font=font, fill=(255, 255, 255, 255), anchor="mt")

    arr = np.array(bg)
    # Clampear end a total (Req 6.5)
    clamped_end = min(end, total)
    clip = (
        ImageClip(arr, ismask=False)
        .set_start(start)
        .set_end(clamped_end)
        .set_position(("center", int(H * 0.75)))  # 75 % desde arriba (Req 5.6)
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

    # Redimensionar imagenes a la resolucion de salida
    resized: list[str] = []
    for p in media_paths:
        try:
            img = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
            out = p.replace(".jpg", "_sm.jpg")
            img.save(out, "JPEG", quality=85)
            resized.append(out)
        except Exception as exc:
            logger.warning("[Video] No se pudo redimensionar %s: %s", p, exc)
            resized.append(p)

    # Crear clips de imagen
    clips = []
    for p, dur in zip(resized, durations):
        try:
            clips.append(ImageClip(p).set_duration(max(0.1, dur)))
        except Exception as exc:
            logger.warning("[Video] No se pudo crear clip para %s: %s", p, exc)

    # Req 5.9: RuntimeError descriptivo si no hay clips
    if not clips:
        raise RuntimeError(
            f"No se pudieron cargar las imagenes para el job '{job_id}'. "
            "Verifica que los archivos de media existan y sean imagenes JPEG validas."
        )

    video = (
        concatenate_videoclips(clips, method="compose")
        .set_duration(total)
        .set_audio(audio)
    )

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

    if not is_premium:
        try:
            from moviepy.editor import TextClip
            watermark = (
                TextClip("Generado con TikTok AI Studio", font="Arial", fontsize=24, color='white', bg_color='black')
                .set_position(("center", "bottom"))
                .set_duration(total)
                .set_opacity(0.6)
            )
            layers.append(watermark)
        except Exception as exc:
            logger.warning("[Watermark] No se pudo crear marca de agua: %s", exc)

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

    # Eliminar outputs/audio/{job_id}.mp3
    audio_file = f"outputs/audio/{job_id}.mp3"
    try:
        os.remove(audio_file)
        logger.info("[Cleanup] Eliminado %s", audio_file)
    except OSError as exc:
        logger.warning("[Cleanup] No se pudo eliminar %s: %s", audio_file, exc)

    # Eliminar todos los archivos _sm.jpg intermedios
    for p in resized:
        if p.endswith("_sm.jpg"):
            try:
                os.remove(p)
                logger.info("[Cleanup] Eliminado %s", p)
            except OSError as exc:
                logger.warning("[Cleanup] No se pudo eliminar %s: %s", p, exc)

    return out_path