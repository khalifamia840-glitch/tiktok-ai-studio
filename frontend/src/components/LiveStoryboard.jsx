import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Clapperboard, MonitorPlay } from 'lucide-react'
import { getVideoUrl } from '../api'

export default function LiveStoryboard({ scenes = [], message = "" }) {
  const [currentIndex, setCurrentIndex] = useState(0)

  // Ciclar entre las escenas disponibles para dar sensación de video
  useEffect(() => {
    if (scenes.length <= 1) return
    const timer = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % scenes.length)
    }, 4000)
    return () => clearInterval(timer)
  }, [scenes.length])

  // Saltar a la última escena cuando llega una nueva
  useEffect(() => {
    if (scenes.length > 0) {
      setCurrentIndex(scenes.length - 1)
    }
  }, [scenes.length])

  // Si no hay escenas aún, mostrar placeholder cinemático de carga
  if (scenes.length === 0) {
    return (
      <div className="relative aspect-[9/16] w-full max-w-[320px] mx-auto rounded-3xl overflow-hidden bg-[#050505] border border-white/5 shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-b from-[#fe2c55]/10 via-transparent to-[#25f4ee]/5 animate-pulse" />
        <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center space-y-4">
          <div className="relative">
            <div className="absolute inset-0 bg-[#fe2c55] blur-2xl opacity-20 animate-pulse" />
            <Clapperboard size={48} className="text-zinc-700 animate-bounce" />
          </div>
          <div className="space-y-1">
            <p className="text-xs font-black uppercase tracking-[0.2em] text-zinc-500 animate-pulse">
              Initializing AI Director
            </p>
            <p className="text-[10px] text-zinc-600 font-medium italic">
              {message || "Crafting cinematic narrative..."}
            </p>
          </div>
        </div>
        {/* Grain effect */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
      </div>
    )
  }

  const currentScene = scenes[currentIndex]

  return (
    <div className="relative aspect-[9/16] w-full max-w-[320px] mx-auto rounded-3xl overflow-hidden bg-black border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
      <AnimatePresence mode="wait">
        <motion.div
          key={currentScene}
          initial={{ opacity: 0, scale: 1.1 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          className="absolute inset-0"
        >
          {/* Ken Burns Effect simulation via framer-motion */}
          <motion.img
            src={getVideoUrl(currentScene)}
            alt="AI Storyboard"
            className="w-full h-full object-cover"
            loading="eager"
            fetchpriority="high"
            initial={{ scale: 1 }}
            animate={{ scale: 1.15 }}
            transition={{ duration: 6, ease: "linear" }}
          />
        </motion.div>
      </AnimatePresence>

      {/* Overlay: Cinematic HUD */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/20 pointer-events-none" />
      
      <div className="absolute top-4 left-4 flex items-center gap-2">
        <div className="flex items-center gap-1.5 bg-black/40 backdrop-blur-md border border-white/10 px-2 py-1 rounded-full">
          <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
          <span className="text-[9px] font-bold text-white uppercase tracking-widest">Live Preview</span>
        </div>
      </div>

      <div className="absolute bottom-6 left-4 right-4 space-y-2">
        <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-[#25f4ee] uppercase tracking-tighter flex items-center gap-1">
                <MonitorPlay size={10} /> Scene {currentIndex + 1}/{scenes.length}
            </span>
            <span className="text-[9px] text-zinc-400 font-mono">24 FPS · AI RENDER</span>
        </div>
        <div className="h-0.5 bg-white/10 rounded-full overflow-hidden">
            <motion.div 
                className="h-full bg-[#fe2c55]"
                initial={{ width: 0 }}
                animate={{ width: "100%" }}
                transition={{ duration: 4, ease: "linear", repeat: Infinity }}
            />
        </div>
        <p className="text-[11px] text-white font-medium line-clamp-2 drop-shadow-lg">
            {message}
        </p>
      </div>

      {/* Film Grain & Dust */}
      <div className="absolute inset-0 opacity-[0.05] pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
    </div>
  )
}
