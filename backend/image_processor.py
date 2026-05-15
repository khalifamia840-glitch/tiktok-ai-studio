"""
Image Processor — Validación y Normalización Profesional
=========================================================
Garantiza que TODAS las imágenes sean JPEG válidos antes del ensamblado.

Resuelve:
  - WEBP / PNG / RGBA → convierte a RGB JPEG
  - Imágenes corruptas → retry + fallback
  - Imágenes vacías (0KB) → detecta y regenera
  - Progressive JPEG → convierte a baseline JPEG
  - Animated WEBP → toma el primer frame
  - Imágenes de tamaño incorrecto → resize forzado
  - Logs detallados de cada imagen procesada
"""
import os
import io
import logging
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)

# Resolución TikTok
TIKTOK_W = 540
TIKTOK_H = 960


# ─────────────────────────────────────────────
# VALIDACIÓN
# ─────────────────────────────────────────────

def validate_image(path: str) -> bool:
    """
    Verifica si un archivo de imagen es válido y legible.
    Comprobaciones: existe, > 0 bytes, PIL puede abrirla y verificarla.
    """
    if not path:
        return False
    if not os.path.exists(path):
        logger.warning("[Validate] No existe: %s", path)
        return False
    if os.path.getsize(path) == 0:
        logger.warning("[Validate] Archivo vacío (0 bytes): %s", path)
        return False

    try:
        with Image.open(path) as img:
            img.verify()  # Comprueba integridad sin decodificar del todo
        return True
    except Exception as e:
        logger.warning("[Validate] Imagen corrupta %s: %s", path, e)
        return False


def get_image_info(path: str) -> dict:
    """Devuelve metadatos de la imagen para logging detallado."""
    info = {"path": path, "exists": False, "size_kb": 0, "format": None, "mode": None, "dimensions": None}
    try:
        if os.path.exists(path):
            info["exists"] = True
            info["size_kb"] = os.path.getsize(path) // 1024
            with Image.open(path) as img:
                info["format"] = img.format
                info["mode"] = img.mode
                info["dimensions"] = img.size
    except Exception:
        pass
    return info


# ─────────────────────────────────────────────
# NORMALIZACIÓN
# ─────────────────────────────────────────────

def normalize_image(
    source_path: str,
    output_path: str,
    target_w: int = TIKTOK_W,
    target_h: int = TIKTOK_H,
) -> str | None:
    """
    Normaliza CUALQUIER imagen al formato JPEG válido para MoviePy/FFmpeg.

    Maneja:
      - WEBP (incluyendo animated) → primer frame RGB
      - PNG con transparencia (RGBA) → fondo negro + RGB
      - Progressive JPEG → baseline JPEG
      - Imágenes en modo incorrecto (L, P, CMYK) → RGB
      - Resize automático al aspect ratio 9:16 TikTok

    Returns:
        output_path si éxito, None si fallo total.
    """
    try:
        info = get_image_info(source_path)
        logger.info(
            "[Normalize] Procesando: formato=%s, modo=%s, dims=%s, tamaño=%dKB — %s",
            info["format"], info["mode"], info["dimensions"], info["size_kb"], source_path
        )

        with Image.open(source_path) as img:
            # Manejar imágenes animadas (WEBP, GIF) → primer frame
            try:
                img.seek(0)
            except (AttributeError, EOFError):
                pass

            # Convertir SIEMPRE a RGB (elimina transparencias, canales extra, etc.)
            if img.mode == "RGBA":
                # Componer sobre fondo negro para transparencias
                background = Image.new("RGB", img.size, (0, 0, 0))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode == "P":
                img = img.convert("RGBA").convert("RGB")
            elif img.mode == "CMYK":
                img = img.convert("RGB")
            elif img.mode == "L":
                img = img.convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Resize al formato TikTok 9:16
            img = _crop_and_resize(img, target_w, target_h)

            # Guardar como JPEG baseline (no progressive) — FFmpeg compatible
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, "JPEG", quality=88, optimize=False, progressive=False)

        # Verificar que el archivo guardado es válido
        if validate_image(output_path):
            logger.info("[Normalize] ✅ OK: %s (%dKB)", output_path, os.path.getsize(output_path) // 1024)
            return output_path
        else:
            logger.error("[Normalize] ❌ El archivo guardado no pasó validación: %s", output_path)
            return None

    except Exception as e:
        logger.error("[Normalize] ❌ Error procesando %s: %s", source_path, e)
        return None


def _crop_and_resize(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Recorta al centro y redimensiona a la resolución objetivo manteniendo el ratio."""
    target_ratio = target_w / target_h
    w, h = img.size

    # Evitar imágenes de 1x1 o dimensiones inválidas
    if w <= 1 or h <= 1:
        return Image.new("RGB", (target_w, target_h), (10, 10, 10))

    current_ratio = w / h
    if abs(current_ratio - target_ratio) > 0.01:
        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))

    return img.resize((target_w, target_h), Image.LANCZOS)


# ─────────────────────────────────────────────
# SISTEMA DE FALLBACK
# ─────────────────────────────────────────────

def create_fallback_image(output_path: str, idx: int = 0, label: str = "") -> str:
    """
    Crea una imagen de fallback cinematográfica oscura.
    Garantizado que siempre funciona — sin dependencias externas.
    """
    try:
        w, h = TIKTOK_W, TIKTOK_H
        # Gradiente oscuro cinético según índice
        palettes = [
            ((15, 8, 30), (40, 20, 80)),   # púrpura oscuro
            ((8, 15, 30), (20, 40, 80)),   # azul oscuro
            ((30, 8, 15), (80, 20, 40)),   # rojo oscuro
            ((8, 25, 20), (20, 60, 50)),   # verde oscuro
        ]
        top_col, bottom_col = palettes[idx % len(palettes)]

        img = Image.new("RGB", (w, h))
        pixels = img.load()
        for y in range(h):
            ratio = y / h
            r = int(top_col[0] + (bottom_col[0] - top_col[0]) * ratio)
            g = int(top_col[1] + (bottom_col[1] - top_col[1]) * ratio)
            b = int(top_col[2] + (bottom_col[2] - top_col[2]) * ratio)
            for x in range(w):
                pixels[x, y] = (r, g, b)

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        img.save(output_path, "JPEG", quality=85, progressive=False)
        logger.info("[Fallback] Imagen de emergencia creada: %s", output_path)
        return output_path

    except Exception as e:
        # Último recurso absoluto: PIL puro
        logger.error("[Fallback] Error crítico: %s — usando Image.new", e)
        img = Image.new("RGB", (TIKTOK_W, TIKTOK_H), (10, 5, 20))
        img.save(output_path, "JPEG")
        return output_path


# ─────────────────────────────────────────────
# NORMALIZACIÓN EN LOTE CON RETRY
# ─────────────────────────────────────────────

def normalize_batch(
    source_paths: list[str],
    output_dir: str,
    job_id: str,
    max_retries: int = 2,
) -> list[str]:
    """
    Normaliza una lista de imágenes a JPEG válidos.
    
    Por cada imagen:
      1. Valida que existe y no está vacía
      2. Normaliza (convert, resize, save JPEG)
      3. Valida el resultado
      4. Si falla, usa fallback cinematográfico
    
    SIEMPRE devuelve una lista del mismo tamaño que source_paths.
    Nunca devuelve None ni entradas vacías.
    """
    os.makedirs(output_dir, exist_ok=True)
    results: list[str] = []

    for idx, src in enumerate(source_paths):
        out_path = os.path.join(output_dir, f"normalized_{idx:03d}.jpg")
        success = False

        # Intento de normalización con retry
        for attempt in range(max_retries + 1):
            if not validate_image(src):
                logger.warning(
                    "[Batch] Escena %d/%d: imagen inválida (intento %d/%d): %s",
                    idx + 1, len(source_paths), attempt + 1, max_retries + 1, src
                )
                break  # Si no existe/vacía, no tiene sentido reintentar

            result = normalize_image(src, out_path)
            if result and validate_image(result):
                results.append(result)
                success = True
                logger.info(
                    "[Batch] ✅ Escena %d/%d OK (intento %d)",
                    idx + 1, len(source_paths), attempt + 1
                )
                break
            else:
                logger.warning(
                    "[Batch] Escena %d/%d falló normalización (intento %d/%d)",
                    idx + 1, len(source_paths), attempt + 1, max_retries + 1
                )

        if not success:
            logger.error(
                "[Batch] ❌ Escena %d/%d: usando fallback cinematográfico",
                idx + 1, len(source_paths)
            )
            fallback_path = os.path.join(output_dir, f"fallback_{idx:03d}.jpg")
            create_fallback_image(fallback_path, idx=idx)
            results.append(fallback_path)

    logger.info(
        "[Batch] Normalización completada: %d/%d imágenes procesadas para job %s",
        len(results), len(source_paths), job_id
    )
    return results
