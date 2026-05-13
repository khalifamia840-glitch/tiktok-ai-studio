"""
Media Service - Imagenes reales garantizadas
Orden: Pollinations (IA gratis) -> DALL-E 3 -> Pexels -> Pixabay -> Unsplash -> HuggingFace
"""
import os, io, asyncio, requests, urllib.parse
from PIL import Image, ImageDraw
import config

# Cache en memoria
_image_cache: dict = {}

TIKTOK_W, TIKTOK_H = 540, 960  # Resolucion reducida para plan gratuito de Render


async def fetch_media(keywords: list, duration: int, job_id: str) -> list:
    """Descarga todas las imagenes EN PARALELO."""
    os.makedirs(f"outputs/media/{job_id}", exist_ok=True)
    clips_needed = max(4, duration // 5)
    kws = list(keywords[:clips_needed])
    while len(kws) < clips_needed:
        kws.append(keywords[0] if keywords else "nature")

    # Descargar en paralelo
    tasks = [_get_image(kw, i, job_id) for i, kw in enumerate(kws)]
    paths = await asyncio.gather(*tasks)
    return list(paths)


async def _get_image(keyword: str, idx: int, job_id: str) -> str:
    """Obtiene imagen real. Pollinations primero (siempre funciona)."""
    loop = asyncio.get_event_loop()
    cache_key = keyword.lower().strip()[:40]

    # Cache hit
    if cache_key in _image_cache:
        cached = _image_cache[cache_key]
        if os.path.exists(cached):
            out = f"outputs/media/{job_id}/img_{idx}.jpg"
            try:
                import shutil; shutil.copy2(cached, out)
                return out
            except Exception:
                pass

    # 1. Pollinations.ai - GRATIS, sin API key, siempre disponible
    path = await loop.run_in_executor(None, _pollinations_image, keyword, idx, job_id)
    if path:
        _image_cache[cache_key] = path
        return path

    # 2. DALL-E 3
    if config.OPENAI_API_KEY and config.IMAGE_PROVIDER == "dalle":
        path = await loop.run_in_executor(None, _dalle_image, keyword, idx, job_id)
        if path:
            _image_cache[cache_key] = path
            return path

    # 3. Pexels
    if config.PEXELS_API_KEY:
        path = await loop.run_in_executor(None, _pexels_image, keyword, idx, job_id)
        if path:
            _image_cache[cache_key] = path
            return path

    # 4. Pixabay
    if config.PIXABAY_API_KEY:
        path = await loop.run_in_executor(None, _pixabay_image, keyword, idx, job_id)
        if path:
            _image_cache[cache_key] = path
            return path

    # 5. Unsplash (sin key)
    path = await loop.run_in_executor(None, _unsplash_image, keyword, idx, job_id)
    if path:
        return path

    # 6. HuggingFace
    if os.getenv("HF_TOKEN"):
        path = await loop.run_in_executor(None, _huggingface_image, keyword, idx, job_id)
        if path:
            return path

    # 7. Ultimo recurso - imagen oscura (no color solido)
    return _dark_placeholder(keyword, idx, job_id)


def _pollinations_image(keyword: str, idx: int, job_id: str) -> str | None:
    """Pollinations.ai - Flux model - GRATIS, sin API key."""
    try:
        prompt = f"cinematic vertical portrait photo {keyword}, TikTok 9:16, photorealistic, high quality, dramatic lighting, no text no watermark"
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=576&height=1024&model=flux&nologo=true&enhance=true&seed={idx}"
        r = requests.get(url, timeout=35, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 5000:
            img = Image.open(io.BytesIO(r.content)).convert("RGB")
            img = _crop_to_tiktok(img)
            out = f"outputs/media/{job_id}/img_{idx}.jpg"
            img.save(out, "JPEG", quality=88)
            print(f"[Pollinations] OK: {keyword}")
            return out
    except Exception as e:
        print(f"[Pollinations] Error: {e}")
    return None


def _dalle_image(keyword: str, idx: int, job_id: str) -> str | None:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        prompt = f"Cinematic vertical TikTok photo: {keyword}. 9:16, photorealistic, no text, dramatic lighting."
        response = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1792", quality="standard", n=1)
        img_data = requests.get(response.data[0].url, timeout=20).content
        img = Image.open(io.BytesIO(img_data)).convert("RGB")
        img = _crop_to_tiktok(img)
        out = f"outputs/media/{job_id}/img_{idx}.jpg"
        img.save(out, "JPEG", quality=90)
        print(f"[DALL-E 3] OK: {keyword}")
        return out
    except Exception as e:
        print(f"[DALL-E 3] Error: {e}")
    return None


def _pexels_image(keyword: str, idx: int, job_id: str) -> str | None:
    try:
        r = requests.get("https://api.pexels.com/v1/search",
            headers={"Authorization": config.PEXELS_API_KEY},
            params={"query": keyword, "per_page": 1, "orientation": "portrait"}, timeout=8)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                img_data = requests.get(photos[0]["src"]["large"], timeout=10).content
                img = Image.open(io.BytesIO(img_data)).convert("RGB")
                img = _crop_to_tiktok(img)
                out = f"outputs/media/{job_id}/img_{idx}.jpg"
                img.save(out, "JPEG", quality=88)
                return out
    except Exception as e:
        print(f"[Pexels] Error: {e}")
    return None


def _pixabay_image(keyword: str, idx: int, job_id: str) -> str | None:
    try:
        r = requests.get("https://pixabay.com/api/",
            params={"key": config.PIXABAY_API_KEY, "q": keyword, "image_type": "photo",
                    "orientation": "vertical", "per_page": 3, "safesearch": "true"}, timeout=8)
        if r.status_code == 200:
            hits = r.json().get("hits", [])
            if hits:
                img_data = requests.get(hits[0].get("largeImageURL", hits[0]["webformatURL"]), timeout=10).content
                img = Image.open(io.BytesIO(img_data)).convert("RGB")
                img = _crop_to_tiktok(img)
                out = f"outputs/media/{job_id}/img_{idx}.jpg"
                img.save(out, "JPEG", quality=88)
                return out
    except Exception as e:
        print(f"[Pixabay] Error: {e}")
    return None


def _unsplash_image(keyword: str, idx: int, job_id: str) -> str | None:
    try:
        clean = urllib.parse.quote(keyword.strip())
        # Usar un endpoint más estable de Unsplash Source o directo
        url = f"https://images.unsplash.com/photo-1?utm_source=tiktok-ai-studio&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=576&h=1024&fit=crop&sig={idx}&content={clean}"
        # Intentar también con el motor de búsqueda gratuito sin API key
        r = requests.get(f"https://unsplash.com/napi/search/photos?query={clean}&per_page=1", timeout=10)
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                url = results[0]["urls"]["regular"]
        
        img_data = requests.get(url, timeout=12).content
        if len(img_data) > 10000:
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            img = _crop_to_tiktok(img)
            out = f"outputs/media/{job_id}/img_{idx}.jpg"
            img.save(out, "JPEG", quality=85)
            print(f"[Unsplash] OK: {keyword}")
            return out
    except Exception as e:
        print(f"[Unsplash] Error: {e}")
    return None


def _huggingface_image(keyword: str, idx: int, job_id: str) -> str | None:
    try:
        hf_token = os.getenv("HF_TOKEN", "")
        if not hf_token:
            return None
        prompt = f"photorealistic vertical portrait photo {keyword}, TikTok style, cinematic"
        r = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers={"Authorization": f"Bearer {hf_token}"},
            json={"inputs": prompt, "parameters": {"width": 576, "height": 1024}},
            timeout=30)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
            img = Image.open(io.BytesIO(r.content)).convert("RGB")
            img = _crop_to_tiktok(img)
            out = f"outputs/media/{job_id}/img_{idx}.jpg"
            img.save(out, "JPEG", quality=88)
            print(f"[HuggingFace] OK: {keyword}")
            return out
    except Exception as e:
        print(f"[HuggingFace] Error: {e}")
    return None


def _crop_to_tiktok(img: Image.Image) -> Image.Image:
    target_ratio = TIKTOK_W / TIKTOK_H
    w, h = img.size
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        img = img.crop(((w - new_w) // 2, 0, (w - new_w) // 2 + new_w, h))
    else:
        new_h = int(w / target_ratio)
        img = img.crop((0, (h - new_h) // 2, w, (h - new_h) // 2 + new_h))
    return img.resize((TIKTOK_W, TIKTOK_H), Image.LANCZOS)


def _dark_placeholder(keyword: str, idx: int, job_id: str) -> str:
    """Imagen oscura con gradiente - NUNCA color solido brillante."""
    import numpy as np
    arr = np.zeros((TIKTOK_H, TIKTOK_W, 3), dtype=np.uint8)
    colors = [(20, 10, 40), (10, 20, 40), (40, 10, 20), (10, 40, 20)]
    c = colors[idx % len(colors)]
    for y in range(TIKTOK_H):
        ratio = y / TIKTOK_H
        arr[y] = [int(c[0] * (1 + ratio)), int(c[1] * (1 + ratio)), int(c[2] * (1 + ratio))]
    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img)
    draw.text((TIKTOK_W // 2, TIKTOK_H // 2), keyword.upper()[:25], fill=(200, 200, 200), anchor="mm")
    out = f"outputs/media/{job_id}/img_{idx}.jpg"
    img.save(out, "JPEG")
    return out