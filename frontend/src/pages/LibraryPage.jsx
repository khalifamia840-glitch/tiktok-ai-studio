import { useState, useEffect } from 'react'
import { Trash2, Download, RefreshCw, Film, Play, AlertCircle, Loader2 } from 'lucide-react'
import { listVideos, deleteVideo, getVideoUrl } from '../api'

export default function LibraryPage() {
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const data = await listVideos()
      setVideos(data.videos || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (filename) => {
    setConfirmDelete(filename)
  }

  const confirmAndDelete = async () => {
    const filename = confirmDelete
    setConfirmDelete(null)
    setDeleting(filename)
    try {
      await deleteVideo(filename)
      setVideos(v => v.filter(x => x.filename !== filename))
    } catch (e) {
      alert('Error al eliminar')
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8 animate-slide-up">
      {/* Modal de confirmación */}
      {confirmDelete && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center z-[100] px-4">
          <div className="glass-card w-full max-w-sm text-center space-y-6 shadow-2xl border-white/20">
            <div className="w-16 h-16 bg-red-500/20 text-red-500 rounded-full flex items-center justify-center mx-auto">
              <Trash2 size={32} />
            </div>
            <div>
              <h3 className="text-xl font-bold font-heading">¿Eliminar Video?</h3>
              <p className="text-gray-400 text-sm mt-2">Esta acción no se puede deshacer.</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setConfirmDelete(null)}
                className="flex-1 py-3 rounded-2xl bg-white/5 hover:bg-white/10 font-bold transition-all"
              >
                Cancelar
              </button>
              <button
                onClick={confirmAndDelete}
                className="flex-1 py-3 rounded-2xl bg-red-600 hover:bg-red-500 text-white font-bold transition-all shadow-lg shadow-red-600/20"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}

      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-heading">Mi Biblioteca</h1>
          <p className="text-gray-400 mt-1">Todos tus videos generados listos para publicar</p>
        </div>
        <button 
          onClick={load} 
          className="p-3 bg-white/5 hover:bg-white/10 rounded-2xl transition-all group active:scale-90"
          title="Actualizar"
        >
          <RefreshCw size={20} className={`${loading ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
        </button>
      </header>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-24 text-gray-500">
          <Loader2 size={48} className="animate-spin mb-4 text-[#fe2c55]" />
          <p className="font-bold">Cargando tus videos...</p>
        </div>
      ) : videos.length === 0 ? (
        <div className="glass-card flex flex-col items-center justify-center py-32 text-center space-y-4 border-dashed">
          <div className="w-20 h-20 bg-white/5 rounded-3xl flex items-center justify-center text-gray-600">
            <Film size={40} />
          </div>
          <div>
            <h2 className="text-xl font-bold">Aún no tienes videos</h2>
            <p className="text-gray-400 max-w-xs mt-2">Crea tu primer video viral en la pestaña de Generador para verlo aquí.</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map(video => (
            <div key={video.filename} className="glass-card !p-0 overflow-hidden flex flex-col group">
              <div className="relative aspect-[9/16] bg-black">
                <video
                  src={getVideoUrl(video.url)}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                  <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/20">
                    <Play fill="white" size={24} />
                  </div>
                </div>
              </div>
              
              <div className="p-4 space-y-4">
                <div>
                  <p className="font-bold truncate text-gray-100">{video.filename}</p>
                  <p className="text-xs text-gray-500 font-medium">{video.size_mb} MB • MP4</p>
                </div>
                
                <div className="flex gap-2">
                  <a
                    href={getVideoUrl(video.url)}
                    download
                    className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-[#fe2c55] hover:bg-[#ff4b2b] text-white font-bold text-sm transition-all shadow-lg shadow-[#fe2c55]/20"
                  >
                    <Download size={16} /> Descargar
                  </a>
                  <button
                    onClick={() => handleDelete(video.filename)}
                    disabled={deleting === video.filename}
                    className="p-3 rounded-xl bg-white/5 hover:bg-red-500/10 hover:text-red-500 text-gray-400 transition-all disabled:opacity-50"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
