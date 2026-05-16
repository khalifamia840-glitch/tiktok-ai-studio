import os
import requests
import json
import asyncio
from PIL import Image
import io


def generate_veo_3_image(prompt: str, seed: int = 42) -> bytes | None:
    """
    Integración con Google AI Studio para generación de imágenes con Imagen 3.
    Usa la API REST real de Google AI Studio (generativelanguage.googleapis.com).
    Fallback: Imagen 3 Flash si el modelo principal falla.
    """
    api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
    if not api_key:
        print("[Google AI Studio] ERROR: No se encontró GOOGLE_AI_STUDIO_KEY")
        return None

    # Modelos de imagen disponibles en Google AI Studio (en orden de preferencia)
    models_to_try = [
        "imagen-3.0-generate-002",
        "imagen-3.0-fast-generate-001",
    ]

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "instances": [
                {
                    "prompt": prompt[:900],  # Límite seguro de caracteres
                }
            ],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "9:16",
                "safetyFilterLevel": "BLOCK_ONLY_HIGH",
                "personGeneration": "ALLOW_ADULT",
            }
        }

        try:
            print(f"[Google AI Studio] Intentando modelo: {model}")
            r = requests.post(url, headers=headers, json=payload, timeout=45)

            if r.status_code == 200:
                response_json = r.json()
                # La respuesta trae base64 en predictions[0].bytesBase64Encoded
                predictions = response_json.get("predictions", [])
                if predictions:
                    import base64
                    b64_data = predictions[0].get("bytesBase64Encoded", "")
                    if b64_data:
                        image_bytes = base64.b64decode(b64_data)
                        print(f"[Google AI Studio] Imagen generada con {model} ({len(image_bytes)//1024}KB)")
                        return image_bytes
                print(f"[Google AI Studio] Warning: Respuesta sin imagen con {model}: {response_json}")
            else:
                error_info = ""
                try:
                    error_info = r.json().get("error", {}).get("message", r.text[:200])
                except Exception:
                    error_info = r.text[:200]
                print(f"[Google AI Studio] Error: {model} -> HTTP {r.status_code}: {error_info}")

        except requests.exceptions.Timeout:
            print(f"[Google AI Studio] Timeout con {model}, probando siguiente...")
        except Exception as e:
            print(f"[Google AI Studio] Excepcion con {model}: {e}")

    print("[Google AI Studio] Todos los modelos fallaron, usando fallback Pollinations.")
    return None


async def generate_veo_3_async(prompt: str, seed: int = 42):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_veo_3_image, prompt, seed)
