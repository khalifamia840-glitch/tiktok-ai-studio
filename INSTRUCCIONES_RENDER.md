# 🚀 Guía de Despliegue en Render (TikTok AI Studio)

He configurado un archivo `render.yaml` (Blueprint) que automatiza todo el proceso. Sigue estos pasos para subir tu aplicación a la nube:

## 1. Preparar el Repositorio
Asegúrate de que todos los cambios estén en tu repositorio de GitHub:
1. Sube el código a un repositorio (público o privado).
2. Verifica que el archivo `render.yaml` esté en la raíz.

## 2. Desplegar en Render
1. Ve a tu [Dashboard de Render](https://dashboard.render.com/).
2. Haz clic en **"New +"** y selecciona **"Blueprint"**.
3. Conecta tu repositorio de GitHub.
4. Render detectará automáticamente el archivo `render.yaml` y te mostrará los dos servicios:
   - `tiktok-ai-backend` (Servicio Web Docker)
   - `tiktok-ai-frontend` (Sitio Estático)

## 3. Configurar Variables de Entorno
Durante la creación del Blueprint, Render te pedirá que rellenes las variables de entorno. Debes poner tus API Keys:
- `GROQ_API_KEY`: Consíguela en [Groq Console](https://console.groq.com).
- `PEXELS_API_KEY`: Consíguela en [Pexels API](https://www.pexels.com/api/).
- `PIXABAY_API_KEY`: Consíguela en [Pixabay API](https://pixabay.com/api/docs/).
- `ELEVENLABS_API_KEY` (Opcional): Para voces ultra-reales.
- `OPENAI_API_KEY` (Opcional): Si prefieres usar GPT o DALL-E.

## 4. ¡Listo!
- Una vez configuradas, Render compilará ambos servicios.
- El frontend se conectará automáticamente al backend gracias a la variable vinculada `VITE_API_URL`.
- Podrás acceder a tu app desde la URL que te proporcione el servicio `tiktok-ai-frontend`.

---

### 💡 Notas Importantes
- **FFmpeg**: El backend ya incluye FFmpeg dentro del contenedor Docker, así que los videos se generarán sin problemas.
- **PWA**: Una vez desplegado, abre la URL en tu móvil y verás la opción de "Instalar App".
- **Plan Gratis**: El backend puede tardar unos segundos en "despertar" si no ha tenido uso reciente.
