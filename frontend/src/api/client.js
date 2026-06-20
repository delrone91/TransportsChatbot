import axios from 'axios'

// Client HTTP configuré pour toutes les requêtes vers le backend Flask
// En dev : baseURL '/' fonctionne grâce au proxy configuré dans vite.config.js
// En prod : VITE_API_URL pointe vers l'URL publique du backend (Render)
const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/',
  headers: { 'Content-Type': 'application/json' },
})

// Intercepteur : avant chaque requête, on ajoute automatiquement le token
// d'authentification s'il est présent dans le localStorage
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default client
