import { motion } from 'framer-motion'
import { Image as ImageIcon, Mic, Type, Clock } from 'lucide-react'

export default function Timeline({ script }) {
  if (!script) return null

  // Mock scenes based on script keywords or duration
  // In a full implementation, the backend would return exact scene breakdowns.
  const scenes = script.keywords?.map((kw, i) => ({
    id: i,
    keyword: kw,
    duration: 3, // mock 3s per scene
    image: null, // would be URL
  })) || []

  return (
    <div className="glass-card mt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-gray-300">Timeline de Escenas</h3>
        <span className="text-xs text-gray-500 uppercase tracking-widest bg-white/5 px-2 py-1 rounded-md">Solo Lectura</span>
      </div>

      <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide snap-x">
        {scenes.map((scene, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="shrink-0 w-48 bg-[#0a0a0a] rounded-2xl border border-white/5 overflow-hidden snap-start"
          >
            {/* Scene Preview Block */}
            <div className="aspect-[9/16] bg-[#1a1a1a] relative flex items-center justify-center border-b border-white/5 group">
              <ImageIcon size={24} className="text-gray-600" />
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
                <span className="text-xs font-bold text-white px-3 py-1 bg-white/10 rounded-full border border-white/10">
                  {scene.keyword}
                </span>
              </div>
            </div>

            {/* Scene Info */}
            <div className="p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-gray-500 uppercase">Scene {i + 1}</span>
                <span className="text-[10px] font-bold text-[#25f4ee] bg-[#25f4ee]/10 px-1.5 py-0.5 rounded flex items-center gap-1">
                  <Clock size={10} /> {scene.duration}s
                </span>
              </div>
              
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Mic size={12} className="shrink-0" />
                <span className="truncate">Auto TTS</span>
              </div>
              
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Type size={12} className="shrink-0" />
                <span className="truncate">Auto Subs</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
