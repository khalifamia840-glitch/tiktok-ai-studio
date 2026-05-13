import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export const useAuth = () => useContext(AuthContext)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('auth_token'))

  useEffect(() => {
    if (token) {
      localStorage.setItem('auth_token', token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchMe()
    } else {
      localStorage.removeItem('auth_token')
      delete axios.defaults.headers.common['Authorization']
      setUser(null)
      setLoading(false)
    }
  }, [token])

  const fetchMe = async () => {
    try {
      const res = await axios.get(`${import.meta.env.VITE_API_URL || ''}/api/auth/me`)
      setUser(res.data)
    } catch (e) {
      console.error('Session expired')
      setToken(null)
    } finally {
      setLoading(false)
    }
  }

  const login = (newToken, userData) => {
    setToken(newToken)
    setUser(userData)
  }

  const logout = () => {
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
