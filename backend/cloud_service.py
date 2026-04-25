"""
Servicio de almacenamiento en la nube - Cloudinary (gratis 25GB)
Si no hay credenciales, guarda localmente.
"""
import os, json, sqlite3

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")


def upload_video(file_path: str, job_id: str) -> str | None:
    """Sube video a Cloudinary. Retorna URL publica o None si falla/no hay credenciales."""
    if not all([CLOUD_NAME, API_KEY, API_SECRET]):
        return None
    try:
        import cloudinary
        import cloudinary.uploader
        cloudinary.config(cloud_name=CLOUD_NAME, api_key=API_KEY, api_secret=API_SECRET)
        result = cloudinary.uploader.upload(
            file_path,
            resource_type="video",
            public_id=f"tiktok_videos/{job_id}",
            overwrite=True,
            transformation=[{"width": 1080, "height": 1920, "crop": "fill"}]
        )
        print(f"[Cloudinary] Video subido: {result['secure_url']}")
        return result["secure_url"]
    except Exception as e:
        print(f"[Cloudinary] Error: {e}")
        return None


def save_to_cloud(job_id: str, video_path: str, script: dict, topic: str) -> dict:
    """Sube video a Cloudinary y guarda metadatos en DB local.
    
    Retorna dict con video_url (Cloudinary si disponible, local como fallback).
    """
    cloud_url = upload_video(video_path, job_id)
    video_url = cloud_url if cloud_url else f"/outputs/{os.path.basename(video_path)}"

    try:
        conn = sqlite3.connect("cloud_storage.db")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cloud_videos (
                id TEXT PRIMARY KEY,
                topic TEXT,
                video_url TEXT,
                script TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(
            "INSERT OR REPLACE INTO cloud_videos (id, topic, video_url, script) VALUES (?,?,?,?)",
            (job_id, topic, video_url, json.dumps(script))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[CloudStorage] DB error: {e}")

    return {"video_url": video_url, "job_id": job_id}
