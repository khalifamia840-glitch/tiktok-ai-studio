"""
AI Cinematic Visual Engine — Prompt Engine
==========================================
Transforma keywords basicos en prompts cinematograficos completos.

Detecta automaticamente:
  - Emocion dominante por escena
  - Tipo de camara (Shot Director)
  - Iluminacion emocional
  - Estilo visual (Realista, Anime, Oscuro, TikTok Viral, etc.)

Genera negative prompts profesionales para evitar deformidades.
"""

from __future__ import annotations
import re
import random


# ─────────────────────────────────────────────
# MAPAS DE EMOCION
# ─────────────────────────────────────────────

EMOTION_KEYWORDS: dict[str, list[str]] = {
    "sad": [
        "solo", "triste", "llorar", "perder", "muerto", "murio", "fallecio",
        "abandonado", "broken", "tears", "cry", "lost", "alone", "sad",
        "abandoned", "grief", "pain", "despair", "lluvia", "rain", "oscuridad",
        "desamor", "goodbye", "adios", "perro", "dog", "alone"
    ],
    "tense": [
        "misterio", "secreto", "oscuro", "peligro", "miedo", "terror",
        "mystery", "secret", "dark", "danger", "fear", "horror", "unknown",
        "shadow", "threat", "suspense", "tension", "conspiracy", "hidden",
        "forbidden", "creepy", "paranoia", "haunted", "sinister"
    ],
    "epic": [
        "batalla", "guerra", "ejercito", "soldado", "heroe", "poderoso",
        "battle", "war", "army", "soldier", "hero", "powerful", "warrior",
        "fight", "victory", "empire", "king", "queen", "ancient", "legend",
        "epic", "dragon", "sword", "shield", "conquista", "conquest"
    ],
    "motivational": [
        "exito", "dinero", "millonario", "disciplina", "gym", "fitness",
        "success", "money", "millionaire", "discipline", "workout", "hustle",
        "grind", "ambition", "dream", "goal", "rich", "wealthy", "achieve",
        "power", "focus", "mindset", "ganar", "win", "trophy"
    ],
    "romantic": [
        "amor", "pareja", "beso", "romance", "enamorado", "corazon",
        "love", "couple", "kiss", "romantic", "heart", "passion", "tender",
        "sweet", "together", "wedding", "boda", "feliz", "happy"
    ],
    "shocking": [
        "increible", "impactante", "sorprendente", "revelacion", "verdad",
        "incredible", "shocking", "surprising", "reveal", "truth", "exposed",
        "secret exposed", "never before", "unbelievable", "mind-blowing",
        "viral", "fact", "dato", "nadie sabe"
    ],
}

# ─────────────────────────────────────────────
# MAPAS DE ILUMINACION POR EMOCION
# ─────────────────────────────────────────────

LIGHTING_MAP: dict[str, str] = {
    "sad":         "dramatic cold blue lighting, heavy shadows, overcast sky, volumetric rain light, dim street lamps",
    "tense":       "dark moody lighting, deep shadows, single harsh light source, atmospheric fog, noir style",
    "epic":        "golden hour dramatic sunlight, volumetric god rays, high contrast dramatic lighting, cinematic orange glow",
    "motivational":"powerful studio lighting, warm golden tones, motivational bright atmosphere, high contrast",
    "romantic":    "soft warm bokeh, golden hour light, gentle diffused sunlight, romantic candlelight glow",
    "shocking":    "harsh dramatic lighting, high contrast, flash-style lighting, intense spotlight",
    "neutral":     "cinematic natural lighting, soft directional light, shallow depth of field, professional photography",
}

# ─────────────────────────────────────────────
# MAPAS DE ATMOSFERA POR EMOCION
# ─────────────────────────────────────────────

ATMOSPHERE_MAP: dict[str, str] = {
    "sad":         "melancholic atmosphere, heavy rain, empty street, solitude, quiet despair",
    "tense":       "ominous atmosphere, thick fog, eerie silence, unsettling tension, dark alley",
    "epic":        "grandiose epic atmosphere, ancient ruins, vast landscape, heroic composition",
    "motivational":"energetic powerful atmosphere, urban city skyline, luxury environment",
    "romantic":    "warm intimate atmosphere, soft petals, gentle breeze, beautiful scenery",
    "shocking":    "intense dramatic atmosphere, high energy tension, urgency",
    "neutral":     "cinematic atmosphere, documentary feel, authentic environment",
}

# ─────────────────────────────────────────────
# SHOT TYPES POR POSICION DE ESCENA
# ─────────────────────────────────────────────

def _get_shot_type(scene_index: int, total_scenes: int, emotion: str) -> str:
    """Asigna tipo de camara segun posicion narrativa y emocion."""
    progress = scene_index / max(total_scenes - 1, 1)

    if emotion == "tense":
        options = ["extreme close-up shot", "dutch angle shot", "over the shoulder shot", "low angle shot"]
        return options[scene_index % len(options)]

    if emotion == "epic":
        if progress < 0.2:
            return "wide establishing shot, drone view"
        elif progress < 0.5:
            return "medium cinematic shot"
        elif progress < 0.8:
            return "dynamic action shot"
        else:
            return "epic wide shot, hero pose"

    if emotion == "sad":
        if progress < 0.3:
            return "wide lonely shot"
        elif progress < 0.7:
            return "medium emotional shot"
        else:
            return "close-up emotional face, tears"

    # Default narrative arc
    if progress < 0.15:
        return "wide establishing shot"
    elif progress < 0.35:
        return "medium shot"
    elif progress < 0.6:
        return "close-up shot"
    elif progress < 0.85:
        return "medium shot"
    else:
        return "wide cinematic final shot"


# ─────────────────────────────────────────────
# ESTILOS VISUALES
# ─────────────────────────────────────────────

STYLE_SUFFIXES: dict[str, str] = {
    "realistic":    "ultra realistic, photorealistic, 8k detail, RAW photo, DSLR quality, sharp focus",
    "cinematic":    "cinematic color grading, anamorphic lens flare, film grain, movie still, director's cut",
    "dark":         "dark moody aesthetic, noir style, deep shadows, high contrast, gritty texture, ominous",
    "anime":        "anime style, detailed anime illustration, vibrant colors, manga aesthetic, studio ghibli quality",
    "tiktok_viral": "viral TikTok aesthetic, trendy visual style, high saturation, eye-catching composition",
    "documentary":  "documentary photography, journalistic style, authentic, raw, handheld feel",
    "hyperrealistic": "hyper realistic, 8k ultra HD, microscopic detail, perfect anatomy, flawless skin texture",
}

# ─────────────────────────────────────────────
# NEGATIVE PROMPT UNIVERSAL
# ─────────────────────────────────────────────

NEGATIVE_PROMPT = (
    "low quality, blurry, deformed hands, extra fingers, missing fingers, "
    "ugly face, bad anatomy, distorted eyes, watermark, text, logo, signature, "
    "duplicate, cropped, out of frame, jpeg artifacts, pixelated, grain noise, "
    "overexposed, underexposed, cartoon, 3d render, painting, sketch, drawing, "
    "artificial, plastic, doll, unrealistic proportions, bad lighting"
)


# ─────────────────────────────────────────────
# MOTOR PRINCIPAL
# ─────────────────────────────────────────────

def detect_emotion(text: str) -> str:
    """Detecta la emocion dominante en un keyword o narracion."""
    text_lower = text.lower()
    scores: dict[str, int] = {e: 0 for e in EMOTION_KEYWORDS}

    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[emotion] += 1

    best = max(scores, key=lambda e: scores[e])
    return best if scores[best] > 0 else "neutral"


def build_cinematic_prompt(
    image_keyword: str,
    narration: str = "",
    scene_index: int = 0,
    total_scenes: int = 4,
    visual_style: str = "cinematic",
    character_descriptor: str = "",
    emotion_override: str = "",
) -> dict[str, str]:
    """
    Construye un prompt cinematografico completo a partir de un keyword basico.

    Returns:
        {
            "positive": str,   # Prompt completo para la IA de imagen
            "negative": str,   # Negative prompt universal
            "emotion":  str,   # Emocion detectada
            "shot_type": str,  # Tipo de camara asignado
        }
    """
    # Detectar emocion combinando keyword + narracion
    combined_text = f"{image_keyword} {narration}"
    emotion = emotion_override if emotion_override else detect_emotion(combined_text)

    # Obtener tipo de camara
    shot_type = _get_shot_type(scene_index, total_scenes, emotion)

    # Obtener iluminacion y atmosfera
    lighting = LIGHTING_MAP.get(emotion, LIGHTING_MAP["neutral"])
    atmosphere = ATMOSPHERE_MAP.get(emotion, ATMOSPHERE_MAP["neutral"])

    # Obtener sufijo de estilo visual
    style_suffix = STYLE_SUFFIXES.get(visual_style, STYLE_SUFFIXES["cinematic"])

    # Construir el core del prompt
    # Si hay un descriptor de personaje, incluirlo para consistencia
    character_part = f"{character_descriptor}, " if character_descriptor else ""

    positive_prompt = (
        f"{shot_type}, {character_part}{image_keyword}, "
        f"{lighting}, {atmosphere}, "
        f"vertical 9:16 portrait format, "
        f"TikTok video frame, "
        f"{style_suffix}, "
        f"no text, no watermark, no logo"
    )

    return {
        "positive": positive_prompt,
        "negative": NEGATIVE_PROMPT,
        "emotion": emotion,
        "shot_type": shot_type,
        "lighting": lighting,
    }


def generate_character_seed(topic: str) -> int:
    """
    Genera un seed deterministico basado en el topico.
    El mismo topico siempre produce el mismo seed → mismo personaje.
    """
    seed = 0
    for char in topic.lower():
        seed = (seed * 31 + ord(char)) % (2**32)
    return seed


def build_style_prompt_batch(
    segments: list[dict],
    topic: str,
    visual_style: str = "cinematic",
) -> list[dict]:
    """
    Procesa todos los segmentos de un script y genera los prompts
    cinematograficos completos para cada uno.

    Args:
        segments: Lista de segmentos del script (con image_keyword, narration, emotion)
        topic: Topico general del video (para character seed)
        visual_style: Estilo visual elegido por el usuario

    Returns:
        Lista de dicts con {positive, negative, emotion, shot_type, lighting}
    """
    character_seed = generate_character_seed(topic)
    total = len(segments)
    results = []

    for i, seg in enumerate(segments):
        keyword = seg.get("image_keyword", seg.get("narration", "cinematic scene"))
        narration = seg.get("narration", "")
        emotion_override = seg.get("emotion", "")

        prompt_data = build_cinematic_prompt(
            image_keyword=keyword,
            narration=narration,
            scene_index=i,
            total_scenes=total,
            visual_style=visual_style,
            emotion_override=emotion_override,
        )
        prompt_data["character_seed"] = character_seed + i  # Leve variacion por escena
        prompt_data["scene_index"] = i
        results.append(prompt_data)

    return results
