@echo off
cd /d "%~dp0"
chcp 65001 > nul
echo ========================================
echo  TikTok AI Video Generator - Backend
echo ========================================
echo.
if not exist ".env" (
    copy .env.example .env
    echo [!] Archivo .env creado.
    echo     Edita las API keys antes de continuar:
    echo     - GROQ_API_KEY  : https://console.groq.com  (GRATIS)
    echo     - PEXELS_API_KEY: https://www.pexels.com/api (GRATIS)
    echo.
    pause
)
echo [*] Instalando dependencias Python...
pip install -r requirements.txt
echo.
echo [*] Servidor iniciado en http://localhost:8000
echo [*] Documentacion API: http://localhost:8000/docs
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
