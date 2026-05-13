# Bugfix Requirements Document

## Introduction

Se han identificado 9 bugs en la aplicación **TikTok AI Video Generator** que afectan a distintas capas del sistema: backend (Python/FastAPI), servicios de generación de video, y frontend (React/JSX). Los bugs van desde funcionalidad silenciosamente rota (imports sin uso, persistencia perdida al reiniciar) hasta problemas de calidad de video, encoding de texto, y compatibilidad con dispositivos móviles/PWA. Este documento captura el comportamiento defectuoso actual, el comportamiento correcto esperado, y el comportamiento que debe preservarse sin cambios.

---

## Bug Analysis

### Current Behavior (Defect)

**Bug 1 — save_to_cloud importado pero nunca usado (main.py)**

1.1 WHEN el pipeline completa la generación de un video THEN el sistema no sube el video a Cloudinary aunque `save_to_cloud` esté importado y Cloudinary esté configurado en el entorno.

**Bug 2 — run_pipeline no actualiza la DB (main.py)**

2.1 WHEN un job cambia de estado (running, completed, error) THEN el sistema solo actualiza el diccionario en memoria `jobs` y nunca llama a `update_job()` para persistir el estado en SQLite.

2.2 WHEN el servidor se reinicia después de haber procesado jobs THEN el sistema pierde todos los estados de jobs porque solo existían en memoria.

**Bug 3 — save_video_stats nunca se llama (main.py)**

3.1 WHEN un video se completa exitosamente THEN el sistema no registra las estadísticas del video en la base de datos, aunque `save_video_stats` está importado desde `jobs_db`.

3.2 WHEN el endpoint `/api/trending` es consultado THEN el sistema retorna datos vacíos o desactualizados porque nunca se han guardado estadísticas de videos generados.

**Bug 4 — Texto con encoding roto (script_service.py)**

4.1 WHEN el modelo Groq genera un script THEN el sistema incluye en el prompt la cadena `NarraciÃƒÆ'Ã‚Â³n` (doble encoding UTF-8 corrupto) en lugar de `Narración`.

4.2 WHEN el prompt llega al modelo de IA con texto corrupto THEN el sistema puede producir scripts con instrucciones malformadas que degradan la calidad del output.

**Bug 5 — Resolución inconsistente (video_service.py vs config.py)**

5.1 WHEN se genera un video THEN el sistema lo produce en resolución 540×960 porque `VideoSpec` en `models.py` define `width=540, height=960`, ignorando los valores `VIDEO_W=1080, VIDEO_H=1920` definidos en `config.py`.

5.2 WHEN el usuario descarga el video THEN el sistema entrega un archivo en baja resolución (540×960) aunque el README y la configuración central indican 1080×1920.

**Bug 6 — Duplicación de servicios TTS (audio_service.py vs tts_service.py)**

6.1 WHEN el pipeline necesita generar audio THEN el sistema usa `audio_service.py` que solo soporta `edge` y `gtts`, ignorando `services/tts_service.py` que tiene soporte para ElevenLabs.

6.2 WHEN el usuario tiene `ELEVENLABS_API_KEY` configurada y selecciona voz de alta calidad THEN el sistema no usa ElevenLabs porque el pipeline nunca invoca `tts_service.py`.

**Bug 7 — Timeout muy corto en el frontend (api.js)**

7.1 WHEN el frontend envía una solicitud de generación de video THEN el sistema configura un timeout de 30 segundos (`timeout: 30000`) para una operación que puede tardar entre 2 y 5 minutos.

7.2 WHEN la generación de video supera los 30 segundos THEN el sistema muestra un error de red en el frontend aunque el backend siga procesando correctamente el job.

**Bug 8 — Campo niche ausente en el formulario (GeneratePage.jsx)**

8.1 WHEN el usuario llena el formulario de generación de video THEN el sistema no expone el campo `niche` en la interfaz, por lo que siempre se envía `"general"` al backend.

8.2 WHEN el backend recibe la solicitud con `niche="general"` forzado THEN el sistema ignora la capacidad de personalización por nicho que el backend sí soporta.

**Bug 9 — confirm() no funciona en PWA/iOS (LibraryPage.jsx)**

9.1 WHEN el usuario intenta eliminar un video en un navegador móvil o en modo PWA en iOS THEN el sistema llama a `window.confirm()` que está bloqueado en esos entornos, haciendo que el diálogo de confirmación no aparezca o sea ignorado silenciosamente.

9.2 WHEN `window.confirm()` es bloqueado por el navegador THEN el sistema puede no ejecutar la eliminación o comportarse de forma impredecible dependiendo del navegador.

---

### Expected Behavior (Correct)

**Bug 1 — save_to_cloud**

2.1 WHEN el pipeline completa la generación de un video exitosamente THEN el sistema SHALL llamar a `save_to_cloud(video_path)` para subir el video a Cloudinary cuando la integración esté configurada.

**Bug 2 — Persistencia de jobs en DB**

2.2 WHEN un job cambia de estado (running, completed, error) THEN el sistema SHALL llamar a `update_job(job_id, ...)` para persistir el estado en SQLite además de actualizar el diccionario en memoria.

2.3 WHEN el servidor se reinicia THEN el sistema SHALL recuperar los estados de jobs desde SQLite a través de `get_job()`.

**Bug 3 — save_video_stats**

3.1 WHEN un video se completa exitosamente THEN el sistema SHALL llamar a `save_video_stats(job_id, topic, niche, ...)` para registrar las estadísticas del video generado.

3.2 WHEN el endpoint `/api/trending` es consultado THEN el sistema SHALL retornar los temas más populares basados en estadísticas reales acumuladas.

**Bug 4 — Encoding del prompt**

4.1 WHEN el sistema construye el prompt para el modelo Groq THEN el sistema SHALL usar la cadena correctamente codificada `Narración` en lugar de `NarraciÃƒÆ'Ã‚Â³n`.

4.2 WHEN el archivo `script_service.py` es guardado THEN el sistema SHALL declarar o garantizar la codificación UTF-8 para que los caracteres especiales en español se preserven correctamente.

**Bug 5 — Resolución del video**

5.1 WHEN se genera un video THEN el sistema SHALL producirlo en resolución 1080×1920 (Full HD vertical, formato TikTok estándar).

5.2 WHEN `VideoSpec` es instanciada THEN el sistema SHALL usar los valores de `config.py` (`VIDEO_W=1080`, `VIDEO_H=1920`) como fuente de verdad para las dimensiones del video.

**Bug 6 — Unificación TTS**

6.1 WHEN el pipeline necesita generar audio y `ELEVENLABS_API_KEY` está configurada THEN el sistema SHALL usar `tts_service.py` (o su lógica equivalente) para aprovechar ElevenLabs.

6.2 WHEN el pipeline genera audio THEN el sistema SHALL soportar los tres motores: `gtts`, `edge` y `elevenlabs`, usando el más apropiado según la configuración disponible.

**Bug 7 — Timeout del frontend**

7.1 WHEN el frontend envía una solicitud de generación de video THEN el sistema SHALL configurar un timeout suficientemente largo (mínimo 10 minutos / 600 000 ms) o deshabilitar el timeout para la llamada de inicio de generación.

7.2 WHEN la generación de video tarda más de 30 segundos THEN el sistema SHALL no mostrar error de red, ya que el polling de estado es independiente de la solicitud inicial.

**Bug 8 — Campo niche en el formulario**

8.1 WHEN el usuario llena el formulario de generación de video THEN el sistema SHALL exponer un campo `niche` (selector o input) que permita al usuario especificar el nicho del contenido.

8.2 WHEN el usuario selecciona un nicho THEN el sistema SHALL enviar el valor seleccionado al backend en el campo `niche` de la solicitud.

**Bug 9 — Confirmación de eliminación sin confirm()**

9.1 WHEN el usuario pulsa el botón de eliminar un video THEN el sistema SHALL mostrar un diálogo de confirmación implementado en React (estado local o modal) que funcione en todos los entornos incluyendo PWA e iOS.

9.2 WHEN el usuario confirma la eliminación en el diálogo React THEN el sistema SHALL proceder con la llamada a `deleteVideo()` y actualizar la lista de videos.

---

### Unchanged Behavior (Regression Prevention)

3.1 WHEN el usuario genera un video con los parámetros actuales (topic, style, audience, duration, language, voice, add_subtitles) THEN el sistema SHALL CONTINUE TO procesar la solicitud y retornar un `job_id` inmediatamente.

3.2 WHEN el frontend hace polling al endpoint `/api/status/{job_id}` THEN el sistema SHALL CONTINUE TO retornar el estado actual del job con los campos `status`, `progress`, `message`, `video_url` y `script`.

3.3 WHEN el pipeline genera un video exitosamente THEN el sistema SHALL CONTINUE TO servir el archivo MP4 desde `/outputs/{filename}` como archivo estático.

3.4 WHEN el usuario accede al endpoint `/api/videos` THEN el sistema SHALL CONTINUE TO listar todos los videos disponibles en el directorio `outputs/`.

3.5 WHEN el usuario elimina un video desde la librería THEN el sistema SHALL CONTINUE TO eliminar el archivo del servidor y actualizar la lista en el frontend.

3.6 WHEN el pipeline genera el script con Groq THEN el sistema SHALL CONTINUE TO retornar la estructura de script con `title`, `narration`, `keywords`, `subtitles`, `hook`, `cta` y `segments`.

3.7 WHEN el motor TTS es `gtts` o `edge` THEN el sistema SHALL CONTINUE TO generar el audio correctamente sin requerir API keys adicionales.

3.8 WHEN el video se ensambla con MoviePy THEN el sistema SHALL CONTINUE TO aplicar subtítulos, concatenar clips de imagen y mezclar el audio correctamente.

3.9 WHEN los endpoints de autenticación (`/api/auth/register`, `/api/auth/login`, `/api/auth/me`) son invocados THEN el sistema SHALL CONTINUE TO funcionar sin cambios.

3.10 WHEN el usuario accede a la aplicación desde un navegador de escritorio THEN el sistema SHALL CONTINUE TO mostrar el formulario de generación y la librería de videos sin regresiones visuales.

---

## Bug Condition Pseudocode

### Bug 1 — save_to_cloud nunca llamado

```pascal
FUNCTION isBugCondition_1(pipeline_result)
  INPUT: pipeline_result con success=true y output_path definido
  OUTPUT: boolean
  RETURN save_to_cloud_was_called = FALSE
END FUNCTION

// Fix Checking
FOR ALL pipeline_result WHERE isBugCondition_1(pipeline_result) DO
  result ← run_pipeline'(pipeline_result)
  ASSERT save_to_cloud_was_called = TRUE
END FOR

// Preservation Checking
FOR ALL pipeline_result WHERE NOT isBugCondition_1(pipeline_result) DO
  ASSERT run_pipeline(pipeline_result) = run_pipeline'(pipeline_result)
END FOR
```

### Bug 2 — update_job nunca llamado

```pascal
FUNCTION isBugCondition_2(job_state_change)
  INPUT: job_state_change con nuevo estado (running | completed | error)
  OUTPUT: boolean
  RETURN update_job_was_called = FALSE
END FUNCTION

// Fix Checking
FOR ALL job_state_change WHERE isBugCondition_2(job_state_change) DO
  run_pipeline'(job_state_change)
  ASSERT sqlite_contains(job_id, new_status) = TRUE
END FOR
```

### Bug 4 — Encoding roto en prompt

```pascal
FUNCTION isBugCondition_4(prompt_text)
  INPUT: prompt_text generado por _call_groq
  OUTPUT: boolean
  RETURN "NarraciÃƒÆ'Ã‚Â³n" IN prompt_text
END FUNCTION

// Fix Checking
FOR ALL prompt_text WHERE isBugCondition_4(prompt_text) DO
  result ← _call_groq'(prompt_text)
  ASSERT "Narración" IN prompt_text AND "NarraciÃƒÆ'Ã‚Â³n" NOT IN prompt_text
END FOR
```

### Bug 5 — Resolución incorrecta

```pascal
FUNCTION isBugCondition_5(video_spec)
  INPUT: video_spec instancia de VideoSpec
  OUTPUT: boolean
  RETURN video_spec.width = 540 AND video_spec.height = 960
END FUNCTION

// Fix Checking
FOR ALL video_spec WHERE isBugCondition_5(video_spec) DO
  spec ← VideoSpec'()
  ASSERT spec.width = 1080 AND spec.height = 1920
END FOR
```

### Bug 7 — Timeout demasiado corto

```pascal
FUNCTION isBugCondition_7(axios_config)
  INPUT: axios_config del cliente API
  OUTPUT: boolean
  RETURN axios_config.timeout = 30000
END FUNCTION

// Fix Checking
FOR ALL axios_config WHERE isBugCondition_7(axios_config) DO
  config ← create_api_client'()
  ASSERT config.timeout >= 600000 OR config.timeout = 0
END FOR
```
