import { useState, useEffect } from 'react'
import { TrendingUp, BarChart3, Users, Play, Sparkles, Loader2 } from 'lucide-react'
import { getTrending, generateVideo } from '../api'
import { useNavigate } from 'react-router-dom'

export default function DashboardPage() {
  const [trending, setTrending] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchTrending()
  }, [])

  const fetchTrending = async () => {
    try {
      const res = await getTrending()
      setTrending(res.trending || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleTrendingClick = (topic) => {
    // Redirigir a crear con el tema pre-cargado
    navigate('/', { state: { topic } })
  }

  const stats = [
    { label: 'Videos Generados', value: '12', icon: Play, color: 'text-pink-500' },
    { label: 'Alcance Estimado', value: '5.2K', icon: Users, color: 'text-blue-500' },
    { label: 'Engagement', value: '8.4%', icon: BarChart3, color: 'text-green-500' },
  ]

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8 animate-slide-up">
      <header>
        <h1 className="text-3xl font-bold font-heading">Panel de Control</h1>
        <p className="text-gray-400 mt-1">Monitorea tu crecimiento y encuentra tendencias</p>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((stat, i) => (
          <div key={i} className="glass-card flex items-center gap-4">
            <div className={`p-3 rounded-2xl bg-white/5 ${stat.color}`}>
              <stat.icon size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-medium">{stat.label}</p>
              <p className="text-2xl font-bold font-heading mt-1">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Trending Topics */}
      <div className="glass-card">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <TrendingUp className="text-[#fe2c55]" size={20} />
            <h2 className="text-xl font-bold font-heading">Temas Tendencia</h2>
          </div>
          <button onClick={fetchTrending} className="text-sm text-[#25f4ee] hover:underline">
            Actualizar
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="animate-spin text-gray-500" size={32} />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {trending.length > 0 ? trending.map((item, i) => (
              <button
                key={i}
                onClick={() => handleTrendingClick(item.topic)}
                className="flex items-center justify-between p-4 bg-white/5 border border-white/5 rounded-2xl hover:border-[#fe2c55]/50 transition-all text-left group"
              >
                <div>
                  <p className="font-semibold text-gray-200 group-hover:text-white transition-colors">{item.topic}</p>
                  <p className="text-xs text-gray-500 mt-1 uppercase tracking-wider">{item.niche} • {item.style}</p>
                </div>
                <div className="w-8 h-8 rounded-full bg-[#fe2c55]/10 flex items-center justify-center text-[#fe2c55] group-hover:bg-[#fe2c55] group-hover:text-white transition-all">
                  <Sparkles size={14} />
                </div>
              </button>
            )) : (
              <p className="text-gray-500 text-center py-8 col-span-2">
                Genera tu primer video para ver tendencias aquí
              </p>
            )}
          </div>
        )}
      </div>

      {/* AI Tips */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/20">
        <div className="flex gap-4">
          <div className="w-12 h-12 rounded-2xl bg-blue-500/20 flex items-center justify-center text-blue-400 shrink-0">
            <Sparkles size={24} />
          </div>
          <div>
            <h3 className="font-bold text-lg">Tip del Experto IA</h3>
            <p className="text-gray-400 text-sm mt-1 leading-relaxed">
              Los videos de "Estilo Educativo" en el nicho de "Finanzas" están teniendo un 40% más de retención esta semana. 
              Prueba crear un video de 45 segundos sobre "Cómo ahorrar en 2025".
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
