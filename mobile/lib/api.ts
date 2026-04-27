import axios from 'axios'
import { API_BASE_URL } from './constants'

export interface VideoRequest {
  topic: string
  style: string
  audience: string
  duration: number
  language: string
  voice: string
  add_subtitles: boolean
  niche: string
}

export interface JobStatus {
  status: 'pending' | 'running' | 'completed' | 'error'
  progress: number
  message: string
  video_url?: string
  script?: { title: string; narration: string; hook?: string }
}

export interface VideoItem {
  filename: string
  url: string
  size_mb: number
}

function addInterceptor(instance: ReturnType<typeof axios.create>) {
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.code === 'ECONNABORTED') {
        return Promise.reject(
          new Error(
            'La solicitud tardó demasiado. Verifica tu conexión e intenta de nuevo.'
          )
        )
      }
      const detail = error.response?.data?.detail
      return Promise.reject(new Error(detail ?? error.message ?? 'Error desconocido'))
    }
  )
}

// Long timeout for video generation (5 min)
const generateApi = axios.create({ baseURL: API_BASE_URL, timeout: 300_000 })
addInterceptor(generateApi)

// Short timeout for all other requests (10s)
const api = axios.create({ baseURL: API_BASE_URL, timeout: 10_000 })
addInterceptor(api)

export async function generateVideo(data: VideoRequest): Promise<{ job_id: string }> {
  const res = await generateApi.post<{ job_id: string }>('/api/generate', data)
  return res.data
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const res = await api.get<JobStatus>(`/api/status/${jobId}`)
  return res.data
}

export async function listVideos(): Promise<{ videos: VideoItem[] }> {
  const res = await api.get<{ videos: VideoItem[] }>('/api/videos')
  return res.data
}

export async function deleteVideo(filename: string): Promise<void> {
  await api.delete(`/api/videos/${filename}`)
}

export function getVideoUrl(url: string): string {
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  const base = API_BASE_URL.replace(/\/$/, '')
  const path = url.startsWith('/') ? url : `/${url}`
  return `${base}${path}`
}
