import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Sparkles, Play, TrendingUp, Users, Video as VideoIcon } from 'lucide-react'

export default function LandingPage() {
  const [topic, setTopic] = useState('')
  const navigate = useNavigate()

  const handleGenerate = (e) => {
    e.preventDefault()
    if (!topic.trim()) return
    navigate('/generate', { state: { topic } })
  }

  const examples = [
    "POV: eres un soldado romano en batalla",
    "Historia triste de un perrito abandonado",
    "El misterio del vuelo 370 resuelto",
    "10 cosas que no sabías de la antigua Roma"
  ]

  return (
    <div className="min-h-screen bg-[#010101] text-white overflow-x-hidden relative selection:bg-[#fe2c55]/30">
      
      {/* Background Effects */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-[#fe2c55]/20 blur-[120px] mix-blend-screen animate-pulse-slow" />
        <div className="absolute top-[20%] -right-[10%] w-[50%] h-[50%] rounded-full bg-[#25f4ee]/10 blur-[120px] mix-blend-screen" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
      </div>

      {/* Header */}
      <header className="relative z-20 flex items-center justify-between px-6 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 cursor-pointer">
          <div className="w-10 h-10 bg-gradient-to-br from-[#fe2c55] to-[#25f4ee] rounded-xl flex items-center justify-center shadow-lg shadow-[#fe2c55]/20">
            <VideoIcon size={22} />
          </div>
          <span className="font-bold text-2xl font-heading tracking-tight">AI Studio</span>
        </div>
        <div className="flex gap-4">
          <button onClick={() => navigate('/auth')} className="text-sm font-semibold text-gray-300 hover:text-white transition-colors">
            Iniciar Sesión
          </button>
        </div>
      </header>

      {/* Main Hero */}
      <main className="relative z-10 flex flex-col items-center justify-center min-h-[80vh] px-4 pt-10 pb-20 max-w-5xl mx-auto text-center">
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="space-y-6 w-full"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs font-semibold uppercase tracking-widest text-[#25f4ee] mb-4">
            <Sparkles size={14} /> La máquina viral ha despertado
          </div>
          
          <h1 className="text-5xl md:text-7xl font-black font-heading leading-[1.1] tracking-tight">
            Crea videos virales <br className="hidden md:block" />
            <span className="tiktok-gradient-text">en 1 clic con IA.</span>
          </h1>
          
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
            Escribe tu idea. Nuestra IA generará el guion viral, imágenes, voz clonada, música y subtítulos dinámicos al estilo Hormozi. <strong className="text-white">Sin editar nada.</strong>
          </p>

          {/* Giant Input Box */}
          <form onSubmit={handleGenerate} className="mt-12 max-w-3xl mx-auto relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-[#fe2c55] to-[#25f4ee] rounded-3xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />
            <div className="relative flex flex-col md:flex-row items-center gap-3 p-2 bg-[#0a0a0a] rounded-3xl border border-white/10 shadow-2xl">
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Escribe tu idea viral aquí..."
                className="w-full bg-transparent text-white text-lg md:text-xl px-6 py-4 outline-none placeholder:text-gray-600 font-medium"
                required
              />
              <button
                type="submit"
                disabled={!topic.trim()}
                className="w-full md:w-auto px-8 py-4 bg-gradient-to-r from-[#fe2c55] to-[#ff4b2b] text-white rounded-2xl font-bold text-lg hover:scale-[1.02] active:scale-95 transition-all shadow-lg shadow-[#fe2c55]/30 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                <Play size={20} className="fill-white" /> GENERAR VIDEO
              </button>
            </div>
          </form>

          {/* Quick Examples */}
          <div className="pt-8 flex flex-wrap justify-center gap-2">
            <span className="text-xs text-gray-500 font-bold uppercase tracking-widest mr-2 py-2">Ejemplos:</span>
            {examples.map((ex, i) => (
              <button
                key={i}
                onClick={() => setTopic(ex)}
                className="px-4 py-2 rounded-xl bg-white/5 border border-white/5 text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors"
              >
                "{ex}"
              </button>
            ))}
          </div>

        </motion.div>

        {/* Stats Section */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-32 w-full max-w-4xl border-t border-white/10 pt-16"
        >
          <div className="flex flex-col items-center">
            <TrendingUp size={32} className="text-[#25f4ee] mb-4" />
            <h3 className="text-4xl font-black font-heading">82%</h3>
            <p className="text-gray-500 font-medium mt-1">Mayor retención</p>
          </div>
          <div className="flex flex-col items-center">
            <Users size={32} className="text-[#fe2c55] mb-4" />
            <h3 className="text-4xl font-black font-heading">+50M</h3>
            <p className="text-gray-500 font-medium mt-1">Vistas generadas</p>
          </div>
          <div className="flex flex-col items-center">
            <Sparkles size={32} className="text-yellow-500 mb-4" />
            <h3 className="text-4xl font-black font-heading">30s</h3>
            <p className="text-gray-500 font-medium mt-1">Tiempo de creación</p>
          </div>
        </motion.div>
      </main>
    </div>
  )
}
