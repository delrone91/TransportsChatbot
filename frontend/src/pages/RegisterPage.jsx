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
      setError(err.response?.data?.error || "Inscription impossible")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <section className="auth-shell">
        <div className="auth-panel">
          <div className="auth-logo">
            <div className="auth-logo-icon">
              <img src="/logo.png" alt="NavigIA" />
            </div>
            <div>
              <div className="auth-logo-name">NavigIA</div>
              <p className="auth-subtitle">Infos transports Ile-de-France</p>
            </div>
          </div>

          <h1>Creer un compte</h1>
          <p className="auth-intro">Gardez vos recherches utiles et reprenez vos conversations plus tard.</p>

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
              <label>Mot de passe <span className="label-note">min. 6 caracteres</span></label>
              <input type="password" value={form.password} onChange={update('password')} minLength={6} required />
            </div>
            {error && <p className="form-error">{error}</p>}
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creation...' : 'Creer mon compte'}
            </button>
          </form>
          <p className="auth-link">
            Deja un compte ? <Link to="/login">Se connecter</Link>
          </p>
        </div>

        <aside className="auth-aside">
          <p className="auth-aside-label">Simple et lisible</p>
          <h2>Un espace clair pour vos questions de transport.</h2>
          <div className="auth-lines">
            <span style={{ background: 'var(--rera)' }}>A</span>
            <span style={{ background: 'var(--rerb)' }}>B</span>
            <span style={{ background: 'var(--rerc)', color: '#2d2d2d' }}>C</span>
            <span style={{ background: 'var(--rerd)' }}>D</span>
          </div>
        </aside>
      </section>
    </div>
  )
}
