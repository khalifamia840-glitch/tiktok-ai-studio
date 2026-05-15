"""
Generacion de scripts con Groq - con segmentos coordinados, nicho y mood
"""
import os, json, re, asyncio
from groq import Groq

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY no configurada. Edita el archivo .env")
        _client = Groq(api_key=api_key)
    return _client


async def generate_script(topic, style, audience, duration, language, niche="general"):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _call_groq, topic, style, audience, duration, language, niche)


def _call_groq(topic, style, audience, duration, language, niche="general"):
    lang_name = "espanol" if language == "es" else "English"
    clips_count = max(4, duration // 5)

    prompt = f"""Eres un maestro en viralidad de TikTok, experto en retención de audiencia y hooks psicológicos.
Crea un script para un video de {duration} segundos sobre: "{topic}"
Nicho: {niche} | Estilo: {style} | Audiencia: {audience} | Idioma: {lang_name}

El video tendra exactamente {clips_count} segmentos visuales coordinados.
Tu objetivo principal es MAXIMIZAR la retención.

Responde UNICAMENTE con JSON valido:
{{
  "title": "titulo super clickbait (max 60 chars)",
  "hook": "El gancho de los primeros 3s. Debe generar una curiosidad extrema o controversia.",
  "cta": "llamada a la accion brutal al final",
  "pacing": "rapido y dinamico",
  "emotions": ["intriga", "shock", "revelacion"],
  "segments": [
    {{
      "order": 1,
      "narration": "texto narrado - el primer segmento DEBE ser el hook",
      "image_keyword": "descripcion visual muy especifica y cinematografica en ingles",
      "duration_ratio": 0.33,
      "subtitle_style": "viral"
    }}
  ]
}}

REGLAS DE VIRALIDAD:
- Exactamente {clips_count} segmentos.
- duration_ratio debe sumar 1.0
- image_keyword: en ingles, listo para un modelo de IA (ej: "cinematic dark lighting, highly detailed roman soldier face").
- subtitle_style: "viral" (para hooks), "emotional", "energetic", o "normal".
- El HOOK es lo mas importante. Usa técnicas como: "Lo que nadie te cuenta sobre...", "POV:...", "El secreto oscuro de...".
- Ritmo rapido, frases cortas, sin emojis en la narracion.
"""

    response = get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()
    match = re.search(r'\{[\s\S]*\}', raw)
    if match:
        raw = match.group()

    try:
        data = json.loads(raw)
        result = _process_segments(data, duration)
        result["mood"] = _detect_mood(style, niche)
        result["niche"] = niche
        return result
    except Exception as e:
        print(f"[Script] Error: {e}")
        return _fallback_script(topic, duration, clips_count, niche)


def _process_segments(data, duration):
    segments = data.get("segments", [])
    if not segments:
        return _fallback_script(data.get("title", "video"), duration, 3)

    total_ratio = sum(s.get("duration_ratio", 1/len(segments)) for s in segments)
    keywords, narration_parts, subtitles, subtitle_styles = [], [], [], []
    current_time = 0.0

    for seg in segments:
        ratio = seg.get("duration_ratio", 1/len(segments)) / total_ratio
        seg_duration = duration * ratio
        narration = seg.get("narration", "").strip()
        keyword = seg.get("image_keyword", seg.get("narration", "video"))
        style = seg.get("subtitle_style", "normal")

        keywords.append(keyword)
        narration_parts.append(narration)
        subtitle_styles.append(style)

        words = narration.split()
        if words:
            words_per_sub = 5
            chunks = [words[i:i+words_per_sub] for i in range(0, len(words), words_per_sub)]
            chunk_dur = seg_duration / len(chunks)
            for j, chunk in enumerate(chunks):
                start = current_time + j * chunk_dur
                end = start + chunk_dur
                subtitles.append({
                    "start": round(start, 2),
                    "end": round(min(end, duration), 2),
                    "text": " ".join(chunk),
                    "style": style
                })

        current_time += seg_duration

    return {
        "title": data.get("title", "Video"),
        "narration": " ".join(narration_parts),
        "keywords": keywords,
        "subtitles": subtitles,
        "subtitle_styles": subtitle_styles,
        "segments": segments,
        "hook": data.get("hook", ""),
        "cta": data.get("cta", ""),
        "segment_durations": [
            duration * (s.get("duration_ratio", 1/len(segments)) / total_ratio)
            for s in segments
        ]
    }


def _detect_mood(style, niche):
    motivational = ["motivacional", "disciplina", "gym", "fitness", "exito", "dinero", "emprendedor", "negocios"]
    emotional = ["emocional", "relaciones", "amor", "familia", "tristeza", "inspiracional"]
    energetic = ["humor", "entretenido", "viral", "baile", "fiesta", "comedia"]
    educational = ["educativo", "informativo", "tecnologia", "ciencia", "historia"]

    combined = (style + " " + niche).lower()
    if any(w in combined for w in motivational): return "motivacional"
    elif any(w in combined for w in emotional): return "emocional"
    elif any(w in combined for w in energetic): return "energetico"
    elif any(w in combined for w in educational): return "educativo"
    return "motivacional"


def _fallback_script(topic, duration, clips_count, niche="general"):
    return {
        "title": topic,
        "narration": f"Descubre todo sobre {topic}.",
        "keywords": [topic] * clips_count,
        "subtitles": [],
        "mood": _detect_mood("motivacional", niche),
        "niche": niche,
        "segment_durations": [duration / clips_count] * clips_count,
    }
