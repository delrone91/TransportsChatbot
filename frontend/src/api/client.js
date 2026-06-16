import axios from 'axios'

// Client HTTP configuré pour toutes les requêtes vers le backend Flask
// Le baseURL '/' fonctionne grâce au proxy configuré dans vite.config.js
const client = axios.create({
  baseURL: '/',
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
