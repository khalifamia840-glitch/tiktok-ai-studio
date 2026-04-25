# -*- coding: utf-8 -*-
"""
Subtitle Service - Genera subtitulos sincronizados para videos TikTok.

Divide el script en segmentos de maximo 6 palabras y los distribuye
uniformemente a lo largo de la duracion del audio.
"""
from __future__ import annotations

# Estilos disponibles para subtitulos
_STYLES = ("normal", "viral", "emotional", "energetic")

# Maximo de palabras por segmento de subtitulo
_MAX_WORDS_PER_SEGMENT = 6


def _split_into_segments(script: str) -> list[str]:
    """Divide el script en segmentos de maximo _MAX_WORDS_PER_SEGMENT palabras."""
    words = script.split()
    if not words:
        return []

    segments: list[str] = []
    for i in range(0, len(words), _MAX_WORDS_PER_SEGMENT):
        chunk = words[i : i + _MAX_WORDS_PER_SEGMENT]
        segments.append(" ".join(chunk))

    return segments


def _assign_style(index: int, total: int) -> str:
    """
    Asigna un estilo al segmento segun su posicion en el video.

    - Inicio (primer 25%): energetic  -> engancha al espectador
    - Medio-inicio (25-50%): viral    -> contenido principal
    - Medio-final (50-75%): emotional -> conexion emocional
    - Final (ultimo 25%): normal      -> cierre tranquilo
    """
    if total == 0:
        return "normal"

    ratio = index / total
    if ratio < 0.25:
        return "energetic"
    elif ratio < 0.50:
        return "viral"
    elif ratio < 0.75:
        return "emotional"
    else:
        return "normal"


def generate_subtitles(script: str, audio_duration: float) -> list[dict]:
    """
    Genera subtitulos sincronizados a partir de un script y la duracion del audio.

    Divide el script en segmentos de maximo 6 palabras y los distribuye
    uniformemente a lo largo de audio_duration.

    Args:
        script: Texto completo del script del video.
        audio_duration: Duracion total del audio en segundos (>= 0).

    Returns:
        Lista de dicts con las claves:
            - "start" (float): Tiempo de inicio en segundos. 0 <= start < end.
            - "end"   (float): Tiempo de fin en segundos. end <= audio_duration.
            - "text"  (str):   Texto del subtitulo.
            - "style" (str):   Uno de "normal", "viral", "emotional", "energetic".

    Raises:
        ValueError: Si audio_duration es negativa.
    """
    if audio_duration < 0:
        raise ValueError(f"audio_duration must be >= 0, got {audio_duration}")

    segments = _split_into_segments(script.strip())

    # Sin segmentos o duracion cero -> lista vacia
    if not segments or audio_duration == 0.0:
        return []

    n = len(segments)
    segment_duration = audio_duration / n

    result: list[dict] = []
    for i, text in enumerate(segments):
        start = i * segment_duration
        # El ultimo segmento termina exactamente en audio_duration
        end = audio_duration if i == n - 1 else (i + 1) * segment_duration

        # Garantizar invariante: start < end
        if start >= end:
            end = min(start + 0.001, audio_duration)
            if start >= end:
                # Segmento no representable; omitir
                continue

        style = _assign_style(i, n)

        result.append(
            {
                "start": round(start, 6),
                "end": round(end, 6),
                "text": text,
                "style": style,
            }
        )

    return result