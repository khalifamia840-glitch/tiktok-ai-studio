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
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import config
from services.prompt_engine import build_cinematic_prompt, build_style_prompt_batch

# Cache en memoria
_image_cache: dict = {}

# Resoluciones
FAST_W, FAST_H = 540, 960
HD_W, HD_H = 1080, 1920


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

    # Generar en paralelo
    tasks = [
        _get_image_cinematic(kws[i], prompt_data_list[i], i, job_id, fast_mode, upscaler)
        for i in range(clips_needed)
    ]
    paths = await asyncio.gather(*tasks)
    return list(paths)


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
) -> str:
    """Obtiene la mejor imagen posible para la escena con el prompt cinematografico."""
    loop = asyncio.get_event_loop()

    positive_prompt = prompt_data.get("positive", keyword)
    character_seed = prompt_data.get("character_seed", idx * 1000)

    # --- Cache key basado en el prompt + indice ---
    # Esto evita que escenas con prompts identicos repitan la misma imagen
    cache_key = hashlib.md5(f"{positive_prompt}_{idx}".encode()).hexdigest()[:16]
    if cache_key in _image_cache:
        cached = _image_cache[cache_key]
        if os.path.exists(cached):
            out = f"outputs/media/{job_id}/img_{idx}.jpg"
            try:
                import shutil; shutil.copy2(cached, out)
                return out
            except Exception:
                pass

    # --- FAST MODE: Pollinations Schnell ---
    if fast_mode:
        path = await loop.run_in_executor(
            None, _pollinations_schnell, positive_prompt, character_seed, idx, job_id
        )
        if path:
            _image_cache[cache_key] = path
            return path

    # --- CINEMATIC MODE ---
    # 1. Intentar Replicate (máxima calidad, si API key disponible)
    replicate_key = os.getenv("REPLICATE_API_KEY", "")
    if replicate_key and not fast_mode:
        path = await loop.run_in_executor(
            None, _replicate_flux_dev, positive_prompt, prompt_data.get("negative", ""), character_seed, idx, job_id
        )
        if path:
            path = _apply_upscale(path, upscaler, fast_mode)
            _image_cache[cache_key] = path
            return path

    # 2. HuggingFace FLUX Dev (gratis con token)
    hf_token = os.getenv("HF_TOKEN", "")
    if hf_token and not fast_mode:
        path = await loop.run_in_executor(
            None, _huggingface_flux_dev, positive_prompt, character_seed, idx, job_id, hf_token
        )
        if path:
            path = _apply_upscale(path, upscaler, fast_mode)
            _image_cache[cache_key] = path
            return path

    # 3. Pollinations FLUX Cinematic (gratuito, calidad HD)
    path = await loop.run_in_executor(
        None, _pollinations_cinematic, positive_prompt, character_seed, idx, job_id
    )
    if path:
        path = _apply_upscale(path, upscaler, fast_mode)
        _image_cache[cache_key] = path
        return path

    # 4. Fallback cinematografico oscuro
    return _dark_cinematic_placeholder(keyword, idx, job_id, fast_mode)


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
            f"?width=576&height=1024&model=flux&nologo=true&enhance=true&seed={seed}"
        )
        r = requests.get(url, timeout=45, allow_redirects=True)
        
        # Verificar que la respuesta sea realmente una imagen
        content_type = r.headers.get("content-type", "")
        is_image = content_type.startswith("image/") or len(r.content) > 15000
        
        if r.status_code == 200 and is_image:
            try:
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
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
        r = requests.get(url, timeout=25, allow_redirects=True)
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
        models = [
            "black-forest-labs/FLUX.1-dev",
            "stabilityai/stable-diffusion-xl-base-1.0",
        ]
        for model in models:
            r = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers={"Authorization": f"Bearer {hf_token}"},
                json={
                    "inputs": prompt,
                    "parameters": {
                        "width": 576,
                        "height": 1024,
                        "seed": seed,
                        "num_inference_steps": 28,
                    }
                },
                timeout=60,
            )
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
                img = _crop_to_tiktok(img, HD_W, HD_H)
                out = f"outputs/media/{job_id}/img_{idx}.jpg"
                img.save(out, "JPEG", quality=92)
                print(f"[HuggingFace FLUX] OK escena {idx}")
                return out
    except Exception as e:
        print(f"[HuggingFace FLUX] Error: {e}")
    return None


def _replicate_flux_dev(
    prompt: str, negative_prompt: str, seed: int, idx: int, job_id: str
) -> str | None:
    """
    Replicate API — FLUX Dev, Juggernaut XL, RealvisXL.
    Requiere REPLICATE_API_KEY en el entorno.
    """
    try:
        import replicate  # pip install replicate
        replicate_key = os.getenv("REPLICATE_API_KEY", "")
        client = replicate.Client(api_token=replicate_key)

        output = client.run(
            "black-forest-labs/flux-dev",
            input={
                "prompt": prompt,
                "width": 576,
                "height": 1024,
                "num_inference_steps": 28,
                "seed": seed,
                "guidance": 3.5,
            }
        )
        # El output es una URL o FileOutput
        if output:
            url = str(output[0]) if isinstance(output, list) else str(output)
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
                img = _crop_to_tiktok(img, HD_W, HD_H)
                out = f"outputs/media/{job_id}/img_{idx}.jpg"
                img.save(out, "JPEG", quality=95)
                print(f"[Replicate FLUX Dev] OK escena {idx}")
                return out
    except ImportError:
        print("[Replicate] Paquete 'replicate' no instalado. Ejecuta: pip install replicate")
    except Exception as e:
        print(f"[Replicate] Error: {e}")
    return None


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