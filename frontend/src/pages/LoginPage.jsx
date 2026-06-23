import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './AuthPage.css'

export default function LoginPage() {
  const { login } = useAuth()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form.email, form.password)
    } catch (err) {
      setError(err.response?.data?.error || 'Connexion impossible')
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

          <h1>Bon retour</h1>
          <p className="auth-intro">Retrouvez vos recherches et vos conversations transport.</p>

          <form onSubmit={submit}>
            <div className="form-group">
              <label htmlFor="login-email">Email</label>
              <input id="login-email" type="email" value={form.email} onChange={update('email')} required autoFocus />
            </div>
            <div className="form-group">
              <label htmlFor="login-password">Mot de passe</label>
              <input id="login-password" type="password" value={form.password} onChange={update('password')} required />
            </div>
            {error && <p className="form-error">{error}</p>}
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>
          <p className="auth-link">
            Pas encore de compte ? <Link to="/register">Creer un compte</Link>
          </p>
        </div>

        <aside className="auth-aside">
          <p className="auth-aside-label">A portee de main</p>
          <h2>Les reponses utiles avant de prendre la route.</h2>
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
