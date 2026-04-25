import { useState, useEffect, useRef } from 'react'
import { Sparkles, Loader2, Download, CheckCircle, AlertCircle, ChevronDown } from 'lucide-react'
import { generateVideo, getJobStatus, getVideoUrl } from '../api'

const STYLES = ['entretenido','educativo','motivacional','humor','misterio','viral']
const NICHES = ['general','fitness','tecnologia','negocios','humor','educacion','lifestyle','salud','viajes','cocina']
const DURATIONS = [15, 30, 60]
const VOICES = [
  { value: 'edge', label: 'Edge TTS (natural)' },
  { value: 'gtts', label: 'Google TTS (basico)' },
]

export default function GeneratePage() {
  const [form, setForm] = useState({
    topic: '',
    style: 'entretenido',
    audience: 'general',
    duration: 30,
    language: 'es',
    voice: 'edge',
    add_subtitles: true,
    niche: 'general',
  })
  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)

  // Polling del estado del job
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
        clearInterval(pollRef.current)
        setLoading(false)
        setError('Error al consultar el estado del video')
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
      const msg = e.response?.data?.detail || e.message || 'Error al iniciar la generacion'
      setError(msg)
    }
  }

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  return (
    <div className="max-w-lg mx-auto px-4 py-6 space-y-5">
      {/* Titulo */}
      <div className="text-center">
        <h2 className="text-2xl font-bold">
          <span className="text-[#fe2c55]">Genera</span> tu video
        </h2>
        <p className="text-gray-400 text-sm mt-1">
          Escribe un tema y la IA crea el video completo
        </p>
      </div>

      {/* Formulario */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Tema */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Tema del video *
          </label>
          <input
            type="text"
            value={form.topic}
            onChange={e => set('topic', e.target.value)}
            placeholder="Ej: 5 habitos de personas exitosas"
            className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3
                       text-white placeholder-gray-500 focus:outline-none focus:border-[#fe2c55]
                       transition-colors"
            required
            maxLength={200}
          />
        </div>

        {/* Estilo + Duracion */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Estilo</label>
            <div className="relative">
              <select
                value={form.style}
                onChange={e => set('style', e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-xl px-3 py-3
                           text-white appearance-none focus:outline-none focus:border-[#fe2c55]"
              >
                {STYLES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
              <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Duracion</label>
            <div className="flex gap-2">
              {DURATIONS.map(d => (
                <button key={d} type="button"
                  onClick={() => set('duration', d)}
                  className={`flex-1 py-3 rounded-xl text-sm font-medium border transition-colors ${
                    form.duration === d
                      ? 'bg-[#fe2c55] border-[#fe2c55] text-white'
                      : 'bg-gray-900 border-gray-700 text-gray-300 hover:border-gray-500'
                  }`}
                >
                  {d}s
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Nicho */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Nicho</label>
          <div className="relative">
            <select
              value={form.niche}
              onChange={e => set('niche', e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-xl px-3 py-3
                         text-white appearance-none focus:outline-none focus:border-[#fe2c55]"
            >
              {NICHES.map(n => <option key={n} value={n}>{n}</option>)}
            </select>
            <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
          </div>
        </div>

        {/* Idioma + Voz */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Idioma</label>
            <div className="flex gap-2">
              {[['es','ES'],['en','EN']].map(([v,l]) => (
                <button key={v} type="button"
                  onClick={() => set('language', v)}
                  className={`flex-1 py-3 rounded-xl text-sm font-medium border transition-colors ${
                    form.language === v
                      ? 'bg-[#25f4ee] border-[#25f4ee] text-black'
                      : 'bg-gray-900 border-gray-700 text-gray-300 hover:border-gray-500'
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Voz</label>
            <div className="relative">
              <select
                value={form.voice}
                onChange={e => set('voice', e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-xl px-3 py-3
                           text-white appearance-none focus:outline-none focus:border-[#fe2c55]"
              >
                {VOICES.map(v => <option key={v.value} value={v.value}>{v.label}</option>)}
              </select>
              <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Subtitulos */}
        <label className="flex items-center gap-3 cursor-pointer">
          <div
            onClick={() => set('add_subtitles', !form.add_subtitles)}
            className={`w-11 h-6 rounded-full transition-colors relative ${
              form.add_subtitles ? 'bg-[#fe2c55]' : 'bg-gray-700'
            }`}
          >
            <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
              form.add_subtitles ? 'translate-x-6' : 'translate-x-1'
            }`} />
          </div>
          <span className="text-sm text-gray-300">Agregar subtitulos</span>
        </label>

        {/* Error */}
        {error && (
          <div className="flex items-start gap-2 bg-red-900/30 border border-red-800 rounded-xl p-3">
            <AlertCircle size={16} className="text-red-400 mt-0.5 shrink-0" />
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}

        {/* Boton */}
        <button
          type="submit"
          disabled={loading || !form.topic.trim()}
          className="w-full py-4 rounded-xl font-bold text-white text-base
                     bg-gradient-to-r from-[#fe2c55] to-[#ff6b6b]
                     hover:from-[#e0253c] hover:to-[#e05555]
                     disabled:opacity-50 disabled:cursor-not-allowed
                     active:scale-95 transition-all duration-200
                     flex items-center justify-center gap-2"
        >
          {loading ? (
            <><Loader2 size={20} className="animate-spin" /> Generando...</>
          ) : (
            <><Sparkles size={20} /> Generar Video</>
          )}
        </button>
      </form>

      {/* Estado del job */}
      {status && <JobStatus status={status} />}
    </div>
  )
}

function JobStatus({ status }) {
  const isCompleted = status.status === 'completed'
  const isError = status.status === 'error'
  const isRunning = status.status === 'running' || status.status === 'pending'

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 space-y-4">
      {/* Progreso */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-300">{status.message}</span>
          <span className="text-gray-400">{status.progress}%</span>
        </div>
        <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-[#fe2c55] to-[#25f4ee] transition-all duration-500"
            style={{ width: `${status.progress}%` }}
          />
        </div>
      </div>

      {/* Completado */}
      {isCompleted && status.video_url && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-green-400">
            <CheckCircle size={18} />
            <span className="font-medium">Video listo</span>
          </div>
          {/* Preview del video */}
          <video
            src={getVideoUrl(status.video_url)}
            controls
            playsInline
            className="w-full rounded-xl bg-black"
            style={{ maxHeight: '400px' }}
          />
          {/* Boton descargar */}
          <a
            href={getVideoUrl(status.video_url)}
            download
            className="flex items-center justify-center gap-2 w-full py-3 rounded-xl
                       bg-green-600 hover:bg-green-500 text-white font-bold transition-colors"
          >
            <Download size={18} />
            Descargar MP4
          </a>
          {/* Script generado */}
          {status.script && (
            <details className="text-sm">
              <summary className="text-gray-400 cursor-pointer hover:text-gray-200">
                Ver script generado
              </summary>
              <div className="mt-2 bg-gray-800 rounded-xl p-3 space-y-2">
                <p className="font-medium text-white">{status.script.title}</p>
                <p className="text-gray-300 text-xs leading-relaxed">{status.script.narration}</p>
                {status.script.hook && (
                  <p className="text-[#25f4ee] text-xs">Hook: {status.script.hook}</p>
                )}
              </div>
            </details>
          )}
        </div>
      )}

      {/* Error */}
      {isError && (
        <div className="flex items-start gap-2 text-red-400">
          <AlertCircle size={16} className="mt-0.5 shrink-0" />
          <p className="text-sm">{status.message}</p>
        </div>
      )}
    </div>
  )
}
