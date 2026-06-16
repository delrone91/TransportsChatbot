import { createContext, useContext, useState, useEffect } from 'react'
import client from '../api/client'

// Contexte global pour partager l'état de connexion dans toute l'application
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Au chargement de la page, on vérifie si un token est déjà sauvegardé
    // Si oui, on récupère les infos de l'utilisateur pour le reconnecter automatiquement
    const token = localStorage.getItem('token')
    if (!token) { setLoading(false); return }
    client.get('/auth/me')
      .then(r => setUser(r.data))
      .catch(() => localStorage.removeItem('token')) // Token invalide, on le supprime
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const r = await client.post('/auth/login', { email, password })
    // On sauvegarde le token dans le localStorage pour persister la session
    localStorage.setItem('token', r.data.token)
    setUser(r.data.user)
  }

  const register = async (username, email, password) => {
    const r = await client.post('/auth/register', { username, email, password })
    localStorage.setItem('token', r.data.token)
    setUser(r.data.user)
  }

  const logout = async () => {
    // On appelle le backend pour invalider le token côté serveur
    try { await client.post('/auth/logout') } catch {}
    localStorage.removeItem('token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook personnalisé pour accéder facilement au contexte dans n'importe quel composant
export const useAuth = () => useContext(AuthContext)
