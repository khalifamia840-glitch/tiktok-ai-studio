/**
 * Cliente API para el backend
 * Detecta automáticamente si estamos en desarrollo o producción
 */
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'https://tiktok-ai-studio.onrender.com'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 0, // sin timeout — la generación puede tardar varios minutos
})

export const generateVideo = (data) =>
  api.post('/api/generate', data).then(r => r.data)

export const getJobStatus = (jobId) =>
  api.get(`/api/status/${jobId}`).then(r => r.data)

export const listVideos = () =>
  api.get('/api/videos').then(r => r.data)

export const deleteVideo = (filename) =>
  api.delete(`/api/videos/${filename}`).then(r => r.data)

// Soporta URLs absolutas (Cloudinary) y relativas (local)
export const getVideoUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  return `${API_BASE}${url}`
}
