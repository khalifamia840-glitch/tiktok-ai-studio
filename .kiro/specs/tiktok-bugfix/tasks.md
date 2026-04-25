# Tareas de Implementación — TikTok Bugfix

- [x] 1. Arreglar persistencia de jobs en DB y llamadas faltantes (main.py)
  - [x] 1.1 Agregar llamadas a `update_job()` en cada cambio de estado dentro de `run_pipeline`
  - [x] 1.2 Llamar `save_to_cloud()` al completar exitosamente un video
  - [x] 1.3 Llamar `save_video_stats()` al completar exitosamente un video

- [x] 2. Arreglar encoding roto en script_service.py
  - [x] 2.1 Reemplazar `NarraciÃƒÆ'Ã‚Â³n` por `Narración` en el prompt de `_call_groq`
  - [x] 2.2 Verificar que el archivo tenga `# -*- coding: utf-8 -*-` al inicio

- [x] 3. Arreglar resolución inconsistente (models.py y media_service.py)
  - [x] 3.1 Actualizar `VideoSpec` en `models.py` para usar `VIDEO_W=1080` y `VIDEO_H=1920` de `config.py`
  - [x] 3.2 Actualizar `TIKTOK_W, TIKTOK_H` en `media_service.py` de 540×960 a 1080×1920

- [x] 4. Unificar servicios TTS (audio_service.py)
  - [x] 4.1 Agregar soporte para ElevenLabs en `audio_service.py`
  - [x] 4.2 Agregar fallback automático: elevenlabs → edge → gtts

- [x] 5. Arreglar timeout en frontend (api.js)
  - [x] 5.1 Cambiar `timeout: 30000` a `timeout: 0` en el cliente axios

- [x] 6. Agregar campo niche al formulario (GeneratePage.jsx)
  - [x] 6.1 Agregar constante `NICHES` con las opciones disponibles
  - [x] 6.2 Agregar `niche: 'general'` al estado inicial del formulario
  - [x] 6.3 Agregar selector de nicho en el formulario

- [x] 7. Reemplazar confirm() con modal React (LibraryPage.jsx)
  - [x] 7.1 Agregar estado `confirmDelete` para controlar el modal
  - [x] 7.2 Implementar modal de confirmación inline en JSX
  - [x] 7.3 Conectar el modal con la función `handleDelete`
