import { createContext, useContext, useState, useEffect } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

function hasStoredToken() {
  return typeof window !== 'undefined' && Boolean(localStorage.getItem('token'))
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(hasStoredToken)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setLoading(false)
      return
    }

    client.get('/auth/me')
      .then(r => setUser(r.data))
      .catch(() => localStorage.removeItem('token'))
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const r = await client.post('/auth/login', { email, password })
    localStorage.setItem('token', r.data.token)
    setUser(r.data.user)
  }

  const register = async (username, email, password) => {
    const r = await client.post('/auth/register', { username, email, password })
    localStorage.setItem('token', r.data.token)
    setUser(r.data.user)
  }

  const logout = async () => {
    try {
      await client.post('/auth/logout')
    } catch (err) {
      console.error('Logout serveur echoue, deconnexion locale forcee', err)
    } finally {
      localStorage.removeItem('token')
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext)
