# Diseño Técnico — TikTok Bugfix

## Bug 1 — save_to_cloud nunca llamado (main.py)

Llamar `save_to_cloud(job_id, video_path, script, topic)` dentro de `run_pipeline` justo después de que el resultado sea exitoso, antes de actualizar el estado a `completed`.

```python
# En run_pipeline, bloque success:
save_to_cloud(job_id, video_path, result.get("script", {}), req.topic)
```

---

## Bug 2 — run_pipeline no persiste en DB (main.py)

Agregar llamadas a `update_job()` en cada cambio de estado dentro de `run_pipeline`:

```python
# Al iniciar:
update_job(job_id, status="running", progress=10, message="Iniciando pipeline...")

# Al completar:
update_job(job_id, status="completed", progress=100, message="Video listo", video_url=video_url)

# Al fallar:
update_job(job_id, status="error", progress=0, message=error_msg)
```

---

## Bug 3 — save_video_stats nunca llamado (main.py)

Llamar `save_video_stats()` al completar exitosamente un video:

```python
save_video_stats(job_id, req.topic, req.style, req.niche, req.duration)
```

---

## Bug 4 — Encoding roto en script_service.py

Reemplazar la cadena corrupta `NarraciÃƒÆ'Ã‚Â³n` por `Narración` en el prompt de `_call_groq`. Verificar que el archivo tenga `# -*- coding: utf-8 -*-` al inicio.

---

## Bug 5 — Resolución inconsistente (models.py vs config.py)

Actualizar `VideoSpec` en `models.py` para leer los valores de `config.py`:

```python
from config import VIDEO_W, VIDEO_H, VIDEO_FPS

@dataclass
class VideoSpec:
    width: int = VIDEO_W      # 1080
    height: int = VIDEO_H     # 1920
    fps: int = VIDEO_FPS      # 24
    video_codec: str = "libx264"
    audio_codec: str = "aac"
```

También actualizar `media_service.py` donde `TIKTOK_W, TIKTOK_H = 540, 960` para usar 1080×1920.

---

## Bug 6 — Duplicación TTS (audio_service.py)

Unificar en `audio_service.py` agregando soporte para ElevenLabs, eliminando la necesidad de `tts_service.py` en el pipeline:

```python
async def generate_audio(script, job_id, language="es", engine="gtts"):
    if engine == "elevenlabs" and os.getenv("ELEVENLABS_API_KEY"):
        return await _synthesize_elevenlabs(script, language, out_path)
    elif engine == "edge":
        return await _synthesize_edge(script, language, out_path)
    else:
        return await _synthesize_gtts(script, language, out_path)
```

---

## Bug 7 — Timeout muy corto (api.js)

Cambiar el timeout del cliente axios de 30s a 0 (sin límite) para la instancia general, o crear una instancia separada para la generación:

```js
const api = axios.create({
  baseURL: API_BASE,
  timeout: 0, // sin timeout — el polling maneja el estado
})
```

---

## Bug 8 — Campo niche ausente (GeneratePage.jsx)

Agregar un selector de nicho al formulario con las opciones que el backend ya soporta:

```jsx
const NICHES = ['general','fitness','tecnologia','negocios','humor','educacion','lifestyle']

// En el estado inicial:
niche: 'general',

// En el formulario, nuevo campo selector similar a "Estilo"
```

---

## Bug 9 — confirm() en PWA/iOS (LibraryPage.jsx)

Reemplazar `window.confirm()` con un estado local de React que muestre un modal de confirmación inline:

```jsx
const [confirmDelete, setConfirmDelete] = useState(null) // filename o null

// En lugar de confirm():
setConfirmDelete(filename)

// Modal inline que aparece cuando confirmDelete !== null
```
