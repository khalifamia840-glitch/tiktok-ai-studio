"""
Media Service — AI Cinematic Visual Engine
==========================================
Multi-AI Image Router con Emotion-Based Prompting.

Orden de prioridad:
  CINEMATIC MODE:
    1. Pollinations FLUX (gratis, máxima calidad, con prompt cinematografico)
    2. HuggingFace FLUX Dev (si HF_TOKEN disponible)
    3. Replicate FLUX Dev / Juggernaut XL (si REPLICATE_API_KEY disponible)
    4. Fallback oscuro cinematografico

  FAST MODE:
    1. Pollinations FLUX Schnell (rapido)
    2. Fallback

Caracteristicas:
  - Emotion-Based Prompting automatico
  - Shot Director por escena
  - Character Seed Locking (consistencia de personaje)
  - Smart Image Selection (3 variantes, elige la mejor)
  - Upscale PIL Lanczos (siempre) o Real-ESRGAN (si disponible)
  - Negative prompts profesionales
"""
import os
import io
import asyncio
import requests
import urllib.parse
import hashlib
import random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import config
from services.prompt_engine import build_cinematic_prompt, build_style_prompt_batch

# Cache en memoria
_image_cache: dict = {}

# Resoluciones
FAST_W, FAST_H = 540, 960
HD_W, HD_H = 1080, 1920


def _log_response_debug(response, provider: str):
    """Guarda detalles crudos de la respuesta para auditoría en caso de error."""
    try:
        debug_info = (
            f"PROVIDER: {provider}\n"
            f"STATUS: {response.status_code}\n"
            f"HEADERS: {dict(response.headers)}\n"
            f"BODY (START): {response.text[:2000]}\n"
        )
        with open("debug_response.txt", "a", encoding="utf-8") as f:
            f.write("\n" + "="*50 + "\n")
            f.write(debug_info)
    except Exception as e:
        print(f"[DebugLog] Error guardando log: {e}")

# ─────────────────────────────────────────────
# FUNCION PRINCIPAL
# ─────────────────────────────────────────────

async def fetch_media(
    keywords: list,
    duration: int,
    job_id: str,
    fast_mode: bool = False,
    visual_style: str = "cinematic",
    segments: list = None,
    topic: str = "",
    upscaler: str = "pil",  # "pil" o "realesrgan"
) -> list:
    """Genera todas las imagenes EN PARALELO con prompts cinematograficos."""
    os.makedirs(f"outputs/media/{job_id}", exist_ok=True)
    clips_needed = max(4, duration // 5)

    kws = list(keywords[:clips_needed])
    while len(kws) < clips_needed:
        kws.append(keywords[0] if keywords else "cinematic dark scene")

    # Construir prompts cinematograficos para cada escena
    if segments:
        prompt_data_list = build_style_prompt_batch(segments[:clips_needed], topic, visual_style)
        # Rellenar si hay menos segmentos que clips
        while len(prompt_data_list) < clips_needed:
            prompt_data_list.append(build_cinematic_prompt(kws[len(prompt_data_list)], visual_style=visual_style))
    else:
        # Sin segmentos, construir prompts basicos por keyword
        prompt_data_list = [
            build_cinematic_prompt(kw, scene_index=i, total_scenes=clips_needed, visual_style=visual_style)
            for i, kw in enumerate(kws)
        ]

    # Generar de forma progresiva para permitir streaming visual
    from jobs_db import update_job
    import json
    from cloud_service import upload_image
    
    scenes_ready: dict[int, str] = {}   # idx -> cloud/local URL
    path_by_idx: dict[int, str] = {}    # idx -> local path (para video assembly)
    
    pending_tasks = [
        asyncio.create_task(_get_image_cinematic(kws[i], prompt_data_list[i], i, job_id, fast_mode, upscaler))
        for i in range(clips_needed)
    ]
    
    for completed_task in asyncio.as_completed(pending_tasks):
        idx, path = await completed_task
        if path:
            # VALIDACIÓN ESTRICTA: No permitir placeholders ni archivos inexistentes
            if not os.path.exists(path):
                raise Exception(f"REAL IMAGE FAILED: Scena {idx} - File not found at {path}")
            
            if "placeholder" in path.lower():
                raise Exception(f"STRICT MODE: Placeholder detected for scene {idx}. Stopping render.")

            path_by_idx[idx] = path

            # Subir a la nube para visibilidad inmediata
            cloud_url = upload_image(path, job_id, idx)
            scene_url = cloud_url if cloud_url else f"/outputs/media/{job_id}/{os.path.basename(path)}"
            scenes_ready[idx] = scene_url
            
            # Storyboard parcial
            sorted_scenes = [scenes_ready[k] for k in sorted(scenes_ready.keys())]
            update_job(job_id, scenes_json=json.dumps(sorted_scenes))
        else:
            # Si el router devolvió None, todos los proveedores fallaron
            print(f"[fetch_media] FATAL: La escena {idx} falló en todos los proveedores IA.")
            raise Exception(f"AI IMAGE PIPELINE FAILED at scene {idx}. All providers returned invalid results.")

    # Reconstruir lista ORDENADA
    final_paths = [path_by_idx.get(i) for i in range(clips_needed)]
    
    # Verificación final de integridad
    for i, p in enumerate(final_paths):
        if not p or not os.path.exists(p):
            raise Exception(f"INTEGRITY ERROR: Scene {i} is missing its final image asset.")
            
    return final_paths



# ─────────────────────────────────────────────
# ROUTER DE IMAGEN
# ─────────────────────────────────────────────

async def _get_image_cinematic(
    keyword: str,
    prompt_data: dict,
    idx: int,
    job_id: str,
    fast_mode: bool,
    upscaler: str,
) -> tuple[int, str | None]:
    """Obtiene la mejor imagen posible para la escena con el prompt cinematografico."""
    loop = asyncio.get_event_loop()

    positive_prompt = prompt_data.get("positive", keyword)
    character_seed = prompt_data.get("character_seed", idx * 1000)
    # Añadir aleatoriedad para evitar resultados repetidos si el usuario re-intenta
    character_seed += random.randint(0, 999999)

    # --- Cache key basado en el prompt + indice ---
    cache_key = hashlib.md5(f"{positive_prompt}_{idx}".encode()).hexdigest()[:16]
    if cache_key in _image_cache:
        cached = _image_cache[cache_key]
        if os.path.exists(cached):
            out = f"outputs/media/{job_id}/img_{idx}.jpg"
            try:
                import shutil; shutil.copy2(cached, out)
                return idx, out
            except Exception:
                pass

    # ─── FAST MODE ────────────────────────────────────────────────────
    if fast_mode:
        path = await loop.run_in_executor(
            None, _pollinations_schnell, positive_prompt, character_seed, idx, job_id
        )
        if path:
            from image_processor import validate_image
            if validate_image(path):
                _image_cache[cache_key] = path
                return idx, path
        
        # Si schnell falla en fast mode, intentar cinematic (último recurso)
        path = await loop.run_in_executor(
            None, _pollinations_cinematic, positive_prompt, character_seed, idx, job_id
        )
        if path:
            from image_processor import validate_image
            if validate_image(path):
                _image_cache[cache_key] = path
                return idx, path
        
        # En FAST MODE permitimos placeholder solo si es explícitamente para testeo, 
        # pero para el flujo principal de producción lanzaremos None para que fetch_media falle.
        return idx, None


    # ─── MODO NORMAL: cadena de proveedores (PRIORIDAD ALTA CALIDAD) ──────────

    # PRIORIDAD 1: Replicate FLUX schnell (Calidad Profesional)
    replicate_key = os.getenv("REPLICATE_API_KEY", "")
    if replicate_key:
        print(f"[Router] Escena {idx}: intentando Replicate FLUX...")
        path = await loop.run_in_executor(
            None, _replicate_http, positive_prompt, character_seed, idx, job_id, replicate_key
        )
        if path:
            from image_processor import validate_image
            if validate_image(path):
                path = _apply_upscale(path, upscaler, fast_mode)
                _image_cache[cache_key] = path
                print(f"[Router] Escena {idx}: OK via Replicate")
                return idx, path
            else:
                print(f"[Router] Escena {idx}: Replicate devolvió imagen inválida")

    # PRIORIDAD 2: Google AI Studio Imagen 3 (Realismo Extremo)
    google_key = os.getenv("GOOGLE_AI_STUDIO_KEY", "")
    if google_key:
        print(f"[Router] Escena {idx}: intentando Google AI Studio...")
        path = await loop.run_in_executor(
            None, _google_veo_3_engine, positive_prompt, character_seed, idx, job_id
        )
        if path:
            from image_processor import validate_image
            if validate_image(path):
                path = _apply_upscale(path, upscaler, fast_mode)
                _image_cache[cache_key] = path
                print(f"[Router] Escena {idx}: OK via Google AI Studio")
                return idx, path

    # PRIORIDAD 3: Fal.ai FLUX (Recomendado)
    fal_key = os.getenv("FAL_KEY", "")
    if fal_key:
        print(f"[Router] Escena {idx}: intentando Fal.ai...")
        path = await loop.run_in_executor(
            None, _fal_ai_flux, positive_prompt, character_seed, idx, job_id, fal_key
        )
        if path:
            from image_processor import validate_image
            if validate_image(path):
                path = _apply_upscale(path, upscaler, fast_mode)
                _image_cache[cache_key] = path
                print(f"[Router] Escena {idx}: OK via Fal.ai")
                return idx, path

    # PRIORIDAD 4: HuggingFace (si tiene token)
    hf_token = os.getenv("HF_TOKEN", "")
    if hf_token:
        print(f"[Router] Escena {idx}: intentando HuggingFace...")
        path = await loop.run_in_executor(
            None, _huggingface_flux_dev, positive_prompt, character_seed, idx, job_id, hf_token
        )
        if path:
            from image_processor import validate_image
            if validate_image(path):
                path = _apply_upscale(path, upscaler, fast_mode)
                _image_cache[cache_key] = path
                print(f"[Router] Escena {idx}: OK via HuggingFace")
                return idx, path

    # PRIORIDAD 5: Pollinations FLUX (Último Fallback Gratuito)
    print(f"[Router] Escena {idx}: intentando Pollinations FLUX (Último recurso)...")
    for attempt in range(3):
        # En el tercer intento, simplificar el prompt
        prompt_to_use = positive_prompt if attempt < 2 else keyword + ", cinematic, photorealistic, 9:16 vertical"
        
        p = await loop.run_in_executor(
            None, _pollinations_cinematic, prompt_to_use, character_seed + attempt * 111, idx, job_id
        )
        if p:
            from image_processor import validate_image
            if validate_image(p):
                p = _apply_upscale(p, upscaler, fast_mode)
                _image_cache[cache_key] = p
                print(f"[Router] Escena {idx}: OK via Pollinations (intento {attempt+1})")
                return idx, p
        
        if attempt < 2:
            print(f"[Router] Pollinations intento {attempt+1} fallo, reintentando...")
            await asyncio.sleep(2)


    # ERROR CRÍTICO: Ningún proveedor devolvió imagen real válida
    print(f"[Router] FATAL: TODOS los proveedores fallaron para escena {idx}.")
    # NO devolvemos placeholder aquí para que fetch_media lance error real
    return idx, None



# ─────────────────────────────────────────────
# PROVEEDORES ELITE (MOCKS / WRAPPERS)
# ─────────────────────────────────────────────

def _google_veo_3_engine(prompt: str, seed: int, idx: int, job_id: str) -> str | None:
    """
    Wrapper para Google AI Studio Imagen 3.
    """
    from services.google_ai_studio import generate_veo_3_image
    print(f"[Google AI Studio] Intentando Imagen 3 para escena {idx}...")

    image_bytes = generate_veo_3_image(prompt, seed)
    if image_bytes:
        out = f"outputs/media/{job_id}/img_{idx}.jpg"
        with open(out, "wb") as f:
            f.write(image_bytes)
        return out
    return None

def _fal_ai_flux(prompt: str, seed: int, idx: int, job_id: str, api_key: str) -> str | None:
    """
    Wrapper para Fal.ai FLUX.
    """
    try:
        url = "https://fal.run/fal-ai/flux/schnell"
        headers = {
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "image_size": "portrait_4_3", # Fal suele usar portrait_4_3 o custom
            "num_inference_steps": 4,
            "seed": seed
        }
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if r.status_code == 200:
            data = r.json()
            img_url = data.get("images", [{}])[0].get("url")
            if img_url:
                rd = requests.get(img_url, timeout=30)
                if rd.status_code == 200:
                    out = f"outputs/media/{job_id}/img_{idx}.jpg"
                    with open(out, "wb") as f:
                        f.write(rd.content)
                    return out
        else:
            print(f"[Fal.ai] Error HTTP {r.status_code}: {r.text[:500]}")
    except Exception as e:
        print(f"[Fal.ai] Exception: {e}")
    return None


def _seedance_2_fast_engine(prompt: str, seed: int, idx: int, job_id: str) -> str | None:
    """Wrapper para Fast Mode - usa Pollinations Schnell."""
    print(f"[Fast Engine] Generacion rapida escena {idx}...")
    return _pollinations_schnell(prompt, seed, idx, job_id)


# ─────────────────────────────────────────────
# PROVEEDORES DE IMAGEN
# ─────────────────────────────────────────────

def _pollinations_cinematic(prompt: str, seed: int, idx: int, job_id: str) -> str | None:
    """
    Pollinations.ai con FLUX — Gratis, sin API key.
    Usa 1 sola variante para evitar timeouts de 120s.
    """
    try:
        # Limitar el prompt a 400 chars para evitar URLs demasiado largas
        prompt_short = prompt[:400]
        encoded = urllib.parse.quote(prompt_short)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=576&height=1024&model=flux&nologo=true&enhance=false&seed={seed}"
        )
        r = requests.get(url, timeout=90, allow_redirects=True)
        
        # 3. DETECTAR HTML FALSO / ERRORES
        content_type = r.headers.get("content-type", "")
        if "image" not in content_type:
            print(f"[Pollinations] Error: Content-Type inválido ({content_type})")
            _log_response_debug(r, "Pollinations")
            return None

        if r.status_code == 200 and len(r.content) > 15000:
            try:
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
                
                # --- FILTROS DE POST-PROCESADO ELITE ---
                # 1. Si es NOIR, forzar Blanco y Negro físico
                if "black and white" in prompt.lower() or "monochrome" in prompt.lower():
                    img = img.convert("L").convert("RGB") # Escala de grises pura
                    print(f"[Post-Process] Forzado Blanco y Negro (Noir) para escena {idx}")
                
                # 2. Si es REALISTA, desaturar ligeramente para look analógico
                elif "photorealistic" in prompt.lower() or "analog" in prompt.lower():
                    img = ImageEnhance.Color(img).enhance(0.85) # Look menos saturado, más real
                    img = ImageEnhance.Contrast(img).enhance(1.05)
                    print(f"[Post-Process] Desaturación analógica para escena {idx}")

                img = _crop_to_tiktok(img, HD_W, HD_H)
                out = f"outputs/media/{job_id}/img_{idx}.jpg"
                img.save(out, "JPEG", quality=90)
                print(f"[Pollinations FLUX] OK escena {idx} ({len(r.content)//1024}KB)")
                return out
            except Exception as pil_err:
                print(f"[Pollinations FLUX] PIL error escena {idx}: {pil_err}")
                return None
    except Exception as e:
        print(f"[Pollinations FLUX] Error escena {idx}: {e}")
    return None


def _pollinations_schnell(prompt: str, seed: int, idx: int, job_id: str) -> str | None:
    """Pollinations con modelo rapido para Fast Mode."""
    try:
        encoded = urllib.parse.quote(prompt)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=576&height=1024&model=flux-schnell&nologo=true&seed={seed}"
        )
        r = requests.get(url, timeout=60, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 5000:
            img = Image.open(io.BytesIO(r.content)).convert("RGB")
            img = _crop_to_tiktok(img, FAST_W, FAST_H)
            out = f"outputs/media/{job_id}/img_{idx}.jpg"
            img.save(out, "JPEG", quality=85)
            print(f"[Pollinations Schnell] OK escena {idx}")
            return out
    except Exception as e:
        print(f"[Pollinations Schnell] Error: {e}")
    return None


def _huggingface_flux_dev(
    prompt: str, seed: int, idx: int, job_id: str, hf_token: str
) -> str | None:
    """HuggingFace FLUX Dev — Gratis con token, alta calidad."""
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=hf_token)
        # FLUX.1-schnell is fast and freely available on Inference API
        image = client.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell")
        
        # Guardar imagen generada
        img = _crop_to_tiktok(image, HD_W, HD_H)
        out = f"outputs/media/{job_id}/img_{idx}.jpg"
        img.save(out, "JPEG", quality=92)
        print(f"[HuggingFace FLUX] OK escena {idx}")
        return out
    except Exception as e:
        print(f"[HuggingFace FLUX] Error: {e}")
    return None


def _replicate_http(
    prompt: str, seed: int, idx: int, job_id: str, api_key: str
) -> str | None:
    """
    Replicate API via HTTP REST puro — sin paquete Python.
    Usa flux-schnell: mas rapido (3-5s), mas barato, sin NSFW block.
    Detecta 402 (sin creditos) y retorna None inmediatamente.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "wait",  # Espera sincrona hasta 60s
    }
    payload = {
        "version": "black-forest-labs/flux-schnell",
        "input": {
            "prompt": prompt[:500],
            "num_outputs": 1,
            "aspect_ratio": "9:16",
            "output_format": "jpg",
            "output_quality": 90,
            "seed": int(seed) % (2**32 - 1),
        },
    }
    try:
        print(f"[Replicate] Escena {idx}: enviando a flux-schnell...")
        r = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=90,
        )
        if r.status_code == 402:
            print(f"[Replicate] Sin creditos (402) - saltando a siguiente proveedor")
            return None
        if r.status_code not in (200, 201):
            print(f"[Replicate] HTTP {r.status_code}: {r.text[:200]}")
            _log_response_debug(r, "Replicate (POST)")
            return None

        prediction = r.json()
        if "error" in prediction:
            print(f"[Replicate] API Error: {prediction['error']}")
            return None
        status = prediction.get("status", "")
        output = prediction.get("output")

        # Si 'Prefer: wait' no funciona, hacer polling manual
        if not output and status not in ("failed", "canceled"):
            poll_url = prediction.get("urls", {}).get("get", "")
            if poll_url:
                import time
                for _ in range(30):  # Max 90s (30 x 3s)
                    time.sleep(3)
                    rp = requests.get(poll_url, headers=headers, timeout=15)
                    pred = rp.json()
                    status = pred.get("status", "")
                    output = pred.get("output")
                    print(f"[Replicate] Escena {idx} status: {status}")
                    if status == "succeeded" and output:
                        break
                    if status in ("failed", "canceled"):
                        print(f"[Replicate] Escena {idx} fallida: {pred.get('error', '')}")
                        return None

        if not output:
            print(f"[Replicate] Escena {idx}: sin output")
            return None

        img_url = output[0] if isinstance(output, list) else output
        print(f"[Replicate] Descargando imagen escena {idx}: {str(img_url)[:80]}")
        rd = requests.get(str(img_url), timeout=30)
        if rd.status_code == 200 and len(rd.content) > 5000:
            img = Image.open(io.BytesIO(rd.content)).convert("RGB")
            img = _crop_to_tiktok(img, HD_W, HD_H)
            out = f"outputs/media/{job_id}/img_{idx}.jpg"
            img.save(out, "JPEG", quality=92)
            print(f"[Replicate] OK escena {idx} ({len(rd.content)//1024}KB)")
            return out
        else:
            print(f"[Replicate] Descarga fallida: HTTP {rd.status_code}, {len(rd.content)} bytes")
            return None

    except requests.exceptions.Timeout:
        print(f"[Replicate] Timeout escena {idx}")
        return None
    except Exception as e:
        print(f"[Replicate] Excepcion escena {idx}: {e}")
        return None


def _replicate_flux_dev(
    prompt: str, negative_prompt: str, seed: int, idx: int, job_id: str
) -> str | None:
    """Wrapper legacy — redirige al nuevo caller HTTP."""
    key = os.getenv("REPLICATE_API_KEY", "")
    if not key:
        return None
    return _replicate_http(prompt, seed, idx, job_id, key)


# ─────────────────────────────────────────────
# UPSCALER
# ─────────────────────────────────────────────

def _apply_upscale(path: str, upscaler: str, fast_mode: bool) -> str:
    """
    Aplica upscale a la imagen.
    - "pil": Lanczos a 1080x1920 (siempre disponible)
    - "realesrgan": Real-ESRGAN 4x (requiere basicsr + realesrgan instalados)
    """
    if fast_mode:
        return path  # No upscale en fast mode

    if upscaler == "realesrgan":
        result = _upscale_realesrgan(path)
        if result:
            return result
        print("[Upscaler] Real-ESRGAN no disponible, usando PIL como fallback")

    # PIL Lanczos upscale
    return _upscale_pil(path)


def _upscale_pil(path: str) -> str:
    """Upscale a 1080x1920 usando PIL Lanczos (siempre disponible)."""
    try:
        img = Image.open(path).convert("RGB")
        w, h = img.size
        if w < HD_W or h < HD_H:
            img = img.resize((HD_W, HD_H), Image.LANCZOS)

            # Sharpen sutil para compensar el upscale
            img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=110, threshold=2))

            out = path.replace(".jpg", "_hd.jpg")
            img.save(out, "JPEG", quality=92)
            return out
    except Exception as e:
        print(f"[Upscale PIL] Error: {e}")
    return path


def _upscale_realesrgan(path: str) -> str | None:
    """
    Upscale con Real-ESRGAN (x4 super resolución).
    Requiere: pip install basicsr realesrgan
    """
    try:
        import numpy as np
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet

        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        model_path = "backend/assets/RealESRGAN_x4plus.pth"

        if not os.path.exists(model_path):
            print("[Real-ESRGAN] Modelo no encontrado. Descarga desde: https://github.com/xinntao/Real-ESRGAN")
            return None

        upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=False,
        )

        img_np = np.array(Image.open(path).convert("RGB"))
        output, _ = upsampler.enhance(img_np, outscale=4)
        output_img = Image.fromarray(output)

        # Recortar a 1080x1920
        output_img = _crop_to_tiktok(output_img, HD_W, HD_H)
        out = path.replace(".jpg", "_esrgan.jpg")
        output_img.save(out, "JPEG", quality=95)
        print(f"[Real-ESRGAN] OK: {path}")
        return out
    except ImportError:
        return None
    except Exception as e:
        print(f"[Real-ESRGAN] Error: {e}")
        return None


# ─────────────────────────────────────────────
# COLOR GRADING
# ─────────────────────────────────────────────

def apply_color_grading(img: Image.Image, emotion: str) -> Image.Image:
    """
    Aplica color grading cinematografico por emocion usando PIL.
    """
    import numpy as np

    arr = np.array(img, dtype=np.float32)

    if emotion == "sad":
        # Frio azulado, ligeramente desaturado
        arr[:, :, 0] *= 0.85  # menos rojo
        arr[:, :, 2] *= 1.15  # mas azul
        arr = np.clip(arr, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8))
        img = ImageEnhance.Color(img).enhance(0.82)  # desaturar
        img = ImageEnhance.Contrast(img).enhance(1.1)

    elif emotion == "tense":
        # Oscuro, alto contraste, tinte purpura
        arr[:, :, 0] *= 0.75
        arr[:, :, 1] *= 0.70
        arr[:, :, 2] *= 0.90
        arr = np.clip(arr, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8))
        img = ImageEnhance.Contrast(img).enhance(1.4)
        img = ImageEnhance.Brightness(img).enhance(0.85)

    elif emotion == "epic":
        # Dorado/naranja epico, alto contraste
        arr[:, :, 0] *= 1.15  # mas rojo/naranja
        arr[:, :, 1] *= 1.05
        arr[:, :, 2] *= 0.80  # menos azul
        arr = np.clip(arr, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8))
        img = ImageEnhance.Contrast(img).enhance(1.25)
        img = ImageEnhance.Color(img).enhance(1.2)

    elif emotion == "motivational":
        # Calido, brillante, energetico
        arr[:, :, 0] *= 1.1
        arr[:, :, 1] *= 1.05
        arr = np.clip(arr, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8))
        img = ImageEnhance.Brightness(img).enhance(1.1)
        img = ImageEnhance.Color(img).enhance(1.15)

    else:
        # Teal & Orange cinematografico (estandar cine)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.05, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.95, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8))
        img = ImageEnhance.Contrast(img).enhance(1.1)

    return img


# ─────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────

def _crop_to_tiktok(img: Image.Image, target_w: int = HD_W, target_h: int = HD_H) -> Image.Image:
    target_ratio = target_w / target_h
    w, h = img.size
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        img = img.crop(((w - new_w) // 2, 0, (w - new_w) // 2 + new_w, h))
    else:
        new_h = int(w / target_ratio)
        img = img.crop((0, (h - new_h) // 2, w, (h - new_h) // 2 + new_h))
    return img.resize((target_w, target_h), Image.LANCZOS)


def _dark_cinematic_placeholder(keyword: str, idx: int, job_id: str, fast_mode: bool) -> str:
    """Placeholder cinematografico oscuro con gradiente. SIEMPRE devuelve una imagen valida."""
    try:
        import numpy as np
        w, h = (FAST_W, FAST_H) if fast_mode else (540, 960)  # Usar resolucion base siempre
        arr = np.zeros((h, w, 3), dtype=np.uint8)

        palette = [(15, 8, 30), (8, 15, 30), (30, 8, 15), (8, 25, 20)]
        c = palette[idx % len(palette)]
        for y in range(h):
            ratio = y / h
            arr[y] = [
                min(255, int(c[0] + (c[0] * 1.5) * ratio)),
                min(255, int(c[1] + (c[1] * 1.5) * ratio)),
                min(255, int(c[2] + (c[2] * 1.5) * ratio)),
            ]

        img = Image.fromarray(arr, "RGB")
        try:
            draw = ImageDraw.Draw(img)
            # NO usar anchor="mm" — no funciona con la fuente por defecto de PIL
            words = keyword.upper()[:25]
            draw.text((w // 2 - 50, h // 2), words, fill=(160, 160, 160))
        except Exception:
            pass  # Si el texto falla, guardar la imagen sin texto igualmente

        out = f"outputs/media/{job_id}/img_{idx}.jpg"
        img.save(out, "JPEG", quality=85)
        print(f"[Placeholder] Creado fallback oscuro escena {idx}")
        return out
    except Exception as e:
        # Ultimo recurso absoluto: imagen negra pura
        print(f"[Placeholder] Error critico: {e}, creando imagen negra")
        w, h = 540, 960
        img = Image.new("RGB", (w, h), (10, 10, 10))
        out = f"outputs/media/{job_id}/img_{idx}.jpg"
        img.save(out, "JPEG")
        return out