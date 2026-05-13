import { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { Sparkles, Loader2, Download, CheckCircle, AlertCircle, ChevronDown, Wand2, Type, Music, Video as VideoIcon } from 'lucide-react'
import { generateVideo, getJobStatus, getVideoUrl } from '../api'

const STYLES = ['entretenido','educativo','motivacional','humor','misterio','viral','informativo','storytelling']
const NICHES = ['general','fitness','tecnologia','negocios','humor','educacion','lifestyle','salud','viajes','cocina','dinero','relaciones']
const DURATIONS = [15, 30, 45, 60]
const VOICES = [
  { value: 'edge', label: 'Edge TTS (Ultra-Natural)' },
  { value: 'gtts', label: 'Google TTS (Básico)' },
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
  })

  // Cargar tema desde el state (Dashboard)
  useEffect(() => {
    if (location.state?.topic) {
      setForm(f => ({ ...f, topic: location.state.topic }))
    }
  }, [location.state])

  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)

  useEffect(() => {
    if (!jobId) return
    pollRef.current = setInterval(async () => {
      try {
        const s = await getJobStatus(jobId)
        setStatus(s)
        if (s.status === 'completed' || s.status === 'error') {
          clearInterval(pollRef.current)
          setLoading(false)
        }
      } catch (e) {
        console.error(e)
      }
    }, 2000)
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
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8 animate-slide-up">
      {/* Header */}
      <div className="text-center md:text-left">
        <h2 className="text-4xl font-bold font-heading">
          <span className="tiktok-gradient-text">Genera</span> tu video
        </h2>
        <p className="text-gray-400 mt-2">Nuestra IA se encarga del guion, la voz y el montaje</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
        {/* Formulario */}
        <form onSubmit={handleSubmit} className="md:col-span-3 space-y-6">
          <div className="glass-card space-y-5">
            {/* Tema */}
            <div>
              <label className="flex items-center gap-2 text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
                <Wand2 size={14} /> Tema o Idea del Video
              </label>
              <textarea
                value={form.topic}
                onChange={e => set('topic', e.target.value)}
                placeholder="Ej: 5 hábitos para ser más productivo en la mañana..."
                className="input-premium min-h-[120px] resize-none"
                required
              />
            </div>

            {/* Duración */}
            <div>
              <label className="flex items-center gap-2 text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
                Duración Sugerida
              </label>
              <div className="grid grid-cols-4 gap-2">
                {DURATIONS.map(d => (
                  <button key={d} type="button"
                    onClick={() => set('duration', d)}
                    className={`py-2.5 rounded-xl text-sm font-bold border transition-all ${
                      form.duration === d
                        ? 'bg-[#fe2c55] border-[#fe2c55] text-white shadow-lg shadow-[#fe2c55]/20'
                        : 'bg-white/5 border-white/5 text-gray-400 hover:border-white/10'
                    }`}
                  >
                    {d}s
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Estilo */}
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Estilo</label>
                <div className="relative">
                  <select
                    value={form.style}
                    onChange={e => set('style', e.target.value)}
                    className="input-premium appearance-none pr-10 py-3"
                  >
                    {STYLES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                  <ChevronDown size={16} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
                </div>
              </div>
              {/* Nicho */}
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Nicho</label>
                <div className="relative">
                  <select
                    value={form.niche}
                    onChange={e => set('niche', e.target.value)}
                    className="input-premium appearance-none pr-10 py-3"
                  >
                    {NICHES.map(n => <option key={n} value={n}>{n}</option>)}
                  </select>
                  <ChevronDown size={16} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Idioma */}
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Idioma</label>
                <div className="flex bg-white/5 p-1 rounded-xl">
                  {[['es','ES'],['en','EN']].map(([v,l]) => (
                    <button key={v} type="button"
                      onClick={() => set('language', v)}
                      className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${
                        form.language === v ? 'bg-[#25f4ee] text-black shadow-lg' : 'text-gray-400'
                      }`}
                    >
                      {l}
                    </button>
                  ))}
                </div>
              </div>
              {/* Voz */}
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Voz</label>
                <div className="relative">
                  <select
                    value={form.voice}
                    onChange={e => set('voice', e.target.value)}
                    className="input-premium appearance-none pr-10 py-3"
                  >
                    {VOICES.map(v => <option key={v.value} value={v.value}>{v.label}</option>)}
                  </select>
                  <ChevronDown size={16} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
                </div>
              </div>
            </div>

            {/* Subtítulos */}
            <label className="flex items-center justify-between p-4 bg-white/5 rounded-2xl cursor-pointer hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${form.add_subtitles ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-500'}`}>
                  <Type size={18} />
                </div>
                <span className="text-sm font-semibold">Subtítulos Automáticos</span>
              </div>
              <input 
                type="checkbox" 
                checked={form.add_subtitles}
                onChange={e => set('add_subtitles', e.target.checked)}
                className="w-5 h-5 accent-[#fe2c55]"
              />
            </label>
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
            className="btn-premium w-full shadow-2xl shadow-[#fe2c55]/20"
          >
            {loading ? (
              <><Loader2 className="animate-spin" /> Generando Video...</>
            ) : (
              <><Sparkles /> Crear Video Viral</>
            )}
          </button>
        </form>

        {/* Status Panel */}
        <div className="md:col-span-2">
          <div className="sticky top-8">
            {status ? (
              <JobStatus status={status} />
            ) : (
              <div className="glass-card border-dashed border-white/5 flex flex-col items-center justify-center py-20 text-center space-y-4">
                <div className="w-16 h-16 rounded-3xl bg-white/5 flex items-center justify-center text-gray-600">
                  <VideoIcon size={32} />
                </div>
                <div>
                  <p className="font-bold text-gray-400">Sin Video en Proceso</p>
                  <p className="text-xs text-gray-600 mt-1 max-w-[180px]">Configura tu video y haz clic en generar para comenzar</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function JobStatus({ status }) {
  const isCompleted = status.status === 'completed'
  const isError = status.status === 'error'

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

      {/* Resultado */}
      {isCompleted && status.video_url && (
        <div className="space-y-4 animate-slide-up">
          <video
            src={getVideoUrl(status.video_url)}
            controls
            playsInline
            className="w-full rounded-2xl bg-black shadow-2xl"
            style={{ maxHeight: '400px' }}
          />
          <a
            href={getVideoUrl(status.video_url)}
            download
            className="btn-premium w-full !bg-green-600 hover:!bg-green-500 shadow-lg shadow-green-600/20"
          >
            <Download size={18} /> Descargar MP4
          </a>
          {status.script && (
            <div className="p-4 bg-white/5 rounded-2xl space-y-2 border border-white/5">
              <p className="text-xs font-bold text-[#25f4ee] uppercase tracking-widest">Script Generado</p>
              <p className="text-sm font-bold text-white">{status.script.title}</p>
              <p className="text-xs text-gray-400 leading-relaxed italic">"{status.script.narration}"</p>
            </div>
          )}
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
