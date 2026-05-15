import { motion } from 'framer-motion'
import { LayoutTemplate, Play, Ghost, HeartCrack, Zap, Brain, Rocket, Eye, Search } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'

export default function TemplatesPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')

  const templates = [
    {
      id: 'horror-1',
      title: 'Historia de Terror Corta',
      niche: 'Misterio / Terror',
      icon: Ghost,
      color: 'from-purple-900 to-black',
      prompt: 'Una historia corta de terror que ocurre en un pueblo remoto donde nadie envejece.',
      views: '+2.4M',
      tags: ['Storytelling', 'Oscuro']
    },
    {
      id: 'sad-1',
      title: 'Desamor y Superación',
      niche: 'Relaciones',
      icon: HeartCrack,
      color: 'from-blue-900 to-black',
      prompt: 'Una historia triste sobre dejar ir a alguien que amas, pero con un final motivador.',
      views: '+5.1M',
      tags: ['Emocional', 'Lluvia']
    },
    {
      id: 'pov-1',
      title: 'POV: Eres Millonario',
      niche: 'Lifestyle / Dinero',
      icon: Zap,
      color: 'from-yellow-600 to-black',
      prompt: 'POV: Acabas de hacer tu primer millón de dólares a los 21 años. Consejos rápidos.',
      views: '+8.9M',
      tags: ['Dinero', 'Rápido']
    },
    {
      id: 'psy-1',
      title: 'Truco Psicológico',
      niche: 'Educación / Psicología',
      icon: Brain,
      color: 'from-green-800 to-black',
      prompt: 'Un truco oscuro de psicología para que alguien piense en ti todo el día.',
      views: '+12M',
      tags: ['Misterio', 'Hook Fuerte']
    },
    {
      id: 'mot-1',
      title: 'Disciplina Implacable',
      niche: 'Motivación / Fitness',
      icon: Rocket,
      color: 'from-red-900 to-black',
      prompt: 'Un discurso agresivo y motivador sobre la disciplina y levantarse a las 4 AM.',
      views: '+3.2M',
      tags: ['Gym', 'Épico']
    },
    {
      id: 'fact-1',
      title: 'Dato Perturbador',
      niche: 'Curiosidades',
      icon: Eye,
      color: 'from-teal-900 to-black',
      prompt: 'Un dato perturbador sobre el espacio exterior que te dejará sin dormir.',
      views: '+6.5M',
      tags: ['Espacio', 'Intriga']
    }
  ]

  const filtered = templates.filter(t => t.title.toLowerCase().includes(search.toLowerCase()) || t.niche.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8 animate-slide-up">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-white/5 text-white rounded-2xl flex items-center justify-center border border-white/10">
            <LayoutTemplate size={24} />
          </div>
          <div>
            <h2 className="text-4xl font-bold font-heading">Plantillas <span className="tiktok-gradient-text">Virales</span></h2>
            <p className="text-gray-400 mt-1">Estructuras probadas que garantizan retención.</p>
          </div>
        </div>

        <div className="relative w-full md:w-72">
          <input 
            type="text" 
            placeholder="Buscar plantillas..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#0a0a0a] border border-white/10 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-[#fe2c55] transition-colors"
          />
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((tpl, i) => (
          <motion.div 
            key={tpl.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            className={`rounded-3xl p-6 relative overflow-hidden group cursor-pointer border border-white/5 hover:border-white/20 transition-all`}
            onClick={() => navigate('/generate', { state: { topic: tpl.prompt, autoGenerate: true } })}
          >
            {/* Bg Gradient */}
            <div className={`absolute inset-0 bg-gradient-to-br ${tpl.color} opacity-40 group-hover:opacity-60 transition-opacity`} />
            <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />

            <div className="relative z-10 space-y-4">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center backdrop-blur-md">
                  <tpl.icon size={20} className="text-white" />
                </div>
                <span className="text-xs font-bold px-2 py-1 bg-white/10 rounded-lg backdrop-blur-md">
                  {tpl.views}
                </span>
              </div>

              <div>
                <p className="text-xs text-gray-300 uppercase tracking-widest mb-1">{tpl.niche}</p>
                <h3 className="text-xl font-bold font-heading leading-tight">{tpl.title}</h3>
              </div>

              <div className="flex flex-wrap gap-2 pt-2">
                {tpl.tags.map(tag => (
                  <span key={tag} className="text-[10px] font-bold uppercase tracking-wider px-2 py-1 bg-white/5 border border-white/10 rounded-md text-gray-400">
                    {tag}
                  </span>
                ))}
              </div>

              <button className="w-full mt-4 py-3 bg-white text-black rounded-xl font-bold flex items-center justify-center gap-2 opacity-0 translate-y-4 group-hover:opacity-100 group-hover:translate-y-0 transition-all shadow-[0_0_20px_rgba(255,255,255,0.2)]">
                <Play size={16} className="fill-black" /> Usar Plantilla
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
