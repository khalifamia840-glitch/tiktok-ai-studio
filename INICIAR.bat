@echo off
title TikTok AI Studio

if not exist "%~dp0backend\.env" (
    copy "%~dp0backend\.env.example" "%~dp0backend\.env" >nul
)

echo Iniciando Backend...
start /min "Backend" cmd /c "cd /d %~dp0backend && uvicorn main:app --host 0.0.0.0 --port 8000"

echo Iniciando Frontend sin cache...
timeout /t 2 /nobreak >nul
start /min "Frontend" cmd /c "python %~dp0server.py"

echo Esperando...
timeout /t 4 /nobreak >nul

start http://localhost:5173/