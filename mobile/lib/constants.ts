export const COLORS = {
  background: '#010101',
  primary: '#fe2c55',
  secondary: '#25f4ee',
  textPrimary: '#ffffff',
  textSecondary: '#aaaaaa',
  cardBg: '#1a1a1a',
  border: '#2a2a2a',
  tabInactive: '#555555',
  tabBorder: '#1a1a1a',
} as const

export const STYLES_OPTIONS = [
  { value: 'entretenido', label: 'Entretenido' },
  { value: 'educativo', label: 'Educativo' },
  { value: 'motivacional', label: 'Motivacional' },
  { value: 'humor', label: 'Humor' },
  { value: 'misterio', label: 'Misterio' },
  { value: 'viral', label: 'Viral' },
]

export const NICHE_OPTIONS = [
  { value: 'general', label: 'General' },
  { value: 'fitness', label: 'Fitness' },
  { value: 'tecnologia', label: 'Tecnología' },
  { value: 'negocios', label: 'Negocios' },
  { value: 'humor', label: 'Humor' },
  { value: 'educacion', label: 'Educación' },
  { value: 'lifestyle', label: 'Lifestyle' },
  { value: 'salud', label: 'Salud' },
  { value: 'viajes', label: 'Viajes' },
  { value: 'cocina', label: 'Cocina' },
]

export const DURATION_OPTIONS = [
  { value: 15, label: '15s' },
  { value: 30, label: '30s' },
  { value: 60, label: '60s' },
]

export const VOICE_OPTIONS = [
  { value: 'edge', label: 'Edge TTS' },
  { value: 'gtts', label: 'Google TTS' },
]

export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ?? 'https://tiktok-ai-studio.onrender.com'
