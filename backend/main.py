# -*- coding: utf-8 -*-
"""
TikTok AI Video Generator - FastAPI Backend
Funciona en Windows, macOS y Linux
"""
import os, uuid, asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from cloud_service import save_to_cloud
from jobs_db import create_job, update_job, get_job, get_all_jobs, save_video_stats, get_trending_topics
from auth import create_user, authenticate_user, create_token, verify_token
from fastapi import Header

load_dotenv()

# Importar orquestador principal
from video_generator import generate_video as _generate_video

app = FastAPI(title="TikTok AI Video Generator", version="1.0.0")

# CORS abierto - permite acceso desde web, iOS (PWA) y Android (PWA)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir videos generados como archivos estaticos
os.makedirs("outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Estado de trabajos en memoria (en produccion usar Redis/DB)
jobs: dict = {}


class VideoRequest(BaseModel):
    topic: str
    style: str = "entretenido"
    audience: str = "general"
    duration: int = 30          # segundos: 15, 30 o 60
    language: str = "es"        # es | en
    voice: str = "gtts"         # gtts | edge
    add_subtitles: bool = True
    niche: str = "general"


# ===== AUTH ENDPOINTS =====

class RegisterRequest(BaseModel):
    name: str
    apellido: str
    edad: int
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="La contrasena debe tener al menos 6 caracteres")
    try:
        user = create_user(req.name, req.apellido, req.edad, req.email, req.password)
        token = create_token(user["id"])
        return {"token": token, "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
def login(req: LoginRequest):
    try:
        user = authenticate_user(req.email, req.password)
        token = create_token(user["id"])
        return {"token": token, "user": user}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/api/auth/me")
def get_me(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autenticado")
    try:
        user = verify_token(authorization.replace("Bearer ", ""))
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/")
def root():
    return {"status": "ok", "message": "TikTok AI Video Generator API v1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/generate")
async def generate_video_endpoint(req: VideoRequest, background_tasks: BackgroundTasks, authorization: str = Header(None)):
    is_premium = False
    if authorization and authorization.startswith("Bearer "):
        try:
            user = verify_token(authorization.replace("Bearer ", ""))
            if user:
                is_premium = True
                # Opcional: increment_videos(user["id"])
        except Exception:
            pass

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "progress": 0,
        "message": "Iniciando pipeline...",
        "video_url": None,
        "script": None,
        "is_premium": is_premium
    }
    background_tasks.add_task(run_pipeline, job_id, req, is_premium)
    return {"job_id": job_id}


@app.get("/api/status/{job_id}")
def get_status(job_id: str):
    # Buscar en memoria primero, luego en DB
    if job_id in jobs:
        return jobs[job_id]
    db_job = get_job(job_id)
    if db_job:
        return db_job
    raise HTTPException(status_code=404, detail="Job no encontrado")


@app.get("/api/videos")
def list_videos():
    videos = []
    if os.path.exists("outputs"):
        for f in sorted(os.listdir("outputs"), reverse=True):
            if f.endswith(".mp4"):
                videos.append({
                    "filename": f,
                    "url": f"/outputs/{f}",
                    "size_mb": round(os.path.getsize(f"outputs/{f}") / 1024 / 1024, 2),
                })
    return {"videos": videos}

class RetentionRequest(BaseModel):
    topic: str
    script: str

@app.post("/api/analyze-retention")
def analyze_retention(req: RetentionRequest):
    """
    Analiza un script y devuelve un puntaje de retencion viral estimado.
    En una implementacion completa, esto usaria un LLM para analizar el hook, pacing, etc.
    Por ahora retorna un valor calculado basado en longitud y palabras clave.
    """
    import random
    
    score = 70
    hook_strength = "Moderada"
    
    # Analisis muy basico
    if "pov" in req.topic.lower() or "secreto" in req.topic.lower():
        score += 15
        hook_strength = "Muy Fuerte"
        
    if len(req.script.split()) > 50:
        score += 5
        
    score = min(score + random.randint(-5, 10), 99)
    
    return {
        "score": score,
        "hook_strength": hook_strength,
        "metrics": [
            {"label": "Fuerza del Hook", "value": hook_strength},
            {"label": "Ritmo (Pacing)", "value": "Rápido" if score > 80 else "Normal"},
            {"label": "Retención Est.", "value": f"{min(85, score - 10)}%"}
        ]
    }

@app.get("/api/trending")
def get_trending():
    """Retorna los temas mas populares (sistema de aprendizaje)."""
    return {"trending": get_trending_topics(10)}


@app.get("/api/check-system")
def check_system():
    """Verifica el estado de las APIs y dependencias."""
    import config
    import subprocess
    
    warnings = config.validate()
    ffmpeg_ok = False
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True)
        ffmpeg_ok = True
    except Exception:
        pass
        
    return {
        "ffmpeg": "OK" if ffmpeg_ok else "ERROR (Instala FFmpeg)",
        "apis": {
            "groq": "CONFIGURADA" if config.GROQ_API_KEY else "FALTA",
            "pexels": "CONFIGURADA" if config.PEXELS_API_KEY else "FALTA",
            "pixabay": "CONFIGURADA" if config.PIXABAY_API_KEY else "FALTA",
            "openai": "CONFIGURADA" if config.OPENAI_API_KEY else "OPCIONAL",
        },
        "warnings": warnings,
        "status": "ready" if (config.GROQ_API_KEY or config.OPENAI_API_KEY) and ffmpeg_ok else "needs_config"
    }

@app.delete("/api/videos/cleanup")
def cleanup_old_videos():
    """Elimina videos de mas de 7 dias para liberar espacio."""
    import time
    deleted = 0
    if os.path.exists("outputs"):
        for f in os.listdir("outputs"):
            if f.endswith(".mp4"):
                path = f"outputs/{f}"
                age_days = (time.time() - os.path.getmtime(path)) / 86400
                if age_days > 7:
                    os.remove(path)
                    deleted += 1
    return {"deleted": deleted, "message": f"{deleted} videos eliminados"}
@app.delete("/api/videos/{filename}")
def delete_video(filename: str):
    filepath = f"outputs/{filename}"
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"message": "Video eliminado"}
    raise HTTPException(status_code=404, detail="Video no encontrado")


async def run_pipeline(job_id: str, req: VideoRequest, is_premium: bool = False):
    create_job(job_id)
    """Pipeline completo delegado a video_generator.generate_video()"""
    jobs[job_id].update({"status": "running", "progress": 10,
                          "message": "Iniciando pipeline de generacion..."})
    update_job(job_id, status="running", progress=10, message="Iniciando pipeline de generacion...")
    try:
        result = await _generate_video(
            topic=req.topic,
            duration=req.duration,
            language=req.language,
            voice=req.voice,
            niche=req.niche,
            style=req.style,
            audience=req.audience,
            add_subtitles=req.add_subtitles,
            is_premium=is_premium,
        )

        if result["success"]:
            video_path = result["output_path"]
            # Subir a Cloudinary si está configurado, sino usar URL local
            cloud_result = save_to_cloud(job_id, video_path, result.get("script", {}), req.topic)
            video_url = cloud_result["video_url"]
            # Si no hay URL de Cloudinary, usar ruta local
            if not video_url or video_url.startswith("/outputs/"):
                video_url = f"/outputs/{os.path.basename(video_path)}"
            save_video_stats(job_id, req.topic, req.style, req.niche, req.duration)
            jobs[job_id].update({
                "status": "completed",
                "progress": 100,
                "message": "Video listo para descargar",
                "video_url": video_url,
                "script": result.get("script"),
            })
            update_job(job_id, status="completed", progress=100, message="Video listo para descargar", video_url=video_url)
        else:
            error_msg = f"Error en etapa '{result.get('error_stage')}': {result.get('error_message')}"
            jobs[job_id].update({
                "status": "error",
                "progress": 0,
                "message": error_msg,
                "video_url": None,
                "script": result.get("script"),
            })
            update_job(job_id, status="error", progress=0, message=error_msg)

    except Exception as e:
        import traceback
        error_msg = f"Error inesperado: {str(e)}"
        jobs[job_id].update({
            "status": "error",
            "message": error_msg,
            "progress": 0,
            "traceback": traceback.format_exc(),
        })
        update_job(job_id, status="error", progress=0, message=error_msg)