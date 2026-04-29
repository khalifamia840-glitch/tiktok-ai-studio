@echo off
echo ============================================
echo  🔍 VERIFICACIÓN COMPLETA PARA LA NUBE
echo ============================================
echo.

echo 📋 VERIFICANDO ARCHIVOS DE CONFIGURACIÓN...
echo.

if exist "render.yaml" (
    echo ✅ render.yaml encontrado
) else (
    echo ❌ render.yaml NO encontrado
)

if exist "frontend\vercel.json" (
    echo ✅ frontend/vercel.json encontrado
) else (
    echo ❌ frontend/vercel.json NO encontrado
)

if exist ".github\workflows\ci.yml" (
    echo ✅ CI workflow encontrado
) else (
    echo ❌ CI workflow NO encontrado
)

if exist ".github\workflows\render-deploy.yml" (
    echo ✅ Render deploy workflow encontrado
) else (
    echo ❌ Render deploy workflow NO encontrado
)

if exist ".github\workflows\vercel-deploy.yml" (
    echo ✅ Vercel deploy workflow encontrado
) else (
    echo ❌ Vercel deploy workflow NO encontrado
)

if exist "backend\Dockerfile" (
    echo ✅ Dockerfile del backend encontrado
) else (
    echo ❌ Dockerfile del backend NO encontrado
)

echo.
echo 🔧 VERIFICANDO DEPENDENCIAS...
echo.

echo [*] Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python instalado
) else (
    echo ❌ Python NO instalado
)

echo [*] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js instalado
) else (
    echo ❌ Node.js NO instalado
)

echo [*] Verificando npm...
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ npm instalado
) else (
    echo ❌ npm NO instalado
)

echo.
echo 🚀 VERIFICANDO BUILDS...
echo.

echo [*] Verificando build del frontend...
cd frontend
if exist "node_modules" (
    echo ✅ node_modules existe
    npm run build >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Frontend build exitoso
    ) else (
        echo ❌ Error en build del frontend
    )
) else (
    echo ❌ node_modules NO existe - ejecutar npm install
)
cd ..

echo.
echo 📦 VERIFICANDO BACKEND...
echo.

cd backend
python -c "import fastapi, uvicorn; print('✅ Dependencias del backend OK')" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Backend dependencies OK
) else (
    echo ❌ Error en dependencias del backend
)
cd ..

echo.
echo 🔑 VARIABLES DE ENTORNO REQUERIDAS:
echo.
echo Para Render (Backend):
echo   - GROQ_API_KEY
echo   - PEXELS_API_KEY
echo   - ELEVENLABS_API_KEY
echo   - ELEVENLABS_VOICE_ID
echo   - CLOUDINARY_CLOUD_NAME
echo   - CLOUDINARY_API_KEY
echo   - CLOUDINARY_API_SECRET
echo.
echo Para Vercel (Frontend):
echo   - VITE_API_URL (URL del backend en Render)
echo.
echo Para GitHub Secrets:
echo   - RENDER_API_KEY
echo   - RENDER_SERVICE_ID
echo   - VERCEL_DEPLOY_HOOK_URL
echo.

echo ============================================
echo  🎉 VERIFICACIÓN COMPLETA
echo ============================================
echo.
echo Si todo está ✅, tu app está lista para la nube!
echo.
echo Pasos finales:
echo 1. Configurar secrets en GitHub
echo 2. Hacer push a main
echo 3. Los despliegues serán automáticos
echo.

pause