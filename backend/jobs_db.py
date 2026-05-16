"""
Cola de jobs persistente con SQLite.
Los jobs sobreviven reinicios del servidor.
"""
import sqlite3, json, os
from datetime import datetime

DB_PATH = "jobs.db"


def init_jobs_db(reset_running=False):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            message TEXT DEFAULT 'Iniciando...',
            video_url TEXT,
            script TEXT,
            scenes_json TEXT,
            error TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    if reset_running:
        conn.execute("""
            UPDATE jobs SET status='failed', message='Generación interrumpida por reinicio del servidor.'
            WHERE status IN ('running', 'pending')
        """)
    conn.commit()
    conn.close()


def create_job(job_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT OR REPLACE INTO jobs (id, status, progress, message) VALUES (?, 'pending', 0, 'Iniciando...')", (job_id,))
    conn.commit()
    conn.close()


def update_job(job_id: str, **kwargs):
    conn = sqlite3.connect(DB_PATH)
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [datetime.utcnow().isoformat(), job_id]
    conn.execute(f"UPDATE jobs SET {fields}, updated_at=? WHERE id=?", values)
    conn.commit()
    conn.close()


def get_job(job_id: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0], "status": row[1], "progress": row[2],
        "message": row[3], "video_url": row[4],
        "script": json.loads(row[5]) if row[5] else None,
        "scenes": json.loads(row[6]) if row[6] else [],
        "error": row[7], "created_at": row[8]
    }


def get_all_jobs(limit: int = 50) -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [{"id": r[0], "status": r[1], "progress": r[2], "message": r[3],
             "video_url": r[4], "created_at": r[7]} for r in rows]


def save_video_stats(job_id: str, topic: str, style: str, niche: str, duration: int):
    """Guarda estadisticas para el sistema de aprendizaje."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS video_stats (
            id TEXT PRIMARY KEY,
            topic TEXT, style TEXT, niche TEXT,
            duration INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0, downloads INTEGER DEFAULT 0
        )
    """)
    conn.execute("INSERT OR REPLACE INTO video_stats (id, topic, style, niche, duration) VALUES (?,?,?,?,?)",
                 (job_id, topic, style, niche, duration))
    conn.commit()
    conn.close()


def get_trending_topics(limit: int = 10) -> list:
    """Retorna los temas mas generados (sistema de aprendizaje)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("""
            SELECT topic, style, niche, COUNT(*) as count
            FROM video_stats
            GROUP BY topic, style, niche
            ORDER BY count DESC
            LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return [{"topic": r[0], "style": r[1], "niche": r[2], "count": r[3]} for r in rows]
    except Exception:
        return []