"""
Sistema de autenticacion con SQLite + JWT
Campos: id, name, apellido, edad, email, password_hash, plan, created_at, videos_created
"""
import os, sqlite3, secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
DB_PATH = "users.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            apellido TEXT NOT NULL DEFAULT '',
            edad INTEGER NOT NULL DEFAULT 18,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            plan TEXT DEFAULT 'gratis',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            videos_created INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def create_user(name: str, apellido: str, edad: int, email: str, password: str) -> dict:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        hash_pw = pwd_context.hash(password)
        conn.execute(
            "INSERT INTO users (name, apellido, edad, email, password_hash) VALUES (?, ?, ?, ?, ?)",
            (name, apellido, int(edad), email.lower().strip(), hash_pw)
        )
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email.lower().strip(),)).fetchone()
        return _row_to_dict(user)
    except sqlite3.IntegrityError:
        raise ValueError("El email ya esta registrado")
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> dict:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    # id=0, name=1, apellido=2, edad=3, email=4, password_hash=5
    user = conn.execute("SELECT * FROM users WHERE email=?", (email.lower().strip(),)).fetchone()
    conn.close()
    if not user:
        raise ValueError("Email o contrasena incorrectos")
    password_hash = user[5]
    if not pwd_context.verify(password, password_hash):
        raise ValueError("Email o contrasena incorrectos")
    return _row_to_dict(user)


def create_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        init_db()
        conn = sqlite3.connect(DB_PATH)
        user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        conn.close()
        if not user:
            raise ValueError("Usuario no encontrado")
        return _row_to_dict(user)
    except JWTError:
        raise ValueError("Token invalido o expirado")


def increment_videos(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE users SET videos_created = videos_created + 1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def authenticate_biometric(biometric_id: str) -> dict:
    """Simulación de autenticación WebAuthn/Passkeys."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    # En producción 2026, buscaríamos por public_key_id
    user = conn.execute("SELECT * FROM users ORDER BY created_at ASC LIMIT 1").fetchone()
    conn.close()
    if not user:
        raise ValueError("No hay usuarios registrados para biometría")
    return _row_to_dict(user)


def _row_to_dict(row) -> dict:
    # id=0, name=1, apellido=2, edad=3, email=4, password_hash=5, plan=6, created_at=7, videos_created=8
    return {
        "id": row[0],
        "name": row[1],
        "apellido": row[2],
        "edad": row[3],
        "email": row[4],
        "plan": row[6],
        "created_at": row[7],
        "videos_created": row[8]
    }