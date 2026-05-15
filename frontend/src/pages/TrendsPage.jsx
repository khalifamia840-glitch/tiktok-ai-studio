import { motion } from 'framer-motion'
import { TrendingUp, Flame, Play, Music, Hash } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function TrendsPage() {
  const navigate = useNavigate()

  const trends = [
    {
      niche: 'Desarrollo Personal',
      hook: 'POV: Tienes 6 meses para cambiar tu vida',
      format: 'Video motivacional oscuro con lluvia',
      growth: '+142%',
      audio: 'Interstellar Theme (Slowed)',
    },
    {
      niche: 'Misterio / Terror',
      hook: 'La gente de este pueblo nunca envejece...',
      format: 'Imágenes IA estilo 1990s',
      growth: '+89%',
      audio: 'Creepy Music Box',
    },
    {
      niche: 'Historias',
      hook: 'El hombre que engañó a todo un país',
      format: 'Documental rápido con zooms constantes',
      growth: '+215%',
      audio: 'Suspense Cinematic',
    }
  ]

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8 animate-slide-up">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 bg-[#fe2c55]/10 text-[#fe2c55] rounded-2xl flex items-center justify-center">
          <Flame size={24} />
        </div>
        <div>
          <h2 className="text-4xl font-bold font-heading">Tendencias <span className="tiktok-gradient-text">Virales</span></h2>
          <p className="text-gray-400 mt-1">Formatos y nichos que están explotando en TikTok hoy.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {trends.map((trend, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card flex flex-col group relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4">
              <span className="flex items-center gap-1 text-green-400 text-sm font-bold bg-green-400/10 px-2 py-1 rounded-lg">
                <TrendingUp size={14} /> {trend.growth}
              </span>
            </div>
            
            <div className="flex-1 space-y-4 pt-4">
              <div className="inline-block px-3 py-1 bg-white/5 rounded-full text-xs font-bold uppercase tracking-widest text-gray-400">
                {trend.niche}
              </div>
              
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">Mejor Hook</p>
                <p className="font-bold text-lg text-white leading-snug">"{trend.hook}"</p>
              </div>

              <div className="space-y-2 border-t border-white/5 pt-4">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <Hash size={14} className="text-[#25f4ee]" /> {trend.format}
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <Music size={14} className="text-[#fe2c55]" /> {trend.audio}
                </div>
              </div>
            </div>

            <button 
              onClick={() => navigate('/generate', { state: { topic: trend.hook, autoGenerate: false } })}
              className="mt-6 w-full py-3 bg-white/5 hover:bg-[#fe2c55] text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-colors group-hover:shadow-[0_0_20px_rgba(254,44,85,0.3)]"
            >
              <Play size={16} className="fill-current" /> Usar esta Tendencia
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
