import { useState } from 'react'
import './Sidebar.css'

export default function Sidebar({ sessions, activeSession, user, onSelect, onCreate, onDelete, onLogout }) {
  const [open, setOpen] = useState(false) // panneau deplie sur mobile

  const handleSelect = (session) => {
    onSelect(session)
    setOpen(false)
  }

  const handleCreate = () => {
    onCreate()
    setOpen(false)
  }

  return (
    <aside className={`sidebar ${open ? 'sidebar--open' : ''}`}>
      <div className="sidebar-top">
        <div className="sidebar-brand">
          <div className="brand-icon">
            <img src="/logo.png" alt="NavigIA" />
          </div>
          <div>
            <div className="brand-name">NavigIA</div>
            <div className="brand-subtitle">Transports Ile-de-France</div>
          </div>
          <button
            className="sidebar-toggle"
            onClick={() => setOpen((o) => !o)}
            aria-label={open ? 'Fermer le menu' : 'Ouvrir le menu'}
            aria-expanded={open}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M3 12h18M3 18h18" />
            </svg>
          </button>
        </div>

        <button className="btn-new" onClick={handleCreate}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4">
            <path d="M12 5v14M5 12h14" />
          </svg>
          Nouvelle recherche
        </button>
      </div>

      <nav className="sessions-list">
        {sessions.length > 0 && <p className="sessions-label">Historique</p>}
        {sessions.length === 0 && (
          <p className="no-sessions">Aucune recherche pour le moment.</p>
        )}
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`session-item ${activeSession?.id === session.id ? 'active' : ''}`}
            onClick={() => handleSelect(session)}
          >
            <span className="session-marker" />
            <span className="session-title">{session.title}</span>
            <button
              className="btn-del"
              onClick={(e) => onDelete(session.id, e)}
              title="Supprimer"
              aria-label="Supprimer la conversation"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">{user?.username?.[0]?.toUpperCase()}</div>
          <div className="user-copy">
            <span className="user-name">{user?.username}</span>
            <span className="user-status">Connecte</span>
          </div>
        </div>
        <button className="btn-logout" onClick={onLogout} title="Se deconnecter" aria-label="Se deconnecter">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
        </button>
      </div>
    </aside>
  )
}
