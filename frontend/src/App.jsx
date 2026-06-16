import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ChatPage from './pages/ChatPage'

// Route accessible uniquement si l'utilisateur est connecté
// Sinon on redirige vers la page de connexion
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="full-loading">Chargement...</div>
  return user ? children : <Navigate to="/login" replace />
}

// Route accessible uniquement si l'utilisateur n'est PAS connecté
// Evite qu'un utilisateur déjà connecté accède à /login ou /register
function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="full-loading">Chargement...</div>
  return user ? <Navigate to="/" replace /> : children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login"    element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
      <Route path="/"         element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
      {/* Toute URL inconnue redirige vers la page principale */}
      <Route path="*"         element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
