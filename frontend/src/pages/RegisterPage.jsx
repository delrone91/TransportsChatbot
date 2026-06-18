import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './AuthPage.css'

export default function RegisterPage() {
  const { register } = useAuth()
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(form.username, form.email, form.password)
    } catch (err) {
      setError(err.response?.data?.error || "Erreur d'inscription")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-box">
        <div className="auth-logo">
          <div className="auth-logo-icon">
            <img src="/logo.png" alt="NavigIA" />
          </div>
          <div className="auth-logo-name">NAVIG<span>IA</span></div>
        </div>
        <p className="auth-subtitle">Assistant transports Île-de-France</p>

        <h1>Inscription</h1>
        <form onSubmit={submit}>
          <div className="form-group">
            <label>Nom d'utilisateur</label>
            <input type="text" value={form.username} onChange={update('username')} required autoFocus />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={form.email} onChange={update('email')} required />
          </div>
          <div className="form-group">
            <label>Mot de passe <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(min. 6 caractères)</span></label>
            <input type="password" value={form.password} onChange={update('password')} minLength={6} required />
          </div>
          {error && <p className="form-error">{error}</p>}
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Inscription...' : "S'inscrire"}
          </button>
        </form>
        <p className="auth-link">
          Déjà un compte ? <Link to="/login">Se connecter</Link>
        </p>
      </div>
    </div>
  )
}
