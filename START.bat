@echo off
chcp 65001 > nul
echo.
echo  🚀 INICIANDO SERVIDORES LOCALES
echo  =================================
echo.

echo [*] Verificando backend...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -Method GET -UseBasicParsing -TimeoutSec 3; Write-Host '✅ Backend ya está corriendo' -ForegroundColor Green } catch { Write-Host '❌ Backend no responde, iniciando...' -ForegroundColor Red; exit 1 }" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Iniciando backend...
    start "Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    timeout /t 5 /nobreak > nul
)

echo [*] Verificando frontend...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5173' -Method GET -UseBasicParsing -TimeoutSec 3; Write-Host '✅ Frontend ya está corriendo' -ForegroundColor Green } catch { Write-Host '❌ Frontend no responde, iniciando...' -ForegroundColor Red; exit 1 }" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Iniciando frontend...
    start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
    timeout /t 3 /nobreak > nul
)

echo.
echo  🎉 ¡SERVIDORES INICIADOS!
echo  ===========================
echo.
echo  🌐 Frontend: http://localhost:5173
echo  🔧 Backend:  http://localhost:8000
echo.
echo  Presiona cualquier tecla para continuar...
pause > nul