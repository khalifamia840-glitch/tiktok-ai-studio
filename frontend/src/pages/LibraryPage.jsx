import { useState, useEffect } from 'react'
import { Trash2, Download, RefreshCw, Film } from 'lucide-react'
import { listVideos, deleteVideo, getVideoUrl } from '../api'

export default function LibraryPage() {
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null) // filename a confirmar

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
    <div className="max-w-lg mx-auto px-4 py-6 space-y-4">
      {/* Modal de confirmación */}
      {confirmDelete && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-sm space-y-4">
            <p className="text-white font-medium text-center">¿Eliminar este video?</p>
            <p className="text-gray-400 text-sm text-center truncate">{confirmDelete}</p>
            <div className="flex gap-3">
              <button
                onClick={() => setConfirmDelete(null)}
                className="flex-1 py-2 rounded-xl border border-gray-600 text-gray-300 hover:bg-gray-800 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={confirmAndDelete}
                className="flex-1 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-medium transition-colors"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Mis Videos</h2>
        <button onClick={load} className="p-2 text-gray-400 hover:text-white transition-colors">
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {loading && (
        <div className="text-center py-12 text-gray-500">
          <RefreshCw size={32} className="animate-spin mx-auto mb-3" />
          <p>Cargando videos...</p>
        </div>
      )}

      {!loading && videos.length === 0 && (
        <div className="text-center py-16 text-gray-500">
          <Film size={48} className="mx-auto mb-3 opacity-30" />
          <p className="font-medium">No hay videos aun</p>
          <p className="text-sm mt-1">Genera tu primer video en la pestana Crear</p>
        </div>
      )}

      <div className="space-y-3">
        {videos.map(video => (
          <div key={video.filename}
            className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
            <video
              src={getVideoUrl(video.url)}
              controls
              playsInline
              className="w-full bg-black"
              style={{ maxHeight: '300px' }}
            />
            <div className="p-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-200 truncate max-w-[200px]">
                  {video.filename}
                </p>
                <p className="text-xs text-gray-500">{video.size_mb} MB</p>
              </div>
              <div className="flex gap-2">
                <a
                  href={getVideoUrl(video.url)}
                  download
                  className="p-2 bg-green-700 hover:bg-green-600 rounded-lg transition-colors"
                >
                  <Download size={16} />
                </a>
                <button
                  onClick={() => handleDelete(video.filename)}
                  disabled={deleting === video.filename}
                  className="p-2 bg-red-900 hover:bg-red-800 rounded-lg transition-colors disabled:opacity-50"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
