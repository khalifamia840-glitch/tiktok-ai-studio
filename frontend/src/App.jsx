import { Routes, Route, NavLink, useNavigate, useLocation, Navigate } from 'react-router-dom'
import { Video, Library, LayoutDashboard, Settings, LogOut, Menu, X, Sparkles, Flame } from 'lucide-react'
import { useState, useEffect } from 'react'
import GeneratePage from './pages/GeneratePage'
import LibraryPage from './pages/LibraryPage'
import DashboardPage from './pages/DashboardPage'
import AuthPage from './pages/AuthPage'
import LandingPage from './pages/LandingPage'
import TrendsPage from './pages/TrendsPage'
import { AuthProvider, useAuth } from './contexts/AuthContext'

function AuthGuard({ children }) {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/auth" replace />
  return children
}

function AppLayout({ children }) {
  const { user, logout } = useAuth()
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const location = useLocation()

  // Cerrar sidebar al cambiar de ruta en móvil
  useEffect(() => {
    setIsSidebarOpen(false)
  }, [location])

  const navItems = [
    { to: '/generate', icon: Video, label: 'Crear Video' },
    { to: '/trends', icon: Flame, label: 'Tendencias' },
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/library', icon: Library, label: 'Biblioteca' },
    { to: '/settings', icon: Settings, label: 'Ajustes' },
  ]

  return (
    <div className="min-h-screen flex bg-[#010101] text-white overflow-hidden">
      {/* Mobile Header */}
      <header className="lg:hidden fixed top-0 left-0 right-0 h-16 glass z-40 px-4 flex items-center justify-between border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-[#fe2c55] to-[#25f4ee] rounded-lg flex items-center justify-center">
            <Video size={18} />
          </div>
          <span className="font-bold font-heading">AI Studio</span>
        </div>
        <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-white/5 rounded-xl transition-colors">
          {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </header>

      {/* Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/80 backdrop-blur-sm z-40"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50 w-72 glass border-r border-white/5 
        transform transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="h-full flex flex-col p-6">
          {/* Logo */}
          <div className="hidden lg:flex items-center gap-3 mb-10 px-2 cursor-pointer" onClick={() => window.location.href='/'}>
            <div className="w-10 h-10 bg-gradient-to-br from-[#fe2c55] to-[#25f4ee] rounded-xl flex items-center justify-center shadow-lg shadow-[#fe2c55]/20">
              <Video size={22} />
            </div>
            <div>
              <h1 className="font-bold text-xl font-heading leading-none">AI Studio</h1>
              <span className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">TikTok Pro</span>
            </div>
          </div>

          {/* Nav */}
          <nav className="flex-1 space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `
                  flex items-center gap-4 px-4 py-3.5 rounded-2xl transition-all duration-200 group
                  ${isActive 
                    ? 'bg-gradient-to-r from-[#fe2c55] to-[#ff4b2b] text-white shadow-lg shadow-[#fe2c55]/20' 
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'}
                `}
              >
                <item.icon size={20} className={({ isActive }) => isActive ? '' : 'group-hover:scale-110 transition-transform'} />
                <span className="font-semibold">{item.label}</span>
              </NavLink>
            ))}
          </nav>

          {/* User & Logout */}
          <div className="mt-auto pt-6 border-t border-white/5">
            {user ? (
              <>
                <div className="flex items-center gap-3 px-2 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center font-bold text-sm">
                    {user.name?.[0]}{user.apellido?.[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-sm truncate">{user.name} {user.apellido}</p>
                    <p className="text-xs text-gray-500 truncate capitalize">{user.role || 'Plan Gratis'}</p>
                  </div>
                </div>
                <button 
                  onClick={logout}
                  className="w-full flex items-center gap-4 px-4 py-3.5 rounded-2xl text-gray-400 hover:bg-red-500/10 hover:text-red-500 transition-all group"
                >
                  <LogOut size={20} className="group-hover:translate-x-1 transition-transform" />
                  <span className="font-semibold">Cerrar Sesión</span>
                </button>
              </>
            ) : (
              <div className="text-center space-y-3 px-2">
                <p className="text-xs text-gray-500">¿Quieres guardar tus videos?</p>
                <NavLink to="/auth" className="btn-premium w-full !py-2 !text-sm">Crear Cuenta</NavLink>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 h-screen overflow-y-auto pt-16 lg:pt-0 sidebar-scroll relative z-10">
        {children}
      </main>
    </div>
  )
}

function AppContent() {
  const { loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#010101]">
        <div className="w-12 h-12 border-4 border-[#fe2c55] border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/auth" element={<AuthPage />} />
      
      {/* Rutas con Sidebar (algunas públicas, otras protegidas) */}
      <Route path="/generate" element={<AppLayout><GeneratePage /></AppLayout>} />
      <Route path="/trends" element={<AppLayout><TrendsPage /></AppLayout>} />
      
      {/* Rutas Privadas */}
      <Route path="/dashboard" element={<AuthGuard><AppLayout><DashboardPage /></AppLayout></AuthGuard>} />
      <Route path="/library" element={<AuthGuard><AppLayout><LibraryPage /></AppLayout></AuthGuard>} />
      <Route path="/settings" element={
        <AuthGuard>
          <AppLayout>
            <div className="p-8 text-center text-gray-500">
              <Settings size={48} className="mx-auto mb-4 opacity-20" />
              <h2 className="text-xl font-bold text-white mb-2">Configuración</h2>
              <p>Funcionalidad en desarrollo...</p>
            </div>
          </AppLayout>
        </AuthGuard>
      } />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}
