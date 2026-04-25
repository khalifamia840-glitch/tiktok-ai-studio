"""
Text-to-Speech Service
- gtts: Google TTS (gratis)
- edge: Microsoft Edge TTS (gratis, voces naturales)
- elevenlabs: ElevenLabs (voz ultra-realista, requiere API key)
"""
import os, asyncio, requests

VOICE_MAP = {
    "es": {"edge": "es-ES-AlvaroNeural", "gtts_lang": "es", "elevenlabs": "pNInz6obpgDQGcFmaJgB"},
    "en": {"edge": "en-US-GuyNeural", "gtts_lang": "en", "elevenlabs": "21m00Tcm4TlvDq8ikWAM"},
}

ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY", "")


async def generate_audio(text: str, language: str, engine: str, job_id: str) -> str:
    os.makedirs("outputs/audio", exist_ok=True)
    out_path = f"outputs/audio/{job_id}.mp3"
    cfg = VOICE_MAP.get(language, VOICE_MAP["es"])

    # ElevenLabs - voz ultra-realista
    if engine == "elevenlabs" and ELEVENLABS_KEY:
        try:
            voice_id = cfg["elevenlabs"]
            r = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"},
                json={"text": text, "model_id": "eleven_multilingual_v2",
                      "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}},
                timeout=30
            )
            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    f.write(r.content)
                print(f"[ElevenLabs] OK")
                return out_path
        except Exception as e:
            print(f"[ElevenLabs] Error: {e}, usando fallback")

    # Edge TTS
    if engine == "edge" or (engine == "elevenlabs" and not ELEVENLABS_KEY):
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, cfg["edge"])
            await communicate.save(out_path)
            return out_path
        except Exception as e:
            print(f"[edge-tts] Error: {e}")

    # gTTS fallback
    from gtts import gTTS
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: gTTS(text=text, lang=cfg["gtts_lang"]).save(out_path))
    return out_path