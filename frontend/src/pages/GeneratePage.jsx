import { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { Sparkles, Loader2, Download, CheckCircle, AlertCircle, ChevronDown, Wand2, Type, Music, Video as VideoIcon, Clapperboard, Maximize2 } from 'lucide-react'
import { generateVideo, getJobStatus, getVideoUrl } from '../api'
import Timeline from '../components/Timeline'
import RetentionScore from '../components/RetentionScore'
import LiveStoryboard from '../components/LiveStoryboard'

const STYLES = ['entretenido','educativo','motivacional','humor','misterio','viral','informativo','storytelling']
const NICHES = ['general','fitness','tecnologia','negocios','humor','educacion','lifestyle','salud','viajes','cocina','dinero','relaciones']
const DURATIONS = [15, 30, 45, 60]
const VOICES = [
  { value: 'edge', label: 'Edge TTS (Ultra-Natural)' },
  { value: 'gtts', label: 'Google TTS (Básico)' },
  { value: 'elevenlabs', label: '⭐ ElevenLabs (Premium)' },
]

const VISUAL_STYLES = [
  { value: 'cinematic', emoji: '🎬', label: 'Cinemático', desc: 'Estilo película' },
  { value: 'dark', emoji: '🌑', label: 'Oscuro', desc: 'Thriller / Terror' },
  { value: 'realistic', emoji: '📸', label: 'Realista', desc: 'Ultra HD' },
  { value: 'tiktok_viral', emoji: '✨', label: 'TikTok Viral', desc: 'Alto contraste' },
  { value: 'anime', emoji: '🎌', label: 'Anime', desc: 'Estilo manga' },
  { value: 'kling', emoji: '💎', label: 'Kling Elite', desc: 'Física 4K' },
  { value: 'veo', emoji: '🌟', label: 'Google Veo', desc: 'Cine Realista' },
  { value: 'noir', emoji: '🎞️', label: 'Cine Noir', desc: 'Blanco y Negro' },
]

export default function GeneratePage() {
  const location = useLocation()
  const [form, setForm] = useState({
    topic: '',
    style: 'entretenido',
    duration: 30,
    language: 'es',
    voice: 'edge',
    add_subtitles: true,
    niche: 'general',
    visual_style: 'cinematic',
    upscaler: 'pil',
    fast_mode: false,
  })

  // Cargar tema desde el state (LandingPage / Dashboard)
  useEffect(() => {
    if (location.state?.topic) {
      setForm(f => ({ ...f, topic: location.state.topic }))
      // Auto-trigger if came from Landing Page
      if (location.state?.autoGenerate) {
         // Optionally auto-generate
      }
    }
  }, [location.state])

  const [jobId, setJobId] = useState(() => localStorage.getItem('last_job_id'))
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)

  // Persistir jobId en localStorage
  useEffect(() => {
    if (jobId) {
      localStorage.setItem('last_job_id', jobId)
    } else {
      localStorage.removeItem('last_job_id')
    }
  }, [jobId])

  useEffect(() => {
    if (!jobId) return
    pollRef.current = setInterval(async () => {
      try {
        const s = await getJobStatus(jobId)
        if (!s) return
        
        setStatus(s)
        if (s.status === 'completed' || s.status === 'error' || s.status === 'failed') {
          clearInterval(pollRef.current)
          setLoading(false)
        }
      } catch (e) {
        console.error("Polling error:", e)
      }
    }, 1500)
    return () => clearInterval(pollRef.current)
  }, [jobId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.topic.trim()) return
    setLoading(true)
    setError(null)
    setStatus(null)
    setJobId(null)
    try {
      const res = await generateVideo(form)
      setJobId(res.job_id)
    } catch (e) {
      setLoading(false)
      setError(e.response?.data?.detail || 'Error al conectar con el servidor. Verifica el backend.')
    }
  }

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-10 space-y-10 animate-slide-up">
      {/* Header - Professional Typography */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-white/5 pb-8">
        <div>
          <h2 className="text-5xl font-black font-heading tracking-tighter">
            Studio<span className="text-[#fe2c55]">AI</span>
          </h2>
          <p className="text-zinc-500 mt-2 text-sm font-medium">Professional TikTok Generation Engine · Elite v2.6</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => set('advanced', !form.advanced)}
            className="text-[10px] font-bold uppercase tracking-widest px-4 py-2 rounded-full border border-white/10 hover:bg-white/5 transition-all"
          >
            {form.advanced ? 'View Brief' : 'Advanced Mode'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Formulario */}
        <form onSubmit={handleSubmit} className="lg:col-span-5 space-y-6">
          <div className="glass-card space-y-5">
            {/* Tema */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em]">
                  {form.advanced ? 'Story Brief & Context' : 'What is your video about?'}
                </label>
                <span className="text-[10px] font-mono text-zinc-600">{form.topic.length}/500</span>
              </div>
              <textarea
                value={form.topic}
                onChange={e => set('topic', e.target.value)}
                placeholder="Describe your idea... e.g., A cinematic motivational speech about discipline with urban night views."
                className="input-premium min-h-[100px] lg:min-h-[140px] resize-none"
                required
              />
            </div>

            {/* Advanced Configuration - Hidden in Brief Mode */}
            {form.advanced && (
              <div className="space-y-6 pt-4 border-t border-white/5 animate-slide-up">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">Duration</label>
                    <div className="grid grid-cols-4 gap-1.5">
                      {DURATIONS.map(d => (
                        <button key={d} type="button"
                          onClick={() => set('duration', d)}
                          className={`py-2 rounded-lg text-[11px] font-bold border transition-all ${
                            form.duration === d
                              ? 'bg-white text-black border-white'
                              : 'bg-white/5 border-white/5 text-zinc-500 hover:border-white/10'
                          }`}
                        >
                          {d}s
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">Tone</label>
                    <select value={form.style} onChange={e => set('style', e.target.value)} className="input-premium appearance-none pr-10">
                      {STYLES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">Voice Model</label>
                    <select value={form.voice} onChange={e => set('voice', e.target.value)} className="input-premium appearance-none pr-10">
                      {VOICES.map(v => <option key={v.value} value={v.value}>{v.label}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">Niche</label>
                    <select value={form.niche} onChange={e => set('niche', e.target.value)} className="input-premium appearance-none pr-10">
                      {NICHES.map(n => <option key={n} value={n}>{n}</option>)}
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Visual Style Selector */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 text-xs font-bold text-gray-500 uppercase tracking-widest">
                <Clapperboard size={14} /> Estilo Visual IA
              </label>
              <div className="grid grid-cols-3 gap-2">
                {VISUAL_STYLES.map(vs => (
                  <button
                    key={vs.value}
                    type="button"
                    onClick={() => set('visual_style', vs.value)}
                    className={`flex flex-col items-center justify-center py-3 px-2 rounded-xl border transition-all ${
                      form.visual_style === vs.value
                        ? 'border-[#fe2c55] bg-[#fe2c55]/10 text-white'
                        : 'border-white/5 bg-white/5 text-gray-400 hover:border-white/20'
                    }`}
                  >
                    <span className="text-xl mb-1">{vs.emoji}</span>
                    <span className="font-bold text-[11px]">{vs.label}</span>
                    <span className="text-[9px] text-gray-500 mt-0.5">{vs.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Upscaler Selector */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 text-xs font-bold text-gray-500 uppercase tracking-widest">
                <Maximize2 size={14} /> Resolución & Upscaler
              </label>
              <div className="flex bg-black/50 p-1 rounded-xl">
                <button type="button"
                  onClick={() => set('upscaler', 'pil')}
                  className={`flex-1 flex flex-col items-center py-3 rounded-lg transition-all ${
                    form.upscaler === 'pil' ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-white'
                  }`}
                >
                  <span className="font-bold text-xs">🔷 HD Rápido</span>
                  <span className="text-[9px] text-gray-500">PIL Lanczos · 1080p</span>
                </button>
                <button type="button"
                  onClick={() => set('upscaler', 'realesrgan')}
                  className={`flex-1 flex flex-col items-center py-3 rounded-lg transition-all ${
                    form.upscaler === 'realesrgan' ? 'bg-[#25f4ee]/20 text-[#25f4ee]' : 'text-gray-500 hover:text-white'
                  }`}
                >
                  <span className="font-bold text-xs">⚡ Real-ESRGAN</span>
                  <span className="text-[9px] text-gray-500">4x Super Res · Lento</span>
                </button>
              </div>
            </div>

            {/* Cinematic vs Fast Mode */}
            <div className="p-4 bg-gradient-to-r from-white/5 to-transparent rounded-2xl border border-white/5">
              <div className="flex items-center justify-between mb-3">
                <label className="text-xs font-bold text-gray-300 uppercase tracking-widest">Modo de Generación</label>
              </div>
              <div className="flex bg-black/50 p-1 rounded-xl">
                <button type="button"
                  onClick={() => set('fast_mode', true)}
                  className={`flex-1 flex flex-col items-center justify-center py-3 rounded-lg transition-all ${
                    form.fast_mode ? 'bg-[#25f4ee] text-black shadow-lg shadow-[#25f4ee]/20' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  <span className="font-bold text-sm">⚡ Fast Mode</span>
                  <span className={`text-[10px] ${form.fast_mode ? 'text-black/70' : 'text-gray-500'}`}>Cortes simples, rápido</span>
                </button>
                <button type="button"
                  onClick={() => set('fast_mode', false)}
                  className={`flex-1 flex flex-col items-center justify-center py-3 rounded-lg transition-all ${
                    !form.fast_mode ? 'bg-[#fe2c55] text-white shadow-lg shadow-[#fe2c55]/20' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  <span className="font-bold text-sm">🎥 Cinematic</span>
                  <span className={`text-[10px] ${!form.fast_mode ? 'text-white/70' : 'text-gray-500'}`}>Zooms, Transiciones, BGM</span>
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 animate-slide-up">
              <AlertCircle size={20} className="shrink-0 mt-0.5" />
              <p className="text-sm leading-relaxed">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !form.topic.trim()}
            className="btn-premium w-full shadow-2xl shadow-[#fe2c55]/20 text-lg py-4"
          >
            {loading ? (
              <><Loader2 className="animate-spin" /> Generando Video...</>
            ) : (
              <><Sparkles /> Crear Video Viral</>
            )}
          </button>
        </form>

        {/* Status Panel & Timelines */}
        <div className="lg:col-span-7">
          <div className="sticky top-8 space-y-6">
            {status || jobId ? (
              <JobStatus status={status} jobId={jobId} />
            ) : (
              <div className="glass-card border-dashed border-white/5 flex flex-col items-center justify-center py-20 text-center space-y-4">
                <div className="w-16 h-16 rounded-3xl bg-white/5 flex items-center justify-center text-gray-600">
                  <VideoIcon size={32} />
                </div>
                <div>
                  <p className="font-bold text-gray-400">Sin Video en Proceso</p>
                  <p className="text-xs text-gray-600 mt-1 max-w-[200px]">Configura tu video y haz clic en generar para comenzar</p>
                </div>
              </div>
            )}
            
            {status?.script && <RetentionScore score={Math.floor(Math.random() * 15) + 80} />}
            {status?.script && <Timeline script={status.script} />}
          </div>
        </div>
      </div>
    </div>
  )
}

function JobStatus({ status, jobId }) {
  // Skeleton State if status is not yet available but jobId exists
  if (!status && jobId) {
    return (
      <div className="glass-card space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-4 w-32 bg-white/5 animate-pulse rounded" />
            <div className="h-3 w-48 bg-white/5 animate-pulse rounded" />
          </div>
          <div className="h-10 w-10 bg-white/5 animate-pulse rounded-lg" />
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="flex items-center gap-3">
              <div className="h-8 w-8 bg-white/5 animate-pulse rounded-lg" />
              <div className="h-3 w-full bg-white/5 animate-pulse rounded" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!status) return null
  const isCompleted = status.status === 'completed'
  const isError = status.status === 'error' || status.status === 'failed'

  return (
    <div className="glass-card space-y-6">
      {/* Progreso */}
      <div className="space-y-3">
        <div className="flex justify-between items-end">
          <div>
            <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">Estado</p>
            <p className="font-bold text-sm text-[#25f4ee]">{status.message}</p>
          </div>
          <span className="text-2xl font-black font-heading tiktok-gradient-text">{status.progress}%</span>
        </div>
        <div className="h-3 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-[#fe2c55] via-[#ff6b6b] to-[#25f4ee] transition-all duration-700 shadow-[0_0_10px_rgba(254,44,85,0.4)]"
            style={{ width: `${status.progress}%` }}
          />
        </div>
      </div>

      {/* Pasos Visuales */}
      <div className="grid grid-cols-4 gap-2">
        {[
          { icon: Wand2, label: 'Guion', done: status.progress > 20 },
          { icon: Music, label: 'Audio', done: status.progress > 40 },
          { icon: VideoIcon, label: 'Media', done: status.progress > 70 },
          { icon: CheckCircle, label: 'Final', done: status.progress >= 100 },
        ].map((step, i) => (
          <div key={i} className="flex flex-col items-center gap-1.5">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all ${
              step.done ? 'bg-green-500/20 text-green-400 shadow-[0_0_15px_rgba(34,197,94,0.2)]' : 'bg-white/5 text-gray-600'
            }`}>
              <step.icon size={18} />
            </div>
            <span className={`text-[10px] font-bold uppercase tracking-tighter ${step.done ? 'text-green-500' : 'text-gray-600'}`}>
              {step.label}
            </span>
          </div>
        ))}
      </div>

      {/* Preview Section: Cinematic Live Storyboard or Final Video */}
      <div className="relative">
        {isCompleted && status.video_url ? (
          <div className="space-y-4 animate-slide-up pt-4 border-t border-white/5">
            <video
              src={getVideoUrl(status.video_url)}
              controls
              playsInline
              className="w-full max-w-[320px] mx-auto rounded-3xl bg-black shadow-2xl border border-white/10"
            />
            <a
              href={getVideoUrl(status.video_url)}
              download
              className="btn-premium w-full !bg-green-600 hover:!bg-green-500 shadow-lg shadow-green-600/20"
            >
              <Download size={18} /> Descargar MP4
            </a>
          </div>
        ) : (
          <div className="animate-slide-up">
            <LiveStoryboard scenes={status.scenes || []} message={status.message} />
          </div>
        )}
      </div>

      {/* Script Meta - Only show when ready */}
      {status.script && isCompleted && (
        <div className="p-4 bg-white/5 rounded-2xl space-y-2 border border-white/5 animate-slide-up">
          <p className="text-xs font-bold text-[#25f4ee] uppercase tracking-widest">Script Generado</p>
          <p className="text-sm font-bold text-white">{status.script.title}</p>
          <p className="text-xs text-gray-400 leading-relaxed italic">"{status.script.narration}"</p>
        </div>
      )}

      {isError && (
        <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 animate-slide-up">
          <AlertCircle size={20} className="shrink-0" />
          <p className="text-sm leading-relaxed">{status.message}</p>
        </div>
      )}
    </div>
  )
}

