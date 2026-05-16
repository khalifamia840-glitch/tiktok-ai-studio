import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Video, Mail, Lock, User, Calendar, Loader2, AlertCircle } from 'lucide-react'
import { login as apiLogin, register as apiRegister, biometricLogin as apiBiometricLogin } from '../api'
import { useAuth } from '../contexts/AuthContext'

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const { login } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    name: '',
    apellido: '',
    edad: '',
    email: '',
    password: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      if (isLogin) {
        const res = await apiLogin(form.email, form.password)
        login(res.token, res.user)
      } else {
        const res = await apiRegister({
          name: form.name,
          apellido: form.apellido,
          edad: parseInt(form.edad),
          email: form.email,
          password: form.password
        })
        login(res.token, res.user)
      }
      navigate('/')
    } catch (e) {
      setError(e.response?.data?.detail || 'Error en la autenticación')
    } finally {
      setLoading(false)
    }
  }

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-radial-gradient">
      <div className="w-full max-w-md animate-slide-up">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-[#fe2c55] to-[#25f4ee] rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <Video size={32} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold font-heading tiktok-gradient-text">TikTok AI Studio</h1>
          <p className="text-gray-400 mt-2">Genera videos virales en segundos</p>
        </div>

        {/* Form Card */}
        <div className="glass-card">
          <div className="flex bg-white/5 p-1 rounded-xl mb-6">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${isLogin ? 'bg-[#fe2c55] text-white shadow-lg' : 'text-gray-400 hover:text-white'}`}
            >
              Entrar
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${!isLogin ? 'bg-[#fe2c55] text-white shadow-lg' : 'text-gray-400 hover:text-white'}`}
            >
              Registrarse
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <>
                <div className="grid grid-cols-2 gap-3">
                  <div className="relative">
                    <User className="absolute left-4 top-4 text-gray-500" size={18} />
                    <input
                      type="text"
                      placeholder="Nombre"
                      className="input-premium pl-12"
                      value={form.name}
                      onChange={e => set('name', e.target.value)}
                      required
                    />
                  </div>
                  <div className="relative">
                    <User className="absolute left-4 top-4 text-gray-500" size={18} />
                    <input
                      type="text"
                      placeholder="Apellido"
                      className="input-premium pl-12"
                      value={form.apellido}
                      onChange={e => set('apellido', e.target.value)}
                      required
                    />
                  </div>
                </div>
                <div className="relative">
                  <Calendar className="absolute left-4 top-4 text-gray-500" size={18} />
                  <input
                    type="number"
                    placeholder="Edad"
                    className="input-premium pl-12"
                    value={form.edad}
                    onChange={e => set('edad', e.target.value)}
                    required
                  />
                </div>
              </>
            )}

            <div className="relative">
              <Mail className="absolute left-4 top-4 text-gray-500" size={18} />
              <input
                type="email"
                placeholder="Email"
                className="input-premium pl-12"
                value={form.email}
                onChange={e => set('email', e.target.value)}
                required
              />
            </div>

            <div className="relative">
              <Lock className="absolute left-4 top-4 text-gray-500" size={18} />
              <input
                type="password"
                placeholder="Contraseña"
                className="input-premium pl-12"
                value={form.password}
                onChange={e => set('password', e.target.value)}
                required
              />
            </div>

            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-premium w-full mt-4"
            >
              {loading ? <Loader2 className="animate-spin" /> : (isLogin ? 'Iniciar Sesión' : 'Crear Cuenta Gratis')}
            </button>
          </form>

          {isLogin && (
            <div className="mt-6 space-y-4">
              <div className="relative flex items-center justify-center">
                <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-white/5"></div></div>
                <span className="relative px-2 text-[10px] font-bold text-zinc-600 bg-[#050505] uppercase tracking-[0.2em]">O usar biometría</span>
              </div>
              
              <button 
                type="button"
                onClick={async () => {
                  setLoading(true);
                  try {
                    const res = await apiBiometricLogin();
                    login(res.token, res.user);
                    navigate('/');
                  } catch (err) {
                    setError("Error en autenticación biométrica");
                  } finally {
                    setLoading(false);
                  }
                }}
                className="w-full py-3 flex items-center justify-center gap-3 bg-white/5 border border-white/10 rounded-xl text-xs font-bold text-white hover:bg-white/10 transition-all group"
              >
                <div className="p-1.5 rounded-lg bg-gradient-to-br from-[#25f4ee] to-[#fe2c55] group-hover:scale-110 transition-transform">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
                </div>
                Acceso con Biometría (WebAuthn)
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
