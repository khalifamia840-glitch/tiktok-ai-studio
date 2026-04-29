@echo off
chcp 65001 > nul
echo.
echo  ============================================
echo   AUTO TIKTOK AI - Arreglando todo
echo  ============================================
echo.

echo [*] Verificando backend...
cd /d "%~dp0backend"
if not exist ".env" (
    copy .env.example .env
    echo [!] Archivo .env creado en backend.
    echo     Edita las API keys antes de continuar.
    pause
)

echo [*] Instalando dependencias backend...
pip install -r requirements.txt

echo [*] Iniciando backend...
start "Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo [*] Esperando backend...
timeout /t 3 /nobreak > nul

echo [*] Verificando frontend...
cd /d "%~dp0frontend"

echo [*] Limpiando dependencias frontend...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json

echo [*] Instalando dependencias frontend...
call npm install

echo [*] Iniciando frontend...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo  ============================================
echo   ¡TODO LISTO!
echo  ============================================
echo.
echo  🌐 Frontend: http://localhost:5173
echo  🔧 Backend:  http://localhost:8000
echo.
echo  Presiona cualquier tecla para continuar...
pause > nul