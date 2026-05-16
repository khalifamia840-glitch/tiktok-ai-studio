@echo off
cd /d "%~dp0"
echo ========================================
echo  TikTok AI Studio - Frontend Server
echo ========================================
echo.
echo [*] Instalando dependencias (por si acaso)...
call npm install
echo.
echo [*] Iniciando servidor de desarrollo...
echo [*] Abre tu navegador en: http://localhost:5173
echo.
npm run dev
