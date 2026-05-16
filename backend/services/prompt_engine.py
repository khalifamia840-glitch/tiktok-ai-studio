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
# MOVIMIENTOS DE CAMARA (CAMERA MOVEMENTS)
# ─────────────────────────────────────────────

CAMERA_MOVEMENTS: dict[str, str] = {
    "epic":        "dramatic slow drone pan, cinematic crane shot, sweeping vista movement",
    "tense":       "slow push-in, unsettling handheld camera shake, tight tracking shot",
    "sad":         "static mournful composition, slow zoom-out to emphasize solitude",
    "motivational":"fast dolly zoom, energetic camera tracking, low angle pan up",
    "romantic":    "gentle circular camera rotation, soft handheld movement, intimate focus pull",
    "shocking":    "sudden quick zoom, whip pan, high energy camera shake",
    "neutral":     "smooth slider movement, clean professional camera work",
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
            return "extreme wide establishing shot"
        elif progress < 0.5:
            return "low angle cinematic medium shot"
        elif progress < 0.8:
            return "dynamic high-angle action shot"
        else:
            return "epic panoramic wide shot"

    if emotion == "sad":
        if progress < 0.3:
            return "isolated wide shot"
        elif progress < 0.7:
            return "intimate medium emotional shot"
        else:
            return "extreme close-up on eyes, emotional intensity"

    # Default narrative arc
    if progress < 0.15:
        return "wide establishing shot"
    elif progress < 0.35:
        return "cinematic medium shot"
    elif progress < 0.6:
        return "intimate close-up shot"
    elif progress < 0.85:
        return "medium tracking shot"
    else:
        return "wide cinematic payoff shot"


# ─────────────────────────────────────────────
# ESTILOS VISUALES
# ─────────────────────────────────────────────

STYLE_SUFFIXES: dict[str, str] = {
    "realistic":    "analog photography, 35mm Fujifilm, realistic skin texture, pores, imperfections, natural lighting, RAW, unedited",
    "cinematic":    "movie still from a 35mm film, cinematic grain, natural colors, anamorphic lens, high dynamic range",
    "dark":         "low key lighting, heavy shadows, gritty film look, realistic noir, dark aesthetic",
    "anime":        "anime style, detailed anime illustration, vibrant colors, manga aesthetic, studio ghibli quality",
    "tiktok_viral": "viral TikTok aesthetic, trendy visual style, high saturation, eye-catching composition",
    "documentary":  "documentary photography, journalistic style, authentic, raw, handheld feel",
    "hyperrealistic": "hyper realistic, 8k ultra HD, microscopic detail, perfect anatomy, flawless skin texture",
    "kling": "Kling AI 2.0 aesthetics, cinematic physical simulation, dynamic lighting, ultra photorealistic, high-end motion blur",
    "veo": "Google Veo 3 quality, high-fidelity generative video style, realistic fluid physics, professional cinematography, soft light reflections",
    "noir": "black and white photography, high contrast noir, 35mm monochrome film, dramatic shadows, classic cinema look",
}

# ─────────────────────────────────────────────
# NEGATIVE PROMPT UNIVERSAL
# ─────────────────────────────────────────────

NEGATIVE_PROMPT = (
    "low quality, blurry, deformed hands, extra fingers, missing fingers, "
    "ugly face, bad anatomy, distorted eyes, watermark, text, logo, signature, "
    "duplicate, cropped, out of frame, jpeg artifacts, pixelated, grain noise, "
    "overexposed, underexposed, cartoon, 3d render, painting, sketch, drawing, "
    "illustration, vector, digital art, cg, anime, comic, saturated colors, "
    "artificial, plastic, doll, unrealistic proportions, bad lighting, "
    "3d render, unreal engine, octane render, stylized, airbrushed, smooth skin"
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


def _detect_action(narration: str) -> str:
    """Detecta acciones físicas simples en la narración."""
    n = narration.lower()
    if "caminando" in n or "walking" in n: return "walking forward, "
    if "corriendo" in n or "running" in n: return "running fast, "
    if "hablando" in n or "talking" in n: return "talking to camera, "
    if "mirando" in n or "looking" in n: return "looking into the distance, "
    if "sonriendo" in n or "smiling" in n: return "smiling warmly, "
    if "llorando" in n or "crying" in n: return "crying, "
    return ""

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

    # Si hay un descriptor de personaje, incluirlo para consistencia
    character_part = f"{character_descriptor}, " if character_descriptor else ""

    # Obtener movimiento de camara
    camera_movement = CAMERA_MOVEMENTS.get(emotion, CAMERA_MOVEMENTS["neutral"])

    # Detectar accion
    action = _detect_action(narration)

    # Construir el MASTER PROMPT ELITE v3.0 (5 Dimensiones)
    # 1. TOMA (Shot Description)
    # 2. ENTORNO (Environment)
    # 3. MOVIMIENTO (Camera Movement)
    # 4. ILUMINACIÓN (Lighting Style)
    # 5. ACCIÓN (Character Action / Image Keyword)
    
    positive_prompt = (
        f"HYPER-PHOTOREALISTIC CINEMATIC STILL, masterpiece quality, National Geographic style, shot on 35mm film, Canon EOS R5: "
        f"[TOMA: {shot_type}], "
        f"[ENTORNO: in a {atmosphere}], "
        f"[MOVIMIENTO: {camera_movement}], "
        f"[ILUMINACIÓN: {lighting}], "
        f"[ACCIÓN: {character_part}{action}{image_keyword}], "
        f"9:16 vertical TikTok ratio, {style_suffix}, "
        f"hyper-realistic textures, intricate details, 8k, professional color grading, "
        f"ultra-sharp focus, filmic atmosphere, no text, no watermark"
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
