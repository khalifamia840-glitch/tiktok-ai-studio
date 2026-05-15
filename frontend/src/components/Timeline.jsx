import { motion } from 'framer-motion'
import { Camera, Mic, Type, Clock, Flame, Zap, Heart, AlertTriangle, Star, Globe } from 'lucide-react'

const EMOTION_CONFIG = {
  sad: { label: 'Tristeza', color: 'text-blue-400', bg: 'bg-blue-400/10', icon: '😢' },
  tense: { label: 'Tensión', color: 'text-purple-400', bg: 'bg-purple-400/10', icon: '😰' },
  epic: { label: 'Épico', color: 'text-yellow-400', bg: 'bg-yellow-400/10', icon: '⚔️' },
  motivational: { label: 'Motivación', color: 'text-orange-400', bg: 'bg-orange-400/10', icon: '🔥' },
  romantic: { label: 'Romance', color: 'text-pink-400', bg: 'bg-pink-400/10', icon: '💖' },
  shocking: { label: 'Impacto', color: 'text-red-400', bg: 'bg-red-400/10', icon: '😱' },
  neutral: { label: 'Neutral', color: 'text-gray-400', bg: 'bg-gray-400/10', icon: '🎬' },
}

export default function Timeline({ script }) {
  if (!script) return null

  const scenes = script.segments?.map((seg, i) => ({
    id: i,
    keyword: seg.image_keyword || script.keywords?.[i] || `Escena ${i + 1}`,
    narration: seg.narration || '',
    duration: seg.duration || 3,
    emotion: seg.emotion || 'neutral',
    shot_type: seg.shot_type || 'medium shot',
    lighting: seg.lighting || 'cinematic lighting',
  })) || script.keywords?.map((kw, i) => ({
    id: i,
    keyword: kw,
    duration: 3,
    emotion: 'neutral',
    shot_type: 'medium shot',
    lighting: 'cinematic lighting',
  })) || []

  if (scenes.length === 0) return null

  return (
    <div className="glass-card mt-2">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="font-bold text-gray-200">Storyboard Cinematográfico</h3>
          <p className="text-xs text-gray-500 mt-0.5">{scenes.length} escenas · Shot Director IA</p>
        </div>
        <span className="text-xs text-gray-500 bg-white/5 px-2 py-1 rounded-md border border-white/5">
          🎬 AI Director
        </span>
      </div>

      <div className="flex gap-3 overflow-x-auto pb-3 scrollbar-hide snap-x">
        {scenes.map((scene, i) => {
          const emo = EMOTION_CONFIG[scene.emotion] || EMOTION_CONFIG.neutral
          return (
            <motion.div 
              key={i}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              className="shrink-0 w-44 bg-[#0a0a0a] rounded-2xl border border-white/5 overflow-hidden snap-start"
            >
              {/* Scene Preview Block */}
              <div className="aspect-[9/16] bg-gradient-to-b from-[#1a1a2e] to-[#0a0a0a] relative flex items-end justify-start p-2 border-b border-white/5">
                <div className="absolute top-2 right-2">
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${emo.bg} ${emo.color} flex items-center gap-0.5`}>
                    {emo.icon} {emo.label}
                  </span>
                </div>
                <div className="absolute top-2 left-2 text-[10px] font-bold text-gray-400 bg-black/40 px-1.5 py-0.5 rounded">
                  #{i + 1}
                </div>
                <p className="text-[9px] text-gray-300 leading-relaxed italic line-clamp-3 bg-black/60 rounded-lg p-1.5 backdrop-blur-sm">
                  "{scene.keyword.substring(0, 60)}..."
                </p>
              </div>

              {/* Scene Info */}
              <div className="p-2.5 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[9px] font-bold text-gray-500 uppercase">SHOT</span>
                  <span className="text-[9px] font-bold text-[#25f4ee] bg-[#25f4ee]/10 px-1.5 py-0.5 rounded flex items-center gap-1">
                    <Clock size={8} /> {Math.round(scene.duration)}s
                  </span>
                </div>

                <div className="flex items-center gap-1 text-[10px] text-gray-400">
                  <Camera size={10} className="shrink-0 text-[#fe2c55]" />
                  <span className="truncate capitalize">{scene.shot_type}</span>
                </div>
                
                <div className="flex items-center gap-1 text-[10px] text-gray-500">
                  <Mic size={10} className="shrink-0" />
                  <span className="truncate">Auto TTS</span>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
