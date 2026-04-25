import { Routes, Route, NavLink } from 'react-router-dom'
import { Video, Library, Settings } from 'lucide-react'
import GeneratePage from './pages/GeneratePage'
import LibraryPage from './pages/LibraryPage'

export default function App() {
  return (
    <div className="min-h-screen bg-[#010101] text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-4 py-3 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#fe2c55] to-[#25f4ee] flex items-center justify-center">
          <Video size={16} className="text-white" />
        </div>
        <h1 className="font-bold text-lg">
          <span className="text-[#fe2c55]">TikTok</span>
          <span className="text-white"> AI</span>
        </h1>
        <span className="ml-auto text-xs text-gray-500">v1.0</span>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<GeneratePage />} />
          <Route path="/library" element={<LibraryPage />} />
        </Routes>
      </main>

      {/* Bottom nav - estilo mobile (funciona en iOS y Android) */}
      <nav className="border-t border-gray-800 flex">
        <NavLink to="/" end className={({isActive}) =>
          `flex-1 flex flex-col items-center py-3 gap-1 text-xs transition-colors ${
            isActive ? 'text-[#fe2c55]' : 'text-gray-500 hover:text-gray-300'
          }`
        }>
          <Video size={20} />
          <span>Crear</span>
        </NavLink>
        <NavLink to="/library" className={({isActive}) =>
          `flex-1 flex flex-col items-center py-3 gap-1 text-xs transition-colors ${
            isActive ? 'text-[#fe2c55]' : 'text-gray-500 hover:text-gray-300'
          }`
        }>
          <Library size={20} />
          <span>Biblioteca</span>
        </NavLink>
      </nav>
    </div>
  )
}
