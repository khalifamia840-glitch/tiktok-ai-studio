/**
 * Cliente API para el backend
 * Soporta autenticación y múltiples funciones
 */
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // 60s timeout para procesos largos
})

// Interceptor para agregar token si existe
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor para logs de error globales
api.interceptors.response.use(
  response => response,
  error => {
    console.error("🌐 API ERROR:", {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data
    })
    return Promise.reject(error)
  }
)

// --- AUTH ---
export const login = (email, password) => 
  api.post('/api/auth/login', { email, password }).then(r => r.data)

export const register = (data) => 
  api.post('/api/auth/register', data).then(r => r.data)

// --- VIDEO GENERATION ---
export const generateVideo = (data) =>
  api.post('/api/generate', data).then(r => r.data)

export const getJobStatus = (jobId) =>
  api.get(`/api/status/${jobId}`).then(r => r.data)

// --- LIBRARY & TRENDING ---
export const listVideos = () =>
  api.get('/api/videos').then(r => r.data)

export const deleteVideo = (filename) =>
  api.delete(`/api/videos/${filename}`).then(r => r.data)

export const getTrending = () =>
  api.get('/api/trending').then(r => r.data)

// --- UTILS ---
export const getVideoUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${API_BASE}${url}`
}

export default api
