@echo off
chcp 65001 > nul
echo.
echo  ============================================
echo   AUTO TIKTOK AI - Iniciando todo
echo  ============================================
echo.
start "Backend" cmd /k "cd /d %~dp0backend && start.bat"
timeout /t 4 /nobreak > nul
start "Frontend" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"
echo.
echo  Abre en tu navegador: http://localhost:5173
echo  Desde movil (misma WiFi): usa la IP de tu PC
echo.
pause
