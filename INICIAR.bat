@echo off
title TikTok AI Studio

if not exist "C:\Users\ra\Desktop\tiktok-ai-generator\backend\.env" (
    copy "C:\Users\ra\Desktop\tiktok-ai-generator\backend\.env.example" "C:\Users\ra\Desktop\tiktok-ai-generator\backend\.env" >nul
)

echo Iniciando Backend...
start /min "Backend" cmd /c "cd /d C:\Users\ra\Desktop\tiktok-ai-generator\backend && uvicorn main:app --host 0.0.0.0 --port 8000"

echo Iniciando Frontend sin cache...
timeout /t 2 /nobreak >nul
start /min "Frontend" cmd /c "python C:\Users\ra\Desktop\tiktok-ai-generator\server.py"

echo Esperando...
timeout /t 4 /nobreak >nul

start http://localhost:5173/tiktok-video-generator/