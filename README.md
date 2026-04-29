# 🎬 TikTok AI Video Generator

Genera videos automáticos para TikTok, Instagram Reels y YouTube Shorts con IA.
Funciona en **Windows, macOS y Linux**. Accesible desde **iOS, Android y PC** via navegador.

## ✨ Características
- 🤖 Scripts con IA usando **Groq + Llama3** (GRATIS)
- 🎙️ Voz con **gTTS** o **Edge TTS** (GRATIS, voces naturales)
- 🖼️ Imágenes de **Pexels** (GRATIS) con fallback a imágenes generadas
- 🎬 Ensamblaje con **MoviePy + FFmpeg** (auto-descargado)
- 📝 Subtítulos automáticos (requiere ImageMagick, opcional)
- 📱 Formato vertical 1080x1920 (9:16) optimizado para TikTok
- 🌐 Web app PWA — funciona en iOS, Android y PC

## 🚀 Instalación Rápida

### Requisitos
- Python 3.11+
- Node.js 18+

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
copy .env.example .env
# Edita .env con tus API keys
start.bat
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

Abre **http://localhost:5173** en cualquier navegador.
Para acceder desde móvil: usa la IP de tu PC en la misma red WiFi.

## ⚙️ Ejecución y despliegue automático
- Localmente: usa `start-all.bat` desde la raíz para iniciar backend y frontend juntos.
- En la nube: conecta tu repo a Render y Vercel.
- En Vercel, configura `VITE_API_URL=https://<tu-backend-en-render>.onrender.com`.
- Para backend automático en Render, usa el workflow GitHub: `.github/workflows/render-deploy.yml`.
- Para frontend automático en Vercel, usa el workflow GitHub: `.github/workflows/vercel-deploy.yml`.
- Para validación automática de código, usa el workflow GitHub: `.github/workflows/ci.yml`.

Al hacer push a `main`, Render desplegará el backend automáticamente si defines estos secretos en GitHub:
- `RENDER_API_KEY`
- `RENDER_SERVICE_ID`

Y para desplegar el frontend automáticamente, define:
- `VERCEL_DEPLOY_HOOK_URL`

Si tu frontend está conectado por Git en Vercel, también se desplegará en cada push sin necesidad extra.

## Flujo automático completo
1. Push a `main` → GitHub Actions ejecuta `ci.yml`.
2. Si pasa la validación, `render-deploy.yml` dispara el deploy del backend en Render.
3. Si configuras el hook, `vercel-deploy.yml` dispara el deploy del frontend en Vercel.
4. El frontend usa `VITE_API_URL` para conectarse al backend en la nube.

## 🔑 API Keys (todas GRATIS)

| API | Uso | Link |
|-----|-----|------|
| Groq | Generación de scripts (Llama3) | https://console.groq.com |
| Pexels | Imágenes y videos | https://www.pexels.com/api |

## 📁 Estructura
```
tiktok-ai-generator/
├── backend/          # Python FastAPI
│   ├── main.py
│   ├── config.py
│   ├── services/
│   │   ├── script_service.py
│   │   ├── tts_service.py
│   │   ├── media_service.py
│   │   └── video_service.py
│   └── outputs/
└── frontend/         # React + Vite (PWA)
    └── src/
        ├── App.jsx
        ├── pages/
        └── components/
```
