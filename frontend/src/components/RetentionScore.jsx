import { motion } from 'framer-motion'
import { Flame, Activity, Zap, Clock, Users } from 'lucide-react'

export default function RetentionScore({ score = 85, metrics }) {
  // Determine color based on score
  let color = 'text-[#25f4ee]' // Excellent
  let bg = 'bg-[#25f4ee]/20'
  let label = 'VIRAL POTENTIAL'
  
  if (score < 60) {
    color = 'text-yellow-500'
    bg = 'bg-yellow-500/20'
    label = 'MODERADO'
  }
  if (score < 40) {
    color = 'text-red-500'
    bg = 'bg-red-500/20'
    label = 'BAJO'
  }

  const defaultMetrics = metrics || [
    { label: 'Fuerza del Hook', value: 'Fuerte', icon: Flame },
    { label: 'Ritmo (Pacing)', value: 'Rápido', icon: Activity },
    { Emociones: 'Tensión', icon: Zap },
    { label: 'Retención Est.', value: '18s', icon: Clock }
  ]

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card overflow-hidden relative"
    >
      <div className={`absolute top-0 left-0 w-full h-1 ${bg}`} />
      
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-bold text-gray-300">Retention Score</h3>
          <p className="text-xs text-gray-500 uppercase tracking-widest mt-1">{label}</p>
        </div>
        <div className={`text-4xl font-black font-heading ${color}`}>
          {score}%
        </div>
      </div>

      <div className="space-y-4">
        {/* Main Bar */}
        <div className="h-3 w-full bg-white/5 rounded-full overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${score}%` }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            className={`h-full ${bg.replace('/20', '')}`}
          />
        </div>

        {/* Breakdown */}
        <div className="grid grid-cols-2 gap-3 mt-6">
          {defaultMetrics.map((m, i) => (
            <div key={i} className="flex items-center gap-2 p-2 rounded-xl bg-white/5">
              <div className="p-1.5 rounded-lg bg-white/5 text-gray-400">
                <m.icon size={14} />
              </div>
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-widest">{m.label || Object.keys(m)[0]}</p>
                <p className="text-xs font-bold text-white">{m.value || Object.values(m)[0]}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
