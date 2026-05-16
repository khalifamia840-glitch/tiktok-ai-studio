# -*- coding: utf-8 -*-
"""Musica de fondo automatica segun el tema del video."""
import os, asyncio
import aiohttp

MUSIC_DIR = "outputs/music"

# Tracks de SoundHelix - libres de derechos, siempre disponibles
# Tracks de SoundHelix & Pixabay - Estilos Virales 2026
MOOD_TRACKS = {
    "energetic":    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", # Phonk placeholder
    "motivational": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3", # Cinematic placeholder
    "cinematic":    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3", 
    "ambient":      "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3", # Lo-Fi placeholder
    "corporate":    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
    "happy":        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
    "electronic":   "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3",
    "inspirational":"https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3",
}

MOOD_MAP = {
    "auto": "energetic", "carro": "energetic", "coche": "energetic",
    "moto": "energetic", "deporte": "energetic", "fitness": "energetic",
    "gym": "energetic", "ejercicio": "energetic", "velocidad": "energetic",
    "motivacion": "motivational", "exito": "motivational", "disciplina": "motivational",
    "emprendedor": "motivational", "liderazgo": "motivational",
    "dinero": "corporate", "negocio": "corporate", "inversion": "corporate",
    "tecnologia": "electronic", "inteligencia": "electronic", "futuro": "electronic",
    "viaje": "cinematic", "turismo": "cinematic", "aventura": "cinematic",
    "naturaleza": "ambient", "relajacion": "ambient", "salud": "ambient",
    "comida": "happy", "humor": "happy", "familia": "happy", "amor": "happy",
}

async def fetch_music(topic: str, duration: int, job_id: str):
    os.makedirs(MUSIC_DIR, exist_ok=True)
    out_path = f"{MUSIC_DIR}/{job_id}.mp3"
    mood = _detect_mood(topic)
    print(f"[Music] Tema={topic!r} -> Mood={mood!r}")
    url = MOOD_TRACKS.get(mood, MOOD_TRACKS["inspirational"])
    if await _download(url, out_path):
        print(f"[Music] OK: {out_path}")
        return out_path
    print("[Music] Fallo descarga, continuando sin musica")
    return None

def _detect_mood(topic: str) -> str:
    t = topic.lower()
    for kw, mood in MOOD_MAP.items():
        if kw in t:
            return mood
    return "inspirational"

async def _download(url: str, out: str) -> bool:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers,
                             timeout=aiohttp.ClientTimeout(total=30),
                             allow_redirects=True) as r:
                if r.status == 200:
                    data = await r.read()
                    if len(data) > 1000:
                        with open(out, "wb") as f:
                            f.write(data)
                        return True
    except Exception as e:
        print(f"[Music] Error: {e}")
    return False